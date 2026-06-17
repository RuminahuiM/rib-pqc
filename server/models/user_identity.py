"""UserIdentity-ORM-Modell.

Story: PQC-39 (BRK-4) AC-3, AC-4.
Architektur-Bezug: docs/07_design.md Abschnitt 5.3 (User-ERD-Erweiterung
fuer Multi-Provider-Account-Linking).

**Modell-Konzept (Industry-Standard, vgl. Auth0/Cognito/Keycloak):**

Ein User kann **mehrere** externe Identities haben (z.B. einen Google-Account
UND einen Microsoft-Account, beide gemappt auf dasselbe interne User-Record).
Pro IdP+sub-Paar genau ein UserIdentity-Row, mit FK zu User.id.

**Composite Unique-Constraint:** `(auth_method, external_sub)` global eindeutig.
Damit ist der Lookup "find user by (google, sub-xyz)" O(log n) ueber den
Composite-Index.

**Lifecycle:**

- Lokaler User wird via UserRepository.create_local(email, password_hash)
  angelegt, ohne UserIdentity-Row.
- Federated Login: bei Erst-Login wird ggf. neuer User-Record angelegt
  und sofort ein UserIdentity-Row mit (auth_method, external_sub).
- Account-Linking: bei Email-Match auf existing-User + email_verified=true
  wird ein neuer UserIdentity-Row gegen die existing User.id angelegt.

**Verhaeltnis zum User-Modell:**

- `User.auth_method` + `User.external_sub` bleiben aus Backward-Compat-
  Gruenden im Schema (Sprint-1-Migrations-Daten landen dort). PQC-39
  Daten-Migration kopiert sie ins user_identities-Modell und liest ab
  jetzt nur noch das neue Modell.
- Neue User-Records (ab BRK-4) haben `User.auth_method='local'` wenn lokal,
  oder `User.auth_method=<provider>` plus parallel ein user_identities-Row
  fuer die federated Identity.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


def _new_identity_id() -> str:
    return str(uuid.uuid4())


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)  # noqa: UP017


class UserIdentity(Base):
    """Eine externe IdP-Identitaet (Google, Microsoft, ...) eines Users.

    Story-Bezug: PQC-39 BRK-4.
    """

    __tablename__ = "user_identities"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=_new_identity_id,
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    auth_method: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
    )
    external_sub: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=_utc_now,
    )

    __table_args__ = (
        # Global-eindeutiger Lookup: zwei verschiedene User koennen NICHT
        # denselben (auth_method, external_sub) haben.
        UniqueConstraint("auth_method", "external_sub", name="uq_user_identity_external"),
    )

    def __repr__(self) -> str:
        return (
            f"<UserIdentity id={self.id!r} user_id={self.user_id!r} "
            f"auth_method={self.auth_method!r}>"
        )
