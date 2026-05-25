"""Unit-Tests fuer crypto/registry.py und crypto/registry_init.py.

Story: PQC-21 (CRY-1), Acceptance Criterion AC-5.

Deckt ab:
- Happy-Path: register plus get fuer KEM und Signature
- Duplikat-Erkennung wirft DuplicateAlgorithmError
- Get-mit-unbekanntem-Namen wirft AlgorithmNotFoundError
- ``init_crypto_registry`` registriert die in der Config genannten Algorithmen
- Unbekannter Algorithmus in der Config wirft UnsupportedAlgorithmError

Kein liboqs-Import, alle Tests laufen ohne Container.
"""

from __future__ import annotations

import pytest

from crypto.registry import (
    AlgorithmNotFoundError,
    CryptoRegistry,
    DuplicateAlgorithmError,
    KemPlugin,
    SignaturePlugin,
)
from crypto.registry_init import (
    PlaceholderKem,
    PlaceholderSignature,
    UnsupportedAlgorithmError,
    init_crypto_registry,
)

# ---------------------------------------------------------------------------
# CryptoRegistry: Happy-Path
# ---------------------------------------------------------------------------


def test_register_and_get_kem_happy_path() -> None:
    registry = CryptoRegistry()
    plugin = PlaceholderKem("ML-KEM-768")

    registry.register_kem("ML-KEM-768", plugin)

    assert registry.get_kem("ML-KEM-768") is plugin
    assert registry.supported_kem() == ["ML-KEM-768"]


def test_register_and_get_signature_happy_path() -> None:
    registry = CryptoRegistry()
    plugin = PlaceholderSignature("ML-DSA-65")

    registry.register_signature("ML-DSA-65", plugin)

    assert registry.get_signature("ML-DSA-65") is plugin
    assert registry.supported_signature() == ["ML-DSA-65"]


def test_supported_kem_sorted() -> None:
    registry = CryptoRegistry()
    registry.register_kem("ML-KEM-1024", PlaceholderKem("ML-KEM-1024"))
    registry.register_kem("ML-KEM-768", PlaceholderKem("ML-KEM-768"))

    assert registry.supported_kem() == ["ML-KEM-1024", "ML-KEM-768"]


# ---------------------------------------------------------------------------
# CryptoRegistry: Fehlerfaelle (AC-2, AC-3)
# ---------------------------------------------------------------------------


def test_register_kem_duplicate_raises() -> None:
    registry = CryptoRegistry()
    registry.register_kem("ML-KEM-768", PlaceholderKem("ML-KEM-768"))

    with pytest.raises(DuplicateAlgorithmError) as exc:
        registry.register_kem("ML-KEM-768", PlaceholderKem("ML-KEM-768"))
    assert "ML-KEM-768" in str(exc.value)


def test_register_signature_duplicate_raises() -> None:
    registry = CryptoRegistry()
    registry.register_signature("ML-DSA-65", PlaceholderSignature("ML-DSA-65"))

    with pytest.raises(DuplicateAlgorithmError) as exc:
        registry.register_signature("ML-DSA-65", PlaceholderSignature("ML-DSA-65"))
    assert "ML-DSA-65" in str(exc.value)


def test_get_kem_unknown_raises() -> None:
    registry = CryptoRegistry()
    with pytest.raises(AlgorithmNotFoundError) as exc:
        registry.get_kem("ML-KEM-768")
    assert "ML-KEM-768" in str(exc.value)


def test_get_signature_unknown_raises() -> None:
    registry = CryptoRegistry()
    with pytest.raises(AlgorithmNotFoundError) as exc:
        registry.get_signature("ML-DSA-65")
    assert "ML-DSA-65" in str(exc.value)


# ---------------------------------------------------------------------------
# Protocol-Konformitaet: Placeholder-Plugins erfuellen die Protocols
# ---------------------------------------------------------------------------


def test_placeholder_kem_satisfies_kem_protocol() -> None:
    plugin = PlaceholderKem("ML-KEM-768")
    assert isinstance(plugin, KemPlugin)
    assert plugin.algorithm == "ML-KEM-768"


def test_placeholder_signature_satisfies_signature_protocol() -> None:
    plugin = PlaceholderSignature("ML-DSA-65")
    assert isinstance(plugin, SignaturePlugin)
    assert plugin.algorithm == "ML-DSA-65"


def test_placeholder_kem_methods_raise_not_implemented() -> None:
    """Sicherheitsnetz: Placeholder darf NIE eine echte Crypto-Operation ausfuehren."""
    plugin = PlaceholderKem("ML-KEM-768")
    with pytest.raises(NotImplementedError):
        plugin.keygen()
    with pytest.raises(NotImplementedError):
        plugin.encaps(b"\x00" * 32)
    with pytest.raises(NotImplementedError):
        plugin.decaps(b"\x00", b"\x00")


def test_placeholder_signature_methods_raise_not_implemented() -> None:
    plugin = PlaceholderSignature("ML-DSA-65")
    with pytest.raises(NotImplementedError):
        plugin.keygen()
    with pytest.raises(NotImplementedError):
        plugin.sign(b"msg", b"sk")
    with pytest.raises(NotImplementedError):
        plugin.verify(b"msg", b"sig", b"pk")


# ---------------------------------------------------------------------------
# init_crypto_registry (AC-4)
# ---------------------------------------------------------------------------


def test_init_crypto_registry_registers_configured_algorithms() -> None:
    registry = CryptoRegistry()
    init_crypto_registry(
        registry,
        kem_supported=["ML-KEM-768"],
        signature_supported=["ML-DSA-65"],
    )

    assert registry.supported_kem() == ["ML-KEM-768"]
    assert registry.supported_signature() == ["ML-DSA-65"]
    # Plugin-Existenz pruefen
    assert isinstance(registry.get_kem("ML-KEM-768"), KemPlugin)
    assert isinstance(registry.get_signature("ML-DSA-65"), SignaturePlugin)


def test_init_crypto_registry_supports_multiple_algorithms() -> None:
    registry = CryptoRegistry()
    init_crypto_registry(
        registry,
        kem_supported=["ML-KEM-768", "ML-KEM-1024"],
        signature_supported=["ML-DSA-65"],
    )

    assert registry.supported_kem() == ["ML-KEM-1024", "ML-KEM-768"]


def test_init_crypto_registry_rejects_unknown_kem() -> None:
    registry = CryptoRegistry()
    with pytest.raises(UnsupportedAlgorithmError) as exc:
        init_crypto_registry(
            registry,
            kem_supported=["Kyber768"],  # Pre-Standard-Name, nicht NIST
            signature_supported=[],
        )
    assert "Kyber768" in str(exc.value)


def test_init_crypto_registry_rejects_unknown_signature() -> None:
    registry = CryptoRegistry()
    with pytest.raises(UnsupportedAlgorithmError) as exc:
        init_crypto_registry(
            registry,
            kem_supported=[],
            signature_supported=["Dilithium3"],  # Pre-Standard-Name
        )
    assert "Dilithium3" in str(exc.value)


def test_init_crypto_registry_idempotency_check_via_duplicate() -> None:
    """Zweiter Aufruf mit derselben Registry und gleichen Inputs muss scheitern.

    Das ist Absicht: Init wird genau einmal pro Service-Start gemacht. Mehrfach-
    Aufruf signalisiert einen Bug im Aufrufer-Code.
    """
    registry = CryptoRegistry()
    init_crypto_registry(
        registry,
        kem_supported=["ML-KEM-768"],
        signature_supported=["ML-DSA-65"],
    )
    with pytest.raises(DuplicateAlgorithmError):
        init_crypto_registry(
            registry,
            kem_supported=["ML-KEM-768"],
            signature_supported=["ML-DSA-65"],
        )
