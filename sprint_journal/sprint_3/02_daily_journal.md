# Daily Journal: Sprint 3

**Sprint-Zeitraum:** 18.06 bis 28.06.2026 (11 Tage, komprimiert)
**Sprint-Ziel:** Am Sprint-Ende ist der Mobile-Pfad End-to-End funktional auf iPhone via Expo Go: User öffnet Profile-Screen, App etabliert eine PQ-Session zum Server (ML-KEM-768 plus HKDF), ruft `/api/profile` AES-256-GCM-verschlüsselt auf, Profile-Daten werden angezeigt. D-008 reproduzierbar.

---

> Format: kurze Notiz pro Arbeitstag am Projekt (nicht pro Kalendertag), maximal drei Sätze. Drei Fragen: Was wurde fertig? Was ist heute geplant? Welche Blocker?

---

## 2026-06-18 / 2026-06-19 (vorgezogener Arbeitstag, vor Tag 1 im Schedule)

**Gestern fertig (Planning 18.06):** Sprint-3-Planning + Sprint-2-Retro committed (User-Side). Implementation-Chat ueber Reihenfolge + Block-Session-vs-verteilte-Tage geklaert.

**Heute fertig (18./19.06 Block-Session):** Foundation komplett. CRY-4 LibOqsKem, CRY-3 Facade-KEM/HKDF/AEAD/Negotiation, CRY-7 Wire-Format-Spec docs/wire_format.md, SES-3 SessionService Redis, SES-2 derive_session_key, SES-1 POST /session/init Router, SES-4 Negotiation-Tests + Mini-Demo D-008-Vorlaeufer, CRY-6 App-Side @noble-Crypto-Module. Plus 2 Hotfix-Commits (registry.py + login.tsx, beide pre-existing Edit-Truncation aus Sprint 2).

**Heute geplant (Rest 19.06 falls Energie):** DCH-Block start (DCH-1 AES-GCM-Wrapper, S=2 SP, dann ggf. DCH-2 Header-Routing).

**Blocker / offene Fragen:** F-106 login.tsx-Hotfix als Side-Note gefixt, F-107 Sandbox-Constraint (kein npm install) als May-Polish dokumentiert. Jira-MCP-Server zwischendurch disconnected, Worklog/Transition fuer PQC-26 evtl. nachzuholen.

**Arbeitszeit:** ~4h 40min reine Story-Arbeit (Session uebersprang Mitternacht 18→19.06).

---

## 2026-06-26 (Freitag, vorgezogene Session vor Halbzeit-Check 24.06 ueberholt)

**Gestern fertig (19.06 Block-Session-Ende):** Sprint-3-Foundation done (8 Stories: CRY-4/CRY-3/CRY-7/SES-3/SES-2/SES-1/SES-4/CRY-6). DCH-Block geplant aber zeitlich nicht mehr geschafft.

**Heute fertig (26.06 Session):** DCH-Block fast komplett. DCH-1 AES-GCM-Wrapper plus `aead_random_nonce` Helper, DCH-2 FastAPI-Dependency `authenticated_session` mit Wire-Format-Konformer Header-Parsing/Decrypt/JSON-Parse-Logik plus NonceTracker-Hook fuer DCH-4, DCH-4 RedisNonceTracker mit atomarem SET NX EX plus Reihenfolge-Refactor der DCH-2-Dependency (Race-Condition aus PQC-51 geschlossen). docs/wire_format.md zweimal aktualisiert (v0.3 fuer DCH-2 Sec 5.4, v0.4 fuer DCH-4 Sec 5.5 Replay-Schutz + Trade-Off-Tabelle). NFR-Sec-2 ist mit DCH-4 erfuellt.

**Heute geplant (Rest, falls Energie):** PQC-52 DCH-3 `/api/profile` als letzter Server-Block, dann waere der Server-Pfad fuer Sprint-Goal-Demo D-008 funktional komplett.

**Blocker / offene Fragen:** Edit-Tool-Truncation hat erneut zwei Mal zugeschlagen (F-108 main.py + wire_format.md), beide via Python-Patch-Script + git-show-Restore gefixt. Memory verschaerft auf Markdown-Files explizit. Heredoc-Default-Strategie hat alle weiteren Truncations vermieden.

**Arbeitszeit:** 2h 10min reine Story-Arbeit (3 Stories: 45+40+45 Minuten). Plus ~30 Minuten Workflow-Overhead (Hotfix-Recoveries, Memory-Updates, Closing-Reviews). Reale Session-Dauer ~2.5h.

---

## 2026-06-28 (Sonntag, kurze Catch-up-Session in den Ferien)

**Gestern fertig (26.06):** DCH-Foundation komplett ausser DCH-3 (DCH-1 + DCH-2 + DCH-4). NFR-Sec-2 erfuellt. wire_format.md v0.4 mit Replay-Schutz-Sec 5.5.

**Heute fertig (28.06 Catch-up):** PQC-52 DCH-3 `/api/profile` als letzter Server-Block. Geschuetzter Endpoint mit Encrypted-Channel-Roundtrip (Decrypt-via-DCH-2-Dependency, UserRepository-Lookup, Response-Encryption mit fresh CSPRNG-Nonce + Tracker-Eintrag). wire_format.md v0.5 mit Sec 5.3 final (F-094 closed). Plus Mini-Demo D-008: 8-Schritt End-to-End-Roundtrip-Script in `server/scripts/demo_d008.py` plus Doku-File. Demo zeigt Login -> ML-KEM-Handshake -> HKDF -> Encrypted /api/profile -> Decrypt-Response -> Replay-Test 400. Lauft im Docker-Container, Mentor-Material-Quelle.

**Heute geplant (Rest, falls Energie):** APP-Stories (PQC-58 APP-5 SessionContext, dann ggf. PQC-59 APP-6 secureClient.ts). Wenn 28.06 nicht reicht, naechste Session.

**Blocker / offene Fragen:** Demo-Run hatte zwei Tooling-Stolpersteine: Dockerfile kopierte `scripts/` + `dependencies/` nicht (Hotfix-Commit df2d0fb), Git-Bash auf Windows konvertiert UNIX-Pfade (`/app/...` -> `C:/Program Files/...`) - drei Workarounds (Doppelslash, MSYS_NO_PATHCONV, relativer Pfad) in der Demo-Doku.

**Arbeitszeit:** 30 min reine Story-Arbeit fuer PQC-52, plus ~20 min fuer Demo-Script + Doku + Dockerfile-Fix. Reale Session-Dauer ~1h. In den Ferien hatte ich weniger Zeit als geplant, daher diese kuerzere Session.

---

## Sprint-Ende-Notiz 28.06.2026 (Sprint-3-Closure)

**Sprint-3-Ergebnis:** 12 von 18 Stories Done (66% von 79 SP, also 52 SP geliefert). Server-Pfad vollstaendig (PQ-Session plus Data-Channel plus geschuetzter /api/profile-Endpoint plus D-008 Mini-Demo). Mobile-Pfad nicht angegangen (4 APP-Stories offen), Integration-Tests nicht angegangen (QUA-4 plus QUA-5 offen).

**Ferien-Kontext (Transparenz):** Ich war in den Ferien vor dem Sprint-Ende und habe mir nicht so viel Zeit fuer das Schulprojekt genommen wie urspruenglich geplant. Das ist meine eigene Verantwortung, nicht externe Belastung wie in Sprint 2. Lesson fuer die naechste Projekt-Planung: Ferien als echte Ferien einplanen, ohne Projektarbeit. Die Projekt-Arbeitszeit muss rund um die Ferien-Phasen geplant werden, nicht in sie hinein.

**Carry-Over nach Sprint 4 (entschieden im Sprint-Closure):**

| Story | T-Shirt | SP | Begruendung |
|---|---|---|---|
| PQC-58 APP-5 | S | 2 | SessionContext, Voraussetzung fuer APP-6 |
| PQC-59 APP-6 | M | 5 | secureClient.ts, Voraussetzung fuer APP-3 |
| PQC-55 APP-2 | S | 2 | Home-Screen mit Logout |
| PQC-56 APP-3 | M | 5 | Profile-Screen mit /api/profile-Aufruf, Sprint-Goal-Mobile-Demo |
| PQC-66 QUA-4 | M | 5 | Integration-Tests Broker-Flow |
| PQC-67 QUA-5 | L | 8 | End-to-End-Integration-Test |

Total Carry-Over: **27 SP in 6 Stories**. Sprint 4 wird damit zum Hybrid-Sprint (Carry-Over plus Doku-Stories), R-S04 (Doku-Zeit Sprint 4 zu kurz) muss aggressiv beobachtet werden.

---

## Verweise auf Mentor-Feedback (falls vorhanden)

- 20.06.2026: Mentor-Termin geplant. Themen: Update plus D-007 Demo, Hauptfokus Abgabeform und Dokumentationsstruktur (siehe `../sprint_2/03_review.md` Sektion 7.2).

---

## Sprint-Zwischenstand (einmal pro Woche, hier mid-sprint)

> Stand der Stories aus dem Sprint Backlog. Wird am Halbzeit-Check 24.06 zum ersten Mal ausgefüllt.

### Critical Path (15 Stories, 63 SP)

| Story | Status | Anmerkung |
|---|---|---|
| PQC-24 CRY-4 | Done | LibOqsKem, registry_init hot-fixed |
| PQC-23 CRY-3 | Done | CryptoFacade KEM/HKDF/AEAD/Negotiation |
| PQC-27 CRY-7 | Done | docs/wire_format.md (230 Zeilen) |
| PQC-48 SES-3 | Done | SessionService Redis, API in PQC-46 erweitert (F-101) |
| PQC-47 SES-2 | Done | derive_session_key + F-098 Cross-Validation-Vector |
| PQC-46 SES-1 | Done | POST /session/init, 12 Tests, F-101+F-102 in-Story-resolved |
| PQC-50 DCH-1 | Done | AES-GCM-Wrapper plus aead_random_nonce-Helper, 4 dezidierte Server-Tests plus 2 App-Tests |
| PQC-51 DCH-2 | Done | FastAPI-Dependency authenticated_session, 13 Tests, Wire-Format-Spec v0.3 |
| PQC-53 DCH-4 | Done | RedisNonceTracker atomar SET NX EX, eigene DB=4, Race-Condition aus DCH-2 mitgeschlossen, Wire-Format-Spec v0.4 mit Trade-Off-Tabelle |
| PQC-52 DCH-3 | Done | POST /api/profile mit Depends(authenticated_session), Response-Encryption fresh CSPRNG-Nonce + Tracker-Eintrag, wire_format.md v0.5 (F-094 closed), Mini-Demo D-008 8-Schritte |
| PQC-26 CRY-6 | Done | App-Side @noble-Module + Jest-Setup + F-098 resolved, F-106 Hotfix |
| PQC-58 APP-5 | | |
| PQC-59 APP-6 | | |
| PQC-55 APP-2 | | |
| PQC-56 APP-3 | | |

### Defer-Kandidaten (High, 3 Stories, 16 SP)

| Story | Status | Anmerkung |
|---|---|---|
| PQC-49 SES-4 (High) | Done | Server-Logik schon in PQC-46 erfuellt, hier 2 dezidierte Tests + Doku |
| PQC-66 QUA-4 (High) | | |
| PQC-67 QUA-5 (High) | | |

---

## Zeit-Tracking pro Story (für AI-Multiplier-Auswertung)

> Pro abgeschlossener Story nach Done-Transition eintragen. Schätzungs-Mittel-h-Wert pro T-Shirt-Size: XS=1h, S=3h, M=7h, L=15h. Multiplier = Schätzung-h dividiert durch tatsächlich-h. Quelle der Konvention: `../../docs/08_scrum_setup.md` Sektion 7.4. Worklog wird zusätzlich im Jira via `addWorklogToJiraIssue` gepflegt.

| Story | T-Shirt | SP | Schätzung (h) | Tatsächlich | Multiplier | Notiz |
|---|---|---|---|---|---|---|
| PQC-24 CRY-4 | M | 5 | 7.0 | 0.75 | 9.3x | Pattern-Replikation aus LibOqsSignature (PQC-25) |
| PQC-23 CRY-3 | M | 5 | 7.0 | 0.5 | 14x | Pattern + cryptography.hazmat Standard-Lib |
| PQC-27 CRY-7 | S | 2 | 3.0 | 0.33 | 9x | Doku-Story, Wire-Format-Spec |
| PQC-48 SES-3 | M | 5 | 7.0 | 0.5 | 14x | Pattern aus OidcStateService |
| PQC-47 SES-2 | S | 2 | 3.0 | 0.5 | 6x | Helper plus Cross-Validation-Vector |
| PQC-46 SES-1 | L | 8 | 15.0 | 0.67 | 22x | Router + Audit-Roundtrip + 2 in-Story-Findings-Fixes |
| PQC-50 DCH-1 | S | 2 | 3.0 | 0.75 | 4x | Symmetrie-Fix Server aead_random_nonce + 4 DCH-1-Tests Server + 2 App |
| PQC-51 DCH-2 | M | 5 | 7.0 | 0.67 | 10.5x | Dependency-Pattern, 13 Tests, F-108 Hotfix main.py + wire_format.md, F-109 in-Story resolved |
| PQC-53 DCH-4 | M | 5 | 7.0 | 0.75 | 9.3x | RedisNonceTracker plus DCH-2-Reihenfolge-Refactor, Race-Condition geschlossen, 9 neue Tests |
| PQC-52 DCH-3 | M | 5 | 7.0 | 0.5 | 14x | /api/profile-Endpoint, 7 Tests, Hook von DCH-2 hat 80% Vorarbeit geliefert, plus Mini-Demo D-008 |
| PQC-26 CRY-6 | M | 5 | 7.0 | 1.25 | 5.6x | App-Side 7 Module + 6 Tests + Jest-Setup + F-106 Hotfix |
| PQC-58 APP-5 | S | 2 | 3.0 |  |  |  |
| PQC-59 APP-6 | M | 5 | 7.0 |  |  |  |
| PQC-55 APP-2 | S | 2 | 3.0 |  |  |  |
| PQC-56 APP-3 | M | 5 | 7.0 |  |  |  |
| PQC-49 SES-4 (High) | S | 3 | 3.0 | 0.17 | 18x | Server-Logik schon erfuellt, nur 2 Tests + Doku |
| PQC-66 QUA-4 (High) | M | 5 | 7.0 |  |  |  |
| PQC-67 QUA-5 (High) | L | 8 | 15.0 |  |  |  |

**Sprint-Aggregat (Zwischenstand nach 28.06 Catch-up-Session):**

- Done in Sprint 3 bisher: 12 Stories, 52 SP (66% von 79 SP geplant).
- Tatsaechliche Story-Zeit: ~7.34h fuer 76h Schaetzung = aggregierter Multiplier ~10.4x.
- Hypothese-Check: vor Sprint-Start war 5x bis 8x erwartet, real liegt bei ~10x weiter ueber dem oberen Limit. Hook-First-Pattern besonders sichtbar bei PQC-52 (14x): DCH-2-Dependency hat fast die ganze Arbeit gemacht.
- Bemerkung: Workflow-Overhead (Audits, Hotfixes, Edit-Truncation-Recoveries) NICHT in Story-Zeit. Reale Session-Dauer 28.06 war ~1h inklusive (kurze Catch-up-Session in den Ferien).
- **DCH-Block komplett** (DCH-1 + DCH-2 + DCH-3 + DCH-4). **Server-Pfad fuer Sprint-Goal D-008 funktional komplett**. Mini-Demo D-008 ist live (`server/scripts/demo_d008.py` im Container ausfuehrbar).
- Restscope: APP-Stories (PQC-58/59/55/56) fuer Mobile-Seite. Defer-Kandidaten QUA-4/QUA-5 noch offen.
- Wird beim Halbzeit-Check 24.06 ggf. nochmal aktualisiert (Halbzeit-Datum ist durch die vorgezogene Session ueberholt).
