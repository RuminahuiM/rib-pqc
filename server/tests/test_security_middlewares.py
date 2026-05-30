"""Tests fuer PQC-80 (CORS), PQC-81 (TrustedHost), PQC-82 (Security-Headers).

Wir bauen Mini-FastAPI-Apps mit jeweils der zu testenden Middleware-Kombination
und verifizieren das Verhalten via TestClient.
"""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from middleware.security_headers import SecurityHeadersMiddleware

# ===========================================================================
# PQC-82 SEC-4: Security-Headers
# ===========================================================================


def _make_app_with_security_headers(
    *,
    hsts_enabled: bool = False,
    hsts_max_age: int = 31536000,
    hsts_include_subdomains: bool = True,
) -> FastAPI:
    app = FastAPI()
    app.add_middleware(
        SecurityHeadersMiddleware,
        hsts_enabled=hsts_enabled,
        hsts_max_age_seconds=hsts_max_age,
        hsts_include_subdomains=hsts_include_subdomains,
    )

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


def test_security_headers_x_content_type_options() -> None:
    """AC-1: X-Content-Type-Options: nosniff."""
    client = TestClient(_make_app_with_security_headers())
    r = client.get("/health")
    assert r.headers["X-Content-Type-Options"] == "nosniff"


def test_security_headers_x_frame_options() -> None:
    """AC-1: X-Frame-Options: DENY."""
    client = TestClient(_make_app_with_security_headers())
    r = client.get("/health")
    assert r.headers["X-Frame-Options"] == "DENY"


def test_security_headers_referrer_policy() -> None:
    """AC-1: Referrer-Policy: no-referrer."""
    client = TestClient(_make_app_with_security_headers())
    r = client.get("/health")
    assert r.headers["Referrer-Policy"] == "no-referrer"


def test_security_headers_hsts_disabled_in_dev() -> None:
    """AC-1: HSTS NICHT gesetzt wenn hsts_enabled=False (Dev-Default)."""
    client = TestClient(_make_app_with_security_headers(hsts_enabled=False))
    r = client.get("/health")
    assert "Strict-Transport-Security" not in r.headers


def test_security_headers_hsts_enabled_with_subdomains() -> None:
    """AC-1: HSTS gesetzt mit max-age + includeSubDomains."""
    client = TestClient(
        _make_app_with_security_headers(
            hsts_enabled=True,
            hsts_max_age=31536000,
            hsts_include_subdomains=True,
        )
    )
    r = client.get("/health")
    assert r.headers["Strict-Transport-Security"] == (
        "max-age=31536000; includeSubDomains"
    )


def test_security_headers_hsts_enabled_without_subdomains() -> None:
    client = TestClient(
        _make_app_with_security_headers(
            hsts_enabled=True,
            hsts_max_age=7200,
            hsts_include_subdomains=False,
        )
    )
    r = client.get("/health")
    assert r.headers["Strict-Transport-Security"] == "max-age=7200"


# ===========================================================================
# PQC-81 SEC-3: TrustedHost
# ===========================================================================


def _make_app_with_trusted_host(allowed: list[str]) -> FastAPI:
    app = FastAPI()

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed)
    return app


def test_trusted_host_allows_listed_host() -> None:
    """AC-2: Allowed-Host wird durchgelassen."""
    client = TestClient(
        _make_app_with_trusted_host(["testserver", "localhost"])
    )
    r = client.get("/health")
    assert r.status_code == 200


def test_trusted_host_rejects_unknown_host() -> None:
    """AC-3: Host-Header 'evil.com' returns 400."""
    client = TestClient(_make_app_with_trusted_host(["testserver"]))
    r = client.get("/health", headers={"Host": "evil.com"})
    assert r.status_code == 400
    assert "Invalid host" in r.text.lower() or "invalid host" in r.text.lower()


# ===========================================================================
# PQC-80 SEC-2: CORS
# ===========================================================================


def _make_app_with_cors(
    *,
    origins: list[str],
    credentials: bool = False,
    methods: list[str] | None = None,
    headers: list[str] | None = None,
) -> FastAPI:
    app = FastAPI()

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_methods=methods or ["GET", "POST", "OPTIONS"],
        allow_headers=headers or ["Authorization", "Content-Type", "X-Request-ID"],
        allow_credentials=credentials,
    )
    return app


def test_cors_allows_listed_origin() -> None:
    """AC-2: Allow-Origin Echo bei allowed origin."""
    client = TestClient(_make_app_with_cors(origins=["http://localhost:8081"]))
    r = client.get(
        "/health", headers={"Origin": "http://localhost:8081"}
    )
    assert r.status_code == 200
    assert r.headers.get("access-control-allow-origin") == "http://localhost:8081"


def test_cors_blocks_unknown_origin() -> None:
    """AC-2: bei unbekanntem Origin kein Allow-Origin-Header (Browser blockt)."""
    client = TestClient(_make_app_with_cors(origins=["http://localhost:8081"]))
    r = client.get(
        "/health", headers={"Origin": "http://evil.com"}
    )
    # Request kommt durch (CORS ist Browser-side), aber kein Allow-Origin-Header
    assert r.status_code == 200
    assert r.headers.get("access-control-allow-origin") is None


def test_cors_preflight_options_returns_headers() -> None:
    """AC-5: Preflight-OPTIONS-Request liefert korrekte Allow-Headers."""
    client = TestClient(
        _make_app_with_cors(
            origins=["http://localhost:8081"],
            methods=["GET", "POST", "OPTIONS"],
            headers=["Authorization", "Content-Type", "X-Request-ID"],
        )
    )
    r = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:8081",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "authorization, content-type",
        },
    )
    assert r.status_code == 200
    assert r.headers["access-control-allow-origin"] == "http://localhost:8081"
    allow_methods = r.headers.get("access-control-allow-methods", "")
    assert "POST" in allow_methods
    allow_headers = r.headers.get("access-control-allow-headers", "")
    assert "Authorization" in allow_headers or "authorization" in allow_headers.lower()


def test_cors_no_wildcard_in_default_config() -> None:
    """AC-3: Default-Origins-Liste enthaelt KEINE Wildcards."""
    from config import CorsConfig

    cfg = CorsConfig()
    assert "*" not in cfg.allowed_origins


def test_cors_wildcard_with_credentials_raises() -> None:
    """AC-3: Pydantic-Validator lehnt Wildcard + allow_credentials=True ab."""
    from config import CorsConfig

    with pytest.raises(ValueError, match="allow_credentials=True"):
        CorsConfig(allowed_origins=["*"], allow_credentials=True)


def test_cors_wildcard_without_credentials_ok() -> None:
    """Wildcard alleine (ohne credentials) ist erlaubt - nicht Best-Practice,
    aber Browser-spec-konform."""
    from config import CorsConfig

    cfg = CorsConfig(allowed_origins=["*"], allow_credentials=False)
    assert cfg.allowed_origins == ["*"]



@pytest.mark.parametrize(
    "method",
    ["GET", "POST", "OPTIONS"],
)
def test_cors_allowed_methods_in_preflight(method: str) -> None:
    """AC-4: GET, POST, OPTIONS sind in den Preflight-Methods."""
    client = TestClient(
        _make_app_with_cors(
            origins=["http://localhost:8081"],
            methods=["GET", "POST", "OPTIONS"],
        )
    )
    r = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:8081",
            "Access-Control-Request-Method": method,
        },
    )
    assert r.status_code == 200
    assert method in r.headers.get("access-control-allow-methods", "")
