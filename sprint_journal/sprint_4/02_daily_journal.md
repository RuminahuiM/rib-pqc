# Daily Journal: Sprint 4

**Sprint-Zeitraum:** 29.06 bis 05.07.2026 (7 Tage, Abgabe-Sprint)
**Sprint-Ziel:** Schulprojekt-Abgabe komplett. Schlussbericht (DOC-1) plus Schluss-Präsentation (DOC-2) plus README (DOC-3) plus ADRs (DOC-4). Zusätzlich Carry-Over-Mobile-Demo D-009 falls Day-Marathon-Tag-1 erfolgreich. Doku ist unverhandelbar, Carry-Over bei Verzug radikal streichbar.

---

> Format: kurze Notiz pro Arbeitstag am Projekt (nicht pro Kalendertag), maximal drei Sätze. Drei Fragen: Was wurde fertig? Was ist heute geplant? Welche Blocker?

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
| PQC-71 DOC-1 Schlussbericht | | |
| PQC-72 DOC-2 Schluss-Präsentation | | |
| PQC-73 DOC-3 README | | |
| PQC-74 DOC-4 ADRs | | |

### Must non-blocking (Carry-Over plus Performance, 6 Stories, 18 SP)

| Story | Status | Anmerkung |
|---|---|---|
| PQC-58 APP-5 SessionContext (Carry-Over) | | |
| PQC-59 APP-6 secureClient.ts (Carry-Over) | | |
| PQC-56 APP-3 Profile-Screen (Carry-Over) | | |
| PQC-68 QUA-6 Performance PQ-Session | | |
| PQC-69 QUA-7 Performance Token-Verify | | |
| PQC-70 QUA-8 Performance AES-GCM | | |

### Defer-Kandidaten (5 Stories, 22 SP)

| Story | Status | Anmerkung |
|---|---|---|
| PQC-55 APP-2 Home-Screen (Carry-Over) | | |
| PQC-66 QUA-4 Integration-Tests Broker (Carry-Over) | | |
| PQC-67 QUA-5 End-to-End-Integration-Test (Carry-Over) | | |
| PQC-34 TOK-3 Schlüssel-Rotation | | |
| PQC-35 TOK-4 JWKS-Endpoint | | |

---

## Zeit-Tracking pro Story (für AI-Multiplier-Auswertung)

> Pro abgeschlossener Story nach Done-Transition eintragen. Schätzungs-Mittel-h-Wert pro T-Shirt-Size: XS=1h, S=3h, M=7h, L=15h. Multiplier = Schätzung-h dividiert durch tatsächlich-h. Quelle der Konvention: `../../docs/08_scrum_setup.md` Sektion 7.4. Worklog wird zusätzlich im Jira via `addWorklogToJiraIssue` gepflegt.

| Story | T-Shirt | SP | Schätzung (h) | Tatsächlich | Multiplier | Notiz |
|---|---|---|---|---|---|---|
| PQC-71 DOC-1 | L | 13 | 15.0 | | | |
| PQC-72 DOC-2 | M | 8 | 7.0 | | | |
| PQC-73 DOC-3 | S | 2 | 3.0 | | | |
| PQC-74 DOC-4 | S | 3 | 3.0 | | | |
| PQC-58 APP-5 | S | 2 | 3.0 | | | |
| PQC-59 APP-6 | M | 5 | 7.0 | | | |
| PQC-56 APP-3 | M | 5 | 7.0 | | | |
| PQC-68 QUA-6 | S | 2 | 3.0 | | | |
| PQC-69 QUA-7 | S | 2 | 3.0 | | | |
| PQC-70 QUA-8 | S | 2 | 3.0 | | | |
| PQC-55 APP-2 (Defer) | S | 2 | 3.0 | | | |
| PQC-66 QUA-4 (Defer) | M | 5 | 7.0 | | | |
| PQC-67 QUA-5 (Defer) | L | 8 | 15.0 | | | |
| PQC-34 TOK-3 (Defer) | M | 5 | 7.0 | | | |
| PQC-35 TOK-4 (Defer) | S | 2 | 3.0 | | | |

**Sprint-Aggregat (Zwischenstand, wird beim Sprint Review final aktualisiert):**

- Done in Sprint 4 bisher: 0 Stories, 0 SP.
- Hypothese: aggregierter Multiplier 8x bis 15x. Doku-Stories erwarte ich höher (Daten-Synthese aus bestehenden Quellen), Code-Carry-Over im Hook-First-Stack-Modus auch hoch.
- Wird beim Halbzeit-Check 01.07 zum ersten Mal aktualisiert.
