"""Repository-Pattern fuer Datenbank-Aggregate.

Stories:
- PQC-28 (AUT-1) AC-3: UserRepository
- PQC-39 (BRK-4): UserIdentityRepository
"""

from __future__ import annotations

from db.repositories.user_identity_repository import (
    IdentityAlreadyExistsError,
    InvalidIdentityDataError,
    UserIdentityRepository,
    UserIdentityRepositoryError,
)
from db.repositories.user_repository import (
    UserAlreadyExistsError,
    UserRepository,
    UserRepositoryError,
)

__all__ = [
    "IdentityAlreadyExistsError",
    "InvalidIdentityDataError",
    "UserAlreadyExistsError",
    "UserIdentityRepository",
    "UserIdentityRepositoryError",
    "UserRepository",
    "UserRepositoryError",
]
