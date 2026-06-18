"""Tests fuer services/session_key_derivation.py.

Story: PQC-47 SES-2.

Pruefen:
- AC-1 Server-Ableitung: HKDF(shared_secret, info=hkdf_info, salt=session_id).
- AC-3 Determinismus: gleiche Inputs liefern byte-identischen Output.
- 32 Byte Output.
- Domain-Separation: andere info/salt -> anderer Output.
- App-Side-Cross-Check (AC-2/AC-3) muss in PQC-26 CRY-6 ueber App-Side mit
  identischen Inputs verifiziert werden. Hier dokumentiert via Test-Vektor.

Diese Tests benoetigen die ``cryptography``-Library (kein liboqs noetig).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from services.session_key_derivation import (
    SESSION_KEY_LENGTH_BYTES,
    derive_session_key,
)

if TYPE_CHECKING:
    from crypto.facade import CryptoFacade

# Test-Vektoren: bewusst deterministisch fuer Cross-Implementation-Check
# (AC-3). Wenn die App-Seite (PQC-26 CRY-6) das gleiche reproduziert,
# pruefen wir Identitaet ueber Sprachen-Grenzen.
_TEST_SHARED_SECRET = bytes(range(32))  # 0x00..0x1F deterministisch
_TEST_SESSION_ID = "test-session-id-22ch"  # 20 chars
_TEST_HKDF_INFO = b"app-session-v1"


@pytest.fixture
def facade() -> CryptoFacade:
    """Minimale CryptoFacade nur fuer den HKDF-Pfad. KEM/Signature werden
    nicht aufgerufen, also brauchen wir kein liboqs."""
    from crypto.registry import CryptoRegistry
    from crypto.registry_init import PlaceholderSignature

    registry = CryptoRegistry()
    # Nur Signature wird in CryptoFacade-Konstruktor benoetigt (signing_kid-Validation).
    placeholder_sig = PlaceholderSignature("ML-DSA-65")
    registry.register_signature("ML-DSA-65", placeholder_sig)

    from crypto.facade import CryptoFacade

    return CryptoFacade(
        registry=registry,
        default_signature_alg="ML-DSA-65",
        signing_kid="test-kid",
        signing_secret_key=b"\x00" * 32,
        verifying_keys_by_kid={"test-kid": b"\x00" * 32},
    )


def test_derive_session_key_returns_32_bytes(facade: CryptoFacade) -> None:
    """AC-3 Teil: Output ist exakt 32 Byte (AES-256-GCM-Key)."""
    key = derive_session_key(
        facade,
        shared_secret=_TEST_SHARED_SECRET,
        session_id=_TEST_SESSION_ID,
        hkdf_info=_TEST_HKDF_INFO,
    )
    assert isinstance(key, bytes)
    assert len(key) == SESSION_KEY_LENGTH_BYTES == 32


def test_derive_session_key_is_deterministic(facade: CryptoFacade) -> None:
    """RFC 5869 HKDF ist deterministisch fuer feste Inputs.

    AC-3-Grundlage: wenn Server und App identische Inputs verwenden, kommen
    auch identische Outputs raus."""
    key_a = derive_session_key(
        facade,
        shared_secret=_TEST_SHARED_SECRET,
        session_id=_TEST_SESSION_ID,
        hkdf_info=_TEST_HKDF_INFO,
    )
    key_b = derive_session_key(
        facade,
        shared_secret=_TEST_SHARED_SECRET,
        session_id=_TEST_SESSION_ID,
        hkdf_info=_TEST_HKDF_INFO,
    )
    assert key_a == key_b


def test_derive_session_key_changes_with_session_id(facade: CryptoFacade) -> None:
    """Domain-Separation per Salt: andere session_id -> anderer Key."""
    key_a = derive_session_key(
        facade,
        shared_secret=_TEST_SHARED_SECRET,
        session_id="session-A",
        hkdf_info=_TEST_HKDF_INFO,
    )
    key_b = derive_session_key(
        facade,
        shared_secret=_TEST_SHARED_SECRET,
        session_id="session-B",
        hkdf_info=_TEST_HKDF_INFO,
    )
    assert key_a != key_b


def test_derive_session_key_changes_with_hkdf_info(facade: CryptoFacade) -> None:
    """Domain-Separation per Info: andere Protokoll-Version -> anderer Key.

    Beispiel: v1 vs v2 koennen denselben shared_secret + session_id haben,
    aber unterschiedliche keys via Info-Inkrement."""
    key_v1 = derive_session_key(
        facade,
        shared_secret=_TEST_SHARED_SECRET,
        session_id=_TEST_SESSION_ID,
        hkdf_info=b"app-session-v1",
    )
    key_v2 = derive_session_key(
        facade,
        shared_secret=_TEST_SHARED_SECRET,
        session_id=_TEST_SESSION_ID,
        hkdf_info=b"app-session-v2",
    )
    assert key_v1 != key_v2


def test_derive_session_key_changes_with_shared_secret(facade: CryptoFacade) -> None:
    """Anderer KEM-shared_secret -> anderer Key. Trivial aber wichtig."""
    key_a = derive_session_key(
        facade,
        shared_secret=bytes(range(32)),
        session_id=_TEST_SESSION_ID,
        hkdf_info=_TEST_HKDF_INFO,
    )
    key_b = derive_session_key(
        facade,
        shared_secret=bytes(range(31, -1, -1)),  # umgekehrt
        session_id=_TEST_SESSION_ID,
        hkdf_info=_TEST_HKDF_INFO,
    )
    assert key_a != key_b


def test_derive_session_key_uses_ascii_session_id_as_salt(facade: CryptoFacade) -> None:
    """Verifikation der Salt-Konvention: session_id.encode('ascii') wird
    als HKDF-Salt verwendet. Wir pruefen indirekt: zwei session_ids mit
    nur 1-byte-Unterschied im string ergeben unterschiedliche Keys."""
    key_a = derive_session_key(
        facade,
        shared_secret=_TEST_SHARED_SECRET,
        session_id="sess-AAA",
        hkdf_info=_TEST_HKDF_INFO,
    )
    key_b = derive_session_key(
        facade,
        shared_secret=_TEST_SHARED_SECRET,
        session_id="sess-AAB",
        hkdf_info=_TEST_HKDF_INFO,
    )
    assert key_a != key_b


def test_derive_session_key_matches_direct_facade_hkdf(facade: CryptoFacade) -> None:
    """Sanity: derive_session_key ist ein echter Pass-Through auf facade.hkdf.

    Falls SES-1 in einer zukuenftigen Story facade.hkdf direkt aufruft,
    muessen die Ergebnisse identisch sein."""
    indirect = derive_session_key(
        facade,
        shared_secret=_TEST_SHARED_SECRET,
        session_id=_TEST_SESSION_ID,
        hkdf_info=_TEST_HKDF_INFO,
    )
    direct = facade.hkdf(
        ikm=_TEST_SHARED_SECRET,
        info=_TEST_HKDF_INFO,
        salt=_TEST_SESSION_ID.encode("ascii"),
        length=32,
    )
    assert indirect == direct
