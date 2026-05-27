"""Tests fuer crypto/facade.py.

Story: PQC-22 (CRY-2), Acceptance Criterion AC-4.

Tests benoetigen ``oqs`` Python-Library (LibOqsSignature). Ohne liboqs
werden alle Tests via ``pytest.importorskip`` uebersprungen.
"""

from __future__ import annotations

import pytest

from crypto.facade import CryptoFacade, CryptoFacadeError, UnknownKidError
from crypto.registry import AlgorithmNotFoundError, CryptoRegistry

oqs = pytest.importorskip("oqs", reason="liboqs-python not installed in this environment")

from crypto.adapters.liboqs_signature import LibOqsSignature  # noqa: E402


@pytest.fixture
def registry_with_ml_dsa_65() -> CryptoRegistry:
    """Registry mit einem echten LibOqsSignature-Adapter fuer ML-DSA-65."""
    registry = CryptoRegistry()
    registry.register_signature("ML-DSA-65", LibOqsSignature("ML-DSA-65"))
    return registry


@pytest.fixture
def facade_with_keypair(registry_with_ml_dsa_65: CryptoRegistry) -> CryptoFacade:
    """CryptoFacade mit echtem ML-DSA-65 Keypair, kid 'test-key-1'."""
    plugin = registry_with_ml_dsa_65.get_signature("ML-DSA-65")
    public_key, secret_key = plugin.keygen()
    return CryptoFacade(
        registry=registry_with_ml_dsa_65,
        default_signature_alg="ML-DSA-65",
        signing_kid="test-key-1",
        signing_secret_key=secret_key,
        verifying_keys_by_kid={"test-key-1": public_key},
    )


# ---------------------------------------------------------------------------
# Konstruktor-Validierung
# ---------------------------------------------------------------------------


def test_facade_init_rejects_signing_kid_not_in_verifying_keys(
    registry_with_ml_dsa_65: CryptoRegistry,
) -> None:
    """signing_kid muss in verifying_keys_by_kid sein, sonst koennte der Service
    seine eigenen Tokens nicht verifizieren."""
    plugin = registry_with_ml_dsa_65.get_signature("ML-DSA-65")
    public_key, secret_key = plugin.keygen()

    with pytest.raises(CryptoFacadeError, match="must be present"):
        CryptoFacade(
            registry=registry_with_ml_dsa_65,
            default_signature_alg="ML-DSA-65",
            signing_kid="missing-kid",
            signing_secret_key=secret_key,
            verifying_keys_by_kid={"other-kid": public_key},
        )


# ---------------------------------------------------------------------------
# AC-1: sign liefert (signature, alg, kid)
# ---------------------------------------------------------------------------


def test_facade_sign_returns_signature_alg_and_kid(facade_with_keypair: CryptoFacade) -> None:
    payload = b"hello broker token"
    signature, alg, kid = facade_with_keypair.sign(payload, purpose="broker-token")

    assert isinstance(signature, bytes)
    assert len(signature) > 0
    assert alg == "ML-DSA-65"
    assert kid == "test-key-1"


def test_facade_sign_signature_changes_with_payload(facade_with_keypair: CryptoFacade) -> None:
    """Sanity: zwei verschiedene Payloads liefern verschiedene Signaturen."""
    sig_a, _, _ = facade_with_keypair.sign(b"payload-a", purpose="test")
    sig_b, _, _ = facade_with_keypair.sign(b"payload-b", purpose="test")
    assert sig_a != sig_b


# ---------------------------------------------------------------------------
# AC-2: verify waehlt Algorithmus anhand alg-Parameter, kid anhand Lookup
# ---------------------------------------------------------------------------


def test_facade_round_trip_sign_verify(facade_with_keypair: CryptoFacade) -> None:
    """AC-4: Unit-Test sign/verify Round-Trip fuer ML-DSA-65."""
    payload = b"this is the broker token body"
    signature, alg, kid = facade_with_keypair.sign(payload, purpose="broker-token")
    assert facade_with_keypair.verify(payload, signature, alg, kid) is True


def test_facade_verify_rejects_tampered_payload(facade_with_keypair: CryptoFacade) -> None:
    signature, alg, kid = facade_with_keypair.sign(b"original", purpose="test")
    assert facade_with_keypair.verify(b"tampered", signature, alg, kid) is False


def test_facade_verify_rejects_unknown_kid(facade_with_keypair: CryptoFacade) -> None:
    signature, alg, _kid = facade_with_keypair.sign(b"payload", purpose="test")
    with pytest.raises(UnknownKidError, match="unknown-kid"):
        facade_with_keypair.verify(b"payload", signature, alg, "unknown-kid")


def test_facade_verify_rejects_unknown_alg(facade_with_keypair: CryptoFacade) -> None:
    signature, _alg, kid = facade_with_keypair.sign(b"payload", purpose="test")
    with pytest.raises(AlgorithmNotFoundError):
        facade_with_keypair.verify(b"payload", signature, "Dilithium3", kid)


def test_facade_verify_with_two_kids(registry_with_ml_dsa_65: CryptoRegistry) -> None:
    """Mehrere kids im Lookup: korrekter wird gefunden, falscher schlaegt fehl."""
    plugin = registry_with_ml_dsa_65.get_signature("ML-DSA-65")
    pk_a, sk_a = plugin.keygen()
    pk_b, _ = plugin.keygen()

    facade = CryptoFacade(
        registry=registry_with_ml_dsa_65,
        default_signature_alg="ML-DSA-65",
        signing_kid="key-a",
        signing_secret_key=sk_a,
        verifying_keys_by_kid={"key-a": pk_a, "key-b": pk_b},
    )

    sig, alg, kid = facade.sign(b"payload", purpose="test")
    assert kid == "key-a"
    # Korrekt mit key-a verifiziert
    assert facade.verify(b"payload", sig, alg, "key-a") is True
    # Mit key-b verifiziert: falscher Public Key, sollte False sein
    assert facade.verify(b"payload", sig, alg, "key-b") is False


# ---------------------------------------------------------------------------
# AC-3: KEM-Operationen explicit NICHT implementiert
# ---------------------------------------------------------------------------


def test_facade_kem_keygen_not_implemented(facade_with_keypair: CryptoFacade) -> None:
    with pytest.raises(NotImplementedError, match="PQC-23"):
        facade_with_keypair.kem_keygen()


def test_facade_kem_encaps_not_implemented(facade_with_keypair: CryptoFacade) -> None:
    with pytest.raises(NotImplementedError, match="PQC-23"):
        facade_with_keypair.kem_encaps(b"\x00" * 32, "ML-KEM-768")


def test_facade_kem_decaps_not_implemented(facade_with_keypair: CryptoFacade) -> None:
    with pytest.raises(NotImplementedError, match="PQC-23"):
        facade_with_keypair.kem_decaps(b"\x00", b"\x00", "ML-KEM-768")


# ---------------------------------------------------------------------------
# Diagnostik
# ---------------------------------------------------------------------------


def test_facade_supported_signature_algorithms(facade_with_keypair: CryptoFacade) -> None:
    assert facade_with_keypair.supported_signature_algorithms() == ["ML-DSA-65"]
