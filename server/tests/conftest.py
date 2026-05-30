"""Pytest Shared Fixtures fuer den rib-pqc Auth-Service.

Story: PQC-63 QUA-1 (Pytest-Setup).

**Scope-Strategie (Hybrid):**

- Shared Fixtures die in mehreren Test-Modulen verwendet werden landen hier
  (z.B. ``fast_hasher``, ``async_engine``, ``session_factory``, ``client_factory``).
- Test-spezifische Fixtures (z.B. ``app_with_user`` in test_auth_router.py)
  bleiben in der jeweiligen Test-Datei, weil sie eine spezifische Wiring-
  Variante beschreiben die nur dort gebraucht wird.
- Top-Level-Code setzt Environment-Variablen damit das Module-level
  ``Limiter``-Singleton aus ``middleware.rate_limit`` mit ``memory://`` statt
  Redis instantiiert wird (sonst crasht der Import in Sandbox-Umgebungen
  ohne Redis-Service).
"""

from __future__ import annotations

import os

# ---------------------------------------------------------------------------
# Test-Environment-Defaults (Top-Level, MUSS vor allen App-Imports laufen)
# ---------------------------------------------------------------------------
#
# Module-level Limiter in middleware/rate_limit.py wird beim ersten Import
# aus den Settings instantiiert. In Sandbox- und CI-Umgebungen gibt es
# keinen Redis-Service, daher zwingen wir hier Memory-Storage und
# disabled-Limit BEVOR irgendein Test-Modul middleware importiert.
#
# Diese Zeilen muessen am Top-Level stehen (nicht in einer Fixture), weil
# pytest test-files vor Fixture-Setup importiert und Module-Level-Code dann
# bereits laeuft.

os.environ.setdefault("RIB_SECURITY__RATE_LIMIT__STORAGE_URI", "memory://")
os.environ.setdefault("RIB_SECURITY__RATE_LIMIT__ENABLED", "false")
os.environ.setdefault("RIB_ENVIRONMENT", "dev")


from collections.abc import AsyncIterator
from typing import TYPE_CHECKING

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from fastapi import FastAPI
    from sqlalchemy.ext.asyncio import AsyncEngine

    from auth.password import PasswordHasher


# ---------------------------------------------------------------------------
# DB-Fixtures: Async-Engine, Session-Factory, Session
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def async_engine() -> AsyncIterator[AsyncEngine]:
    """Liefert eine frische SQLite-In-Memory-Async-Engine pro Test.

    Schema wird via ``Base.metadata.create_all`` initialisiert. Per Test
    eine eigene Engine, damit Tests voll isoliert sind und keine State-
    Lecks zwischen Test-Funktionen haben.
    """
    from models import Base

    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    try:
        yield engine
    finally:
        await engine.dispose()


@pytest_asyncio.fixture
async def session_factory(
    async_engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    """Liefert eine async_sessionmaker an die bestehende Engine gebunden."""
    return async_sessionmaker(bind=async_engine, expire_on_commit=False)


@pytest_asyncio.fixture
async def async_session(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncIterator[AsyncSession]:
    """Liefert eine frische AsyncSession pro Test, sauber geschlossen."""
    async with session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


# ---------------------------------------------------------------------------
# Auth-Fixtures: Fast-Argon2-Hasher fuer Test-Speed
# ---------------------------------------------------------------------------


@pytest.fixture
def fast_hasher() -> PasswordHasher:
    """Argon2id-Hasher mit niedrigen Cost-Parametern fuer Test-Speed.

    Production-Defaults (m=64MB, t=3, p=4) brauchen ~50ms pro hash. Fuer
    Test-Suite-Geschwindigkeit setzen wir m=8MB, t=1, p=1, was ungefaehr
    5ms pro Hash bedeutet. Tests pruefen Korrektheit, nicht Brute-Force-
    Resistenz.
    """
    from auth.password import PasswordHasher
    from config import Argon2Config

    return PasswordHasher(
        Argon2Config(memory_cost_kb=8192, time_cost=1, parallelism=1),
    )


# ---------------------------------------------------------------------------
# Helper-Fixture: Generic FastAPI-TestClient-Factory
# ---------------------------------------------------------------------------


@pytest.fixture
def client_factory() -> Callable[[FastAPI], TestClient]:
    """Helper-Factory zum Bauen eines TestClient gegen eine beliebige App.

    Verwendung in Tests, die eine selbst-gebaute App haben::

        def test_xyz(client_factory):
            app = build_my_test_app()
            client = client_factory(app)
            r = client.get("/...")

    Fuer Tests die haeufig dieselbe App brauchen ist eine dedizierte Fixture
    im Test-Modul vorzuziehen (siehe z.B. ``test_auth_router.py:client``).
    """
    return TestClient
