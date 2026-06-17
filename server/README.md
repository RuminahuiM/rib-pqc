# server/

**Auth-Service** des Implementing-PQC-Projekts. Python 3.12 plus FastAPI plus liboqs-python.

## Aktueller Stand: PQC-19 (SKL-1)

Skeleton ist lauffaehig. Folgende Bereiche sind angelegt:

```
server/
├── pyproject.toml         # PEP 621, uv-managed, ruff plus mypy plus pytest Config
├── Dockerfile             # python:3.12-slim plus uv, non-root, /health Healthcheck
├── .dockerignore
├── config.yaml            # Default-Konfiguration (Sprint 1)
├── config.py              # pydantic-settings: YAML plus .env plus ENV-Override
├── logging_config.py      # structlog JSON-Output auf stdout
├── main.py                # FastAPI-App mit lifespan-Hook
└── routers/
    ├── __init__.py
    └── health.py          # GET /health
```

Folge-Sprint-Stories ergaenzen diese Struktur (geplant):

```
server/
├── crypto/
│   ├── registry.py        # PQC-21 (CRY-1) Algorithm-Registry
│   ├── facade.py          # PQC-22 (CRY-2) Crypto-Facade
│   └── adapters/          # PQC-25 (CRY-5) liboqs-Adapter pro Algorithmus
├── models/
│   ├── user.py            # PQC-28 (AUT-1) SQLAlchemy User-Model
│   └── session.py         # Session-Stories Redis-Session-Schema
├── routers/
│   ├── auth.py            # PQC-30 (AUT-3) /auth/local/* Endpoints
│   ├── federated.py       # Sprint 2 /auth/federated/<provider>/* Endpoints
│   ├── session.py         # Sprint 2-3 /session/* Endpoints
│   └── api.py             # Sprint 3 geschuetzte /api/* Endpoints
├── services/
│   ├── token_service.py   # PQC-32, PQC-33 (TOK-1, TOK-2) Broker-Token Sign/Verify
│   ├── idp_registry.py    # External-IdP-Plugin-Registry
│   └── idp_plugins/       # Google, Microsoft Plugins
└── tests/                 # PQC-63 bis PQC-65 (QUA-Stories)
```

Bezug zu Backlog-Stories: siehe `../docs/09_product_backlog.md`, Epics AUT, TOK, BRK, SES, DCH, CRY, SKL.

## Lokales Setup (ohne Docker)

```bash
cd server
uv sync                              # Installiert prod- plus dev-Dependencies
uv run uvicorn main:app --reload     # Server auf http://127.0.0.1:8000
```

Optional Tests, Linter und Type-Checks:

```bash
uv run ruff check .                  # Linter
uv run ruff format --check .         # Format-Check
uv run mypy .                        # Type-Checker (strict)
uv run pytest                        # Tests (sobald PQC-63 QUA-1 Pytest-Setup ran)
```

`uv` muss lokal installiert sein. Installation auf macOS und Linux:
`curl -LsSf https://astral.sh/uv/install.sh | sh`. Windows: `irm https://astral.sh/uv/install.ps1 | iex` in PowerShell, oder via `pipx install uv`.

## Lokales Setup (mit Docker Compose)

Standardweg fuer alle Sprint-1-Tests. Stack laeuft als auth-service plus nginx
plus redis. Reverse-Proxy auf Host-Port 8080.

```bash
cd ../infra
cp .env.example .env
docker compose up --build
curl http://localhost:8080/health
# -> {"status":"ok","version":"0.1.0"}
```

## Configuration

`config.yaml` liefert die Default-Werte fuer Dev. Override-Reihenfolge (von
schwach nach stark): YAML, `.env`, Environment-Variablen mit Praefix `RIB_`.

Konkrete ENV-Variablen (Sprint 1):

| Name | Default | Zweck |
|---|---|---|
| `RIB_LOG_LEVEL` | `info` | structlog Level |
| `RIB_ENVIRONMENT` | `dev` | dev, staging, prod |
| `RIB_HOST` | `0.0.0.0` | uvicorn bind |
| `RIB_PORT` | `8000` | uvicorn port |
| `RIB_REDIS_URL` | `redis://redis:6379/0` | Redis URL fuer kuenftige Session-Stories |
| `RIB_SQLITE_PATH` | `/data/auth.sqlite` | SQLite-Datei-Pfad fuer kuenftige Auth-Stories |
| `RIB_CONFIG_FILE` | `server/config.yaml` | Optional: alternativer YAML-Pfad |

## Endpoints (Sprint 1)

| Methode | Pfad | Zweck |
|---|---|---|
| GET | `/health` | `{ "status": "ok", "version": "0.1.0" }` |
| GET | `/docs` | FastAPI Swagger-UI |
| GET | `/openapi.json` | OpenAPI-Schema |

## Logging

`structlog` schreibt JSON-Eintraege auf `stdout`. Beispiel:

```json
{"event": "service.start", "level": "info", "timestamp": "2026-05-25T08:30:01.000Z", "app": "rib-pqc-auth-service", "version": "0.1.0", "env": "dev", "host": "0.0.0.0", "port": 8000, "log_level": "info"}
```

uvicorn- und FastAPI-Logs werden ueber die stdlib-Bridge auch durch den
structlog-JSON-Formatter geleitet, damit alle Log-Eintraege ein konsistentes
Schema haben.

## OAuth Provider Setup (PQC-84 BRK-0)

Federation-Stories BRK-1 bis BRK-7 brauchen OAuth-Apps bei Google und
Microsoft. Diese Apps werden manuell in den Provider-Consoles registriert,
Client-ID und Client-Secret landen in `infra/.env` (gitignored).

### Google Cloud Console

1. Account anlegen: separater Test-Google-Account (z.B. `rib-pqc-test@gmail.com`) statt privatem Account.
2. Google Cloud Console (`https://console.cloud.google.com/`) -> neues Projekt `rib-pqc`.
3. Branding-Page (Google Auth Platform): App-Name `rib-pqc`, Support-Email + Developer-Email setzen.
4. Zielgruppe: `External`, App bleibt in Testing-Status. Test-User-Liste pflegen falls externe Tester die App benutzen sollen (sonst 403).
5. Clients -> "OAuth-Client erstellen":
   - Anwendungstyp: **Webanwendung**
   - Name: `rib-pqc-dev`
   - Autorisierte JavaScript-Quellen: `http://localhost:8080`
   - Autorisierte Weiterleitungs-URIs: `http://localhost:8080/auth/oauth/google/callback`
6. Client-ID + Client-Secret aus dem Modal (oder JSON-Download) sichern.

**Discovery-URL fuer Verifikation:**
`https://accounts.google.com/.well-known/openid-configuration` (liefert JSON
mit `authorization_endpoint`, `token_endpoint`, `userinfo_endpoint`, `jwks_uri`).

### Microsoft Entra ID (Azure AD)

1. Azure Portal (`https://portal.azure.com/`) -> Microsoft Entra ID.
2. App registrations -> "+ New registration":
   - Name: `rib-pqc-dev`
   - Supported account types: **Accounts in this organizational directory only (Single tenant)**
   - Redirect URI: Platform `Web`, URI `http://localhost:8080/auth/oauth/microsoft/callback`
3. Overview-Page: `Application (client) ID`, `Directory (tenant) ID` notieren.
4. Certificates & secrets -> Client secrets -> "+ New client secret":
   - Description: `rib-pqc-dev-secret`
   - Expires: 180 days (default) bis 24 Monate
   - **Value** sofort kopieren (wird nur einmal angezeigt). Secret-ID ist NICHT der Secret-Wert.
5. API permissions -> Microsoft Graph -> Delegated:
   - `openid`, `email`, `profile` (plus `User.Read` als Default)
   - Optional: "Grant admin consent for <tenant>" damit der Consent-Bildschirm beim ersten Login uebersprungen wird.

**Discovery-URL fuer Verifikation (Single-Tenant):**
`https://login.microsoftonline.com/<TENANT_ID>/v2.0/.well-known/openid-configuration`

### Credentials in `.env` ablegen

`infra/.env.example` enthaelt die Variablennamen mit Platzhaltern. Lokale
Kopie unter `infra/.env` (gitignored):

```
GOOGLE_OAUTH_CLIENT_ID=...apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=GOCSPX-...
MICROSOFT_OAUTH_CLIENT_ID=<application-client-id-uuid>
MICROSOFT_OAUTH_CLIENT_SECRET=<secret-value-not-secret-id>
MICROSOFT_OAUTH_TENANT_ID=<directory-tenant-id-uuid>
```

### Dev vs Production: Redirect-URI

Sprint 2 nutzt `http://localhost:8080/...` weil lokaler nginx Reverse-Proxy
vor dem Auth-Service auf Port 8000 sitzt. Beide Provider erlauben das nur
fuer localhost als Sonderfall.

Production braucht eine echte Domain mit **HTTPS**:
`https://<dein-domain>/auth/oauth/<provider>/callback`. Beide Provider
erlauben mehrere Redirect-URIs pro App, daher kann die HTTPS-Production-URI
bei spaeterem Deploy einfach zusaetzlich in der gleichen OAuth-App-Reg
eingetragen werden. Localhost-URI bleibt parallel fuer weitere Dev-Arbeit.

### Secret-Rotation

Bei Secret-Exposition (z.B. accidentale Commit, Chat-Upload):

- Google: Cloud Console -> Clients -> rib-pqc-dev -> "Neues Geheimnis hinzufuegen", altes loeschen
- Microsoft: Azure Portal -> Entra ID -> App registrations -> rib-pqc-dev -> Certificates & secrets -> neues Secret erstellen, altes loeschen

Alte Secret-Strings sind invalid sobald sie geloescht sind. `.env` muss
entsprechend nachgepflegt werden, Container neu starten damit Auth-Service
die neuen Werte laedt.
