# Fachliche Umsetzung: Implementing Post-Quantum Cryptography in a Python Authentication Service

> **Semesterarbeit 3, ITCNE25** — Dodoe Rumiñahui Mannale (Einzelarbeit)
> **Abgabe:** 04./05.07.2026
> Dieses Dokument deckt die fachliche Komponente ab (Bewertungskriterien 1, 2, 4, 5). Projektkontext, Ziele und Vorgehen sind in [`Projektmanagement.md`](./Projektmanagement.md) dokumentiert.

> _Hinweis (Platzhalter, wird am Ende entfernt): Detailtiefe liegt in den verlinkten Artefakten (`docs/`, `sprint_journal/*/evidence/`, `sprint_journal/*/demos/`, Code im `server/`). Dieses Dokument bleibt schlank und gut lesbar._

---

## Inhaltsverzeichnis

1. [Fachlicher Aufhänger](#1-fachlicher-aufhänger)
2. [Fachlicher Kontext und Theorie](#2-fachlicher-kontext-und-theorie)
3. [Anforderungen](#3-anforderungen)
4. [Architektur und Design](#4-architektur-und-design)
5. [Implementierung](#5-implementierung)
6. [Test und Qualitätssicherung](#6-test-und-qualitätssicherung)
7. [Ergebnis und Abnahme](#7-ergebnis-und-abnahme)
8. [Reflexion und offene Punkte](#8-reflexion-und-offene-punkte)
9. [Anhang und Verzeichnisse](#9-anhang-und-verzeichnisse)

---

## 1. Fachlicher Aufhänger

> **Worum es geht:** Kurzer Einstieg ins fachliche Thema mit Verweis auf die vollständige Einleitung in `Projektmanagement.md`.
> **Vorgaben:** Kriterium 1 (verständliche Einführung).
> **Datenquellen:** `Projektmanagement.md` Abschnitt 1.

_(Inhalt folgt im sequenziellen Review.)_

---

## 2. Fachlicher Kontext und Theorie

> **Worum es geht:** PQC-Bedrohungsmodell (Harvest Now, Decrypt Later), ML-KEM (FIPS 203) und ML-DSA (FIPS 204), Einordnung der NIST-Standards. Kompakt gehalten.
> **Vorgaben:** Kriterium 2 (korrekte Darstellung der Theorie, sinnvolle Beispiele), Kriterium 4 (fachliche Tiefe).
> **Datenquellen:** `docs/02_pqc_technical_brief.md`, `docs/04_quellen.md`.

_(Inhalt folgt im sequenziellen Review.)_

---

## 3. Anforderungen

> **Worum es geht:** Fachliche Functional und Non-Functional Requirements, Use Cases.
> **Vorgaben:** Kriterium 4, Anforderungen aus Kundensicht.
> **Datenquellen:** `docs/05_requirements.md`, `docs/12_traceability_matrix.md`.

_(Inhalt folgt im sequenziellen Review.)_

---

## 4. Architektur und Design

> **Worum es geht:** Cloud-Architekturdiagramm, Code-Architekturdiagramm, Identity-Broker-Entscheidung, Komponentenübersicht.
> **Vorgaben:** Kriterium 2/4, theoretische Lösungsansätze mit Begründung (System-Design), Architekturdiagramme, Schnittstellen.
> **Datenquellen:** `docs/03_entscheidung_auth_architektur.md`, `docs/06_tech_stack.md`, `docs/07_design.md`.

_(Inhalt folgt im sequenziellen Review.)_

---

## 5. Implementierung

> **Worum es geht:** Zentrale Bausteine (Crypto-Facade, PQC-TLS-Handshake, Broker-Token, Auth, Mobile-App) mit ausgewählten Codeausschnitten und Screenshots, je verlinkt auf Evidence und Demos.
> **Vorgaben:** Kriterium 4 (Verknüpfung Theorie-Praxis fachlich), dokumentierte sinnvolle Codeausschnitte, Screenshots der Umsetzung.
> **Datenquellen:** `sprint_journal/*/evidence/`, `sprint_journal/*/demos/`, Code in `server/` und `app/`.

_(Inhalt folgt im sequenziellen Review.)_

---

## 6. Test und Qualitätssicherung

> **Worum es geht:** Teststrategie, Testfälle, Testprotokoll mit Nachweisen.
> **Vorgaben:** Testfälle und Testprotokoll dokumentiert, Screenshots/Nachweise des Testings.
> **Datenquellen:** `server/tests/`, Evidence der QUA-Stories, `sprint_journal/`.

_(Inhalt folgt im sequenziellen Review.)_

---

## 7. Ergebnis und Abnahme

> **Worum es geht:** Lauffähiger MMP-Stand, was funktioniert, Demo, Inbetriebnahme.
> **Vorgaben:** Dokumentation der Installation/Inbetriebnahme, Projektabnahme/Übergabe.
> **Datenquellen:** `sprint_journal/*/demos/`, `infra/README.md`, `server/README.md`.

_(Inhalt folgt im sequenziellen Review.)_

---

## 8. Reflexion und offene Punkte

> **Worum es geht:** Fachliche Reflexion, abgewogene technische Varianten, Vorbehalte, offene Punkte und weiteres Vorgehen.
> **Vorgaben:** Kriterium 5 (Reflexionstiefe), Handlungsempfehlungen.
> **Datenquellen:** `docs/13_deferred_findings.md`, Retrospektiven.

_(Inhalt folgt im sequenziellen Review.)_

---

## 9. Anhang und Verzeichnisse

> **Worum es geht:** Gemeinsames Glossar (für beide Dokumente), Quellenverzeichnis, gesammelte Evidence-/Demo-Links, Abbildungsverzeichnis, Tabellenverzeichnis.
> **Vorgaben:** Kriterium 1 (Verzeichnisse vorhanden), Quellenangaben für nicht selbst verfasste Inhalte.
> **Datenquellen:** `docs/04_quellen.md`.

### Glossar

Gemeinsames Glossar für beide Dokumente. Wird pro Abschnitt fortlaufend ergänzt; definiert PQC- und projektspezifische Begriffe, gängige Grundbegriffe (TLS, RSA, ECDSA) werden vorausgesetzt.

| Begriff | Definition |
|---|---|
| Post-Quantum Cryptography (PQC) | Kryptografische Verfahren, die auch gegen Angriffe mit Quantencomputern sicher sind. |
| Shors Algorithmus | Quantenalgorithmus, der die mathematischen Probleme hinter RSA und ECC effizient löst und diese damit brechbar macht. |
| Harvest Now, Decrypt Later (HNDL) | Angriffsmodell: heute verschlüsselten Verkehr aufzeichnen und später mit einem Quantencomputer entschlüsseln. |
| ML-KEM (FIPS 203) | NIST-Standard für quantensicheren Schlüsselaustausch (Key Encapsulation Mechanism), basierend auf CRYSTALS-Kyber. |
| ML-DSA (FIPS 204) | NIST-Standard für quantensichere digitale Signaturen, basierend auf CRYSTALS-Dilithium. |
| SLH-DSA (FIPS 205) | Hash-basierter NIST-Signaturstandard, als konservatives Backup zu ML-DSA. |
| KEM | Key Encapsulation Mechanism: Verfahren, um über einen unsicheren Kanal einen gemeinsamen symmetrischen Schlüssel zu etablieren. |
| Hybrider Schlüsselaustausch (X25519MLKEM768) | Kombination aus klassischem (X25519) und post-quantum (ML-KEM-768) Schlüsselaustausch; sicher, solange mindestens eines der beiden Verfahren hält. |
| oqs-provider / liboqs | Open-Source-Bausteine des Open-Quantum-Safe-Projekts, die PQC-Algorithmen in OpenSSL und nginx einbringen. |
| OIDC (OpenID Connect) | Standardprotokoll für Authentifizierung über externe Identity Provider wie Google oder Microsoft. |
| Identity Broker | Komponente, die externe Identitäten annimmt und in projekteigene, hier PQ-sichere, Sessions überführt. |
| PQ-Uplift | In diesem Projekt: das Anheben einer klassisch authentifizierten Identität auf eine post-quantum-sichere Session. |
| Crypto-Agility | Architektur-Prinzip, das den Austausch kryptografischer Algorithmen ohne Code-Änderung erlaubt. |
| AES-256-GCM | Symmetrisches Verschlüsselungsverfahren für die eigentlichen Nutzdaten, gilt als quantensicher genug. |
| Definition of Done (DoD) | Projektweite Qualitäts-Checkliste, die jede Story zusätzlich zu ihren Akzeptanzkriterien erfüllen muss. |
| Akzeptanzkriterien | Storyspezifische, nachprüfbare Bedingungen, die die fachliche Korrektheit genau einer Story belegen. |
| Definition of Ready (DoR) | Eingangslatte: Bedingungen, die eine Story erfüllen muss, bevor sie in einen Sprint geplant wird. |
| Story Points / T-Shirt-Sizing | Relatives Schätzmass für Aufwand (XS bis XL, abgebildet auf die Fibonacci-Folge) statt absoluter Stunden. |
| Velocity | Pro Sprint abgeschlossene Story Points; bei Einzelarbeit nur eingeschränkt aussagekräftig. |
| AI-Multiplier (projektspezifisch) | Verhältnis aus klassischer Schätzung ohne AI zu tatsächlicher Arbeitszeit mit AI-Unterstützung, am Projektende ausgewertet. |
| MoSCoW | Priorisierungsmethode: Must, Should, Could, Won't. |
| MVP / MLP / MMP | Release-Stufen: Minimum Viable (früh Feedback), Minimum Lovable (Qualität), Minimum Marketable (Abgabe). |
| Epic | Übergeordnete Arbeitseinheit im Backlog, die mehrere thematisch zusammengehörige Stories bündelt. |
| Roadmap | Grobe zeitliche Übersicht der Releases und Meilensteine, nicht die Detailplanung. |

### Quellenverzeichnis

_(Inhalt folgt im sequenziellen Review.)_

### Abbildungsverzeichnis

_(Inhalt folgt im sequenziellen Review.)_

### Tabellenverzeichnis

_(Inhalt folgt im sequenziellen Review.)_
