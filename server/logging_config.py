"""Logging-Setup mit structlog im JSON-Format.

Story: PQC-19 (SKL-1), Acceptance Criterion AC-5.

structlog 24.x wird so konfiguriert, dass alle Log-Eintraege als ein-zeiliges
JSON auf stdout landen. stdlib-logging-Logger werden via ProcessorFormatter
eingehaengt, sodass auch Logs von FastAPI, Uvicorn und Drittbibliotheken
das gleiche JSON-Format bekommen (Tech-Stack-Doku Abschnitt 2.5).

Beispiel-Ausgabe (eine Zeile, hier umgebrochen)::

    {
      "event": "service.start",
      "level": "info",
      "timestamp": "2026-05-25T10:12:33Z",
      "app": "rib-pqc-auth-service",
      "version": "0.1.0"
    }
"""

from __future__ import annotations

import logging
import sys

import structlog
from structlog.types import EventDict, Processor


def _add_app_context(app_name: str, version: str, environment: str) -> Processor:
    """Inject statische App-Felder in jedes Log-Event."""

    def processor(_logger: logging.Logger, _method: str, event_dict: EventDict) -> EventDict:
        event_dict.setdefault("app", app_name)
        event_dict.setdefault("version", version)
        event_dict.setdefault("env", environment)
        return event_dict

    return processor


def setup_logging(
    *,
    log_level: str,
    app_name: str,
    version: str,
    environment: str,
) -> None:
    """Konfiguriere structlog plus stdlib-logging fuer JSON-Output auf stdout.

    Idempotent: mehrfaches Aufrufen ist erlaubt und ueberschreibt die
    vorherige Konfiguration. Wichtig fuer den FastAPI-lifespan-Hook.
    """
    level = getattr(logging, log_level.upper(), logging.INFO)

    # Gemeinsame structlog-Pre-Processors: laufen auf BEIDEN Pfaden, also bei
    # nativen structlog-Calls UND bei stdlib-logging-Calls, die ueber den
    # ProcessorFormatter geleitet werden.
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        _add_app_context(app_name, version, environment),
    ]

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # stdlib-logging-Bridge: Drittanbieter-Logs werden zu JSON umgeschrieben.
    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            structlog.processors.JSONRenderer(),
        ],
    )

    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(formatter)

    root = logging.getLogger()
    # Vorhandene Handler entfernen, sonst doppelte Ausgaben nach reload.
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)

    # Uvicorn schreibt seine eigenen Logger; auf stdout-Handler umlenken.
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        log = logging.getLogger(name)
        log.handlers.clear()
        log.propagate = True
        log.setLevel(level)


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Hole einen konfigurierten structlog-Logger."""
    return structlog.get_logger(name)
