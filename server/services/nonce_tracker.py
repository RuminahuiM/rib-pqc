"""Nonce-Tracker-Protocol fuer DCH-Replay-Schutz.

Story: PQC-51 (DCH-2) legt den Hook, PQC-53 (DCH-4) liefert echte
Implementation mit Redis-Persistenz.

Bezug:
- docs/wire_format.md Sec 5.1 (X-Nonce-Header)
- docs/wire_format.md Sec 5.4 (`nonce_reused` 400 Trigger)
- F-091, F-092 in docs/13_deferred_findings.md

**Architektur-Entscheidung (PQC-51):**

Die ``authenticated_session``-Dependency aus DCH-2 erhaelt eine
``NonceTracker``-Instanz als Constructor-Parameter. Default ist
``NoOpNonceTracker`` der keine Replay-Pruefung macht und immer ``False``
zurueckgibt (= "nonce wurde NICHT vorher gesehen"). Damit ist DCH-2
funktional komplett ohne Replay-Schutz, und PQC-53 (DCH-4) muss nur
einen ``RedisNonceTracker`` implementieren plus im Lifespan einwechseln
(``app.state.nonce_tracker = RedisNonceTracker(...)``). Die Dependency-
Signatur selbst aendert sich nicht.

**Symmetrie zu SessionService:**

Beide Komponenten teilen das Pattern Protocol-Definition + Default-Impl
mit minimalem Verhalten + spaetere Redis-basierte Production-Impl. Das
macht Mocking in Tests trivial (``FakeNonceTracker`` mit Set).
"""

from __future__ import annotations

import logging
from typing import Protocol

logger = logging.getLogger(__name__)


class NonceTracker(Protocol):
    """Interface fuer Nonce-Replay-Schutz pro Session.

    Implementationen muessen idempotent sein: mehrfache ``has_seen``-Aufrufe
    mit gleicher (session_id, nonce)-Kombination liefern stabil dasselbe
    Ergebnis bis ein Retention-Fenster (DCH-4: typisch session-TTL) ablaeuft.
    """

    async def has_seen(self, *, session_id: str, nonce: bytes) -> bool:
        """Prueft ob ``nonce`` fuer ``session_id`` bereits gespeichert ist.

        Returns:
            True wenn die Nonce in dieser Session schon einmal gesehen wurde
            (Replay-Trigger), False wenn das die erste Verwendung ist.
        """
        ...

    async def record(self, *, session_id: str, nonce: bytes) -> None:
        """Speichert ``nonce`` als gesehen fuer ``session_id``.

        Muss nach einem erfolgreichen AEAD-Decrypt aufgerufen werden, damit
        ein spaeterer Replay desselben (ct, nonce, session_id)-Tripels
        erkannt wird.
        """
        ...


class NoOpNonceTracker:
    """Default-Tracker ohne Replay-Schutz. Stub fuer DCH-2-Story.

    Story: PQC-51 (DCH-2).

    Verhalten:
    - ``has_seen`` liefert immer False (jede Nonce ist "neu"),
    - ``record`` ist ein No-Op (keine Persistenz),

    DCH-4 (PQC-53) ersetzt diese Klasse im Lifespan durch
    ``RedisNonceTracker`` ohne Touch der Dependency.
    """

    async def has_seen(self, *, session_id: str, nonce: bytes) -> bool:
        # Bewusst keine Pruefung. Sprint-3-Story DCH-4 zieht das nach.
        del session_id, nonce  # markiert fuer linter dass wir die Args wegwerfen
        return False

    async def record(self, *, session_id: str, nonce: bytes) -> None:
        del session_id, nonce
        return None
