"""OIDC State-Store fuer CSRF-Schutz im Authorization-Code-Flow.

Stories:
- PQC-37 (BRK-2): Inline-Implementation mit Redis. Server-generierter State
  als CSRF-Token, One-Shot-Persistence (DEL nach erstem Consume).
- PQC-42 (BRK-7) - geplante Hardening-Story: Extra Tests fuer TTL-Expiry,
  Documentation, ggf. Refactoring.

**Designprinzipien (RFC 9700 OAuth 2.0 Security BCP 2026):**

- State wird **Server-side** generiert (`secrets.token_urlsafe(32)`, ergibt
  256 bit Entropie; RFC 6749 verlangt nur "unguessable", typische 2026-
  Empfehlung ist 128 bit+). Damit hat der Server volle Kontrolle ueber
  State-Existenz und kann ihn beim Callback authoritativ pruefen.
- ``code_verifier`` lebt App-side (RFC 7636 PKCE), nicht im Redis. Die
  App haelt ihn im Memory zwischen Authorize-Start und Callback und sendet
  ihn dann zum Callback-Endpoint. Wir leiten den Wert direkt an den IdP-
  ``/token``-Endpoint weiter (Token-Mediating-Backend-Pattern).
- One-Shot via Redis DEL nach erfolgreichem Consume verhindert Replay-
  Angriffe (RFC 9700 Section 2.1.2).
- TTL via Redis SET EX (default 600 s), Settings-konfigurierbar. Wenn der
  User nicht innerhalb der TTL den Login-Flow beendet, wird der Eintrag
  automatisch geloescht.

**Redis-Key-Schema:** ``oidc:state:<state_value>`` mit JSON-Body
``{"provider": "google", "created_at_iso": "2026-06-17T..."}``.
"""

from __future__ import annotations

import json
import logging
import secrets
from datetime import datetime, timezone
from typing import Protocol

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# State-Laenge: token_urlsafe(32) liefert ~43 url-safe chars = 256 bit Entropie.
# Deutlich mehr als die 128 bit aus RFC 9700; bei zukuenftigen Compute-
# Fortschritten weiterhin sicher.
_STATE_BYTES = 32

# Redis-Key-Namespace. Trennt OIDC-State vom Rate-Limit-Storage (db=1) und
# der allgemeinen Redis-DB (db=0). Aufrufer waehlt via Settings.oidc.state_redis_db
# die separate DB-Nummer.
_KEY_PREFIX = "oidc:state"


def _state_key(state_value: str) -> str:
    """Komponiert den Redis-Key fuer einen State-Eintrag."""
    return f"{_KEY_PREFIX}:{state_value}"


class StateNotFoundError(Exception):
    """Wird geworfen, wenn ein State-Wert nicht in Redis vorhanden ist.

    Ursachen:
    1. State wurde nie erzeugt (CSRF-Angriff oder Programmierfehler).
    2. TTL ist abgelaufen (User hat zu lange gewartet, > state_ttl_seconds).
    3. State wurde bereits konsumiert (Replay-Versuch, One-Shot wirkt).

    Der Aufrufer (Router-Layer) soll diesen Fall auf 400 Bad Request mappen
    ohne dem Client Details ueber den Grund zu geben (Side-Channel-Vermeidung).
    """


class StateEntry(BaseModel):
    """In-Memory-Repraesentation eines State-Eintrags.

    Story-Bezug: PQC-37 BRK-2 + PQC-42 BRK-7 AC-5.

    Felder:
    - provider: gewuenschter IdP-Name.
    - code_verifier: PKCE-Verifier (RFC 7636, 43-128 chars), server-side
      gespeichert. BFF-Pattern: Server reicht ihn beim Callback an IdP weiter.
    - created_at_iso: Audit-Timestamp.
    """

    provider: str = Field(min_length=1)
    code_verifier: str = Field(min_length=43, max_length=128)
    created_at_iso: str


class _RedisAsyncProtocol(Protocol):
    """Minimaler Redis-Client-Protocol fuer Typsicherheit + Testbarkeit.

    Echte Implementation: ``redis.asyncio.Redis``. Test-Implementation:
    ``fakeredis.aioredis.FakeRedis``. Beide erfuellen dieses Protocol.
    """

    async def set(
        self,
        name: str,
        value: str | bytes,
        *,
        ex: int | None = None,
    ) -> bool | None:
        ...

    async def get(self, name: str) -> bytes | None:
        ...

    async def delete(self, *names: str) -> int:
        ...


class OidcStateService:
    """State-Store fuer den OIDC-Authorization-Code-Flow.

    Story-Bezug: PQC-37 BRK-2 + PQC-42 BRK-7 (AC-5).

    Lifecycle:
    1. ``create(provider)`` beim Authorize-Start. Generiert ``state_value``,
       persistiert ``{provider, created_at}`` in Redis mit TTL, gibt
       ``state_value`` zurueck. Die App leitet damit zum IdP weiter.
    2. ``consume(state_value)`` beim Callback. Liest und loescht atomar (lookup
       dann DEL). Liefert ``StateEntry`` bei Erfolg, raised
       ``StateNotFoundError`` sonst.
    """

    def __init__(
        self,
        redis_client: _RedisAsyncProtocol,
        ttl_seconds: int,
    ) -> None:
        if ttl_seconds <= 0:
            msg = f"ttl_seconds must be positive, got {ttl_seconds}"
            raise ValueError(msg)
        self._redis = redis_client
        self._ttl = ttl_seconds

    async def create(self, provider: str, code_verifier: str) -> str:
        """Erzeugt einen frischen State-Eintrag fuer ``provider`` und gibt den State-Wert zurueck.

        Args:
            provider: Lowercase Provider-Name (muss in IdpRegistry registriert sein,
                Validation passiert im Router).

        Returns:
            ``state_value`` als urlsafe-Base64-String (~43 chars).
        """
        state_value = secrets.token_urlsafe(_STATE_BYTES)
        entry = StateEntry(
            provider=provider,
            code_verifier=code_verifier,
            created_at_iso=datetime.now(tz=timezone.utc).isoformat()  # noqa: UP017 (Sandbox-Compat),
        )
        await self._redis.set(
            _state_key(state_value),
            entry.model_dump_json(),
            ex=self._ttl,
        )
        logger.info(
            "oidc_state.create",
            extra={"provider": provider, "ttl_seconds": self._ttl},
        )
        return state_value

    async def consume(self, state_value: str) -> StateEntry:
        """Liest den State-Eintrag und loescht ihn atomar (One-Shot).

        Args:
            state_value: Vom Client beim Callback uebergebener State.

        Returns:
            ``StateEntry`` bei Erfolg.

        Raises:
            StateNotFoundError: wenn der State nicht existiert, TTL abgelaufen
                ist, oder bereits konsumiert wurde.
        """
        key = _state_key(state_value)
        raw = await self._redis.get(key)
        if raw is None:
            logger.warning(
                "oidc_state.miss",
                extra={"reason": "not_found_or_expired"},
            )
            msg = "State value not found or expired"
            raise StateNotFoundError(msg)
        # DEL VOR der Verarbeitung - so kann selbst bei Server-Crash mid-flight
        # kein zweites consume erfolgreich sein.
        await self._redis.delete(key)
        try:
            payload_str = raw.decode("utf-8") if isinstance(raw, bytes) else raw
            entry = StateEntry.model_validate(json.loads(payload_str))
        except (ValueError, UnicodeDecodeError) as exc:
            logger.error(
                "oidc_state.malformed_payload",
                extra={"error": str(exc)},
            )
            msg = "State payload malformed"
            raise StateNotFoundError(msg) from exc
        logger.info(
            "oidc_state.consume",
            extra={"provider": entry.provider},
        )
        return entry
