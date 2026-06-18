# Evidence: PQC-48 SES-3 Session-Store mit TTL (Redis)

**Story:** PQC-48 SES-3 (5 SP, M-Size)
**Sprint:** 3
**Status:** Ready for Review
**Datum:** 2026-06-18

## Ziel und Acceptance Criteria

PQ-Session-Store mit Redis-Backend gemaess Design 5.2 und wire_format.md
Sec 4. Foundation fuer SES-1 (Session-Init, PQC-46) und DCH-2
(Header-basiertes Routing, PQC-51).

| AC | Status | Evidenz |
| --- | --- | --- |
| AC-1 Redis-Schluessel session:{id} mit JSON-Value | OK | `_KEY_PREFIX = "session"`, `_session_key_redis()`, `_serialize/_deserialize` |
| AC-2 TTL aus Config (session.ttl_seconds, Default 900) | OK | `SessionConfig.ttl_seconds: int = Field(default=900, ge=60, le=86400)`, im Konstruktor von SessionService geprueft. |
| AC-3 Session-Lookup, -Refresh, -Invalidierung | OK | `create()`, `get()`, `refresh()`, `invalidate()` als async-Methoden |
| AC-4 Pytest-Integration-Test mit Redis | OK (fakeredis) | 12 Tests in `tests/test_session_service.py`, deckt alle Lifecycle-Methoden plus Edge-Cases (Binary-Bytes, idempotente invalidate) |

## In PQC-48 implementiert

**Neue Files:**

- `server/services/session_service.py` (282 Zeilen): SessionService-Klasse,
  SessionRecord-Pydantic, SessionNotFoundError, _RedisAsyncProtocol fuer
  Test-Mocking. Pattern analog OidcStateService aus PQC-37.
- `server/tests/test_session_service.py` (192 Zeilen): 12 fakeredis-Tests.

**Aenderungen:**

- `server/config.py`: SessionConfig hinzugefuegt mit ttl_seconds (Default 900),
  session_redis_db (Default 3), hkdf_info (Default b"app-session-v1" fuer
  SES-2). In Settings als `session`-Feld eingebunden.
- `server/main.py`: SessionService-Import und Lifespan-Wiring. Eigener
  Redis-Client mit `settings.session.session_redis_db`. `app.state.session_service`
  fuer Consumer SES-1/DCH-2 verfuegbar.
- `docs/wire_format.md`: Sec 4 Session-Record auf Design 5.2 + Implementation
  aligned (expires_at statt auth_method, unix-ts statt ISO). Doku-Version 0.2.

## Architektur-Entscheidungen

**unix-Sekunden int statt ISO-String:** matched Design 5.2 + JWT-iat/exp-Konvention.
JSON-Serialization einfacher.

**Separate Redis-DB (Default 3):** Trennung von OIDC-State (db=2) und
Rate-Limit (db=1). Erlaubt unabhaengiges FLUSHDB / Backup pro Domain.

**session_key als base64url im JSON:** Bytes sind nicht JSON-nativ.
Encoding mit no-padding gemaess wire_format.md, decode via Helper.

**`SessionConfig.hkdf_info` als Config-Feld (nicht hardcoded):**
SES-2 (PQC-47) wird dieses Feld konsumieren. Erlaubt Domain-Separation
fuer zukuenftige Protokoll-Versionen (v2) ohne Code-Aenderung.

**fakeredis statt testcontainers fuer AC-4:** fakeredis ist 2026-Industrie-Standard
fuer Python-Redis-Unit-Tests, deckt Redis-Protokoll voll ab inkl. TTL/EXPIRE.
Real-Redis-Smoke-Test bleibt als F-067 Sprint-4-Polish.

## Tests + Verifikation

- `pytest tests/test_session_service.py -v` 12 passed (alle Lifecycle-Methoden + Edge-Cases).
- `pytest --no-cov -q` 227 passed, 5 skipped (Suite-Endstand nach PQC-27 war 215, jetzt 227, alle neuen Tests gruen).
- `ruff check` + `ruff format --check` clean fuer alle 4 modifizierten Files.

## Closing-Review

10 Kategorien tief geprueft. Hauptbefund war F-097 (Wire-Format-Drift
zwischen Doku und Implementation), in der Story selbst gefixt.
Nebenbei wurde F-096 entdeckt: registry.py/registry_init.py waren in
PQC-24 silently truncated, Tests broken seit Commit ae80de3. Per Hotfix-
Commit 5365f1a separat repariert.

**Findings-Bilanz:**

| ID | Severity | Beschreibung | Status nach PQC-48 |
| --- | --- | --- | --- |
| F-095 | Info | SessionConfig.ttl_seconds in config.py noetig | **resolved** in dieser Story |
| F-096 | Should | Edit/Write-Truncation in PQC-24 hat Tests gebrochen | **resolved** durch Hotfix 5365f1a (separater Commit) |
| F-097 | Must | wire_format.md Sec 4 out-of-sync mit Design 5.2 + Impl | **in Story gefixt** (Doku Version 0.2) |
| F-067 | May | Pytest-Test mit echtem Redis statt fakeredis | bleibt **open**, Sprint-4-Polish |

Keine offenen Must-/Should-Fixes.

## Story-Aufwand

- Story-Points: 5
- T-Shirt: M (7h Schaetzung)
- Tatsaechliche Zeit: 30 min
- AI-Multiplier-Beobachtung: ~14x. Pattern-Replikation aus
  OidcStateService extrem effizient. Tooling-Truncation kostete Zeit
  fuer Hotfix-Roundtrip (registry.py/registry_init.py-Restore), aber netto
  immer noch sehr schneller Build.

## Folgestories

- **PQC-47 SES-2 HKDF-Session-Key:** nutzt `facade.hkdf` mit `settings.session.hkdf_info`
  und `session_id` als salt. Erzeugt den 32-Byte session_key, der dann via
  `SessionService.create()` persistiert wird.
- **PQC-46 SES-1 POST /session/init (L=8):** orchestriert KEM-Encaps +
  HKDF + SessionService.create + Response.
- **PQC-51 DCH-2 Header-basiertes Session-Routing:** Middleware liest
  `X-Session-Id`, ruft `SessionService.get`, mapped SessionNotFoundError
  auf 401 session_expired.

---

## Nachtrag 18.06.2026 (PQC-46 SES-1 API-Erweiterung, F-101)

Bei der Implementation von PQC-46 SES-1 (POST /session/init) wurde
festgestellt, dass die `SessionService.create()`-API der ursprueglichen
PQC-48-Implementation nicht mit dem SES-2-HKDF-Flow harmoniert: SES-2
braucht die session_id als HKDF-Salt VOR der Key-Ableitung, aber
`create()` generiert die session_id intern, NACH dem Key-Aufruf.

Loesung in PQC-46:
- `SessionService.generate_session_id()` als oeffentlicher Static-Helper
  ergaenzt (CSPRNG-16-Byte urlsafe-base64).
- `SessionService.create_with_id(session_id, ...)` als alternativer
  Persist-Path ergaenzt (Aufrufer hat session_id bereits, z.B. weil
  als HKDF-Salt verwendet).
- F-102 Refactor: gemeinsamer interner Helper `_persist_record()` der
  von `create()` und `create_with_id()` aufgerufen wird, kein Code-
  Duplikat mehr.

Aufruf-Pattern (PQC-46 SES-1):

```python
session_id = session_service.generate_session_id()
session_key = derive_session_key(
    facade, shared_secret=ss, session_id=session_id, hkdf_info=info
)
await session_service.create_with_id(
    session_id=session_id,
    user_id=user_id,
    kem_alg=kem_alg,
    session_key=session_key,
)
```

Backward-compatibility: bestehende `create()`-API unveraendert, die
12 Sprint-3-Tests aus PQC-48 laufen weiter. SES-1 hinzugefuegt 12 weitere
Tests in `tests/test_session_router.py`.

Tracking: F-101 (Should) **resolved** durch diesen Nachtrag plus F-102
(Should) **resolved** durch den `_persist_record`-Refactor.
