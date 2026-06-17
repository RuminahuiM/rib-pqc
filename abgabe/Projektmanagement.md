# Projektmanagement: Implementing Post-Quantum Cryptography in a Python Authentication Service

> **Semesterarbeit 3, ITCNE25** — Dodoe Rumiñahui Mannale (Einzelarbeit)
> **Abgabe:** 04./05.07.2026
> Dieses Dokument deckt die Projektmanagement-Komponente ab (Bewertungskriterien 1, 2, 3, 5). Die fachliche Umsetzung ist in [`Fachliche-Umsetzung.md`](./Fachliche-Umsetzung.md) dokumentiert.

> _Hinweis (Platzhalter, wird am Ende entfernt): Detailtiefe liegt in den verlinkten Tracking-Artefakten (Jira, `docs/`, `sprint_journal/`). Dieses Dokument bleibt schlank und gut lesbar._

---

## Inhaltsverzeichnis

1. [Einleitung](#1-einleitung)
2. [Projektmethodik](#2-projektmethodik)
3. [Planung](#3-planung)
4. [Durchführung](#4-durchführung)
5. [Risikomanagement](#5-risikomanagement)
6. [Reflexion und Lessons Learned](#6-reflexion-und-lessons-learned)
7. [Anhang und Verzeichnisse](#7-anhang-und-verzeichnisse)

---

## 1. Einleitung

### 1.1 Problemstellung

Klassische asymmetrische Kryptografie (RSA, ECC, ECDSA) und der ECDH-Schlüsselaustausch sind durch Shors Algorithmus auf ausreichend grossen Quantencomputern brechbar. Ein solcher Computer existiert 2026 noch nicht, doch die Bedrohung ist bereits real: Unter dem Stichwort "Harvest Now, Decrypt Later" zeichnen Angreifer heute verschlüsselten Verkehr auf, um ihn später, sobald ein ausreichend leistungsfähiger Quantencomputer verfügbar ist, vollständig zu entschlüsseln. Betroffen ist potenziell jeglicher aufgezeichnete TLS-Verkehr, von Chat-Verläufen über Finanztransaktionen und Gesundheitsdaten bis zu Authentifizierungs-Sessions. Besonders kritisch ist das für Daten, die über viele Jahre vertraulich bleiben müssen, denn sie sind heute schon angreifbar, auch wenn die Entschlüsselung erst in Zukunft gelingt.

Seit August 2024 sind mit FIPS 203 (ML-KEM), FIPS 204 (ML-DSA) und FIPS 205 (SLH-DSA) die ersten NIST-Standards final. Die industrielle Adoption steckt 2026 aber noch in einer frühen Phase, gerade im Bereich Mobile Authentication: Grosse Identity Provider stellen weiterhin klassisch signierte Tokens aus, und mobile Betriebssysteme erlauben keinen zuverlässigen Zugriff auf die TLS-Cipher-Suite-Aushandlung. Hier setzt diese Arbeit an.

### 1.2 Project Summary

Die Arbeit entwirft und implementiert einen Authentifizierungs-Microservice in Python (FastAPI), der die neuen NIST-Standards praktisch anwendet, demonstriert über eine bewusst minimale React-Native-App (Expo). PQC wirkt auf zwei Ebenen: server-seitig als hybrides PQ-TLS (X25519MLKEM768 hinter nginx mit oqs-provider) und auf Applikationsebene als PQ-Sitzungsschicht (ML-KEM-768 zur Schlüsselverkapselung, AES-256-GCM für Payloads, ML-DSA-65-signierte Tokens). Ergänzt wird dies durch ein Identity-Broker-Pattern, das klassische OIDC-Provider (Google, Microsoft) einbindet und deren Claims in eine PQ-sichere Session überführt ("PQ-Uplift"). Crypto-Agility ist durchgehendes Architektur-Prinzip: Algorithmen sind per Konfiguration austauschbar.

### 1.3 Stakeholder

| Stakeholder | Rolle | Hauptinteresse |
|---|---|---|
| Dodoe R. Mannale | Entwickler, Autor | Erfolgreicher Abschluss, Lerneffekt PQC, nutzbare Architektur-Erfahrung |
| Experten TBZ | Bewerter (PM und Fachlich) | Nachvollziehbare Architektur, dokumentierte Entscheidungen, korrekte Standard-Anwendung |
| Fiktive End-User | Persona | Einfacher Login, unsichtbare Verschlüsselung |
| Future Maintainer | Zukünftiger Entwickler | Verständliche, erweiterbare, algorithmus-agile Architektur |
| Externe IdP (Google, Microsoft) | OIDC-Quellen | Standardkonforme Client-Integration |

### 1.4 Ziele (SMART)

Die Ziele sind spezifisch, messbar, attraktiv, realistisch und terminiert (Abgabe 05.07.2026):

1. **Auth-Microservice mit PQ-Token.** FastAPI-Service mit Register/Login, der ML-DSA-65-signierte Tokens ausstellt. Messbar: pytest-Suite (mind. 20 Tests, >= 80 % Coverage auf Auth-Modulen), grüner CI-Lauf.
2. **Hybrides PQ-TLS server-seitig.** TLS-1.3-Endpoint mit X25519MLKEM768. Messbar: Verifikation per `openssl s_client` und in einem Browser, automatischer Check des NamedGroup-Werts `0x11ec`.
3. **End-to-End-PQ-Demo.** Expo-App durchläuft Login, etabliert ML-KEM-768-Session, ruft eine geschützte Ressource ab und entschlüsselt eine AES-GCM-Antwort. Messbar: E2E-Flow endet mit `200 OK` und korrekt entschlüsseltem Body.
4. **Identity-Broker mit PQ-Uplift.** Login via Google und Microsoft, Claims werden in eine PQ-sichere Session überführt. Messbar: erfolgreicher Login über beide externen Provider.
5. **Crypto-Agility.** KEM- und Signatur-Algorithmus per Config umschaltbar ohne Application-Code-Änderung. Messbar: Algorithmus-Wechsel nur über Konfiguration nachgewiesen.

### 1.5 Scope und Abgrenzung

Die Arbeit ist eine Schul-Semesterarbeit mit demonstrativem Charakter, kein Produktionssystem. Bewusst nicht im Scope sind: ein externes Security-Audit, eine Skalierungs- und Hochverfügbarkeits-Architektur, Self-Service-Funktionen für Nutzer (Selbstregistrierung, Passwort-Reset) sowie formale Compliance-Zertifizierungen wie DSGVO oder eIDAS. Ausserdem baut der Service keinen eigenen vollwertigen Identity-Provider: Statt die Anmeldung selbst von Grund auf zu implementieren, bindet er bestehende Anbieter wie Google und Microsoft als Broker ein (siehe 1.2). Das Vorgehen ist in Abschnitt 2 beschrieben.

> Fachbegriffe siehe [Glossar](./Fachliche-Umsetzung.md#glossar) in der fachlichen Dokumentation.

---

## 2. Projektmethodik

### 2.1 Warum Scrum

Das Projekt startet mit hoher Unsicherheit: Die NIST-Standards sind erst seit 2024 final, die Reife der Bibliotheken und die Grenzen mobiler Kryptografie sind zu Beginn unklar. Anforderungen und Architektur schärfen sich also erst während der Arbeit. Ein plangetriebenes Vorgehen wie Wasserfall oder IPERKA würde diese Unsicherheit zu früh einfrieren. Scrum mit seinen kurzen, iterativen Zyklen und der empirischen Steuerung (Transparenz, Inspektion, Adaption) passt deshalb besser und ist zugleich der im Modul PRJ2 vermittelte Standard. Die normative Theorie liegt im Scrum Guide 2020; dieses Dokument wendet sie an, statt sie zu wiederholen.

### 2.2 Solo-Scrum-Adaption

Die Arbeit ist eine Einzelarbeit, es gibt also kein klassisches Scrum-Team. Alle drei Verantwortlichkeiten liegen bei einer Person und werden bewusst getrennt eingenommen: als Developer (Umsetzung, Schätzung, tägliche Selbstorganisation), als Product Owner (Priorisierung nach Wert, hier Erfüllung der Bewertungskriterien plus Lerneffekt) und als Scrum Master (saubere Scrum-Anwendung, Prozess-Reflexion). Die beiden TBZ-Experten und die Lehrgangsleitung sind echte Stakeholder, aber nicht Teil des Teams.

Die Scrum-Events sind an die Solo-Situation angepasst:

| Event | Anpassung |
|---|---|
| Sprint | 2 Wochen (Ausnahmen Sprint 0 und 4) |
| Sprint Planning | Sprint-Ziel, Auswahl der Stories, Zerlegung in Tasks (Jira) |
| Daily Scrum | Ersetzt durch kurze Tagesnotiz pro Arbeitstag (max. drei Sätze) |
| Sprint Review | Selbst-Inspektion gegen Akzeptanzkriterien und DoD, plus separate Mentor-Termine als externe Reviews |
| Retrospektive | Reflexion über Produkt, Prozess und Selbstmanagement, liefert konkrete Massnahmen für den nächsten Sprint |

Solo-Scrum verliert bewusst einige Stärken des Frameworks (kein Peer-Review, keine echte Rollentrennung, statistisch unbrauchbare Velocity). Diese Limitationen werden offen benannt und mit Gegenmassnahmen versehen (Mentor-Termine als externe Reviews, schriftliche Architektur-Entscheidungen, ehrliche Retrospektiven). Die ausführliche Limitations-Tabelle steht in [`../docs/08_scrum_setup.md`](../docs/08_scrum_setup.md).

### 2.3 User Stories, Akzeptanzkriterien und Definition of Done

Gearbeitet wird mit User Stories im Format "Als Rolle möchte ich Funktion, damit Nutzen", rein technische Stories mit begründeter technischer Beschreibung. Jede Story hat mindestens zwei nachprüfbare Akzeptanzkriterien (fachliche Korrektheit dieser einen Story) und muss zusätzlich die projektweite Definition of Done erfüllen (Qualitäts-Latte für alle Stories). Eine Story ist erst "done", wenn beides erfüllt ist.

Kern der Definition of Done: Code im main-Branch mit nachvollziehbaren Commits, automatisierter Test für funktionale Backend-Änderungen, erfüllte Akzeptanzkriterien, aktualisierte Doku, Quellenangabe für fremden Code, eine Evidence-Datei im Sprint-Journal (ab Sprint 1 pro Story geführt) und die Jira-Story auf "Done" mit strukturiertem Abschluss-Kommentar. Eine Evidence-Datei ist dabei eine kurze, in diesem Projekt eingeführte Markdown-Notiz pro Story, die belegt, wie jedes Akzeptanzkriterium erfüllt wurde (mit Test-Ausgabe, Screenshots und Begründung bewusster Abweichungen). Sie erlaubt den Experten, das Gelieferte nachzuvollziehen, ohne den Code durchgehen zu müssen. Eine Definition of Ready dient als Eingangslatte fürs Planning.

### 2.4 Schätzung

Geschätzt wird relativ mit T-Shirt-Sizes (XS bis XL), abgebildet auf Story Points der Fibonacci-Folge. Absolute Stundenschätzungen wären bei einem einzelnen Entwickler zu optimistisch, und die Velocity ist statistisch kaum belastbar; deshalb dient zusätzlich die tatsächliche Wochenkapazität als grobe Richtgrösse für die Planung.

Eine Besonderheit dieses Projekts: Die Schätzungen sind bewusst als klassische Solo-Schätzung ohne AI-Unterstützung dokumentiert, während tatsächlich mit AI-Unterstützung gearbeitet wird. Pro Story wird die tatsächlich benötigte Arbeitszeit erfasst. Am Projektende lassen sich so die Schätzung (ohne AI) und der reale Aufwand (mit AI) vergleichen, woraus sich ablesen lässt, wie stark die AI-Unterstützung die Arbeit beschleunigt hat. Diese Auswertung fliesst in die Reflexion (Abschnitt 6) ein.

### 2.5 AI-gestützter Arbeitsablauf

Ich führe die Arbeit durchgehend mit AI-Unterstützung (Claude und Claude Code) durch und lege das hier offen. Der Einsatz ist in zwei getrennte Arbeitsstränge gegliedert: einen für Planung, Prozess und Reflexion (in der Scrum-Master-Perspektive) und einen für die technische Umsetzung (in einer Senior-Engineer-Perspektive). So bleiben Projektsteuerung und Implementierung sauber getrennt.

Die AI hat nicht nur beim Programmieren geholfen, sondern bereits in der Konzeptphase: Das Requirements Engineering ([`../docs/05_requirements.md`](../docs/05_requirements.md)), die Architektur-Entscheidung für den Identity-Broker-Ansatz ([`../docs/03_entscheidung_auth_architektur.md`](../docs/03_entscheidung_auth_architektur.md)), die Tech-Stack-Wahl ([`../docs/06_tech_stack.md`](../docs/06_tech_stack.md)) und das System-Design ([`../docs/07_design.md`](../docs/07_design.md)) sind im Dialog mit der AI entstanden. Sie diente dabei als eine Art Sparringspartner, mit dem ich Optionen gegeneinander abwägen, eigene Annahmen hinterfragen und blinde Flecken aufdecken konnte, bevor ich eine Entscheidung traf. In der Umsetzungsphase kamen Code-Generierung und Refactoring, ergänzende Code-Reviews (als Ersatz für das im Solo-Setup fehlende Vier-Augen-Prinzip) sowie Hilfe beim Formulieren dieser Dokumentation dazu.

Die Verantwortung liegt bei mir: Jede AI-Ausgabe prüfe, teste und verstehe ich, bevor ich sie übernehme; Akzeptanzkriterien und Definition of Done sind die Kontrollinstanz. Den dadurch entstehenden Effizienzgewinn messe ich über den in 2.4 beschriebenen Vergleich.

---

## 3. Planung

### 3.1 Roadmap und Releases

Jeder Sprint mündet in ein nutzbares Increment. Die drei geforderten Release-Stufen sind an die Meilensteine gebunden:

| Release | Bedeutung | Zeitpunkt | Inhalt |
|---|---|---|---|
| MVP (Minimum Viable Product) | Früh Feedback einholen | Ende Sprint 1 | Lokaler Login funktioniert End-to-End mit ML-DSA-signiertem Token |
| MLP (Minimum Lovable Product) | Qualität und Stabilität | Ende Sprint 3 | Vollständige PQC-Kette: Federation, hybrides PQ-TLS, PQ-Session und verschlüsselter Datenkanal |
| MMP (Minimum Marketable Product) | Abgabe und Präsentation | Ende Sprint 4 | Dokumentation, Benchmarks, Politur, Schlusspräsentation |

### 3.2 Gantt-Chart

> TODO: Sauberer, manuell erstellter Gantt-Chart mit Sprints, Releases (MVP/MLP/MMP) und Meilensteinen (Mentor-Termine, Code-Freeze, Abgabe). Wird später eingefügt.

### 3.3 Backlog-Struktur

Das Backlog ist in 14 Epics mit insgesamt 69 Stories gegliedert (Stand nach den Sprint-1- und Sprint-2-Reviews). Die Epics bilden die Architektur-Bausteine ab, von der Infrastruktur über den Crypto-Abstraction-Layer, lokale Authentifizierung, Token-Service, Identity-Broker, hybrides TLS, PQ-Session und Datenkanal bis zur Mobile-App, Qualitätssicherung und Dokumentation. Die Reihenfolge folgt den Abhängigkeiten (Bottom-up: erst die Grundlagen, dann der Aufbau) und dem Risiko (riskante Stories früh, damit Lernen und Umplanung möglich bleiben). Das vollständige Backlog steht in [`../docs/09_product_backlog.md`](../docs/09_product_backlog.md), die Live-Version in Jira.

### 3.4 Priorisierung (MoSCoW)

Priorisiert wird mit MoSCoW. Die Verteilung:

| Priorität | Stories | Story Points (ca.) |
|---|---|---|
| Must | 59 | 212 |
| Should | 7 | 22 |
| Could (Stretch) | 3 | 18 |
| Total | 69 | 252 |

Die hohe Must-Quote spiegelt die enge Verzahnung der Architektur-Komponenten: Fällt etwas weg, dann am ehesten App-Politur (z.B. Profile-Screen-Detail) oder Stretch-Goals. Ergänzend zu MoSCoW steuern drei weitere Achsen die Reihenfolge (Sprint-Zuordnung, Stretch-Markierung, Jira-Priority-Feld); Details in [`../docs/09_product_backlog.md`](../docs/09_product_backlog.md).

### 3.5 Kapazität und Schätzung

Die geplante Story-Point-Last liegt in allen Sprints bewusst über der klassischen Solo-Kapazität, weil die Schätzungen ohne AI-Unterstützung dokumentiert sind (siehe 2.4). Sprint 1 wurde gezielt als Mess-Experiment genutzt: geplant 41 Punkte auf 7 Tage, tatsächlich in rund 13,5 Stunden abgeschlossen. Diese empirischen Werte fliessen in die Sprint-Planung der Folge-Sprints und in die Reflexion (Abschnitt 6) ein.

---

## 4. Durchführung

> **Worum es geht:** Sprint-Überblick (Planning, Review, Retro je Sprint), Kommunikation mit Dozierenden, Mentor-Meetings.
> **Vorgaben:** Kriterium 3 (Verknüpfung Theorie-Praxis formell), dokumentiertes Planning/Review/Retro, proaktive Stakeholder-Kommunikation, sichtbare Projektentwicklung über die Zeit.
> **Datenquellen:** `sprint_journal/sprint_0..2/` (01_planning, 03_review, 04_retrospective), `sprint_journal/mentor_meetings/`, Jira.

_(Inhalt folgt im sequenziellen Review.)_

---

## 5. Risikomanagement

> **Worum es geht:** Risiko-Matrix plus daraus abgeleitete, ausgearbeitete Maßnahmen.
> **Vorgaben:** Risikoanalyse und -management (B5.4, B5.7), Risiko-Matrix mit echtem Zweck statt reiner Grafik.
> **Datenquellen:** `docs/11_risk_register.md`.

_(Inhalt folgt im sequenziellen Review.)_

---

## 6. Reflexion und Lessons Learned

> **Worum es geht:** Projektmanagement-seitige Reflexion, abgewogene Entscheidungen, eigene Erfahrungen, Vorbehalte.
> **Vorgaben:** Kriterium 5 (Reflexionstiefe): Aussagen hinterfragen, Varianten abwägen, eigene Erfahrungen einbringen, Erkenntnisse aufzeigen.
> **Datenquellen:** `sprint_journal/*/04_retrospective.md`, `docs/13_deferred_findings.md`.

_(Inhalt folgt im sequenziellen Review.)_

---

## 7. Anhang und Verzeichnisse

> **Worum es geht:** Zentrale Sammlung aller Referenzen (Jira-Epics, Sprint-Artefakte, Evidence), Abbildungsverzeichnis, Tabellenverzeichnis.
> **Vorgaben:** Kriterium 1 (Verzeichnisse vorhanden), Beschriftung aller Bilder und Tabellen.

> Das gemeinsame Glossar für beide Dokumente liegt im [Anhang der fachlichen Dokumentation](./Fachliche-Umsetzung.md#glossar).

_(Inhalt folgt im sequenziellen Review.)_
