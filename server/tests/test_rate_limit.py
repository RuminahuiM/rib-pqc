"""Tests fuer PQC-83 (SEC-5) Rate-Limiting.

Wir bauen Mini-FastAPI-Apps mit einer test-lokalen ``Limiter``-Instanz mit
``storage_uri="memory://"`` (keine Redis-Abhaengigkeit). Das Module-level
Singleton aus ``middleware.rate_limit`` wird in den Tests NICHT verwendet,
weil es bei Import bereits aus den realen Settings instantiiert wurde und
gegen Redis sprechen wuerde.

Test-Strategie:
- ``register_rate_limit`` haengt das module-level limiter an app.state und
  registriert Middleware + Exception-Handler. Smoke-Check.
- Endpoint mit lokalem ``@limiter.limit("N/period")`` triggert 429 nach N Calls.
- 429-Response hat ``Retry-After``-Header und JSON-Body
  ``{"error": "rate_limit_exceeded", "retry_after": <int>}``.
- ``limiter.enabled = False`` deaktiviert Rate-Limit vollstaendig (Sandbox/Test).
- Per-IP-Isolation: Unterschiedliche key_func-Returns ergeben unabhaengige
  Buckets.
"""

from __future__ import annotations

from typing import Any

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from middleware.rate_limit import (
    _rate_limit_exceeded_handler,
    register_rate_limit,
)
from middleware.rate_limit import (
    limiter as module_limiter,
)

# ---------------------------------------------------------------------------
# Helper: Mini-App-Factory mit test-lokalem Limiter
# ---------------------------------------------------------------------------


def _make_app(
    *,
    limit: str = "2/minute",
    key_func: Any = None,
    enabled: bool = True,
) -> tuple[FastAPI, Limiter]:
    """Baut eine Mini-FastAPI-App mit einem frischen, in-memory Limiter.

    Wir registrieren Middleware + Exception-Handler manuell (statt
    register_rate_limit), weil register_rate_limit das module-level Singleton
    nutzt, das gegen Redis spricht.
    """
    if key_func is None:
        # Default: feste Test-Key fuer reproduzierbare Counter.
        # WICHTIG: Parameter MUSS "request" heissen, weil slowapi via
        # inspect.signature(key_func).parameters prueft, ob das Argument
        # "request" vorhanden ist und nur dann den Request uebergibt.
        def key_func(request: Request) -> str:
            return "test-client"

    test_limiter = Limiter(
        key_func=key_func,
        storage_uri="memory://",
        enabled=enabled,
    )

    app = FastAPI()
    app.state.limiter = test_limiter
    app.add_middleware(SlowAPIMiddleware)
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    @app.get("/ping")
    @test_limiter.limit(limit)
    async def ping(request: Request) -> dict[str, str]:
        del request  # slowapi braucht request im Signature, wir nicht
        return {"ok": "true"}

    return app, test_limiter


# ---------------------------------------------------------------------------
# AC-1 / Setup: register_rate_limit installiert Limiter, Middleware, Handler
# ---------------------------------------------------------------------------


def test_register_rate_limit_installs_state_and_handler() -> None:
    """register_rate_limit haengt module_limiter an app.state und registriert
    SlowAPIMiddleware und RateLimitExceeded-Handler.
    """
    app = FastAPI()
    register_rate_limit(app)

    assert app.state.limiter is module_limiter
    # Exception-Handler registriert?
    assert RateLimitExceeded in app.exception_handlers
    # Middleware registriert? (Starlette speichert in user_middleware)
    middleware_cls = [m.cls for m in app.user_middleware]
    assert SlowAPIMiddleware in middleware_cls


# ---------------------------------------------------------------------------
# AC-2 / AC-3: Limit-Hit triggert 429
# ---------------------------------------------------------------------------


def test_rate_limit_allows_under_limit() -> None:
    """Unter dem Limit: alle Requests liefern 200."""
    app, _ = _make_app(limit="3/minute")
    client = TestClient(app)
    for _ in range(3):
        r = client.get("/ping")
        assert r.status_code == 200, f"unerwarteter Status {r.status_code}: {r.text}"


def test_rate_limit_blocks_over_limit() -> None:
    """4. Request bei limit=3/minute liefert 429."""
    app, _ = _make_app(limit="3/minute")
    client = TestClient(app)
    for _ in range(3):
        assert client.get("/ping").status_code == 200
    r = client.get("/ping")
    assert r.status_code == 429


# ---------------------------------------------------------------------------
# AC-4: 429-Response-Format (Retry-After-Header + JSON-Body)
# ---------------------------------------------------------------------------


def test_rate_limit_response_has_retry_after_header() -> None:
    """429-Response enthaelt Retry-After-Header (RFC 6585)."""
    app, _ = _make_app(limit="1/minute")
    client = TestClient(app)
    assert client.get("/ping").status_code == 200
    r = client.get("/ping")
    assert r.status_code == 429
    assert "Retry-After" in r.headers
    # Wert muss ein positiver Integer sein
    retry_after = int(r.headers["Retry-After"])
    assert retry_after > 0


def test_rate_limit_response_json_body_format() -> None:
    """429-Response-Body: {"error": "rate_limit_exceeded", "retry_after": <int>}."""
    app, _ = _make_app(limit="1/minute")
    client = TestClient(app)
    assert client.get("/ping").status_code == 200
    r = client.get("/ping")
    assert r.status_code == 429
    body = r.json()
    assert body["error"] == "rate_limit_exceeded"
    assert isinstance(body["retry_after"], int)
    assert body["retry_after"] > 0


# ---------------------------------------------------------------------------
# Sandbox/Test: enabled=False deaktiviert Limit
# ---------------------------------------------------------------------------


def test_rate_limit_disabled_bypasses_all_limits() -> None:
    """Mit enabled=False werden Limits nicht enforced (fuer Tests/Sandbox)."""
    app, _ = _make_app(limit="1/minute", enabled=False)
    client = TestClient(app)
    # Auch nach 10 Calls noch 200
    for _ in range(10):
        r = client.get("/ping")
        assert r.status_code == 200


# ---------------------------------------------------------------------------
# Per-IP-Isolation: Unterschiedliche key_func-Returns -> unabhaengige Buckets
# ---------------------------------------------------------------------------


def test_rate_limit_per_key_isolation() -> None:
    """Zwei verschiedene IPs (simuliert via Header) haben unabhaengige Limits.

    Wir nutzen einen custom key_func, der ``X-Test-Client`` aus dem Header
    nimmt, weil get_remote_address in TestClient immer ``testclient`` liefert
    und wir den Per-IP-Effekt nicht ueber HTTP nachstellen koennen.
    """

    def key_from_header(request: Request) -> str:
        return request.headers.get("X-Test-Client", "anon")

    app, _ = _make_app(limit="2/minute", key_func=key_from_header)
    client = TestClient(app)

    # Client A schoepft Limit aus
    for _ in range(2):
        assert client.get("/ping", headers={"X-Test-Client": "ip-a"}).status_code == 200
    assert client.get("/ping", headers={"X-Test-Client": "ip-a"}).status_code == 429

    # Client B hat eigenen Bucket, ist NICHT geblockt
    assert client.get("/ping", headers={"X-Test-Client": "ip-b"}).status_code == 200
    assert client.get("/ping", headers={"X-Test-Client": "ip-b"}).status_code == 200
    # Aber dritter Call von B wird auch geblockt
    assert client.get("/ping", headers={"X-Test-Client": "ip-b"}).status_code == 429


# ---------------------------------------------------------------------------
# Exception-Handler: Direktaufruf liefert korrekt geformte Response
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_handler_returns_correct_response_shape() -> None:
    """_rate_limit_exceeded_handler liefert 429 + JSON + Retry-After-Header.

    Wir bauen ein echtes RateLimitExceeded via Limiter, das die internen
    Felder (limit, retry_after) korrekt populiert.
    """
