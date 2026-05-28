"""Configuration loading fuer den Auth-Service.

Stories: PQC-19 SKL-1, PQC-21 CRY-1, PQC-25 CRY-5, PQC-22 CRY-2,
PQC-32 TOK-1, PQC-33 TOK-2, PQC-28 AUT-1.

Lade Settings in folgender Reihenfolge (von schwach nach stark):
  1. Defaults im ``Settings``-Modell
  2. Werte aus YAML-File (Pfad ueber ``RIB_CONFIG_FILE`` env, Default config.yaml)
  3. Werte aus ``.env``-File
  4. Environment-Variablen mit Praefix ``RIB_``
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict

LogLevel = Literal["debug", "info", "warning", "error", "critical"]
Environment = Literal["dev", "staging", "prod"]

_CONFIG_FILE_ENV: str = "RIB_CONFIG_FILE"


def _project_root() -> Path:
    return Path(__file__).resolve().parent


def _default_config_yaml() -> Path:
    return _project_root() / "config.yaml"


def _load_yaml_config(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh) or {}
    if not isinstance(raw, dict):
        msg = f"config YAML at {path} must be a mapping at top level, got {type(raw).__name__}"
        raise ValueError(msg)
    return raw


class YamlConfigSource(PydanticBaseSettingsSource):
    """Pydantic-Settings-Source, die Werte aus einer YAML-Datei liest."""

    def __init__(self, settings_cls: type[BaseSettings], yaml_path: Path) -> None:
        super().__init__(settings_cls)
        self._yaml_data: dict[str, Any] = _load_yaml_config(yaml_path)

    def get_field_value(self, field: Any, field_name: str) -> tuple[Any, str, bool]:
        del field
        value = self._yaml_data.get(field_name)
        return value, field_name, False

    def prepare_field_value(
        self,
        field_name: str,
        field: Any,
        value: Any,
        value_is_complex: bool,
    ) -> Any:
        del field_name, field, value_is_complex
        return value

    def __call__(self) -> dict[str, Any]:
        return {k: v for k, v in self._yaml_data.items() if v is not None}


# ---------------------------------------------------------------------------
# Crypto-Config (PQC-21 / CRY-1 AC-4)
# ---------------------------------------------------------------------------


class KemConfig(BaseModel):
    supported: list[str] = Field(default_factory=lambda: ["ML-KEM-768"])
    default: str = Field(default="ML-KEM-768")


class SignatureConfig(BaseModel):
    supported: list[str] = Field(default_factory=lambda: ["ML-DSA-65"])
    default: str = Field(default="ML-DSA-65")
    private_key_path: str = Field(default="/data/keys/auth_signing_key.bin")
    public_key_path: str = Field(default="/data/keys/auth_signing_key.pub")
    allow_autogen_in_dev: bool = Field(default=False)
    signing_kid: str = Field(default="auth-signing-key-v1")


class CryptoConfig(BaseModel):
    kem: KemConfig = Field(default_factory=KemConfig)
    signature: SignatureConfig = Field(default_factory=SignatureConfig)


# ---------------------------------------------------------------------------
# Token-Config (PQC-32 / TOK-1, erweitert in PQC-33 / TOK-2)
# ---------------------------------------------------------------------------


class TokenConfig(BaseModel):
    """Konfiguration fuer Broker-Token-Issuance und -Verifikation."""

    issuer: str = Field(default="pqc-auth-service")
    ttl_seconds: int = Field(default=3600, ge=1)
    # PQC-33 AC-6: case-insensitive Allowlist (RFC 8725 BCP).
    allowed_algs: list[str] = Field(default_factory=lambda: ["ML-DSA-65"])
    # PQC-33 AC-3: Clock-Skew-Toleranz fuer exp-Check, nicht iat.
    exp_leeway_seconds: int = Field(default=30, ge=0)


# ---------------------------------------------------------------------------
# Argon2-Config (PQC-28 / AUT-1 AC-4)
# ---------------------------------------------------------------------------


class Argon2Config(BaseModel):
    """Argon2id-Parameter fuer Password-Hashing.

    Story-AC-4 Default-Werte (m=64MB, t=3, p=4): sicherer als OWASP-2024-
    Sweet-Spot, CPU/RAM-intensiver pro Hash (~250-500ms auf modernem Host).

    Tuning-Hinweis: Falls Login zu langsam wirkt im realen Setup, koennen die
    Werte ohne Code-Aenderung auf OWASP-2024 reduziert werden (z.B.
    memory_cost_kb=46000, time_cost=1, parallelism=1). Sicherheits-Tradeoff
    vorab dokumentieren.
    """

    memory_cost_kb: int = Field(default=65536, ge=8)
    time_cost: int = Field(default=3, ge=1)
    parallelism: int = Field(default=4, ge=1)
    salt_length: int = Field(default=16, ge=8)
    hash_length: int = Field(default=32, ge=16)


# ---------------------------------------------------------------------------
# Database-Config (PQC-28 / AUT-1 AC-2, AC-3)
# ---------------------------------------------------------------------------


class DatabaseConfig(BaseModel):
    """Async-Database-Konfiguration (SQLAlchemy 2.0 + aiosqlite).

    Application nutzt async_url (aiosqlite-Treiber).
    Alembic nutzt sync_url (Standard sqlite3-Treiber) fuer Migrations.
    Beide URLs zeigen typisch auf dieselbe Datei, nur Treiber unterscheidet.
    """

    async_url: str = Field(default="sqlite+aiosqlite:////data/auth.sqlite")
    sync_url: str = Field(default="sqlite:////data/auth.sqlite")
    echo: bool = Field(default=False)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="RIB_",
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_nested_delimiter="__",
    )

    # Identitaet
    app_name: str = Field(default="rib-pqc-auth-service")
    version: str = Field(default="0.1.0")
    environment: Environment = Field(default="dev")

    # HTTP-Server
    host: str = Field(default="0.0.0.0")  # noqa: S104
    port: int = Field(default=8000, ge=1, le=65535)

    # Logging
    log_level: LogLevel = Field(default="info")

    # Datenspeicher (Legacy-Felder, durch DatabaseConfig schrittweise abgeloest)
    sqlite_path: str = Field(default="/data/auth.sqlite")
    redis_url: str = Field(default="redis://redis:6379/0")

    # Crypto-Layer (PQC-21 / CRY-1)
    crypto: CryptoConfig = Field(default_factory=CryptoConfig)

    # Token-Layer (PQC-32 / TOK-1, PQC-33 / TOK-2)
    token: TokenConfig = Field(default_factory=TokenConfig)

    # Argon2-Layer (PQC-28 / AUT-1)
    argon2: Argon2Config = Field(default_factory=Argon2Config)

    # Database-Layer (PQC-28 / AUT-1)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)

    @classmethod
    def settings_customise_sources(  # type: ignore[override]
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        yaml_path_str = os.environ.get(_CONFIG_FILE_ENV)
        yaml_path = Path(yaml_path_str) if yaml_path_str else _default_config_yaml()
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            YamlConfigSource(settings_cls, yaml_path),
            file_secret_settings,
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
