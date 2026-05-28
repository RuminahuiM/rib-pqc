# Evidence: PQC-33 (TOK-2) - Broker-Token-Verifikation mit ML-DSA-65

**Story:** PQC-33, TOK-2, "Broker-Token-Verifikation"
**Sprint:** PQC Sprint 1 (23.05.2026 - 30.05.2026)
**Datum der Verifikation:** 28.05.2026
**Maschine:** Windows mit Docker Desktop, Git Bash (MINGW64)
**Verifiziert durch:** Dodoe (User), zusammen mit Implementation-Chat

## Was diese Evidence beweist

Der `TokenService` kann jetzt ausgestellte Broker-Tokens vollstaendig
verifizieren. Die 9-stufige fail-fast Pruefkette beweist die kryptographische
Integritaet und schuetzt vor RFC-8725-BCP-relevanten Angriffen
(alg-confusion, alg=none, Manipulation, Replay).

Sprint-1-Vollstaendigkeit Broker-Token-Layer: TOK-1 (Issue) + TOK-2 (Verify)
sind beide produktiv im Container.

## Ausgefuehrte Befehle (User-Maschine)

```bash
cd infra
docker compose down
docker compose up --build -d
docker compose logs auth-service --tail 50
docker compose exec auth-service python -c "..."
```

(Vollstaendiges Demo-Script siehe `sprint_journal/sprint_1/demos/D-003_broker_token_verify.md`)

## Output: Container-Logs nach Rebuild (NEU: erweiterte token.service.initialized Felder)

```json
{"event": "service.start", ...}
{"event": "crypto.registry.initialized", ...}
{"event": "crypto.signing_key.loaded", ...}
{"event": "crypto.facade.initialized", "default_signature_alg": "ML-DSA-65", "signing_kid": "auth-signing-key-v1", ...}
{"event": "token.service.initialized", "issuer": "pqc-auth-service", "ttl_seconds": 3600, "allowed_algs": ["ML-DSA-65"], "exp_leeway_seconds": 30, ...}
{"event": "Application startup complete.", ...}
```

**Wichtigster neuer Beleg:** das `token.service.initialized` Event traegt
jetzt die zwei neuen Felder `allowed_algs` und `exp_leeway_seconds` -
Beweis dass beide TokenConfig-Erweiterungen vom Lifespan-Hook eingelesen
und an den TokenService durchgereicht wurden.

## AC-Verifikation

| AC | Anforderung | Beweis |
|---|---|---|
| AC-1 | `token_service.verify(token_str)` liefert Claims-Dict oder wirft Sub-Exception | Container-Demo: Round-Trip liefert Claims-Dict mit allen 6 Feldern. 7 Fail-Cases werfen erwartete Sub-Exception-Typen. |
| AC-2 | Signatur-Verifikation via CryptoFacade mit `alg` und `kid` aus Header | `crypto.facade.verify` log-Event `result: true` bei good Token. Test `test_verify_round_trip_local`. |
| AC-3 | `exp`-Check mit Leeway (Default 30s, configurable), `ExpiredTokenError` | Test `test_verify_rejects_expired_token_outside_leeway` (3700s in Zukunft = abgelaufen) plus `test_verify_accepts_token_within_leeway` (3620s = innerhalb 30s Leeway). |
| AC-4 | `iss` gegen `settings.token.issuer`, `InvalidClaimError` | Live-Demo Szenario 6: `iss='evil'` -> `InvalidClaimError: iss 'evil' does not match expected 'pqc-auth-service'`. |
| AC-5 | Manipulierte Payload/Signatur, `InvalidSignatureError` | Live-Demo Szenario 5: Fake-Sig-Bytes (3309 Bytes 'X') -> `crypto.facade.verify result: false` -> `InvalidSignatureError`. Test `test_verify_rejects_tampered_signature` plus Frankenstein-Test. |
| **AC-6** | **alg-Allowlist (RFC 8725 BCP)**, case-insensitive, none blockiert | Live-Demo Szenario 3: `alg=none` blocked. Szenario 4: `alg=HS256` blocked. Parametrized Test `test_verify_rejects_alg_none_case_insensitive` (None, NONE, nOnE, none alle blockiert). |

## Code-Review-Findings (Closing-Review)

**0 Must, 0 neue Tier-1. F-028 resolved. 3 neue Tier-2-Findings.**

| ID | Titel | Severity | Tier | Status |
|---|---|---|---|---|
| F-028 | alg-Allowlist-Check (RFC 8725 BCP) | Should | 1 | resolved (in dieser Story implementiert) |
| F-031 | Verify-Errors nicht als Audit-Log-Event geloggt | Should | 2 | open, mit F-021/F-026 buendeln vor PQC-30 |
| F-032 | iat-Plausibilitaets-Check fehlt | Info | 2 | open (Sprint 3 Polish) |
| F-033 | typ-Header wird beim Verify nicht geprueft | Info | 2 | open (Sprint 3 Polish, mit F-032 buendeln) |

## Bewusste Design-Entscheidungen

- **`verify` auf bestehendem `TokenService`** statt separater `TokenVerifier`-Klasse: Issue plus Verify gehoeren semantisch zusammen, kein doppelter Lookup-Code, Tests muessen nur eine Klasse kennen.
- **9-stufige fail-fast Pruefkette** mit klar definierter Severity-Reihenfolge: erst billige strukturelle Checks (Format, Char-Allowlist), dann Claims, dann teurer Crypto-Check ganz am Ende. Spart Crypto-Resource bei manifest unsinnigen Tokens.
- **`alg=none` als hartes "no-go"**, auch wenn es in der Allowlist stuende: niemals Verify ohne Signatur (RFC 8725 BCP Pflicht).
- **case-insensitive alg-Compare** ueber Lowercase-frozenset: matched `ml-dsa-65`, `ML-DSA-65`, `Ml-DsA-65` etc. RFC 8725-bis explizit so empfohlen.
- **30s Clock-Skew-Leeway** als Sweet-Spot (Curity-Empfehlung) statt 60s OpenID-Default - NTP-synchronisierte Container haben typisch <5s Drift, kleineres Fenster ist sicherer. Configurable per `token.exp_leeway_seconds`.
- **Leeway gilt nur auf `exp`, NICHT auf `iat`** - sonst koennte ein Angreifer future-dated Tokens akzeptieren lassen (Replay-Risiko, RFC 8725 BCP).
- **`bool` aus `isinstance(exp, int)` ausgeschlossen** - Python's `bool` ist subclass von int, ohne expliziten Check wuerde `exp: true` als gueltiger NumericDate durchgehen.
- **Granular 4 Exception-Sub-Klassen** statt 1 Catch-All: in PQC-30 Login-Endpoints koennen wir damit differenziertes 401-vs-403-vs-400 Response-Handling machen.
- **Token-Char-Validation per `_VALID_TOKEN_CHARS` frozenset** (`[A-Za-z0-9-_.]`): faengt Whitespace, Curly-Braces, Code-Injection-Versuche frueh ab (RFC 8725-bis 2026 Empfehlung).

## Bewusste Limitationen

- **Verify-Errors werden nicht als Audit-Log-Event geloggt** (F-031). Bei AUT-3 vor PQC-30 mit F-021/F-026 als "Logging-Hardening"-Bundle adressieren.
- **`iat`-Plausibilitaet wird nicht geprueft** (F-032). Token-from-future als Replay-Schutz waere zusaetzliche Tiefe, aber Spec-konform optional.
- **`typ`-Header wird nicht validiert** (F-033). RFC 7515 sagt `typ` ist optional; wenn vorhanden, sollten wir gegen `"JWT"` matchen. Polish.

## Files in dieser Story

- erweitert: `server/config.py` (TokenConfig: allowed_algs, exp_leeway_seconds)
- erweitert: `server/config.yaml` (token.allowed_algs, token.exp_leeway_seconds)
- erweitert: `server/services/token_service.py` (von 188 auf 418 Zeilen):
  - 4 neue Exception-Klassen (`InvalidTokenFormatError`, `InvalidSignatureError`, `InvalidClaimError`, `ExpiredTokenError`)
  - `_b64url_decode`-Helper mit Exception-Mapping
  - `_VALID_TOKEN_CHARS` frozenset
  - `TokenService.__init__` um `allowed_algs` und `exp_leeway_seconds` erweitert
  - `TokenService.verify(token_str) -> dict` mit 9-stufiger Pruefkette
- erweitert: `server/main.py` (Lifespan reicht 2 neue Felder durch)
- erweitert: `server/tests/test_token_service.py` (von 215 auf 580 Zeilen, plus PQC-33 verify-Tests)
- erweitert: `docs/13_deferred_findings.md` (F-028 resolved, F-031/F-032/F-033 neu)
- neu: `sprint_journal/sprint_1/demos/D-003_broker_token_verify.md`
- neu: diese Evidence-Datei

## Folge-Tasks

- **PQC-30 (AUT-3 Login):** kann jetzt `app.state.token_service.issue()` plus spaeter geschuetzte Endpoints koennen `app.state.token_service.verify()` nutzen. Vor PQC-30 sollten F-021/F-026/F-031 als "Logging-Hardening"-Bundle adressiert werden.
- **F-032/F-033** als Sprint-3-Polish-Bundle.

## Quellen und Referenzen

- Jira: https://rumidesigns.atlassian.net/browse/PQC-33
- Story-Bezug: FR-Token-2, RFC 8725 BCP, `docs/07_design.md` Abschnitt 5.1
- Vorgaenger (Done): PQC-22 (CRY-2 CryptoFacade), PQC-32 (TOK-1 Issue)
- RFC 7515 (JWS Compact Serialization), RFC 7519 (JWT Claims), RFC 8725 (JWT BCP)
- Curity: JWT Security Best Practices (Clock-Skew-Sweet-Spot)
