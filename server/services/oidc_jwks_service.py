"""JWKS-Fetch-Service mit TTL-Cache und Force-Refresh.

Story: PQC-38 (BRK-3) AC-1.

**Aufgabe:**

Holt die JSON-Web-Key-Set-Daten (JWKS) eines OIDC-Providers vom ``jwks_uri``
(typisch aus dem Discovery-Doc) und cacht sie in-memory mit TTL. Wird vom
ID-Token-Verifier benutzt um den zum ``kid`` passenden Public-Key zu finden.

**Designprinzipien (RFC 7517, RFC 9700 BCP 2026):**

- JWKS-TTL ist Best Practice **deutlich kuerzer** als Discovery-TTL, weil
  Provider Keys haeufig rotieren (typisch alle 24-48h bei Google, bei MS
  variabel). Default 1h ist konservativ-sicher.
- **Force-Refresh** bei Sig-Validation-Fehler: wenn die Sig-Verify failed
  obwohl der Code-Flow erfolgreich war, ist haeufig ein Key-Rotation-Race.
  Der Verifier triggert dann einen Force-Refresh und probiert nochmal.
- httpx-Async-Client wird per DI uebergeben (gleicher Client wie
  OidcExchangeService und Discovery-Service, Connection-Pool wiederverwendet).

**Cache-Schema:** ``{jwks_uri: (fetched_at_monotonic, jwks_dict)}``.
"""

from __future__ import annotations

import logging
import time
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class JwksFetchError(Exception):
    """JWKS-Fetch ist fehlgeschlagen (Netzwerk, HTTP-Status, JSON-Parse)."""


class OidcJwksService:
    """JWKS-Fetch + TTL-Cache + Force-Refresh.

    Story-Bezug: PQC-38 BRK-3 AC-1.
    """

    def __init__(
        self,
        http_client: httpx.AsyncClient,
        cache_ttl_seconds: int,
    ) -> None:
        if cache_ttl_seconds <= 0:
            msg = f"cache_ttl_seconds must be positive, got {cache_ttl_seconds}"
            raise ValueError(msg)
        self._client = http_client
        self._ttl = cache_ttl_seconds
        # Cache-Schema: {jwks_uri: (fetched_at_monotonic, jwks_dict)}
        self._cache: dict[str, tuple[float, dict[str, Any]]] = {}

    async def get_jwks(
        self,
        jwks_uri: str,
        *,
        force_refresh: bool = False,
    ) -> dict[str, Any]:
        """Liefert das JWKS-Dict fuer ``jwks_uri`` (cached, TTL).

        Args:
            jwks_uri: URL zum JWKS-Endpoint (typisch aus dem Discovery-Doc
                ``jwks_uri``-Feld).
            force_refresh: wenn True, ignoriere Cache und fetche frisch.
                Hilfreich nach Sig-Validation-Failure (Key-Rotation-Race).

        Raises:
            JwksFetchError: Netzwerk-Fehler, HTTP-Status >=400, JSON-Parse-Fail,
                oder fehlendes ``keys``-Field.
        """
        now = time.monotonic()
        if not force_refresh:
            cached = self._cache.get(jwks_uri)
            if cached is not None:
                fetched_at, jwks = cached
                if now - fetched_at < self._ttl:
                    logger.debug(
                        "oidc_jwks.cache_hit",
                        extra={"jwks_uri": jwks_uri},
                    )
                    return jwks

        logger.info(
            "oidc_jwks.fetch",
            extra={"jwks_uri": jwks_uri, "force_refresh": force_refresh},
        )
        try:
            response = await self._client.get(jwks_uri)
        except httpx.RequestError as exc:
            msg = f"JWKS fetch failed: {exc}"
            raise JwksFetchError(msg) from exc

        if response.status_code >= 400:
            msg = f"JWKS endpoint returned HTTP {response.status_code} for {jwks_uri}"
            raise JwksFetchError(msg)

        try:
            jwks = response.json()
        except ValueError as exc:
            msg = f"JWKS body is not valid JSON: {exc}"
            raise JwksFetchError(msg) from exc

        if not isinstance(jwks, dict) or "keys" not in jwks:
            msg = "JWKS body must be a JSON object with 'keys' field"
            raise JwksFetchError(msg)

        keys = jwks.get("keys")
        if not isinstance(keys, list):
            msg = "JWKS 'keys' field must be a JSON array"
            raise JwksFetchError(msg)

        self._cache[jwks_uri] = (now, jwks)
        return jwks

    def invalidate(self, jwks_uri: str) -> None:
        """Loescht den Cache-Eintrag fuer ``jwks_uri`` (z.B. nach Key-Rotation)."""
        self._cache.pop(jwks_uri, None)
