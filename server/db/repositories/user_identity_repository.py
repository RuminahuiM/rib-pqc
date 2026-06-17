"""UserIdentityRepository: CRUD fuer user_identities-Tabelle.

Story: PQC-39 (BRK-4) AC-1, AC-2, AC-4.

Pattern: AsyncSession-DI analog UserRepository. Geschaeftsregeln (z.B.
auth_method-Whitelist) werden hier validiert.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from logging_config import get_logger
from models.user_identity import UserIdentity

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


_logger = get_logger("rib_pqc.db.user_identity_repo")


_SUPPORTED_AUTH_METHODS: frozenset[str] = frozenset({"google", "microsoft"})


class UserIdentityRepositoryError(Exception):
    """Basis-Fehler fuer UserIdentityRepository-Probleme."""


class InvalidIdentityDataError(UserIdentityRepositoryError):
    """Identity-Daten verletzen Geschaeftsregeln."""


class IdentityAlreadyExistsError(UserIdentityRepositoryError):
    """``(auth_method, external_sub)`` ist bereits global registriert."""


class UserIdentityRepository:
    """CRUD-Operationen fuer ``user_identities``-Tabelle."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # -----------------------------------------------------------------------
    # Create
    # -----------------------------------------------------------------------

    async def create(
        self,
        *,
        user_id: str,
        auth_method: str,
        external_sub: str,
    ) -> UserIdentity:
        """Legt einen neuen UserIdentity-Row an und commit'tet.

        Story-Bezug: PQC-39 AC-1, AC-4.

        Raises:
            InvalidIdentityDataError: bei leeren Pflichtfeldern oder
                ungueltigem auth_method.
            IdentityAlreadyExistsError: bei Duplikat ``(auth_method,
                external_sub)`` global.
        """
        if not user_id:
            msg = "user_id must be non-empty"
            raise InvalidIdentityDataError(msg)
        if auth_method not in _SUPPORTED_AUTH_METHODS:
            msg = (
                f"unsupported auth_method '{auth_method}'. "
                f"allowed: {sorted(_SUPPORTED_AUTH_METHODS)}"
            )
            raise InvalidIdentityDataError(msg)
        if not external_sub:
            msg = "external_sub must be non-empty"
            raise InvalidIdentityDataError(msg)

        identity = UserIdentity(
            user_id=user_id,
            auth_method=auth_method,
            external_sub=external_sub,
        )
        self._session.add(identity)
        try:
            await self._session.flush()
        except IntegrityError as exc:
            await self._session.rollback()
            msg = (
                f"identity (auth_method={auth_method!r}, "
                f"external_sub={external_sub!r}) already exists"
            )
            raise IdentityAlreadyExistsError(msg) from exc
        await self._session.commit()
        await self._session.refresh(identity)
        _logger.info(
            "user_identity.created",
            identity_id=identity.id,
            user_id=user_id,
            auth_method=auth_method,
        )
        return identity

    # -----------------------------------------------------------------------
    # Find
    # -----------------------------------------------------------------------

    async def find_by_external(
        self,
        *,
        auth_method: str,
        external_sub: str,
    ) -> UserIdentity | None:
        """Sucht eine Identity per Composite-Key.

        Story-Bezug: PQC-39 AC-2.
        """
        if not auth_method or not external_sub:
            return None
        stmt = select(UserIdentity).where(
            UserIdentity.auth_method == auth_method,
            UserIdentity.external_sub == external_sub,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_for_user(self, user_id: str) -> list[UserIdentity]:
        """Liefert alle Identities die zu einem User gehoeren."""
        if not user_id:
            return []
        stmt = (
            select(UserIdentity)
            .where(UserIdentity.user_id == user_id)
            .order_by(UserIdentity.created_at)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
