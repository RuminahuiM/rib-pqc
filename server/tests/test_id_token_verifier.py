"""Tests fuer services/id_token_verifier.py.

Story: PQC-38 BRK-3 AC-2..AC-5.

Generiert echte RS256-signierte JWTs mit Test-Keypair via pyjwt + cryptography,
publishet das Public-Key-JWK ueber respx-mock und verifiziert dann.

Algorithm-Pinning, exp/iss/aud/sig-Mismatch werden alle abgedeckt.
"""

from __future__ import annotations

import datetime as dt
from typing import Any
from unittest.mock import AsyncMock

import httpx
import jwt
import pytest
import pytest_asyncio
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from services.id_token_verifier import IdTokenVerifier, IdTokenVerifyError
from services.oidc_jwks_service import JwksFetchError, OidcJwksService

# ---------------------------------------------------------------------------
# Helper: RSA-Keypair + JWK + sign Token
# ---------------------------------------------------------------------------


def _rsa_keypair() -> tuple[rsa.RSAPrivateKey, dict[str, Any]]:
    """Generiert RSA-Keypair + zugehoeriges JWK-Dict (public)."""
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_numbers = private_key.public_key().public_numbers()

    def _b64u_uint(n: int) -> str:
        import base64

        size_bytes = (n.bit_length() + 7) // 8
        return base64.urlsafe_b64encode(n.to_bytes(size_bytes, "big")).rstrip(b"=").decode()

    jwk = {
        "kty": "RSA",
        "kid": "test-key-1",
        "use": "sig",
        "alg": "RS256",
        "n": _b64u_uint(public_numbers.n),
        "e": _b64u_uint(public_numbers.e),
    }
    return private_key, jwk


def _sign_token(
    private_key: rsa.RSAPrivateKey,
    kid: str = "test-key-1",
    *,
    payload_override: dict[str, Any] | None = None,
    alg: str = "RS256",
) -> str:
    """Signiert ein JWT mit dem Test-Private-Key. Default-Claims sind gueltig."""
    now = int(dt.datetime.now(tz=dt.timezone.utc).timestamp())
    payload = {
        "iss": "https://idp.example",
        "aud": "test-client-id",
        "sub": "user-1234",
        "exp": now + 3600,
        "iat": now,
    }
    if payload_override:
        payload.update(payload_override)

    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    return jwt.encode(payload, pem, algorithm=alg, headers={"kid": kid})


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def http_client() -> httpx.AsyncClient:
    client = httpx.AsyncClient(timeout=5.0)
    try:
        yield client
    finally:
        await client.aclose()


@pytest.fixture
def jwks_service(http_client: httpx.AsyncClient) -> OidcJwksService:
    return OidcJwksService(http_client=http_client, cache_ttl_seconds=3600)


@pytest.fixture
def verifier(jwks_service: OidcJwksService) -> IdTokenVerifier:
    return IdTokenVerifier(jwks_service=jwks_service, exp_leeway_seconds=30)


@pytest.fixture
def keypair() -> tuple[rsa.RSAPrivateKey, dict[str, Any]]:
    return _rsa_keypair()


@pytest.fixture
def mocked_jwks_service(keypair: tuple[rsa.RSAPrivateKey, dict[str, Any]]) -> AsyncMock:
    """JWKS-Service-Mock liefert das Public-JWK aus dem keypair."""
    _, jwk = keypair
    svc = AsyncMock(spec=OidcJwksService)
    svc.get_jwks.return_value = {"keys": [jwk]}
    return svc


@pytest.fixture
def verifier_mocked(mocked_jwks_service: AsyncMock) -> IdTokenVerifier:
    return IdTokenVerifier(jwks_service=mocked_jwks_service, exp_leeway_seconds=30)


# ---------------------------------------------------------------------------
# Happy-Path
# ---------------------------------------------------------------------------


async def test_verify_happy_path(
    verifier_mocked: IdTokenVerifier,
    keypair: tuple[rsa.RSAPrivateKey, dict[str, Any]],
) -> None:
    private_key, _ = keypair
    token = _sign_token(private_key)
    payload = await verifier_mocked.verify(
        token=token,
        jwks_uri="https://idp.example/jwks",
        issuer="https://idp.example",
        audience="test-client-id",
        allowed_algs=["RS256"],
    )
    assert payload["sub"] == "user-1234"
    assert payload["iss"] == "https://idp.example"
    assert payload["aud"] == "test-client-id"


# ---------------------------------------------------------------------------
# AC-3: Signature-Mismatch
# ---------------------------------------------------------------------------


async def test_verify_invalid_signature_raises(
    verifier_mocked: IdTokenVerifier,
    keypair: tuple[rsa.RSAPrivateKey, dict[str, Any]],
) -> None:
    private_key, _ = keypair
    token = _sign_token(private_key)
    # Token-Sig tamper: ein Char in der Mitte des Signature-Teils flippen.
    # JWT = header.payload.signature - wir tampern in der Sig (letzter Teil).
    parts = token.split(".")
    sig = parts[2]
    # Char in der Mitte des Sig flippen (Char "A" wird zu "B" oder umgekehrt)
    mid = len(sig) // 2
    tampered_sig = sig[:mid] + ("A" if sig[mid] != "A" else "B") + sig[mid + 1 :]
    tampered = f"{parts[0]}.{parts[1]}.{tampered_sig}"
    with pytest.raises(IdTokenVerifyError) as exc:
        await verifier_mocked.verify(
            token=tampered,
            jwks_uri="https://idp.example/jwks",
            issuer="https://idp.example",
            audience="test-client-id",
            allowed_algs=["RS256"],
        )
    assert exc.value.reason in ("invalid_signature", "invalid_token")


# ---------------------------------------------------------------------------
# AC-4: Expired
# ---------------------------------------------------------------------------


async def test_verify_expired_token_raises(
    verifier_mocked: IdTokenVerifier,
    keypair: tuple[rsa.RSAPrivateKey, dict[str, Any]],
) -> None:
    private_key, _ = keypair
    # exp in der Vergangenheit (jenseits des 30s Leeway)
    now = int(dt.datetime.now(tz=dt.timezone.utc).timestamp())
    token = _sign_token(
        private_key,
        payload_override={"exp": now - 3600, "iat": now - 7200},
    )
    with pytest.raises(IdTokenVerifyError) as exc:
        await verifier_mocked.verify(
            token=token,
            jwks_uri="https://idp.example/jwks",
            issuer="https://idp.example",
            audience="test-client-id",
            allowed_algs=["RS256"],
        )
    assert exc.value.reason == "expired"


# ---------------------------------------------------------------------------
# Algorithm-Pinning
# ---------------------------------------------------------------------------


async def test_disallowed_alg_raises(
    verifier_mocked: IdTokenVerifier,
    keypair: tuple[rsa.RSAPrivateKey, dict[str, Any]],
) -> None:
    """Token mit nicht-erlaubtem alg (z.B. nur RS256 erlaubt, Token ist RS512)."""
    private_key, _ = keypair
    token = _sign_token(private_key, alg="RS512")
    with pytest.raises(IdTokenVerifyError) as exc:
        await verifier_mocked.verify(
            token=token,
            jwks_uri="https://idp.example/jwks",
            issuer="https://idp.example",
            audience="test-client-id",
            allowed_algs=["RS256"],
        )
    assert exc.value.reason == "disallowed_alg"


# ---------------------------------------------------------------------------
# iss/aud-Mismatch
# ---------------------------------------------------------------------------


async def test_invalid_issuer_raises(
    verifier_mocked: IdTokenVerifier,
    keypair: tuple[rsa.RSAPrivateKey, dict[str, Any]],
) -> None:
    private_key, _ = keypair
    token = _sign_token(private_key, payload_override={"iss": "https://evil.example"})
    with pytest.raises(IdTokenVerifyError) as exc:
        await verifier_mocked.verify(
            token=token,
            jwks_uri="https://idp.example/jwks",
            issuer="https://idp.example",
            audience="test-client-id",
            allowed_algs=["RS256"],
        )
    assert exc.value.reason == "invalid_issuer"


async def test_invalid_audience_raises(
    verifier_mocked: IdTokenVerifier,
    keypair: tuple[rsa.RSAPrivateKey, dict[str, Any]],
) -> None:
    private_key, _ = keypair
    token = _sign_token(private_key, payload_override={"aud": "other-client"})
    with pytest.raises(IdTokenVerifyError) as exc:
        await verifier_mocked.verify(
            token=token,
            jwks_uri="https://idp.example/jwks",
            issuer="https://idp.example",
            audience="test-client-id",
            allowed_algs=["RS256"],
        )
    assert exc.value.reason == "invalid_audience"


# ---------------------------------------------------------------------------
# Unknown kid + Force-Refresh
# ---------------------------------------------------------------------------


async def test_unknown_kid_triggers_force_refresh_then_fails(
    mocked_jwks_service: AsyncMock,
    keypair: tuple[rsa.RSAPrivateKey, dict[str, Any]],
) -> None:
    """Verifier soll bei unknown_kid einen Force-Refresh probieren, dann erst fail."""
    private_key, _ = keypair
    token = _sign_token(private_key, kid="non-existent-kid")
    # Mock liefert IMMER nur key-1, also kid-Miss bleibt nach Force-Refresh
    verifier_local = IdTokenVerifier(jwks_service=mocked_jwks_service, exp_leeway_seconds=30)
    with pytest.raises(IdTokenVerifyError) as exc:
        await verifier_local.verify(
            token=token,
            jwks_uri="https://idp.example/jwks",
            issuer="https://idp.example",
            audience="test-client-id",
            allowed_algs=["RS256"],
        )
    assert exc.value.reason == "unknown_kid"
    # Erster Call (cached) + zweiter Call (force_refresh=True)
    assert mocked_jwks_service.get_jwks.await_count == 2


# ---------------------------------------------------------------------------
# JWKS-Fetch-Fehler
# ---------------------------------------------------------------------------


async def test_jwks_fetch_failure_raises_verify_error(
    keypair: tuple[rsa.RSAPrivateKey, dict[str, Any]],
) -> None:
    private_key, _ = keypair
    token = _sign_token(private_key)
    mocked = AsyncMock(spec=OidcJwksService)
    mocked.get_jwks.side_effect = JwksFetchError("network down")
    verifier_local = IdTokenVerifier(jwks_service=mocked, exp_leeway_seconds=30)
    with pytest.raises(IdTokenVerifyError) as exc:
        await verifier_local.verify(
            token=token,
            jwks_uri="https://idp.example/jwks",
            issuer="https://idp.example",
            audience="test-client-id",
            allowed_algs=["RS256"],
        )
    assert exc.value.reason == "jwks_fetch_failed"


# ---------------------------------------------------------------------------
# Malformed token
# ---------------------------------------------------------------------------


async def test_malformed_token_raises(verifier_mocked: IdTokenVerifier) -> None:
    with pytest.raises(IdTokenVerifyError) as exc:
        await verifier_mocked.verify(
            token="not.a.valid.jwt",
            jwks_uri="https://idp.example/jwks",
            issuer="https://idp.example",
            audience="test-client-id",
            allowed_algs=["RS256"],
        )
    assert exc.value.reason == "malformed_token"


# ---------------------------------------------------------------------------
# Constructor
# ---------------------------------------------------------------------------


def test_invalid_leeway_raises(jwks_service: OidcJwksService) -> None:
    with pytest.raises(ValueError):
        IdTokenVerifier(jwks_service=jwks_service, exp_leeway_seconds=-1)
