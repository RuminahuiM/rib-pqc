"""Tests fuer services/nonce_tracker.RedisNonceTracker.

Story: PQC-53 (DCH-4).

Test-Strategie:
- ``fakeredis.aioredis.FakeRedis`` als Backend (analog test_session_service.py).
- check_and_register: erste-Verwendung True, zweite-Verwendung False.
- TTL: Eintrag bekommt EX gesetzt, fakeredis honoriert das (TTL inspizierbar).
- Race-Free: asyncio.gather von zwei concurrent check_and_register mit
  gleicher (session_id, nonce) liefert genau ein True.
- Isolation: zwei verschiedene session_ids teilen sich keine Tracker-Slots.
- Legacy-API: has_seen + record bleiben funktional.
"""

from __future__ import annotations

import asyncio

import pytest

fakeredis_aio = pytest.importorskip(
    "fakeredis.aioredis",
    reason="fakeredis not installed",
)

from services.nonce_tracker import RedisNonceTracker  # noqa: E402


@pytest.fixture
def redis_client() -> object:
    return fakeredis_aio.FakeRedis()


@pytest.fixture
def tracker(redis_client: object) -> RedisNonceTracker:
    return RedisNonceTracker(redis_client=redis_client, ttl_seconds=900)


@pytest.mark.asyncio
async def test_check_and_register_first_use_returns_true(
    tracker: RedisNonceTracker,
) -> None:
    """Detail-AC 2: erste Verwendung -> True."""
    result = await tracker.check_and_register(
        session_id="session-aaa",
        nonce=b"\x01" * 12,
    )
    assert result is True


@pytest.mark.asyncio
async def test_check_and_register_replay_returns_false(
    tracker: RedisNonceTracker,
) -> None:
    """Detail-AC 2: zweite Verwendung -> False (Replay-Trigger)."""
    nonce = b"\x02" * 12
    first = await tracker.check_and_register(session_id="session-aaa", nonce=nonce)
    second = await tracker.check_and_register(session_id="session-aaa", nonce=nonce)
    assert first is True
    assert second is False


@pytest.mark.asyncio
async def test_different_sessions_isolated(tracker: RedisNonceTracker) -> None:
    """Gleiche Nonce in anderer Session ist kein Replay."""
    nonce = b"\x03" * 12
    a = await tracker.check_and_register(session_id="session-aaa", nonce=nonce)
    b = await tracker.check_and_register(session_id="session-bbb", nonce=nonce)
    assert a is True
    assert b is True


@pytest.mark.asyncio
async def test_check_and_register_is_atomic_under_concurrency(
    tracker: RedisNonceTracker,
) -> None:
    """Race-Test (Detail-AC 2): zwei parallele check_and_register mit gleicher
    (session_id, nonce) - genau einer gewinnt.

    fakeredis ist nicht echt-parallel, aber gather erzwingt non-sequential
    Scheduling. Bei echtem Redis ist SET NX EX atomar an einem Single-Thread-
    Server, derselbe Garantie-Level.
    """
    nonce = b"\x04" * 12
    session_id = "session-race"

    results = await asyncio.gather(
        tracker.check_and_register(session_id=session_id, nonce=nonce),
        tracker.check_and_register(session_id=session_id, nonce=nonce),
    )
    assert sorted(results) == [False, True]


@pytest.mark.asyncio
async def test_check_and_register_sets_ttl(
    redis_client: object,
    tracker: RedisNonceTracker,
) -> None:
    """Detail-AC 3: TTL wird gesetzt (positiv, nahe Konfig-Wert)."""
    nonce = b"\x05" * 12
    session_id = "session-ttl"
    await tracker.check_and_register(session_id=session_id, nonce=nonce)
    # Direkt am Redis nachschauen: TTL pro Key.
    ttl = await redis_client.ttl(f"nonce:{session_id}:BQUFBQUFBQUFBQUF")
    assert 0 < ttl <= 900


@pytest.mark.asyncio
async def test_constructor_rejects_zero_ttl(redis_client: object) -> None:
    """ttl_seconds <= 0 ist invalid."""
    with pytest.raises(ValueError, match="ttl_seconds must be positive"):
        RedisNonceTracker(redis_client=redis_client, ttl_seconds=0)
    with pytest.raises(ValueError, match="ttl_seconds must be positive"):
        RedisNonceTracker(redis_client=redis_client, ttl_seconds=-1)


@pytest.mark.asyncio
async def test_legacy_has_seen_record_works(tracker: RedisNonceTracker) -> None:
    """Legacy-API: has_seen + record bleiben funktional (Backward-Compat)."""
    nonce = b"\x06" * 12
    session_id = "session-legacy"
    assert await tracker.has_seen(session_id=session_id, nonce=nonce) is False
    await tracker.record(session_id=session_id, nonce=nonce)
    assert await tracker.has_seen(session_id=session_id, nonce=nonce) is True


@pytest.mark.asyncio
async def test_record_overlaps_with_check_and_register(
    tracker: RedisNonceTracker,
) -> None:
    """Wenn legacy record() schon gelaufen ist, returnt check_and_register False."""
    nonce = b"\x07" * 12
    session_id = "session-mix"
    await tracker.record(session_id=session_id, nonce=nonce)
    result = await tracker.check_and_register(session_id=session_id, nonce=nonce)
    assert result is False


def test_ttl_seconds_property() -> None:
    """ttl_seconds-Property liefert den Konfig-Wert."""
    tracker = RedisNonceTracker(
        redis_client=fakeredis_aio.FakeRedis(),
        ttl_seconds=600,
    )
    assert tracker.ttl_seconds == 600
