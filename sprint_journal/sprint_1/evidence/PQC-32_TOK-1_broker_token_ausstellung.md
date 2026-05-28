# Evidence: PQC-32 (TOK-1) - Broker-Token-Ausstellung mit ML-DSA-65

**Story:** PQC-32, TOK-1, "Broker-Token-Ausstellung mit ML-DSA-65"
**Sprint:** PQC Sprint 1 (23.05.2026 - 30.05.2026)
**Datum der Verifikation:** 28.05.2026 (Wochenend-Slot)
**Maschine:** Windows mit Docker Desktop, Git Bash (MINGW64)
**Verifiziert durch:** Dodoe (User), zusammen mit Implementation-Chat

## Was diese Evidence beweist

Der Auth-Service kann jetzt Broker-Tokens im JWS-Compact-Format ausstellen,
signiert mit ML-DSA-65 ueber die `CryptoFacade`. Ein neuer `TokenService` lebt
als Singleton in `app.state.token_service` und wird im Lifespan-Hook gegen
die `CryptoFacade` dependency-injiziert. Application-Code wird in spaeteren
Stories ueber `request.app.state.token_service.issue(...)` Tokens ausstellen.

Token-Layout (RFC 7515 JWS Compact, RFC 7519 JWT Claims):

```
eyJhbGciOiJNTC1EU0EtNjUiLCJ0eXAiOiJKV1QiLCJraWQiOiJhdXRoLXNp...  (Header)
.eyJzdWIiOiJ1c2VyLXRlc3QtMDAxIiwiaXNzIjoicHFjLWF1dGgtc2Vy...  (Payload)
.AAAAAAAAAAAACRATGiIp                                          (Signature)
```

mit Header `{"alg": "ML-DSA-65", "typ": "JWT", "kid": "auth-signing-key-v1"}`
und Payload `{"sub", "iss", "iat", "exp", "auth_method", "external_sub"}`.

Verifikations-Round-Trip durch dieselbe `CryptoFacade.verify` ist live
gegen den Container bestaetigt.

## Ausgefuehrte Befehle

```bash
cd infra
docker compose down
docker compose up --build -d
docker compose logs auth-service --tail 50

docker compose exec auth-service python -c "
from fastapi.testclient import TestClient
from main import app
with TestClient(app) as client:
    ts = app.state.token_service
    facade = app.state.crypto_facade
    token = ts.issue('user-test-001', 'local')
    print(f'Token: {token[:60]}...{token[-20:]} (len {len(token)})')
    ...
"
```

(Vollstaendiger Test-Script-Aufruf siehe Demo D-002.)

## Output: Container-Logs nach Rebuild

```json
{"event": "service.start", ..., "host": "0.0.0.0", "port": 8000, "log_level": "info"}
{"event": "crypto.registry.initialized", ..., "kem": ["ML-KEM-768"], "signature": ["ML-DSA-65"]}
{"event": "crypto.signing_key.loaded", ..., "algorithm": "ML-DSA-65", "private_key_path": "/data/keys/auth_signing_key.bin"}
{"event": "crypto.facade.initialized", ..., "default_signature_alg": "ML-DSA-65", "signing_kid": "auth-signing-key-v1", "verifying_kids": ["auth-signing-key-v1"]}
{"event": "token.service.initialized", ..., "issuer": "pqc-auth-service", "ttl_seconds": 3600}
{"event": "Application startup complete.", ...}
{"event": "Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)", ...}
```

**Wichtigster Beleg:** das neue `token.service.initialized` Event mit
`issuer=pqc-auth-service` und `ttl_seconds=3600`. Beweist dass der
`TokenService` im Lifespan instantiiert wurde und in `app.state.token_service`
liegt.

## Output: Live Token-Issue plus Verify im Container

```text
{"event": "crypto.facade.sign", "purpose": "broker-token", "alg": "ML-DSA-65", "kid": "auth-signing-key-v1", "payload_len": 246, "signature_len": 3309, ...}
{"event": "token.issued", "sub": "user-test-001", "auth_method": "local", "external_sub_present": false, "alg": "ML-DSA-65", "kid": "auth-signing-key-v1", "iat": 1779893633, "exp": 1779897233, "ttl_seconds": 3600, "token_length": 4659, ...}

Token: eyJhbGciOiJNTC1EU0EtNjUiLCJ0eXAiOiJKV1QiLCJraWQiOiJhdXRoLXNp...AAAAAAAAAAAACRATGiIp (len 4659)

{"event": "crypto.facade.verify", "alg": "ML-DSA-65", "kid": "auth-signing-key-v1", "payload_len": 246, "signature_len": 3309, "result": true, ...}
Header: {'alg': 'ML-DSA-65', 'typ': 'JWT', 'kid': 'auth-signing-key-v1'}
Payload: {'sub': 'user-test-001', 'iss': 'pqc-auth-service', 'iat': 1779893633, 'exp': 1779897233, 'auth_method': 'local', 'external_sub': None}
verify (local-Token): True

{"event": "token.issued", "sub": "user-test-002", "auth_method": "google", "external_sub_present": true, ...}
{"event": "crypto.facade.verify", ..., "result": true}
Federated payload: {'sub': 'user-test-002', 'iss': 'pqc-auth-service', ..., 'auth_method': 'google', 'external_sub': 'google|aabbcc'}
verify (google-Token): True

{"event": "crypto.facade.verify", ..., "result": false}
verify (tampered): False
```

## AC-Verifikation

| AC | Anforderung | Beweis |
|---|---|---|
| AC-1 | `token_service.issue(user_id, auth_method, external_sub)` liefert Token-String | `services/token_service.py::TokenService.issue` returned `str`. Container-Demo zeigt Token-Output 4659 chars. |
| AC-2 | JWS-Compact-Format: `base64url(header).base64url(payload).base64url(signature)` | Token-Split per `.` ergibt 3 base64url-Segmente, jedes ohne Padding (`=`). Tests `test_issue_returns_three_base64url_segments` plus Demo-Decode. |
| AC-3 | Header enthaelt `alg`, `typ: "JWT"`, `kid` aus Crypto-Facade | Live-Decode `{'alg': 'ML-DSA-65', 'typ': 'JWT', 'kid': 'auth-signing-key-v1'}`. Test `test_issue_header_contains_alg_typ_kid`. |
| AC-4 | Payload enthaelt `sub`, `iss`, `iat`, `exp`, `auth_method`, optional `external_sub` | Live-Decode zeigt alle 6 Felder. `external_sub: None` bei local, `external_sub: "google\|aabbcc"` bei federated. Test `test_issue_payload_contains_required_claims`. |
| AC-5 | TTL aus `token.ttl_seconds` (Config) | `exp - iat = 3600` bei Default. Test `test_issue_exp_equals_iat_plus_ttl` (parametrisiert mit 7200). Config-Loading-Test zeigt `token.ttl_seconds=3600`. |

Zusatzlich:
- Round-Trip `CryptoFacade.verify(signing_input, signature, alg, kid) == True` fuer local plus federated.
- Tamper-Detection: veraenderte signing_input fuehrt zu `verify == False`.

## Code-Review-Findings (Closing-Review)

**0 Must-Findings. 1 Tier-1-Should-Finding mit Story-Trigger (PQC-33). 5 Tier-2-Findings.**

| ID | Titel | Severity | Tier | Status |
|---|---|---|---|---|
| F-025 | `AuthMethod` Literal deklariert aber `issue()` nutzt `str` plus Runtime-Whitelist | Info | 2 | open |
| F-026 | `sub`-Claim wird auf INFO-Level pro Issue geloggt | Should | 2 | open, mit F-021 buendeln |
| F-027 | Kein `jti` (JWT ID), RFC 8725 BCP empfiehlt Replay-Protection | May | 2 | open |
| F-028 | TOK-2 (PQC-33) MUSS alg-Allowlist-Check haben (RFC 8725 BCP) | Should | 1+2 | direkt in PQC-33 AC einarbeiten |
| F-029 | `from main import app` ohne TestClient triggert Lifespan nicht | Info | 2+3 | Memory `pqc-demo-convention` geupdated |
| F-030 | server/README.md erwaehnt `services/`-Subpackage noch nicht | Info | 2 | Sprint 4 Doku-Polish |

Alle Findings sind in `docs/13_deferred_findings.md` getrackt.

## Bewusste Design-Entscheidungen

- **`token.issuer` als Config-Feld, getrennt vom internen `app_name`.** Damit bricht ein Rebrand des Service-Namens nicht alle bereits ausgestellten Tokens. Default `pqc-auth-service` matched Design 5.1.
- **`TokenService` als framework-unabhaengige Klasse** (kein FastAPI-Coupling). Reuse-faehig in CLI-Tools oder anderen Web-Frameworks, Tests muessen kein TestClient hochziehen.
- **Dependency-Injection via Konstruktor:** CryptoFacade, issuer, ttl_seconds und optional clock-Funktion. Tests injizieren `fixed_clock`, Container nutzt `time.time`.
- **`external_sub` immer im Payload, `None` bei local-Auth.** Damit ist die JSON-Struktur konstant unabhaengig vom auth_method. Konsistent zu Design 5.1.
- **`auth_method` als Runtime-Whitelist `frozenset({"local", "google", "microsoft"})`.** Sprint 1 nur lokale Methode aktiv, federated kommt mit Broker-Stories. Whitelist macht Erweiterung explizit.
- **Defensive Konsistenz-Pruefung** nach `Facade.sign`: `header.alg/kid` muss `sign`-Result-Tupel matchen. Schuetzt vor stillschweigender Misskonfiguration.
- **JSON-Serialisierung kompakt** (`separators=(',', ':')`) ohne sort_keys. Python 3.7+ garantiert dict-insertion-order, also deterministische bytes.
- **base64url ohne Padding** per RFC 7515 Anhang C (`rstrip(b"=")`).

## Bewusste Limitationen

- **`sub` wird auf INFO-Level geloggt** (F-026). Bei AUT-3 Login-Hochfrequenz auf DEBUG reduzieren, mit F-021 buendeln.
- **Kein `jti`** im Token (F-027). Replay-Protection ueber TTL (1h) plus zukuenftiges Session-Layer. RFC 8725 BCP-Empfehlung als deferred.
- **Privater Attribut-Zugriff auf Facade** (`_default_signature_alg`, `_signing_kid`) im `_lookup_signing_metadata`. Sauberer waere ein Getter `facade.signing_metadata()`. Bereits in F-024 dokumentiert, kein neues Finding.
- **`AuthMethod` Literal-Type ist deklariert, aber Parameter ist `str`** (F-025). Konsistent mit Pattern "extern eingehende Daten via Runtime-Whitelist validieren", aber Literal koennte beim naechsten Touch besser ausgenutzt werden.

## Files in dieser Story

- `server/services/__init__.py` (neu, Package-Marker mit Hinweis auf Folge-Sprint-Services)
- `server/services/token_service.py` (neu, 188 Zeilen, TokenService-Klasse)
- `server/main.py` (erweitert: TokenService-Import, Lifespan-Instantiierung, `app.state.token_service`)
- `server/config.py` (erweitert: `TokenConfig` mit `issuer` plus `ttl_seconds`)
- `server/config.yaml` (neuer `token:` Block)
- `server/Dockerfile` (erweitert: `COPY services ./services`)
- `server/pyproject.toml` (hatch only-include plus mypy.files erweitert um `services`)
- `server/tests/test_token_service.py` (neu, 14 Tests mit Round-Trip ueber echte LibOqsSignature)
- `docs/13_deferred_findings.md` (neuer PQC-32 Review-Abschnitt mit F-025 bis F-030)
- `sprint_journal/sprint_1/demos/D-002_*.md` (Integration-Demo, separate Datei)
- `sprint_journal/sprint_1/evidence/PQC-32_TOK-1_broker_token_ausstellung.md` (diese Datei)

## Folge-Tasks

- **PQC-33 (TOK-2 Broker-Token-Verifikation):** kann jetzt `app.state.crypto_facade.verify()` direkt nutzen, plus muss F-028 (alg-Allowlist gegen RFC 8725 BCP) als zusaetzlichen AC einarbeiten.
- **PQC-30 (AUT-3 Login):** kann jetzt `app.state.token_service.issue(user_id, "local")` nach erfolgreichem Login aufrufen. Vor PQC-30 sollten F-021 (sign/verify-Log-Frequency) und F-026 (sub-Log-Frequency) als Bundle gefixt werden.

## Quellen und Referenzen

- Jira: https://rumidesigns.atlassian.net/browse/PQC-32
- Story-Bezug: FR-Token-1, `docs/07_design.md` Abschnitt 5.1
- Vorgaenger (Done): PQC-22 (CRY-2 CryptoFacade), PQC-25 (CRY-5 liboqs ML-DSA-65)
- RFC 7515 (JWS Compact Serialization), RFC 7519 (JWT Claims), RFC 8725 (JWT BCP)
- IETF Draft: draft-ietf-cose-dilithium-11 (ML-DSA for JOSE and COSE)
