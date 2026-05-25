# syntax=docker/dockerfile:1.7
# Auth-Service Dockerfile
# Story: PQC-19 (SKL-1), Acceptance Criterion AC-4.
#
# Single-Stage Build mit uv als Package-Manager (Tech-Stack-Doku 4.4).
# In einer Sprint-4-Polish-Story kann auf Multi-Stage umgestellt werden, falls
# Image-Groesse zum Thema wird. Fuer Sprint 1 ist Single-Stage einfacher zu
# debuggen.
#
# uv-Binary wird aus dem offiziellen Astral-Image kopiert, sodass wir keine
# zusaetzlichen System-Dependencies pinnen muessen.

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

# Minimale Systembibliotheken plus curl fuer Healthcheck/Debug.
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Schritt 1: Build-Metadaten kopieren. README.md wird mitgenommen, weil
# pyproject.toml im [project]-Block `readme = "README.md"` referenziert.
# Hatchling validiert das Feld waehrend des editable-Wheel-Builds und scheitert
# sonst mit "Readme file does not exist".
COPY pyproject.toml README.md ./
COPY uv.lock* ./

# Schritt 2: Production-Dependencies installieren (ohne Dev-Extras, ohne das
# Projekt selbst). Cached so lange pyproject.toml und uv.lock stabil sind.
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev --no-install-project

# Schritt 3: Anwendungs-Code kopieren.
COPY main.py config.py logging_config.py config.yaml ./
COPY routers ./routers
COPY crypto ./crypto

# Schritt 4: Projekt selbst registrieren (ueber pyproject.toml).
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev

# Non-root User aus Security-Best-Practice. /data wird vom Volume gemountet
# und braucht Schreibrechte.
RUN groupadd --system app \
    && useradd --system --gid app --create-home --home-dir /home/app app \
    && mkdir -p /data \
    && chown -R app:app /app /data /opt/venv

USER app

EXPOSE 8000

# Default-Command. ``python main.py`` triggert den ``_run``-Helper, der
# Settings.host und Settings.port liest. Damit funktionieren ``RIB_HOST`` und
# ``RIB_PORT`` Environment-Overrides wie das Settings-Modell suggeriert.
CMD ["python", "main.py"]
