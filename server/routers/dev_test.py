"""Dev-only Test-Endpoints fuer Rate-Limit-Verifikation.

Story: PQC-83 (SEC-5) AC-5.

Dieser Router wird nur in ``main.py`` registriert wenn ``environment == "dev"``.
In Production-Builds existiert die Route nicht.

**Endpoint:** ``GET /__debug/rate-limit-test``

- Limit: 3 Requests pro Minute pro IP (niedriger als Login, damit Tests
  schnell den Limit-Hit triggern ohne 5+ Argon2-Verify-Operationen).
- Liefert ``{"ok": true, "marker": "rate-limit-test"}``.

Bei Limit-Hit greift der ``RateLimitExceeded``-Handler aus
``middleware/rate_limit.py`` und liefert 429 + Retry-After.
"""

from __future__ import annotations

from fastapi import APIRouter, Request

from middleware.rate_limit import limiter

router = APIRouter(prefix="/__debug", tags=["dev"])


@router.get("/rate-limit-test")
@limiter.limit("3/minute")
async def rate_limit_test(request: Request) -> dict[str, object]:
    """Dummy-Endpoint zur Rate-Limit-Verifikation (nur dev)."""
    del request  # benoetigt fuer slowapi.get_remote_address
    return {"ok": True, "marker": "rate-limit-test"}
