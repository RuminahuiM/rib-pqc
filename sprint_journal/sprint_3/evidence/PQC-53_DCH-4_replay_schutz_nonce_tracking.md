# Evidence PQC-53 DCH-4: Replay-Schutz via Nonce-Tracking

**Story:** PQC-53 (DCH-4)
**Datum:** 2026-06-26
**T-Shirt:** M | **SP:** 5 | **Sprint:** 3

## Was wurde gebaut

`RedisNonceTracker` im selben Modul `server/services/nonce_tracker.py` ergaenzt, der das in PQC-51 (DCH-2) eingefuehrte `NonceTracker`-Protocol implementiert. Atomare Replay-Detection via `SET NX EX` in einer eigenen Redis-DB=4. NonceTracker-Protocol um Methode `check_and_register(session_id, nonce) -> bool` erweitert (True bei erster Verwendung, False bei Replay). DCH-2-Dependency wurde umgestellt: Replay-Check kommt NACH AEAD-Decrypt + JSON-Parse, damit Forge-Versuche keine Tracker-Slots verbrennen (Side-Channel-frei).

## AC-Mapping (3 Original + 9 Detail-AC)

| AC | Status | Verifikation |
|---|---|---|
| Original AC1 (Nonces pro Session in Redis) | erfuellt | `RedisNonceTracker` mit Key-Format `nonce:{session_id}:{nonce_b64url}`, eigene DB=4 |
| Original AC2 (Replay -> 400 + Security-Log) | erfuellt | Tests #2 + #4, `logger.warning("nonce.replay_detected", ...)` im Tracker + `logger.warning("dch2.nonce_reused", ...)` in der Dependency |
| Original AC3 (Trade-Off Stateful vs Timestamp dokumentiert) | erfuellt | `nonce_tracker.py` Module-Docstring + `docs/wire_format.md` Sec 5.5 mit Trade-Off-Tabelle |
| Detail-AC 1 (RedisNonceTracker neue Klasse) | erfuellt | services/nonce_tracker.py L167-246 |
| Detail-AC 2 (atomares `check_and_register`) | erfuellt | `SET NX EX`-Single-Command, Test #4 (asyncio.gather Race) |
| Detail-AC 3 (Key-Format + TTL = Session-TTL) | erfuellt | Test #5 inspiziert TTL via redis.ttl |
| Detail-AC 4 (eigene Redis-DB=4) | erfuellt | `SessionConfig.replay_redis_db = 4`, main.py Lifespan eigener Client |
| Detail-AC 5 (Reihenfolge NACH Decrypt+Parse) | erfuellt | authenticated_session.py umstrukturiert (check_and_register nach json.loads) |
| Detail-AC 6 (400 nonce_reused + WARNING) | erfuellt | dependency.warning-Log + 400 detail |
| Detail-AC 7 (main.py Lifespan wiring) | erfuellt | replay_redis client + RedisNonceTracker + app.state.nonce_tracker + aclose im finally |
| Detail-AC 8 (Tests neu + DCH-2 angepasst) | erfuellt | 9 RedisNonceTracker-Tests + 13 DCH-2-Tests angepasst, alle gruen |
| Detail-AC 9 (Trade-Off-Doku) | erfuellt | Module-Docstring + wire_format.md Sec 5.5 |

## Verifikation

```bash
# RedisNonceTracker + DCH-2 (Sandbox via fakeredis)
cd server && python3 -m pytest tests/test_redis_nonce_tracker.py tests/test_authenticated_session.py -v
# 22 passed in 13.89s

# Volle Test-Suite (kein Regress, +9 vs PQC-51)
cd server && python3 -m pytest
# 270 passed, 5 skipped (liboqs-Skip), 0 failed in 30.29s
```

## Architektur-Entscheidungen (Trade-Off Stateful vs Timestamp)

Stateful gewaehlt. Begruendung in `nonce_tracker.py` Module-Docstring:
- Redis ist bereits Teil der Architektur (SES-3, Rate-Limit, OIDC-State).
- Mobile-Clock-Skew bei iPhones macht Timestamp-Toleranz-Window unzuverlaessig.
- Deterministisches Verhalten ohne Toleranz-Edge-Cases.
- `SET NX EX` ist Standard-Pattern (WebSearch-Konsensus 2026).
- Bericht-Notiz: Timestamp-Ansatz waere fuer hochskalierbare Stateless-Microservices ohne shared Redis sinnvoll, mit NTP-Sync + 5s-Toleranz-Window.

## Reihenfolge-Refactor (DCH-2-Anpassung)

PQC-51 hatte `has_seen` -> `decrypt` -> `record`. Das war race-anfaellig (parallel-Requests koennten beide has_seen=False sehen, beide durchlaufen). PQC-53 ersetzt das durch:
1. Format-Check Headers + Nonce-Laenge
2. SessionService.get (session_expired?)
3. AEAD-Decrypt + JSON-Parse
4. `tracker.check_and_register(...)` (atomar) -> wenn False -> 400 nonce_reused
5. Return AuthenticatedSession

Vorteil: Forge-Versuche mit zufaelligen Nonces fallen am AEAD-Tag durch und fuettern den Tracker gar nicht erst (Side-Channel-frei). Race-Condition geschlossen durch atomares SET NX EX.

## Findings (resolved + tracked)

| ID | Severity | Status |
|---|---|---|
| Must | 0 | — |
| Should | 0 | — |
| F-114 | May | tracked (Redis-Outage waere stillschweigender Replay-Schutz-Aus, Sprint-4 Health-Check + Fail-Closed-Strategie) |
| F-115 | Info | tracked (replay_redis_db=4 ist neuer Default, README/docker-compose-Pruefung in Sprint-4) |
| F-116 | May | tracked (Race-Test gegen fakeredis statt echtem Redis, mit F-067 als Sprint-4 Integration-Test buendeln) |

## Out-of-Scope (explizit)

- App-Side-Nonce-Reuse-Prevention: App generiert eindeutige Nonces via `randomNonce()` aus PQC-26 CRY-6
- End-to-End-Replay-Integration-Test gegen echten Redis-Container: Sprint-4 Polish (F-067 + F-116)

## Links

- Code: `server/services/nonce_tracker.py` (246 Z, `+RedisNonceTracker` + `check_and_register` API), `server/dependencies/authenticated_session.py` (Reihenfolge-Refactor)
- Config: `server/config.py` `SessionConfig.replay_redis_db` Default 4
- Wiring: `server/main.py` Lifespan replay_redis_client + RedisNonceTracker + aclose
- Tests: `server/tests/test_redis_nonce_tracker.py` (145 Z, 9 Tests), `server/tests/test_authenticated_session.py` (469 Z, 13 Tests angepasst)
- Spec-Update: `docs/wire_format.md` v0.4 (Sec 5.5 + Trade-Off-Tabelle + History)
- Findings: `docs/13_deferred_findings.md` Sektion "PQC-53 DCH-4"
- Jira: https://rumidesigns.atlassian.net/browse/PQC-53
