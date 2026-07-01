"""Tests fuer TOK-3 Schluessel-Rotation (PQC-34).

Test-Strategie:
- Multi-Key-Config-Parsing via Pydantic (SignatureConfig.get_effective_keys).
- Backwards-Compat: alte signing_kid-only-Config liefert default-Eintrag.
- get_active_kid: active_kid-Override vs signing_kid-Fallback.
- CLI rotate-signing-key (liboqs-Skip-Pattern fuer Sandbox).
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from config import KeyEntry, SignatureConfig

if TYPE_CHECKING:
    pass


# --- Multi-Key-Config-Parsing ---


def test_signature_config_default_backwards_compat() -> None:
    """Ohne keys-Dict: get_effective_keys liefert ein Single-Key-Default."""
    cfg = SignatureConfig()
    effective = cfg.get_effective_keys()
    assert len(effective) == 1
    assert cfg.signing_kid in effective
    entry = effective[cfg.signing_kid]
    assert entry.private_key_path == cfg.private_key_path
    assert entry.public_key_path == cfg.public_key_path


def test_signature_config_multi_key_explicit() -> None:
    """Mit keys-Dict: get_effective_keys gibt diesen Dict zurueck."""
    cfg = SignatureConfig(
        active_kid="key-v2",
        keys={
            "key-v1": KeyEntry(
                private_key_path="/tmp/k1.bin",
                public_key_path="/tmp/k1.pub",
            ),
            "key-v2": KeyEntry(
                private_key_path="/tmp/k2.bin",
                public_key_path="/tmp/k2.pub",
            ),
        },
    )
    effective = cfg.get_effective_keys()
    assert set(effective) == {"key-v1", "key-v2"}
    assert cfg.get_active_kid() == "key-v2"


def test_signature_config_active_kid_fallback_to_signing_kid() -> None:
    """Ohne active_kid: Fallback auf signing_kid."""
    cfg = SignatureConfig(signing_kid="legacy-kid")
    assert cfg.active_kid is None
    assert cfg.get_active_kid() == "legacy-kid"


def test_signature_config_active_kid_overrides_signing_kid() -> None:
    """active_kid hat Vorrang ueber signing_kid (falls beide gesetzt)."""
    cfg = SignatureConfig(
        signing_kid="legacy-kid",
        active_kid="key-v2",
        keys={
            "key-v2": KeyEntry(
                private_key_path="/tmp/k2.bin",
                public_key_path="/tmp/k2.pub",
            ),
        },
    )
    assert cfg.get_active_kid() == "key-v2"


# --- KeyEntry-Validierung ---


def test_key_entry_requires_both_paths() -> None:
    """KeyEntry braucht private + public path."""
    entry = KeyEntry(private_key_path="/p1", public_key_path="/p2")
    assert entry.private_key_path == "/p1"
    assert entry.public_key_path == "/p2"

    with pytest.raises(ValueError):
        KeyEntry(private_key_path="/p1")  # type: ignore[call-arg]


# --- CLI rotate-signing-key (liboqs-Skip fuer Sandbox per-Test) ---

_liboqs_available: bool
try:
    import oqs as _oqs  # noqa: F401

    _liboqs_available = True
except ImportError:
    _liboqs_available = False

_skip_no_liboqs = pytest.mark.skipif(
    not _liboqs_available,
    reason="liboqs-python not installed in this environment",
)


@_skip_no_liboqs
def test_rotate_signing_key_cli_creates_key_files_and_updates_config(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Voll-Integration: CLI generiert Key-Files + updated YAML."""
    import yaml

    # Setup: minimal-Config-YAML mit Single-Key-Sprint-1-Stil.
    keys_dir = tmp_path / "keys"
    keys_dir.mkdir()
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        yaml.safe_dump(
            {
                "crypto": {
                    "signature": {
                        "supported": ["ML-DSA-65"],
                        "default": "ML-DSA-65",
                        "signing_kid": "default",
                        "private_key_path": str(keys_dir / "default.bin"),
                        "public_key_path": str(keys_dir / "default.pub"),
                    },
                    "kem": {"supported": ["ML-KEM-768"]},
                },
            },
        ),
    )

    from admin import _cmd_rotate_signing_key

    rc = _cmd_rotate_signing_key(
        new_kid="key-v2",
        keys_dir=str(keys_dir),
        config_path=str(config_file),
    )
    assert rc == 0

    # Key-Files vorhanden
    assert (keys_dir / "key-v2.bin").exists()
    assert (keys_dir / "key-v2.pub").exists()

    # Config-YAML geupdated
    updated = yaml.safe_load(config_file.read_text())
    sig = updated["crypto"]["signature"]
    assert sig["active_kid"] == "key-v2"
    assert "key-v2" in sig["keys"]
    assert sig["keys"]["key-v2"]["private_key_path"] == str(keys_dir / "key-v2.bin")
    assert sig["keys"]["key-v2"]["public_key_path"] == str(keys_dir / "key-v2.pub")


@_skip_no_liboqs
def test_rotate_signing_key_cli_rejects_duplicate_kid(
    tmp_path: Path,
) -> None:
    """CLI lehnt duplicate kid ab."""
    import yaml

    keys_dir = tmp_path / "keys"
    keys_dir.mkdir()
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        yaml.safe_dump(
            {
                "crypto": {
                    "signature": {
                        "supported": ["ML-DSA-65"],
                        "default": "ML-DSA-65",
                        "signing_kid": "existing",
                        "keys": {
                            "existing": {
                                "private_key_path": str(keys_dir / "existing.bin"),
                                "public_key_path": str(keys_dir / "existing.pub"),
                            },
                        },
                    },
                    "kem": {"supported": ["ML-KEM-768"]},
                },
            },
        ),
    )

    from admin import _cmd_rotate_signing_key

    rc = _cmd_rotate_signing_key(
        new_kid="existing",  # collision
        keys_dir=str(keys_dir),
        config_path=str(config_file),
    )
    assert rc != 0
