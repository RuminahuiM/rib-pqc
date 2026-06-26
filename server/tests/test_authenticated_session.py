"""Tests fuer dependencies/authenticated_session.py.

Story: PQC-51 (DCH-2).

Test-Strategie:
- FastAPI-TestClient gegen eine kleine App mit Test-Endpoint ``/api/echo``,
  der ``AuthenticatedSession`` injecten laesst und das Payload zurueckspiegelt.
- fakeredis fuer SessionService (analog test_session_router.py).
- ``_StubFacade`` mit echter AES-256-GCM-Crypto via ``cryptography.hazmat``,
  damit Sandbox-Tests ohne liboqs laufen koennen.
- ``_FakeNonceTracker`` zum expliziten Tracker-Verhalten in einem Test
  (Replay-Trigger).

Detail-AC 1-11 sind im File-Docstring von authenticated_session.py
dokumentiert; jeder Test referenziert die getestete AC im Test-Namen.
"""

from __future__ import annotations

import base64
import json

import pytest
import pytest_asyncio
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

fakeredis_aio = pytest.importorskip(
    "fakeredis.aioredis",
    reason="fakeredis not installed",
)

from crypto.facade import AeadDecryptError  # noqa: E402
from dependencies.authenticated_session import (  # noqa: E402
    AuthenticatedSession,
    authenticated_session,
)
from services.nonce_tracker import NoOpNonceTracker  # noqa: E402
from services.session_service import SessionService  # noqa: E402

# ---------------------------------------------------------------------------
# Stubs + Fixtures
# ---------------------------------------------------------------------------


class _StubFacade:
    """Minimaler CryptoFacade-Stub mit echter AES-256-GCM-Logik.

    Implementiert nur ``aead_decrypt``, was die Dependency nutzt. Echte
    Crypto via ``cryptography.hazmat`` AESGCM. Damit laufen die Tests
    auch in Sandbox-Envs ohne liboqs.
    """

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


class _FakeNonceTracker:
    """In-Memory Nonce-Tracker fuer Replay-Tests.

    PQC-53 DCH-4: atomarer ``check_and_register`` als primary API.
    ``has_seen``/``record`` als Legacy-Stubs erhalten fuer Kompatibilitaet.
    """

    def __init__(self) -> None:
        self._seen: set[tuple[str, bytes]] = set()

    async def check_and_register(self, *, session_id: str, nonce: bytes) -> bool:
        key = (session_id, nonce)
        if key in self._seen:
            return False
        self._seen.add(key)
        return True

    async def has_seen(self, *, session_id: str, nonce: bytes) -> bool:
        return (session_id, nonce) in self._seen

    async def record(self, *, session_id: str, nonce: bytes) -> None:
        self._seen.add((session_id, nonce))


def _b64url(value: bytes) -> str:
    """Encode ``value`` als base64url ohne Padding (passt zu X-Nonce-Konvention)."""
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _b64std(value: bytes) -> str:
    """Encode ``value`` mit Padding (X-Nonce muss auch das tolerieren)."""
    return base64.urlsafe_b64encode(value).decode("ascii")


def _build_app(
    *,
    session_service: SessionService,
    facade: _StubFacade,
    nonce_tracker: object | None = None,
) -> FastAPI:
    """Baut eine FastAPI-App mit Test-Endpoint /api/echo + DCH-2-Dependency."""
    app = FastAPI()
    app.state.crypto_facade = facade
    app.state.session_service = session_service
    app.state.nonce_tracker = nonce_tracker if nonce_tracker is not None else NoOpNonceTracker()

    @app.post("/api/echo")
    async def echo(
        session: AuthenticatedSession = Depends(authenticated_session),
    ) -> dict:
        # Echo zurueck damit Tests die geparsten Payload-Felder pruefen koennen.
        return {
            "user_id": session.record.user_id,
            "kem_alg": session.record.kem_alg,
            "session_id": session.session_id,
            "echo": session.payload,
        }

    return app


@pytest_asyncio.fixture
async def session_setup() -> tuple[SessionService, str, bytes]:
    """Legt einen frischen SessionRecord an und liefert (svc, session_id, key)."""
    svc = SessionService(redis_client=fakeredis_aio.FakeRedis(), ttl_seconds=900)
    session_key = b"\x42" * 32  # 32 Byte fuer AES-256-GCM
    session_id, _ = await svc.create(
        user_id="user-dch2-test",
        kem_alg="ML-KEM-768",
        session_key=session_key,
    )
    return svc, session_id, session_key


def _encrypt_payload(
    *,
    key: bytes,
    nonce: bytes,
    session_id: str,
    payload: dict,
) -> bytes:
    """Helper: erzeugt das Wire-Format-Body-Byte-Blob (ciphertext || tag)."""
    aad = session_id.encode("ascii")
    cipher = AESGCM(key)
    return cipher.encrypt(nonce, json.dumps(payload).encode("utf-8"), aad)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_dch2_happy_path(session_setup: tuple[SessionService, str, bytes]) -> None:
    """Detail-AC 1+8+9: vollstaendiger Wire-Format-Roundtrip."""
    svc, session_id, key = session_setup
    app = _build_app(session_service=svc, facade=_StubFacade())
    nonce = b"\x10" * 12
    payload = {"hello": "world", "n": 42}
    body = _encrypt_payload(key=key, nonce=nonce, session_id=session_id, payload=payload)

    with TestClient(app) as client:
        resp = client.post(
            "/api/echo",
            headers={
                "X-Session-Id": session_id,
                "X-Nonce": _b64url(nonce),
                "Content-Type": "application/octet-stream",
            },
            content=body,
        )
    assert resp.status_code == 200, resp.text
    out = resp.json()
    assert out["user_id"] == "user-dch2-test"
    assert out["kem_alg"] == "ML-KEM-768"
    assert out["session_id"] == session_id
    assert out["echo"] == payload


@pytest.mark.asyncio
async def test_dch2_session_missing_header(
    session_setup: tuple[SessionService, str, bytes],
) -> None:
    """Detail-AC 3: ohne X-Session-Id -> 401 session_missing."""
    svc, _, key = session_setup
    app = _build_app(session_service=svc, facade=_StubFacade())

    with TestClient(app) as client:
        resp = client.post(
            "/api/echo",
            headers={"X-Nonce": _b64url(b"\x00" * 12)},
            content=b"",
        )
    assert resp.status_code == 401
    assert resp.json() == {"detail": {"error": "session_missing"}}


@pytest.mark.asyncio
async def test_dch2_nonce_missing_header(
    session_setup: tuple[SessionService, str, bytes],
) -> None:
    """Detail-AC 4: ohne X-Nonce -> 401 nonce_missing."""
    svc, session_id, _ = session_setup
    app = _build_app(session_service=svc, facade=_StubFacade())

    with TestClient(app) as client:
        resp = client.post(
            "/api/echo",
            headers={"X-Session-Id": session_id},
            content=b"",
        )
    assert resp.status_code == 401
    assert resp.json() == {"detail": {"error": "nonce_missing"}}


@pytest.mark.asyncio
async def test_dch2_nonce_wrong_length(
    session_setup: tuple[SessionService, str, bytes],
) -> None:
    """Detail-AC 5: Nonce nicht 12 Byte -> 400 nonce_format_invalid (F-092)."""
    svc, session_id, _ = session_setup
    app = _build_app(session_service=svc, facade=_StubFacade())

    with TestClient(app) as client:
        resp = client.post(
            "/api/echo",
            headers={
                "X-Session-Id": session_id,
                "X-Nonce": _b64url(b"\x00" * 8),  # 8 statt 12
            },
            content=b"",
        )
    assert resp.status_code == 400
    assert resp.json() == {"detail": {"error": "nonce_format_invalid"}}


@pytest.mark.asyncio
async def test_dch2_nonce_invalid_base64(
    session_setup: tuple[SessionService, str, bytes],
) -> None:
    """Detail-AC 5: Nonce nicht base64-decodierbar -> 400 nonce_format_invalid."""
    svc, session_id, _ = session_setup
    app = _build_app(session_service=svc, facade=_StubFacade())

    with TestClient(app) as client:
        resp = client.post(
            "/api/echo",
            headers={
                "X-Session-Id": session_id,
                "X-Nonce": "@@@not_base64@@@",
            },
            content=b"",
        )
    assert resp.status_code == 400
    assert resp.json() == {"detail": {"error": "nonce_format_invalid"}}


@pytest.mark.asyncio
async def test_dch2_unknown_session_id_returns_expired(
    session_setup: tuple[SessionService, str, bytes],
) -> None:
    """Detail-AC 6: unbekannte session_id -> 401 session_expired (Side-Channel-Schutz)."""
    svc, _, _ = session_setup
    app = _build_app(session_service=svc, facade=_StubFacade())

    with TestClient(app) as client:
        resp = client.post(
            "/api/echo",
            headers={
                "X-Session-Id": "unknown-session-id-xx",
                "X-Nonce": _b64url(b"\x00" * 12),
            },
            content=b"",
        )
    assert resp.status_code == 401
    assert resp.json() == {"detail": {"error": "session_expired"}}


@pytest.mark.asyncio
async def test_dch2_aead_decrypt_tag_mismatch(
    session_setup: tuple[SessionService, str, bytes],
) -> None:
    """Detail-AC 7: getampertes Ciphertext -> 400 aead_decrypt_failed."""
    svc, session_id, key = session_setup
    app = _build_app(session_service=svc, facade=_StubFacade())
    nonce = b"\x11" * 12
    body = _encrypt_payload(key=key, nonce=nonce, session_id=session_id, payload={"a": 1})
    tampered = body[:-1] + bytes([body[-1] ^ 0x01])  # letzten byte flippen (Tag-Bereich)

    with TestClient(app) as client:
        resp = client.post(
            "/api/echo",
            headers={
                "X-Session-Id": session_id,
                "X-Nonce": _b64url(nonce),
            },
            content=tampered,
        )
    assert resp.status_code == 400
    assert resp.json() == {"detail": {"error": "aead_decrypt_failed"}}


@pytest.mark.asyncio
async def test_dch2_aad_mismatch_yields_aead_failed(
    session_setup: tuple[SessionService, str, bytes],
) -> None:
    """Detail-AC 8: falsche AAD -> 400 aead_decrypt_failed.

    Verschluesseln mit einer anderen session_id als AAD, dann mit der echten
    session_id-AAD entschluesseln. Tag-Verifikation schlaegt fehl.
    """
    svc, session_id, key = session_setup
    app = _build_app(session_service=svc, facade=_StubFacade())
    nonce = b"\x12" * 12
    # Mit falscher AAD verschluesseln (irgend ein anderer session_id-String).
    cipher = AESGCM(key)
    wrong_aad = b"some-other-session-id"
    body = cipher.encrypt(nonce, json.dumps({"a": 1}).encode("utf-8"), wrong_aad)

    with TestClient(app) as client:
        resp = client.post(
            "/api/echo",
            headers={
                "X-Session-Id": session_id,
                "X-Nonce": _b64url(nonce),
            },
            content=body,
        )
    assert resp.status_code == 400
    assert resp.json() == {"detail": {"error": "aead_decrypt_failed"}}


@pytest.mark.asyncio
async def test_dch2_payload_not_json(
    session_setup: tuple[SessionService, str, bytes],
) -> None:
    """Detail-AC 9: Plaintext kein UTF-8-JSON -> 400 payload_not_json."""
    svc, session_id, key = session_setup
    app = _build_app(session_service=svc, facade=_StubFacade())
    nonce = b"\x13" * 12
    # Plaintext sind binary bytes die kein UTF-8 sind
    aad = session_id.encode("ascii")
    cipher = AESGCM(key)
    body = cipher.encrypt(nonce, b"\xff\xfe\xfd", aad)

    with TestClient(app) as client:
        resp = client.post(
            "/api/echo",
            headers={
                "X-Session-Id": session_id,
                "X-Nonce": _b64url(nonce),
            },
            content=body,
        )
    assert resp.status_code == 400
    assert resp.json() == {"detail": {"error": "payload_not_json"}}


@pytest.mark.asyncio
async def test_dch2_payload_json_list_rejected(
    session_setup: tuple[SessionService, str, bytes],
) -> None:
    """Detail-AC 9: JSON-Array (kein dict) -> 400 payload_not_json."""
    svc, session_id, key = session_setup
    app = _build_app(session_service=svc, facade=_StubFacade())
    nonce = b"\x14" * 12
    aad = session_id.encode("ascii")
    cipher = AESGCM(key)
    body = cipher.encrypt(nonce, b"[1, 2, 3]", aad)

    with TestClient(app) as client:
        resp = client.post(
            "/api/echo",
            headers={
                "X-Session-Id": session_id,
                "X-Nonce": _b64url(nonce),
            },
            content=body,
        )
    assert resp.status_code == 400
    assert resp.json() == {"detail": {"error": "payload_not_json"}}


@pytest.mark.asyncio
async def test_dch2_nonce_replay_via_tracker(
    session_setup: tuple[SessionService, str, bytes],
) -> None:
    """Detail-AC 10: Replay-Tracker erkennt zweite Verwendung -> 400 nonce_reused.

    Belegt den DCH-4-Hook-Vertrag mit einem FakeNonceTracker. Erst Request OK
    (Nonce wird recorded), zweiter Request mit gleicher Nonce -> 400.
    """
    svc, session_id, key = session_setup
    tracker = _FakeNonceTracker()
    app = _build_app(session_service=svc, facade=_StubFacade(), nonce_tracker=tracker)
    nonce = b"\x15" * 12
    payload = {"x": 1}
    body = _encrypt_payload(key=key, nonce=nonce, session_id=session_id, payload=payload)

    with TestClient(app) as client:
        first = client.post(
            "/api/echo",
            headers={"X-Session-Id": session_id, "X-Nonce": _b64url(nonce)},
            content=body,
        )
        assert first.status_code == 200, first.text

        # Zweiter Request mit identischer Nonce
        replay = client.post(
            "/api/echo",
            headers={"X-Session-Id": session_id, "X-Nonce": _b64url(nonce)},
            content=body,
        )
    assert replay.status_code == 400
    assert replay.json() == {"detail": {"error": "nonce_reused"}}


@pytest.mark.asyncio
async def test_dch2_nonce_with_padding_accepted(
    session_setup: tuple[SessionService, str, bytes],
) -> None:
    """X-Nonce mit Padding-Form `=` muss ebenso akzeptiert werden (Toleranz)."""
    svc, session_id, key = session_setup
    app = _build_app(session_service=svc, facade=_StubFacade())
    nonce = b"\x16" * 12
    body = _encrypt_payload(key=key, nonce=nonce, session_id=session_id, payload={"k": "v"})

    with TestClient(app) as client:
        resp = client.post(
            "/api/echo",
            headers={
                "X-Session-Id": session_id,
                "X-Nonce": _b64std(nonce),  # mit Padding-=
            },
            content=body,
        )
    assert resp.status_code == 200
    assert resp.json()["echo"] == {"k": "v"}


def test_dch2_noop_tracker_default_behaviour() -> None:
    """NoOp: check_and_register=True, has_seen=False, record=no-op.

    Updated PQC-53: check_and_register ist die primary API. NoOp signalisiert
    'jede Nonce ist neu' (= no replay protection, Dev-Default).
    """
    import asyncio

    tracker = NoOpNonceTracker()

    async def run() -> None:
        # Primary API: jede Nonce gilt als "erste Verwendung".
        assert await tracker.check_and_register(session_id="a", nonce=b"x") is True
        assert await tracker.check_and_register(session_id="a", nonce=b"x") is True
        # Legacy-API: has_seen bleibt immer False (NoOp), record ist no-op.
        assert await tracker.has_seen(session_id="a", nonce=b"x") is False
        await tracker.record(session_id="a", nonce=b"x")
        assert await tracker.has_seen(session_id="a", nonce=b"x") is False

    asyncio.run(run())
