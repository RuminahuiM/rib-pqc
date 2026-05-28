"""User-Repository: Persistenz-Operationen fuer User-Records.

Story: PQC-28 (AUT-1) AC-3, AC-5.

Pattern: Konstruktor-DI mit ``AsyncSession``. Pro Request bekommt die
Repository-Instanz die Session vom FastAPI-Depends-Mechanismus. Tests koennen
``MockUserRepository`` mit gleichem Interface verwenden.

Geschaeftsregeln (vom Repository validiert, nicht von der DB):
- ``email`` wird vor dem Speichern lowercase-normalisiert.
- ``auth_method`` muss aus Whitelist sein.
- Bei ``auth_method='local'`` MUSS ``password_hash`` gesetzt sein.
- Bei federated (``google``, ``microsoft``) MUSS ``external_sub`` gesetzt sein
  und ``password_hash`` SOLL ``None`` sein.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from logging_config import get_logger
from models.user import User

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


_logger = get_logger("rib_pqc.db.user_repo")


_SUPPORTED_AUTH_METHODS: frozenset[str] = frozenset({"local", "google", "microsoft"})


class UserRepositoryError(Exception):
    """Basis-Fehler fuer UserRepository-Probleme."""


class UserAlreadyExistsError(UserRepositoryError):
    """Email ist bereits in der Datenbank registriert."""


class InvalidUserDataError(UserRepositoryError):
    """User-Daten verletzen Geschaeftsregeln (z.B. local ohne password_hash)."""


def _normalize_email(email: str) -> str:
    """Lowercase plus strip fuer konsistente Email-Lookups."""
    return email.strip().lower()


class UserRepository:
    """CRUD-Operationen fuer ``users``-Tabelle mit Geschaeftsregel-Validation."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # -----------------------------------------------------------------------
    # Create
    # -----------------------------------------------------------------------

    async def create(
        self,
        *,
        email: str,
        auth_method: str,
        password_hash: str | None = None,
        external_sub: str | None = None,
    ) -> User:
        """Legt einen neuen User-Record an und commit'tet.

        Args:
            email: wird lowercase-normalisiert.
            auth_method: ``"local"``, ``"google"`` oder ``"microsoft"``.
            password_hash: Argon2id-Hash bei ``local``, ``None`` bei federated.
            external_sub: externe sub bei federated, ``None`` bei local.

        Returns:
            den gespeicherten User mit generierter ``id`` und Timestamps.

        Raises:
            InvalidUserDataError: bei Geschaeftsregel-Verletzung.
            UserAlreadyExistsError: bei Duplicate-Email.
        """
        if not email:
            msg = "email must be a non-empty string"
            raise InvalidUserDataError(msg)
        if auth_method not in _SUPPORTED_AUTH_METHODS:
            msg = (
                f"unsupported auth_method '{auth_method}'. "
                f"allowed: {sorted(_SUPPORTED_AUTH_METHODS)}"
            )
            raise InvalidUserDataError(msg)
        if auth_method == "local" and not password_hash:
            msg = "auth_method='local' requires non-empty password_hash"
            raise InvalidUserDataError(msg)
        if auth_method != "local":
            if not external_sub:
                msg = f"auth_method='{auth_method}' requires non-empty external_sub"
                raise InvalidUserDataError(msg)
            if password_hash is not None:
                msg = f"auth_method='{auth_method}' must NOT have password_hash"
                raise InvalidUserDataError(msg)

        normalized_email = _normalize_email(email)
        user = User(
            email=normalized_email,
            auth_method=auth_method,
            password_hash=password_hash,
            external_sub=external_sub,
        )
        self._session.add(user)
        try:
            await self._session.flush()
        except IntegrityError as exc:
            await self._session.rollback()
            msg = f"user with email '{normalized_email}' already exists"
            raise UserAlreadyExistsError(msg) from exc
        await self._session.commit()
        await self._session.refresh(user)
        _logger.info(
            "user.created",
            user_id=user.id,
            auth_method=auth_method,
            external_sub_present=external_sub is not None,
        )
        return user

    # -----------------------------------------------------------------------
    # Find
    # -----------------------------------------------------------------------

    async def find_by_email(self, email: str) -> User | None:
        """Sucht einen User per (case-insensitiver) Email.

        Returns:
            User oder ``None`` wenn nicht gefunden.
        """
        if not email:
            return None
        normalized = _normalize_email(email)
        stmt = select(User).where(User.email == normalized)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_id(self, user_id: str) -> User | None:
        """Sucht einen User per UUID-String."""
        if not user_id:
            return None
        return await self._session.get(User, user_id)

    async def list_all(self) -> list[User]:
        """Liefert alle User-Records, sortiert nach created_at (asc).

        Wird vom Admin-CLI (PQC-29 AUT-2) fuer ``list-users`` verwendet.
        Sprint-1: keine Pagination - bei wachsender User-Base muss das
        spaeter durch ein gepagedtes Interface ersetzt werden.
        """
        stmt = select(User).order_by(User.created_at)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_external(
        self, auth_method: str, external_sub: str
    ) -> User | None:
        """Sucht einen federated User per (auth_method, external_sub)-Composite.

        Wird von BRK-4 (Broker-Login) verwendet, hier schon angelegt damit das
        Schema beim ersten Touch ready ist.
        """
        if not auth_method or not external_sub:
            return None
        stmt = select(User).where(
            User.auth_method == auth_method, User.external_sub == external_sub
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
