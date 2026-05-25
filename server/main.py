"""FastAPI-App-Entry fuer den rib-pqc Auth-Service.

Stories: PQC-19 (SKL-1), PQC-21 (CRY-1).

Aktuelle Aufgabe: minimaler Service, der per Health-Endpoint Liveness zeigt,
korrekt strukturiertes JSON-Logging ausgibt und eine CryptoRegistry mit den
in der Config aufgefuehrten KEM- und Signatur-Algorithmen aufbaut.

Lokal starten (mit Hot-Reload, ignoriert Settings.host/port)::

    uv sync
    uv run uvicorn main:app --reload

Lokal mit Settings.host/port aus YAML oder ENV::

    uv run python main.py

Im Container (default CMD ruft ``python main.py``)::

    docker compose up --build  # aus dem infra/-Ordner heraus
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from fastapi import FastAPI

from config import get_settings
from crypto.registry import CryptoRegistry
from crypto.registry_init import init_crypto_registry
from logging_config import get_logger, setup_logging
from routers import health

if TYPE_CHECKING:
    from collections.abc import AsyncIterator


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Initialisiere Logging und CryptoRegistry beim App-Start."""
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

    # CryptoRegistry per Config befuellen. PQC-25 ersetzt die Placeholder
    # durch echte liboqs-Adapter.
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

    # State im App-Lifecycle ablegen, damit nachfolgende Stories (CRY-2 Facade,
    # AUT/TOK-Stories) den gleichen Singleton verwenden koennen.
    app.state.settings = settings
    app.state.crypto_registry = registry
    try:
        yield
    finally:
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
    app.include_router(health.router)
    return app


app = create_app()


def _run() -> None:
    """Entry-Point fuer ``python main.py`` und Docker-CMD.

    Liest Settings.host und Settings.port und startet uvicorn programmatisch.
    Lokale Dev mit Hot-Reload nutzt weiterhin ``uvicorn main:app --reload``,
    weil --reload einen Worker-Subprozess startet und nicht zur programmatischen
    API passt.
    """
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        log_config=None,  # structlog uebernimmt das Logging via lifespan
    )


if __name__ == "__main__":
    _run()
