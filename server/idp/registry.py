"""IdpRegistry: zentrale Plugin-Registry fuer External Identity Provider.

Story: PQC-36 (BRK-1).
Architektur-Bezug: docs/07_design.md Abschnitt 2.1 (Identity-Broker-Federation),
FR-Broker-1.

**Designprinzipien (analog crypto/registry.py PQC-21 CRY-1):**

- Plugins sind ``typing.Protocol``-Klassen mit ``@runtime_checkable``.
  Strukturelle Subtyping statt Inheritance, passt zum Plugin-Charakter.
- Provider-Namen folgen lowercase-Convention ("google", "microsoft").
- Registry kennt KEINE konkreten Implementationen. Plugin-Adapter werden
  in ``idp/plugins/`` registriert via ``init_idp_registry`` (siehe
  ``idp/registry_init.py``).
- Neue Provider (z.B. Apple in STR-2 PQC-76) brauchen nur:
  1. Neue Pydantic-Subklasse in ``config.py`` (z.B. ``AppleProviderConfig``)
  2. Plugin-Klasse in ``idp/plugins/apple.py``
  3. Registrierung in ``init_idp_registry``.

**Verwendungsbeispiel::**

    from idp.registry import IdpRegistry

    registry = IdpRegistry()
    registry.register("google", google_plugin)
    plugin = registry.get("google")
    plugin.client_id  # type: str
    plugin.scopes     # type: list[str]
    plugin.claim_mapper(token_payload)  # NotImplementedError bis BRK-4

In Tests koennen Mock-Plugins registriert werden, ohne dass echte Provider
erreichbar sein muessen.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


class RegistryError(Exception):
    """Basis-Fehler fuer alle IdP-Registry-bezogenen Probleme."""


class DuplicateProviderError(RegistryError):
    """Wird geworfen, wenn ein bereits registrierter Provider erneut registriert wird.

    Doppel-Registrierung wuerde stillschweigend ueberschreiben, was bei
    Auth-Code zu schwer auffindbaren Bugs fuehren wuerde (z.B. falscher
    Plugin fuer denselben Namen waehrend Test-vs-Prod-Mix-Up).
    """


class UnknownProviderError(RegistryError):
    """Wird geworfen, wenn ein angefragter Provider-Name nicht registriert ist.

    Story-Bezug: PQC-36 BRK-1 AC-4. Fail-fast statt None-Return, damit der
    Aufrufer (typisch BRK-2 OIDC-Code-Flow-Endpoint) den Fehler nicht
    versehentlich verschluckt.
    """


@runtime_checkable
class IdpProvider(Protocol):
    """Strukturelle Schnittstelle fuer External Identity Provider.

    Story-Bezug: PQC-36 BRK-1 AC-2. Plugin-Schnittstelle definiert:

    - ``discovery_url`` (str): OIDC-Discovery-Endpoint. BRK-2 nutzt diesen
      um authorization_endpoint/token_endpoint/jwks_uri runtime zu ziehen.
    - ``client_id`` (str): OAuth-Client-ID des Providers. Wird in der
      Authorize-URL als ``client_id``-Parameter gesendet.
    - ``scopes`` (list[str]): OIDC-Scopes-Set fuer den Authorize-Request.
      Default: ``["openid", "email", "profile"]``.
    - ``claim_mapper(payload)``: provider-spezifische Funktion die
      User-Identitaet aus dem ID-Token-Payload zieht. Stub in BRK-1,
      voll implementiert in BRK-4 (PQC-39 Identity-Normalisierung).
    - ``verify_id_token(token)``: provider-spezifische JWS-Signature-
      Validierung gegen Provider-JWKS. Stub in BRK-1, voll implementiert
      in BRK-3 (PQC-38 ID-Token-Verifikation).

    Plugins werden in PQC-40 (Google, BRK-5) und PQC-41 (Microsoft, BRK-6)
    voll ausgebaut. BRK-1 liefert nur die Schnittstelle plus Stub-Bodies.
    """

    @property
    def name(self) -> str:
        """Lowercase Provider-Name (``"google"``, ``"microsoft"``, ...)."""
        ...

    @property
    def discovery_url(self) -> str:
        """OIDC-Discovery-Endpoint-URL."""
        ...

    @property
    def client_id(self) -> str:
        """OAuth-Client-ID."""
        ...

    @property
    def scopes(self) -> list[str]:
        """Liste der angefragten OIDC-Scopes."""
        ...

    def claim_mapper(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Mappt Provider-spezifische Claims auf normalisierte User-Info.

        Voll implementiert in PQC-39 (BRK-4 Identity-Normalisierung).
        Returns: Dict mit normalisierten Feldern (z.B. external_sub, email,
        email_verified, display_name).
        """
        ...

    def verify_id_token(self, token: str) -> dict[str, Any]:
        """Verifiziert die JWS-Signature des ID-Tokens gegen Provider-JWKS.

        Voll implementiert in PQC-38 (BRK-3 ID-Token-Verifikation).
        Returns: dekodierter Token-Payload bei Erfolg.
        Raises: provider-spezifische Exceptions bei ungueltigem Token.
        """
        ...


class IdpRegistry:
    """Plugin-Registry fuer External Identity Provider.

    Story-Bezug: PQC-36 BRK-1 AC-1. Thread-safe ist sie nicht; Registrierung
    findet einmal im Lifespan-Hook statt, danach nur noch Lookups.
    """

    def __init__(self) -> None:
        self._providers: dict[str, IdpProvider] = {}

    def register(self, name: str, plugin: IdpProvider) -> None:
        """Registriert ein Plugin unter ``name``.

        Story-Bezug: PQC-36 BRK-1 AC-1.

        Raises:
            DuplicateProviderError: wenn ``name`` bereits registriert ist.
        """
        if name in self._providers:
            msg = f"Provider already registered: {name!r}"
            raise DuplicateProviderError(msg)
        self._providers[name] = plugin

    def get(self, name: str) -> IdpProvider:
        """Liefert das Plugin zu ``name``.

        Story-Bezug: PQC-36 BRK-1 AC-1, AC-4.

        Raises:
            UnknownProviderError: wenn ``name`` nicht registriert ist.
        """
        plugin = self._providers.get(name)
        if plugin is None:
            registered = sorted(self._providers.keys())
            msg = (
                f"Unknown provider: {name!r}. "
                f"Registered providers: {registered}"
            )
            raise UnknownProviderError(msg)
        return plugin

    def supported(self) -> list[str]:
        """Liefert die Liste aller registrierten Provider-Namen (sortiert)."""
        return sorted(self._providers.keys())

    def __contains__(self, name: str) -> bool:
        """Erlaubt ``"google" in registry`` Idiom."""
        return name in self._providers
