# infra/

**Infrastruktur**: Docker-Compose, nginx-Konfiguration mit oqs-provider, Beispiel-Secrets.

## Stand nach Sprint 1 (Story PQC-17 / INF-3)

Diese Ebene enthaelt jetzt ein lauffaehiges Docker-Compose-Skeleton mit drei Services. Hybrides TLS via oqs-provider folgt in PQC-18 (INF-4) und PQC-2-Epic-Stories aus Sprint 2.

Aktuelle Struktur:

```
infra/
├── docker-compose.yml      # nginx + auth-service + redis (PQC-17)
├── nginx/
│   └── nginx.conf          # Placeholder-Reverse-Proxy auf Port 80
├── .env.example            # Beispiel-Konfiguration (kopieren zu .env)
└── README.md
```

Geplante Erweiterungen in spaeteren Sprints:

- `nginx/Dockerfile` auf `openquantumsafe/oqs-ossl3`-Base mit TLS 1.3 und X25519MLKEM768 (PQC-18, INF-4)
- `certs/` mit Hinweis zu Self-Signed-Cert-Erstellung (Sprint 2)
- `nginx/nginx.conf` umgeruestet auf Port 443 mit hybrider Cipher-Suite (Sprint 2)

Bezug zu Backlog-Stories: siehe `../docs/09_product_backlog.md`, Epic INF und TLS.

## Quickstart

```bash
cd infra
cp .env.example .env       # Werte ausfuellen
docker compose up --build  # Standard-Befehl, AC-5 von PQC-17
```

Nach dem Start erreichbar:

```bash
# Reverse-Proxy ueber nginx (Default-Port 8080 auf dem Host, mappt auf nginx:80)
curl http://localhost:8080/
curl http://localhost:8080/health
```

Beide Calls landen am auth-service-Placeholder-Container, der ein kleines JSON ausliefert. Echte Endpunkte kommen mit den Sprint-1-Stories PQC-19 (SKL-1), PQC-28 (AUT-1), PQC-30 (AUT-3) und PQC-32 (TOK-1).

## Voraussetzungen

- Docker Desktop / Docker Engine ab Version 24
- Docker Compose v2 (`docker compose`, nicht `docker-compose`)

## Aufraeumen

```bash
docker compose down              # Container stoppen
docker compose down -v           # zusaetzlich Volumes (auth-data, redis-data) loeschen
```

## Architektur-Hinweise

Der aktuelle Stand ist bewusst als Placeholder gebaut, damit die folgenden Sprint-1-Stories sauber daran anknuepfen koennen:

- **PQC-18 (INF-4)** baut das nginx-Image neu auf der oqs-ossl3-Basis und ersetzt das stock `nginx:1.27-alpine` Image.
- **PQC-19 (SKL-1)** legt das FastAPI-Skeleton in `../server/` an, bringt einen eigenen Dockerfile mit und tauscht in `docker-compose.yml` die Service-Definition von `image: python:3.12-slim` plus inline `command` auf `build: ../server` um.
- **PQC-28 (AUT-1)** definiert das SQLite-Schema, das im `auth-data`-Volume unter `/data/auth.sqlite` persistiert wird.

Die Service-Namen (`auth-service`, `redis`, `nginx`) sind als DNS-Hostnames im Compose-Netzwerk `pqc-net` ansprechbar. Die env-Variable `REDIS_URL=redis://redis:6379/0` ist bereits gesetzt und entspricht dem Tech-Stack-Standard.
