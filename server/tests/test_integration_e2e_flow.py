"""End-to-End Integration-Test: Local Login -> PQ-Session -> /api/profile.

Story: PQC-67 QUA-5.
Bezug: Erfolgskriterien aus 05_requirements.md 2.3.

**Test-Strategie:**

* Voll-integrierte FastAPI-App: echter Argon2id-Hasher (fast-mode), echte
  User-Repo gegen In-Memory-SQLite, echte CryptoFacade mit liboqs (ML-DSA-65
  + ML-KEM-768), echte SessionService + NonceTracker gegen fakeredis, echter
  TokenService, echte Auth+Session+Api-Router.
* Kein Mock ausser fakeredis fuer den redis-abhaengigen Zustand. Nur die
  Test-Fixtures nutzen Test-Data (kein echter Google/Microsoft-OIDC-Flow -
  der ist in QUA-4/PQC-66 integration-tested).
* Client faehrt die ganze Kette wie ein echter Mobile-Client durch:
  1. POST /auth/local/login -> broker_token
  2. POST /session/init mit ML-KEM-768 Client-Keypair -> session_id + ciphertext
  3. KEM-Decaps + HKDF Client-Side -> session_key (32 Byte)
  4. AES-256-GCM Encrypt Request -> POST /api/profile mit X-Session-Id + X-Nonce
  5. Response-Decrypt -> Profile-JSON
  6. Replay: gleicher Nonce nochmal -> 400 nonce_reused

**Tests:**

1. E2E Happy-Path: alle 6 Schritte gruen.
2. Multi-Session-Isolation: 2 unabhaengige Sessions parallel, keine Crosstalk.
3. Replay-Detection: 2. Request mit gleicher Nonce -> 400.
4. Unknown-Session: /api/profile mit fabrizierter session-id -> 401.

**Sandbox-Verhalten:** liboqs-Skip-Marker (wie test_integration_broker_flow.py).
"""
from __future__ import annotations

import base64
import json
import secrets
from collections.abc import AsyncIterator
from typing import Any

import fakeredis.aioredis
import pytest
import pytest_asyncio
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker
from cryptography.hazmat.primitives import hashes as _hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

try:
    import oqs as _oqs
    _oqs.get_enabled_sig_mechanisms()
    _liboqs_available = True
except (ImportError, RuntimeError, OSError, SystemExit):
    _liboqs_available = False

pytestmark = pytest.mark.skipif(
    not _liboqs_available,
    reason="liboqs shared lib nicht ladbar (Sandbox-Mode). Tests laufen im Docker-Container.",
)

from auth.password import PasswordHasher  # noqa: E402
from config import Argon2Config, SessionConfig  # noqa: E402
from crypto.facade import CryptoFacade  # noqa: E402
from crypto.registry import CryptoRegistry  # noqa: E402
from db.repositories.user_repository import UserRepository  # noqa: E402
from routers import api, auth, session as session_router_module  # noqa: E402
from services.nonce_tracker import RedisNonceTracker  # noqa: E402
from services.session_service import SessionService  # noqa: E402
from services.token_service import TokenService  # noqa: E402


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def redis_all() -> AsyncIterator[fakeredis.aioredis.FakeRedis]:
    """Ein fakeredis-Client fuer Session + Nonce (verschiedene Keys, kein Konflikt)."""
    client = fakeredis.aioredis.FakeRedis()
    try:
        yield client
    finally:
        await client.aclose()


@pytest.fixture
def crypto_facade() -> CryptoFacade:
    from crypto.adapters.liboqs_kem import LibOqsKem
    from crypto.adapters.liboqs_signature import LibOqsSignature

    registry = CryptoRegistry()
    sig_plugin = LibOqsSignature("ML-DSA-65")
    kem_plugin = LibOqsKem("ML-KEM-768")
    registry.register_signature("ML-DSA-65", sig_plugin)
    registry.register_kem("ML-KEM-768", kem_plugin)
    pub, priv = sig_plugin.keygen()
    return CryptoFacade(
        registry=registry,
        default_signature_alg="ML-DSA-65",
        signing_kid="e2e-test-kid",
        signing_secret_key=priv,
        verifying_keys_by_kid={"e2e-test-kid": pub},
    )


@pytest_asyncio.fixture
async def e2e_app(
    redis_all: fakeredis.aioredis.FakeRedis,
    session_factory: async_sessionmaker,
    crypto_facade: CryptoFacade,
    fast_hasher: PasswordHasher,
) -> FastAPI:
    """Voll-integrierte App mit Auth, Session, Api-Routern."""
    app = FastAPI()

    session_service = SessionService(redis_client=redis_all, ttl_seconds=900)
    nonce_tracker = RedisNonceTracker(redis_client=redis_all, ttl_seconds=900)
    token_service = TokenService(
        crypto_facade=crypto_facade,
        issuer="e2e-test",
        ttl_seconds=3600,
        allowed_algs=["ML-DSA-65"],
        exp_leeway_seconds=30,
    )

    class _Settings:
        session = SessionConfig()

    app.state.crypto_facade = crypto_facade
    app.state.session_service = session_service
    app.state.nonce_tracker = nonce_tracker
    app.state.token_service = token_service
    app.state.session_factory = session_factory
    app.state.password_hasher = fast_hasher
    app.state.settings = _Settings()

    app.include_router(auth.router)
    app.include_router(session_router_module.router)
    app.include_router(api.router)
    return app


@pytest_asyncio.fixture
async def _demo_user(session_factory: async_sessionmaker, fast_hasher: PasswordHasher):
    """Legt einen local Demo-User an und liefert (email, password, user_id)."""
    email = "e2e-user@example.com"
    password = "e2e-passwort-super-safe"  # noqa: S105
    pw_hash = fast_hasher.hash(password)
    async with session_factory() as db:
        repo = UserRepository(db)
        user = await repo.create(
            email=email,
            password_hash=pw_hash,
            auth_method="local",
        )
        await db.commit()
        return email, password, user.id


@pytest.fixture
def client(e2e_app: FastAPI) -> TestClient:
    return TestClient(e2e_app)


# ---------------------------------------------------------------------------
# Client-Helper: fahrt die volle E2E-Kette durch, gibt (session_id, session_key, token)
# ---------------------------------------------------------------------------


def _b64url_no_pad(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _b64url_pad(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def _establish_session(client: TestClient, email: str, password: str, oqs_module: Any) -> tuple[str, bytes, str]:
    """Client-side full-flow: login -> keypair -> /session/init -> HKDF -> (id, key, token)."""
    # 1. Login
    r_login = client.post(
        "/auth/local/login",
        json={"email": email, "password": password},
    )
    assert r_login.status_code == 200, r_login.text
    token = r_login.json()["broker_token"]

    # 2. Client-Keypair (echt liboqs)
    with oqs_module.KeyEncapsulation("ML-KEM-768") as kem:
        client_pk = kem.generate_keypair()
        # 3. /session/init
        r_init = client.post(
            "/session/init",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "kem_alg": "ML-KEM-768",
                "encapsulation_key": _b64url_no_pad(client_pk),
            },
        )
        assert r_init.status_code == 200, r_init.text
        body = r_init.json()
        session_id = body["session_id"]
        ct = _b64url_pad(body["ciphertext"])
        # 4. Client-Decaps
        shared_secret = kem.decap_secret(ct)

    # 5. HKDF -> session_key (matched server services/session_key_derivation.py:
    # salt = session_id-ASCII, info = settings.session.hkdf_info default
    # "app-session-v1").
    session_key = HKDF(
        algorithm=_hashes.SHA256(),
        length=32,
        salt=session_id.encode("ascii"),
        info=b"app-session-v1",
    ).derive(shared_secret)

    return session_id, session_key, token


# ---------------------------------------------------------------------------
# Test 1: E2E Happy-Path - alle Schritte gruen
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_e2e_full_happy_path(
    client: TestClient,
    _demo_user: tuple[str, str, str],
) -> None:
    email, password, user_id = _demo_user
    import oqs

    session_id, session_key, _token = _establish_session(client, email, password, oqs)

    # 6. Encrypt request-body ({}, DCH-3 nutzt empty-plaintext)
    nonce = secrets.token_bytes(12)
    aad = session_id.encode("ascii")
    ct_and_tag = AESGCM(session_key).encrypt(nonce, b"{}", aad)

    r_prof = client.post(
        "/api/profile",
        headers={
            "X-Session-Id": session_id,
            "X-Nonce": _b64url_no_pad(nonce),
            "Content-Type": "application/octet-stream",
        },
        content=ct_and_tag,
    )
    assert r_prof.status_code == 200, r_prof.text
    response_nonce = _b64url_pad(r_prof.headers["X-Nonce"])
    plaintext = AESGCM(session_key).decrypt(response_nonce, r_prof.content, aad)
    profile = json.loads(plaintext.decode("utf-8"))
    assert profile["user_id"] == user_id
    assert profile["email"] == email
    assert profile["auth_method"] == "local"


# ---------------------------------------------------------------------------
# Test 2: Replay-Detection (gleiche Nonce zweimal)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_e2e_replay_same_nonce_returns_400(
    client: TestClient,
    _demo_user: tuple[str, str, str],
) -> None:
    email, password, _uid = _demo_user
    import oqs

    session_id, session_key, _token = _establish_session(client, email, password, oqs)
    nonce = secrets.token_bytes(12)
    aad = session_id.encode("ascii")
    ct = AESGCM(session_key).encrypt(nonce, b"{}", aad)
    hdrs = {
        "X-Session-Id": session_id,
        "X-Nonce": _b64url_no_pad(nonce),
        "Content-Type": "application/octet-stream",
    }

    r1 = client.post("/api/profile", headers=hdrs, content=ct)
    assert r1.status_code == 200, r1.text

    r2 = client.post("/api/profile", headers=hdrs, content=ct)
    assert r2.status_code == 400, r2.text
    assert r2.json()["detail"]["error"] == "nonce_reused"


# ---------------------------------------------------------------------------
# Test 3: Unknown-Session -> 401
# ---------------------------------------------------------------------------


def test_e2e_unknown_session_returns_401(
    client: TestClient,
) -> None:
    fake_session_id = _b64url_no_pad(secrets.token_bytes(16))
    nonce = secrets.token_bytes(12)
    r = client.post(
        "/api/profile",
        headers={
            "X-Session-Id": fake_session_id,
            "X-Nonce": _b64url_no_pad(nonce),
            "Content-Type": "application/octet-stream",
        },
        content=b"garbage-body-since-decrypt-cannot-succeed",
    )
    assert r.status_code == 401, r.text


# ---------------------------------------------------------------------------
# Test 4: Multi-Session-Isolation (zwei parallele Sessions, keine Crosstalk)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_e2e_two_sessions_isolated(
    client: TestClient,
    _demo_user: tuple[str, str, str],
) -> None:
    email, password, _uid = _demo_user
    import oqs

    s1_id, s1_key, _ = _establish_session(client, email, password, oqs)
    s2_id, s2_key, _ = _establish_session(client, email, password, oqs)
    assert s1_id != s2_id
    assert s1_key != s2_key

    # Cross-Use: verschluessele mit s1_key aber sende an s2_id. Server-Flow:
    # authenticated_session macht erst session-lookup (s2_id existiert -> ok),
    # dann AEAD-decrypt mit s2_key (schlaegt fehl weil ct mit s1_key
    # verschluesselt). Erwartung: 400 aead_decrypt_failed (matched aktuelle
    # Server-Behavior).
    #
    # BEWUSST DOKUMENTIERT (F-142 in docs/13_deferred_findings.md,
    # SEC-6 Jira-Story fuer Sprint-5-Fix): Die Response-Code-Differenz
    # 401 session_expired (kein Session) vs 400 aead_decrypt_failed
    # (Session vorhanden, falscher Key) ist ein Side-Channel-Info-Leak:
    # Angreifer kann valide session_ids per Response-Code enumerieren.
    # Sauberer Fix in SEC-6: alle POST-existence-check-Errors uniform als
    # 401 authentication_failed. Braucht Test- und App-Side-Impact-Review
    # (secureClient.ts reagiert auf spezifische Error-Strings), daher
    # nicht mehr im Sprint-4-Scope.
    nonce = secrets.token_bytes(12)
    ct_wrong = AESGCM(s1_key).encrypt(nonce, b"{}", s1_id.encode("ascii"))
    r_cross = client.post(
        "/api/profile",
        headers={
            "X-Session-Id": s2_id,
            "X-Nonce": _b64url_no_pad(nonce),
            "Content-Type": "application/octet-stream",
        },
        content=ct_wrong,
    )
    assert r_cross.status_code == 400, r_cross.text
    assert r_cross.json()["detail"]["error"] == "aead_decrypt_failed"
