# Evidence: PQC-19 (SKL-1) - FastAPI-Skeleton mit Config-Loading

**Story:** PQC-19, SKL-1, "FastAPI-Skeleton mit Config-Loading"
**Sprint:** PQC Sprint 1 (23.05.2026 - 30.05.2026)
**Datum der Verifikation:** 25.05.2026
**Maschine:** Windows mit Docker Desktop, Git Bash (MINGW64)
**Verifiziert durch:** Dodoe (User), zusammen mit Implementation-Chat

## Was diese Evidence beweist

Der FastAPI-Auth-Service-Skeleton baut als Docker-Image, startet im Compose-Stack
zusammen mit nginx und redis, und antwortet ueber den nginx-Reverse-Proxy auf
`/health`, `/docs` und `/openapi.json`. Logging laeuft als JSON auf stdout via
structlog, Config wird via pydantic-settings aus `config.yaml` plus optional
Environment-Variablen geladen.

## Ausgefuehrte Befehle

```bash
cd infra
docker compose down              # alten Placeholder-Stack stoppen
docker compose up --build        # neuer Stack mit echtem FastAPI-Skeleton
# In zweitem Terminal:
docker compose ps
curl -s http://localhost:8080/health
curl -s -I http://localhost:8080/docs
curl -s http://localhost:8080/openapi.json | head -c 200
```

## Output: docker compose ps

```
NAME               IMAGE                      COMMAND                  SERVICE        CREATED         STATUS                   PORTS
pqc-auth-service   rib-pqc-auth-service:dev   "uvicorn main:app --..."  auth-service   3 minutes ago   Up 3 minutes (healthy)   8000/tcp
pqc-nginx          nginx:1.27-alpine          "/docker-entrypoint..."   nginx          3 minutes ago   Up 3 minutes (healthy)   0.0.0.0:8080->80/tcp, [::]:8080->80/tcp
pqc-redis          redis:7-alpine             "docker-entrypoint.s..."  redis          3 minutes ago   Up 3 minutes (healthy)   6379/tcp
```

Drei Container `Up (healthy)`. Wichtig: auth-service-Image ist jetzt
`rib-pqc-auth-service:dev` (eigenes Image, gebaut aus `../server`), nicht mehr
`python:3.12-slim` mit Inline-Placeholder wie in PQC-17.

## Output: curl http://localhost:8080/health

```json
{"status":"ok","version":"0.1.0"}
```

AC-3 erfuellt: 200 OK mit exakt dem geforderten Body-Schema.

## Output: curl -s -I http://localhost:8080/docs

```
HTTP/1.1 200 OK
Server: nginx/1.27.5
Date: Mon, 25 May 2026 12:43:38 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 944
Connection: keep-alive
```

FastAPI Swagger-UI wird vom auth-service-Container ausgeliefert und korrekt
durch den nginx-Reverse-Proxy gerouted.

## Output: curl http://localhost:8080/openapi.json (erste 200 Bytes)

```json
{"openapi":"3.1.0","info":{"title":"rib-pqc-auth-service","version":"0.1.0"},"paths":{"/health":{"get":{"tags":["meta"],"summary":"Liveness und Version","description":"Liefert 200 OK mit dem aktuellen
```

OpenAPI-Schema 3.1.0 vorhanden, Service-Identitaet aus `config.yaml`, /health
ist als Route dokumentiert mit Tag `meta`. Beweist dass `app.include_router(health.router)`
korrekt registriert wurde.

## Output: Container-Logs Auszug (JSON-Logging, AC-5)

```json
{"host": "0.0.0.0", "port": 8000, "log_level": "info", "event": "service.start", "level": "info", "timestamp": "2026-05-25T12:36:19.004566Z", "app": "rib-pqc-auth-service", "version": "0.1.0", "env": "dev"}
{"event": "Application startup complete.", "level": "info", "timestamp": "2026-05-25T12:36:19.006156Z", "app": "rib-pqc-auth-service", "version": "0.1.0", "env": "dev"}
{"event": "Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)", "level": "info", "timestamp": "2026-05-25T12:36:19.024225Z", "app": "rib-pqc-auth-service", "version": "0.1.0", "env": "dev"}
{"event": "127.0.0.1:43740 - \"GET /health HTTP/1.1\" 200", "level": "info", "timestamp": "2026-05-25T12:36:22.252638Z", "app": "rib-pqc-auth-service", "version": "0.1.0", "env": "dev"}
{"event": "172.18.0.4:47906 - \"GET /health HTTP/1.1\" 200", "level": "info", "timestamp": "2026-05-25T12:36:27.789064Z", "app": "rib-pqc-auth-service", "version": "0.1.0", "env": "dev"}
```

Drei wichtige Belege in diesem Auszug:

1. Strukturiertes JSON-Logging via structlog mit konsistenten Feldern
   (`event`, `level`, `timestamp`, `app`, `version`, `env`).
2. Uvicorn- und stdlib-Logs werden ueber die ProcessorFormatter-Bridge auch in
   JSON umgesetzt ("Application startup complete." und Request-Logs).
3. Healthcheck-Calls von beiden Seiten erkennbar: `127.0.0.1` ist der eigene
   Compose-Healthcheck im auth-service-Container, `172.18.0.4` ist der
   nginx-Healthcheck der durch den Proxy laeuft.

## AC-Verifikation

| AC | Anforderung | Beweis im Output |
|---|---|---|
| AC-1 | server/ enthaelt FastAPI-App mit main.py, config.py, routers/ | Container `pqc-auth-service` baut aus `../server` mit allen drei Files, OpenAPI-Schema zeigt rib-pqc-auth-service als Service |
| AC-2 | pydantic-settings laedt aus config.yaml und ENV | App startet mit Werten aus YAML (`port:8000`, `log_level:info`), ENV-Overrides via `RIB_*` aktiv (sichtbar in `docker-compose.yml` `RIB_REDIS_URL` etc.) |
| AC-3 | /health liefert 200 OK mit {"status":"ok","version":"..."} | `curl http://localhost:8080/health` returned `{"status":"ok","version":"0.1.0"}` |
| AC-4 | App startet via uvicorn UND im Docker-Compose | Container-CMD `uvicorn main:app --host 0.0.0.0 --port 8000` laeuft, Healthcheck PASSED. Lokal mit `uv run uvicorn main:app --reload` verifiziert in Sandbox |
| AC-5 | Basic-Logging im JSON-Format | Logs sind ein-zeiliges JSON via structlog, mit App-Kontext-Feldern, mit stdlib-Bridge fuer Uvicorn |

Alle fuenf Akzeptanzkriterien sind durch diesen Test-Run gedeckt.

## Bewusste Design-Entscheidungen mit Sprint-Plan-Implikation

- **uv als Package-Manager** statt pip (Tech-Stack-Doku 4.4). Dockerfile kopiert die uv-Binary aus dem offiziellen `ghcr.io/astral-sh/uv:0.5.4` Image.
- **Single-Stage Dockerfile** statt Multi-Stage. Einfacher zu debuggen fuer Sprint 1. Multi-Stage waere ein Sprint-4-Polish-Thema.
- **Non-root User `app`** im Container fuer Security-Best-Practice. `/data`-Mount-Punkt wird in spaeteren Stories (SQLite via Volume) genutzt.
- **`fastapi[standard]` als dependency-Group**. Bringt seit Mai 2026 das `fastapi-cloud-cli` mit, das wir nicht brauchen. Image-Slim-Variante `fastapi[standard-no-fastapi-cloud-cli]` ist ein Polish-Kandidat fuer Sprint 4.
- **structlog-Bridge** fuer alle Drittanbieter-Logger (uvicorn, fastapi). Ergebnis ist konsistentes JSON auf stdout, kompatibel mit Docker Logging Drivers.

## Bewusster Bug-Fix waehrend der Story

Erster `docker compose up --build`-Versuch scheiterte mit:

```
OSError: Readme file does not exist: README.md
ERROR: failed to solve: process "/bin/sh -c uv sync --no-dev" did not complete successfully: exit code: 1
```

Ursache: pyproject.toml referenziert `readme = "README.md"`, mein Dockerfile
hat README.md aber nicht in den Build-Kontext kopiert. Fix: COPY-Zeile von
`COPY pyproject.toml ./` auf `COPY pyproject.toml README.md ./` geaendert.
Danach lief der Build sauber durch.

Senior-Engineer-Lesson: Sandbox-Smoke-Test verifizierte nur Python-Imports
und TestClient, NICHT den Docker-Build. Fuer Dockerfile-Stories braucht es
einen echten Docker-Build als Verifikations-Schritt. Ab jetzt entsprechend in
den Verifikationsplaenen.

## Aufraeumen

```bash
docker compose down              # Container stoppen
docker compose down -v           # zusaetzlich Volumes loeschen (Daten weg)
```

## Quellen und Referenzen

- Jira: https://rumidesigns.atlassian.net/browse/PQC-19
- Story-Bezug: `docs/07_design.md` Abschnitt 2.1, `docs/06_tech_stack.md` Abschnitte 2.2 und 2.5
- Implementation-Files:
  - `server/pyproject.toml`, `server/Dockerfile`, `server/.dockerignore`
  - `server/main.py`, `server/config.py`, `server/config.yaml`
  - `server/logging_config.py`, `server/routers/__init__.py`, `server/routers/health.py`
  - `server/README.md` aktualisiert
- Compose-Update: `infra/docker-compose.yml` (auth-service von Inline-Placeholder auf `build: ../server` umgestellt)

## Code-Review und unmittelbare Fixes (Nachtrag 25.05.2026 abends)

Nach AC-Verifikation wurde ein voller Code-Review durchgefuehrt (Standards,
Best Practices, Security). Ergebnis: 13 Findings, davon 1 noch in dieser Story
gefixt, 5 als Tier-1-Jira-Story-Drafts vorbereitet, 7 als Tier-2-Findings
getrackt.

**In PQC-19 gefixte Findings:**

- **C-1 (Settings.host/port nicht gewired):** `main.py` hat jetzt einen
  `_run()`-Helper plus `if __name__ == "__main__"`-Block, der `uvicorn.run`
  mit Settings.host und Settings.port aufruft. Docker-Dockerfile-CMD wurde
  von `["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]` auf
  `["python", "main.py"]` umgestellt. Damit funktionieren `RIB_HOST` und
  `RIB_PORT` Environment-Overrides wie das Settings-Modell suggeriert.

**Inline-TODO-Marker gesetzt:**

- `main.py` create_app: TODO(F-013) zu Access-Log-Filtering vor AUT-3.
- `config.py` settings_customise_sources: TODO(F-010) zu Class-Konstante.

**Weitere Findings tracked in:**

- `docs/13_deferred_findings.md` (Tier-2-Liste)
- `sprint_journal/sprint_1/jira_drafts_post_pqc19_review.md` (Tier-1-Drafts
  fuer SEC-1 bis SEC-5)

**Nicht-funktionale Auswirkung auf PQC-19:**
- Container muss erneut gebaut werden, damit die neue CMD `python main.py`
  greift. Funktional gleiches Verhalten, nur saubere Setting-zu-Runtime-Bruecke.
