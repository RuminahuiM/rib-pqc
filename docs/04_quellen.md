# Quellen-Arbeitsdokument

**Zweck:** Sammlung aller externen Quellen, die im Verlauf des Projekts "Implementing PQC" verwendet wurden. Wird laufend ergänzt und dient als Grundlage für das spätere Quellenverzeichnis im Abschlussbericht.

**Stand:** 08.05.2026 (wird fortlaufend gepflegt)

**Eintragsformat:** Titel, URL, Typ (Standard/Spec/Paper/Doku/Blog/Library), Verwendung im Projekt, Zugriffsdatum.

---

## 1. Offizielle Standards (NIST)

### 1.1 FIPS 203: Module-Lattice-Based Key-Encapsulation Mechanism Standard (ML-KEM)
- **URL:** https://nvlpubs.nist.gov/nistpubs/fips/nist.fips.203.pdf
- **Typ:** Standard
- **Verwendung:** Definiert ML-KEM-768, das Kern-KEM für unsere App-Layer PQ-Session. Referenz für Encaps/Decaps-Operationen.
- **Zugriff:** 05.2026

### 1.2 FIPS 204: Module-Lattice-Based Digital Signature Standard (ML-DSA)
- **URL:** https://nvlpubs.nist.gov/nistpubs/fips/nist.fips.204.pdf
- **Typ:** Standard
- **Verwendung:** Definiert ML-DSA-65, der Signatur-Algorithmus für unsere Broker-Tokens.
- **Zugriff:** 05.2026

### 1.3 FIPS 205: Stateless Hash-Based Digital Signature Standard (SLH-DSA)
- **URL:** https://nvlpubs.nist.gov/nistpubs/fips/nist.fips.205.pdf
- **Typ:** Standard
- **Verwendung:** Nur konzeptionell erwähnt. Für mobile Use Cases ungeeignet wegen grosser Signaturen.
- **Zugriff:** 05.2026

### 1.4 NIST CSWP 39: Considerations for Achieving Crypto Agility
- **URL:** https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.39.pdf
- **Typ:** White Paper
- **Verwendung:** Grundlegende Prinzipien der Crypto-Agility, die in unsere Crypto-Abstraction-Layer-Architektur eingeflossen sind.
- **Zugriff:** 05.2026

---

## 2. IETF-Drafts und RFCs

### 2.1 draft-ietf-tls-ecdhe-mlkem-04: Post-quantum hybrid ECDHE-MLKEM Key Agreement for TLSv1.3
- **URL:** https://datatracker.ietf.org/doc/draft-ietf-tls-ecdhe-mlkem/
- **Typ:** IETF Draft
- **Verwendung:** Grundlage für unsere hybride TLS-Konfiguration (X25519MLKEM768, NamedGroup `0x11ec`) auf der Server-Seite via nginx + oqs-provider.
- **Zugriff:** 05.2026

### 2.2 draft-ietf-tls-mlkem-07: ML-KEM Post-Quantum Key Agreement for TLS 1.3
- **URL:** https://datatracker.ietf.org/doc/draft-ietf-tls-mlkem/
- **Typ:** IETF Draft
- **Verwendung:** Pure-PQ-Variante (ohne klassischen Hybrid). Konzeptionell relevant, nicht in unserem produktiv eingesetzten Stack.
- **Zugriff:** 05.2026

### 2.3 draft-ietf-jose-pqc: Post-Quantum Algorithms for JOSE
- **URL:** https://datatracker.ietf.org/doc/draft-ietf-jose-pqc/
- **Typ:** IETF Draft
- **Verwendung:** Definiert PQC-`alg`-Werte für JWS und JWE. Wir orientieren uns daran für unsere ML-DSA-signierten Broker-Tokens, obwohl der Draft noch nicht ratifiziert ist.
- **Zugriff:** 05.2026

### 2.4 draft-ietf-hpke-pq-03: Post-Quantum and Post-Quantum/Traditional Hybrid Algorithms for HPKE
- **URL:** https://datatracker.ietf.org/doc/draft-ietf-hpke-pq/
- **Typ:** IETF Draft
- **Verwendung:** Referenz für hybride KEM-Kombinationen, relevant für unseren Stretch-Goal "hybrider Key-Combiner im App-Layer".
- **Zugriff:** 05.2026

### 2.5 RFC 5869: HMAC-based Extract-and-Expand Key Derivation Function (HKDF)
- **URL:** https://datatracker.ietf.org/doc/html/rfc5869
- **Typ:** RFC
- **Verwendung:** Für die Ableitung des AES-256-GCM-Session-Keys aus dem ML-KEM Shared Secret nach der Session-Etablierung.
- **Zugriff:** 05.2026

### 2.6 RFC 6749: OAuth 2.0 Authorization Framework
- **URL:** https://datatracker.ietf.org/doc/html/rfc6749
- **Typ:** RFC
- **Verwendung:** Grundlage für den Authorization-Code-Flow mit PKCE, den wir als OIDC-Client gegenüber Google und Microsoft nutzen.
- **Zugriff:** 05.2026

---

## 3. OpenID Connect

### 3.1 OpenID Connect Core 1.0 Specification
- **URL:** https://openid.net/specs/openid-connect-core-1_0.html
- **Typ:** Standard
- **Verwendung:** Referenz für ID-Token-Aufbau, Discovery, UserInfo. Wir konsumieren OIDC (Client-Rolle) gegenüber Google/Microsoft.
- **Zugriff:** 05.2026

### 3.2 OpenID Foundation: How OpenID Connect Works
- **URL:** https://openid.net/developers/how-connect-works/
- **Typ:** Doku
- **Verwendung:** Erklärung der OIDC-Rollen (RP, OP, End User) und des Flows. Grundlage für die Architektur-Diskussion.
- **Zugriff:** 05.2026

### 3.3 OpenID Foundation: Post-Quantum Identity Standards
- **URL:** https://openid.net/post-quantum-identity-standards/
- **Typ:** Whitepaper
- **Verwendung:** Position der OpenID Foundation zur PQ-Migration von OIDC. Begründung für die Aussage, dass die grossen IdPs 2026 noch keine PQ-Tokens ausstellen.
- **Zugriff:** 05.2026

### 3.4 Curity: What Is OpenID Connect, and How Does It Work?
- **URL:** https://curity.io/resources/learn/openid-connect-overview/
- **Typ:** Blog/Doku
- **Verwendung:** Übersichtliche Erklärung der OIDC-Konzepte, verwendet zur Klärung der Rollen.
- **Zugriff:** 05.2026

### 3.5 Microsoft Learn: OpenID Connect authentication with Entra ID
- **URL:** https://learn.microsoft.com/en-us/entra/architecture/auth-oidc
- **Typ:** Doku
- **Verwendung:** Referenz für Microsoft als OIDC-Provider, für die spätere Federation-Implementierung.
- **Zugriff:** 05.2026

---

## 4. Identity Broker / Federation Patterns

### 4.1 Red Hat: Identity Brokering (Server Administration Guide)
- **URL:** https://docs.redhat.com/en/documentation/red_hat_single_sign-on/7.0/html/server_administration_guide/identity_broker
- **Typ:** Doku
- **Verwendung:** Definition und Best Practices des Identity-Broker-Patterns. Grundlage für unsere Architektur-Entscheidung Option 3.
- **Zugriff:** 05.2026

### 4.2 Zitadel: Identity Brokering Concepts
- **URL:** https://zitadel.com/docs/concepts/features/identity-brokering
- **Typ:** Doku
- **Verwendung:** Industrie-Referenz, wie ein moderner Identity Broker aussieht.
- **Zugriff:** 05.2026

### 4.3 Amazon Cognito Federation Implementation Guide
- **URL:** https://hidekazu-konishi.com/entry/amazon_cognito_federation_implementation_guide.html
- **Typ:** Blog
- **Verwendung:** Praxis-Beispiel für Federation mit Google, Apple, Microsoft. Referenz für die Architektur-Diskussion.
- **Zugriff:** 05.2026

---

## 5. Crypto-Agility

### 5.1 IBM Quantum Blog: Crypto-agility and quantum-safe readiness
- **URL:** https://www.ibm.com/quantum/blog/crypto-agility
- **Typ:** Blog
- **Verwendung:** Allgemeines Verständnis der Crypto-Agility-Prinzipien, Stand 2025-2026.
- **Zugriff:** 05.2026

### 5.2 Cryptomathic: What is a Crypto-Abstraction Layer?
- **URL:** https://www.cryptomathic.com/blog/what-is-a-crypto-abstraction-layer
- **Typ:** Blog
- **Verwendung:** Konkrete Pattern-Beschreibung für die Crypto-Abstraction-Layer, die wir im Auth-Service implementieren.
- **Zugriff:** 05.2026

### 5.3 Software-Defined Cryptography: A Design Feature of Cryptographic Agility (arXiv)
- **URL:** https://arxiv.org/html/2404.01808v2
- **Typ:** Paper
- **Verwendung:** Akademische Referenz für die Algorithmus-Registry und Konfigurations-basierte Algorithmus-Auswahl.
- **Zugriff:** 05.2026

### 5.4 Security Boulevard: PQC for Authentication, Enterprise Migration Guide 2026
- **URL:** https://securityboulevard.com/2026/03/post-quantum-cryptography-for-authentication-the-enterprise-migration-guide-2026/
- **Typ:** Blog/Whitepaper
- **Verwendung:** Aktueller Industrie-Stand zur PQ-Migration von Auth-Systemen.
- **Zugriff:** 05.2026

---

## 6. PQ-Session-Protokolle und Hybride Verschlüsselung

### 6.1 Frontiers: Design and implementation of an authenticated post-quantum session protocol (ML-KEM + ML-DSA + AES-256-GCM)
- **URL:** https://www.frontiersin.org/journals/physics/articles/10.3389/fphy.2025.1723966/full
- **Typ:** Peer-Reviewed Paper
- **Verwendung:** Direkte Referenz für unser App-Layer-Session-Protokoll. Verwendet die gleiche Algorithmus-Kombination (ML-KEM, ML-DSA, AES-256-GCM) und ähnliches HKDF-Setup.
- **Zugriff:** 05.2026

### 6.2 IACR ePrint 2018/903: Hybrid Key Encapsulation Mechanisms and Authenticated Key Exchange
- **URL:** https://eprint.iacr.org/2018/903.pdf
- **Typ:** Paper
- **Verwendung:** Theoretische Grundlage für hybride KEM-Konstruktionen, relevant für unser Stretch-Goal "Hybrid Key Combiner".
- **Zugriff:** 05.2026

### 6.3 IACR ePrint 2022/065: Practical (Post-Quantum) Key Combiners from One-Wayness and Applications to TLS
- **URL:** https://eprint.iacr.org/2022/065.pdf
- **Typ:** Paper
- **Verwendung:** Sicherheits-Analyse von Key-Combinern, wie sie in unserer hybriden Architektur eingesetzt würden.
- **Zugriff:** 05.2026

### 6.4 ETSI TS 103 744: Quantum-safe Hybrid Key Exchanges
- **URL:** https://www.etsi.org/deliver/etsi_ts/103700_103799/103744/01.01.01_60/ts_103744v010101p.pdf
- **Typ:** Standard
- **Verwendung:** Standardisierter Rahmen für hybride PQ-Schlüssel-Exchanges.
- **Zugriff:** 05.2026

### 6.5 Akamai Blog: Post-Quantum Cryptography Beyond TLS
- **URL:** https://www.akamai.com/blog/security/post-quantum-cryptography-beyond-tls
- **Typ:** Blog
- **Verwendung:** Begründung, warum Application-Layer-PQ neben TLS-PQ Sinn macht, besonders für Mobile-Szenarien.
- **Zugriff:** 05.2026

---

## 7. PQC-Bibliotheken und Tools

### 7.1 Open Quantum Safe Project (liboqs)
- **URL:** https://openquantumsafe.org/
- **Typ:** Library
- **Verwendung:** Kern-Bibliothek für PQC-Implementationen. Unsere Server-Seite nutzt sie via `liboqs-python` und `oqs-provider`.
- **Zugriff:** 05.2026

### 7.2 oqs-provider (OpenSSL 3 Plugin)
- **URL:** https://github.com/open-quantum-safe/oqs-provider
- **Typ:** Library
- **Verwendung:** OpenSSL-Provider, der ML-KEM und ML-DSA für TLS bereitstellt. Hinter nginx eingesetzt.
- **Zugriff:** 05.2026

### 7.3 openquantumsafe/oqs-ossl3 (Docker Image)
- **URL:** https://hub.docker.com/r/openquantumsafe/oqs-ossl3
- **Typ:** Container Image
- **Verwendung:** Basis für unseren Docker-Compose-Stack, vermeidet Build-Aufwand von liboqs/oqs-provider.
- **Zugriff:** 05.2026

### 7.4 liboqs-python
- **URL:** https://github.com/open-quantum-safe/liboqs-python
- **Typ:** Library
- **Verwendung:** Python-Bindings für ML-DSA-Signing und ML-KEM-Operationen im Auth-Service.
- **Zugriff:** 05.2026

### 7.5 @noble/post-quantum (npm)
- **URL:** https://github.com/paulmillr/noble-post-quantum
- **Typ:** Library
- **Verwendung:** Auditierte, dependency-freie JS-Implementierung von ML-KEM und ML-DSA für die React-Native-App.
- **Zugriff:** 05.2026

### 7.6 react-native-get-random-values
- **URL:** https://github.com/LinusU/react-native-get-random-values
- **Typ:** Library
- **Verwendung:** Polyfill für `crypto.getRandomValues` in React Native, nötig für `@noble/post-quantum`.
- **Zugriff:** 05.2026

---

## 8. Mobile / React Native / Expo Auth

### 8.1 Expo Documentation: Authentication
- **URL:** https://docs.expo.dev/develop/authentication/
- **Typ:** Doku
- **Verwendung:** Übersicht über Auth-Optionen in Expo, Grundlage für die OIDC-Client-Implementierung.
- **Zugriff:** 05.2026

### 8.2 Expo Documentation: Google Authentication
- **URL:** https://docs.expo.dev/guides/google-authentication/
- **Typ:** Doku
- **Verwendung:** Konkrete Schritte für Google-Federation in der RN-App.
- **Zugriff:** 05.2026

### 8.3 Expo Documentation: Authentication with OAuth or OpenID providers
- **URL:** https://docs.expo.dev/guides/authentication/
- **Typ:** Doku
- **Verwendung:** Verwendung von `expo-auth-session` für generische OIDC-Flows (Microsoft, später Apple).
- **Zugriff:** 05.2026

---

## 9. Praxis und Industrie-Perspektiven

### 9.1 PQC Today: API Security & PQC JWT, ML-DSA Signing, ML-KEM JWE & OAuth 2.0 Migration
- **URL:** https://www.pqctoday.com/learn/api-security-jwt/
- **Typ:** Industrie-Blog
- **Verwendung:** Details zu ML-DSA-Signatur-Grössen (3309 Bytes für ML-DSA-65) und deren Implikationen für JWT-Header-Limits.
- **Zugriff:** 05.2026

### 9.2 MojoAuth Blog: Quantum Computing Milestones That Will Redefine Authentication
- **URL:** https://mojoauth.com/blog/quantum-computing-milestones-that-will-redefine-authentication
- **Typ:** Industrie-Blog
- **Verwendung:** Übersicht über kommerzielle CIAM-Plattformen und ihre PQ-Roadmap.
- **Zugriff:** 05.2026

### 9.3 Secure Identity Alliance: Preparing for Post-Quantum Cryptography in Identity Documents
- **URL:** https://secureidentityalliance.org/insights/preparing-for-post-quantum-cryptography-in-identity-documents/
- **Typ:** Industrie-Bericht
- **Verwendung:** Allgemeiner Kontext zur PQ-Migration in Identity-Systemen.
- **Zugriff:** 05.2026

---

## 10. Praktische OIDC-Implementations-Referenzen

### 10.1 GitHub: post-quantum-oidc-oauth2 (fredericoschardong)
- **URL:** https://github.com/fredericoschardong/post-quantum-oidc-oauth2
- **Typ:** Referenz-Implementierung
- **Verwendung:** Akademische PQ-OIDC-Implementation als Vergleich/Inspiration.
- **Zugriff:** 05.2026

### 10.2 GitHub: golang-jwt-pqc (salrashid123)
- **URL:** https://github.com/salrashid123/golang-jwt-pqc
- **Typ:** Referenz-Implementierung
- **Verwendung:** Go-basiertes Beispiel für PQC-signierte JWTs. Nicht direkt genutzt (anderes Sprach-Ökosystem), aber als Konzept-Referenz.
- **Zugriff:** 05.2026

---

## 11. Tech-Stack-Komponenten (Server-Side)

### 11.1 FastAPI
- **URL:** https://fastapi.tiangolo.com/
- **Typ:** Framework
- **Verwendung:** Web-Framework des Auth-Service. Implementiert die HTTP-Endpoints für lokale Auth, Federation, Session-Etablierung und geschützte API-Calls.
- **Zugriff:** 05.2026

### 11.2 Uvicorn
- **URL:** https://www.uvicorn.org/
- **Typ:** ASGI-Server
- **Verwendung:** Hostet die FastAPI-App hinter nginx.
- **Zugriff:** 05.2026

### 11.3 PyJWT
- **URL:** https://pyjwt.readthedocs.io/
- **Typ:** Library
- **Verwendung:** Verifikation der externen ID-Tokens (Google, Microsoft) mit RS256/ES256 im Federation-Flow. Nicht für interne Broker-Token-Signierung (kein ML-DSA-Support in 2026).
- **Zugriff:** 05.2026

### 11.4 argon2-cffi
- **URL:** https://argon2-cffi.readthedocs.io/
- **Typ:** Library
- **Verwendung:** Argon2id Password-Hashing für lokale User-Passwörter im User-Store.
- **Zugriff:** 05.2026

### 11.5 cryptography (pyca/cryptography)
- **URL:** https://cryptography.io/
- **Typ:** Library
- **Verwendung:** HKDF-Schlüsselableitung, AES-256-GCM-Verschlüsselung und klassische Krypto-Primitive auf der Server-Seite.
- **Zugriff:** 05.2026

### 11.6 SQLAlchemy 2.x
- **URL:** https://www.sqlalchemy.org/
- **Typ:** ORM
- **Verwendung:** Typed ORM-Layer für den SQLite-basierten User-Store. Bietet async-Support für FastAPI-Integration.
- **Zugriff:** 05.2026

### 11.7 Alembic
- **URL:** https://alembic.sqlalchemy.org/
- **Typ:** Tool
- **Verwendung:** Schema-Migrationen für den User-Store. Versioniert das DB-Schema.
- **Zugriff:** 05.2026

### 11.8 Redis
- **URL:** https://redis.io/
- **Typ:** Datenbank / In-Memory Store
- **Verwendung:** Session-Store für aktive PQ-Sessions mit TTL. Überlebt Service-Restarts. Erweiterbar für JWKS-Cache und Rate-Limiting.
- **Zugriff:** 05.2026

### 11.9 redis-py
- **URL:** https://redis.readthedocs.io/
- **Typ:** Library
- **Verwendung:** Python-Client für Redis (async-Variante `redis.asyncio`).
- **Zugriff:** 05.2026

### 11.10 Authlib
- **URL:** https://authlib.org/
- **Typ:** Library
- **Verwendung:** OIDC-Client-Library für Federation mit Google und Microsoft. Implementiert Authorization Code Flow mit PKCE, JWKS-Verifikation und Discovery. Version 1.7.2 (Release Mai 2026).
- **Zugriff:** 05.2026

### 11.11 httpx
- **URL:** https://www.python-httpx.org/
- **Typ:** Library
- **Verwendung:** Async-HTTP-Client für externe Calls zu Google- und Microsoft-Endpoints. Wird von Authlib intern verwendet.
- **Zugriff:** 05.2026

### 11.12 structlog
- **URL:** https://www.structlog.org/
- **Typ:** Library
- **Verwendung:** Strukturiertes JSON-Logging für den Auth-Service. Erfüllt NFR-Ops-1.
- **Zugriff:** 05.2026

### 11.13 pydantic-settings
- **URL:** https://docs.pydantic.dev/latest/concepts/pydantic_settings/
- **Typ:** Library
- **Verwendung:** Typed Config-Management aus YAML und ENV-Variablen, mit Validierung beim Service-Start.
- **Zugriff:** 05.2026

---

## 12. Tech-Stack-Komponenten (Mobile, Ergänzungen zu Sektion 8)

### 12.1 Expo Router
- **URL:** https://docs.expo.dev/router/introduction/
- **Typ:** Library
- **Verwendung:** File-basiertes Routing zwischen den Screens der Mock-App (Login, Home, Profil).
- **Zugriff:** 05.2026

### 12.2 expo-secure-store
- **URL:** https://docs.expo.dev/versions/latest/sdk/securestore/
- **Typ:** Library
- **Verwendung:** Speicherung des Broker-Tokens in iOS Keychain bzw. Android Keystore.
- **Zugriff:** 05.2026

### 12.3 @noble/ciphers
- **URL:** https://github.com/paulmillr/noble-ciphers
- **Typ:** Library
- **Verwendung:** AES-256-GCM-Verschlüsselung der API-Payloads in der Mock-App.
- **Zugriff:** 05.2026

### 12.4 @noble/hashes
- **URL:** https://github.com/paulmillr/noble-hashes
- **Typ:** Library
- **Verwendung:** HKDF und SHA-256 in der Mock-App.
- **Zugriff:** 05.2026

---

## 13. Dev-Tooling

### 13.1 pytest
- **URL:** https://docs.pytest.org/
- **Typ:** Framework
- **Verwendung:** Server-side Unit- und Integration-Tests. Mit `pytest-asyncio` für FastAPI's async-Code.
- **Zugriff:** 05.2026

### 13.2 Jest
- **URL:** https://jestjs.io/
- **Typ:** Framework
- **Verwendung:** Mobile-side Unit- und Component-Tests. Default mit Expo.
- **Zugriff:** 05.2026

### 13.3 React Native Testing Library
- **URL:** https://callstack.github.io/react-native-testing-library/
- **Typ:** Library
- **Verwendung:** Component-Tests in der Mock-App.
- **Zugriff:** 05.2026

### 13.4 ruff
- **URL:** https://docs.astral.sh/ruff/
- **Typ:** Tool
- **Verwendung:** Python-Linter und -Formatter. Ersetzt flake8 + black.
- **Zugriff:** 05.2026

### 13.5 mypy
- **URL:** https://mypy-lang.org/
- **Typ:** Tool
- **Verwendung:** Statische Type-Checks für Python-Code.
- **Zugriff:** 05.2026

### 13.6 uv
- **URL:** https://docs.astral.sh/uv/
- **Typ:** Tool
- **Verwendung:** Modernes Python-Package-Management. Ersetzt pip + venv + pip-tools in einem Tool.
- **Zugriff:** 05.2026

### 13.7 GitHub Actions (optional)
- **URL:** https://github.com/features/actions
- **Typ:** Service
- **Verwendung:** Optional, falls Zeit reicht: automatische Tests bei jedem Push. Could-Goal.
- **Zugriff:** 05.2026

---

## Anhang: Hinweise zur Pflege dieses Dokuments

- Neue Quellen werden in die thematisch passende Sektion eingeordnet. Falls keine passende Sektion existiert, eine neue anlegen.
- Jeder Eintrag braucht: Titel, URL, Typ, Verwendung im Projekt, Zugriffsdatum.
- Wenn eine Quelle in mehreren Projektteilen verwendet wird, das in der "Verwendung"-Zeile vermerken.
- Beim Erstellen des finalen Quellenverzeichnisses für den Bericht werden die Einträge in das Zitierformat der TBZ übernommen (Format wird im Bericht-Sprint geklärt).
