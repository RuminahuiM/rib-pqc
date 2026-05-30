"""Tests fuer middleware/request_id.py.

Story: PQC-79 (SEC-1).
AC-1: UUID4 als request_id in structlog.contextvars.
AC-2: X-Request-ID-Header wird uebernommen wenn vorhanden.
AC-3: Response enthaelt X-Request-ID-Header.
AC-4: Alle Logs eines Calls tragen dieselbe request_id.
"""

from __future__ import annotations

import logging
import uuid

import pytest
import structlog
from fastapi import FastAPI
from fastapi.testclient import TestClient

from middleware.request_id import (
    _REQUEST_ID_HEADER,
    RequestIdMiddleware,
    _sanitize_or_generate,
)


@pytest.fixture
def app() -> FastAPI:
    """Minimal-FastAPI-App mit RequestIdMiddleware plus zwei Endpoints."""
    app = FastAPI()
    app.add_middleware(RequestIdMiddleware)

    @app.get("/echo-context")
    async def echo_context() -> dict[str, object]:
        ctx = structlog.contextvars.get_contextvars()
        return {"context_request_id": ctx.get("request_id")}

    @app.get("/log-events")
    async def log_events() -> dict[str, str]:
        # Mehrere Log-Events absetzen, der Test prueft dass alle dieselbe
        # request_id im Context haben (via _events_seen-Fixture).
        log = structlog.get_logger("test.handler")
        log.info("event-one")
        log.info("event-two")
        log.info("event-three")
        return {"status": "ok"}

    return app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    return TestClient(app)


# ---------------------------------------------------------------------------
# _sanitize_or_generate (Unit-Tests)
# ---------------------------------------------------------------------------


def test_sanitize_returns_valid_value() -> None:
    assert _sanitize_or_generate("abc123-XYZ_456") == "abc123-XYZ_456"


def test_sanitize_uuid_passthrough() -> None:
    incoming = "550e8400-e29b-41d4-a716-446655440000"
    assert _sanitize_or_generate(incoming) == incoming


def test_sanitize_rejects_invalid_chars() -> None:
    # Curly-Braces, Newlines, Spaces sollen verworfen werden, neue UUID4
    result = _sanitize_or_generate("evil{injection}")
    assert result != "evil{injection}"
    uuid.UUID(result)  # ist eine UUID


def test_sanitize_rejects_too_long() -> None:
    too_long = "a" * 65
    result = _sanitize_or_generate(too_long)
    assert result != too_long
    uuid.UUID(result)


def test_sanitize_none_generates_uuid() -> None:
    result = _sanitize_or_generate(None)
    uuid.UUID(result)


def test_sanitize_empty_generates_uuid() -> None:
    result = _sanitize_or_generate("")
    uuid.UUID(result)


# ---------------------------------------------------------------------------
# AC-1: UUID4 wird in structlog.contextvars gesetzt
# ---------------------------------------------------------------------------


def test_request_id_set_in_context(client: TestClient) -> None:
    """AC-1: Endpoint sieht ``request_id`` im structlog.contextvars."""
    response = client.get("/echo-context")
    assert response.status_code == 200
    ctx_id = response.json()["context_request_id"]
    assert ctx_id is not None
    uuid.UUID(ctx_id)


def test_request_id_unique_per_request(client: TestClient) -> None:
    """Zwei separate Requests bekommen verschiedene UUIDs."""
    r1 = client.get("/echo-context")
    r2 = client.get("/echo-context")
    assert r1.json()["context_request_id"] != r2.json()["context_request_id"]


# ---------------------------------------------------------------------------
# AC-2: Incoming X-Request-ID wird uebernommen
# ---------------------------------------------------------------------------


def test_incoming_request_id_taken(client: TestClient) -> None:
    """AC-2: wenn X-Request-ID im Request, wird er uebernommen."""
    response = client.get(
        "/echo-context", headers={_REQUEST_ID_HEADER: "client-trace-id-001"}
    )
    assert response.json()["context_request_id"] == "client-trace-id-001"


def test_incoming_invalid_id_rejected_new_generated(client: TestClient) -> None:
    """Wenn eingehende ID ungueltig (z.B. Newline), wird neue generiert."""
    response = client.get(
        "/echo-context", headers={_REQUEST_ID_HEADER: "bad value with spaces"}
    )
    ctx_id = response.json()["context_request_id"]
    assert ctx_id != "bad value with spaces"
    uuid.UUID(ctx_id)


# ---------------------------------------------------------------------------
# AC-3: Response enthaelt X-Request-ID-Header
# ---------------------------------------------------------------------------


def test_response_contains_request_id_header(client: TestClient) -> None:
    """AC-3: Response-Header trägt die gleiche request_id."""
    response = client.get("/echo-context")
    header_id = response.headers.get(_REQUEST_ID_HEADER)
    assert header_id is not None
    assert header_id == response.json()["context_request_id"]


def test_response_echoes_incoming_id(client: TestClient) -> None:
    """Wenn Client X-Request-ID setzt, wird sie im Response gleich zurueckgegeben."""
    response = client.get(
        "/echo-context", headers={_REQUEST_ID_HEADER: "client-trace-id-002"}
    )
    assert response.headers[_REQUEST_ID_HEADER] == "client-trace-id-002"


# ---------------------------------------------------------------------------
# AC-4: Alle Logs einer Anfrage haben dieselbe request_id
# ---------------------------------------------------------------------------


def test_all_logs_share_request_id(
    client: TestClient, caplog: pytest.LogCaptureFixture
) -> None:
    """AC-4: Mehrere Log-Events im selben Request teilen die request_id."""
    # Re-configure structlog so dass es durch caplog laeuft.
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.KeyValueRenderer(key_order=["request_id", "event"]),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
    )

    incoming_id = "test-correlation-001"
    with caplog.at_level(logging.INFO, logger="test.handler"):
        response = client.get(
            "/log-events", headers={_REQUEST_ID_HEADER: incoming_id}
        )
    assert response.status_code == 200

    # caplog enthaelt 3 Records, alle sollten die incoming_id tragen
    relevant_records = [r for r in caplog.records if r.name == "test.handler"]
    assert len(relevant_records) >= 3
    for record in relevant_records:
        # structlog KeyValueRenderer rendert ins .msg-Feld
        assert incoming_id in record.msg, f"missing request_id in: {record.msg}"


# ---------------------------------------------------------------------------
# Context-Isolation: ContextVar ist per asyncio-Task isoliert (PEP 567)
# ---------------------------------------------------------------------------


def test_context_isolation_per_request(client: TestClient) -> None:
    """Zwei sequenzielle Requests bekommen jeweils ihre eigene request_id im Context.

    structlog.contextvars nutzt PEP-567 ``contextvars.ContextVar``, die per
    asyncio-Task isoliert ist. Wir verifizieren das indirekt: zwei sequenzielle
    Requests sehen verschiedene request_ids in /echo-context, also leakt der
    Context nicht zwischen Requests.
    """
    r1 = client.get("/echo-context")
    r2 = client.get("/echo-context")
    assert r1.json()["context_request_id"] != r2.json()["context_request_id"]
    # Header-Echo bestaetigt das Pairing:
    assert r1.json()["context_request_id"] == r1.headers[_REQUEST_ID_HEADER]
    assert r2.json()["context_request_id"] == r2.headers[_REQUEST_ID_HEADER]
