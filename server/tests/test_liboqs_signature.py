"""Tests fuer crypto/adapters/liboqs_signature.py und crypto/keys.py.

Story: PQC-25 (CRY-5), Acceptance Criteria AC-3, AC-4, AC-5.

Diese Tests benoetigen die ``oqs`` Python-Library. Wenn sie nicht verfuegbar
ist, werden die liboqs-spezifischen Tests via ``pytest.importorskip``
uebersprungen. Die ``crypto.keys``-Tests sind unabhaengig von liboqs und
laufen immer.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from crypto import keys

oqs = pytest.importorskip("oqs", reason="liboqs-python not installed in this environment")

from crypto.adapters.liboqs_signature import LibOqsSignature  # noqa: E402

# ---------------------------------------------------------------------------
# crypto/keys.py: File-Roundtrip
# ---------------------------------------------------------------------------


def test_save_and_load_secret_key_roundtrip(tmp_path: Path) -> None:
    key_path = tmp_path / "subdir" / "secret.bin"
    payload = b"\x01" * 64
    keys.save_secret_key(key_path, payload)
    assert keys.key_file_exists(key_path)
    loaded = keys.load_key(key_path)
    assert loaded == payload


def test_save_and_load_public_key_roundtrip(tmp_path: Path) -> None:
    key_path = tmp_path / "public.bin"
    payload = b"\x02" * 32
    keys.save_public_key(key_path, payload)
    assert keys.load_key(key_path) == payload


def test_load_key_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        keys.load_key(tmp_path / "does_not_exist.bin")


def test_load_key_empty_file_raises(tmp_path: Path) -> None:
    empty = tmp_path / "empty.bin"
    empty.write_bytes(b"")
    with pytest.raises(ValueError, match="empty"):
        keys.load_key(empty)


def test_key_file_exists_negative(tmp_path: Path) -> None:
    assert keys.key_file_exists(tmp_path / "absent.bin") is False


# ---------------------------------------------------------------------------
# LibOqsSignature: Algorithm-Whitelist
# ---------------------------------------------------------------------------


def test_liboqs_signature_rejects_unsupported_algorithm() -> None:
    with pytest.raises(ValueError, match="ML-DSA-65"):
        LibOqsSignature("Dilithium3")  # Pre-Standard-Name


def test_liboqs_signature_accepts_ml_dsa_65() -> None:
    plugin = LibOqsSignature("ML-DSA-65")
    assert plugin.algorithm == "ML-DSA-65"


# ---------------------------------------------------------------------------
# Round-Trip Tests (AC-3)
# ---------------------------------------------------------------------------


def test_liboqs_signature_round_trip_happy_path() -> None:
    plugin = LibOqsSignature("ML-DSA-65")
    message = b"hello post-quantum world"

    public_key, secret_key = plugin.keygen()
    assert isinstance(public_key, bytes)
    assert isinstance(secret_key, bytes)
    assert len(public_key) > 0
    assert len(secret_key) > 0

    signature = plugin.sign(message, secret_key)
    assert isinstance(signature, bytes)
    assert len(signature) > 0

    assert plugin.verify(message, signature, public_key) is True


def test_liboqs_signature_round_trip_with_long_message() -> None:
    plugin = LibOqsSignature("ML-DSA-65")
    message = b"x" * 10_000  # 10 KB Payload
    public_key, secret_key = plugin.keygen()
    signature = plugin.sign(message, secret_key)
    assert plugin.verify(message, signature, public_key) is True


# ---------------------------------------------------------------------------
# Tamper-Detection Tests (AC-4)
# ---------------------------------------------------------------------------


def test_liboqs_signature_rejects_tampered_message() -> None:
    plugin = LibOqsSignature("ML-DSA-65")
    public_key, secret_key = plugin.keygen()
    message = b"original message"
    signature = plugin.sign(message, secret_key)

    tampered = b"tampered message"
    assert plugin.verify(tampered, signature, public_key) is False


def test_liboqs_signature_rejects_tampered_signature() -> None:
    plugin = LibOqsSignature("ML-DSA-65")
    public_key, secret_key = plugin.keygen()
    message = b"original message"
    signature = plugin.sign(message, secret_key)

    # Flip last byte
    tampered_sig = signature[:-1] + bytes([signature[-1] ^ 0xFF])
    assert plugin.verify(message, tampered_sig, public_key) is False


def test_liboqs_signature_rejects_wrong_public_key() -> None:
    plugin = LibOqsSignature("ML-DSA-65")
    public_key_a, secret_key_a = plugin.keygen()
    public_key_b, _ = plugin.keygen()  # Anderes Keypair

    message = b"original message"
    signature = plugin.sign(message, secret_key_a)

    assert plugin.verify(message, signature, public_key_a) is True
    assert plugin.verify(message, signature, public_key_b) is False


# ---------------------------------------------------------------------------
# Key-Persistierung Tests (AC-5)
# ---------------------------------------------------------------------------


def test_liboqs_signature_keys_persist_through_file_roundtrip(tmp_path: Path) -> None:
    plugin = LibOqsSignature("ML-DSA-65")
    public_key, secret_key = plugin.keygen()

    pk_path = tmp_path / "keys" / "pub.bin"
    sk_path = tmp_path / "keys" / "sec.bin"
    keys.save_public_key(pk_path, public_key)
    keys.save_secret_key(sk_path, secret_key)

    loaded_pk = keys.load_key(pk_path)
    loaded_sk = keys.load_key(sk_path)

    message = b"test after disk roundtrip"
    signature = plugin.sign(message, loaded_sk)
    assert plugin.verify(message, signature, loaded_pk) is True


def test_ml_dsa_65_advertised_by_liboqs() -> None:
    """Sanity-Check: liboqs hat ML-DSA-65 als Signature-Mechanism aktiv."""
    assert "ML-DSA-65" in oqs.get_enabled_sig_mechanisms()
