"""Microsoft Entra ID IdP-Plugin (Single-Tenant).

Stories:
- PQC-36 (BRK-1): Plugin-Struktur mit Stubs.
- PQC-41 (BRK-6): Voll-Implementation (verify_id_token mit MS-JWKS).
- PQC-39 (BRK-4): claim_mapper-Logik (MS nutzt ``oid`` als stable tenant-ID).
- PQC-38 (BRK-3): verify_id_token mit JWKS-Caching.

Microsoft-Convention:
- ``oid`` ist die stable Object-ID im Tenant (besser als ``sub`` weil
  ``sub`` pro App-Client pairwise ist).
- ``preferred_username`` enthaelt UPN/Email.
- ``tid`` Claim muss gegen unseren konfigurierten tenant_id geprueft werden.
- Issuer ist ``https://login.microsoftonline.com/<tenant>/v2.0``.
"""

from __future__ import annotations

from typing import Any

from config import MicrosoftProviderConfig


class MicrosoftIdpPlugin:
    """Microsoft Entra ID OIDC-Provider-Plugin (Single-Tenant).

    Voll funktional fuer die passiven Properties (discovery_url, client_id,
    scopes, tenant_id). ``claim_mapper`` und ``verify_id_token`` sind in BRK-1
    Stubs; werden in BRK-4 / BRK-3 voll implementiert.
    """

    name: str = "microsoft"

    def __init__(self, config: MicrosoftProviderConfig) -> None:
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
    def tenant_id(self) -> str:
        return self._config.tenant_id

    @property
    def redirect_uri(self) -> str:
        return self._config.redirect_uri

    def claim_mapper(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Mappt Microsoft-Claims auf normalisierte User-Info.

        STUB fuer BRK-1. Voll implementiert in PQC-39 (BRK-4 Identity-
        Normalisierung). Geplante Logik:
            external_sub = payload["oid"]   # tenant-stable Object-ID
            email = payload.get("email") or payload.get("preferred_username")
            email_verified = True  # Entra ID verifiziert UPN
            display_name = payload.get("name")
            # Plus: tid-Claim gegen self.tenant_id pruefen
        """
        msg = (
            "MicrosoftIdpPlugin.claim_mapper ist ein Stub in BRK-1. "
            "Wird in PQC-39 BRK-4 Identity-Normalisierung voll implementiert."
        )
        raise NotImplementedError(msg)

    def verify_id_token(self, token: str) -> dict[str, Any]:
        """Verifiziert ID-Token-Signature gegen Microsoft-JWKS.

        STUB fuer BRK-1. Voll implementiert in PQC-38 (BRK-3 ID-Token-
        Verifikation). Geplante Logik:
            1. JWKS aus Discovery-Doc holen (cached)
            2. JWS-Header lesen, kid extrahieren, passenden Public-Key holen
            3. Signature verifizieren (RS256)
            4. iss-Claim gegen ``self.issuer`` pruefen
            5. aud-Claim gegen ``self.client_id`` pruefen
            6. tid-Claim gegen ``self.tenant_id`` pruefen (Single-Tenant!)
            7. exp-Claim pruefen (mit Leeway analog TokenService)
        """
        msg = (
            "MicrosoftIdpPlugin.verify_id_token ist ein Stub in BRK-1. "
            "Wird in PQC-38 BRK-3 ID-Token-Verifikation voll implementiert."
        )
        raise NotImplementedError(msg)
