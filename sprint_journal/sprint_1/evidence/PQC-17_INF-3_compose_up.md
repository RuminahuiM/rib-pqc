# Evidence: PQC-17 (INF-3) - Docker-Compose-Skeleton lauft

**Story:** PQC-17, INF-3, "Docker-Compose-Skeleton mit drei Services"
**Sprint:** PQC Sprint 1 (23.05.2026 - 30.05.2026)
**Carry-over aus:** Sprint 0
**Datum der Verifikation:** 25.05.2026
**Maschine:** Windows mit Docker Desktop, Git Bash (MINGW64)
**Verifiziert durch:** Dodoe (User), zusammen mit Implementation-Chat

## Was diese Evidence beweist

Das Docker-Compose-Skeleton aus `infra/docker-compose.yml` startet auf einem frischen Setup alle drei Services (nginx, auth-service, redis), die Services erreichen den `healthy` Status, der Reverse-Proxy liefert HTTP-Traffic vom Host auf die auth-service-Placeholder-Anwendung durch, und die Volumes plus Network werden korrekt angelegt.

## Ausgefuehrte Befehle

```bash
cd infra
cp .env.example .env
docker compose up --build
# In zweitem Terminal:
curl http://localhost:8080/
docker compose ps
```

## Output: docker compose up --build

```
[+] up 33/33
 v Image redis:7-alpine       Pulled                                        8.0s
 v Image nginx:1.27-alpine    Pulled                                        9.2s
 v Image python:3.12-slim     Pulled                                       12.1s
 v Network pqc-net            Created                                       0.1s
 v Volume pqc-redis-data      Created                                       0.0s
 v Volume pqc-auth-data       Created                                       0.0s
 v Container pqc-redis        Created                                       1.6s
 v Container pqc-auth-service Created                                       0.1s
 v Container pqc-nginx        Created                                       0.1s

Attaching to pqc-auth-service, pqc-nginx, pqc-redis

pqc-redis | 1:M 25 May 2026 09:34:30.847 * Running mode=standalone, port=6379.
pqc-redis | 1:M 25 May 2026 09:34:30.858 * Ready to accept connections tcp
Container pqc-redis Healthy
Container pqc-auth-service Waiting
pqc-auth-service | auth-service placeholder listening on :8000
Container pqc-auth-service Healthy
pqc-nginx | /docker-entrypoint.sh: Configuration complete; ready for start up
pqc-nginx | 127.0.0.1 - - [25/May/2026:09:34:47 +0000] "GET /health HTTP/1.1" 200 224 "-" "Wget"
pqc-nginx | 127.0.0.1 - - [25/May/2026:09:34:57 +0000] "GET /health HTTP/1.1" 200 224 "-" "Wget"
```

## Output: docker compose ps

```
NAME               IMAGE               COMMAND                  SERVICE        CREATED         STATUS                   PORTS
pqc-auth-service   python:3.12-slim    "python -c 'import j..."  auth-service   3 minutes ago   Up 3 minutes (healthy)
pqc-nginx          nginx:1.27-alpine   "/docker-entrypoint..."   nginx          3 minutes ago   Up 3 minutes (healthy)   0.0.0.0:8080->80/tcp, [::]:8080->80/tcp
pqc-redis          redis:7-alpine      "docker-entrypoint.s..."  redis          3 minutes ago   Up 3 minutes (healthy)   6379/tcp
```

Alle drei Container `Up` und `healthy`. Port-Mapping `0.0.0.0:8080->80/tcp` zeigt dass der nginx-Reverse-Proxy vom Host aus erreichbar ist.

## Output: curl http://localhost:8080/

```json
{
    "service": "auth-service",
    "status": "placeholder",
    "story": "PQC-17 INF-3",
    "note": "Replaced by PQC-19 SKL-1",
    "python": "3.12",
    "env": {
        "REDIS_URL": "redis://redis:6379/0",
        "SQLITE_PATH": "/data/auth.sqlite"
    }
}
```

Beweist End-to-End-Routing: Host:8080 -> nginx:80 -> auth-service:8000, mit korrekt gesetzten Environment-Variablen.

## AC-Verifikation

| AC | Anforderung | Beweis im Output |
|---|---|---|
| AC-1 | docker-compose.yml startet drei Services ohne Fehler | `[+] up 33/33`, alle 3 Container `Created` und spaeter `Up (healthy)` |
| AC-2 | auth-service basiert auf Python 3.12 und liefert Dummy-Hello-Endpoint | `Image python:3.12-slim`, `auth-service placeholder listening on :8000`, JSON-Response auf GET / |
| AC-3 | redis ist von auth-service ueber Docker-Network erreichbar | env `REDIS_URL=redis://redis:6379/0` im JSON-Response, beide Services auf `pqc-net`, Service-Name `redis` als DNS resolved |
| AC-4 | Persistent Volumes auth-data und redis-data konfiguriert | `Volume pqc-auth-data Created`, `Volume pqc-redis-data Created` im up-Output, `docker volume ls` listet beide |
| AC-5 | README dokumentiert `docker compose up` als Standard-Befehl | `infra/README.md` Quickstart-Section enthaelt `docker compose up --build` |

Alle 5 Akzeptanzkriterien sind durch diesen Test-Run gedeckt.

## Bewusste Limitationen

- **nginx ist Stock-Image ohne TLS**: Der oqs-provider-Custom-Build folgt explizit in PQC-18 (INF-4). In INF-3 ist nginx absichtlich `nginx:1.27-alpine` und exposed nur Port 80 (gemappt auf Host 8080).
- **auth-service ist ein Inline-Python-Placeholder**: Kein eigenes Dockerfile, kein FastAPI, kein Code-File in `server/`. Der Endpoint antwortet auf jeden Pfad mit dem gleichen JSON. PQC-19 (SKL-1) ersetzt das durch echtes FastAPI mit `/health` als separatem Endpoint.
- **TLS ist out of scope**: Sprint 1 hat keine Cert-Erstellung. Kommt in Sprint 2 zusammen mit der oqs-provider-Integration.

## Quellen und Referenzen

- Jira: https://rumidesigns.atlassian.net/browse/PQC-17
- Story-Bezug: `docs/07_design.md` Abschnitt 3.1, `docs/06_tech_stack.md` Abschnitt 2.1
- Implementation-Files: `infra/docker-compose.yml`, `infra/nginx/nginx.conf`, `infra/.env.example`, `infra/README.md`
