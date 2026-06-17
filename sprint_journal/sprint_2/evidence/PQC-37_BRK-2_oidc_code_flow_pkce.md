# Evidence: PQC-37 BRK-2 OIDC Authorization Code Flow mit PKCE

**Story:** PQC-37 BRK-2 OIDC Code Flow + PKCE (8 SP)
**Sprint:** 2
**Status:** Ready for Review
**Datum:** 2026-06-17

## Ziel und Acceptance Criteria

Code-zu-Token-Exchange gegen externe OIDC-Provider (Google, Microsoft) ueber
unseren Auth-Service. App startet den Authorize-Flow direkt beim IdP mit
PKCE, sendet danach `{code, code_verifier, state}` an unseren Callback-
Endpoint, der den Tausch macht und das `id_token` zurueckliefert.

**Acceptance Criteria:**

| AC | Status | Evidenz |
| --- | --- | --- |
| AC-1: Endpoint POST /auth/federated/{provider}/callback akzeptiert `{code, code_verifier}` | OK (erweitert) | `routers/auth_federated.py` Callback-Endpoint. AC-1 wurde um `state` erweitert (siehe Abweichungen). |
| AC-2: Endpoint tauscht Code gegen IdP-Tokens via Provider /token-URL | OK | `OidcExchangeService.exchange_code` + Tests `test_exchange_code_happy_path` plus `test_exchange_code_sends_correct_form_payload`. |
| AC-3: PKCE durchgehend (kein client_secret in App, code_verifier aus App-Request) | OK | Server holt client_secret aus Settings/ENV, leitet code_verifier App-side weiter. |
| AC-4: Tausch-Fehler -> 400 Bad Request mit Error-Body | OK | Tests `test_callback_idp_invalid_grant_returns_400`, `test_exchange_code_400_returns_code_exchange_error`. |
| AC-5: Erfolgreicher Tausch liefert ID-Token zur BRK-3-Weiterverarbeitung | OK | `CallbackResponse` enthaelt `id_token` + `access_token` + `expires_in`. |

## Abweichungen von der Original-Spec

**AC-1 um `state`-Param erweitert:** RFC 9700 (OAuth 2.0 Security BCP 2026)
verlangt State-Validierung fuer CSRF-Schutz. Das war urspruenglich
PQC-42 BRK-7 vorbehalten, aber bei Reihenfolge BRK-2-first muss BRK-2 die
inline State-Logik mitliefern. BRK-7 wird sie spaeter in eigene Service-
Klasse extrahieren und zusaetzliche Tests fuer TTL-Expiry, Replay-Protection
etc. ergaenzen.

**Zusaetzlicher Endpoint POST /authorize:** Spec hatte nur den Callback-
Endpoint. Damit der Flow voll funktioniert (Server-side State-Gen),
brauchten wir auch einen Authorize-Start-Endpoint. Der baut die
Authorize-URL inkl. State + PKCE-Challenge.

**F-058 inline gefixt:** Misconfig-Validation in `init_idp_registry` (Fail-
Fast wenn enabled-Provider client_id/secret/redirect_uri leer).

## Architektur-Entscheidungen (Senior-Decisions)

| Entscheidung | Begruendung |
| --- | --- |
| Inline Redis-State-Storage in BRK-2, BRK-7 extrahiert in Service | Schon ab BRK-2 production-grade, kein In-Memory-Fallback. Redis-Client steht via PQC-83 bereits zur Verfuegung. |
| Module: `routers/auth_federated.py` + `services/oidc_state_service.py` + `services/oidc_exchange_service.py` | Konsistent mit bestehender token_service-Konvention. Klare Test-Layer-Trennung. |
| Lazy Discovery-Doc-Cache (24h TTL) | RFC 9700 BCP. Schlanker als Eager-Fetch im Lifespan, robust bei Provider-Downtime. |
| Server-side State-Gen via `secrets.token_urlsafe(32)` | 256 bit Entropie, deutlich mehr als RFC 9700-Minimum (128 bit). |
| One-Shot via Redis DEL VOR Payload-Parsing | Selbst bei Crash mid-flight kann kein zweites consume durchkommen (Replay-Schutz). |
| `client_secret_post`-Auth (RFC 6749 Section 2.3.1) | Expliziter als Basic-Auth, von Google + Microsoft akzeptiert. |
| Dependencies: `fakeredis` + `respx` + `httpx[socks]` | fakeredis fuer State-Tests, respx fuer httpx-Mocking, httpx[socks] fuer korrekte Transport-Layer-Init in Sandbox. |

## Implementierte Files

| Pfad | Zweck |
| --- | --- |
| `server/config.py` | `OidcConfig` (state_ttl=600s, discovery_cache_ttl=86400s, state_redis_db=2, http_timeout=10s). Settings.oidc Feld. |
| `server/idp/registry_init.py` | F-058 Fix: `IdpConfigError` + `_check_provider_credentials`. |
| `server/services/oidc_state_service.py` | `OidcStateService` mit Redis, `StateEntry`, `StateNotFoundError`. |
| `server/services/oidc_exchange_service.py` | `OidcExchangeService` mit httpx-Async + Discovery-Cache. `DiscoveryError`, `CodeExchangeError`, `TokenExchangeResult`. |
| `server/routers/auth_federated.py` | POST `/auth/federated/{provider}/authorize` + POST `/auth/federated/{provider}/callback`. |
| `server/main.py` | Lifespan-Hook erweitert: Redis-Client + State + Exchange Services + Router-Registration. |
| `server/pyproject.toml` | Dev-deps: fakeredis, respx. |
| `server/tests/test_idp_registry.py` | +7 F-058-Tests. |
| `server/tests/test_oidc_state_service.py` | 11 Tests. |
| `server/tests/test_oidc_exchange_service.py` | 14 Tests. |
| `server/tests/test_auth_federated_router.py` | 15 Tests. |

## Tests

```
=============================== 172 passed, 4 skipped in ~10s ================================
```

Neue Tests in BRK-2: **47** (7+11+14+15). Volle Suite **172 passed** (vorher
125), 4 erwartete Skips (liboqs-Sandbox). Ruff `All checks passed`.

Test-Cluster:
- `test_oidc_state_service.py`: Happy create+consume, One-Shot Replay-Schutz,
  Unknown-State, TTL-Expiry, Entropie-Sanity, Constructor-Validation,
  Malformed-Payload.
- `test_oidc_exchange_service.py`: Discovery happy + cache + http-error +
  invalid-json + missing-token-endpoint + network-error. Exchange happy +
  form-payload + 400 + 500 + missing-id-token + malformed + network-error.
- `test_auth_federated_router.py`: Authorize happy + PKCE + 404 + 422-Pattern
  + 502-Discovery. Callback happy + One-Shot + State-Mismatch + Provider-
  Mismatch + 404 + 400-IdP-Error + 502-Discovery + Validation.
- `test_idp_registry.py`: +7 F-058 Tests (Google ohne ID/Secret/URI, MS
  ohne tenant_id, all-missing-listed, IdpConfigError-Base, Disabled-no-check).

## Code-Review und Findings

Closing-Review nach Standard-Prozedur (10 Kategorien, 4 Severity-Stufen).
WebSearches: RFC 9700 BCP, PKCE+BFF 2026-Patterns. Keine Must-Fixes,
keine Security-Hole.

| ID | Severity | Beschreibung | Tracking |
| --- | --- | --- | --- |
| F-058 | (close) | init_idp_registry Misconfig-Validation | resolved durch diese Story |
| F-062 | Info | `discovery_cache` ist In-Memory pro Service-Instanz. Bei Scale-Out wuerde jede Replica separat cachen (kein Korrektheits-, nur Effizienz-Issue). | Sprint 4 oder Scale-Out-Story |
| F-063 | Should | PKCE-Verifier wird vom Server NICHT gegen ein gespeichertes code_challenge gepruft (wir vertrauen auf IdP-Validation, ist RFC 7636-Standard). Defense-in-Depth optional in BRK-7. | vor PQC-42 BRK-7 wenn State-Service erweitert wird |
| F-064 | May | Spaces in scope-Query werden als `+` URL-encoded statt `%20`. Beide RFC 3986-konform, aber `%20` ist universal-kompatibel. | Sprint 4 wenn echte IdP-Tests evtl. Probleme zeigen |
| F-065 | Info | id_token wird roh an die App returned ohne Server-side Signature-Verifikation. BRK-3 (PQC-38) wird das aufgreifen. AC-5 spec'ed das so. | erledigt durch PQC-38 BRK-3 |
| F-066 | Info | Router validiert code_verifier nur per Laenge (43-128), nicht per Character-Class (RFC 7636: A-Z a-z 0-9 - . _ ~). App muss korrekte Generierung sicherstellen. | Sprint 4 oder bei PQC-60 APP-7 |
| F-067 | Info | Server-side haetten wir einen zusaetzlichen Test mit echtem Redis-Container (`docker-compose redis` mit TTL-Sleep) statt nur fakeredis. Higher-fidelity, aber langsam. | Sprint 4 Polish, optional |

Keine Must-Fixes. In-Story-Fix: F-058 (war Should). Rest via Tier 2 in
`docs/13_deferred_findings.md`.

## Verifikation

- `pytest tests/` 172/172 gruen, 4 erwartete Skips (liboqs-Sandbox).
- `ruff check services/ routers/ idp/` All checks passed.
- `python -c "from main import create_app; create_app()"` -> Imports + Route
  -Registration funktionieren (`/auth/federated/{provider}/authorize` und
  `/auth/federated/{provider}/callback` registriert).
- F-058-Verifikation: Manueller Test mit `enabled=true` ohne client_secret
  -> `IdpConfigError` bei Service-Start.

## Story-Aufwand

- Story-Points: 8
- Tatsaechliche Zeit: noch zu vermerken (User entscheidet, sofern abweichend
  vom Standard).
- AI-Multiplier-Beobachtung: 8 SP in einer Session ist deutlich oberhalb
  des historischen 4-6x-Multipliers. Pattern-Replikation aus
  token_service.py + crypto/registry.py hat erneut massiv beschleunigt.
  Sandbox-Compat-Probleme (datetime.UTC vs timezone.utc, httpx[socks])
  haben ein paar Minuten gekostet.

## Folgestories

- **PQC-42 BRK-7** (Hardening): Extrahiert State-Service in eigenes Modul
  (ist bereits getrennt!), ergaenzt Tests fuer TTL-Expiry mit Real-Time,
  ggf. F-063 Defense-in-Depth code_challenge-Pruefung.
- **PQC-38 BRK-3** (ID-Token-Verify): voll-implementiert `verify_id_token`
  der Plugins (JWKS-Fetch, RS256-Signature-Pruefung, iss+aud+exp).
- **PQC-39 BRK-4** (Identity-Normalisierung): voll-implementiert
  `claim_mapper` der Plugins.
- **PQC-40 BRK-5** + **PQC-41 BRK-6**: Vollausbau Google + Microsoft, wenn
  BRK-3 + BRK-4 fertig sind.
- **PQC-60 APP-7** + **PQC-61 APP-8**: App-Seite startet den Authorize-Flow
  ueber unseren Endpoint, postet zum Callback.
