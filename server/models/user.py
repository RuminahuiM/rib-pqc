"""User-ORM-Modell.

Story: PQC-28 (AUT-1) AC-1.
Architektur-Bezug: docs/07_design.md Abschnitt 5.3 (User-ERD).

Felder gemaess Design 5.3:
- id (UUID-String, Primary Key): zufaellige UUIDv4 als String
- email (String, lowercase, unique): Login-Identifier, lowercase-stored
- password_hash (String, nullable): Argon2id-Hash bei local-Auth, NULL bei federated
- auth_method (String): "local", "google" oder "microsoft"
- external_sub (String, nullable): federated sub-Claim, NULL bei local
- created_at, updated_at (DateTime, UTC, tz-aware): Audit-Timestamps

Konsistenz-Constraints (z.B. local XOR password_hash) werden Sprint-1-pragmatisch
NICHT als DB-CHECK gesetzt, sondern im UserRepository validiert. SQLite hat
limitierten Check-Constraint-Support; bei Postgres-Migration koennen Constraints
DB-seitig nachgezogen werden.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


def _new_user_id() -> str:
    """Generiert eine neue UUIDv4 als 36-Zeichen-String."""
    return str(uuid.uuid4())


def _utc_now() -> datetime:
    """UTC-jetzt mit tz-info."""
    return datetime.now(timezone.utc)  # noqa: UP017


class User(Base):
    """Lokaler oder federated User-Record."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=_new_user_id,
    )
    email: Mapped[str] = mapped_column(
        String(320),
        unique=True,
        nullable=False,
        index=True,
    )
    password_hash: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    auth_method: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        index=True,
    )
    external_sub: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=_utc_now,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=_utc_now,
        onupdate=_utc_now,
    )

    def __repr__(self) -> str:
        return f"<User id={self.id!r} email={self.email!r} auth_method={self.auth_method!r}>"

