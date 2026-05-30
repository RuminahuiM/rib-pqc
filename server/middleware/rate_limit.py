"""Rate-Limiting Setup via slowapi mit Redis-Backend.

Story: PQC-83 (SEC-5).
Resolves Finding: F-005.

**Setup-Pattern:**

1. Im Lifespan-Hook (oder `create_app`) wird ein ``Limiter`` mit der
   konfigurierten ``storage_uri`` instantiiert.
2. ``Limiter`` wird auf ``app.state.limiter`` abgelegt (slowapi-Convention).
3. ``SlowAPIMiddleware`` wird registriert.
4. Der ``rate_limit_exceeded_handler`` wird als ``RateLimitExceeded``-Handler
   registriert (liefert 429 plus Retry-After-Header).
5. Endpoints koennen per Decorator `@limiter.limit("X/period")` overriden.

**Key-Strategie:**

Per-IP via ``slowapi.util.get_remote_address``. Senior-Decision Sprint-1:
- Per-IP-Schutz deckt 95% der Brute-Force-Angriffe (Single-IP-Quellen).
- Per-Email-Composite-Key (gegen Distributed-Botnet) als Sprint-3-Polish.
- Per-Email-DoS-Risiko (Account-Lockout durch absichtliche Fails) ist real
  und braucht 401-statt-429-Mitigation, die wir bewusst nicht in Sprint 1
  implementieren.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from config import get_settings
from logging_config import get_logger

if TYPE_CHECKING:
    from fastapi import FastAPI


_logger = get_logger("rib_pqc.middleware.rate_limit")


# Module-level Limiter Singleton.
# slowapi-Pattern: Decorator @limiter.limit(...) braucht Limiter-Object zur
# Decoration-Zeit. Daher hier ein module-level Singleton, der aus Settings
# bei Module-Load instantiiert wird.
#
# In Tests kann der Limiter via ``monkeypatch.setattr`` oder direkt durch
# Setzen von ``limiter.enabled = False`` deaktiviert werden.
_settings = get_settings()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[_settings.security.rate_limit.global_default],
    storage_uri=_settings.security.rate_limit.storage_uri,
    enabled=_settings.security.rate_limit.enabled,
)


def register_rate_limit(app: FastAPI) -> None:
    """Registriert den Module-level Limiter, Middleware und Exception-Handler.

    Args:
        app: FastAPI-Instanz (typisch aus ``create_app``).
    """
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]
    _logger.info(
        "rate_limit.registered",
        global_default=_settings.security.rate_limit.global_default,
        storage_scheme=_settings.security.rate_limit.storage_uri.split("://", 1)[0],
        enabled=_settings.security.rate_limit.enabled,
    )


async def _rate_limit_exceeded_handler(request: object, exc: RateLimitExceeded) -> object:
    """Liefert 429 + Retry-After-Header + JSON-Body bei Limit-Hit (AC-4)."""
    from fastapi.responses import JSONResponse

    del request  # nicht benoetigt fuer Standard-Response
    retry_after = int(getattr(exc, "retry_after", 60))
    _logger.warning(
        "rate_limit.exceeded",
        detail=str(exc.detail) if hasattr(exc, "detail") else "limit exceeded",
        retry_after=retry_after,
    )
    return JSONResponse(
        status_code=429,
        content={"error": "rate_limit_exceeded", "retry_after": retry_after},
        headers={"Retry-After": str(retry_after)},
    )
