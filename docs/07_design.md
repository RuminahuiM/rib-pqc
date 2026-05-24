# Design: PQC Auth-Service mit Identity Broker und E2E PQ-Kommunikation

**Projekt:** Implementing PQC (Semesterarbeit 3, ITCNE25)
**Autor:** Dodoe Rumiñahui Mannale
**Erstellt:** 08.05.2026
**Status:** Initial-Version (v1.0)

**Bezug:** Konkretisiert die Architektur aus `03_entscheidung_auth_architektur.md` und implementiert die Requirements aus `05_requirements.md` mit dem Tech-Stack aus `06_tech_stack.md`.

---

## Inhaltsverzeichnis

1. [Übersicht und System-Kontext](#1-übersicht-und-system-kontext)
2. [Komponenten-Architektur](#2-komponenten-architektur)
3. [Deployment-Architektur](#3-deployment-architektur)
4. [Sequenz-Diagramme](#4-sequenz-diagramme)
5. [Datenmodell](#5-datenmodell)
6. [Crypto-Abstraction-Layer Design](#6-crypto-abstraction-layer-design)
7. [Versionsverlauf](#7-versionsverlauf)

---

## 1. Übersicht und System-Kontext

### 1.1 System-Kontext

Das System besteht aus zwei Hauptkomponenten (Mock-App und Auth-Service) und nutzt zwei externe Identity Provider (Google, Microsoft) für die Federation. Die folgende Übersicht zeigt die Akteure und Hauptverbindungen:

```mermaid
flowchart LR
    User["End-User"]
    App["Mock-App<br/>(RN/Expo)"]
    Auth["Auth-Service<br/>(FastAPI hinter nginx)"]
    Google["Google OIDC OP"]
    Microsoft["Microsoft Entra OP"]

    User -->|"verwendet"| App
    App -->|"hybrid TLS<br/>+ App-Layer PQ"| Auth
    User -->|"federated Login<br/>(klassisch RS256)"| Google
    User -->|"federated Login<br/>(klassisch RS256)"| Microsoft
    Auth -.->|"Token-Verifikation<br/>via JWKS"| Google
    Auth -.->|"Token-Verifikation<br/>via JWKS"| Microsoft
```

### 1.2 Architektur-Leitsätze

Das Design folgt vier Leitsätzen:

- **Krypto-Operationen laufen IMMER durch die Crypto-Abstraction-Layer.** Application-Code kennt keine konkreten Algorithmus-Namen.
- **Externe IdPs sind austauschbare Plugins.** Apple kann später hinzugefügt werden ohne Architektur-Änderung.
- **PQ-Verschlüsselung ist End-to-End auf Application-Layer.** TLS-PQ ist Zusatz-Schutz, nicht primärer Verschlüsselungskanal.
- **Trennung von klassischer Pre-Authentication (extern) und PQ-Sphäre (intern).** Die "PQ-Uplift"-Grenze ist klar definiert: ab dem Broker-Token ist alles PQ-sicher.

---

## 2. Komponenten-Architektur

### 2.1 Auth-Service: Interne Komponenten

Der Auth-Service ist intern in Module gegliedert, die jeweils klar definierte Verantwortungen haben:

```mermaid
flowchart TB
    subgraph AuthService["Auth-Service (FastAPI)"]
        direction TB

        subgraph API["HTTP-Layer"]
            AuthEndpoint["/auth/local/*"]
            FedEndpoint["/auth/federated/*"]
            SessionEndpoint["/session/*"]
            ProtectedEndpoint["/api/*"]
            HealthEndpoint["/health"]
        end

        subgraph Modules["Business-Module"]
            AuthMod["Auth-Module<br/>(Local Login)"]
            BrokerMod["Broker-Module<br/>(Federation)"]
            TokenMod["Token-Module<br/>(Sign / Verify)"]
            SessionMod["Session-Module<br/>(PQ-Handshake + Store)"]
            DataChannelMod["DataChannel-Module<br/>(AES-GCM + Routing)"]
        end

        subgraph Registries["Registries"]
            IdPRegistry["IdP-Registry<br/>(Google, Microsoft)"]
            CryptoRegistry["Crypto-Registry<br/>(ML-KEM, ML-DSA, ...)"]
        end

        subgraph CryptoLayer["Crypto-Abstraction-Layer"]
            CryptoFacade["Crypto-Facade<br/>(sign, verify, encaps, ...)"]
        end

        subgraph DataAccess["Data-Access"]
            UserStore["User-Store<br/>(SQLAlchemy/SQLite)"]
            SessionStore["Session-Store<br/>(redis-py)"]
        end

        AuthEndpoint --> AuthMod
        FedEndpoint --> BrokerMod
        SessionEndpoint --> SessionMod
        ProtectedEndpoint --> DataChannelMod

        AuthMod --> TokenMod
        BrokerMod --> IdPRegistry
        BrokerMod --> TokenMod
        TokenMod --> CryptoFacade
        SessionMod --> CryptoFacade
        DataChannelMod --> CryptoFacade

        AuthMod --> UserStore
        BrokerMod --> UserStore
        SessionMod --> SessionStore
        DataChannelMod --> SessionStore

        CryptoFacade --> CryptoRegistry
    end
```

**Verantwortlichkeiten pro Modul:**

| Modul | Verantwortlichkeit | Erfüllt FR |
|---|---|---|
| Auth-Module | Lokale Email/Passwort-Authentifizierung | FR-Auth-1, FR-Auth-2 |
| Broker-Module | Federation-Flow mit externen IdPs, Identity-Normalisierung | FR-Broker-1 bis FR-Broker-4 |
| Token-Module | Broker-Token-Ausstellung und -Verifikation | FR-Token-1, FR-Token-2, FR-Token-3 |
| Session-Module | PQ-Session-Etablierung, Session-Lifecycle | FR-Session-1 bis FR-Session-4 |
| DataChannel-Module | Verschlüsselter Daten-Kanal für API-Calls | FR-DataChannel-1, FR-DataChannel-2 |
| IdP-Registry | Plugin-Registry für externe OIDC-Provider | FR-Broker-1 |
| Crypto-Registry | Plugin-Registry für KEM- und Signatur-Algorithmen | FR-Crypto-1 |
| Crypto-Facade | Abstrakte Schnittstelle zu allen Krypto-Operationen | FR-Crypto-2, FR-Crypto-3 |

### 2.2 Mobile-App: Interne Komponenten

Die Mock-App ist als TypeScript-Expo-App strukturiert:

```mermaid
flowchart TB
    subgraph App["Mock-App (Expo / RN / TypeScript)"]
        direction TB

        subgraph Screens["Screens (Expo Router)"]
            LoginScreen["Login-Screen"]
            HomeScreen["Home-Screen"]
            ProfileScreen["Profile-Screen"]
        end

        subgraph AppLogic["App-Logic"]
            AuthCtx["Auth-Context"]
            SessionCtx["Session-Context"]
            SecureClient["secureClient.ts<br/>(HTTP-Wrapper)"]
        end

        subgraph CryptoLayer["Crypto-Abstraction (App)"]
            KemMod["crypto/kem.ts"]
            CipherMod["crypto/cipher.ts"]
            SignatureMod["crypto/signature.ts"]
            HashMod["crypto/hash.ts"]
        end

        subgraph Storage["Storage"]
            SecureStore["expo-secure-store<br/>(Token-Speicherung)"]
            Memory["In-Memory<br/>(Session-Key)"]
        end

        subgraph OIDCClient["OIDC-Client"]
            AuthSession["expo-auth-session"]
        end

        LoginScreen --> AuthCtx
        LoginScreen --> AuthSession
        HomeScreen --> SecureClient
        ProfileScreen --> SecureClient

        AuthCtx --> SecureStore
        SessionCtx --> Memory

        SecureClient --> CipherMod
        SecureClient --> SessionCtx
        SecureClient --> AuthCtx

        AuthSession --> AuthCtx

        KemMod -.->|"@noble/post-quantum"| nobleA["noble/post-quantum"]
        CipherMod -.->|"@noble/ciphers"| nobleB["noble/ciphers"]
        SignatureMod -.->|"@noble/post-quantum"| nobleA
        HashMod -.->|"@noble/hashes"| nobleC["noble/hashes"]
    end
```

**Verantwortlichkeiten:**

| Komponente | Verantwortlichkeit |
|---|---|
| Login-Screen | Drei Login-Optionen (Email/Passwort, Google, Microsoft) |
| Home-Screen | Demonstration eines geschützten API-Calls nach erfolgreichem Login |
| Profile-Screen | Anzeige der eigenen User-Daten via PQ-verschlüsseltem `/api/profile`-Call |
| Auth-Context | Globaler State für Broker-Token und User-Info |
| Session-Context | Globaler State für aktuelle PQ-Session (session_id, session_key) |
| secureClient.ts | HTTP-Wrapper, der jede API-Anfrage automatisch verschlüsselt und entschlüsselt |
| crypto/* | Eigene Abstraction-Module über die `@noble/*` Libraries |

---

## 3. Deployment-Architektur

### 3.1 Container-Setup (Docker Compose)

```mermaid
flowchart TB
    subgraph Host["Lokales Demo-System (Laptop)"]
        direction TB

        subgraph DockerCompose["Docker Compose"]
            direction LR

            subgraph nginxContainer["nginx-Container<br/>(openquantumsafe/oqs-ossl3)"]
                nginxProc["nginx 1.27<br/>+ oqs-provider<br/>+ OpenSSL 3.5+"]
            end

            subgraph authContainer["auth-service-Container<br/>(Python 3.12)"]
                fastapi["FastAPI + Uvicorn"]
                liboqs["liboqs-python<br/>(ML-KEM, ML-DSA)"]
                fastapi --- liboqs
            end

            subgraph redisContainer["redis-Container<br/>(Redis 7.x)"]
                redisProc["Redis (Session-Store)"]
            end

            subgraph dbVolume["Docker Volume<br/>'auth-data'"]
                sqlite["SQLite-DB<br/>(User-Store)"]
            end
        end

        AppDevice["Mock-App<br/>(Expo Go auf Test-Phone)"]

        AppDevice -->|"hybrid TLS<br/>(X25519MLKEM768)"| nginxProc
        nginxProc -->|"upstream proxy<br/>(plain HTTP intern)"| fastapi
        fastapi -->|"async TCP"| redisProc
        fastapi -.->|"SQLAlchemy"| sqlite
    end

    External["Externe IdPs<br/>(Google, Microsoft)"]
    fastapi -->|"HTTPS<br/>(httpx async)"| External
```

### 3.2 Netzwerk- und Port-Layout

| Komponente | Port (intern) | Port (extern) | Protokoll |
|---|---|---|---|
| nginx | 443 | 443 | HTTPS mit X25519MLKEM768 |
| auth-service (Uvicorn) | 8000 | n.A. (nur intern) | HTTP |
| redis | 6379 | n.A. (nur intern) | RESP-Protokoll |
| SQLite | n.A. (File-DB) | n.A. | n.A. |

### 3.3 Volumes und Persistenz

- `auth-data`: Docker-Volume für die SQLite-DB. Persistiert User-Records über Container-Restarts.
- `redis-data` (optional): Docker-Volume für Redis-Persistenz. Sessions überleben Redis-Restart, sterben aber bei vollständigem Compose-Down.

---

## 4. Sequenz-Diagramme

### 4.1 UC-1: Lokaler Login mit Email/Passwort

```mermaid
sequenceDiagram
    participant User
    participant App as Mock-App
    participant nginx
    participant Auth as Auth-Service
    participant UserStore as User-Store (SQLite)

    User->>App: Email + Passwort eingeben
    App->>nginx: POST /auth/local/login<br/>{ email, password }
    Note over App,nginx: hybrid TLS X25519MLKEM768
    nginx->>Auth: POST /auth/local/login

    Auth->>UserStore: SELECT user WHERE email=?
    UserStore-->>Auth: user record (mit Argon2-Hash)

    Auth->>Auth: argon2.verify(password, hash)

    alt Passwort korrekt
        Auth->>Auth: Broker-Token erzeugen<br/>(ML-DSA-65 via Crypto-Facade)
        Auth-->>nginx: 200 OK<br/>{ broker_token, expires_in }
        nginx-->>App: 200 OK
        App->>App: Token in expo-secure-store
        App->>User: Navigation zum Home-Screen
    else Passwort falsch oder User unbekannt
        Auth-->>nginx: 401 Unauthorized<br/>{ error: "invalid_credentials" }
        nginx-->>App: 401
        App->>User: "Anmeldung fehlgeschlagen"
    end
```

### 4.2 UC-2: Login mit Google (Federated)

```mermaid
sequenceDiagram
    participant User
    participant App as Mock-App
    participant Browser as Browser (System-Tab)
    participant Auth as Auth-Service
    participant Google as Google OIDC OP

    User->>App: "Login mit Google" klicken
    App->>App: PKCE: code_verifier + code_challenge<br/>generate state
    App->>Browser: Öffne Google /authorize<br/>(code_challenge, state, redirect_uri)
    Browser->>Google: GET /authorize
    Google->>User: Login-UI von Google
    User->>Google: Credentials eingeben (ggf. 2FA)
    Google-->>Browser: Redirect zur App<br/>?code=...&state=...
    Browser->>App: Deep-Link mit code+state

    App->>App: state validieren

    alt state OK
        App->>Auth: POST /auth/federated/google/callback<br/>{ code, code_verifier }
        Auth->>Google: POST /token<br/>(code + code_verifier + client_secret)
        Google-->>Auth: { id_token, access_token }

        Auth->>Google: GET /jwks (oder Cache)
        Google-->>Auth: JWKS (Public Keys)
        Auth->>Auth: id_token verifizieren<br/>(Signature, iss, aud, exp)

        Auth->>Auth: Identity-Normalisierung<br/>(google.sub → internal user_id)
        Auth->>Auth: Broker-Token erzeugen<br/>(ML-DSA-65 via Crypto-Facade)
        Auth-->>App: 200 OK { broker_token, expires_in }
        App->>App: Token speichern
        App->>User: Home-Screen
    else state mismatch
        App->>User: "Sicherheitsfehler"
    end
```

### 4.3 UC-4: Etablierung der PQ-Session

```mermaid
sequenceDiagram
    participant App as Mock-App
    participant Auth as Auth-Service
    participant CryptoLayer as Crypto-Facade
    participant SessionStore as Session-Store (Redis)

    Note over App: User ist authentifiziert<br/>(broker_token vorhanden)

    App->>App: ML-KEM-768 KeyGen<br/>(pk_app, sk_app)
    App->>Auth: POST /session/init<br/>Authorization: Bearer broker_token<br/>{ kem_alg: "ML-KEM-768", encapsulation_key: pk_app }

    Auth->>CryptoLayer: token.verify(broker_token)
    CryptoLayer-->>Auth: claims OK / 401

    alt Token gültig
        Auth->>CryptoLayer: kem.is_supported("ML-KEM-768")
        CryptoLayer-->>Auth: true

        Auth->>CryptoLayer: kem.encaps(pk_app, "ML-KEM-768")
        CryptoLayer-->>Auth: (ciphertext, shared_secret)

        Auth->>Auth: session_id = uuid4()
        Auth->>CryptoLayer: hkdf(shared_secret,<br/>info="app-session-v1",<br/>salt=session_id)
        CryptoLayer-->>Auth: session_key (32 Bytes)

        Auth->>SessionStore: SET session:{id} {key, user_id, exp, kem_alg}<br/>EX 900
        SessionStore-->>Auth: OK

        Auth-->>App: 200 OK<br/>{ session_id, ciphertext, expires_in }

        App->>App: shared_secret = kem.decaps(ciphertext, sk_app)
        App->>App: session_key = hkdf(shared_secret, "app-session-v1", salt=session_id)
        App->>App: session in Memory-Context

        Note over App: Beide haben jetzt<br/>denselben session_key
    else Token ungültig
        Auth-->>App: 401 Unauthorized
    end
```

### 4.4 UC-5: Geschützter API-Call

```mermaid
sequenceDiagram
    participant App as Mock-App
    participant Auth as Auth-Service
    participant SessionStore as Session-Store (Redis)
    participant DB as User-Store

    App->>App: nonce = random(96 bit)
    App->>App: ciphertext = AES-GCM.encrypt(<br/>session_key, nonce, payload)

    App->>Auth: POST /api/profile<br/>X-Session-Id: ...<br/>X-Nonce: base64(nonce)<br/>Body: ciphertext+tag

    Auth->>SessionStore: GET session:{id}
    SessionStore-->>Auth: {session_key, user_id, ...}

    alt Session existiert und nicht abgelaufen
        Auth->>Auth: plaintext = AES-GCM.decrypt(<br/>session_key, nonce, ciphertext+tag)

        alt Tag gültig
            Auth->>DB: SELECT user WHERE id=user_id
            DB-->>Auth: user record
            Auth->>Auth: response_plaintext = serialize(user)

            Auth->>Auth: response_nonce = random(96 bit)
            Auth->>Auth: response_cipher = AES-GCM.encrypt(<br/>session_key, response_nonce, response_plaintext)

            Auth-->>App: 200 OK<br/>X-Nonce: base64(response_nonce)<br/>Body: response_cipher+tag

            App->>App: response_plaintext = AES-GCM.decrypt(<br/>session_key, response_nonce, response_cipher+tag)
            App->>App: User-Profil anzeigen
        else Tag ungültig (Tampering)
            Auth-->>App: 400 Bad Request<br/>(Security-Event geloggt)
        end
    else Session abgelaufen
        Auth-->>App: 401 Unauthorized<br/>{ error: "session_expired" }
        App->>App: Re-Auth-Flow starten (UC-6)
    end
```

### 4.5 UC-7: Algorithmus-Wechsel via Config

```mermaid
sequenceDiagram
    participant Operator
    participant Config as config.yaml
    participant Service as Auth-Service
    participant Registry as Crypto-Registry
    participant App as Mock-App

    Note over Service: Vor-Zustand:<br/>crypto.kem.default = "ML-KEM-768"

    Operator->>Config: Edit: crypto.kem.default = "ML-KEM-1024"
    Operator->>Service: docker compose restart auth-service

    Service->>Config: Load config (pydantic-settings)
    Config-->>Service: parsed config
    Service->>Registry: register algorithms<br/>(ML-KEM-768, ML-KEM-1024)
    Service->>Registry: assert "ML-KEM-1024" in registry
    Registry-->>Service: OK
    Service->>Service: aktive Default-KEM = "ML-KEM-1024"

    Note over Service: Service ist bereit<br/>mit neuem Default-Algorithmus

    App->>Service: POST /session/init<br/>{ kem_alg: "ML-KEM-768", ... }
    Note over App: App weiss noch nicht<br/>von der Änderung

    Service->>Service: angefragter Algo "ML-KEM-768"<br/>≠ aktiver Default
    Service-->>App: 406 Not Acceptable<br/>{ supported_algorithms: ["ML-KEM-1024"] }

    App->>App: Algorithmus-Wechsel:<br/>kem_alg = "ML-KEM-1024"
    App->>App: ML-KEM-1024 KeyGen<br/>(neues pk_app, sk_app)
    App->>Service: POST /session/init<br/>{ kem_alg: "ML-KEM-1024", ... }

    Service->>Service: kem.encaps mit ML-KEM-1024
    Service-->>App: 200 OK<br/>(Session etabliert mit neuem Algo)

    Note over Operator: Demo zeigt: kein .py-Diff,<br/>nur Config-Diff
```

---

## 5. Datenmodell

### 5.1 Broker-Token-Struktur (intern, JWS-shaped mit ML-DSA)

Der Broker-Token folgt der JWS-Compact-Serialization aus RFC 7515:

```
base64url(header) . base64url(payload) . base64url(signature)
```

**Header:**

```json
{
  "alg": "ML-DSA-65",
  "typ": "JWT",
  "kid": "key-2026-05-1"
}
```

**Payload (Claims):**

```json
{
  "sub": "user-uuid-...",
  "iss": "pqc-auth-service",
  "iat": 1746700800,
  "exp": 1746704400,
  "auth_method": "local",
  "external_sub": null
}
```

Bei federated Logins:

```json
{
  "sub": "user-uuid-...",
  "iss": "pqc-auth-service",
  "iat": 1746700800,
  "exp": 1746704400,
  "auth_method": "google",
  "external_sub": "115234567890123456789"
}
```

**Signatur:** ML-DSA-65 über die Bytes von `base64url(header).base64url(payload)`.

### 5.2 Session-Record (Redis)

Key: `session:{session_id}`
Value (JSON-serialisiert):

```json
{
  "session_key": "base64-encoded-32-bytes",
  "user_id": "user-uuid-...",
  "kem_alg": "ML-KEM-768",
  "created_at": 1746700800,
  "expires_at": 1746701700
}
```

TTL via Redis EXPIRE auf 900 Sekunden (15 Minuten Default).

### 5.3 User-Record (SQLite)

```mermaid
erDiagram
    USERS {
        string id PK "UUID"
        string email UK "Unique"
        string password_hash "Argon2id, nullable für federated-only Users"
        string auth_method "local | google | microsoft"
        string external_sub "nullable, für Federated Users"
        timestamp created_at
        timestamp updated_at
    }
```

### 5.4 Config-Struktur (`config.yaml`)

```yaml
crypto:
  kem:
    default: "ML-KEM-768"
    supported:
      - "ML-KEM-768"
      - "ML-KEM-1024"
  signature:
    default: "ML-DSA-65"
    supported:
      - "ML-DSA-65"
  symmetric:
    cipher: "AES-256-GCM"
    kdf: "HKDF-SHA256"

token:
  ttl_seconds: 3600
  issuer: "pqc-auth-service"
  active_kid: "key-2026-05-1"

session:
  ttl_seconds: 900

idp_providers:
  google:
    client_id: "${GOOGLE_CLIENT_ID}"
    discovery_url: "https://accounts.google.com/.well-known/openid-configuration"
    scopes: ["openid", "email", "profile"]
    claim_mapping:
      external_sub: "sub"
  microsoft:
    client_id: "${MICROSOFT_CLIENT_ID}"
    discovery_url: "https://login.microsoftonline.com/common/v2.0/.well-known/openid-configuration"
    scopes: ["openid", "email", "profile"]
    claim_mapping:
      external_sub: "oid"

logging:
  level: "INFO"
  format: "json"

server:
  host: "0.0.0.0"
  port: 8000
```

Secrets (`.env`-File, nicht im Git):

```env
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
MICROSOFT_CLIENT_ID=...
MICROSOFT_CLIENT_SECRET=...
ML_DSA_PRIVATE_KEY_PATH=/data/keys/ml-dsa-65.priv
DATABASE_URL=sqlite+aiosqlite:///data/auth.db
REDIS_URL=redis://redis:6379/0
```

---

## 6. Crypto-Abstraction-Layer Design

Der Crypto-Abstraction-Layer ist das Herzstück der Crypto-Agility. Er trennt das "Was wird gemacht" (Application-Logic) sauber vom "Wie wird es gemacht" (konkreter Algorithmus).

### 6.1 Schnittstelle (Server-Seite, Python)

```python
class CryptoFacade:
    """Zentrale Crypto-Schnittstelle. Application-Code ruft NUR diese Methoden auf."""

    # Signatur-Operationen (für Token-Signing)
    def sign(self, payload: bytes, purpose: str = "id_token") -> tuple[bytes, str, str]:
        """Returns (signature, alg_name, kid). Wahl des Algos via Config."""

    def verify(self, payload: bytes, signature: bytes, alg: str, kid: str) -> bool:
        """Verifiziert mit dem Algo und kid aus dem Token-Header."""

    # KEM-Operationen (für Session-Etablierung)
    def kem_keygen(self, alg: str | None = None) -> tuple[bytes, bytes]:
        """Returns (public_key, private_key). Default-Algo aus Config falls alg=None."""

    def kem_encaps(self, public_key: bytes, alg: str) -> tuple[bytes, bytes]:
        """Returns (ciphertext, shared_secret)."""

    def kem_decaps(self, ciphertext: bytes, private_key: bytes, alg: str) -> bytes:
        """Returns shared_secret."""

    # Schlüssel-Ableitung
    def hkdf(self, ikm: bytes, info: bytes, salt: bytes, length: int = 32) -> bytes:
        """HKDF-SHA256 als Default."""

    # Symmetrische Verschlüsselung
    def aead_encrypt(self, key: bytes, nonce: bytes, plaintext: bytes, aad: bytes = b"") -> bytes:
        """AES-256-GCM. Returns ciphertext+tag."""

    def aead_decrypt(self, key: bytes, nonce: bytes, ciphertext_and_tag: bytes, aad: bytes = b"") -> bytes:
        """AES-256-GCM. Raises on tag mismatch."""

    # Negotiation-Support
    def supported_kem_algorithms(self) -> list[str]:
        """Returns Liste aller registrierten KEM-Algorithmen."""

    def is_kem_supported(self, alg: str) -> bool:
        ...
```

### 6.2 Wie Crypto-Agility funktioniert (Algorithmus-Wechsel-Mechanik)

```mermaid
flowchart TD
    AppCode["Application-Code<br/>(z.B. Session-Module)"]
    Facade["CryptoFacade.kem_encaps(pk_app)"]
    Config["config.yaml<br/>crypto.kem.default"]
    Registry["CryptoRegistry"]
    Plugin1["ML-KEM-768<br/>(liboqs-python)"]
    Plugin2["ML-KEM-1024<br/>(liboqs-python)"]
    PluginN["Future-KEM-X<br/>(zukünftig)"]

    AppCode -->|"ruft abstrakt"| Facade
    Facade -->|"liest aktiven Algo"| Config
    Facade -->|"holt Plugin"| Registry
    Registry -->|"liefert"| Plugin1
    Registry -.->|"oder"| Plugin2
    Registry -.->|"oder zukünftig"| PluginN

    Plugin1 -->|"shared_secret"| Facade
    Facade -->|"Result"| AppCode

    style Config fill:#fff3cd
    style Registry fill:#d4edda
```

**Wichtigste Eigenschaft**: Application-Code referenziert keine konkreten Algorithmus-Namen (kein Import von `mlkem768`, kein String `"ML-KEM-768"` ausserhalb der Crypto-Layer). Das macht den Wechsel von ML-KEM-768 zu ML-KEM-1024 zu einer reinen Config-Änderung.

### 6.3 Algorithmus-Registry Setup (beim Service-Start)

```python
# auth_service/crypto/registry_init.py
from liboqs import KeyEncapsulation, Signature

def init_crypto_registry(registry: CryptoRegistry, config: CryptoConfig):
    # KEM-Algorithmen
    for alg_name in config.kem.supported:
        if alg_name == "ML-KEM-768":
            registry.register_kem("ML-KEM-768", LibOqsKem("ML-KEM-768"))
        elif alg_name == "ML-KEM-1024":
            registry.register_kem("ML-KEM-1024", LibOqsKem("ML-KEM-1024"))
        else:
            raise ConfigError(f"Unknown KEM algorithm: {alg_name}")

    # Signatur-Algorithmen analog
    for alg_name in config.signature.supported:
        if alg_name == "ML-DSA-65":
            registry.register_signature("ML-DSA-65", LibOqsSignature("ML-DSA-65"))
        else:
            raise ConfigError(f"Unknown signature algorithm: {alg_name}")
```

Beim Wechsel auf einen neuen NIST-Standard (z.B. zukünftige FIPS-Updates) ist nur dieser File anzupassen plus ein neuer Plugin-Adapter. Application-Code bleibt unverändert.

### 6.4 Mobile-Side Crypto-Abstraction (TypeScript)

Symmetrisch zur Server-Seite, ein eigenes Modul pro Verantwortlichkeit:

```typescript
// crypto/kem.ts
import { ml_kem768, ml_kem1024 } from '@noble/post-quantum/ml-kem';
import { cryptoConfig } from '../config';

export type KemAlgorithm = 'ML-KEM-768' | 'ML-KEM-1024';

const KEM_IMPLS: Record<KemAlgorithm, typeof ml_kem768> = {
  'ML-KEM-768': ml_kem768,
  'ML-KEM-1024': ml_kem1024,
};

export function keygen(alg: KemAlgorithm = cryptoConfig.defaultKem) {
  const impl = KEM_IMPLS[alg];
  return impl.keygen();
}

export function encaps(publicKey: Uint8Array, alg: KemAlgorithm) {
  return KEM_IMPLS[alg].encapsulate(publicKey);
}

export function decaps(ciphertext: Uint8Array, privateKey: Uint8Array, alg: KemAlgorithm) {
  return KEM_IMPLS[alg].decapsulate(ciphertext, privateKey);
}

export function supportedAlgorithms(): KemAlgorithm[] {
  return Object.keys(KEM_IMPLS) as KemAlgorithm[];
}
```

Die App nutzt diese Abstraction-Module statt direkter `@noble/*`-Imports. Der einzige Ort, der konkrete Algorithmus-Namen kennt, ist diese Datei.

---

## 7. Versionsverlauf

| Version | Datum | Änderung |
|---|---|---|
| 1.0 | 08.05.2026 | Initial-Version. System-Kontext, Komponenten-Architektur (Server und Mobile), Deployment-Architektur, 5 Sequenz-Diagramme (UC-1, UC-2, UC-4, UC-5, UC-7), Datenmodell (Broker-Token, Session-Record, User-Record, Config-Struktur), Crypto-Abstraction-Layer Design mit Schnittstellen-Beispielen für Server und Mobile. |
