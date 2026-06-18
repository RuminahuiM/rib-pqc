"""Tests fuer crypto/facade.py.

Stories:
- PQC-22 (CRY-2), Acceptance Criterion AC-4: sign/verify.
- PQC-23 (CRY-3): KEM-Methoden + HKDF + AEAD + Negotiation-Support.

Tests benoetigen ``oqs`` Python-Library. Ohne liboqs werden alle Tests via
``pytest.importorskip`` uebersprungen.
"""

from __future__ import annotations

import os

import pytest

from crypto.facade import (
    AeadDecryptError,
    CryptoFacade,
    CryptoFacadeError,
    UnknownKidError,
)
from crypto.registry import AlgorithmNotFoundError, CryptoRegistry

oqs = pytest.importorskip("oqs", reason="liboqs-python not installed in this environment")

from crypto.adapters.liboqs_kem import LibOqsKem  # noqa: E402
from crypto.adapters.liboqs_signature import LibOqsSignature  # noqa: E402


@pytest.fixture
def registry_with_ml_dsa_65() -> CryptoRegistry:
    """Registry mit einem echten LibOqsSignature-Adapter fuer ML-DSA-65."""
    registry = CryptoRegistry()
    registry.register_signature("ML-DSA-65", LibOqsSignature("ML-DSA-65"))
    return registry


@pytest.fixture
def registry_with_signature_and_kems() -> CryptoRegistry:
    """Registry mit Signature plus beiden KEM-Algorithmen (fuer PQC-23 Tests)."""
    registry = CryptoRegistry()
    registry.register_signature("ML-DSA-65", LibOqsSignature("ML-DSA-65"))
    registry.register_kem("ML-KEM-768", LibOqsKem("ML-KEM-768"))
    registry.register_kem("ML-KEM-1024", LibOqsKem("ML-KEM-1024"))
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


@pytest.fixture
def facade_with_kems(registry_with_signature_and_kems: CryptoRegistry) -> CryptoFacade:
    """CryptoFacade mit Signature plus ML-KEM-768 und ML-KEM-1024 (PQC-23)."""
    sig_plugin = registry_with_signature_and_kems.get_signature("ML-DSA-65")
    public_key, secret_key = sig_plugin.keygen()
    return CryptoFacade(
        registry=registry_with_signature_and_kems,
        default_signature_alg="ML-DSA-65",
        signing_kid="test-key-1",
        signing_secret_key=secret_key,
        verifying_keys_by_kid={"test-key-1": public_key},
    )


# --- Konstruktor + Sign/Verify (PQC-22 CRY-2) ----------------------------------


def test_facade_init_rejects_signing_kid_not_in_verifying_keys(
    registry_with_ml_dsa_65: CryptoRegistry,
) -> None:
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


def test_facade_sign_returns_signature_alg_and_kid(facade_with_keypair: CryptoFacade) -> None:
    signature, alg, kid = facade_with_keypair.sign(b"hello broker token", purpose="broker-token")
    assert isinstance(signature, bytes)
    assert len(signature) > 0
    assert alg == "ML-DSA-65"
    assert kid == "test-key-1"


def test_facade_sign_signature_changes_with_payload(facade_with_keypair: CryptoFacade) -> None:
    sig_a, _, _ = facade_with_keypair.sign(b"payload-a", purpose="test")
    sig_b, _, _ = facade_with_keypair.sign(b"payload-b", purpose="test")
    assert sig_a != sig_b


def test_facade_round_trip_sign_verify(facade_with_keypair: CryptoFacade) -> None:
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
    assert facade.verify(b"payload", sig, alg, "key-a") is True
    assert facade.verify(b"payload", sig, alg, "key-b") is False


# --- PQC-23 CRY-3: KEM ---------------------------------------------------------


@pytest.mark.parametrize("alg", ["ML-KEM-768", "ML-KEM-1024"])
def test_facade_kem_roundtrip(facade_with_kems: CryptoFacade, alg: str) -> None:
    pk, sk = facade_with_kems.kem_keygen(alg)
    ct, ss_a = facade_with_kems.kem_encaps(pk, alg)
    ss_b = facade_with_kems.kem_decaps(ct, sk, alg)
    assert ss_a == ss_b
    assert len(ss_a) == 32


def test_facade_kem_keygen_rejects_unknown_alg(facade_with_kems: CryptoFacade) -> None:
    with pytest.raises(AlgorithmNotFoundError):
        facade_with_kems.kem_keygen("Kyber768")


def test_facade_kem_encaps_rejects_unknown_alg(facade_with_kems: CryptoFacade) -> None:
    with pytest.raises(AlgorithmNotFoundError):
        facade_with_kems.kem_encaps(b"\x00" * 1184, "Kyber768")


def test_facade_kem_decaps_implicit_rejection(facade_with_kems: CryptoFacade) -> None:
    """FIPS-203: kem_decaps mit falschem sk wirft KEINEN Error,
    liefert Pseudo-shared-secret. Authentifizierung muss auf AEAD-Layer."""
    pk_alice, _ = facade_with_kems.kem_keygen("ML-KEM-768")
    _, sk_bob = facade_with_kems.kem_keygen("ML-KEM-768")
    ct, ss_alice = facade_with_kems.kem_encaps(pk_alice, "ML-KEM-768")
    ss_bob = facade_with_kems.kem_decaps(ct, sk_bob, "ML-KEM-768")
    assert ss_bob != ss_alice
    assert len(ss_bob) == 32


# --- PQC-23 CRY-3: HKDF --------------------------------------------------------


def test_facade_hkdf_deterministic_for_same_inputs(facade_with_kems: CryptoFacade) -> None:
    ikm = b"\x42" * 32
    info = b"app-session-v1"
    salt = b"session-id-abc"
    assert facade_with_kems.hkdf(ikm, info, salt) == facade_with_kems.hkdf(ikm, info, salt)


def test_facade_hkdf_default_length_32(facade_with_kems: CryptoFacade) -> None:
    key = facade_with_kems.hkdf(b"\x42" * 32, b"info", b"salt")
    assert len(key) == 32


def test_facade_hkdf_custom_length(facade_with_kems: CryptoFacade) -> None:
    key64 = facade_with_kems.hkdf(b"\x42" * 32, b"info", b"salt", length=64)
    assert len(key64) == 64


def test_facade_hkdf_different_info_different_output(facade_with_kems: CryptoFacade) -> None:
    ikm = b"\x42" * 32
    salt = b"same-salt"
    key_a = facade_with_kems.hkdf(ikm, b"info-A", salt)
    key_b = facade_with_kems.hkdf(ikm, b"info-B", salt)
    assert key_a != key_b


def test_facade_hkdf_different_salt_different_output(facade_with_kems: CryptoFacade) -> None:
    ikm = b"\x42" * 32
    info = b"same-info"
    key_a = facade_with_kems.hkdf(ikm, info, b"salt-A")
    key_b = facade_with_kems.hkdf(ikm, info, b"salt-B")
    assert key_a != key_b


# --- PQC-23 CRY-3: AEAD --------------------------------------------------------


def _fresh_aead_inputs() -> tuple[bytes, bytes, bytes]:
    return os.urandom(32), os.urandom(12), b"hello session payload"


def test_facade_aead_roundtrip(facade_with_kems: CryptoFacade) -> None:
    key, nonce, plaintext = _fresh_aead_inputs()
    blob = facade_with_kems.aead_encrypt(key, nonce, plaintext)
    assert facade_with_kems.aead_decrypt(key, nonce, blob) == plaintext


def test_facade_aead_blob_includes_tag(facade_with_kems: CryptoFacade) -> None:
    key, nonce, plaintext = _fresh_aead_inputs()
    blob = facade_with_kems.aead_encrypt(key, nonce, plaintext)
    assert len(blob) == len(plaintext) + 16


def test_facade_aead_with_aad_roundtrip(facade_with_kems: CryptoFacade) -> None:
    key, nonce, plaintext = _fresh_aead_inputs()
    aad = b"session-id=abc&route=/api/profile"
    blob = facade_with_kems.aead_encrypt(key, nonce, plaintext, aad=aad)
    assert facade_with_kems.aead_decrypt(key, nonce, blob, aad=aad) == plaintext


def test_facade_aead_decrypt_tampered_ciphertext_raises(facade_with_kems: CryptoFacade) -> None:
    key, nonce, plaintext = _fresh_aead_inputs()
    blob = facade_with_kems.aead_encrypt(key, nonce, plaintext)
    tampered = bytearray(blob)
    tampered[0] ^= 0x01
    with pytest.raises(AeadDecryptError):
        facade_with_kems.aead_decrypt(key, nonce, bytes(tampered))


def test_facade_aead_decrypt_tampered_tag_raises(facade_with_kems: CryptoFacade) -> None:
    key, nonce, plaintext = _fresh_aead_inputs()
    blob = facade_with_kems.aead_encrypt(key, nonce, plaintext)
    tampered = bytearray(blob)
    tampered[-1] ^= 0x01
    with pytest.raises(AeadDecryptError):
        facade_with_kems.aead_decrypt(key, nonce, bytes(tampered))


def test_facade_aead_decrypt_wrong_key_raises(facade_with_kems: CryptoFacade) -> None:
    key, nonce, plaintext = _fresh_aead_inputs()
    blob = facade_with_kems.aead_encrypt(key, nonce, plaintext)
    with pytest.raises(AeadDecryptError):
        facade_with_kems.aead_decrypt(os.urandom(32), nonce, blob)


def test_facade_aead_decrypt_wrong_nonce_raises(facade_with_kems: CryptoFacade) -> None:
    key, nonce, plaintext = _fresh_aead_inputs()
    blob = facade_with_kems.aead_encrypt(key, nonce, plaintext)
    with pytest.raises(AeadDecryptError):
        facade_with_kems.aead_decrypt(key, os.urandom(12), blob)


def test_facade_aead_decrypt_wrong_aad_raises(facade_with_kems: CryptoFacade) -> None:
    key, nonce, plaintext = _fresh_aead_inputs()
    blob = facade_with_kems.aead_encrypt(key, nonce, plaintext, aad=b"AAD-A")
    with pytest.raises(AeadDecryptError):
        facade_with_kems.aead_decrypt(key, nonce, blob, aad=b"AAD-B")


# --- PQC-23 CRY-3: Diagnostik + Negotiation ------------------------------------


def test_facade_supported_signature_algorithms(facade_with_keypair: CryptoFacade) -> None:
    assert facade_with_keypair.supported_signature_algorithms() == ["ML-DSA-65"]


def test_facade_supported_kem_algorithms(facade_with_kems: CryptoFacade) -> None:
    assert facade_with_kems.supported_kem_algorithms() == ["ML-KEM-1024", "ML-KEM-768"]


def test_facade_is_kem_supported_positive(facade_with_kems: CryptoFacade) -> None:
    assert facade_with_kems.is_kem_supported("ML-KEM-768") is True
    assert facade_with_kems.is_kem_supported("ML-KEM-1024") is True


def test_facade_is_kem_supported_negative(facade_with_kems: CryptoFacade) -> None:
    assert facade_with_kems.is_kem_supported("Kyber768") is False
    assert facade_with_kems.is_kem_supported("ML-KEM-512") is False


# --- Integration: KEM -> HKDF -> AEAD-Pipeline (Sprint-3-Konsumenten) -----------


def test_facade_kem_hkdf_aead_full_pipeline(facade_with_kems: CryptoFacade) -> None:
    """End-to-End Sprint-3-Pipeline: ML-KEM-Encap, HKDF-Session-Key-Ableitung,
    AEAD-Encrypt-Decrypt. Konzeptueller SES-1 + SES-2 + DCH-1 Datenfluss."""
    pk, sk = facade_with_kems.kem_keygen("ML-KEM-768")
    ct, ss_sender = facade_with_kems.kem_encaps(pk, "ML-KEM-768")
    ss_receiver = facade_with_kems.kem_decaps(ct, sk, "ML-KEM-768")
    assert ss_sender == ss_receiver

    session_id = b"sess_" + os.urandom(8)
    session_key_sender = facade_with_kems.hkdf(ss_sender, info=b"app-session-v1", salt=session_id)
    session_key_receiver = facade_with_kems.hkdf(
        ss_receiver, info=b"app-session-v1", salt=session_id
    )
    assert session_key_sender == session_key_receiver
    assert len(session_key_sender) == 32

    nonce = os.urandom(12)
    plaintext = b'{"user_id": "demo", "scope": "profile"}'
    blob = facade_with_kems.aead_encrypt(session_key_sender, nonce, plaintext, aad=session_id)
    restored = facade_with_kems.aead_decrypt(session_key_receiver, nonce, blob, aad=session_id)
    assert restored == plaintext
