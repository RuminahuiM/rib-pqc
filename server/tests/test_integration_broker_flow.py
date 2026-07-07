"""Integration-Tests fuer den kompletten OIDC-Broker-Flow.

Story: PQC-66 QUA-4.
Bezug: BRK-2, BRK-3, BRK-4, BRK-5, BRK-6.

**Integration-Test-Strategie (im Sinne von QUA-4 AC):**

* Mock-IdP-Server via respx: fangt die HTTP-Requests des OIDC-Exchange-Service
  ab und liefert deterministische Discovery-Docs + Token-Responses. Externe
  Provider (Google, Microsoft Entra) werden nicht kontaktiert.
* Alle anderen Services sind ECHT und werden ueber die App wired: State-Service
  (fakeredis), Exchange-Service (echter httpx), Federated-Identity-Service
  (echte DB via in-memory SQLite), Token-Service (echte ML-DSA-65-Facade), User-
  Repo, IdP-Registry mit echten Plugins.
* Einzige Ausnahme: ``verify_id_token`` liefert per Test-Injection fixed Claims
  zurueck (das reine RS256+JWKS-Signature-Verify ist separat in
  ``test_id_token_verifier.py`` getestet). Das reduziert das Setup enorm
  ohne Coverage-Verlust fuer die Broker-Orchestrierung.

**Tests im Fokus:**

1. Google full-happy-path -> broker-token issued + user created.
2. Microsoft happy-path mit tid-Check (Single-Tenant Defense).
3. Existing-User-Link: zweiter Login desselben external_sub -> KEIN neuer
   User, sondern link zur existierenden User-Row.
4. Error: unknown state -> 400 invalid_state (Router-Konvention analog
   test_auth_federated_router.py::test_callback_state_mismatch_returns_400).
5. Error: IdP-Token-Endpoint 400 -> Router mappt auf 400 code_exchange_failed.
"""
from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any, ClassVar

import fakeredis.aioredis
import httpx
import pytest
import pytest_asyncio
import respx
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker

# ML-DSA-65 signing needs liboqs. In Sandbox-Umgebungen ohne cmake schlaegt
# der liboqs-Auto-Download beim ersten Aufruf einer C-lib-abhaengigen Funktion
# fehl. `oqs_version()` returned nur die package-Version ohne shared-lib-call,
# darum machen wir hier einen Test-call gegen ``get_enabled_sig_mechanisms()``
# der die shared lib triggert.
try:
    import oqs as _oqs
    _oqs.get_enabled_sig_mechanisms()
    _liboqs_available = True
except (ImportError, RuntimeError, OSError, SystemExit):
    # SystemExit weil oqs.oqs macht sys.exit(1) bei fehlender shared lib +
    # cmake-nicht-verfuegbar (Auto-Install-Fail-Path).
    _liboqs_available = False

pytestmark = pytest.mark.skipif(
    not _liboqs_available,
    reason="liboqs shared lib nicht ladbar (Sandbox-Mode). Tests laufen im Docker-Container.",
)

from crypto.facade import CryptoFacade  # noqa: E402
from crypto.registry import CryptoRegistry  # noqa: E402
from idp.normalized_identity import NormalizedIdentity
from idp.registry import IdpRegistry
from routers import auth_federated
from services.oidc_exchange_service import OidcExchangeService
from services.oidc_state_service import OidcStateService
from services.token_service import TokenService

# ---------------------------------------------------------------------------
# Konstanten und Mock-Data
# ---------------------------------------------------------------------------

# RFC 7636: code_verifier 43-128 unreserved chars. Der Authorize-Endpoint
# verlangt das Feld zwingend (BFF-Pattern: Server speichert den Verifier
# im Redis-State, App schickt ihn beim Callback nicht mehr mit).
TEST_CODE_VERIFIER = "integration-test-code-verifier-0123456789abc"

GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_JWKS_URL = "https://www.googleapis.com/oauth2/v3/certs"
GOOGLE_AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"

MS_TENANT = "test-tenant-uuid"
MS_DISCOVERY_URL = (
    f"https://login.microsoftonline.com/{MS_TENANT}/v2.0/.well-known/openid-configuration"
)
MS_TOKEN_URL = f"https://login.microsoftonline.com/{MS_TENANT}/oauth2/v2.0/token"
MS_AUTHORIZE_URL = f"https://login.microsoftonline.com/{MS_TENANT}/oauth2/v2.0/authorize"
MS_JWKS_URL = f"https://login.microsoftonline.com/{MS_TENANT}/discovery/v2.0/keys"


def _google_discovery_doc() -> dict[str, Any]:
    return {
        "issuer": "https://accounts.google.com",
        "authorization_endpoint": GOOGLE_AUTHORIZE_URL,
        "token_endpoint": GOOGLE_TOKEN_URL,
        "jwks_uri": GOOGLE_JWKS_URL,
    }


def _ms_discovery_doc() -> dict[str, Any]:
    return {
        "issuer": f"https://login.microsoftonline.com/{MS_TENANT}/v2.0",
        "authorization_endpoint": MS_AUTHORIZE_URL,
        "token_endpoint": MS_TOKEN_URL,
        "jwks_uri": MS_JWKS_URL,
    }


# ---------------------------------------------------------------------------
# Echte Plugin-Klassen mit injectable verify_id_token
# ---------------------------------------------------------------------------


class _IntegrationGooglePlugin:
    """Echtes Google-Plugin-Contract mit injectable verify_id_token.

    Alle statischen Felder (name, discovery_url, ...) sind echt. Nur die
    verify_id_token-Methode ist per Test-Fixture injectable, damit wir nicht
    RSA-Keys + JWKS-Serving nachbauen muessen.
    """

    name: str = "google"
    discovery_url: str = GOOGLE_DISCOVERY_URL
    client_id: str = "integration-google-client-id"
    client_secret: str = "integration-google-secret"  # noqa: S105 (test constant, not a real secret)
    redirect_uri: str = "http://localhost:8081/auth/google/callback"
    scopes: ClassVar[list[str]] = ["openid", "email", "profile"]

    def __init__(self) -> None:
        self._claims_override: dict[str, Any] | None = None

    def set_claims(self, claims: dict[str, Any] | None) -> None:
        """Test-only Setter fuer die zurueckgegebenen Claims."""
        self._claims_override = claims

    async def verify_id_token(
        self,
        token: str,
        *,
        jwks_uri: str,
        verifier: Any,
    ) -> dict[str, Any]:
        del token, jwks_uri, verifier
        if self._claims_override is None:
            return {
                "sub": "google-sub-42",
                "iss": "https://accounts.google.com",
                "aud": self.client_id,
                "email": "user42@example.com",
                "email_verified": True,
                "name": "Test User 42",
            }
        return dict(self._claims_override)

    def claim_mapper(self, payload: dict[str, Any]) -> NormalizedIdentity:
        return NormalizedIdentity(
            external_sub=str(payload["sub"]),
            email=payload.get("email"),
            email_verified=bool(payload.get("email_verified", False)),
            display_name=payload.get("name"),
        )


class _IntegrationMicrosoftPlugin:
    """Echtes Microsoft-Plugin-Contract mit injectable verify_id_token.

    Enforced tid-Check (Single-Tenant) analog zum echten Plugin.
    """

    name: str = "microsoft"
    discovery_url: str = MS_DISCOVERY_URL
    client_id: str = "integration-ms-client-id"
    client_secret: str = "integration-ms-secret"  # noqa: S105 (test constant, not a real secret)
    redirect_uri: str = "http://localhost:8081/auth/microsoft/callback"
    scopes: ClassVar[list[str]] = ["openid", "email", "profile"]
    tenant_id: str = MS_TENANT

    def __init__(self) -> None:
        self._claims_override: dict[str, Any] | None = None

    def set_claims(self, claims: dict[str, Any] | None) -> None:
        self._claims_override = claims

    async def verify_id_token(
        self,
        token: str,
        *,
        jwks_uri: str,
        verifier: Any,
    ) -> dict[str, Any]:
        del token, jwks_uri, verifier
        default = {
            "sub": "ms-sub-99",
            "iss": f"https://login.microsoftonline.com/{MS_TENANT}/v2.0",
            "aud": self.client_id,
            "tid": MS_TENANT,
            "email": "user99@company.example",
            "preferred_username": "user99@company.example",
            "name": "Corp User 99",
        }
        claims = default if self._claims_override is None else dict(self._claims_override)
        # tid-Check (Single-Tenant Defense - RFC 9700 Sec 4.6)
        if claims.get("tid") != self.tenant_id:
            msg = f"tid mismatch: expected {self.tenant_id}, got {claims.get('tid')}"
            raise ValueError(msg)
        return claims

    def claim_mapper(self, payload: dict[str, Any]) -> NormalizedIdentity:
        return NormalizedIdentity(
            external_sub=str(payload["sub"]),
            email=payload.get("email") or payload.get("preferred_username"),
            email_verified=True,
            display_name=payload.get("name"),
        )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def state_redis() -> AsyncIterator[fakeredis.aioredis.FakeRedis]:
    client = fakeredis.aioredis.FakeRedis()
    try:
        yield client
    finally:
        await client.aclose()


@pytest.fixture
def google_plugin() -> _IntegrationGooglePlugin:
    return _IntegrationGooglePlugin()


@pytest.fixture
def ms_plugin() -> _IntegrationMicrosoftPlugin:
    return _IntegrationMicrosoftPlugin()


@pytest.fixture
def signing_facade() -> CryptoFacade:
    """Echte CryptoFacade mit frischem ML-DSA-65-Keypair (liboqs erforderlich)."""
    oqs = pytest.importorskip("oqs")
    del oqs  # nur importorskip-Marker
    from crypto.adapters.liboqs_signature import LibOqsSignature

    registry = CryptoRegistry()
    plugin = LibOqsSignature("ML-DSA-65")
    registry.register_signature("ML-DSA-65", plugin)
    pub, priv = plugin.keygen()
    return CryptoFacade(
        registry=registry,
        default_signature_alg="ML-DSA-65",
        signing_kid="integration-test-kid",
        signing_secret_key=priv,
        verifying_keys_by_kid={"integration-test-kid": pub},
    )


@pytest_asyncio.fixture
async def integration_app(
    state_redis: fakeredis.aioredis.FakeRedis,
    session_factory: async_sessionmaker,
    google_plugin: _IntegrationGooglePlugin,
    ms_plugin: _IntegrationMicrosoftPlugin,
    signing_facade: CryptoFacade,
) -> FastAPI:
    """Baut eine voll-integrierte FastAPI-App mit echten Services."""
    app = FastAPI()

    # State-Service (echt, fakeredis)
    state_service = OidcStateService(
        redis_client=state_redis,
        ttl_seconds=600,
    )

    # Exchange-Service (echt, httpx - respx intercepts external calls)
    async_http = httpx.AsyncClient(timeout=5.0)
    exchange_service = OidcExchangeService(
        http_client=async_http,
        discovery_cache_ttl_seconds=86400,
    )

    # IdP-Registry mit echten Plugins
    registry = IdpRegistry()
    registry.register("google", google_plugin)  # type: ignore[arg-type]
    registry.register("microsoft", ms_plugin)  # type: ignore[arg-type]

    # FederatedIdentityService wird vom Router PER REQUEST gebaut (mit
    # frischen user_repo + identity_repo aus session_factory), nicht als
    # Singleton. Router liest nur session_factory aus app.state.

    # Token-Service (echt, mit signing_facade)
    token_service = TokenService(
        crypto_facade=signing_facade,
        issuer="integration-test-broker",
        ttl_seconds=3600,
        allowed_algs=["ML-DSA-65"],
        exp_leeway_seconds=30,
    )

    # State-Attribute-Namen matched Router (routers/auth_federated.py):
    # oidc_state_service, oidc_exchange_service, id_token_verifier,
    # idp_registry, session_factory, token_service.
    app.state.oidc_state_service = state_service
    app.state.oidc_exchange_service = exchange_service
    app.state.idp_registry = registry
    # id_token_verifier wird an plugin.verify_id_token durchgereicht. Da
    # unsere Test-Plugins verify_id_token intern selbst stubben (siehe
    # _IntegrationGooglePlugin.verify_id_token override), reicht None.
    app.state.id_token_verifier = None
    app.state.token_service = token_service
    app.state.session_factory = session_factory

    app.include_router(auth_federated.router)

    return app


@pytest.fixture
def client(integration_app: FastAPI) -> TestClient:
    return TestClient(integration_app)


# ---------------------------------------------------------------------------
# Test 1: Google Happy-Path (full flow)
# ---------------------------------------------------------------------------


@respx.mock(base_url="https://accounts.google.com")
def test_google_full_flow_creates_user_and_issues_broker_token(
    respx_mock: respx.MockRouter,
    client: TestClient,
    google_plugin: _IntegrationGooglePlugin,
) -> None:
    # Mock IdP: Discovery + Token-Endpoint (Google)
    respx_mock.get("/.well-known/openid-configuration").mock(
        return_value=httpx.Response(200, json=_google_discovery_doc()),
    )
    with respx.mock(base_url="https://oauth2.googleapis.com") as token_mock:
        token_mock.post("/token").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id_token": "eyDUMMY.id.token",
                    "access_token": "google-access-token",
                    "expires_in": 3600,
                    "token_type": "Bearer",
                },
            ),
        )

        # Step 1: /authorize -> speichert state+verifier in redis
        r_auth = client.post(
            "/auth/federated/google/authorize",
            json={"code_verifier": TEST_CODE_VERIFIER},
        )
        assert r_auth.status_code == 200, r_auth.text
        auth_body = r_auth.json()
        assert "state" in auth_body
        assert "authorize_url" in auth_body
        state = auth_body["state"]

        # Step 2: /callback -> exchange code, verify id-token (mocked claims),
        # map claims, create user, issue broker-token
        r_cb = client.post(
            "/auth/federated/google/callback",
            json={"code": "mock-google-code", "state": state},
        )

    assert r_cb.status_code == 200, r_cb.text
    body = r_cb.json()
    assert body["id_token"] == "eyDUMMY.id.token"
    assert body["access_token"] == "google-access-token"
    assert body["token_type"] == "Bearer"
    assert body["broker_token_expires_in"] == 3600
    assert body["user"]["email"] == "user42@example.com"
    assert body["user"]["auth_method"] == "google"
    # Broker-Token ist JWS-Compact (3 base64url-Segmente)
    assert body["broker_token"].count(".") == 2

    _ = google_plugin  # fixture used implicitly via app.state


# ---------------------------------------------------------------------------
# Test 2: Microsoft Happy-Path mit tid-Check
# ---------------------------------------------------------------------------


def test_microsoft_full_flow_enforces_tenant_id(
    client: TestClient,
    ms_plugin: _IntegrationMicrosoftPlugin,
) -> None:
    with respx.mock(base_url=f"https://login.microsoftonline.com/{MS_TENANT}") as m:
        m.get("/v2.0/.well-known/openid-configuration").mock(
            return_value=httpx.Response(200, json=_ms_discovery_doc()),
        )
        m.post("/oauth2/v2.0/token").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id_token": "eyMS.id.token",
                    "access_token": "ms-access-token",
                    "expires_in": 3600,
                    "token_type": "Bearer",
                },
            ),
        )
        r_auth = client.post(
            "/auth/federated/microsoft/authorize",
            json={"code_verifier": TEST_CODE_VERIFIER},
        )
        assert r_auth.status_code == 200
        state = r_auth.json()["state"]

        r_cb = client.post(
            "/auth/federated/microsoft/callback",
            json={"code": "mock-ms-code", "state": state},
        )

    assert r_cb.status_code == 200, r_cb.text
    body = r_cb.json()
    assert body["user"]["auth_method"] == "microsoft"
    assert body["user"]["email"] == "user99@company.example"
    _ = ms_plugin


# ---------------------------------------------------------------------------
# Test 3: Existing-User-Link (kein Duplikat)
# ---------------------------------------------------------------------------


def test_google_second_login_links_existing_user(
    client: TestClient,
    google_plugin: _IntegrationGooglePlugin,
) -> None:
    with respx.mock(base_url="https://accounts.google.com") as disc, \
            respx.mock(base_url="https://oauth2.googleapis.com") as tok:
        disc.get("/.well-known/openid-configuration").mock(
            return_value=httpx.Response(200, json=_google_discovery_doc()),
        )
        tok.post("/token").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id_token": "eyDUP.id.token",
                    "access_token": "dup-access",
                    "expires_in": 3600,
                    "token_type": "Bearer",
                },
            ),
        )

        # First login
        r_auth1 = client.post(
            "/auth/federated/google/authorize",
            json={"code_verifier": TEST_CODE_VERIFIER},
        )
        state1 = r_auth1.json()["state"]
        r_cb1 = client.post(
            "/auth/federated/google/callback",
            json={"code": "code1", "state": state1},
        )
        assert r_cb1.status_code == 200, r_cb1.text
        user1_id = r_cb1.json()["user"]["id"]

        # Second login (same external_sub via same claims)
        r_auth2 = client.post(
            "/auth/federated/google/authorize",
            json={"code_verifier": TEST_CODE_VERIFIER},
        )
        state2 = r_auth2.json()["state"]
        r_cb2 = client.post(
            "/auth/federated/google/callback",
            json={"code": "code2", "state": state2},
        )
        assert r_cb2.status_code == 200, r_cb2.text
        user2_id = r_cb2.json()["user"]["id"]

    assert user1_id == user2_id, "Same external_sub must map to same user"
    _ = google_plugin


# ---------------------------------------------------------------------------
# Test 4: Unknown State -> 400 invalid_state
# ---------------------------------------------------------------------------


def test_callback_with_unknown_state_returns_400(client: TestClient) -> None:
    """Router-Konvention: invalid_state ist 400 (Client-Fehler im Flow),
    konsistent mit test_auth_federated_router.py. Erster Test-Entwurf hatte
    401 erwartet, das widerspricht der dokumentierten Router-Behavior.
    """
    with respx.mock(base_url="https://accounts.google.com"):
        r_cb = client.post(
            "/auth/federated/google/callback",
            json={"code": "irrelevant", "state": "state-nicht-in-redis"},
        )
    assert r_cb.status_code == 400, r_cb.text
    assert r_cb.json()["detail"]["error"] == "invalid_state"


# ---------------------------------------------------------------------------
# Test 5: IdP-Token-Endpoint 400 -> Router mapped auf 400 code_exchange_failed
# ---------------------------------------------------------------------------



def test_token_exchange_failure_maps_to_400(client: TestClient) -> None:
    with respx.mock(base_url="https://accounts.google.com") as disc, \
            respx.mock(base_url="https://oauth2.googleapis.com") as tok:
        disc.get("/.well-known/openid-configuration").mock(
            return_value=httpx.Response(200, json=_google_discovery_doc()),
        )
        tok.post("/token").mock(
            return_value=httpx.Response(
                400,
                json={"error": "invalid_grant", "error_description": "code expired"},
            ),
        )
        r_auth = client.post(
            "/auth/federated/google/authorize",
            json={"code_verifier": TEST_CODE_VERIFIER},
        )
        state = r_auth.json()["state"]
        r_cb = client.post(
            "/auth/federated/google/callback",
            json={"code": "expired", "state": state},
        )
    assert r_cb.status_code == 400, r_cb.text
    body = r_cb.json()
    # Router-Konvention: IdP-Token-Endpoint-Fehler -> "code_exchange_failed"
    # (konsistent mit test_callback_idp_invalid_grant_returns_400).
    assert body["detail"]["error"] == "code_exchange_failed"
