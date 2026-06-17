"""Tests fuer db/repositories/user_identity_repository.py.

Story: PQC-39 BRK-4.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from auth.password import PasswordHasher
from db.repositories import (
    IdentityAlreadyExistsError,
    InvalidIdentityDataError,
    UserIdentityRepository,
    UserRepository,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def _create_local_user(
    session: AsyncSession,
    hasher: PasswordHasher,
    email: str = "alice@example.com",
) -> str:
    repo = UserRepository(session)
    user = await repo.create(
        email=email,
        auth_method="local",
        password_hash=hasher.hash("Secret-123!"),
    )
    return user.id


async def test_create_identity_happy_path(
    async_session: AsyncSession,
    fast_hasher: PasswordHasher,
) -> None:
    user_id = await _create_local_user(async_session, fast_hasher)
    repo = UserIdentityRepository(async_session)
    identity = await repo.create(
        user_id=user_id,
        auth_method="google",
        external_sub="sub-1234",
    )
    assert identity.user_id == user_id
    assert identity.auth_method == "google"
    assert identity.external_sub == "sub-1234"


async def test_find_by_external_hit(
    async_session: AsyncSession,
    fast_hasher: PasswordHasher,
) -> None:
    user_id = await _create_local_user(async_session, fast_hasher)
    repo = UserIdentityRepository(async_session)
    await repo.create(user_id=user_id, auth_method="microsoft", external_sub="oid-1")
    found = await repo.find_by_external(auth_method="microsoft", external_sub="oid-1")
    assert found is not None
    assert found.user_id == user_id


async def test_find_by_external_miss(
    async_session: AsyncSession,
) -> None:
    repo = UserIdentityRepository(async_session)
    found = await repo.find_by_external(auth_method="google", external_sub="nope")
    assert found is None


async def test_create_duplicate_external_raises(
    async_session: AsyncSession,
    fast_hasher: PasswordHasher,
) -> None:
    user_id = await _create_local_user(async_session, fast_hasher)
    repo = UserIdentityRepository(async_session)
    await repo.create(user_id=user_id, auth_method="google", external_sub="dup-sub")
    with pytest.raises(IdentityAlreadyExistsError):
        await repo.create(user_id=user_id, auth_method="google", external_sub="dup-sub")


async def test_create_invalid_auth_method_raises(
    async_session: AsyncSession,
    fast_hasher: PasswordHasher,
) -> None:
    user_id = await _create_local_user(async_session, fast_hasher)
    repo = UserIdentityRepository(async_session)
    with pytest.raises(InvalidIdentityDataError):
        await repo.create(user_id=user_id, auth_method="apple", external_sub="x")


async def test_create_empty_external_sub_raises(
    async_session: AsyncSession,
    fast_hasher: PasswordHasher,
) -> None:
    user_id = await _create_local_user(async_session, fast_hasher)
    repo = UserIdentityRepository(async_session)
    with pytest.raises(InvalidIdentityDataError):
        await repo.create(user_id=user_id, auth_method="google", external_sub="")


async def test_list_for_user_returns_all_identities(
    async_session: AsyncSession,
    fast_hasher: PasswordHasher,
) -> None:
    user_id = await _create_local_user(async_session, fast_hasher)
    repo = UserIdentityRepository(async_session)
    await repo.create(user_id=user_id, auth_method="google", external_sub="g-1")
    await repo.create(user_id=user_id, auth_method="microsoft", external_sub="m-1")
    identities = await repo.list_for_user(user_id)
    assert len(identities) == 2
    methods = {i.auth_method for i in identities}
    assert methods == {"google", "microsoft"}


async def test_list_for_user_unknown_returns_empty(async_session: AsyncSession) -> None:
    repo = UserIdentityRepository(async_session)
    identities = await repo.list_for_user("non-existent-user-id")
    assert identities == []
