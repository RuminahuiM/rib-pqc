"""HKDF-Session-Key-Ableitung fuer PQ-Sessions.

Story: PQC-47 (SES-2).
Bezug: FR-Session-2, docs/wire_format.md Sektion 4, docs/07_design.md
Sektion 5.2.

**Konvention (Server- und App-Seite muessen identisch implementieren):**

- Algorithmus: HKDF-SHA256 (RFC 5869), 32-Byte-Output (passt zu AES-256-GCM-Key).
- Input Keying Material (IKM): das von ML-KEM-Encaps/Decaps erzeugte
  shared_secret (32 Byte gemaess FIPS 203).
- Info-Bytes (Domain-Separation): aus ``settings.session.hkdf_info``,
  Default ``b"app-session-v1"``. Bei Protokoll-Version-Wechsel auf v2
  inkrementieren (z.B. ``b"app-session-v2"``).
- Salt: die ``session_id`` als **ASCII-bytes des urlsafe-base64-Strings**
  wie sie vom Server in der SES-1-Response geliefert wird (z.B.
  ``b"abc123def..."``). Beide Seiten haben diese Form ohnehin, kein
  zusaetzliches Decoding noetig.

**App-Seite (PQC-26 CRY-6, AC-2):** Mit ``@noble/hashes`` HKDF-SHA256,
gleichen IKM/info/salt verwenden. Server- und App-Output muessen
byte-identisch sein. Cross-Validation-Test in App's Crypto-Suite.

**Sicherheit:**

- session_key niemals loggen. Aufrufer sind dafuer verantwortlich.
- HKDF mit dem ML-KEM-shared_secret als IKM verteilt Zufaelligkeit
  cryptographically robust selbst wenn der shared_secret aus Implicit-
  Rejection stammt (siehe F-090). Authentifizierung erfolgt erst beim
  AEAD-Tag-Check in DCH-1.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from crypto.facade import CryptoFacade


SESSION_KEY_LENGTH_BYTES = 32  # AES-256-GCM-Key-Laenge


def derive_session_key(
    facade: CryptoFacade,
    *,
    shared_secret: bytes,
    session_id: str,
    hkdf_info: bytes,
) -> bytes:
    """Leitet den 32-Byte-Session-Key gemaess SES-2-Konvention ab.

    Story-Bezug: PQC-47 SES-2 AC-1.

    Args:
        facade: ``CryptoFacade`` aus ``app.state.crypto_facade``.
        shared_secret: 32-Byte-Output aus ``facade.kem_encaps`` (Server-Seite)
            bzw. ``facade.kem_decaps`` (App-Seite). Wird als HKDF-IKM verwendet.
        session_id: urlsafe-base64-String wie aus SES-1-Response. Wird als
            ASCII-bytes als HKDF-Salt verwendet (siehe Konvention im Modul-
            Docstring).
        hkdf_info: Domain-Separation-Bytes aus ``settings.session.hkdf_info``,
            typisch ``b"app-session-v1"``. Pro Protokoll-Version
            inkrementieren.

    Returns:
        32-Byte AES-256-GCM-Schluessel als ``bytes``.

    **Verwendungsbeispiel (Server, in SES-1 PQC-46):**

        from services.session_key_derivation import derive_session_key

        ciphertext, shared_secret = facade.kem_encaps(client_pk, alg=kem_alg)
        session_id, _ = await session_service.create(
            user_id=user_id,
            kem_alg=kem_alg,
            session_key=derive_session_key(
                facade,
                shared_secret=shared_secret,
                session_id=session_id_placeholder,
                hkdf_info=settings.session.hkdf_info,
            ),
        )
    """
    salt = session_id.encode("ascii")
    return facade.hkdf(
        ikm=shared_secret,
        info=hkdf_info,
        salt=salt,
        length=SESSION_KEY_LENGTH_BYTES,
    )
