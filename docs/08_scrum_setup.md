# Scrum-Setup: Implementing PQC

**Projekt:** Implementing PQC (Semesterarbeit 3, ITCNE25)
**Autor:** Dodoe Rumiñahui Mannale
**Erstellt:** 17.05.2026
**Status:** Initial-Version (v1.0)

**Bezug:** Dieses Dokument legt die Scrum-Anwendung für die Semesterarbeit fest. Es ist die Referenz für alle Bewertungspunkte rund um die Handlungskompetenz B5 (ICT-Projekte planen, leiten, umsetzen und evaluieren) und ergänzt die fachlichen Dokumente `05_requirements.md` und `07_design.md`. Die normative Scrum-Theorie liegt extern (siehe Abschnitt 1.2 Quellen).

---

## Inhaltsverzeichnis

1. [Einleitung und Geltungsbereich](#1-einleitung-und-geltungsbereich)
2. [Scrum-Team in dieser Arbeit (Solo-Scrum-Adaption)](#2-scrum-team-in-dieser-arbeit-solo-scrum-adaption)
3. [Scrum-Events angepasst für Solo-Arbeit](#3-scrum-events-angepasst-für-solo-arbeit)
4. [Scrum-Artefakte für dieses Projekt](#4-scrum-artefakte-für-dieses-projekt)
5. [Commitments: Product Goal, Sprint Goal, Definition of Done](#5-commitments-product-goal-sprint-goal-definition-of-done)
6. [Definition of Ready (DoR) und Akzeptanzkriterien](#6-definition-of-ready-dor-und-akzeptanzkriterien)
7. [Story-Sizing und Schätzmethode](#7-story-sizing-und-schätzmethode)
8. [Sprint-Plan (aktualisiert)](#8-sprint-plan-aktualisiert)
9. [Stakeholder-Reviews und Mentor-Termine](#9-stakeholder-reviews-und-mentor-termine)
10. [Mapping zu Handlungskompetenzen und Bewertungskriterien](#10-mapping-zu-handlungskompetenzen-und-bewertungskriterien)
11. [Tooling](#11-tooling)
12. [Versionsverlauf](#12-versionsverlauf)

---

## 1. Einleitung und Geltungsbereich

### 1.1 Zweck dieses Dokuments

Die Semesterarbeit verlangt laut Merkblatt-A einen nachvollziehbaren Projektablauf gemäss Unterricht an der TBZ. Im Modul PRJ2 wurde Scrum als Methode behandelt. Dieses Dokument beschreibt verbindlich, wie Scrum in dieser konkreten Arbeit angewendet wird, welche Anpassungen sich aus der Solo-Situation ergeben und wie sich die Scrum-Praxis zu den Bewertungs-Kompetenzen (Bewertungs-Kriterien 1 bis 5) verhält.

Das Dokument referenziert die Scrum-Theorie statt sie zu wiederholen, und macht die projektspezifische Adaption transparent.

### 1.2 Quellen

- Scrum Guide 2020 (Schwaber, Sutherland), normative Definition aller Begriffe, online unter scrumguides.org
- TBZ-Unterricht PRJ2, kondensiert in `../tbz_resources/Komplette-Scrum-Theorie-in-einem-Dokument.md`
- Merkblatt-A der Semesterarbeit (Bewertungs-Kriterien und Handlungs-Kompetenzen)
- Handlungs-Kompetenzen-Liste PRJ1 bis PRJ5

### 1.3 Geltungsbereich

Dieses Dokument gilt ab dem 17.05.2026 für den restlichen Verlauf der Semesterarbeit bis zur Abgabe am 04. bis 05.07.2026. Änderungen sind im Versionsverlauf (Abschnitt 12) zu dokumentieren.

---

## 2. Scrum-Team in dieser Arbeit (Solo-Scrum-Adaption)

### 2.1 Ausgangslage

Die Semesterarbeit ist als Einzelarbeit eingereicht und genehmigt. Es gibt keinen Auftraggeber, kein Stakeholder-Komitee, keine Mitstudierenden im selben Projekt. Der Lehrbetrieb HEKS ist nicht Auftraggeber dieser Arbeit, die Arbeit ist ein TBZ-Schul-Projekt.

Daraus folgt: Es existiert kein klassisches Scrum-Team. Alle drei Verantwortlichkeiten (Developer, Product Owner, Scrum Master) liegen physisch bei einer einzigen Person, dem Studierenden. Diese Realität wird in dieser Arbeit ehrlich dokumentiert, statt sie hinter konstruierten Rollen-Wechseln zu verstecken. **Stakeholder existieren aber sehr wohl**: die beiden TBZ-Experten (Fach- und Projektmanagement) sowie die Lehrgangsleitung. Sie sind nicht Teil des Scrum-Teams, aber liefern externe Inspektion und Feedback.

### 2.2 Wie die drei Verantwortlichkeiten gelebt werden

Auch wenn alle Rollen bei einer Person liegen, bleiben die drei Verantwortlichkeiten gedanklich getrennt. Vor jeder grösseren Entscheidung wird bewusst die zuständige Rolle eingenommen.

**Developer-Verantwortlichkeit.** Umsetzung der Stories im Sprint. Schätzung von Aufwand. Selbstorganisation der täglichen Arbeit. Einhaltung der Definition of Done. Diese Rolle dominiert zeitlich, denn der grösste Teil der 70 bis 100 Projekt-Stunden ist Implementation.

**Product-Owner-Verantwortlichkeit.** Priorisierung des Backlogs nach Wert. Pflege der Akzeptanzkriterien. Entscheidung über Scope-Cuts, wenn Sprints zu eng werden. In dieser Arbeit ist Wert nicht Umsatz, sondern Erfüllung der Bewertungs-Kompetenzen plus persönlicher Lerneffekt im PQC-Bereich. Diese Rolle wird bewusst vor jedem Sprint-Planning und vor jeder grösseren Backlog-Änderung eingenommen, zeitlich etwa 10 Prozent.

**Scrum-Master-Verantwortlichkeit.** Sicherstellen, dass Scrum richtig angewendet wird. Hindernisse beseitigen. Reflexion über den Prozess in der Retrospektive. In einer Solo-Arbeit reduziert sich diese Rolle auf ehrliche Selbst-Beobachtung und auf die Pflege der Process-Dokumente (dieses Dokument, Sprint-Journal, Retros). Zeitlich etwa 5 Prozent. Ergänzend wird in dieser Session Claude als unterstützender Scrum-Master herangezogen, um blinde Flecken sichtbar zu machen.

### 2.3 Stakeholder

Stakeholder sind laut Scrum Guide 2020 Personen ausserhalb des Scrum-Teams mit spezifischem Interesse und Wissen, das für die inkrementelle Entdeckung des Produkts notwendig ist. In dieser Arbeit:

| Stakeholder | Stakeholder-Typ | Hauptinteraktion |
|---|---|---|
| Studierender (Dodoe) | Nicht Stakeholder, sondern das gesamte Scrum-Team | Tägliche Umsetzung, sprintweise Planung und Retro |
| Fach-Experte (TBZ) | Stakeholder (fachlich) | Drei Mentor-Termine, asynchrones Feedback in MS Teams, prüft technische Korrektheit und PQC-Anwendung |
| Projektmanagement-Experte (TBZ) | Stakeholder (Prozess) | Drei Mentor-Termine, asynchrones Feedback, prüft Projekt-Management-Praxis und Scrum-Anwendung |
| Lehrgangsleitung | Stakeholder (formell) | Eskalationsweg, finale Notenkonferenz |

Wichtig: Die Mentor-Termine sind **zusätzliche externe Reviews**, keine Ersetzung der internen Sprint Reviews. Beide finden statt (siehe Abschnitt 3.4 und 9).

### 2.4 Bekannte Limitationen und Gegenmassnahmen

Solo-Scrum verliert einige wichtige Vorteile des Frameworks. Diese Limitationen sind transparent zu nennen, damit die Bewertung kritischer Reflexion (Bewertungs-Kriterium 5) Stoff hat.

| Limitation | Konsequenz | Gegenmassnahme |
|---|---|---|
| Kein Peer-Review im Team | Code-Qualität und Architektur-Entscheidungen werden nicht durch Vier-Augen-Prinzip abgesichert | Mentor-Termine als externe Reviews, schriftliche Architektur-Entscheidungs-Dokumente (`03_entscheidung_auth_architektur.md` als Vorlage), AI-gestützte Reviews als ergänzende Quelle |
| Keine Rollenseparation zwischen Dev und PO | Risiko, dass technisch Interessantes statt Wertbringendes priorisiert wird | PBIs haben Akzeptanzkriterien und Bezug zu Requirements/Bewertungs-Kriterien, jede Sprint-Planning-Sitzung beginnt mit dem Re-Lesen der Projekt-Ziele aus `05_requirements.md` |
| Kein Scrum-Master, der Anti-Patterns aufdeckt | Risiko von ScrumBut (Scrum nur dem Namen nach) | Ehrliche Retros mit konkreten Beispielen, dieses Setup-Dokument als Massstab, dritte Mentor-Termin-Frage immer "wie läuft der Prozess", Claude als SM-Unterstützung in den Arbeits-Sessions |
| Daily Scrum entartet zur Selbstgespräch-Pflicht | Verlust des Inspektions-Wertes | Tagesnotiz als kurze schriftliche Form, nicht jeden Tag, sondern an Arbeitstagen am Projekt; nicht länger als drei Sätze pro Tag |
| Velocity-Messung ist statistisch unbrauchbar bei einem Entwickler | Sprint-Planung kann nicht auf Velocity-Trend basieren | Schätzung initial in T-Shirt-Sizes, nach Sprint 1 wird kalibriert mit tatsächlichen Stunden, ab Sprint 2 wird die durchschnittliche tatsächliche Wochenkapazität (in Stunden) als Heuristik genutzt |

---

## 3. Scrum-Events angepasst für Solo-Arbeit

### 3.1 Sprint

Der Sprint ist der Rahmen-Event und enthält alle anderen Events.

- **Dauer:** 2 Wochen (14 Kalendertage). Ausnahmen: Sprint 0 (Setup, 13 Tage), Sprint 4 (finale Polish-Phase, 7 Tage).
- **Beginn/Ende:** Sprint 1 startet Montag 25.05, danach wechselnde Tage durch Anpassung an Mentor-Termine.
- **Sprint-Ziel:** Wird in Sprint-Planning festgelegt und bleibt im Sprint stabil. Wenn das Ziel obsolet wird, kann der Sprint abgebrochen werden, mit dokumentierter Begründung.
- **Ergebnis:** Jeder Sprint endet mit einem Increment, das die DoD erfüllt (siehe Abschnitt 5.3).

### 3.2 Sprint Planning

Findet am ersten Tag eines neuen Sprints statt, Timebox 2 Stunden für 2-Wochen-Sprints.

**Drei Fragen:**

- Warum ist dieser Sprint wertvoll? Antwort als Sprint-Ziel-Satz formulieren.
- Was kann in diesem Sprint fertig werden? Top-Backlog-Items auswählen.
- Wie wird die Arbeit erledigt? Stories in Tasks zerlegen (in Jira).

**Output:** Sprint Backlog in Jira plus schriftliches Sprint-Ziel im Sprint-Journal (Template unter `../sprint_journal/_templates/sprint_planning_template.md`).

### 3.3 Daily Scrum (adaptiert als Tagesnotiz)

Klassisch ein 15-Minuten-Event für das Team. In Solo-Arbeit ohne Adressaten würde es zur leeren Übung. Ersetzt durch eine **kurze Tagesnotiz** pro Arbeitstag (nicht pro Kalendertag).

Format pro Eintrag, maximal drei Sätze:

- Was wurde seit der letzten Notiz fertig?
- Was ist heute geplant?
- Welche Blocker oder offenen Fragen gibt es?

Geführt als `daily_journal.md` pro Sprint im Sprint-Journal-Ordner. Ziel: Selbst-Inspektion plus eine ehrliche Datenbasis für die Retrospektive und für die Mentor-Termine. Nicht das Tagebuch wird benotet, sondern die Erkenntnisse, die daraus folgen.

### 3.4 Sprint Review (interne Selbst-Inspektion)

Findet am letzten Tag jedes Sprints statt, Timebox 1 Stunde. Dies ist **nicht** identisch mit den Mentor-Terminen.

**Ablauf:**

1. **Self-Demo:** Increment wird gegen die Akzeptanzkriterien aller im Sprint enthaltenen Stories durchgegangen. Manuelles Durchspielen plus automatisierte Tests laufen lassen.
2. **Erfüllungsprüfung:** Pro Story: Akzeptanzkriterien erfüllt? DoD erfüllt? Falls nein, Story zurück in den Product Backlog.
3. **Schriftliches Demo-Protokoll** anhand des Templates `sprint_review_template.md`.
4. **Backlog-Update:** Erkenntnisse fliessen direkt in den Product Backlog (neue Stories, geänderte Priorität, ergänzte Akzeptanzkriterien).

Output: ausgefülltes `sprint_review.md` im Sprint-Ordner.

### 3.5 Sprint-Retrospektive (Reflexions-Eintrag)

Findet am Ende jedes Sprints nach dem Review statt, Timebox 45 Minuten.

**Drei Reflexions-Achsen:**

- **Produkt:** Habe ich das Sprint-Ziel erreicht? Wenn nein, warum nicht?
- **Prozess:** Was lief gut in der Anwendung von Scrum, was sollte im nächsten Sprint anders sein?
- **Selbstmanagement:** Wie war Zeitmanagement, Fokus, Energie? Welche Anti-Patterns sind aufgetaucht?

Geführt als `sprint_retrospective.md` pro Sprint. Output: bis zu drei konkrete Massnahmen für den nächsten Sprint, die in Sprint-Planning aufgegriffen werden. Die Retros sind die Hauptquelle für die Reflexionstiefe im Schlussbericht (Bewertungs-Kriterium 5).

---

## 4. Scrum-Artefakte für dieses Projekt

### 4.1 Product Backlog

Das Product Backlog ist die einzige Quelle für Arbeit am Produkt. Es ist eine geordnete Liste aller bekannten Features, Verbesserungen, Bugs und nicht-funktionalen Arbeiten.

**In dieser Arbeit:**

- Initialer Inhalt wird in `09_product_backlog.md` definiert und in Jira übertragen.
- Quelle der Items: Use Cases (UC-1 bis UC-7) und Functional Requirements (FR-Auth-*, FR-Broker-*, FR-Token-*, FR-Session-*, FR-DataChannel-*, FR-Crypto-*) aus `05_requirements.md`, ergänzt um Querschnitts-Items aus den Non-Functional Requirements und um Doku-Items.
- Priorisierung primär nach Risiko und Voraussetzungs-Beziehungen (Bottom-up): Was muss zuerst da sein, damit später aufgebaut werden kann? In der vorliegenden Architektur z.B. Crypto-Abstraction-Layer vor Token-Modul vor Session-Modul.
- Refinement (Backlog-Pflege) erfolgt fortlaufend, vor allem aber bei jedem Sprint-Planning, und beim Auftauchen neuer Erkenntnisse.

### 4.2 Sprint Backlog

Das Sprint Backlog ist das Commitment für den aktuellen Sprint. Es besteht aus drei Teilen: Sprint-Ziel (Warum), ausgewählte Backlog-Items (Was), Plan zur Umsetzung (Wie, in Form von Tasks).

**In dieser Arbeit:**

- Sprint Backlog lebt in Jira als Sprint-Snapshot des Product Backlogs plus zugeordnete Tasks pro Story.
- Tasks werden so klein gehalten, dass sie maximal einen Arbeitstag dauern (typisch 2 bis 4 Stunden).
- Während des Sprints können Tasks ergänzt, geteilt oder gelöscht werden, das Sprint-Ziel bleibt aber stabil.

### 4.3 Increment

Ein Increment ist ein nutzbares, integriertes Ergebnis am Ende eines Sprints. Es muss die Definition of Done erfüllen und auf allen vorherigen Increments aufbauen.

**In dieser Arbeit:**

- Increment ist nicht ein Production-Deployment, sondern ein lauffähiger Zwischenstand auf der lokalen Demo-Umgebung (Docker Compose).
- Pro Sprint mindestens ein Increment.
- Sprint 0 hat als Increment die Tooling- und Entscheidungs-Basis (Jira-Setup, Repo-Setup, oqs-provider-Image baut, alle Architektur-Dokumente). Skeleton-Setup wurde bewusst nach Sprint 1 verschoben (siehe Abschnitt 8.1).

---

## 5. Commitments: Product Goal, Sprint Goal, Definition of Done

Jedes Scrum-Artefakt hat im Scrum Guide 2020 ein eingebautes Commitment, das den Fokus schärft.

### 5.1 Product Goal (Commitment des Product Backlogs)

Übergeordnetes, langfristiges Ziel des Produkts. Hier ist der Sinn des ganzen Projekts.

**Product Goal:**
"Eine vollständig funktionierende Mobile-Auth-Demo, die NIST-PQC-Standards (ML-KEM-768, ML-DSA-65) End-to-End anwendet, klassische OIDC-Provider als Identity-Quelle einbindet und Crypto-Agility als Architektur-Prinzip umsetzt. Verifizierbar durch lauffähige App, lauffähigen Server, automatisierte Tests, dokumentierter Bericht und Schlusspräsentation bis 04. bis 05.07.2026."

Dieses Goal ist direkt abgeleitet aus G-1 bis G-5 in `05_requirements.md`.

### 5.2 Sprint Goal (Commitment des Sprint Backlogs)

Konkretes Ziel des aktuellen Sprints in einem Satz. Wird im Sprint-Planning festgelegt, bleibt stabil.

**Beispiel Sprint 1:** "FastAPI- und Expo-Skeletons stehen, lokaler Login funktioniert End-to-End mit ML-DSA-65-signiertem Broker-Token inklusive automatisierten Tests und Argon2id-Passwort-Hashing."

Die konkreten Sprint Goals pro Sprint sind im Sprint-Plan in Abschnitt 8 vermerkt.

### 5.3 Definition of Done (Commitment des Increments)

Die DoD ist eine **projektweite, storyunabhängige Qualitäts-Checkliste**, die für *jede* Story gilt. Sie beantwortet die Frage "Hat die Arbeit unsere Qualitäts-Standards erfüllt?" und ist klar getrennt von den Akzeptanzkriterien (siehe Abschnitt 6.2), welche die fachliche Korrektheit einer spezifischen Story beschreiben. Eine Story ist erst "done", wenn **beides** erfüllt ist: DoD plus Akzeptanzkriterien.

**Definition of Done für dieses Projekt (gilt für jede Story):**

- Code ist im Git-Hauptbranch (main) gemergt
- Code hat einen klaren Commit-Message-Verlauf mit nachvollziehbaren Schritten (atomic commits)
- Für funktionale Änderungen am Backend: mindestens ein automatisierter Test (pytest), der den Happy-Path und mindestens einen relevanten Fehlerfall abdeckt
- Für funktionale Änderungen an der Mobile-App: manuelle Test-Notiz mit Screenshot oder Recording, plus optional Jest-Unit-Test für reine Logik
- Akzeptanzkriterien der Story sind nachprüfbar erfüllt (formelle Prüfung im Sprint Review)
- Keine offenen kritischen Warnungen oder TODOs ohne Ticket im Code, die im Sprint-Scope liegen
- Relevante Dokumentation ist aktualisiert (mindestens README, falls Konfigurations- oder Setup-Aspekte verändert wurden; passender Markdown-Artefakt, falls Architektur betroffen ist)
- Quellen für nicht-trivialen Code oder fremde Snippets sind in `04_quellen.md` referenziert
- Evidence-File im aktuellen Sprint-Journal angelegt (siehe Evidence-Konvention unten)
- Die Story ist in Jira auf "Done" gesetzt mit strukturiertem Done-Comment (Erledigt-Punkte, Abweichungen mit Begründung, Links zur Evidence-Datei und relevanten Commits)

**Evidence-File-Konvention (etabliert mit PQC-17 in Sprint 1, gilt ab Sprint 1):**

Pro Story wird ein Evidence-Markdown im Pfad `sprint_journal/sprint_<n>/evidence/<JIRA-KEY>_<STORY-ID>_<kurze-bezeichnung>.md` abgelegt. Inhalt mindestens: AC-Check (welcher AC durch welchen Output erfüllt), getroffene Architektur-Entscheidungen, bewusste Abweichungen mit Begründung, Verifikations-Output (Logs, `docker compose ps`-Output, Test-Result, Screenshots). Der Jira-Done-Comment enthält einen Relative-Link auf diese Evidence-Datei. Begründung: Mentor und Bewertung müssen nachvollziehbar prüfen können was tatsächlich geliefert wurde und warum von der Story-Spec abgewichen wurde, ohne dass dafür ein Code-Walkthrough nötig ist. Die Done-Notiz im Jira allein ist zu kurz dafür.

**Done-Comment-Struktur in Jira (etabliert in Sprint 0):**

```
**Done Note (TT.MM.JJJJ)**

Erledigt:
- <Punkt 1>
- <Punkt 2>

Abweichungen von den ACs:
- <Welches AC nicht 1:1 umgesetzt, mit Begründung>

Links:
- <Evidence-File-Pfad, Commit-Hashes, Doku-Pfade>
```

Sektionen "Abweichungen" und "Links" können weggelassen werden wenn nicht zutreffend; "Erledigt" ist Pflicht.

---

## 6. Definition of Ready (DoR) und Akzeptanzkriterien

### 6.1 Definition of Ready (DoR)

Die DoR ist im offiziellen Scrum Guide nicht enthalten, gilt aber als Best Practice und wird im PRJ-Unterricht explizit erwähnt. Sie ist eine Eingangs-Latte für das Sprint-Planning: nur "ready"-Stories werden in den Sprint eingeplant. Eine Story ist "ready", wenn folgende Punkte erfüllt sind:

- **Beschreibung im User-Story-Format:** "Als <Rolle> möchte ich <Funktion>, damit <Nutzen>". Bei rein technischen Stories (z.B. Crypto-Abstraction-Layer-Setup) reicht eine klar formulierte technische Beschreibung mit Begründung.
- **Akzeptanzkriterien vorhanden:** Mindestens zwei nachprüfbare Kriterien (siehe 6.2).
- **Abhängigkeiten geklärt:** Stories, die zuerst fertig sein müssen, sind im Jira-Link-Feld eingetragen. Falls externe Abhängigkeit (z.B. Google-OAuth-Client-Registrierung), ist diese identifiziert.
- **Geschätzt:** Story hat eine T-Shirt-Size oder einen Story-Point-Wert (siehe Abschnitt 7).
- **Bezug zu Requirement oder Ziel:** Story referenziert mindestens ein UC, FR oder NFR aus `05_requirements.md`, oder ist explizit als Dokumentations- oder Querschnitts-Arbeit markiert.
- **Klein genug:** Story passt in einen Sprint mit Reserve. Wenn nicht, ist sie zu zerlegen.

### 6.2 Akzeptanzkriterien (storyspezifisch)

Akzeptanzkriterien beantworten die Frage "Funktioniert dieses spezielle Feature richtig?" und sind storyspezifisch. Sie sind klar getrennt von der DoD, die die projektweite Qualitäts-Latte definiert.

**Form:** Pro Story mindestens zwei konkret prüfbare Kriterien, möglichst im Given/When/Then-Format oder als Liste prüfbarer Aussagen. Beispiele aus den UCs in `05_requirements.md`:

- "Erfolgreicher Login liefert einen Token, der mit dem Public-Key des Auth-Service ML-DSA-verifizierbar ist"
- "Falsche Credentials und nicht-existierender User liefern identische 401-Responses"

**Verhältnis zu DoD:** Eine Story ist "done", wenn sowohl alle Akzeptanzkriterien (fachliche Korrektheit) als auch alle DoD-Punkte (Qualitäts-Latte) erfüllt sind.

---

## 7. Story-Sizing und Schätzmethode

### 7.1 Methode

Initial werden T-Shirt-Sizes verwendet, weil bei nur einem Entwickler keine Multi-Person-Schätzungen möglich sind und absolute Stunden-Schätzungen erfahrungsgemäss zu optimistisch ausfallen. T-Shirt-Sizes werden bei der Backlog-Pflege vergeben und auf Story-Points abgebildet (für die Jira-Eingabe und für die Velocity-Heuristik).

| T-Shirt-Size | Story-Points (Fibonacci) | Typischer Aufwand | Beispiel |
|---|---|---|---|
| XS | 1 | weniger als 2 Stunden | Konfig-Eintrag, kleine Refactorings |
| S | 2 | 2 bis 4 Stunden | Einzelner Endpoint ohne neue Crypto-Logik |
| M | 5 | 4 bis 10 Stunden | Endpoint plus Tests plus Doku |
| L | 8 | 10 bis 20 Stunden | Modul-Einführung (z.B. Token-Modul) |
| XL | 13 | mehr als 20 Stunden | Zu gross, zerlegen |

XL-Stories sind ein Signal, dass die Story noch nicht "ready" ist und zerlegt werden muss.

### 7.2 Velocity

Velocity (Story-Points pro Sprint) wird ab Sprint 1 dokumentiert, aber nicht als alleiniges Planungs-Kriterium genutzt. Begründung: Bei einem Entwickler ist die Varianz zu hoch, eine glaubwürdige Velocity-Statistik bräuchte 5 oder mehr Sprints. Stattdessen wird die tatsächliche Stundenkapazität pro Woche (variabel: 10 bis 15 Stunden plus Block-Phasen) als Heuristik genutzt.

### 7.3 Re-Schätzung

Stories werden nicht nachträglich umgeschätzt, auch wenn sie sich als grösser oder kleiner als geschätzt erweisen. Stattdessen wird in der Retro reflektiert, was zu der Fehlschätzung geführt hat, und beim nächsten ähnlichen Item adjustiert.

### 7.4 AI-Multiplier-Konvention

**Wichtig für die Auswertung am Projekt-Ende:** Die T-Shirt-Sizes und Story-Point-Werte im Backlog (`09_product_backlog.md`) sind als **klassische Solo-Dev-Schätzungen ohne AI-Unterstützung** dokumentiert. Tatsächlich wird die Arbeit mit AI-Unterstützung (Claude / Claude Code) durchgeführt, was eine ungefähre Beschleunigung von **1.5x** erwarten lässt.

**Konsequenzen:**

- **Schätzungen werden nicht angepasst.** Sie bleiben "ohne AI" stehen.
- **Tatsächliche Arbeitszeit wird pro Story und pro Sprint dokumentiert** (siehe Zeit-Tracking-Methode unten).
- **Vergleich am Projekt-Ende:** Geschätzte vs. tatsächliche Arbeitszeit erlaubt eine empirische Messung des AI-Multipliers für dieses konkrete Projekt. Diese Auswertung fliesst in den Reflexions-Teil des Schlussberichts.
- **Bei Sprint-Planning** wird berücksichtigt, dass die nominal "über-allokierte" Sprint-Last (z.B. Sprint 1 mit 41 SP vs. 20-25 SP klassischer Kapazität) durch den AI-Multiplier auf etwa 30-37 SP effektive Kapazität pro Sprint erweitert wird. Damit ist die Planung enger aber nicht unrealistisch.
- **Risiko:** Falls der AI-Multiplier in der Praxis unter 1.5x ausfällt (z.B. bei subtilen Crypto-Bugs, wo AI weniger hilft als bei Boilerplate), greift die Stretch-Goal-Streichung (siehe `11_risk_register.md` R-S01).

**Zeit-Tracking-Methode (etabliert ab Sprint 1):**

Pro abgeschlossener Story werden zwei Stellen gepflegt:

1. **Tabelle "Zeit-Tracking pro Story" im Daily Journal des Sprints.** Spalten: Story-Key, T-Shirt-Size, Story Points (ohne AI), tatsächliche Zeit (Minuten oder Stunden), berechneter Multiplier (Schätzung in h geteilt durch tatsächliche Zeit in h), Notiz mit Kontext (Carry-Over, Recherche-lastig, blocker, neue Library etc.). Wird beim Sprint Review aggregiert.
2. **Jira Worklog auf der jeweiligen Story** via `addWorklogToJiraIssue` mit `timeSpent` (z.B. `40m`, `2h`, `1h30m`) und kurzem Kontext-Kommentar. Macht die Daten mentor-sichtbar und export-fähig.

**Schätzung-in-Stunden-Mapping (Mittel des T-Shirt-Ranges für die Multiplier-Berechnung):**

| T-Shirt | SP | Klassisch Mittel-h | Beispiel-Multiplier-Berechnung |
|---|---|---|---|
| XS | 1 | 1.0 h | tatsächlich 30 Min: Multiplier 2.0x |
| S | 2 | 3.0 h | tatsächlich 1h: Multiplier 3.0x |
| M | 5 | 7.0 h | tatsächlich 2h: Multiplier 3.5x |
| L | 8 | 15.0 h | tatsächlich 5h: Multiplier 3.0x |
| XL | 13 | 25.0 h | (XL ist Signal zum Zerlegen) |

Bei der Auswertung im Schlussbericht wird zusätzlich nach Story-Typ aufgeschlüsselt (Crypto-Logik vs. Infrastructure-Setup vs. UI-Implementation vs. Doku), weil der AI-Multiplier vermutlich nach Typ stark variiert.

---

## 8. Sprint-Plan (aktualisiert)

### 8.1 Übersicht und Verzug-Begründung

Der ursprüngliche Sprint-Plan vom 08.05.2026 hatte Sprint 0 als 6-tägigen Block (06.05 bis 11.05). Sprint 0 wurde in zwei Schritten verlängert auf insgesamt 19 Tage (06.05 bis 24.05): zuerst wegen Unsicherheit über Scope, Umsetzbarkeit und Sinnhaftigkeit des Projekts, was vertiefte Recherche (NIST-Standards, Library-Reife, Mobile-Crypto-Limitationen) sowie eine fundierte Architektur-Entscheidung (Option 2 plus Identity Broker, dokumentiert in `03_entscheidung_auth_architektur.md`) erforderte. In einer zweiten Phase kamen umfangreiche Setup-Arbeiten dazu (Scrum-Setup, Backlog, Jira-Projekt mit 76 Issues, Sprint-Journal-Templates, Risk Register, Traceability-Matrix), bevor mit Coding begonnen werden konnte. Diese Vorarbeit zahlt sich in den Folge-Sprints durch klare Anforderungen, dokumentiertes Design und durchstrukturierte Planung aus (siehe `05_requirements.md`, `07_design.md`, `09_product_backlog.md`, `11_risk_register.md`, `12_traceability_matrix.md`).

Aus Scrum-Master-Sicht ist diese Verlängerung legitim als Adaption gemäss der dritten Säule des empirischen Prozesses. Der ursprüngliche Plan basierte auf zu optimistischen Annahmen über Vorwissen und über den Setup-Aufwand. Der korrigierte Plan ist realistischer.

Die Skeleton-Erstellung (FastAPI- und Expo-Boilerplate) wird bewusst nach Sprint 1 verschoben, weil sie eigentlich erste Implementation-Arbeit ist und thematisch zu Sprint 1 passt. Damit bleibt Sprint 0 in seinem Charakter als Setup-, Recherche- und Entscheidungs-Phase.

Sprint 1 ist dadurch auf 7 Tage komprimiert (statt 14). Die Sprint-Last wird bewusst nicht reduziert, sondern Sprint 1 wird als empirisches Experiment genutzt, um die Schätz-Genauigkeit unter AI-Unterstützung zu messen (siehe Abschnitt 7.4 AI-Multiplier). Falls Sprint 1 zeigt, dass die Last unrealistisch war, wird ab Sprint 2 angepasst. Die restlichen Sprints (2, 3, 4) bleiben in ihrer ursprünglichen Länge.

**Fixe Termine, die nicht verschoben werden können:**

- Mentor 1:1 #1: 01.06.2026 (bestätigt, eingetragen)
- Mentor 1:1 #2: noch zu definieren
- Mentor 1:1 #3: noch zu definieren
- Abgabe: 04. bis 05.07.2026

### 8.2 Aktualisierter Sprint-Plan

| Sprint | Zeitraum | Tage | Sprint-Ziel | Schlüssel-Liefer-Elemente |
|---|---|---|---|---|
| Sprint 0 | 06.05 bis 24.05 | 19 | Scope, Architektur und Tooling-Basis ready | Architektur-Entscheidung, Requirements, Design, Jira-Setup, GitHub-Repo, oqs-provider-Image baut, dieses Scrum-Setup-Dokument |
| Sprint 1 | 25.05 bis 31.05 | 7 | FastAPI- und Expo-Skeletons stehen; lokaler Login End-to-End mit ML-DSA-signiertem Broker-Token | FastAPI-Skeleton, Expo-Skeleton, FR-Auth-1, FR-Auth-2, FR-Token-1 (Teil), FR-Token-2 (Teil), FR-Crypto-1 (Teil), erste pytest-Suite, einfacher Login-Screen |
| Sprint 2 | 01.06 bis 14.06 | 14 | Federated Login (Google, Microsoft) plus hybrid TLS am Server | FR-Broker-1 bis FR-Broker-4, NFR-Sec-5 (CSRF), nginx plus oqs-provider mit X25519MLKEM768, Demo via curl. **Mentor 1:1 #1 am 01.06 (Start des Sprints)** |
| Sprint 3 | 15.06 bis 28.06 | 14 | App-Layer PQ-Session mit ML-KEM-768 plus geschützter API-Call und Algorithmus-Wechsel-Demo | FR-Session-1 bis FR-Session-4, FR-DataChannel-1, FR-DataChannel-2, FR-Crypto-2, FR-Crypto-3, NFR-Sec-2. Mentor 1:1 #2 (Datum noch festzulegen) |
| Sprint 4 | 29.06 bis 05.07 | 7 | Bericht, Benchmarks, Schlusspräsentation fertig zur Abgabe | Schlussbericht (DOCX), Schluss-Präsentation (PPTX), Performance-Messungen (NFR-Perf-1 bis NFR-Perf-3), Quellen-Vollständigkeit, Submission |

**Code-Freeze:** Ende Sprint 3, also 28.06.2026. Nach diesem Datum keine neuen Features mehr. Bugfixes nur, wenn ein Bug einen Abgabe-Show-Stopper verursacht.

### 8.3 Stretch-Goals (nur wenn Zeit reicht)

- FR-Crypto-4: Hybrid-Key-Combiner (ML-KEM + X25519 via HKDF) als Defense-in-Depth, vor allem für NFR-Sec-6
- Apple Sign In als dritter IdP
- Self-signed ML-DSA-Test-Cert als TLS-Demo

Stretch-Goals werden im Backlog als "Could"-Priorität geführt und nur in Sprint 4 oder bei freiem Slack in Sprint 3 angegangen.

### 8.4 Risikoreserven

In jedem Sprint sind 20 Prozent Kapazitäts-Reserve eingeplant, um Schätz-Fehler und unvorhersehbare Probleme abzufedern (z.B. liboqs-Build-Probleme, Mobile-Crypto-Quirks). Reserve wird nicht für Stretch-Goals genutzt.

### 8.5 Eskalation bei Sprint-Abbruch

Wenn ein Sprint-Ziel offensichtlich nicht erreichbar ist:

1. Im Tages-Tagebuch dokumentieren, ab wann das klar wurde.
2. Sprint-Scope reduzieren (Stories aus dem Sprint Backlog zurück ins Product Backlog).
3. Wenn auch der reduzierte Scope nicht trägt, Sprint formell abbrechen mit Begründung.
4. In Mentor-Kommunikation transparent machen.

Sprint-Abbrüche sind kein Versagen, sondern Anwendung der Adaption-Säule. Die Retrospektive deckt die Ursache auf und der Backlog wird repriorisiert.

---

## 9. Stakeholder-Reviews und Mentor-Termine

### 9.1 Verhältnis Sprint Review zu Mentor-Termin

Wichtig: Sprint Review (Abschnitt 3.4) und Mentor-Termin sind **zwei separate Events** mit unterschiedlichem Zweck.

| Event | Wann | Wer | Zweck |
|---|---|---|---|
| Sprint Review | Letzter Tag jedes Sprints | Studierender allein (Selbst-Inspektion) | Akzeptanzkriterien und DoD pro Story prüfen, Backlog aktualisieren |
| Mentor-Termin | Drei feste Termine pro Semester | Studierender plus Fach-Experte plus Projektmanagement-Experte | Externes Feedback zu Architektur, PQC-Anwendung, Scrum-Praxis, offene Fragen klären |

Sprint Reviews finden also häufiger statt (etwa alle 2 Wochen), Mentor-Termine sind seltener und externe Stakeholder-Reviews mit höherem Anspruch an Vorbereitung.

### 9.2 Geplante Mentor-Termine

| Termin | Datum | Sprint-Phase | Fokus |
|---|---|---|---|
| Mentor 1:1 #1 | 01.06.2026 (bestätigt) | Start Sprint 2 | Rückblick auf Sprint 0 (Architektur-Entscheidung), Sprint 1 (Skeletons plus Local Auth), Vorausblick Sprint 2 (Federation plus TLS) |
| Mentor 1:1 #2 | noch zu definieren | Vermutlich Mitte/Ende Sprint 3 | App-Layer-PQ-Session-Demo, Algorithmus-Wechsel-Demo, Bericht-Struktur |
| Mentor 1:1 #3 | noch zu definieren | Vermutlich Anfang/Mitte Sprint 4 oder Vor-Abgabe | Bericht-Review, Schlusspräsentations-Probe, letzte fachliche Klärungen |
| Abgabe-Kolloquium | 04. bis 05.07.2026 | Ende Sprint 4 | Komplette Demo, Schlussbericht, Schlusspräsentation |

Die noch zu definierenden Mentor-Termine 2 und 3 werden in den nächsten Tagen mit den Experten abgestimmt und dann in diesem Dokument nachgetragen.

### 9.3 Vorbereitung pro Mentor-Termin

Vor jedem Mentor-Termin wird ein kurzes Status-Dokument (1 bis 2 Seiten) erstellt, anhand des Templates `mentor_meeting_template.md` mit:

- Was wurde seit letztem Termin abgeschlossen
- Was läuft aktuell
- Welche offenen Fragen oder Risiken
- Eine 5-Minuten-Live-Demo des aktuellen Stands

Das deckt die Bewertungs-Kriterien rund um Kommunikation (A2.7 Berichte verfassen, A2.4 Präsentation) ab.

### 9.4 Eingehendes Feedback

Feedback aus Mentor-Terminen wird:

- Im Sprint-Tagebuch als Eintrag dokumentiert
- Bei Bedarf in den Backlog als neue Stories überführt
- In der nächsten Retrospektive reflektiert

---

## 10. Mapping zu Handlungskompetenzen und Bewertungskriterien

### 10.1 PRJ2-Handlungskompetenzen (Modul Projektmanagement)

Die relevanten Kompetenzen aus `Projekmanagement-erwartete-Handlungskonpetenzen.md`:

| Kompetenz | Scrum-Element, das sie abdeckt | Konkrete Artefakte/Praxis in dieser Arbeit |
|---|---|---|
| B5.1: ICT-Projekte selbständig planen und steuern (KN:3) | Sprint-Plan, Backlog-Pflege, Sprint Planning | Dieses Dokument, `09_product_backlog.md`, Jira-Sprints, Sprint-Planning-Templates |
| B5.4: Risikoanalyse durchführen und in Planung berücksichtigen (KN:3) | Risiko-Liste plus Risikoreserve im Sprint-Plan, Retro-Reflexion | Risk Register in Phase 4 dieses Setups (separat erstellt) |
| B5.5: Initiative und Kreativität bei Gestaltung, Durchsetzungsvermögen bei Durchführung (KN:3) | Eigenständige Architektur-Entscheidungen (Option 2 plus Identity Broker), eigene Crypto-Agility-Architektur | `03_entscheidung_auth_architektur.md`, Crypto-Abstraction-Layer |
| B5.7: Ausweichpläne für potenzielle Umsetzungsprobleme entwickeln (KN:3) | Sprint-Abbruch-Eskalation, Stretch-Goal-Trennung, Code-Freeze-Datum, Container-Build-Strategie aus Pre-Built-Image | Abschnitt 8.5, `06_tech_stack.md` Build-Begründung |
| B5.8: Verhältnis zwischen Kosten und Terminen optimieren (KN:2) | Scope-Reduktion bei Sprint-Engpässen, T-Shirt-Sizing | Abschnitt 7 und 8.5 |
| B5.9: Dokumente für Projektfortschritts-Überwachung erstellen und pflegen (KN:3) | Sprint-Tagebücher, Reviews, Retros, Jira-Board, Mentor-Status-Dokumente | Abschnitt 3.3 bis 3.5, 9.3, Sprint-Journal-Templates |
| B5.10: ICT-Projekte termin- und budgetgerecht in Übereinstimmung mit Anforderungen abschliessen (KN:3) | DoD plus Sprint-Goal plus Backlog-Linking zu Requirements | Abschnitt 5.3, 6, 4.1 |
| A2.1 bis A2.7: Kommunikation sachlich und adressatengerecht | Sprint-Reviews, Mentor-Termine, Schlussbericht | Abschnitt 9, separater Schlussbericht (Sprint 4) |

### 10.2 Bewertungs-Kriterien aus Merkblatt-A

| Bewertungs-Kriterium | Scrum-Beitrag in dieser Arbeit |
|---|---|
| 1. Substanz, Aufbau des Inhalts | Klare Dokumenten-Struktur, Inhaltsverzeichnis, Verweise zwischen Dokumenten (`05_requirements`, `07_design`, dieses Dokument, `09_product_backlog`) |
| 2. Darstellung der Theorie | Verweis auf Scrum Guide 2020 und TBZ-Theorie-Dokument als normative Quellen; Theorie wird nicht dupliziert, sondern angewendet |
| 3. und 4. Verknüpfung von Theorie und Praxis | Solo-Scrum-Adaption (Abschnitt 2) und Event-Anpassungen (Abschnitt 3) zeigen explizit, wie Theorie auf den konkreten Kontext übertragen wird; Mapping-Tabellen in Abschnitt 10 schaffen Theorie-Praxis-Brücke |
| 5. Reflexionstiefe | Limitations-Tabelle in 2.4, Sprint-Retros (3.5), kritische Reflexion über Solo-Scrum statt Verstecken |
| 6. Kolloquium | Schluss-Präsentation in Sprint 4 plus Mentor-Termine als Trainings-Reviews |

### 10.3 Anforderungs-Niveau

Die anvisierte Bewertungs-Stufe für Projektmanagement-Kompetenzen ist **Kompetenz professionellen Handelns (KN:3)**: neue komplexe Aufgaben in nicht vorhersehbarem Arbeitskontext, autonomes Planen, Handeln und Evaluieren. Solo-Scrum-Adaption mit ehrlicher Limitations-Reflexion ist eine bewusste Entscheidung in diese Richtung; reines Abarbeiten eines Standard-Templates wäre nur Novizen- oder fortgeschrittene Kompetenz.

---

## 11. Tooling

### 11.1 Jira Cloud Free

Die Backlog- und Sprint-Pflege erfolgt in Jira Cloud Free (Team-managed Scrum-Template). Begründung:

- Industrie-Standard, deckt PRJ2-Lerninhalte ab
- Free-Tier reicht für eine Person (Limit 10 User, 2 GB Storage)
- Bietet Sprint-Board, Backlog-View, Burndown-Chart, Reports
- Mentoren können per Guest-Link Zugriff bekommen

Setup-Schritte werden separat in `10_jira_setup.md` dokumentiert. Wichtige Konfigurations-Entscheidungen:

- Custom Fields: Story Points, Sprint, Akzeptanzkriterien, Bezug zu Requirement
- Workflow: To Do, In Progress, In Review (Self-Demo), Done
- Releases/Versionen: Mentor-Termine und Abgabe als feste Releases

### 11.2 Git (GitHub)

Repo dient als Single Source of Truth für Code und Dokumentation. Commits referenzieren wo sinnvoll Jira-Story-IDs (z.B. `PQC-15: implement local auth endpoint`).

### 11.3 MS Teams Kanal

Offizieller Kommunikations-Kanal für Mentor-Feedback laut Merkblatt-A. Mentor-Status-Dokumente und Demo-Recordings werden dorthin geteilt.

### 11.4 Sprint-Journal (Markdown)

Der Ordner `../sprint_journal/` enthält Templates und ausgefüllte Sprint-Dokumente. Struktur:

- `_templates/` mit Vorlagen für Planning, Daily Journal, Review, Retrospective, Mentor Meeting
- Pro Sprint ein Unterordner (`sprint_0/`, `sprint_1/`, etc.) mit den ausgefüllten Dokumenten
- `mentor_meetings/` für die zusätzlichen Mentor-Termine

Templates werden im Sprint Review gemeinsam mit dem Scrum-Master-Support (Claude in der aktuellen Session) ausgefüllt.

---

## 12. Versionsverlauf

| Version | Datum | Änderung |
|---|---|---|
| 1.0 | 17.05.2026 | Initial-Version. Solo-Scrum-Adaption mit Limitationen, angepasste Events (Tagesnotiz, Self-Demo, Reflexions-Eintrag), Artefakte und Commitments (Product Goal, Sprint Goal, DoD, DoR plus Akzeptanzkriterien separat), T-Shirt-Sizing-Methode, aktualisierter Sprint-Plan nach Sprint-0-Verzug, klare Trennung Sprint Review vs. Mentor-Termin, vollständiges Mapping zu PRJ2-Kompetenzen und Merkblatt-A-Bewertungskriterien. |
