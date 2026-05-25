# Sprint Planning: Sprint 1

**Datum:** 24.05.2026
**Sprint-Zeitraum:** 24.05 bis 31.05.2026 (8 Kalendertage, 7 Arbeitstage + 1 Review-Tag)
**Timebox Planning:** 1 Stunde

---

## 1. Sprint-Ziel (Warum ist dieser Sprint wertvoll?)

> Demo-orientiert formuliert.

**Sprint Goal:** Am Sprint-Ende kann ich einen End-to-End-Login lokal durchspielen: Test-User wird via Admin-CLI angelegt, dann via POST `/auth/local/login` mit Email und Passwort authentifiziert, und der Server liefert einen ML-DSA-65-signierten Broker-Token zurück, der mit dem Public Key verifizierbar ist.

**Implizit dazu:** Docker-Compose-Setup mit FastAPI-Skeleton läuft, Crypto-Abstraction-Layer steht für ML-DSA-65, lokaler User-Store mit Argon2id-Hashes funktioniert.

---

## 2. Ausgewählte Backlog-Items

### Critical Path (Must für Demo, 37 SP)

| Jira-Key | Story | Bezug | T-Shirt | SP | Priorität |
|---|---|---|---|---|---|
| PQC-17 | INF-3: Docker-Compose-Skeleton | Design 3.1 | M | 5 | Must (Carry-Over) |
| PQC-19 | SKL-1: FastAPI-Skeleton mit Config-Loading | Design 2.1 | S | 2 | Must |
| PQC-21 | CRY-1: Algorithm Registry für KEM und Signature | FR-Crypto-1 | M | 5 | Must |
| PQC-25 | CRY-5: liboqs-python Wrapper für ML-DSA-65 | FR-Crypto-1, FIPS 204 | M | 5 | Must |
| PQC-22 | CRY-2: Crypto-Facade für sign/verify (partial) | FR-Crypto-2 | S | 3 | Must |
| PQC-32 | TOK-1: Broker-Token-Ausstellung mit ML-DSA-65 | FR-Token-1 | M | 5 | Must |
| PQC-28 | AUT-1: User-Store mit SQLAlchemy und SQLite | FR-Auth-1, Design 5.3 | M | 5 | Must |
| PQC-29 | AUT-2: Admin-CLI für User-Provisioning | FR-Auth-2 | S | 2 | Must |
| PQC-30 | AUT-3: POST /auth/local/login Endpoint | UC-1, FR-Auth-1 | M | 5 | Must |

### Wichtig, aber nicht strikt auf Critical Path (17 SP)

| Jira-Key | Story | Bezug | T-Shirt | SP | Priorität |
|---|---|---|---|---|---|
| PQC-33 | TOK-2: Broker-Token-Verifikation | FR-Token-2 | S | 2 | Must (für Test des Tokens) |
| PQC-31 | AUT-4: User-Enumeration-Schutz | NFR-Sec-4 | XS | 1 | Must |
| PQC-63 | QUA-1: Pytest-Setup | Bewertung K5, DoD | XS | 1 | Must |
| PQC-64 | QUA-2: Unit-Tests Auth-Module | AUT-* | S | 2 | Must |
| PQC-65 | QUA-3: Unit-Tests Token- und Crypto-Module | TOK-1/2, CRY-* | S | 3 | Must |
| PQC-18 | INF-4: oqs-provider-fähiges nginx-Image | NFR-Sec-1 | M | 5 | Must (Carry-Over, eigentlich Sprint-2-Vorbereitung) |
| PQC-20 | SKL-2: Expo-Skeleton mit Navigation | Design 2.2 | S | 3 | Must (eigentlich Sprint-2-Vorbereitung) |

### Sprint-Level Stretch (5 SP, erst nach allen Must-Items)

| Jira-Key | Story | T-Shirt | SP |
|---|---|---|---|
| PQC-54 | APP-1: Login-Screen mit drei Optionen (UI only) | S | 2 |
| PQC-57 | APP-4: AuthContext (globaler Auth-State) | S | 2 |
| PQC-62 | APP-9: Token-Persistenz mit expo-secure-store | XS | 1 |

**Summe geplante Story Points:** 54 Must + 5 Stretch = 59 SP
**Geschätzte Wochenkapazität:** ~20 Stunden real, mit AI-Multiplier 1.5x effektiv ~30 Stunden klassisch-Output. SM-Anmerkung: nominell 33h Defizit gegenüber Schätzung. Sprint 1 als Experiment um AI-Multiplier für Code-Arbeit empirisch zu messen.

---

## 3. Umsetzungsplan (Arbeitstag-basiert)

**Tatsächliche Arbeitstage:** Wochenenden und Mittwoche sind die Standard-Arbeitstage. Sprint 1 hat damit nur fünf Arbeitstage statt sieben Kalendertage: Sun 24.05, Mon 25.05 (Feiertags-Ausnahme), Wed 27.05 (Abend), Sat 30.05, Sun 31.05. Tue 26.05, Thu 28.05 und Fri 29.05 sind keine Arbeitstage. Diese Realität verändert die Tag-Verteilung deutlich, der Plan ist verdichtet.

### Tag 1: Sonntag 24.05 (heute, ca. 2-3h)

- **Sprint Planning ausfüllen** (dieses Dokument)
- **Daily Journal** anlegen und ersten Eintrag schreiben
- Falls Zeit und Energie: in INF-3 reinkommen, docker-compose.yml-Skeleton anfangen

### Tag 2: Montag 25.05 (Feiertag-Ausnahme, ca. 5-6h)

Fokus: Infrastruktur und FastAPI-Skeleton, Crypto-Foundation starten

- **INF-3 (5 SP):** Docker-Compose-Skeleton
  - Tasks: docker-compose.yml schreiben (nginx, auth-service, redis Services), Python-3.12-Dockerfile für auth-service, persistent Volumes konfigurieren, Dummy-Endpoint in auth-service, `docker compose up` test
- **SKL-1 (2 SP):** FastAPI-Skeleton
  - Tasks: `server/` Struktur (main.py, config.py, routers/), pydantic-settings für config.yaml, `/health` Endpoint, JSON-Logging, in Docker-Compose integrieren
- **CRY-1 starten falls Zeit (5 SP):** Algorithm Registry
  - Tasks: `crypto/registry.py` mit `CryptoRegistry`-Klasse, `register_kem`/`register_signature`-Methoden, Error-Handling, Unit-Tests

### Tag 3: Mittwoch 27.05 (Abend, ca. 2-3h) — HALBZEIT-CHECK

Fokus: Crypto-Foundation finalisieren

- **CRY-1 (5 SP):** Algorithm Registry fertig machen falls Montag nicht abgeschlossen
- **Halftime-Check im Daily Journal:** Sind INF-3, SKL-1, CRY-1 done? Falls nein, sofort Scope-Entscheidung treffen: INF-4 streichen, SKL-2 streichen, Test-Coverage reduzieren auf nur Auth-Modul. Falls ja, weiter zum CRY-5-Start am Samstag.

### Tag 4: Samstag 30.05 (ca. 6-8h, schwerster Tag)

Fokus: Crypto-Layer abschliessen, Token-Service, User-Store

- **CRY-5 (5 SP):** liboqs-python Wrapper für ML-DSA-65
  - Tasks: `LibOqsSignature`-Adapter (keygen, sign, verify), Registry-Integration, Round-Trip-Test, Schlüssel-Persistierung aus File-Pfad
- **CRY-2 (3 SP):** Crypto-Facade für sign/verify
  - Tasks: `CryptoFacade.sign()` und `.verify()`, Algorithmus-Wahl via Config, Tests sign/verify Round-Trip ML-DSA-65
- **TOK-1 (5 SP):** Broker-Token-Ausstellung
  - Tasks: `token_service.issue()`, JWS-Compact-Format, Claims (sub, iss, iat, exp, auth_method), TTL aus Config, base64url-Encoding
- **TOK-2 (2 SP):** Broker-Token-Verifikation
  - Tasks: `token_service.verify()`, Expiry- und Issuer-Check, Custom Exceptions

### Tag 5: Sonntag 31.05 (ca. 6-8h, inklusive Sprint Review/Retro)

Fokus: Login-Flow, Tests, Sprint-Abschluss

- **AUT-1 (5 SP):** User-Store
  - Tasks: SQLAlchemy User-Model, Alembic-Migration, aiosqlite async, Argon2id-Hash-Konfiguration, Unit-Tests CRUD
- **AUT-2 (2 SP):** Admin-CLI
  - Tasks: `python -m auth_service.admin create-user`, Argon2id-Hash, `list-users`
- **AUT-3 (5 SP):** POST /auth/local/login Endpoint
  - Tasks: Endpoint definieren, Argon2-Verify, Token via TOK-1 ausstellen, 401 bei falschen Credentials
- **AUT-4 (1 SP):** User-Enumeration-Schutz (Konstante-Zeit-Verhalten)
- **QUA-1 + QUA-2 + QUA-3 (6 SP):** Test-Setup und Test-Coverage für Auth, Token, Crypto
- **End-to-End-Demo-Test:** curl-Flow durchspielen (User anlegen, einloggen, Token verifizieren)
- **Sprint Review** (gemeinsam mit Co-SM): Self-Demo, Story-Prüfung gegen AC und DoD, Risk Review
- **Sprint Retrospective** (gemeinsam): drei Achsen, Top 3 Massnahmen für Sprint 2
- **Mentor-Update-Post** vorbereiten für Zwischengespräch am 01.06 (Mo)
- **Falls Zeit:** INF-4 (5 SP) oder Sprint-Stretch (APP-1, APP-4, APP-9)

### Realistische SP-Verteilung pro Tag

| Tag | Datum | Stunden | Plausible SP | Notiz |
|---|---|---|---|---|
| 1 | So 24.05 | 2-3 | 0-2 | Heute hauptsächlich Planning |
| 2 | Mo 25.05 | 5-6 | 7-12 | Feiertag, produktiver Tag |
| 3 | Mi 27.05 | 2-3 | 3-5 | Abend, Halbzeit-Check |
| 4 | Sa 30.05 | 6-8 | 13-15 | Schwerster Tag, Crypto/Token |
| 5 | So 31.05 | 6-8 | 13-17 | Inklusive Sprint Review/Retro |

**Realistische Summe:** 36 bis 51 SP. Bei Must-Ziel von 54 SP ist das knapp aber machbar wenn AI-Multiplier hilft.

---

## 4. Risiken und Abhängigkeiten

| Risk-ID | Risiko | Wahrscheinlichkeit Sprint 1 | Auswirkung Sprint 1 | Mitigation in Sprint 1 |
|---|---|---|---|---|
| R-S01 (Sprint-Kapazität) | Nominell ~33h Defizit gegenüber Schätzung | Hoch (eingetreten in der Planung) | Mittel bis hoch | Critical-Path-Priorisierung, INF-4 und SKL-2 als Defer-Kandidaten, ehrliche Velocity-Auswertung in Retro |
| R-T01 (liboqs-Build) | Erstmals real getestet in CRY-5 | Mittel | Hoch | Container-First via openquantumsafe/oqs-ossl3, Pre-Built-Image als Base wenn möglich |
| R-T03 (Mobile-OS-Crypto-Quirks) | Sprint-Stretch und SKL-2 bringen erstes Touch-Point | Niedrig (nur falls Stretch erreicht) | Niedrig | `react-native-get-random-values` Polyfill direkt einrichten |
| R-P01 (Motivation/Konsistenz) | Sprint-0-Retro zeigte 0.5 h/Tag Schnitt, müssen wir auf ~3 h/Tag steigern | Mittel | Hoch | Sprint-0-Retro Top-3-Massnahme #2 (Wochenkapazität reservieren) konsequent leben |

### Externe Abhängigkeiten

Keine harten externen Abhängigkeiten in Sprint 1. Sprint 2 wird Google- und Microsoft-OAuth-App-Setup brauchen, das wird in dieser Woche parallel vorbereitet (OAuth-Client-IDs anlegen, redirect URIs konfigurieren), damit Sprint 2 nicht durch Setup-Wartezeiten gebremst wird.

---

## 5. Verzicht / Bewusste Ausgrenzungen

Folgende Stories sind im Sprint 1 explizit nicht im Scope (bzw. wurden nicht hier ausgewählt):

- **TOK-3 (Schlüssel-Rotation), TOK-4 (JWKS-Endpoint):** Sprint 4 (Should-Items, nicht kritisch für Sprint-1-Demo)
- **BRK-1 bis BRK-7 (Federation):** Sprint 2, weil Sprint 1 nur lokalen Login abdeckt
- **TLS-1 bis TLS-3 (Hybrid TLS):** Sprint 2, transparent zum Auth-Service
- **CRY-3 (KEM-Operationen), CRY-4 (ML-KEM-Wrapper), CRY-6 (Client-Crypto), CRY-7 (Algorithmus-Identifier):** Sprint 3, erst dann für Session-Establishment relevant
- **SES, DCH (PQ-Session und Data-Channel):** Sprint 3
- **STR-1, STR-2, STR-3 (Stretch-Goals):** nur bei vorhandenem Slack am Projekt-Ende

---

## 6. Reserve / Stretch

### Kapazitäts-Reserve im Sprint

Keine echte 20-Prozent-Reserve eingeplant, weil die nominale Last sowieso schon über der Kapazität liegt. Statt Reserve gilt: Sprint-Level-Stretch wird nur angerührt nach Abschluss aller Must-Items. Falls Critical Path schneller als geplant durchläuft (z.B. wegen höherem AI-Multiplier), werden zuerst die Non-Critical Must-Items (TOK-2, AUT-4, QUA-1/2/3, dann INF-4, SKL-2) und erst danach die Sprint-Stretch-Items (APP-1, APP-4, APP-9) angegangen.

### Stretch-Reihenfolge falls Zeit

1. Critical Path Must (37 SP) — Pflicht
2. Test-Coverage (QUA-1, QUA-2, QUA-3, TOK-2, AUT-4) — Pflicht für Sprint-Goal-DoD
3. Sprint-2-Vorbereitung (INF-4 für TLS, SKL-2 für App)
4. Sprint-Stretch (APP-1 → APP-4 → APP-9 in dieser Reihenfolge)
5. Stretch-Stretch: OAuth-App-Setup für Sprint 2 (Google, Microsoft)

---

## 7. Definition of Ready Check

Für alle ausgewählten Stories bestätigt:

- [x] User-Story-Format oder klare technische Beschreibung in jedem Issue
- [x] Mindestens zwei Akzeptanzkriterien pro Story (siehe Jira-Descriptions)
- [x] Abhängigkeiten geklärt (siehe Build-Reihenfolge oben, Bottom-up)
- [x] Geschätzt (T-Shirt und Story Points)
- [x] Bezug zu Requirement vorhanden (FR-Auth, FR-Token, FR-Crypto, etc.)
- [x] Klein genug für einen Sprint (keine XL-Stories drin, alle ≤ 5 SP ausser SES-1 in späteren Sprints)

Alle 19 Stories sind technisch DoR-konform.

---

## 8. Notizen und offene Punkte

- **AI-Multiplier-Experiment.** Sprint 1 ist der erste reale Test für den AI-Multiplier in Code-Arbeit (Sprint 0 hatte nur Doku-Arbeit). In der Retro wird systematisch ausgewertet: wie viele Story Points wurden tatsächlich abgeschlossen vs. real geleistete Stunden, und was bedeutet das für die effektive Geschwindigkeit.
- **Wochenkapazität konkret.** Sprint-0-Retro-Massnahme #2: feste Slots fürs Projekt einplanen. Konkret bestätigt für Sprint 1: heute Sun 24.05, Mon 25.05 (Feiertag-Ausnahme), Wed 27.05 Abend, Sat 30.05, Sun 31.05. Standard-Cadence ab Sprint 2: Wochenenden plus Mittwoch-Abend.
- **Daily Journal Pflicht.** Sprint-0-Retro-Massnahme #1: pro Arbeitstag ein Eintrag, kein Schummeln. Erste Erfassung heute.
- **Mentor-Termin am 01.06 (Tag nach Sprint-Ende).** Demo-Vorbereitung läuft am Sprint-Tag 7 oder 8, falls möglich aufzeichnen oder zumindest Demo-Skript notieren.
- **Sprint-Stretch APP-Stories.** Falls erreicht, gehen sie ins Sprint-Review als zusätzliche Done-Items aber NICHT als Sprint-Goal-Bestandteil. Sprint-Goal bleibt auf Server-Side-Login fokussiert.
- **Carry-Over INF-4 vs. Sprint 2.** INF-4 ist Sprint-0-Carry-Over aber technisch erst in Sprint 2 (TLS) gebraucht. Im Sprint 1 nur dann bauen wenn alle Must- und Critical-Path-Items durch sind, sonst nach Sprint 2 schieben.

---

## SM-Risk-Warnung (am Sprint-Anfang)

Sprint 1 ist nominell überzeichnet. Mit nur fünf realen Arbeitstagen (Sun, Mon, Wed Abend, Sat, Sun) ist das Critical-Path-Schaffen abhängig davon, dass der AI-Multiplier wirklich greift und Mon plus Sat als heavy Days durchgezogen werden. Halbzeit-Check am Mittwoch 27.05: wenn INF-3, SKL-1 und CRY-1 nicht done sind, dann sofort Scope reduzieren (INF-4 streichen, SKL-2 streichen, Test-Coverage minimieren auf nur Auth-Module). Sonst Sprint-Ziel kommunikativ anpassen.

Daily-Journal-Eintrag am 27.05 muss explizit dieser Halbzeit-Check sein.

## Co-SM und Co-Project-Lead Rolle in dieser Chat-Session

Die Implementation (Code-Arbeit für die Stories) erfolgt in einem zweiten Chat. Diese Session dient als Strategie- und Reflexions-Ort:

- Sprint Planning, Reviews und Retrospektiven werden hier ausgefüllt
- Daily Journal Einträge werden hier gemacht (nach jeder Implementations-Session vom Studierenden gemeldet, dann gemeinsam dokumentiert)
- Mentor-Kommunikation wird hier formuliert
- Scope-Entscheidungen, Risiko-Updates und Adaption werden hier diskutiert
- Code-Snippets oder konkrete Implementation-Decisions kommen aus dem zweiten Chat

Daraus folgt: nach jeder Coding-Session sollte der Studierende hier kurz Bescheid sagen mit Stunden plus erledigten Stories plus aufgetauchten Blockern, damit das Daily Journal aktuell bleibt.
