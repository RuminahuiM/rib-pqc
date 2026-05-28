"""Alembic environment fuer rib-pqc Auth-Service.

Stories: PQC-28 (AUT-1) AC-2.

Sync-Setup: Migrations laufen via Sync-SQLAlchemy-Engine gegen
settings.database.sync_url. Application selber nutzt unabhaengig den
Async-Engine zur Laufzeit (separater Treiber, gleiche SQLite-Datei).
"""

from __future__ import annotations

import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import engine_from_config, pool

from alembic import context

# server/-Pfad in sys.path, damit ``from models import Base`` funktioniert
_SERVER_DIR = Path(__file__).resolve().parent.parent
if str(_SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(_SERVER_DIR))

from config import get_settings  # noqa: E402
from models import Base  # noqa: E402

config = context.config

# Sync-URL aus Settings (statt sqlalchemy.url im alembic.ini).
settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.database.sync_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Offline-Modus: SQL-Statements werden in stdout/file ausgegeben."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Online-Modus: Migrations gegen echte DB."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,  # SQLite-friendly fuer ALTER TABLE
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
