# Evidence PQC-51 DCH-2: Header-basiertes Session-Routing

**Story:** PQC-51 (DCH-2)
**Datum:** 2026-06-26
**T-Shirt:** M | **SP:** 5 | **Sprint:** 3

## Was wurde gebaut

Eine FastAPI-Dependency `authenticated_session` als Einstiegspunkt fuer alle geschuetzten Encrypted-Channel-Endpoints. Statt globaler Middleware (Best-Practice-Search 2026 + CVE-2026-48710-safe-Argument) wird Dependency-Injection genutzt - konsistent mit PQC-46 SES-1 (HTTPBearer-Pattern).

Die Dependency:

1. Liest `X-Session-Id` und `X-Nonce` aus den Request-Headers.
2. Validiert Nonce-Format (12 Byte nach base64url-Decode, F-092 streng durchgesetzt).
3. Schlaegt den `SessionRecord` im `SessionService` (Redis, fakeredis in Tests) nach.
4. Liest den Body als raw `application/octet-stream` (wire_format.md Sec 5.2).
5. AEAD-Decrypt via `CryptoFacade.aead_decrypt` mit `session_id.encode("ascii")` als AAD.
6. Parst Plaintext als UTF-8-JSON, liefert dict.
7. Konsultiert `NonceTracker`-Hook fuer DCH-4-Replay-Schutz (Default `NoOpNonceTracker`).

## AC-Mapping (4 Original + 11 Detail-AC)

| AC | Status | Verifikation |
|---|---|---|
| Original AC1 (Headers lesen) | erfuellt | Test #1 happy_path, Test #2/3 missing-Header-Faelle |
| Original AC2 (fehlender Header -> 401) | erfuellt | Test #2 session_missing, Test #3 nonce_missing |
| Original AC3 (ungueltige session_id -> 401 session_expired) | erfuellt | Test #6 unknown_session_id_returns_expired |
| Original AC4 (Tag-Mismatch -> 400 + Security-Log WARNING) | erfuellt | Test #7 aead_decrypt_tag_mismatch + WARNING-Log in Code |
| Detail-AC 1 (Dependency, nicht Middleware) | erfuellt | `Depends(authenticated_session)` Pattern |
| Detail-AC 5 (nonce_format_invalid 400) | erfuellt | Test #4 wrong_length, Test #5 invalid_base64 |
| Detail-AC 8 (AAD = ASCII-Bytes) | erfuellt | Test #8 aad_mismatch_yields_aead_failed |
| Detail-AC 9 (payload_not_json 400) | erfuellt | Test #9 (non-UTF8), Test #10 (JSON-Array statt dict) |
| Detail-AC 10 (NonceTracker-Hook) | erfuellt | Test #11 nonce_replay_via_tracker, Test #13 NoOp-Default |
| Detail-AC 11 (Coverage) | erfuellt | 13 Tests, 97.8% Coverage auf authenticated_session.py |

## Verifikation

```bash
# Sandbox (ohne liboqs, AES-GCM via cryptography.hazmat verfuegbar)
cd server && python3 -m pytest tests/test_authenticated_session.py -v
# 13 passed in 5.22s

# Volle Test-Suite (kein Regress)
cd server && python3 -m pytest
# 261 passed, 5 skipped (liboqs-Skip-Pattern), 0 failed in 13.95s
```

## Wire-Format-Konformitaet (docs/wire_format.md Sec 5)

- Headers: `X-Session-Id` (Sec 5.1) + `X-Nonce` (Sec 5.1) ✓
- Body: raw octet-stream `ciphertext || tag` (Sec 5.2) ✓
- AAD: `session_id.encode("ascii")` (Sec 5.2 + neu in v0.3 explizit dokumentiert) ✓
- Error-Responses: Sec 5.4 v0.3 deckt alle 7 produzierten Codes ab ✓

## Findings (resolved + tracked)

| ID | Severity | Status |
|---|---|---|
| F-108 | Should | in-Story resolved (main.py Truncation-Hotfix + wire_format.md Truncation-Hotfix via Python-Patch-Script. Memory verschaerft auf Markdown-Files) |
| F-109 | Should | in-Story resolved (wire_format.md v0.3: Sec 5.4 erweitert, Body-Konvention `{detail: {error: ...}}`, AAD-Konvention ASCII-Bytes) |
| F-110 | May | tracked (Code-Dup `_get_facade`/`_get_session_service` mit `routers/session.py` - Sprint-4-Polish: Shared-Helper-Modul `dependencies/state.py`) |
| F-111 | Info | tracked (Coverage-Branch `nonce_tracker is None` defensive Fallback untested) |
| F-112 | Info | tracked (payload_not_json triggert kein Nonce-Recording - bewusste Entscheidung, kein Replay-Risiko) |
| F-113 | Info | tracked (`_AES_GCM_NONCE_BYTES = 12` Magic-Number, sollte aus CryptoFacade kommen wenn die einen Constant exportiert) |

## Audit-Note (User-Pushback fuer Workflow-Diszipin)

User hat zu Beginn der Story-Implementation auf das Pattern "Comprehension-Questions nach WebSearch, nicht davor" verschaerft. Resultat: Phase-1 WebSearch + Code-Review von Vor-Story-Findings + wire_format.md + risk_register lief vor den 3 Comprehension-Fragen. Damit bekam der User informierte Optionen mit Recommended-Markern statt Optionen-Salat. Memory `feedback_comprehension_questions.md` entsprechend ergaenzt.

## Links

- Code: `server/dependencies/authenticated_session.py` (330 Z), `server/services/nonce_tracker.py` (84 Z)
- Wiring: `server/main.py` (+6 Z nonce_tracker im Lifespan)
- Tests: `server/tests/test_authenticated_session.py` (451 Z, 13 Tests)
- Spec-Update: `docs/wire_format.md` v0.3 (Sec 5.4 erweitert)
- Findings-Tracking: `docs/13_deferred_findings.md` Sektion "PQC-51 DCH-2"
- Jira: https://rumidesigns.atlassian.net/browse/PQC-51
