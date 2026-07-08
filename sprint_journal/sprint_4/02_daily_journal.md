# Daily Journal: Sprint 4

**Sprint-Zeitraum:** 29.06 bis 05.07.2026 (7 Tage, Abgabe-Sprint)
**Sprint-Ziel:** Schulprojekt-Abgabe komplett. Schlussbericht (DOC-1) plus Schluss-Präsentation (DOC-2) plus README (DOC-3) plus ADRs (DOC-4). Zusätzlich Carry-Over-Mobile-Demo D-009 falls Day-Marathon-Tag-1 erfolgreich. Doku ist unverhandelbar, Carry-Over bei Verzug radikal streichbar.

---

> Format: kurze Notiz pro Arbeitstag am Projekt (nicht pro Kalendertag), maximal drei Sätze. Drei Fragen: Was wurde fertig? Was ist heute geplant? Welche Blocker?

> Hinweis zur Transparenz: Die Eintraege ab 29.06 wurden am 08.07 (Abgabetag) nachtraeglich rekonstruiert, die Zeitwerte sind Schaetzungen ("ca."), nicht live getrackt.

---

## 2026-06-29 (Montag, Day-Marathon Tag 1: Carry-Over-Rush)

Fertig: APP-5 SessionContext, APP-6 secureClient.ts, APP-3 Profile-Screen, APP-2 Home-Screen im Hook-First-Stack; TOK-3 Schluessel-Rotation und TOK-4 JWKS-Endpoint gleich mitgezogen. Geplant war genau dieser Rush gemaess Planning-Strategie. Blocker: keine, der Server-Unterbau aus Sprint 3 stand.

## 2026-06-30 (Dienstag, Benchmarks)

Fertig: QUA-6/7/8 Performance-Benchmarks (bench_*.py, Ergebnisse in `docs/14_performance_results.md`, alle NFR-Perf-Ziele PASS mit deutlicher Marge). Geplant: Halbzeit-Check vorbereiten. Blocker: keine.

## 2026-07-01 (Mittwoch, Halbzeit-Check)

Halbzeit-Check durchgefuehrt: Carry-Over-Rush erfolgreich, DOC-1-Gliederung steht, DOC-2-Outline vorhanden, also weiter wie geplant statt Streichungs-Szenario. Mentor-Update verschickt (Update-Regel diesmal eingehalten).

## 2026-07-05 bis 2026-07-07 (Doku- und Praesentations-Block)

Fertig: DOC-2 Kolloquiums-Deck (v3) plus Demo-Runbook und QA-Vorbereitung; am 07.07 zusaetzlich QUA-4 und QUA-5 abgeschlossen (Container-Run 420 passed, nach offiziellem Sprint-Ende, ehrlich im Review vermerkt). Blocker: Zeitdruck, DOC-1-Feinschliff verschob sich auf den Abgabetag.

## 2026-07-08 (Mittwoch, Kolloquium und Abgabe)

Kolloquium 08:30 mit erfolgreicher Live-Demo (D-009). Danach DOC-1-Schlussspurt: Ein-File-Schlussbericht als Repo-README konsolidiert, Grafiken ueberarbeitet, ADRs (DOC-4) erstellt, Sprint-4-Review/Retro nachgefuehrt, Abgabe bis Mitternacht.

---

## Halbzeit-Check 01.07 (Mittwoch, kritischer Korrektur-Punkt)

> Reminder vom SM: Sprint 4 ist letzter Sprint, kein Reserve-Sprint folgt. Halbzeit-Check muss ernst genommen werden. Zu prüfen: DOC-1 in Skelett-Form? DOC-2 mit Outline? Carry-Over-Rush am 29.06 erfolgreich? Wenn DOC-1 nicht in Skelett-Form: alle Carry-Over plus QUA-Defer-Kandidaten (PQC-55, 66, 67, 34, 35) sofort streichen. Wenn DOC-2 nicht mit Outline: heute PPTX-Skelett anlegen. Wenn Sprint-3-Mobile-Demo D-009 nicht erfolgreich: R-T08-Limitation plus reduzierte Mobile-Demo im Bericht.

---

## Verweise auf Mentor-Feedback (falls vorhanden)

- 20.06.2026: Mentor-Termin durchgeführt. Demo-Struktur-Referenz auf Mitschüler-Beispiel hingewiesen. Commit-Nachvollziehbarkeits-Schwachstelle als Lesson dokumentiert. (Details in `../sprint_3/03_review.md` Sektion 7.2)
- 28.06.2026: Mentor-Update zur Sprint-3-Closure plus Carry-Over-Strategie wird zwei Tage nach Sprint-Ende nachgeholt.
- Schluss-Mentor-Termin für Feedback vor Abgabe: Termin in ersten Sprint-4-Tagen vereinbaren, idealerweise 03.07 oder 04.07 vormittags.

---

## Sprint-Zwischenstand (einmal pro Woche, hier mid-sprint)

> Stand der Stories aus dem Sprint Backlog. Wird am Halbzeit-Check 01.07 zum ersten Mal ausgefüllt.

### Critical Path (Doku-Pflicht, 4 Stories, 26 SP)

| Story | Status | Anmerkung |
|---|---|---|
| PQC-71 DOC-1 Schlussbericht | Done 08.07 | Ein-File-Schlussbericht als Repo-README (Teil A PM, Teil B Fachlich, Anhang) |
| PQC-72 DOC-2 Schluss-Präsentation | Done 08.07 | PPTX v3 plus Runbook plus QA-Doc, Kolloquium 08.07 08:30 gehalten |
| PQC-73 DOC-3 README | Done 08.07 (reduziert) | Top-Level-README durch Schlussbericht ersetzt; Produkt-Setup in infra/ und server/ READMEs; Vollausbau bewusst zurueckgestellt |
| PQC-74 DOC-4 ADRs | Done 08.07 | 6 ADRs plus Index unter `docs/adr/` |

### Must non-blocking (Carry-Over plus Performance, 6 Stories, 18 SP)

| Story | Status | Anmerkung |
|---|---|---|
| PQC-58 APP-5 SessionContext (Carry-Over) | Done 29.06 | Hook-First-Stack Tag 1 |
| PQC-59 APP-6 secureClient.ts (Carry-Over) | Done 29.06 | Auto-Encrypt/Decrypt-Wrapper |
| PQC-56 APP-3 Profile-Screen (Carry-Over) | Done 29.06 | UC-5 mobil komplett, Basis fuer D-009 |
| PQC-68 QUA-6 Performance PQ-Session | Done 30.06 | P95 4.8 ms gegen Target 500 ms |
| PQC-69 QUA-7 Performance Token-Verify | Done 30.06 | P50 0.54 ms (full) gegen Target 10 ms |
| PQC-70 QUA-8 Performance AES-GCM | Done 30.06 | AEAD-Overhead kleiner als ASGI-Overhead |

### Defer-Kandidaten (5 Stories, 22 SP)

| Story | Status | Anmerkung |
|---|---|---|
| PQC-55 APP-2 Home-Screen (Carry-Over) | Done 29.06 | Im APP-Bundle mitgezogen |
| PQC-66 QUA-4 Integration-Tests Broker (Carry-Over) | Done 07.07 | Container-Run 420 passed, Evidence `evidence/PQC-66_QUA-4_integration_tests_broker_flow.md`, Findings F-143/144/145 |
| PQC-67 QUA-5 End-to-End-Integration-Test (Carry-Over) | Done 07.07 | Evidence `evidence/PQC-67_QUA-5_end_to_end_integration_test.md`, sichert Demo-Pfad fuers Kolloquium ab |
| PQC-34 TOK-3 Schlüssel-Rotation | Done 29.06 | Mehrere kids parallel gueltig |
| PQC-35 TOK-4 JWKS-Endpoint | Done 29.06 | Public-Key-Abruf fuer Verifier |

---

## Zeit-Tracking pro Story (für AI-Multiplier-Auswertung)

> Pro abgeschlossener Story nach Done-Transition eintragen. Schätzungs-Mittel-h-Wert pro T-Shirt-Size: XS=1h, S=3h, M=7h, L=15h. Multiplier = Schätzung-h dividiert durch tatsächlich-h. Quelle der Konvention: `../../docs/08_scrum_setup.md` Sektion 7.4. Worklog wird zusätzlich im Jira via `addWorklogToJiraIssue` gepflegt.

| Story | T-Shirt | SP | Schätzung (h) | Tatsächlich | Multiplier | Notiz |
|---|---|---|---|---|---|---|
| PQC-71 DOC-1 | L | 13 | 15.0 | ca. 6 h | ca. 2.5x | Nachtraeglich geschaetzt; Synthese aus Journals/Evidence, Ein-File-Umbau am Abgabetag |
| PQC-72 DOC-2 | M | 8 | 7.0 | ca. 4 h | ca. 1.8x | Nachtraeglich geschaetzt; 3 Deck-Iterationen plus Runbook plus QA-Doc |
| PQC-73 DOC-3 | S | 2 | 3.0 | ca. 0.5 h | --- | Reduziert umgesetzt (deferred), kein Multiplier ausgewiesen |
| PQC-74 DOC-4 | S | 3 | 3.0 | ca. 0.5 h | ca. 6x | Nachtraeglich geschaetzt; Material lag in docs/03, 06 und Journals vor |
| PQC-58 APP-5 | S | 2 | 3.0 | ca. 0.5 h | ca. 6x | Nachtraeglich geschaetzt; Hook-First-Stack |
| PQC-59 APP-6 | M | 5 | 7.0 | ca. 1 h | ca. 7x | Nachtraeglich geschaetzt |
| PQC-56 APP-3 | M | 5 | 7.0 | ca. 1 h | ca. 7x | Nachtraeglich geschaetzt |
| PQC-68 QUA-6 | S | 2 | 3.0 | ca. 0.5 h | ca. 6x | Nachtraeglich geschaetzt; Skript-Pattern geteilt |
| PQC-69 QUA-7 | S | 2 | 3.0 | ca. 0.5 h | ca. 6x | Nachtraeglich geschaetzt |
| PQC-70 QUA-8 | S | 2 | 3.0 | ca. 0.5 h | ca. 6x | Nachtraeglich geschaetzt |
| PQC-55 APP-2 (Defer) | S | 2 | 3.0 | ca. 0.5 h | ca. 6x | Nachtraeglich geschaetzt; im APP-Bundle |
| PQC-66 QUA-4 (Defer-Kandidat, doch umgesetzt) | M | 5 | 7.0 | 2.5 | 2.8x | Docker-Test-Runner-Infra inkl., 3 Debug-Runden am 07.07 |
| PQC-67 QUA-5 (Defer-Kandidat, doch umgesetzt) | L | 8 | 15.0 | 1.5 | 10.0x | Tests ab erstem Container-Run gruen, Aufwand lag im Client-Nachbau |
| PQC-34 TOK-3 (Defer) | M | 5 | 7.0 | ca. 1 h | ca. 7x | Nachtraeglich geschaetzt |
| PQC-35 TOK-4 (Defer) | S | 2 | 3.0 | ca. 0.5 h | ca. 6x | Nachtraeglich geschaetzt |

**Sprint-Aggregat (final, Stand 08.07):**

- Done in Sprint 4: 15 Stories, 66 SP (40 Implementation plus 26 DOC).
- Zeitwerte grossteils nachtraeglich geschaetzt (Ausnahme QUA-4/QUA-5, live getrackt); deshalb weist der Schlussbericht fuer Sprint 4 bewusst keinen aggregierten Multiplier aus, sondern nur die zwei belastbaren Einzelwerte (QUA-4 2.8x, QUA-5 10x).
- Lesson fuer kuenftige Projekte: Zeiterfassung auch im Abgabe-Sprint live fuehren (siehe Retro Erkenntnis 3).
