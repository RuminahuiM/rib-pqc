"""CryptoRegistry: zentrale Plugin-Registry fuer KEM- und Signatur-Algorithmen.

Story: PQC-21 (CRY-1).
Architektur-Bezug: docs/07_design.md Abschnitte 6.1, 6.2, 6.3.

**Designprinzipien:**

- Plugins sind ``typing.Protocol``-Klassen mit ``@runtime_checkable``,
  damit Plugin-Adapter (z.B. der liboqs-Adapter aus PQC-25) ohne explicit
  Inheritance einfach passende Methoden anbieten muessen. Strukturelles
  Subtyping passt zum Plugin-Charakter besser als ABC.
- Algorithmus-Namen folgen NIST-Standard ("ML-KEM-768", "ML-DSA-65"),
  keine Pre-Standard-Namen wie "Kyber768" oder "Dilithium3".
- Registry kennt KEINE konkreten Implementationen (kein liboqs-Import).
  Plugin-Adapter werden in PQC-25 (CRY-5) hinzugefuegt.

**Verwendungsbeispiel::**

    from crypto.registry import CryptoRegistry, KemPlugin

    registry = CryptoRegistry()
    registry.register_kem("ML-KEM-768", my_kem_plugin)
    plugin = registry.get_kem("ML-KEM-768")
    pk, sk = plugin.keygen()

In Tests kann ein Mock-Plugin registriert werden, ohne dass liboqs verfuegbar
sein muss.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


class RegistryError(Exception):
    """Basis-Fehler fuer alle Registry-bezogenen Probleme."""


class DuplicateAlgorithmError(RegistryError):
    """Wird geworfen, wenn ein bereits registrierter Algorithmus erneut registriert wird.

    Doppel-Registrierung wuerde stillschweigend ueberschreiben, was bei
    Crypto-Code zu schwer auffindbaren Bugs fuehrt (z.B. falscher Plugin
    fuer denselben Namen).
    """


class AlgorithmNotFoundError(RegistryError):
    """Wird geworfen, wenn ein angefragter Algorithmus nicht registriert ist."""


@runtime_checkable
class KemPlugin(Protocol):
    """Strukturelle Schnittstelle fuer KEM-Implementationen (ML-KEM-* etc.).

    Spec orientiert sich an liboqs.KeyEncapsulation und ML-KEM (FIPS 203).
    Konkrete Adapter (z.B. PQC-25 LibOqsKem) muessen lediglich diese Methoden
    bereitstellen, kein ``isinstance(plugin, KemPlugin)``-Vererbung noetig.
    """

    @property
    def algorithm(self) -> str:
        """NIST-Algorithmus-Name, z.B. 'ML-KEM-768'."""

    def keygen(self) -> tuple[bytes, bytes]:
        """Liefert (public_key, secret_key)."""

    def encaps(self, public_key: bytes) -> tuple[bytes, bytes]:
        """Liefert (ciphertext, shared_secret) fuer den uebergebenen Public Key."""

    def decaps(self, ciphertext: bytes, secret_key: bytes) -> bytes:
        """Liefert shared_secret aus ciphertext und secret_key."""


@runtime_checkable
class SignaturePlugin(Protocol):
    """Strukturelle Schnittstelle fuer Signatur-Implementationen (ML-DSA-* etc.).

    Spec orientiert sich an liboqs.Signature und ML-DSA (FIPS 204).
    """

    @property
    def algorithm(self) -> str:
        """NIST-Algorithmus-Name, z.B. 'ML-DSA-65'."""

    def keygen(self) -> tuple[bytes, bytes]:
        """Liefert (public_key, secret_key)."""

    def sign(self, message: bytes, secret_key: bytes) -> bytes:
        """Liefert die Signatur ueber ``message`` unter ``secret_key``."""

    def verify(self, message: bytes, signature: bytes, public_key: bytes) -> bool:
        """Liefert True, wenn die Signatur unter ``public_key`` gueltig ist."""


class CryptoRegistry:
    """In-Memory-Registry fuer KEM- und Signatur-Algorithmen.

    Ein Service hat genau eine Registry-Instanz, die beim Service-Start
    ueber ``crypto.registry_init.init_crypto_registry`` befuellt wird.

    Threadsafety: aktuell nicht thread-safe. Die Registry wird nur einmal
    beim Service-Start befuellt und danach read-only verwendet. Falls
    spaeter dynamisches Hot-Reload-Registrieren noetig wird, lock einbauen.
    """

    def __init__(self) -> None:
        self._kem: dict[str, KemPlugin] = {}
        self._signature: dict[str, SignaturePlugin] = {}

    # ----- KEM ---------------------------------------------------------------

    def register_kem(self, name: str, plugin: KemPlugin) -> None:
        """Registriert ein KEM-Plugin unter ``name``.

        Raises:
            DuplicateAlgorithmError: wenn ``name`` bereits registriert ist.
        """
        if name in self._kem:
            msg = f"KEM algorithm '{name}' is already registered"
            raise DuplicateAlgorithmError(msg)
        self._kem[name] = plugin

    def get_kem(self, name: str) -> KemPlugin:
        """Liefert das KEM-Plugin fuer ``name``.

        Raises:
            AlgorithmNotFoundError: wenn ``name`` nicht registriert ist.
        """
        try:
            return self._kem[name]
        except KeyError as exc:
            msg = f"KEM algorithm '{name}' is not registered. Known: {sorted(self._kem)}"
            raise AlgorithmNotFoundError(msg) from exc

    def supported_kem(self) -> list[str]:
        """Liefert die Namen aller registrierten KEM-Algorithmen, sortiert."""
        return sorted(self._kem)

    # ----- Signature ---------------------------------------------------------

    def register_signature(self, name: str, plugin: SignaturePlugin) -> None:
        """Registriert ein Signatur-Plugin unter ``name``.

        Raises:
            DuplicateAlgorithmError: wenn ``name`` bereits registriert ist.
        """
        if name in self._signature:
            msg = f"Signature algorithm '{name}' is already registered"
            raise DuplicateAlgorithmError(msg)
        self._signature[name] = plugin

    def get_signature(self, name: str) -> SignaturePlugin:
        """Liefert das Signatur-Plugin fuer ``name``.

        Raises:
            AlgorithmNotFoundError: wenn ``name`` nicht registriert ist.
        """
        try:
            return self._signature[name]
        except KeyError as exc:
            msg = (
                f"Signature algorithm '{name}' is not registered. Known: {sorted(self._signature)}"
            )
            raise AlgorithmNotFoundError(msg) from exc

    def supported_signature(self) -> list[str]:
        """Liefert die Namen aller registrierten Signatur-Algorithmen, sortiert."""
        return sorted(self._signature)
