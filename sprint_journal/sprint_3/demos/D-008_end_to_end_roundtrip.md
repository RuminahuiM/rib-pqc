# Demo D-008: End-to-End-Roundtrip (PQ-Session + Encrypted /api/profile)

**Status:** Server-Side komplett, App-Side noch ausstehend (APP-2/3/5/6).
**Bezug:** PQC-46 SES-1, PQC-47 SES-2, PQC-48 SES-3, PQC-49 SES-4, PQC-50 DCH-1, PQC-51 DCH-2, PQC-52 DCH-3, PQC-53 DCH-4.
**Datum:** 2026-06-30.
**Trigger:** F-100 (Mini-Demo nach DCH-3) ist erreicht.

## Was wird demonstriert

End-to-End-Pipeline ueber den vollstaendigen Server-Pfad in 8 Schritten:

1. **Login -> Broker-Token** (Sprint 1 AUT-3 + TOK-1, ML-DSA-65 signiert)
2. **ML-KEM-768 Keypair Client-Side** (liboqs-python)
3. **POST /session/init** (PQC-46 SES-1): Server-Encapsulation, session_id + ciphertext zurueck
4. **KEM-Decaps + HKDF Client-Side** (PQC-47 SES-2): 32-Byte AES-256-GCM-Key abgeleitet
5. **AES-256-GCM Encrypt** (PQC-50 DCH-1): Profile-Request `{}` mit Nonce + AAD verschluesselt
6. **POST /api/profile** (PQC-52 DCH-3): Server entschluesselt via DCH-2-Dependency, laed User-Profile aus DB
7. **Decrypt Response** (PQC-52 DCH-3): X-Nonce-Header + verschluesselter Body -> Klartext-Profile
8. **Replay-Test** (PQC-53 DCH-4): zweiter Request mit gleicher Nonce -> 400 nonce_reused

---

## Voraussetzungen

- Server lauft (docker compose up).
- Demo-User existiert. Anlegen mit:

  ```bash
  cd infra
  docker compose exec auth-service python -m admin create-user \
      --email demo@example.com \
      --password demo-passwort-12345
  ```

- liboqs (oqs Python-Bindings) im Container vorhanden (Sprint-1 INF-4).

---

## Ausfuehrung

```bash
# Aus dem infra/-Ordner heraus:
docker compose exec auth-service python /app/scripts/demo_d008.py
```

Optional via Environment-Variablen ueberschreiben:

```bash
docker compose exec -e DEMO_EMAIL=alice@example.com \
                    -e DEMO_PASSWORD=geheim42 \
                    -e DEMO_BASE_URL=http://localhost:8080 \
                    auth-service python /app/scripts/demo_d008.py
```

---

## Erwarteter Output (gekuerzt)

```
Demo D-008: End-to-End-Roundtrip gegen http://localhost:8080
Demo-User: demo@example.com
KEM: ML-KEM-768, AEAD: AES-256-GCM, KDF: HKDF-SHA256

=== Schritt 1: Login -> Broker-Token ===
Token preview: eyJhbGciOiJNTC1EU0EtNjUi... (3245 chars)
Status: OK

=== Schritt 2: ML-KEM-768 Keypair Client-Side ===
client_pk: 9e3a1b... (1184 bytes)
client_sk: 7b21cf... (2400 bytes) (NEVER print outside demo)

=== Schritt 3: POST /session/init -> session_id + ciphertext ===
session_id: B3wMqL7Yz0fXn2Pt9KaTrA (22 chars)
ciphertext: 4dfa2c... (1088 bytes)
expires_in: 900s
Status: OK

=== Schritt 4: KEM-Decaps + HKDF-Session-Key ===
shared_secret: 1a8b2e... (32 bytes)
session_key: 99c8db... (32 byte AES-256-GCM-Key)
Status: OK

=== Schritt 5: Encrypt Profile-Request mit AES-256-GCM ===
plaintext: b'{}'
X-Nonce: <12-byte b64>
X-Session-Id: B3wMqL7Yz0fXn2Pt9KaTrA
body (ct||tag): 5cfa3d... (18 bytes)
Status: OK

=== Schritt 6: POST /api/profile ===
HTTP 200
Content-Type: application/octet-stream
X-Nonce (response): <12-byte b64, andere Nonce!>
response body: 8af1bc... (~150 bytes)
Status: OK

=== Schritt 7: Decrypt Response + Profile-Plaintext ===
profile (Klartext): {
  "user_id": "11111111-1111-1111-1111-111111111111",
  "email": "demo@example.com",
  "auth_method": "local",
  "created_at": "2026-06-30T10:00:00Z"
}
Status: OK

=== Schritt 8: Replay-Test - gleiche Nonce nochmal -> 400 nonce_reused ===
HTTP 400
body: {"detail": {"error": "nonce_reused"}}
Status: OK (Replay korrekt erkannt)

=== DEMO D-008 KOMPLETT ===
Alle 8 Schritte erfolgreich. Encrypted Channel funktioniert E2E.
```

---

## Was die Demo belegt

- **AC-1 Sprint-3-Goal (Mobile-Demo D-008-Pendant Server-Side):** Token + Session-Init + Encrypted-Profile-Roundtrip + Replay-Schutz funktional komplett.
- **NFR-Sec-2 (Replay-Schutz):** Schritt 8 zeigt 400 nonce_reused live.
- **UC-5 Hauptablauf:** Schritte 5-7 sind buchstaeblich UC-5-Schritte 1-9.
- **FIPS-203 Implicit-Rejection (F-090):** Indirekt - bei falscher PK liefert decap ein Garbage-Secret, Schritt 6 wuerde mit aead_decrypt_failed 400 antworten (nicht in der Happy-Path-Demo gezeigt, aber Test-Suite #7 in test_authenticated_session.py).

## Video-Aufnahme fuer Mentor-Material

Empfohlene Tools (Mac): QuickTime Player ("Bildschirmaufnahme..." -> Terminalbereich auswaehlen). Linux: `peek` oder `kazam`.

Aufgenommenes Video kann in `sprint_journal/sprint_3/demos/D-008_video.mov` (oder mp4) gespeichert werden (User-Bereich). Empfohlene Lauflaenge: 90-120 Sekunden.

---

## Links

- Script: `server/scripts/demo_d008.py` (224 Z)
- Vorlaeufer-Demo: `D-008-vorlaeufer_session_init_with_negotiation.md`
- Server-Endpoints: `server/routers/session.py` + `server/routers/api.py`
