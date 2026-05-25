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

## 2026-05-25 (Tag 2 im Sprint, Pfingstmontag, Zusatz-Arbeitstag)

**Gestern fertig:** PQC-17 INF-3 Done (Docker-Compose-Skeleton, ca. 40 Min Implementation), plus Sprint-Setup-Arbeit (Sprint 1 Planning, Sprint 0 Closing in Jira, Mentor-Update versendet, Repo-Restrukturierung).

**Heute geplant:**

- Strategie-Session (heute Vormittag, schon erledigt): Priorisierungs-Konvention etabliert (4 Achsen: MoSCoW, Sprint-Zuordnung, Stretch-Markierung, Built-in Priority Field), Built-in Priority Field auf alle 61 offenen Stories gesetzt (9 Highest, 7 High, 32 Medium, 7 Low, 6 Lowest). Konvention dokumentiert in `../../docs/09_product_backlog.md` Sektion 1.3 (Konzept) und `../../docs/10_jira_setup.md` Sektion 2 (Jira-Umsetzung).
- Implementation-Session (später heute): PQC-19 (SKL-1) FastAPI-Skeleton mit Config-Loading. Schließt den auth-service-Placeholder-Loop aus PQC-17 und gibt Basis für alle weiteren AUT/TOK/BRK-Stories. Alternative wenn Parallelität gewünscht: PQC-21 (CRY-1) Algorithm Registry, HTTP-unabhängig.

**Blocker / offene Fragen:** Keine.

**Arbeitszeit:** Strategie-Session ca. 1h. Implementation-Zeit wird nach Tagesende ergänzt.

---

## Halbzeit-Check 27.05 (Tag 3 von 5 Arbeitstagen, Mittwoch Abend)

> Reminder vom SM: an diesem Tag im Daily Journal explizit prüfen, wo der Critical Path steht. Wenn INF-3, SKL-1 und CRY-1 nicht done sind: Scope-Cut-Entscheidung sofort (INF-4 streichen, SKL-2 streichen, Test-Coverage minimieren auf nur Auth-Module).

---

## Verweise auf Mentor-Feedback (falls vorhanden)

- 24.05.2026: Erstes Status-Update versendet, siehe `../mentor_meetings/2026-05-24_status_update_pre_meeting_1.md`. Mentor-Reaktion noch ausstehend.

---

## Sprint-Zwischenstand (einmal pro Woche, hier mid-sprint)

> Stand der Stories aus dem Sprint Backlog. Wird am Halbzeit-Check 27.05 zum ersten Mal ausgefüllt.

| Story | Status | Anmerkung |
|---|---|---|
| PQC-17 INF-3 | Done (24.05) | 5 AC erfüllt, Evidence in `evidence/PQC-17_INF-3_compose_up.md`. nginx und auth-service als Stock-Placeholder, Ersatz in INF-4 und SKL-1. |
| PQC-19 SKL-1 | | |
| PQC-21 CRY-1 | | |
| PQC-25 CRY-5 | | |
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
| PQC-19 SKL-1 | | | | | | |
| PQC-21 CRY-1 | | | | | | |
| PQC-25 CRY-5 | | | | | | |
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

**Sprint-Aggregat (wird im Sprint Review berechnet):**

- Summe geschätzte Stunden (Must, ohne Stretch): TBD beim Sprint Review.
- Summe tatsächliche Stunden: TBD.
- Sprint-Multiplier (Summe Schätzung / Summe Tatsächlich): TBD.
- Aufschlüsselung nach Story-Typ (Infrastructure / Crypto / Auth / Token / Quality): TBD.
