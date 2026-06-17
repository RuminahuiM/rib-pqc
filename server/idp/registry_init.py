"""Bootstrap-Funktion fuer die IdpRegistry.

Story: PQC-36 (BRK-1).

Liest aus ``config.idp_providers`` welche Provider als ``enabled=True`` markiert
sind und registriert genau diese in der ``IdpRegistry``. Aufgerufen vom
Lifespan-Hook in ``main.py``.

Designprinzip (analog ``crypto/registry_init.py`` aus PQC-21):
- Konfiguration treibt Verhalten, nicht Hardcoded-Listen.
- Disabled Provider werden komplett uebersprungen (kein Object im Memory).
- Doppelregistrierung wirft DuplicateProviderError (Fail-Fast).
"""

from __future__ import annotations

import logging

from config import Settings

from .plugins.google import GoogleIdpPlugin
from .plugins.microsoft import MicrosoftIdpPlugin
from .registry import IdpRegistry

logger = logging.getLogger(__name__)


def init_idp_registry(settings: Settings) -> IdpRegistry:
    """Erzeugt und initialisiert die IdpRegistry aus den Settings.

    Story-Bezug: PQC-36 BRK-1 AC-3.

    Args:
        settings: geladene Settings-Instanz mit ``idp_providers`` Sektion.

    Returns:
        IdpRegistry mit allen ``enabled=True`` Providern registriert.

    Side-effect: Logged auf INFO welche Provider registriert wurden, auf DEBUG
    welche uebersprungen wurden.
    """
    registry = IdpRegistry()
    providers_config = settings.idp_providers

    if providers_config.google.enabled:
        plugin = GoogleIdpPlugin(providers_config.google)
        registry.register("google", plugin)
        logger.info("Registered IdP provider: google")
    else:
        logger.debug("IdP provider 'google' disabled in config, skipping")

    if providers_config.microsoft.enabled:
        plugin = MicrosoftIdpPlugin(providers_config.microsoft)
        registry.register("microsoft", plugin)
        logger.info(
            "Registered IdP provider: microsoft (tenant_id=%s)",
            providers_config.microsoft.tenant_id or "<unset>",
        )
    else:
        logger.debug("IdP provider 'microsoft' disabled in config, skipping")

    logger.info(
        "IdpRegistry initialized with providers: %s",
        registry.supported(),
    )
    return registry
