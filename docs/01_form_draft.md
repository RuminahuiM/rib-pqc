# Einreichungsformular — Inhaltlicher Entwurf

> **Status:** Entwurf zur Review. Sobald du das hier abgesegnet (oder geändert) hast, übertrage ich den Inhalt 1:1 in die `.docx`.
> **Klasse:** ITCNE25 — 3. Semesterarbeit
> **Heutiges Datum:** 03.05.2026 — Abgabe: 04./05.07.2026

---

## Name und Vorname des Studierenden

Mannale, Dodoe Rumiñahui (Einzelarbeit)

## Titel der Semesterarbeit

**Implementing Post-Quantum Cryptography in a Python Authentication Service**
*A FastAPI-based microservice with FIPS-204 / FIPS-203 authentication and hybrid post-quantum TLS, demonstrated by a React-Native (Expo) client.*

## Zu behandelnde Themenfelder / Module

- [x] **Projektmanagement** (Corrado Parisi) — *Pflicht, bereits markiert*
- [x] **Microservices mit Python** (Boris Langer) — *anzukreuzen*

> *Hinweis:* Die Bewertungstabelle in Tabelle 2 nennt "Themenfelder (mindestens zwei!)". Wir markieren genau zwei (Pflicht + Microservices). Falls dein Dozent doch einen weiteren möchte, wäre **Netzwerk** (Martin Iten, TLS/PQC-Kontext) der natürliche Kandidat.

---

## Kurzbeschreibung des Zertifikatsarbeit Themas (1 – max. 2 Seiten)

Quantencomputer bedrohen die Vertraulichkeit und Authentizität heutiger TLS-Verbindungen. Die in TLS 1.3 verwendeten klassischen Verfahren — RSA, ECDSA und der ECDH-Schlüsselaustausch über Kurven wie X25519 — sind durch den Algorithmus von Shor in polynomialer Zeit auf ausreichend grossen Quantencomputern brechbar. Auch wenn ein "kryptografisch relevanter" Quantencomputer nach heutigem Stand noch nicht existiert, ist die "Harvest Now, Decrypt Later"-Bedrohung real: heute aufgezeichneter Verkehr kann später entschlüsselt werden, sobald die Hardware bereit ist.

Im August 2024 hat das amerikanische NIST drei Standards für quantenresistente Kryptografie finalisiert: **FIPS 203 (ML-KEM)**, abgeleitet aus CRYSTALS-Kyber, für den Schlüsselaustausch; **FIPS 204 (ML-DSA)**, abgeleitet aus CRYSTALS-Dilithium, für digitale Signaturen; und **FIPS 205 (SLH-DSA)**, ein hash-basiertes Signaturverfahren als Backup. Auf TLS-Ebene definiert der IETF-Draft `draft-ietf-tls-ecdhe-mlkem-04` (Februar 2026) hybride Schlüsselagreement-Mechanismen wie *X25519MLKEM768* — dieses Verfahren wird seit Chrome 131 (Nov 2024), Firefox 132, Edge 131, OpenSSL 3.5 (April 2025) und Go 1.24 (Februar 2025) standardmässig ausgehandelt. Bei der Authentifizierung über Zertifikate ist `draft-ietf-tls-mldsa-01` für ML-DSA-Signaturen der aktuelle Stand; öffentliche Zertifizierungsstellen beginnen 2026 erst mit dem produktiven Rollout.

Diese Arbeit baut einen **Python-Microservice für Authentifizierung**, der diese neuen Standards praktisch anwendet. Zur Demonstration wird eine bewusst einfach gehaltene **React-Native-App (Expo Go)** gegen den Service authentifiziert. Architektonisch teilt sich PQC dabei auf zwei Ebenen auf:

1. **Transportebene (Server-seitig):** Der Auth-Microservice (FastAPI + Uvicorn) wird hinter einem nginx-Reverse-Proxy mit dem `oqs-provider`-Plugin für OpenSSL 3 betrieben. nginx terminiert TLS 1.3 mit hybridem Schlüsselaustausch *X25519MLKEM768*. Das Server-Zertifikat bleibt vorerst ECDSA, da öffentliche CAs ML-DSA noch nicht ausstellen — als Erweiterung wird zusätzlich ein selbstsigniertes ML-DSA-Zertifikat aus einer Test-CA bereitgestellt und mit `openssl s_client` und einem Browser verifiziert.

2. **Applikationsebene (App ↔ Backend):** Da React Native auf iOS und Android nicht über die OS-eigene TLS-Stack hinaus PQ-Cipher-Suites aushandeln kann, ergänzt die App eine PQC-Sitzungsschicht in JavaScript: **ML-KEM-768 Schlüsselverkapselung** mit `@noble/post-quantum` zur Etablierung eines symmetrischen Sitzungsschlüssels, mit dem Anfragebodies AES-GCM-verschlüsselt werden. **Authentifizierungstoken werden serverseitig mit ML-DSA-65 signiert** (analog zu JWT, aber mit FIPS-204-Signatur statt RS256/ES256). So entsteht ein "Defense in Depth"-Ansatz: PQ auf der TLS-Ebene wo möglich, plus PQ auf der Applikationsebene als Absicherung gegenüber Geräten, die noch keine PQ-TLS-Aushandlung unterstützen.

Das Projekt ist als Einzelarbeit konzipiert, wird in Scrum mit Jira als Backlog-Tool durchgeführt und folgt den Prinzipien sauberer Microservice-Architektur (FastAPI, asyncio, Pydantic, Docker). Schwerpunkt ist nicht die App, sondern der Authentifizierungs-Microservice und die saubere, dokumentierte Integration der drei NIST-Standards in eine moderne Web-Architektur.

---

## Problemstellung / Ausgangslage / Potential der Semesterarbeit

Klassische TLS-Verfahren (RSA, ECDSA, ECDH/X25519) sind durch Shor's Algorithmus auf ausreichend grossen Quantencomputern angreifbar. Die "Harvest Now, Decrypt Later"-Bedrohung zwingt Organisationen, schon heute zu PQC zu migrieren — selbst wenn ein praxistauglicher Quantencomputer erst in zehn oder mehr Jahren entsteht. NIST hat im August 2024 mit FIPS 203/204/205 die ersten Standards finalisiert; die IETF arbeitet aktiv an deren Integration in TLS 1.3. Browser-, Server- und Cloud-Stacks (Chrome, Firefox, OpenSSL, AWS, Cloudflare) haben hybride PQ-Verfahren wie X25519MLKEM768 bereits standardmässig aktiviert. Die Zertifikatsarbeit setzt genau hier an: einen praxisnahen, messbaren Auth-Microservice zu bauen, der die neuen Standards anwendet und so das Migrationswissen produziert, das Schweizer Banken, Versicherungen und KRITIS-Betreiber in den kommenden Jahren brauchen.

**SMORE-Selbstcheck:**

- **Ambitioniert** — PQC ist Cutting-Edge; die NIST-Standards sind erst 18 Monate alt, IETF-Drafts noch nicht final. Es gibt wenig fertige Tutorials, viel Eigenarbeit nötig.
- **Motivierend** — Persönliches Interesse an Sicherheitsarchitektur und Kryptografie; klarer Praxiswert für meinen späteren Berufseinsatz.
- **Organisiert** — Alle Werkzeuge (liboqs, oqs-provider, FastAPI, Expo, Jira, OpenSSL 3.5, nginx) sind quelloffen und auf eigener Hardware lauffähig.
- **Realistisch** — Scope auf den Auth-Microservice fokussiert, App ist bewusst minimal; 9 Arbeitssessions + 1 Vier-Tage-Block ergeben ~18 Arbeitstage.
- **Echt** — Direkter Bezug zum Modul "Microservices mit Python" und zum Querschnittsmodul "Projektmanagement".

---

## Zielsetzung der Semesterarbeit (mindestens drei messbare Ziele)

1. **Funktionierender Auth-Microservice mit PQ-Komponenten.** Ein in Python (FastAPI) implementierter Microservice, der `POST /auth/register` und `POST /auth/login` anbietet und nach erfolgreichem Login ein mit **ML-DSA-65 (FIPS 204) signiertes Sitzungstoken** zurückgibt. *Messbar:* automatisierte pytest-Tests (mind. 20 Tests, ≥ 80 % Code-Coverage auf den Auth-Modulen), grüner CI-Lauf in GitHub Actions.

2. **Hybrides PQ-TLS auf der Server-Seite.** Der Microservice ist hinter nginx mit `oqs-provider` so konfiguriert, dass eine TLS-1.3-Verbindung mit der hybriden Schlüsselgruppe **X25519MLKEM768** aufgebaut werden kann. *Messbar:* Verifikation per `openssl s_client -groups X25519MLKEM768 -connect ...`, in mindestens einem Browser (Chrome ≥ 131 oder Firefox ≥ 132), und ein automatisiertes Test-Skript prüft, dass der ausgehandelte NamedGroup-Wert `0x11ec` (X25519MLKEM768) ist.

3. **End-to-End-Demo mit React-Native-App.** Eine Expo-App führt einen Login-Flow durch, etabliert per `@noble/post-quantum` (**ML-KEM-768**) einen Sitzungsschlüssel, ruft eine geschützte Ressource (`GET /me`) mit ML-DSA-signiertem Token auf und entschlüsselt die mit AES-GCM verschlüsselte Antwort. *Messbar:* End-to-End-Test-Skript, das den vollen Flow im Expo-Simulator durchläuft und am Schluss `200 OK` mit korrekt entschlüsseltem Body liefert.

4. ***(Stretch) Performance- und Grössenmessung.*** Ein Benchmark-Skript misst Handshake-Dauer, Zertifikatsgrösse und Token-Grösse für drei Konfigurationen: (a) klassisch (X25519 + ECDSA), (b) hybrid (X25519MLKEM768 + ECDSA), (c) hybrid + ML-DSA-Token. *Messbar:* tabellarische Auswertung in der Zertifikatsarbeit mit mindestens 100 Messpunkten pro Konfiguration.

---

## Terminplan mit den wesentlichen Arbeitsschritten

Vorgehen: Scrum, 1 Sprint 0 (Setup) + 4 zweiwöchige Sprints. Mentor-Termine als Sprint-Reviews.

| Sprint | Datum | Arbeitssessions | Hauptthema | Definition of Done |
|---|---|---|---|---|
| **0 — Setup** | 06.05 – 11.05 | 06.05 (Jira), 08.–11.05 (4-Tage-Block) | Jira-Backlog & Sprintplanung; Git-Repo + Docker-Compose; OpenSSL 3.5 + oqs-provider lokal bauen oder OQS-Docker-Image; FastAPI-Skeleton; Expo-Skeleton | Tech-Stack lauffähig ohne PQC, Backlog steht, "Hello World" durchgängig vom App bis Backend |
| **1 — Auth-Service klassisch** | 12.05 – 25.05 | 16./17.05, 23./24.05 | Auth-Microservice mit Register/Login, klassische JWT-Tokens, pytest-Suite, klassisches TLS in nginx, GitHub Actions CI | Funktionierender Auth-Service mit klassischer Krypto, ≥ 20 Tests grün, ≥ 80 % Coverage |
| **2 — Server-seitiges PQ-TLS** | 26.05 – 08.06 | 30./31.05, 06./07.06 | nginx + oqs-provider Integration, X25519MLKEM768 hybrid KEX, optional self-signed ML-DSA-Zertifikat, Verifikation via `openssl s_client` und Browser. **08.06: 1. Mentor-Termin** | Hybrider PQ-TLS-Endpoint live; Wireshark-Capture als Beleg; Mentor-Feedback eingearbeitet |
| **3 — App-Layer PQC** | 09.06 – 21.06 | 13./14.06, 20./21.06 | RN-App: ML-KEM-Sitzungsschlüssel via `@noble/post-quantum`; ML-DSA-signierte Tokens im Backend; AES-GCM-Body-Encryption; End-to-End-Auth-Demo. **19.06: 2. Mentor-Termin** | E2E-Login-Flow funktioniert; Tokens sind ML-DSA-signiert; Mentor-Feedback eingearbeitet |
| **4 — Doku, Polish, Submission** | 22.06 – 05.07 | 27./28.06, 04./05.07 | Zertifikatsarbeit fertigschreiben; Performance-Benchmarks (Stretch); Architektur-Diagramme; Code-Cleanup; Abgabe | **05.07.2026 — Abgabe der Arbeit** |

**Harter Cut:** Nach Sprint 3 (21.06) wird keine neue Implementierung mehr gestartet; die letzten zwei Wochenenden gehören vollständig der Doku.

---

## Sachmittel / Rahmenbedingungen

**Hardware**

- Eigener Notebook (macOS oder Linux) für Entwicklung
- Ein Smartphone (iOS oder Android) für die Expo-Go-App-Demo
- Optional: kleiner VPS (z. B. Hetzner CX22) für eine öffentlich erreichbare Live-Demo

**Software & Tooling**

- *Backend:* Python 3.12+, FastAPI, Uvicorn, Pydantic, pytest, httpx, ruff, mypy
- *PQC:* liboqs ≥ 0.14, oqs-provider ≥ 0.10, OpenSSL 3.5+, nginx 1.27+
- *Mobile:* Node.js 20+, Expo SDK 51+, React Native, `@noble/post-quantum`, `expo-secure-store`
- *Infrastruktur:* Docker, Docker Compose, Git/GitHub, GitHub Actions
- *Projektmanagement:* Jira (Scrum-Board, Sprints, Backlog), Confluence/Markdown für Doku
- *Analyse / Verifikation:* Wireshark, OpenSSL CLI, curl mit OpenSSL 3.5

**Räume / Infrastruktur**

Heimarbeitsplatz; bei Bedarf HEKS-Büro. Keine spezifische Cloud-Infrastruktur erforderlich.

---

## Vorgaben, Methoden und Werkzeuge

**Vorgehensmodell**

Scrum mit zweiwöchigen Sprints, Einzelperson in den Rollen Product Owner, Developer und Scrum Master. Backlog und Sprintplanung in Jira (Epics → User Stories → Tasks). Daily-Standups entfallen wegen Einzelarbeit; ersetzt durch eine schriftliche Reflexion am Ende jeder Arbeitssession ("Was lief, was hakte, was als Nächstes"). Sprint-Reviews finden an den Mentor-Terminen (08.06., 19.06.) statt; Retrospektiven nach jedem Sprint im Jira-Wiki.

**Engineering-Praxis**

- Trunk-based Development auf einem GitHub-Repository
- Pull-Request-Reviews via Self-Review-Checkliste; jeder PR muss CI-grün sein, bevor er gemergt wird
- Conventional Commits (`feat:`, `fix:`, `chore:`, …)
- Automatisierte Tests via pytest (Backend) und Jest (App), CI in GitHub Actions
- Linting via ruff/black, Type-Checking via mypy; ESLint für die App
- Container-First: jeder Service als Docker-Image, `docker-compose up` startet den vollständigen lokalen Stack

**Standards & Referenzen (normativ)**

- NIST FIPS 203 (ML-KEM), FIPS 204 (ML-DSA), FIPS 205 (SLH-DSA)
- IETF-Drafts: `draft-ietf-tls-ecdhe-mlkem-04` (Hybrid KEX), `draft-ietf-tls-mldsa-01` (ML-DSA für TLS 1.3)
- TLS 1.3 (RFC 8446) als Basis
- Open-Quantum-Safe-Projekt (liboqs, oqs-provider) als Referenz-Implementierung
- OWASP ASVS L1 als Sicherheits-Checkliste für die Auth-Logik

**Dokumentation**

Die Zertifikatsarbeit wird parallel in Markdown geschrieben und am Ende nach DOCX exportiert. Architektur-Diagramme in Mermaid (PlantUML als Fallback). Alle Code-Snippets im Bericht sind direkt aus dem Repo extrahiert (kein "geschönter Code").

---

## Risiken

| # | Risiko | Eintrittswahrscheinlichkeit | Auswirkung | Pro-aktive Massnahmen |
|---|---|---|---|---|
| **R1** | RN/Expo bekommt PQ-TLS-Negotiation auf Mobilgeräten nicht ausgehandelt (iOS/Android-TLS-Stack lässt sich nicht steuern) | Hoch | Hoch ohne Plan, gering mit Plan | Scope explizit getrennt: Server-seitiges PQ-TLS wird mit `openssl s_client` / Browser verifiziert; auf der App-Seite läuft PQC als Applikationsschicht (ML-KEM + ML-DSA via `@noble/post-quantum`). Das Mobil-Limit wird zum bewussten Architektur-Statement. |
| **R2** | `oqs-provider` / `liboqs`-Build oder nginx-Integration scheitert lokal | Mittel | Mittel | Spike-Story in Sprint 0 zum Bauen von OpenSSL 3.5 + oqs-provider in einem Docker-Image; offizielles `openquantumsafe/oqs-ossl3`-Image als Fallback. |
| **R3** | Zeitknappheit (9 Wochenenden, parallel zu Job/Schule) | Mittel-Hoch | Hoch | Stretch-Goals klar markiert; harter Implementierungs-Cut nach Sprint 3 (21.06); 2 Mentor-Termine als Pflicht-Reviewpunkte; jede Session beginnt mit Jira-Sprint-Goal. |
| **R4** | Falsches Verständnis der Standards (Verwechslung Kyber ↔ ML-KEM, alte Tutorials) | Mittel | Mittel | Direkt aus FIPS 203/204/205 und den IETF-Drafts arbeiten; Tutorials älter als Q1/2025 nicht als Quelle nutzen; oqs-provider-Versionshinweise als Lackmustest. |
| **R5** | Authentifizierungslogik enthält klassische Sicherheitslücken (Replay, Session-Fixation, Side-Channels in der JS-PQC-Bibliothek) | Mittel | Hoch | OWASP-ASVS L1 als Checklist; Replay-Schutz via Nonce + signierter Timestamp; `@noble/post-quantum` ist auditiert; **keine Eigen-Implementierung** von Krypto-Primitiven. |
| **R6** | Performance / Token-Grösse im Mobilszenario unbrauchbar (ML-DSA-65 Signatur ≈ 3.3 KB) | Niedrig-Mittel | Niedrig | Wird in Stretch-Ziel 4 explizit gemessen und im Bericht diskutiert; reines Doku-Risiko, kein Implementierungs-Risiko. |
| **R7** | Zertifikatsarbeit funktional, aber ohne ausreichende Reflexion/Doku abgegeben | Mittel | Hoch | Sprint 4 ist explizit "Doku & Reflexion", keine Implementierungs-Aufgaben in den letzten zwei Wochenenden. |

---
