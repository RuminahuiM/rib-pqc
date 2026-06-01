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

## 2026-05-30 (Tag 5 im Sprint, Samstag) — Endspurt mit Carry-Over auf 31.05 morgens

**Gestern fertig (29.05):** PQC-29 (AUT-2) Done-Transition nach User-OK (in der Doku als Status-Update nachgepflegt, keine neue Implementation).

**Tatsächlich erreicht (Endspurt-Implementation-Session 30.05, Senior-Engineer-Modus):**

Massive Endspurt-Session mit 11 Stories Done plus eine 12. Story am 31.05 morgens als Carry-Over. Sprint 1 ist damit funktional komplett.

Drei Workblöcke in dieser Session:

*Workblock 1: Auth-Vervollständigung (PQC-30 plus PQC-31)*

- **PQC-30 (AUT-3): Login-Endpoint POST /auth/local/login — Done.** 30 Min. Email-Lookup, Argon2id-Verify via PasswordHasher, Broker-Token via TokenService.issue("local"). Schließt Sprint-Goal (End-to-End Login).
- **PQC-31 (AUT-4): User-Enumeration-Schutz — Done.** 15 Min. dummy_verify war aus PQC-28 vorbereitet, deshalb sehr schnell. Quick-Win.

*Workblock 2: SEC-Bundle (PQC-79 bis PQC-83 alle in Sprint 1 statt Sprint 2)*

Der Implementation-Chat hat das komplette SEC-Bundle in Sprint 1 reingezogen, weil alle SEC-Middlewares Voraussetzung für PQC-30 (AUT-3) waren und ohnehin gebündelt umgesetzt werden konnten. Damit ist Sprint 2 stark entlastet.

- **PQC-79 (SEC-1): Request-ID Middleware mit structlog-Context — Done.** 30 Min plus Logging-Hardening-Refactor F-021/F-026/F-031/F-034 als kombinierter Pass. Zwei Verifikations-Runden wegen ContextVar-Task-Isolation-Bug (uvicorn-access-Log hatte keine request_id, fix: kein manuelles unbind).
- **PQC-80 (SEC-2): CORS-Middleware mit Allowlist — Done.** 12 Min Bundle-Anteil. Pydantic-Validator gegen Wildcard plus Credentials.
- **PQC-81 (SEC-3): TrustedHostMiddleware — Done.** 6 Min Bundle-Anteil. evil.com Live-Verifikation 400.
- **PQC-82 (SEC-4): Security-Headers-Middleware — Done.** 12 Min Bundle-Anteil. OWASP-konform, HSTS conditional auf non-dev, CSP bewusst weggelassen wegen Swagger-UI.
- **PQC-83 (SEC-5): Rate-Limiting — Done.** 45 Min. slowapi plus Redis, 5/15min Login plus 60/min Global. F-005 und F-048 resolved. F-048-Audit-Fix: Per-IP-Rate-Limit war faktisch Per-Cluster-Limit weil request.client.host hinter nginx immer Container-IP ist. uvicorn proxy_headers=True plus forwarded_allow_ips fixt das.

*Workblock 3: Quality-Schicht (PQC-63 plus PQC-64 plus PQC-65)*

- **PQC-63 (QUA-1): Pytest-Setup mit Coverage — Done.** 30 Min. conftest.py plus pytest-cov plus HTML-Coverage, 57% Sandbox-Coverage.
- **PQC-64 (QUA-2): Auth-Unit-Tests Coverage-Verifikation — Done.** 10 Min Verifikations-Story. 85% Auth-Module-Coverage gemessen (AC-4 übererfüllt).
- **PQC-65 (QUA-3): Token plus Crypto-Tests Coverage-Verifikation — Done.** 10 Min Verifikations-Story. 76 Tests gemessen plus AC plus Test-Inventory-Follow-Up-Comment.

*Workblock 4: Sprint-0-Carry-Overs (PQC-18 plus PQC-20)*

- **PQC-18 (INF-4): oqs-provider nginx — Done.** 60 Min. Multi-Stage Source-Build, X25519MLKEM768-Handshake live verifiziert (Demo D-005). Sprint-0-Carry-Over erledigt.
- **PQC-20 (SKL-2): Expo-Skeleton — Done am 31.05 morgens.** 90 Min mit ca. 30 Min Setup-Friction (Node-Upgrade, Expo-SDK-Downgrade von 56 auf 54 wegen iPhone-App-Store-Kompatibilität, ERESOLVE peer-deps). SDK 54 als FINAL für ganzes Projekt-Lebenszyklus festgelegt. Drei Stack-Routes live auf iPhone via Expo Go verifiziert.

**Major Architectural Milestones aus dieser Session:**

- Sprint-Goal End-to-End Local Login erreicht. Demo D-004 reproduzierbar.
- SEC-Schicht produktionsreif. Sprint 2 entlastet (alle 5 SEC-Stories vorgezogen).
- PQC-TLS-Handshake X25519MLKEM768 live (PQC-18 Foundation). Sprint-2-TLS-Bundle wird dadurch leichter.
- Mobile-Foundation gelegt (PQC-20). Expo SDK 54 als Projekt-Standard (iPhone-Demo-Kompatibilität, Memory persistiert in `project_pqc_expo_sdk.md`).
- Quality-Schicht formal abgeschlossen mit Coverage-Reporting.

**Demos erstellt in dieser Session:**

- D-004 Local-Login-Pipeline (Sprint-Goal-Meilenstein, reproduzierbar). Liegt in `demos/`.
- D-005 PQC-TLS-Handshake mit X25519MLKEM768 plus ML-DSA-65 Server-Cert (PQC-18). Eindrucksvolles Bericht-Material via `openssl s_client -groups X25519MLKEM768`.
- Mobile-Skeleton auf iPhone (PQC-20, drei Stack-Screens via Expo Go).

**Findings-Tracking-Stand (`../../docs/13_deferred_findings.md`):**

- Resolved-in-Story (HIGH durch Phase-1-Audit): F-048 (PQC-83) Per-IP-Rate-Limit-Bug. uvicorn proxy_headers gefixt.
- Resolved Tier-1: F-005 (Rate-Limiting-Infrastruktur fehlt) durch PQC-83 Done.
- Neu Tier-2-Polish: F-049 bis F-054 (alle Info, Tracking-Targets Sprint 4 oder vor Production). F-054 ist die Expo-SDK-54-Lock-In-Notiz.

**Hand-Off Risk Register an Co-SM-Chat:**

R-N01-Empfehlung: Expo SDK Version nicht in App Store verfügbar. Wahrscheinlichkeit HOCH, Impact NIEDRIG (Downgrade unter 5 Min, alle Features in SDK 54 verfügbar). Mitigated in PQC-20. Wird beim nächsten Risk-Register-Update aufgenommen.

**Process-Beobachtung:**

Die SEC-Stories als Bundle in einer Session umzusetzen war effizienter als pro-Story-Einzelumsetzung (Bundle-Total ca. 75 Min für 5 Stories mit 9 SP). Für die AI-Multiplier-Auswertung wichtig: Bundle-Effekt bedeutet die Einzel-Multiplier sind hoch (10x bis 15x für Bundle-Stories), aggregiert über Bundle aber realistischer.

**Blocker / offene Fragen:** Keine. Sprint-1-Closure-Termin Sprint Review am 31.05 nachmittags.

**Arbeitszeit Samstag 30.05 plus 31.05 morgens:**

- Workblock 1 (Auth-Vervollständigung): 45 Min (30+15).
- Workblock 2 (SEC-Bundle): 105 Min (30+12+6+12+45).
- Workblock 3 (Quality): 50 Min (30+10+10).
- Workblock 4 (Carry-Overs): 60 Min am 30.05 plus 90 Min am 31.05 morgens.
- **Total: 350 Min, also 5h 50m Active-Work über zwei Tage**.

---

## 2026-05-31 (Tag 6 im Sprint, Sonntag) — Stretch-Abschluss plus Sprint-Review-Tag

**Gestern Abend plus heute Morgen fertig:** PQC-20 (SKL-2) als letzte Carry-Over-Story Done. Sprint 1 funktional komplett.

**Tatsächlich erreicht (Implementation-Session 31.05 Nachmittag, App-Bundle, Senior-Engineer-Modus):**

Drei Sprint-Level-Stretch-Stories in einer kompakten Bundle-Session (50 Min Active-Work für 5 SP). Sprint 1 ist damit zu 100% komplett (alle Must plus alle drei Sprint-Stretch erledigt, kein Carry-Over für Sprint 2).

- **PQC-57 (APP-4): AuthContext — Done.** 25 Min. React Context mit `broker_token` plus `user` plus `is_authenticated` Feldern, `login(token)` plus `logout()` Methoden, expo-secure-store-Persistenz (überlappt mit PQC-62), Auto-Login mit Token-Gültigkeitscheck via jwt-decode plus `isExpired()`. Client-side JWS-Decode statt naivem "Token vorhanden = authenticated", damit kein späterer Umbau nötig wird.
- **PQC-62 (APP-9): Token-Persistenz — Done.** 10 Min Bundle-Anteil. expo-secure-store-Wrapper mit Schlüssel-Konvention `rib_pqc.<purpose>`. setItemAsync/getItemAsync/deleteItemAsync. AC-4 (Real-Phone-Test Auto-Login nach App-Neustart) ist PARTIAL wegen Dev-Mode-Limitation (siehe F-055).
- **PQC-54 (APP-1): Login-Screen — Done.** 15 Min. Drei Buttons (Email/Pass plus Google plus Microsoft als Placeholder mit Alert), Email/Pass-Form mit Email-Regex plus PW-Min-8-Validation, Fake-Login mit Dummy-Token (Sprint-1-Scope "UI only", echter Server-Call kommt in PQC-59 APP-6 secureClient). Dummy-Token mit `exp=Jan 1 2100` damit Auto-Login-Test ihn nie als expired sieht.

**Demo D-006 Mobile-Login auf iPhone:**

End-to-End Live-Verifikation auf echtem iPhone via Expo Go: App laden via QR-Scan, Loading-Spinner auf index, Redirect zu /login (kein Token in secure-store), Empty-Form-Submit zeigt Validation-Errors, gültige Inputs (`alice@example.com` plus `password123`) führen zu Loading dann push zu /home, Welcome-Message zeigt `demo-user` plus `local`, "View Profile" pusht zu /profile, "Logout" löscht Token aus secure-store und redirect zu /login. Force-Close-Test nicht zuverlässig (F-055), Mechanik via Hot-Reload verifiziert. Demo-File in `demos/D-006_mobile_login.md` (vom Implementation-Chat angelegt).

**Senior-Decisions in dieser Session:**

- Strikt sequentiell PQC-57 → PQC-62 → PQC-54 mit drei separaten Closing-Reviews (auf User-Wahl). Konsistent mit Workflow-Regel.
- Fake-Login statt Server-Call wegen Sprint-1-Scope "UI only".
- jwt-decode-Library statt naivem Token-Check.
- Zentralisierter secureStore-Wrapper mit Namespacing.
- Dummy-Token mit Far-Future-exp damit Auto-Login-Test stabil ist.

**Findings:**

- F-055 (Info, open, Sprint 4 falls TestFlight-Deploy): Auto-Login nach Force-Close von Expo Go funktioniert im Dev-Mode nicht zuverlässig. Echter Test braucht standalone .ipa-Build. Sprint-4-Material falls Demo via TestFlight, sonst Bericht-Limitation.

**Sprint-Goal-Bonus-Erfüllung:**

Die drei Stretch-Stories sind über das ursprüngliche Sprint-Goal hinaus (das nur End-to-End Local Login auf der Server-Seite verlangte). Mit dem App-Bundle ist auch die Client-Side Login-Foundation gelegt. Für Sprint 2 plus 3 können alle folgenden App-Stories (PQC-55 Home, PQC-56 Profile, PQC-58 SessionContext, PQC-59 secureClient, PQC-60 Google-Login, PQC-61 Microsoft-Login) direkt auf AuthContext plus secureStore-Wrapper aufbauen.

**Arbeitszeit 31.05 total:**

- App-Bundle Implementation: 50 Min (25+10+15).
- Doku-Pflege im Strategie-Chat (dieser Eintrag plus Risk Register Update plus Backlog-Updates): ca. 30 Min.
- Sprint-Review plus Retrospective plus Mentor-Memo: noch zu erledigen.

**Heute geplant (Sprint-Abschluss):**

Sprint Review (`03_review.md` ausfüllen), Sprint Retrospective (`04_retrospective.md`), Memorandum zum Mentor-Termin am 01.06 vorbereiten, Sprint 2 Planning-Vorbereitung.

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
| PQC-29 AUT-2 | Done (29.05) | Admin-CLI OWASP-konform. Funktional fertig 28.05, auf Done transitioniert nach User-OK. |
| PQC-30 AUT-3 | Done (30.05) | Login-Endpoint POST /auth/local/login. Email-Lookup, Argon2id-Verify, Broker-Token-Ausgabe. Sprint-Goal Demo D-004 reproduzierbar. |
| PQC-33 TOK-2 | Done (28.05) | Token-Verifikation RFC 8725 BCP, 7 Verify-Szenarien grün. F-028 als AC-6 integriert und resolved. Demo D-003 Sprint-Goal-Meilenstein. |
| PQC-31 AUT-4 | Done (30.05) | User-Enumeration-Schutz via dummy_verify. Quick-Win weil PQC-28 vorbereitet hatte. |
| PQC-63 QUA-1 | Done (30.05) | Pytest-Setup mit pytest-cov plus HTML-Coverage. 57% Sandbox. |
| PQC-64 QUA-2 | Done (30.05) | Auth-Module-Coverage 85% gemessen, AC-4 (50%) übererfüllt. Verifikations-Story. |
| PQC-65 QUA-3 | Done (30.05) | Token plus Crypto Coverage-Verifikation, 76 Tests. |
| PQC-18 INF-4 | Done (30.05) | oqs-provider nginx Multi-Stage Source-Build. X25519MLKEM768 Live-Handshake verifiziert (Demo D-005). |
| PQC-20 SKL-2 | Done (31.05 morgens) | Expo SDK 54 Skeleton. Drei Routes live auf iPhone via Expo Go. SDK 54 als FINAL für Projekt-Lebenszyklus (siehe Memory). |
| PQC-79 SEC-1 (vorgezogen) | Done (30.05) | Request-ID Middleware plus Logging-Hardening-Refactor-Bundle. |
| PQC-80 SEC-2 (vorgezogen) | Done (30.05) | CORS-Middleware mit Allowlist. |
| PQC-81 SEC-3 (vorgezogen) | Done (30.05) | TrustedHostMiddleware. |
| PQC-82 SEC-4 (vorgezogen) | Done (30.05) | Security-Headers-Middleware OWASP. |
| PQC-83 SEC-5 (vorgezogen) | Done (30.05) | Rate-Limiting slowapi plus Redis. F-048 Per-IP-Bug aus Phase-1-Audit gefixt. |
| PQC-54 APP-1 (Stretch) | Done (31.05) | Login-Screen mit Email/Pass-Form plus Google/Microsoft-Placeholders. Validation Email-Regex plus PW min 8. Fake-Login Dummy-Token (UI only). |
| PQC-57 APP-4 (Stretch) | Done (31.05) | AuthContext mit jwt-decode exp-Check, Auto-Login, expo-secure-store-Persistenz. |
| PQC-62 APP-9 (Stretch) | Done (31.05) | secureStore-Wrapper mit Namespacing `rib_pqc.<purpose>`. AC-4 PARTIAL (Force-Close-Limitation Dev-Mode, F-055). |

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
| PQC-29 AUT-2 | S | 2 | 3.0 | 30 Min (0.5 h) | 6.0x | Admin-CLI für User-Provisioning. OWASP-konform (kein --password-argv, getpass plus stdin). AC-1 Pfad-Update im Jira (auth_service.admin → admin). Done am 29.05 nach User-OK. |
| PQC-30 AUT-3 | M | 5 | 7.0 | 30 Min (0.5 h) | 14.0x | Login-Endpoint POST /auth/local/login. Reine Integration über vorhandene Pattern (UserRepository plus PasswordHasher plus TokenService). Outlier nach oben weil alle Bausteine schon standen. Sprint-Goal erreicht. |
| PQC-31 AUT-4 | XS | 1 | 1.0 | 15 Min (0.25 h) | 4.0x | User-Enumeration-Schutz via dummy_verify. Quick-Win, weil dummy_verify aus PQC-28 vorbereitet. |
| PQC-63 QUA-1 | XS | 1 | 1.0 | 30 Min (0.5 h) | 2.0x | Pytest-Setup mit conftest plus pytest-cov plus HTML-Coverage. Konfigurations-Arbeit, deshalb realistischer Multiplier. |
| PQC-64 QUA-2 | S | 2 | 3.0 | 10 Min (0.17 h) | 17.6x | Verifikations-Story (Coverage-Messung Auth-Module = 85%). Sehr wenig Aufwand weil keine neue Logik, nur Coverage-Run und Report. Outlier nach oben. |
| PQC-65 QUA-3 | S | 3 | 3.0 | 10 Min (0.17 h) | 17.6x | Verifikations-Story (Token plus Crypto Coverage). Analog PQC-64. |
| PQC-18 INF-4 | M | 5 | 7.0 | 60 Min (1.0 h) | 7.0x | oqs-provider nginx Multi-Stage Source-Build, X25519MLKEM768-Handshake live. Sprint-0-Carry-Over erledigt. Demo D-005. |
| PQC-20 SKL-2 | S | 3 | 3.0 | 90 Min (1.5 h) | 2.0x | Expo SDK 54 Skeleton mit Setup-Friction-Anteil (~30 Min für Node-Upgrade, SDK-Downgrade von 56 auf 54, ERESOLVE peer-deps). Realistischer Multiplier wegen Friction. Sprint-0-Carry-Over erledigt. |
| PQC-79 SEC-1 (vorgezogen) | S | 2 | 3.0 | 30 Min (0.5 h) | 6.0x | Request-ID Middleware plus Logging-Hardening-Refactor-Bundle (F-021/F-026/F-031/F-034). ContextVar-Bug nötig zwei Verifikations-Runden. |
| PQC-80 SEC-2 (vorgezogen) | S | 2 | 3.0 | 12 Min (0.2 h) | 15.0x | CORS-Middleware. Bundle-Anteil-Multiplier nach oben (gemeinsame Setup-Arbeit war in PQC-79 schon erledigt). |
| PQC-81 SEC-3 (vorgezogen) | XS | 1 | 1.0 | 6 Min (0.1 h) | 10.0x | TrustedHost. Bundle-Anteil. |
| PQC-82 SEC-4 (vorgezogen) | S | 2 | 3.0 | 12 Min (0.2 h) | 15.0x | Security-Headers. Bundle-Anteil. |
| PQC-83 SEC-5 (vorgezogen) | S | 3 | 3.0 | 45 Min (0.75 h) | 4.0x | Rate-Limiting slowapi plus Redis. Plus F-048-Audit-Fix für Per-IP-vs-Per-Cluster-Bug. Realistischerer Multiplier weil eigene Substanz. |
| PQC-57 APP-4 (Stretch) | S | 2 | 3.0 | 25 Min (0.42 h) | 7.2x | React AuthContext mit jwt-decode exp-Check und Auto-Login. Bundle-Anteil mit PQC-62 (gemeinsamer secureStore-Wrapper). |
| PQC-62 APP-9 (Stretch) | XS | 1 | 1.0 | 10 Min (0.17 h) | 5.9x | secureStore-Wrapper Bundle-Anteil. AC-4 PARTIAL wegen Dev-Mode-Limitation (F-055). |
| PQC-54 APP-1 (Stretch) | S | 2 | 3.0 | 15 Min (0.25 h) | 12.0x | Login-Screen. Profitiert vom AuthContext-Vorbau, deshalb hoher Multiplier. |
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

**Sprint-Aggregat (FINAL FINAL Stand 31.05 Sonntag Abend, inklusive Stretch):**

- Done in Sprint 1: **20 Stories total**. Davon 12 Sprint-1-geplant plus 2 INF-Carry-Over plus 5 SEC vorgezogen plus 3 Stretch.
- Summe Story Points: 42 SP (Must) plus 5 SP (Stretch) = **47 SP Done**.
- Sprint hatte 41 SP Must geplant plus 5 SP Stretch = 46 SP. Mit SEC-Vorziehen sind effektiv 47 SP erreicht, also über das ursprüngliche Sprint-Plus-Stretch-Budget hinaus.
- Summe geschätzte Stunden (klassisch ohne AI) für alle 20 Done-Stories: 85h (siehe vorherige Berechnung) plus 3+1+3 = 7h für die 3 Stretch-Stories = **92 h**.
- Summe tatsächliche Stunden mit AI: 13.46h plus 0.42+0.17+0.25 = 0.84h für Stretch = **14.30 h (14h 18m)**.
- **Aggregierter Sprint-Multiplier final: 92 / 14.30 = 6.43x**.
- Aufschlüsselung nach Story-Typ:
  - Infrastructure (INF-3, INF-4): 10.5x, 7.0x → Mittel 8.75x.
  - Skeleton (SKL-1, SKL-2): 2.0x, 2.0x → Mittel 2.0x (jeweils Friction-Anteil).
  - Crypto (CRY-1, CRY-5, CRY-2): 14.0x, 9.33x, 4.0x → Mittel 9.1x.
  - Token (TOK-1, TOK-2): 3.5x, 6.0x → Mittel 4.75x.
  - Auth (AUT-1, AUT-2, AUT-3, AUT-4): 7.0x, 6.0x, 14.0x, 4.0x → Mittel 7.75x.
  - Quality (QUA-1, QUA-2, QUA-3): 2.0x, 17.6x, 17.6x → Mittel 12.4x.
  - Security (SEC-1, SEC-2, SEC-3, SEC-4, SEC-5): 6.0x, 15.0x, 10.0x, 15.0x, 4.0x → Mittel 10.0x.
  - App (APP-4, APP-9, APP-1): 7.2x, 5.9x, 12.0x → Mittel 8.4x (Bundle-Effekt mit AuthContext als gemeinsamer Vorbau).

**Beobachtungen für den Sprint-1-Bericht und Mentor-Termin:**

- Hochzuverlässige Stories mit niedrigem Multiplier (2.0x bis 4.0x): die Setup-lastigen Skeleton-Stories (SKL-1, SKL-2) plus reine Konfig (QUA-1) plus PQC-83 mit Audit-Fix. Das ist konsistent mit der Beobachtung dass Setup-Friction den AI-Multiplier deckelt.
- Outlier nach oben (10x bis 18x): Verifikations-Stories (QUA-2, QUA-3) und Bundle-Stories (PQC-80/81/82, APP-1). Diese Multiplier sind nicht repräsentativ für "echte" Implementation-Arbeit, sondern reflektieren Effizienz-Effekte aus Vorarbeit oder gemeinsamer Bundle-Setup-Arbeit.
- Stabiler Mittelbereich (5x bis 8x): typisch für Stories mit echter Validation-Logik plus Tests (CRY-2, TOK-1, AUT-1, AUT-3, INF-4, APP-4).
- **Bottom Line: Der initiale Multiplier-Ansatz von 1.5x war massiv konservativ. Realistisch hat sich 6.4x ergeben. Aber diese Zahl muss mit Vorbehalt interpretiert werden: Sprint 1 hatte überdurchschnittlich viele Setup-Stories, Verifikations-Stories und Bundle-Stories. Für Sprint 2 plus 3 mit echter Crypto-Interaktion (KEM, TLS, Federation) erwarte ich realistisch 3x bis 5x.**

**Sprint-Goal-Stand FINAL FINAL:**

- Sprint-Goal "End-to-End Local Login lokal durchspielen": **erreicht und reproduzierbar in D-004**.
- Zusätzlich erreicht (Bonus): SEC-Schicht produktionsreif (5 SEC-Stories vorgezogen), Quality-Schicht formal abgeschlossen mit Coverage-Reporting (85% Auth-Module), PQC-TLS-Handshake X25519MLKEM768 live (D-005), Mobile-Login-Flow auf iPhone live mit AuthContext plus secureStore (D-006).
- **Alle drei Sprint-Stretch-Stories APP-1, APP-4, APP-9 sind Done.** Sprint 1 ist 100% komplett (alle Must plus alle Stretch).

**Carry-Over nach Sprint 2:**

**Null.** Keine offenen Sprint-1-Stories. Sprint 2 startet sauber mit BRK-Bundle plus TLS-Bundle plus Mobile-Federation-Stories (APP-Rest).

**Sprint-Goal-Stand (End-to-End-Login):**

Konkrete Restbedarf für Sprint-Goal:
- Test-User via Admin-CLI angelegt: PQC-29 (In Review, fast da).
- POST `/auth/local/login` mit Email plus Passwort: PQC-30 (AUT-3, offen, 5 SP M).
- ML-DSA-65-signierter Broker-Token zurück: PQC-32 Done.
- Verifizierbar mit Public Key: PQC-33 Done.

Sprint-Goal ist mit PQC-29-Closure plus PQC-30 vollständig erreichbar. Realistisch in 1 bis 2 verbleibenden Arbeitstagen (Sa 30.05, So 31.05).
