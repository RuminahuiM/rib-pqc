"""Tests fuer routers/auth_federated.py.

Story: PQC-37 BRK-2 AC-1 bis AC-5.

End-to-End-Tests gegen den Router mit gemockten Services (StateService +
ExchangeService) und einer In-Memory IdpRegistry. Kein echter Redis-Server,
keine echten IdP-HTTP-Calls.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from idp.registry import IdpRegistry
from routers import auth_federated
from services.oidc_exchange_service import (
    CodeExchangeError,
    DiscoveryError,
    TokenExchangeResult,
)
from services.oidc_state_service import StateEntry, StateNotFoundError

VALID_VERIFIER = "A" * 64  # 43-128 chars per RFC 7636


class _MockPlugin:
    name: str = "google"
    discovery_url: str = "https://idp.example/.well-known/openid-configuration"
    client_id: str = "g-id"
    client_secret: str = "g-secret"
    redirect_uri: str = "http://localhost:8000/auth/google/callback"
    scopes: list[str] = ["openid", "email", "profile"]

    async def verify_id_token(
        self,
        token: str,
        *,
        jwks_uri: str,
        verifier: Any,
    ) -> dict[str, Any]:
        """Mock-Verify: gibt Test-Claims zurueck. Override per Test mittels self._verify_result."""
        del token, jwks_uri, verifier
        return getattr(self, "_verify_result", {"sub": "mock-user-id", "iss": "https://idp.example", "aud": "g-id"})


@pytest.fixture
def mock_state_service() -> AsyncMock:
    svc = AsyncMock()
    svc.create.return_value = "state-12345"
    svc.consume.return_value = StateEntry(
        provider="google",
        created_at_iso="2026-06-17T10:00:00+00:00",
    )
    return svc


@pytest.fixture
def mock_exchange_service() -> AsyncMock:
    svc = AsyncMock()
    svc.get_discovery_document.return_value = {
        "authorization_endpoint": "https://idp.example/auth",
        "token_endpoint": "https://idp.example/token",
        "jwks_uri": "https://idp.example/jwks",
    }
    svc.exchange_code.return_value = TokenExchangeResult(
        id_token="eyFAKE.id.token",
        access_token="fake-access",
        expires_in=3600,
    )
    return svc


@pytest.fixture
def test_app(
    mock_state_service: AsyncMock,
    mock_exchange_service: AsyncMock,
) -> FastAPI:
    """FastAPI-App nur mit dem auth_federated-Router + mocked Services."""
    app = FastAPI()
    app.include_router(auth_federated.router)

    registry = IdpRegistry()
    registry.register("google", _MockPlugin())  # type: ignore[arg-type]

    app.state.idp_registry = registry
    app.state.oidc_state_service = mock_state_service
    app.state.oidc_exchange_service = mock_exchange_service
    # PQC-38 (BRK-3): IdTokenVerifier wird Plugin uebergeben. In Tests aber
    # ruft Plugin.verify_id_token den verifier auf - wir muessen den Plugin
    # Mock-fy oder den verify_id_token-Call mocken.
    app.state.id_token_verifier = AsyncMock()
    return app


@pytest.fixture
def client(test_app: FastAPI) -> TestClient:
    return TestClient(test_app)


# ---------------------------------------------------------------------------
# POST /authorize Happy + Errors
# ---------------------------------------------------------------------------


def test_authorize_happy_path(
    client: TestClient,
    mock_state_service: AsyncMock,
) -> None:
    r = client.post("/auth/federated/google/authorize")
    assert r.status_code == 200
    body = r.json()
    assert body["state"] == "state-12345"
    assert body["authorize_url"].startswith("https://idp.example/auth?")
    assert "client_id=g-id" in body["authorize_url"]
    assert "redirect_uri=" in body["authorize_url"]
    assert "state=state-12345" in body["authorize_url"]
    assert "scope=openid+email+profile" in body["authorize_url"]
    mock_state_service.create.assert_awaited_once_with(provider="google")


def test_authorize_with_pkce_challenge(client: TestClient) -> None:
    r = client.post(
        "/auth/federated/google/authorize?code_challenge=challengeABC",
    )
    assert r.status_code == 200
    body = r.json()
    assert "code_challenge=challengeABC" in body["authorize_url"]
    assert "code_challenge_method=S256" in body["authorize_url"]


def test_authorize_unknown_provider_returns_404(client: TestClient) -> None:
    r = client.post("/auth/federated/apple/authorize")
    assert r.status_code == 404
    assert r.json()["detail"]["error"] == "unknown_provider"


def test_authorize_provider_format_invalid_returns_422(client: TestClient) -> None:
    """Path-Pattern lehnt Grossbuchstaben + Sonderzeichen ab."""
    r = client.post("/auth/federated/Google!/authorize")
    assert r.status_code == 422


def test_authorize_discovery_failure_returns_502(
    client: TestClient,
    mock_exchange_service: AsyncMock,
) -> None:
    mock_exchange_service.get_discovery_document.side_effect = DiscoveryError("nope")
    r = client.post("/auth/federated/google/authorize")
    assert r.status_code == 502
    assert r.json()["detail"]["error"] == "discovery_failed"


# ---------------------------------------------------------------------------
# POST /callback Happy + Errors (AC-1..AC-5)
# ---------------------------------------------------------------------------


def _callback_payload(**overrides: Any) -> dict[str, Any]:
    base = {
        "code": "auth-code-xyz",
        "code_verifier": VALID_VERIFIER,
        "state": "state-12345",
    }
    base.update(overrides)
    return base


def test_callback_happy_path_returns_id_token(client: TestClient) -> None:
    r = client.post("/auth/federated/google/callback", json=_callback_payload())
    assert r.status_code == 200
    body = r.json()
    assert body["id_token"] == "eyFAKE.id.token"
    assert body["access_token"] == "fake-access"
    assert body["expires_in"] == 3600


def test_callback_consumes_state_one_shot(
    client: TestClient,
    mock_state_service: AsyncMock,
) -> None:
    client.post("/auth/federated/google/callback", json=_callback_payload())
    mock_state_service.consume.assert_awaited_once_with("state-12345")


def test_callback_state_mismatch_returns_400(
    client: TestClient,
    mock_state_service: AsyncMock,
) -> None:
    mock_state_service.consume.side_effect = StateNotFoundError("opaque")
    r = client.post("/auth/federated/google/callback", json=_callback_payload())
    assert r.status_code == 400
    assert r.json()["detail"]["error"] == "invalid_state"


def test_callback_state_provider_mismatch_returns_400(
    client: TestClient,
    mock_state_service: AsyncMock,
) -> None:
    """State wurde fuer Microsoft erzeugt, App POSTed an Google-Callback."""
    mock_state_service.consume.return_value = StateEntry(
        provider="microsoft",
        created_at_iso="2026-06-17T10:00:00+00:00",
    )
    r = client.post("/auth/federated/google/callback", json=_callback_payload())
    assert r.status_code == 400
    assert r.json()["detail"]["error"] == "state_provider_mismatch"


def test_callback_unknown_provider_returns_404(client: TestClient) -> None:
    r = client.post("/auth/federated/apple/callback", json=_callback_payload())
    assert r.status_code == 404


def test_callback_idp_invalid_grant_returns_400(
    client: TestClient,
    mock_exchange_service: AsyncMock,
) -> None:
    mock_exchange_service.exchange_code.side_effect = CodeExchangeError(
        "Code expired",
        provider_error="invalid_grant",
        provider_error_description="Code already used",
    )
    r = client.post("/auth/federated/google/callback", json=_callback_payload())
    assert r.status_code == 400
    body = r.json()["detail"]
    assert body["error"] == "code_exchange_failed"
    assert body["provider_error"] == "invalid_grant"
    assert body["provider_error_description"] == "Code already used"


def test_callback_discovery_failure_returns_502(
    client: TestClient,
    mock_exchange_service: AsyncMock,
) -> None:
    mock_exchange_service.exchange_code.side_effect = DiscoveryError("provider down")
    r = client.post("/auth/federated/google/callback", json=_callback_payload())
    assert r.status_code == 502


def test_callback_validates_code_verifier_length(client: TestClient) -> None:
    """RFC 7636: 43-128 chars."""
    r = client.post(
        "/auth/federated/google/callback",
        json=_callback_payload(code_verifier="too-short"),
    )
    assert r.status_code == 422


def test_callback_requires_state_field(client: TestClient) -> None:
    payload = _callback_payload()
    del payload["state"]
    r = client.post("/auth/federated/google/callback", json=payload)
    assert r.status_code == 422


def test_callback_requires_code_field(client: TestClient) -> None:
    payload = _callback_payload()
    del payload["code"]
    r = client.post("/auth/federated/google/callback", json=payload)
    assert r.status_code == 422
