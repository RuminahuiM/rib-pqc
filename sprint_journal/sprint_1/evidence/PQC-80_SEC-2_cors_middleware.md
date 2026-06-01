# Evidence: PQC-80 (SEC-2) - CORS-Middleware mit Allowlist-Konfiguration

**Story:** PQC-80, SEC-2, "CORS-Middleware mit Allowlist-Konfiguration"
**Sprint:** PQC Sprint 1 (24.05.2026 bis 31.05.2026, SEC-Bundle aus Sprint 2 vorgezogen)
**Datum der Verifikation:** 30.05.2026
**Maschine:** Windows mit Docker Desktop, Git Bash (MINGW64)
**Verifiziert durch:** Dodoe (User), zusammen mit Implementation-Chat

## Was diese Evidence beweist

Der Auth-Service akzeptiert Cross-Origin-Calls nur von den explizit in der Settings-Konfig erlaubten Origins. Wildcards `"*"` sind in Kombination mit `allow_credentials=True` per Pydantic-Validator blockiert (verhindert ein klassisches FastAPI-CORS-Misskonfig). Allowed-Methods sind GET/POST/OPTIONS, allowed-Headers sind `Authorization`, `Content-Type`, `X-Request-ID`.

Damit ist Finding F-002 (CORS-Middleware fehlt) geschlossen.

## Ausgefuehrte Befehle (User-Maschine)

```bash
# 1. Preflight-OPTIONS gegen /health mit erlaubtem Origin
curl -s -i -X OPTIONS http://localhost:8080/health \
    -H "Origin: http://localhost:8081" \
    -H "Access-Control-Request-Method: POST" \
    -H "Access-Control-Request-Headers: Content-Type,Authorization"
# Erwartet: 200, Access-Control-Allow-Origin: http://localhost:8081

# 2. Preflight mit nicht-erlaubtem Origin
curl -s -i -X OPTIONS http://localhost:8080/health \
    -H "Origin: http://evil.com" \
    -H "Access-Control-Request-Method: POST"
# Erwartet: 200 ohne Access-Control-Allow-Origin (Starlette CORS-Default-Verhalten)

# 3. Simple Request mit erlaubtem Origin
curl -s -i -H "Origin: http://localhost:8081" http://localhost:8080/health
# Erwartet: Access-Control-Allow-Origin: http://localhost:8081 im Response

# 4. Validator-Test: Wildcard plus allow_credentials muss Startup brechen
docker compose exec auth-service python -c "
from config import Settings
try:
    s = Settings(cors_allowed_origins=['*'], cors_allow_credentials=True)
    print('FAIL: should have raised')
except Exception as e:
    print(f'OK: {type(e).__name__}: {e}')
"
```

## Output (Auszug)

```text
=== 1. Allowed Origin Preflight ===
HTTP/1.1 200 OK
access-control-allow-origin: http://localhost:8081
access-control-allow-methods: GET, POST, OPTIONS
access-control-allow-headers: Authorization, Content-Type, X-Request-ID
access-control-allow-credentials: true
access-control-max-age: 600

=== 2. Disallowed Origin Preflight ===
HTTP/1.1 200 OK
(kein Access-Control-Allow-Origin Header)

=== 3. Simple Request Allowed Origin ===
HTTP/1.1 200 OK
access-control-allow-origin: http://localhost:8081
vary: Origin

=== 4. Pydantic-Validator gegen Wildcard plus Credentials ===
OK: ValidationError: cors_allow_credentials=True is incompatible with cors_allowed_origins=['*']
```

## AC-Verifikation

| AC | Anforderung | Beweis |
|---|---|---|
| AC-1 | `starlette.middleware.cors.CORSMiddleware` registriert in `create_app()` | `server/main.py` plus Live-Header-Check |
| AC-2 | Allowed-Origins aus Settings (`cors_allowed_origins: list[str]`), Dev-Default `[localhost:8081, localhost:8080]` | `config.py` plus `config.yaml`. Live-Demo Test 1 mit `localhost:8081` Origin echo |
| AC-3 | Keine Wildcards `"*"` in Default, Validator blockt Wildcard plus Credentials | Pydantic-Validator in `config.py` plus Live-Test 4 wirft `ValidationError` |
| AC-4 | Allowed-Methods GET/POST/OPTIONS, Allowed-Headers Authorization/Content-Type/X-Request-ID | Response-Headers in Live-Test 1 zeigen exakt diese Werte |
| AC-5 | Preflight-OPTIONS gegen /health zeigt korrekte Headers | Test 1 plus Test 2 |

## Code-Review-Findings (Closing-Review)

0 Must, 0 Tier-1, 0 neue Tier-2-Findings. SEC-2 ist eine kompakte Story die direkt auf Starlette-Boilerplate setzt, kein Bug-Potential im eigenen Code.

## Bewusste Design-Entscheidungen

- **Starlette `CORSMiddleware` statt eigene Implementation.** Production-tested, deckt alle Edge-Cases (Preflight, simple, credentialed) ab.
- **Pydantic-Validator gegen Wildcard plus Credentials.** Klassischer FastAPI-CORS-Misskonfig (`allow_origins=["*"], allow_credentials=True` ist von Starlette stillschweigend toleriert, kann aber Browser-Side-Probleme machen und ist sicherheitstechnisch problematisch). Validator failt explizit beim Startup statt Laufzeit-Bug.
- **Dev-Default mit `localhost:8081` (Expo-Dev-Server) plus `localhost:8080` (nginx-Reverse-Proxy).** Production-Default ist leere Liste, muss per Settings explizit gesetzt werden.
- **Allowed-Headers eng (`Authorization`, `Content-Type`, `X-Request-ID`).** Kein `*` um Custom-Header-Injection zu verhindern. `X-Request-ID` ist drin damit Frontend Korrelations-IDs setzen kann.

## Bewusste Limitationen

- **Kein Per-Endpoint-CORS-Override.** Globale Konfiguration fuer den ganzen Service. Wenn spaeter ein Public-API-Endpoint mit anderen Origins gebraucht wird, muesste das separat geloest werden.
- **Kein Origin-Pattern-Matching.** Nur Exact-Match-Allowlist. Fuer Multi-Tenant oder Wildcard-Subdomain (`*.example.com`) waere `allow_origin_regex` noetig, hier nicht relevant.

## Files in dieser Story

- erweitert: `server/main.py` (CORSMiddleware-Registrierung)
- erweitert: `server/config.py` (`cors_allowed_origins`, `cors_allow_credentials`, Pydantic-Validator)
- erweitert: `server/config.yaml` (cors-Section)
- erweitert: `server/tests/test_middleware/test_cors.py` (Preflight-Tests, Validator-Test)
- erweitert: `docs/13_deferred_findings.md` (F-002 als resolved markiert)
- neu: diese Evidence-Datei

## Folge-Tasks

- SEC-3 (PQC-81 TrustedHost) folgt direkt im Bundle.
- Bei Expo-Mobile-App: wenn der Expo-Dev-Server-Port wechselt, Settings updaten.

## Quellen und Referenzen

- Jira: https://rumidesigns.atlassian.net/browse/PQC-80
- Story-Bezug: NFR-Sec-3
- Doku: Starlette CORS https://www.starlette.io/middleware/#corsmiddleware
- OWASP CORS Cheat Sheet 2024
- Folge aus: PQC-19 Senior-Closing-Review (Finding F-002 als Story uebernommen)
