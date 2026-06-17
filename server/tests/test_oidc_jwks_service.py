"""Tests fuer services/oidc_jwks_service.py.

Story: PQC-38 BRK-3 AC-1.
"""

from __future__ import annotations

import httpx
import pytest
import pytest_asyncio
import respx

from services.oidc_jwks_service import JwksFetchError, OidcJwksService

JWKS_URI = "https://idp.example/jwks"
SAMPLE_JWKS = {
    "keys": [
        {
            "kty": "RSA",
            "kid": "key-1",
            "use": "sig",
            "alg": "RS256",
            "n": "fake-modulus",
            "e": "AQAB",
        }
    ]
}


@pytest_asyncio.fixture
async def http_client() -> httpx.AsyncClient:
    client = httpx.AsyncClient(timeout=5.0)
    try:
        yield client
    finally:
        await client.aclose()


@pytest.fixture
def service(http_client: httpx.AsyncClient) -> OidcJwksService:
    return OidcJwksService(http_client=http_client, cache_ttl_seconds=3600)


# ---------------------------------------------------------------------------
# Fetch happy + cache
# ---------------------------------------------------------------------------


@respx.mock
async def test_fetch_jwks_happy_path(service: OidcJwksService) -> None:
    respx.get(JWKS_URI).respond(json=SAMPLE_JWKS)
    jwks = await service.get_jwks(JWKS_URI)
    assert jwks == SAMPLE_JWKS
    assert jwks["keys"][0]["kid"] == "key-1"


@respx.mock
async def test_second_fetch_uses_cache(service: OidcJwksService) -> None:
    route = respx.get(JWKS_URI).respond(json=SAMPLE_JWKS)
    await service.get_jwks(JWKS_URI)
    await service.get_jwks(JWKS_URI)
    assert route.call_count == 1


@respx.mock
async def test_force_refresh_bypasses_cache(service: OidcJwksService) -> None:
    route = respx.get(JWKS_URI).respond(json=SAMPLE_JWKS)
    await service.get_jwks(JWKS_URI)
    await service.get_jwks(JWKS_URI, force_refresh=True)
    assert route.call_count == 2


@respx.mock
async def test_invalidate_drops_cache_entry(service: OidcJwksService) -> None:
    route = respx.get(JWKS_URI).respond(json=SAMPLE_JWKS)
    await service.get_jwks(JWKS_URI)
    service.invalidate(JWKS_URI)
    await service.get_jwks(JWKS_URI)
    assert route.call_count == 2


# ---------------------------------------------------------------------------
# Error-Faelle
# ---------------------------------------------------------------------------


@respx.mock
async def test_http_error_raises_jwks_fetch_error(service: OidcJwksService) -> None:
    respx.get(JWKS_URI).respond(status_code=500)
    with pytest.raises(JwksFetchError) as exc:
        await service.get_jwks(JWKS_URI)
    assert "500" in str(exc.value)


@respx.mock
async def test_invalid_json_raises(service: OidcJwksService) -> None:
    respx.get(JWKS_URI).respond(text="not-json")
    with pytest.raises(JwksFetchError):
        await service.get_jwks(JWKS_URI)


@respx.mock
async def test_missing_keys_field_raises(service: OidcJwksService) -> None:
    respx.get(JWKS_URI).respond(json={"not_keys": []})
    with pytest.raises(JwksFetchError) as exc:
        await service.get_jwks(JWKS_URI)
    assert "keys" in str(exc.value)


@respx.mock
async def test_keys_not_list_raises(service: OidcJwksService) -> None:
    respx.get(JWKS_URI).respond(json={"keys": "not-a-list"})
    with pytest.raises(JwksFetchError):
        await service.get_jwks(JWKS_URI)


@respx.mock
async def test_network_error_raises(service: OidcJwksService) -> None:
    respx.get(JWKS_URI).mock(side_effect=httpx.ConnectError("conn refused"))
    with pytest.raises(JwksFetchError):
        await service.get_jwks(JWKS_URI)


# ---------------------------------------------------------------------------
# Constructor
# ---------------------------------------------------------------------------


async def test_invalid_ttl_raises(http_client: httpx.AsyncClient) -> None:
    with pytest.raises(ValueError):
        OidcJwksService(http_client=http_client, cache_ttl_seconds=0)
