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


class KeyEntry(BaseModel):
    """Pfade fuer ein einzelnes Signing-Keypair (PQC-34 TOK-3)."""

    private_key_path: str
    public_key_path: str


class SignatureConfig(BaseModel):
    supported: list[str] = Field(default_factory=lambda: ["ML-DSA-65"])
    default: str = Field(default="ML-DSA-65")
    # Single-Key-Felder (Sprint 1, Backward-Compat).
    private_key_path: str = Field(default="/data/keys/auth_signing_key.bin")
    public_key_path: str = Field(default="/data/keys/auth_signing_key.pub")
    allow_autogen_in_dev: bool = Field(default=False)
    signing_kid: str = Field(default="auth-signing-key-v1")
    # Multi-Key-Felder (PQC-34 TOK-3): wenn ``keys`` gesetzt sind, wird
    # daraus ``verifying_keys_by_kid`` gebaut; sonst Fallback auf das
    # Single-Key-Setup oben.
    # ``active_kid`` ist der Schluessel fuer Token-Signierung. Wenn None,
    # wird ``signing_kid`` genutzt (Backward-Compat).
    active_kid: str | None = Field(default=None)
    keys: dict[str, KeyEntry] = Field(default_factory=dict)

    def get_active_kid(self) -> str:
        """Returns active_kid oder Fallback auf signing_kid."""
        return self.active_kid or self.signing_kid

    def get_effective_keys(self) -> dict[str, KeyEntry]:
        """Returns Multi-Key-Dict, mit Backwards-Compat-Fallback.

        Wenn ``keys`` leer ist, wird ein Default-Eintrag aus
        ``signing_kid`` + ``private_key_path`` + ``public_key_path``
        konstruiert (Sprint-1-Behavior beibehalten).
        """
        if self.keys:
            return self.keys
        return {
            self.signing_kid: KeyEntry(
                private_key_path=self.private_key_path,
                public_key_path=self.public_key_path,
            ),
        }


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
    allowed_methods: list[str] = Field(default_factory=lambda: ["GET", "POST", "OPTIONS"])
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


class SessionConfig(BaseModel):
    """PQ-Session-Konfiguration (Stories PQC-48 SES-3, PQC-46 SES-1).

    - ``ttl_seconds``: TTL fuer Session-Record im Redis. Design 5.2 Default 900.
      Untergrenze 60 (Test-Friendly), Obergrenze 86400 (24h, Best-Practice).
    - ``session_redis_db``: Separate Redis-DB-Nummer fuer den Session-Store
      (Default 3), getrennt von Rate-Limit (1), OIDC-State (2) und Allgemein (0).
    - ``replay_redis_db``: Separate Redis-DB-Nummer fuer Nonce-Replay-Tracking
      (PQC-53 DCH-4, Default 4). Eigener Namespace fuer die Single-Use-Eintraege
      via SET NX EX, getrennt von session_records.
    - ``hkdf_info``: Domain-Separation-Bytes fuer HKDF-Session-Key-Ableitung
      (PQC-47 SES-2). Default ``b"app-session-v1"``.
    """

    ttl_seconds: int = Field(default=900, ge=60, le=86400)
    session_redis_db: int = Field(default=3, ge=0, le=15)
    replay_redis_db: int = Field(default=4, ge=0, le=15)
    hkdf_info: bytes = Field(default=b"app-session-v1")


class OidcConfig(BaseModel):
    """OIDC-Federation-Konfiguration (Stories PQC-37 BRK-2, PQC-42 BRK-7).

    - ``state_ttl_seconds``: TTL fuer State+PKCE-Eintrag im Redis (BRK-7 AC-5
      sagt 10 Min Default, Best-Practice-2026 RFC 9700).
    - ``discovery_cache_ttl_seconds``: TTL fuer Provider-Discovery-Doc plus
      JWKS-Cache. 24h ist 2026-Standard, deckt JWKS-Rotation-Frequency ab
      ohne pro Login-Flow neu zu fetchen.
    - ``state_redis_db``: Separate Redis-DB-Nummer fuer den State-Store
      (Default 2), getrennt von Rate-Limit-DB (1) und Allgemein (0).
    - ``http_timeout_seconds``: Timeout fuer IdP-HTTP-Calls
      (Discovery + Token-Exchange + JWKS).
    """

    state_ttl_seconds: int = Field(default=600, ge=60, le=3600)
    discovery_cache_ttl_seconds: int = Field(default=86400, ge=3600)
    state_redis_db: int = Field(default=2, ge=0, le=15)
    http_timeout_seconds: float = Field(default=10.0, gt=0)
    # PQC-38 BRK-3: JWKS-Cache fuer ID-Token-Verify. Kuerzer als Discovery-Cache
    # weil Provider-Keys haeufiger rotieren (Best Practice 2026).
    jwks_cache_ttl_seconds: int = Field(default=3600, ge=300)
    # PQC-38 BRK-3: Leeway fuer exp-Check (Clock-Skew zwischen Auth-Service und IdP).
    # Analog token.exp_leeway_seconds aus PQC-32 TOK-1.
    id_token_exp_leeway_seconds: int = Field(default=30, ge=0, le=300)


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
    oidc: OidcConfig = Field(default_factory=OidcConfig)
    session: SessionConfig = Field(default_factory=SessionConfig)

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
