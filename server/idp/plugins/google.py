"""Google IdP-Plugin.

Stories:
- PQC-36 (BRK-1): Plugin-Struktur mit Stubs.
- PQC-38 (BRK-3): verify_id_token voll-implementiert mit JWKS + Verifier.
- PQC-40 (BRK-5): Wenn weitere provider-spezifische Logik dazukommt.
- PQC-39 (BRK-4): claim_mapper-Logik (Google nutzt ``sub`` als stable ID).

**Google-Convention (OIDC Core 1.0 + Google-Docs 2026):**

- ``sub`` ist die stable Google-User-ID.
- ``email`` plus ``email_verified`` werden im ID-Token mitgeliefert (wenn
  ``email`` im Scope).
- ``iss`` ist ``https://accounts.google.com`` (kein Trailing-Slash, Google
  liefert beide Varianten - wir akzeptieren die Default-Form).
- ``aud`` ist unser Client-ID. Google liefert Single-Audience.
- Sig-Algorithmus: RS256.
"""

from __future__ import annotations

from typing import Any

from config import GoogleProviderConfig
from services.id_token_verifier import IdTokenVerifier


class GoogleIdpPlugin:
    """Google OIDC-Provider-Plugin."""

    name: str = "google"

    # Google verwendet ausschliesslich RS256 (Google-OIDC-Docs 2026).
    _ALLOWED_ALGS: tuple[str, ...] = ("RS256",)

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

        STUB bis PQC-39 BRK-4 Identity-Normalisierung.
        """
        msg = (
            "GoogleIdpPlugin.claim_mapper ist ein Stub. "
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
        """Verifiziert Google-ID-Token mit RS256 gegen Google-JWKS.

        Story-Bezug: PQC-38 BRK-3 AC-2..AC-4.

        Returns: validierter Token-Payload-Dict.
        Raises: IdTokenVerifyError aus dem zentralen Verifier.
        """
        return await verifier.verify(
            token=token,
            jwks_uri=jwks_uri,
            issuer=self.issuer,
            audience=self.client_id,
            allowed_algs=list(self._ALLOWED_ALGS),
        )
