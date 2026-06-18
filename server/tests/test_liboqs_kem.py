"""Tests fuer crypto/adapters/liboqs_kem.py.

Story: PQC-24 (CRY-4), Acceptance Criteria AC-1, AC-2, AC-3.

Diese Tests benoetigen die ``oqs`` Python-Library. Wenn sie nicht verfuegbar
ist, werden die liboqs-spezifischen Tests via ``pytest.importorskip``
uebersprungen.

**Test-Strategie fuer AC-3 (NIST-Test-Vektoren):**
liboqs selbst validiert beim Build gegen NIST-KATs (FIPS-203 Known-Answer-Tests).
Auf Adapter-Ebene fokussieren wir auf Roundtrip- und Property-Tests, die das
Adapter-Interface gegen das liboqs-Verhalten verifizieren. Externes KAT-Replay
waere redundant zur liboqs-internen Validation und wuerde grosse Test-Vektor-
Files erfordern.
"""

from __future__ import annotations

import pytest

from crypto.registry import CryptoRegistry, KemPlugin
from crypto.registry_init import (
    UnsupportedAlgorithmError,
    init_crypto_registry,
)

oqs = pytest.importorskip("oqs", reason="liboqs-python not installed in this environment")

from crypto.adapters.liboqs_kem import LibOqsKem  # noqa: E402

# ML-KEM Groessen laut FIPS 203 Table 2. Wir nutzen sie als Soll-Werte
# fuer die Adapter-Ausgaben.
_FIPS_203_SIZES: dict[str, dict[str, int]] = {
    "ML-KEM-768": {
        "public_key": 1184,
        "secret_key": 2400,
        "ciphertext": 1088,
        "shared_secret": 32,
    },
    "ML-KEM-1024": {
        "public_key": 1568,
        "secret_key": 3168,
        "ciphertext": 1568,
        "shared_secret": 32,
    },
}


# ---------------------------------------------------------------------------
# Algorithm-Whitelist (AC-2)
# ---------------------------------------------------------------------------


def test_liboqs_kem_rejects_unsupported_algorithm() -> None:
    with pytest.raises(ValueError, match="ML-KEM-768"):
        LibOqsKem("Kyber768")  # Pre-Standard-Name


def test_liboqs_kem_rejects_ml_kem_512() -> None:
    # CAT-1 ist absichtlich nicht enthalten (Tech-Stack legt CAT-3 als Min fest).
    with pytest.raises(ValueError, match="ML-KEM-768"):
        LibOqsKem("ML-KEM-512")


def test_liboqs_kem_accepts_ml_kem_768() -> None:
    plugin = LibOqsKem("ML-KEM-768")
    assert plugin.algorithm == "ML-KEM-768"


def test_liboqs_kem_accepts_ml_kem_1024() -> None:
    plugin = LibOqsKem("ML-KEM-1024")
    assert plugin.algorithm == "ML-KEM-1024"


# ---------------------------------------------------------------------------
# Keygen + Encaps + Decaps Round-Trip (AC-1, AC-3)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("algorithm", ["ML-KEM-768", "ML-KEM-1024"])
def test_liboqs_kem_roundtrip_happy_path(algorithm: str) -> None:
    """End-to-End: keygen -> encaps -> decaps liefert identische shared_secrets.

    Das ist der Kern-AC: ein erfolgreich encapsulated shared secret muss
    nach der Decapsulation mit dem zugehoerigen secret_key wieder
    rekonstruierbar sein.
    """
    plugin = LibOqsKem(algorithm)

    public_key, secret_key = plugin.keygen()
    ciphertext, shared_secret_a = plugin.encaps(public_key)
    shared_secret_b = plugin.decaps(ciphertext, secret_key)

    assert shared_secret_a == shared_secret_b
    assert len(shared_secret_a) == _FIPS_203_SIZES[algorithm]["shared_secret"]


# ---------------------------------------------------------------------------
# Output-Groessen gemaess FIPS 203 (AC-3)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("algorithm", ["ML-KEM-768", "ML-KEM-1024"])
def test_liboqs_kem_keygen_output_sizes(algorithm: str) -> None:
    plugin = LibOqsKem(algorithm)
    public_key, secret_key = plugin.keygen()
    sizes = _FIPS_203_SIZES[algorithm]

    assert len(public_key) == sizes["public_key"], (
        f"{algorithm} public_key length deviates from FIPS 203 Table 2"
    )
    assert len(secret_key) == sizes["secret_key"], (
        f"{algorithm} secret_key length deviates from FIPS 203 Table 2"
    )


@pytest.mark.parametrize("algorithm", ["ML-KEM-768", "ML-KEM-1024"])
def test_liboqs_kem_encaps_output_sizes(algorithm: str) -> None:
    plugin = LibOqsKem(algorithm)
    public_key, _ = plugin.keygen()
    ciphertext, shared_secret = plugin.encaps(public_key)
    sizes = _FIPS_203_SIZES[algorithm]

    assert len(ciphertext) == sizes["ciphertext"], (
        f"{algorithm} ciphertext length deviates from FIPS 203 Table 2"
    )
    assert len(shared_secret) == sizes["shared_secret"], (
        f"{algorithm} shared_secret length deviates from FIPS 203 Table 2"
    )


# ---------------------------------------------------------------------------
# Fresh-Randomness Properties
# ---------------------------------------------------------------------------


def test_liboqs_kem_keygen_returns_fresh_keys() -> None:
    """Zwei keygen-Aufrufe liefern unterschiedliche Keys (Randomness sanity check)."""
    plugin = LibOqsKem("ML-KEM-768")
    pk1, sk1 = plugin.keygen()
    pk2, sk2 = plugin.keygen()
    assert pk1 != pk2
    assert sk1 != sk2


def test_liboqs_kem_encaps_returns_fresh_ciphertext() -> None:
    """Zwei encaps gegen denselben pk liefern unterschiedliche (ct, ss)-Paare.

    ML-KEM encapsulation ist randomisiert (frische Zufallsbytes intern). Aus
    Sicht des Aufrufers heisst das: zwei encaps gegen den gleichen pk liefern
    immer unterschiedliche ciphertexts und shared_secrets.
    """
    plugin = LibOqsKem("ML-KEM-768")
    pk, _ = plugin.keygen()
    ct1, ss1 = plugin.encaps(pk)
    ct2, ss2 = plugin.encaps(pk)
    assert ct1 != ct2
    assert ss1 != ss2


# ---------------------------------------------------------------------------
# Implicit Rejection (FIPS 203 spec)
# ---------------------------------------------------------------------------


def test_liboqs_kem_decaps_wrong_secret_key_implicit_rejection() -> None:
    """FIPS-203-konformes implicit rejection: ein wrong secret_key liefert
    einen deterministischen Pseudo-shared-secret, KEINEN Error.

    Das ist by-design (Algorithm 18 Step 9 in FIPS 203). Authentifizierung
    muss auf Application-Layer (AEAD-Tag) erfolgen, nicht ueber den KEM
    selbst. Der Test stellt sicher dass unser Adapter diese Spec respektiert
    und nicht versucht, einen Fehler zu werfen.
    """
    plugin = LibOqsKem("ML-KEM-768")
    pk_alice, _ = plugin.keygen()
    _, sk_bob = plugin.keygen()  # andere Identitaet, gleicher Algorithmus

    ciphertext, ss_alice = plugin.encaps(pk_alice)
    ss_bob_decaps = plugin.decaps(ciphertext, sk_bob)  # FALSCHER sk

    # Implicit rejection: kein Fehler, aber Output != original shared_secret.
    assert ss_bob_decaps != ss_alice
    assert len(ss_bob_decaps) == 32


# ---------------------------------------------------------------------------
# Protocol-Konformitaet (CRY-1)
# ---------------------------------------------------------------------------


def test_liboqs_kem_is_kemplugin_via_runtime_protocol() -> None:
    """LibOqsKem implementiert das KemPlugin-Protocol strukturell.

    runtime_checkable Protocol erlaubt isinstance ohne explicit Inheritance.
    """
    plugin = LibOqsKem("ML-KEM-768")
    assert isinstance(plugin, KemPlugin)


# ---------------------------------------------------------------------------
# Registry-Integration (AC-2: "registrierbar")
# ---------------------------------------------------------------------------


def test_init_crypto_registry_registers_both_kems() -> None:
    """init_crypto_registry registriert ML-KEM-768 und ML-KEM-1024 als
    LibOqsKem-Plugins (nicht mehr Placeholder seit PQC-24)."""
    registry = CryptoRegistry()
    init_crypto_registry(
        registry,
        kem_supported=["ML-KEM-768", "ML-KEM-1024"],
        signature_supported=["ML-DSA-65"],
    )
    assert registry.supported_kem() == ["ML-KEM-1024", "ML-KEM-768"]

    plugin_768 = registry.get_kem("ML-KEM-768")
    plugin_1024 = registry.get_kem("ML-KEM-1024")
    assert isinstance(plugin_768, LibOqsKem)
    assert isinstance(plugin_1024, LibOqsKem)
    assert plugin_768.algorithm == "ML-KEM-768"
    assert plugin_1024.algorithm == "ML-KEM-1024"


def test_init_crypto_registry_rejects_unknown_kem() -> None:
    registry = CryptoRegistry()
    with pytest.raises(UnsupportedAlgorithmError, match="ML-KEM-768"):
        init_crypto_registry(
            registry,
            kem_supported=["Kyber768"],
            signature_supported=["ML-DSA-65"],
        )


def test_registered_kem_can_perform_full_roundtrip() -> None:
    """End-to-End ueber die Registry-API: ein via init_crypto_registry
    registrierter Plugin liefert das gleiche Verhalten wie ein direkt
    konstruierter."""
    registry = CryptoRegistry()
    init_crypto_registry(
        registry,
        kem_supported=["ML-KEM-768"],
        signature_supported=["ML-DSA-65"],
    )
    plugin = registry.get_kem("ML-KEM-768")

    pk, sk = plugin.keygen()
    ct, ss_a = plugin.encaps(pk)
    ss_b = plugin.decaps(ct, sk)
    assert ss_a == ss_b
