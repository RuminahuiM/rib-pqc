# Demo D-008-Vorlaeufer: Session-Init mit Algorithmus-Negotiation

**Status:** Server-Side komplett, App-Side-Vollendung nach PQC-26 CRY-6 + APP-Stories.
**Bezug:** PQC-46 SES-1, PQC-47 SES-2, PQC-48 SES-3, PQC-49 SES-4.
**Datum:** 2026-06-18.

## Was wird demonstriert

End-to-End-Pipeline der Session-Etablierung server-seitig:

1. **Token-Authentifizierung** (HTTPBearer + TokenService.verify, Sprint 1 PQC-32/33).
2. **Algorithmus-Negotiation** (SES-4 PQC-49): Server lehnt unbekannten
   kem_alg mit 406 + supported_algorithms-Liste ab.
3. **ML-KEM-Encapsulation** (CRY-4 + CRY-3 + SES-1): Server fuehrt
   `facade.kem_encaps(client_pk, kem_alg)` aus.
4. **HKDF-Session-Key-Ableitung** (CRY-3 + SES-2): Server leitet 32-Byte
   AES-256-GCM-Key aus dem shared_secret ab mit session_id als Salt und
   `b"app-session-v1"` als Domain-Info.
5. **Session-Persistenz mit TTL** (SES-3): Redis-Key `session:<id>` mit
   JSON-Record und 900s TTL.

Damit steht die Session bereit fuer Encrypted-Channel-Requests (DCH-1
bis DCH-4, kommt in PQC-50/51/52/53).

---

## Variante A: Pytest-basiert (jetzt sofort lauffaehig)

Diese Variante ist **ohne Container** lauffaehig. Sie nutzt FastAPI mit
httpx-ASGITransport gegen den Router plus fakeredis + Mock-Facade
(Mock weil liboqs in der Sandbox nicht installiert ist).

```bash
cd server
python -m pytest tests/test_session_router.py -v --no-cov
```

Erwarteter Output:
```
tests/test_session_router.py::test_session_init_happy_path_ml_kem_768 PASSED
tests/test_session_router.py::test_session_init_happy_path_ml_kem_1024 PASSED
tests/test_session_router.py::test_session_init_persists_session_in_redis PASSED
tests/test_session_router.py::test_session_init_missing_auth_returns_401 PASSED
tests/test_session_router.py::test_session_init_invalid_signature_returns_401 PASSED
tests/test_session_router.py::test_session_init_expired_token_returns_401 PASSED
tests/test_session_router.py::test_session_init_non_bearer_scheme_returns_401 PASSED
tests/test_session_router.py::test_session_init_unknown_kem_alg_returns_406 PASSED
tests/test_session_router.py::test_session_init_invalid_base64_returns_400 PASSED
tests/test_session_router.py::test_session_init_wrong_pk_length_returns_400 PASSED
tests/test_session_router.py::test_session_init_empty_kem_alg_returns_422 PASSED
tests/test_session_router.py::test_session_init_missing_body_field_returns_422 PASSED
tests/test_session_router.py::test_ses4_mismatch_response_includes_supported_algorithms_list PASSED
tests/test_session_router.py::test_ses4_client_retry_after_406_succeeds PASSED

============================== 14 passed in 0.68s ==============================
```

Besonders demo-relevant: **test_ses4_client_retry_after_406_succeeds**
zeigt den Zwei-Stufen-Roundtrip (Mismatch -> 406 + Liste -> Retry mit
gewaehltem alg -> 200 mit Session).

---

## Variante B: Container-Live-Demo (Real-liboqs, User-Aktion)

Echter End-to-End-Test gegen den pqc-auth-Container mit liboqs.

### Schritt 1: Container starten

```bash
cd infra
docker compose up -d
docker compose ps  # alle Services healthy abwarten
```

### Schritt 2: Broker-Token holen (Sprint-1 Pipeline)

```bash
TOKEN=$(curl -sk https://localhost/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@example.com","password":"demo-password-123"}' \
  | jq -r '.broker_token')
echo "Token-Prefix: ${TOKEN:0:30}..."
```

(Setze vorher per admin.py einen lokalen User mit dem demo-Passwort, oder
nutze Federated-Login PQC-40 falls eingerichtet.)

### Schritt 3a: Negotiation-Mismatch demonstrieren (406)

```bash
curl -sk https://localhost/session/init \
  -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "kem_alg": "Kyber768",
    "encapsulation_key": "AAAAAAA"
  }' | jq .
```

Erwartete Response:
```json
{
  "detail": {
    "error": "kem_alg_not_supported",
    "requested": "Kyber768",
    "supported_algorithms": ["ML-KEM-1024", "ML-KEM-768"]
  }
}
```

HTTP-Status: 406.

### Schritt 3b: Erfolgreicher Init mit ML-KEM-768

App-seitig muss ein ML-KEM-Keypair generiert werden. Fuer Demo-Zwecke
nehmen wir liboqs aus dem Container:

```bash
# In einem separaten Terminal: Public Key generieren via liboqs-CLI-Tool
# oder per docker exec im auth-service-Container:
PK_B64=$(docker compose exec -T auth python -c "
import oqs, base64
with oqs.KeyEncapsulation('ML-KEM-768') as kem:
    pk = kem.generate_keypair()
    print(base64.urlsafe_b64encode(pk).decode().rstrip('='))
")
echo "PK-Prefix: ${PK_B64:0:50}..."  # ~1579 chars total

# Session-Init
curl -sk https://localhost/session/init \
  -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"kem_alg\": \"ML-KEM-768\", \"encapsulation_key\": \"$PK_B64\"}" \
  | jq .
```

Erwartete Response:
```json
{
  "session_id": "<22-char urlsafe-base64>",
  "ciphertext": "<base64url ML-KEM ciphertext>",
  "expires_in": 900,
  "kem_alg": "ML-KEM-768"
}
```

HTTP-Status: 200.

### Schritt 4: Persistenz pruefen (Optional)

```bash
docker compose exec redis redis-cli -n 3 GET session:<id>
```

Liefert das JSON-Record mit user_id, kem_alg, session_key (base64url),
created_at, expires_at.

---

## Was diese Demo NICHT zeigt (Folge-Stories)

- **App-Side**: Retry-Loop bei 406, sowie kem.decaps + HKDF auf
  Client-Seite zur Session-Key-Wiederherstellung -> PQC-26 CRY-6.
- **Encrypted Channel**: AES-GCM-Verschluesselung von /api/profile-Calls
  ueber den abgeleiteten Session-Key -> PQC-50/51/52/53 DCH-Layer.
- **Mobile-End-to-End**: iPhone-Expo-App ruft /session/init und etabliert
  PQ-Session -> PQC-56 APP-3 + APP-Stories.

Diese fehlenden Schritte sind die Naechsten in der Sprint-3-Planung.
Sobald DCH-3 (PQC-52) und APP-3 (PQC-56) durch sind, wird daraus D-008
(Sprint-Goal-Demo "Mobile-Pfad End-to-End", siehe sprint_3/01_planning.md).

---

## Reproduzierbarkeit-Stand

| Schritt | Sandbox (Tests) | Container (User-Aktion) |
|---|---|---|
| Variante A pytest-Run | jetzt lauffaehig | n/a |
| Variante B Container-Up | n/a | User-Aktion |
| Token-Holen (Sprint-1) | n/a | User-Aktion mit User in DB |
| 406-Negotiation Demo | jetzt lauffaehig | User-Aktion |
| 200-Session-Init mit ML-KEM | jetzt lauffaehig | User-Aktion (PK-Generierung via container exec) |
| Redis-Persistenz-Check | jetzt lauffaehig | User-Aktion |
