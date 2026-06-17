"""Tests fuer services/oidc_exchange_service.py.

Story: PQC-37 BRK-2 AC-2, AC-3, AC-4.

Mockt httpx via respx (router-level mocking) statt globalem Transport-Mock.
Discovery + Token-Exchange werden gegen erfundene URLs gemockt.
"""

from __future__ import annotations

from typing import ClassVar

import httpx
import pytest
import pytest_asyncio
import respx

from services.oidc_exchange_service import (
    CodeExchangeError,
    DiscoveryError,
    OidcExchangeService,
    TokenExchangeResult,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


DISCOVERY_URL = "https://idp.example/.well-known/openid-configuration"
TOKEN_ENDPOINT = "https://idp.example/oauth2/v3/token"


@pytest_asyncio.fixture
async def http_client() -> httpx.AsyncClient:
    client = httpx.AsyncClient(timeout=5.0)
    try:
        yield client
    finally:
        await client.aclose()


@pytest.fixture
def service(http_client: httpx.AsyncClient) -> OidcExchangeService:
    return OidcExchangeService(
        http_client=http_client,
        discovery_cache_ttl_seconds=86400,
    )


class _MockPlugin:
    """Test-Plugin mit fester Provider-Config."""

    name: str = "mock"
    discovery_url: str = DISCOVERY_URL
    client_id: str = "test-client-id"
    client_secret: str = "test-client-secret"
    redirect_uri: str = "http://localhost:8000/auth/mock/callback"
    scopes: ClassVar[list[str]] = ["openid", "email"]


@pytest.fixture
def plugin() -> _MockPlugin:
    return _MockPlugin()


# ---------------------------------------------------------------------------
# Discovery-Fetch + Cache
# ---------------------------------------------------------------------------


@respx.mock
async def test_discovery_fetches_and_returns_token_endpoint(
    service: OidcExchangeService,
) -> None:
    respx.get(DISCOVERY_URL).respond(
        json={"token_endpoint": TOKEN_ENDPOINT, "issuer": "https://idp.example"},
    )
    doc = await service.get_discovery_document(DISCOVERY_URL)
    assert doc["token_endpoint"] == TOKEN_ENDPOINT


@respx.mock
async def test_discovery_second_call_uses_cache(
    service: OidcExchangeService,
) -> None:
    route = respx.get(DISCOVERY_URL).respond(
        json={"token_endpoint": TOKEN_ENDPOINT},
    )
    await service.get_discovery_document(DISCOVERY_URL)
    await service.get_discovery_document(DISCOVERY_URL)
    assert route.call_count == 1


@respx.mock
async def test_discovery_http_error_raises_discovery_error(
    service: OidcExchangeService,
) -> None:
    respx.get(DISCOVERY_URL).respond(status_code=500)
    with pytest.raises(DiscoveryError) as exc:
        await service.get_discovery_document(DISCOVERY_URL)
    assert "500" in str(exc.value)


@respx.mock
async def test_discovery_invalid_json_raises_discovery_error(
    service: OidcExchangeService,
) -> None:
    respx.get(DISCOVERY_URL).respond(text="<html>not json</html>")
    with pytest.raises(DiscoveryError):
        await service.get_discovery_document(DISCOVERY_URL)


@respx.mock
async def test_discovery_missing_token_endpoint_raises(
    service: OidcExchangeService,
) -> None:
    respx.get(DISCOVERY_URL).respond(json={"issuer": "https://idp.example"})
    with pytest.raises(DiscoveryError) as exc:
        await service.get_discovery_document(DISCOVERY_URL)
    assert "token_endpoint" in str(exc.value)


@respx.mock
async def test_discovery_network_error_raises(
    service: OidcExchangeService,
) -> None:
    respx.get(DISCOVERY_URL).mock(side_effect=httpx.ConnectError("conn refused"))
    with pytest.raises(DiscoveryError):
        await service.get_discovery_document(DISCOVERY_URL)


# ---------------------------------------------------------------------------
# Code-Token-Exchange Happy-Path
# ---------------------------------------------------------------------------


@respx.mock
async def test_exchange_code_happy_path(
    service: OidcExchangeService,
    plugin: _MockPlugin,
) -> None:
    respx.get(DISCOVERY_URL).respond(json={"token_endpoint": TOKEN_ENDPOINT})
    respx.post(TOKEN_ENDPOINT).respond(
        json={
            "id_token": "eyFAKE.jwt.token",
            "access_token": "fake-access",
            "expires_in": 3600,
            "token_type": "Bearer",
        }
    )
    result = await service.exchange_code(
        plugin=plugin,  # type: ignore[arg-type]
        code="auth-code-123",
        code_verifier="pkce-verifier-456",
    )
    assert isinstance(result, TokenExchangeResult)
    assert result.id_token == "eyFAKE.jwt.token"
    assert result.access_token == "fake-access"
    assert result.expires_in == 3600


@respx.mock
async def test_exchange_code_sends_correct_form_payload(
    service: OidcExchangeService,
    plugin: _MockPlugin,
) -> None:
    respx.get(DISCOVERY_URL).respond(json={"token_endpoint": TOKEN_ENDPOINT})
    token_route = respx.post(TOKEN_ENDPOINT).respond(
        json={"id_token": "tok", "access_token": "acc"},
    )
    await service.exchange_code(
        plugin=plugin,  # type: ignore[arg-type]
        code="auth-code-123",
        code_verifier="pkce-verifier-456",
    )
    assert token_route.called
    request = token_route.calls[0].request
    body = request.content.decode("utf-8")
    # form-encoded
    assert "grant_type=authorization_code" in body
    assert "code=auth-code-123" in body
    assert "code_verifier=pkce-verifier-456" in body
    assert "client_id=test-client-id" in body
    assert "client_secret=test-client-secret" in body


# ---------------------------------------------------------------------------
# Code-Token-Exchange Error-Cases (AC-4)
# ---------------------------------------------------------------------------


@respx.mock
async def test_exchange_code_400_returns_code_exchange_error(
    service: OidcExchangeService,
    plugin: _MockPlugin,
) -> None:
    respx.get(DISCOVERY_URL).respond(json={"token_endpoint": TOKEN_ENDPOINT})
    respx.post(TOKEN_ENDPOINT).respond(
        status_code=400,
        json={
            "error": "invalid_grant",
            "error_description": "Code expired or already used",
        },
    )
    with pytest.raises(CodeExchangeError) as exc:
        await service.exchange_code(
            plugin=plugin,  # type: ignore[arg-type]
            code="bad-code",
            code_verifier="verifier",
        )
    assert exc.value.provider_error == "invalid_grant"
    assert exc.value.provider_error_description == "Code expired or already used"


@respx.mock
async def test_exchange_code_500_returns_code_exchange_error_with_http_default(
    service: OidcExchangeService,
    plugin: _MockPlugin,
) -> None:
    respx.get(DISCOVERY_URL).respond(json={"token_endpoint": TOKEN_ENDPOINT})
    respx.post(TOKEN_ENDPOINT).respond(status_code=500, text="oops")
    with pytest.raises(CodeExchangeError) as exc:
        await service.exchange_code(
            plugin=plugin,  # type: ignore[arg-type]
            code="any-code",
            code_verifier="verifier",
        )
    assert "500" in str(exc.value)
    assert exc.value.provider_error == "http_error"


@respx.mock
async def test_exchange_code_missing_id_token_raises(
    service: OidcExchangeService,
    plugin: _MockPlugin,
) -> None:
    respx.get(DISCOVERY_URL).respond(json={"token_endpoint": TOKEN_ENDPOINT})
    respx.post(TOKEN_ENDPOINT).respond(
        json={"access_token": "only-access-no-id-token"},
    )
    with pytest.raises(CodeExchangeError) as exc:
        await service.exchange_code(
            plugin=plugin,  # type: ignore[arg-type]
            code="any-code",
            code_verifier="verifier",
        )
    assert exc.value.provider_error == "missing_id_token"


@respx.mock
async def test_exchange_code_malformed_response_raises(
    service: OidcExchangeService,
    plugin: _MockPlugin,
) -> None:
    respx.get(DISCOVERY_URL).respond(json={"token_endpoint": TOKEN_ENDPOINT})
    respx.post(TOKEN_ENDPOINT).respond(text="not-json")
    with pytest.raises(CodeExchangeError) as exc:
        await service.exchange_code(
            plugin=plugin,  # type: ignore[arg-type]
            code="any-code",
            code_verifier="verifier",
        )
    assert exc.value.provider_error == "malformed_response"


@respx.mock
async def test_exchange_code_network_error_raises_code_exchange_error(
    service: OidcExchangeService,
    plugin: _MockPlugin,
) -> None:
    respx.get(DISCOVERY_URL).respond(json={"token_endpoint": TOKEN_ENDPOINT})
    respx.post(TOKEN_ENDPOINT).mock(
        side_effect=httpx.ConnectError("connection refused"),
    )
    with pytest.raises(CodeExchangeError) as exc:
        await service.exchange_code(
            plugin=plugin,  # type: ignore[arg-type]
            code="any-code",
            code_verifier="verifier",
        )
    assert exc.value.provider_error == "network_error"


# ---------------------------------------------------------------------------
# Constructor-Validation
# ---------------------------------------------------------------------------


async def test_invalid_discovery_cache_ttl_raises(
    http_client: httpx.AsyncClient,
) -> None:
    with pytest.raises(ValueError):
        OidcExchangeService(
            http_client=http_client,
            discovery_cache_ttl_seconds=0,
        )
