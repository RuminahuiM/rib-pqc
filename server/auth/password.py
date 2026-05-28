"""Argon2id-Password-Hasher mit Tuning per Config.

Story: PQC-28 (AUT-1) AC-4.

Verwendet ``argon2-cffi``-Bindings (de-facto-Standard in Python-Ecosystem).
Parameter aus ``settings.argon2`` mit Story-AC-4 Default (m=64MB, t=3, p=4).

**API:**

- ``PasswordHasher.hash(plain_password) -> str``: erzeugt Argon2id-Hash.
- ``PasswordHasher.verify(plain_password, hashed) -> bool``: prueft Plaintext
  gegen Hash. Liefert ``False`` bei Mismatch ohne Exception. Sicher gegen
  ungueltigen Hash-String.
- ``PasswordHasher.needs_rehash(hashed) -> bool``: signalisiert ob Hash mit
  alten Parametern erstellt wurde und bei naechstem Login neu gehashed werden
  sollte. AUT-3 Use-Case.
- ``PasswordHasher.dummy_verify()``: konstant-zeit-Dummy-Verify fuer
  User-Enumeration-Schutz (PQC-31 AUT-4 Vorbereitung).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from argon2 import PasswordHasher as Argon2Hasher
from argon2 import Type as Argon2Type
from argon2.exceptions import (
    InvalidHashError,
    VerifyMismatchError,
)

from logging_config import get_logger

if TYPE_CHECKING:
    from config import Argon2Config


_logger = get_logger("rib_pqc.auth.password")


# Pre-computed Dummy-Hash fuer constant-time User-Enumeration-Schutz
# (AUT-4-Vorbereitung). Wird beim Modul-Load erzeugt mit Default-Params, ist
# also unabhaengig von Settings (auch wenn Tuning sich aendert, der Schutz
# bleibt funktional). Wert ist konstant pro Prozess-Lebenszeit.
_DUMMY_HASH: str = Argon2Hasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
    type=Argon2Type.ID,
).hash("dummy-password-for-enumeration-defense")


class PasswordHasher:
    """Argon2id-Wrapper mit Config-Tuning und User-Enumeration-Schutz.

    Konstruktor liest Tuning aus ``Argon2Config`` und erstellt einen
    internen ``argon2.PasswordHasher`` mit den gewuenschten Parametern.
    """

    def __init__(self, config: Argon2Config) -> None:
        self._config = config
        self._hasher = Argon2Hasher(
            time_cost=config.time_cost,
            memory_cost=config.memory_cost_kb,
            parallelism=config.parallelism,
            hash_len=config.hash_length,
            salt_len=config.salt_length,
            type=Argon2Type.ID,
        )
        _logger.info(
            "password_hasher.initialized",
            type="argon2id",
            memory_cost_kb=config.memory_cost_kb,
            time_cost=config.time_cost,
            parallelism=config.parallelism,
            salt_length=config.salt_length,
            hash_length=config.hash_length,
        )

    def hash(self, plain_password: str) -> str:
        """Hasht plain_password mit den konfigurierten Argon2id-Parametern.

        Args:
            plain_password: das zu hashende Passwort.

        Returns:
            Argon2id-Hash-String im Standard-Argon2-Format
            (``$argon2id$v=19$m=...,t=...,p=...$salt$hash``).
        """
        if not plain_password:
            msg = "plain_password must be a non-empty string"
            raise ValueError(msg)
        return self._hasher.hash(plain_password)

    def verify(self, plain_password: str, hashed: str) -> bool:
        """Prueft plain_password gegen hashed.

        Liefert ``False`` bei Mismatch oder ungueltigem Hash-String. Wirft
        keine Exception, sodass Endpoint-Code einfach branchen kann.

        Args:
            plain_password: das zu pruefende Passwort.
            hashed: Argon2id-Hash aus DB.

        Returns:
            ``True`` bei korrektem Passwort, ``False`` sonst.
        """
        if not plain_password or not hashed:
            return False
        try:
            return self._hasher.verify(hashed, plain_password)
        except VerifyMismatchError:
            return False
        except InvalidHashError:
            _logger.warning("password_hasher.invalid_hash_string")
            return False

    def needs_rehash(self, hashed: str) -> bool:
        """Signal ob hashed mit alten/anderen Parametern erstellt wurde.

        Wenn ``True``: nach erfolgreichem Login mit dem alten Hash kann der
        Endpoint-Code das Passwort mit aktuellen Parametern re-hashen und
        speichern. So migriert die User-Base ohne Mass-Operation.
        """
        try:
            return self._hasher.check_needs_rehash(hashed)
        except InvalidHashError:
            return True

    def dummy_verify(self) -> None:
        """Constant-Time-Dummy-Verify fuer User-Enumeration-Schutz (AUT-4).

        Bei unbekannter Email im Login soll Response-Zeit identisch zu
        falscher-Passwort-Case sein. Diese Methode konsumiert die gleiche
        CPU-Zeit wie ein echter verify-Call gegen den Dummy-Hash.

        Returns:
            None. Exceptions werden geschluckt (Dummy ist by Design ein Mismatch).
        """
        import contextlib

        # Erwartet, der Dummy-Hash matched nichts. Wir wollen nur die CPU-Zeit.
        with contextlib.suppress(VerifyMismatchError, InvalidHashError):
            self._hasher.verify(_DUMMY_HASH, "different-password")
