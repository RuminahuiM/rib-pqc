"""PQ-Session-Store fuer Auth-Service.

Story: PQC-48 (SES-3).
Bezug: docs/07_design.md Sektion 5.2, docs/wire_format.md Sektion 4,
FR-Session-3.

**Designprinzipien:**

- Redis-Key-Schema: ``session:<session_id>`` mit JSON-Body. session_id ist
  CSPRNG-erzeugte 16 Byte als urlsafe-base64 (22 chars, kein Padding).
- TTL via Redis SET EX, aus ``settings.session.ttl_seconds`` (Default 900).
- Session-Key (HKDF-Output 32 Byte) wird base64url-encoded gespeichert,
  damit JSON-serialisierbar. Auf Lookup zurueckdekodiert.
- created_at / expires_at als unix-Sekunden (int) gemaess Design 5.2.
- **session_key niemals loggen.** Logs nur Lengths plus session_id-Prefix.

**Lifecycle-Methoden:**

1. ``create(user_id, kem_alg, session_key)``: legt frischen Eintrag an,
   liefert die session_id.
2. ``get(session_id)``: Lookup, raised ``SessionNotFoundError`` wenn TTL
   abgelaufen oder Eintrag nie existierte. Verlaengert KEIN TTL (das macht
   ``refresh``).
3. ``refresh(session_id)``: setzt TTL erneut auf ``ttl_seconds``. Verwendet
   PERSIST + EXPIRE - kein Race. Raised ``SessionNotFoundError`` bei
   abgelaufenem Eintrag.
4. ``invalidate(session_id)``: explizites DEL fuer Logout, idempotent
   (kein Fehler wenn Eintrag schon weg).

**FIPS-203-Implicit-Rejection-Konnex (F-090):** Wenn das KEM Decaps mit einem
ungueltigen ct ein Pseudo-shared-secret liefert, landen wir mit einem
"Garbage-Session-Key" hier. Das ist OK: die Authentifizierung des Channels
passiert ueber den AEAD-Tag bei DCH-1/DCH-3, nicht hier. SessionService
speichert was er bekommt.
"""

from __future__ import annotations

import base64
import json
import logging
import secrets
import time
from typing import Protocol

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Session-ID-Laenge: 16 Byte CSPRNG, urlsafe-base64 ergibt 22 chars (ohne Padding).
# Best-Practice 2026: mindestens 128 bit. 128 bit = 16 Byte.
_SESSION_ID_BYTES = 16

# Redis-Key-Namespace. Trennt PQ-Sessions von OIDC-State (db=2) und
# Rate-Limit (db=1). Aufrufer waehlt via settings.session.session_redis_db die
# separate DB-Nummer (Default 3).
_KEY_PREFIX = "session"


def _session_key_redis(session_id: str) -> str:
    """Komponiert den Redis-Key fuer einen Session-Eintrag."""
    return f"{_KEY_PREFIX}:{session_id}"


def _b64url_encode_no_pad(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _b64url_decode(s: str) -> bytes:
    pad = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + pad)


class SessionNotFoundError(Exception):
    """Wird geworfen, wenn die session_id nicht (mehr) in Redis ist.

    Ursachen:
    1. session_id wurde nie erzeugt (Forge-Versuch oder Programmierfehler).
    2. TTL abgelaufen (User-Inaktivitaet > session.ttl_seconds).
    3. Session wurde explizit invalidiert (Logout).

    Der Aufrufer (Router-Middleware DCH-2) soll das auf 401
    ``session_expired`` mappen ohne weiter zu differenzieren
    (Side-Channel-Vermeidung).
    """


class SessionRecord(BaseModel):
    """In-Memory-Repraesentation eines Session-Records.

    Story-Bezug: PQC-48 SES-3 plus docs/07_design.md Sektion 5.2.

    Felder:
    - ``user_id``: aus verifiziertem Broker-Token sub-Claim.
    - ``kem_alg``: KEM-Algorithmus der Session (z.B. ``ML-KEM-768``).
      Wird bei jedem Channel-Request fuer Algorithmus-Logging mitgeschrieben.
    - ``session_key``: 32-Byte HKDF-Ausgabe (passt zu AES-256-GCM-Key).
      In Redis als base64url-no-pad gespeichert.
    - ``created_at``: unix-Sekunden, fuer Debug-Forensik und Sprint-3-Demo.
    - ``expires_at``: unix-Sekunden = created_at + ttl_seconds.
      Redis-TTL ist die Truth, ``expires_at`` ist Convenience fuer Clients
      die das Ablauf-Datum brauchen ohne TTL extra abzufragen.
    """

    user_id: str = Field(min_length=1)
    kem_alg: str = Field(min_length=1)
    session_key: bytes = Field(min_length=32, max_length=64)  # 32 Byte HKDF-Default
    created_at: int = Field(gt=0)
    expires_at: int = Field(gt=0)


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
    ) -> bool | None: ...

    async def get(self, name: str) -> bytes | None: ...

    async def delete(self, *names: str) -> int: ...

    async def expire(self, name: str, time: int) -> bool: ...


class SessionService:
    """Session-Store fuer PQ-Sessions (ML-KEM-Handshake + HKDF-Key).

    Story-Bezug: PQC-48 SES-3 (FR-Session-3).

    Lifecycle:

    1. ``create(user_id, kem_alg, session_key)`` beim Session-Init (SES-1):
       Erzeugt session_id, persistiert Record in Redis mit TTL, gibt
       (session_id, SessionRecord) zurueck.
    2. ``get(session_id)`` bei jedem Channel-Request (DCH-2):
       Lookup, kein TTL-Refresh. Raised SessionNotFoundError.
    3. ``refresh(session_id)`` bei aktiver User-Aktion (optional):
       Setzt TTL neu auf ttl_seconds.
    4. ``invalidate(session_id)`` beim Logout: DEL.
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
        self._ttl_seconds = ttl_seconds

    @property
    def ttl_seconds(self) -> int:
        return self._ttl_seconds

    @staticmethod
    def generate_session_id() -> str:
        """Erzeugt eine frische CSPRNG-session_id (urlsafe-base64, 22 chars).

        Story-Bezug: PQC-46 SES-1. SES-1 braucht die session_id vor dem
        SessionService.create-Aufruf, weil sie als HKDF-Salt fuer die
        Session-Key-Ableitung verwendet wird (PQC-47 SES-2 Konvention).
        """
        return _b64url_encode_no_pad(secrets.token_bytes(_SESSION_ID_BYTES))

    async def _persist_record(
        self,
        *,
        session_id: str,
        user_id: str,
        kem_alg: str,
        session_key: bytes,
    ) -> SessionRecord:
        """Interner Helper: baut SessionRecord, persistiert in Redis mit TTL.

        Story-Bezug: PQC-48 SES-3 + PQC-46 SES-1 + F-102 Refactor.
        Gemeinsame Implementation fuer ``create`` und ``create_with_id``.
        """
        now = int(time.time())
        record = SessionRecord(
            user_id=user_id,
            kem_alg=kem_alg,
            session_key=session_key,
            created_at=now,
            expires_at=now + self._ttl_seconds,
        )
        await self._redis.set(
            _session_key_redis(session_id),
            self._serialize(record),
            ex=self._ttl_seconds,
        )
        logger.info(
            "session.persisted session_id_prefix=%s user_id=%s kem_alg=%s ttl=%d",
            session_id[:8],
            user_id,
            kem_alg,
            self._ttl_seconds,
        )
        return record

    async def create(
        self,
        *,
        user_id: str,
        kem_alg: str,
        session_key: bytes,
    ) -> tuple[str, SessionRecord]:
        """Legt einen neuen Session-Record an und liefert (session_id, record).

        Args:
            user_id: aus verifiziertem Broker-Token-sub-Claim.
            kem_alg: KEM-Algorithmus der Session.
            session_key: HKDF-Output, typisch 32 Byte (AES-256-GCM-Key).

        Returns:
            Tuple aus session_id (urlsafe-base64, 22 chars) und Pydantic-Record.
        """
        session_id = self.generate_session_id()
        record = await self._persist_record(
            session_id=session_id,
            user_id=user_id,
            kem_alg=kem_alg,
            session_key=session_key,
        )
        return session_id, record

    async def create_with_id(
        self,
        *,
        session_id: str,
        user_id: str,
        kem_alg: str,
        session_key: bytes,
    ) -> SessionRecord:
        """Persistiert einen Session-Record mit pre-generated session_id.

        Story-Bezug: PQC-46 SES-1 (API-Erweiterung von PQC-48 SES-3, siehe
        F-101). Aufrufer hat bereits eine session_id mit ``generate_session_id()``
        erzeugt (z.B. weil sie als HKDF-Salt fuer den session_key benoetigt
        wurde) und uebergibt sie hier.

        Returns:
            SessionRecord mit created_at/expires_at gesetzt.
        """
        return await self._persist_record(
            session_id=session_id,
            user_id=user_id,
            kem_alg=kem_alg,
            session_key=session_key,
        )

    async def get(self, session_id: str) -> SessionRecord:
        """Lookup ohne TTL-Refresh.

        Raises:
            SessionNotFoundError: wenn session_id nicht (mehr) im Store ist.
        """
        raw = await self._redis.get(_session_key_redis(session_id))
        if raw is None:
            logger.warning(
                "session.lookup_miss session_id_prefix=%s",
                session_id[:8],
            )
            msg = "session not found or expired"
            raise SessionNotFoundError(msg)
        return self._deserialize(raw)

    async def refresh(self, session_id: str) -> None:
        """Setzt die TTL des Eintrags erneut auf ``ttl_seconds``.

        Raises:
            SessionNotFoundError: wenn der Eintrag schon weg ist (z.B. TTL
                war bereits abgelaufen, kein Refresh moeglich).
        """
        ok = await self._redis.expire(_session_key_redis(session_id), self._ttl_seconds)
        if not ok:
            logger.warning(
                "session.refresh_miss session_id_prefix=%s",
                session_id[:8],
            )
            msg = "session not found or expired"
            raise SessionNotFoundError(msg)
        logger.debug(
            "session.refreshed session_id_prefix=%s ttl=%d",
            session_id[:8],
            self._ttl_seconds,
        )

    async def invalidate(self, session_id: str) -> bool:
        """Loescht den Eintrag idempotent. Returns True wenn etwas geloescht
        wurde, False wenn der Eintrag schon weg war."""
        deleted = await self._redis.delete(_session_key_redis(session_id))
        logger.info(
            "session.invalidated session_id_prefix=%s deleted=%d",
            session_id[:8],
            deleted,
        )
        return deleted > 0

    # ----- Serialization helpers -----

    @staticmethod
    def _serialize(record: SessionRecord) -> str:
        payload = {
            "user_id": record.user_id,
            "kem_alg": record.kem_alg,
            "session_key": _b64url_encode_no_pad(record.session_key),
            "created_at": record.created_at,
            "expires_at": record.expires_at,
        }
        return json.dumps(payload, separators=(",", ":"))

    @staticmethod
    def _deserialize(raw: bytes | str) -> SessionRecord:
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8")
        data = json.loads(raw)
        return SessionRecord(
            user_id=data["user_id"],
            kem_alg=data["kem_alg"],
            session_key=_b64url_decode(data["session_key"]),
            created_at=data["created_at"],
            expires_at=data["expires_at"],
        )
