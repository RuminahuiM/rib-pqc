"""Init-Function fuer die CryptoRegistry, plus Sprint-1-Placeholder-Plugins.

Story: PQC-21 (CRY-1), Acceptance Criterion AC-4.
Architektur-Bezug: docs/07_design.md Abschnitt 6.3.

**Wichtig fuer Sprint 1:**
Diese Datei registriert *Placeholder*-Plugins, keine echten liboqs-Adapter.
PQC-25 (CRY-5) tauscht die ``PlaceholderKem`` und ``PlaceholderSignature``
durch ``LibOqsKem`` und ``LibOqsSignature`` aus. Damit ist R-T01 (liboqs-Build
schlaegt fehl, siehe ``docs/11_risk_register.md``) auf eine einzige Story
isoliert und CRY-1 kann ohne liboqs-Container getestet werden.

**Erlaubte Algorithmen** (per Tech-Stack-Doku 2.3 und Project-Decisions):

- KEM: ``ML-KEM-768``, ``ML-KEM-1024`` (FIPS 203)
- Signature: ``ML-DSA-65`` (FIPS 204)

Unbekannte Namen in der Config werfen ``UnsupportedAlgorithmError``, damit
Tippfehler im Setup nicht stillschweigend laufen.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from crypto.registry import RegistryError

if TYPE_CHECKING:
    from crypto.registry import CryptoRegistry


# Whitelist der in Sprint 1 unterstuetzten Algorithmus-Identifier.
# In PQC-25 (CRY-5) wird diese Liste auch geprueft, bevor wir auf liboqs zugreifen.
_SUPPORTED_KEM_ALGORITHMS: frozenset[str] = frozenset({"ML-KEM-768", "ML-KEM-1024"})
_SUPPORTED_SIGNATURE_ALGORITHMS: frozenset[str] = frozenset({"ML-DSA-65"})


class UnsupportedAlgorithmError(RegistryError):
    """Wird geworfen, wenn die Config einen Algorithmus-Namen enthaelt, den wir
    in diesem Sprint nicht supporten (z.B. Tippfehler 'ML-KEM-512')."""


class PlaceholderKem:
    """Placeholder-Plugin, das die ``KemPlugin``-Protocol-Methoden hat, aber
    bei jedem Crypto-Call ``NotImplementedError`` wirft.

    Wird in Sprint 1 registriert, damit AC-4 erfuellbar ist. PQC-25 ersetzt
    durch echten liboqs-Adapter.
    """

    def __init__(self, algorithm: str) -> None:
        self._algorithm = algorithm

    @property
    def algorithm(self) -> str:
        return self._algorithm

    def keygen(self) -> tuple[bytes, bytes]:
        msg = (
            f"PlaceholderKem({self._algorithm}).keygen() not implemented. "
            "Replace via PQC-25 (CRY-5) liboqs-Adapter."
        )
        raise NotImplementedError(msg)

    def encaps(self, public_key: bytes) -> tuple[bytes, bytes]:
        del public_key
        msg = (
            f"PlaceholderKem({self._algorithm}).encaps() not implemented. "
            "Replace via PQC-25 (CRY-5)."
        )
        raise NotImplementedError(msg)

    def decaps(self, ciphertext: bytes, secret_key: bytes) -> bytes:
        del ciphertext, secret_key
        msg = (
            f"PlaceholderKem({self._algorithm}).decaps() not implemented. "
            "Replace via PQC-25 (CRY-5)."
        )
        raise NotImplementedError(msg)


class PlaceholderSignature:
    """Placeholder-Plugin fuer Signaturen, analog zu ``PlaceholderKem``."""

    def __init__(self, algorithm: str) -> None:
        self._algorithm = algorithm

    @property
    def algorithm(self) -> str:
        return self._algorithm

    def keygen(self) -> tuple[bytes, bytes]:
        msg = (
            f"PlaceholderSignature({self._algorithm}).keygen() not implemented. "
            "Replace via PQC-25 (CRY-5) liboqs-Adapter."
        )
        raise NotImplementedError(msg)

    def sign(self, message: bytes, secret_key: bytes) -> bytes:
        del message, secret_key
        msg = (
            f"PlaceholderSignature({self._algorithm}).sign() not implemented. "
            "Replace via PQC-25 (CRY-5)."
        )
        raise NotImplementedError(msg)

    def verify(self, message: bytes, signature: bytes, public_key: bytes) -> bool:
        del message, signature, public_key
        msg = (
            f"PlaceholderSignature({self._algorithm}).verify() not implemented. "
            "Replace via PQC-25 (CRY-5)."
        )
        raise NotImplementedError(msg)


class CryptoConfigLike:
    """Minimale Strukturdefinition der Crypto-Config, die wir hier brauchen.

    In der Realitaet kommt das Objekt aus pydantic-settings (siehe config.py).
    Hier verwenden wir Duck-Typing, damit wir in Tests Mock-Configs einfach
    bauen koennen.
    """

    kem_supported: list[str]
    signature_supported: list[str]


def init_crypto_registry(
    registry: CryptoRegistry,
    *,
    kem_supported: list[str],
    signature_supported: list[str],
) -> None:
    """Befuelle ``registry`` mit Placeholder-Plugins fuer alle in der Config
    aufgelisteten Algorithmen.

    Args:
        registry: Eine frische ``CryptoRegistry``-Instanz.
        kem_supported: Liste der KEM-Namen aus ``config.crypto.kem.supported``.
        signature_supported: Liste der Signature-Namen aus
            ``config.crypto.signature.supported``.

    Raises:
        UnsupportedAlgorithmError: wenn ein Name in den Listen nicht in der
            internen Whitelist steht.

    Diese Function ist idempotent in dem Sinne, dass ein zweiter Aufruf mit
    derselben Registry zu ``DuplicateAlgorithmError`` fuehrt. Aufrufer
    instanziieren pro Service-Start eine neue Registry.
    """
    for alg in kem_supported:
        if alg not in _SUPPORTED_KEM_ALGORITHMS:
            msg = (
                f"Unsupported KEM algorithm '{alg}' in crypto.kem.supported. "
                f"Sprint-1-Whitelist: {sorted(_SUPPORTED_KEM_ALGORITHMS)}"
            )
            raise UnsupportedAlgorithmError(msg)
        registry.register_kem(alg, PlaceholderKem(alg))

    for alg in signature_supported:
        if alg not in _SUPPORTED_SIGNATURE_ALGORITHMS:
            msg = (
                f"Unsupported signature algorithm '{alg}' in crypto.signature.supported. "
                f"Sprint-1-Whitelist: {sorted(_SUPPORTED_SIGNATURE_ALGORITHMS)}"
            )
            raise UnsupportedAlgorithmError(msg)
        registry.register_signature(alg, PlaceholderSignature(alg))
