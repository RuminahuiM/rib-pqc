# infra/

**Infrastruktur**: Docker-Compose, nginx-Konfiguration mit oqs-provider, Beispiel-Secrets.

Inhalt wird in Sprint 0 (Carry-Over) und Sprint 2 aufgebaut. Geplante Struktur:

```
infra/
├── docker-compose.yml      # nginx + auth-service + redis
├── nginx/
│   ├── Dockerfile          # auf openquantumsafe/oqs-ossl3-Base
│   └── nginx.conf          # TLS 1.3 mit X25519MLKEM768
├── certs/
│   └── README.md           # Hinweis zu Self-Signed-Cert-Erstellung
└── .env.example            # Beispiel-Konfiguration (kopieren zu .env)
```

Bezug zu Backlog-Stories: siehe `../docs/09_product_backlog.md`, Epic INF und TLS.

Setup (vorläufig):

```bash
cd infra
cp .env.example .env       # Werte ausfüllen
docker compose up --build
```

Erforderlich: Docker Desktop / Docker Engine ab Version 24, mit Compose v2.
