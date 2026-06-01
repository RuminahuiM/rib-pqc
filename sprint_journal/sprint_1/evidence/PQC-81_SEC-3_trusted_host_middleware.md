# Evidence: PQC-81 (SEC-3) - TrustedHostMiddleware gegen Host-Header-Injection

**Story:** PQC-81, SEC-3, "TrustedHostMiddleware gegen Host-Header-Injection"
**Sprint:** PQC Sprint 1 (24.05.2026 bis 31.05.2026, SEC-Bundle aus Sprint 2 vorgezogen)
**Datum der Verifikation:** 30.05.2026
**Maschine:** Windows mit Docker Desktop, Git Bash (MINGW64)
**Verifiziert durch:** Dodoe (User), zusammen mit Implementation-Chat

## Was diese Evidence beweist

Der Auth-Service akzeptiert Requests nur mit `Host`-Header-Werten aus der konfigurierten Allowlist (`localhost`, `127.0.0.1`, `auth-service`, plus `testserver` fuer TestClient). Requests mit Host-Header `evil.com` oder anderen unbekannten Werten werden mit HTTP 400 Invalid Host abgewiesen. Damit ist Host-Header-Injection (z.B. spätere Token-Subject-Manipulation oder Password-Reset-Link-Spoofing) unterbunden.

Finding F-003 ist damit geschlossen.

## Ausgefuehrte Befehle (User-Maschine)

```bash
# 1. Request mit erlaubtem Host
curl -s -i -H "Host: localhost" http://localhost:8080/health
# Erwartet: 200 OK

# 2. Request mit Container-Hostname
curl -s -i -H "Host: auth-service" http://localhost:8080/health
# Erwartet: 200 OK

# 3. Request mit Evil-Host
curl -s -i -H "Host: evil.com" http://localhost:8080/health
# Erwartet: 400 Invalid Host

# 4. Request mit Subdomain-Injection
curl -s -i -H "Host: localhost.evil.com" http://localhost:8080/health
# Erwartet: 400 Invalid Host (keine implizite Subdomain-Akzeptanz)
```

## Output (Auszug)

```text
=== 1. Allowed Host (localhost) ===
HTTP/1.1 200 OK
content-type: application/json
{"status":"ok"}

=== 2. Allowed Host (auth-service) ===
HTTP/1.1 200 OK
{"status":"ok"}

=== 3. Disallowed Host (evil.com) ===
HTTP/1.1 400 Bad Request
content-type: text/plain; charset=utf-8
Invalid host header

=== 4. Subdomain-Injection ===
HTTP/1.1 400 Bad Request
Invalid host header
```

## AC-Verifikation

| AC | Anforderung | Beweis |
|---|---|---|
| AC-1 | `starlette.middleware.trustedhost.TrustedHostMiddleware` in `create_app()` registriert | `server/main.py`, plus Live-Demo Test 1 funktioniert |
| AC-2 | Allowed-Hosts aus Settings (`trusted_hosts: list[str]`), Default `[localhost, 127.0.0.1, auth-service]` | `config.py` plus `config.yaml`. `testserver` zusaetzlich fuer TestClient-Tests |
| AC-3 | Request mit Host-Header `evil.com` returnt 400 Invalid Host | Test 3 zeigt exakt das. Test 4 verifiziert dass kein Subdomain-Drift erlaubt ist |

## Code-Review-Findings (Closing-Review)

0 Must, 0 Tier-1, 0 neue Tier-2-Findings. Wieder eine kompakte Story die auf Starlette-Boilerplate setzt.

## Bewusste Design-Entscheidungen

- **Starlette `TrustedHostMiddleware` statt eigene Implementation.** Robuste Behandlung von Host-Header-Quirks (Port-Spec, IPv6-Brackets, Punycode).
- **`testserver` in der Allowlist.** Damit FastAPI-TestClient (der intern `Host: testserver` setzt) gegen die Middleware nicht failt. Wichtig fuer die Pytest-Suite die im selben Container laeuft.
- **Exact-Match statt Pattern-Match.** Keine Wildcards (`*.example.com`-style), weil in dieser Projekt-Skala nicht relevant. Pattern-Match ist im Bedarfsfall via `allowed_hosts=["*.foo.com"]` von Starlette unterstuetzt, hier explizit nicht aktiviert.
- **Keine Custom-Error-Response.** Starlette default `400 Bad Request` mit Plain-Text-Body. Sicherheitstechnisch fine: ein Angreifer mit falschem Host bekommt keine Information ueber den Service.

## Bewusste Limitationen

- **Container-internal Calls.** Wenn der Auth-Service mal einen Outgoing-Call zu sich selbst macht (Loopback), muss der Host-Header passen. Bei der aktuellen Architektur passiert das nicht, aber wenn spaeter ein Self-Call-Pattern eingefuehrt wird (z.B. fuer Health-Probe), Hostname konsistent halten.

## Files in dieser Story

- erweitert: `server/main.py` (TrustedHostMiddleware-Registrierung)
- erweitert: `server/config.py` (`trusted_hosts: list[str]`)
- erweitert: `server/config.yaml` (trusted_hosts-Liste)
- erweitert: `server/tests/test_middleware/test_trusted_host.py` (Allowed plus Disallowed Tests)
- erweitert: `docs/13_deferred_findings.md` (F-003 als resolved markiert)
- neu: diese Evidence-Datei

## Folge-Tasks

- SEC-4 (PQC-82 Security-Headers) folgt direkt im Bundle.
- Bei Production-Deploy: trusted_hosts auf den echten DNS-Namen setzen, nicht `localhost`.

## Quellen und Referenzen

- Jira: https://rumidesigns.atlassian.net/browse/PQC-81
- Story-Bezug: NFR-Sec-3
- Doku: Starlette TrustedHostMiddleware https://www.starlette.io/middleware/#trustedhostmiddleware
- OWASP Host Header Injection 2024
- Folge aus: PQC-19 Senior-Closing-Review (Finding F-003 als Story uebernommen)
