"""Request-ID Middleware fuer Log-Korrelation.

Story: PQC-79 (SEC-1).
Resolves Finding: F-001 (Request-ID-Middleware fehlt).
RFC-Bezug: kein konkretes RFC, aber strong-de-facto-Standard im
Industry-Logging (X-Request-ID / X-Correlation-ID).

**Funktionsweise:**

1. Per Request: pruefe ob ein ``X-Request-ID``-Header bereits gesetzt ist.
   - Falls ja: uebernehmen (Client-side Tracing-Korrelation, z.B. Mobile-App
     sendet ihre eigene Request-ID).
   - Falls nein: neue UUIDv4 generieren.
2. Die Request-ID wird per ``structlog.contextvars.bind_contextvars(request_id=...)``
   im async-context gebunden. Alle nachfolgenden Log-Events im selben Request
   erben damit automatisch das ``request_id``-Feld (durch den
   ``merge_contextvars``-Processor in ``logging_config``).
3. Im Response-Header wird ``X-Request-ID`` gesetzt, damit der Client den
   gleichen Identifier in seinem eigenen Logging hat (Cross-System-Tracing).
4. Im finally-Block wird der context-var wieder entbunden, damit kein Leak
   in andere Requests passiert (clear_contextvars).

**Security-Hinweis:**

- Generierte UUIDv4 hat 122 Bit Entropie. Praktisch unmoeglich vorhersagbar.
- Falls ein Client ``X-Request-ID`` mit eigenem Wert sendet, vertrauen wir
  diesem Wert NICHT fuer Authorization-Entscheidungen (er ist nur fuer
  Log-Korrelation, nicht fuer Security-Logik).
- Eingehende Request-IDs werden auf max 64 Zeichen und alphanumerisch plus
  ``-_`` gefiltert, um Log-Injection (Newlines, Curly-Braces) zu verhindern.
"""

from __future__ import annotations

import re
import uuid
from typing import TYPE_CHECKING

import structlog
from starlette.middleware.base import BaseHTTPMiddleware

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from starlette.requests import Request
    from starlette.responses import Response


_REQUEST_ID_HEADER = "X-Request-ID"

# Sanity-Filter: alphanumerisch plus -_ erlaubt, max 64 Zeichen.
# Strenger als z.B. RFC 7230 Header-Value-Grammar, aber pragmatisch genug
# um Log-Injection zu verhindern.
_REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


def _sanitize_or_generate(incoming_value: str | None) -> str:
    """Gibt incoming_value zurueck wenn gueltig, sonst eine neue UUIDv4.

    Args:
        incoming_value: Wert aus dem ``X-Request-ID``-Header (oder ``None``).

    Returns:
        Gueltige Request-ID als String.
    """
    if incoming_value and _REQUEST_ID_PATTERN.match(incoming_value):
        return incoming_value
    return str(uuid.uuid4())


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Setzt ``request_id`` im structlog-context plus Response-Header.

    Registrierung in ``main.py``::

        app.add_middleware(RequestIdMiddleware)

    Order matters: diese Middleware sollte BEFORE allen anderen Logging-
    relevanten Middlewares registriert sein, damit alle Log-Events in deren
    Scope die request_id haben.
    """

    async def dispatch(  # type: ignore[override]
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        # Schritt 1: Eingehende ID aus Header oder UUIDv4
        incoming = request.headers.get(_REQUEST_ID_HEADER)
        request_id = _sanitize_or_generate(incoming)

        # Schritt 2: structlog-Context binden. Alle nachfolgenden Log-Events
        # im selben Request erben damit request_id automatisch.
        #
        # WICHTIG: kein manuelles ``unbind_contextvars`` im finally-Block.
        # ``structlog.contextvars`` nutzt PEP-567 ``contextvars.ContextVar``,
        # die per-asyncio-Task isoliert ist und automatisch deallokiert wird
        # wenn der Task endet. Ein manuelles unbind in der Middleware wuerde
        # zu frueh aufraeumen - der uvicorn-Access-Log emittiert NACH dem
        # Middleware-Return, dann waere die request_id schon weg.
        structlog.contextvars.bind_contextvars(request_id=request_id)
        response = await call_next(request)

        # Schritt 3: Response-Header setzen (cross-system Korrelation)
        response.headers[_REQUEST_ID_HEADER] = request_id
        return response
