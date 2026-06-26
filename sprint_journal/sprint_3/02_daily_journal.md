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

## Halbzeit-Check 24.06 (Mittwoch, nach Tag 2 der 4 Arbeitstage)

> Reminder vom SM: an diesem Tag explizit prüfen, wo der Critical Path steht. Wenn CRY-4, CRY-3, SES-3, SES-2 nicht alle Done sind: Scope-Cut-Entscheidung sofort. SES-4, QUA-4, QUA-5 nach Sprint 4 als Polish verschieben. Falls SES-1 nicht Done: APP-2 (Home-Screen) als reduzierbar markieren.

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
| PQC-50 DCH-1 | | |
| PQC-51 DCH-2 | | |
| PQC-53 DCH-4 | | |
| PQC-52 DCH-3 | | |
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
| PQC-50 DCH-1 | S | 2 | 3.0 |  |  |  |
| PQC-51 DCH-2 | M | 5 | 7.0 |  |  |  |
| PQC-53 DCH-4 | M | 5 | 7.0 |  |  |  |
| PQC-52 DCH-3 | M | 5 | 7.0 |  |  |  |
| PQC-26 CRY-6 | M | 5 | 7.0 | 1.25 | 5.6x | App-Side 7 Module + 6 Tests + Jest-Setup + F-106 Hotfix |
| PQC-58 APP-5 | S | 2 | 3.0 |  |  |  |
| PQC-59 APP-6 | M | 5 | 7.0 |  |  |  |
| PQC-55 APP-2 | S | 2 | 3.0 |  |  |  |
| PQC-56 APP-3 | M | 5 | 7.0 |  |  |  |
| PQC-49 SES-4 (High) | S | 3 | 3.0 | 0.17 | 18x | Server-Logik schon erfuellt, nur 2 Tests + Doku |
| PQC-66 QUA-4 (High) | M | 5 | 7.0 |  |  |  |
| PQC-67 QUA-5 (High) | L | 8 | 15.0 |  |  |  |

**Sprint-Aggregat (Zwischenstand nach 18./19.06 Block-Session):**

- Done in Sprint 3 bisher: 8 Stories, 35 SP (44% von 79 SP geplant).
- Tatsaechliche Story-Zeit: ~4.67h fuer 52h Schaetzung = aggregierter Multiplier ~11.1x.
- Hypothese-Check: vor Sprint-Start war 5x bis 8x erwartet, real liegt bei 11x dank Pattern-Replikation aus Sprint 1+2 + AI-Bundle-Effekt im Block-Mode.
- Bemerkung: zusaetzliche Zeit fuer Workflow-Roundtrips (Audits, Hotfixes, Disaster-Recoveries) ist NICHT in Story-Zeit eingerechnet. Reale Session-Dauer war ~6-7h inklusive.
- Wird beim Halbzeit-Check 24.06 final aktualisiert.
