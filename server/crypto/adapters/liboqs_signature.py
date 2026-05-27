"""liboqs-python Adapter fuer Signatur-Algorithmen (ML-DSA-65).

Story: PQC-25 (CRY-5).
Spec: FIPS 204 (ML-DSA), implementiert via Open Quantum Safe liboqs.
Protocol-Konformitaet: ``crypto.registry.SignaturePlugin``.

**Wichtig fuer Tests:** Die Klasse importiert ``oqs`` erst zur Laufzeit
(nicht beim Modul-Import), damit der Modul-Import nicht crasht falls
liboqs lokal nicht installiert ist. Tests koennen via
``pytest.importorskip("oqs")`` selektiv ausgeschlossen werden.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


class LibOqsSignature:
    """Signatur-Adapter ueber liboqs-python.

    Stateless: keygen liefert (public_key, secret_key) als bytes. sign und
    verify nehmen Keys explizit als Parameter. Schluessel-Persistierung lebt
    in einem separaten Modul (``crypto.keys``).

    Algorithmus-Whitelist: aktuell nur ``ML-DSA-65`` (FIPS 204). ML-DSA-44
    und ML-DSA-87 kann man trivial nachziehen, wir bleiben aber bei der
    Tech-Stack-Doku-Wahl ML-DSA-65.
    """

    _SUPPORTED: tuple[str, ...] = ("ML-DSA-65",)

    def __init__(self, algorithm: str) -> None:
        if algorithm not in self._SUPPORTED:
            msg = (
                f"LibOqsSignature does not support '{algorithm}'. "
                f"Supported: {list(self._SUPPORTED)}"
            )
            raise ValueError(msg)
        self._algorithm = algorithm

    @property
    def algorithm(self) -> str:
        return self._algorithm

    # ----- Keygen ------------------------------------------------------------

    def keygen(self) -> tuple[bytes, bytes]:
        """Erzeugt ein frisches Keypair.

        Returns:
            (public_key, secret_key) als raw bytes.
        """
        import oqs

        with oqs.Signature(self._algorithm) as signer:
            public_key = signer.generate_keypair()
            secret_key = signer.export_secret_key()
        return public_key, secret_key

    # ----- Sign --------------------------------------------------------------

    def sign(self, message: bytes, secret_key: bytes) -> bytes:
        """Signiert ``message`` unter ``secret_key`` mit ML-DSA-65.

        Returns:
            Signatur als raw bytes.
        """
        import oqs

        with oqs.Signature(self._algorithm, secret_key=secret_key) as signer:
            signature: bytes = signer.sign(message)
        return signature

    # ----- Verify ------------------------------------------------------------

    def verify(self, message: bytes, signature: bytes, public_key: bytes) -> bool:
        """Verifiziert ``signature`` ueber ``message`` unter ``public_key``.

        Returns:
            True bei gueltiger Signatur, False sonst. liboqs wirft bei
            invalidem Format eventuell Exceptions; die kapseln wir hier in
            False, damit Aufrufer ein einheitliches bool-Interface haben.
        """
        import oqs

        # TODO(F-015): Exception-Klasse einengen. Aktuell faengt das alles ab,
        # was liboqs werfen koennte; klarer waere nur Format-/Decoding-Errors zu
        # fangen und echte Crashes nach aussen weiterzureichen. Siehe
        # docs/13_deferred_findings.md (F-015).
        try:
            with oqs.Signature(self._algorithm) as verifier:
                result: bool = verifier.verify(message, signature, public_key)
        except Exception:
            return False
        return bool(result)
