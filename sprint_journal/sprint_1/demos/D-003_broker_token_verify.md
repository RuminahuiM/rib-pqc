# Demo D-003: Broker-Token Verify-Pipeline (TOK-2)

**Demo-ID:** D-003
**Datum:** 28.05.2026
**Stories integriert:** PQC-22 (CryptoFacade.verify), PQC-32 (TokenService.issue), PQC-33 (TokenService.verify mit RFC 8725 BCP)
**Maschine:** Windows mit Docker Desktop, Git Bash (MINGW64)
**Vorgaenger-Demo:** D-001 (Crypto-Foundation), D-002 (Token-Issue)
**Status:** funktional, Mentor-tauglich, **Sprint-1-Sprint-Goal-Meilenstein erreicht**

## Was diese Demo zeigt

End-to-End Broker-Token-Pipeline: Issue plus Verify mit allen RFC-8725-BCP-
Schutzschichten. Sieben Szenarien decken Happy-Path plus alle relevanten
Angriffs-Vektoren ab.

Sprint-Goal-Meilenstein: nach D-003 ist die Broker-Token-Pipeline
funktional vollstaendig. Application-Code kann jetzt:

```python
token = app.state.token_service.issue(user_id, "local")
# token wandert ueber HTTP/Header/Cookie ...
claims = app.state.token_service.verify(token)  # bei jedem geschuetzten Request
```

## Ausgefuehrter Befehl

```bash
docker compose exec auth-service python -c "
from fastapi.testclient import TestClient
from main import app
from services.token_service import (
    InvalidClaimError, InvalidSignatureError, InvalidTokenFormatError, ExpiredTokenError
)

with TestClient(app) as client:
    ts = app.state.token_service

    # Szenario 1: Happy-Path Round-Trip
    token = ts.issue('user-001', 'local')
    claims = ts.verify(token)

    # Szenario 2: Federated Round-Trip
    token2 = ts.issue('user-002', 'google', external_sub='google|abc123')
    claims2 = ts.verify(token2)

    # Szenario 3: RFC 8725 BCP alg=none Block
    # Szenario 4: alg=HS256 Allowlist-Reject
    # Szenario 5: Tampered Signature
    # Szenario 6: Wrong iss
    # Szenario 7: Format-Error (nur 2 Segmente)
    ...
"
```

(Vollstaendiges Script siehe Conversation-Log Implementation-Chat 28.05.2026.)

## Output (gekuerzt, structlog-JSON-Events plus Demo-Output)

```text
{"event": "service.start", ...}
{"event": "crypto.registry.initialized", "signature": ["ML-DSA-65"], ...}
{"event": "crypto.signing_key.loaded", ...}
{"event": "crypto.facade.initialized", "default_signature_alg": "ML-DSA-65", ...}
{"event": "token.service.initialized", "issuer": "pqc-auth-service", "ttl_seconds": 3600, "allowed_algs": ["ML-DSA-65"], "exp_leeway_seconds": 30, ...}

=== 1. Happy-Path Round-Trip ===
{"event": "crypto.facade.sign", "alg": "ML-DSA-65", "signature_len": 3309, ...}
{"event": "token.issued", "sub": "user-001", "token_length": 4652, ...}
{"event": "crypto.facade.verify", "result": true, ...}
{"event": "token.verified", "sub": "user-001", "alg": "ML-DSA-65", "kid": "auth-signing-key-v1", ...}
  verified, sub=user-001, auth_method=local

=== 2. Federated Round-Trip ===
{"event": "token.issued", "sub": "user-002", "auth_method": "google", ...}
{"event": "crypto.facade.verify", "result": true, ...}
{"event": "token.verified", "auth_method": "google", ...}
  verified, external_sub=google|abc123

=== 3. RFC 8725: alg=none rejected ===
  OK rejected: alg=none is explicitly forbidden (RFC 8725 BCP)

=== 4. alg=HS256 rejected (alg-confusion guard) ===
  OK rejected: alg 'HS256' is not in allowlist ['ML-DSA-65'] (RFC 8725 BCP alg-confusion guard)

=== 5. Tampered Signature ===
{"event": "crypto.facade.verify", "result": false, ...}
  OK rejected: signature verification failed

=== 6. Wrong iss ===
  OK rejected: iss 'evil' does not match expected 'pqc-auth-service'

=== 7. Format-Error: only 2 segments ===
  OK rejected: token must have exactly 3 segments separated by '.', got 2

ALL VERIFY-SCENARIOS PASSED
```

## Interpretation

| Szenario | Belegt |
|---|---|
| **Lifespan-Init** | Neue Felder `allowed_algs` und `exp_leeway_seconds` werden korrekt aus Config gelesen und an TokenService durchgereicht. |
| **Happy-Path Issue+Verify** | TokenService kann seine eigenen Tokens via 9-stufige verify-Pruefkette validieren. Beide Events (`token.issued` plus `token.verified`) erscheinen sauber im Log. |
| **Federated Variant** | `auth_method=google` plus `external_sub` durchlaufen denselben Pfad unveraendert. |
| **RFC 8725 BCP `alg=none` Block** | Selbst wenn ein Angreifer einen Token mit `alg=none` baut (klassische JWT-Vulnerability), wird er hart abgelehnt. Case-insensitive Test (None/NONE/nOnE in pytest) ebenfalls green. |
| **alg-confusion Schutz** | HS256-Token (RSA-vs-HMAC-Verwechslung im JWT-Universum) ist ein bekannter Angriffsvektor. Allowlist `["ML-DSA-65"]` blockiert. |
| **Tamper-Detection** | Strukturell gueltiger Token mit zufaelligen 3309-Byte-Signature schlaegt durch ML-DSA-65-verify fehl. Beweist kryptographische Integritaet. |
| **iss-Check** | Token mit gefakter `iss='evil'` wird abgelehnt. Verhindert Issuer-Substitution-Attacks. |
| **Format-Error** | Strukturell defekte Tokens (zu wenige Segmente, ungueltige Chars) werden VOR dem teuren Crypto-Check abgelehnt - Fail-Fast-Prinzip. |

## Sprint-Goal-Meilenstein-Aussage

Mit D-003 ist die Broker-Token-Pipeline funktional vollstaendig. Sprint 1
hat damit das initial geplante Sprint-Goal "ML-DSA-65 als Signatur-Schicht
fuer authentifizierte Tokens" erreicht. Naechste Stories (PQC-30 AUT-3
Login, Sprint 2 Broker-Stories) koennen direkt auf
`app.state.token_service.issue/verify` aufbauen.

## Mentor-Hinweis fuer 08.06.2026

Diese Demo ist Bewertungs-relevant: sie zeigt nicht nur die positive
Funktionalitaet (Issue+Verify), sondern explizit die Schutz-Schichten
gegen die haeufigsten JWT-Angriffe (RFC 8725 BCP-Konformitaet). Damit
ist die Crypto-Agility-Architektur (CRY-1 Registry plus CRY-5 Adapter
plus CRY-2 Facade plus TOK-1/2 Application-Layer) End-to-End
demonstriert.

Optional fuer Mentor-Termin: Live-Demo der 7 Szenarien wiederholen, plus
die strukturierte Log-Pipeline `token.issued` -> `crypto.facade.sign` ->
`crypto.facade.verify` -> `token.verified` zeigen.

## Quellen und Referenzen

- Story PQC-33: https://rumidesigns.atlassian.net/browse/PQC-33
- Evidence-File: `sprint_journal/sprint_1/evidence/PQC-33_TOK-2_broker_token_verifikation.md`
- Vorgaenger-Demos: `D-001_crypto_foundation.md`, `D-002_broker_token_issue.md`
- RFC 7515 (JWS Compact), RFC 7519 (JWT Claims), RFC 8725 (JWT BCP)
- Curity: JWT Security Best Practices
