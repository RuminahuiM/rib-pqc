"""FastAPI-Dependency fuer Session-authentifizierte Encrypted-Channel-Endpoints.

Story: PQC-51 (DCH-2).
Bezug: docs/wire_format.md Sec 5 (Encrypted-Channel Wire-Format),
FR-DataChannel-2, F-090/F-091/F-092 in docs/13_deferred_findings.md.

**Verantwortung:**

Diese Dependency wird als ``Depends(authenticated_session)`` in alle
geschuetzten Endpoints injected (DCH-3 PQC-52 baut darauf das erste,
``POST /api/profile``). Sie:

1. Liest ``X-Session-Id`` und ``X-Nonce`` aus den Request-Headers.
2. Schlaegt den ``SessionRecord`` im ``SessionService`` (Redis) nach.
3. Liest den Request-Body als ``application/octet-stream``
   (raw ``ciphertext || tag``).
4. Decapsuliert via ``CryptoFacade.aead_decrypt`` mit
   ``session_key`` als Key, X-Nonce-Bytes als Nonce und
   ``session_id.encode("ascii")`` als AAD.
5. Parst den entschluesselten Plaintext als UTF-8-JSON.
6. Konsultiert den ``NonceTracker`` (DCH-4 PQC-53 Hook) auf Replay.
7. Liefert ein ``AuthenticatedSession``-Dataclass-Bundle an den Endpoint.

**Wire-Format-Konformitaet (docs/wire_format.md Sec 5):**

- Headers ``X-Session-Id`` und ``X-Nonce`` sind Pflicht.
- Body ist raw octet-stream mit ``ciphertext || tag`` (Tag konkatenert
  hinten, ``AESGCM.decrypt`` erwartet exakt dieses Format).
- AAD = ``session_id.encode("ascii")``, identisch zu App-Side
  ``aeadEncrypt(..., session_id_bytes)``.

**Error-Mapping (docs/wire_format.md Sec 5.4 erweitert in PQC-51-AC):**

| Trigger                          | Status | Detail-Error              |
|----------------------------------|--------|---------------------------|
| ``X-Session-Id`` fehlt           | 401    | ``session_missing``       |
| ``X-Nonce`` fehlt                | 401    | ``nonce_missing``         |
| ``X-Nonce`` Format ungueltig     | 400    | ``nonce_format_invalid``  |
| session_id nicht in Redis        | 401    | ``session_expired``       |
| AEAD-Tag-Mismatch                | 400    | ``aead_decrypt_failed``   |
| Plaintext nicht UTF-8-JSON       | 400    | ``payload_not_json``      |
| Nonce-Replay (DCH-4)             | 400    | ``nonce_reused``          |

**DCH-4-Hook (PQC-53):**

Die ``NonceTracker``-Pruefung ist bereits drin. Default ist
``NoOpNonceTracker`` der immer ``False`` liefert (keine Replays
erkannt). PQC-53 wechselt im Lifespan auf ``RedisNonceTracker`` ohne
Touch der Dependency-Logik.

**FIPS-203-Implicit-Rejection-Konnex (F-090):**

Wenn das KEM in SES-1 mit einem falschen Public-Key initialisiert wurde
(Forge-Versuch), liefert decaps ein Pseudo-Shared-Secret und HKDF
einen Pseudo-Session-Key. Dieser Key wird in Redis persistiert.
Beim ersten DCH-2-Decrypt schlaegt der AEAD-Tag-Check fehl
(``AeadDecryptError`` -> 400). Das ist die einzige Stelle wo Forge-
Sessions erkannt werden, und sie funktioniert by-design.

**Nonce-Format (F-092):**

``cryptography.hazmat`` ``AESGCM.decrypt`` wirft ``ValueError`` bei
falscher Nonce-Laenge. Wir pruefen explizit auf 12 Byte (NIST SP 800-38D
Section 8.2 Recommended Length) und liefern 400 ``nonce_format_invalid``
statt einen unkontrollierten 500. Falsch dimensionierte Nonces sind ein
Client-Bug, kein Server-Crash.
"""

from __future__ import annotations

import base64
import binascii
import json
from dataclasses import dataclass
from typing import Annotated, Any

from fastapi import Depends, HTTPException, Request, status

from crypto.facade import AeadDecryptError, CryptoFacade
from logging_config import get_logger
from services.nonce_tracker import NonceTracker, NoOpNonceTracker
from services.session_service import (
    SessionNotFoundError,
    SessionRecord,
    SessionService,
)

logger = get_logger("rib_pqc.dependencies.authenticated_session")

# NIST SP 800-38D Section 8.2 Empfehlung: 96-bit (12-byte) Nonce fuer AES-GCM.
_AES_GCM_NONCE_BYTES = 12

_HEADER_SESSION_ID = "X-Session-Id"
_HEADER_NONCE = "X-Nonce"


@dataclass(frozen=True, slots=True)
class AuthenticatedSession:
    """Resultat einer erfolgreichen DCH-2-Dependency-Aufloesung.

    Story: PQC-51 (DCH-2).

    Felder:
    - ``session_id``: die base64url-encoded session_id aus dem Header
      (gleichzeitig der AAD-Wert in ASCII).
    - ``record``: voller SessionRecord aus Redis (user_id, kem_alg,
      session_key, timestamps).
    - ``nonce``: die 12-Byte AES-GCM-Nonce aus X-Nonce (dekodiert).
    - ``plaintext``: rohe entschluesselte Body-Bytes.
    - ``payload``: ``plaintext`` als UTF-8-JSON geparst (dict).
    """

    session_id: str
    record: SessionRecord
    nonce: bytes
    plaintext: bytes
    payload: dict[str, Any]


def _decode_b64url(value: str) -> bytes:
    """Toleranter base64url-Decode mit Padding-Recovery."""
    pad = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + pad)


# ---------------------------------------------------------------------------
# Default-Service-Lookups via app.state (Pattern wie routers/session.py)
# ---------------------------------------------------------------------------


def _get_facade(request: Request) -> CryptoFacade:
    """Liefert die im Lifespan gewirete ``CryptoFacade``."""
    return request.app.state.crypto_facade  # type: ignore[no-any-return]


def _get_session_service(request: Request) -> SessionService:
    """Liefert den im Lifespan gewireten ``SessionService``."""
    return request.app.state.session_service  # type: ignore[no-any-return]


def _get_nonce_tracker(request: Request) -> NonceTracker:
    """Liefert den ``NonceTracker`` aus ``app.state`` (Default NoOp).

    Story-Bezug: PQC-51 DCH-2 (NoOp), PQC-53 DCH-4 (Redis-basiert).
    """
    # Fallback auf NoOp wenn Wiring vergessen (defensive). DCH-4 sorgt fuer
    # echten Tracker.
    tracker = getattr(request.app.state, "nonce_tracker", None)
    if tracker is None:
        return NoOpNonceTracker()
    return tracker  # type: ignore[no-any-return]


# ---------------------------------------------------------------------------
# Die Dependency
# ---------------------------------------------------------------------------


async def authenticated_session(
    request: Request,
    facade: Annotated[CryptoFacade, Depends(_get_facade)],
    session_service: Annotated[SessionService, Depends(_get_session_service)],
    nonce_tracker: Annotated[NonceTracker, Depends(_get_nonce_tracker)],
) -> AuthenticatedSession:
    """FastAPI-Dependency: loest einen Encrypted-Channel-Aufruf auf.

    Story: PQC-51 (DCH-2). Implementation der Detail-AC 1-11.

    Use:

    .. code-block:: python

        @router.post("/api/profile")
        async def profile(
            session: Annotated[AuthenticatedSession, Depends(authenticated_session)],
        ):
            ...

    Raises:
        HTTPException 401 ``session_missing`` wenn ``X-Session-Id`` fehlt.
        HTTPException 401 ``nonce_missing`` wenn ``X-Nonce`` fehlt.
        HTTPException 400 ``nonce_format_invalid`` bei base64-Fehler oder
            Laenge != 12 Byte.
        HTTPException 401 ``session_expired`` wenn session_id nicht in Redis.
        HTTPException 400 ``nonce_reused`` wenn DCH-4-Tracker die Nonce kennt.
        HTTPException 400 ``aead_decrypt_failed`` bei Tag-Mismatch.
        HTTPException 400 ``payload_not_json`` bei JSON-Decode-Fehler.
    """
    session_id = request.headers.get(_HEADER_SESSION_ID)
    if not session_id:
        logger.info(
            "dch2.session_missing path=%s",
            request.url.path,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "session_missing"},
        )

    nonce_header = request.headers.get(_HEADER_NONCE)
    if not nonce_header:
        logger.info(
            "dch2.nonce_missing session_id_prefix=%s path=%s",
            session_id[:8],
            request.url.path,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "nonce_missing"},
        )

    # Detail-AC 5: Nonce-Format (12 Byte nach base64url-Decode).
    # F-092 streng durchsetzen.
    try:
        nonce = _decode_b64url(nonce_header)
    except (binascii.Error, ValueError):
        logger.info(
            "dch2.nonce_format_invalid session_id_prefix=%s reason=base64_decode",
            session_id[:8],
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "nonce_format_invalid"},
        )
    if len(nonce) != _AES_GCM_NONCE_BYTES:
        logger.info(
            "dch2.nonce_format_invalid session_id_prefix=%s len=%d expected=%d",
            session_id[:8],
            len(nonce),
            _AES_GCM_NONCE_BYTES,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "nonce_format_invalid"},
        )

    # Detail-AC 6: SessionService-Lookup. Side-Channel-frei
    # ``session_expired`` mappen.
    try:
        record = await session_service.get(session_id)
    except SessionNotFoundError:
        logger.info(
            "dch2.session_expired session_id_prefix=%s",
            session_id[:8],
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "session_expired"},
        )

    # Body als raw octet-stream lesen.
    body = await request.body()

    # AAD = session_id ASCII-Bytes (wire_format.md Sec 5.2).
    aad = session_id.encode("ascii")

    # Detail-AC 7: AEAD-Decrypt. AeadDecryptError -> 400 + WARNING-Log
    # (Security-Forensik).
    try:
        plaintext = facade.aead_decrypt(
            record.session_key,
            nonce,
            body,
            aad=aad,
        )
    except AeadDecryptError:
        logger.warning(
            "dch2.aead_decrypt_failed session_id_prefix=%s body_len=%d reason=tag_mismatch",
            session_id[:8],
            len(body),
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "aead_decrypt_failed"},
        )

    # Detail-AC 9: UTF-8-JSON-Parsing. Decode-Fehler -> 400.
    try:
        payload = json.loads(plaintext.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        logger.info(
            "dch2.payload_not_json session_id_prefix=%s plaintext_len=%d",
            session_id[:8],
            len(plaintext),
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "payload_not_json"},
        )
    if not isinstance(payload, dict):
        logger.info(
            "dch2.payload_not_json session_id_prefix=%s top_type=%s",
            session_id[:8],
            type(payload).__name__,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "payload_not_json"},
        )

    # DCH-4 (PQC-53): atomarer Replay-Check via NonceTracker.
    # Reihenfolge NACH Decrypt+Parse ist absichtlich Side-Channel-frei:
    # nur bonafide (= AEAD-Tag-verifizierte) Nonces werden im Tracker
    # registriert, Forge-Versuche mit zufaelligen Nonces verbrennen keine
    # Replay-Slots. check_and_register ist atomar (Redis SET NX EX), das
    # schliesst die Race-Condition aus, die das alte has_seen->record-Paar
    # noch offen liess.
    first_use = await nonce_tracker.check_and_register(
        session_id=session_id, nonce=nonce
    )
    if not first_use:
        logger.warning(
            "dch2.nonce_reused session_id_prefix=%s",
            session_id[:8],
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "nonce_reused"},
        )

    logger.debug(
        "dch2.authenticated session_id_prefix=%s user_id=%s body_len=%d plaintext_len=%d",
        session_id[:8],
        record.user_id,
        len(body),
        len(plaintext),
    )
    return AuthenticatedSession(
        session_id=session_id,
        record=record,
        nonce=nonce,
        plaintext=plaintext,
        payload=payload,
    )
