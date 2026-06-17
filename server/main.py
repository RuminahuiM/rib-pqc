"""FastAPI-App-Entry fuer den rib-pqc Auth-Service.

Stories: PQC-19 (SKL-1), PQC-21 (CRY-1), PQC-25 (CRY-5).

Lifespan-Hook:
  1. Logging initialisieren
  2. CryptoRegistry mit Plugins befuellen
  3. ML-DSA-65 Signing-Key laden oder im Dev-Modus generieren plus speichern

Lokal starten (mit Hot-Reload)::

    uv sync
    uv run uvicorn main:app --reload

Mit Settings.host/port aus YAML oder ENV::

    uv run python main.py

Im Container::

    docker compose up --build  # aus dem infra/-Ordner heraus
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
from typing import TYPE_CHECKING

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from auth.password import PasswordHasher
from config import get_settings
from crypto import keys
from crypto.facade import CryptoFacade
from crypto.registry import CryptoRegistry
from crypto.registry_init import init_crypto_registry
from db.engine import create_engine_from_config, create_session_factory
from idp.registry_init import init_idp_registry
from logging_config import get_logger, setup_logging
from middleware import (
    RequestIdMiddleware,
    SecurityHeadersMiddleware,
    register_rate_limit,
)
from routers import auth, auth_federated, dev_test, health
from services.id_token_verifier import IdTokenVerifier
from services.oidc_exchange_service import OidcExchangeService
from services.oidc_jwks_service import OidcJwksService
from services.oidc_state_service import OidcStateService
from services.token_service import TokenService

if TYPE_CHECKING:
    from collections.abc import AsyncIterator


def _ensure_signing_keypair(
    *,
    registry: CryptoRegistry,
    algorithm: str,
    private_key_path: Path,
    public_key_path: Path,
    environment: str,
    allow_autogen_in_dev: bool,
) -> tuple[bytes, bytes]:
    """Laed das Signing-Keypair aus der Disk, oder erzeugt es in Dev-Modus.

    PQC-25 AC-5: Private Key wird aus File-Pfad geladen, Public Key extrahierbar.
    Im Dev-Modus wird beim ersten Start auto-keygen plus save gemacht, damit
    der Bootstrap nicht manuelle Pre-Setup-Schritte braucht.

    Returns:
        (public_key, secret_key) als raw bytes.

    Raises:
        FileNotFoundError: wenn Private-Key-File fehlt UND environment != 'dev'.
    """
    plugin = registry.get_signature(algorithm)
    logger = get_logger("rib_pqc.crypto")

    if keys.key_file_exists(private_key_path):
        secret_key = keys.load_key(private_key_path)
        if keys.key_file_exists(public_key_path):
            public_key = keys.load_key(public_key_path)
        else:
            # Public Key fehlt aber Secret Key da. Re-derive via keygen, das
            # liefert ein FRISCHES Keypair, also nicht passend. Bessere Loesung:
            # liboqs hat keine "derive public from secret" Direkt-API. Wir
            # speichern das Public-Key-File zusammen mit dem Secret-Key beim
            # ersten Generieren. Falls public_key_path fehlt, abbrechen.
            msg = (
                f"Public key file missing at {public_key_path} but secret key "
                f"present. Cannot derive public from secret. Re-generate by "
                f"deleting {private_key_path}."
            )
            raise FileNotFoundError(msg)
        logger.info(
            "crypto.signing_key.loaded",
            algorithm=algorithm,
            private_key_path=str(private_key_path),
            public_key_path=str(public_key_path),
        )
        return public_key, secret_key

    # Kein Key-File da. Im Dev-Modus auto-keygen, aber nur mit doppeltem
    # Flag-Check (K-3 aus PQC-25 Review).
    if environment != "dev":
        msg = (
            f"Signing key file does not exist at {private_key_path} and "
            f"environment is '{environment}' (not 'dev'). Refusing to "
            f"auto-generate in non-dev mode."
        )
        raise FileNotFoundError(msg)
    if not allow_autogen_in_dev:
        msg = (
            f"Signing key file does not exist at {private_key_path}. "
            f"Auto-generation requires both environment='dev' AND "
            f"crypto.signature.allow_autogen_in_dev=true. The latter is "
            f"currently false. Refusing to auto-generate."
        )
        raise FileNotFoundError(msg)

    public_key, secret_key = plugin.keygen()
    keys.save_secret_key(private_key_path, secret_key)
    keys.save_public_key(public_key_path, public_key)
    # Warning-Level: Auto-Keygen ist ein Dev-Bequemlichkeitsfeature, sollte
    # niemals stillschweigend in produktivem Setup passieren.
    logger.warning(
        "crypto.signing_key.generated",
        algorithm=algorithm,
        private_key_path=str(private_key_path),
        public_key_path=str(public_key_path),
        public_key_len=len(public_key),
        secret_key_len=len(secret_key),
        note="auto-generated in dev mode, do not use in production",
    )
    return public_key, secret_key


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Initialisiere Logging, CryptoRegistry und Signing-Keypair beim App-Start."""
    settings = get_settings()
    setup_logging(
        log_level=settings.log_level,
        app_name=settings.app_name,
        version=settings.version,
        environment=settings.environment,
    )
    logger = get_logger("rib_pqc.startup")
    logger.info(
        "service.start",
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level,
    )

    # CryptoRegistry per Config befuellen.
    registry = CryptoRegistry()
    init_crypto_registry(
        registry,
        kem_supported=settings.crypto.kem.supported,
        signature_supported=settings.crypto.signature.supported,
    )
    logger.info(
        "crypto.registry.initialized",
        kem=registry.supported_kem(),
        kem_default=settings.crypto.kem.default,
        signature=registry.supported_signature(),
        signature_default=settings.crypto.signature.default,
    )

    # ML-DSA-65 Signing-Key laden oder generieren.
    sig_alg = settings.crypto.signature.default
    public_key, secret_key = _ensure_signing_keypair(
        registry=registry,
        algorithm=sig_alg,
        private_key_path=Path(settings.crypto.signature.private_key_path),
        public_key_path=Path(settings.crypto.signature.public_key_path),
        environment=settings.environment,
        allow_autogen_in_dev=settings.crypto.signature.allow_autogen_in_dev,
    )

    # CryptoFacade als zentraler Einstiegspunkt fuer alle Crypto-Operationen
    # in nachfolgenden Stories (TOK-1 Broker-Token, AUT-3 Login, etc.).
    facade = CryptoFacade(
        registry=registry,
        default_signature_alg=settings.crypto.signature.default,
        signing_kid=settings.crypto.signature.signing_kid,
        signing_secret_key=secret_key,
        verifying_keys_by_kid={settings.crypto.signature.signing_kid: public_key},
    )
    logger.info(
        "crypto.facade.initialized",
        default_signature_alg=settings.crypto.signature.default,
        signing_kid=settings.crypto.signature.signing_kid,
        verifying_kids=sorted({settings.crypto.signature.signing_kid}),
    )

    # PQC-32 (TOK-1): TokenService als Singleton im App-Lifecycle. Stellt
    # Broker-Tokens im JWS-Compact-Format mit ML-DSA-65-Signatur aus. Die
    # CryptoFacade wird per Dependency-Injection uebergeben, der TokenService
    # selber kennt keine Crypto-Implementierungs-Details.
    token_service = TokenService(
        crypto_facade=facade,
        issuer=settings.token.issuer,
        ttl_seconds=settings.token.ttl_seconds,
        allowed_algs=settings.token.allowed_algs,
        exp_leeway_seconds=settings.token.exp_leeway_seconds,
    )
    logger.info(
        "token.service.initialized",
        issuer=settings.token.issuer,
        ttl_seconds=settings.token.ttl_seconds,
        allowed_algs=settings.token.allowed_algs,
        exp_leeway_seconds=settings.token.exp_leeway_seconds,
    )

    # PQC-36 (BRK-1): IdpRegistry initialisieren aus config.idp_providers.
    # Plugin-Adapter werden hier registriert; BRK-2..BRK-6 verwenden sie via
    # ``app.state.idp_registry``. Plugins haben in BRK-1 Stub-Bodies fuer
    # claim_mapper und verify_id_token (NotImplementedError).
    idp_registry = init_idp_registry(settings)
    logger.info(
        "idp.registry.initialized",
        providers=idp_registry.supported(),
    )

    # PQC-28 (AUT-1): Async-DB-Engine plus Session-Factory plus PasswordHasher.
    db_engine = create_engine_from_config(settings.database)
    session_factory = create_session_factory(db_engine)
    password_hasher = PasswordHasher(settings.argon2)
    db_engine = create_engine_from_config(settings.database)
    session_factory = create_session_factory(db_engine)
    password_hasher = PasswordHasher(settings.argon2)
    logger.info(
        "db.session_factory.initialized",
        async_url_scheme=settings.database.async_url.split("://", 1)[0],
    )

    # PQC-37 (BRK-2): Redis-Client + OIDC State + Exchange Services.
    import redis.asyncio as redis_async  # noqa: PLC0415
    import httpx  # noqa: PLC0415
    redis_base = settings.redis_url.rsplit("/", 1)[0]
    state_redis_url = f"{redis_base}/{settings.oidc.state_redis_db}"
    oidc_redis = redis_async.from_url(state_redis_url, decode_responses=False)
    oidc_state_service = OidcStateService(
        redis_client=oidc_redis,
        ttl_seconds=settings.oidc.state_ttl_seconds,
    )
    oidc_http_client = httpx.AsyncClient(timeout=settings.oidc.http_timeout_seconds)
    oidc_exchange_service = OidcExchangeService(
        http_client=oidc_http_client,
        discovery_cache_ttl_seconds=settings.oidc.discovery_cache_ttl_seconds,
    )
    # PQC-38 BRK-3: JwksService + IdTokenVerifier teilen sich denselben
    # httpx-Client wie OidcExchangeService (Connection-Pool wiederverwendet).
    oidc_jwks_service = OidcJwksService(
        http_client=oidc_http_client,
        cache_ttl_seconds=settings.oidc.jwks_cache_ttl_seconds,
    )
    id_token_verifier = IdTokenVerifier(
        jwks_service=oidc_jwks_service,
        exp_leeway_seconds=settings.oidc.id_token_exp_leeway_seconds,
    )
    logger.info(
        "oidc.services.initialized",
        state_redis_url=state_redis_url,
        state_ttl_seconds=settings.oidc.state_ttl_seconds,
        discovery_cache_ttl_seconds=settings.oidc.discovery_cache_ttl_seconds,
        jwks_cache_ttl_seconds=settings.oidc.jwks_cache_ttl_seconds,
        id_token_exp_leeway_seconds=settings.oidc.id_token_exp_leeway_seconds,
    )

    # State im App-Lifecycle ablegen.
    app.state.settings = settings
    app.state.crypto_registry = registry
    app.state.crypto_facade = facade
    app.state.token_service = token_service
    app.state.signing_public_key = public_key
    app.state.signing_secret_key = secret_key
    app.state.db_engine = db_engine
    app.state.session_factory = session_factory
    app.state.password_hasher = password_hasher
    app.state.idp_registry = idp_registry
    app.state.oidc_state_service = oidc_state_service
    app.state.oidc_exchange_service = oidc_exchange_service
    app.state.oidc_jwks_service = oidc_jwks_service
    app.state.id_token_verifier = id_token_verifier
    try:
        yield
    finally:
        await oidc_exchange_service.aclose()
        await oidc_redis.aclose()
        await db_engine.dispose()
        logger.info("service.stop")


def create_app() -> FastAPI:
    """App-Factory. Wird auch fuer Tests verwendet."""
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url=None,
        openapi_url="/openapi.json",
    )
    # TODO(F-013): Bevor `routers.auth` oder andere Endpoints mit Email/Password im
    # Path oder Query hinzukommen (PQC-30 AUT-3), Access-Log-Filtering einrichten.
    # Siehe docs/13_deferred_findings.md (F-013) und Story-Start-Checklist.

    # Middleware-Order (Code-Reihenfolge ist invers zum Request-Flow:
    # last-added ist OUTERMOST). Geplante Request-Flow-Order:
    #
    #   Client -> TrustedHost -> CORS -> SecurityHeaders -> RequestId -> Endpoint
    #
    # - TrustedHost (outermost): early reject bei Host-Header-Injection
    # - CORS: Preflight-OPTIONS-Handling, Allow-Origin-Check
    # - SecurityHeaders: setzt defensive Response-Headers
    # - RequestId (innermost): structlog-Context-Binding, alle anderen Logs
    #   inkl. Endpoint sehen die request_id

    # PQC-83 (SEC-5): Rate-Limiting. Module-level Limiter Singleton aus
    # middleware.rate_limit. SlowAPIMiddleware wird hier registriert.
    register_rate_limit(app)

    # PQC-79 (SEC-1)
    app.add_middleware(RequestIdMiddleware)

    # PQC-82 (SEC-4)
    app.add_middleware(
        SecurityHeadersMiddleware,
        hsts_enabled=(settings.environment != "dev") and settings.security.headers.enabled,
        hsts_max_age_seconds=settings.security.headers.hsts_max_age_seconds,
        hsts_include_subdomains=settings.security.headers.hsts_include_subdomains,
    )

    # PQC-80 (SEC-2): CORS-Middleware. starlette built-in.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.security.cors.allowed_origins,
        allow_methods=settings.security.cors.allowed_methods,
        allow_headers=settings.security.cors.allowed_headers,
        allow_credentials=settings.security.cors.allow_credentials,
    )

    # PQC-81 (SEC-3): TrustedHost outermost - rejected vor allem anderen.
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.security.trusted_hosts,
    )

    app.include_router(health.router)
    # PQC-30 (AUT-3) + PQC-31 (AUT-4): Auth-Router
    app.include_router(auth.router)
    # PQC-37 (BRK-2)
    app.include_router(auth_federated.router)
    # PQC-83 (SEC-5) AC-5: Dev-only Rate-Limit-Test-Endpoint
    if settings.environment == "dev":
        app.include_router(dev_test.router)
    return app



app = create_app()


def _run() -> None:
    """Entry-Point fuer ``python main.py`` und Docker-CMD.

    PQC-83 SEC-5 Closing-Review F-048: ``proxy_headers=True`` und
    ``forwarded_allow_ips`` so setzen, dass uvicorn die ``X-Forwarded-For``-
    Header vom davorgelagerten nginx (Docker-Bridge-Range 172.16.0.0/12)
    auswertet und ``request.client.host`` auf die echte Client-IP setzt.
    Ohne diesen Fix waere ``get_remote_address`` immer die nginx-Container-IP
    und das Rate-Limit wuerde *alle* externen Clients in *einen* Bucket
    zwingen (Per-Cluster statt Per-IP).

    Hinweis fuer Production-Deployment (Sprint 2 PQC-15 TLS-Story): in einer
    echten Umgebung sollte ``forwarded_allow_ips`` auf eine konkrete IP oder
    eine schmale CIDR-Range eingeschraenkt werden, niemals auf ``"*"``.
    """
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        log_config=None,
        proxy_headers=True,
        forwarded_allow_ips="172.16.0.0/12",
    )


if __name__ == "__main__":
    _run()
