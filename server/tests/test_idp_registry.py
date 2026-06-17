"""Unit-Tests fuer idp/registry.py, idp/registry_init.py und idp/plugins/*.

Story: PQC-36 (BRK-1), Acceptance Criteria AC-1..AC-5.

Deckt ab:
- Happy-Path: register plus get fuer Provider
- Duplikat-Erkennung wirft DuplicateProviderError
- Get-mit-unbekanntem-Namen wirft UnknownProviderError
- Protocol-Konformitaet: GoogleIdpPlugin und MicrosoftIdpPlugin satisfy IdpProvider
- Plugin-Stubs werfen NotImplementedError fuer claim_mapper + verify_id_token
- ``init_idp_registry`` registriert nur enabled=True Provider
- Disabled Provider werden nicht registriert
- Microsoft tenant_id wird in issuer/discovery_url-Property komponiert

Kein Netzwerk-Zugriff, keine echten OAuth-Calls. Alle Tests laufen offline.
"""

from __future__ import annotations

import pytest

from config import (
    GoogleProviderConfig,
    IdpProvidersConfig,
    MicrosoftProviderConfig,
    Settings,
)
from idp.plugins.google import GoogleIdpPlugin
from idp.plugins.microsoft import MicrosoftIdpPlugin
from idp.registry import (
    DuplicateProviderError,
    IdpProvider,
    IdpRegistry,
    RegistryError,
    UnknownProviderError,
)
from idp.registry_init import IdpConfigError, init_idp_registry

# ---------------------------------------------------------------------------
# IdpRegistry: Happy-Path (AC-1)
# ---------------------------------------------------------------------------


def _google_plugin(enabled: bool = True, client_id: str = "g-id") -> GoogleIdpPlugin:
    return GoogleIdpPlugin(
        GoogleProviderConfig(
            enabled=enabled,
            client_id=client_id,
            client_secret="g-secret",
            redirect_uri="http://localhost:8000/auth/google/callback",
        )
    )


def _microsoft_plugin(
    enabled: bool = True,
    tenant_id: str = "tenant-abc",
) -> MicrosoftIdpPlugin:
    return MicrosoftIdpPlugin(
        MicrosoftProviderConfig(
            enabled=enabled,
            client_id="m-id",
            client_secret="m-secret",
            redirect_uri="http://localhost:8000/auth/microsoft/callback",
            tenant_id=tenant_id,
        )
    )


def test_register_and_get_google_happy_path() -> None:
    registry = IdpRegistry()
    plugin = _google_plugin()

    registry.register("google", plugin)

    assert registry.get("google") is plugin
    assert registry.supported() == ["google"]
    assert "google" in registry


def test_register_and_get_microsoft_happy_path() -> None:
    registry = IdpRegistry()
    plugin = _microsoft_plugin()

    registry.register("microsoft", plugin)

    assert registry.get("microsoft") is plugin
    assert registry.supported() == ["microsoft"]


def test_supported_is_sorted() -> None:
    registry = IdpRegistry()
    registry.register("microsoft", _microsoft_plugin())
    registry.register("google", _google_plugin())

    assert registry.supported() == ["google", "microsoft"]


def test_contains_returns_false_for_unknown() -> None:
    registry = IdpRegistry()
    assert "google" not in registry


# ---------------------------------------------------------------------------
# IdpRegistry: Fehlerfaelle (AC-1, AC-4)
# ---------------------------------------------------------------------------


def test_register_duplicate_raises() -> None:
    registry = IdpRegistry()
    registry.register("google", _google_plugin())

    with pytest.raises(DuplicateProviderError) as exc:
        registry.register("google", _google_plugin())
    assert "google" in str(exc.value)


def test_get_unknown_raises() -> None:
    registry = IdpRegistry()
    with pytest.raises(UnknownProviderError) as exc:
        registry.get("apple")
    assert "apple" in str(exc.value)


def test_get_unknown_message_lists_registered_providers() -> None:
    """Operationaler Hint: Fehlertext soll zeigen welche Provider registriert sind."""
    registry = IdpRegistry()
    registry.register("google", _google_plugin())

    with pytest.raises(UnknownProviderError) as exc:
        registry.get("apple")
    assert "google" in str(exc.value)


def test_errors_share_registry_error_base() -> None:
    """Sammel-Catch via RegistryError soll funktionieren (Aufrufer-Convenience)."""
    assert issubclass(DuplicateProviderError, RegistryError)
    assert issubclass(UnknownProviderError, RegistryError)


# ---------------------------------------------------------------------------
# Protocol-Konformitaet (AC-2)
# ---------------------------------------------------------------------------


def test_google_plugin_satisfies_idp_protocol() -> None:
    plugin = _google_plugin()
    assert isinstance(plugin, IdpProvider)


def test_microsoft_plugin_satisfies_idp_protocol() -> None:
    plugin = _microsoft_plugin()
    assert isinstance(plugin, IdpProvider)


def test_google_plugin_properties() -> None:
    plugin = _google_plugin(client_id="my-google-id")
    assert plugin.name == "google"
    assert plugin.client_id == "my-google-id"
    assert plugin.discovery_url.endswith("/.well-known/openid-configuration")
    assert "openid" in plugin.scopes
    assert plugin.issuer == "https://accounts.google.com"


def test_microsoft_plugin_properties() -> None:
    plugin = _microsoft_plugin(tenant_id="my-tenant")
    assert plugin.name == "microsoft"
    assert plugin.tenant_id == "my-tenant"
    assert plugin.discovery_url == (
        "https://login.microsoftonline.com/my-tenant"
        "/v2.0/.well-known/openid-configuration"
    )
    assert plugin.issuer == "https://login.microsoftonline.com/my-tenant/v2.0"


# ---------------------------------------------------------------------------
# Plugin-Stubs: NotImplementedError (AC-2)
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# init_idp_registry (AC-3)
# ---------------------------------------------------------------------------


def _settings_with_providers(
    *,
    google_enabled: bool,
    microsoft_enabled: bool,
    microsoft_tenant: str = "tenant-xyz",
) -> Settings:
    """Baut ein Settings-Objekt mit gewuenschten Provider-Flags.

    Wir konstruieren das Settings-Objekt direkt statt via Env, weil das
    isolation gegen Test-Environment garantiert.
    """
    return Settings(
        idp_providers=IdpProvidersConfig(
            google=GoogleProviderConfig(
                enabled=google_enabled,
                client_id="g-id",
                client_secret="g-secret",
                redirect_uri="http://localhost:8000/auth/google/callback",
            ),
            microsoft=MicrosoftProviderConfig(
                enabled=microsoft_enabled,
                client_id="m-id",
                client_secret="m-secret",
                redirect_uri="http://localhost:8000/auth/microsoft/callback",
                tenant_id=microsoft_tenant,
            ),
        )
    )


def test_init_registers_both_when_both_enabled() -> None:
    settings = _settings_with_providers(google_enabled=True, microsoft_enabled=True)
    registry = init_idp_registry(settings)

    assert registry.supported() == ["google", "microsoft"]
    assert isinstance(registry.get("google"), GoogleIdpPlugin)
    assert isinstance(registry.get("microsoft"), MicrosoftIdpPlugin)


def test_init_skips_disabled_google() -> None:
    settings = _settings_with_providers(google_enabled=False, microsoft_enabled=True)
    registry = init_idp_registry(settings)

    assert registry.supported() == ["microsoft"]
    assert "google" not in registry


def test_init_skips_disabled_microsoft() -> None:
    settings = _settings_with_providers(google_enabled=True, microsoft_enabled=False)
    registry = init_idp_registry(settings)

    assert registry.supported() == ["google"]
    assert "microsoft" not in registry


def test_init_with_all_disabled_yields_empty_registry() -> None:
    """AC-5: Empty-Registry-Edge-Case soll funktionieren, ohne zu crashen."""
    settings = _settings_with_providers(google_enabled=False, microsoft_enabled=False)
    registry = init_idp_registry(settings)

    assert registry.supported() == []
    with pytest.raises(UnknownProviderError):
        registry.get("google")


def test_init_propagates_microsoft_tenant_to_plugin() -> None:
    settings = _settings_with_providers(
        google_enabled=False,
        microsoft_enabled=True,
        microsoft_tenant="my-fancy-tenant",
    )
    registry = init_idp_registry(settings)
    plugin = registry.get("microsoft")
    assert isinstance(plugin, MicrosoftIdpPlugin)
    assert plugin.tenant_id == "my-fancy-tenant"
    assert "my-fancy-tenant" in plugin.discovery_url


# ---------------------------------------------------------------------------
# F-058 Fix (in PQC-37 BRK-2): Misconfig-Validation at startup
# ---------------------------------------------------------------------------


def test_init_raises_when_google_enabled_without_client_id() -> None:
    settings = Settings(
        idp_providers=IdpProvidersConfig(
            google=GoogleProviderConfig(
                enabled=True,
                client_id="",
                client_secret="g-secret",
                redirect_uri="http://localhost:8000/auth/google/callback",
            ),
        )
    )
    with pytest.raises(IdpConfigError) as exc:
        init_idp_registry(settings)
    assert "google" in str(exc.value)
    assert "client_id" in str(exc.value)


def test_init_raises_when_google_enabled_without_client_secret() -> None:
    settings = Settings(
        idp_providers=IdpProvidersConfig(
            google=GoogleProviderConfig(
                enabled=True,
                client_id="g-id",
                client_secret="",
                redirect_uri="http://localhost:8000/auth/google/callback",
            ),
        )
    )
    with pytest.raises(IdpConfigError) as exc:
        init_idp_registry(settings)
    assert "client_secret" in str(exc.value)


def test_init_raises_when_google_enabled_without_redirect_uri() -> None:
    settings = Settings(
        idp_providers=IdpProvidersConfig(
            google=GoogleProviderConfig(
                enabled=True,
                client_id="g-id",
                client_secret="g-secret",
                redirect_uri="",
            ),
        )
    )
    with pytest.raises(IdpConfigError) as exc:
        init_idp_registry(settings)
    assert "redirect_uri" in str(exc.value)


def test_init_raises_when_microsoft_enabled_without_tenant_id() -> None:
    """tenant_id ist fuer Microsoft Single-Tenant kritisch (sonst falscher Issuer)."""
    settings = Settings(
        idp_providers=IdpProvidersConfig(
            microsoft=MicrosoftProviderConfig(
                enabled=True,
                client_id="m-id",
                client_secret="m-secret",
                redirect_uri="http://localhost:8000/auth/microsoft/callback",
                tenant_id="",
            ),
        )
    )
    with pytest.raises(IdpConfigError) as exc:
        init_idp_registry(settings)
    assert "microsoft" in str(exc.value)
    assert "tenant_id" in str(exc.value)


def test_init_error_lists_all_missing_fields_for_provider() -> None:
    """Operationaler Hint: Fehlermeldung zeigt alle leeren Felder auf einmal."""
    settings = Settings(
        idp_providers=IdpProvidersConfig(
            google=GoogleProviderConfig(
                enabled=True,
                client_id="",
                client_secret="",
                redirect_uri="",
            ),
        )
    )
    with pytest.raises(IdpConfigError) as exc:
        init_idp_registry(settings)
    msg = str(exc.value)
    assert "client_id" in msg
    assert "client_secret" in msg
    assert "redirect_uri" in msg


def test_idp_config_error_is_registry_error() -> None:
    """IdpConfigError soll via RegistryError-Base abfangbar sein."""
    assert issubclass(IdpConfigError, RegistryError)


def test_init_does_not_validate_disabled_provider() -> None:
    """Disabled-Provider duerfen Stub-Configs haben ohne dass es kracht."""
    settings = Settings(
        idp_providers=IdpProvidersConfig(
            google=GoogleProviderConfig(
                enabled=False,
                client_id="",
                client_secret="",
                redirect_uri="",
            ),
            microsoft=MicrosoftProviderConfig(
                enabled=False,
                tenant_id="",
            ),
        )
    )
    # darf nicht raisen
    registry = init_idp_registry(settings)
    assert registry.supported() == []


# ---------------------------------------------------------------------------
# Plugin claim_mapper Voll-Impl (PQC-39 AC-3)
# ---------------------------------------------------------------------------


def test_google_claim_mapper_happy_path() -> None:
    plugin = _google_plugin()
    result = plugin.claim_mapper({
        "sub": "1234567890",
        "email": "alice@example.com",
        "email_verified": True,
        "name": "Alice",
        "given_name": "Alice",
    })
    assert result.external_sub == "1234567890"
    assert result.email == "alice@example.com"
    assert result.email_verified is True
    assert result.display_name == "Alice"


def test_google_claim_mapper_email_unverified() -> None:
    plugin = _google_plugin()
    result = plugin.claim_mapper({
        "sub": "x",
        "email": "x@example.com",
        "email_verified": False,
    })
    assert result.email_verified is False


def test_google_claim_mapper_missing_sub_raises() -> None:
    plugin = _google_plugin()
    with pytest.raises(ValueError):
        plugin.claim_mapper({"email": "x@example.com"})


def test_google_claim_mapper_fallback_given_name() -> None:
    plugin = _google_plugin()
    result = plugin.claim_mapper({
        "sub": "x",
        "given_name": "GivenOnly",
    })
    assert result.display_name == "GivenOnly"


def test_microsoft_claim_mapper_happy_path_with_oid() -> None:
    plugin = _microsoft_plugin()
    result = plugin.claim_mapper({
        "oid": "tenant-stable-oid",
        "email": "bob@example.com",
        "name": "Bob",
        "tid": "tenant-abc",
    })
    assert result.external_sub == "tenant-stable-oid"
    assert result.email == "bob@example.com"
    assert result.email_verified is True
    assert result.display_name == "Bob"


def test_microsoft_claim_mapper_preferred_username_fallback() -> None:
    plugin = _microsoft_plugin()
    result = plugin.claim_mapper({
        "oid": "x",
        "preferred_username": "user@upn.example",
    })
    assert result.email == "user@upn.example"
    assert result.email_verified is True


def test_microsoft_claim_mapper_no_email_unverified() -> None:
    plugin = _microsoft_plugin()
    result = plugin.claim_mapper({"oid": "x"})
    assert result.email is None
    assert result.email_verified is False


def test_microsoft_claim_mapper_missing_oid_raises() -> None:
    plugin = _microsoft_plugin()
    with pytest.raises(ValueError):
        plugin.claim_mapper({"sub": "should-be-oid"})
