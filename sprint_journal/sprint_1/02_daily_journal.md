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

**Critical-Path-Stand zum Halbzeit-Check (Vormittag, 9 Highest-Stories):**

- PQC-17 (INF-3) Done am 24.05.
- PQC-19 (SKL-1) Done am 25.05.
- PQC-21 (CRY-1) Done am 25.05.
- PQC-25 (CRY-5) Done am 25.05.
- PQC-22 (CRY-2), PQC-32 (TOK-1), PQC-28 (AUT-1), PQC-29 (AUT-2), PQC-30 (AUT-3): noch offen.

4 von 9 Critical-Path-Stories Done, alle drei kritischen Foundation-Stories (INF-3, SKL-1, CRY-1) erfüllt. Der SM-Reminder zur Scope-Cut-Entscheidung trifft also nicht ein, kein Scope-Cut nötig.

**Tatsächlich erreicht (Strategie-Session 27.05 Nachmittag):**

Dokumentation der Implementation-Session vom 25.05, Risk Register R-T01 von Active auf Mitigated, Backlog-Markdown um Epic SEC plus 5 SEC-Stories (PQC-78 plus PQC-79 bis PQC-83) erweitert, Sprint-Zwischenstand und Zeit-Tracking-Tabelle aktualisiert.

**Tatsächlich erreicht (Implementation-Session 27.05 Abend, Senior-Engineer-Modus):**

Zwei substantielle Stories in einem Mittwoch-Slot. Damit klettert der Sprint von 4 Done auf 5 Done plus 1 In Review.

- **PQC-22 (CRY-2): Crypto-Facade für sign/verify — Done.** CryptoFacade als zentrale sign/verify-Abstraktion in `server/crypto/facade.py`. Konstruktor-Validierung (signing_kid muss in verifying_keys_by_kid), KEM-Methoden als explizite NotImplementedError mit Verweis auf PQC-23. 11 Tests, 10 mit echtem ML-DSA-65-Round-Trip. F-015 in der Story selbst gelöst (enge Exception-Klausel). 4 neue Tier-2-Findings F-020 bis F-024.
- **PQC-32 (TOK-1): Broker-Token-Ausstellung mit ML-DSA-65 — In Review.** TokenService in `server/services/token_service.py` (188 Zeilen). JWS-Compact (RFC 7515) mit ML-DSA-65 (FIPS 204). TokenConfig in config.py und yaml (issuer, ttl_seconds). Singleton via Lifespan in app.state.token_service, DI gegen CryptoFacade. 14 Tests, AC-1 bis AC-5 alle in Live-Container-Demo verifiziert. Federated-Token (Google) plus Tamper-Detection live demonstriert. 5 Tier-2-Findings F-025 bis F-030, davon F-028 als Tier-1-Should der direkt in PQC-33 AC einfliesst (RFC 8725 alg-Allowlist). Wartet auf explizites User-OK für Done-Transition gemäss harter Workflow-Regel.

**Demos erstellt in dieser Session:**

- D-001 Crypto-Foundation Demo (integriert PQC-21 plus PQC-25 plus PQC-22). Nachgereicht.
- D-002 Broker-Token-Ausstellung (integriert PQC-22 plus PQC-25 plus PQC-32). Live ausgeführt.

Beide Demos liegen in `demos/` mit reproduzierbaren docker-exec-Outputs und Mentor-Hinweisen.

**Findings-Tracking-Stand (`../../docs/13_deferred_findings.md`):**

- Total 30 Findings (F-001 bis F-030).
- 5 resolved: F-010, F-015, K-3 plus F-001 bis F-005 sind als Jira-SEC-Stories überführt worden.
- 1 neuer Tier-1-Eintrag F-028: fliesst in PQC-33 (TOK-2) AC ein.

**Process-Konventionen etabliert in dieser Session (sessionsübergreifend in Memory abgelegt):**

- **HARTE WORKFLOW-REGEL** für Stories: To Do → In Progress → In Review → Done, mit explizitem User-OK vor der Done-Transition. Konsequenz aus den Premature-Done-Fehlern bei PQC-25 und PQC-22.
- **Phase 8 Demo-Check** in der Story-Closing-Review-Procedure (nach jedem Story-Done explizit prüfen ob Demo-Trigger erreicht ist).
- **Demo-Konvention (neu):** D-NNN-Marker-System mit Screenshot-Naming und Trigger-Liste (Sprint-Goal-Meilenstein, Mentor-Termin, Session-Ende). Plus F-029-Lesson: TestClient-Pattern für Lifespan-Demos, `from main import app` allein triggert Lifespan nicht.

**Process-Beobachtung (Selbstkritik aus dem Implementation-Chat):**

Auch bei PQC-22 wurde anfangs der Done-Transition-Versuch vor dem Closing-Review gemacht (gleiche Lesson wie PQC-25 in der Vor-Session). Das war der direkte Trigger die HARTE WORKFLOW-REGEL ins Memory aufzunehmen.

**Sprint-Cumulative (Stand Mittwoch Abend, ohne PQC-32):**

| Story | SP | Done am | Tatsächlich |
|---|---|---|---|
| PQC-17 INF-3 | 5 | 24.05 | 40 Min |
| PQC-19 SKL-1 | 2 | 25.05 | 1h 30m |
| PQC-21 CRY-1 | 5 | 25.05 | 30 Min |
| PQC-25 CRY-5 | 5 | 25.05 | 45 Min |
| PQC-22 CRY-2 | 3 | 27.05 | 45 Min |
| **Summe Done** | **20 SP** | | **4h 10m** |
| PQC-32 TOK-1 (In Review) | 5 | wartet auf OK | 60 Min |

20 SP Done bedeutet 49% Sprint-Fortschritt. Mit PQC-32 wären es 25 SP (61%). Restliche Arbeitstage: Sa 30.05 und So 31.05 (zwei Wochenend-Tage). Aggregierter Sprint-Multiplier bisher: 27h klassisch geschätzt für die 5 Done-Stories, 4h 10m tatsächlich = 6.5x.

**Blocker / offene Fragen:** PQC-32 wartet auf explizites User-OK für Done-Transition. Empfehlung Implementation-Chat: PQC-33 (TOK-2) als nächste Story mit F-028 als zusätzlichem AC (RFC 8725 alg-Allowlist).

**Arbeitszeit Mittwoch 27.05 total:**

- Strategie-Session (Nachmittag): ca. 1h (Doku-Pflege).
- Implementation-Session (Abend): 1h 45m (PQC-22 45m plus PQC-32 60m).
- Plus Doku-Session am Donnerstag 28.05 für 27.05-Eintrag: ca. 30 Min.

---

## 2026-05-28 (Tag 4 im Sprint, Donnerstag) — Abweichung vom Standard-Schedule

> Hinweis: Donnerstag ist laut Standard-Arbeitsrhythmus kein Projekt-Tag. Diese Session ist eine bewusste Ausnahme (Donnerstag-Lang-Slot, Abend bis spät), motiviert durch den nahenden Sprint-Endtermin am 30.05 und die Möglichkeit den Sprint-Goal (End-to-End-Login) noch zu erreichen.

**Gestern fertig (27.05):** PQC-22 (CRY-2) Done, PQC-32 (TOK-1) funktional fertig und In Review.

**Tatsächlich erreicht (Implementation-Session 28.05 Abend, Senior-Engineer-Modus):**

Vier Stories in einer Langen Session. Eine davon (PQC-32) war seit gestern In Review und wartete auf das User-OK. Heute auf Done transitioniert nach explizitem OK. Drei weitere Stories neu implementiert.

- **PQC-32 (TOK-1): Broker-Token-Ausstellung — Done.** Heute auf Done transitioniert nach explizitem User-OK gemäss harter Workflow-Regel. 60 Min Implementation-Zeit am 27.05 plus weitere 60 Min am 28.05 für Senior-Decisions, Live-Verifikation und Closing-Review-Diskussion. Total 2h User-Zeit auf der Story.
- **PQC-33 (TOK-2): Broker-Token-Verifikation (RFC 8725 BCP) — Done.** RFC 8725 BCP konform: alg-Allowlist case-insensitive, none-Block, 30s exp-Leeway. Live-Container 7 Verify-Szenarien grün. F-028 aus PQC-32-Review als AC-6 integriert und in dieser Story resolved. 30 Min Implementation. Demo D-003 (Broker-Token Verify-Pipeline) als Sprint-Goal-Meilenstein erstellt.
- **PQC-28 (AUT-1): User-Store SQLAlchemy 2.0 plus Argon2id — Done.** SQLAlchemy 2.0 async plus aiosqlite plus Alembic-Migrations. Auto-Migration im Container-CMD (idempotent). User-Model mit lowercase email und nullable password_hash. Argon2id mit OWASP-konformen Defaults (m=64MB/t=3/p=4). Live-Verify gegen echten Container. 60 Min Implementation.
- **PQC-29 (AUT-2): Admin-CLI für User-Provisioning — In Review.** OWASP-konform: getpass-Prompt default, --password-stdin für Scripting, kein --password als argv (verhindert Shell-History, ps-Leak und Container-Log-Leak). 30 Min Implementation. Wartet auf explizites User-OK für Done-Transition.

**Major Architectural Milestones aus dieser Session:**

- Broker-Token-Pipeline funktional vollständig: JWS-Compact mit ML-DSA-65, RFC 8725 BCP konform, 7 Verify-Szenarien grün im Live-Container. Sprint-Goal in Sichtweite.
- Persistenz-Schicht eingeführt (PQC-28): SQLAlchemy 2.0 async, aiosqlite, Alembic-Migrations mit Auto-Migration im Container-CMD.
- Argon2id mit OWASP-konformen Defaults: m=64MB, t=3, p=4. Live-Verifikation funktioniert.
- Admin-CLI OWASP-konform für Credential-Handling (kein --password-argv).

**Demos in dieser Session:**

- D-002 wiederholt (Sprint-Goal-Bestätigung).
- D-003 Broker-Token Verify-Pipeline (Sprint-Goal-Meilenstein, integriert PQC-22 plus PQC-32 plus PQC-33). Liegt in `demos/`.
- Geplant nach AUT-3 plus AUT-4: D-004 Local Login Pipeline.

**Bewusste Spec-Updates in Jira (mit Begründung):**

- PQC-33 AC-6 ergänzt: RFC 8725 BCP alg-Allowlist. Direkt aus F-028 PQC-32-Review eingeflossen.
- PQC-29 AC-1 Pfad-Update: `auth_service.admin` → `admin`, weil die Server-Struktur flach ist (kein auth_service-Subpackage). Jira-Description entsprechend angepasst.

**Findings-Tracking-Stand (`../../docs/13_deferred_findings.md`):**

- Total 42 Findings (F-001 bis F-042). Heute neu:
  - PQC-32 Review: F-025 bis F-030 (6 neue, F-028 als Tier-1 in PQC-33 integriert).
  - PQC-33 Review: F-031 bis F-033 (3 neue, F-028 resolved).
  - PQC-28 Review: F-034 bis F-039 (5 neue, F-036 als Duplikat von F-012 entfallen).
  - PQC-29 Review: F-040 bis F-042 (3 neue, alle Info-Polish).
- Bundle-Vorschläge für nächste Sessions:
  - Logging-Hardening-Bundle (vor PQC-30 angehen): F-021, F-026, F-031, F-034.
  - Sprint-3-Polish-Bundle: F-027, F-032, F-033, F-039 (Pepper), F-040, F-041, F-042.

**Code-Stats heute:**

- 4 neue Production-Module: `services/token_service.py` (388 Zeilen final), `models/user.py`, `db/engine.py`, `db/repositories/user_repository.py`, `auth/password.py`, `admin.py`.
- 5 neue Config-Felder: `token.allowed_algs`, `token.exp_leeway_seconds`, plus komplette Argon2Config und DatabaseConfig.
- 1 Alembic-Migration (initial users table).
- Ca. 120 neue Tests. Total Sandbox-Stand: 65 passed plus 3 skipped (liboqs).

**Blocker / offene Fragen:**

- PQC-29 wartet auf explizites User-OK für Done-Transition.
- Atlassian-MCP in dieser Session disconnected: Worklogs für PQC-33, PQC-28, PQC-29 und Done-Comments stehen aus, müssen beim nächsten Connect nachgepflegt werden.

**Arbeitszeit Donnerstag 28.05 total:**

- Implementation- und Closing-Review-Arbeit (Abend bis spät): 3h total (PQC-32 Closing-Review 60m plus PQC-33 30m plus PQC-28 60m plus PQC-29 30m).
- Doku-Pflege im Strategie-Chat (dieser Eintrag): ca. 20 Min.

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
| PQC-22 CRY-2 | Done (27.05) | CryptoFacade sign/verify mit ML-DSA-65, 11 Tests, 10 Round-Trip. Evidence: `evidence/PQC-22_CRY-2_crypto_facade.md` (falls vom Implementation-Chat angelegt). F-015 in Story gefixt, 4 neue Tier-2-Findings F-020 bis F-024. |
| PQC-32 TOK-1 | Done (28.05) | TokenService 388 Zeilen final, JWS-Compact mit ML-DSA-65, 14 Tests, Live-Container-Demo (D-002). Funktional fertig am 27.05, auf Done transitioniert am 28.05 nach User-OK. |
| PQC-28 AUT-1 | Done (28.05) | SQLAlchemy 2.0 async plus aiosqlite plus Alembic. User-Model, Argon2id (m=64MB/t=3/p=4 OWASP). Auto-Migration im Container-CMD. |
| PQC-29 AUT-2 | In Review (28.05) | Admin-CLI OWASP-konform (getpass plus --password-stdin, kein --password-argv). Wartet auf explizites User-OK. |
| PQC-30 AUT-3 | | |
| PQC-33 TOK-2 | Done (28.05) | Token-Verifikation RFC 8725 BCP, 7 Verify-Szenarien grün. F-028 als AC-6 integriert und resolved. Demo D-003 Sprint-Goal-Meilenstein. |
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
| PQC-22 CRY-2 | S | 3 | 3.0 | 45 Min (0.75 h) | 4.0x | CryptoFacade sign/verify. Klare Abhängigkeit von PQC-21 und PQC-25 die schon standen. F-015 (enge Exception-Klausel) in der Story gefixt, plus 4 Tier-2-Findings F-020 bis F-024. Closing-Review verlief sauber, einziger Bruch in der Prozedur: Done-Transition zuerst versucht bevor Review komplett war (gleicher Fehler wie PQC-25, triggerte die HARTE WORKFLOW-REGEL ins Memory). |
| PQC-32 TOK-1 | M | 5 | 7.0 | 2h (1h Impl 27.05 + 1h Closing-Review 28.05) | 3.5x | TokenService mit JWS-Compact und ML-DSA-65 (FIPS 204). 388 Zeilen final (nach PQC-33-Verify-Integration), 14 Tests, Live-Container-Demo (D-002 mit Federated Google Token plus Tamper-Detection). Closing-Review-Aufwand erklärt warum Multiplier unter den anderen Token-Stories liegt, das ist der erste echte Datenpunkt zum Closing-Review-Anteil pro Story. |
| PQC-33 TOK-2 | S | 2 | 3.0 | 30 Min (0.5 h) | 6.0x | Broker-Token-Verifikation, RFC 8725 BCP konform (alg-Allowlist case-insensitive, none-Block, 30s exp-Leeway). 7 Verify-Szenarien grün im Live-Container. F-028 als AC-6 in dieser Story integriert und resolved. Demo D-003 als Sprint-Goal-Meilenstein. |
| PQC-28 AUT-1 | M | 5 | 7.0 | 60 Min (1.0 h) | 7.0x | SQLAlchemy 2.0 async, aiosqlite, Alembic-Migrations mit Auto-Migration. User-Model, Argon2id OWASP-Defaults. Erste Story mit DB-Persistenz, deshalb erwartungsgemäss höherer Aufwand. Trotz neuer Schicht-Einführung kein Multiplier-Knick weil Foundation-Pattern (Repository, async-Engine) bekannt sind. |
| PQC-29 AUT-2 | S | 2 | 3.0 | 30 Min (0.5 h) | 6.0x | Admin-CLI für User-Provisioning. OWASP-konform (kein --password-argv, getpass plus stdin). AC-1 Pfad-Update im Jira (auth_service.admin → admin) wegen flacher Server-Struktur. Status In Review, wartet auf User-OK. |
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

**Sprint-Aggregat (Zwischenstand 28.05 Donnerstag Abend, korrigiert nach Jira-Worklog-Verifikation 29.05):**

- Done in Sprint 1 bisher: 8 Stories, 32 SP. Plus 1 In Review (PQC-29 AUT-2, 2 SP).
- Summe geschätzte Stunden (klassisch ohne AI, für die 8 Done-Stories): 7+3+7+7+3+7+3+7 = 44 h.
- Summe tatsächliche Stunden mit AI für Done-Stories: 0.67 + 1.5 + 0.5 + 0.75 + 0.75 + 2.0 + 0.5 + 1.0 = 7.67 h (7h 40m).
- Aggregierter Sprint-Multiplier bisher (nur Done-Stories): 44 / 7.67 = **5.74x**.
- Falls PQC-29 mit gerechnet wird (S=3h, 0.5h tatsächlich): 47 / 8.17 = **5.75x**.
- Sprint-Fortschritt: 32 SP von 41 SP geplanten Must-Stories = **78% Done**. Mit PQC-29 In Review: 83%.
- Aufschlüsselung nach Story-Typ:
  - Infrastructure (INF-3): 10.5x.
  - Skeleton (SKL-1): 2.0x.
  - Crypto (CRY-1, CRY-5, CRY-2): 14.0x, 9.33x, 4.0x → Mittel 9.1x für Foundation-Crypto.
  - Token (TOK-1, TOK-2): 3.5x, 6.0x → Mittel 4.75x für Token-Services.
  - Auth (AUT-1): 7.0x. AUT-2 (In Review) 6.0x.
- Beobachtung Stand Tag 4: Korrektur nach Jira-Verifikation zeigt einen wichtigen Daten-Punkt: PQC-32 hat tatsächlich 2h gekostet (1h Implementation plus 1h Closing-Review-Arbeit am nächsten Tag). Damit liegt der TOK-1-Multiplier bei 3.5x statt 7.0x. Das ist konsistent mit der Beobachtung dass je nach Erfassungs-Granularität (nur Coding-Zeit vs Coding-plus-Review-Zeit) der Multiplier deutlich variiert. Für die finale Auswertung im Schlussbericht wichtig: konsistent Coding-plus-Review-Zeit erfassen.
- Erwartung Sprint-Ende: aggregierter Multiplier um 5x bis 6x, deutlich höher als initial angenommen (1.5x), aber tiefer als das vorläufige 6.6x das vor der PQC-32-Korrektur stand.

**Sprint-Goal-Stand (End-to-End-Login):**

Konkrete Restbedarf für Sprint-Goal:
- Test-User via Admin-CLI angelegt: PQC-29 (In Review, fast da).
- POST `/auth/local/login` mit Email plus Passwort: PQC-30 (AUT-3, offen, 5 SP M).
- ML-DSA-65-signierter Broker-Token zurück: PQC-32 Done.
- Verifizierbar mit Public Key: PQC-33 Done.

Sprint-Goal ist mit PQC-29-Closure plus PQC-30 vollständig erreichbar. Realistisch in 1 bis 2 verbleibenden Arbeitstagen (Sa 30.05, So 31.05).
