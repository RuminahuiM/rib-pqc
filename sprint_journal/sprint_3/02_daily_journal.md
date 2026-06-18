# Daily Journal: Sprint 3

**Sprint-Zeitraum:** 18.06 bis 28.06.2026 (11 Tage, komprimiert)
**Sprint-Ziel:** Am Sprint-Ende ist der Mobile-Pfad End-to-End funktional auf iPhone via Expo Go: User öffnet Profile-Screen, App etabliert eine PQ-Session zum Server (ML-KEM-768 plus HKDF), ruft `/api/profile` AES-256-GCM-verschlüsselt auf, Profile-Daten werden angezeigt. D-008 reproduzierbar.

---

> Format: kurze Notiz pro Arbeitstag am Projekt (nicht pro Kalendertag), maximal drei Sätze. Drei Fragen: Was wurde fertig? Was ist heute geplant? Welche Blocker?

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
| PQC-24 CRY-4 | | |
| PQC-23 CRY-3 | | |
| PQC-27 CRY-7 | | |
| PQC-48 SES-3 | | |
| PQC-47 SES-2 | | |
| PQC-46 SES-1 | | |
| PQC-50 DCH-1 | | |
| PQC-51 DCH-2 | | |
| PQC-53 DCH-4 | | |
| PQC-52 DCH-3 | | |
| PQC-26 CRY-6 | | |
| PQC-58 APP-5 | | |
| PQC-59 APP-6 | | |
| PQC-55 APP-2 | | |
| PQC-56 APP-3 | | |

### Defer-Kandidaten (High, 3 Stories, 16 SP)

| Story | Status | Anmerkung |
|---|---|---|
| PQC-49 SES-4 (High) | | |
| PQC-66 QUA-4 (High) | | |
| PQC-67 QUA-5 (High) | | |

---

## Zeit-Tracking pro Story (für AI-Multiplier-Auswertung)

> Pro abgeschlossener Story nach Done-Transition eintragen. Schätzungs-Mittel-h-Wert pro T-Shirt-Size: XS=1h, S=3h, M=7h, L=15h. Multiplier = Schätzung-h dividiert durch tatsächlich-h. Quelle der Konvention: `../../docs/08_scrum_setup.md` Sektion 7.4. Worklog wird zusätzlich im Jira via `addWorklogToJiraIssue` gepflegt.

| Story | T-Shirt | SP | Schätzung (h) | Tatsächlich | Multiplier | Notiz |
|---|---|---|---|---|---|---|
| PQC-24 CRY-4 | M | 5 | 7.0 | | | |
| PQC-23 CRY-3 | M | 5 | 7.0 | | | |
| PQC-27 CRY-7 | S | 2 | 3.0 | | | |
| PQC-48 SES-3 | M | 5 | 7.0 | | | |
| PQC-47 SES-2 | S | 2 | 3.0 | | | |
| PQC-46 SES-1 | L | 8 | 15.0 | | | |
| PQC-50 DCH-1 | S | 2 | 3.0 | | | |
| PQC-51 DCH-2 | M | 5 | 7.0 | | | |
| PQC-53 DCH-4 | M | 5 | 7.0 | | | |
| PQC-52 DCH-3 | M | 5 | 7.0 | | | |
| PQC-26 CRY-6 | M | 5 | 7.0 | | | |
| PQC-58 APP-5 | S | 2 | 3.0 | | | |
| PQC-59 APP-6 | M | 5 | 7.0 | | | |
| PQC-55 APP-2 | S | 2 | 3.0 | | | |
| PQC-56 APP-3 | M | 5 | 7.0 | | | |
| PQC-49 SES-4 (High) | S | 3 | 3.0 | | | |
| PQC-66 QUA-4 (High) | M | 5 | 7.0 | | | |
| PQC-67 QUA-5 (High) | L | 8 | 15.0 | | | |

**Sprint-Aggregat (Zwischenstand, wird beim Sprint Review final aktualisiert):**

- Done in Sprint 3 bisher: 0 Stories, 0 SP.
- Hypothese: aggregierter Multiplier 5x bis 8x für Crypto-Implementation. Sprint 2 war 13.6x im Block-Modus, Sprint 3 plane ich auf verteilte Arbeitstage.
- Wird beim Halbzeit-Check 24.06 zum ersten Mal aktualisiert.
