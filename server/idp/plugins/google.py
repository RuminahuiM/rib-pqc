"""Google IdP-Plugin.

Stories:
- PQC-36 (BRK-1): Plugin-Struktur mit Stubs.
- PQC-40 (BRK-5): Voll-Implementation (verify_id_token mit Google JWKS).
- PQC-39 (BRK-4): claim_mapper-Logik (Google nutzt ``sub`` als stable ID).
- PQC-38 (BRK-3): verify_id_token mit JWKS-Caching.

Google-Convention:
- ``sub`` ist die stable Google-User-ID.
- ``email`` plus ``email_verified`` werden im ID-Token mitgeliefert.
- Issuer ist ``https://accounts.google.com``.
"""

from __future__ import annotations

from typing import Any

from config import GoogleProviderConfig


class GoogleIdpPlugin:
    """Google OIDC-Provider-Plugin.

    Voll funktional fuer die passiven Properties (discovery_url, client_id,
    scopes). ``claim_mapper`` und ``verify_id_token`` sind in BRK-1 Stubs;
    werden in BRK-4 / BRK-3 voll implementiert.
    """

    name: str = "google"

    def __init__(self, config: GoogleProviderConfig) -> None:
        self._config = config

    @property
    def discovery_url(self) -> str:
        return self._config.discovery_url

    @property
    def client_id(self) -> str:
        return self._config.client_id

    @property
    def client_secret(self) -> str:
        """Wird in BRK-2 OIDC-Code-Flow fuer Token-Exchange benoetigt."""
        return self._config.client_secret

    @property
    def scopes(self) -> list[str]:
        return list(self._config.scopes)

    @property
    def issuer(self) -> str:
        return self._config.issuer

    @property
    def redirect_uri(self) -> str:
        return self._config.redirect_uri

    def claim_mapper(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Mappt Google-Claims auf normalisierte User-Info.

        STUB fuer BRK-1. Voll implementiert in PQC-39 (BRK-4 Identity-
        Normalisierung). Geplante Logik:
            external_sub = payload["sub"]
            email = payload.get("email")
            email_verified = payload.get("email_verified", False)
            display_name = payload.get("name") or payload.get("given_name")
        """
        msg = (
            "GoogleIdpPlugin.claim_mapper ist ein Stub in BRK-1. "
            "Wird in PQC-39 BRK-4 Identity-Normalisierung voll implementiert."
        )
        raise NotImplementedError(msg)

    def verify_id_token(self, token: str) -> dict[str, Any]:
        """Verifiziert ID-Token-Signature gegen Google-JWKS.

        STUB fuer BRK-1. Voll implementiert in PQC-38 (BRK-3 ID-Token-
        Verifikation). Geplante Logik:
            1. JWKS von ``https://www.googleapis.com/oauth2/v3/certs`` laden (cached)
            2. JWS-Header lesen, kid extrahieren, passenden Public-Key holen
            3. Signature verifizieren (RS256, ES256)
            4. iss-Claim gegen ``self.issuer`` pruefen
            5. aud-Claim gegen ``self.client_id`` pruefen
            6. exp-Claim pruefen (mit Leeway analog TokenService)
        """
        msg = (
            "GoogleIdpPlugin.verify_id_token ist ein Stub in BRK-1. "
            "Wird in PQC-38 BRK-3 ID-Token-Verifikation voll implementiert."
        )
        raise NotImplementedError(msg)
