# Demo D-008: End-to-End-Roundtrip (PQ-Session + Encrypted /api/profile)

**Status:** Server-Side komplett, App-Side noch ausstehend (APP-2/3/5/6).
**Bezug:** PQC-46 SES-1, PQC-47 SES-2, PQC-48 SES-3, PQC-49 SES-4, PQC-50 DCH-1, PQC-51 DCH-2, PQC-52 DCH-3, PQC-53 DCH-4.
**Datum:** 2026-06-30.
**Trigger:** F-100 (Mini-Demo nach DCH-3) ist erreicht.

## Was wird demonstriert

End-to-End-Pipeline ueber den vollstaendigen Server-Pfad **mit beiden
PQ-Schichten gleichzeitig**:

- **Transport-Layer-PQ:** X25519MLKEM768 im TLS-Handshake (Sprint-2
  PQC-43/44/45, nginx mit oqs-provider)
- **Application-Layer-PQ:** ML-KEM-768 fuer Session-Handshake +
  AES-256-GCM-Channel (Sprint-3 DCH-Block)

8 Schritte:

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
- Demo-User existiert. Admin-CLI liest Passwort via getpass (interaktiv)
  oder `--password-stdin` (Pipe). Sprint-1-Security-Design: kein Password
  im argv / ps / shell-history.

  **Option A (interaktiv, Prompt erscheint):**

  ```bash
  cd infra
  docker compose exec auth-service python -m admin create-user \
      --email demo@example.com
  # Prompt: 'Password: ' -> demo-passwort-12345
  ```

  **Option B (Pipe-friendly, `-T` deaktiviert TTY):**

  ```bash
  cd infra
  echo "demo-passwort-12345" | docker compose exec -T auth-service \
      python -m admin create-user \
      --email demo@example.com --password-stdin
  ```

- liboqs (oqs Python-Bindings) im Container vorhanden (Sprint-1 INF-4).

---

## Netzwerk-Topologie + BASE_URL

Aus Container-Sicht (Demo laeuft IM `auth-service`-Container):

| Endpoint | Erreichbar als | Schicht |
| --- | --- | --- |
| FastAPI direkt (kein nginx, kein TLS) | `http://localhost:8000` (Default) | App-Layer-PQ (ML-KEM + AES-GCM) |
| nginx HTTP-Proxy | `http://nginx:80` | App-Layer-PQ via Proxy |
| nginx HTTPS-Proxy (X25519MLKEM768) | `https://nginx:443` (`verify=False`) | App-Layer-PQ + Transport-Layer-PQ |

Aus Host-Sicht (Demo extern, z.B. lokales liboqs):

| Endpoint | Erreichbar als |
| --- | --- |
| nginx HTTP | `http://localhost:8080` |
| nginx HTTPS | `https://localhost:8443` |

**Default** ist `https://nginx:443` (Container-intern, durch nginx mit
X25519MLKEM768-TLS). Damit zeigt die Demo BEIDE PQ-Schichten:
Transport-Layer-PQ (TLS-Handshake) und Application-Layer-PQ (ML-KEM +
AES-GCM-Channel).

**TLS-Verify:** `verify=False` weil das Test-Cert self-signed ist (kein
echter CA-Trust). In Production wuerde das Cert von einer echten CA
kommen. Fuer Demo akzeptabel, weil der App-Layer einen eigenen
Authentication-Mechanismus hat (Broker-Token + Session-Key + AEAD-Tag),
TLS dient hier als reine Transport-Layer-Demo.

**Overrides** fuer alternative Pfade:

```bash
# FastAPI direkt (bypasst nginx, schneller fuer Iterations-Tests)
docker compose exec -e DEMO_BASE_URL=http://localhost:8000 \
    auth-service python scripts/demo_d008.py

# nginx HTTP (Reverse-Proxy, kein TLS)
docker compose exec -e DEMO_BASE_URL=http://nginx:80 \
    auth-service python scripts/demo_d008.py

# TLS-Verify einschalten (z.B. wenn Cert ins Truststore importiert)
docker compose exec -e DEMO_VERIFY_TLS=true \
    auth-service python scripts/demo_d008.py
```

## Ausfuehrung

**Wichtig (einmalig, falls Image vorher gebaut):** Nach Dockerfile-Update
Image rebuilden, damit `scripts/` und `dependencies/` im Container sind:

```bash
cd infra
docker compose build auth-service
docker compose up -d auth-service
```

**Git-Bash auf Windows konvertiert UNIX-Pfade automatisch.** Workaround:
doppelten Slash am Anfang ODER `MSYS_NO_PATHCONV=1` ODER relativen Pfad
(WORKDIR im Container ist `/app`):

```bash
# Variante A: doppelter Slash (Git-Bash-friendly)
docker compose exec auth-service python //app/scripts/demo_d008.py

# Variante B: env-Variable
MSYS_NO_PATHCONV=1 docker compose exec auth-service python /app/scripts/demo_d008.py

# Variante C: relativer Pfad (sauberste, cross-platform)
docker compose exec auth-service python scripts/demo_d008.py
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
Demo D-008: End-to-End-Roundtrip gegen https://nginx:443
Demo-User: demo@example.com
App-Layer:       ML-KEM-768 + HKDF-SHA256 + AES-256-GCM (Sprint-3 DCH-Block)
Transport-Layer: X25519MLKEM768 (nginx + oqs-provider)
TLS-Verify: False (self-signed Test-Cert in Dev)

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
