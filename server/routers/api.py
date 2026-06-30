"""Geschuetzter API-Endpoint /api/profile.

Story: PQC-52 (DCH-3).
Bezug: UC-5, FR-DataChannel-1, FR-DataChannel-2, docs/wire_format.md Sec 5.2/5.3.

**Endpoint:**

- ``POST /api/profile``: liefert das User-Profile verschluesselt zurueck.
  Authentication + Decrypt sind komplett im DCH-2 ``authenticated_session``
  Dependency gekapselt (Session-Lookup, AEAD-Decrypt, JSON-Parse, Replay-
  Check via DCH-4). Dieser Endpoint kuemmert sich ausschliesslich um den
  DB-Lookup und die Response-Encryption.

**Wire-Format (Response):**

- Status 200 OK
- Headers:

  * ``X-Nonce: <base64url(12-byte fresh CSPRNG nonce)>``
  * ``Content-Type: application/octet-stream``

- Body: raw ``ciphertext || tag`` (AES-256-GCM, AAD = ``session_id.encode("ascii")``).

  Plaintext (vor Encryption):

  .. code-block:: json

      {
        "user_id": "<uuid>",
        "email": "<lowercase>",
        "auth_method": "local|google|microsoft",
        "created_at": "<ISO-8601 with Z>"
      }

**Fehler-Responses:**

- 401 ``user_not_found`` (plaintext, ``{detail: {error: user_not_found}}``)
  wenn der ``session.record.user_id`` keinen User-Record in der DB hat.
  Edge-Case: Session lebt, User wurde geloescht. App soll Re-Auth triggern.
- 401 ``session_expired`` / ``session_missing`` / ``nonce_missing`` etc.:
  alle vom DCH-2 Dependency aus authenticated_session.py geliefert (delegiert).

**Sicherheits-Notizen:**

- ``aead_random_nonce`` via ``CryptoFacade`` ist CSPRNG (``secrets.token_bytes``).
  Birthday-Limit fuer Nonce-Kollision bei 96-bit ist ~2^48 Sessions parallel.
- Response-Nonce wird im NonceTracker registriert (DCH-4-Konvention), damit
  derselbe Wert nicht spaeter als Request-Nonce wiederverwendet werden
  koennte. ``check_and_register`` sollte praktisch immer True liefern; bei
  False wird 500 returnt (interner Fehler).
- ``password_hash`` und ``external_sub`` werden bewusst NICHT in die Response
  geschrieben (User-Hygiene, vor allem Privacy-by-Design).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from crypto.facade import CryptoFacade
from dependencies.authenticated_session import (
    AuthenticatedSession,
    authenticated_session,
)
from db.repositories.user_repository import UserRepository
from logging_config import get_logger
from services.nonce_tracker import NonceTracker

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

import base64
import json

logger = get_logger("rib_pqc.api.profile")

router = APIRouter(prefix="/api", tags=["api"])


# ---------------------------------------------------------------------------
# Local Service-Lookups (Pattern wie routers/session.py)
# ---------------------------------------------------------------------------


async def _get_db_session(request: Request) -> AsyncIterator[AsyncSession]:
    """Frische DB-Session pro Request (Pattern aus routers/auth.py)."""
    session_factory = request.app.state.session_factory
    async with session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


def _get_facade(request: Request) -> CryptoFacade:
    return request.app.state.crypto_facade  # type: ignore[no-any-return]


def _get_nonce_tracker(request: Request) -> NonceTracker:
    return request.app.state.nonce_tracker  # type: ignore[no-any-return]


def _format_iso_utc(ts) -> str:
    """Formatiert ein datetime als ISO-8601 mit `Z`-Suffix fuer UTC.

    Robust gegen tz-naive Werte (SQLite-Fall: `DateTime(timezone=True)`
    speichert ohne TZ-Suffix). Wenn tzinfo None: Annahme UTC.
    """
    iso = ts.isoformat()
    if ts.tzinfo is None:
        return iso + "Z"
    return iso.replace("+00:00", "Z")


def _b64url_no_pad(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------


@router.post("/profile")
async def get_profile(
    request: Request,
    session: Annotated[AuthenticatedSession, Depends(authenticated_session)],
    db: Annotated[AsyncSession, Depends(_get_db_session)],
    facade: Annotated[CryptoFacade, Depends(_get_facade)],
    nonce_tracker: Annotated[NonceTracker, Depends(_get_nonce_tracker)],
) -> Response:
    """Liefert das verschluesselte User-Profile.

    Story: PQC-52 (DCH-3).

    Authentication, Decrypt + Replay-Check passieren in
    ``authenticated_session``. Hier nur:

    1. UserRepository-Lookup via ``session.record.user_id``.
    2. Profile-JSON bauen (id/email/auth_method/created_at).
    3. Fresh CSPRNG-Nonce ueber CryptoFacade.aead_random_nonce.
    4. Nonce im Tracker registrieren (Defense gegen Nonce-Crosstalk Request-Response).
    5. AEAD-Encrypt mit session_key + Nonce + AAD = session_id.encode("ascii").
    6. HTTP 200 mit Header X-Nonce + raw octet-stream-Body.

    Logging delete-Sentinel ``request`` aus Argumenten ist absichtlich
    da, falls spaeter request-spezifisches Logging dazukommt.
    """
    del request  # aktuell nicht direkt benutzt, Future-Hook

    user_repo = UserRepository(db)
    user = await user_repo.find_by_id(session.record.user_id)
    if user is None:
        logger.warning(
            "dch3.user_not_found session_id_prefix=%s user_id=%s",
            session.session_id[:8],
            session.record.user_id,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "user_not_found"},
        )

    # Plaintext-Payload (UC-5 Schritt 8). created_at als ISO-8601 mit Z.
    payload = {
        "user_id": user.id,
        "email": user.email,
        "auth_method": user.auth_method,
        "created_at": _format_iso_utc(user.created_at),
    }
    plaintext = json.dumps(payload, separators=(",", ":")).encode("utf-8")

    # Fresh CSPRNG-Nonce + Tracker-Eintrag.
    response_nonce = facade.aead_random_nonce()
    first_use = await nonce_tracker.check_and_register(
        session_id=session.session_id,
        nonce=response_nonce,
    )
    if not first_use:
        # Mit 96-bit CSPRNG astronomisch unwahrscheinlich (Birthday 2^48).
        # Falls es trotzdem mal triggert, dann ist das ein interner Fehler:
        # nicht silently weitergeben, sonst koennte ein Replay einer alten
        # Server-Response triggern.
        logger.error(
            "dch3.response_nonce_collision session_id_prefix=%s",
            session.session_id[:8],
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "response_nonce_collision"},
        )

    aad = session.session_id.encode("ascii")
    ciphertext_and_tag = facade.aead_encrypt(
        session.record.session_key,
        response_nonce,
        plaintext,
        aad=aad,
    )

    logger.debug(
        "dch3.profile_responded session_id_prefix=%s user_id=%s plaintext_len=%d body_len=%d",
        session.session_id[:8],
        user.id,
        len(plaintext),
        len(ciphertext_and_tag),
    )

    return Response(
        content=ciphertext_and_tag,
        status_code=status.HTTP_200_OK,
        media_type="application/octet-stream",
        headers={"X-Nonce": _b64url_no_pad(response_nonce)},
    )
