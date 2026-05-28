"""Admin-CLI fuer User-Provisioning (PQC-29 / AUT-2).

Aufruf::

    docker compose exec auth-service python -m admin create-user --email alice@example.com
    echo "secret" | docker compose exec -T auth-service \\
        python -m admin create-user --email alice@example.com --password-stdin
    docker compose exec auth-service python -m admin list-users
    docker compose exec auth-service python -m admin list-users --json

**Sicherheits-Design (OWASP-konform):**

- ``--password <plain>`` als argv wird **NICHT** angeboten. Shell-History,
  ``ps aux`` und Container-Logs leaken sonst das Passwort.
- Default: ``getpass.getpass()`` Prompt (kein Echo, kein argv).
- Optional: ``--password-stdin`` liest aus stdin (Scripting via Pipe).
- Bei Email-Konflikt: Exit-Code 1, klare Message via stderr.
- ``list-users`` zeigt KEINEN ``password_hash``-Wert.
"""

from __future__ import annotations

import argparse
import asyncio
import getpass
import json
import sys
from typing import TYPE_CHECKING

from auth.password import PasswordHasher
from config import get_settings
from db.engine import create_engine_from_config, create_session_factory
from db.repositories import (
    UserAlreadyExistsError,
    UserRepository,
    UserRepositoryError,
)

if TYPE_CHECKING:
    from collections.abc import Sequence


# Exit-Codes
_EXIT_OK = 0
_EXIT_USAGE_ERROR = 2
_EXIT_BUSINESS_ERROR = 1


def _read_password_stdin() -> str:
    """Liest Passwort aus stdin (ohne Prompt, fuer Scripting via pipe)."""
    pw = sys.stdin.read().rstrip("\n").rstrip("\r")
    if not pw:
        msg = "password from stdin is empty"
        raise ValueError(msg)
    return pw


def _prompt_password_interactive() -> str:
    """Interaktiver Prompt via getpass mit Bestaetigung."""
    pw1 = getpass.getpass("Password: ")
    pw2 = getpass.getpass("Password (repeat): ")
    if pw1 != pw2:
        msg = "passwords do not match"
        raise ValueError(msg)
    if not pw1:
        msg = "password must be non-empty"
        raise ValueError(msg)
    return pw1


async def _cmd_create_user(
    email: str,
    password: str,
    *,
    repo: UserRepository,
    hasher: PasswordHasher,
) -> int:
    """Erzeugt einen Local-User. Returns Exit-Code."""
    password_hash = hasher.hash(password)
    try:
        user = await repo.create(
            email=email,
            auth_method="local",
            password_hash=password_hash,
        )
    except UserAlreadyExistsError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return _EXIT_BUSINESS_ERROR
    except UserRepositoryError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return _EXIT_BUSINESS_ERROR
    print(f"created user: id={user.id}, email={user.email}, auth_method={user.auth_method}")
    return _EXIT_OK


async def _cmd_list_users(
    *,
    repo: UserRepository,
    as_json: bool,
) -> int:
    """Listet alle Users (ohne password_hash). Returns Exit-Code."""
    users = await repo.list_all()

    if as_json:
        records = [
            {
                "id": u.id,
                "email": u.email,
                "auth_method": u.auth_method,
                "external_sub": u.external_sub,
                "created_at": u.created_at.isoformat(),
                "updated_at": u.updated_at.isoformat(),
            }
            for u in users
        ]
        print(json.dumps(records, indent=2))
    else:
        if not users:
            print("(no users)")
            return _EXIT_OK
        # Plain-Text-Tabelle. Keine externe Library, manuell formatieren.
        rows: list[tuple[str, str, str, str, str]] = [
            ("id", "email", "auth_method", "external_sub", "created_at"),
        ]
        for u in users:
            rows.append(
                (
                    u.id[:8] + "...",
                    u.email,
                    u.auth_method,
                    u.external_sub or "-",
                    u.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                )
            )
        # Spalten-Breite berechnen
        col_widths = [max(len(r[i]) for r in rows) for i in range(len(rows[0]))]
        # Header
        header_line = "  ".join(c.ljust(col_widths[i]) for i, c in enumerate(rows[0]))
        sep_line = "  ".join("-" * w for w in col_widths)
        print(header_line)
        print(sep_line)
        for row in rows[1:]:
            print("  ".join(c.ljust(col_widths[i]) for i, c in enumerate(row)))
    return _EXIT_OK


async def _run_with_session(coro_factory):  # type: ignore[no-untyped-def]
    """Bootstrap-Helper: Engine + SessionFactory + Hasher hochziehen, dann coro_factory aufrufen.

    Trennt Bootstrap-Logik von Command-Logik, sodass Tests die Command-Coros mit
    Mock-Session direkt aufrufen koennen.
    """
    settings = get_settings()
    engine = create_engine_from_config(settings.database)
    session_factory = create_session_factory(engine)
    hasher = PasswordHasher(settings.argon2)
    try:
        async with session_factory() as session:
            repo = UserRepository(session)
            return await coro_factory(repo=repo, hasher=hasher)
    finally:
        await engine.dispose()


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m admin",
        description="rib-pqc Admin-CLI for user provisioning (PQC-29 / AUT-2)",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # create-user
    create = subparsers.add_parser(
        "create-user",
        help="Create a local user with Argon2id-hashed password",
        description=(
            "Create a new local user. Password is read via getpass prompt by "
            "default (no shell-history/ps-leak). Use --password-stdin to read "
            "from stdin (e.g. for pipe-based scripting)."
        ),
    )
    create.add_argument(
        "--email",
        required=True,
        help="Email address (will be lowercase-normalized)",
    )
    create.add_argument(
        "--password-stdin",
        action="store_true",
        help="Read password from stdin instead of interactive prompt",
    )

    # list-users
    list_p = subparsers.add_parser(
        "list-users",
        help="List all users without password hash",
    )
    list_p.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Output as JSON (default: plain-text table)",
    )

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "create-user":
        try:
            if args.password_stdin:
                password = _read_password_stdin()
            else:
                password = _prompt_password_interactive()
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return _EXIT_USAGE_ERROR

        async def runner(*, repo: UserRepository, hasher: PasswordHasher) -> int:
            return await _cmd_create_user(
                email=args.email,
                password=password,
                repo=repo,
                hasher=hasher,
            )

        return asyncio.run(_run_with_session(runner))

    if args.command == "list-users":

        async def runner(*, repo: UserRepository, hasher: PasswordHasher) -> int:
            del hasher  # nicht benoetigt fuer list
            return await _cmd_list_users(repo=repo, as_json=args.as_json)

        return asyncio.run(_run_with_session(runner))

    # argparse sollte unbekannte commands abfangen, defensive fallback
    parser.print_help(sys.stderr)
    return _EXIT_USAGE_ERROR


if __name__ == "__main__":
    sys.exit(main())

