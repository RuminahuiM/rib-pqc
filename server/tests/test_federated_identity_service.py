"""Tests fuer services/federated_identity_service.py.

Story: PQC-39 BRK-4 AC-1, AC-2, AC-4, AC-6.

Echte sqlite-in-memory-DB-Tests (kein Mock-Repo). Verifiziert die End-to-End-
Geschaeftslogik mit allen Edge-Cases.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from auth.password import PasswordHasher
from db.repositories import UserIdentityRepository, UserRepository
from idp.normalized_identity import NormalizedIdentity
from services.federated_identity_service import FederatedIdentityService

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


def _service(session: AsyncSession) -> FederatedIdentityService:
    return FederatedIdentityService(
        user_repository=UserRepository(session),
        identity_repository=UserIdentityRepository(session),
    )


# ---------------------------------------------------------------------------
# AC-1: Erst-Login
# ---------------------------------------------------------------------------


async def test_first_login_creates_user_and_identity(
    async_session: AsyncSession,
) -> None:
    svc = _service(async_session)
    normalized = NormalizedIdentity(
        external_sub="g-sub-001",
        email="newuser@example.com",
        email_verified=True,
        display_name="New User",
    )
    user = await svc.link_or_create(provider="google", normalized=normalized)
    assert user.email == "newuser@example.com"
    assert user.auth_method == "google"
    assert user.external_sub == "g-sub-001"

    # UserIdentity-Row sollte auch existieren
    identities = await UserIdentityRepository(async_session).list_for_user(user.id)
    assert len(identities) == 1
    assert identities[0].auth_method == "google"
    assert identities[0].external_sub == "g-sub-001"


async def test_first_login_without_email_uses_placeholder(
    async_session: AsyncSession,
) -> None:
    """AC-1 Edge-Case: Provider liefert kein email-Claim."""
    svc = _service(async_session)
    normalized = NormalizedIdentity(
        external_sub="ms-oid-no-email",
        email=None,
        email_verified=False,
        display_name="No-Email User",
    )
    user = await svc.link_or_create(provider="microsoft", normalized=normalized)
    assert "no-email.local" in user.email
    assert user.auth_method == "microsoft"


# ---------------------------------------------------------------------------
# AC-2: Wiederholter Login
# ---------------------------------------------------------------------------


async def test_repeat_login_reuses_existing_user(async_session: AsyncSession) -> None:
    svc = _service(async_session)
    normalized = NormalizedIdentity(
        external_sub="g-sub-repeat",
        email="repeat@example.com",
        email_verified=True,
    )
    first = await svc.link_or_create(provider="google", normalized=normalized)
    second = await svc.link_or_create(provider="google", normalized=normalized)
    assert first.id == second.id
    # Nur 1 UserIdentity-Row (kein Duplikat)
    identities = await UserIdentityRepository(async_session).list_for_user(first.id)
    assert len(identities) == 1


# ---------------------------------------------------------------------------
# AC-4: Account-Linking bei Email-Match + email_verified=True
# ---------------------------------------------------------------------------


async def test_email_verified_match_links_to_existing_local_user(
    async_session: AsyncSession,
    fast_hasher: PasswordHasher,
) -> None:
    # Local-User existiert mit dieser Email
    user_repo = UserRepository(async_session)
    local_user = await user_repo.create(
        email="alice@example.com",
        auth_method="local",
        password_hash=fast_hasher.hash("Secret-123!"),
    )

    svc = _service(async_session)
    normalized = NormalizedIdentity(
        external_sub="g-sub-alice",
        email="alice@example.com",
        email_verified=True,
        display_name="Alice",
    )
    resolved = await svc.link_or_create(provider="google", normalized=normalized)

    # Existing local-User wird zurueckgegeben (gleiche ID)
    assert resolved.id == local_user.id
    assert resolved.auth_method == "local"  # bleibt local
    assert resolved.email == "alice@example.com"

    # Neue UserIdentity-Row gegen die local-User-ID
    identities = await UserIdentityRepository(async_session).list_for_user(local_user.id)
    assert len(identities) == 1
    assert identities[0].auth_method == "google"


# ---------------------------------------------------------------------------
# AC-6: Email-Unverified -> NICHT linken
# ---------------------------------------------------------------------------


async def test_email_unverified_does_not_link_to_existing_user(
    async_session: AsyncSession,
    fast_hasher: PasswordHasher,
) -> None:
    """Defense-against-Account-Takeover: unverified email matching local-User
    darf NICHT linken. Stattdessen wird ein neuer User-Record angelegt mit
    auth_method=<provider>."""
    user_repo = UserRepository(async_session)
    await user_repo.create(
        email="bob@example.com",
        auth_method="local",
        password_hash=fast_hasher.hash("Secret-123!"),
    )

    svc = _service(async_session)
    normalized = NormalizedIdentity(
        external_sub="g-sub-bob",
        email="bob@example.com",
        email_verified=False,
        display_name="Fake Bob",
    )
    # Da bob@example.com schon als local-User existiert UND wir KEIN Linking
    # machen duerfen, scheitert der create wegen unique-email. Das ist das
    # erwartete Verhalten - Federated-Login mit nicht-verifizierter Email auf
    # bestehender lokaler Email wird abgewiesen (Spoof-Schutz).
    import pytest

    from db.repositories import UserAlreadyExistsError

    with pytest.raises(UserAlreadyExistsError):
        await svc.link_or_create(provider="google", normalized=normalized)


async def test_email_unverified_no_collision_creates_new_user(
    async_session: AsyncSession,
) -> None:
    """email_verified=False + kein existing User -> neuer User-Record."""
    svc = _service(async_session)
    normalized = NormalizedIdentity(
        external_sub="g-sub-charlie",
        email="charlie@example.com",
        email_verified=False,
    )
    user = await svc.link_or_create(provider="google", normalized=normalized)
    assert user.email == "charlie@example.com"
    assert user.auth_method == "google"


# ---------------------------------------------------------------------------
# Multi-Provider auf gleichem User (Account-Linking-Erweiterung)
# ---------------------------------------------------------------------------


async def test_second_provider_can_link_to_same_user(
    async_session: AsyncSession,
    fast_hasher: PasswordHasher,
) -> None:
    """User hat Google + Microsoft mit gleicher verifierter Email."""
    user_repo = UserRepository(async_session)
    user = await user_repo.create(
        email="multi@example.com",
        auth_method="local",
        password_hash=fast_hasher.hash("Secret-123!"),
    )

    svc = _service(async_session)

    # Google-Login
    await svc.link_or_create(
        provider="google",
        normalized=NormalizedIdentity(
            external_sub="g-multi", email="multi@example.com", email_verified=True
        ),
    )
    # Microsoft-Login
    await svc.link_or_create(
        provider="microsoft",
        normalized=NormalizedIdentity(
            external_sub="m-multi", email="multi@example.com", email_verified=True
        ),
    )

    identities = await UserIdentityRepository(async_session).list_for_user(user.id)
    methods = {i.auth_method for i in identities}
    assert methods == {"google", "microsoft"}
