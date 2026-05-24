# Status-Update Nr. 1 (vor Mentor-Termin am 01.06.2026)

**Format:** MS Teams Channel-Post für die Semesterarbeit
**Datum:** 24.05.2026
**Empfänger:** Fach-Experte (TBZ), Projektmanagement-Experte (TBZ)

---

## Post-Text (zum Kopieren in MS Teams)

**Erstes Status-Update Semesterarbeit "Implementing PQC"**

Liebe Experten

Entschuldigt das späte erste Update, ich hole das hiermit nach. Hier mein aktueller Stand.

**Projekt-Setup abgeschlossen (Sprint 0, 06.05 bis 24.05.2026)**

Sprint 0 habe ich als Setup- und Konzeptions-Phase genutzt. Folgende Deliverables sind fertig dokumentiert:

- Architektur-Entscheidung mit Begründung (Option 2: Custom Auth Service plus Identity-Broker-Pattern, "PQ-Uplift")
- Vollständige Requirements (Use Cases, Functional und Non-Functional Requirements, Traceability-Matrix)
- System-Design mit Komponenten-, Deployment- und Sequenz-Diagrammen
- Tech-Stack mit Versions-Pinning (FastAPI plus liboqs-python serverseitig, React Native Expo plus @noble/post-quantum clientseitig, nginx mit oqs-provider für hybrid TLS)
- Scrum-Setup mit Solo-Adaption
- Product Backlog (13 Epics, 63 Stories) komplett in Jira angelegt mit Story Points und Sprint-Zuweisung
- Risk Register mit 19 identifizierten Risiken und Mitigation/Contingency-Plänen
- Sprint-Journal mit Templates, Sprint-0-Review und -Retrospektive

**Scope-Anpassung und Optionen-Wahl**

In den ersten Tagen von Sprint 0 habe ich vertiefte Recherche zu NIST-PQC-Standards (FIPS 203, 204), zur Reife der relevanten Libraries (liboqs, @noble/post-quantum) und zu den Mobile-OS-Limitationen rund um TLS-Konfiguration durchgeführt. Dabei wurde mir klar, dass der initial angedachte Scope (klassisches OIDC mit aufgesetzter PQ-Signatur) zu wenig PQC-Substanz für eine Semesterarbeit mit dem Titel "Implementing PQC" liefern würde. Daraufhin habe ich drei Architektur-Optionen ausgearbeitet und bewertet:

- **Option 1 (Full OIDC Provider):** Vollständige OIDC-Provider-Implementation mit PQ-Token-Signaturen. Pro: standards-konform, breit einsetzbar. Contra: ~70-80% des Codes wäre OIDC-Boilerplate (Discovery-Endpoints, JWKS, Token-Endpoints, Consent-Screens), nur ~20% wären PQC-spezifisch. Geschätzter Aufwand 100-140h, Sprint-Crunch-Risiko zu hoch.
- **Option 2 (Custom Auth Service mit Identity-Broker, "PQ-Uplift"):** Eigenes Token-Format mit ML-DSA-65-Signatur, externe IdPs (Google, Microsoft) liefern Pre-Authentication, dann durchgehende PQ-Sphäre (ML-KEM-768 Session, AES-256-GCM Payload). Pro: ~60% des Codes ist PQC-spezifisch. Vertikale Tiefe (eine App, alle Layer post-quantum). Aufwand 70-100h, im Rahmen. Demonstriert ehrlich die realistische Übergangs-Architektur 2026. Contra: nicht voll standards-konform, Pre-Authentication-Teil mit Google/Microsoft bleibt klassisch (RS256), das wird im Bericht transparent als Limitation benannt.
- **Option 3 (OIDC-Lite):** Vereinfachter OIDC-Provider ohne volle Standards-Konformität. Mittelweg. Contra: zwischen den Stühlen, Komplexität von OIDC ohne klaren Standards-Vorteil, verwässert die Botschaft.

**Entscheidung Option 2.** Begründung: Der Projekttitel verlangt Tiefe in PQC, nicht Breite in OIDC. Option 2 maximiert den PQC-Anteil im Code und passt zeitlich in den verfügbaren Rahmen (Solo-Aufwand ca. 10-15h/Woche plus AI-Unterstützung als Multiplier). Der Identity-Broker-Pattern (klassische OIDC-Provider für Pre-Authentication, eigener Auth-Service für die PQ-Sphäre) wird im Bericht als "PQ-Uplift" beschrieben, also als realistische Übergangs-Architektur für die Phase 2026-2030, in der externe IdPs noch klassisch arbeiten.

Diese Entscheidung wurde am 08.05.2026 mit dem Dozenten besprochen und bestätigt. Das eingereichte Thema bleibt unverändert ("Implementing PQC"), kein Form-Wechsel nötig.

**Architektur in einem Satz**

Mobile-App (React Native Expo) plus Auth-Service (FastAPI hinter nginx). Externe IdPs (Google, Microsoft) für Pre-Authentication via klassisches OIDC. Anschliessend PQ-signierter Broker-Token (ML-DSA-65), App-Layer-Session via ML-KEM-768-Encapsulation, Payload-Verschlüsselung via AES-256-GCM. Crypto-Abstraction-Layer als Plugin-Registry für Algorithmen-Austauschbarkeit (Crypto-Agility).

**Sprint 1 (25.05 bis 31.05.2026)**

Sprint-Ziel: FastAPI- und Expo-Skeletons stehen, lokaler Login End-to-End mit ML-DSA-65-signiertem Broker-Token. Plus Carry-Over aus Sprint 0: GitHub-Repo final aufsetzen, Docker-Compose, oqs-provider-fähiges nginx-Image.

**Mentor-Termin Nr. 1 am 01.06.2026, was ich gerne diskutieren würde**

- Architektur-Review aus eurer Sicht, insbesondere die Identity-Broker-Entscheidung und die ehrliche Limitation des klassischen Pre-Auth-Teils
- PQC-Fragen: Bestätigung der ML-KEM-768 und ML-DSA-65 Anwendung und Parameter-Wahl gemäss FIPS 203 / 204
- Sprint-1-Code-Demo (was bis dahin steht)
- Prozess-Fragen zur Solo-Scrum-Anwendung

**Zugriff für euch**

- Jira-Projekt: https://rumidesigns.atlassian.net/jira/software/projects/PQC/backlog. Für Read-Access bitte ich um eure Atlassian-Account-Emails, dann lade ich euch ein.
- GitHub-Repository: ist angelegt, ich richte in den nächsten Tagen den finalen Setup und euren Zugriff ein. Link folgt sobald bereit.
- Die Markdown-Dokumente (Requirements, Design, Scrum-Setup, Risk Register, etc.) kann ich euch gerne als Bundle teilen, sagt mir welches Format euch passt (Direkt-Links oder PDF-Export).

Bei Fragen oder Anmerkungen vorab gerne Bescheid geben, sonst freue ich mich auf den Termin am 01.06.

Beste Grüsse
Dodoe Mannale

---

## Hinweise zum Versenden

- Vor dem Posten prüfen: Atlassian-Workspace `rumidesigns` ist öffentlich genug, dass Mentoren auch ohne Einladung den Backlog ansehen können (oder im Workspace-Settings öffentlich für Read).
- Wenn Mentoren-Emails bekannt sind: Atlassian "Invite people" Funktion nutzen, Role "Member" (Free-Tier-Limit 10 User ist nicht überschritten).
- Falls keine Atlassian-Accounts gewünscht: PDF-Export aus Jira via "..." Menü > "Export issues" als Backup.
- GitHub-Setup: Repo entweder privat mit Mentoren-Einladung, oder public mit klarer LICENSE.
- Nach dem Posten: Mentoren-Reaktion in Sprint-1-Daily-Journal als Erwähnung tracken, im Risk Register R-S05 (externe Abhängigkeiten) ggf. Status updaten.

## Format-Vorlage für zukünftige Updates

Dieser Post dient gleichzeitig als Vorlage für die regelmässigen Updates nach jeder Sprint-Retro (Top-3-Massnahme #3 aus Sprint-0-Retro). Folgende Struktur sollte beibehalten werden:

1. Anrede plus Kontext-Satz
2. "Sprint X abgeschlossen" mit Stichworten zum Delivery
3. "Sprint X+1" mit Ziel und Zeitfenster
4. Offene Fragen oder Bitten an Mentoren
5. Hinweis auf Mentor-Termin falls relevant
6. Zugriff-Infos falls Änderungen

Optional bei wichtigen Ereignissen: Architektur-Entscheidungen, Scope-Cuts, Risk-Eskalationen. Bei Erst-Updates oder grossen Scope-Änderungen: ausführliche Optionen-Bewertung wie in diesem Post.
