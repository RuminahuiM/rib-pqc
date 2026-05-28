"""Tests fuer auth/password.py (Argon2id-Hasher).

Story: PQC-28 (AUT-1) AC-5.

Tests verwenden reduzierte Argon2-Parameter (m=8MB, t=1, p=1) damit der
Test-Suite-Run schnell bleibt. Die Produktiv-Werte (m=64MB, t=3, p=4) sind
nur in einem dedizierten Slow-Test verifiziert.
"""

from __future__ import annotations

import pytest

from auth.password import PasswordHasher
from config import Argon2Config


@pytest.fixture
def fast_config() -> Argon2Config:
    """Reduzierte Params fuer schnelle Tests."""
    return Argon2Config(
        memory_cost_kb=8192,
        time_cost=1,
        parallelism=1,
        salt_length=16,
        hash_length=32,
    )


@pytest.fixture
def hasher(fast_config: Argon2Config) -> PasswordHasher:
    return PasswordHasher(fast_config)


# ---------------------------------------------------------------------------
# hash + verify Round-Trip (AC-5)
# ---------------------------------------------------------------------------


def test_hash_returns_argon2id_formatted_string(hasher: PasswordHasher) -> None:
    h = hasher.hash("correct horse battery staple")
    assert h.startswith("$argon2id$")
    assert "$v=19$" in h


def test_verify_correct_password(hasher: PasswordHasher) -> None:
    h = hasher.hash("my-secret-pw")
    assert hasher.verify("my-secret-pw", h) is True


def test_verify_wrong_password(hasher: PasswordHasher) -> None:
    h = hasher.hash("correct-pw")
    assert hasher.verify("wrong-pw", h) is False


def test_verify_empty_password(hasher: PasswordHasher) -> None:
    h = hasher.hash("any-pw")
    assert hasher.verify("", h) is False


def test_verify_empty_hash(hasher: PasswordHasher) -> None:
    assert hasher.verify("any-pw", "") is False


def test_verify_invalid_hash_string(hasher: PasswordHasher) -> None:
    assert hasher.verify("any-pw", "not-a-valid-argon2-hash") is False


def test_hash_same_password_yields_different_hashes(hasher: PasswordHasher) -> None:
    """Argon2id verwendet Random-Salt - identische Passwoerter haben verschiedene Hashes."""
    h1 = hasher.hash("identical")
    h2 = hasher.hash("identical")
    assert h1 != h2
    # Beide sollen aber das gleiche Passwort verifizieren
    assert hasher.verify("identical", h1) is True
    assert hasher.verify("identical", h2) is True


def test_hash_rejects_empty_password(hasher: PasswordHasher) -> None:
    with pytest.raises(ValueError, match="non-empty"):
        hasher.hash("")


# ---------------------------------------------------------------------------
# needs_rehash
# ---------------------------------------------------------------------------


def test_needs_rehash_fresh_hash_false(hasher: PasswordHasher) -> None:
    """Hash gerade mit aktuellen Params erstellt -> kein Rehash noetig."""
    h = hasher.hash("pw")
    assert hasher.needs_rehash(h) is False


def test_needs_rehash_invalid_hash_true(hasher: PasswordHasher) -> None:
    """Defekter Hash-String triggert needs_rehash=True."""
    assert hasher.needs_rehash("garbage") is True


def test_needs_rehash_old_params_true(fast_config: Argon2Config) -> None:
    """Hash mit alten Params -> Rehash empfohlen."""
    old_hasher = PasswordHasher(
        Argon2Config(memory_cost_kb=8192, time_cost=1, parallelism=1)
    )
    old_hash = old_hasher.hash("pw")
    # Neuer Hasher mit hoeheren Params
    new_hasher = PasswordHasher(
        Argon2Config(memory_cost_kb=16384, time_cost=2, parallelism=2)
    )
    assert new_hasher.needs_rehash(old_hash) is True


# ---------------------------------------------------------------------------
# Dummy-Verify (User-Enumeration-Schutz, AUT-4-Vorbereitung)
# ---------------------------------------------------------------------------


def test_dummy_verify_does_not_raise(hasher: PasswordHasher) -> None:
    """Dummy-verify schluckt VerifyMismatchError + InvalidHashError silently."""
    hasher.dummy_verify()  # darf nicht crashen


def test_dummy_verify_consumes_cpu_time(hasher: PasswordHasher) -> None:
    """Dummy-verify dauert messbar (>=1ms) - bestaetigt CPU-Burn."""
    import time

    t0 = time.time()
    hasher.dummy_verify()
    elapsed_ms = (time.time() - t0) * 1000
    # 1ms ist sehr konservativ. Realistisch ist 50ms-1000ms je nach Hardware.
    assert elapsed_ms >= 1.0
