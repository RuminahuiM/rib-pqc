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
import os
import sys
from pathlib import Path
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


def _cmd_rotate_signing_key(
    *,
    new_kid: str,
    keys_dir: str,
    config_path: str | None,
) -> int:
    """Generiert ein neues ML-DSA-65 Keypair, schreibt Key-Files,
    updated die Config-YAML.

    Story: PQC-34 TOK-3.

    Workflow:
      1. Load Config-YAML (Default: settings._CONFIG_FILE_ENV oder config.yaml).
      2. Validiere dass new_kid noch nicht in keys-Dict existiert.
      3. Lade signature-Registry + Plugin, generiere Keypair.
      4. Speichere {keys_dir}/{new_kid}.bin + {new_kid}.pub.
      5. Update YAML: keys-Dict um neuen Eintrag erweitern, active_kid auf new_kid setzen.
      6. Print Confirmation.

    Lock-File-Schutz gegen concurrent rotations via {keys_dir}/.rotate.lock.
    """
    import yaml

    from crypto import keys as keys_module
    from crypto.registry_init import init_crypto_registry
    from crypto.registry import CryptoRegistry

    keys_dir_path = Path(keys_dir)
    keys_dir_path.mkdir(parents=True, exist_ok=True)
    lock_file = keys_dir_path / ".rotate.lock"
    if lock_file.exists():
        print(
            f"error: rotation lock exists at {lock_file}. Remove if stale.",
            file=sys.stderr,
        )
        return _EXIT_USAGE_ERROR
    lock_file.touch()
    try:
        # 1. Config-Path bestimmen.
        if config_path is None:
            settings_path = os.environ.get("RIB_CONFIG_FILE", "config.yaml")
        else:
            settings_path = config_path
        cfg_file = Path(settings_path)
        if not cfg_file.exists():
            print(f"error: config file not found: {cfg_file}", file=sys.stderr)
            return _EXIT_USAGE_ERROR
        with cfg_file.open("r", encoding="utf-8") as f:
            cfg_data = yaml.safe_load(f) or {}

        # 2. new_kid uniqueness check
        sig_node = cfg_data.setdefault("crypto", {}).setdefault("signature", {})
        keys_node = sig_node.setdefault("keys", {}) or {}
        if new_kid in keys_node:
            print(
                f"error: kid '{new_kid}' already in keys-Dict. "
                f"Pick a different kid.",
                file=sys.stderr,
            )
            return _EXIT_USAGE_ERROR

        # 3. Keypair generieren via Registry
        registry = CryptoRegistry()
        sig_supported = sig_node.get("supported", ["ML-DSA-65"])
        kem_supported = (
            cfg_data.get("crypto", {}).get("kem", {}).get("supported", ["ML-KEM-768"])
        )
        init_crypto_registry(
            registry,
            kem_supported=kem_supported,
            signature_supported=sig_supported,
        )
        sig_alg = sig_node.get("default", "ML-DSA-65")
        plugin = registry.get_signature(sig_alg)
        public_key, secret_key = plugin.keygen()

        # 4. Speichern
        private_path = keys_dir_path / f"{new_kid}.bin"
        public_path = keys_dir_path / f"{new_kid}.pub"
        keys_module.save_secret_key(private_path, secret_key)
        keys_module.save_public_key(public_path, public_key)

        # 5. Config-YAML updaten
        keys_node[new_kid] = {
            "private_key_path": str(private_path),
            "public_key_path": str(public_path),
        }
        sig_node["keys"] = keys_node
        sig_node["active_kid"] = new_kid
        with cfg_file.open("w", encoding="utf-8") as f:
            yaml.safe_dump(cfg_data, f, default_flow_style=False, sort_keys=False)

        # 6. Confirmation
        print(
            f"OK: rotated signing key.\n"
            f"  new_kid    = {new_kid}\n"
            f"  active_kid = {new_kid}\n"
            f"  private    = {private_path}\n"
            f"  public     = {public_path}\n"
            f"  config     = {cfg_file}\n"
            f"  total_keys = {len(keys_node)}",
        )
        return 0
    finally:
        lock_file.unlink(missing_ok=True)


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

    # rotate-signing-key (PQC-34 TOK-3)
    rotate = subparsers.add_parser(
        "rotate-signing-key",
        help="Generate a new ML-DSA-65 signing keypair, write Key-Files and update config",
        description=(
            "Generates a fresh ML-DSA-65 keypair and registers it in the\n"
            "config under crypto.signature.keys[<kid>]. Sets active_kid to\n"
            "the new kid. Existing keys remain in the keys-Dict for\n"
            "verification of older tokens. Key-Files default into\n"
            "/data/keys/<kid>.bin + <kid>.pub."
        ),
    )
    rotate.add_argument(
        "--new-kid",
        required=True,
        help="New kid (Key-ID) for the keypair, must be unique in keys-Dict",
    )
    rotate.add_argument(
        "--keys-dir",
        default="/data/keys",
        help="Directory for the key files (default /data/keys)",
    )
    rotate.add_argument(
        "--config-path",
        default=None,
        help="Path to config.yaml (default from settings: rib-pqc internal lookup)",
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

    if args.command == "rotate-signing-key":
        return _cmd_rotate_signing_key(
            new_kid=args.new_kid,
            keys_dir=args.keys_dir,
            config_path=args.config_path,
        )

    # argparse sollte unbekannte commands abfangen, defensive fallback
    parser.print_help(sys.stderr)
    return _EXIT_USAGE_ERROR


if __name__ == "__main__":
    sys.exit(main())

