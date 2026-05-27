"""Configuration loading fuer den Auth-Service.

Stories: PQC-19 (SKL-1) AC-2, PQC-21 (CRY-1) AC-4.

Lade Settings in folgender Reihenfolge (von schwach nach stark):
  1. Defaults im ``Settings``-Modell (pydantic-Default-Werte)
  2. Werte aus YAML-File (Pfad ueber ``RIB_CONFIG_FILE`` env, Default ``config.yaml``)
  3. Werte aus ``.env``-File im Projekt-Root oder im server/-Ordner
  4. Environment-Variablen mit Praefix ``RIB_``

Verwendet pydantic-settings 2.x (Tech-Stack-Doku Abschnitt 2.5).

Beispielnutzung::

    from config import get_settings
    settings = get_settings()
    print(settings.app_name)
    print(settings.crypto.kem.supported)

In Tests kann der LRU-Cache via ``get_settings.cache_clear()`` zurueckgesetzt werden.
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

# Env-Var-Name fuer den optionalen alternativen YAML-Pfad (geschlossen Finding F-010
# aus docs/13_deferred_findings.md durch Class-Konstante).
_CONFIG_FILE_ENV: str = "RIB_CONFIG_FILE"


def _project_root() -> Path:
    """Wurzel des server/-Ordners."""
    return Path(__file__).resolve().parent


def _default_config_yaml() -> Path:
    return _project_root() / "config.yaml"


def _load_yaml_config(path: Path) -> dict[str, Any]:
    """Lade die YAML-Konfiguration. Gibt leeres dict zurueck, wenn die Datei fehlt."""
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
        del field  # unused, signature required by base class
        value = self._yaml_data.get(field_name)
        return value, field_name, False

    def prepare_field_value(
        self,
        field_name: str,
        field: Any,
        value: Any,
        value_is_complex: bool,
    ) -> Any:
        del field_name, field, value_is_complex  # unused, signature required by base
        return value

    def __call__(self) -> dict[str, Any]:
        return {k: v for k, v in self._yaml_data.items() if v is not None}


# ---------------------------------------------------------------------------
# Crypto-Config (PQC-21 / CRY-1 AC-4)
# ---------------------------------------------------------------------------


class KemConfig(BaseModel):
    """Konfiguration fuer KEM-Algorithmen."""

    supported: list[str] = Field(default_factory=lambda: ["ML-KEM-768"])
    default: str = Field(default="ML-KEM-768")


class SignatureConfig(BaseModel):
    """Konfiguration fuer Signatur-Algorithmen."""

    supported: list[str] = Field(default_factory=lambda: ["ML-DSA-65"])
    default: str = Field(default="ML-DSA-65")
    # PQC-25 (CRY-5) AC-5: Pfad zum persistierten Private Key.
    # In Dev wird der Key beim ersten Start auto-generiert wenn das File fehlt.
    private_key_path: str = Field(default="/data/keys/auth_signing_key.bin")
    public_key_path: str = Field(default="/data/keys/auth_signing_key.pub")
    # Defense-in-Depth (Finding K-3 aus PQC-25 Review): Auto-Keygen verlangt
    # ZWEI Flags: environment=dev UND allow_autogen_in_dev=true. Damit reicht
    # ein versehentliches RIB_ENVIRONMENT=dev in Production nicht aus, der
    # Service wuerde trotzdem hart scheitern wenn kein vorgenerierter Key da
    # ist und allow_autogen_in_dev nicht explizit gesetzt wurde.
    allow_autogen_in_dev: bool = Field(default=False)


class CryptoConfig(BaseModel):
    """Top-Level-Wrapper fuer die crypto-Section in config.yaml."""

    kem: KemConfig = Field(default_factory=KemConfig)
    signature: SignatureConfig = Field(default_factory=SignatureConfig)


class Settings(BaseSettings):
    """Typsichere Settings, geladen aus YAML, .env und Environment."""

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

    # Datenspeicher (in spaeteren Stories tatsaechlich genutzt)
    sqlite_path: str = Field(default="/data/auth.sqlite")
    redis_url: str = Field(default="redis://redis:6379/0")

    # Crypto-Layer (PQC-21 / CRY-1)
    crypto: CryptoConfig = Field(default_factory=CryptoConfig)

    @classmethod
    def settings_customise_sources(  # type: ignore[override]
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Reihenfolge: env > .env > YAML > Defaults im Modell.

        Pydantic resolved tuples in der angegebenen Prioritaets-Reihenfolge,
        wobei der erste Eintrag die hoechste Prioritaet hat.
        """
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
    """Cached Settings-Singleton. ``get_settings.cache_clear()`` resettet in Tests."""
    return Settings()
