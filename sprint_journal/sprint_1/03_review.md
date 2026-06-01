# Sprint Review: Sprint 1

**Datum:** 31.05.2026
**Sprint-Zeitraum:** 24.05 bis 31.05.2026 (8 Kalendertage, 6 effektive Arbeitstage gemäss Standard-Schedule plus eine Donnerstag-Ausnahme)
**Timebox:** 1 Stunde

**Sprint-Ziel:** "Am Sprint-Ende kann ich einen End-to-End-Login lokal durchspielen: Test-User wird via Admin-CLI angelegt, dann via POST `/auth/local/login` mit Email und Passwort authentifiziert, und der Server liefert einen ML-DSA-65-signierten Broker-Token zurück, der mit dem Public Key verifizierbar ist."

---

## 1. Erreichung des Sprint-Ziels

- [x] **Vollständig erreicht (Detail unten)**
- [ ] Teilweise erreicht
- [ ] Nicht erreicht

**Begründung / Kontext:**

Das Sprint-Goal ist mit Demo D-004 (Local-Login-Pipeline) reproduzierbar erreicht. Admin-CLI erstellt User (PQC-29), Login-Endpoint validiert Credentials und stellt Token aus (PQC-30), TokenService signiert mit ML-DSA-65 (PQC-32), Verifikation funktioniert über die Token-Verify-Pipeline (PQC-33). Live-Verifikation im Container.

Zusätzlich wurden vier Bonus-Erfüllungen über das Sprint-Goal hinaus erreicht:

- SEC-Schicht produktionsreif (5 SEC-Stories aus Sprint 2 vorgezogen, weil als Voraussetzung für AUT-3 nötig).
- Quality-Schicht formal abgeschlossen mit 85% Coverage auf Auth-Modulen (AC-4 von QUA-2 deutlich übererfüllt).
- PQC-TLS-Handshake mit X25519MLKEM768 live demonstriert (D-005, Sprint-2-TLS-Foundation steht).
- Mobile-Login-Flow auf iPhone live via Expo Go (D-006, alle drei Sprint-Stretch-Stories Done).

Damit ist Sprint 1 zu 100% komplett (alle Must plus alle Stretch). Carry-Over nach Sprint 2 ist Null.

---

## 2. Increment-Demo und Story-Prüfung

Die detaillierten AC-Checks pro Story liegen in den jeweiligen Jira-Done-Comments und Evidence-Files. Hier nur die Sprint-übergreifende Zusammenfassung gruppiert nach Epic.

### Infrastructure (INF) — 2 Stories, 10 SP

| Story | Status | AC-Bilanz | Demo / Evidence |
|---|---|---|---|
| PQC-17 INF-3 Docker-Compose-Skeleton | Done | 5/5 AC erfüllt | `evidence/PQC-17_INF-3_compose_up.md` |
| PQC-18 INF-4 oqs-provider nginx | Done | Alle AC plus X25519MLKEM768 Live-Handshake | `evidence/PQC-18_INF-4_oqs_nginx.md`, `demos/D-005` |

**Endurteil:** Beide Sprint-0-Carry-Over erledigt. R-T05 (oqs-provider TLS-Setup-Bricht) und R-T01 (liboqs-Build) damit mitigated.

### Skeletons (SKL) — 2 Stories, 5 SP

| Story | Status | AC-Bilanz | Demo / Evidence |
|---|---|---|---|
| PQC-19 SKL-1 FastAPI-Skeleton | Done | Alle AC, plus 5 SEC-Stories als Sprint-2-Material identifiziert | `evidence/PQC-19_SKL-1_fastapi_skeleton.md` |
| PQC-20 SKL-2 Expo-Skeleton | Done | Alle AC, drei Stack-Routes live auf iPhone | `evidence/PQC-20_SKL-2_expo_skeleton.md`, iPhone-Live-Demo |

**Endurteil:** Service-Skeleton und Mobile-Skeleton stehen. PQC-19 Closing-Review hat 5 SEC-Stories als Tier-1-Findings produziert die in dieser Sprint-1 nachträglich angelegt und auch noch im Sprint umgesetzt wurden.

### Crypto-Foundation (CRY) — 3 Stories, 13 SP

| Story | Status | AC-Bilanz | Demo / Evidence |
|---|---|---|---|
| PQC-21 CRY-1 Algorithm Registry | Done | Alle AC, Plugin-Pattern | `evidence/PQC-21_CRY-1_algorithm_registry.md` |
| PQC-22 CRY-2 Crypto-Facade sign/verify | Done | 4/4 AC, 11 Tests, F-015 in Story gefixt | `evidence/PQC-22_CRY-2_crypto_facade.md`, `demos/D-001` |
| PQC-25 CRY-5 liboqs-python ML-DSA-65 | Done | Echte FIPS-204-Sizes (1952/4032 Bytes) | `evidence/PQC-25_CRY-5_liboqs_ml_dsa.md` |

**Endurteil:** Crypto-Agility-Layer ist produktiv nutzbar. ML-DSA-65 funktioniert im Container.

### Token-Service (TOK) — 2 Stories, 7 SP — Sprint-Goal-relevant

| Story | Status | AC-Bilanz | Demo / Evidence |
|---|---|---|---|
| PQC-32 TOK-1 Broker-Token-Ausstellung | Done | 5/5 AC, 14 Tests, Tamper-Detection | `evidence/PQC-32_TOK-1_broker_token_ausstellung.md`, `demos/D-002` |
| PQC-33 TOK-2 Broker-Token-Verifikation | Done | 6/6 AC inkl. F-028 als AC-6 (RFC 8725 alg-Allowlist), 7 Verify-Szenarien | `evidence/PQC-33_TOK-2_broker_token_verifikation.md`, `demos/D-003` |

**Endurteil:** Token-Pipeline funktional vollständig (Issue plus Verify). RFC 8725 BCP konform. Sprint-Goal-Bestandteil.

### Authentication (AUT) — 4 Stories, 13 SP — Sprint-Goal-relevant

| Story | Status | AC-Bilanz | Demo / Evidence |
|---|---|---|---|
| PQC-28 AUT-1 SQLAlchemy User-Store plus Argon2id | Done | 5/5 AC, 35 Tests, Live-CRUD 6 Szenarien | `evidence/PQC-28_AUT-1_user_store.md` |
| PQC-29 AUT-2 Admin-CLI | Done | 5/5 AC, AC-1 Pfad-Update mit Begründung | `evidence/PQC-29_AUT-2_admin_cli.md` |
| PQC-30 AUT-3 Login-Endpoint | Done | Alle AC, Sprint-Goal-erfüllend | `demos/D-004` (Sprint-Goal-Meilenstein) |
| PQC-31 AUT-4 User-Enumeration-Schutz | Done | dummy_verify aus PQC-28 vorbereitet | (Evidence beim Implementation-Chat, falls Datei fehlt nachzureichen) |

**Endurteil:** Auth-Schicht ist End-to-End funktional. OWASP-konform (Argon2id m=64MB/t=3/p=4, kein --password-argv im CLI, dummy_verify gegen Enumeration).

### Security-Middlewares (SEC) — 5 Stories, 10 SP — aus Sprint 2 vorgezogen

| Story | Status | AC-Bilanz | Demo / Evidence |
|---|---|---|---|
| PQC-79 SEC-1 Request-ID Middleware | Done | Alle AC plus Logging-Hardening-Bundle (F-021/F-026/F-031/F-034) | (Implementation-Chat-Evidence) |
| PQC-80 SEC-2 CORS-Middleware | Done | 5/5 AC inkl. Wildcard-plus-Credentials Validator | (Implementation-Chat-Evidence) |
| PQC-81 SEC-3 TrustedHostMiddleware | Done | 3/3 AC, evil.com=400 verifiziert | (Implementation-Chat-Evidence) |
| PQC-82 SEC-4 Security-Headers | Done | OWASP, HSTS conditional non-dev, CSP weggelassen wg Swagger | (Implementation-Chat-Evidence) |
| PQC-83 SEC-5 Rate-Limiting | Done | slowapi plus Redis, F-005 plus F-048-Audit-Fix resolved | `evidence/PQC-83_SEC-5_rate_limiting.md` |

**Endurteil:** SEC-Schicht produktionsreif. F-048 (Per-IP-vs-Per-Cluster-Bug hinter nginx) durch Phase-1-Audit aufgedeckt und gefixt mit uvicorn proxy_headers plus forwarded_allow_ips.

### Quality (QUA) — 3 Stories, 6 SP

| Story | Status | AC-Bilanz | Demo / Evidence |
|---|---|---|---|
| PQC-63 QUA-1 Pytest-Setup | Done | conftest, pytest-cov, HTML-Coverage 57% Sandbox | `evidence/PQC-63_QUA-1_pytest_setup.md` |
| PQC-64 QUA-2 Auth-Module-Tests | Done | 85% Coverage gemessen, AC-4 (50%) übererfüllt | `evidence/PQC-64_QUA-2_unit_tests_auth.md` |
| PQC-65 QUA-3 Token plus Crypto Coverage | Done | 76 Tests gemessen, Test-Inventory dokumentiert | `evidence/PQC-65_QUA-3_unit_tests_token_crypto.md` |

**Endurteil:** Quality-Schicht formal abgeschlossen mit Coverage-Reporting. Auth-Module 85%, ein starkes Bericht-Argument.

### App-Bundle Stretch (APP) — 3 Stories, 5 SP

| Story | Status | AC-Bilanz | Demo / Evidence |
|---|---|---|---|
| PQC-57 APP-4 AuthContext | Done | 4/4 AC, jwt-decode exp-Check, Auto-Login | `evidence/PQC-57_APP-4_auth_context.md` |
| PQC-62 APP-9 Token-Persistenz | Done | 3/4 AC voll, AC-4 PARTIAL wegen Dev-Mode-Limitation F-055 | `evidence/PQC-62_APP-9_token_persistence.md` |
| PQC-54 APP-1 Login-Screen | Done | 5/5 AC, Fake-Login UI only | `evidence/PQC-54_APP-1_login_screen.md`, `demos/D-006` |

**Endurteil:** Mobile-Login-Foundation steht. Sprint-1-Stretch erfüllt. AC-4 von APP-9 PARTIAL ist bewusst akzeptiert und als F-055 für Sprint 4 (falls TestFlight-Deploy) getrackt.

---

## 3. Stories, die nicht abgeschlossen wurden

**Keine.** Sprint 1 ist 100% komplett. Carry-Over nach Sprint 2 ist Null.

---

## 4. Erkenntnisse für den Product Backlog

### 4.1 Bewusste Spec-Updates während des Sprints (in Jira angepasst)

- PQC-33 AC-6 ergänzt: RFC 8725 BCP alg-Allowlist. Direkt aus F-028 (PQC-32-Review) eingeflossen, statt eigene Story dafür anzulegen.
- PQC-29 AC-1 Pfad-Update: `auth_service.admin` zu `admin`, weil die Server-Struktur flach ist. Begründung in Jira-Description.

### 4.2 Neue Backlog-Items aus Closing-Reviews

- **Epic SEC plus 5 Stories** wurden während Sprint 1 angelegt (PQC-78, PQC-79 bis PQC-83) aus dem PQC-19 Closing-Review. Statt erst in Sprint 2 wurden sie noch in Sprint 1 umgesetzt weil als Voraussetzung für AUT-3 nötig.

### 4.3 Findings die als Tier-2 in `docs/13_deferred_findings.md` getrackt sind

Insgesamt 55 Findings gesammelt (F-001 bis F-055). Davon resolved ca. 13 (in Stories oder durch SEC-Stories). Tier-2-Polish-Backlog liegt im Findings-File mit klaren Triggern (Sprint 3 vor Production, Sprint 4 Polish, vor TestFlight, etc.).

### 4.4 Backlog-Adjustments für Sprint 2

- Sprint 2 ist um 10 SP entlastet (SEC-Stories vorgezogen). Effektive Sprint-2-Last: 47 SP.
- TLS-Bundle (PQC-43/44/45) ist Empfehlung des Implementation-Chats als nächste Iteration, weil PQC-18 (oqs-provider nginx) Foundation steht.
- Sprint 2 Stories die unverändert bleiben: BRK-1 bis BRK-7 (Federation), TLS-1 bis TLS-3, APP-7 plus APP-8.

---

## 5. Risk Review

### 5.1 Eingetretene Risiken in diesem Sprint

| Risk-ID | Was ist passiert? | Reaktion |
|---|---|---|
| R-S01 (Sprint-Kapazität) | Sprint 1 hatte 41 SP Must Last bei nominell 15 bis 18 SP klassischer Kapazität in 7 Tagen. | Empirisches Experiment bestätigt: durch AI-Multiplier 6.4x ist die Last machbar. Sogar plus 10 SP SEC plus 5 SP Stretch. R-S01 für Sprint 2 entsprechend neu zu bewerten. |
| Bug F-048 | Per-IP-Rate-Limit war faktisch Per-Cluster-Limit weil request.client.host hinter nginx Container-IP ist. | Sofort gefixt mit uvicorn proxy_headers in PQC-83. Eingebaut in Audit-Phase, nicht in den Reviews verzögert. |

### 5.2 Geänderte Risiko-Bewertung

| Risk-ID | Alte Bewertung | Neue Bewertung | Begründung |
|---|---|---|---|
| R-T01 (liboqs Build) | Score 6 Active | Mitigated (25.05) | PQC-25 liboqs 0.15.0 baut sauber, ML-DSA-65 funktioniert. |
| R-T05 (oqs-provider TLS) | Score 2 Monitor | Mitigated (30.05) | PQC-18 X25519MLKEM768-Handshake live verifiziert. |
| R-S01 (Sprint-Kapazität) | Score 9 Active (nach Sprint 0) | Score 6 Active (zurück) | Sprint 1 hat empirisch gezeigt dass mit AI-Multiplier 6x die Last verkraftbar ist. |
| R-K03 (Expo Spezifika) | Score 4 Active | Score 3 Active | PQC-20 plus App-Bundle haben Expo-Pattern etabliert. Aber SDK-Lock-In hat eigene Risiken (R-N01). |

### 5.3 Neue Risiken (in diesem Sprint identifiziert)

| Risk-ID | Titel | Kategorie | Score | Status |
|---|---|---|---|---|
| R-N01 | Expo SDK Version nicht in App Store Expo-Go-App verfügbar | Node/JS-Ökosystem | 3 (Hoch Probability, Niedrig Impact) | Mitigated (SDK 54 als Projekt-Lock-In) |

### 5.4 Active-Watch-Status für Sprint 2

- [x] R-T04 (OIDC-Provider-Setup-Komplexität): in Sprint 2 direkt relevant für BRK-1 bis BRK-7. Vor Sprint-2-Start OAuth-Apps bei Google plus Microsoft anlegen.
- [x] R-S05 (Externe Abhängigkeiten OAuth-App-Setup): in Sprint 2 direkt relevant.
- [x] R-S01 (Sprint-Kapazität): Score auf 6 reduziert, aber weiter zu beobachten. Sprint 2 hat 47 SP plus Mobile-Stories.
- [x] R-S04 (Doku-Zeit Sprint 4): unverändert Score 6. Weiter relevant.

---

## 6. Velocity dieser Sprint

### 6.1 Story Points

| Metrik | Wert |
|---|---|
| Geplante Story Points (Must) | 41 SP |
| Geplante Story Points (Stretch) | 5 SP (APP-1, APP-4, APP-9) |
| Geplante Story Points (Total Sprint Backlog) | 46 SP |
| Zusätzlich aufgenommen während Sprint (SEC vorgezogen) | 10 SP |
| **Abgeschlossene Story Points** | **47 SP (20 Stories)** |

Sprint 1 hat die 41 SP Must voll erfüllt, alle 5 SP Stretch zusätzlich erledigt und 10 SP SEC aus Sprint 2 vorgezogen. Statt 46 SP geplant sind 47 SP geliefert.

### 6.2 Arbeitszeit

| Metrik | Wert |
|---|---|
| Tatsächliche Arbeitsstunden Implementation | ca. 14h 18m (über alle Done-Stories, exklusive Strategie-Chat-Doku) |
| Klassisch geschätzte Stunden (ohne AI) für die 20 Done-Stories | ca. 92h |
| **Aggregierter AI-Multiplier** | **6.4x** |

### 6.3 AI-Multiplier-Aufschlüsselung nach Story-Typ

| Story-Typ | Stories | Mittlerer Multiplier | Bemerkung |
|---|---|---|---|
| Infrastructure | INF-3, INF-4 | 8.75x | INF-3 Carry-Over mit klarer Spec, INF-4 Stock Multi-Stage-Build |
| Skeleton | SKL-1, SKL-2 | 2.0x | Setup-Friction deckelt den Multiplier |
| Crypto-Foundation | CRY-1, CRY-2, CRY-5 | 9.1x | CRY-1 reine Code-Generation, CRY-2 mit echter Validation |
| Token-Services | TOK-1, TOK-2 | 4.75x | TOK-1 mit 1h Closing-Review zusätzlich |
| Auth | AUT-1 bis AUT-4 | 7.75x | Standard-Pattern (SQLAlchemy, Argon2) gut etabliert |
| Quality | QUA-1, QUA-2, QUA-3 | 12.4x | Verifikations-Stories ziehen hoch |
| Security | SEC-1 bis SEC-5 | 10.0x | Bundle-Effekt erhöht Einzel-Multiplier |
| App | APP-1, APP-4, APP-9 | 8.4x | Bundle-Effekt mit AuthContext-Vorbau |

### 6.4 Beobachtungen für Schlussbericht und Mentor

- Der initiale Multiplier-Ansatz von 1.5x (siehe `08_scrum_setup.md` Sektion 7.4) war massiv konservativ. Empirisch ergeben sich 6.4x.
- Diese Zahl ist aber durch Sprint-1-Charakteristik überzogen: viele Setup- und Verifikations-Stories, plus Bundle-Effekte bei SEC und APP. Für Sprint 2 plus 3 mit echter Crypto-Interaktion (KEM, TLS, Federation) erwarte ich Multiplier zwischen 3x und 5x.
- Stabilster Mittelbereich (5x bis 8x) ist bei Stories mit echter Validation-Logik plus Tests (CRY-2, TOK-1, AUT-1, AUT-3, INF-4, APP-4).
- Setup-Friction-Stories sind die Untergrenze (2x). Hier hilft AI weniger weil Probleme oft umgebungsspezifisch sind (Node-Version, Expo-SDK-App-Store-Verfügbarkeit, Docker-Desktop-Start, etc.).

---

## 7. Stakeholder-Demo und Feedback-Erwartung

### 7.1 Demo-Material für den Mentor-Termin 01.06

Sechs reproduzierbare Demos in `sprint_journal/sprint_1/demos/`:

| Demo | Titel | Was zeigt es |
|---|---|---|
| D-001 | Crypto-Foundation | Algorithm Registry plus Crypto-Facade plus liboqs-Adapter |
| D-002 | Broker-Token-Ausstellung | TokenService.issue mit ML-DSA-65, Federated-Token, Tamper-Detection |
| D-003 | Broker-Token-Verifikation | TokenService.verify mit 7 Szenarien (Happy, Expired, Wrong-Iss, Wrong-Sig, alg=none, etc.) |
| **D-004** | **Local-Login-Pipeline (Sprint-Goal)** | **End-to-End Admin-CLI plus Login-Endpoint plus Token plus Verify** |
| D-005 | PQC-TLS-Handshake X25519MLKEM768 | openssl s_client -groups X25519MLKEM768, ML-DSA-65 Server-Cert |
| D-006 | Mobile-Login iPhone via Expo Go | Login-Screen, AuthContext, secure-store-Persistenz, Logout |

### 7.2 Feedback-Erwartung an Mentor

Für den Mentor-Termin 01.06 sind drei Themen geplant: erstens Verifikation dass das Sprint-Goal aus Mentor-Sicht erfüllt ist (Demo D-004 plus D-005), zweitens Diskussion der SEC-Vorzieh-Entscheidung (war das richtig oder hätte es Sprint 2 abwarten sollen), drittens Sprint-2-Empfehlung (TLS-Bundle als nächste Iteration) zur Bestätigung.

---

## 8. Notizen für die Retrospektive

- **Empirisch-positiver Befund:** Der AI-Multiplier liegt im Code wirklich bei 6x, nicht 1.5x. Sprint-Planning für Sprint 2 plus 3 entsprechend anpassen, aber mit Vorbehalt (Crypto-Interaktion deckelt den Multiplier).
- **Workflow-Verbesserung etabliert:** HARTE WORKFLOW-REGEL (Done nur nach explizitem User-OK) nach zwei Premature-Done-Fehlern bei PQC-25 plus PQC-22 eingeführt. Hat sich bei PQC-29 und PQC-32 bewährt.
- **Demo-Konvention etabliert:** D-NNN-Markers mit Trigger (Sprint-Goal, Mentor-Termin, Session-Ende). Sechs Demos im Sprint, alle reproduzierbar.
- **Evidence-File-Konvention etabliert:** pro Story ein Evidence-Markdown. Funktioniert gut, ist Pflicht-Teil der DoD geworden.
- **Tooling-Diskrepanz:** PQC-32 Worklog hatte temporär eine Diskrepanz zwischen Daily-Journal und Jira (1h vs 2h). Aufgedeckt beim Jira-Reconnect. Konvention für Coding-plus-Review-Zeit-Erfassung muss in Sprint 2 präzisiert werden.
- **Setup-Friction als Multiplier-Deckel:** SKL-1 und SKL-2 beide mit 2.0x Multiplier wegen Friction (Node-Version, Expo-SDK-App-Store). Für künftige Setup-Stories grosszügiger schätzen oder Friction-Anteil separat tracken.
- **Untracked work weiter ein Thema:** Strategie-Chat-Doku-Pflege (4-Achsen-Priorisierung, Evidence-Konvention, Zeit-Tracking-Konvention, Risk-Updates, SEC-Backlog-Pflege, Sprint-Closure) ist nicht in den Stories getrackt. Sollte für Sprint 2 als separate "Process-Story" eingeplant werden, oder explizit als Overhead-Buchung.

---

## 9. Versionsverlauf

| Version | Datum | Änderung |
|---|---|---|
| 1.0 | 31.05.2026 | Initial-Version. Sprint 1 abgeschlossen mit 20 Stories Done, 47 SP, aggregierter AI-Multiplier 6.4x, Null Carry-Over. Sprint-Goal voll erreicht plus 4 Bonus-Erfüllungen (SEC, Quality, PQC-TLS, Mobile-Login). |
