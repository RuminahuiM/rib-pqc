# Evidence PQC-52 DCH-3: Geschuetzter API-Endpoint /api/profile

**Story:** PQC-52 (DCH-3)
**Datum:** 2026-06-30
**T-Shirt:** M | **SP:** 5 | **Sprint:** 3

## Was wurde gebaut

Neuer Router `server/routers/api.py` mit `POST /api/profile`. Komplettes Encrypted-Channel-Roundtrip: Request entschluesselt via `Depends(authenticated_session)` aus DCH-2 (delegiert Header-Validation, Session-Lookup, AEAD-Decrypt, JSON-Parse, Replay-Check), Endpoint laedt User-Profile aus DB via `UserRepository.find_by_id`, erzeugt fresh CSPRNG-Nonce ueber `CryptoFacade.aead_random_nonce`, registriert die Response-Nonce im `RedisNonceTracker` (Defense gegen Cross-Talk Request<->Response), verschluesselt das Profile-JSON mit AAD = `session_id.encode("ascii")`, gibt HTTP 200 mit `X-Nonce`-Header und raw `application/octet-stream`-Body zurueck.

## AC-Mapping (3 Original + 9 Detail-AC)

| AC | Status | Verifikation |
|---|---|---|
| Original AC1 (Request entschluesselt via Session-Key) | erfuellt | Test #1 happy_path, Decrypt delegiert an authenticated_session |
| Original AC2 (User-Profile verschluesselt zurueck) | erfuellt | Test #1 + #7 (Klartext-Email nicht im Response-Body) |
| Original AC3 (Response AES-GCM mit neuer Nonce) | erfuellt | Test #2 (request_nonce != response_nonce) |
| Detail-AC 1 (POST /api/profile Router) | erfuellt | server/routers/api.py 216 Z |
| Detail-AC 2 (Depends(authenticated_session)) | erfuellt | Endpoint-Signatur |
| Detail-AC 3 (user_not_found 401 plaintext + WARNING) | erfuellt | Test #4 + WARNING-Log im Code |
| Detail-AC 4 (UC-5-Basis-Felder + ISO-8601 Z) | erfuellt | Test #1 prueft exakt das Dict |
| Detail-AC 5 (fresh CSPRNG-Nonce + AAD-Symmetrie) | erfuellt | Test #2 + Test #7 |
| Detail-AC 6 (Response-Nonce im Tracker registriert) | erfuellt | Test #3 (second check_and_register liefert False) |
| Detail-AC 7 (HTTP 200 + X-Nonce + octet-stream) | erfuellt | Test #1 Headers + Content-Type |
| Detail-AC 8 (Tests) | erfuellt | 7 Tests + 277 passed gesamt |
| Detail-AC 9 (wire_format Sec 5.3 final, F-094 close) | erfuellt | wire_format.md v0.5 |

## Verifikation

```bash
# Story-Tests
cd server && python3 -m pytest tests/test_api_profile_router.py -v
# 7 passed in 12.71s

# Volle Suite (kein Regress, +7 vs DCH-4)
cd server && python3 -m pytest
# 277 passed, 5 skipped (liboqs), 0 failed in 28.88s
```

## Architektur-Entscheidungen

- **POST statt GET:** UC-5 spec explicit POST. RESTful-Purist wuerde GET, aber GET-Body ist nicht universell unterstuetzt und POST mit verschluesseltem Body ist Standard 2026 fuer encrypted-channels.
- **Response-Nonce-Tracker-Eintrag:** Verhindert dass eine Server-Response-Nonce spaeter als Request-Nonce wiederverwendet werden kann (Cross-Talk-Schutz). Tracker-Slots fuer Request- und Response-Nonces sind dasselbe Key-Schema, also automatisch geschuetzt.
- **AAD-Symmetrie:** beide Richtungen (Request + Response) nutzen `session_id.encode("ascii")` als AAD. Damit ist Cross-Session-Replay zusaetzlich zur Session-Bindung verhindert.
- **user_not_found als 401 plaintext:** UC-5 E-1 (Session-Probleme) sagt 401 plaintext. Edge-Case User-Existenz-Verlust faellt in dasselbe Bucket aus App-Sicht (Re-Auth).
- **`_format_iso_utc` Helper:** SQLite stripped TZ-Info aus `DateTime(timezone=True)`. Robust gegen tz-naive Werte (Annahme: UTC). Postgres-Migration kann das vereinfachen (F-117).

## Findings (resolved + tracked)

| ID | Severity | Status |
|---|---|---|
| F-094 | Info | **resolved in-Story** (wire_format.md Sec 5.3 finalisiert, v0.5) |
| F-117 | May | tracked (_format_iso_utc Helper, bei Postgres-Migration vereinfachen) |
| F-110 (Update) | May | Tracking-Update auf 3x-Dup (Sprint-4 Shared-Helper-Refactor) |
| F-118 | Info | tracked (_get_db_session Pattern dupliziert auth.py.get_session, mit F-110 buendeln) |

## Sprint-3-Milestone

Mit PQC-52 ist der **Server-Pfad fuer Sprint-Goal D-008 funktional komplett**:

1. Token-Auth (Sprint 1)
2. KEM-Handshake `/session/init` (PQC-46)
3. HKDF-Session-Key (PQC-47)
4. Session-Store Redis (PQC-48)
5. Algorithmus-Negotiation (PQC-49)
6. AES-GCM-Wrapper (PQC-50)
7. Header-Routing-Dependency (PQC-51)
8. Replay-Schutz (PQC-53)
9. Encrypted `/api/profile`-Endpoint (PQC-52) <- diese Story

F-100-Trigger (Mini-Demo nach DCH-3) erreicht. Restscope Sprint 3: APP-Stories (APP-2/3/5/6) fuer Mobile-Seite.

## Out-of-Scope (explizit)

- App-Side-Wiring (APP-Stories PQC-58/59/55/56)
- Multi-Endpoint-Generalisierung (kommt erst wenn weitere geschuetzte Endpoints anstehen)
- /api/profile-Felder ueber UC-5-Basis hinaus

## Links

- Code: `server/routers/api.py` (216 Z, neu)
- Wiring: `server/main.py` Lifespan `app.include_router(api.router)`
- Tests: `server/tests/test_api_profile_router.py` (354 Z, 7 Tests)
- Spec-Update: `docs/wire_format.md` v0.5 (Sec 5.3 finalisiert)
- Findings: `docs/13_deferred_findings.md` Sektion "PQC-52 DCH-3"
- Jira: https://rumidesigns.atlassian.net/browse/PQC-52
