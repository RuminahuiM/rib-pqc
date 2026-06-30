"""Tests fuer routers/api.py POST /api/profile.

Story: PQC-52 (DCH-3).

Test-Strategie:
- FastAPI TestClient gegen eine kleine App mit dem echten api.router-Modul,
  authenticated_session-Dependency und allen Lifespan-Services als app.state-
  Werten.
- In-Memory SQLite fuer den UserRepository (echter UserRepository via
  session_factory).
- ``_StubFacade`` mit echter AES-256-GCM-Logik via ``cryptography.hazmat``
  (kein liboqs-Skip in Sandbox).
- fakeredis fuer SessionService + RedisNonceTracker.
- Test-Helper baut echten Session-Record + verschluesselt Request mit
  korrekter AAD, decrypted die Response.
"""

from __future__ import annotations

import asyncio
import base64
import json
from datetime import datetime, timezone

import pytest
import pytest_asyncio
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

fakeredis_aio = pytest.importorskip(
    "fakeredis.aioredis",
    reason="fakeredis not installed",
)

from crypto.facade import AeadDecryptError  # noqa: E402
from models import Base  # noqa: E402
from models.user import User  # noqa: E402
from routers.api import router as api_router  # noqa: E402
from services.nonce_tracker import RedisNonceTracker  # noqa: E402
from services.session_service import SessionService  # noqa: E402


# ---------------------------------------------------------------------------
# Stubs + Fixtures
# ---------------------------------------------------------------------------


class _StubFacade:
    """Minimaler CryptoFacade-Stub mit echter AES-256-GCM-Logik + secrets-Nonce."""

    def aead_decrypt(
        self,
        key: bytes,
        nonce: bytes,
        ct: bytes,
        aad: bytes = b"",
    ) -> bytes:
        cipher = AESGCM(key)
        try:
            return cipher.decrypt(nonce, ct, aad if aad else None)
        except InvalidTag as exc:
            raise AeadDecryptError("stub tag mismatch") from exc

    def aead_encrypt(
        self,
        key: bytes,
        nonce: bytes,
        plaintext: bytes,
        aad: bytes = b"",
    ) -> bytes:
        cipher = AESGCM(key)
        return cipher.encrypt(nonce, plaintext, aad if aad else None)

    @staticmethod
    def aead_random_nonce() -> bytes:
        import secrets

        return secrets.token_bytes(12)


def _b64url(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _b64url_decode(value: str) -> bytes:
    pad = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + pad)


def _encrypt_request(
    *,
    key: bytes,
    nonce: bytes,
    session_id: str,
    payload: dict,
) -> bytes:
    aad = session_id.encode("ascii")
    cipher = AESGCM(key)
    return cipher.encrypt(nonce, json.dumps(payload).encode("utf-8"), aad)


@pytest_asyncio.fixture
async def app_setup() -> tuple[FastAPI, SessionService, RedisNonceTracker, User, str, bytes]:
    """Baut eine vollstaendige TestApp mit DB + Session + User-Record."""
    # In-Memory SQLite
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)

    # User anlegen
    async with session_factory() as db:
        user = User(
            id="11111111-1111-1111-1111-111111111111",
            email="alice@example.com",
            auth_method="local",
            password_hash="$argon2id$...$dummy",
            external_sub=None,
            created_at=datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            updated_at=datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    # Session anlegen
    redis_session = fakeredis_aio.FakeRedis()
    redis_replay = fakeredis_aio.FakeRedis()
    svc = SessionService(redis_client=redis_session, ttl_seconds=900)
    session_key = b"\x42" * 32
    session_id, _ = await svc.create(
        user_id=user.id,
        kem_alg="ML-KEM-768",
        session_key=session_key,
    )
    tracker = RedisNonceTracker(redis_client=redis_replay, ttl_seconds=900)

    app = FastAPI()
    app.state.session_factory = session_factory
    app.state.crypto_facade = _StubFacade()
    app.state.session_service = svc
    app.state.nonce_tracker = tracker
    app.include_router(api_router)
    return app, svc, tracker, user, session_id, session_key


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_dch3_happy_path_roundtrip(
    app_setup: tuple[FastAPI, SessionService, RedisNonceTracker, User, str, bytes],
) -> None:
    """AC-1 + AC-2 + AC-3: vollstaendiger Encrypt-Decrypt-Roundtrip."""
    app, _svc, _tracker, user, session_id, key = app_setup
    request_nonce = b"\x10" * 12
    body = _encrypt_request(
        key=key,
        nonce=request_nonce,
        session_id=session_id,
        payload={},
    )

    with TestClient(app) as client:
        resp = client.post(
            "/api/profile",
            headers={
                "X-Session-Id": session_id,
                "X-Nonce": _b64url(request_nonce),
            },
            content=body,
        )
    assert resp.status_code == 200, resp.text
    # Headers
    assert resp.headers["content-type"] == "application/octet-stream"
    resp_nonce = _b64url_decode(resp.headers["x-nonce"])
    assert len(resp_nonce) == 12
    # Body decrypten
    aad = session_id.encode("ascii")
    plaintext = AESGCM(key).decrypt(resp_nonce, resp.content, aad)
    profile = json.loads(plaintext.decode("utf-8"))
    assert profile == {
        "user_id": user.id,
        "email": "alice@example.com",
        "auth_method": "local",
        "created_at": "2026-01-01T12:00:00Z",
    }


@pytest.mark.asyncio
async def test_dch3_request_response_nonces_differ(
    app_setup: tuple[FastAPI, SessionService, RedisNonceTracker, User, str, bytes],
) -> None:
    """Response-Nonce ist nicht gleich Request-Nonce (fresh CSPRNG)."""
    app, _svc, _tracker, _user, session_id, key = app_setup
    request_nonce = b"\x11" * 12
    body = _encrypt_request(
        key=key,
        nonce=request_nonce,
        session_id=session_id,
        payload={},
    )

    with TestClient(app) as client:
        resp = client.post(
            "/api/profile",
            headers={"X-Session-Id": session_id, "X-Nonce": _b64url(request_nonce)},
            content=body,
        )
    assert resp.status_code == 200
    resp_nonce = _b64url_decode(resp.headers["x-nonce"])
    assert resp_nonce != request_nonce


@pytest.mark.asyncio
async def test_dch3_response_nonce_is_tracked(
    app_setup: tuple[FastAPI, SessionService, RedisNonceTracker, User, str, bytes],
) -> None:
    """Detail-AC 6: Response-Nonce wird im Tracker registriert."""
    app, _svc, tracker, _user, session_id, key = app_setup
    request_nonce = b"\x12" * 12
    body = _encrypt_request(
        key=key,
        nonce=request_nonce,
        session_id=session_id,
        payload={},
    )

    with TestClient(app) as client:
        resp = client.post(
            "/api/profile",
            headers={"X-Session-Id": session_id, "X-Nonce": _b64url(request_nonce)},
            content=body,
        )
    assert resp.status_code == 200
    resp_nonce = _b64url_decode(resp.headers["x-nonce"])
    # Tracker hat die Response-Nonce gespeichert: zweiter check_and_register
    # mit derselben Nonce muss False liefern.
    second = await tracker.check_and_register(
        session_id=session_id, nonce=resp_nonce
    )
    assert second is False


@pytest.mark.asyncio
async def test_dch3_user_not_found_returns_401_plaintext(
    app_setup: tuple[FastAPI, SessionService, RedisNonceTracker, User, str, bytes],
) -> None:
    """Detail-AC 3: User geloescht / nicht vorhanden -> 401 plaintext."""
    app, svc, _tracker, _user, _existing_session, key = app_setup

    # Neue Session mit non-existent user_id
    new_session_id, _ = await svc.create(
        user_id="00000000-0000-0000-0000-000000000000",
        kem_alg="ML-KEM-768",
        session_key=key,
    )
    request_nonce = b"\x13" * 12
    body = _encrypt_request(
        key=key,
        nonce=request_nonce,
        session_id=new_session_id,
        payload={},
    )

    with TestClient(app) as client:
        resp = client.post(
            "/api/profile",
            headers={"X-Session-Id": new_session_id, "X-Nonce": _b64url(request_nonce)},
            content=body,
        )
    assert resp.status_code == 401
    assert resp.json() == {"detail": {"error": "user_not_found"}}


@pytest.mark.asyncio
async def test_dch3_smoke_session_missing_header(
    app_setup: tuple[FastAPI, SessionService, RedisNonceTracker, User, str, bytes],
) -> None:
    """Delegation an DCH-2: ohne X-Session-Id -> 401 session_missing."""
    app, *_ = app_setup
    with TestClient(app) as client:
        resp = client.post("/api/profile", content=b"")
    assert resp.status_code == 401
    assert resp.json() == {"detail": {"error": "session_missing"}}


@pytest.mark.asyncio
async def test_dch3_smoke_replay_request_nonce_returns_400(
    app_setup: tuple[FastAPI, SessionService, RedisNonceTracker, User, str, bytes],
) -> None:
    """Delegation an DCH-2 + DCH-4: identische Request-Nonce zweimal -> 400 nonce_reused.

    Auch belegt: keine Cross-Talk zwischen Request- und Response-Nonce
    Tracker-Slots (jede ist eigener Key).
    """
    app, _svc, _tracker, _user, session_id, key = app_setup
    request_nonce = b"\x14" * 12
    body = _encrypt_request(
        key=key,
        nonce=request_nonce,
        session_id=session_id,
        payload={},
    )

    with TestClient(app) as client:
        first = client.post(
            "/api/profile",
            headers={"X-Session-Id": session_id, "X-Nonce": _b64url(request_nonce)},
            content=body,
        )
        assert first.status_code == 200
        second = client.post(
            "/api/profile",
            headers={"X-Session-Id": session_id, "X-Nonce": _b64url(request_nonce)},
            content=body,
        )
    assert second.status_code == 400
    assert second.json() == {"detail": {"error": "nonce_reused"}}


@pytest.mark.asyncio
async def test_dch3_response_body_is_not_plaintext_json(
    app_setup: tuple[FastAPI, SessionService, RedisNonceTracker, User, str, bytes],
) -> None:
    """AC-3: Response-Body ist verschluesselt (kein Klartext-JSON sichtbar).

    Manuelle Verifikation aus UC-5: Wireshark-Capture-Pendant.
    Wir pruefen hier: bytes(profile-JSON) nicht im response.content enthalten.
    """
    app, _svc, _tracker, user, session_id, key = app_setup
    request_nonce = b"\x15" * 12
    body = _encrypt_request(
        key=key,
        nonce=request_nonce,
        session_id=session_id,
        payload={},
    )

    with TestClient(app) as client:
        resp = client.post(
            "/api/profile",
            headers={"X-Session-Id": session_id, "X-Nonce": _b64url(request_nonce)},
            content=body,
        )
    assert resp.status_code == 200
    # Klartext-Email darf nicht im verschluesselten Body sein.
    assert user.email.encode("utf-8") not in resp.content
    assert b"local" not in resp.content
