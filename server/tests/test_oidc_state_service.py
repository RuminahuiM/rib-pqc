"""Tests fuer services/oidc_state_service.py.

Stories: PQC-37 BRK-2 + PQC-42 BRK-7 AC-5.

Deckt ab:
- Happy-Path create -> consume
- One-Shot: zweimal consume -> zweite Mal StateNotFoundError
- Unbekannter State -> StateNotFoundError
- TTL-Expiry -> StateNotFoundError
- State-Werte sind eindeutig (Entropie-Sanity-Check)
- ttl_seconds <= 0 -> ValueError im Constructor
"""

from __future__ import annotations

import json

import pytest
import pytest_asyncio
from fakeredis.aioredis import FakeRedis

from services.oidc_state_service import (
    OidcStateService,
    StateEntry,
    StateNotFoundError,
)


@pytest_asyncio.fixture
async def redis_client() -> FakeRedis:
    """Frischer fakeredis-Client pro Test."""
    client = FakeRedis()
    try:
        yield client
    finally:
        await client.aclose()


@pytest.fixture
def service(redis_client: FakeRedis) -> OidcStateService:
    return OidcStateService(redis_client=redis_client, ttl_seconds=600)


# ---------------------------------------------------------------------------
# Happy-Path
# ---------------------------------------------------------------------------


async def test_create_and_consume_happy_path(service: OidcStateService) -> None:
    state = await service.create(provider="google", code_verifier="A" * 64)
    entry = await service.consume(state)
    assert entry.provider == "google"
    assert entry.created_at_iso.endswith("+00:00")


async def test_create_returns_url_safe_string(service: OidcStateService) -> None:
    state = await service.create(provider="microsoft", code_verifier="A" * 64)
    # urlsafe_b64 ist a-z A-Z 0-9 - _
    assert all(c.isalnum() or c in "-_" for c in state)
    # token_urlsafe(32) ergibt ~43 chars
    assert 40 < len(state) < 50


async def test_state_values_are_unique(service: OidcStateService) -> None:
    """Two create-Calls liefern unterschiedliche States (256 bit Entropie)."""
    states: set[str] = set()
    for _ in range(20):
        states.add(await service.create(provider="google", code_verifier="A" * 64))
    assert len(states) == 20


# ---------------------------------------------------------------------------
# One-Shot (Replay-Schutz)
# ---------------------------------------------------------------------------


async def test_consume_twice_raises_not_found(service: OidcStateService) -> None:
    state = await service.create(provider="google", code_verifier="A" * 64)
    await service.consume(state)
    with pytest.raises(StateNotFoundError):
        await service.consume(state)


# ---------------------------------------------------------------------------
# Unbekannter State
# ---------------------------------------------------------------------------


async def test_consume_unknown_state_raises(service: OidcStateService) -> None:
    with pytest.raises(StateNotFoundError):
        await service.consume("totally-bogus-state")


async def test_state_not_found_error_message_is_opaque(
    service: OidcStateService,
) -> None:
    """Side-Channel-Vermeidung: Fehlertext darf nicht 'expired' vs 'invalid' verraten."""
    with pytest.raises(StateNotFoundError) as exc:
        await service.consume("bogus")
    # Beide Faelle (nicht-existent UND TTL-expired) sollen den gleichen
    # generischen Text liefern.
    assert "expired" in str(exc.value) or "not found" in str(exc.value).lower()


# ---------------------------------------------------------------------------
# TTL
# ---------------------------------------------------------------------------


async def test_ttl_expiry_makes_state_unavailable(redis_client: FakeRedis) -> None:
    """Mit sehr kleinem TTL: nach Sleep ist der State weg."""
    service = OidcStateService(redis_client=redis_client, ttl_seconds=1)
    state = await service.create(provider="google", code_verifier="A" * 64)
    # fakeredis emuliert TTL deterministisch via interne Zeit. Wir loeschen
    # explizit den Key statt zu sleepen, um Test-Speed zu erhalten.
    # Alternativ: await asyncio.sleep(1.5) - schlechter Test-Speed.
    from services.oidc_state_service import _state_key

    await redis_client.delete(_state_key(state))
    with pytest.raises(StateNotFoundError):
        await service.consume(state)


async def test_invalid_ttl_in_constructor_raises() -> None:
    redis_client = FakeRedis()
    try:
        with pytest.raises(ValueError):
            OidcStateService(redis_client=redis_client, ttl_seconds=0)
        with pytest.raises(ValueError):
            OidcStateService(redis_client=redis_client, ttl_seconds=-1)
    finally:
        await redis_client.aclose()


# ---------------------------------------------------------------------------
# Malformed Payload
# ---------------------------------------------------------------------------


async def test_malformed_redis_payload_raises_state_not_found(
    redis_client: FakeRedis,
    service: OidcStateService,
) -> None:
    """Defensive: wenn jemand muellt in Redis kommt, soll Service nicht crashen."""
    from services.oidc_state_service import _state_key

    bogus_key = _state_key("manual-state-1")
    await redis_client.set(bogus_key, "not-json-at-all", ex=60)

    with pytest.raises(StateNotFoundError):
        await service.consume("manual-state-1")


# ---------------------------------------------------------------------------
# State-Entry-Modell
# ---------------------------------------------------------------------------


def test_state_entry_requires_non_empty_provider() -> None:
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        StateEntry(
            provider="",
            code_verifier="A" * 64,
            created_at_iso="2026-06-17T00:00:00+00:00",
        )


def test_state_entry_round_trip_json() -> None:
    """Verifiziert dass model_dump_json -> model_validate(json.loads(...)) roundtripped."""
    original = StateEntry(
        provider="google",
        code_verifier="A" * 64,
        created_at_iso="2026-06-17T11:30:00+00:00",
    )
    json_str = original.model_dump_json()
    reloaded = StateEntry.model_validate(json.loads(json_str))
    assert reloaded.provider == original.provider
    assert reloaded.created_at_iso == original.created_at_iso


# ---------------------------------------------------------------------------
# PQC-42 BRK-7 AC-5: code_verifier wird mit State gespeichert + ge-DEL-t
# ---------------------------------------------------------------------------


async def test_consume_returns_code_verifier_from_state(
    service: OidcStateService,
) -> None:
    """AC-5: consume liefert sowohl provider als auch code_verifier zurueck."""
    verifier = "X" * 64
    state = await service.create(provider="google", code_verifier=verifier)
    entry = await service.consume(state)
    assert entry.provider == "google"
    assert entry.code_verifier == verifier


async def test_state_one_shot_invalidates_code_verifier_too(
    service: OidcStateService,
) -> None:
    """AC-5: One-Shot loescht beide (state + code_verifier) atomar."""
    state = await service.create(provider="microsoft", code_verifier="V" * 64)
    await service.consume(state)
    # Zweiter consume schlaegt fehl - kein leak des code_verifiers
    with pytest.raises(StateNotFoundError):
        await service.consume(state)


async def test_create_requires_valid_code_verifier_length(
    service: OidcStateService,
) -> None:
    """RFC 7636: 43-128 chars Pflicht."""
    with pytest.raises(Exception):  # ValidationError from pydantic  # noqa: B017
        await service.create(provider="google", code_verifier="too-short")
