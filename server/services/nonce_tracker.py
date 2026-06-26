"""Nonce-Tracker fuer DCH-Replay-Schutz.

Stories:
- PQC-51 (DCH-2): Protocol + NoOpNonceTracker (Hook).
- PQC-53 (DCH-4): atomares ``check_and_register`` + RedisNonceTracker.

Bezug:
- docs/wire_format.md Sec 5.1 (X-Nonce-Header)
- docs/wire_format.md Sec 5.4 (`nonce_reused` 400 Trigger)
- docs/05_requirements.md NFR-Sec-2 (Schutz vor Replay-Angriffen)
- docs/11_risk_register.md R-T06 (Redis-Session-Store Bugs)
- F-091, F-092 in docs/13_deferred_findings.md

**Architektur:**

Die ``authenticated_session``-Dependency aus DCH-2 ruft fuer jeden
authentifizierten Request eine atomare ``check_and_register(session_id,
nonce)``-Operation auf. Returns ``True`` bei erster Verwendung der Nonce
in der Session, ``False`` bei Replay.

PQC-51 hatte das Pattern in zwei nicht-atomaren Methoden (``has_seen``
gefolgt von ``record``) eingefuehrt - das ist race-condition-anfaellig.
In PQC-53 ist ``check_and_register`` die Single-Source-of-Truth.
``has_seen``/``record`` bleiben fuer Backward-Compat als Wrapper, sollten
aber in neuem Code nicht mehr genutzt werden.

**Trade-Off Stateful (Redis) vs Timestamp-basiert (PQC-53 AC-3):**

| Aspekt | Stateful (gewaehlt) | Timestamp-basiert |
|---|---|---|
| Storage | Redis (shared, multi-instance-safe) | keine, server-stateless |
| Clock-Skew | irrelevant | kritisch (Mobile-Clients driften) |
| TTL-Steuerung | Redis-TTL, deterministisch | Toleranz-Window, weicher |
| Race-Condition | SET NX EX ist atomar | unkritisch (kein Shared-State) |
| Multi-Instance | trivial (shared Redis) | trivial (kein Shared-State) |
| Komplexitaet | Redis-Client + DB | Clock-Sync + Toleranz-Logic |

**Begruendung Stateful:**

- Redis ist schon Teil der rib-pqc-Architektur (SES-3, Rate-Limit, OIDC-State).
- Keine Annahme ueber Mobile-Client-Clock-Genauigkeit (R-T08-affin).
- Deterministisches Verhalten ohne Toleranz-Window-Gymnastik.
- SET NX EX ist Standard-Pattern (WebSearch-Konsensus 2026).

**Bericht-Notiz:** Timestamp-basierter Ansatz waere fuer hochskalierbare
Stateless-Microservices ohne shared Redis sinnvoll. In Kombination mit
JWT-Token (eingebetteter ``iat``) und einem Sliding-Window von z.B. 5s
auf Server-Seite + NTP-Sync. Trade-Off: false rejects unter
Clock-Skew sind moeglich; valid Bonafide-Replays innerhalb des Windows
schlagen durch. Fuer unser Use-Case (Mobile-Client mit driftender Clock)
ungeeignet.

**FIPS-203 Implicit-Rejection-Konnex (F-090):**

Decrypt findet VOR ``check_and_register`` statt. Bei Forge-Versuch mit
zufaelliger Nonce schlaegt AEAD-Tag-Check fehl, Replay-Tracker wird
gar nicht gefuettert. Damit sind Tracker-Slots Side-Channel-frei.
"""

from __future__ import annotations

import base64
import logging
from typing import Protocol

logger = logging.getLogger(__name__)

# Redis-Key-Namespace fuer Nonce-Tracking. Separater Namespace und separate
# DB (Default 4) trennen die Replay-Eintraege von Session-Records (db=3),
# OIDC-State (db=2) und Rate-Limit (db=1).
_KEY_PREFIX = "nonce"


def _b64url_encode_no_pad(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _nonce_redis_key(session_id: str, nonce: bytes) -> str:
    """Komponiert den Redis-Key fuer einen Replay-Eintrag.

    Format: ``nonce:{session_id}:{nonce_b64url}``. session_id ist URL-safe-base64
    (22 chars, kein Padding), Nonce ist 12 Byte AES-GCM-Nonce als base64url
    (16 chars, kein Padding). Komplette Key-Laenge ~40 chars.
    """
    return f"{_KEY_PREFIX}:{session_id}:{_b64url_encode_no_pad(nonce)}"


class NonceTracker(Protocol):
    """Interface fuer Nonce-Replay-Schutz pro Session.

    Implementationen muessen ``check_and_register`` atomar ausfuehren
    (Check + Insert in einer Operation), damit kein Race-Condition-Window
    zwischen zwei parallelen Requests mit gleicher (session_id, nonce)
    entsteht. Storage-Backends sind frei (Redis, In-Memory, Distributed-Cache).
    """

    async def check_and_register(self, *, session_id: str, nonce: bytes) -> bool:
        """Atomare Operation: ist das die erste Verwendung der Nonce?

        Args:
            session_id: die session_id aus dem X-Session-Id-Header.
            nonce: die 12-Byte AES-GCM-Nonce aus X-Nonce.

        Returns:
            True wenn die Nonce in dieser Session noch nicht gesehen wurde
            (= bonafide, durchwinken). False wenn die Nonce schon einmal
            registriert ist (= Replay-Trigger).
        """
        ...

    # Legacy-API (PQC-51 DCH-2), fuer Backward-Compat:
    async def has_seen(self, *, session_id: str, nonce: bytes) -> bool:
        """Nicht-atomar. In neuem Code ``check_and_register`` nutzen."""
        ...

    async def record(self, *, session_id: str, nonce: bytes) -> None:
        """Nicht-atomar. In neuem Code ``check_and_register`` nutzen."""
        ...


class NoOpNonceTracker:
    """Default-Tracker ohne Replay-Schutz. Stub fuer Tests und Dev-Setup.

    Story: PQC-51 (DCH-2) Hook.

    Verhalten:
    - ``check_and_register`` liefert immer True (= "Nonce ist neu"),
    - ``has_seen`` liefert immer False (legacy),
    - ``record`` ist ein No-Op (legacy).

    In Production wird ``RedisNonceTracker`` im Lifespan eingewechselt
    (PQC-53 DCH-4).
    """

    async def check_and_register(self, *, session_id: str, nonce: bytes) -> bool:
        del session_id, nonce
        return True

    async def has_seen(self, *, session_id: str, nonce: bytes) -> bool:
        del session_id, nonce
        return False

    async def record(self, *, session_id: str, nonce: bytes) -> None:
        del session_id, nonce
        return None


class _RedisAsyncProtocol(Protocol):
    """Minimaler Redis-Client-Subset fuer Typsicherheit + Testbarkeit.

    Echte Implementation: ``redis.asyncio.Redis``. Test-Implementation:
    ``fakeredis.aioredis.FakeRedis``. Beide erfuellen dieses Protocol.
    """

    async def set(
        self,
        name: str,
        value: str | bytes,
        *,
        ex: int | None = None,
        nx: bool = False,
    ) -> bool | None: ...

    async def get(self, name: str) -> bytes | None: ...


class RedisNonceTracker:
    """Redis-basierter Replay-Schutz fuer DCH-Channel.

    Story: PQC-53 (DCH-4). NFR-Sec-2.

    **Pattern:** ``SET key 1 NX EX ttl`` ist die kanonische atomare Operation
    fuer Single-Use-Tracking in Redis. ``NX`` (Set if Not Exists) liefert
    ``True`` nur beim erstmaligen Schreiben, ``None`` (Python-Truth-y False)
    beim Replay. ``EX`` setzt die TTL in Sekunden.

    **TTL-Konvention:** ``ttl_seconds`` sollte gleich der Session-TTL sein
    (Default 900s). Sobald die Session abgelaeuft ist, kann ein Replay
    eh nicht mehr decrypten (session_expired in der Dependency),
    daher braucht die Nonce nicht laenger persistent zu sein. Speicher-
    Beschraenkung: maximal ~3600 Nonces pro Session bei 4Hz-Traffic, vermutlich
    deutlich weniger im Mobile-Use-Case.

    **Key-Format:** ``nonce:{session_id}:{nonce_b64url}``. Kein TTL-Refresh
    bei has_seen-Aufruf (das macht ``check_and_register`` automatisch beim
    Initial-Insert).

    **Atomaritaet:** ``SET NX EX`` ist eine einzige Redis-Command, keine
    Race-Window zwischen zwei parallelen Aufrufen. WebSearch-Konsensus 2026.
    """

    def __init__(self, redis_client: _RedisAsyncProtocol, ttl_seconds: int) -> None:
        if ttl_seconds <= 0:
            msg = f"ttl_seconds must be positive, got {ttl_seconds}"
            raise ValueError(msg)
        self._redis = redis_client
        self._ttl_seconds = ttl_seconds

    @property
    def ttl_seconds(self) -> int:
        return self._ttl_seconds

    async def check_and_register(self, *, session_id: str, nonce: bytes) -> bool:
        """Atomare SET NX EX. True = erste Verwendung, False = Replay.

        Story: PQC-53 DCH-4 AC-2.
        """
        key = _nonce_redis_key(session_id, nonce)
        # Redis-py ``set`` returnt True bei erfolgreichem NX-Insert,
        # None bei NX-Konflikt (Key existiert bereits).
        result = await self._redis.set(key, b"1", ex=self._ttl_seconds, nx=True)
        first_use = bool(result)
        if first_use:
            logger.debug(
                "nonce.registered session_id_prefix=%s nonce_len=%d ttl=%d",
                session_id[:8],
                len(nonce),
                self._ttl_seconds,
            )
        else:
            logger.warning(
                "nonce.replay_detected session_id_prefix=%s nonce_len=%d",
                session_id[:8],
                len(nonce),
            )
        return first_use

    async def has_seen(self, *, session_id: str, nonce: bytes) -> bool:
        """Legacy-API: Lookup ohne Mutation.

        In neuem Code ``check_and_register`` bevorzugen (atomar).
        """
        raw = await self._redis.get(_nonce_redis_key(session_id, nonce))
        return raw is not None

    async def record(self, *, session_id: str, nonce: bytes) -> None:
        """Legacy-API: Insert ohne Check.

        In neuem Code ``check_and_register`` bevorzugen (atomar).
        Ueberschreibt bestehende TTL beim Re-Insert (idempotent).
        """
        await self._redis.set(
            _nonce_redis_key(session_id, nonce),
            b"1",
            ex=self._ttl_seconds,
        )
