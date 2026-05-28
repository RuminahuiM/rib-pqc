"""Tests fuer admin.py Admin-CLI (PQC-29 / AUT-2).

Story: PQC-29 AC-1 bis AC-5.

Wir testen die Command-Coroutines (_cmd_create_user, _cmd_list_users) direkt
mit einer in-memory SQLite-Session, statt main(argv) durch asyncio.run zu
fahren (weniger Setup-Boilerplate, dieselbe Coverage).
"""

from __future__ import annotations

import io
import json
from typing import TYPE_CHECKING

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from admin import (
    _EXIT_BUSINESS_ERROR,
    _EXIT_OK,
    _cmd_create_user,
    _cmd_list_users,
    _prompt_password_interactive,
    _read_password_stdin,
)
from auth.password import PasswordHasher
from config import Argon2Config
from db.repositories import UserRepository
from models import Base

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession


@pytest_asyncio.fixture
async def engine() -> AsyncEngine:
    eng = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    await eng.dispose()


@pytest_asyncio.fixture
async def session(engine: AsyncEngine) -> AsyncSession:
    sf = async_sessionmaker(bind=engine, expire_on_commit=False)
    async with sf() as s:
        yield s


@pytest_asyncio.fixture
async def repo(session: AsyncSession) -> UserRepository:
    return UserRepository(session)


@pytest.fixture
def hasher() -> PasswordHasher:
    """Schneller Hasher fuer Tests."""
    return PasswordHasher(
        Argon2Config(memory_cost_kb=8192, time_cost=1, parallelism=1)
    )


# ---------------------------------------------------------------------------
# _read_password_stdin
# ---------------------------------------------------------------------------


def test_read_password_stdin_returns_password(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("sys.stdin", io.StringIO("my-secret-pw\n"))
    assert _read_password_stdin() == "my-secret-pw"


def test_read_password_stdin_strips_crlf(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("sys.stdin", io.StringIO("with-crlf\r\n"))
    assert _read_password_stdin() == "with-crlf"


def test_read_password_stdin_empty_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("sys.stdin", io.StringIO(""))
    with pytest.raises(ValueError, match="empty"):
        _read_password_stdin()


# ---------------------------------------------------------------------------
# _prompt_password_interactive
# ---------------------------------------------------------------------------


def test_prompt_password_matching(monkeypatch: pytest.MonkeyPatch) -> None:
    """getpass returns same password twice -> success."""
    answers = iter(["pw1", "pw1"])
    monkeypatch.setattr("getpass.getpass", lambda _: next(answers))
    assert _prompt_password_interactive() == "pw1"


def test_prompt_password_mismatch_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    answers = iter(["pw1", "pw2"])
    monkeypatch.setattr("getpass.getpass", lambda _: next(answers))
    with pytest.raises(ValueError, match="do not match"):
        _prompt_password_interactive()


def test_prompt_password_empty_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    answers = iter(["", ""])
    monkeypatch.setattr("getpass.getpass", lambda _: next(answers))
    with pytest.raises(ValueError, match="non-empty"):
        _prompt_password_interactive()


# ---------------------------------------------------------------------------
# _cmd_create_user (AC-1, AC-2, AC-3, AC-4)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_user_happy_path(
    repo: UserRepository, hasher: PasswordHasher, capsys: pytest.CaptureFixture
) -> None:
    """AC-1, AC-2, AC-3: User wird angelegt mit Argon2id-Hash und auth_method=local."""
    exit_code = await _cmd_create_user(
        email="alice@example.com",
        password="secret-pw",
        repo=repo,
        hasher=hasher,
    )
    assert exit_code == _EXIT_OK
    out = capsys.readouterr().out
    assert "created user" in out
    assert "alice@example.com" in out
    assert "auth_method=local" in out

    # Verifikation in DB
    user = await repo.find_by_email("alice@example.com")
    assert user is not None
    assert user.auth_method == "local"
    assert user.password_hash is not None
    assert user.password_hash.startswith("$argon2id$")
    # AC-2: Argon2id-Hash kann das urspruengliche Passwort verifizieren
    assert hasher.verify("secret-pw", user.password_hash) is True


@pytest.mark.asyncio
async def test_create_user_duplicate_email_exits_with_error(
    repo: UserRepository, hasher: PasswordHasher, capsys: pytest.CaptureFixture
) -> None:
    """AC-4: Email-Konflikt -> Exit-Code 1, klare Message auf stderr."""
    await _cmd_create_user(email="dup@test.com", password="pw1", repo=repo, hasher=hasher)
    exit_code = await _cmd_create_user(
        email="dup@test.com", password="pw2", repo=repo, hasher=hasher
    )
    assert exit_code == _EXIT_BUSINESS_ERROR
    captured = capsys.readouterr()
    assert "already exists" in captured.err


@pytest.mark.asyncio
async def test_create_user_lowercase_normalizes_email(
    repo: UserRepository, hasher: PasswordHasher
) -> None:
    await _cmd_create_user(
        email="MixedCase@Example.COM", password="pw", repo=repo, hasher=hasher
    )
    user = await repo.find_by_email("mixedcase@example.com")
    assert user is not None
    assert user.email == "mixedcase@example.com"


# ---------------------------------------------------------------------------
# _cmd_list_users (AC-5)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_users_empty_plain_text(
    repo: UserRepository, capsys: pytest.CaptureFixture
) -> None:
    """Leere Tabelle -> Marker '(no users)' output."""
    exit_code = await _cmd_list_users(repo=repo, as_json=False)
    assert exit_code == _EXIT_OK
    assert "(no users)" in capsys.readouterr().out


@pytest.mark.asyncio
async def test_list_users_empty_json(
    repo: UserRepository, capsys: pytest.CaptureFixture
) -> None:
    """Leere Tabelle als JSON -> leere Liste."""
    exit_code = await _cmd_list_users(repo=repo, as_json=True)
    assert exit_code == _EXIT_OK
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data == []


@pytest.mark.asyncio
async def test_list_users_with_records_plain_text(
    repo: UserRepository, hasher: PasswordHasher, capsys: pytest.CaptureFixture
) -> None:
    """Mehrere Users -> Tabelle mit Spalten id, email, auth_method, etc."""
    await _cmd_create_user(
        email="alice@example.com", password="pw", repo=repo, hasher=hasher
    )
    await repo.create(
        email="bob@google.com", auth_method="google", external_sub="google|abc"
    )
    capsys.readouterr()  # Buffer leeren
    exit_code = await _cmd_list_users(repo=repo, as_json=False)
    assert exit_code == _EXIT_OK
    out = capsys.readouterr().out
    # Spalten-Header sind drin
    assert "email" in out
    assert "auth_method" in out
    assert "external_sub" in out
    # Beide Users sind drin
    assert "alice@example.com" in out
    assert "bob@google.com" in out
    # password_hash darf nicht erscheinen (AC-5: ohne password)
    assert "argon2" not in out.lower()
    # external_sub erscheint fuer federated User
    assert "google|abc" in out


@pytest.mark.asyncio
async def test_list_users_with_records_json(
    repo: UserRepository, hasher: PasswordHasher, capsys: pytest.CaptureFixture
) -> None:
    """JSON-Output enthaelt alle Felder ausser password_hash."""
    await _cmd_create_user(
        email="alice@example.com", password="pw", repo=repo, hasher=hasher
    )
    capsys.readouterr()
    exit_code = await _cmd_list_users(repo=repo, as_json=True)
    assert exit_code == _EXIT_OK
    out = capsys.readouterr().out
    data = json.loads(out)
    assert len(data) == 1
    rec = data[0]
    assert rec["email"] == "alice@example.com"
    assert rec["auth_method"] == "local"
    assert rec["external_sub"] is None
    assert "id" in rec
    assert "created_at" in rec
    assert "updated_at" in rec
    # password_hash darf NICHT im JSON sein
    assert "password_hash" not in rec
    assert "password" not in rec


@pytest.mark.asyncio
async def test_list_users_orders_by_created_at(
    repo: UserRepository, hasher: PasswordHasher, capsys: pytest.CaptureFixture
) -> None:
    """list-users sortiert nach created_at."""
    import asyncio

    await _cmd_create_user(email="first@x.com", password="pw", repo=repo, hasher=hasher)
    await asyncio.sleep(0.01)  # genug Timestamp-Differenz fuer SQLite
    await _cmd_create_user(email="second@x.com", password="pw", repo=repo, hasher=hasher)
    capsys.readouterr()
    await _cmd_list_users(repo=repo, as_json=True)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert [r["email"] for r in data] == ["first@x.com", "second@x.com"]
