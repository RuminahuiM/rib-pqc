"""Tests fuer routers/session.py.

Story: PQC-46 SES-1 (FR-Session-1, UC-4).

Test-Strategie:
- httpx-AsyncClient + ASGI-Transport gegen FastAPI-App.
- fakeredis fuer SessionService.
- Mock-CryptoFacade die kem_encaps deterministisch macht (keine echte
  liboqs noetig, das ist in CRY-4 getestet).
- Mock-TokenService das Claims liefert ohne echte Crypto.
"""

from __future__ import annotations

import base64
from typing import TYPE_CHECKING, Any

import pytest

fakeredis_aio = pytest.importorskip(
    "fakeredis.aioredis",
    reason="fakeredis not installed",
)

from fastapi import FastAPI  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402

from config import SessionConfig  # noqa: E402
from routers.session import router as session_router  # noqa: E402
from services.session_service import SessionService  # noqa: E402
from services.token_service import (  # noqa: E402
    ExpiredTokenError,
    InvalidSignatureError,
)

if TYPE_CHECKING:
    pass


# --- Mocks ---


class _MockFacade:
    """CryptoFacade-Mock fuer Router-Tests ohne liboqs.

    kem_encaps liefert deterministische (ciphertext, shared_secret), damit
    Tests die HKDF-Pipeline gegen feste Werte verifizieren koennen.
    hkdf delegiert an cryptography.hazmat (echte HKDF).
    """

    def __init__(self, supported: list[str] | None = None) -> None:
        self._supported = supported if supported is not None else ["ML-KEM-768", "ML-KEM-1024"]

    def supported_kem_algorithms(self) -> list[str]:
        return sorted(self._supported)

    def is_kem_supported(self, alg: str) -> bool:
        return alg in self._supported

    def kem_encaps(self, public_key: bytes, alg: str) -> tuple[bytes, bytes]:
        # Deterministische Test-Outputs basierend auf alg.
        if alg == "ML-KEM-768":
            return b"\x01" * 1088, b"\x02" * 32
        if alg == "ML-KEM-1024":
            return b"\x03" * 1568, b"\x04" * 32
        msg = f"Mock does not support {alg}"
        raise ValueError(msg)

    def hkdf(self, ikm: bytes, info: bytes, salt: bytes, length: int = 32) -> bytes:
        # Echte HKDF aus cryptography.hazmat.
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.kdf.hkdf import HKDF

        return HKDF(algorithm=hashes.SHA256(), length=length, salt=salt, info=info).derive(ikm)


class _MockTokenServiceOK:
    """TokenService-Mock der jeden Token als gueltig akzeptiert."""

    def verify(self, token_str: str) -> dict[str, Any]:
        del token_str
        return {"sub": "user-test-1", "iss": "pqc-auth-service", "iat": 1, "exp": 2**31}


class _MockTokenServiceInvalid:
    """TokenService-Mock der jeden Token mit InvalidSignatureError ablehnt."""

    def verify(self, token_str: str) -> dict[str, Any]:
        del token_str
        msg = "mock-invalid"
        raise InvalidSignatureError(msg)


class _MockTokenServiceExpired:
    """TokenService-Mock fuer Expired-Token-Test."""

    def verify(self, token_str: str) -> dict[str, Any]:
        del token_str
        msg = "mock-expired"
        raise ExpiredTokenError(msg)


# --- Fixtures ---


@pytest.fixture
async def session_service() -> SessionService:
    return SessionService(redis_client=fakeredis_aio.FakeRedis(), ttl_seconds=900)


def _build_app(
    *,
    facade: _MockFacade,
    session_service: SessionService,
    token_service: Any,
) -> FastAPI:
    app = FastAPI()

    class _Settings:
        session = SessionConfig()

    app.state.crypto_facade = facade
    app.state.session_service = session_service
    app.state.token_service = token_service
    app.state.settings = _Settings()
    app.include_router(session_router)
    return app


@pytest.fixture
async def client_ok(session_service: SessionService) -> AsyncClient:
    app = _build_app(
        facade=_MockFacade(),
        session_service=session_service,
        token_service=_MockTokenServiceOK(),
    )
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


def _valid_pk_b64(alg: str) -> str:
    """Erzeugt einen base64url-codierten Pseudo-Public-Key der korrekten Laenge."""
    sizes = {"ML-KEM-768": 1184, "ML-KEM-1024": 1568}
    pk_bytes = b"\x05" * sizes[alg]
    return base64.urlsafe_b64encode(pk_bytes).decode("ascii").rstrip("=")


# --- AC-1 + AC-2 + AC-3 + AC-4 Happy-Path ---


@pytest.mark.asyncio
async def test_session_init_happy_path_ml_kem_768(client_ok: AsyncClient) -> None:
    resp = await client_ok.post(
        "/session/init",
        headers={"Authorization": "Bearer dummy-token"},
        json={
            "kem_alg": "ML-KEM-768",
            "encapsulation_key": _valid_pk_b64("ML-KEM-768"),
        },
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["kem_alg"] == "ML-KEM-768"
    assert body["expires_in"] == 900
    assert isinstance(body["session_id"], str)
    assert len(body["session_id"]) == 22
    assert isinstance(body["ciphertext"], str)
    # ML-KEM-768 ciphertext ist 1088 Byte -> base64url-ohne-Padding ~1451 chars
    assert len(body["ciphertext"]) > 1400


@pytest.mark.asyncio
async def test_session_init_happy_path_ml_kem_1024(client_ok: AsyncClient) -> None:
    resp = await client_ok.post(
        "/session/init",
        headers={"Authorization": "Bearer dummy-token"},
        json={
            "kem_alg": "ML-KEM-1024",
            "encapsulation_key": _valid_pk_b64("ML-KEM-1024"),
        },
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["kem_alg"] == "ML-KEM-1024"


@pytest.mark.asyncio
async def test_session_init_persists_session_in_redis(
    client_ok: AsyncClient, session_service: SessionService
) -> None:
    """AC-4: Session wird im Redis-Store mit TTL gespeichert."""
    resp = await client_ok.post(
        "/session/init",
        headers={"Authorization": "Bearer dummy-token"},
        json={"kem_alg": "ML-KEM-768", "encapsulation_key": _valid_pk_b64("ML-KEM-768")},
    )
    assert resp.status_code == 200
    session_id = resp.json()["session_id"]

    record = await session_service.get(session_id)
    assert record.user_id == "user-test-1"
    assert record.kem_alg == "ML-KEM-768"
    assert len(record.session_key) == 32


# --- AC-2: Token-Verify ---


@pytest.mark.asyncio
async def test_session_init_missing_auth_returns_401(session_service: SessionService) -> None:
    app = _build_app(
        facade=_MockFacade(),
        session_service=session_service,
        token_service=_MockTokenServiceOK(),
    )
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.post(
            "/session/init",
            json={"kem_alg": "ML-KEM-768", "encapsulation_key": _valid_pk_b64("ML-KEM-768")},
        )
    assert resp.status_code == 401
    assert resp.json()["detail"]["error"] == "invalid_token"
    assert resp.headers.get("www-authenticate") == "Bearer"


@pytest.mark.asyncio
async def test_session_init_invalid_signature_returns_401(
    session_service: SessionService,
) -> None:
    app = _build_app(
        facade=_MockFacade(),
        session_service=session_service,
        token_service=_MockTokenServiceInvalid(),
    )
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.post(
            "/session/init",
            headers={"Authorization": "Bearer bad-token"},
            json={"kem_alg": "ML-KEM-768", "encapsulation_key": _valid_pk_b64("ML-KEM-768")},
        )
    assert resp.status_code == 401
    assert resp.json()["detail"]["error"] == "invalid_token"


@pytest.mark.asyncio
async def test_session_init_expired_token_returns_401(
    session_service: SessionService,
) -> None:
    app = _build_app(
        facade=_MockFacade(),
        session_service=session_service,
        token_service=_MockTokenServiceExpired(),
    )
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.post(
            "/session/init",
            headers={"Authorization": "Bearer expired-token"},
            json={"kem_alg": "ML-KEM-768", "encapsulation_key": _valid_pk_b64("ML-KEM-768")},
        )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_session_init_non_bearer_scheme_returns_401(
    session_service: SessionService,
) -> None:
    app = _build_app(
        facade=_MockFacade(),
        session_service=session_service,
        token_service=_MockTokenServiceOK(),
    )
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.post(
            "/session/init",
            headers={"Authorization": "Basic dXNlcjpwYXNz"},
            json={"kem_alg": "ML-KEM-768", "encapsulation_key": _valid_pk_b64("ML-KEM-768")},
        )
    assert resp.status_code == 401


# --- SES-4 Negotiation: 406 bei unbekanntem kem_alg ---


@pytest.mark.asyncio
async def test_session_init_unknown_kem_alg_returns_406(client_ok: AsyncClient) -> None:
    resp = await client_ok.post(
        "/session/init",
        headers={"Authorization": "Bearer dummy"},
        json={"kem_alg": "Kyber768", "encapsulation_key": _valid_pk_b64("ML-KEM-768")},
    )
    assert resp.status_code == 406
    body = resp.json()
    assert body["detail"]["error"] == "kem_alg_not_supported"
    assert body["detail"]["requested"] == "Kyber768"
    assert "ML-KEM-768" in body["detail"]["supported_algorithms"]


# --- 400 invalid_encapsulation_key ---


@pytest.mark.asyncio
async def test_session_init_invalid_base64_returns_400(client_ok: AsyncClient) -> None:
    resp = await client_ok.post(
        "/session/init",
        headers={"Authorization": "Bearer dummy"},
        json={"kem_alg": "ML-KEM-768", "encapsulation_key": "not!valid@base64"},
    )
    assert resp.status_code == 400
    assert resp.json()["detail"]["error"] == "invalid_encapsulation_key"


@pytest.mark.asyncio
async def test_session_init_wrong_pk_length_returns_400(client_ok: AsyncClient) -> None:
    """ML-KEM-768 erwartet 1184 Byte. Wir senden zu kurzen Key."""
    short_pk = base64.urlsafe_b64encode(b"\x00" * 100).decode("ascii").rstrip("=")
    resp = await client_ok.post(
        "/session/init",
        headers={"Authorization": "Bearer dummy"},
        json={"kem_alg": "ML-KEM-768", "encapsulation_key": short_pk},
    )
    assert resp.status_code == 400
    body = resp.json()["detail"]
    assert body["error"] == "invalid_encapsulation_key"
    assert body["reason"] == "length_mismatch"
    assert body["expected_bytes"] == 1184


# --- Pydantic-Validation (missing fields) ---


@pytest.mark.asyncio
async def test_session_init_empty_kem_alg_returns_422(client_ok: AsyncClient) -> None:
    resp = await client_ok.post(
        "/session/init",
        headers={"Authorization": "Bearer dummy"},
        json={"kem_alg": "", "encapsulation_key": _valid_pk_b64("ML-KEM-768")},
    )
    assert resp.status_code == 422  # Pydantic min_length=1


@pytest.mark.asyncio
async def test_session_init_missing_body_field_returns_422(client_ok: AsyncClient) -> None:
    resp = await client_ok.post(
        "/session/init",
        headers={"Authorization": "Bearer dummy"},
        json={"kem_alg": "ML-KEM-768"},  # encapsulation_key fehlt
    )
    assert resp.status_code == 422


# --- PQC-49 SES-4: Dezidierte Algorithmus-Negotiation-Tests --------------------


@pytest.mark.asyncio
async def test_ses4_mismatch_response_includes_supported_algorithms_list(
    session_service: SessionService,
) -> None:
    """SES-4 AC-1 + AC-3: Server muss bei nicht-unterstuetztem kem_alg eine
    406-Response mit der vollstaendigen supported_algorithms-Liste liefern,
    damit der Client einen Retry-Algorithmus waehlen kann.

    Mismatch-Scenario explizit konfiguriert: Server unterstuetzt nur
    ML-KEM-768, Client fragt Kyber768 (Pre-Standard) an.
    """
    facade = _MockFacade(supported=["ML-KEM-768"])  # nur eine Variante
    app = _build_app(
        facade=facade,
        session_service=session_service,
        token_service=_MockTokenServiceOK(),
    )
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.post(
            "/session/init",
            headers={"Authorization": "Bearer dummy"},
            json={
                "kem_alg": "Kyber768",  # Pre-Standard-Name, nicht in Whitelist
                "encapsulation_key": _valid_pk_b64("ML-KEM-768"),
            },
        )

    assert resp.status_code == 406
    detail = resp.json()["detail"]
    assert detail["error"] == "kem_alg_not_supported"
    assert detail["requested"] == "Kyber768"
    # supported_algorithms muss vollstaendig sein, nicht nur teilweise
    assert detail["supported_algorithms"] == ["ML-KEM-768"]


@pytest.mark.asyncio
async def test_ses4_client_retry_after_406_succeeds(
    session_service: SessionService,
) -> None:
    """SES-4 AC-2 (Server-Side): Wenn der Client den 406-Response liest und
    mit einem unterstuetzten Algorithmus retried, muss der Server die Session
    erfolgreich initialisieren.

    Simulation des Client-Retry-Patterns: zwei aufeinanderfolgende Requests,
    erst mit nicht-unterstuetztem alg (406), dann mit unterstuetztem (200).
    App-seitiger Retry-Code ist Sache von PQC-26 CRY-6 (F-098, F-103).
    """
    facade = _MockFacade(supported=["ML-KEM-768"])
    app = _build_app(
        facade=facade,
        session_service=session_service,
        token_service=_MockTokenServiceOK(),
    )
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Erster Request: Mismatch -> 406
        resp_mismatch = await ac.post(
            "/session/init",
            headers={"Authorization": "Bearer dummy"},
            json={
                "kem_alg": "ML-KEM-1024",  # Server unterstuetzt nur ML-KEM-768
                "encapsulation_key": _valid_pk_b64("ML-KEM-1024"),
            },
        )
        assert resp_mismatch.status_code == 406
        supported = resp_mismatch.json()["detail"]["supported_algorithms"]
        assert "ML-KEM-768" in supported

        # Zweiter Request: Retry mit dem Server-vorgeschlagenen Algorithmus.
        chosen_alg = supported[0]
        resp_retry = await ac.post(
            "/session/init",
            headers={"Authorization": "Bearer dummy"},
            json={
                "kem_alg": chosen_alg,
                "encapsulation_key": _valid_pk_b64(chosen_alg),
            },
        )
        assert resp_retry.status_code == 200
        assert resp_retry.json()["kem_alg"] == chosen_alg
