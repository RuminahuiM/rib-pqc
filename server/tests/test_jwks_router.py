"""Tests fuer routers/jwks.py.

Story: PQC-35 TOK-4.

Test-Strategie:
- FastAPI TestClient + Stub-Facade mit Mock-Public-Keys (kein liboqs).
- 4 Tests: happy-path, JWK-Felder, Single-Key-Backwards-Compat, Cache-Header.
"""

from __future__ import annotations

import base64

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from routers.jwks import router as jwks_router


class _StubFacade:
    """Minimaler CryptoFacade-Stub mit fester verifying_keys()-Antwort."""

    def __init__(self, keys: dict[str, bytes]) -> None:
        self._keys = dict(keys)

    def verifying_keys(self) -> dict[str, bytes]:
        return dict(self._keys)


def _make_app(keys: dict[str, bytes]) -> FastAPI:
    app = FastAPI()
    app.state.crypto_facade = _StubFacade(keys)
    app.include_router(jwks_router)
    return app


def test_jwks_multi_key_response() -> None:
    """Happy-path: Multi-Key liefert mehrere JWK-Eintraege."""
    keys = {
        "key-v1": b"\x01" * 1952,  # ML-DSA-65 Public-Key-Size 1952 Byte
        "key-v2": b"\x02" * 1952,
    }
    app = _make_app(keys)
    with TestClient(app) as client:
        resp = client.get("/auth/.well-known/jwks.json")
    assert resp.status_code == 200
    body = resp.json()
    assert "keys" in body
    assert len(body["keys"]) == 2
    kids = [k["kid"] for k in body["keys"]]
    assert sorted(kids) == ["key-v1", "key-v2"]


def test_jwks_jwk_fields_rfc7517_compatible() -> None:
    """Jeder JWK-Eintrag hat kty, alg, kid, use, x als Pflicht-Felder."""
    keys = {"only-key": b"\xab" * 1952}
    app = _make_app(keys)
    with TestClient(app) as client:
        resp = client.get("/auth/.well-known/jwks.json")
    assert resp.status_code == 200
    jwk = resp.json()["keys"][0]
    assert jwk["kty"] == "AKP"
    assert jwk["alg"] == "ML-DSA-65"
    assert jwk["kid"] == "only-key"
    assert jwk["use"] == "sig"
    # x ist base64url ohne Padding
    assert "x" in jwk
    assert "=" not in jwk["x"]
    assert "+" not in jwk["x"]
    assert "/" not in jwk["x"]
    # Decode + check Length-Match (1952 byte ML-DSA-65 raw)
    pad = "=" * (-len(jwk["x"]) % 4)
    decoded = base64.urlsafe_b64decode(jwk["x"] + pad)
    assert len(decoded) == 1952
    assert decoded == b"\xab" * 1952


def test_jwks_single_key_backwards_compat() -> None:
    """Single-Key-Setup liefert genau 1 Eintrag."""
    keys = {"auth-signing-key-v1": b"\x55" * 1952}
    app = _make_app(keys)
    with TestClient(app) as client:
        resp = client.get("/auth/.well-known/jwks.json")
    assert resp.status_code == 200
    assert len(resp.json()["keys"]) == 1
    assert resp.json()["keys"][0]["kid"] == "auth-signing-key-v1"


def test_jwks_cache_control_header_set() -> None:
    """Cache-Control mit max-age=3600 ist gesetzt."""
    keys = {"k": b"\x00" * 1952}
    app = _make_app(keys)
    with TestClient(app) as client:
        resp = client.get("/auth/.well-known/jwks.json")
    cache_header = resp.headers.get("cache-control", "")
    assert "max-age=3600" in cache_header
    assert "public" in cache_header
