"""NormalizedIdentity Pydantic-Modell.

Story: PQC-39 (BRK-4).

Provider-agnostic Repraesentation der Identitaet, die ein OIDC-Plugin aus
einem verifizierten ID-Token-Payload extrahiert. Wird vom
``FederatedIdentityService`` konsumiert um link_or_create_user zu machen.

**Felder:**

- ``external_sub``: stable Identifier beim Provider (Google: `sub`, Microsoft: `oid`).
- ``email``: User-Email-Address, lowercase normalisiert (kann auch None sein
  wenn Provider sie nicht liefert).
- ``email_verified``: True wenn Provider die Email bestaetigt hat. Wird in
  PQC-39 AC-6 zur Steuerung des Account-Linkings verwendet.
- ``display_name``: User-anzeigbarer Name fuer UI (optional).
"""

from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


class NormalizedIdentity(BaseModel):
    """Provider-agnostic Identity-Repraesentation."""

    external_sub: str = Field(min_length=1, max_length=255)
    email: EmailStr | None = None
    email_verified: bool = False
    display_name: str | None = Field(default=None, max_length=255)

    @property
    def has_email(self) -> bool:
        """True wenn ``email`` gesetzt ist (egal ob verified)."""
        return self.email is not None
