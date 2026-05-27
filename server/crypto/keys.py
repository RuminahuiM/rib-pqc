"""Helpers zum Lesen und Schreiben von Krypto-Schluesseln auf der Disk.

Story: PQC-25 (CRY-5), Acceptance Criterion AC-5 (Schluessel-Persistierung).

**Schema:** Raw-Bytes-Format. Eine Datei enthaelt genau einen Key (Private oder
Public). Die Wahl welcher Key drin ist, bestimmt die Datei-Namens-Konvention
des Aufrufers (z.B. ``auth_signing_key.bin`` fuer den Private Key,
``auth_signing_key.pub`` fuer den Public Key).

**Datei-Permissions:** Private-Key-Dateien werden mit ``chmod 0600``
geschrieben, damit nur der Owner-Process lesen darf. Public-Key-Dateien
behalten die System-Default-Permissions.

**Erweiterungs-Hinweis:** Spaetere Stories (Session-Keys, OIDC-Client-Secrets)
koennten ein generischeres Key-Storage-Interface gebrauchen. Fuer Sprint 1 ist
diese einfache File-Variante ausreichend.
"""

from __future__ import annotations

import contextlib
import os
from pathlib import Path


def save_secret_key(path: Path, key: bytes) -> None:
    """Schreibt ``key`` nach ``path`` mit Permissions 0600.

    Erzeugt fehlende Parent-Directories.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    # Geschrieben via Open mit O_CREAT plus O_EXCL Logik nicht noetig, weil
    # Idempotenz erlaubt ist (Restart laedt vorhandenen Key).
    path.write_bytes(key)
    # chmod nach dem Schreiben. Auf Windows / WSL ist 0600 nicht immer
    # enforceable, das ist OK fuer Dev. Production-Container laeuft als
    # non-root und chmod klappt.
    with contextlib.suppress(PermissionError, OSError):
        os.chmod(path, 0o600)


def save_public_key(path: Path, key: bytes) -> None:
    """Schreibt ``key`` nach ``path`` mit Default-Permissions."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(key)


def load_key(path: Path) -> bytes:
    """Laedt einen Key aus der Datei ``path``.

    Raises:
        FileNotFoundError: wenn die Datei nicht existiert.
        ValueError: wenn die Datei leer ist.
    """
    if not path.is_file():
        msg = f"Key file does not exist: {path}"
        raise FileNotFoundError(msg)
    data = path.read_bytes()
    if not data:
        msg = f"Key file is empty: {path}"
        raise ValueError(msg)
    return data


def key_file_exists(path: Path) -> bool:
    """Praktischer Wrapper fuer Existenz-Pruefung."""
    return path.is_file() and path.stat().st_size > 0
