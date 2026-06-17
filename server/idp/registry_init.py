"""Bootstrap-Funktion fuer die IdpRegistry.

Stories:
- PQC-36 (BRK-1): Init liest config.idp_providers und registriert
  enabled=True Provider.
- PQC-37 (BRK-2) + F-058 Fix: Misconfig-Validation. Wenn ein Provider
  enabled=True ist aber client_id, client_secret, redirect_uri oder
  Microsoft-tenant_id leer sind, wird ein ``IdpConfigError`` geworfen
  (Fail-Fast at startup statt unleserlicher 401 zur Laufzeit).

Designprinzip (analog ``crypto/registry_init.py`` aus PQC-21):
- Konfiguration treibt Verhalten, nicht Hardcoded-Listen.
- Disabled Provider werden komplett uebersprungen (kein Object im Memory).
- Doppelregistrierung wirft DuplicateProviderError (Fail-Fast).
- Misconfig wirft IdpConfigError (Fail-Fast).
"""

from __future__ import annotations

import logging

from config import (
    BaseProviderConfig,
    MicrosoftProviderConfig,
    Settings,
)

from .plugins.google import GoogleIdpPlugin
from .plugins.microsoft import MicrosoftIdpPlugin
from .registry import IdpRegistry, RegistryError

logger = logging.getLogger(__name__)


class IdpConfigError(RegistryError):
    """Wird geworfen, wenn ein enabled-Provider unvollstaendig konfiguriert ist.

    Story-Bezug: F-058 Fix in PQC-37 BRK-2.

    Beispiel: ``RIB_IDP_PROVIDERS__GOOGLE__ENABLED=true`` aber
    ``RIB_IDP_PROVIDERS__GOOGLE__CLIENT_SECRET`` nicht gesetzt -> Fehler
    bei Service-Start statt unleserlicher 401 beim ersten OAuth-Flow.
    """


_REQUIRED_BASE_FIELDS: tuple[str, ...] = ("client_id", "client_secret", "redirect_uri")


def _check_provider_credentials(name: str, config: BaseProviderConfig) -> list[str]:
    """Liefert eine Liste leerer Pflichtfelder fuer den Provider ``name``.

    Returns:
        Liste der Feldnamen die leer (``""``) oder ``None`` sind. Leere Liste
        bedeutet alles ist gesetzt.
    """
    del name
    missing: list[str] = []
    for field in _REQUIRED_BASE_FIELDS:
        value = getattr(config, field, "")
        if not value:
            missing.append(field)
    if isinstance(config, MicrosoftProviderConfig) and not config.tenant_id:
        missing.append("tenant_id")
    return missing


def init_idp_registry(settings: Settings) -> IdpRegistry:
    """Erzeugt und initialisiert die IdpRegistry aus den Settings.

    Story-Bezug: PQC-36 BRK-1 AC-3 plus F-058 Fix in PQC-37 BRK-2.

    Args:
        settings: geladene Settings-Instanz mit ``idp_providers`` Sektion.

    Returns:
        IdpRegistry mit allen ``enabled=True`` Providern registriert.

    Raises:
        IdpConfigError: wenn ein enabled-Provider unvollstaendig
            konfiguriert ist.
    """
    registry = IdpRegistry()
    providers_config = settings.idp_providers

    if providers_config.google.enabled:
        missing = _check_provider_credentials("google", providers_config.google)
        if missing:
            msg = (
                f"IdP provider 'google' is enabled but missing required "
                f"credential fields: {missing}. Set them via env vars "
                f"RIB_IDP_PROVIDERS__GOOGLE__<FIELD>."
            )
            raise IdpConfigError(msg)
        plugin = GoogleIdpPlugin(providers_config.google)
        registry.register("google", plugin)
        logger.info("Registered IdP provider: google")
    else:
        logger.debug("IdP provider 'google' disabled in config, skipping")

    if providers_config.microsoft.enabled:
        missing = _check_provider_credentials("microsoft", providers_config.microsoft)
        if missing:
            msg = (
                f"IdP provider 'microsoft' is enabled but missing required "
                f"credential fields: {missing}. Set them via env vars "
                f"RIB_IDP_PROVIDERS__MICROSOFT__<FIELD>."
            )
            raise IdpConfigError(msg)
        plugin = MicrosoftIdpPlugin(providers_config.microsoft)
        registry.register("microsoft", plugin)
        logger.info(
            "Registered IdP provider: microsoft (tenant_id=%s)",
            providers_config.microsoft.tenant_id,
        )
    else:
        logger.debug("IdP provider 'microsoft' disabled in config, skipping")

    logger.info(
        "IdpRegistry initialized with providers: %s",
        registry.supported(),
    )
    return registry
