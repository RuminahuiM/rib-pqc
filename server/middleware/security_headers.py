"""Security-Headers Middleware (OWASP Secure Headers Project).

Story: PQC-82 (SEC-4).
Resolves Finding: F-004.

**Gesetzte Response-Header (AC-1):**

- ``X-Content-Type-Options: nosniff``: verhindert dass Browser den
  Content-Type "erraet" (Schutz gegen MIME-Sniffing-Attacks).
- ``X-Frame-Options: DENY``: verhindert Embedding in iframe (Clickjacking-
  Schutz).
- ``Referrer-Policy: no-referrer``: kein Referrer-Leak bei Outbound-Links.
- ``Strict-Transport-Security``: zwingt Browser zu HTTPS-only. Nur in
  non-dev-Environments, weil Dev kein TLS hat.

**Content-Security-Policy (CSP):** in Sprint 1 NICHT gesetzt - Swagger-UI auf
``/docs`` braucht relaxed CSP (inline-scripts, CDN-resources). Wird Sprint-3-
Polish.

**Bezuege:**
- OWASP Secure Headers Project: https://owasp.org/www-project-secure-headers/
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from starlette.middleware.base import BaseHTTPMiddleware

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from starlette.requests import Request
    from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Setzt defensive Response-Headers (OWASP-konform).

    Konstruktor-DI:
    - ``hsts_enabled``: ob HSTS-Header gesetzt wird. Nur in non-dev sinnvoll.
    - ``hsts_max_age_seconds``: HSTS max-age.
    - ``hsts_include_subdomains``: HSTS includeSubDomains-Flag.
    """

    def __init__(
        self,
        app: object,  # ASGI app
        *,
        hsts_enabled: bool = False,
        hsts_max_age_seconds: int = 31536000,
        hsts_include_subdomains: bool = True,
    ) -> None:
        super().__init__(app)  # type: ignore[arg-type]
        self._hsts_enabled = hsts_enabled
        self._hsts_max_age = hsts_max_age_seconds
        self._hsts_include_subdomains = hsts_include_subdomains

    async def dispatch(  # type: ignore[override]
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        response = await call_next(request)

        # Constant Security-Headers (immer aktiv)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "no-referrer")

        # HSTS nur wenn enabled (typisch non-dev mit TLS)
        if self._hsts_enabled:
            hsts_value = f"max-age={self._hsts_max_age}"
            if self._hsts_include_subdomains:
                hsts_value += "; includeSubDomains"
            response.headers.setdefault("Strict-Transport-Security", hsts_value)

        return response
