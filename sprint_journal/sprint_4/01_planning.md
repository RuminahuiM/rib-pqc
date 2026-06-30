# Sprint Planning: Sprint 4

**Datum:** 28.06.2026
**Sprint-Zeitraum:** 29.06 bis 05.07.2026 (7 Kalendertage, Abgabe-Sprint)
**Timebox Planning:** 1 Stunde

---

## 1. Sprint-Ziel (Warum ist dieser Sprint wertvoll?)

> Demo-orientiert formuliert.

**Sprint Goal:** Am Sprint-Ende ist die Schulprojekt-Abgabe (04 bis 05.07.2026) komplett: Schlussbericht (DOC-1), Schluss-Präsentation (DOC-2), Top-Level-README mit Setup-Anleitung (DOC-3), Architecture Decision Records (DOC-4). Zusätzlich werden die Carry-Over-Stories aus Sprint 3 (Mobile-End-to-End-Demo D-009) angegangen, primär am ersten Sprint-Tag im Day-Marathon-Modus. Wenn der Carry-Over-Rush erfolgreich ist, kommt D-009 plus die Performance-Benchmarks (QUA-6/7/8) als zusätzliches Schlussbericht-Material dazu. Wenn nicht, ist Doku absolute Priorität und die Carry-Over-Stories werden radikal gestrichen.

**Implizit dazu:**

- Schlussbericht-Manuskript ist abgabe-fertig (40 bis 60 Seiten, Bewertungs-Kriterien 1 bis 5 adressiert).
- Schluss-Präsentation als PPTX-Deck ist bereit für das Kolloquium (15 Slides, 15-20 Min).
- README plus ADRs sind committed und im Repo verlinkt.
- Mentor-Termin für Schluss-Feedback ist vor der Abgabe wahrgenommen.

**Anmerkung zur Strategie:** Sprint 4 ist der letzte Sprint vor Abgabe. R-S04 (Doku-Zeit zu kurz) ist auf Score 9 kritisch hochgestuft. Die Doku-Stories sind unverhandelbar. Carry-Over wird über Day-Marathon-Versuch am Tag 1 abgehandelt, bei Misserfolg sofort Strategie-Wechsel auf Doku-Only.

---

## 2. Ausgewählte Backlog-Items

Sprint 4 hat insgesamt **66 SP** in zwei Story-Sets: 4 Doku-Stories (26 SP) plus original-geplante Sprint-4-Stories (QUA-6/7/8 plus TOK-3/4 = 13 SP) plus 6 Carry-Over-Stories aus Sprint 3 (27 SP). Sehr ambitioniert, nur mit aggressiver Priorisierung und Defer-Bereitschaft machbar.

### Critical Path (Highest, Doku-Pflicht, 26 SP)

| Jira-Key | Story | T-Shirt | SP | Block |
|---|---|---|---|---|
| PQC-71 | DOC-1: Schlussbericht | L | 13 | Doku-Pflicht, Bewertungs-zentral |
| PQC-72 | DOC-2: Schluss-Präsentation (PPTX) | M | 8 | Doku-Pflicht, Kolloquium-Material |
| PQC-73 | DOC-3: README und Setup-Anleitung | S | 2 | Doku-Pflicht, Mentor-Setup-Test |
| PQC-74 | DOC-4: Architecture Decision Records (ADRs) | S | 3 | Doku-Pflicht laut Original-Plan |

### Must non-blocking, Carry-Over plus Performance (High, 18 SP)

| Jira-Key | Story | T-Shirt | SP | Anmerkung |
|---|---|---|---|---|
| PQC-58 | APP-5: SessionContext | S | 2 | Carry-Over Sprint 3, Voraussetzung für APP-6 |
| PQC-59 | APP-6: secureClient.ts | M | 5 | Carry-Over Sprint 3, Voraussetzung für APP-3 |
| PQC-56 | APP-3: Profile-Screen mit /api/profile | M | 5 | Carry-Over Sprint 3, Sprint-3-Goal-Mobile-Demo |
| PQC-68 | QUA-6: Performance-Benchmark PQ-Session | S | 2 | Schlussbericht-Performance-Doku |
| PQC-69 | QUA-7: Performance-Benchmark Token-Verifikation | S | 2 | Schlussbericht-Performance-Doku |
| PQC-70 | QUA-8: Performance-Benchmark AES-GCM-Overhead | S | 2 | Schlussbericht-Performance-Doku |

### Defer-Kandidaten (Medium/Low, 22 SP)

| Jira-Key | Story | T-Shirt | SP | Defer-Logik |
|---|---|---|---|---|
| PQC-55 | APP-2: Home-Screen | S | 2 | Carry-Over Sprint 3, nicht Sprint-3-Goal-blockierend |
| PQC-66 | QUA-4: Integration-Tests Broker-Flow | M | 5 | Carry-Over Sprint 3, Tests sind durch D-008 Manual-Demo teilweise gedeckt |
| PQC-67 | QUA-5: End-to-End-Integration-Test | L | 8 | Carry-Over Sprint 3, wegen R-T08 sowieso eingeschränkt automatisierbar |
| PQC-34 | TOK-3: Schlüssel-Rotation für Token-Signierung | M | 5 | Original-Sprint-4, Should-Priorität |
| PQC-35 | TOK-4: JWKS-Endpoint für Token-Verifikation | S | 2 | Original-Sprint-4, Should-Priorität |

**Sprint-Total:** 66 SP, davon 26 SP unverhandelbar (Doku), 18 SP wichtig non-blocking, 22 SP Defer-Kandidaten.

### Sprint-Level-Stretch

Keine. Defer-Kandidaten erfüllen die Stretch-Funktion implizit.

---

## 3. Cross-Cutting-Concerns-Checkliste

Aus Sprint-1-Retro plus Sprint-2-Retro plus Sprint-3-Retro Maßnahmen.

| Concern | Status | Aktion |
|---|---|---|
| Doku-Pflicht-Inhalt (Bewertungs-Kriterien 1 bis 5) | Erforderlich | DOC-1 muss alle Bewertungs-Kriterien adressieren. Skelett-Outline am Sprint-Start |
| Mentor-Termin vor Abgabe | Erforderlich | Termin in ersten Sprint-4-Tagen vereinbaren, vor 04.07 wahrnehmen |
| Schlussbericht-Anhänge (Sprint-Journale, Demos, Wire-Format-Spec, Risk-Register) | Erforderlich | Bei DOC-1-Story explizit Anhang-Liste prüfen plus Querverweise setzen |
| Reflexions-Kapitel (AI-Multiplier-Daten, Solo-Scrum-Adaption) | Erforderlich | Quellmaterial aus Sprint-Reviews/Retros plus Daily Journals zusammenführen |
| Performance-Doku im Schlussbericht | Vorhanden | QUA-6/7/8 liefern Performance-Daten. Falls Carry-Over-Rush klappt: Mobile-Demo-Performance auch messen |
| Abgabe-Logistik (Format, Repo-Zugang) | Klären beim Mentor-Termin | Format laut Mentor-20.06-Diskussion: PDF plus Repo-Link. Konkrete Anforderungen beim Schluss-Termin bestätigen |
| Commit-Nachvollziehbarkeit (Mentor-Feedback 20.06) | Lesson für nächstes Projekt | Für aktuelles Projekt nicht mehr änderbar, aber im Reflexions-Kapitel erwähnen |
| Mobile-PQC-TLS-Limitation (R-T08) | Im Bericht erwähnen | Als Plattform-Befund im Architektur-Kapitel plus Reflexion |

---

## 4. Umsetzungsplan (Arbeitstag-basiert)

Sprint-4-Zeitraum: 29.06 bis 05.07.2026 (7 Kalendertage).
Abgabe-Fenster: 04 bis 05.07.2026. Realistisch: alle Inhalte am 03.07 abend abgeschlossen, 04.07 als Polish-Tag, 05.07 als Abgabe-Tag.

Effektive Arbeitstage abhängig vom Schedule plus Energie. Geplant:

| Tag | Datum | Geplante Stories | Begründung |
|---|---|---|---|
| Tag 1 | Mo 29.06 | **Carry-Over-Rush:** APP-5 → APP-6 → APP-3 als Hook-First-Stack, ggf. APP-2 (Total: 12-14 SP) | Day-Marathon-Modus laut Top-3-Maßnahme. Sprint-3-Goal-Mobile-Demo nachholen. Sprint-2 hat gezeigt dass 13 Stories in 6h machbar sind. |
| Tag 2 | Di 30.06 | DOC-1 Skelett, DOC-2 Outline, DOC-4 ADRs-Start | Doku-Start nach Carry-Over-Rush. Wenn Tag-1-Rush gescheitert: stattdessen Doku-Vollfokus. |
| Tag 3 | Mi 01.07 | DOC-1 Hauptarbeit (Theorie, Architektur, Implementation-Sektionen). **HALBZEIT-CHECK.** | Mittwoch-Standard-Slot. Halbzeit-Check entscheidet ob noch Reserve für QUA-Benchmarks oder Carry-Over-Reste. |
| Tag 4 | Do 02.07 | DOC-1 Fortsetzung (Tests, Performance, Reflexion). DOC-2 Slides erste Hälfte. QUA-6/7/8 Benchmarks falls Zeit. | |
| Tag 5 | Fr 03.07 | DOC-1 Finalisierung. DOC-2 Slides zweite Hälfte. DOC-3 README. Schluss-Mentor-Termin falls möglich. | |
| Tag 6 | Sa 04.07 | Polish-Tag: Schlussbericht-Lesedurchgang, Präsentation-Generalprobe, DOC-3 plus DOC-4 Review, Repo-Cleanup | Abgabe-Vorbereitung |
| Tag 7 | So 05.07 | Abgabe plus eventuell letzte Polish-Items | Abgabe-Tag |

**Halbzeit-Check Mi 01.07 (kritisch):**

- DOC-1 in Skelett-Form? Ja: weiter wie geplant. Nein: alle Carry-Over plus QUA-Defer-Kandidaten sofort streichen.
- DOC-2 mit Outline? Ja: ok. Nein: PPTX-Skelett heute angehen.
- Sprint-3-Mobile-Demo D-009 erfolgreich aus Tag-1-Rush? Ja: Bonus, im Bericht erwähnen. Nein: R-T08-Limitation plus reduzierte Mobile-Demo im Bericht.

**Defer-Pfad bei Verzug am Halbzeit-Check:**

- Sofort defer: QUA-4, QUA-5 (Tests sind durch Manual-D-008-Demo teilweise gedeckt).
- Defer falls Tag 4 nicht durch: APP-2 (Home-Screen), TOK-3, TOK-4.
- Letztes-Defer-Niveau: QUA-6/7/8 als Anhang-Stub mit Hinweis "Benchmarks nicht durchgeführt, R-S04-Konsequenz".

---

## 5. Sprint-Risiken und Critical Path

**Active Risks aus dem Risk Register die in Sprint 4 direkt relevant sind:**

| Risk-ID | Titel | Score | Sprint-4-Relevanz |
|---|---|---|---|
| R-S04 | Doku-Zeit Sprint 4 zu kurz | 9 (kritisch) | Direkt relevant. 66 SP in 7 Tagen ist nur mit aggressive Defer-Bereitschaft machbar. Halbzeit-Check ist Schlüssel-Korrektur-Punkt. |
| R-S06 | Sprint-3-Komprimierung | 6 Active | Faktisch in Sprint 4 als Carry-Over-Belastung eingetreten. Day-Marathon-Tag-1 ist Mitigation. |
| R-P02 | Berufliche Belastungen HEKS | 6 Active | Falls in Sprint 4 Arbeit-Problem auftritt: Mentor-Update binnen 24-48h, Carry-Over plus alle Should-Stories sofort streichen. |
| R-T08 | Mobile-PQC-TLS-Limitation | Identifiziert | Nicht direkt in Sprint 4 lösbar, im Schlussbericht als ehrlicher Befund. |

**Critical-Path-Definition für Sprint 4:**

DOC-1 → DOC-2 → DOC-3 → DOC-4 (in dieser Reihenfolge der Bewertungs-Wichtigkeit, mit Parallelarbeit erlaubt).

Alle anderen Stories sind sekundär und können defer werden ohne dass die Abgabe scheitert.

**Sprint-Abbruch-Kriterien (Final-Sprint):**

- Nicht anwendbar. Sprint 4 ist der letzte Sprint, kein Abbruch möglich. Statt Abbruch: aggressiver Defer auf das Sprint-Goal-Minimum (DOC-1 plus DOC-2 plus DOC-3 plus DOC-4 = Abgabe ok).

---

## 6. Definition-of-Done-Check und Sprint-Anmerkungen

**Definition of Done für Sprint 4:** unverändert gegenüber Sprint 1/2/3. Bei Doku-Stories gilt zusätzlich: "Done" heisst Mentor-Review-fähig plus Bewertungs-Kriterien-deckend, nicht nur "Datei existiert".

**Plus Sprint-1-bis-3-etablierte Konventionen:**

- HARTE WORKFLOW-REGEL: Done-Transition nur nach explizitem User-OK.
- Closing-Review-Prozedur mit 7 Phasen plus Phase 8 Demo-Check (für Code-Stories).
- Bei Doku-Stories: angepasstes Closing-Review (Lesedurchgang plus Bewertungs-Kriterien-Abgleich statt Code-Audit).
- 4-Tier-Findings-Klassifikation.
- D-NNN-Demo-Konvention.
- Evidence-File pro Story plus Zeit-Tracking pro Story.

**Sprint-spezifische Anmerkungen:**

- **Carry-Over-Rush-Strategie am Tag 1.** Sprint 2 hat gezeigt dass 13 Stories in 6h im Block-Modus machbar sind. Sprint-4-Tag-1-Versuch: 4-5 Stories Mobile-Carry-Over plus eventuell QUA-Benchmarks. Klares Cut-Off nach 6-8h Arbeit, dann Strategie-Bewertung.
- **Doku-Stories sind Bewertungs-Pflicht.** DOC-1 plus DOC-2 sind nicht-verhandelbar. Wenn am Halbzeit-Check Doku nicht im Plan ist, harter Scope-Cut.
- **AI-Multiplier-Hypothese für Sprint 4.** Bei Doku-Stories erwarte ich höhere Multiplier als bei Code-Stories (Markdown-Generation plus Daten-Synthese aus Sprint-Reviews/Retros). Bei Carry-Over erwarte ich 8x-13x (Hook-First-Stack analog Sprint 3 DCH-Block).
- **Schluss-Mentor-Termin in ersten Sprint-Tagen vereinbaren.** Mentoren brauchen Vorlauf für Verfügbarkeit. Termin idealerweise am 03.07 oder 04.07 vormittags, damit Mentor-Feedback noch eingearbeitet werden kann.
- **Reflexions-Material zusammenführen.** Alle Sprint-1-bis-3-Reviews/Retros plus Daily Journals plus AI-Multiplier-Tabellen plus Risk-Register-Updates sind Quellen für das Reflexions-Kapitel. Bei DOC-1-Story explizit als Subtask einplanen.
- **Sprint 4 als letzter Sprint im Projekt.** Keine Sprint-5-Reserve. Alle Defer-Items werden nicht mehr eingeholt, sondern als Project-Limitation im Bericht erwähnt.
