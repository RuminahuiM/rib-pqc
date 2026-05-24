# Implementing PQC

**Semesterarbeit 3, ITCNE25 (TBZ, dipl. Informatiker/in HF)**

**Autor:** Dodoe Rumiñahui Mannale
**Abgabe:** 04. bis 05.07.2026
**Status:** Sprint 1 (25.05 bis 31.05.2026)

---

## Worum geht's

End-to-End-Anwendung von Post-Quantum-Kryptografie (NIST-Standards FIPS 203 und FIPS 204) in einem realistischen Mobile-Auth-Szenario. Eine React-Native-App authentifiziert User entweder lokal oder via externe OIDC-Provider (Google, Microsoft), erhält einen ML-DSA-65-signierten Broker-Token von einem custom Auth-Service (FastAPI), etabliert eine ML-KEM-768-basierte Session und kommuniziert anschliessend AES-256-GCM-verschlüsselt mit dem Backend.

**Architektur-Pattern:** "Identity Broker mit PQ-Uplift", entwickelt nach Sprint-0-Optionen-Bewertung (siehe `docs/03_entscheidung_auth_architektur.md`). Klassische OIDC-Provider liefern Pre-Authentication, ab dem Broker-Token läuft die gesamte Kommunikation post-quantum.

**Crypto-Agility-Layer** als zentrales Architektur-Prinzip: Algorithmen sind als Plugins in einer Registry austauschbar, Algorithmus-Wechsel via Config statt Code-Diff.

---

## Repo-Navigation

| Verzeichnis | Inhalt |
|---|---|
| `docs/` | Alle Projekt-Dokumente: Architektur-Entscheidung, Requirements, Design, Tech-Stack, Scrum-Setup, Product Backlog, Jira-Setup, Risk Register, Traceability-Matrix |
| `sprint_journal/` | Sprint Reviews, Retrospektiven, Daily Journals, Templates, Mentor-Termin-Status-Dokumente |
| `tbz_resources/` | TBZ-Vorgaben (Merkblätter, Handlungskompetenzen, Scrum-Theorie-Dokument) |
| `server/` | Auth-Service (Python 3.12, FastAPI, liboqs-python) — ab Sprint 1 |
| `app/` | Mobile-App (React Native Expo, TypeScript, @noble/post-quantum) — ab Sprint 1 |
| `infra/` | Docker-Compose, nginx mit oqs-provider, Konfigurationsdateien — ab Sprint 0 bis 2 |
| `scripts/` | Demo- und Verifikations-Scripts (z.B. PQ-TLS-Handshake-Check) — ab Sprint 2 |

---

## Wo finde ich was

- **Architektur und Optionen-Bewertung:** `docs/03_entscheidung_auth_architektur.md`
- **Vollständige Requirements:** `docs/05_requirements.md`
- **System-Design (Diagramme, Datenmodell, Crypto-Layer):** `docs/07_design.md`
- **Scrum-Setup mit Solo-Adaption und Sprint-Plan:** `docs/08_scrum_setup.md`
- **Product Backlog (13 Epics, 63 Stories):** `docs/09_product_backlog.md`
- **Jira-Projekt-Mapping:** `docs/10_jira_setup.md`
- **Risk Register (19 Risiken):** `docs/11_risk_register.md`
- **Traceability-Matrix (UC zu Stories zu Sprints zu Bewertungs-Kriterien):** `docs/12_traceability_matrix.md`
- **Sprint-Review und -Retrospektive aktueller Sprint:** `sprint_journal/sprint_<N>/`
- **Mentor-Termin-Status-Updates:** `sprint_journal/mentor_meetings/`

---

## Aktueller Stand

- Sprint 0 (06.05 bis 24.05): Setup, Recherche, Architektur-Entscheidung, vollständige Doku und Planung abgeschlossen. 12 Markdown-Dokumente, 76 Jira-Issues (13 Epics, 63 Stories), Sprint-Journal-Templates aufgesetzt.
- Sprint 1 (25.05 bis 31.05): FastAPI- und Expo-Skeletons, lokaler Login End-to-End mit ML-DSA-65-Broker-Token. Plus Carry-Over: GitHub-Repo final aufsetzen, Docker-Compose, oqs-nginx-Image.
- Sprint 2 (01.06 bis 14.06): Federation (Google, Microsoft) und hybrid TLS am Server. Mentor 1:1 #1 am 01.06.
- Sprint 3 (15.06 bis 28.06): App-Layer PQ-Session, geschützter API-Call, Algorithmus-Wechsel-Demo. Code-Freeze 28.06.
- Sprint 4 (29.06 bis 05.07): Bericht, Benchmarks, Schlusspräsentation, Abgabe.

---

## Setup (vorläufig, wird mit Sprint 1 final ausgearbeitet)

Nachdem Sprint 1 die Skeletons aufgebaut hat, wird hier eine vollständige Setup-Anleitung dokumentiert. Bis dahin:

- Lokale Demo wird via Docker-Compose laufen: `docker compose up` aus dem Repo-Root.
- Auth-Service Python 3.12 plus FastAPI, Mobile-App via Expo Go.
- Lokale `.env`-Datei mit OIDC-Client-IDs und ML-DSA-Schlüssel-Pfaden (Beispiel in `infra/.env.example` ab Sprint 1).

---

## Kontakt

**Dodoe Mannale** — dodoe.mannale@heks.ch

**Mentoren (TBZ):** via MS Teams Channel "Semesterarbeit Implementing PQC"
