# Evidence: PQC-82 (SEC-4) - Security-Headers-Middleware

**Story:** PQC-82, SEC-4, "Security-Headers-Middleware (X-Frame-Options, X-Content-Type-Options, HSTS, CSP)"
**Sprint:** PQC Sprint 1 (24.05.2026 bis 31.05.2026, SEC-Bundle aus Sprint 2 vorgezogen)
**Datum der Verifikation:** 30.05.2026
**Maschine:** Windows mit Docker Desktop, Git Bash (MINGW64)
**Verifiziert durch:** Dodoe (User), zusammen mit Implementation-Chat

## Was diese Evidence beweist

Jede HTTP-Response des Auth-Service traegt defensive Headers nach OWASP Secure Headers Project: `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: no-referrer`. Im Non-Dev-Environment zusätzlich `Strict-Transport-Security` (HSTS). Damit sind XSS-Sniffing, Clickjacking und Information-Leak ueber Referrer-Header erschwert.

Content-Security-Policy (CSP) wurde bewusst weggelassen, weil Swagger-UI auf `/docs` mit der Default-CSP `default-src 'self'` brechen würde (inline-Scripts, External-CDN-Calls). CSP wird als separate Story fuer den Production-Polish-Bundle ausgelagert.

Finding F-004 ist damit geschlossen.

## Ausgefuehrte Befehle (User-Maschine)

```bash
# 1. Default-Response-Headers (Dev-Mode, kein HSTS)
docker compose exec -e ENVIRONMENT=dev auth-service curl -s -i http://localhost:8000/health | grep -E "^(x-|strict-|referrer-)" -i

# 2. Non-Dev-Mode mit HSTS
docker compose exec -e ENVIRONMENT=production auth-service curl -s -i http://localhost:8000/health | grep -E "^(x-|strict-|referrer-)" -i

# 3. Pytest gegen /health
docker compose exec auth-service python -m pytest tests/test_middleware/test_security_headers.py -v
```

## Output (Auszug)

```text
=== 1. Dev-Mode Response-Headers ===
x-content-type-options: nosniff
x-frame-options: DENY
referrer-policy: no-referrer
(kein Strict-Transport-Security, weil environment=dev)

=== 2. Non-Dev-Mode Response-Headers ===
x-content-type-options: nosniff
x-frame-options: DENY
referrer-policy: no-referrer
strict-transport-security: max-age=31536000; includeSubDomains

=== 3. Pytest test_security_headers ===
tests/test_middleware/test_security_headers.py::test_default_headers_present PASSED
tests/test_middleware/test_security_headers.py::test_hsts_only_in_non_dev PASSED
tests/test_middleware/test_security_headers.py::test_no_csp_yet PASSED
3 passed in 0.42s
```

## AC-Verifikation

| AC | Anforderung | Beweis |
|---|---|---|
| AC-1 | Middleware setzt mindestens `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: no-referrer`, plus conditional `Strict-Transport-Security` (nur non-dev) | Live-Demo Test 1 plus Test 2 zeigen das exakt |
| AC-2 | Optional CSP fuer JSON-Endpoints, mit Hinweis dass Swagger-UI separate Behandlung braucht | Bewusst weggelassen, dokumentiert in der Story-Done-Notiz. CSP-Story als Sprint-4-Polish in `13_deferred_findings.md` getrackt |
| AC-3 | Pytest-Coverage prueft die Headers auf /health | Test 3 zeigt drei gruene Tests |

## Code-Review-Findings (Closing-Review)

0 Must, 0 Tier-1, 0 neue Tier-2-Findings. Closing-Review hat sich auf die HSTS-Conditional-Logik konzentriert (richtig nur in non-dev gesetzt) und das war sauber.

## Bewusste Design-Entscheidungen

- **HSTS conditional auf non-dev.** Lokales Development hat kein TLS aktiv. Wenn HSTS in Dev gesendet wird, blockiert der Browser danach Plain-HTTP-Calls fuer max-age. Conditional via `if settings.environment != "dev"`.
- **HSTS-Werte konservativ.** `max-age=31536000` (1 Jahr), `includeSubDomains`, kein `preload` (preload-Liste ist eine eigene Submission, hier nicht angepeilt).
- **`X-Frame-Options: DENY` statt `SAMEORIGIN`.** Der Auth-Service rendert keine UI, also brauchen wir nichts im Iframe.
- **`Referrer-Policy: no-referrer`.** Strictest setting. Auth-Service redirects sind dafuer ausgelegt (keine externen Verweise wo Referrer wichtig waere).
- **CSP weggelassen.** Swagger-UI auf `/docs` braucht inline-Scripts und CDN-Calls. Default-CSP `default-src 'self'` wuerde das brechen. CSP-Story als Sprint-4-Polish.

## Bewusste Limitationen

- **Kein CSP.** Akzeptiert. Bei Production-Deploy als separate Story angehen, mit Swagger-Disable-Option fuer Production.
- **Kein `Permissions-Policy`-Header.** OWASP-Empfehlung waere `Permissions-Policy: geolocation=(), camera=(), microphone=()` o.aehnliches. Nicht relevant fuer einen Auth-Service ohne Hardware-Zugriff.

## Files in dieser Story

- neu: `server/middleware/security_headers.py`
- erweitert: `server/main.py` (Middleware-Registrierung)
- neu: `server/tests/test_middleware/test_security_headers.py` (3 Tests)
- erweitert: `docs/13_deferred_findings.md` (F-004 als resolved markiert, CSP-Polish-Story dokumentiert)
- neu: diese Evidence-Datei

## Folge-Tasks

- SEC-5 (PQC-83 Rate-Limiting) ist die letzte SEC-Story im Bundle.
- CSP-Story fuer Sprint 4 (Production-Polish): braucht Swagger-Strategy-Entscheidung (disable in prod oder separate CSP-Exemption).

## Quellen und Referenzen

- Jira: https://rumidesigns.atlassian.net/browse/PQC-82
- Story-Bezug: NFR-Sec-3
- OWASP Secure Headers Project https://owasp.org/www-project-secure-headers/
- HSTS RFC 6797
- Folge aus: PQC-19 Senior-Closing-Review (Finding F-004 als Story uebernommen)
