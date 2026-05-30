"""CryptoFacade: abstrakter Einstiegspunkt fuer alle Krypto-Operationen.

Story: PQC-22 (CRY-2), partial - sign/verify implementiert, KEM kommt in CRY-3.
Architektur-Bezug: docs/07_design.md Abschnitte 6.1, 6.2.

**Crypto-Agility-Prinzip:** Application-Code (Token-Module, Session-Module, etc.)
ruft NIE konkrete Algorithmen direkt auf. Stattdessen geht jede Krypto-
Operation durch diese Facade. Die Facade schaut in der ``CryptoRegistry``
welcher Plugin-Adapter (z.B. ``LibOqsSignature``) den angefragten Algorithmus
implementiert.

**Sprint-1-Stand:**
- ``sign()`` und ``verify()`` sind echt und nutzen ML-DSA-65 ueber liboqs.
- ``kem_keygen``, ``kem_encaps``, ``kem_decaps`` sind noch ``NotImplementedError``.
  Implementation in PQC-23 (CRY-3, ML-KEM-Adapter).

**Beispiel-Nutzung::**

    facade = CryptoFacade(
        registry=registry,
        default_signature_alg="ML-DSA-65",
        signing_kid="auth-signing-key-v1",
        signing_secret_key=secret_key_bytes,
        verifying_keys_by_kid={"auth-signing-key-v1": public_key_bytes},
    )
    signature, alg, kid = facade.sign(payload=b"hello", purpose="broker-token")
    ok = facade.verify(payload=b"hello", signature=signature, alg=alg, kid=kid)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from logging_config import get_logger

if TYPE_CHECKING:
    from crypto.registry import CryptoRegistry


class CryptoFacadeError(Exception):
    """Basis-Fehler fuer CryptoFacade-Probleme."""


class UnknownKidError(CryptoFacadeError):
    """Wird geworfen, wenn ``verify`` einen unbekannten ``kid`` bekommt."""


class CryptoFacade:
    """Abstrakte Crypto-Operations-Schicht.

    Stateless an der API-Oberflaeche: jeder Call ist self-contained. Intern
    haelt die Facade aber das Signing-Secret und einen ``kid → public_key``
    Lookup. Das ist OK weil pro Service-Start eine Instance lebt und in
    ``app.state.crypto_facade`` referenziert wird.
    """

    def __init__(
        self,
        *,
        registry: CryptoRegistry,
        default_signature_alg: str,
        signing_kid: str,
        signing_secret_key: bytes,
        verifying_keys_by_kid: dict[str, bytes],
    ) -> None:
        """Initialisiere die Facade.

        Args:
            registry: Befuellte ``CryptoRegistry`` mit allen unterstuetzten
                Plugins.
            default_signature_alg: Algorithmus-Name (z.B. ``"ML-DSA-65"``),
                den ``sign()`` ohne expliziten alg-Parameter nutzt.
            signing_kid: kid-String, den ``sign()`` in der Antwort zurueck-
                liefert. JOSE-JWK-Thumbprint-Format ist Sprint-3-Polish.
            signing_secret_key: Secret-Key-Bytes fuer ``sign()``. Lebt im
                Python-Memory ueber die Service-Lifetime (Finding F-014).
            verifying_keys_by_kid: Mapping kid → public_key fuer ``verify()``.
                Muss mindestens ``signing_kid`` enthalten, damit der Service
                seine eigenen Tokens verifizieren kann.

        Raises:
            CryptoFacadeError: wenn ``signing_kid`` nicht in
                ``verifying_keys_by_kid`` enthalten ist.
        """
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

    # ----- Sign / Verify (PQC-22 AC-1, AC-2) ---------------------------------

    def sign(self, payload: bytes, purpose: str) -> tuple[bytes, str, str]:
        """Signiert ``payload`` mit dem Default-Signatur-Algorithmus.

        Args:
            payload: Bytes zum Signieren (typisch: serialisierter Token-Body).
            purpose: Semantischer Kontext (z.B. ``"broker-token"``,
                ``"session-handshake"``). Sprint 1: nur als Log-Feld; spaetere
                Stories koennen pro Purpose verschiedene Keys nutzen
                (siehe Finding F-020 in docs/13_deferred_findings.md).

        Returns:
            ``(signature, alg_name, kid)`` zum Einbau in den Token-Header.
        """
        alg = self._default_signature_alg
        plugin = self._registry.get_signature(alg)
        signature = plugin.sign(payload, self._signing_secret_key)
        # PQC-30-Logging-Hardening (F-021): DEBUG statt INFO, weil sign/verify
        # bei AUT-3 hochfrequent ist und INFO-Volume sonst zu gross wird.
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
        """Verifiziert ``signature`` ueber ``payload`` mit dem per ``alg`` und
        ``kid`` ausgewaehlten Plugin und Public Key.

        Args:
            payload: Bytes ueber die signiert wurde.
            signature: Signatur aus dem Token-Header.
            alg: Algorithmus-Name aus dem Token-Header.
            kid: Key-ID aus dem Token-Header.

        Returns:
            True bei gueltiger Signatur, False sonst.

        Raises:
            AlgorithmNotFoundError: wenn ``alg`` nicht in der Registry ist.
            UnknownKidError: wenn ``kid`` nicht in ``verifying_keys_by_kid`` ist.
        """
        try:
            public_key = self._verifying_keys_by_kid[kid]
        except KeyError as exc:
            msg = (
                f"Unknown kid '{kid}'. Known: {sorted(self._verifying_keys_by_kid)}"
            )
            raise UnknownKidError(msg) from exc

        plugin = self._registry.get_signature(alg)
        result = plugin.verify(payload, signature, public_key)
        # F-021 + F-031 Logging-Hardening: erfolgreicher Verify auf DEBUG
        # (hochfrequent), failed verify auf WARNING (audit-forensik fuer
        # Token-Manipulation-Versuche). F-022 (result True/False loggen) als
        # bewusste Entscheidung behalten - hilft bei Forensik.
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

    # ----- KEM (PQC-22 AC-3: in dieser Story explizit NICHT implementiert) ---

    def kem_keygen(self, alg: str | None = None) -> tuple[bytes, bytes]:
        """Nicht implementiert. Wird in PQC-23 (CRY-3) ergaenzt."""
        del alg
        msg = (
            "CryptoFacade.kem_keygen not implemented in PQC-22 (CRY-2 partial). "
            "ML-KEM-Adapter folgt in PQC-23 (CRY-3)."
        )
        raise NotImplementedError(msg)

    def kem_encaps(self, public_key: bytes, alg: str) -> tuple[bytes, bytes]:
        """Nicht implementiert. Wird in PQC-23 (CRY-3) ergaenzt."""
        del public_key, alg
        msg = (
            "CryptoFacade.kem_encaps not implemented in PQC-22 (CRY-2 partial). "
            "ML-KEM-Adapter folgt in PQC-23 (CRY-3)."
        )
        raise NotImplementedError(msg)

    def kem_decaps(self, ciphertext: bytes, secret_key: bytes, alg: str) -> bytes:
        """Nicht implementiert. Wird in PQC-23 (CRY-3) ergaenzt."""
        del ciphertext, secret_key, alg
        msg = (
            "CryptoFacade.kem_decaps not implemented in PQC-22 (CRY-2 partial). "
            "ML-KEM-Adapter folgt in PQC-23 (CRY-3)."
        )
        raise NotImplementedError(msg)

    # ----- Diagnostik --------------------------------------------------------

    def supported_signature_algorithms(self) -> list[str]:
        """Pass-Through fuer Diagnose und Negotiation."""
        return self._registry.supported_signature()
