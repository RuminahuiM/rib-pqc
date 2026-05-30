"""Auth-Endpoints fuer den rib-pqc Auth-Service.

Stories: PQC-30 (AUT-3 Login-Endpoint), PQC-31 (AUT-4 Enumeration-Schutz).

**Endpoint:** ``POST /auth/local/login``

Akzeptiert JSON ``{"email": "...", "password": "..."}``. Bei korrekten
Credentials liefert es einen ML-DSA-65-signierten Broker-Token als
``{"broker_token": "...", "expires_in": <ttl_seconds>}``.

**Enumeration-Schutz (AUT-4):**

- Bei unbekannter Email wird ``PasswordHasher.dummy_verify()`` aufgerufen,
  damit Response-Zeit nicht zwischen "Email existiert nicht" und "Email
  existiert aber falsches Passwort" unterscheidet.
- Beide Fail-Faelle liefern identische Response: ``401 Unauthorized`` mit
  ``{"error": "invalid_credentials"}``.

**Logging:**

- Erfolgreicher Login: INFO-Level ``auth.login.success`` mit user_id (UUID),
  auth_method. KEIN email-Plaintext (Privacy-by-Design).
- Fehlgeschlagener Login: WARNING-Level ``auth.login.failed`` mit
  generic reason (kein User vs falsches Passwort werden NICHT
  unterschieden, sonst Side-Channel via Logs).
"""

from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession

from auth.password import PasswordHasher
from config import get_settings
from db.repositories import UserRepository
from logging_config import get_logger
from middleware.rate_limit import limiter
from services.token_service import TokenService

_logger = get_logger("rib_pqc.auth.login")

router = APIRouter(prefix="/auth", tags=["auth"])


# ---------------------------------------------------------------------------
# Pydantic Schemas (AC-1, AC-2)
# ---------------------------------------------------------------------------


class LoginRequest(BaseModel):
    """JSON-Body fuer POST /auth/local/login."""

    email: EmailStr = Field(..., description="User-Email-Adresse")
    password: str = Field(
        ...,
        min_length=1,
        max_length=1024,
        description="Plaintext-Passwort (wird ueber TLS uebertragen)",
    )


class LoginResponse(BaseModel):
    """Erfolg-Response 200 OK."""

    broker_token: str = Field(..., description="JWS-Compact-Token mit ML-DSA-65-Signatur")
    expires_in: int = Field(..., description="TTL in Sekunden")


class ErrorResponse(BaseModel):
    """Fail-Response 401 Unauthorized."""

    error: str = Field(..., description="Fehler-Code, z.B. 'invalid_credentials'")


# ---------------------------------------------------------------------------
# FastAPI-Dependencies (Senior-Decision: Depends-Pattern)
# ---------------------------------------------------------------------------


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    """Liefert eine frische AsyncSession pro Request.

    Session-Factory haengt im app.state (gesetzt im lifespan PQC-28).
    """
    session_factory = request.app.state.session_factory
    async with session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_user_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserRepository:
    return UserRepository(session)


def get_password_hasher(request: Request) -> PasswordHasher:
    """PasswordHasher-Singleton aus app.state (gesetzt im lifespan PQC-28)."""
    return request.app.state.password_hasher


def get_token_service(request: Request) -> TokenService:
    """TokenService-Singleton aus app.state (gesetzt im lifespan PQC-32)."""
    return request.app.state.token_service


# ---------------------------------------------------------------------------
# Login-Endpoint (AC-1 bis AC-5)
# ---------------------------------------------------------------------------


_INVALID_CREDENTIALS_DETAIL = "invalid_credentials"


@router.post(
    "/local/login",
    response_model=LoginResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": ErrorResponse,
            "description": "Email oder Passwort falsch (identisch fuer beide Faelle)",
        },
        status.HTTP_429_TOO_MANY_REQUESTS: {
            "description": (
                "Rate-Limit ueberschritten. PQC-83 SEC-5: 5 Login-Versuche pro 15 Minuten "
                "pro IP. Response enthaelt Retry-After-Header."
            ),
        },
    },
    summary="Lokaler Login mit Email/Passwort",
)
@limiter.limit(get_settings().security.rate_limit.login_limit)
async def local_login(
    request: Request,
    payload: LoginRequest,
    repo: Annotated[UserRepository, Depends(get_user_repository)],
    hasher: Annotated[PasswordHasher, Depends(get_password_hasher)],
    token_service: Annotated[TokenService, Depends(get_token_service)],
) -> LoginResponse | JSONResponse:
    """Login-Handler mit Argon2id-Verify und ML-DSA-65-Token-Issue.

    PQC-31 (AUT-4) Enumeration-Schutz:
    - Bei unbekanntem User: ``dummy_verify()`` aufrufen (constant-time)
    - Identische 401-Response unabhaengig vom Fail-Grund
    - Logs mit generic reason

    PQC-30 (AUT-3) Issue-Flow:
    - User-Lookup per Email
    - Argon2id-Verify gegen DB-Hash
    - TokenService.issue(user_id, "local") -> Broker-Token
    """
    email_input = payload.email
    user = await repo.find_by_email(email_input)

    if user is None or user.password_hash is None:
        # Unknown email ODER federated-user (kein password_hash).
        # Beide Faelle: dummy_verify fuer constant-time, dann 401.
        hasher.dummy_verify()
        _logger.warning(
            "auth.login.failed",
            reason="invalid_credentials",
            auth_method="local",
        )
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": _INVALID_CREDENTIALS_DETAIL},
        )

    # User exists with password_hash. Verify.
    if not hasher.verify(payload.password, user.password_hash):
        _logger.warning(
            "auth.login.failed",
            reason="invalid_credentials",
            auth_method="local",
            user_id=user.id,
        )
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": _INVALID_CREDENTIALS_DETAIL},
        )

    # Success: Broker-Token ausstellen.
    token = token_service.issue(
        user_id=user.id,
        auth_method="local",
        external_sub=None,
    )
    _logger.info(
        "auth.login.success",
        user_id=user.id,
        auth_method="local",
    )
    return LoginResponse(
        broker_token=token,
        expires_in=token_service._ttl,
    )


