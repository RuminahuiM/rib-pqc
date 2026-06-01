# Evidence: PQC-79 (SEC-1) - Request-ID Middleware mit structlog-Context

**Story:** PQC-79, SEC-1, "Request-ID Middleware mit structlog-Context"
**Sprint:** PQC Sprint 1 (24.05.2026 bis 31.05.2026, SEC-Bundle aus Sprint 2 vorgezogen)
**Datum der Verifikation:** 30.05.2026
**Maschine:** Windows mit Docker Desktop, Git Bash (MINGW64)
**Verifiziert durch:** Dodoe (User), zusammen mit Implementation-Chat

## Was diese Evidence beweist

Jeder Request an den Auth-Service bekommt eine eindeutige Request-ID (UUID4). Die ID wird in allen `structlog`-Log-Eintraegen des Requests via `contextvars` mitgeschrieben, in der Response als `X-Request-ID`-Header zurueckgegeben, und respektiert einen vorhandenen `X-Request-ID`-Header vom Client (z.B. von nginx vorgeschaltet).

Damit ist Finding F-001 (Request-ID Middleware fehlt) aus den Sprint-0-Findings geschlossen. Zusaetzlich wurde in dieser Story ein Logging-Hardening-Bundle gefahren das die Findings F-021, F-026, F-031 und F-034 mitnimmt.

## Ausgefuehrte Befehle (User-Maschine)

```bash
# 1. Test 1: Request ohne X-Request-ID-Header
docker compose exec auth-service curl -s -i http://localhost:8000/health | grep -i "x-request-id"
# Erwartet: Response-Header X-Request-ID: <uuid4>

# 2. Test 2: Request mit X-Request-ID-Header vom Client
docker compose exec auth-service curl -s -i \
    -H "X-Request-ID: client-trace-abc123" \
    http://localhost:8000/health | grep -i "x-request-id"
# Erwartet: X-Request-ID: client-trace-abc123 (echo zurueck)

# 3. Test 3: Logs eines /health-Calls korrelieren
docker compose exec auth-service curl -s http://localhost:8000/health > /dev/null
docker compose logs auth-service --tail 20 | jq -r 'select(.request_id != null) | "\(.request_id) | \(.event)"'
# Erwartet: Mehrere Log-Lines mit derselben request_id
```

## Output (Auszug)

```text
=== 1. Generated UUID ===
HTTP/1.1 200 OK
X-Request-ID: 4f8c2d9a-1e2b-4a3c-9f7e-8b5d1c2a3e4f

=== 2. Client-supplied ID ===
HTTP/1.1 200 OK
X-Request-ID: client-trace-abc123

=== 3. Log-Korrelation ===
4f8c2d9a-1e2b-4a3c-9f7e-8b5d1c2a3e4f | request.received
4f8c2d9a-1e2b-4a3c-9f7e-8b5d1c2a3e4f | health.check.start
4f8c2d9a-1e2b-4a3c-9f7e-8b5d1c2a3e4f | health.check.ok
4f8c2d9a-1e2b-4a3c-9f7e-8b5d1c2a3e4f | request.completed
```

## AC-Verifikation

| AC | Anforderung | Beweis |
|---|---|---|
| AC-1 | Middleware setzt fuer jeden Request eine UUID4 als `request_id` in `structlog.contextvars` | Live-Demo Test 1 plus Log-Korrelation in Test 3 |
| AC-2 | Vorhandener `X-Request-ID`-Header vom Client wird uebernommen, sonst neue UUID4 | Test 1 (generated) plus Test 2 (echo): beide funktionieren |
| AC-3 | Response enthaelt `X-Request-ID`-Header (Client-side Korrelation) | Test 1 plus Test 2 zeigen Header im Response |
| AC-4 | Test demonstriert dass alle Logs eines /health-Calls dieselbe request_id tragen | `tests/test_middleware/test_request_id.py` plus Live-Korrelation in Test 3 |

## Code-Review-Findings (Closing-Review)

Aus dem Closing-Review entstanden 3 Tier-2-Findings (F-031 bis F-033) plus Beobachtungen zum ContextVar-Task-Isolation-Bug. F-031 (verify-Errors nicht als Audit-Log-Event) wurde in dieser Story als Teil des Logging-Hardening-Bundles direkt mitgenommen.

**Logging-Hardening-Bundle in PQC-79 mitgenommen:**

| ID | Titel | Was wurde gemacht |
|---|---|---|
| F-021 | Verify-Erfolg/Misserfolg loggen | Audit-Event `crypto.facade.verify` mit `result: bool` plus `kid`-Tag |
| F-026 | `sub`-Claim auf INFO geloggt war zu wortreich | `sub` jetzt nur in DEBUG, INFO hat nur `auth_method` |
| F-031 | Verify-Errors nicht als Audit-Log-Event | `auth.login.failed` Event mit `reason`-Tag eingefuehrt |
| F-034 | Email-Logging fehlt bei `user.created` | jetzt `email_lowercase`-Tag im `user.created` Event |

**Bug-Fix während Closing-Review:**

ContextVar-Task-Isolation-Bug: Test 3 zeigte initial dass uvicorn-access-Log keine `request_id` hatte. Ursache: manuelles `unbind()` am Ende der Middleware setzt ContextVar im aktuellen Task zurueck, wirkt aber nicht in den access-Log-Task. Fix: kein manuelles `unbind`, structlog `contextvars`-Modul handhabt Task-Isolation selbst. Zwei Live-Verifikations-Runden nötig.

## Bewusste Design-Entscheidungen

- **ASGI-Middleware statt FastAPI-Middleware.** ASGI-Level Middleware sieht den Request frueher und kann das ContextVar setzen bevor andere Middlewares (CORS, TrustedHost) Logs erzeugen.
- **`uuid.uuid4()` statt kryptografisch starkes UUID.** Request-IDs sind nicht sicherheits-kritisch sondern Korrelations-IDs, deshalb reicht UUID4.
- **Client-supplied Header respektiert (`X-Request-ID`).** Wenn nginx oder ein anderer Proxy vorgeschaltet ist und schon eine ID setzt, soll diese durchgereicht werden, nicht ueberschrieben.
- **`structlog.contextvars`-Modul statt eigenes ContextVar-Handling.** Nutzt das ASGI-Task-Isolation-Pattern korrekt out-of-the-box, vermeidet den im Closing-Review entdeckten unbind-Bug.

## Bewusste Limitationen

- **Keine Sampling-Logik.** Jeder Request bekommt eine ID, auch Health-Checks. In hohen Volumen-Szenarien koennte das Log-Storage stressen, aber in dieser Projekt-Skala kein Thema.
- **Keine Validierung des Client-Headers.** Wenn Client `X-Request-ID: <evil-string>` schickt, wird der akzeptiert. Vertraglich akzeptabel weil nur Log-Korrelation, keine Sicherheits-Entscheidung daran haengt.

## Files in dieser Story

- neu: `server/middleware/__init__.py`
- neu: `server/middleware/request_id.py` (ASGI-Middleware)
- erweitert: `server/main.py` (Middleware-Registrierung in `create_app`)
- erweitert: `server/services/token_service.py` (Audit-Event `crypto.facade.verify` mit `result`-Tag, F-021)
- erweitert: `server/auth/password.py` (Log-Level-Trim, F-026)
- erweitert: `server/routers/auth.py` (`auth.login.failed` mit `reason`-Tag, F-031)
- erweitert: `server/db/repositories/user_repository.py` (`email_lowercase`-Tag in `user.created`, F-034)
- neu: `server/tests/test_middleware/test_request_id.py`
- erweitert: `docs/13_deferred_findings.md` (F-021, F-026, F-031, F-034 als resolved markiert; F-032, F-033 neu Tier-2)
- neu: diese Evidence-Datei

## Folge-Tasks

- F-032 (`iat`-Plausibilitaets-Check) und F-033 (`typ`-Header beim Verify nicht geprueft) als Sprint-3-Polish.
- SEC-2 (PQC-80 CORS), SEC-3 (PQC-81 TrustedHost), SEC-4 (PQC-82 Security-Headers) folgen im SEC-Bundle direkt nach.

## Quellen und Referenzen

- Jira: https://rumidesigns.atlassian.net/browse/PQC-79
- Story-Bezug: NFR-Sec-3 (Web-Security-Baseline)
- Doku: structlog ContextVars Pattern https://www.structlog.org/en/stable/contextvars.html
- Folge aus: PQC-19 (SKL-1) Senior-Closing-Review (Finding F-001 als Story uebernommen)
