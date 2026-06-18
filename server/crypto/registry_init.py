"""Init-Function fuer die CryptoRegistry.

Story-Kontext:
- PQC-21 (CRY-1): Registry-Setup, Placeholder-Plugins.
- PQC-25 (CRY-5): Signaturen werden jetzt von ``LibOqsSignature`` bedient.
- PQC-24 (CRY-4): KEMs werden jetzt von ``LibOqsKem`` bedient.
  Placeholder-Klassen bleiben als Test-Hilfsmittel (Unit-Tests die liboqs
  nicht laden wollen).

**Wichtig:** Algorithmen sind in den ``_SUPPORTED_*_ALGORITHMS``-Sets
geweisslistet. Unbekannte Namen in der Config werfen
``UnsupportedAlgorithmError``, damit Tippfehler nicht stillschweigend laufen.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from crypto.adapters.liboqs_kem import LibOqsKem
from crypto.adapters.liboqs_signature import LibOqsSignature
from crypto.registry import RegistryError

if TYPE_CHECKING:
    from crypto.registry import CryptoRegistry


# Whitelist der in Sprint 1 unterstuetzten Algorithmus-Identifier.
_SUPPORTED_KEM_ALGORITHMS: frozenset[str] = frozenset({"ML-KEM-768", "ML-KEM-1024"})
_SUPPORTED_SIGNATURE_ALGORITHMS: frozenset[str] = frozenset({"ML-DSA-65"})


class UnsupportedAlgorithmError(RegistryError):
    """Wird geworfen, wenn die Config einen Algorithmus-Namen enthaelt, den wir
    in diesem Sprint nicht supporten."""


class PlaceholderKem:
    """Placeholder-Plugin fuer KEM. Wird in CRY-3 (PQC-23) durch echten Adapter ersetzt.

    Bleibt aktuell in Verwendung, weil PQC-25 nur den Signatur-Adapter abdeckt.
    """

    def __init__(self, algorithm: str) -> None:
        self._algorithm = algorithm

    @property
    def algorithm(self) -> str:
        return self._algorithm

    def keygen(self) -> tuple[bytes, bytes]:
        msg = (
            f"PlaceholderKem({self._algorithm}).keygen() not implemented. "
            "Replace via PQC-23 (CRY-3) liboqs-KEM-Adapter."
        )
        raise NotImplementedError(msg)

    def encaps(self, public_key: bytes) -> tuple[bytes, bytes]:
        del public_key
        msg = (
            f"PlaceholderKem({self._algorithm}).encaps() not implemented. "
            "Replace via PQC-23 (CRY-3)."
        )
        raise NotImplementedError(msg)

    def decaps(self, ciphertext: bytes, secret_key: bytes) -> bytes:
        del ciphertext, secret_key
        msg = (
            f"PlaceholderKem({self._algorithm}).decaps() not implemented. "
            "Replace via PQC-23 (CRY-3)."
        )
        raise NotImplementedError(msg)


class PlaceholderSignature:
    """Placeholder-Plugin fuer Signaturen.

    Bleibt als Test-Hilfsmittel (Unit-Tests die liboqs nicht laden wollen).
    Produktiv-Registry verwendet seit PQC-25 ``LibOqsSignature``.
    """

    def __init__(self, algorithm: str) -> None:
        self._algorithm = algorithm

    @property
    def algorithm(self) -> str:
        return self._algorithm

    def keygen(self) -> tuple[bytes, bytes]:
        msg = (
            f"PlaceholderSignature({self._algorithm}).keygen() not implemented. "
            "Production registry uses LibOqsSignature since PQC-25."
        )
        raise NotImplementedError(msg)

    def sign(self, message: bytes, secret_key: bytes) -> bytes:
        del message, secret_key
        msg = (
            f"PlaceholderSignature({self._algorithm}).sign() not implemented. "
            "Production registry uses LibOqsSignature since PQC-25."
        )
        raise NotImplementedError(msg)

    def verify(self, message: bytes, signature: bytes, public_key: bytes) -> bool:
        del message, signature, public_key
        msg = (
            f"PlaceholderSignature({self._algorithm}).verify() not implemented. "
            "Production registry uses LibOqsSignature since PQC-25."
        )
        raise NotImplementedError(msg)


def init_crypto_registry(
    registry: CryptoRegistry,
    *,
    kem_supported: list[str],
    signature_supported: list[str],
) -> None:
    """Befuelle ``registry`` mit Plugins fuer die in der Config aufgelisteten
    Algorithmen.

    Aktueller Stand (Sprint 3):
    - KEMs: ``LibOqsKem`` (echt, seit PQC-24 CRY-4)
    - Signaturen: ``LibOqsSignature`` (echt, seit PQC-25 CRY-5)

    Raises:
        UnsupportedAlgorithmError: wenn ein Name in den Listen nicht in der
            internen Whitelist steht.
    """
    for alg in kem_supported:
        if alg not in _SUPPORTED_KEM_ALGORITHMS:
            msg = (
                f"Unsupported KEM algorithm '{alg}' in crypto.kem.supported. "
                f"Whitelist: {sorted(_SUPPORTED_KEM_ALGORITHMS)}"
            )
            raise UnsupportedAlgorithmError(msg)
        registry.register_kem(alg, LibOqsKem(alg))

    for alg in signature_supported:
        if alg not in _SUPPORTED_SIGNATURE_ALGORITHMS:
            msg = (
                f"Unsupported signature algorithm '{alg}' in crypto.signature.supported. "
                f"Sprint-1-Whitelist: {sorted(_SUPPORTED_SIGNATURE_ALGORITHMS)}"
            )
       