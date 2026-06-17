"""add user_identities table

Revision ID: e24c7cf373f9
Revises: 65d6577e4bf6
Create Date: 2026-06-17

Story: PQC-39 (BRK-4) Identity-Normalisierung.

Schema-Add:
- Tabelle user_identities (id PK, user_id FK->users.id ON DELETE CASCADE,
  auth_method, external_sub, created_at) mit Composite-Unique
  (auth_method, external_sub).

Data-Migration:
- Bestehende users-Records mit auth_method != 'local' und external_sub IS NOT NULL
  werden in user_identities gespiegelt, damit der Lookup-Code ab BRK-4 nur die
  neue Tabelle befragt. Die User.auth_method + User.external_sub-Spalten
  bleiben aus Backward-Compat erstmal im Schema; ein spaeterer Cleanup (Sprint 4
  oder Sprint 5) kann sie nullbar machen oder droppen.
"""

from __future__ import annotations

import uuid
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers
revision: str = "e24c7cf373f9"
down_revision: str | Sequence[str] | None = "65d6577e4bf6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "user_identities",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("auth_method", sa.String(length=16), nullable=False),
        sa.Column("external_sub", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
            name="fk_user_identities_user_id",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "auth_method", "external_sub", name="uq_user_identity_external"
        ),
    )
    with op.batch_alter_table("user_identities", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_user_identities_user_id"), ["user_id"], unique=False
        )

    # Daten-Migration: existierende federated User in user_identities spiegeln.
    # SQLite-vertraeglich via SELECT + INSERT.
    bind = op.get_bind()
    existing = bind.execute(
        sa.text(
            "SELECT id, auth_method, external_sub FROM users "
            "WHERE auth_method != 'local' AND external_sub IS NOT NULL"
        )
    ).fetchall()
    for row in existing:
        identity_id = str(uuid.uuid4())
        bind.execute(
            sa.text(
                "INSERT INTO user_identities "
                "(id, user_id, auth_method, external_sub) "
                "VALUES (:id, :user_id, :auth_method, :external_sub)"
            ),
            {
                "id": identity_id,
                "user_id": row[0],
                "auth_method": row[1],
                "external_sub": row[2],
            },
        )


def downgrade() -> None:
    with op.batch_alter_table("user_identities", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_user_identities_user_id"))
    op.drop_table("user_identities")
