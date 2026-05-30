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

from auth.password import PasswordHasher
from config import get_settings
from crypto import keys
from crypto.facade import CryptoFacade
from crypto.registry import CryptoRegistry
from crypto.registry_init import init_crypto_registry
from db.engine import create_engine_from_config, create_session_factory
from logging_config import get_logger, setup_logging
from middleware import RequestIdMiddleware, SecurityHeadersMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from routers import health
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
    try:
        yield
    finally:
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
    return app



app = create_app()


def _run() -> None:
    """Entry-Point fuer ``python main.py`` und Docker-CMD."""
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        log_config=None,
    )


if __name__ == "__main__":
    _run()
