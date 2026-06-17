# Evidence: PQC-36 BRK-1 External-IdP-Registry

**Story:** PQC-36 BRK-1 External-IdP-Registry (5 SP)
**Sprint:** 2
**Status:** Done
**Datum:** 2026-06-17

## Ziel und Acceptance Criteria

Foundation-Story fuer die externe Identity-Provider-Federation. Nach BRK-0
(PQC-84, OAuth-App-Setup) liefert BRK-1 die zentrale Registry-Schnittstelle
plus Plugin-Adapter-Skeleton fuer Google und Microsoft. Sie ist die Voraus-
setzung fuer alle nachfolgenden BRK-Stories (BRK-2 OIDC-Code-Flow,
BRK-3 ID-Token-Verify, BRK-4 Identity-Normalisierung, BRK-5/6 Google/MS-Voll-
Implementation).

- **AC-1:** Registry-API erlaubt register und get pro Provider-Name.
- **AC-2:** Plugin-Schnittstelle definiert (Discovery-URL, Client-ID, Scopes,
  claim_mapper, verify_id_token).
- **AC-3:** Bootstrap aus Pydantic-Settings registriert nur enabled=True
  Provider.
- **AC-4:** Fail-Fast: Doppelregistrierung und Unbekannter-Provider werfen
  dedizierte Errors.
- **AC-5:** Pattern ist erweiterbar (neue Provider wie Apple in STR-2 PQC-76
  ohne Eingriff in den Registry-Core).

Alle ACs erfuellt.

## Architektur-Entscheidungen

| Entscheidung | Begruendung |
| --- | --- |
| Modul `server/idp/` analog `server/crypto/` | Konsistenter Codebase-Aufbau, niedrige kognitive Last beim Verstehen, Wiederverwendung des bekannten Plugin-Patterns aus PQC-21 CRY-1. |
| `typing.Protocol` mit `@runtime_checkable` | Strukturelles Subtyping passt zum Plugin-Charakter ohne Inheritance-Zwang, ermoeglicht Mock-Plugins in Tests via `isinstance`. |
| Stubs mit `NotImplementedError` fuer `claim_mapper` + `verify_id_token` | Foundation-Story liefert Schnittstelle, voll-Implementation in PQC-39 (BRK-4) und PQC-38 (BRK-3). Pattern analog PlaceholderKEM in PQC-21. |
| Microsoft `issuer`/`discovery_url` als Property, nicht Field | Tenant-spezifisch komponiert aus `tenant_id`, vermeidet Daten-Duplikation und Drift zwischen `tenant_id` und URL. |
| `IdpProvidersConfig` als Container statt flacher Settings-Felder | Klare Pydantic-Struktur erlaubt nested ENV-Variablen (RIB_IDP_PROVIDERS__GOOGLE__CLIENT_ID), entkoppelt von BaseSettings-Subclassing. |

## Implementierte Files

| Pfad | Zweck |
| --- | --- |
| `server/idp/__init__.py` | Modul-Docstring mit Story-Mapping (BRK-1..BRK-6). |
| `server/idp/registry.py` | RegistryError + DuplicateProviderError + UnknownProviderError + IdpProvider Protocol + IdpRegistry. |
| `server/idp/plugins/__init__.py` | Modul-Docstring. |
| `server/idp/plugins/google.py` | GoogleIdpPlugin (passive Properties voll, claim_mapper + verify_id_token als NotImplementedError-Stubs). |
| `server/idp/plugins/microsoft.py` | MicrosoftIdpPlugin analog Google, mit tenant_id-Property. |
| `server/idp/registry_init.py` | `init_idp_registry(settings)` Bootstrap-Funktion. |
| `server/config.py` | BaseProviderConfig + GoogleProviderConfig + MicrosoftProviderConfig + IdpProvidersConfig hinzugefuegt; Settings.idp_providers Feld. |
| `server/main.py` | Lifespan-Hook erweitert: `app.state.idp_registry = init_idp_registry(settings)`. |
| `server/Dockerfile` | `COPY idp ./idp` hinzugefuegt. |
| `server/pyproject.toml` | `idp` in `only-include` und in `mypy.files`. |
| `server/tests/test_idp_registry.py` | 21 Tests, siehe Test-Sektion. |

## Tests

Suite: `tests/test_idp_registry.py`, 21 Tests, alle gruen.

Test-Cluster:
- IdpRegistry Happy-Path: register, get, supported, __contains__, sortierung.
- Fehlerfaelle: Duplicate, Unknown, Fehlertext listet registrierte Provider,
  RegistryError-Base-Hierarchie.
- Protocol-Konformitaet: isinstance-Check fuer beide Plugins gegen
  IdpProvider Protocol.
- Plugin-Properties: discovery_url, client_id, scopes, issuer, tenant_id
  korrekt aus Config.
- Stub-Verhalten: claim_mapper und verify_id_token werfen NotImplementedError
  mit Story-Hint (PQC-38 / PQC-39).
- init_idp_registry: beide enabled, einer disabled, beide disabled, Microsoft
  tenant_id-Propagation.

```
============================== 21 passed in 0.25s ==============================
```

Volle Suite-Regressions-Check: 125 passed, 4 skipped (liboqs-Sandbox), keine
Regressions.

## Code-Review und Findings

Closing-Review nach Standard-Prozedur (Phase 1..7, 10 Kategorien, 4
Severity-Stufen). Erkenntnisse aus WebSearch fuer aktuelle 2026-Patterns:

- OIDC-Discovery via `.well-known/openid-configuration` ist Standard, von
  uns bereits abgebildet.
- ID-Token-Validierung muss iss + aud + Signature pruefen, voll-Implementation
  in PQC-38 BRK-3 vorgesehen.
- Multi-Provider-Broker normalisiert Profile auf einheitliches Schema; bei uns
  in PQC-39 BRK-4 vorgesehen.

Findings:

| ID | Severity | Beschreibung | Tracking |
| --- | --- | --- | --- |
| F-057 | (close) | Stub idp_providers.* in config.yaml -> echte Pydantic-Klassen | resolved durch diese Story |
| F-058 | Should | `init_idp_registry` validiert nicht, dass `enabled=True` Provider client_id + client_secret + redirect_uri befuellt haben. Fail-fast at startup besser als Runtime-Fehler im OAuth-Flow. | Tier 2 docs/13_deferred_findings.md, Trigger: vor PQC-37 BRK-2 |
| F-059 | May | scopes-Default enthaelt kein `offline_access`. Wenn Refresh-Tokens in BRK-2 gebraucht werden, muss das per Provider ergaenzt werden. | Tier 2, Trigger: vor PQC-37 wenn Refresh-Strategie entschieden |
| F-060 | May | server/README.md erwaehnt noch nicht das idp/-Modul und die Plugin-Architektur. | Tier 2, Sprint 4 Doku-Polish |
| F-061 | Info | `name` ist im IdpProvider-Protocol als Property markiert, beide Plugins liefern es als Klassen-Attribut (str). isinstance-Check ist gruen via strukturelles Subtyping. Kein Action-Item. | Tier 2 Info-Eintrag |

Keine Must-Fixes. Alle Findings werden via Tier 2 (deferred_findings.md) plus
Story-Trigger getrackt. In-Story-Fix erfolgt nicht (Scope-Disziplin: BRK-1 ist
Foundation, F-058 ist sinnvoll erst wenn BRK-2 die Validierung tatsaechlich
verwendet).

## Verifikation

- `pytest tests/test_idp_registry.py` 21/21 gruen.
- `pytest tests/` 125/125 gruen (4 erwartete Skips liboqs).
- `ruff check idp/ tests/test_idp_registry.py` All checks passed.
- Smoke-Test Settings-Load mit IdP-Provider-Config: import + Settings()
  Konstruktion ohne Fehler.

## Story-Aufwand

- Story-Points: 5
- Tatsaechliche Zeit: **30 Minuten** (Implementation + Tests + Review +
  Evidence). Worklog in Jira eingetragen.
- AI-Multiplier-Beobachtung: Pattern-Replikation aus PQC-21 CRY-1 (crypto/
  Modul) hat Implementations-Zeit massiv verkuerzt. 5 SP in 0.5h = sehr
  hoher Multiplier, getrieben durch Strukturanalogie zur bestehenden
  CryptoRegistry plus klar definierten Stubs ohne JWKS/Token-Logik.

## Follow-Up

Naechste BRK-Story: PQC-42 BRK-7 CSRF/State+Redis (2 SP) ODER direkt
PQC-37 BRK-2 OIDC Code Flow PKCE (8 SP). Entscheidung gemeinsam mit User.
