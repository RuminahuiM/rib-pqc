# Status-Update Nr. 1 (vor Mentor-Termin am 01.06.2026)

**Format:** MS Teams Channel-Post für die Semesterarbeit
**Datum:** 24.05.2026
**Empfänger:** Fach-Experte (TBZ), Projektmanagement-Experte (TBZ)

---

## Post-Text (versendet am 24.05.2026)

**Erstes Status-Update Semesterarbeit "Implementing PQC"**

Hallo zusammen

Sorry, dass das erste Update so spät kommt. Leider habe ich für die Planung etwas länger gebraucht als gedacht. Hier mein aktueller Stand.

**Was in Sprint 0 (06.05 bis 24.05) passiert ist**

Diese Phase habe ich für Recherche und Planung genutzt. Im Einreichungsformular war noch keine OIDC-Integration geplant. Während der Recherche habe ich aber gemerkt, dass ich dem Projekt einen höheren Wiederverwendbarkeitswert geben möchte, also dass es einer realen Anwendung näher kommt und nicht nur ein reines Lern-Beispiel bleibt.

Zuerst dachte ich, ich baue dafür selbst einen OIDC-Provider. Habe dann aber relativ schnell gemerkt, das macht eigentlich keinen Sinn, weil es schon genug grosse Anbieter wie Google oder Microsoft gibt und kaum jemand einen weiteren OIDC-Provider braucht. Durch weitere Recherche bin ich auf das Identity-Broker-Pattern gestossen, das in der Industrie auch so eingesetzt wird. Ich habe drei Varianten gegeneinander abgewogen:

1. **Eigener Full OIDC Provider mit PQ-Signaturen.** Etwa 70 bis 80 Prozent des Codes wäre OIDC-Boilerplate, nur ein kleiner Teil wirklich PQC. Praktischer Nutzen gering, weil die grossen Anbieter den Markt eh abdecken. Aufwand über 100 Stunden, zu viel für meinen Zeitrahmen.
2. **Identity Broker mit "PQ-Uplift" (gewählt).** Mein eigener Auth-Service stellt PQ-signierte Tokens aus. Google und Microsoft werden weiter für die Anmeldung selbst genutzt (klassisch, weil sie 2026 noch nichts anderes anbieten), aber ab dem Token läuft alles post-quantum: ML-DSA-65 für die Signatur, ML-KEM-768 für die Session-Keys, AES-256-GCM für die Payloads. Damit ist etwa 60 Prozent des Codes wirklich PQC, das Pattern entspricht der gängigen Industrie-Praxis, der Aufwand passt in den Plan und das Projekt fühlt sich nicht weiter aufgebläht an.
3. **Reines Anwendungs-Beispiel gemäss Einreichungsformular.** Schien für mich mehr ein Fallbeispiel als ein wirklich brauchbares Endprodukt zu erzeugen.

Fertig dokumentiert sind in Sprint 0: Architektur-Entscheidung mit Begründung, Anforderungen, System-Design, Tech-Stack, Scrum-Setup mit Solo-Adaption, Product Backlog (13 Epics, 63 Stories in Jira), Risk Register und Traceability-Matrix.

**Hinweis zur Arbeitsweise**

Ich arbeite stark mit AI-Unterstützung (Claude). Die bisherigen Dokumente sind in stark kontrollierter Zusammenarbeit entstanden, also kein generischer AI-Output, sondern jeder Schritt bewusst geprüft und gesteuert. Auf mein konkretes Vorgehen mit AI inklusive Lehren und Limitationen werde ich in der finalen Projekt-Dokumentation eingehen.

**Sprint 1 (24.05 bis 31.05) läuft seit heute**

Ziel: FastAPI- und Expo-Skeletons stehen, plus lokaler Login mit ML-DSA-signiertem Broker-Token. Dazu Carry-Over aus Sprint 0: Docker-Compose-Setup und oqs-fähiges nginx-Image.

**Zwischengespräch am 01.06, gerne besprechen würde ich:**

- Architektur-Review
- Demo vom Sprint-1-Code, soweit bis dahin steht

**Zugriff für euch:**

- GitHub-Repo: https://github.com/RuminahuiM/rib-pqc. Wichtig: das Repo dient mir als zentrale Ablage für alle Projekt-Daten (Doku, Code, Sprint-Journal, etc.), weil das die Arbeit mit AI deutlich vereinfacht. Es ist nicht die finale Projekt-Dokumentation, die werde ich später mit dem Portfolio-Template aus dem letzten Semester aufsetzen. Aktuelle Struktur:
  - `docs/` hat alle Projekt-Dokumente
  - `sprint_journal/` hat Sprint-Reviews und Retros
  - `tbz_resources/` hat die TBZ-Vorgaben (damit Claude diese nachschauen kann)
  - `server/`, `app/`, `infra/`, `scripts/` sind aktuell leer und kommen mit Sprint 1
  - `README.md` am Top-Level als Wegweiser
- Jira-Projekt: https://rumidesigns.atlassian.net/jira/software/projects/PQC/backlog.

Ihr solltet bereits Einladungen für die Zugriffe per E-Mail erhalten haben. Falls irgendwas nicht funktioniert, gebt mir bitte eine kurze Rückmeldung.

Grüsse Dodoe

---

## Hinweise zum Versenden

- Vor dem Posten prüfen: GitHub-Repo `rib-pqc` ist gepusht (`git push -u origin main`) und entweder public oder mit Mentor-Zugriff (Settings > Collaborators).
- Atlassian-Workspace `rumidesigns`: prüfen ob Backlog public-read ist oder ob Einladungen nötig sind.
- Wenn Mentoren-Emails bekannt sind: Atlassian "Invite people" Funktion nutzen, Role "Member" (Free-Tier-Limit 10 User ist nicht überschritten). Für GitHub: Repo-Settings > Manage access.
- Falls keine Atlassian-Accounts gewünscht: CSV-Export aus Jira via "..." Menü > "Export issues" als Backup.
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
