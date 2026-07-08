# Sprint Review: Sprint 4

**Datum:** 08.07.2026 (Abgabetag, nach dem Kolloquium)
**Sprint-Zeitraum:** 29.06 bis 05.07.2026 (7 Kalendertage, Abgabe-Sprint), plus Nachlaeufer QUA-4/QUA-5 am 07.07
**Timebox:** 45 Minuten

**Sprint-Ziel:** "Schulprojekt-Abgabe komplett (DOC-1 bis DOC-4), Carry-Over-Rush am ersten Sprint-Tag"

---

## 1. Erreichung des Sprint-Ziels

- [x] **Vollstaendig erreicht (mit zwei ehrlichen Anmerkungen, Detail unten)**
- [ ] Teilweise erreicht
- [ ] Nicht erreicht

**Begruendung / Kontext:**

Die Planning-Strategie (Day-Marathon fuer die Carry-Over-Stories an Tag 1, bei
Misserfolg radikaler Schwenk auf Doku-Only) ist aufgegangen. Der Mobile-Pfad
ist End-to-End demonstrierbar (D-009), die Live-Demo lief am Kolloquium
(08.07, 08:30) erfolgreich. Die vier DOC-Stories werden mit der Abgabe des
Schlussberichts am 08.07 geschlossen.

**Anmerkung 1 (Zeitpunkt):** QUA-4 und QUA-5 wurden erst am 07.07 abgeschlossen,
also nach dem offiziellen Sprint-Ende. Der finale Container-Testlauf
(420 passed, 0 failed) stammt vom 07.07.

**Anmerkung 2 (Mobile-Federation):** Der Federation-Login (Google/Microsoft)
funktioniert End-to-End ueber den Browser-Pfad, liess sich in der Mobile-App
selbst aber nicht durchgaengig abschliessen. Die Luecke ist im Schlussbericht
offen benannt (Kapitel 12.1) und nicht mehr behoben worden.

---

## 2. Gelieferte Stories

| Story-Gruppe | Stories | SP | Status |
|---|---|---|---|
| Mobile-App Carry-Over (APP-5, APP-6, APP-3, APP-2) | 4 | 14 | Done (Day-Marathon Tag 1) |
| Integrations-/E2E-Tests (QUA-4, QUA-5) | 2 | 13 | Done (07.07) |
| Performance-Benchmarks (QUA-6/7/8) | 3 | 6 | Done, alle NFR-Perf-Ziele mit Marge PASS |
| Schluessel-Rotation, JWKS (TOK-3, TOK-4) | 2 | 7 | Done |
| Doku (DOC-1 Schlussbericht, DOC-2 Praesentation, DOC-3 README, DOC-4 ADRs) | 4 | 26 | DOC-2/DOC-4 fertig, DOC-1 mit Abgabe, DOC-3 bewusst reduziert (deferred, siehe unten) |

**DOC-3-Anmerkung:** Das Top-Level-README wurde durch den Schlussbericht ersetzt
(Ein-File-Entscheid am Abgabetag); die produktseitige Setup-Anleitung liegt in
`infra/README.md` und `server/README.md`. Der Ausbau zu einer vollstaendigen
Produkt-Setup-Doku ist als zurueckgestellt dokumentiert.

## 3. Demo

- D-009 (Mobile End-to-End: Login, PQ-Session, entschluesseltes Profil auf dem
  iPhone), live am Kolloquium gezeigt, dokumentiert in `demos/D-009_mobile_end_to_end.md`.

## 4. Velocity

| Metrik | Wert |
|---|---|
| Geplante Story Points (Total, inkl. Carry-Over und DOC) | 66 SP |
| Abgeschlossene Story Points | 66 SP (40 Implementation plus 26 DOC) |
| Nicht gezogen (bewusst) | Stretch STR-1/2/3 (18 SP, Could) |
