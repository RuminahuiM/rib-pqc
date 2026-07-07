# syntax=docker/dockerfile:1.7
# Auth-Service Dockerfile - Multi-Stage
# Stories: PQC-19 (SKL-1), PQC-21 (CRY-1), PQC-25 (CRY-5), PQC-66/67 (QUA-4/5)
#
# Multi-Stage-Build mit uv als Package-Manager (Tech-Stack-Doku 4.4).
# - Stage ``runtime`` (default): Prod-Image mit --no-dev, keine Tests.
# - Stage ``test`` (extending runtime): fuegt dev-deps + tests fuer
#   Integration-Test-Runs im Container hinzu. Wird via
#   `docker compose build auth-service-test` oder
#   `docker build --target test` gebaut.
#
# uv-Binary aus offiziellem Astral-Image kopiert, sodass wir keine
# zusaetzlichen System-Dependencies pinnen muessen.
#
# liboqs-python triggert beim ersten Import den Download und Build der
# liboqs C-Library aus dem oqs-Source-Tree. Wir pre-compilen das im
# Docker-Build, damit der Container-Start nicht jedes Mal mehrere Minuten
# braucht. Das passiert im "import oqs" RUN-Step.

FROM python:3.12-slim AS runtime

# uv-Binary (statisches Release) holen.
COPY --from=ghcr.io/astral-sh/uv:0.5.4 /uv /uvx /usr/local/bin/

# Python-Runtime-Optimierungen und uv-Caching-Verhalten.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

# System-Dependencies:
#   - ca-certificates plus curl: TLS plus Debug-Tools
#   - build-essential, cmake, ninja-build, git: liboqs C-Library-Build
#     (von liboqs-python beim ersten Import getriggert)
#   - libssl-dev: liboqs linkt gegen OpenSSL fuer klassische Krypto-Primitive
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        build-essential \
        cmake \
        ninja-build \
        git \
        libssl-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Schritt 1: Build-Metadaten kopieren. README.md wird mitgenommen, weil
# pyproject.toml im [project]-Block `readme = "README.md"` referenziert.
COPY pyproject.toml README.md ./
COPY uv.lock* ./

# Schritt 2: Production-Dependencies installieren (ohne Dev-Extras, ohne das
# Projekt selbst). Cached so lange pyproject.toml und uv.lock stabil sind.
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev --no-install-project

# Schritt 3: liboqs C-Library beim ersten oqs-Import pre-compilen und in das
# venv-Verzeichnis caching. Dauert beim allerersten Build mehrere Minuten,
# danach via Layer-Cache instant. Per OQS_INSTALL_PATH explizit ablegen.
ENV OQS_INSTALL_PATH=/opt/oqs
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=cache,target=/root/.cache/pip \
    python -c "import oqs; print('liboqs version:', oqs.oqs_version()); print('liboqs ML-DSA available:', 'ML-DSA-65' in oqs.get_enabled_sig_mechanisms())"

# Schritt 4: Anwendungs-Code kopieren.
COPY main.py admin.py config.py logging_config.py config.yaml alembic.ini ./
COPY routers ./routers
COPY crypto ./crypto
COPY services ./services
COPY models ./models
COPY db ./db
COPY auth ./auth
COPY middleware ./middleware
COPY idp ./idp
COPY dependencies ./dependencies
COPY scripts ./scripts
COPY alembic ./alembic

# Schritt 5: Projekt selbst registrieren (ueber pyproject.toml).
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev

# Non-root User aus Security-Best-Practice. /data wird vom Volume gemountet
# und braucht Schreibrechte fuer SQLite und kuenftige Key-Files.
RUN groupadd --system app \
    && useradd --system --gid app --create-home --home-dir /home/app app \
    && mkdir -p /data /data/keys \
    && chown -R app:app /app /data /opt/venv /opt/oqs

USER app

EXPOSE 8000

# Default-Command. PQC-28: Alembic-Migrations werden bei jedem Start
# ausgefuehrt (idempotent, no-op wenn schon current). Danach uvicorn-Run via
# ``python main.py`` (liest Settings.host/port).
CMD ["sh", "-c", "alembic upgrade head && python main.py"]


# ===========================================================================
# Stage: test - Integration-Test-Runner (PQC-66/67 QUA-4/5)
# ===========================================================================
#
# Baut auf ``runtime`` auf und ergaenzt:
# - dev-deps (pytest, pytest-asyncio, pytest-cov, respx, fakeredis, ...)
# - tests/ Verzeichnis
#
# Prod-Image bleibt schlank; Test-Image ist explizit fuer QUA-4/5 gedacht.
# Ausfuehrung via docker compose:
#     docker compose build auth-service-test
#     docker compose run --rm auth-service-test pytest tests/ -v
#
# Alle liboqs-Layer + prod-Deps sind aus ``runtime`` gecacht, nur die
# dev-Sync + Tests-Copy laufen neu.
FROM runtime AS test

USER root
# WICHTIG: dev-Deps liegen unter [project.optional-dependencies].dev, nicht
# unter [dependency-groups]. Plain `uv sync` installiert Extras NICHT, darum
# explizit --extra dev (sonst fehlt pytest im Image -> Container-Start-Fail).
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --extra dev
COPY tests ./tests
RUN chown -R app:app /app/tests /opt/venv

USER app
CMD ["pytest", "tests/", "-v"]
