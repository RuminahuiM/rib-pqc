"""CryptoFacade: abstrakter Einstiegspunkt fuer alle Krypto-Operationen.

Stories:
- PQC-22 (CRY-2): sign/verify Implementation.
- PQC-23 (CRY-3): KEM-Methoden + HKDF + AEAD + Negotiation-Support.

Architektur-Bezug: docs/07_design.md Abschnitte 6.1, 6.2.

**Crypto-Agility-Prinzip:** Application-Code (Token-Module, Session-Module, etc.)
ruft NIE konkrete Algorithmen direkt auf. Stattdessen geht jede Krypto-
Operation durch diese Facade. Die Facade schaut in der ``CryptoRegistry``
welcher Plugin-Adapter (z.B. ``LibOqsSignature``, ``LibOqsKem``) den
angefragten Algorithmus implementiert.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

from logging_config import get_logger

if TYPE_CHECKING:
    from crypto.registry import CryptoRegistry


class CryptoFacadeError(Exception):
    """Basis-Fehler fuer CryptoFacade-Probleme."""


class UnknownKidError(CryptoFacadeError):
    """Wird geworfen, wenn ``verify`` einen unbekannten ``kid`` bekommt."""


class AeadDecryptError(CryptoFacadeError):
    """Wird geworfen, wenn ``aead_decrypt`` den AEAD-Tag nicht verifizieren kann.

    Story: PQC-23 CRY-3 plus PQC-50 DCH-1. FIPS-203-Konnex (F-090): KEM-
    Decapsulation liefert bei ungueltigem ct ein Pseudo-shared-secret, KEINEN
    Fehler. Die Authentifizierung des Channels haengt daher an dieser AEAD-
    Tag-Verifikation. Aufrufer muss diesen Fehler in 4xx-Response abbilden.
    """


class CryptoFacade:
    """Abstrakte Crypto-Operations-Schicht."""

    def __init__(
        self,
        *,
        registry: CryptoRegistry,
        default_signature_alg: str,
        signing_kid: str,
        signing_secret_key: bytes,
        verifying_keys_by_kid: dict[str, bytes],
    ) -> None:
        if signing_kid not in verifying_keys_by_kid:
            msg = (
                f"signing_kid '{signing_kid}' must be present in "
                f"verifying_keys_by_kid (got keys: {list(verifying_keys_by_kid)})"
            )
            raise CryptoFacadeError(msg)
        self._registry = registry
        self._default_signature_alg = default_signature_alg
        self._signing_kid = signing_kid
        self._signing_secret_key = signing_secret_key
        self._verifying_keys_by_kid = dict(verifying_keys_by_kid)
        self._logger = get_logger("rib_pqc.crypto.facade")

    # ----- Sign / Verify (PQC-22 AC-1, AC-2) -----

    def sign(self, payload: bytes, purpose: str) -> tuple[bytes, str, str]:
        """Signiert ``payload`` mit dem Default-Signatur-Algorithmus."""
        alg = self._default_signature_alg
        plugin = self._registry.get_signature(alg)
        signature = plugin.sign(payload, self._signing_secret_key)
        self._logger.debug(
            "crypto.facade.sign",
            purpose=purpose,
            alg=alg,
            kid=self._signing_kid,
            payload_len=len(payload),
            signature_len=len(signature),
        )
        return signature, alg, self._signing_kid

    def verify(self, payload: bytes, signature: bytes, alg: str, kid: str) -> bool:
        """Verifiziert ``signature`` ueber ``payload`` mit Plugin+PublicKey."""
        try:
            public_key = self._verifying_keys_by_kid[kid]
        except KeyError as exc:
            msg = f"Unknown kid '{kid}'. Known: {sorted(self._verifying_keys_by_kid)}"
            raise UnknownKidError(msg) from exc

        plugin = self._registry.get_signature(alg)
        result = plugin.verify(payload, signature, public_key)
        if result:
            self._logger.debug(
                "crypto.facade.verify",
                alg=alg,
                kid=kid,
                payload_len=len(payload),
                signature_len=len(signature),
                result=result,
            )
        else:
            self._logger.warning(
                "crypto.facade.verify_failed",
                alg=alg,
                kid=kid,
                payload_len=len(payload),
                signature_len=len(signature),
                reason="signature_invalid",
            )
        return result

    # ----- KEM (PQC-23 CRY-3) -----

    def kem_keygen(self, alg: str) -> tuple[bytes, bytes]:
        """ML-KEM-Keypair ueber Registry-Plugin fuer ``alg``."""
        plugin = self._registry.get_kem(alg)
        public_key, secret_key = plugin.keygen()
        self._logger.debug(
            "crypto.facade.kem_keygen",
            alg=alg,
            public_key_len=len(public_key),
            secret_key_len=len(secret_key),
        )
        return public_key, secret_key

    def kem_encaps(self, public_key: bytes, alg: str) -> tuple[bytes, bytes]:
        """Encapsuliert frisches shared_secret gegen ``public_key``."""
        plugin = self._registry.get_kem(alg)
        ciphertext, shared_secret = plugin.encaps(public_key)
        self._logger.debug(
            "crypto.facade.kem_encaps",
            alg=alg,
            public_key_len=len(public_key),
            ciphertext_len=len(ciphertext),
            shared_secret_len=len(shared_secret),
        )
        return ciphertext, shared_secret

    def kem_decaps(self, ciphertext: bytes, secret_key: bytes, alg: str) -> bytes:
        """ML-KEM Decaps. Implicit-Rejection (F-090): KEIN Error bei wrong ct."""
        plugin = self._registry.get_kem(alg)
        shared_secret = plugin.decaps(ciphertext, secret_key)
        self._logger.debug(
            "crypto.facade.kem_decaps",
            alg=alg,
            ciphertext_len=len(ciphertext),
            shared_secret_len=len(shared_secret),
        )
        return shared_secret

    # ----- HKDF (PQC-23 CRY-3, RFC 5869) -----

    def hkdf(
        self,
        ikm: bytes,
        info: bytes,
        salt: bytes,
        length: int = 32,
    ) -> bytes:
        """HKDF-SHA256 Schluessel-Ableitung (RFC 5869). Default 32 Byte."""
        kdf = HKDF(
            algorithm=hashes.SHA256(),
            length=length,
            salt=salt,
            info=info,
        )
        derived = kdf.derive(ikm)
        self._logger.debug(
            "crypto.facade.hkdf",
            ikm_len=len(ikm),
            info_len=len(info),
            salt_len=len(salt),
            length=length,
        )
        return derived

    # ----- AEAD (PQC-23 CRY-3, AES-256-GCM) -----

    def aead_encrypt(
        self,
        key: bytes,
        nonce: bytes,
        plaintext: bytes,
        aad: bytes = b"",
    ) -> bytes:
        """AES-256-GCM Encrypt. Returns ciphertext concatenated with tag."""
        cipher = AESGCM(key)
        blob = cipher.encrypt(nonce, plaintext, aad if aad else None)
        self._logger.debug(
            "crypto.facade.aead_encrypt",
            key_len=len(key),
            nonce_len=len(nonce),
            plaintext_len=len(plaintext),
            aad_len=len(aad),
            blob_len=len(blob),
        )
        return blob

    def aead_decrypt(
        self,
        key: bytes,
        nonce: bytes,
        ciphertext_and_tag: bytes,
        aad: bytes = b"",
    ) -> bytes:
        """AES-256-GCM Decrypt. Wirft AeadDecryptError bei Tag-Mismatch."""
        cipher = AESGCM(key)
        try:
            plaintext = cipher.decrypt(nonce, ciphertext_and_tag, aad if aad else None)
        except InvalidTag as exc:
            self._logger.warning(
                "crypto.facade.aead_decrypt_failed",
                key_len=len(key),
                nonce_len=len(nonce),
                blob_len=len(ciphertext_and_tag),
                aad_len=len(aad),
                reason="invalid_tag",
            )
            msg = "AEAD tag verification failed (key/nonce/aad mismatch or tampered ciphertext)"
            raise AeadDecryptError(msg) from exc
        self._logger.debug(
            "crypto.facade.aead_decrypt",
            key_len=len(key),
            nonce_len=len(nonce),
            blob_len=len(ciphertext_and_tag),
            aad_len=len(aad),
            plaintext_len=len(plaintext),
        )
        return plaintext

    # ----- Diagnostik + Negotiation (PQC-23 CRY-3) -----

    def supported_signature_algorithms(self) -> list[str]:
        """Pass-Through fuer Diagnose und Negotiation."""
        return self._registry.supported_signature()

    def supported_kem_algorithms(self) -> list[str]:
        """Liste registrierter KEM-Algorithmen (fuer SES-4 Negotiation)."""
        return self._registry.supported_kem()

    def is_kem_supported(self, alg: str) -> bool:
        """Prueft ob ``alg`` als KEM in der Registry steht (SES-1, SES-4)."""
        return alg in self._registry.supported_kem()
