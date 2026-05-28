"""Async SQLAlchemy 2.0 Engine plus Session-Factory.

Story: PQC-28 (AUT-1) AC-3.

Im Lifespan-Hook (server/main.py) wird beim App-Start:
1. ``create_async_engine_from_settings(settings)`` aufgerufen
2. Engine in ``app.state.db_engine`` abgelegt
3. ``async_sessionmaker`` gegen die Engine erzeugt und in ``app.state.session_factory`` abgelegt

In FastAPI-Endpoints (kommt erst mit PQC-30 AUT-3) wird ``get_session()`` als
Dependency injiziert, das pro Request eine Session aufmacht und im Finally
wieder schliesst.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from logging_config import get_logger

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from config import DatabaseConfig

_logger = get_logger("rib_pqc.db")


def create_engine_from_config(db_config: DatabaseConfig) -> AsyncEngine:
    """Erstellt einen Async-Engine gemaess Settings.

    Args:
        db_config: ``settings.database`` mit ``async_url`` und ``echo``.

    Returns:
        AsyncEngine, bereit fuer ``async_sessionmaker`` und Endpoint-Use.
    """
    engine = create_async_engine(
        db_config.async_url,
        echo=db_config.echo,
        future=True,
    )
    _logger.info(
        "db.engine.created",
        url=_redact_url(db_config.async_url),
        echo=db_config.echo,
    )
    return engine


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Erstellt eine ``async_sessionmaker`` gegen den gegebenen Engine.

    Das Factory-Pattern: pro Request rufen Endpoints ``session_factory()`` und
    haben damit eine frische AsyncSession. Engine bleibt der Singleton.
    """
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


async def session_dependency_factory(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncIterator[AsyncSession]:
    """Async-Generator fuer FastAPI-Depends.

    Verwendung in Endpoints (kommt mit PQC-30 AUT-3):

        async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
            async for session in session_dependency_factory(request.app.state.session_factory):
                yield session

    Pro Request eine Session, commit/rollback wird vom Endpoint-Code gesteuert.
    """
    async with session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


def _redact_url(url: str) -> str:
    """Entfernt Passwort-Teile aus DB-URLs fuer's Logging.

    Sqlite-URLs haben keine Credentials, aber bei Postgres-Migration relevant.
    """
    if "@" not in url:
        return url
    # Format: dialect+driver://user:password@host/db
    scheme_sep = url.find("://")
    if scheme_sep == -1:
        return url
    scheme = url[: scheme_sep + 3]
    rest = url[scheme_sep + 3 :]
    at_pos = rest.find("@")
    if at_pos == -1:
        return url
    return f"{scheme}***@{rest[at_pos + 1 :]}"
