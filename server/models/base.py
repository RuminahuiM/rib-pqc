"""SQLAlchemy 2.0 DeclarativeBase fuer alle ORM-Modelle.

Stories: PQC-28 (AUT-1).

Pattern: `from __future__ import annotations` plus `Mapped[]`-Annotations
fuer Python-Typing-First-ORM, kompatibel mit mypy strict.
"""

from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Gemeinsame Basis fuer alle ORM-Modelle im rib-pqc Auth-Service.

    Spaetere Modelle (Session, AuditEvent, IdpAccount, ...) erben hierauf,
    sodass Alembic-Autogenerate alle Tabellen in einer Migration findet.
    """
