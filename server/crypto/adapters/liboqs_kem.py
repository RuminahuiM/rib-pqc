"""liboqs-python Adapter fuer KEM-Algorithmen (ML-KEM-768, ML-KEM-1024).

Story: PQC-24 (CRY-4).
Spec: FIPS 203 (ML-KEM), implementiert via Open Quantum Safe liboqs.
Protocol-Konformitaet: ``crypto.registry.KemPlugin``.

**Wichtig fuer Tests:** Die Klasse importiert ``oqs`` erst zur Laufzeit
(nicht beim Modul-Import), damit der Modul-Import nicht crasht falls
liboqs lokal nicht installiert ist. Tests koennen via
``pytest.importorskip("oqs")`` selektiv ausgeschlossen werden.

**ML-KEM-Properties laut FIPS 203:**

- ML-KEM-768 (NIST Security Category 3): public_key 1184B, secret_key 2400B,
  ciphertext 1088B, shared_secret 32B.
- ML-KEM-1024 (NIST Security Category 5): public_key 1568B, secret_key 3168B,
  ciphertext 1568B, shared_secret 32B.
- Decapsulation hat **implicit rejection**: ein ungueltiger ciphertext liefert
  kein Error-Signal, sondern einen deterministisch-aus-(sk, ct)-abgeleiteten
  Pseudo-Shared-Secret. Authentifizierung muss daher auf Application-Layer
  (AEAD-Tag) erfolgen, siehe DCH-1.
"""

from __future__ import annotations


class LibOqsKem:
    """KEM-Adapter ueber liboqs-python.

    Stateless: keygen liefert (public_key, secret_key) als bytes. encaps und
    decaps nehmen Keys explizit als Parameter. Persistierung lebt - falls
    benoetigt - in einem separaten Modul (``crypto.keys``).

    Algorithmus-Whitelist: aktuell ``ML-KEM-768`` (CAT-3) und ``ML-KEM-1024``
    (CAT-5) gemaess FIPS 203. ML-KEM-512 ist absichtlich nicht enthalten,
    weil die Tech-Stack-Doku Sicherheits-Categorie 3 als Minimum festlegt.
    """

    _SUPPORTED: tuple[str, ...] = ("ML-KEM-768", "ML-KEM-1024")

    def __init__(self, algorithm: str) -> None:
        if algorithm not in self._SUPPORTED:
            msg = f"LibOqsKem does not support '{algorithm}'. Supported: {list(self._SUPPORTED)}"
            raise ValueError(msg)
        self._algorithm = algorithm

    @property
    def algorithm(self) -> str:
        return self._algorithm

    # ----- Keygen ------------------------------------------------------------

    def keygen(self) -> tuple[bytes, bytes]:
        """Erzeugt ein frisches KEM-Keypair (FIPS 203 K-PKE.KeyGen + K-PKE.Encaps Setup).

        Returns:
            (public_key, secret_key) als raw bytes. Groessen siehe Modul-Docstring.
        """
        import oqs

        with oqs.KeyEncapsulation(self._algorithm) as kem:
            public_key = kem.generate_keypair()
            secret_key = kem.export_secret_key()
        return public_key, secret_key

    # ----- Encaps ------------------------------------------------------------

    def encaps(self, public_key: bytes) -> tuple[bytes, bytes]:
        """Encapsuliert gegen ``public_key`` (FIPS 203 ML-KEM.Encaps).

        Returns:
            (ciphertext, shared_secret) als raw bytes. shared_secret ist
            laut FIPS 203 immer 32 Byte, unabhaengig vom Security-Level.
        """
        import oqs

        with oqs.KeyEncapsulation(self._algorithm) as kem:
            ciphertext, shared_secret = kem.encap_secret(public_key)
        return ciphertext, shared_secret

    # ----- Decaps ------------------------------------------------------------

    def decaps(self, ciphertext: bytes, secret_key: bytes) -> bytes:
        """Decapsuliert ``ciphertext`` mit ``secret_key`` (FIPS 203 ML-KEM.Decaps).

        FIPS-203-Hinweis: Bei ungueltigem Ciphertext liefert ML-KEM einen
        deterministisch-aus-(sk, ct)-abgeleiteten Pseudo-Shared-Secret zurueck
        ("implicit rejection", FIPS 203 Algorithm 18). Es gibt KEIN
        Error-Signal aus dem Algorithmus. Aufrufer muss Authentizitaet auf
        Application-Layer pruefen (typisch via AEAD-Tag in DCH-1).

        Returns:
            shared_secret als 32 Byte raw bytes.
        """
        import oqs

        with oqs.KeyEncapsulation(self._algorithm, secret_key=secret_key) as kem:
            shared_secret: bytes = kem.decap_secret(ciphertext)
        return shared_secret
