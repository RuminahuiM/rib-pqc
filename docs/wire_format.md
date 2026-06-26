# Wire-Format und Krypto-Artefakte

**Story:** PQC-27 CRY-7 (FR-Crypto-3).
**Sprint:** 3.
**Stand:** 2026-06-18.

Dieses Dokument beschreibt das Wire-Format aller Krypto-Artefakte
in rib-pqc und stellt sicher dass jeder Artefakt seinen verwendeten
Algorithmus selbst-deklariert. Crypto-Agility-Prinzip: jeder Artefakt
fuehrt den Algorithmus mit, damit ein Wechsel ohne Schema-Change
moeglich ist.

---

## 1. Algorithmus-Whitelisten (Sprint-3-Stand)

| Domain | Erlaubte Werte | Quelle |
| --- | --- | --- |
| Signatur (`alg`) | `ML-DSA-65` | `crypto/registry_init.py _SUPPORTED_SIGNATURE_ALGORITHMS`, FIPS 204 |
| KEM (`kem_alg`) | `ML-KEM-768`, `ML-KEM-1024` | `crypto/registry_init.py _SUPPORTED_KEM_ALGORITHMS`, FIPS 203 |
| KDF | `HKDF-SHA256` | `crypto/facade.py hkdf()`, RFC 5869 |
| AEAD | `AES-256-GCM` | `crypto/facade.py aead_encrypt/decrypt`, NIST SP 800-38D |

Pre-Standard-Namen (`Kyber768`, `Dilithium3`) sind explizit verboten und
werden bei Registry-Init mit `UnsupportedAlgorithmError` abgelehnt.

---

## 2. Broker-Token (JWS-Compact, Sprint 1 PQC-32/33)

**Format:** `<base64url(header)>.<base64url(payload)>.<base64url(signature)>`

**Header (JSON):**

```json
{
  "alg": "ML-DSA-65",
  "typ": "JWT",
  "kid": "auth-signing-key-v1"
}
```

- `alg` (string, **Pflicht**): Signatur-Algorithmus. Sprint-3-Whitelist erlaubt
  nur `ML-DSA-65`. `alg=none` und Case-Varianten werden vom TokenService
  abgelehnt (RFC 8725 BCP).
- `kid` (string, **Pflicht**): Key-ID die im Lookup
  `verifying_keys_by_kid` aufgeloest wird. Aktuell `auth-signing-key-v1`.
- `typ` (string, optional): `"JWT"` zur RFC-7519-Kompatibilitaet.

**Payload (JSON):**

```json
{
  "iss": "pqc-auth-service",
  "sub": "<user-id>",
  "iat": 1718700000,
  "exp": 1718703600,
  "auth_method": "local|federated-google|federated-microsoft",
  "external_sub": null
}
```

**Signatur:** ML-DSA-65 ueber die ASCII-Bytes von `header_b64.payload_b64`.

---

## 3. Session-Init Wire-Format (PQC-46 SES-1)

### 3.1 Request `POST /session/init`

```json
{
  "kem_alg": "ML-KEM-768",
  "encapsulation_key": "<base64url(ML-KEM public key, 1184 byte)>"
}
```

- `kem_alg` (string, **Pflicht**): KEM-Algorithmus den der Client unterstuetzt.
  Server prueft per `CryptoFacade.is_kem_supported`. Bei unbekanntem Wert
  Response 406 `Not Acceptable` mit `supported_algorithms`-Liste (siehe SES-4).
- `encapsulation_key` (string base64url, **Pflicht**): ML-KEM-Public-Key des
  Clients (KEM-Encapsulation-Empfaenger). Laenge je nach `kem_alg`:
  ML-KEM-768 = 1184 Byte, ML-KEM-1024 = 1568 Byte.

**Headers:** `Authorization: Bearer <broker-token>` (validiert via TokenService).

### 3.2 Response `200 OK`

```json
{
  "session_id": "<urlsafe-base64, 16 byte raw>",
  "ciphertext": "<base64url(ML-KEM ciphertext)>",
  "expires_in": 900,
  "kem_alg": "ML-KEM-768"
}
```

- `session_id` (string, **Pflicht**): Server-erzeugter Identifier (CSPRNG
  16 Byte, urlsafe-base64). Wird als Redis-Schluessel `session:<id>`
  verwendet und als `X-Session-Id`-Header in nachfolgenden Requests
  mitgeschickt.
- `ciphertext` (string base64url, **Pflicht**): ML-KEM-Ciphertext aus
  `facade.kem_encaps`. Laenge je nach kem_alg: ML-KEM-768 = 1088 Byte,
  ML-KEM-1024 = 1568 Byte. Client decapsuliert mit seinem Secret-Key.
- `expires_in` (integer, **Pflicht**): Sekunden bis Session-TTL Ablauf,
  aus `settings.session.ttl_seconds` (zu ergaenzendes Config-Feld in PQC-48 SES-3) (Default 900 = 15 Minuten).
- `kem_alg` (string, **Pflicht**): Echo des Algorithmus zum Selbst-Deklaration
  der Session.

### 3.3 Response `406 Not Acceptable` (SES-4 Algorithmus-Negotiation)

```json
{
  "error": "kem_alg_not_supported",
  "requested": "Kyber768",
  "supported_algorithms": ["ML-KEM-1024", "ML-KEM-768"]
}
```

Server-Liste kommt aus `facade.supported_kem_algorithms()`. Client soll
Request mit einem unterstuetzten Algorithmus wiederholen.

---

## 4. Session-Record (Redis-Schema, PQC-48 SES-3)

**Schluessel:** `session:<session_id>`
**Wert:** JSON-Blob, TTL aus `settings.session.ttl_seconds` (zu ergaenzendes Config-Feld in PQC-48 SES-3, Default 900 Sekunden).

```json
{
  "user_id": "<broker-token sub>",
  "kem_alg": "ML-KEM-768",
  "session_key": "<base64url(HKDF-output, 32 byte)>",
  "created_at": 1718700000,
  "expires_at": 1718700900
}
```

- `user_id`: aus dem verifizierten Broker-Token sub-Claim.
- `kem_alg`: zur Selbst-Deklaration. Algorithmus-Wechsel ueber neue
  Session-Init, alte Session bleibt unveraendert bis TTL Expiry.
- `session_key`: HKDF-SHA256-Output aus `facade.hkdf(ikm=shared_secret,
  info=b"app-session-v1", salt=session_id)`. 32 Byte (AES-256-GCM-Key).
  In Redis als base64url-no-pad gespeichert. **Niemals in Logs.**
- `created_at`: unix-Sekunden int, fuer Debug-Forensik.
- `expires_at`: unix-Sekunden int = created_at + ttl_seconds.

---

## 5. Encrypted-Channel Wire-Format (PQC-50/51/52/53 DCH-*)

### 5.1 Request-Headers (alle geschuetzten Endpoints)

| Header | Wert | Story |
| --- | --- | --- |
| `X-Session-Id` | urlsafe-base64 (session_id) | DCH-2 (PQC-51) |
| `X-Nonce` | base64url (12 byte CSPRNG, einmalig pro Session) | DCH-2 + DCH-4 |
| `Authorization` | `Bearer <broker-token>` (optional, falls Endpoint Token-Authentifizierung zusaetzlich braucht) | AUT-1 |

### 5.2 Request-Body (verschluesselter Payload)

```text
Content-Type: application/octet-stream
Body: <ciphertext_and_tag>  // raw bytes, AES-256-GCM
```

`ciphertext_and_tag` = Output von `facade.aead_encrypt(session_key, nonce,
plaintext, aad=session_id)`. Tag (16 Byte) ist hinten konkatenert.

**AAD (Additional Authenticated Data):** `session_id` als Bytes. Bindet die
Verschluesselung an die Session, verhindert Cross-Session-Replay (Defense-
in-Depth zusaetzlich zur Nonce-Tracking aus DCH-4).

### 5.3 Response-Body

Gleiche Struktur wie 5.2, aber mit frischer Nonce (`X-Response-Nonce`-Header
falls Client den Tag selbst pruefen muss). Konkrete Konvention wird in
PQC-52 DCH-3 finalisiert.

### 5.4 Fehler-Responses

**Body-Konvention (PQC-51 DCH-2):** alle Fehler liefern FastAPI-idiomatisch
`{"detail": {"error": "<code>"}}`. Konsistent mit POST /session/init (PQC-46).

| Status | Detail-Error | Trigger |
| --- | --- | --- |
| 401 | `session_missing` | `X-Session-Id`-Header fehlt |
| 401 | `nonce_missing` | `X-Nonce`-Header fehlt |
| 400 | `nonce_format_invalid` | `X-Nonce` kein base64url oder Laenge != 12 Byte (NIST SP 800-38D Section 8.2 Empfehlung). F-092 Implementation. |
| 401 | `session_expired` | session_id nicht in Redis (TTL abgelaufen oder unbekannt). Side-Channel-Schutz: kein Unterschied zwischen never-existed und expired. |
| 400 | `nonce_reused` | Nonce schon getrackt (DCH-4 Replay-Schutz, PQC-53). |
| 400 | `aead_decrypt_failed` | AEAD-Tag-Mismatch (`CryptoFacade.AeadDecryptError`). **Security-Log-Eintrag mit Severity WARNING.** |
| 400 | `payload_not_json` | Plaintext ist kein gueltiges UTF-8 JSON oder JSON-Top-Level ist nicht `dict` (Endpoint-Konvention). |

**AAD-Konvention:** AAD = `session_id.encode("ascii")`, identisch zwischen
Server (`dependencies/authenticated_session.py`) und App (`@noble/ciphers`).

---

## 6. Algorithmus-Wechsel-Mechanik

Sprint-3-Defaults: `ML-DSA-65` (Signatur), `ML-KEM-768` (KEM), `HKDF-SHA256`
(KDF), `AES-256-GCM` (AEAD).

**Wechsel-Pfade fuer Crypto-Agility:**

1. **Signatur-Algorithmus ersetzen** (z.B. zukuenftiger Hash-basierter Algo):
   - Neuer Adapter in `crypto/adapters/`.
   - Whitelist in `crypto/registry_init.py _SUPPORTED_SIGNATURE_ALGORITHMS`.
   - Neuer `signing_kid` in der Config, alter `kid` bleibt im Lookup damit
     bestehende Tokens verifiziert werden koennen (Schluessel-Rollover).
   - Token-Header trägt automatisch den neuen `alg`+`kid` durch
     `facade.sign()`-Output.

2. **KEM-Algorithmus ersetzen oder zweite Variante zulassen** (z.B. ML-KEM-1024
   parallel zu ML-KEM-768):
   - Whitelist erweitern, neuer Adapter wenn nicht ML-KEM (LibOqsKem deckt
     beide ML-KEM-Varianten).
   - Session-Init-Request gibt `kem_alg`-Wert vor, Server akzeptiert wenn
     in Whitelist.
   - Session-Record speichert `kem_alg`. Mischbetrieb verschiedener KEMs
     pro User moeglich.

3. **AEAD- oder KDF-Algorithmus ersetzen:** zentrale Aenderung in
   `CryptoFacade.aead_encrypt`/`hkdf`. Aktuell hartcodiert auf AES-256-GCM
   und HKDF-SHA256 (Standard-Library). Falls Wechsel noetig: dispatch ueber
   neue Parameter `aead_alg`, `kdf_alg`. Wire-Format-Erweiterung muesste
   die jeweiligen Algorithmus-Identifier in Session-Record und Request-
   Headers ergaenzen.

---

## 7. Aenderungs-Historie

| Version | Datum | Aenderung |
| --- | --- | --- |
| 0.1 | 18.06.2026 | Initial fuer PQC-27 CRY-7. Token-Header, Session-Init, Session-Record, Encrypted-Channel-Wire-Format. |
| 0.2 | 18.06.2026 | PQC-48 SES-3: Session-Record-Felder auf Design 5.2 + Implementation aligniert (expires_at statt auth_method, unix-ts statt ISO-created_at). F-095 closed durch SessionConfig in config.py. |
| 0.3 | 26.06.2026 | PQC-51 DCH-2: Sec 5.4 um `nonce_missing`/`nonce_format_invalid`/`payload_not_json` erweitert, Body-Konvention auf `{detail: {error: ...}}` aligniert, AAD-Konvention auf `session_id.encode('ascii')` festgeschrieben. F-109 closed. |
