# Traceability-Matrix: Requirements bis Bewertungskriterien

**Projekt:** Implementing PQC (Semesterarbeit 3, ITCNE25)
**Autor:** Dodoe Rumiñahui Mannale
**Erstellt:** 17.05.2026
**Status:** Initial-Version (v1.0)

**Bezug:** Konsolidiert die Nachverfolgbarkeit von ursprünglichen Use Cases und Requirements aus `05_requirements.md` bis zu konkreten Jira-Stories, Sprint-Zuordnung und Bewertungs-Kriterien aus dem Merkblatt-A. Ergänzt die Requirements-interne Traceability-Matrix in `05_requirements.md` Section 7 um die Sprint- und Bewertungs-Dimension.

---

## Inhaltsverzeichnis

1. [Zweck und Lese-Anleitung](#1-zweck-und-lese-anleitung)
2. [Use Case zu Stories zu Sprints](#2-use-case-zu-stories-zu-sprints)
3. [Functional Requirements zu Stories zu Sprints](#3-functional-requirements-zu-stories-zu-sprints)
4. [Non-Functional Requirements zu Stories zu Sprints](#4-non-functional-requirements-zu-stories-zu-sprints)
5. [Bewertungs-Kriterien zu Deliverables](#5-bewertungs-kriterien-zu-deliverables)
6. [Handlungs-Kompetenzen zu Deliverables](#6-handlungs-kompetenzen-zu-deliverables)
7. [Dokument-Konsistenz-Check](#7-dokument-konsistenz-check)
8. [Versionsverlauf](#8-versionsverlauf)

---

## 1. Zweck und Lese-Anleitung

Dieses Dokument beantwortet vier Fragen aus Bewertungs-Sicht:

1. **Werden alle Use Cases und Requirements durch konkrete Stories adressiert?** (Sections 2 bis 4)
2. **Welche Stories tragen zu welchen Bewertungs-Kriterien bei?** (Section 5)
3. **Welche Handlungs-Kompetenzen werden durch welche Deliverables nachgewiesen?** (Section 6)
4. **Sind alle Dokumente konsistent untereinander?** (Section 7)

Die Tabellen verwenden folgende Konventionen:

- **Markdown-ID**: Story-ID aus `09_product_backlog.md` (z.B. AUT-3).
- **Jira-Key**: Korrespondierender Jira-Issue-Key (z.B. PQC-30).
- **Sprint**: Initial geplanter Sprint (kann sich durch Adaption ändern).
- **Status**: Open / In Progress / Done (initial alle Open).

---

## 2. Use Case zu Stories zu Sprints

| UC | Titel | Stories | Jira-Keys | Sprint |
|---|---|---|---|---|
| UC-1 | Lokaler Login mit Email/Passwort | AUT-3, AUT-4, TOK-1, TOK-2, APP-1, APP-4, APP-9 | PQC-30, PQC-31, PQC-32, PQC-33, PQC-54, PQC-57, PQC-62 | 1 |
| UC-2 | Login mit Google (Federated) | BRK-2, BRK-3, BRK-4, BRK-5, BRK-7, APP-7 | PQC-37, PQC-38, PQC-39, PQC-40, PQC-42, PQC-60 | 2 |
| UC-3 | Login mit Microsoft (Federated) | BRK-2, BRK-3, BRK-4, BRK-6, BRK-7, APP-8 | PQC-37, PQC-38, PQC-39, PQC-41, PQC-42, PQC-61 | 2 |
| UC-4 | Etablierung der PQ-Session | SES-1, SES-2, SES-3, CRY-3, CRY-4, CRY-6, APP-5 | PQC-46, PQC-47, PQC-48, PQC-23, PQC-24, PQC-26, PQC-58 | 3 |
| UC-5 | Geschützter API-Call | DCH-1, DCH-2, DCH-3, DCH-4, APP-3, APP-6 | PQC-50, PQC-51, PQC-52, PQC-53, PQC-56, PQC-59 | 3 |
| UC-6 | Re-Authentication nach Session-Ablauf | (implizit in APP-3, APP-6, DCH-2) | PQC-56, PQC-59, PQC-51 | 3 |
| UC-7 | Algorithmus-Wechsel via Config | CRY-3, CRY-7, SES-4 (Demo) | PQC-23, PQC-27, PQC-49 | 3 |

**Lese-Hinweis:** UC-6 hat keine eigene Story, weil das Re-Auth-Verhalten in den Session/Client-Stories enthalten ist. Bei Sprint 3 Planning explizit als Akzeptanzkriterium-Punkt aufnehmen.

---

## 3. Functional Requirements zu Stories zu Sprints

| FR-ID | Beschreibung | Stories | Jira-Keys | Sprint |
|---|---|---|---|---|
| FR-Auth-1 | User-Authentifizierung via Email und Passwort | AUT-1, AUT-3, AUT-4 | PQC-28, PQC-30, PQC-31 | 1 |
| FR-Auth-2 | User-Provisioning via Admin-CLI | AUT-2 | PQC-29 | 1 |
| FR-Broker-1 | External-IdP-Registry mit Plugin-Architektur | BRK-1, BRK-5, BRK-6 | PQC-36, PQC-40, PQC-41 | 2 |
| FR-Broker-2 | OIDC Authorization Code Flow mit PKCE | BRK-2 | PQC-37 | 2 |
| FR-Broker-3 | ID-Token-Verifikation gegen IdP-JWKS | BRK-3 | PQC-38 | 2 |
| FR-Broker-4 | Identity-Normalisierung | BRK-4 | PQC-39 | 2 |
| FR-Token-1 | Broker-Token-Ausstellung mit ML-DSA-Signatur | TOK-1 | PQC-32 | 1 |
| FR-Token-2 | Broker-Token-Verifikation | TOK-2 | PQC-33 | 1 |
| FR-Token-3 | Schlüssel-Rotation für Token-Signierung | TOK-3, TOK-4 | PQC-34, PQC-35 | 4 |
| FR-Session-1 | ML-KEM-basierte Session-Etablierung | SES-1, CRY-4 | PQC-46, PQC-24 | 3 |
| FR-Session-2 | Session-Key-Ableitung via HKDF | SES-2, CRY-3 | PQC-47, PQC-23 | 3 |
| FR-Session-3 | Session-Store mit TTL | SES-3 | PQC-48 | 3 |
| FR-Session-4 | Algorithmus-Negotiation | SES-4 | PQC-49 | 3 |
| FR-DataChannel-1 | AES-256-GCM-Verschlüsselung für Payloads | DCH-1, DCH-3 | PQC-50, PQC-52 | 3 |
| FR-DataChannel-2 | Header-basiertes Session-Routing | DCH-2 | PQC-51 | 3 |
| FR-Crypto-1 | Algorithmus-Registry für KEM und Signatur | CRY-1, CRY-4, CRY-5, CRY-6 | PQC-21, PQC-24, PQC-25, PQC-26 | 1+3 |
| FR-Crypto-2 | Konfigurations-basierte Algorithmus-Auswahl | CRY-2, CRY-3 | PQC-22, PQC-23 | 1+3 |
| FR-Crypto-3 | Algorithmus-Identifier in allen Krypto-Artefakten | CRY-7 | PQC-27 | 3 |
| FR-Crypto-4 | Hybrid-Key-Combiner (Stretch) | STR-1 | PQC-75 | Stretch |

**Coverage:** Alle 19 FRs sind durch mindestens eine Story abgedeckt. FR-Crypto-4 ist explizit als Project-Stretch markiert.

---

## 4. Non-Functional Requirements zu Stories zu Sprints

| NFR-ID | Beschreibung | Stories | Jira-Keys | Sprint |
|---|---|---|---|---|
| NFR-Sec-1 | Hybride PQ-Sicherheit auf Transport-Layer | TLS-1, TLS-2, TLS-3, INF-4 | PQC-43, PQC-44, PQC-45, PQC-18 | 0+2 |
| NFR-Sec-2 | Schutz vor Replay-Angriffen | DCH-4 | PQC-53 | 3 |
| NFR-Sec-3 | Kein Klartext für Geheimnisse | APP-9 | PQC-62 | 1 |
| NFR-Sec-4 | Schutz vor User-Enumeration | AUT-4 | PQC-31 | 1 |
| NFR-Sec-5 | Schutz vor CSRF in OIDC-Flows | BRK-7 | PQC-42 | 2 |
| NFR-Sec-6 | Defense-in-Depth durch Hybrid-Verschlüsselung (Stretch) | STR-1 | PQC-75 | Stretch |
| NFR-Perf-1 | Latenz für PQ-Session-Etablierung | QUA-6 | PQC-68 | 4 |
| NFR-Perf-2 | Latenz für Token-Verifikation | QUA-7 | PQC-69 | 4 |
| NFR-Perf-3 | Verschlüsselungs-Overhead pro API-Call | QUA-8 | PQC-70 | 4 |
| NFR-Maint-1 | Crypto-Agility ohne Code-Änderung | CRY-1, CRY-2, CRY-3, CRY-7 | PQC-21, PQC-22, PQC-23, PQC-27 | 1+3 |

**Coverage:** Alle NFRs sind durch Stories abgedeckt. Performance-NFRs verschoben in Sprint 4 (nach Implementation), Sicherheits-NFRs verteilt auf die jeweiligen Sprint-Phasen ihrer betroffenen Komponenten.

---

## 5. Bewertungs-Kriterien zu Deliverables

Die Bewertungs-Kriterien aus `Merkblatt-A-2-SemArbeit.md` Section "Kompetenzmatrix" werden so adressiert:

| Bewertungs-Kriterium | Wichtigste Deliverables | Sprint |
|---|---|---|
| **1. Substanz, Aufbau des Inhalts** | Markdown-Dokumente 01 bis 12, Schlussbericht `DOC-1` | 0 bis 4 |
| **2. Darstellung der Theorie** | `08_scrum_setup.md` (Verweis auf Scrum Guide), Theorie-Kapitel im Schlussbericht `DOC-1`, Crypto-Theorie-Kapitel im Bericht | 0+4 |
| **3. Verknüpfung Theorie und Praxis (Projektmanagement)** | `08_scrum_setup.md` Solo-Adaption (Abschnitt 2), Sprint-Journal-Einträge | 0 bis 4 |
| **4. Verknüpfung Theorie und Praxis (fachlich, PQC)** | `07_design.md` Crypto-Abstraction-Design, Crypto-Implementation (CRY-1 bis CRY-7), Algorithmus-Wechsel-Demo (CRY-3, SES-4), Schlussbericht | 1 bis 4 |
| **5. Reflexionstiefe** | Sprint-Retrospektiven (../sprint_journal/sprint_X/retrospective.md), Risk Register Updates, Solo-Scrum-Limitations-Tabelle in `08_scrum_setup.md` 2.4, Reflexions-Kapitel im Schlussbericht | 0 bis 4 |
| **6. Kolloquium (Produkte-Vorführung)** | Schluss-Präsentation `DOC-2`, Demo-Recording, Live-Demo | 4 |

---

## 6. Handlungs-Kompetenzen zu Deliverables

Aus `Projekmanagement-erwartete-Handlungskonpetenzen.md`:

| Kompetenz | Nachweis durch |
|---|---|
| A2.1 Sachlogisch, transparent, klar kommunizieren | Alle Markdown-Dokumente, Schlussbericht |
| A2.4 Arbeitsergebnisse zielgruppenadäquat präsentieren | Schluss-Präsentation (DOC-2), Mentor-Termin-Status-Dokumente |
| A2.6 Branchenspezifische Fachtermini verwenden | Glossar im Schlussbericht, präzise Verwendung von PQC-Begriffen |
| A2.7 Berichte professionell verfassen | Schlussbericht (DOC-1), README (DOC-3) |
| B5.1 ICT-Projekte selbständig planen und steuern (KN:3) | `08_scrum_setup.md`, `09_product_backlog.md`, Jira-Projekt PQC |
| B5.4 Technische Risikoanalyse durchführen (KN:3) | `11_risk_register.md` |
| B5.5 Initiative und Kreativität bei Gestaltung (KN:3) | `03_entscheidung_auth_architektur.md`, Crypto-Abstraction-Design |
| B5.7 Ausweichpläne für Umsetzungsprobleme (KN:3) | `11_risk_register.md` Contingency-Spalte, `08_scrum_setup.md` 8.5 Sprint-Abbruch-Eskalation |
| B5.8 Kosten-Termin-Verhältnis optimieren (KN:2) | T-Shirt-Sizing in `09_product_backlog.md`, Sprint-Scope-Reduktion bei Engpässen |
| B5.9 Projekt-Fortschritts-Dokumente erstellen (KN:3) | Sprint-Journal, dieses Traceability-Dokument, Jira-Board |
| B5.10 Termin- und budgetgerecht abschliessen (KN:3) | DoD (`08_scrum_setup.md` 5.3), Sprint-Plan mit Code-Freeze, Abgabe-Termin |

---

## 7. Dokument-Konsistenz-Check

Stand 17.05.2026.

### 7.1 Übersicht aller Projekt-Markdown-Dokumente

| Dokument | Zweck | Status |
|---|---|---|
| `01_form_draft.md` | Einreichungsformular-Draft | Eingereicht, nicht mehr aktiv gepflegt |
| `02_pqc_technical_brief.md` | Frühe technische Notizen | Konsolidiert in spätere Dokumente |
| `03_entscheidung_auth_architektur.md` | Architektur-Entscheidung Option 2 | Locked-In |
| `04_quellen.md` | Quellenverzeichnis | Wird laufend ergänzt |
| `05_requirements.md` | Use Cases, FRs, NFRs, eigene Traceability | Vollständig (v1.0) |
| `06_tech_stack.md` | Stack-Entscheidungen und Versionen | Vollständig |
| `07_design.md` | Architektur, Komponenten, Sequenz-Diagramme | Vollständig (v1.0) |
| `08_scrum_setup.md` | Scrum-Anwendung, Sprint-Plan, Solo-Adaption | Vollständig (v1.0) |
| `09_product_backlog.md` | Epics, Stories, Akzeptanzkriterien | Vollständig (v1.0) |
| `10_jira_setup.md` | Jira-Projekt und Mapping | Vollständig (v1.0) |
| `11_risk_register.md` | Risiko-Liste mit Mitigation und Contingency | Vollständig (v1.0) |
| `12_traceability_matrix.md` | Dieses Dokument | Initial-Version |
| `../sprint_journal/` | Templates und (später) ausgefüllte Sprint-Dokumente | Templates fertig |

### 7.2 Konsistenz-Punkte

- **Mentor-Termin-Daten:** `08_scrum_setup.md` 9.2 listet Termin 1 am 01.06 (bestätigt), Termin 2 und 3 als noch zu definieren. Sobald die Daten fixiert sind, in `08`, `11_risk_register.md` R-S03 und ggf. dieses Dokument synchron updaten.
- **Sprint-Plan:** Aktuelle Version mit Sprint-0-Verzug ist im `08_scrum_setup.md` 8.2 und im `09_product_backlog.md` 3 dokumentiert. Beide stimmen überein.
- **Story-IDs:** Markdown-IDs in `09_product_backlog.md` und Jira-Keys in `10_jira_setup.md` 3 stimmen überein.
- **DoD und Akzeptanzkriterien:** Klar getrennt in `08_scrum_setup.md` Abschnitt 5.3 (DoD) und 6.2 (AC). Stories in `09_product_backlog.md` haben spezifische AC, DoD gilt projektweit.
- **Bewertungs-Stufe:** Anvisiert ist Kompetenz professionellen Handelns (KN:3), konsistent in `08_scrum_setup.md` 10.3, `11_risk_register.md` 9, und diesem Dokument 6.

### 7.3 Bekannte offene Punkte

- Mentor-Termine 2 und 3 noch nicht datiert. Update sobald koordiniert.
- Sprint-Objekte in Jira noch nicht angelegt (manueller UI-Schritt, dokumentiert in `10_jira_setup.md` 4.1).
- Sprint 0 Review und Retrospektive noch ausstehend (geplant 17. bis 18.05.2026).

---

## 8. Versionsverlauf

| Version | Datum | Änderung |
|---|---|---|
| 1.0 | 17.05.2026 | Initial-Version. Mapping UC zu Stories zu Sprints (7 UCs), FR zu Stories zu Sprints (19 FRs), NFR zu Stories zu Sprints (10 NFRs). Mapping Bewertungs-Kriterien zu Deliverables. Mapping Handlungs-Kompetenzen zu Deliverables. Dokument-Konsistenz-Check über alle 13 Projekt-Markdown-Dokumente. Bekannte offene Punkte (Mentor-Termine 2 und 3, Sprint-Objekte in Jira, Sprint 0 Review/Retro) identifiziert. |
