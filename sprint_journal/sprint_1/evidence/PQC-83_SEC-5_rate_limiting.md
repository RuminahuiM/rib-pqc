# Evidence: PQC-83 SEC-5 Rate-Limiting

- **Jira**: [PQC-83](https://rumidesigns.atlassian.net/browse/PQC-83)
- **Epic**: [PQC-78 SEC Security Infrastructure](https://rumidesigns.atlassian.net/browse/PQC-78)
- **Sprint**: 1 (Endspurt)
- **Done am**: 2026-05-30
- **Story Points**: 3
- **Resolves**: F-005 (Tier-1 Rate-Limiting fehlt)
- **In Closing-Review entdeckt + gefixt**: F-048 (proxy_headers fehlt -> Per-IP war faktisch Per-Cluster)

## Zusammenfassung

Rate-Limiting via `slowapi` mit Redis-Backend. Module-level `Limiter`-Singleton
mit Per-IP-Key (`get_remote_address`) plus zweite Per-Endpoint-Regel auf dem
Login-Endpoint (OWASP-konform 5/15min). 429-Response mit `Retry-After`-Header
und JSON-Body `{"error": "rate_limit_exceeded", "retry_after": <int>}`. Dev-only
Debug-Endpoint `/__debug/rate-limit-test` mit niedrigem Limit (3/minute) fuer
schnelle Live-Verifikation ohne 5 Argon2-Verify-Operationen.

## AC-Mapping

| AC | Akzeptanzkriterium | Implementation | Live-Verifiziert |
|---|---|---|---|
| AC-1 | Login-Endpoint hat Rate-Limit | `@limiter.limit("5/15minutes")` auf `POST /auth/local/login` | 6 falsche Logins -> Call 1-5 = 401, Call 6 = 429 + Retry-After |
| AC-2 | Globaler Default fuer alle Endpoints | `default_limits=["60/minute"]` im Module-level Limiter | Startup-Log `rate_limit.registered enabled=True global_default=60/minute storage_scheme=redis` |
| AC-3 | Per-IP-Key | `key_func=get_remote_address` + uvicorn `proxy_headers=True, forwarded_allow_ips="172.16.0.0/12"` | Zwei verschiedene X-Forwarded-For -> unabhaengige Buckets (siehe F-048-Fix) |
| AC-4 | 429-Response mit Retry-After-Header und JSON-Body | Custom `_rate_limit_exceeded_handler` liefert 429 + `{"error":"rate_limit_exceeded","retry_after":<int>}` + Header | Body verifiziert, `retry-after: 60` in Headers |
| AC-5 | Dev-only Test-Endpoint | `routers/dev_test.py` mit `@limiter.limit("3/minute")`, in `main.create_app()` nur bei `settings.environment == "dev"` registriert | 4 schnelle GETs -> 3x 200, 4. = 429 |

## Files

- `server/pyproject.toml`: `slowapi >=0.1.9,<0.2`, `redis >=5.0,<7.0` als deps
- `server/config.py`: `RateLimitConfig` (enabled, global_default, login_limit, storage_uri)
- `server/config.yaml`: `security.rate_limit`-Section mit OWASP-konformen Defaults
- `server/middleware/rate_limit.py` (NEU): Module-level `Limiter` Singleton, `register_rate_limit()` Helper, `_rate_limit_exceeded_handler`
- `server/middleware/__init__.py`: Exports `limiter`, `register_rate_limit`
- `server/main.py`: `register_rate_limit(app)` registriert; conditional `dev_test`-Router; uvicorn mit `proxy_headers=True, forwarded_allow_ips="172.16.0.0/12"` (F-048-Fix)
- `server/routers/auth.py`: `@limiter.limit(get_settings().security.rate_limit.login_limit)` auf `local_login`
- `server/routers/dev_test.py` (NEU): `GET /__debug/rate-limit-test` mit `@limiter.limit("3/minute")`
- `server/tests/test_rate_limit.py` (NEU): 8 Tests

## Live-Verifikation (Docker stack auf User-Maschine)

### Test 1: Dev-Test-Endpoint (3/minute, AC-5)

```
--- Call 1 --- HTTP/1.1 200 OK
--- Call 2 --- HTTP/1.1 200 OK
--- Call 3 --- HTTP/1.1 200 OK
--- Call 4 --- HTTP/1.1 429 Too Many Requests
                retry-after: 60
                Content-Type: application/json
                Body: {"error":"rate_limit_exceeded","retry_after":60}
```

### Test 2: Login-Endpoint mit falschen Credentials (5/15minutes, AC-1)

```
--- Login-Call 1 --- HTTP/1.1 401 Unauthorized
--- Login-Call 2 --- HTTP/1.1 401 Unauthorized
--- Login-Call 3 --- HTTP/1.1 401 Unauthorized
--- Login-Call 4 --- HTTP/1.1 401 Unauthorized
--- Login-Call 5 --- HTTP/1.1 401 Unauthorized
--- Login-Call 6 --- HTTP/1.1 429 Too Many Requests
                     retry-after: 60
```

### Test 3 (F-048-Fix-Verifikation): Per-IP-Isolation mit X-Forwarded-For (AC-3)

```
--- F-048-Verify: 4x Call mit X-Forwarded-For: 203.0.113.10 ---
Call 1 = HTTP 200
Call 2 = HTTP 200
Call 3 = HTTP 200
Call 4 = HTTP 429   <- IP-A-Bucket voll

--- F-048-Verify: 4x Call mit X-Forwarded-For: 198.51.100.20 ---
Call 1 = HTTP 200   <- IP-B-Bucket frisch trotz IP-A-Block
Call 2 = HTTP 200
Call 3 = HTTP 200
Call 4 = HTTP 429   <- IP-B-Bucket voll
```

Vor dem F-048-Fix waeren beide X-Forwarded-For-Werte im gleichen Bucket
gewesen (request.client.host = nginx-Container-IP), und IP-B Call 1 waere
sofort 429 gewesen. Der Live-Test beweist, dass jetzt jede echte Client-IP
ihren eigenen Bucket bekommt.

## Tests

- `tests/test_rate_limit.py` (8 Tests): alle gruen
  - `test_register_rate_limit_installs_state_and_handler`
  - `test_rate_limit_allows_under_limit`
  - `test_rate_limit_blocks_over_limit`
  - `test_rate_limit_response_has_retry_after_header`
  - `test_rate_limit_response_json_body_format`
  - `test_rate_limit_disabled_bypasses_all_limits`
  - `test_rate_limit_per_key_isolation`
  - `test_handler_returns_correct_response_shape`

- Volle Suite: `104 passed, 4 skipped` (4 Skips sind liboqs-not-installed in Sandbox)
- `ruff check .`: All checks passed

## Senior-Decisions (Story-Start)

1. **Storage**: Redis (`redis://redis:6379/1`), eigene DB-Nummer (1) damit Rate-Limit-Counter und Session-Daten (DB 0) keinen Keyspace teilen.
2. **Login-Limit**: OWASP-strenger 5/15min per IP (statt slowapi-Default).
3. **Key-Strategy**: Per-IP fuer Sprint 1. Per-Email-Composite-Key (gegen Distributed-Botnet) als Sprint 3 Polish. Per-Email-DoS-Risk (Account-Lockout-Attacker-Plot) bewusst akzeptiert.
4. **Dev-Test-Endpoint**: Ja, `/__debug/rate-limit-test` mit `env=dev`-Guard.
5. **Architektur**: Module-level Limiter Singleton (slowapi-Pattern, weil `@limiter.limit()` Decorator-Zeit-Resolution braucht).

## Findings aus Closing-Review

| ID | Titel | Severity | Status | Verlauf |
|---|---|---|---|---|
| F-005 | Rate-Limiting-Infrastruktur fehlt | Should | resolved | Pre-existent Tier-1, durch PQC-83 erledigt |
| F-048 | Per-IP-Limit war faktisch Per-Cluster (nginx-Proxy) | High | resolved-in-pqc-83 | In Phase-1-Audit entdeckt; main.py `_run()` mit proxy_headers=True + forwarded_allow_ips=172.16.0.0/12 gepatcht; live verifiziert mit 2 unterschiedlichen X-Forwarded-For |
| F-049 | Doppel-Logging `rate_limit.registered` beim Startup | Low | open (Tier-2 Polish) | uvicorn re-importiert main:app -> create_app() laeuft 2x. Funktional unschaedlich, nur Log-Noise. Fix: uvicorn.run mit App-Instanz statt String-Pfad. Trigger: Sprint 4 Image-Slim oder vor Bericht-Abgabe. |

## Web-Recherche-Ergebnisse (Phase 1)

- **slowapi 2026 best practice**: Redis-Backend fuer Multi-Instance (✓), X-RateLimit-* + Retry-After Header (✓ Retry-After), endpoint-spezifische Limits (✓), Monitoring der Limit-Hits (offen, Sprint 4 Observability)
- **OWASP API Security 2023**: Restrictive Rate-Limiting auf Auth-Endpoints empfohlen, Beispiel 3/min. Wir liegen mit 5/15min in der gleichen Groessenordnung. Defense-in-depth: CAPTCHA + MFA + Exponential-Backoff sind ergaenzende Mechanismen ausserhalb Sprint-1-Scope.
- **slowapi X-Forwarded-For-Bypass-Risiko**: `get_remote_address` nutzt `request.client.host` (NICHT direkt X-Forwarded-For wie Issue #255 suggeriert). Mit uvicorn `proxy_headers=True + forwarded_allow_ips=<CIDR>` wird `request.client.host` auf den echten X-Forwarded-For-Wert aus trusted-proxy gesetzt. Damit ist Bypass-Vektor geschlossen (siehe F-048-Fix).

## Demo-Check

- Sprint-Goal Demo-Slot ist D-004 (Local Login Pipeline). Rate-Limiting ist in der Demo bereits Teil des Pipeline-Flusses (Login-Endpoint).
- Mini-Demo separater Slot nicht noetig, weil Rate-Limit ein Schutz-Layer ist, der nicht User-Story-sichtbar ist (User merkt es nur wenn er das Limit hits, und das ist nicht Teil der Happy-Path-Demo).

## Worklog

- **Total: ca. 45min** (User-Schaetzung 2026-05-30, durchgehender Flow:
  Implementation, Live-Verify, F-048-Entdeckung+Fix+Re-Verify, Closing-Review,
  Evidence). Hohe Geschwindigkeit moeglich weil slowapi-Pattern straight-forward
  und SEC-Bundle-Vorarbeit (PQC-79/80/81/82) die Middleware-Order schon richtig
  gesetzt hatte.
