# Tech-Stack: PQC Auth-Service mit Identity Broker

**Projekt:** Implementing PQC (Semesterarbeit 3, ITCNE25)
**Autor:** Dodoe Rumiñahui Mannale
**Erstellt:** 08.05.2026
**Status:** Vollständig (alle Entscheidungen getroffen)

**Bezug:** Implementiert die Requirements aus `05_requirements.md` und die Architektur-Entscheidung Option 3 aus `03_entscheidung_auth_architektur.md`.

---

## Inhaltsverzeichnis

1. [Überblick](#1-überblick)
2. [Server-Stack](#2-server-stack)
3. [Mobile-Stack](#3-mobile-stack)
4. [Dev-Tooling](#4-dev-tooling)
5. [Versionsverlauf](#5-versionsverlauf)

---

## 1. Überblick

Die Tech-Stack-Entscheidungen folgen drei Leitlinien:

- **Production-realistisch**: Wahlen, die auch in einem echten Produkt sinnvoll wären. Keine "Spielzeug"-Bibliotheken.
- **Schul-Scope-tauglich**: Keine über-engineerten Konstruktionen, die im Zeitfenster nicht umsetzbar sind.
- **Crypto-Agility durchgängig**: Krypto-Operationen laufen sowohl server- als auch app-seitig durch eine Abstraction Layer, sodass Algorithmen austauschbar sind.

Pro Komponente ist dokumentiert: Wahl, Funktion, Begründung, verworfene Alternativen, abgedeckte Requirements, Quelle.

---

## 2. Server-Stack

### 2.1 Infrastruktur und Container

#### Docker Compose

**Wahl:** Docker Compose 2.x
**Funktion:** Orchestriert die Server-Container (Auth-Service, nginx, Redis, optional Alembic-Migrations) für lokale Entwicklung und Demo.
**Begründung:** Einfaches Multi-Container-Setup ohne Kubernetes-Overhead. Reproducible "compose up" auf jedem Rechner.
**Alternativen verworfen:** Bare-metal-Installation (zu viel Setup auf neuem Rechner), Kubernetes (Overkill für Schulprojekt).
**Erfüllt Requirements:** C-Tech-5 (Container-basierte Demo-Architektur).
**Quelle:** https://docs.docker.com/compose/

#### Container-Base-Image

**Wahl:** `openquantumsafe/oqs-ossl3` (latest stable Tag, gepinnt auf eine Hash-Version vor Demo)
**Funktion:** Basis-Image für nginx-Container, enthält bereits gebautes OpenSSL 3.5+ mit oqs-provider integriert.
**Begründung:** Vermeidet manuellen 2-Tage-Build-Aufwand von liboqs und oqs-provider. Wird vom Open Quantum Safe Projekt gepflegt.
**Alternativen verworfen:** Self-build von liboqs + oqs-provider (zu zeit-intensiv), alpine-basiertes Image (instabil mit oqs-provider laut Issues).
**Erfüllt Requirements:** C-Tech-5, NFR-Sec-1.
**Quelle:** https://hub.docker.com/r/openquantumsafe/oqs-ossl3

#### Reverse Proxy

**Wahl:** nginx 1.27
**Funktion:** TLS-Termination mit hybrider PQ-Cipher-Suite (X25519MLKEM768). Reverse-Proxy zu FastAPI-App.
**Begründung:** Industrie-Standard für TLS-Termination. oqs-provider-Integration via OpenSSL 3.5 ist stabil ab nginx 1.27.
**Alternativen verworfen:** Caddy (oqs-provider-Integration weniger gut dokumentiert), Traefik (zu komplex für unseren Single-Service-Use-Case).
**Erfüllt Requirements:** NFR-Sec-1 (Hybride PQ-TLS).
**Quelle:** https://nginx.org/

#### oqs-provider

**Wahl:** oqs-provider ≥ 0.10 (im Base-Image)
**Funktion:** OpenSSL-3-Provider-Plugin, das ML-KEM und ML-DSA als TLS-Cipher-Suites verfügbar macht.
**Begründung:** Einziger praktikabler Weg, PQ-Cipher-Suites in OpenSSL 3 zu nutzen. Vom Open Quantum Safe Projekt gepflegt.
**Alternativen verworfen:** Custom-Patches auf OpenSSL (Wartungs-Aufwand), reine PQ-TLS-Libraries wie BoringSSL-fork (mobile-incompatible).
**Erfüllt Requirements:** NFR-Sec-1.
**Quelle:** https://github.com/open-quantum-safe/oqs-provider

#### OpenSSL

**Wahl:** OpenSSL 3.5+
**Funktion:** TLS-Stack, von nginx genutzt, vom oqs-provider erweitert.
**Begründung:** Provider-API erfordert OpenSSL 3.0+, stabile PQ-Integration ab 3.5+.
**Alternativen verworfen:** OpenSSL 1.1.1 (kein Provider-API), LibreSSL (oqs-Integration nicht offiziell).
**Erfüllt Requirements:** NFR-Sec-1.
**Quelle:** https://www.openssl.org/

---

### 2.2 Application-Layer

#### Programmiersprache

**Wahl:** Python 3.12
**Funktion:** Implementierungssprache des Auth-Service.
**Begründung:** Beste Verfügbarkeit von PQC-Wrappern (liboqs-python). Python 3.12 hat moderne async-Performance, ist LTS-tauglich. Im Projekt-Memory festgelegt.
**Alternativen verworfen:** Go (PQC-Bibliotheken weniger reif), Rust (deutlich mehr Aufwand für Schul-Scope), Node.js (PQC-Server-Implementierungen ungeprüft).
**Erfüllt Requirements:** Alle FR-Gruppen (Implementierungs-Sprache).
**Quelle:** https://www.python.org/

#### Web-Framework

**Wahl:** FastAPI (latest stable, 0.115+)
**Funktion:** HTTP-Endpoints für Auth, Federation, Session und API-Calls.
**Begründung:** Modern, async-first, auto-OpenAPI-Generation, type-hint-basiert, ausgezeichnete Pydantic-Integration. De-facto-Standard für moderne Python-APIs.
**Alternativen verworfen:** Flask (kein async-first, älteres Design), Django REST Framework (zu schwergewichtig für Microservice), Starlette pur (FastAPI ist Starlette plus QoL-Features).
**Erfüllt Requirements:** Alle FR-Gruppen (HTTP-Layer).
**Quelle:** https://fastapi.tiangolo.com/

#### ASGI-Server

**Wahl:** Uvicorn (latest stable)
**Funktion:** ASGI-Server, der FastAPI hosted, hinter nginx.
**Begründung:** De-facto-Standard für FastAPI. Async-Performance, einfaches Setup.
**Alternativen verworfen:** Hypercorn (vergleichbar, aber kleinere Community), Gunicorn (sync, nicht ideal für FastAPI).
**Erfüllt Requirements:** Operational requirement.
**Quelle:** https://www.uvicorn.org/

---

### 2.3 Crypto-Layer (Server)

#### PQC-Library

**Wahl:** liboqs-python (latest stable, 0.10+)
**Funktion:** Python-Wrapper um liboqs für ML-KEM-768 (KEM-Operationen) und ML-DSA-65 (Signatur).
**Begründung:** Einziger praktikabler Python-Wrapper für die NIST-PQC-Standards. pyca/cryptography 45.x liefert ML-DSA/ML-KEM nicht in 2026 aus.
**Alternativen verworfen:** pyca/cryptography (kein ML-KEM/ML-DSA in 2026), kyber-py / dilithium-py (pre-Standardization, Sicherheits-Risiko).
**Erfüllt Requirements:** FR-Token-1, FR-Session-1, FR-Crypto-1.
**Quelle:** https://github.com/open-quantum-safe/liboqs-python

#### Internes Token-Format

**Wahl:** Custom JWS-Encoder/Decoder (eigene Implementation, ca. 80 Zeilen)
**Funktion:** Erzeugung und Verifikation der Broker-Tokens im JWS-Format mit ML-DSA-Signatur via liboqs-python.
**Begründung:** PyJWT 3.x hat 2026 noch keine stabile ML-DSA-Unterstützung (auf der Roadmap, aber nicht released). Custom-Implementation ist überschaubar, hält JWS-Format-Konformität und gibt volle Kontrolle für Crypto-Agility-Layer.
**Alternativen verworfen:** PyJWT 3.x Pre-Release (Risiko von Breaking Changes), komplett-eigenes Token-Format (nicht standardkonform, schwächere Bericht-Story).
**Erfüllt Requirements:** FR-Token-1, FR-Token-2, FR-Crypto-3.
**Quelle:** Eigene Implementation. JWS-Spec: RFC 7515.

#### Externe Token-Verifikation

**Wahl:** PyJWT (latest stable, 2.9+)
**Funktion:** Verifikation der Google- und Microsoft-ID-Tokens (RS256/ES256) während Federation-Flow.
**Begründung:** Standard-Library für JWT-Handling in Python. Sehr stabil, gut dokumentiert, RFC-konform für klassische Algorithmen.
**Alternativen verworfen:** python-jose (kleinere Community), Custom-Verifier (kein Vorteil bei klassischen Algorithmen).
**Erfüllt Requirements:** FR-Broker-3.
**Quelle:** https://pyjwt.readthedocs.io/

#### Password-Hashing

**Wahl:** argon2-cffi (latest stable)
**Funktion:** Argon2id-Hashing für lokale User-Passwörter.
**Begründung:** Direkter Wrapper um Argon2-Referenz-Implementation. Weniger Abstraktions-Layer als passlib, dafür klare und direkte API.
**Alternativen verworfen:** passlib (zusätzliche Abstraktion ohne Mehrwert für Single-Algorithmus-Setup), bcrypt (älter, Memory-Hardness schwächer).
**Erfüllt Requirements:** FR-Auth-1 (Argon2id mit m=64MB, t=3, p=4).
**Quelle:** https://argon2-cffi.readthedocs.io/

#### Symmetrische Krypto und HKDF

**Wahl:** cryptography (pyca/cryptography, latest stable, 45.x)
**Funktion:** AES-256-GCM-Verschlüsselung (Server-seitige Payloads), HKDF-Schlüsselableitung (Session-Key aus ML-KEM-Shared-Secret), klassische Krypto-Primitive.
**Begründung:** Standard-Bibliothek der Python-Welt für klassische Krypto. Stabil, auditiert, deckt alle benötigten Primitive ab.
**Alternativen verworfen:** PyCryptodome (kleinere Community, kleinere Auditierung), stdlib hashlib (kein HKDF eingebaut).
**Erfüllt Requirements:** FR-Session-2, FR-DataChannel-1.
**Quelle:** https://cryptography.io/

#### Zufallszahlen

**Wahl:** Python stdlib `secrets`
**Funktion:** CSPRNG für Nonces, State-Parameter, Session-IDs, Salt-Werte.
**Begründung:** Standard-Library, OS-CSPRNG-Wrapper. Keine externe Dependency nötig.
**Alternativen verworfen:** `random` (nicht kryptographisch sicher), externe RNG-Libraries (unnötig).
**Erfüllt Requirements:** NFR-Sec-2 (Replay-Schutz via Nonces), FR-Broker-2 (state mit ≥128 Bit Entropie).
**Quelle:** https://docs.python.org/3/library/secrets.html

---

### 2.4 Data-Layer

#### User-Store: Datenbank

**Wahl:** SQLite via SQLAlchemy 2.x (latest stable)
**Funktion:** Speicherung der User-Records (lokale User mit Argon2-Hash, federated User mit external_sub).
**Begründung:** File-basierte DB, kein zusätzlicher Service nötig. SQLAlchemy 2.x bietet typed-async-Support, kompatibel mit FastAPI. Skalierungs-Anforderungen (2-3 Test-User) reichen weit unter SQLite-Limits.
**Alternativen verworfen:** Postgres (zusätzlicher Container, Overkill für 2-3 User), JSON-File (kein ORM, schwächere Demo-Story), In-Memory (User-Records überleben keinen Restart).
**Erfüllt Requirements:** FR-Auth-1, FR-Auth-2, FR-Broker-4.
**Quelle:** https://www.sqlalchemy.org/

#### User-Store: Migrationen

**Wahl:** Alembic (latest stable)
**Funktion:** Schema-Migrationen für die SQLite-DB.
**Begründung:** Standard mit SQLAlchemy. Auch im Schul-Scope sinnvoll, damit das DB-Schema versioniert und reproducible ist.
**Alternativen verworfen:** Hand-geschriebene SQL-Skripte (fehleranfällig), aerich (nur für Tortoise-ORM).
**Erfüllt Requirements:** Operational-Anforderung.
**Quelle:** https://alembic.sqlalchemy.org/

#### Session-Store

**Wahl:** Redis via redis-py mit async-Support (`redis.asyncio`)
**Funktion:** Speicherung der aktiven PQ-Sessions (session_id, session_key, user_id, expires_at, kem_alg). Sessions überleben Service-Restarts.
**Begründung:** Production-realistisch, einsetzbar in echtem System. Sessions überleben Container-Restarts (kritisch für Demo-Robustheit). Redis ist erweiterbar für JWKS-Cache, Rate-Limiting, Pub/Sub falls später benötigt.
**Alternativen verworfen:** In-Memory mit cachetools (Sessions verloren bei Restart, weniger production-realistisch), Memcached (ältere Technologie, kein TTL-Semantik wie bei Redis), Postgres mit pg_session (zu schwergewichtig für Session-Storage).
**Erfüllt Requirements:** FR-Session-3 (Session-Store mit TTL).
**Quelle:** https://redis.io/, https://redis.readthedocs.io/

---

### 2.5 Operations (Server)

#### Logging

**Wahl:** structlog (latest stable, 24.x+)
**Funktion:** Strukturiertes JSON-Logging mit Severity-Levels, Request-IDs und Korrelation.
**Begründung:** 2026-Standard für strukturiertes Logging in Python. Out-of-the-box JSON-Output, gute FastAPI-Integration via `fastapi-structlog`. Erfüllt NFR-Ops-1 direkt.
**Alternativen verworfen:** Python stdlib logging (Plain-Text-Output, nicht strukturiert), loguru (modern aber kleinere Community als structlog).
**Erfüllt Requirements:** NFR-Ops-1, NFR-Ops-2.
**Quelle:** https://www.structlog.org/

#### Config-Management

**Wahl:** pydantic-settings (latest stable, 2.x)
**Funktion:** Typed Config-Loading aus YAML-File und ENV-Variablen, mit Validierung beim Service-Start.
**Begründung:** Tight integration mit Pydantic (das wir eh für FastAPI nutzen). Typsicher, validiert beim Start, klare Fehlermeldungen bei falscher Konfig.
**Alternativen verworfen:** python-decouple (kein Schema-Validation), YAML-File ohne Layer (kein Type-Checking), Dynaconf (zu komplex).
**Erfüllt Requirements:** FR-Crypto-2 (Konfigurations-basierte Algorithmus-Auswahl).
**Quelle:** https://docs.pydantic.dev/latest/concepts/pydantic_settings/

#### Config-Format

**Wahl:** YAML für statische Konfig (Crypto-Algorithmus-Liste, Provider-Definitionen), `.env`-Datei für Secrets (API-Keys, DB-Passwörter)
**Funktion:** Trennung von versionierbarer Konfig und geheimer Konfig.
**Begründung:** Sauberer Split. YAML-File kann ins Git, `.env`-File bleibt lokal/in CI-Secrets. Pydantic-Settings unterstützt beide nativ.
**Alternativen verworfen:** TOML (weniger nested-friendly), JSON (keine Kommentare).
**Erfüllt Requirements:** NFR-Sec-3 (Kein Klartext für Geheimnisse).
**Quelle:** Industrie-Praxis.

#### Health-Check

**Wahl:** Eigene FastAPI-Route `/health`
**Funktion:** Returns `{ status, version, uptime, registry_status }`, gibt `200` bei OK und `503` bei kritischen Dependency-Problemen.
**Begründung:** Trivial zu implementieren, keine zusätzliche Library nötig.
**Alternativen verworfen:** Dedizierte Health-Check-Bibliothek (Overkill).
**Erfüllt Requirements:** NFR-Ops-3.
**Quelle:** Eigene Implementation.

---

### 2.6 Federation (OIDC Client)

#### OIDC-Client-Library

**Wahl:** authlib v1.7.2 (released Mai 2026)
**Funktion:** OIDC Authorization Code Flow mit PKCE für Google und Microsoft Federation. JWKS-Verifikation, Discovery-Endpoint-Handling.
**Begründung:** Production-Stable, deckt sowohl OAuth2 als auch OIDC ab, hat eingebaute JWKS-Verifikation und Discovery. Python 3.10-3.14 supported. Aktiv gepflegt (letzter Release Mai 2026).
**Alternativen verworfen:** requests-oauthlib (sync only, älteres Design), oauthlib (low-level), eigener OIDC-Client (zu viel Boilerplate, RFC-konforme Implementation aufwendig).
**Erfüllt Requirements:** FR-Broker-1, FR-Broker-2, FR-Broker-3.
**Quelle:** https://authlib.org/, https://docs.authlib.org/

#### HTTP-Client (async)

**Wahl:** httpx (latest stable, 0.27+)
**Funktion:** Async-HTTP-Calls zu Google- und Microsoft-Discovery-/Token-Endpoints. Wird intern von authlib verwendet, plus eigene Calls falls nötig.
**Begründung:** Moderner Standard für async-HTTP in Python. Drop-in-replaceable mit requests-Syntax. authlib hat direkten httpx-Adapter.
**Alternativen verworfen:** aiohttp (älter, mehr Boilerplate), requests (sync only).
**Erfüllt Requirements:** FR-Broker-2, FR-Broker-3.
**Quelle:** https://www.python-httpx.org/

---

## 3. Mobile-Stack

### 3.1 App-Framework

#### Mobile-Framework

**Wahl:** Expo SDK 51+
**Funktion:** React-Native-Wrapper mit Managed-Workflow, vereinfacht Setup und Deployment auf iOS und Android.
**Begründung:** Managed-Workflow ohne native Module reicht für unseren Use-Case. `@noble/post-quantum` ist kompatibel. Test-Geräte via Expo Go.
**Alternativen verworfen:** Bare React Native (mehr Setup, native Module unnötig), Flutter (andere Sprache, weniger PQC-Library-Support).
**Erfüllt Requirements:** C-Tech-6.
**Quelle:** https://expo.dev/

#### Sprache

**Wahl:** TypeScript (latest stable)
**Funktion:** Type-sichere Implementierung aller App-Module, insbesondere Crypto-Module.
**Begründung:** 2026-Standard für RN/Expo. Type-Safety besonders wertvoll für Crypto-Code (z.B. Typunterschied zwischen "encrypted bytes" und "plaintext").
**Alternativen verworfen:** Plain JavaScript (weniger Safety, in 2026 nicht mehr empfohlen).
**Erfüllt Requirements:** NFR-Maint-3 (modularer Code-Aufbau).
**Quelle:** https://www.typescriptlang.org/

#### Navigation

**Wahl:** Expo Router (latest stable, mit Expo SDK 51+)
**Funktion:** File-basiertes Routing zwischen Login-Screen, Home-Screen und Profil-Screen.
**Begründung:** 2026-Default für neue Expo-Apps. Kommt im `create-expo-app`-Template. Automatic Deep Linking, typed routes.
**Alternativen verworfen:** React Navigation pur (mehr Boilerplate-Config), Solito (für Next.js-Sharing, hier irrelevant).
**Erfüllt Requirements:** NFR-Use-1.
**Quelle:** https://docs.expo.dev/router/introduction/

#### State Management

**Wahl:** React Context mit `useReducer` für komplexere States
**Funktion:** Globaler State für Auth-Status, Session-State, aktuelle User-Identität.
**Begründung:** Mock-App hat nur 3 Screens und wenig globalen State. React Context ist built-in, keine extra Dependency. Performance-Probleme von Context greifen erst bei häufigen Updates über viele Komponenten, was hier nicht der Fall ist.
**Alternativen verworfen:** Zustand (mehr Komfort, aber für 3-Screen-App Overkill), Redux Toolkit (deutlich mehr Boilerplate).
**Erfüllt Requirements:** Architektur-Anforderung.
**Quelle:** https://react.dev/reference/react/createContext

#### UI-Komponenten

**Wahl:** React Native built-in components mit StyleSheet
**Funktion:** UI-Aufbau für Login, Home und Profil-Screen.
**Begründung:** Drei Screens rechtfertigen keine UI-Library. Built-in `View`, `Text`, `TextInput`, `Pressable` reichen aus.
**Alternativen verworfen:** React Native Paper (Material Design, Overkill), gluestack-ui (Setup-Aufwand).
**Erfüllt Requirements:** NFR-Use-1.
**Quelle:** React Native Documentation.

#### HTTP-Client

**Wahl:** Built-in `fetch` mit Custom-Wrapper (`secureClient.ts`)
**Funktion:** HTTP-Calls zu Auth-Service. Wrapper handhabt AES-GCM-Verschlüsselung von Payloads, Custom-Headers (`X-Session-Id`, `X-Nonce`), Token-Authorization.
**Begründung:** `fetch` ist Standard und reicht. Wrapper-Layer ist notwendig für die AES-GCM-Logik und wäre auch mit `axios` nötig. Keine extra Library.
**Alternativen verworfen:** axios (zusätzliche Dependency ohne Mehrwert), ky (minimaler Wrapper, kein Vorteil hier).
**Erfüllt Requirements:** FR-DataChannel-1, FR-DataChannel-2.
**Quelle:** MDN Fetch API.

---

### 3.2 Auth und Storage

#### OIDC-Client (Mobile)

**Wahl:** `expo-auth-session` (latest mit SDK 51+)
**Funktion:** OAuth2/OIDC-Client für Login mit Google und Microsoft. PKCE eingebaut. Provider-Konfiguration für Google via `expo-auth-session/providers/google`, für Microsoft via generischen Provider.
**Begründung:** Native Expo-Library, eingebaute Provider-Support, PKCE-Handling automatisch. Standard-Wahl für OIDC in Expo-Apps.
**Alternativen verworfen:** `@react-native-google-signin/google-signin` (nur Google, nicht generisch), Custom-OIDC-Client (Aufwand ohne Vorteil).
**Erfüllt Requirements:** FR-Broker-2 (App-Seite des Authorization Code Flow mit PKCE).
**Quelle:** https://docs.expo.dev/versions/latest/sdk/auth-session/

#### Secure Storage

**Wahl:** `expo-secure-store` (latest mit SDK 51+)
**Funktion:** Speicherung des Broker-Tokens in iOS Keychain bzw. Android Keystore.
**Begründung:** Native Expo-Library, kein zusätzliches Setup. iOS Keychain und Android Keystore sind die Standard-Sicherheits-Container für Tokens.
**Alternativen verworfen:** `react-native-keychain` (mehr Features, aber nicht nötig), AsyncStorage (nicht verschlüsselt, nicht sicher).
**Erfüllt Requirements:** FR-Auth-1 (Token im sicheren Speicher).
**Quelle:** https://docs.expo.dev/versions/latest/sdk/securestore/

---

### 3.3 Crypto-Layer (Mobile)

#### PQC-Library

**Wahl:** `@noble/post-quantum` (latest stable)
**Funktion:** ML-KEM-768-Operationen (KeyGen, Encaps, Decaps), ML-DSA-65-Verifikation (für Broker-Token-Verifikation in der App).
**Begründung:** Audited (von Paul Miller, dem `@noble`-Maintainer), dependency-free, pure JS. Kompatibel mit Expo Managed Workflow.
**Alternativen verworfen:** `react-native-crystals` (pre-Standardization, Kyber/Dilithium statt ML-KEM/ML-DSA), Custom-WASM-Build (zu aufwendig).
**Erfüllt Requirements:** FR-Session-1, FR-Token-2 (App-Seite).
**Quelle:** https://github.com/paulmillr/noble-post-quantum

#### AES-256-GCM

**Wahl:** `@noble/ciphers` (latest stable)
**Funktion:** AES-256-GCM-Verschlüsselung/-Entschlüsselung der API-Payloads.
**Begründung:** Vom selben Autor wie `@noble/post-quantum`. Konsistente Library-Suite. Audited, dependency-free, pure JS.
**Alternativen verworfen:** `expo-crypto` (kein AES-GCM-Support), `crypto-js` (älter, weniger auditiert), `react-native-aes-crypto` (native module, nicht Expo-Managed-kompatibel).
**Erfüllt Requirements:** FR-DataChannel-1.
**Quelle:** https://github.com/paulmillr/noble-ciphers

#### HKDF und SHA-256

**Wahl:** `@noble/hashes` (latest stable)
**Funktion:** HKDF-Schlüsselableitung (Session-Key aus ML-KEM-Shared-Secret), SHA-256 als unterliegender Hash.
**Begründung:** Gleiche `@noble`-Suite. HKDF mit SHA-256 ist Standard für unseren Use-Case.
**Alternativen verworfen:** `crypto-js` (kein HKDF eingebaut), Web Crypto API (nicht durchgängig in React Native verfügbar).
**Erfüllt Requirements:** FR-Session-2.
**Quelle:** https://github.com/paulmillr/noble-hashes

#### Zufallszahlen-Polyfill

**Wahl:** `react-native-get-random-values` (latest stable)
**Funktion:** Polyfill für `crypto.getRandomValues`, das von `@noble/*` Libraries benötigt wird.
**Begründung:** Standard-Polyfill für React Native. Im `@noble/post-quantum`-Setup explizit empfohlen.
**Alternativen verworfen:** `expo-crypto` (alternativer API, weniger kompatibel), eigene Polyfill (unnötig).
**Erfüllt Requirements:** NFR-Sec-2 (sichere Nonce-Generierung).
**Quelle:** https://github.com/LinusU/react-native-get-random-values

#### Crypto-Abstraction-Layer (App-Seite)

**Wahl:** Eigene Module: `crypto/kem.ts`, `crypto/cipher.ts`, `crypto/signature.ts`
**Funktion:** Abstrahiert alle Krypto-Operationen über eine einheitliche App-interne API. Application-Code ruft `kem.encaps(pk)` statt `mlKem768.encapsulate(pk)`.
**Begründung:** Spiegelung der Server-seitigen Crypto-Abstraction-Layer auf der App-Seite. Erlaubt Algorithmus-Wechsel ohne App-Code-Änderung (nur die internen Module wechseln das konkrete `@noble`-Pakete-Modul aus).
**Alternativen verworfen:** Direktaufrufe von `@noble/*` im Application-Code (verletzt Crypto-Agility-Prinzip).
**Erfüllt Requirements:** FR-Crypto-1, FR-Crypto-2, FR-Crypto-3 (App-Seite).
**Quelle:** Eigene Implementation.

---

## 4. Dev-Tooling

### 4.1 Testing

#### Server-Testing

**Wahl:** pytest mit pytest-asyncio
**Funktion:** Unit- und Integration-Tests für den Auth-Service.
**Begründung:** De-facto-Standard für Python. pytest-asyncio für FastAPI's async-Code.
**Alternativen verworfen:** unittest (mehr Boilerplate), nose (deprecated).
**Erfüllt Requirements:** Operations-Best-Practice.
**Quelle:** https://docs.pytest.org/

#### Mobile-Testing

**Wahl:** Jest mit React Native Testing Library
**Funktion:** Unit- und Component-Tests für die App.
**Begründung:** Default im Expo-Template. Bewährter Stack für RN.
**Alternativen verworfen:** Vitest (für RN nicht etabliert).
**Erfüllt Requirements:** Operations-Best-Practice.
**Quelle:** https://jestjs.io/, https://callstack.github.io/react-native-testing-library/

### 4.2 Linting und Formatting

#### Python

**Wahl:** ruff (latest stable, 0.6+)
**Funktion:** Linter und Formatter für Python-Code, ersetzt flake8 + black.
**Begründung:** 2026-Standard, sehr schnell (Rust-implementiert), eine Library statt zwei. Konfiguration via `pyproject.toml`.
**Alternativen verworfen:** flake8 + black separat (zwei Tools statt einem), pylint (langsam).
**Erfüllt Requirements:** Operations-Best-Practice.
**Quelle:** https://docs.astral.sh/ruff/

#### JavaScript/TypeScript

**Wahl:** eslint + prettier (Default im Expo-Template)
**Funktion:** Linting und Formatting für TS/TSX-Code.
**Begründung:** Default-Setup von Expo, etabliert.
**Alternativen verworfen:** Biome (modern, aber für RN noch kleiner, eslint-Plugins für RN sind essenziell).
**Erfüllt Requirements:** Operations-Best-Practice.
**Quelle:** https://eslint.org/, https://prettier.io/

### 4.3 Type-Checking

#### Python

**Wahl:** mypy (latest stable, 1.11+)
**Funktion:** Statische Type-Checks für Python-Code, insbesondere Crypto-Module mit Strict-Mode.
**Begründung:** Standard für Python Type-Checking. Strict-Mode für kritische Module wie Crypto sinnvoll.
**Alternativen verworfen:** pyright (gut, aber Microsoft-getrieben, weniger Python-community), pyre (Meta-eigen, weniger gepflegt).
**Erfüllt Requirements:** NFR-Maint-3.
**Quelle:** https://mypy-lang.org/

#### TypeScript

**Wahl:** tsc (TypeScript Compiler)
**Funktion:** Type-Checks für TS-Code, eingebaut in den TypeScript-Compiler.
**Begründung:** Built-in, kein zusätzliches Tool nötig. IDE-Integration ist out-of-the-box.
**Alternativen verworfen:** N/A (tsc ist der Standard).
**Erfüllt Requirements:** NFR-Maint-3.
**Quelle:** https://www.typescriptlang.org/

### 4.4 Package Management

#### Python

**Wahl:** uv (latest stable, 0.4+)
**Funktion:** Modernes Python-Package-Management. Ersetzt pip + venv + pip-tools.
**Begründung:** 2026-modern, sehr schnell (Rust-implementiert), zukunftsorientiert. Alles in einem Tool (venv-Erstellung, install, lock).
**Alternativen verworfen:** pip mit requirements.txt (älter, langsamer, mehr manuelles venv-Management), Poetry (anderer Workflow, weniger 2026-Mainstream).
**Erfüllt Requirements:** Operations-Best-Practice.
**Quelle:** https://docs.astral.sh/uv/

#### JavaScript/TypeScript

**Wahl:** npm (Default mit Expo)
**Funktion:** Mobile-Dependencies-Verwaltung.
**Begründung:** Default mit Expo-Template, etabliert.
**Alternativen verworfen:** yarn (etwa gleichwertig), pnpm (effizienter, aber für Expo weniger getestet).
**Erfüllt Requirements:** Operations-Best-Practice.
**Quelle:** https://www.npmjs.com/

### 4.5 CI/CD (Optional)

#### CI-Pipeline

**Wahl:** Optional, GitHub Actions (Could-Goal)
**Funktion:** Automatische Tests bei jedem Push.
**Begründung:** Kein direkter Bewertungs-Faktor, aber demonstriert DevOps-Awareness. Wird nur umgesetzt, wenn nach den Must-Goals und High-Should-Goals genug Zeit bleibt.
**Setup-Aufwand:** Ca. 2-4 Stunden für initial Setup.
**Erfüllt Requirements:** Optional, Stretch-Goal.
**Quelle:** https://github.com/features/actions

### 4.6 Versionskontrolle

#### Git

**Wahl:** Git mit GitHub als Remote
**Funktion:** Versionierung des gesamten Projekts (Server-Code, Mobile-Code, Dokumentation).
**Begründung:** Standard. Repository auch fürs Quellenverzeichnis als Verweis im Bericht.
**Alternativen verworfen:** N/A (Git ist Standard).
**Erfüllt Requirements:** Operations-Best-Practice.
**Quelle:** https://git-scm.com/, https://github.com/

---

## 5. Versionsverlauf

| Version | Datum | Änderung |
|---|---|---|
| 1.0 | 08.05.2026 | Initial-Version. Alle Tech-Stack-Entscheidungen pro Layer dokumentiert: Server (Infrastruktur, Application, Crypto, Data, Operations, Federation), Mobile (App-Framework, Auth, Crypto), Dev-Tooling (Testing, Linting, Type-Checking, Package-Management, CI optional, Versionskontrolle). |
