"""OIDC-Code-Exchange-Service.

Stories:
- PQC-37 (BRK-2): Code-zu-Token-Tausch gegen Provider-/token-Endpoint mit
  PKCE-Verifier-Echo. Lazy Discovery-Doc-Cache (24h TTL).
- PQC-38 (BRK-3): Wird ``verify_id_token`` der Plugins benutzen (kommt spaeter).

**Designprinzipien (RFC 9700 OAuth 2.0 Security BCP 2026):**

- ``code_verifier`` wird vom Client beim Callback uebergeben und direkt an
  den IdP-/token-Endpoint weitergereicht (Token-Mediating-Backend, BFF).
- ``client_secret`` lebt server-side, wird im POST-Body zum Token-Endpoint
  als ``application/x-www-form-urlencoded`` gesendet (Auth-Methode
  ``client_secret_post``, RFC 6749 Section 2.3.1).
- Discovery-Doc wird beim ersten Bedarf gefetcht und mit TTL gecached (Default
  24h, Settings-konfigurierbar). JWKS-URL kommt aus dem Discovery-Doc; das
  JWKS-Fetching selbst macht der ID-Token-Verifier in PQC-38, nicht hier.

**Fehlerverhalten:**

- Discovery-Fetch failt -> ``DiscoveryError`` (mappt im Router auf 502).
- Token-Exchange failt (Status 4xx oder 5xx) -> ``CodeExchangeError`` mit
  ``provider_error`` (mappt im Router auf 400).
- HTTP-Timeout -> ``CodeExchangeError`` mit Hint im Body (mappt auf 504/502).
"""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING, Any

import httpx
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from idp.registry import IdpProvider

logger = logging.getLogger(__name__)


class OidcServiceError(Exception):
    """Basis fuer alle Fehler im OidcExchangeService."""


class DiscoveryError(OidcServiceError):
    """Konnte das OIDC-Discovery-Doc nicht laden oder parsen."""


class CodeExchangeError(OidcServiceError):
    """Code-zu-Token-Tausch beim IdP fehlgeschlagen.

    Attributes:
        provider_error: Vom IdP gelieferter ``error``-Code (RFC 6749), oder
            ``"http_error"`` bei HTTP-Status >=400 ohne Error-Body.
        provider_error_description: Optionale lesbare Beschreibung.
    """

    def __init__(
        self,
        message: str,
        *,
        provider_error: str = "unknown_error",
        provider_error_description: str | None = None,
    ) -> None:
        super().__init__(message)
        self.provider_error = provider_error
        self.provider_error_description = provider_error_description


class TokenExchangeResult(BaseModel):
    """Ergebnis eines erfolgreichen Code-Token-Tauschs.

    Story-Bezug: PQC-37 BRK-2 AC-5 (ID-Token weiterleiten an BRK-3).
    """

    id_token: str = Field(min_length=1)
    access_token: str | None = None
    refresh_token: str | None = None
    expires_in: int | None = None
    token_type: str = Field(default="Bearer")


class OidcExchangeService:
    """Service fuer Discovery + Code-zu-Token-Tausch.

    Story-Bezug: PQC-37 BRK-2 AC-2.

    Lifecycle: Single-Instance pro App-Lifecycle. Haelt internen httpx-Async-
    Client (Connection-Pool). Aufrufer muss ``aclose()`` beim App-Shutdown
    aufrufen.

    Internal Discovery-Cache: ``{discovery_url: (fetched_at, doc_dict)}``.
    """

    def __init__(
        self,
        http_client: httpx.AsyncClient,
        discovery_cache_ttl_seconds: int,
    ) -> None:
        if discovery_cache_ttl_seconds <= 0:
            msg = (
                f"discovery_cache_ttl_seconds must be positive, "
                f"got {discovery_cache_ttl_seconds}"
            )
            raise ValueError(msg)
        self._client = http_client
        self._discovery_ttl = discovery_cache_ttl_seconds
        self._discovery_cache: dict[str, tuple[float, dict[str, Any]]] = {}

    async def aclose(self) -> None:
        """Schliesst den httpx-Client (Lifespan-Shutdown)."""
        await self._client.aclose()

    async def get_discovery_document(
        self,
        discovery_url: str,
    ) -> dict[str, Any]:
        """Liefert das OIDC-Discovery-Doc fuer ``discovery_url`` (cached).

        Cache-Strategie:
        - Erster Aufruf: HTTP-Fetch, cache.
        - Folgeaufrufe innerhalb TTL: Cache-Hit, kein HTTP-Call.
        - Nach TTL: erneut fetchen.

        Raises:
            DiscoveryError: wenn HTTP-Status >=400, Timeout, oder Body kein
                gueltiges JSON.
        """
        now = time.monotonic()
        cached = self._discovery_cache.get(discovery_url)
        if cached is not None:
            fetched_at, doc = cached
            if now - fetched_at < self._discovery_ttl:
                logger.debug(
                    "oidc_discovery.cache_hit",
                    extra={"discovery_url": discovery_url},
                )
                return doc

        logger.info(
            "oidc_discovery.fetch",
            extra={"discovery_url": discovery_url},
        )
        try:
            response = await self._client.get(discovery_url)
        except httpx.RequestError as exc:
            msg = f"Discovery fetch failed: {exc}"
            raise DiscoveryError(msg) from exc

        if response.status_code >= 400:
            msg = (
                f"Discovery returned HTTP {response.status_code} for "
                f"{discovery_url}"
            )
            raise DiscoveryError(msg)

        try:
            doc = response.json()
        except ValueError as exc:
            msg = f"Discovery body is not valid JSON: {exc}"
            raise DiscoveryError(msg) from exc

        if not isinstance(doc, dict):
            msg = "Discovery body must be a JSON object"
            raise DiscoveryError(msg)
        if "token_endpoint" not in doc:
            msg = "Discovery doc is missing required field 'token_endpoint'"
            raise DiscoveryError(msg)

        self._discovery_cache[discovery_url] = (now, doc)
        return doc

    async def exchange_code(
        self,
        plugin: IdpProvider,
        code: str,
        code_verifier: str,
    ) -> TokenExchangeResult:
        """Tauscht ``code`` plus ``code_verifier`` gegen IdP-Tokens.

        Story-Bezug: PQC-37 BRK-2 AC-2, AC-3.

        Args:
            plugin: IdP-Plugin aus IdpRegistry (liefert client_id, client_secret,
                redirect_uri, discovery_url).
            code: Authorization-Code aus dem IdP-Callback.
            code_verifier: PKCE-Verifier (RFC 7636), wird direkt an den
                IdP-Token-Endpoint weitergereicht.

        Returns:
            TokenExchangeResult mit id_token, access_token, ggf. refresh_token.

        Raises:
            DiscoveryError: wenn Discovery-Fetch failt.
            CodeExchangeError: wenn IdP den Tausch ablehnt.
        """
        discovery = await self.get_discovery_document(plugin.discovery_url)
        token_endpoint = discovery["token_endpoint"]

        # Plugins exponen client_secret + redirect_uri via Properties (siehe
        # idp/plugins/google.py + microsoft.py).
        client_secret = plugin.client_secret  # type: ignore[attr-defined]
        redirect_uri = plugin.redirect_uri  # type: ignore[attr-defined]

        # client_secret_post (RFC 6749 Section 2.3.1). Alternative
        # client_secret_basic ist gleichwertig, beide werden von Google und
        # Microsoft akzeptiert. Wir nutzen _post weil es expliziter ist.
        form_data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": plugin.client_id,
            "client_secret": client_secret,
            "code_verifier": code_verifier,
        }

        logger.info(
            "oidc_exchange.request",
            extra={
                "provider": plugin.name,
                "token_endpoint": token_endpoint,
                # code und code_verifier NICHT loggen (sensitive)
            },
        )
        try:
            response = await self._client.post(
                token_endpoint,
                data=form_data,
                headers={"Accept": "application/json"},
            )
        except httpx.RequestError as exc:
            msg = f"Token endpoint request failed: {exc}"
            raise CodeExchangeError(
                msg,
                provider_error="network_error",
                provider_error_description=str(exc),
            ) from exc

        if response.status_code >= 400:
            # IdP-Spec: Errors als JSON-Body mit ``error`` und ``error_description``.
            error_code = "http_error"
            error_desc: str | None = None
            try:
                body = response.json()
            except ValueError:
                body = None
            if isinstance(body, dict):
                error_code = body.get("error", error_code)
                error_desc = body.get("error_description")
            logger.warning(
                "oidc_exchange.failed",
                extra={
                    "provider": plugin.name,
                    "http_status": response.status_code,
                    "provider_error": error_code,
                },
            )
            msg = f"Token exchange failed with status {response.status_code}"
            raise CodeExchangeError(
                msg,
                provider_error=error_code,
                provider_error_description=error_desc,
            )

        try:
            body = response.json()
        except ValueError as exc:
            msg = f"Token response is not valid JSON: {exc}"
            raise CodeExchangeError(
                msg,
                provider_error="malformed_response",
            ) from exc

        if not isinstance(body, dict):
            msg = "Token response is not a JSON object"
            raise CodeExchangeError(msg, provider_error="malformed_response")

        if "id_token" not in body:
            # OIDC-Pflicht: id_token muss zurueckkommen wenn scope=openid.
            msg = "Token response missing 'id_token' field"
            raise CodeExchangeError(msg, provider_error="missing_id_token")

        result = TokenExchangeResult.model_validate(body)
        logger.info(
            "oidc_exchange.success",
            extra={
                "provider": plugin.name,
                "has_refresh_token": result.refresh_token is not None,
                "expires_in": result.expires_in,
            },
        )
        return result
