"""Tests fuer services/session_service.py.

Story: PQC-48 SES-3 (FR-Session-3).

Verwendet fakeredis als Redis-Mock (analog test_oidc_state_service.py).
Pytest-Integration-Tests mit echtem Redis sind als F-067-Polish optional.
"""

from __future__ import annotations

import asyncio
import os

import pytest

fakeredis_aio = pytest.importorskip(
    "fakeredis.aioredis",
    reason="fakeredis not installed in this environment",
)

from services.session_service import (  # noqa: E402
    SessionNotFoundError,
    SessionRecord,
    SessionService,
)

_TEST_TTL = 60
_TEST_USER_ID = "user-test-1"
_TEST_KEM_ALG = "ML-KEM-768"


@pytest.fixture
def session_key() -> bytes:
    """Stabiler 32-Byte session_key fuer Tests."""
    return os.urandom(32)


@pytest.fixture
def fake_redis():
    """Frische fakeredis-Instanz pro Test."""
    return fakeredis_aio.FakeRedis()


@pytest.fixture
def service(fake_redis) -> SessionService:
    return SessionService(redis_client=fake_redis, ttl_seconds=_TEST_TTL)


# --- Konstruktor-Validierung ---


def test_session_service_rejects_non_positive_ttl(fake_redis) -> None:
    with pytest.raises(ValueError, match="ttl_seconds"):
        SessionService(redis_client=fake_redis, ttl_seconds=0)
    with pytest.raises(ValueError, match="ttl_seconds"):
        SessionService(redis_client=fake_redis, ttl_seconds=-1)


def test_session_service_exposes_ttl(service: SessionService) -> None:
    assert service.ttl_seconds == _TEST_TTL


# --- Create + Get Roundtrip ---


def test_create_returns_session_id_and_record(service: SessionService, session_key: bytes) -> None:
    sid, rec = asyncio.run(
        service.create(user_id=_TEST_USER_ID, kem_alg=_TEST_KEM_ALG, session_key=session_key)
    )
    assert isinstance(sid, str)
    assert len(sid) == 22  # 16 Byte urlsafe-base64 no-pad
    assert isinstance(rec, SessionRecord)
    assert rec.user_id == _TEST_USER_ID
    assert rec.kem_alg == _TEST_KEM_ALG
    assert rec.session_key == session_key
    assert rec.expires_at - rec.created_at == _TEST_TTL


def test_create_yields_unique_session_ids(service: SessionService, session_key: bytes) -> None:
    sid1, _ = asyncio.run(
        service.create(user_id=_TEST_USER_ID, kem_alg=_TEST_KEM_ALG, session_key=session_key)
    )
    sid2, _ = asyncio.run(
        service.create(user_id=_TEST_USER_ID, kem_alg=_TEST_KEM_ALG, session_key=session_key)
    )
    assert sid1 != sid2


def test_get_after_create_returns_same_record(service: SessionService, session_key: bytes) -> None:
    sid, rec_in = asyncio.run(
        service.create(user_id=_TEST_USER_ID, kem_alg=_TEST_KEM_ALG, session_key=session_key)
    )
    rec_out = asyncio.run(service.get(sid))
    assert rec_out.user_id == rec_in.user_id
    assert rec_out.kem_alg == rec_in.kem_alg
    assert rec_out.session_key == rec_in.session_key
    assert rec_out.created_at == rec_in.created_at
    assert rec_out.expires_at == rec_in.expires_at


def test_get_unknown_session_id_raises(service: SessionService) -> None:
    with pytest.raises(SessionNotFoundError):
        asyncio.run(service.get("not-a-real-session-id"))


# --- TTL + Refresh ---


def test_create_sets_ttl_on_redis(service: SessionService, fake_redis, session_key: bytes) -> None:
    sid, _ = asyncio.run(
        service.create(user_id=_TEST_USER_ID, kem_alg=_TEST_KEM_ALG, session_key=session_key)
    )

    async def _ttl():
        return await fake_redis.ttl(f"session:{sid}")

    ttl = asyncio.run(_ttl())
    # fakeredis liefert int >= 0 oder -1 (kein TTL) / -2 (key fehlt). Wir
    # erwarten einen Wert in 1..ttl_seconds (kann minimal kleiner sein wegen
    # Round-Trip-Zeit).
    assert 0 < ttl <= _TEST_TTL


def test_refresh_extends_ttl(service: SessionService, fake_redis, session_key: bytes) -> None:
    sid, _ = asyncio.run(
        service.create(user_id=_TEST_USER_ID, kem_alg=_TEST_KEM_ALG, session_key=session_key)
    )

    async def _force_short_ttl():
        await fake_redis.expire(f"session:{sid}", 5)

    asyncio.run(_force_short_ttl())

    async def _ttl():
        return await fake_redis.ttl(f"session:{sid}")

    assert asyncio.run(_ttl()) <= 5

    asyncio.run(service.refresh(sid))
    new_ttl = asyncio.run(_ttl())
    # Nach refresh ist TTL wieder ~ttl_seconds
    assert new_ttl > 5
    assert new_ttl <= _TEST_TTL


def test_refresh_unknown_session_id_raises(service: SessionService) -> None:
    with pytest.raises(SessionNotFoundError):
        asyncio.run(service.refresh("not-real"))


# --- Invalidate ---


def test_invalidate_removes_session(service: SessionService, session_key: bytes) -> None:
    sid, _ = asyncio.run(
        service.create(user_id=_TEST_USER_ID, kem_alg=_TEST_KEM_ALG, session_key=session_key)
    )
    deleted = asyncio.run(service.invalidate(sid))
    assert deleted is True

    with pytest.raises(SessionNotFoundError):
        asyncio.run(service.get(sid))


def test_invalidate_unknown_is_idempotent(service: SessionService) -> None:
    deleted = asyncio.run(service.invalidate("never-existed"))
    assert deleted is False


# --- Serialization-Roundtrip mit Binary session_key ---


def test_session_key_with_binary_bytes_roundtrips(service: SessionService) -> None:
    """Echte Binary-Bytes (auch null-bytes) muessen durch base64url-Roundtrip OK sein."""
    binary_key = bytes(range(32))  # 0x00..0x1F, enthaelt Null-Byte
    sid, _ = asyncio.run(
        service.create(user_id=_TEST_USER_ID, kem_alg=_TEST_KEM_ALG, session_key=binary_key)
    )
    rec = asyncio.run(service.get(sid))
    assert rec.session_key == binary_key
