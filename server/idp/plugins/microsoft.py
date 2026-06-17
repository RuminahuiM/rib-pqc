"""Microsoft Entra ID IdP-Plugin (Single-Tenant).

Stories:
- PQC-36 (BRK-1): Plugin-Struktur mit Stubs.
- PQC-38 (BRK-3): verify_id_token voll-implementiert mit JWKS + Verifier + tid-Check.
- PQC-41 (BRK-6): Wenn weitere provider-spezifische Logik dazukommt.
- PQC-39 (BRK-4): claim_mapper-Logik.

**Microsoft-Convention (Entra ID v2.0 Docs 2026):**

- ``oid`` ist die stable Object-ID im Tenant (besser als ``sub`` weil
  ``sub`` pro App-Client pairwise ist).
- ``preferred_username`` enthaelt UPN/Email.
- ``tid`` Claim muss gegen unseren konfigurierten tenant_id geprueft werden,
  sonst koennte ein Token aus einem anderen Tenant unsere App erreichen.
- ``iss`` ist ``https://login.microsoftonline.com/<tenant>/v2.0`` (siehe
  Plugin-Property).
- ``aud`` ist unser Client-ID.
- Sig-Algorithmus: RS256.
"""

from __future__ import annotations

from typing import Any

from config import MicrosoftProviderConfig
from services.id_token_verifier import IdTokenVerifier, IdTokenVerifyError


class MicrosoftIdpPlugin:
    """Microsoft Entra ID OIDC-Provider-Plugin (Single-Tenant)."""

    name: str = "microsoft"

    # Microsoft Entra ID v2.0 nutzt ausschliesslich RS256.
    _ALLOWED_ALGS: tuple[str, ...] = ("RS256",)

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

        STUB bis PQC-39 BRK-4 Identity-Normalisierung.
        """
        msg = (
            "MicrosoftIdpPlugin.claim_mapper ist ein Stub. "
            "Wird in PQC-39 BRK-4 Identity-Normalisierung voll implementiert."
        )
        raise NotImplementedError(msg)

    async def verify_id_token(
        self,
        token: str,
        *,
        jwks_uri: str,
        verifier: IdTokenVerifier,
    ) -> dict[str, Any]:
        """Verifiziert Microsoft-ID-Token plus tid-Claim-Check.

        Story-Bezug: PQC-38 BRK-3 AC-2..AC-4. Zusaetzlich Microsoft-
        spezifischer ``tid``-Check, der das Token einem konkreten Entra-ID-
        Tenant zuordnet. Ohne diesen Check koennte ein Token aus einem
        anderen Tenant theoretisch unsere App erreichen (Single-Tenant-Setup).

        Returns: validierter Token-Payload-Dict.
        Raises: IdTokenVerifyError bei Sig-/Claim-Fehler oder tid-Mismatch.
        """
        payload = await verifier.verify(
            token=token,
            jwks_uri=jwks_uri,
            issuer=self.issuer,
            audience=self.client_id,
            allowed_algs=list(self._ALLOWED_ALGS),
        )
        token_tid = payload.get("tid")
        if token_tid != self.tenant_id:
            msg = (
                f"Microsoft 'tid' claim mismatch: expected {self.tenant_id!r}, "
                f"got {token_tid!r}"
            )
            raise IdTokenVerifyError(msg, reason="invalid_tenant")
        return payload
