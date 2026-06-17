# Evidence: PQC-38 BRK-3 ID-Token-Verifikation

**Story:** PQC-38 BRK-3 (5 SP)
**Sprint:** 2
**Status:** Ready for Review
**Datum:** 2026-06-17

## Ziel und Acceptance Criteria

ID-Tokens von externen IdPs (Google, Microsoft) werden Server-side gegen
das Provider-JWKS verifiziert. Damit ist das `id_token` das von PQC-37 BRK-2
roh weitergereicht wurde, ab jetzt trusted. Schliesst F-065.

| AC | Status | Evidenz |
| --- | --- | --- |
| AC-1 JWKS-Fetch via Discovery + TTL-Cache | OK | `OidcJwksService.get_jwks` + 10 Tests, separate TTL 1h (vs Discovery 24h). |
| AC-2 Sig + iss + aud + exp Check | OK | `IdTokenVerifier.verify` via pyjwt-decode mit `verify_signature/exp/iss/aud` + `require`-Claims. |
| AC-3 Sig-Mismatch -> 401 | OK | `IdTokenVerifyError(reason="invalid_signature")` -> Router HTTP 401. |
| AC-4 Expired-Token -> 401 | OK | `IdTokenVerifyError(reason="expired")` -> Router HTTP 401. |
| AC-5 Unit-Tests mit Mock-JWKS | OK | 20 Tests (10 JWKS + 10 Verifier) plus echte RS256-JWT-Generation. |

## Architektur-Entscheidungen

| Entscheidung | Begruendung |
| --- | --- |
| pyjwt[crypto] >=2.10 | Industry-Standard 2026 (RFC 7519), python-jose barely maintained. Built-in `verify_signature/exp/iss/aud`, `leeway`, `require`-Claims. |
| Eigener OidcJwksService statt PyJWKClient | PyJWKClient ist sync-only und cached-only-per-URL. Wir brauchen async + Force-Refresh + integration im bestehenden services/-Pattern. |
| JWKS-TTL 1h (vs Discovery-TTL 24h) | Google/MS rotieren JWKS-Keys haeufiger als Discovery-Doc. 1h ist conservative-sicher, Force-Refresh-Fallback bei unknown_kid. |
| Algorithm-Pinning per Plugin (RS256-only) | Schutz gegen alg-confusion-attacks (RFC 9700 BCP 2026). Plugin uebergibt `allowed_algs=["RS256"]`, NICHT aus Header gelesen. |
| Plugin-Methode async + verifier injected | Konsistent mit Service-Layer-Async. Plugin orchestriert provider-spezifische post-validation (Microsoft tid-Check). |
| Force-Refresh bei unknown_kid | Key-Rotation-Race recovery: wenn cached JWKS den kid nicht hat, einmal frisch fetchen + nochmal probieren. |

## Implementierte Files

| Pfad | Zweck |
| --- | --- |
| `server/config.py` | `OidcConfig.jwks_cache_ttl_seconds` (default 3600) + `id_token_exp_leeway_seconds` (default 30). |
| `server/services/oidc_jwks_service.py` | `OidcJwksService` mit TTL-Cache + `force_refresh` + `invalidate`. `JwksFetchError`. |
| `server/services/id_token_verifier.py` | `IdTokenVerifier.verify` mit pyjwt + algorithm-pinning + JWKS-Lookup-mit-Retry. `IdTokenVerifyError` mit `reason`. |
| `server/idp/registry.py` | Protocol `verify_id_token` zu async + jwks_uri/verifier Params. |
| `server/idp/plugins/google.py` | Voll-Impl mit RS256-Pinning, ruft Verifier mit Google-iss + client_id-audience. |
| `server/idp/plugins/microsoft.py` | Voll-Impl mit RS256-Pinning + zusaetzlichem `tid`-Claim-Check fuer Single-Tenant. |
| `server/routers/auth_federated.py` | Callback-Endpoint ruft Plugin.verify_id_token nach Exchange. `IdTokenVerifyError -> HTTP 401`. |
| `server/main.py` | Lifespan: `OidcJwksService` + `IdTokenVerifier` an `app.state`. |
| `server/pyproject.toml` | Main-deps: pyjwt[crypto] + httpx. |
| `server/tests/test_oidc_jwks_service.py` | 10 Tests. |
| `server/tests/test_id_token_verifier.py` | 10 Tests inkl. RS256-Token-Generation. |

## Tests

```
======================= 190 passed, 4 skipped in ~15s =======================
```

**+20 neue Tests** in BRK-3. Volle Suite **190 passed** (vorher 172), 4
erwartete Skips (liboqs-Sandbox). Ruff `All checks passed`.

Test-Cluster:
- `test_oidc_jwks_service.py`: Fetch, Cache, Force-Refresh, Invalidate,
  HTTP-Error, Invalid-JSON, Missing-Keys, Network-Error, Constructor.
- `test_id_token_verifier.py`: Happy, Sig-Tamper, Expired, Disallowed-Alg,
  Invalid-Issuer, Invalid-Audience, Unknown-Kid+Force-Refresh, JWKS-Fetch-
  Fail, Malformed-Token, Constructor. Inkl. echter RS256-Token-Generation
  mit cryptography-Library.

## Code-Review und Findings

WebSearch: pyjwt[crypto] >=2.10 als 2026-Standard, Algorithm-Pinning Pflicht,
PyJWKClient gut aber sync-only.

Closing-Review nach Standard-Prozedur. Keine Must-Fixes.

| ID | Severity | Beschreibung | Tracking |
| --- | --- | --- | --- |
| F-065 | (close) | id_token roh weitergereicht | resolved durch diese Story |
| F-068 | Info | JWKS-Cache In-Memory pro Replica (Scale-Out). Analog F-062 fuer Discovery-Cache. | Sprint 4 oder Scale-Out-Story |
| F-069 | May | Verifier loggt `sub` bei Erfolg (User-ID). Mit `oid` (MS) waere besser tenant-stable. Aktuell beides geloggt, kein Privacy-Issue (sub ist opaque), aber kann erweitert werden. | Sprint 4 Logging-Polish |
| F-070 | Info | `nbf`-Claim wird nicht im require-Set verlangt (OIDC erlaubt nbf optional). Falls Provider nbf liefert, wird er aber via pyjwt-default geprueft. | informational |
| F-071 | Info | Force-Refresh-Loop ist auf 1 Retry begrenzt. Bei Provider-side rapid-Rotation (Sekunden) koennte das knapp sein. Provider tut das aber nie. | informational |
| F-072 | Info | Microsoft-Plugin tid-Check kommt NACH Sig-Verify. RFC 9700 sagt Sig-Verify zuerst (was wir machen), tid-Check ist Defense-in-Depth. | informational |

## Verifikation

- `pytest tests/` 190/190 gruen, 4 erwartete Skips (liboqs-Sandbox).
- `ruff check services/ routers/ idp/` All checks passed.
- `from main import create_app; create_app()` -> import + routes OK.
- Sandbox-Smoke: echte RS256-Tokens werden signiert und verifiziert. Token
  mit gefaelschter Sig wird rejected mit `reason=invalid_signature`. Token
  mit `aud=other-client` wird rejected mit `reason=invalid_audience`. Token
  mit `exp` in der Vergangenheit (jenseits Leeway) -> `reason=expired`.

## Story-Aufwand

- Story-Points: 5
- Tatsaechliche Zeit: tba (User entscheidet beim Done).
- AI-Multiplier-Beobachtung: erneut hoch dank Pattern-Replikation (services/-
  Layer, respx-Mock, pyjwt). Sandbox-Compat-Loops bei `datetime.UTC` haben
  ein paar Minuten gekostet.

## Folgestories

Unblockt PQC-39 BRK-4 (claim_mapper Voll-Impl) und PQC-40/41 BRK-5/6
(Google/Microsoft Voll-Impl). Damit ist der End-to-End-OIDC-Flow nach
PQC-39 + PQC-60 APP-7 erstmals funktional.
