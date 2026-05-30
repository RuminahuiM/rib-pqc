"""HTTP-Middleware-Module fuer den rib-pqc Auth-Service.

Stories:
- PQC-79 (SEC-1): Request-ID Middleware.

Spaetere Sprint-Stories ergaenzen CORS (SEC-2), TrustedHost (SEC-3),
Security-Headers (SEC-4), Rate-Limit (SEC-5).
"""

from __future__ import annotations

from middleware.rate_limit import limiter, register_rate_limit
from middleware.request_id import RequestIdMiddleware
from middleware.security_headers import SecurityHeadersMiddleware

__all__ = [
    "RequestIdMiddleware",
    "SecurityHeadersMiddleware",
    "limiter",
    "register_rate_limit",
]
