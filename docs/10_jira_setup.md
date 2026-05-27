# Jira-Setup und Backlog-Transfer

**Projekt:** Implementing PQC (Semesterarbeit 3, ITCNE25)
**Autor:** Dodoe Rumiñahui Mannale
**Erstellt:** 17.05.2026
**Status:** Initial-Version (v1.0)

**Bezug:** Dokumentiert das Jira-Setup, die Mapping zwischen Markdown-IDs und Jira-Keys, sowie die nächsten Schritte (Sprint-Anlegung, Releases, Board-Konfiguration). Bezug auf `08_scrum_setup.md` Abschnitt 11.1 (Tooling) und `09_product_backlog.md`.

---

## Inhaltsverzeichnis

1. [Projekt-Übersicht](#1-projekt-übersicht)
2. [Label-Konvention](#2-label-konvention)
3. [Mapping: Markdown-IDs zu Jira-Keys](#3-mapping-markdown-ids-zu-jira-keys)
4. [Nächste Schritte (manuell in der Jira-UI)](#4-nächste-schritte-manuell-in-der-jira-ui)
5. [Versionsverlauf](#5-versionsverlauf)

---

## 1. Projekt-Übersicht

| Eigenschaft | Wert |
|---|---|
| Atlassian Cloud | rumidesigns.atlassian.net |
| Cloud ID | ccb3f99b-2a35-4948-b643-ecffd4f46bf9 |
| Projekt-Name | Implementing PQC |
| Projekt-Key | PQC |
| Projekt-Typ | Team-managed (next-gen) Scrum |
| Issue-Types verwendet | Epic, Story |
| Stand | 13 Epics und 63 Stories angelegt am 17.05.2026 via MCP |

**Jira-URL:** https://rumidesigns.atlassian.net/jira/software/projects/PQC

---

## 2. Priorisierung und Label-Konvention

Die Priorisierung der Stories erfolgt entlang von vier Achsen (MoSCoW, Sprint-Zuordnung, Stretch-Markierung, Built-in Priority Field). Konzept und Begründung dieser 4-Achsen-Logik stehen in `09_product_backlog.md` Sektion 1.3. Hier ist die Jira-spezifische Umsetzung.

Drei der Achsen werden über Labels abgebildet (MoSCoW, initiale Sprint-Zuordnung, Stretch), eine über das eingebaute Priority-Feld (Reihenfolge innerhalb Sprint). Labels statt Custom Fields, weil Custom Fields auf dem Free-Tier eingeschränkt sind.

### Priorität (MoSCoW, Achse 1)

| Label | Bedeutung |
|---|---|
| `must` | Must-Haves (Erfolgskriterium des Projekts) |
| `should` | Wichtig für Qualität, nicht blockierend |
| `could` | Stretch, nur bei vorhandenem Slack |

### Sprint-Zuordnung (Achse 2, initial)

| Label | Bedeutung |
|---|---|
| `sprint-0` | Initial in Sprint 0 geplant (Setup-Phase) |
| `sprint-1` | Initial in Sprint 1 geplant |
| `sprint-2` | Initial in Sprint 2 geplant |
| `sprint-3` | Initial in Sprint 3 geplant |
| `sprint-4` | Initial in Sprint 4 geplant |

Hinweis: Sobald Sprints in Jira als Sprint-Objekte angelegt sind, werden Stories dorthin gezogen. Die `sprint-X`-Labels dienen nur der Initial-Planung, im laufenden Betrieb ist das Sprint-Feld (Sprint-Objekt) führend.

### Stretch-Markierung (Achse 3)

| Label | Bedeutung |
|---|---|
| `sprint-stretch` | Sprint-Level-Stretch: gehört zu einem konkreten Sprint, wird aber nur bei verbleibender Kapazität nach Erfüllung des Sprint-Goals angerührt. Beispiel: APP-1, APP-4, APP-9 in Sprint 1. |
| `project-stretch` | Project-Level-Stretch: nicht für einen konkreten Sprint zugesagt, gehört zum Epic STR. |

### Built-in Priority Field (Achse 4)

Zusätzlich zu den Labels wird das in Jira eingebaute Priority-Feld pro Story gesetzt, damit innerhalb eines Sprints sofort sichtbar ist, was Critical Path ist und was nicht. Das Feld erzeugt im Board ein farbiges Icon und ist sortierbar.

| Priority | Wann gesetzt |
|---|---|
| `Highest` | Critical Path im aktuellen Sprint, Story blockiert mehrere andere im selben Sprint. Wird zuerst gearbeitet. |
| `High` | Must im aktuellen Sprint, aber nicht blockierend. Auch Defer-Kandidaten (Should im Sprint die als erste rausfliegen wenn Scope-Cut nötig). |
| `Medium` | Must in einem späteren Sprint (Sprint 2, 3 oder 4). Noch nicht aktiv. |
| `Low` | Should aus jedem Sprint. |
| `Lowest` | Could/Stretch (egal ob `sprint-stretch` oder `project-stretch`). |

**Wann wird Priority gesetzt oder angepasst:**

- Initial bei Story-Anlage: einmal beim Backlog-Transfer in Jira gesetzt.
- Beim Sprint Planning: Stories aus dem nächsten Sprint werden von `Medium` auf `Highest`/`High`/`Low`/`Lowest` umgestellt, je nach Critical-Path-Analyse.
- Beim Sprint-Refinement oder bei Scope-Anpassung: wenn eine Story als Defer-Kandidat klar wird, von `Highest`/`High` auf `Low` runtersetzen.
- Beim Sprint-Abschluss: Stories die in den nächsten Sprint übernommen werden, von `Medium` umstellen entsprechend ihrer neuen Rolle im nächsten Sprint.

**MCP-Setz-Anleitung:**

Über das Atlassian-MCP per `editJiraIssue` mit `fields: { priority: { name: "Highest" } }` (oder `"High"`, `"Medium"`, `"Low"`, `"Lowest"`). Cloud-ID, Issue-Key, gewünschter Wert. Bulk-Operationen sind möglich, indem mehrere `editJiraIssue`-Calls parallel geschickt werden.

### Typ-Markierung

| Label | Bedeutung |
|---|---|
| `epic` | Epic-Issue (zusätzlich zum Issue-Type "Epic") |

---

## 3. Mapping: Markdown-IDs zu Jira-Keys

### Epics

| Markdown-ID | Jira-Key | Titel |
|---|---|---|
| EPIC INF | PQC-2 | EPIC INF: Infrastructure und Tooling |
| EPIC SKL | PQC-3 | EPIC SKL: Skeletons |
| EPIC CRY | PQC-4 | EPIC CRY: Crypto-Abstraction-Layer |
| EPIC AUT | PQC-5 | EPIC AUT: Local Authentication |
| EPIC TOK | PQC-6 | EPIC TOK: Token Service |
| EPIC BRK | PQC-7 | EPIC BRK: Identity Broker / Federation |
| EPIC TLS | PQC-8 | EPIC TLS: Hybrid TLS Transport |
| EPIC SES | PQC-9 | EPIC SES: PQ Session |
| EPIC DCH | PQC-10 | EPIC DCH: Data Channel |
| EPIC APP | PQC-11 | EPIC APP: Mobile App UI und Integration |
| EPIC QUA | PQC-12 | EPIC QUA: Quality (Tests und Benchmarks) |
| EPIC DOC | PQC-13 | EPIC DOC: Documentation und Reporting |
| EPIC STR | PQC-14 | EPIC STR: Stretch Goals (Project-level) |
| EPIC SEC | PQC-78 | EPIC SEC: Security Infrastructure (nachträglich aus Sprint-1-Reviews) |

### Stories

| Markdown-ID | Jira-Key | Epic | Sprint |
|---|---|---|---|
| INF-1 | PQC-15 | INF | 0 |
| INF-2 | PQC-16 | INF | 0 |
| INF-3 | PQC-17 | INF | 0 |
| INF-4 | PQC-18 | INF | 0 |
| SKL-1 | PQC-19 | SKL | 1 |
| SKL-2 | PQC-20 | SKL | 1 |
| CRY-1 | PQC-21 | CRY | 1 |
| CRY-2 | PQC-22 | CRY | 1 |
| CRY-3 | PQC-23 | CRY | 3 |
| CRY-4 | PQC-24 | CRY | 3 |
| CRY-5 | PQC-25 | CRY | 1 |
| CRY-6 | PQC-26 | CRY | 3 |
| CRY-7 | PQC-27 | CRY | 3 |
| AUT-1 | PQC-28 | AUT | 1 |
| AUT-2 | PQC-29 | AUT | 1 |
| AUT-3 | PQC-30 | AUT | 1 |
| AUT-4 | PQC-31 | AUT | 1 |
| TOK-1 | PQC-32 | TOK | 1 |
| TOK-2 | PQC-33 | TOK | 1 |
| TOK-3 | PQC-34 | TOK | 4 |
| TOK-4 | PQC-35 | TOK | 4 |
| BRK-1 | PQC-36 | BRK | 2 |
| BRK-2 | PQC-37 | BRK | 2 |
| BRK-3 | PQC-38 | BRK | 2 |
| BRK-4 | PQC-39 | BRK | 2 |
| BRK-5 | PQC-40 | BRK | 2 |
| BRK-6 | PQC-41 | BRK | 2 |
| BRK-7 | PQC-42 | BRK | 2 |
| TLS-1 | PQC-43 | TLS | 2 |
| TLS-2 | PQC-44 | TLS | 2 |
| TLS-3 | PQC-45 | TLS | 2 |
| SES-1 | PQC-46 | SES | 3 |
| SES-2 | PQC-47 | SES | 3 |
| SES-3 | PQC-48 | SES | 3 |
| SES-4 | PQC-49 | SES | 3 |
| DCH-1 | PQC-50 | DCH | 3 |
| DCH-2 | PQC-51 | DCH | 3 |
| DCH-3 | PQC-52 | DCH | 3 |
| DCH-4 | PQC-53 | DCH | 3 |
| APP-1 | PQC-54 | APP | 1 (Sprint-Stretch) |
| APP-2 | PQC-55 | APP | 3 |
| APP-3 | PQC-56 | APP | 3 |
| APP-4 | PQC-57 | APP | 1 (Sprint-Stretch) |
| APP-5 | PQC-58 | APP | 3 |
| APP-6 | PQC-59 | APP | 3 |
| APP-7 | PQC-60 | APP | 2 |
| APP-8 | PQC-61 | APP | 2 |
| APP-9 | PQC-62 | APP | 1 (Sprint-Stretch) |
| QUA-1 | PQC-63 | QUA | 1 |
| QUA-2 | PQC-64 | QUA | 1 |
| QUA-3 | PQC-65 | QUA | 1 |
| QUA-4 | PQC-66 | QUA | 3 |
| QUA-5 | PQC-67 | QUA | 3 |
| QUA-6 | PQC-68 | QUA | 4 |
| QUA-7 | PQC-69 | QUA | 4 |
| QUA-8 | PQC-70 | QUA | 4 |
| DOC-1 | PQC-71 | DOC | 4 |
| DOC-2 | PQC-72 | DOC | 4 |
| DOC-3 | PQC-73 | DOC | 4 |
| DOC-4 | PQC-74 | DOC | 4 |
| STR-1 | PQC-75 | STR | Stretch |
| STR-2 | PQC-76 | STR | Stretch |
| STR-3 | PQC-77 | STR | Stretch |
| SEC-1 | PQC-79 | SEC | 2 |
| SEC-2 | PQC-80 | SEC | 2 |
| SEC-3 | PQC-81 | SEC | 2 |
| SEC-4 | PQC-82 | SEC | 2 |
| SEC-5 | PQC-83 | SEC | 2 |

**Total:** 14 Epics, 68 Stories = 82 Issues. (Initial 13 Epics plus 63 Stories am 17.05; Epic SEC mit 5 Stories nachträglich am 25.05 aus PQC-19 Closing-Review.)

---

## 4. Nächste Schritte (manuell in der Jira-UI)

Die folgenden Setup-Schritte muss der Studierende noch manuell in der Jira-UI ausführen, weil sie entweder nicht via MCP unterstützt werden oder eine bewusste Konfigurations-Entscheidung erfordern.

### 4.1 Sprint-Objekte anlegen

Im Backlog-View (`https://rumidesigns.atlassian.net/jira/software/projects/PQC/backlog`):

1. "Create Sprint" anklicken, eine Sprint anlegen pro Sprint-Plan-Eintrag:
   - Sprint 0: 06.05 bis 24.05.2026 (Abschluss heute)
   - Sprint 1: 25.05 bis 31.05.2026 (komprimiert auf 7 Tage)
   - Sprint 2: 01.06 bis 14.06.2026
   - Sprint 3: 15.06 bis 28.06.2026
   - Sprint 4: 29.06 bis 05.07.2026
2. Pro Sprint Sprint-Goal eintragen (siehe `08_scrum_setup.md` Abschnitt 8.2).
3. Stories aus dem Backlog in den entsprechenden Sprint ziehen (anhand des Labels `sprint-X`).

### 4.2 Releases / Versionen anlegen

Releases dienen als feste Meilenstein-Marker. Unter "Releases" im Projekt-Menü:

| Release-Name | Datum | Beschreibung |
|---|---|---|
| Mentor 1:1 #1 | 01.06.2026 | Erster Mentor-Termin |
| Mentor 1:1 #2 | (noch zu definieren) | Zweiter Mentor-Termin |
| Mentor 1:1 #3 | (noch zu definieren) | Dritter Mentor-Termin |
| Code-Freeze | 28.06.2026 | Ende Sprint 3, keine neuen Features mehr |
| Abgabe | 04.07.2026 | Submission-Datum |

Sobald Termin 2 und 3 fixiert sind, werden die "(noch zu definieren)"-Einträge ergänzt.

### 4.3 Board-Konfiguration

Falls die Standard-Spalten nicht passen (siehe `08_scrum_setup.md` 11.1):

1. Board-Settings → Columns.
2. Spalten konfigurieren: **To Do**, **In Progress**, **In Review**, **Done**.
3. "In Review" entspricht der Self-Demo-Phase einer Story vor dem Sprint Review.

### 4.4 Mentor-Zugriff einrichten

Sobald die Mentor-Email-Adressen verfügbar sind:

1. Project Settings → People → Add People.
2. Mentor-Adressen als "Stakeholder" oder "Customer" einladen (read-only).
3. Falls Free-Tier-Limit (3 User pro Projekt) erreicht: alternative ist ein Public-Read-Link oder Screenshots in den Mentor-Status-Dokumenten.

### 4.5 Akzeptanzkriterien-Feld (optional)

Im Free-Tier ist das Anlegen eigener Custom Fields eingeschränkt. Workaround: Akzeptanzkriterien stehen bereits in der Description jeder Story. Bei Bedarf kann das Feld "Acceptance Criteria" im Issue-Type-Layout aktiviert werden:

1. Settings (Project) → Issue Types → Story.
2. "Acceptance Criteria" aus dem rechten Panel ziehen, aktivieren.

---

## 5. Versionsverlauf

| Version | Datum | Änderung |
|---|---|---|
| 1.0 | 17.05.2026 | Initial-Version. Projekt-Übersicht, Label-Konvention, vollständige Mapping-Tabelle für 13 Epics und 63 Stories (PQC-2 bis PQC-77), nächste Setup-Schritte (Sprints, Releases, Board-Konfiguration, Mentor-Zugriff). |
| 1.1 | 27.05.2026 | Sektion 2 umstrukturiert: vier Achsen der Priorisierung (MoSCoW, Sprint, Stretch, Built-in Priority Field) mit Mapping-Tabelle und MCP-Setz-Anleitung. Epic SEC (PQC-78) plus 5 Stories SEC-1 bis SEC-5 (PQC-79 bis PQC-83) ins Mapping aufgenommen, total jetzt 14 Epics und 68 Stories. |
