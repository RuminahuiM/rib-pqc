# Sprint Review: Sprint 0

**Datum:** 24.05.2026
**Sprint-Zeitraum:** 06.05 bis 24.05.2026 (19 Tage, davon ~10 Stunden effektive Arbeit)
**Timebox:** 1 Stunde

**Sprint-Ziel:** "Scope, Architektur und Tooling-Basis ready"

---

## 1. Erreichung des Sprint-Ziels

- [ ] Vollständig erreicht
- [x] **Teilweise erreicht (Detail unten)**
- [ ] Nicht erreicht

**Begründung / Kontext:**

Scope und Architektur sind vollständig erreicht: Architektur-Entscheidung (Option 2 plus Identity Broker) ist fundiert dokumentiert, Requirements vollständig, Design mit Komponenten-, Deployment- und Sequenz-Diagrammen ist fertig, Tech-Stack-Entscheidungen sind nachvollziehbar begründet.

Konzeptioneller Sprint-Plan ist ebenfalls deutlich über das Sprint-Goal hinaus erreicht: Scrum-Setup mit Solo-Adaption, Product Backlog mit 63 Stories und 13 Epics, Risk Register mit 19 Risiken, Traceability-Matrix, Sprint-Journal-Templates, Jira-Projekt mit 76 Issues sind alle vollständig.

Die Tooling-Basis ist nur teilweise erreicht: Jira-Projekt (INF-1) ist vollständig fertig. GitHub-Repository (INF-2) existiert aber muss noch komplett aufgesetzt werden (Ordner syncen, Mentor-Access teilen, Mentoren informieren). Docker-Compose-Skeleton (INF-3) und oqs-provider-fähiges nginx-Image (INF-4) sind noch nicht angefangen.

---

## 2. Increment-Demo und Story-Prüfung

### Story PQC-15 (INF-1): Jira-Projekt aufsetzen

**Akzeptanzkriterien:**

- [x] AC-1: Jira Cloud Free Workspace existiert mit Team-managed Scrum-Template. → erfüllt
- [x] AC-2: Projekt-Key ist PQC, Workflow mit Standard-Spalten. → erfüllt
- [x] AC-3: Custom Fields handhabbar (Story Points via customfield_10016, Sprint via customfield_10020, Bezug-zu-Requirement via Labels). → erfüllt
- [ ] AC-4: Mentor-Termine als Releases/Versionen eingetragen. → **offen**, manuell in Jira-UI nachzuholen (siehe `10_jira_setup.md` Section 4.2)

**Definition of Done:**

- [x] Issue ist in Jira angelegt mit Story Points (2) und Sprint (Sprint 0)
- [x] Doku aktualisiert (`10_jira_setup.md` Mapping-Tabelle)
- [x] Quellen sind referenziert in `04_quellen.md` (Atlassian-Doku-Links via WebSearch)
- [x] In Jira auf "To Do" mit klarer Beschreibung

**Demo-Notizen:** [Backlog-View Jira](https://rumidesigns.atlassian.net/jira/software/projects/PQC/backlog) zeigt 13 Epics, 63 Stories, alle ihren Sprints zugeordnet, alle mit Story Points.

**Endurteil:** [Done, kleine offene Detail: Mentor-Termine als Releases noch nachzutragen]

---

### Story PQC-16 (INF-2): GitHub-Repo und Branch-Struktur

**Akzeptanzkriterien:**

- [x] AC-1 (Teil): GitHub-Repo existiert. → erfüllt (Repo angelegt)
- [ ] AC-2: Top-Level-Struktur (server/, app/, infra/, docs/, README.md, LICENSE). → **offen**, Ordner-Sync notwendig
- [ ] AC-3: main-Branch geschützt. → **offen**
- [ ] AC-4: Initiale Commit mit existierenden Markdown-Dokumenten. → **offen** (Sync ausstehend)

**Zusätzlich offen ausserhalb der AC:** Mentor-Access auf das Repo teilen, Mentoren über den Repo-Standort informieren.

**Endurteil:** **Carry-Over Sprint 1** mit Rest-Tasks: Ordner syncen, Mentor-Access einrichten, Mentoren informieren.

---

### Story PQC-17 (INF-3): Docker-Compose-Skeleton mit drei Services

**Status:** Noch nicht angefangen.

**Endurteil:** **Carry-Over Sprint 1**. Voraussetzung für SKL-1 (FastAPI-Skeleton), daher früh in Sprint 1 anzugehen.

---

### Story PQC-18 (INF-4): oqs-provider-fähiges nginx-Image baut

**Status:** Noch nicht angefangen.

**Endurteil:** **Carry-Over Sprint 1**. Strikt notwendig erst in Sprint 2 (TLS), aber frühes Bauen reduziert Risiko R-T05 (TLS-Setup-Bricht).

---

## 3. Stories, die nicht abgeschlossen wurden

| Story | Anteil fertig | Aktion | Wohin? |
|---|---|---|---|
| PQC-16 (INF-2) | ca. 20 % (Repo existiert) | Carry-Over | Sprint 1 (Top, blockiert nichts anderes aber sollte früh fertig sein) |
| PQC-17 (INF-3) | 0 % | Carry-Over | Sprint 1 (vor SKL-1) |
| PQC-18 (INF-4) | 0 % | Carry-Over | Sprint 1 (Vorbereitung für Sprint 2) |

Das heisst Sprint 1 erhält drei zusätzliche Stories aus dem Carry-Over (PQC-16, PQC-17, PQC-18). Mit ihren ursprünglich geschätzten 2 + 5 + 5 = 12 SP zusätzlich erhöht sich die Sprint-1-Last von 41 SP auf etwa 53 SP. Bei 7 Tagen Sprint-1-Länge ist das nominal stark über der Kapazität. Wir akzeptieren das im Rahmen des empirischen Sprint-1-Experiments (siehe Notiz Retro).

---

## 4. Erkenntnisse für den Product Backlog

**Untracked work erkannt:** Sprint 0 hat erheblich mehr Output produziert als die vier formellen INF-Stories. Insbesondere die folgenden Deliverables waren nicht als Stories im Backlog, sind aber bedeutende Sprint-0-Increments:

- Architektur-Entscheidungs-Dokument `03_entscheidung_auth_architektur.md`
- Quellen-Dokument `04_quellen.md`
- Requirements `05_requirements.md`
- Tech-Stack `06_tech_stack.md`
- Design `07_design.md`
- Scrum-Setup `08_scrum_setup.md`
- Product Backlog `09_product_backlog.md`
- Jira-Setup `10_jira_setup.md`
- Risk Register `11_risk_register.md`
- Traceability-Matrix `12_traceability_matrix.md`
- Sprint-Journal-Templates (5 Templates plus README)
- 76 Jira-Issues (13 Epics + 63 Stories)

**Lehre für die Folge-Sprints:** Setup- und Doku-Arbeit sollte explizit als Stories im Backlog stehen, damit Velocity-Tracking und Sprint-Goals diese Arbeit umfassen. Wir tracken das ab Sprint 1 strikt.

**Keine neuen Backlog-Stories nötig**, weil die genannten Deliverables fertig sind und nicht wiederholt werden müssen.

---

## 5. Risk Review

### 5.1 Eingetretene Risiken in diesem Sprint

| Risk-ID | Was ist passiert? | Wie reagiert (Mitigation/Contingency aktiviert)? |
|---|---|---|
| R-S02 (Sprint-0-Verzug) | Sprint 0 weiter verlängert auf 19 Tage (06.05 bis 24.05), nicht wie ursprünglich 12 Tage geplant. | Sprint 1 wird auf 7 Tage komprimiert zur Kompensation. Risk Register Updated. |

### 5.2 Geänderte Risiko-Bewertung

| Risk-ID | Alte Bewertung | Neue Bewertung | Begründung |
|---|---|---|---|
| R-S01 (Sprint-Kapazität) | Probability Hoch, Impact Mittel, Score 6 | Probability Hoch, Impact Hoch, Score 9 | Sprint 1 mit nur 7 Tagen und 53 SP Last (inkl. Carry-Over) ist deutlich überzeichnet. |
| R-S04 (Doku-Zeit in Sprint 4) | Score 6 | Score 4 (reduziert) | Viel Doku-Arbeit wurde bereits in Sprint 0 erledigt (Markdown-Dokumente als Vorlage für Bericht). Sprint-4-Doku-Zeit ist weniger kritisch als angenommen. |

### 5.3 Neue Risiken (in diesem Sprint identifiziert)

Keine neuen Risiken im Sprint 0 aufgetreten.

### 5.4 Active-Watch-Status

- [x] R-S01 (Sprint-Kapazität): Score auf 9 hochgestuft. Sprint 1 zeigt es. Wenn Sprint 1 nicht abgeschlossen wird, müssen ab Sprint 2 Last reduziert oder Stretch-Items gestrichen werden.
- [x] R-T04 (OIDC-Setup): Erst in Sprint 2 relevant, vor-bereitend in Sprint 1 möglich (parallel zum Coding OAuth-Apps anlegen).
- [x] R-S04 (Doku-Zeit): Score reduziert, da viel Doku schon fertig.
- [x] R-T01 (liboqs Build): Wird in Sprint 1 / SKL-1 oder INF-3 zum ersten Mal real getestet.
- [x] R-P01 (Motivation): Stabil. Sprint 0 Verzug hat keine Motivation gekostet, im Gegenteil: Klarheit über das Projekt ist gestiegen.

---

## 6. Velocity dieser Sprint

- **Geplante Story Points (nur INF-1 bis INF-4):** 14 SP
- **Abgeschlossene Story Points (formell):** 2 SP (nur INF-1)
- **Real geleistete Arbeit (informell, nicht als Story getrackt):** Sehr hoch (siehe Section 4 untracked work)
- **Tatsächliche Arbeitsstunden:** ca. 10 Stunden über 19 Kalendertage
- **Beobachteter AI-Multiplier:** Volumen der Deliverables (12 Markdown-Dokumente, 76 Jira-Issues, etc.) entspricht erfahrungsgemäss 25 bis 40 Stunden klassischer Solo-Arbeit. Beobachteter Multiplier liegt daher eher bei **2.5x bis 4x**, deutlich über dem konservativen 1.5x-Ansatz in `08_scrum_setup.md` Abschnitt 7.4.

**Wichtig:** Dieser Multiplier-Wert ist nur für Doku- und Planungs-Arbeit erhoben, nicht für Code-Arbeit. Sprint 1 wird zeigen, ob er für Implementierung ebenso hoch ist.

---

## 7. Notizen für die Retrospektive

- **Empirisch-positiver Befund:** AI-Multiplier in Doku/Planung deutlich höher als angenommen. Sprint 1 wird zeigen ob das auch für Code gilt.
- **Negativer Befund:** Untracked work war substantiell. Sprint 0 hatte ein Sprint-Goal aber das Sprint Backlog deckte nur 14 SP der tatsächlichen Arbeit ab. Die restliche Arbeit (Doku, Planung) war "implizit" und nicht in Stories formuliert. Das verzerrt die Velocity-Messung.
- **Prozess-Frage für Retro:** Wie tracken wir in Sprints 1 bis 4 die Doku-Arbeit konsistent? Sollen wir Doku-Stories pro Sprint einplanen, nicht nur in Sprint 4?
- **Self-Management:** 10 Stunden über 19 Tage ist sehr inkonsistent. Im Schnitt 0.5 h/Tag. Sprint 1 mit 53 SP in 7 Tagen würde grob 30 bis 50 effektive Stunden brauchen, also 4 bis 7 h/Tag. Das ist deutlich höher als der Sprint-0-Schnitt. Retro-Frage: ist diese Steigerung realistisch in der Wochenkapazität?
