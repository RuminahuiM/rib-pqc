"""Configuration loading fuer den Auth-Service.

Stories: PQC-19 SKL-1, PQC-21 CRY-1, PQC-25 CRY-5, PQC-22 CRY-2,
PQC-32 TOK-1, PQC-33 TOK-2, PQC-28 AUT-1, PQC-79 SEC-1, PQC-80/81/82 SEC-2/3/4.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, Field, model_validator
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


class TokenConfig(BaseModel):
    issuer: str = Field(default="pqc-auth-service")
    ttl_seconds: int = Field(default=3600, ge=1)
    allowed_algs: list[str] = Field(default_factory=lambda: ["ML-DSA-65"])
    exp_leeway_seconds: int = Field(default=30, ge=0)


class Argon2Config(BaseModel):
    memory_cost_kb: int = Field(default=65536, ge=8)
    time_cost: int = Field(default=3, ge=1)
    parallelism: int = Field(default=4, ge=1)
    salt_length: int = Field(default=16, ge=8)
    hash_length: int = Field(default=32, ge=16)


class DatabaseConfig(BaseModel):
    async_url: str = Field(default="sqlite+aiosqlite:////data/auth.sqlite")
    sync_url: str = Field(default="sqlite:////data/auth.sqlite")
    echo: bool = Field(default=False)


class CorsConfig(BaseModel):
    """CORS-Allowlist (PQC-80 SEC-2)."""

    allowed_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:8081",
            "http://localhost:8080",
        ]
    )
    allowed_methods: list[str] = Field(
        default_factory=lambda: ["GET", "POST", "OPTIONS"]
    )
    allowed_headers: list[str] = Field(
        default_factory=lambda: ["Authorization", "Content-Type", "X-Request-ID"]
    )
    allow_credentials: bool = Field(default=False)

    @model_validator(mode="after")
    def _validate_no_wildcard_with_credentials(self) -> CorsConfig:
        """PQC-80 AC-3: Wildcard mit allow_credentials=True ist Browser-Spec-Violation."""
        if self.allow_credentials and "*" in self.allowed_origins:
            msg = (
                "CORS-Misconfig: allow_credentials=True ist inkompatibel mit "
                "Wildcard '*' in allowed_origins (Browser-Spec). Setze konkrete "
                "Origins oder allow_credentials=False."
            )
            raise ValueError(msg)
        return self


class SecurityHeadersConfig(BaseModel):
    enabled: bool = Field(default=True)
    hsts_max_age_seconds: int = Field(default=31536000, ge=0)
    hsts_include_subdomains: bool = Field(default=True)


class RateLimitConfig(BaseModel):
    """Rate-Limiting (PQC-83 SEC-5).

    Per-IP via slowapi mit Redis-Storage. Defaults:
    - global: 60/minute (AC-2)
    - login: 5/15minutes (OWASP-strenger als AC-3-Vorschlag 5/minute,
      explizite Senior-Decision)

    Production-Hardening: Per-Email-Composite-Key als Sprint-3-Polish gegen
    distributed Brute-Force aus Botnets. Aktuell Per-IP only (DoS-Risiko
    durch Account-Lockout vermieden).
    """

    enabled: bool = Field(default=True)
    global_default: str = Field(default="60/minute")
    login_limit: str = Field(default="5/15minutes")
    # slowapi nutzt limits-Lib mit redis/memory Storage-Backend.
    # storage_uri: "redis://redis:6379/1" fuer Container, "memory://" fuer Tests.
    storage_uri: str = Field(default="redis://redis:6379/1")


class SecurityConfig(BaseModel):
    cors: CorsConfig = Field(default_factory=CorsConfig)
    trusted_hosts: list[str] = Field(
        default_factory=lambda: [
            "localhost",
            "127.0.0.1",
            "auth-service",
            "testserver",
        ]
    )
    headers: SecurityHeadersConfig = Field(default_factory=SecurityHeadersConfig)
    rate_limit: RateLimitConfig = Field(default_factory=RateLimitConfig)


# ---------------------------------------------------------------------------
# IdP Provider Federation (Stories PQC-84 BRK-0, PQC-36 BRK-1)
# ---------------------------------------------------------------------------
# Pro Provider eine Pydantic-Klasse. Gemeinsame Basis fuer Felder die alle
# OIDC-Provider haben (issuer, discovery_url, redirect_uri, scopes, client_id,
# client_secret). Provider-spezifische Felder (z.B. tenant_id fuer Microsoft)
# in den Subklassen.
#
# BFF-Pattern (siehe PQC-84 Evidence): Server ist Confidential Client mit
# client_secret. Client-Secret kommt aus ENV (RIB_IDP_PROVIDERS__<NAME>__CLIENT_SECRET),
# YAML-Default ist Platzhalter "".


class BaseProviderConfig(BaseModel):
    """Gemeinsame Felder fuer alle OIDC-Provider-Configs."""

    enabled: bool = Field(default=False)
    redirect_uri: str = Field(default="")
    scopes: list[str] = Field(default_factory=lambda: ["openid", "email", "profile"])
    client_id: str = Field(default="")
    client_secret: str = Field(default="")


class GoogleProviderConfig(BaseProviderConfig):
    """Google OIDC-Provider-Config.

    issuer und discovery_url sind feste Google-Endpoints, daher hier als
    Default. Override per YAML moeglich (z.B. fuer mock/test-Provider).
    """

    issuer: str = Field(default="https://accounts.google.com")
    discovery_url: str = Field(
        default="https://accounts.google.com/.well-known/openid-configuration"
    )


class MicrosoftProviderConfig(BaseProviderConfig):
    """Microsoft Entra ID OIDC-Provider-Config (Single-Tenant).

    Issuer und discovery_url werden zur Laufzeit aus dem ``tenant_id`` komponiert
    weil sie tenant-spezifisch sind:
        issuer = "https://login.microsoftonline.com/<tenant>/v2.0"
        discovery_url = ".../<tenant>/v2.0/.well-known/openid-configuration"

    Pattern siehe PQC-84 BRK-0 Evidence und docs/06_tech_stack.md.
    """

    tenant_id: str = Field(default="")

    @property
    def issuer(self) -> str:
        """Komponiert den issuer aus tenant_id (Single-Tenant-Pattern)."""
        return f"https://login.microsoftonline.com/{self.tenant_id}/v2.0"

    @property
    def discovery_url(self) -> str:
        """Komponiert die discovery_url aus tenant_id."""
        return (
            f"https://login.microsoftonline.com/{self.tenant_id}"
            f"/v2.0/.well-known/openid-configuration"
        )


class IdpProvidersConfig(BaseModel):
    """Container fuer alle bekannten OIDC-Provider.

    BRK-1 (PQC-36) registriert genau die Provider mit ``enabled=true`` in der
    Registry. Neue Provider (z.B. Apple in STR-2 PQC-76) werden hier als
    weiteres Feld plus Subklasse hinzugefuegt.
    """

    google: GoogleProviderConfig = Field(default_factory=GoogleProviderConfig)
    microsoft: MicrosoftProviderConfig = Field(default_factory=MicrosoftProviderConfig)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="RIB_",
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_nested_delimiter="__",
    )

    app_name: str = Field(default="rib-pqc-auth-service")
    version: str = Field(default="0.1.0")
    environment: Environment = Field(default="dev")

    host: str = Field(default="0.0.0.0")  # noqa: S104
    port: int = Field(default=8000, ge=1, le=65535)

    log_level: LogLevel = Field(default="info")

    sqlite_path: str = Field(default="/data/auth.sqlite")
    redis_url: str = Field(default="redis://redis:6379/0")

    crypto: CryptoConfig = Field(default_factory=CryptoConfig)
    token: TokenConfig = Field(default_factory=TokenConfig)
    argon2: Argon2Config = Field(default_factory=Argon2Config)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    idp_providers: IdpProvidersConfig = Field(default_factory=IdpProvidersConfig)

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
Pattern siehe PQC-84 BRK-0 Evidence und docs/06_tech_stack.md.
    """

    tenant_id: str = Field(default="")

    @property
    def issuer(self) -> str:
        """Komponiert den issuer aus tenant_id (Single-Tenant-Pattern)."""
        return f"https://login.microsoftonline.com/{self.tenant_id}/v2.0"

    @property
    def discovery_url(self) -> str:
        """Komponiert die discovery_url aus tenant_id."""
        return (
            f"https://login.microsoftonline.com/{self.tenant_id}"
            f"/v2.0/.well-known/openid-configuration"
        )


class IdpProvidersConfig(BaseModel):
    """Container fuer alle bekannten OIDC-Provider.

    BRK-1 (PQC-36) registriert genau die Provider mit ``enabled=true`` in der
    Registry. Neue Provider (z.B. Apple in STR-2 PQC-76) werden hier als
    weiteres Feld plus Subklasse hinzugefuegt.
    """

    google: GoogleProviderConfig = Field(default_factory=GoogleProviderConfig)
    microsoft: MicrosoftProviderConfig = Field(default_factory=MicrosoftProviderConfig)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="RIB_",
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_nested_delimiter="__",
    )

    app_name: str = Field(default="rib-pqc-auth-service")
    version: str = Field(default="0.1.0")
    environment: Environment = Field(default="dev")

    host: str = Field(default="0.0.0.0")  # noqa: S104
    port: int = Field(default=8000, ge=1, le=65535)

    log_level: LogLevel = Field(default="info")

    sqlite_path: str = Field(default="/data/auth.sqlite")
    redis_url: str = Field(default="redis://redis:6379/0")

    crypto: CryptoConfig = Field(default_factory=CryptoConfig)
    token: TokenConfig = Field(default_factory=TokenConfig)
    argon2: Argon2Config = Field(default_factory=Argon2Config)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    idp_providers: IdpProvidersConfig = Field(default_factory=IdpProvidersConfig)

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
