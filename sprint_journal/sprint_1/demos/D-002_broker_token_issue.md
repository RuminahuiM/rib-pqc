# Demo D-002: Broker-Token-Ausstellung (TOK-1)

**Demo-ID:** D-002
**Datum:** 28.05.2026
**Stories integriert:** PQC-22 (CRY-2 CryptoFacade), PQC-25 (CRY-5 liboqs ML-DSA-65), PQC-32 (TOK-1 Broker-Token-Ausstellung)
**Maschine:** Windows mit Docker Desktop, Git Bash (MINGW64)
**Vorgaenger-Demo:** D-001 (Crypto-Foundation)
**Status:** funktional, Mentor-tauglich

## Was diese Demo zeigt

End-to-End-Demonstration des frisch fertigen `TokenService` aus PQC-32 im
Live-Container. Drei Szenarien:

1. **Local-Auth-Token:** User loggt sich mit Username/Password ein. Token enthaelt `auth_method: "local"`, `external_sub: null`. ML-DSA-65 Round-Trip via `CryptoFacade.verify` returned `True`.
2. **Federated-Auth-Token:** User loggt sich via Google ein. Token enthaelt `auth_method: "google"`, `external_sub: "google|aabbcc"`. Round-Trip ebenfalls `True`.
3. **Tamper-Detection:** Veraenderte signing-input-bytes fuehren zu `verify == False`. Beweist dass die Signature kryptographisch an den Token-Inhalt gebunden ist.

## Aufgesetztes Demo-Pattern

Demo nutzt `fastapi.testclient.TestClient` als Lifespan-Trigger, weil
`python -c "from main import app"` den FastAPI-Lifespan NICHT ausfuehrt und
deshalb `app.state.token_service` nicht initialisiert wuerde (Lesson aus
PQC-32-Review, F-029).

Demo-Script wird ueber `docker compose exec -T auth-service python -c "..."`
im laufenden Container ausgefuehrt - echte ML-DSA-65 Crypto via liboqs.

## Ausgefuehrter Befehl

```bash
docker compose exec auth-service python -c "
from fastapi.testclient import TestClient
from main import app

with TestClient(app) as client:
    ts = app.state.token_service
    facade = app.state.crypto_facade

    token = ts.issue('user-test-001', 'local')
    print(f'Token: {token[:60]}...{token[-20:]} (len {len(token)})')

    header_b64, payload_b64, sig_b64 = token.split('.')
    import base64, json
    def b64d(s): return base64.urlsafe_b64decode(s + '=' * (-len(s) % 4))
    header = json.loads(b64d(header_b64))
    payload = json.loads(b64d(payload_b64))
    sig = b64d(sig_b64)

    signing_input = f'{header_b64}.{payload_b64}'.encode('ascii')
    ok = facade.verify(signing_input, sig, header['alg'], header['kid'])
    print(f'Header: {header}')
    print(f'Payload: {payload}')
    print(f'verify (local-Token): {ok}')

    # Federated Round-Trip
    token2 = ts.issue('user-test-002', 'google', external_sub='google|aabbcc')
    h2, p2, s2 = token2.split('.')
    pay2 = json.loads(b64d(p2))
    sig2 = b64d(s2)
    si2 = f'{h2}.{p2}'.encode('ascii')
    head2 = json.loads(b64d(h2))
    ok2 = facade.verify(si2, sig2, head2['alg'], head2['kid'])
    print(f'Federated payload: {pay2}')
    print(f'verify (google-Token): {ok2}')

    # Tamper-Detection
    tampered = f'{h2}.{p2}TAMPER'.encode('ascii')
    ok_tamper = facade.verify(tampered, sig2, head2['alg'], head2['kid'])
    print(f'verify (tampered): {ok_tamper}  # erwartet False')
"
```

## Output (gekuerzt, structlog-JSON-Events plus Print-Output)

```text
{"event": "service.start", ...}
{"event": "crypto.registry.initialized", "kem": ["ML-KEM-768"], "signature": ["ML-DSA-65"], ...}
{"event": "crypto.signing_key.loaded", "algorithm": "ML-DSA-65", "private_key_path": "/data/keys/auth_signing_key.bin", ...}
{"event": "crypto.facade.initialized", "default_signature_alg": "ML-DSA-65", "signing_kid": "auth-signing-key-v1", "verifying_kids": ["auth-signing-key-v1"], ...}
{"event": "token.service.initialized", "issuer": "pqc-auth-service", "ttl_seconds": 3600, ...}

# --- Szenario 1: Local-Auth ---
{"event": "crypto.facade.sign", "purpose": "broker-token", "alg": "ML-DSA-65", "kid": "auth-signing-key-v1", "payload_len": 246, "signature_len": 3309, ...}
{"event": "token.issued", "sub": "user-test-001", "auth_method": "local", "external_sub_present": false, "alg": "ML-DSA-65", "kid": "auth-signing-key-v1", "iat": 1779893633, "exp": 1779897233, "ttl_seconds": 3600, "token_length": 4659, ...}

Token: eyJhbGciOiJNTC1EU0EtNjUiLCJ0eXAiOiJKV1QiLCJraWQiOiJhdXRoLXNp...AAAAAAAAAAAACRATGiIp (len 4659)

{"event": "crypto.facade.verify", "alg": "ML-DSA-65", "kid": "auth-signing-key-v1", "payload_len": 246, "signature_len": 3309, "result": true, ...}

Header: {'alg': 'ML-DSA-65', 'typ': 'JWT', 'kid': 'auth-signing-key-v1'}
Payload: {'sub': 'user-test-001', 'iss': 'pqc-auth-service', 'iat': 1779893633, 'exp': 1779897233, 'auth_method': 'local', 'external_sub': None}
verify (local-Token): True

# --- Szenario 2: Federated (Google) ---
{"event": "crypto.facade.sign", "purpose": "broker-token", "alg": "ML-DSA-65", "kid": "auth-signing-key-v1", "payload_len": 262, "signature_len": 3309, ...}
{"event": "token.issued", "sub": "user-test-002", "auth_method": "google", "external_sub_present": true, ..., "token_length": 4675, ...}
{"event": "crypto.facade.verify", ..., "result": true, ...}

Federated payload: {'sub': 'user-test-002', 'iss': 'pqc-auth-service', 'iat': 1779893633, 'exp': 1779897233, 'auth_method': 'google', 'external_sub': 'google|aabbcc'}
verify (google-Token): True

# --- Szenario 3: Tamper-Detection ---
{"event": "crypto.facade.verify", ..., "result": false, ...}
verify (tampered): False  # erwartet False
```

## Interpretation

| Szenario | Belegt |
|---|---|
| **Lifespan-Init** | Alle 5 Init-Events in der erwarteten Reihenfolge: service.start → crypto.registry.initialized → crypto.signing_key.loaded → crypto.facade.initialized → token.service.initialized. Lifespan-Hook orchestriert die Singletons korrekt. |
| **ML-DSA-65 Signature-Groesse** | `signature_len: 3309 bytes`. NIST FIPS 204 ML-DSA-65 produziert deterministisch Signaturen von 3309 Bytes. Bestaetigt dass wirklich ML-DSA-65 (und nicht Mock oder Stub) signiert. |
| **Token-Groesse** | 4659 chars fuer Local-Token (Header ~ 80, Payload ~ 350, Signature-base64url ~ 4412). Federated Token 4675 chars (16 Bytes mehr Payload fuer external_sub). Quantum-safe Authentifizierungs-Beweise sind ca. **70x groesser als RSA-2048-JWT-Tokens** (~ 350 chars). Realistischer Bandbreiten-Aspekt fuer mobile Clients. |
| **JWS-Compact-Format** | Token zerfaellt sauber in 3 base64url-Segmente ohne Padding (`=`-Zeichen). Header-Decode liefert `{alg, typ, kid}` wie spezifiziert. Payload-Decode liefert alle 6 Claims (sub, iss, iat, exp, auth_method, external_sub). |
| **TTL-Korrektheit** | `exp - iat = 1779897233 - 1779893633 = 3600`. Matched config `token.ttl_seconds: 3600`. |
| **Round-Trip Erfolg** | Beide Tokens (local plus federated) werden vom selben Service erfolgreich verifiziert. ML-DSA-65-Public-Key-Lookup ueber `kid: "auth-signing-key-v1"` funktioniert. |
| **Tamper-Detection** | Wenn die signing-input-bytes nach dem sign-Schritt veraendert werden, schlaegt verify mit `result: false` fehl. ML-DSA-65 Signature bindet kryptographisch an den exakten Header+Payload-Bytestring. |

## Mentor-Hinweis fuer 08.06.2026

Diese Demo zeigt den Schritt von "Crypto-Foundation existiert" (D-001) zu
"Crypto-Foundation wird vom Application-Layer verwendet" (D-002). Der
`TokenService` ist die erste Komponente, die `app.state.crypto_facade.sign`
produktiv benutzt. Damit ist die Crypto-Agility-Architektur (Registry +
Facade + Adapter) nicht mehr nur Unit-Test-Theorie, sondern liefert tatsaechlich
verwendbare Broker-Tokens.

Naechster funktionaler Block: TOK-2 (PQC-33) implementiert die Verifikations-
Seite der Pipeline mit alg-Allowlist-Schutz (RFC 8725 BCP). Danach D-003 als
finale "Broker-Token-Issue-plus-Verify-Pipeline".

## Quellen und Referenzen

- Story PQC-32: https://rumidesigns.atlassian.net/browse/PQC-32
- Evidence-File: `sprint_journal/sprint_1/evidence/PQC-32_TOK-1_broker_token_ausstellung.md`
- Vorgaenger-Demo: `sprint_journal/sprint_1/demos/D-001_crypto_foundation.md`
- RFC 7515 (JWS Compact), RFC 7519 (JWT Claims), RFC 8725 (JWT BCP)
- IETF Draft: draft-ietf-cose-dilithium-11 (ML-DSA for JOSE and COSE)
