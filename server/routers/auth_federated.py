"""External OIDC Federated-Auth Router.

Story: PQC-37 (BRK-2) OIDC Authorization Code Flow mit PKCE.

**Endpoints:**

- ``POST /auth/federated/{provider}/authorize`` startet den Flow:
  Server generiert State, speichert ihn in Redis, baut die Authorize-URL.
  Antwort: ``{"authorize_url": "...", "state": "..."}``.

- ``POST /auth/federated/{provider}/callback`` schliesst den Flow ab:
  App sendet ``{code, code_verifier, state}``, Server validiert State (One-Shot),
  tauscht Code gegen IdP-Tokens, gibt ``{id_token, access_token, expires_in}``
  zurueck.

**Note:** PQC-37 AC-1 sagt ``{code, code_verifier}`` ohne ``state``. Wir
erweitern AC-1 um den state-Param fuer CSRF-Schutz, wie es 2026 Best
Current Practice (RFC 9700) verlangt. Erweiterung wird im Done-Comment
dokumentiert.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated

from fastapi import APIRouter, HTTPException, Path, Request, status
from pydantic import BaseModel, Field

from db.repositories import UserIdentityRepository, UserRepository
from idp.registry import IdpRegistry, UnknownProviderError
from logging_config import get_logger
from services.federated_identity_service import FederatedIdentityService
from services.id_token_verifier import IdTokenVerifier, IdTokenVerifyError
from services.oidc_exchange_service import (
    CodeExchangeError,
    DiscoveryError,
    OidcExchangeService,
)
from services.oidc_state_service import OidcStateService, StateNotFoundError

if TYPE_CHECKING:
    pass

logger = get_logger("rib_pqc.auth_federated")

router = APIRouter(prefix="/auth/federated", tags=["auth_federated"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class AuthorizeStartResponse(BaseModel):
    """Response fuer POST /auth/federated/{provider}/authorize."""

    authorize_url: str = Field(min_length=1)
    state: str = Field(min_length=1)


class CallbackRequest(BaseModel):
    """Request fuer POST /auth/federated/{provider}/callback.

    PQC-37 AC-1 erweitert um ``state`` (RFC 9700 BCP CSRF-Schutz, siehe PQC-42).
    """

    code: str = Field(min_length=1, max_length=4096)
    code_verifier: str = Field(min_length=43, max_length=128)  # RFC 7636
    state: str = Field(min_length=1, max_length=512)


class FederatedUserInfo(BaseModel):
    """User-Info Slim-DTO im Callback-Response.

    Story-Bezug: PQC-39 BRK-4. App bekommt die interne User-Identitaet,
    damit sie sie an spaetere Requests anhaengen kann (z.B. via Broker-Token).
    """

    id: str
    email: str
    auth_method: str


class CallbackResponse(BaseModel):
    """Response fuer POST /auth/federated/{provider}/callback.

    Story-Bezug: PQC-37 BRK-2 AC-5 plus PQC-39 BRK-4 (user-Field).
    """

    id_token: str
    access_token: str | None = None
    expires_in: int | None = None
    token_type: str = "Bearer"  # noqa: S105 (OAuth token type, not a password)
    user: FederatedUserInfo


# ---------------------------------------------------------------------------
# Provider-Lookup Helper
# ---------------------------------------------------------------------------


def _get_plugin(request: Request, provider: str):
    """Liefert das IdP-Plugin oder wirft HTTP 404."""
    registry: IdpRegistry = request.app.state.idp_registry
    try:
        return registry.get(provider)
    except UnknownProviderError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "unknown_provider",
                "supported_providers": registry.supported(),
            },
        ) from exc


# ---------------------------------------------------------------------------
# POST /auth/federated/{provider}/authorize
# ---------------------------------------------------------------------------


@router.post(
    "/{provider}/authorize",
    response_model=AuthorizeStartResponse,
    status_code=status.HTTP_200_OK,
)
async def start_authorize(
    request: Request,
    provider: Annotated[str, Path(min_length=1, max_length=32, pattern="^[a-z0-9_-]+$")],
    code_challenge: Annotated[str, ...] = "",
) -> AuthorizeStartResponse:
    """Startet den OIDC-Code-Flow.

    Der Server generiert einen State-Wert, speichert ihn in Redis (mit TTL),
    und baut die Authorize-URL fuer den IdP. Die App leitet den User mit
    dieser URL weiter und behaelt ``state`` lokal um ihn im Callback zu echoen.

    Query-Param ``code_challenge`` ist der PKCE-S256-Hash des App-seitigen
    Verifiers (RFC 7636). Wird in die Authorize-URL durchgereicht.
    """
    del code_challenge  # nur an URL durchreichen, Server speichert nichts dazu

    plugin = _get_plugin(request, provider)
    state_service: OidcStateService = request.app.state.oidc_state_service

    state = await state_service.create(provider=provider)

    # Authorize-URL bauen. Der authorization_endpoint kommt aus dem Discovery-
    # Doc, das der Server cached. Wir fetchen es hier lazy um zu wissen wohin
    # die App weiterleiten soll.
    exchange_service: OidcExchangeService = request.app.state.oidc_exchange_service
    try:
        discovery = await exchange_service.get_discovery_document(plugin.discovery_url)
    except DiscoveryError as exc:
        logger.error(
            "auth_federated.discovery_failed",
            provider=provider,
            error=str(exc),
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={"error": "discovery_failed", "provider": provider},
        ) from exc

    authz_endpoint = discovery.get("authorization_endpoint")
    if not authz_endpoint:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={"error": "discovery_missing_authorization_endpoint"},
        )

    # Query-Params zusammenbauen. ``code_challenge_method=S256`` ist RFC 7636
    # Standard. App liefert das code_challenge ueber Query-String.
    from urllib.parse import urlencode

    query_params = {
        "client_id": plugin.client_id,
        "redirect_uri": plugin.redirect_uri,  # type: ignore[attr-defined]
        "response_type": "code",
        "scope": " ".join(plugin.scopes),
        "state": state,
        # code_challenge wird per request.query_params.get("code_challenge")
        # vom Aufrufer mitgegeben. Wir bauen es so dass die App diesen Param
        # nach dem authorize_url sehen kann.
    }
    code_challenge_value = request.query_params.get("code_challenge")
    if code_challenge_value:
        query_params["code_challenge"] = code_challenge_value
        query_params["code_challenge_method"] = "S256"

    sep = "&" if "?" in authz_endpoint else "?"
    authorize_url = f"{authz_endpoint}{sep}{urlencode(query_params)}"

    logger.info(
        "auth_federated.authorize_start",
        provider=provider,
        state_len=len(state),
        has_pkce=code_challenge_value is not None,
    )

    return AuthorizeStartResponse(authorize_url=authorize_url, state=state)


# ---------------------------------------------------------------------------
# POST /auth/federated/{provider}/callback
# ---------------------------------------------------------------------------


@router.post(
    "/{provider}/callback",
    response_model=CallbackResponse,
    status_code=status.HTTP_200_OK,
)
async def callback(
    request: Request,
    provider: Annotated[str, Path(min_length=1, max_length=32, pattern="^[a-z0-9_-]+$")],
    payload: CallbackRequest,
) -> CallbackResponse:
    """Schliesst den OIDC-Code-Flow ab.

    Story-Bezug: PQC-37 BRK-2 AC-1 bis AC-5.

    Schritte:
    1. Provider-Plugin via Registry holen (404 wenn unknown).
    2. State via OidcStateService.consume (One-Shot, 400 bei Mismatch).
    3. State-Eintrag muss zum Path-Param-Provider passen (400 sonst).
    4. Code+Verifier gegen IdP /token tauschen (400 bei Provider-Fehler).
    5. id_token + access_token zurueckliefern.
    """
    plugin = _get_plugin(request, provider)
    state_service: OidcStateService = request.app.state.oidc_state_service
    exchange_service: OidcExchangeService = request.app.state.oidc_exchange_service

    # State-Validation. One-Shot via consume.
    try:
        state_entry = await state_service.consume(payload.state)
    except StateNotFoundError as exc:
        logger.warning(
            "auth_federated.state_invalid",
            provider=provider,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "invalid_state"},
        ) from exc

    # State-Provider muss zum Path-Param matchen. Schutz gegen Provider-
    # Mix-up (z.B. State fuer Google in /microsoft/callback gepostet).
    if state_entry.provider != provider:
        logger.warning(
            "auth_federated.state_provider_mismatch",
            expected=provider,
            actual=state_entry.provider,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "state_provider_mismatch"},
        )

    # Code-Token-Exchange.
    try:
        result = await exchange_service.exchange_code(
            plugin=plugin,
            code=payload.code,
            code_verifier=payload.code_verifier,
        )
    except DiscoveryError as exc:
        logger.error(
            "auth_federated.discovery_failed",
            provider=provider,
            error=str(exc),
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={"error": "discovery_failed"},
        ) from exc
    except CodeExchangeError as exc:
        logger.warning(
            "auth_federated.exchange_failed",
            provider=provider,
            provider_error=exc.provider_error,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "code_exchange_failed",
                "provider_error": exc.provider_error,
                "provider_error_description": exc.provider_error_description,
            },
        ) from exc

    # PQC-38 (BRK-3) AC-2..AC-4: ID-Token-Verifikation.
    # jwks_uri kommt aus dem Discovery-Doc. Discovery-Doc ist nach exchange
    # bereits gecached, daher hier kein zusaetzlicher Round-Trip.
    id_token_verifier: IdTokenVerifier = request.app.state.id_token_verifier
    try:
        discovery = await exchange_service.get_discovery_document(plugin.discovery_url)
    except DiscoveryError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={"error": "discovery_failed"},
        ) from exc
    jwks_uri = discovery.get("jwks_uri")
    if not jwks_uri:
        logger.error(
            "auth_federated.discovery_missing_jwks_uri",
            provider=provider,
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={"error": "discovery_missing_jwks_uri"},
        )

    try:
        verified_claims = await plugin.verify_id_token(
            token=result.id_token,
            jwks_uri=jwks_uri,
            verifier=id_token_verifier,
        )
    except IdTokenVerifyError as exc:
        logger.warning(
            "auth_federated.id_token_invalid",
            provider=provider,
            reason=exc.reason,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "invalid_id_token",
                "reason": exc.reason,
            },
        ) from exc

    logger.info(
        "auth_federated.id_token_verified",
        provider=provider,
        sub=verified_claims.get("sub"),
    )

    # PQC-39 (BRK-4) AC-1..AC-4, AC-6: claim_mapper + link_or_create.
    try:
        normalized = plugin.claim_mapper(verified_claims)
    except ValueError as exc:
        logger.error(
            "auth_federated.claim_mapper_failed",
            provider=provider,
            error=str(exc),
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "claim_mapper_failed"},
        ) from exc

    # Per-Request DB-Session aus app.state.session_factory.
    session_factory = request.app.state.session_factory
    async with session_factory() as session:
        user_repo = UserRepository(session)
        identity_repo = UserIdentityRepository(session)
        identity_service = FederatedIdentityService(
            user_repository=user_repo,
            identity_repository=identity_repo,
        )
        user = await identity_service.link_or_create(
            provider=provider,
            normalized=normalized,
        )
        user_id = user.id
        user_email = user.email
        user_auth_method = user.auth_method

    logger.info(
        "auth_federated.user_resolved",
        provider=provider,
        user_id=user_id,
    )

    logger.info(
        "auth_federated.callback_success",
        provider=provider,
        has_access_token=result.access_token is not None,
    )

    # AC-5: ID-Token zurueckliefern fuer BRK-3 Weiter-Verarbeitung. Heute
    # gehts noch direkt an die App; in spaeteren Stories wird BRK-4 die
    # Identity normalisieren und einen lokalen Broker-Token signieren.
    return CallbackResponse(
        id_token=result.id_token,
        access_token=result.access_token,
        expires_in=result.expires_in,
        token_type=result.token_type,
        user=FederatedUserInfo(
            id=user_id,
            email=user_email,
            auth_method=user_auth_method,
        ),
    )
