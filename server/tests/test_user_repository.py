"""Tests fuer db/repositories/user_repository.py.

Story: PQC-28 (AUT-1) AC-3, AC-5.

Tests nutzen in-memory SQLite (``sqlite+aiosqlite:///:memory:``) plus
async_sessionmaker. Pro Test eine frische DB damit Tests isoliert sind.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from db.repositories import (
    UserAlreadyExistsError,
    UserRepository,
    UserRepositoryError,
)
from db.repositories.user_repository import InvalidUserDataError
from models import Base

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession


@pytest_asyncio.fixture
async def engine() -> AsyncEngine:
    """In-memory async SQLite-Engine, frische Tabellen pro Test."""
    eng = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    await eng.dispose()


@pytest_asyncio.fixture
async def session(engine: AsyncEngine) -> AsyncSession:
    sf = async_sessionmaker(bind=engine, expire_on_commit=False)
    async with sf() as s:
        yield s


@pytest_asyncio.fixture
async def repo(session: AsyncSession) -> UserRepository:
    return UserRepository(session)


# ---------------------------------------------------------------------------
# create (AC-3, AC-5)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_local_user(repo: UserRepository) -> None:
    u = await repo.create(
        email="alice@example.com",
        auth_method="local",
        password_hash="$argon2id$v=19$m=8192,t=1,p=1$AAAA$BBBB",
    )
    assert u.id  # UUIDv4 generiert
    assert len(u.id) == 36
    assert u.email == "alice@example.com"
    assert u.auth_method == "local"
    assert u.password_hash is not None
    assert u.external_sub is None
    assert u.created_at is not None
    assert u.updated_at is not None


@pytest.mark.asyncio
async def test_create_lowercase_normalizes_email(repo: UserRepository) -> None:
    u = await repo.create(
        email="  Alice@EXAMPLE.com  ",
        auth_method="local",
        password_hash="hash",
    )
    assert u.email == "alice@example.com"


@pytest.mark.asyncio
async def test_create_federated_user(repo: UserRepository) -> None:
    u = await repo.create(
        email="bob@google.example",
        auth_method="google",
        external_sub="google|112233",
    )
    assert u.auth_method == "google"
    assert u.password_hash is None
    assert u.external_sub == "google|112233"


@pytest.mark.asyncio
async def test_create_duplicate_email_raises(repo: UserRepository) -> None:
    await repo.create(email="dup@example.com", auth_method="local", password_hash="h1")
    with pytest.raises(UserAlreadyExistsError, match="already exists"):
        await repo.create(
            email="dup@example.com", auth_method="local", password_hash="h2"
        )


@pytest.mark.asyncio
async def test_create_duplicate_email_case_insensitive(repo: UserRepository) -> None:
    await repo.create(email="dup@example.com", auth_method="local", password_hash="h1")
    with pytest.raises(UserAlreadyExistsError):
        await repo.create(email="DUP@Example.COM", auth_method="local", password_hash="h2")


@pytest.mark.asyncio
async def test_create_local_without_password_hash_raises(repo: UserRepository) -> None:
    with pytest.raises(InvalidUserDataError, match="password_hash"):
        await repo.create(email="x@example.com", auth_method="local")


@pytest.mark.asyncio
async def test_create_federated_with_password_hash_raises(repo: UserRepository) -> None:
    with pytest.raises(InvalidUserDataError, match="must NOT have password_hash"):
        await repo.create(
            email="x@example.com",
            auth_method="google",
            external_sub="google|x",
            password_hash="hash",
        )


@pytest.mark.asyncio
async def test_create_federated_without_external_sub_raises(repo: UserRepository) -> None:
    with pytest.raises(InvalidUserDataError, match="external_sub"):
        await repo.create(email="x@example.com", auth_method="google")


@pytest.mark.asyncio
async def test_create_unsupported_auth_method_raises(repo: UserRepository) -> None:
    with pytest.raises(InvalidUserDataError, match="unsupported auth_method"):
        await repo.create(email="x@example.com", auth_method="facebook")


@pytest.mark.asyncio
async def test_create_empty_email_raises(repo: UserRepository) -> None:
    with pytest.raises(InvalidUserDataError, match="email"):
        await repo.create(email="", auth_method="local", password_hash="h")


# ---------------------------------------------------------------------------
# find_by_email (AC-5)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_find_by_email_returns_user(repo: UserRepository) -> None:
    u = await repo.create(
        email="findme@example.com", auth_method="local", password_hash="h"
    )
    found = await repo.find_by_email("findme@example.com")
    assert found is not None
    assert found.id == u.id


@pytest.mark.asyncio
async def test_find_by_email_case_insensitive(repo: UserRepository) -> None:
    await repo.create(email="case@example.com", auth_method="local", password_hash="h")
    assert await repo.find_by_email("CASE@example.com") is not None
    assert await repo.find_by_email("Case@Example.COM") is not None


@pytest.mark.asyncio
async def test_find_by_email_returns_none_when_missing(repo: UserRepository) -> None:
    assert await repo.find_by_email("nobody@example.com") is None


@pytest.mark.asyncio
async def test_find_by_email_empty_returns_none(repo: UserRepository) -> None:
    assert await repo.find_by_email("") is None


# ---------------------------------------------------------------------------
# find_by_id
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_find_by_id_returns_user(repo: UserRepository) -> None:
    u = await repo.create(
        email="id@example.com", auth_method="local", password_hash="h"
    )
    found = await repo.find_by_id(u.id)
    assert found is not None
    assert found.email == "id@example.com"


@pytest.mark.asyncio
async def test_find_by_id_missing_returns_none(repo: UserRepository) -> None:
    assert await repo.find_by_id("00000000-0000-0000-0000-000000000000") is None


@pytest.mark.asyncio
async def test_find_by_id_empty_returns_none(repo: UserRepository) -> None:
    assert await repo.find_by_id("") is None


# ---------------------------------------------------------------------------
# find_by_external (BRK-4-Vorbereitung)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_find_by_external_returns_user(repo: UserRepository) -> None:
    u = await repo.create(
        email="ext@example.com", auth_method="google", external_sub="google|abc"
    )
    found = await repo.find_by_external("google", "google|abc")
    assert found is not None
    assert found.id == u.id


@pytest.mark.asyncio
async def test_find_by_external_wrong_provider_returns_none(repo: UserRepository) -> None:
    await repo.create(
        email="ext@example.com", auth_method="google", external_sub="google|abc"
    )
    assert await repo.find_by_external("microsoft", "google|abc") is None


@pytest.mark.asyncio
async def test_find_by_external_empty_returns_none(repo: UserRepository) -> None:
    assert await repo.find_by_external("google", "") is None
    assert await repo.find_by_external("", "google|abc") is None


# ---------------------------------------------------------------------------
# Inheritance
# ---------------------------------------------------------------------------


def test_user_already_exists_is_user_repository_error() -> None:
    assert issubclass(UserAlreadyExistsError, UserRepositoryError)


def test_invalid_user_data_is_user_repository_error() -> None:
    assert issubclass(InvalidUserDataError, UserRepositoryError)
