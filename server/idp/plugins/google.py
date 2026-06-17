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
from idp.normalized_identity import NormalizedIdentity
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

    def claim_mapper(self, payload: dict[str, Any]) -> NormalizedIdentity:
        """Mappt Google-ID-Token-Claims auf NormalizedIdentity.

        Story-Bezug: PQC-39 BRK-4 AC-3.

        Google-Claims-Konvention (OIDC Core + Google-Docs):
        - ``sub``: stable Google-User-ID -> ``external_sub``.
        - ``email``: optional, nur wenn scope ``email`` angefragt.
        - ``email_verified``: bool, Google liefert true wenn Email bestaetigt.
        - ``name``/``given_name``: anzeigbarer User-Name.

        Raises:
            ValueError: wenn ``sub`` fehlt.
        """
        sub = payload.get("sub")
        if not sub:
            msg = "Google ID-token payload is missing required 'sub' claim"
            raise ValueError(msg)
        return NormalizedIdentity(
            external_sub=str(sub),
            email=payload.get("email"),
            email_verified=bool(payload.get("email_verified", False)),
            display_name=payload.get("name") or payload.get("given_name"),
        )

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
