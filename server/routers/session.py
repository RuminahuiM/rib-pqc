"""PQ-Session Init Router.

Story: PQC-46 (SES-1).
Bezug: UC-4, FR-Session-1, docs/wire_format.md Sektion 3 (Session-Init Wire-Format).

**Endpoint:**

- ``POST /session/init``: Authentifizierter Endpoint. Akzeptiert
  ``{ kem_alg, encapsulation_key }`` plus ``Authorization: Bearer <broker-token>``.
  Server fuehrt ML-KEM-Encapsulation aus, leitet via HKDF einen 32-Byte
  Session-Key ab und persistiert die Session im Redis-Store mit TTL.
  Response: ``{ session_id, ciphertext, expires_in, kem_alg }``.

**Fehler-Responses:**

- 401 ``invalid_token`` wenn Authorization fehlt oder Token-Verify scheitert.
- 406 ``kem_alg_not_supported`` (SES-4 Negotiation) wenn der angefragte
  kem_alg nicht in der Registry steht. Antwort enthaelt
  ``supported_algorithms`` damit der Client einen unterstuetzten Algorithmus
  waehlen kann.
- 400 ``invalid_encapsulation_key`` wenn die uebergebene base64url-codierte
  Public-Key-Laenge nicht zur FIPS-203-Spezifikation passt
  (ML-KEM-768 = 1184 Byte, ML-KEM-1024 = 1568 Byte) oder das Base64 nicht
  dekodierbar ist.

**Sicherheits-Notizen:**

- F-090 Implicit-Rejection: ``kem_encaps`` selbst kann (anders als decaps)
  bei ungueltigem Public-Key durchaus RuntimeError werfen (liboqs prueft
  Public-Key-Laenge intern). Wir fangen das ab und mappen auf 400.
- Token-Verify-Fehler differenzieren wir nicht (no detail leak).
- session_key wird NIEMALS in Response-Body oder Logs ausgegeben. Nur
  ciphertext + session_id verlassen den Server.
- Rate-Limit-Hook: Endpoint ist via routers/__init__.py potenziell unter
  Rate-Limiter (SEC-5). Sprint-3-Default vererbt die globale Rate.
"""

from __future__ import annotations

import base64
import binascii
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

from crypto.facade import CryptoFacade
from logging_config import get_logger
from services.session_key_derivation import derive_session_key
from services.session_service import SessionService
from services.token_service import TokenService, TokenServiceError

logger = get_logger("rib_pqc.session")

router = APIRouter(prefix="/session", tags=["session"])

# FIPS 203 Public-Key-Laengen pro Algorithmus (Table 3).
# Wir whitelisten beide ML-KEM-Varianten; Registry-Pruefung erfolgt
# zusaetzlich gegen CryptoFacade.is_kem_supported.
_FIPS203_PK_LENGTHS: dict[str, int] = {
    "ML-KEM-768": 1184,
    "ML-KEM-1024": 1568,
}


# ---------------------------------------------------------------------------
# Pydantic Models (Wire-Format laut docs/wire_format.md Sektion 3)
# ---------------------------------------------------------------------------


class SessionInitRequest(BaseModel):
    """Request-Body fuer POST /session/init.

    Story-Bezug: PQC-46 SES-1 AC-1.
    """

    kem_alg: str = Field(
        min_length=1,
        description="KEM-Algorithmus-Name (z.B. 'ML-KEM-768').",
    )
    encapsulation_key: str = Field(
        min_length=1,
        description=(
            "base64url-codierter ML-KEM-Public-Key des Clients. "
            "Laenge muss FIPS-203-Spezifikation entsprechen."
        ),
    )


class SessionInitResponse(BaseModel):
    """Response-Body fuer POST /session/init.

    Story-Bezug: PQC-46 SES-1 AC-3.
    """

    session_id: str = Field(description="urlsafe-base64-Session-Identifier.")
    ciphertext: str = Field(
        description="base64url-codierter ML-KEM-Ciphertext fuer den Client zum Decapsulieren.",
    )
    expires_in: int = Field(
        gt=0,
        description="Sekunden bis Session-TTL-Ablauf (default 900).",
    )
    kem_alg: str = Field(description="Echo des Algorithmus zur Selbst-Deklaration.")


class KemAlgNotSupportedResponse(BaseModel):
    """406 Not Acceptable Body fuer SES-4 Algorithmus-Negotiation."""

    error: str = Field(default="kem_alg_not_supported")
    requested: str
    supported_algorithms: list[str]


# ---------------------------------------------------------------------------
# Dependencies (Service-Lookup via app.state)
# ---------------------------------------------------------------------------


def _get_facade(request: Request) -> CryptoFacade:
    return request.app.state.crypto_facade  # type: ignore[no-any-return]


def _get_session_service(request: Request) -> SessionService:
    return request.app.state.session_service  # type: ignore[no-any-return]


def _get_token_service(request: Request) -> TokenService:
    return request.app.state.token_service  # type: ignore[no-any-return]


def _get_hkdf_info(request: Request) -> bytes:
    return request.app.state.settings.session.hkdf_info  # type: ignore[no-any-return]


# auto_error=True: HTTPBearer wirft 403 wenn Header fehlt. Wir behandeln das
# unten manuell als 401 weil 401 die korrekte Status-Code-Wahl ist (RFC 7235).
_bearer_scheme = HTTPBearer(auto_error=False)


def _verify_bearer_token(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer_scheme)],
    token_service: Annotated[TokenService, Depends(_get_token_service)],
) -> dict[str, object]:
    """Verifiziert das Bearer-Token und liefert die Claims zurueck.

    Story-Bezug: PQC-46 SES-1 AC-2.

    Raises:
        HTTPException(401): wenn Header fehlt, Bearer-Scheme falsch, oder
            Token-Verify scheitert. Keine Detail-Differenzierung (Side-Channel).
    """
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "invalid_token"},
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        claims = token_service.verify(credentials.credentials)
    except TokenServiceError as exc:
        logger.warning(
            "session.init.token_verify_failed",
            reason=type(exc).__name__,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "invalid_token"},
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    return claims


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------


@router.post(
    "/init",
    response_model=SessionInitResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"description": "Authorization fehlt oder Token-Verify scheitert."},
        406: {
            "description": "kem_alg wird nicht unterstuetzt (SES-4 Negotiation).",
            "model": KemAlgNotSupportedResponse,
        },
        400: {
            "description": "encapsulation_key base64url oder Laenge ungueltig.",
        },
    },
)
async def session_init(
    payload: SessionInitRequest,
    claims: Annotated[dict[str, object], Depends(_verify_bearer_token)],
    facade: Annotated[CryptoFacade, Depends(_get_facade)],
    session_service: Annotated[SessionService, Depends(_get_session_service)],
    hkdf_info: Annotated[bytes, Depends(_get_hkdf_info)],
) -> SessionInitResponse:
    """POST /session/init: PQ-Session-Etablierung via ML-KEM-Encapsulation.

    Story-Bezug: PQC-46 SES-1, FR-Session-1, UC-4.
    """
    # AC-2: kem_alg gegen Registry pruefen, SES-4 Negotiation-Fehler.
    if not facade.is_kem_supported(payload.kem_alg):
        logger.info(
            "session.init.kem_alg_not_supported",
            requested=payload.kem_alg,
            supported=facade.supported_kem_algorithms(),
        )
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail={
                "error": "kem_alg_not_supported",
                "requested": payload.kem_alg,
                "supported_algorithms": facade.supported_kem_algorithms(),
            },
        )

    # base64url-Dekoding des Public-Key.
    try:
        # Padding ist optional in urlsafe_b64decode, wir fuegen es defensiv hinzu.
        pk_bytes = base64.urlsafe_b64decode(
            payload.encapsulation_key + "=" * (-len(payload.encapsulation_key) % 4)
        )
    except (binascii.Error, ValueError) as exc:
        logger.info("session.init.b64_decode_failed", reason=str(exc))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "invalid_encapsulation_key", "reason": "base64url_decode_failed"},
        ) from exc

    # FIPS-203-Laengen-Check.
    expected_pk_len = _FIPS203_PK_LENGTHS.get(payload.kem_alg)
    if expected_pk_len is not None and len(pk_bytes) != expected_pk_len:
        logger.info(
            "session.init.pk_length_mismatch",
            kem_alg=payload.kem_alg,
            expected=expected_pk_len,
            got=len(pk_bytes),
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "invalid_encapsulation_key",
                "reason": "length_mismatch",
                "expected_bytes": expected_pk_len,
                "got_bytes": len(pk_bytes),
            },
        )

    # AC-2: ML-KEM-Encapsulation via Facade.
    try:
        ciphertext, shared_secret = facade.kem_encaps(pk_bytes, payload.kem_alg)
    except (RuntimeError, ValueError) as exc:
        # liboqs wirft RuntimeError bei wrong-format-public-key. ValueError bei
        # Python-Level-Checks. Beides ist Client-Input-Fehler.
        logger.warning(
            "session.init.kem_encaps_failed",
            kem_alg=payload.kem_alg,
            reason=type(exc).__name__,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "invalid_encapsulation_key", "reason": "kem_encaps_failed"},
        ) from exc

    # AC-3 + AC-4: Session-Key per HKDF ableiten + im Store persistieren.
    # SES-2-Konvention (PQC-47) braucht session_id als HKDF-Salt VOR der
    # Ableitung. Daher: erst session_id generieren, dann derive_session_key,
    # dann create_with_id (PQC-48 API-Erweiterung fuer diesen Flow).
    session_id = session_service.generate_session_id()
    session_key = derive_session_key(
        facade,
        shared_secret=shared_secret,
        session_id=session_id,
        hkdf_info=hkdf_info,
    )
    await session_service.create_with_id(
        session_id=session_id,
        user_id=str(claims["sub"]),
        kem_alg=payload.kem_alg,
        session_key=session_key,
    )

    logger.info(
        "session.init.success",
        session_id_prefix=session_id[:8],
        user_id=str(claims["sub"]),
        kem_alg=payload.kem_alg,
        ttl=session_service.ttl_seconds,
    )

    return SessionInitResponse(
        session_id=session_id,
        ciphertext=base64.urlsafe_b64encode(ciphertext).decode("ascii").rstrip("="),
        expires_in=session_service.ttl_seconds,
        kem_alg=payload.kem_alg,
    )
