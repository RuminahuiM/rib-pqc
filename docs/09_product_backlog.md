# Product Backlog: Implementing PQC

**Projekt:** Implementing PQC (Semesterarbeit 3, ITCNE25)
**Autor:** Dodoe Rumiñahui Mannale
**Erstellt:** 17.05.2026
**Status:** Initial-Version (v1.0)

**Bezug:** Konkretisiert die Scrum-Praxis aus `08_scrum_setup.md` mit dem Inhalt der Arbeit. Quellen für die Stories: Use Cases und Functional/Non-Functional Requirements aus `05_requirements.md`, Komponenten und Module aus `07_design.md`, Tech-Stack-Constraints aus `06_tech_stack.md`.

---

## Inhaltsverzeichnis

1. [Einleitung und Konventionen](#1-einleitung-und-konventionen)
2. [Epic-Übersicht](#2-epic-übersicht)
3. [Sprint-Allokations-Übersicht](#3-sprint-allokations-übersicht)
4. [Backlog: Epics und Stories](#4-backlog-epics-und-stories)
   - [Epic INF: Infrastructure und Tooling](#epic-inf-infrastructure-und-tooling)
   - [Epic SKL: Skeletons](#epic-skl-skeletons)
   - [Epic CRY: Crypto-Abstraction-Layer](#epic-cry-crypto-abstraction-layer)
   - [Epic AUT: Local Authentication](#epic-aut-local-authentication)
   - [Epic TOK: Token Service](#epic-tok-token-service)
   - [Epic BRK: Identity Broker / Federation](#epic-brk-identity-broker--federation)
   - [Epic TLS: Hybrid TLS Transport](#epic-tls-hybrid-tls-transport)
   - [Epic SES: PQ Session](#epic-ses-pq-session)
   - [Epic DCH: Data Channel](#epic-dch-data-channel)
   - [Epic APP: Mobile App UI und Integration](#epic-app-mobile-app-ui-und-integration)
   - [Epic QUA: Quality (Tests und Benchmarks)](#epic-qua-quality-tests-und-benchmarks)
   - [Epic DOC: Documentation und Reporting](#epic-doc-documentation-und-reporting)
   - [Epic STR: Stretch Goals](#epic-str-stretch-goals)
5. [Story-Points-Übersicht pro Sprint](#5-story-points-übersicht-pro-sprint)
6. [MoSCoW-Verteilung](#6-moscow-verteilung)
7. [Versionsverlauf](#7-versionsverlauf)

---

## 1. Einleitung und Konventionen

### 1.1 Story-Format

Jede Story folgt dem folgenden Format:

```
### <STORY-ID>: <Titel>
- Epic, Bezug, Priorität (Must/Should/Could), T-Shirt, Story Points, Sprint, Abhängigkeiten
- Story-Beschreibung im User-Story-Format (oder klar technische Beschreibung)
- Akzeptanzkriterien (AC)
```

### 1.2 Story-IDs

Story-IDs in diesem Markdown haben einen Epic-Prefix (z.B. INF-1, AUT-3). Beim Transfer nach Jira erhalten sie zusätzlich automatisch sequenzielle Jira-Keys (z.B. PQC-1, PQC-2). Die Mapping wird beim Jira-Setup festgehalten.

### 1.3 Priorisierung (4 Achsen)

Die Priorisierung der Stories in diesem Projekt erfolgt entlang von vier komplementären Achsen, die sich gegenseitig ergänzen. Jede Achse beantwortet eine andere Frage und gemeinsam ergeben sie eine eindeutige Reihenfolge sowohl auf Projekt- als auch auf Sprint-Ebene.

**Achse 1: MoSCoW (Was muss gemacht werden)**

Die klassische MoSCoW-Kategorisierung steht im Backlog-Markdown pro Story als Feld `Priorität` und wird in Jira als Label (`must`, `should`, `could`) gepflegt.

- **Must:** Erfolgskriterium des Projekts, ohne dieses Item kann das Product Goal nicht erreicht werden.
- **Should:** Wichtig für die Qualität oder Vollständigkeit der Story, aber nicht blockierend für den Abgabe-Erfolg.
- **Could:** Stretch-Goal, nur bei vorhandenem Slack zu bearbeiten.

**Achse 2: Sprint-Zuordnung (Wann)**

Jede Story ist einem Sprint zugewiesen (Sprint 0 bis 4 plus Stretch-Slot). Die Allokation ergibt sich aus Abhängigkeiten (Voraussetzungs-Beziehungen, Bottom-up: erst Foundation, dann Aufbau) und aus Risiko (riskante Stories früh, damit Lernen und Re-Planning möglich ist). Siehe Sektion 3 in diesem Dokument für die initiale Allokation und Abschnitt 3 im Sprint-Journal-Planning für die jeweils aktuelle Sprint-Zusammensetzung. Im Jira wird die Sprint-Zuordnung über das Sprint-Feld (nicht über Labels) abgebildet, sobald Sprint-Objekte existieren.

**Achse 3: Stretch-Markierung (Optional innerhalb Sprint-Slot)**

Manche Stories sind einem Sprint zugewiesen, aber nur "wenn Slack vorhanden". Sie werden im Jira mit einem Label gekennzeichnet:

- `sprint-stretch`: Story gehört zu einem konkreten Sprint, wird aber nur bei verbleibender Kapazität nach Erfüllung des Sprint-Goals angerührt. Beispiel: APP-1, APP-4, APP-9 in Sprint 1.
- `project-stretch`: Story gehört nicht zu einem konkreten Sprint, sondern zum Epic STR und wird erst nach Erreichen aller Must-Stories des Projekts angegangen.

**Achse 4: Built-in Jira Priority Field (Reihenfolge innerhalb Sprint)**

Damit innerhalb eines Sprints sofort sichtbar ist, welche Stories am Critical Path liegen (also andere Stories blockieren) und welche unabhängig sind, wird zusätzlich das in Jira eingebaute Priority-Feld gepflegt. Die Konvention:

- **Highest:** Critical Path im aktuellen Sprint, Story blockiert mehrere andere. Wird zuerst gearbeitet.
- **High:** Must im aktuellen Sprint, aber nicht blockierend für andere Stories. Auch Defer-Kandidaten (Should die im Sprint geplant sind aber als erste herausfallen wenn Scope-Cut nötig).
- **Medium:** Must in einem späteren Sprint (Sprint 2/3/4), noch nicht aktiv.
- **Low:** Should aus jedem Sprint.
- **Lowest:** Could/Stretch, egal ob `sprint-stretch` oder `project-stretch`.

Die Built-in Priority wird pro Story einmal initial gesetzt und bei Sprint-Refinement oder Scope-Anpassung bei Bedarf nachgezogen. Sie ist insbesondere im Sprint-Board nützlich, weil sie ein farbiges Icon erzeugt das beim ersten Blick zeigt was zuerst gemacht werden muss. Die konkrete Setz-Anleitung und das Mapping-Schema für Jira liegen in `10_jira_setup.md` Sektion 2.

**Zusammenspiel der Achsen am Beispiel CRY-1 in Sprint 1:**

- MoSCoW: `must` (Crypto-Facade ist Erfolgskriterium)
- Sprint: `Sprint 1` (Foundation muss früh stehen)
- Stretch: kein Label (kein Stretch)
- Built-in Priority: `Highest` (blockiert AUT, TOK, SES, alle weiteren Crypto-Stories)

Und am Beispiel APP-9 in Sprint 1:

- MoSCoW: `must` (Mobile-App-UI ist Erfolgskriterium)
- Sprint: `Sprint 1` (UI-Skelett früh ist sinnvoll)
- Stretch: `sprint-stretch` (Sprint 1 ist überzeichnet, APP-Stories sind erste Cut-Kandidaten)
- Built-in Priority: `Lowest` (Stretch innerhalb des Sprints, nicht blockierend)

### 1.4 Refinement-Stufe

Stories für **Sprint 0, 1 und 2** haben volle Akzeptanzkriterien (refinement abgeschlossen). Stories für **Sprint 3 und 4** haben Summary-AC; volle Refinement passiert im jeweiligen Sprint-Planning (Just-in-Time-Refinement, Scrum-Standard).

### 1.5 Slicing

Stories sind horizontal gesliced (eine Story = eine Schicht oder eine Komponente). Begründung: für Solo-Dev effizienter als vertikale Slices. Der Sprint-Goal-Zusammenhang sorgt am Sprint-Ende für eine vertikal demonstrierbare Funktionalität.

### 1.6 Definition of Ready und Definition of Done

Siehe `08_scrum_setup.md` Abschnitte 6 (DoR plus Akzeptanzkriterien) und 5.3 (DoD).

### 1.7 AI-Multiplier (wichtig fürs Lesen der Schätzungen)

Die Story-Points und T-Shirt-Sizes in diesem Backlog sind als **klassische Solo-Dev-Schätzungen ohne AI-Unterstützung** zu lesen. Tatsächlich wird die Arbeit mit Claude / Claude Code durchgeführt mit einer ungefähren Beschleunigung von **1.5x**. Die Schätzungen werden bewusst nicht angepasst, damit am Projekt-Ende ein empirischer Vergleich von geschätzter zu tatsächlicher Arbeitszeit den AI-Multiplier für dieses Projekt quantifizierbar macht. Details siehe `08_scrum_setup.md` Abschnitt 7.4.

---

## 2. Epic-Übersicht

| Epic-ID | Titel | Bezug zu Design/Requirements | Anzahl Stories |
|---|---|---|---|
| INF | Infrastructure und Tooling | Querschnitt | 4 |
| SKL | Skeletons | Querschnitt | 2 |
| CRY | Crypto-Abstraction-Layer | FR-Crypto-1 bis FR-Crypto-3, Design 2.1, 6.1 | 7 |
| AUT | Local Authentication | UC-1, FR-Auth-1, FR-Auth-2, NFR-Sec-4 | 4 |
| TOK | Token Service | FR-Token-1, FR-Token-2, FR-Token-3 | 4 |
| BRK | Identity Broker / Federation | UC-2, UC-3, FR-Broker-1 bis FR-Broker-4, NFR-Sec-5 | 7 |
| TLS | Hybrid TLS Transport | NFR-Sec-1 | 3 |
| SES | PQ Session | UC-4, FR-Session-1 bis FR-Session-4 | 4 |
| DCH | Data Channel | UC-5, FR-DataChannel-1, FR-DataChannel-2, NFR-Sec-2 | 4 |
| APP | Mobile App UI und Integration | Design 2.2, UCs aus Sicht des Clients | 9 |
| QUA | Quality (Tests und Benchmarks) | NFR-Perf-1 bis NFR-Perf-3, NFR-Maint-1 | 8 |
| DOC | Documentation und Reporting | Bewertungs-Kriterium 1 bis 4, Abgabe-Pflicht | 4 |
| STR | Stretch Goals | FR-Crypto-4, NFR-Sec-6, optionale Items | 3 |
| SEC | Security Infrastructure (nachträglich aus PQC-19 Closing-Review) | NFR-Sec-3 (Web-Security-Baseline) | 5 |

**Total Stories:** 68 (63 initial plus 5 SEC-Stories nachträglich aus Sprint-1-Reviews)

---

## 3. Sprint-Allokations-Übersicht

| Sprint | Zeitraum | Epic-Schwerpunkt | Stories (gekürzt) |
|---|---|---|---|
| Sprint 0 | 06.05 bis 24.05 | INF (Setup, Recherche, Dokumente) | INF-1, INF-2, INF-3, INF-4 |
| Sprint 1 | 25.05 bis 31.05 | SKL + CRY (Foundation) + AUT + TOK | SKL-1, SKL-2, CRY-1, CRY-2 (partial), CRY-5, AUT-1, AUT-2, AUT-3, AUT-4, TOK-1, TOK-2, APP-1, APP-4, APP-9, QUA-1, QUA-2, QUA-3 |
| Sprint 2 | 01.06 bis 14.06 | BRK + TLS + Federation-Integration + SEC | BRK-1, BRK-2, BRK-3, BRK-4, BRK-5, BRK-6, BRK-7, TLS-1, TLS-2, TLS-3, APP-7, APP-8, SEC-1, SEC-2, SEC-3, SEC-4, SEC-5 |
| Sprint 3 | 15.06 bis 28.06 | SES + DCH + Client-Crypto + Algorithmus-Demo | CRY-3, CRY-4, CRY-6, CRY-7, SES-1, SES-2, SES-3, SES-4, DCH-1, DCH-2, DCH-3, DCH-4, APP-2, APP-3, APP-5, APP-6, QUA-4, QUA-5 |
| Sprint 4 | 29.06 bis 05.07 | DOC + Benchmarks + Polish | TOK-3, TOK-4, DOC-1, DOC-2, DOC-3, DOC-4, QUA-6, QUA-7, QUA-8 |
| Stretch | nach Slack | STR | STR-1, STR-2, STR-3 |

**Hinweis zur Allokation:** Diese Allokation ist die initiale Planung. Pro Sprint-Planning wird sie konkret bestätigt oder angepasst. Aus Adaption-Sicht ist Verschiebung explizit erlaubt.

---

## 4. Backlog: Epics und Stories

### Epic INF: Infrastructure und Tooling

**Ziel:** Tooling, Repo, Container-Basis und Projekt-Management-Werkzeuge stehen, damit produktive Arbeit beginnen kann.

#### INF-1: Jira-Projekt aufsetzen

- **Epic:** INF
- **Bezug:** B5.9 (Projekt-Fortschritts-Dokumentation)
- **Priorität:** Must
- **T-Shirt:** S | **Story Points:** 2 | **Sprint:** 0

**Story:**
Als Studierender möchte ich ein konfiguriertes Jira-Projekt haben, damit ich Backlog und Sprints zentral verwalten kann.

**Akzeptanzkriterien:**

- AC-1: Jira Cloud Free Workspace existiert mit Team-managed Scrum-Template.
- AC-2: Projekt-Key ist `PQC`, Workflow hat Spalten To Do / In Progress / In Review / Done.
- AC-3: Custom Fields "Story Points", "Acceptance Criteria", "Bezug-zu-Requirement" sind vorhanden.
- AC-4: Mentor-Termine sind als Releases/Versionen eingetragen.

---

#### INF-2: GitHub-Repo und Branch-Struktur aufsetzen

- **Epic:** INF
- **Bezug:** B5.9, B5.10
- **Priorität:** Must
- **T-Shirt:** S | **Story Points:** 2 | **Sprint:** 0

**Story:**
Als Studierender möchte ich ein GitHub-Repository mit Mono-Repo-Struktur und Branch-Konventionen haben, damit Code und Dokumentation versioniert und nachvollziehbar sind.

**Akzeptanzkriterien:**

- AC-1: Public GitHub-Repo `implementing-pqc` existiert (oder privat mit Lese-Zugriff für Mentoren).
- AC-2: Top-Level-Struktur enthält `server/`, `app/`, `infra/`, `docs/`, `README.md`, `LICENSE`.
- AC-3: `main`-Branch ist geschützt (PRs erforderlich, auch wenn Solo).
- AC-4: Initiale Commit enthält die existierenden Markdown-Dokumente.

---

#### INF-3: Docker-Compose-Skeleton mit drei Services

- **Epic:** INF
- **Bezug:** Design 3.1, 06_tech_stack
- **Priorität:** Must
- **T-Shirt:** M | **Story Points:** 5 | **Sprint:** 0

**Story:**
Als Studierender möchte ich ein lauffähiges Docker-Compose-Setup mit nginx, auth-service und redis haben, damit alle Folge-Sprints auf dieser Basis aufbauen können.

**Akzeptanzkriterien:**

- AC-1: `docker-compose.yml` startet drei Services (nginx, auth-service, redis) ohne Fehler.
- AC-2: auth-service-Container basiert auf Python 3.12 und führt einen Dummy-Hello-Endpoint aus (kommt von SKL-1).
- AC-3: redis-Container ist mit auth-service über Docker-Network erreichbar.
- AC-4: Persistent Volumes für SQLite (`auth-data`) und Redis (`redis-data`) sind konfiguriert.
- AC-5: README dokumentiert `docker compose up` als Standard-Befehl.

---

#### INF-4: oqs-provider-fähiges nginx-Image baut

- **Epic:** INF
- **Bezug:** Design 3.1, NFR-Sec-1
- **Priorität:** Must
- **T-Shirt:** M | **Story Points:** 5 | **Sprint:** 0

**Story:**
Als Studierender möchte ich ein nginx-Image haben, das auf openquantumsafe/oqs-ossl3 basiert, damit hybrid TLS (X25519MLKEM768) später aktiviert werden kann.

**Akzeptanzkriterien:**

- AC-1: `Dockerfile.nginx` baut ohne Fehler aus dem openquantumsafe/oqs-ossl3-Base-Image.
- AC-2: nginx 1.27 ist installiert und startet im Container.
- AC-3: oqs-provider 0.10+ und OpenSSL 3.5+ sind im Image verfügbar (verifiziert mit `openssl list -providers`).
- AC-4: Image-Tag ist `pqc-nginx:0.1` im lokalen Docker-Registry.

---

### Epic SKL: Skeletons

**Ziel:** Server- und Client-Skeletons stehen, damit eigentliche Feature-Entwicklung beginnen kann.

#### SKL-1: FastAPI-Skeleton mit Config-Loading

- **Epic:** SKL
- **Bezug:** Design 2.1
- **Priorität:** Must
- **T-Shirt:** S | **Story Points:** 2 | **Sprint:** 1 | **Blockt:** alle Server-Stories

**Story:**
Als Server-Entwickler möchte ich einen lauffähigen FastAPI-Skeleton mit Config-Loading haben, damit alle weiteren Endpoints darauf aufbauen können.

**Akzeptanzkriterien:**

- AC-1: `server/`-Ordner enthält FastAPI-App mit `main.py`, `config.py`, `routers/`.
- AC-2: `pydantic-settings` lädt Konfiguration aus `config.yaml` und Environment-Variablen.
- AC-3: `/health`-Endpoint liefert `200 OK` mit `{ "status": "ok", "version": "..." }`.
- AC-4: App startet mit `uvicorn main:app --reload` und im Docker-Compose.
- AC-5: Basic-Logging im JSON-Format ist eingerichtet.

---

#### SKL-2: Expo-Skeleton mit Navigation und drei Screens

- **Epic:** SKL
- **Bezug:** Design 2.2
- **Priorität:** Must
- **T-Shirt:** S | **Story Points:** 3 | **Sprint:** 1 | **Blockt:** alle App-Stories

**Story:**
Als App-Entwickler möchte ich einen lauffähigen Expo-Skeleton mit Expo Router und drei Placeholder-Screens haben, damit Login, Home und Profile als Feature-Stories darauf aufbauen können.

**Akzeptanzkriterien:**

- AC-1: `app/`-Ordner enthält Expo-Projekt (SDK 51+) mit TypeScript.
- AC-2: Expo Router ist konfiguriert mit Routen `/login`, `/home`, `/profile`.
- AC-3: Drei Placeholder-Screens existieren und sind navigierbar.
- AC-4: App startet mit `npx expo start` im Simulator und auf Test-Phone.
- AC-5: `@noble/post-quantum`, `@noble/ciphers`, `expo-secure-store`, `expo-auth-session` sind als Dependencies installiert (noch nicht genutzt).

---

### Epic CRY: Crypto-Abstraction-Layer

**Ziel:** Zentrale Crypto-Schicht, die konkrete Algorithmen vor dem Application-Code versteckt. Voraussetzung für alle Krypto-nutzenden Module.

#### CRY-1: Algorithm Registry für KEM und Signature (Server)

- **Epic:** CRY
- **Bezug:** FR-Crypto-1, Design 6.1
- **Priorität:** Must
- **T-Shirt:** M | **Story Points:** 5 | **Sprint:** 1 | **Blockt:** CRY-2, TOK-1

**Story:**
Als Server-Entwickler möchte ich eine zentrale Registry für KEM- und Signatur-Algorithmen, damit neue Algorithmen ohne Application-Code-Änderung registriert werden können.

**Akzeptanzkriterien:**

- AC-1: `crypto/registry.py` implementiert eine `CryptoRegistry`-Klasse mit `register_kem(name, impl)` und `register_signature(name, impl)`.
- AC-2: Registry erkennt Duplikate und wirft `RegistryError`.
- AC-3: `get_kem(name)` und `get_signature(name)` liefern das Plugin oder werfen `AlgorithmNotFoundError`.
- AC-4: Registry-Init-Function liest Config und registriert alle in `crypto.kem.supported` und `crypto.signature.supported` aufgeführten Algorithmen.
- AC-5: Unit-Tests decken Happy-Path und Duplikat-Erkennung ab.

---

#### CRY-2: Crypto-Facade für sign/verify (Server, partial)

- **Epic:** CRY
- **Bezug:** FR-Crypto-2, FR-Crypto-3, Design 6.1
- **Priorität:** Must
- **T-Shirt:** S | **Story Points:** 3 | **Sprint:** 1 | **Hängt ab von:** CRY-1, CRY-5

**Story:**
Als Server-Entwickler möchte ich eine Facade-Schnittstelle für Signier- und Verifikations-Operationen haben, damit das Token-Modul keine konkreten Algorithmen kennt.

**Akzeptanzkriterien:**

- AC-1: `CryptoFacade.sign(payload, purpose) -> (signature, alg_name, kid)` ruft den per Config gewählten Default-Algorithmus auf.
- AC-2: `CryptoFacade.verify(payload, signature, alg, kid) -> bool` wählt den Algorithmus anhand des `alg`-Parameters.
- AC-3: KEM-Operationen sind in dieser Story noch nicht implementiert (kommt in CRY-3).
- AC-4: Unit-Tests sign/verify Round-Trip für ML-DSA-65.

---

#### CRY-3: Crypto-Facade für KEM und HKDF (Server)

- **Epic:** CRY
- **Bezug:** FR-Crypto-2, Design 6.1
- **Priorität:** Must
- **T-Shirt:** M | **Story Points:** 5 | **Sprint:** 3 | **Hängt ab von:** CRY-2, CRY-4

**Summary-AC:**

- KEM-Methoden (`kem_keygen`, `kem_encaps`, `kem_decaps`) sind implementiert.
- HKDF-Methode (`hkdf`) ist implementiert.
- AEAD-Methoden (`aead_encrypt`, `aead_decrypt`) sind implementiert.
- Negotiation-Support-Methoden (`supported_kem_algorithms`, `is_kem_supported`) sind implementiert.
- Unit-Tests pro Methode.

---

#### CRY-4: liboqs-python Wrapper für ML-KEM-768 und ML-KEM-1024 (Server)

- **Epic:** CRY
- **Bezug:** FR-Crypto-1, FIPS 203
- **Priorität:** Must
- **T-Shirt:** M | **Story Points:** 5 | **Sprint:** 3 | **Blockt:** SES-1

**Summary-AC:**

- `LibOqsKem`-Adapter-Klasse implementiert `keygen`, `encaps`, `decaps`.
- ML-KEM-768 und ML-KEM-1024 sind beide registrierbar.
- Test-Vektoren aus NIST-Test-Suite werden korrekt verarbeitet.

---

#### CRY-5: liboqs-python Wrapper für ML-DSA-65 (Server)

- **Epic:** CRY
- **Bezug:** FR-Crypto-1, FIPS 204
- **Priorität:** Must
- **T-Shirt:** M | **Story Points:** 5 | **Sprint:** 1 | **Blockt:** TOK-1, TOK-2

**Story:**
Als Server-Entwickler möchte ich einen liboqs-python-basierten Adapter für ML-DSA-65 haben, damit Tokens digital signiert werden können.

**Akzeptanzkriterien:**

- AC-1: `LibOqsSignature`-Adapter-Klasse implementiert `keygen`, `sign`, `verify`.
- AC-2: ML-DSA-65 ist über die Registry abrufbar.
- AC-3: Round-Trip-Test: erzeuge Keypair, signiere Payload, verifiziere Signatur (alle Schritte erfolgreich).
- AC-4: Fehlerfall: manipulierte Payload schlägt Verifikation fehl.
- AC-5: Schlüssel-Persistierung: Private Key wird aus File-Pfad geladen, Public Key extrahierbar.

---

#### CRY-6: Client-Side Crypto-Abstraction (App)

- **Epic:** CRY
- **Bezug:** FR-Crypto-1 analog für App, Design 2.2, 6.4
- **Priorität:** Must
- **T-Shirt:** M | **Story Points:** 5 | **Sprint:** 3

**Summary-AC:**

- TypeScript-Module `app/crypto/kem.ts`, `cipher.ts`, `signature.ts`, `hash.ts` existieren.
- Wrapping `@noble/post-quantum` (ml-kem768, ml-dsa65), `@noble/ciphers` (AES-GCM), `@noble/hashes` (HKDF).
- Algorithmus-Auswahl via Config (analog Server).
- Unit-Tests via Jest.

---

#### CRY-7: Algorithmus-Identifier in allen Krypto-Artefakten

- **Epic:** CRY
- **Bezug:** FR-Crypto-3
- **Priorität:** Must
- **T-Shirt:** S | **Story Points:** 2 | **Sprint:** 3

**Summary-AC:**

- Token-Header enthält `alg` und `kid`.
- Session-Record enthält `kem_alg`.
- Wire-Format für Session-Init enthält `kem_alg`.
- Documentation in `docs/wire_format.md`.

---

### Epic AUT: Local Authentication

**Ziel:** User können sich mit Email/Passwort gegen den lokalen User-Store authentifizieren (UC-1).

#### AUT-1: User-Store mit SQLAlchemy und SQLite

- **Epic:** AUT
- **Bezug:** Design 5.3, FR-Auth-1
- **Priorität:** Must
- **T-Shirt:** M | **Story Points:** 5 | **Sprint:** 1 | **Blockt:** AUT-2, AUT-3, BRK-4

**Story:**
Als Server-Entwickler möchte ich einen SQLAlchemy-basierten User-Store mit User-Model und Argon2id-Hash-Speicherung haben, damit Benutzer-Records persistiert werden können.

**Akzeptanzkriterien:**

- AC-1: `models/user.py` definiert das User-Model gemäss ERD in Design 5.3 (id UUID, email unique, password_hash, auth_method, external_sub, created_at, updated_at).
- AC-2: Alembic-Migration legt die Tabelle an, Datenbank ist im persistent Docker-Volume `auth-data`.
- AC-3: Async-Repository-Pattern mit `aiosqlite` und SQLAlchemy 2.0 async API.
- AC-4: Argon2id-Parameter (m=64MB, t=3, p=4) sind in Konfiguration definiert.
- AC-5: Unit-Tests: User anlegen, finden via email, password-hash-vergleich.

---

#### AUT-2: Admin-CLI für User-Provisioning

- **Epic:** AUT
- **Bezug:** FR-Auth-2
- **Priorität:** Must
- **T-Shirt:** S | **Story Points:** 2 | **Sprint:** 1 | **Hängt ab von:** AUT-1

**Story:**
Als Administrator möchte ich ein CLI-Werkzeug, das neue lokale Users mit gehashtem Passwort anlegt, damit Test-Users für Demos provisioniert werden können (Self-Service-Registrierung ist explizit out of scope).

**Akzeptanzkriterien:**

- AC-1: `python -m auth_service.admin create-user --email <email> --password <pw>` legt einen lokalen User an.
- AC-2: Passwort wird mit Argon2id gehasht.
- AC-3: `auth_method` ist auf `"local"` gesetzt.
- AC-4: Bei vorhandenem Email-Konflikt wird ein klarer Fehler ausgegeben.
- AC-5: `python -m auth_service.admin list-users` zeigt alle Users (ohne Passwort).

---

#### AUT-3: POST /auth/local/login Endpoint

- **Epic:** AUT
- **Bezug:** UC-1, FR-Auth-1
- **Priorität:** Must
- **T-Shirt:** M | **Story Points:** 5 | **Sprint:** 1 | **Hängt ab von:** AUT-1, TOK-1

**Story:**
Als App möchte ich einen Login-Endpoint POST `/auth/local/login` aufrufen können, der bei korrekten Credentials einen ML-DSA-signierten Broker-Token zurückgibt, damit der User in der App eingeloggt ist.

**Akzeptanzkriterien:**

- AC-1: Endpoint akzeptiert JSON `{ "email": "...", "password": "..." }`.
- AC-2: Bei korrekten Credentials Response `200 OK` mit `{ "broker_token": "...", "expires_in": 3600 }`.
- AC-3: Token-Header enthält `alg: "ML-DSA-65"`, `typ: "JWT"`, `kid: ...`.
- AC-4: Token-Payload enthält Claims `sub`, `iss`, `iat`, `exp`, `auth_method: "local"`.
- AC-5: Token ist mit Public-Key des Auth-Service ML-DSA-verifizierbar (Test).

---

#### AUT-4: User-Enumeration-Schutz

- **Epic:** AUT
- **Bezug:** NFR-Sec-4
- **Priorität:** Must
- **T-Shirt:** XS | **Story Points:** 1 | **Sprint:** 1 | **Hängt ab von:** AUT-3

**Story:**
Als Sicherheits-Bewusster möchte ich, dass falsche Credentials und unbekannte User identische Responses liefern, damit User-Enumeration nicht möglich ist.

**Akzeptanzkriterien:**

- AC-1: Bei unbekannter Email gibt der Endpoint `401 Unauthorized` mit Body `{ "error": "invalid_credentials" }`.
- AC-2: Bei korrekter Email und falschem Passwort identische Response.
- AC-3: Response-Zeit-Differenz: max. 50 ms (durch konstante Dummy-Hash-Operation bei nicht-existierendem User).
- AC-4: Integration-Test mit beiden Cases.

---

### Epic TOK: Token Service

**Ziel:** Broker-Tokens sind ML-DSA-65-signiert ausstellbar und verifizierbar (FR-Token-*).

#### TOK-1: Broker-Token-Ausstellung mit ML-DSA-65

- **Epic:** TOK
- **Bezug:** FR-Token-1, Design 5.1
- **Priorität:** Must
- **T-Shirt:** M | **Story Points:** 5 | **Sprint:** 1 | **Hängt ab von:** CRY-2, CRY-5

**Story:**
Als Auth-Service möchte ich Broker-Tokens im JWS-Compact-Format mit ML-DSA-65-Signatur ausstellen, damit Authentifizierungs-Beweise post-quantum-sicher übertragen werden können.

**Akzeptanzkriterien:**

- AC-1: `token_service.issue(user_id, auth_method, external_sub)` liefert einen Token-String.
- AC-2: Token folgt JWS-Compact: `base64url(header).base64url(payload).base64url(signature)`.
- AC-3: Header enthält `alg`, `typ: "JWT"`, `kid` (alle als Werte aus Crypto-Facade).
- AC-4: Payload enthält `sub`, `iss`, `iat`, `exp`, `auth_method`, optional `external_sub`.
- AC-5: TTL aus Config (`token.ttl_seconds`).

---

#### TOK-2: Broker-Token-Verifikation

- **Epic:** TOK
- **Bezug:** FR-Token-2
- **Priorität:** Must
- **T-Shirt:** S | **Story Points:** 2 | **Sprint:** 1 | **Hängt ab von:** TOK-1

**Story:**
Als Server möchte ich einen ausgestellten Broker-Token wieder verifizieren können, damit geschützte Endpoints den User identifizieren.

**Akzeptanzkriterien:**

- AC-1: `token_service.verify(token_str)` liefert Claims oder wirft `InvalidTokenError`.
- AC-2: Signatur-Verifikation via Crypto-Facade mit dem im Header genannten Algorithmus und kid.
- AC-3: Ablaufzeit (`exp`) wird geprüft, abgelaufenes Token wirft `ExpiredTokenError`.
- AC-4: Issuer (`iss`) wird geprüft gegen Config-Wert.
- AC-5: Manipulierte Payload oder Signatur schlägt Verifikation fehl.

---

#### TOK-3: Schlüssel-Rotation für Token-Signierung

- **Epic:** TOK
- **Bezug:** FR-Token-3
- **Priorität:** Should
- **T-Shirt:** M | **Story Points:** 5 | **Sprint:** 4

**Summary-AC:**

- `active_kid` in Config bestimmt den aktiven Signier-Schlüssel.
- Mehrere Public Keys können gleichzeitig für Verifikation vorgehalten werden.
- Schlüssel-Generierung und Rotation via CLI dokumentiert.

---

#### TOK-4: JWKS-Endpoint für Token-Verifikation

- **Epic:** TOK
- **Bezug:** Design 5.1, NIST-Konventionen
- **Priorität:** Should
- **T-Shirt:** S | **Story Points:** 2 | **Sprint:** 4

**Summary-AC:**

- `/auth/.well-known/jwks.json` liefert die ML-DSA-Public-Keys.
- Format folgt RFC 7517 (mit erweitertem `alg`-Wert `"ML-DSA-65"`).
- Klare Dokumentation, dass `alg`-Wert ein Pre-Standard ist (kein offizieller IANA-Eintrag).

---

### Epic BRK: Identity Broker / Federation

**Ziel:** Login mit Google und Microsoft über OIDC Authorization Code Flow mit PKCE (UC-2, UC-3).

#### BRK-1: External-IdP-Registry mit Plugin-Architektur

- **Epic:** BRK
- **Bezug:** FR-Broker-1, Design 2.1
- **Priorität:** Must
- **T-Shirt:** M | **Story Points:** 5 | **Sprint:** 2 | **Blockt:** BRK-5, BRK-6

**Story:**
Als Server-Entwickler möchte ich eine Plugin-Registry für externe Identity Provider haben, damit neue Provider (z.B. Apple) später ohne Architektur-Änderung hinzugefügt werden können.

**Akzeptanzkriterien:**

- AC-1: `IdpRegistry`-Klasse mit `register(name, plugin)` und `get(name)`.
- AC-2: Plugin-Schnittstelle definiert `discovery_url`, `client_id`, `scopes`, `claim_mapper`, `verify_id_token`.
- AC-3: Init-Function liest `idp_providers`-Section aus Config und registriert alle aktiven Provider.
- AC-4: Unbekannter Provider-Name liefert `UnknownProviderError`.
- AC-5: Unit-Tests für Registry-Logik und für Plugin-Schnittstelle.

---

#### BRK-2: OIDC Authorization Code Flow mit PKCE

- **Epic:** BRK
- **Bezug:** UC-2, UC-3, FR-Broker-2
- **Priorität:** Must
- **T-Shirt:** L | **Story Points:** 8 | **Sprint:** 2 | **Hängt ab von:** BRK-1

**Story:**
Als App möchte ich den OIDC Authorization Code Flow mit PKCE gegen einen externen IdP starten und einen Code-zu-Token-Tausch über den Auth-Service durchführen können, damit ich mich mit Google oder Microsoft einloggen kann.

**Akzeptanzkriterien:**

- AC-1: Auth-Service-Endpoint `POST /auth/federated/<provider>/callback` akzeptiert `{ code, code_verifier }`.
- AC-2: Endpoint tauscht Code gegen IdP-Tokens via Provider-`/token`-URL.
- AC-3: PKCE durchgehend (kein `client_secret` in App, `code_verifier` aus App-Request).
- AC-4: Bei Tausch-Fehler `400 Bad Request` mit Error-Body.
- AC-5: Erfolgreicher Tausch liefert ID-Token zur Weiter-Verarbeitung in BRK-3.

---

#### BRK-3: ID-Token-Verifikation gegen IdP-JWKS

- **Epic:** BRK
- **Bezug:** FR-Broker-3
- **Priorität:** Must
- **T-Shirt:** M | **Story Points:** 5 | **Sprint:** 2 | **Hängt ab von:** BRK-2

**Story:**
Als Auth-Service möchte ich das ID-Token des externen IdP gegen dessen JWKS verifizieren, damit Manipulationen ausgeschlossen sind.

**Akzeptanzkriterien:**

- AC-1: JWKS wird vom Provider-Discovery-URL geholt und gecacht (TTL aus Config).
- AC-2: Signatur, Issuer, Audience, Expiry des ID-Tokens werden geprüft.
- AC-3: Bei Signatur-Mismatch `401 Unauthorized`.
- AC-4: Bei abgelaufenem Token `401`.
- AC-5: Unit-Tests mit Mock-IdP-JWKS.

---

#### BRK-4: Identity-Normalisierung (External Sub zu Internal User ID)

- **Epic:** BRK
- **Bezug:** FR-Broker-4
- **Priorität:** Must
- **T-Shirt:** M | **Story Points:** 5 | **Sprint:** 2 | **Hängt ab von:** BRK-3, AUT-1

**Story:**
Als Auth-Service möchte ich das External-Sub-Field eines IdP auf eine interne User-ID mappen (bzw. einen neuen User-Record anlegen), damit federated Users dieselbe User-Identität haben wie lokale Users.

**Akzeptanzkriterien:**

- AC-1: Bei erstem Login eines neuen External-Sub wird ein User-Record mit `auth_method = <provider>` und `external_sub` angelegt.
- AC-2: Bei wiederholtem Login derselben Identität wird der bestehende User-Record verwendet.
- AC-3: Claim-Mapping per Provider-Plugin (`google.sub`, `microsoft.oid`).
- AC-4: Bei Email-Konflikt mit lokalem User: User-Record bleibt unverändert, `external_sub` wird ergänzt (Account-Linking).
- AC-5: Tests für Erst-Login, Wiederholter Login, Konflikt-Szenario.

---

#### BRK-5: Google IdP-Plugin

- **Epic:** BRK
- **Bezug:** UC-2, FR-Broker-1
- **Priorität:** Must
- **T-Shirt:** M | **Story Points:** 5 | **Sprint:** 2 | **Hängt ab von:** BRK-1

**Story:**
Als Server-Entwickler möchte ich ein Google-Provider-Plugin registrieren, damit Login mit Google funktioniert.

**Akzeptanzkriterien:**

- AC-1: `idp_plugins/google.py` implementiert die Plugin-Schnittstelle.
- AC-2: Plugin verwendet Discovery-URL `https://accounts.google.com/.well-known/openid-configuration`.
- AC-3: Claim-Mapper extrahiert `sub` als External-Sub.
- AC-4: Google-Client-ID und -Secret werden aus Environment-Variablen geladen.
- AC-5: Manuelle Demo: Login eines Google-Test-Accounts liefert einen Broker-Token.

---

#### BRK-6: Microsoft IdP-Plugin

- **Epic:** BRK
- **Bezug:** UC-3, FR-Broker-1
- **Priorität:** Must
- **T-Shirt:** M | **Story Points:** 5 | **Sprint:** 2 | **Hängt ab von:** BRK-1, BRK-5

**Story:**
Als Server-Entwickler möchte ich ein Microsoft-Entra-Provider-Plugin registrieren, damit Login mit Microsoft funktioniert.

**Akzeptanzkriterien:**

- AC-1: `idp_plugins/microsoft.py` implementiert die Plugin-Schnittstelle.
- AC-2: Discovery-URL `https://login.microsoftonline.com/common/v2.0/.well-known/openid-configuration`.
- AC-3: Claim-Mapper extrahiert `oid` als External-Sub (Microsoft-Konvention).
- AC-4: Manuelle Demo: Login eines Microsoft-Test-Accounts liefert einen Broker-Token.

---

#### BRK-7: CSRF/State-Schutz für OIDC-Flows

- **Epic:** BRK
- **Bezug:** NFR-Sec-5
- **Priorität:** Must
- **T-Shirt:** S | **Story Points:** 2 | **Sprint:** 2 | **Hängt ab von:** BRK-2

**Story:**
Als Sicherheits-Bewusster möchte ich, dass jeder OIDC-Flow einen kryptografisch zufälligen State-Parameter mit mindestens 128 Bit Entropie verwendet, damit CSRF-Angriffe ausgeschlossen sind.

**Akzeptanzkriterien:**

- AC-1: App generiert State-Parameter mit `expo-crypto.getRandomBytes(16)` oder vergleichbar.
- AC-2: State wird im Auth-Service-Callback geprüft (Vergleich gegen gespeicherten Wert).
- AC-3: State-Mismatch liefert `400 Bad Request` und App zeigt Sicherheits-Fehler.
- AC-4: Integration-Test mit künstlich falschem State.

---

### Epic TLS: Hybrid TLS Transport

**Ziel:** nginx terminiert TLS mit X25519MLKEM768 als NamedGroup (NFR-Sec-1).

#### TLS-1: nginx-Konfiguration für X25519MLKEM768

- **Epic:** TLS
- **Bezug:** NFR-Sec-1, Design 3.1
- **Priorität:** Must
- **T-Shirt:** M | **Story Points:** 5 | **Sprint:** 2 | **Hängt ab von:** INF-4

**Story:**
Als DevOps möchte ich nginx so konfigurieren, dass es TLS 1.3 mit der hybriden Key-Exchange-Group X25519MLKEM768 anbietet, damit der Transport post-quantum-gesichert ist.

**Akzeptanzkriterien:**

- AC-1: `nginx.conf` aktiviert `ssl_ecdh_curve X25519MLKEM768`.
- AC-2: Self-signed Server-Cert (ECDSA, klassisch) ist eingebaut.
- AC-3: nginx startet ohne Fehler.
- AC-4: TLS 1.3 ist erzwungen.

---

#### TLS-2: Verifikation des PQ-Handshakes mit oqs-curl

- **Epic:** TLS
- **Bezug:** NFR-Sec-1
- **Priorität:** Must
- **T-Shirt:** S | **Story Points:** 2 | **Sprint:** 2 | **Hängt ab von:** TLS-1

**Story:**
Als Tester möchte ich den hybriden TLS-Handshake mit einem PQ-fähigen Client verifizieren, damit der NFR-Sec-1-Beweis dokumentiert ist.

**Akzeptanzkriterien:**

- AC-1: `oqs-curl` (oder vergleichbarer PQ-Client) baut Connection zum nginx auf und protokolliert NamedGroup `X25519MLKEM768`.
- AC-2: Demo-Skript `scripts/verify_pq_tls.sh` mit dokumentiertem Output.
- AC-3: Screenshot oder Log-Auszug für die Berichts-Doku gesichert.

---

#### TLS-3: nginx als Reverse Proxy für auth-service

- **Epic:** TLS
- **Bezug:** Design 3.1
- **Priorität:** Must
- **T-Shirt:** S | **Story Points:** 2 | **Sprint:** 2 | **Hängt ab von:** TLS-1, SKL-1

**Story:**
Als DevOps möchte ich nginx als Reverse Proxy zum FastAPI-Service konfigurieren, damit der TLS-Endpoint auf Port 443 erreichbar ist und intern HTTP läuft.

**Akzeptanzkriterien:**

- AC-1: nginx forwarded alle Requests an `auth-service:8000`.
- AC-2: Health-Check über `https://localhost/health` liefert `200 OK`.
- AC-3: Connection-Header werden korrekt übergeben (`X-Forwarded-For`, `X-Real-IP`).

---

### Epic SES: PQ Session

**Ziel:** ML-KEM-768-basierte Session-Etablierung zwischen App und Server (UC-4).

#### SES-1: POST /session/init mit ML-KEM-Encapsulation

- **Epic:** SES
- **Bezug:** UC-4, FR-Session-1
- **Priorität:** Must
- **T-Shirt:** L | **Story Points:** 8 | **Sprint:** 3 | **Hängt ab von:** CRY-3, CRY-4, TOK-2

**Summary-AC:**

- Endpoint akzeptiert `{ kem_alg, encapsulation_key }` plus Authorization-Bearer-Token.
- Token wird verifiziert, KEM-Encapsulation erfolgt via Crypto-Facade.
- Response liefert `{ session_id, ciphertext, expires_in }`.
- Session wird im Redis-Store mit TTL gespeichert.

---

#### SES-2: HKDF-Session-Key-Ableitung

- **Epic:** SES
- **Bezug:** FR-Session-2
- **Priorität:** Must
- **T-Shirt:** S | **Story Points:** 2 | **Sprint:** 3 | **Hängt ab von:** CRY-3

**Summary-AC:**

- Server leitet `session_key = HKDF(shared_secret, info="app-session-v1", salt=session_id)` ab.
- App-Seite tut dasselbe nach `kem.decaps`.
- Server und App haben identische 32-Byte-Keys.

---

#### SES-3: Session-Store mit TTL (Redis)

- **Epic:** SES
- **Bezug:** FR-Session-3
- **Priorität:** Must
- **T-Shirt:** M | **Story Points:** 5 | **Sprint:** 3

**Summary-AC:**

- Redis-Schlüssel `session:{id}` mit JSON-Value (siehe Design 5.2).
- TTL aus Config (`session.ttl_seconds`, Default 900).
- Session-Lookup, -Refresh, -Invalidierung implementiert.
- Pytest-Integration-Test mit echtem Redis (testcontainers oder docker-compose-Test).

---

#### SES-4: Algorithmus-Negotiation

- **Epic:** SES
- **Bezug:** FR-Session-4
- **Priorität:** Should
- **T-Shirt:** S | **Story Points:** 3 | **Sprint:** 3

**Summary-AC:**

- Falls App einen nicht unterstützten KEM-Algorithmus anfragt: Response `406 Not Acceptable` mit `{ supported_algorithms: [...] }`.
- App reagiert auf 406, wählt einen unterstützten Algorithmus und versucht erneut.
- Test mit explizit konfigurierter Mismatch-Situation.

---

### Epic DCH: Data Channel

**Ziel:** Verschlüsselter API-Kanal nach erfolgreichem PQ-Handshake (UC-5).

#### DCH-1: AES-256-GCM Encrypt/Decrypt Wrapper

- **Epic:** DCH
- **Bezug:** FR-DataChannel-1, FR-Crypto-2
- **Priorität:** Must
- **T-Shirt:** S | **Story Points:** 2 | **Sprint:** 3 | **Hängt ab von:** CRY-3

**Summary-AC:**

- Server- und App-seitige Wrapper für AES-256-GCM mit 96-bit-Nonce.
- Tag-Mismatch wirft Exception.
- Round-Trip-Test mit zufälligem Plaintext.

---

#### DCH-2: Header-basiertes Session-Routing

- **Epic:** DCH
- **Bezug:** FR-DataChannel-2
- **Priorität:** Must
- **T-Shirt:** M | **Story Points:** 5 | **Sprint:** 3

**Summary-AC:**

- Middleware liest `X-Session-Id` und `X-Nonce` aus Headers.
- Bei fehlendem Session-Header: 401.
- Bei ungültiger Session-Id: 401 `session_expired`.
- Bei Tag-Mismatch: 400 mit Security-Log-Eintrag.

---

#### DCH-3: Geschützter API-Endpoint /api/profile

- **Epic:** DCH
- **Bezug:** UC-5
- **Priorität:** Must
- **T-Shirt:** M | **Story Points:** 5 | **Sprint:** 3 | **Hängt ab von:** DCH-1, DCH-2, AUT-1

**Summary-AC:**

- Endpoint entschlüsselt Request-Body via Session-Key.
- Liefert User-Profile (id, email, auth_method) verschlüsselt zurück.
- Response-Body ist AES-GCM-verschlüsselt mit neuer Nonce.

---

#### DCH-4: Replay-Schutz via Nonce-Tracking

- **Epic:** DCH
- **Bezug:** NFR-Sec-2
- **Priorität:** Must
- **T-Shirt:** M | **Story Points:** 5 | **Sprint:** 3 | **Hängt ab von:** DCH-2

**Summary-AC:**

- Nonces pro Session werden in Redis getrackt (z.B. Sliding-Window).
- Wiederverwendete Nonce wirft 400 mit Security-Log-Eintrag.
- Trade-Off Stateful Nonce-Tracking versus Timestamp-basiert dokumentiert (eines wählen, andere im Bericht erwähnen).

---

### Epic APP: Mobile App UI und Integration

**Ziel:** Mobile App stellt drei Login-Optionen, einen Home- und einen Profile-Screen bereit (Design 2.2).

#### APP-1: Login-Screen mit drei Optionen (UI only)

- **Epic:** APP
- **Bezug:** Design 2.2, UC-1/2/3
- **Priorität:** Must
- **T-Shirt:** S | **Story Points:** 2 | **Sprint:** 1 | **Hängt ab von:** SKL-2

**Story:**
Als User möchte ich auf dem Login-Screen drei Login-Optionen sehen (Email/Passwort, Google, Microsoft), damit ich meinen Login-Weg wählen kann.

**Akzeptanzkriterien:**

- AC-1: Login-Screen rendert drei Buttons.
- AC-2: Email/Passwort-Form mit zwei Inputs und einem "Anmelden"-Button.
- AC-3: Google- und Microsoft-Button sind als Placeholder vorhanden (Funktion kommt in APP-7, APP-8).
- AC-4: Basic Form-Validierung (Email-Format, Passwort min. 8 Zeichen).
- AC-5: Visuelles Layout ist ohne Design-Library akzeptabel (Plain RN-Komponenten).

---

#### APP-2: Home-Screen mit Logout

- **Epic:** APP
- **Bezug:** Design 2.2
- **Priorität:** Must
- **T-Shirt:** S | **Story Points:** 2 | **Sprint:** 3

**Summary-AC:**

- Begrüssungs-Text, Logout-Button, Link zum Profile-Screen.

---

#### APP-3: Profile-Screen mit /api/profile-Aufruf

- **Epic:** APP
- **Bezug:** UC-5
- **Priorität:** Must
- **T-Shirt:** M | **Story Points:** 5 | **Sprint:** 3 | **Hängt ab von:** DCH-3, APP-6

**Summary-AC:**

- Bei Screen-Öffnung wird `/api/profile` über secureClient geladen.
- Profile-Daten werden angezeigt.
- Bei Session-Ablauf: Re-Auth-Flow oder Redirect zu Login.

---

#### APP-4: AuthContext (globaler Auth-State)

- **Epic:** APP
- **Bezug:** Design 2.2
- **Priorität:** Must
- **T-Shirt:** S | **Story Points:** 2 | **Sprint:** 1

**Akzeptanzkriterien:**

- AC-1: React Context mit `broker_token`, `user_info`, `is_authenticated`.
- AC-2: `login(token)` und `logout()` Methoden.
- AC-3: Token wird mit `expo-secure-store` persistiert.
- AC-4: Auto-Login bei App-Start, wenn Token gültig.

---

#### APP-5: SessionContext (globaler Session-State, in-memory)

- **Epic:** APP
- **Bezug:** Design 2.2
- **Priorität:** Must
- **T-Shirt:** S | **Story Points:** 2 | **Sprint:** 3

**Summary-AC:**

- React Context mit `session_id`, `session_key`, `expires_at`.
- Session-Key wird **nicht** persistiert (nur in-memory).

---

#### APP-6: secureClient.ts (HTTP-Wrapper mit auto-encrypt)

- **Epic:** APP
- **Bezug:** Design 2.2
- **Priorität:** Must
- **T-Shirt:** M | **Story Points:** 5 | **Sprint:** 3 | **Hängt ab von:** APP-5, CRY-6

**Summary-AC:**

- Wrapper-Function `secureClient.post(path, body)` verschlüsselt Body, fügt Session-Header hinzu.
- Response wird entschlüsselt zurückgegeben.
- Bei Session-Ablauf: triggert Re-Auth-Flow.

---

#### APP-7: Google-Login via expo-auth-session

- **Epic:** APP
- **Bezug:** UC-2
- **Priorität:** Must
- **T-Shirt:** M | **Story Points:** 5 | **Sprint:** 2 | **Hängt ab von:** APP-1, BRK-5

**Akzeptanzkriterien:**

- AC-1: Tap auf Google-Button öffnet System-Browser-Tab mit Google /authorize.
- AC-2: PKCE code_verifier und code_challenge werden korrekt generiert.
- AC-3: State-Parameter mit mind. 128 Bit Entropie wird mitgeschickt und validiert.
- AC-4: Nach Redirect kommt App per Deep-Link zurück, sendet code+verifier an `/auth/federated/google/callback`.
- AC-5: Bei Erfolg landet Token im AuthContext, Navigation zum Home-Screen.

---

#### APP-8: Microsoft-Login via expo-auth-session

- **Epic:** APP
- **Bezug:** UC-3
- **Priorität:** Must
- **T-Shirt:** M | **Story Points:** 5 | **Sprint:** 2 | **Hängt ab von:** APP-1, APP-7, BRK-6

**Akzeptanzkriterien:**

- AC-1: Wie APP-7, aber für Microsoft Entra.
- AC-2: Tenant-Konfiguration (common, organizations, oder specific tenant) dokumentiert.
- AC-3: Bei Erfolg landet Token im AuthContext, Navigation zum Home-Screen.

---

#### APP-9: Token-Persistenz mit expo-secure-store

- **Epic:** APP
- **Bezug:** NFR-Sec-3
- **Priorität:** Must
- **T-Shirt:** XS | **Story Points:** 1 | **Sprint:** 1 | **Hängt ab von:** APP-4

**Akzeptanzkriterien:**

- AC-1: `expo-secure-store.setItemAsync` speichert den Broker-Token.
- AC-2: Beim App-Start wird der Token via `getItemAsync` geladen.
- AC-3: Logout entfernt den Token via `deleteItemAsync`.
- AC-4: Test auf Test-Phone: nach App-Neustart bleibt User eingeloggt (bis Token-Ablauf).

---

### Epic QUA: Quality (Tests und Benchmarks)

**Ziel:** Test-Coverage und Performance-Messungen für die Bewertung und für NFR-Erfüllung.

#### QUA-1: Pytest-Setup

- **Epic:** QUA
- **Bezug:** Bewertungs-Kriterium 5 (Reflexionstiefe), DoD
- **Priorität:** Must
- **T-Shirt:** XS | **Story Points:** 1 | **Sprint:** 1

**Akzeptanzkriterien:**

- AC-1: `pytest`, `pytest-asyncio`, `httpx` als Test-Dependencies.
- AC-2: `tests/conftest.py` mit Fixtures für FastAPI-TestClient.
- AC-3: `pytest` läuft mit grünem Status (initial leere Test-Suite oder Smoke-Test).
- AC-4: Coverage-Report mit `pytest-cov` konfiguriert.

---

#### QUA-2: Unit-Tests Auth-Module

- **Epic:** QUA
- **Bezug:** AUT-1 bis AUT-4
- **Priorität:** Must
- **T-Shirt:** S | **Story Points:** 2 | **Sprint:** 1

**Akzeptanzkriterien:**

- AC-1: Tests für Hash-Round-Trip (Argon2id).
- AC-2: Test für korrekten Login.
- AC-3: Test für falsches Passwort und unbekannte Email mit identischer Response.
- AC-4: Coverage Auth-Module mindestens 80 Prozent.

---

#### QUA-3: Unit-Tests Token- und Crypto-Module

- **Epic:** QUA
- **Bezug:** TOK-1, TOK-2, CRY-1, CRY-2, CRY-5
- **Priorität:** Must
- **T-Shirt:** S | **Story Points:** 3 | **Sprint:** 1

**Akzeptanzkriterien:**

- AC-1: Token-Round-Trip-Test.
- AC-2: Token-Verifikation mit manipulierter Payload schlägt fehl.
- AC-3: Registry-Tests (Happy-Path, Duplikat, Unknown).
- AC-4: Crypto-Facade sign/verify Round-Trip.

---

#### QUA-4: Integration-Tests Broker-Flow

- **Epic:** QUA
- **Bezug:** BRK-2, BRK-3, BRK-4
- **Priorität:** Must
- **T-Shirt:** M | **Story Points:** 5 | **Sprint:** 3

**Summary-AC:**

- Mock-IdP-Server (z.B. via `respx` oder `pytest-httpserver`) simuliert Google/Microsoft.
- Tests für vollen OIDC-Flow (Code-Tausch, ID-Token-Verifikation, User-Mapping).

---

#### QUA-5: End-to-End-Integration-Test

- **Epic:** QUA
- **Bezug:** Erfolgskriterien aus 05_requirements 2.3
- **Priorität:** Must
- **T-Shirt:** L | **Story Points:** 8 | **Sprint:** 3

**Summary-AC:**

- Test deckt komplette Kette ab: Login mit Email/Passwort → PQ-Session-Etablierung → geschützter API-Call → Logout.
- Sowohl HTTP-Client-Test als auch (falls möglich) E2E mit Expo-Test (Detox optional).

---

#### QUA-6: Performance-Benchmark PQ-Session-Etablierung

- **Epic:** QUA
- **Bezug:** NFR-Perf-1
- **Priorität:** Should
- **T-Shirt:** S | **Story Points:** 2 | **Sprint:** 4

**Summary-AC:**

- Skript misst Session-Init-Latenz (P50, P95) über 100 Iterationen.
- Ergebnis im Berichts-Kapitel "Performance" dokumentiert.

---

#### QUA-7: Performance-Benchmark Token-Verifikation

- **Epic:** QUA
- **Bezug:** NFR-Perf-2
- **Priorität:** Should
- **T-Shirt:** S | **Story Points:** 2 | **Sprint:** 4

**Summary-AC:**

- Skript misst Token-Verify-Latenz über 1000 Iterationen.
- Ergebnis dokumentiert.

---

#### QUA-8: Performance-Benchmark AES-GCM-Overhead

- **Epic:** QUA
- **Bezug:** NFR-Perf-3
- **Priorität:** Should
- **T-Shirt:** S | **Story Points:** 2 | **Sprint:** 4

**Summary-AC:**

- Skript misst Verschlüsselungs-Overhead pro API-Call.
- Vergleich Plaintext vs. AES-GCM-verschlüsselter Payload.

---

### Epic DOC: Documentation und Reporting

**Ziel:** Abgabe-konforme Dokumentation und Präsentation (Bewertungs-Kriterien 1 bis 4).

#### DOC-1: Schlussbericht (DOCX)

- **Epic:** DOC
- **Bezug:** Merkblatt-A, Bewertungs-Kriterien 1 bis 5
- **Priorität:** Must
- **T-Shirt:** L | **Story Points:** 13 | **Sprint:** 4

**Summary-AC:**

- DOCX-Bericht enthält: Einleitung, Theorie (PQC, Scrum), Anforderungen, Architektur, Implementation, Tests, Performance, Reflexion, Quellen, Anhänge.
- Bezug zu allen Markdown-Dokumenten ist klar (Inhalt verfeinert, nicht dupliziert).
- Bewertungs-Matrix wird im Bericht implizit beantwortet (jede Sektion adressiert ein oder mehrere Kriterien).
- Geschätzter Umfang: 40 bis 60 Seiten.

---

#### DOC-2: Schluss-Präsentation (PPTX)

- **Epic:** DOC
- **Bezug:** Bewertungs-Kriterium 6 (Kolloquium)
- **Priorität:** Must
- **T-Shirt:** M | **Story Points:** 8 | **Sprint:** 4

**Summary-AC:**

- PPTX-Deck mit ca. 15 Slides für 15-20 Minuten Präsentation.
- Inhalt: Motivation, Architektur, Demo-Highlights, Crypto-Agility-Beweis, Reflexion, Q&A.
- Demo-Recording vorbereitet als Fallback.

---

#### DOC-3: README und Setup-Anleitung

- **Epic:** DOC
- **Bezug:** Merkblatt-A "Installation und Inbetriebnahme"
- **Priorität:** Must
- **T-Shirt:** S | **Story Points:** 2 | **Sprint:** 4

**Summary-AC:**

- Top-Level-README mit Projekt-Beschreibung, Setup, Run, Test, Demo-Anweisungen.
- Mentor kann das System mit den README-Schritten in maximal 15 Minuten zum Laufen bringen.

---

#### DOC-4: Architecture Decision Records (ADRs) finalisieren

- **Epic:** DOC
- **Bezug:** B5.5 (Initiative und Kreativität)
- **Priorität:** Should
- **T-Shirt:** S | **Story Points:** 3 | **Sprint:** 4

**Summary-AC:**

- `docs/adr/` enthält strukturierte Decision-Records für: Architektur-Option (Option 2), Crypto-Library-Wahl, App-Layer vs TLS-Layer, IdP-Plugin-Architektur.
- Format: Title, Context, Decision, Consequences, Alternatives.

---

### Epic STR: Stretch Goals

Items, die nur bei freiem Slack angegangen werden. Nicht für Sprint 1 bis 3 zugesagt.

#### STR-1: Hybrid Key Combiner (ML-KEM + X25519 via HKDF)

- **Epic:** STR
- **Bezug:** FR-Crypto-4, NFR-Sec-6
- **Priorität:** Could
- **T-Shirt:** L | **Story Points:** 8 | **Sprint:** Stretch (idealerweise nach Sprint 3 falls Zeit)

**Summary-AC:**

- App und Server kombinieren ML-KEM-Shared-Secret mit X25519-Shared-Secret via HKDF.
- Defense-in-Depth: Angreifer muss beide Verfahren brechen.
- Tests demonstrieren Funktion.

---

#### STR-2: Apple Sign In Plugin

- **Epic:** STR
- **Bezug:** Projekt-Decisions (memory)
- **Priorität:** Could
- **T-Shirt:** M | **Story Points:** 5 | **Sprint:** Stretch

**Summary-AC:**

- `idp_plugins/apple.py` implementiert die Plugin-Schnittstelle.
- iOS-spezifische OAuth-Flow.
- Manuelle Demo mit Test-Account.

---

#### STR-3: Self-signed ML-DSA-Test-Cert Demo

- **Epic:** STR
- **Bezug:** Projekt-Decisions (Stretch)
- **Priorität:** Could
- **T-Shirt:** M | **Story Points:** 5 | **Sprint:** Stretch

**Summary-AC:**

- ML-DSA-65-signiertes TLS-Zertifikat generiert.
- nginx-Instanz (separate Demo-Konfiguration) bietet ML-DSA-Cert an.
- Demo mit oqs-curl.

---

### Epic SEC: Security Infrastructure (nachträglich angelegt)

Diese fünf Stories sind aus dem Senior-Closing-Review von PQC-19 (SKL-1) am 25.05.2026 entstanden. Es handelt sich um Tier-1-Findings die zu Sprint-2-Material aufgewertet wurden, weil sie eine ordentliche Web-Security-Baseline für das FastAPI-Backend bilden. Alle fünf Stories sind Voraussetzung für PQC-30 (AUT-3 Login-Endpoint) und haben deshalb `blocks PQC-30` Issue-Links im Jira. Volle Akzeptanzkriterien stehen in den jeweiligen Jira-Stories, das vollständige Refinement passiert im Sprint-2-Planning. Bezug: NFR-Sec-3 (Web-Security-Baseline aus `05_requirements.md`).

#### SEC-1: Request-ID Middleware

- **Epic:** SEC
- **Jira-Key:** PQC-79
- **Bezug:** NFR-Sec-3, Folge aus PQC-19 Senior-Closing-Review (Finding tier-1)
- **Priorität:** Must
- **T-Shirt:** S | **Story Points:** 2 | **Sprint:** 2

**Summary-AC (Refinement im Sprint 2 Planning):**

- ASGI-Middleware fügt pro Request eine Request-ID (UUID) hinzu.
- ID ist im Response-Header `X-Request-ID` und in allen structlog-Log-Lines des Requests vorhanden.
- Volle ACs in Jira-Story PQC-79.

---

#### SEC-2: CORS-Middleware

- **Epic:** SEC
- **Jira-Key:** PQC-80
- **Bezug:** NFR-Sec-3, Folge aus PQC-19 Senior-Closing-Review
- **Priorität:** Must
- **T-Shirt:** S | **Story Points:** 2 | **Sprint:** 2

**Summary-AC (Refinement im Sprint 2 Planning):**

- FastAPI CORSMiddleware konfiguriert mit explicit allow-list (App-Origin, Dev-Localhost).
- Volle ACs in Jira-Story PQC-80.

---

#### SEC-3: TrustedHost-Middleware

- **Epic:** SEC
- **Jira-Key:** PQC-81
- **Bezug:** NFR-Sec-3, Folge aus PQC-19 Senior-Closing-Review
- **Priorität:** Must
- **T-Shirt:** XS | **Story Points:** 1 | **Sprint:** 2

**Summary-AC (Refinement im Sprint 2 Planning):**

- TrustedHostMiddleware schützt vor Host-Header-Injection.
- Konfiguration über Settings.
- Volle ACs in Jira-Story PQC-81.

---

#### SEC-4: Security-Headers

- **Epic:** SEC
- **Jira-Key:** PQC-82
- **Bezug:** NFR-Sec-3, Folge aus PQC-19 Senior-Closing-Review
- **Priorität:** Must
- **T-Shirt:** S | **Story Points:** 2 | **Sprint:** 2

**Summary-AC (Refinement im Sprint 2 Planning):**

- Standard-Security-Headers in jeder Response (HSTS, X-Content-Type-Options, Referrer-Policy, X-Frame-Options, CSP-Skelett).
- Volle ACs in Jira-Story PQC-82.

---

#### SEC-5: Rate-Limiting

- **Epic:** SEC
- **Jira-Key:** PQC-83
- **Bezug:** NFR-Sec-3, Folge aus PQC-19 Senior-Closing-Review
- **Priorität:** Must
- **T-Shirt:** S | **Story Points:** 3 | **Sprint:** 2

**Summary-AC (Refinement im Sprint 2 Planning):**

- IP-basiertes Rate-Limit auf Auth-Endpoints, mit Bucket über Redis oder In-Memory.
- 429 Response bei Überschreitung.
- Volle ACs in Jira-Story PQC-83.

---

## 5. Story-Points-Übersicht pro Sprint

| Sprint | Must-Stories (SP) | Should/Could-Stories (SP) | Total SP geplant | Realistische Kapazität (SP) |
|---|---|---|---|---|
| Sprint 0 | INF-1 bis INF-4 = 14 | --- | 14 | 14 (rückblickend, Sprint läuft aus) |
| Sprint 1 | SKL+CRY+AUT+TOK Must Cluster = ca. 41 | 0 | 41 | ca. 20 bis 25 |
| Sprint 2 | BRK + TLS + APP Federation = ca. 47, plus SEC = 10 | 0 | 57 | ca. 25 bis 30 |
| Sprint 3 | SES + DCH + APP Rest + CRY-3/4/6/7 = ca. 60 | SES-4 (3) | 63 | ca. 25 bis 30 |
| Sprint 4 | DOC-1, DOC-2, DOC-3, QUA-6/7/8 = ca. 29 | TOK-3, TOK-4, DOC-4 (10) | 39 | ca. 12 bis 15 |
| Stretch | --- | STR-1, STR-2, STR-3 = 18 | --- | --- |

**SM-Warnung und experimenteller Ansatz für Sprint 1:** Die geplante Story-Point-Last übersteigt in allen Sprints die klassische Solo-Dev-Kapazität deutlich. Bei berücksichtigtem AI-Multiplier (1.5x, siehe 1.7) erweitert sich die effektive Kapazität auf etwa 30 bis 37 SP pro 14-Tage-Sprint. Sprint 1 ist allerdings auf 7 Tage komprimiert (25.05 bis 31.05), womit die effektive Kapazität auf etwa 15 bis 18 SP halbiert ist, bei einer geplanten Last von 41 SP.

**Bewusste Entscheidung:** Sprint 1 wird trotz dieser Diskrepanz nicht im Scope reduziert, sondern als empirisches Experiment genutzt, um die tatsächliche AI-unterstützte Geschwindigkeit zu messen. Nach Sprint 1 wird in der Retro analysiert, wie viele Stories tatsächlich abgeschlossen wurden, und ob die Sprints 2 bis 4 angepasst werden müssen oder ob die ursprüngliche Schätzung mit AI realistisch ist. Code-Freeze am 28.06 bleibt die harte Schranke.

**Konsequenz:** Realistisch werden voraussichtlich Sprint 3-Items wie SES-4 (Algorithmus-Negotiation als Should) und Stretch-Items (STR-1 bis STR-3) gestrichen oder nur skizziert. Das ist nicht Versagen, sondern saubere Adaption.

---

## 6. MoSCoW-Verteilung

| Priorität | Anzahl Stories | Story Points (Summe) |
|---|---|---|
| Must | 58 | ca. 210 |
| Should | 7 | ca. 22 |
| Could | 3 | 18 |
| **Total** | **68** | **ca. 250** |

Die hohe Must-Quote spiegelt die enge Verzahnung der Architektur-Komponenten wider. Wenn ein Must-Item gestrichen werden muss, ist es voraussichtlich aus dem App-Polish-Bereich (z.B. visuelles Layout, Profile-Screen-Detail).

---

## 7. Versionsverlauf

| Version | Datum | Änderung |
|---|---|---|
| 1.0 | 17.05.2026 | Initial-Version. 13 Epics mit 63 Stories. Volle Akzeptanzkriterien für Sprint-0- bis Sprint-2-Stories, Summary-AC für Sprint-3- und Sprint-4-Stories. MoSCoW-Priorisierung. Sprint-Allokation mit SM-Warnung zur Kapazitäts-Über-Allokation. |
| 1.1 | 27.05.2026 | Priorisierungs-Konvention erweitert (4-Achsen-Modell mit Built-in-Priority-Field, Sektion 1.3). Epic SEC nachträglich angelegt (PQC-78) mit 5 Stories SEC-1 bis SEC-5 (PQC-79 bis PQC-83), aus PQC-19 Senior-Closing-Review als Tier-1-Findings. Total jetzt 14 Epics mit 68 Stories. Sprint 2 SP-Last von 47 auf 57 erhöht. |
