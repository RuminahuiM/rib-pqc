# Daily Journal: Sprint 1

**Sprint-Zeitraum:** 24.05 bis 31.05.2026
**Sprint-Ziel:** Am Sprint-Ende kann ich einen End-to-End-Login lokal durchspielen: Test-User wird via Admin-CLI angelegt, dann via POST `/auth/local/login` mit Email und Passwort authentifiziert, und der Server liefert einen ML-DSA-65-signierten Broker-Token zurück, der mit dem Public Key verifizierbar ist.

---

> Format: kurze Notiz pro Arbeitstag am Projekt (nicht pro Kalendertag), maximal drei Sätze. Drei Fragen: Was wurde fertig? Was ist heute geplant? Welche Blocker?

---

## 2026-05-24 (Tag 1 im Sprint, Sonntag) — retrospektiv abgeschlossen

**Tatsächlich erreicht (Sprint-Setup-Arbeit in der Strategie-Session):**

- Sprint 1 Planning vollständig ausgefüllt (`01_planning.md` plus dieses Dokument initialisiert).
- Sprint 0 in Jira formell abgeschlossen (PQC-15 und PQC-16 als Done transitioniert, Done-Comments gepostet).
- Sprint 0 Review (`../sprint_0/03_review.md`) und Retrospective (`../sprint_0/04_retrospective.md`) ausgefüllt.
- Mentor-Status-Update für Zwischengespräch 01.06 versendet (`../mentor_meetings/2026-05-24_status_update_pre_meeting_1.md`).
- Repo-Restrukturierung in `rib-pqc`-Layout abgeschlossen, push zu GitHub.

**Tatsächlich erreicht (Implementation-Session, Senior-Engineer-Modus im zweiten Chat):**

- **PQC-17 (INF-3): Docker-Compose-Skeleton mit drei Services — Done.** Alle fünf AC erfüllt, verifiziert mit `docker compose up --build` und `docker compose ps`. Drei Container `Up (healthy)`, Reverse-Proxy auf Host-Port 8080 liefert JSON vom Placeholder durch. Evidence: `evidence/PQC-17_INF-3_compose_up.md`. Jira-Done-Comment mit AC-Check, Files und Folge-Tasks gepostet.

**Bewusste Abweichungen mit Sprint-Plan-Implikation (Carry-Over für Folge-Stories):**

- nginx ist Stock `nginx:1.27-alpine` ohne TLS. Custom-Build mit oqs-provider passiert in PQC-18 (INF-4).
- auth-service ist Inline-Python-Placeholder im Compose-File ohne File in `server/`. Wird in PQC-19 (SKL-1) durch echtes FastAPI-Skeleton mit eigenem Dockerfile abgelöst. Konkreter AC-Kandidat für SKL-1 beim Refinement: Compose-Block für `auth-service` umstellen von `image` plus inline `command` zu `build: ../server`.
- PQC-19 sollte zusätzlich einen separaten `/health`-Endpoint implementieren (aktueller Placeholder antwortet auf alle Pfade gleich).

**Blocker:** Kurzzeitig: Docker Desktop war auf der User-Maschine nicht gestartet ("dockerDesktopLinuxEngine pipe not found"). Mit Start von Docker Desktop gelöst. Keine offenen Blocker.

**Arbeitszeit:**

- Strategie-Session (Sprint-Setup): nicht separat getrackt, läuft im Sprint-Review-Velocity-Block.
- Implementation-Session (PQC-17): ca. 40 Minuten inklusive Orientierung, Diskussion der Story-Optionen, Implementation, Verifikation, Evidence-Doku und Jira-Pflege.

---

## 2026-05-25 (Tag 2 im Sprint, Pfingstmontag, Zusatz-Arbeitstag) — retrospektiv abgeschlossen

**Tatsächlich erreicht (Strategie-Session am Vormittag):**

- Priorisierungs-Konvention etabliert (4 Achsen: MoSCoW, Sprint-Zuordnung, Stretch-Markierung, Built-in Priority Field), Built-in Priority Field auf alle 61 offenen Stories gesetzt (9 Highest, 7 High, 32 Medium, 7 Low, 6 Lowest). Konvention dokumentiert in `../../docs/09_product_backlog.md` Sektion 1.3 und `../../docs/10_jira_setup.md` Sektion 2.
- Evidence-File-Konvention und Zeit-Tracking-pro-Story-Konvention etabliert und in `../../docs/08_scrum_setup.md` (DoD-Erweiterung und Sektion 7.4) festgehalten.

**Tatsächlich erreicht (Implementation-Session am Nachmittag und Abend, Senior-Engineer-Modus):**

Drei Stories Done in einer Session mit Total 2h 45m User-Zeit für 12 SP, das ist Session-Multiplier ungefähr 5x.

- **PQC-19 (SKL-1): FastAPI-Skeleton mit Config-Loading — Done.** FastAPI plus structlog JSON-Logging plus pydantic-settings. Basis für alle Folge-Stories steht. Tatsächlich 1h 30m. Evidence: `evidence/PQC-19_SKL-1_fastapi_skeleton.md`.
- **PQC-21 (CRY-1): Algorithm Registry für KEM und Signature — Done.** CryptoRegistry mit Protocol-basiertem Plugin-System. Application-Code referenziert nie konkrete Algorithmen, alles über Registry. Tatsächlich 30 Min. Evidence: `evidence/PQC-21_CRY-1_algorithm_registry.md`.
- **PQC-25 (CRY-5): liboqs-python Wrapper für ML-DSA-65 — Done.** Echte PQC-Substanz läuft. liboqs 0.15.0 baut im python:3.12-slim Container in ca. 5 Min, ML-DSA-65 erzeugt korrekte FIPS-204-Sizes (Public 1952 Bytes, Secret 4032 Bytes). Tatsächlich 45 Min. Evidence: `evidence/PQC-25_CRY-5_liboqs_ml_dsa.md`.

**Major Architectural Milestones aus dieser Session:**

- Echte PQC-Substanz im Container lauffähig (PQC-25): liboqs 0.15.0 plus ML-DSA-65 mit korrekten FIPS-Sizes.
- Crypto-Agility-Layer steht (PQC-21 plus PQC-25): Plugin-System bedeutet Algorithmen austauschbar ohne Application-Code anzufassen.
- Service-Skeleton steht (PQC-19): strukturiertes Logging und Config-Loading, Basis für AUT und TOK.

**Neu im Backlog (5 SEC-Stories plus Epic, aus PQC-19 Senior-Closing-Review):**

- PQC-78 EPIC SEC: Security Infrastructure
- PQC-79 SEC-1 Request-ID Middleware (2 SP)
- PQC-80 SEC-2 CORS-Middleware (2 SP)
- PQC-81 SEC-3 TrustedHost-Middleware (1 SP)
- PQC-82 SEC-4 Security-Headers (2 SP)
- PQC-83 SEC-5 Rate-Limiting (3 SP)

Alle 5 SEC-Stories haben `blocks PQC-30 (AUT-3)` Issue-Links und Sprint-2-Label. Total 10 SP zusätzliches Sprint-2-Material. Doku-Nachzug in `../../docs/09_product_backlog.md` und `../../docs/10_jira_setup.md` siehe Tag-3-Eintrag.

**Code-Review-Findings:**

Aus zwei Senior-Closing-Reviews (PQC-19 und PQC-25) insgesamt 20 Findings. Davon 2 direkt in der Session gefixt (F-010 in PQC-21, K-3 in PQC-25), 5 als Tier-1-Jira-Stories überführt (PQC-79 bis PQC-83), 13 als Tier-2 in `../../docs/13_deferred_findings.md` mit Trigger und Status. Inline-TODOs in `main.py` (F-013), `config.py` (F-010 vor Fix), `crypto/adapters/liboqs_signature.py` (F-015).

**Process-Beobachtung (Selbstkritik aus dem Implementation-Chat):**

Bei PQC-25 wurde anfangs die Done-Transition vor dem Senior-Closing-Review gemacht. Story wurde zurück auf In Review gesetzt, Review nachgeholt, K-3 gefixt, dann erst final Done. Lesson für nächste Sessions: Story-Closing-Review-Procedure ist Phase 6 (Verifikation) plus Phase 7 (Doku), Transition erst nach beiden Phasen.

**Blocker / offene Fragen:** Keine.

**Risiko-Update durch diese Session:** R-T01 (liboqs-python Build oder Install schlägt fehl, Score 6 Active) ist durch PQC-25 mitigated. Update in `../../docs/11_risk_register.md` erfolgt am Tag 3.

**Arbeitszeit:**

- Strategie-Session (Priorisierungs-Doku): ca. 1h.
- Implementation-Session (PQC-19 plus PQC-21 plus PQC-25): 2h 45m total (90m + 30m + 45m).

---

## 2026-05-27 (Tag 3 im Sprint, Mittwoch Abend) — Halbzeit-Check

> Reminder vom SM: an diesem Tag im Daily Journal explizit prüfen, wo der Critical Path steht. Wenn INF-3, SKL-1 und CRY-1 nicht done sind: Scope-Cut-Entscheidung sofort (INF-4 streichen, SKL-2 streichen, Test-Coverage minimieren auf nur Auth-Module).

**Critical-Path-Stand (9 Highest-Stories):**

- PQC-17 (INF-3) Done am 24.05.
- PQC-19 (SKL-1) Done am 25.05.
- PQC-21 (CRY-1) Done am 25.05.
- PQC-25 (CRY-5) Done am 25.05.
- PQC-22 (CRY-2), PQC-32 (TOK-1), PQC-28 (AUT-1), PQC-29 (AUT-2), PQC-30 (AUT-3): noch offen.

4 von 9 Critical-Path-Stories Done, alle drei kritischen Foundation-Stories (INF-3, SKL-1, CRY-1) erfüllt. Der SM-Reminder zur Scope-Cut-Entscheidung trifft also nicht ein, kein Scope-Cut nötig.

**Sprint-Cumulative (Done in Sprint 1):**

| Story | SP | Done am | Tatsächlich |
|---|---|---|---|
| PQC-17 INF-3 | 5 | 24.05 | 40 Min |
| PQC-19 SKL-1 | 2 | 25.05 | 1h 30m |
| PQC-21 CRY-1 | 5 | 25.05 | 30 Min |
| PQC-25 CRY-5 | 5 | 25.05 | 45 Min |
| **Summe** | **17 SP** | | **3h 25m** |

Sprint hatte 41 SP Must geplant. 17 SP Done bedeutet 41% Sprint-Fortschritt. Restliche Arbeitstage: Sa 30.05 und So 31.05 (zwei Wochenend-Tage). Mit Sprint-Multiplier-Trend (3h 25m für Stories die klassisch 22h gekostet hätten = aggregierter Multiplier 6.4x) sind weitere 24 SP in zwei Wochenend-Tagen plausibel.

**Heute geplant (Strategie-Session, dieser Eintrag):**

Dokumentation der Implementation-Session vom 25.05, Risk Register R-T01 von Active auf Mitigated, Backlog-Markdown um Epic SEC plus 5 SEC-Stories ergänzen, Sprint-Zwischenstand und Zeit-Tracking aktualisieren.

**Blocker / offene Fragen:** Keine.

**Arbeitszeit Strategie-Session 27.05:** wird am Ende dieses Tags ergänzt.

---

## Verweise auf Mentor-Feedback (falls vorhanden)

- 24.05.2026: Erstes Status-Update versendet, siehe `../mentor_meetings/2026-05-24_status_update_pre_meeting_1.md`. Mentor-Reaktion noch ausstehend.

---

## Sprint-Zwischenstand (einmal pro Woche, hier mid-sprint)

> Stand der Stories aus dem Sprint Backlog. Wird am Halbzeit-Check 27.05 zum ersten Mal ausgefüllt.

| Story | Status | Anmerkung |
|---|---|---|
| PQC-17 INF-3 | Done (24.05) | 5 AC erfüllt, Evidence in `evidence/PQC-17_INF-3_compose_up.md`. nginx und auth-service als Stock-Placeholder, Ersatz in INF-4 und SKL-1. |
| PQC-19 SKL-1 | Done (25.05) | FastAPI plus structlog plus pydantic-settings. Evidence in `evidence/PQC-19_SKL-1_fastapi_skeleton.md`. 5 Tier-1-Findings als SEC-Stories ausgelagert (PQC-79 bis PQC-83). |
| PQC-21 CRY-1 | Done (25.05) | CryptoRegistry mit Protocol-Plugin-System für KEM und Signature. Evidence in `evidence/PQC-21_CRY-1_algorithm_registry.md`. |
| PQC-25 CRY-5 | Done (25.05) | liboqs-python ML-DSA-65. Echte FIPS-204-Sizes (1952/4032 Bytes). Evidence in `evidence/PQC-25_CRY-5_liboqs_ml_dsa.md`. R-T01 mitigated. |
| PQC-22 CRY-2 | | |
| PQC-32 TOK-1 | | |
| PQC-28 AUT-1 | | |
| PQC-29 AUT-2 | | |
| PQC-30 AUT-3 | | |
| PQC-33 TOK-2 | | |
| PQC-31 AUT-4 | | |
| PQC-63 QUA-1 | | |
| PQC-64 QUA-2 | | |
| PQC-65 QUA-3 | | |
| PQC-18 INF-4 | | |
| PQC-20 SKL-2 | | |
| PQC-54 APP-1 (Stretch) | | |
| PQC-57 APP-4 (Stretch) | | |
| PQC-62 APP-9 (Stretch) | | |

---

## Zeit-Tracking pro Story (für AI-Multiplier-Auswertung)

> Pro abgeschlossener Story nach Done-Transition eintragen. Schätzungs-Mittel-h-Wert pro T-Shirt-Size: XS=1h, S=3h, M=7h, L=15h. Multiplier = Schätzung-h dividiert durch tatsächlich-h. Quelle der Konvention: `../../docs/08_scrum_setup.md` Sektion 7.4. Worklog wird zusätzlich im Jira via `addWorklogToJiraIssue` gepflegt.

| Story | T-Shirt | SP | Schätzung (h) | Tatsächlich | Multiplier | Notiz |
|---|---|---|---|---|---|---|
| PQC-17 INF-3 | M | 5 | 7.0 | 40 Min (0.67 h) | 10.5x | Carry-Over aus Sprint 0, Spec war klar. Zwei Placeholder bewusst eingebaut (nginx Stock, auth-service inline) und nach INF-4 plus SKL-1 verschoben. Reine Compose-Datei-Erstellung plus Verifikation. Outlier nach oben, bei Stories mit tatsächlicher Crypto-Logik wird Multiplier deutlich tiefer sein. |
| PQC-19 SKL-1 | S | 2 | 3.0 | 1h 30m (1.5 h) | 2.0x | FastAPI plus structlog plus pydantic-settings Boilerplate, plus Senior-Closing-Review mit 20 Findings (5 als Jira-SEC-Stories, 13 als Tier-2 in `13_deferred_findings.md`). Review-Aufwand erklärt warum Multiplier moderater als bei PQC-17 oder PQC-21. |
| PQC-21 CRY-1 | M | 5 | 7.0 | 30 Min (0.5 h) | 14.0x | Protocol-Plugin-System ohne externe Library. Architektur war klar (Pattern bekannt), reine Code-Generierung. Outlier-Spitze, vermutlich nicht reproduzierbar bei Stories mit Crypto-Logik oder I/O-Interaktion. |
| PQC-25 CRY-5 | M | 5 | 7.0 | 45 Min (0.75 h) | 9.33x | liboqs-python Wrapper für ML-DSA-65. Dockerfile-Erweiterung plus Adapter-Code. Build-Zeit ca. 5 Min ist in den 45 Min nicht enthalten (passive Zeit). R-T01 (liboqs-Build-Risiko) mitigated. Initial K-3 als Should-Finding im Review entdeckt, in Phase 6 nachgefixt. |
| PQC-22 CRY-2 | | | | | | |
| PQC-32 TOK-1 | | | | | | |
| PQC-28 AUT-1 | | | | | | |
| PQC-29 AUT-2 | | | | | | |
| PQC-30 AUT-3 | | | | | | |
| PQC-33 TOK-2 | | | | | | |
| PQC-31 AUT-4 | | | | | | |
| PQC-63 QUA-1 | | | | | | |
| PQC-64 QUA-2 | | | | | | |
| PQC-65 QUA-3 | | | | | | |
| PQC-18 INF-4 | | | | | | |
| PQC-20 SKL-2 | | | | | | |

**Sprint-Aggregat (Zwischenstand 27.05 Mittwoch, wird beim Sprint Review final aktualisiert):**

- Done in Sprint 1 bisher: 4 Stories, 17 SP.
- Summe geschätzte Stunden (klassisch ohne AI, für die 4 Done-Stories): 7+3+7+7 = 24 h.
- Summe tatsächliche Stunden mit AI: 0.67 + 1.5 + 0.5 + 0.75 = 3.42 h (3h 25m).
- Aggregierter Sprint-Multiplier bisher: 24 / 3.42 = 7.0x.
- Aufschlüsselung nach Story-Typ:
  - Infrastructure (INF-3): 10.5x.
  - Skeleton (SKL-1): 2.0x.
  - Crypto (CRY-1, CRY-5): 14.0x, 9.33x → Mittel 11.7x für Foundation-Crypto ohne Algorithm-Verifikation.
- Beobachtung: Die hohen Multiplier sind teils auf reine Code-Generation-Stories zurückzuführen (CRY-1) und auf Carry-Over mit klarer Spec (INF-3). Bei den noch ausstehenden Stories mit echter Crypto-Interaktion (CRY-2 Crypto-Facade, AUT-3 Login-Endpoint) erwarte ich Multiplier eher im 2x bis 4x Bereich. Aggregierter Multiplier am Sprint-Ende vermutlich unter 7x.
