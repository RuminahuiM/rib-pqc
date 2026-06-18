# Evidence: PQC-46 SES-1 POST /session/init mit ML-KEM-Encapsulation

**Story:** PQC-46 SES-1 (8 SP, L-Size)
**Sprint:** 3
**Status:** Done
**Datum:** 2026-06-18

## Ziel und Acceptance Criteria

Erster End-to-End-Pipeline-Endpoint: Token-authentifizierter Session-Init
mit ML-KEM-Encapsulation + HKDF-Session-Key-Ableitung + Redis-Persistenz.
Konsumiert CRY-4 (LibOqsKem), CRY-3 (kem_encaps Facade), SES-2 (HKDF),
SES-3 (SessionService) + TOK-2 (Token-Verify).

| AC | Status | Evidenz |
| --- | --- | --- |
| AC-1 Endpoint nimmt {kem_alg, encapsulation_key} + Bearer | OK | Pydantic SessionInitRequest + HTTPBearer-Dep (auto_error=False fuer 401-konform) |
| AC-2 Token-Verify + KEM-Encaps via Facade | OK | `_verify_bearer_token`-Dep ruft `token_service.verify`, dann `facade.kem_encaps(pk_bytes, kem_alg)` |
| AC-3 Response {session_id, ciphertext, expires_in} | OK | SessionInitResponse plus zusaetzliches kem_alg-Echo gemaess wire_format.md Sec 3.2 |
| AC-4 Session im Redis-Store mit TTL | OK | `session_service.create_with_id` persistiert via `_persist_record`. Test `test_session_init_persists_session_in_redis` verifiziert via session_service.get |

## In PQC-46 implementiert

**Neue Files:**
- `server/routers/session.py` (~290 Zeilen): POST /session/init Handler mit
  vollstaendigem Fehler-Mapping (401 invalid_token, 406 kem_alg_not_supported,
  400 invalid_encapsulation_key (Decode oder Length), 422 Pydantic-Missing).
- `server/tests/test_session_router.py` (12 Tests): httpx-AsyncClient gegen
  ASGI-Transport mit Mock-Facade + Mock-TokenService + fakeredis.

**Aenderungen:**
- `server/services/session_service.py`: API-Erweiterung um
  `generate_session_id()` (Static) und `create_with_id(session_id, ...)` plus
  `_persist_record`-internem Helper (F-102 Refactor). Backward-compatible.
- `server/main.py`: Router included via `app.include_router(session.router)`.

## Architektur-Entscheidungen

**HTTPBearer mit auto_error=False:** Default-Behavior wirft 403 wenn Header
fehlt. Wir mappen manuell auf 401 (RFC 7235) plus WWW-Authenticate-Header.

**FIPS-203-pk-Length-Pre-Check:** vor `facade.kem_encaps` validieren wir die
base64url-decoded-Laenge gegen FIPS-203-Table-3 (ML-KEM-768=1184, ML-KEM-1024=1568).
Schaerftere Fehlermeldung als liboqs-RuntimeError, weniger Crypto-Library-Overhead.

**SessionService API-Erweiterung statt Refactor des Routers:** SES-2-Konvention
braucht session_id als HKDF-Salt VOR der Key-Ableitung. Statt der Router
session_service.create's interne ID-Generierung zu umgehen, haben wir die
SessionService-API erweitert. Dokumentiert in PQC-48-Evidence-Nachtrag (F-101).

**HKDF-Salt = session_id.encode("ascii"):** matched SES-2-Konvention aus
PQC-47, ASCII-bytes des urlsafe-base64-strings.

## Tests + Verifikation

- `pytest --no-cov -q` 246 passed, 5 skipped (12 mehr als nach PQC-47).
- `ruff check` + `ruff format`: all clean.
- 12 Tests in 5 Gruppen:
  - Happy-Path parametrisiert ML-KEM-768/1024
  - Redis-Persistence verifiziert via session_service.get
  - 4 Auth-Fehler-Faelle (missing/invalid/expired/non-Bearer)
  - SES-4 Negotiation 406 mit supported_algorithms-Liste
  - 4 Invalid-Input-Faelle (base64-decode, length, Pydantic-Missing x2)

## Closing-Review (10 Kategorien)

| Kategorie | Befund |
| --- | --- |
| 1 AC | Alle 4 AC erfuellt, AC-3 erweitert um kem_alg-Echo wie spec'd in wire_format.md Sec 3.2 |
| 2 Code-Quality | ruff clean, vollstaendige Type-Hints, async-konsistent |
| 3 Test-Coverage | 12 Tests in 5 Gruppen, Mock-Strategie wegen liboqs-Skip-Pattern |
| 4 Security | session_key niemals geloggt, 401 no-detail-leak, WWW-Authenticate-Header, Pre-Validation vor Facade-Call |
| 5 Cross-Impact | main.py wired, SessionService API-Erweiterung in PQC-48-Evidence dokumentiert |
| 6 Documentation | Modul-Docstring mit Endpoint-Doku + Fehler-Responses + Sicherheits-Notizen |
| 7 Error-Handling | 6 HTTPException-Pfade + Pydantic-422, alle mit strukturiertem detail-Body |
| 8 Performance | linear: 1 Token-Verify + 1 KEM-Encaps + 1 HKDF + 1 Redis-SET |
| 9 Standard-Compliance | RFC 7235 Bearer, FIPS 203 PK-Laengen, RFC 5869 HKDF, NIST SP 800-38D-konformes spaeteres AEAD |
| 10 Demo/Evidence | Demo-Trigger erreicht (Sprint-3-Goal Pipeline-Bestandteil) |

Phase 1 (vor Review): WebSearch FastAPI-Bearer-Best-Practices, FIPS-203-PK-Laengen.
Grep nach hardcoded Secrets/TODOs in neuen Files: keine.

Phase 8: Demo-Trigger erreicht. Mini-Demo "End-to-End Session-Init" nach
PQC-49 SES-4 oder spaetestens vor DCH-3.

## Findings

| ID | Severity | Status |
| --- | --- | --- |
| F-099 | Info | open, Polish |
| F-100 | Info | open, Demo-Trigger erreicht |
| F-101 | Should | **resolved** in PQC-48-Evidence-Nachtrag |
| F-102 | Should | **resolved** durch _persist_record-Refactor |
| F-103 | May | open, Sprint-4-Polish |
| F-104 | May | open, Sprint-4-Polish |

## Story-Aufwand

- Story-Points: 8 (L-Size, 15h Schaetzung)
- Tatsaechliche Zeit: 40 min
- AI-Multiplier ~22x. Beinhaltet Audit-Roundtrip + 2 In-Story-Findings-Fixes.

## Folgestories

- **PQC-49 SES-4 Algorithmus-Negotiation (3 SP):** wir haben 406-Response
  bereits implementiert + getestet, SES-4-Story kann jetzt nur noch
  Client-Retry-Pattern + Cross-Doku-Update enthalten.
- **Mini-Demo D-008-Vorlaeufer:** SES-1 + SES-3 + SES-2 + TOK-2 in einer
  Pipeline. Container-up + curl-Demo nach SES-4.
- **PQC-50 DCH-1 AES-GCM Wrapper:** baut auf Session-Key auf, Nonce-Konvention
  per F-092.
