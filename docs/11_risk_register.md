# Risk Register

**Projekt:** Implementing PQC (Semesterarbeit 3, ITCNE25)
**Autor:** Dodoe Rumiñahui Mannale
**Erstellt:** 17.05.2026
**Status:** Initial-Version (v1.0)

**Bezug:** Erfüllt die Handlungs-Kompetenz B5.4 (Risikoanalyse durchführen und in der Planung berücksichtigen, KN:3) und B5.7 (Ausweichpläne für potenzielle Umsetzungsprobleme entwickeln, KN:3). Ergänzt `08_scrum_setup.md` Abschnitt 8.4 (Risikoreserven im Sprint-Plan).

---

## Inhaltsverzeichnis

1. [Methodik](#1-methodik)
2. [Risiko-Matrix](#2-risiko-matrix)
3. [Technische Risiken](#3-technische-risiken)
4. [Termin- und Kapazitäts-Risiken](#4-termin--und-kapazitäts-risiken)
5. [Wissens-Risiken](#5-wissens-risiken)
6. [Externe Risiken](#6-externe-risiken)
7. [Persönliche und organisatorische Risiken](#7-persönliche-und-organisatorische-risiken)
8. [Risiko-Review-Prozess](#8-risiko-review-prozess)
9. [Mapping zu Handlungs-Kompetenzen](#9-mapping-zu-handlungs-kompetenzen)
10. [Versionsverlauf](#10-versionsverlauf)

---

## 1. Methodik

Das Risk Register folgt einem leichtgewichtigen Ansatz, angepasst an Solo-Arbeit:

- **Identifikation:** Risiken werden pro Kategorie (Technisch, Termin, Wissen, Extern, Persönlich) gesammelt.
- **Bewertung:** Jedes Risiko erhält eine Eintrittswahrscheinlichkeit (Probability) und einen Schadens-Impact, je mit Ausprägungen Niedrig, Mittel oder Hoch.
- **Priorisierung:** Risiken mit Probability x Impact ab "Mittel x Mittel" werden in den Sprint-Reviews aktiv überwacht. Andere werden gelistet aber nicht regelmässig geprüft.
- **Reaktion:** Pro Risiko sind Mitigation (vorbeugende Massnahmen) und Contingency (Reaktion bei Eintritt) definiert.
- **Review:** Risk Register wird in jeder Sprint-Retrospektive geprüft und in den Mentor-Terminen formell besprochen.

**Risk Score (Probability x Impact):**

| Probability \ Impact | Niedrig | Mittel | Hoch |
|---|---|---|---|
| **Niedrig** | 1 | 2 | 3 |
| **Mittel** | 2 | 4 | 6 |
| **Hoch** | 3 | 6 | 9 |

Risiken mit Score ≥ 4 sind "Active Watch", Score ≥ 6 sind "High Priority".

---

## 2. Risiko-Matrix

Übersicht aller Risiken, sortiert nach Risk Score absteigend.

| ID | Titel | Kategorie | Prob. | Impact | Score | Status |
|---|---|---|---|---|---|---|
| R-S01 | Sprint-Kapazität wird systematisch überschritten | Termin | Hoch | Mittel | 6 | Active |
| R-T04 | OIDC-Provider-Setup-Komplexität (Google, Microsoft) | Technisch | Mittel | Hoch | 6 | Active |
| R-S04 | Doku-Zeit in Sprint 4 zu kurz | Termin | Mittel | Hoch | 6 | Active |
| R-T01 | liboqs-python Build oder Install schlägt fehl | Technisch | Mittel | Hoch | 6 | Mitigated (25.05) |
| R-P01 | Motivationsverlust oder Burnout während Projekt | Persönlich | Mittel | Hoch | 6 | Active |
| R-T03 | Mobile-OS-spezifische Crypto-Quirks (iOS/Android) | Technisch | Mittel | Mittel | 4 | Active |
| R-T02 | @noble/post-quantum API-Instabilität | Technisch | Mittel | Mittel | 4 | Active |
| R-K01 | PQC-Standards-Verständnis-Tiefe nicht ausreichend | Wissen | Mittel | Mittel | 4 | Active |
| R-K03 | React Native / Expo Spezifika nicht vertraut | Wissen | Mittel | Mittel | 4 | Active |
| R-S05 | Externe Abhängigkeiten (OAuth-App-Setup) verzögern Sprint 2 | Termin | Mittel | Mittel | 4 | Active |
| R-K02 | ScrumBut-Falle in Solo-Anwendung | Wissen | Mittel | Mittel | 4 | Active |
| R-P02 | Berufliche und private Belastungen (HEKS-Arbeit) | Persönlich | Mittel | Mittel | 4 | Active |
| R-S02 | Sprint-0-Verzug (bereits eingetreten) | Termin | Eingetreten | Mittel | --- | Mitigated |
| R-T05 | nginx + oqs-provider TLS-Setup bricht | Technisch | Niedrig | Mittel | 2 | Monitor |
| R-S03 | Mentor-Termin-Scheduling (Termin 2 und 3 offen) | Termin | Mittel | Niedrig | 2 | Monitor |
| R-T06 | Redis-Session-Store Bugs (Async, TTL, Nonce) | Technisch | Niedrig | Mittel | 2 | Monitor |
| R-E02 | liboqs / oqs-provider Breaking Changes | Extern | Niedrig | Mittel | 2 | Monitor |
| R-P03 | Krankheit oder unerwartete Ausfälle | Persönlich | Niedrig | Hoch | 3 | Monitor |
| R-E01 | NIST-Standard-Updates während Projekt | Extern | Sehr niedrig | Niedrig | 1 | Accepted |
| R-N01 | Expo SDK Version nicht in App Store Expo-Go-App verfügbar | Node/JS-Ökosystem | Hoch | Niedrig | 3 | Mitigated (30.05) |
| R-T07 | Expo Deep-Link für OAuth-Callback im Expo Go nicht zuverlässig | Technisch | Mittel | Mittel | 4 | Active (Sprint 2) |

---

## 3. Technische Risiken

### R-T01: liboqs-python Build oder Install schlägt fehl

**Beschreibung:** liboqs-python ist eine relativ neue Library (Stand 2026). Builds können auf bestimmten Plattformen (Windows-Host, alte glibc-Versionen, Apple-Silicon-Macs) scheitern oder lange dauern.

**Probability:** Mittel | **Impact:** Hoch | **Score:** 6

**Konsequenz bei Eintritt:** Komplette PQC-Funktionalität (ML-KEM, ML-DSA) blockiert. Sprint 1 und 3 betroffen.

**Mitigation:**
- Container-First-Ansatz: openquantumsafe/oqs-ossl3-Image als Docker-Base (vermeidet 2-Day-Yak-Shave beim Bauen).
- Frühe Verifikation in Sprint 0 (INF-3, INF-4): wenn das Image baut, ist das Risiko bereits stark reduziert.
- Versionen explizit pinnen.

**Contingency:** Falls liboqs-python im Python-Code nicht direkt importierbar ist, Alternative: liboqs C-Library via subprocess oder via cffi-Wrapper aufrufen. Mehraufwand ca. 1 Tag.

**Status-Update 25.05.2026:** Mitigated. PQC-25 (CRY-5) hat liboqs-python 0.15.0 erfolgreich im python:3.12-slim Container installiert (Build-Zeit ca. 5 Min), ML-DSA-65 funktioniert mit korrekten FIPS-204-Sizes (Public 1952 Bytes, Secret 4032 Bytes). Contingency-Path nicht benötigt. Evidence: `../sprint_journal/sprint_1/evidence/PQC-25_CRY-5_liboqs_ml_dsa.md`.

---

### R-T02: @noble/post-quantum API-Instabilität

**Beschreibung:** Die Library ist Stand Mai 2026 in v0.x. Breaking Changes sind möglich.

**Probability:** Mittel | **Impact:** Mittel | **Score:** 4

**Konsequenz bei Eintritt:** Mobile-PQ-Code muss angepasst werden, ggf. mehrere Stories (CRY-6, APP-6, APP-7) betroffen.

**Mitigation:**
- Version pinning in package.json mit exakter Version (kein Caret).
- Eigene Crypto-Abstraction-Layer (CRY-6) kapselt die API, sodass Application-Code nicht direkt von Breaking Changes betroffen ist.
- Library-Releases im Auge behalten via GitHub Watch.

**Contingency:** Falls die Library so massiv bricht, dass die Abstraction nicht reicht, Wechsel auf liboqs-js-Bindings. Mehraufwand 2 bis 3 Tage.

---

### R-T03: Mobile-OS-spezifische Crypto-Quirks (iOS/Android)

**Beschreibung:** expo-secure-store, expo-auth-session, native PRNG verhalten sich auf iOS und Android unterschiedlich. Random-Source-Polyfill für @noble kann auf einer Plattform fehlen.

**Probability:** Mittel | **Impact:** Mittel | **Score:** 4

**Konsequenz bei Eintritt:** Demo funktioniert nur auf einer Plattform, oder OAuth-Redirects bekommen Deep-Link-Probleme.

**Mitigation:**
- `react-native-get-random-values` als Polyfill installieren (Sprint 1, SKL-2).
- Test-Phone mit nur einer Plattform fokussieren (iOS oder Android), nicht beide.
- Plattform-spezifisches Verhalten dokumentieren.

**Contingency:** Bei plattformspezifischen Bugs Platform.select() für Branch-Logik, oder Demo nur auf der getesteten Plattform anbieten.

---

### R-T04: OIDC-Provider-Setup-Komplexität (Google, Microsoft)

**Beschreibung:** OAuth-Apps anlegen, redirect URIs konfigurieren, PKCE einrichten, App-Verifikations-Prozesse. Setup ist nicht trivial und Provider-Doku ist oft veraltet oder unklar.

**Probability:** Mittel | **Impact:** Hoch | **Score:** 6

**Konsequenz bei Eintritt:** Sprint 2 Sprint-Goal (Federation) nicht erreichbar. Verzug ins Sprint 3.

**Mitigation:**
- OAuth-App-Setup schon in Sprint 1 parallel zur Server-Arbeit beginnen (kein Implementations-Blocker).
- Microsoft schwerer als Google, also zuerst Google fertig stellen, dann Microsoft.
- Schrittweise testen mit curl/Postman vor Mobile-Integration.

**Contingency:** Federation auf einen Provider (Google) reduzieren, Microsoft als Stretch markieren. Bericht erklärt warum: Plugin-Architektur erlaubt Microsoft jederzeit nachträglich.

---

### R-T05: nginx + oqs-provider TLS-Setup bricht

**Beschreibung:** TLS-Config mit X25519MLKEM768 ist eine custom Build-Combination, kann an Versions-Mismatches oder Config-Syntax scheitern.

**Probability:** Niedrig | **Impact:** Mittel | **Score:** 2

**Konsequenz bei Eintritt:** TLS-PQ am Server (NFR-Sec-1) nicht demonstrierbar. App-Layer-PQ funktioniert weiterhin.

**Mitigation:**
- openquantumsafe/oqs-ossl3 als Docker-Base (offizielles Image).
- Sprint 0 INF-4 verifiziert das Image schon ohne nginx-Config.

**Contingency:** TLS-PQ als Stretch oder reine "Capability-Demo" mit curl ohne App-Integration. Klare Trennung im Bericht: "TLS-PQ am Server transparent verifiziert, App nutzt App-Layer-PQ als primäre E2E-Garantie".

---

### R-T06: Redis-Session-Store Bugs (Async, TTL, Nonce)

**Beschreibung:** Async-Redis-Code, TTL-Management und Nonce-Tracking können subtile Bugs haben (Race Conditions, falsche Expiry, Replay-Schutz-Lücken).

**Probability:** Niedrig | **Impact:** Mittel | **Score:** 2

**Konsequenz bei Eintritt:** Sessions verfallen falsch, oder Replay-Schutz funktioniert nicht.

**Mitigation:**
- Integration-Tests mit echtem Redis (SES-3, DCH-4).
- Standard-Patterns nutzen (redis-py async API).

**Contingency:** Bei kritischen Bugs Fallback auf einfachen in-memory Store für die Demo. Trade-off im Bericht erwähnen.

---

### R-T07: Expo Deep-Link für OAuth-Callback im Expo Go nicht zuverlässig

**Beschreibung:** Mobile-OAuth-Flows (APP-7 Google, APP-8 Microsoft) benötigen einen Deep-Link-Mechanismus damit der externe IdP nach dem User-Login wieder in die Expo-App zurückspringen kann. Die Expo-Go-App im App Store hat bekannte Edge-Cases beim Deep-Link-Handling (Custom-Scheme, Universal-Link), besonders bei iOS-Sandboxing. F-055 aus Sprint 1 hat ein ähnliches Phänomen bei Auto-Login nach Force-Close gezeigt: was in Dev-Mode funktioniert, kann im Expo-Go-Production-Pfad anders verhalten.

**Probability:** Mittel (Pattern ist bekannt, aber nicht alle Quirks vorhersehbar) | **Impact:** Mittel (Sprint-Goal-Demo des Mobile-Login auf iPhone wäre eingeschränkt) | **Score:** 4

**Konsequenz bei Eintritt:** APP-7 plus APP-8 Mobile-Demo-Flow ist nicht End-to-End auf iPhone reproduzierbar. Sprint-Goal Variante B müsste auf Variante "Server-Side Federation plus PQC-TLS plus reduzierte Mobile-Demo" angepasst werden.

**Mitigation:**
- expo-auth-session Library nutzen die Deep-Link-Handling abstrahiert.
- Custom-Scheme `rib-pqc://` in app.json definieren plus bei Google/Microsoft OAuth-App als Redirect-URI eintragen.
- Bei APP-7 Closing-Review explizit den Deep-Link-Pfad auf echtem iPhone testen (nicht nur Simulator).

**Contingency:** Fallback auf manuellen Code-Copy-Flow für die Demo: User kopiert den OAuth-Callback-Code aus dem Browser-Tab in einen Input-Feld in der App. Nicht produktiv, aber demonstrierbar. Im Bericht als Limitation erwähnen, Production-Path braucht Custom-Build via EAS.

---

## 4. Termin- und Kapazitäts-Risiken

### R-S01: Sprint-Kapazität wird systematisch überschritten

**Beschreibung:** Bereits im initialen Backlog erkennbar: Sprint 1 mit 41 SP geplant vs. realistisch 20 bis 25 SP. Sprint 2 und 3 ähnlich. Sprint 4 mit 39 SP vs. 12 bis 15 SP.

**Probability:** Hoch | **Impact:** Mittel | **Score:** 6

**Konsequenz bei Eintritt:** Stories bleiben pro Sprint liegen, kumulieren, Sprint 4 wird unrealistisch.

**Mitigation:**
- 20 Prozent Kapazitäts-Reserve pro Sprint eingeplant (`08_scrum_setup.md` 8.4).
- Pro Sprint-Planning aggressive Selektion auf realistisches Top-Set.
- Sprint-Stretch-Markierung als Reserve, nicht als zusätzliches Commitment.

**Contingency:** Stretch-Items (STR-1, STR-2, STR-3) konsequent streichen. Should-Items (TOK-3, TOK-4, SES-4, DOC-4, QUA-6, QUA-7, QUA-8) als zweite Streich-Reserve. Im Worst-Case Sprint 4 reine Polish-Phase ohne neue Features.

---

### R-S02: Sprint-0-Verzug (bereits eingetreten)

**Beschreibung:** Sprint 0 wurde in zwei Schritten von 6 auf 19 Tage verlängert (Stand 24.05): zuerst wegen Scope- und Recherche-Unsicherheit, dann wegen umfangreicher Setup- und Dokumentations-Arbeiten (Backlog, Jira-Projekt mit 76 Issues, Sprint-Journal-Templates, Risk Register, Traceability-Matrix). Siehe `08_scrum_setup.md` 8.1.

**Probability:** Eingetreten | **Impact:** Mittel bis Hoch | **Score:** ---

**Konsequenz:** Sprint 4 wurde von 14 auf 7 Tage gekürzt, Sprint 1 ebenfalls auf 7 Tage komprimiert zur Kompensation. Code-Freeze bleibt bei 28.06.

**Mitigation (im Nachhinein):**
- Bewusste, dokumentierte Verlängerung als Adaption-Akt.
- Architektur-Entscheidung (Option 2), Requirements/Design, Backlog und Jira-Setup fertig.
- Sprint 1 als empirisches Experiment für AI-unterstützte Schätz-Genauigkeit (siehe `09_product_backlog.md` Abschnitt 5).

**Status:** Mitigated mit erhöhtem Risiko-Niveau. Sprint 1 mit komprimiertem Zeitfenster muss zeigen ob die AI-unterstützte Velocity ausreicht. Weitere Sprint-Verlängerungen sind nicht mehr möglich.

---

### R-S03: Mentor-Termin-Scheduling (Termin 2 und 3 offen)

**Beschreibung:** Mentor 1 ist auf 01.06 fixiert. Termin 2 und 3 sind noch nicht koordiniert.

**Probability:** Mittel | **Impact:** Niedrig | **Score:** 2

**Konsequenz bei Eintritt:** Synchroner Mentor-Termin findet zu unpassendem Zeitpunkt statt, oder muss verschoben werden.

**Mitigation:**
- Bei Mentor 1 am 01.06 direkt die nächsten zwei Termine vorschlagen.
- Ziel-Zeitfenster: Termin 2 Mitte Sprint 3 (ca. 19.06 bis 22.06), Termin 3 Anfang Sprint 4 (ca. 30.06 bis 01.07).

**Contingency:** Asynchrones Feedback via MS Teams Kanal mit Status-Dokument als Ersatz.

---

### R-S04: Doku-Zeit in Sprint 4 zu kurz

**Beschreibung:** Sprint 4 ist nur 7 Tage und enthält Schlussbericht (geschätzt 30 bis 40 h), Schlusspräsentation (8 bis 12 h), Benchmarks, README, ADRs. Bei strikter Arbeit ab 29.06 ist das knapp.

**Probability:** Mittel | **Impact:** Hoch | **Score:** 6

**Konsequenz bei Eintritt:** Bericht oder Präsentation unvollständig, Bewertungs-Kriterien 1 bis 5 leiden.

**Mitigation:**
- Während Sprint 1 bis 3 schon Notizen für Bericht sammeln im Sprint-Journal.
- Markdown-Dokumente (`03_entscheidung`, `05_requirements`, `07_design`, `08_scrum_setup`, dieses Risk Register, etc.) sind bereits Bericht-Material und werden im Sprint 4 nur konsolidiert.
- Falls Sprint 3 schnell läuft, Bericht-Start in Sprint 3 letzte Woche ziehen.

**Contingency:** Code-Freeze früher ziehen (z.B. 25.06), zusätzliche Tage für Bericht freiräumen.

---

### R-S05: Externe Abhängigkeiten (OAuth-App-Setup) verzögern Sprint 2

**Beschreibung:** Google und Microsoft erfordern Account- und App-Setup, manchmal mit Approval-Prozessen.

**Probability:** Mittel | **Impact:** Mittel | **Score:** 4

**Konsequenz bei Eintritt:** Sprint 2 Start verzögert, Federation nicht bis Mentor 1 demonstrierbar.

**Mitigation:**
- OAuth-App-Setup parallel in Sprint 1 starten, nicht erst in Sprint 2.
- Google-Cloud-Console und Microsoft-Entra-Portal bereits konfiguriert haben, bevor BRK-2 anläuft.

**Contingency:** Mock-IdP-Server (z.B. via pytest-httpserver) für Tests in Sprint 2, echte Provider erst später integrieren.

---

## 5. Wissens-Risiken

### R-K01: PQC-Standards-Verständnis-Tiefe nicht ausreichend

**Beschreibung:** ML-KEM, ML-DSA, HKDF Details (Parameter-Sets, Sicherheits-Beweise) könnten oberflächlich verstanden sein. Bewertungs-Kriterien fragen "Ich glaube, der hat verstanden was er schreibt".

**Probability:** Mittel | **Impact:** Mittel | **Score:** 4

**Konsequenz bei Eintritt:** Bericht wirkt oberflächlich, Theorie-Praxis-Verknüpfung leidet.

**Mitigation:**
- NIST-Specs (FIPS 203, 204) als Primärquellen lesen, nicht nur Tutorials.
- Im Code Kommentare schreiben, die das "Warum" erklären, nicht nur das "Was".
- Mentor 1:1 #1 für gezielte Klärung nutzen (Liste mit Fragen vorbereiten).

**Contingency:** Falls Mentor-Termin Lücken aufzeigt, fokussierte Recherche in Sprint 3, Bericht-Theorie-Kapitel erst danach schreiben.

---

### R-K02: ScrumBut-Falle in Solo-Anwendung

**Beschreibung:** Scrum verkommt zum Lippenbekenntnis (Reviews entfallen, Retros oberflächlich, Daily nicht geführt).

**Probability:** Mittel | **Impact:** Mittel | **Score:** 4

**Konsequenz bei Eintritt:** B5-Kompetenzen nur formell erfüllt, Bewertung-Kriterium 5 (Reflexionstiefe) leidet.

**Mitigation:**
- Sprint-Journal-Templates konsequent ausfüllen.
- Claude als SM-Unterstützung in den Arbeits-Sessions.
- Mentor-PM-Experten fragen explizit nach Prozess-Anwendung.

**Contingency:** Bei späteren Sprints noch retrospektiv Journal-Einträge ergänzen, ehrlich kommentieren wo der Prozess gelitten hat.

---

### R-K03: React Native / Expo Spezifika nicht vertraut

**Beschreibung:** Mobile-Entwicklung ist nicht Haupt-Expertise. UI-Schichten und Plattform-spezifische APIs können langsam vorankommen.

**Probability:** Mittel | **Impact:** Mittel | **Score:** 4

**Konsequenz bei Eintritt:** APP-Stories dauern länger als geschätzt, Sprint 3 wird eng.

**Mitigation:**
- UI absichtlich minimalistisch (Plain RN-Komponenten, keine Design-Library).
- AI-Multiplier (Claude) für Mobile-Code intensiv nutzen.
- App-Stories früh in Sprint 1 anschauen (SKL-2 Skeleton), nicht alles auf Sprint 3 schieben.

**Contingency:** Falls App-Stories aus Sprint 3 nicht fertig: Demo mit curl-Skripten statt Mobile-Demo, App-Stories als "Code vorhanden aber UI nicht poliert" abgeben.

---

## 6. Externe Risiken

### R-E01: NIST-Standard-Updates während Projekt

**Beschreibung:** FIPS 203, 204 sind seit August 2024 final. Major-Updates während eines 2-Monats-Fensters sind sehr unwahrscheinlich.

**Probability:** Sehr niedrig | **Impact:** Niedrig | **Score:** 1

**Status:** Accepted. Kein Handlungsbedarf.

---

### R-E02: liboqs oder oqs-provider Breaking Changes

**Beschreibung:** Open-Source-Libraries können Major-Updates haben, die API ändern.

**Probability:** Niedrig | **Impact:** Mittel | **Score:** 2

**Mitigation:**
- Exact Version pinning in requirements.txt (liboqs-python) und Dockerfile (oqs-ossl3-Image-Tag).
- Lock-Files (uv.lock oder pip-tools) committen.

**Contingency:** Bei Inkompatibilität: alte Image-Version weiternutzen, im Bericht erwähnen.

---

### R-N01: Expo SDK Version nicht in App Store Expo-Go-App verfügbar

**Beschreibung:** Die iPhone-Demo des Mobile-Clients erfolgt via Expo Go aus dem App Store, nicht via lokalem Custom-Build. Die App-Store-Version der Expo-Go-App unterstützt nur SDK-Versionen die Apple zugelassen hat. Beim Projekt-Setup im SKL-2 hat sich gezeigt: Expo SDK 56 (latest beim Setup-Zeitpunkt 30.05.2026) ist noch nicht in der App-Store-Expo-Go-App verfügbar, nur SDK 54. Downgrade auf SDK 54 nötig.

**Probability:** Hoch (Apple-Review-Verzug ist Pattern, nicht Ausnahme) | **Impact:** Niedrig (Downgrade unter 5 Min, alle nötigen Features in SDK 54 verfügbar) | **Score:** 3

**Konsequenz bei Eintritt:** Mobile-Demo nicht auf iPhone möglich, alternativ Custom-Build via EAS (Apple Developer Account nötig) oder Android-Demo.

**Mitigation:**
- Sprint 1 hat SDK 54 als FINAL für gesamten Projekt-Lebenszyklus festgelegt (Memory `project_pqc_expo_sdk.md`).
- Kein Upgrade auf SDK 55 oder 56 vor 04.07.2026, ausser App Store zieht nach.
- Im Dockerfile und Setup-Doku ist SDK 54 explizit gepinnt mit Begründung.

**Contingency:** Sollte Apple SDK 54 abkündigen vor Projekt-Abgabe (unwahrscheinlich, SDK-Versionen werden lange supported): Android-Demo via Expo-Go-Android (gleiche App, andere Plattform, mehr SDK-Toleranz).

**Status-Update 30.05.2026:** Mitigated. Downgrade in PQC-20 (SKL-2) erfolgt, iPhone-Demo funktioniert mit SDK 54, drei Stack-Screens via Expo Go live verifiziert.

---

## 7. Persönliche und organisatorische Risiken

### R-P01: Motivationsverlust oder Burnout während Projekt

**Beschreibung:** Solo-Projekte über 2 Monate können frustrieren bei Rückschlägen. Sprint-Verzug, Library-Probleme, oder schwierige Code-Stellen können Motivation kosten.

**Probability:** Mittel | **Impact:** Hoch | **Score:** 6

**Mitigation:**
- Realistische Sprint-Ziele (siehe R-S01 Mitigation).
- Erfolgserlebnisse einplanen: jeden Sprint mit einem demonstrierbaren Increment abschliessen.
- Sprint-Retros nutzen für Reflexion über Energie und Fokus (`../sprint_journal/_templates/sprint_retrospective_template.md` hat Achse 3 dafür).
- Pausen während intensiver Phasen einplanen, nicht "Stunden grinden".

**Contingency:** Bei länger anhaltender Motivationskrise: Scope-Reduktion (Should/Could-Items streichen), Sprint-Goal verkleinern, Mentor proaktiv informieren.

---

### R-P02: Berufliche und private Belastungen (HEKS-Arbeit, Privat)

**Beschreibung:** 10 bis 15 h pro Woche neben Vollzeit-Arbeit bei HEKS ist ambitioniert. Spitzen bei der Arbeit oder im Privat-Bereich können Sprint-Kapazität reduzieren.

**Probability:** Mittel | **Impact:** Mittel | **Score:** 4

**Mitigation:**
- Block-Phasen (Wochenenden, Ferien) bewusst für Projekt-Arbeit reservieren.
- Wochen-Kapazitäts-Plan im Sprint-Planning explizit machen.

**Contingency:** Bei akuten Belastungen: Sprint-Scope sofort reduzieren, nicht "durchziehen".

---

### R-P03: Krankheit oder unerwartete Ausfälle

**Beschreibung:** Solo-Projekt hat kein Backup. Eine Woche Krankheit kostet ~1/8 der gesamten Projektzeit.

**Probability:** Niedrig | **Impact:** Hoch | **Score:** 3

**Mitigation:**
- Kapazitäts-Reserve in jedem Sprint (20 Prozent).
- Pufferzeit im Sprint-Plan (Code-Freeze 28.06 ist vor Abgabe 04.07, gibt 5 Tage Puffer).

**Contingency:** Bei längerem Ausfall (mehr als 1 Woche): Mentor und Lehrgangsleitung informieren, formellen Antrag auf Verschiebung der Abgabe stellen. Backup-Plan: nur Must-Items, Bericht mit Limitations-Kapitel.

---

## 8. Risiko-Review-Prozess

### 8.1 In jedem Sprint Review

Pro Sprint Review wird gefragt:

- Sind eingetretene Risiken zu dokumentieren?
- Haben sich Probability oder Impact bestehender Risiken geändert?
- Gibt es neue Risiken, die wir nicht auf der Liste haben?

Updates direkt in dieser Datei mit neuem Versionsverlauf-Eintrag.

### 8.2 In jedem Mentor-Termin

Risk-Status als Teil der Vorbereitung (`../sprint_journal/_templates/mentor_meeting_template.md` Section 1.5). Mentor kann externe Sicht einbringen.

### 8.3 Bei Sprint-Planning

Active-Watch- und High-Priority-Risiken werden gegen den geplanten Sprint-Scope gehalten. Wenn ein Sprint Stories enthält, die von einem aktiven Risiko betroffen sind, wird die Mitigation/Contingency explizit ins Sprint-Planning aufgenommen (Section 4 des Planning-Templates).

---

## 9. Mapping zu Handlungs-Kompetenzen

| Kompetenz | Wie dieses Dokument sie erfüllt |
|---|---|
| B5.4 Technische Risikoanalyse durchführen und in Planung berücksichtigen (KN:3) | Vollständige Identifikation, Bewertung, Priorisierung in diesem Dokument. Integration in Sprint-Planning durch Active-Watch-Liste. |
| B5.7 Ausweichpläne für potenzielle Umsetzungsprobleme entwickeln (KN:3) | Pro Risiko ist Mitigation (vorbeugend) und Contingency (reagierend) definiert. |
| B5.9 Dokumente für Projektfortschritts-Überwachung pflegen (KN:3) | Risk Register wird in Sprint-Reviews aktualisiert, Versionsverlauf trackt Änderungen. |
| Bewertungs-Kriterium 5 (Reflexionstiefe) | Eingetretene Risiken (R-S02) sind ehrlich als "Mitigated" dokumentiert mit Begründung der Kompensation. Limitationen und Trade-Offs werden offen genannt. |

---

## 10. Versionsverlauf

| Version | Datum | Änderung |
|---|---|---|
| 1.0 | 17.05.2026 | Initial-Version. 19 Risiken identifiziert (6 Technisch, 5 Termin, 3 Wissen, 2 Extern, 3 Persönlich), Bewertung mit Probability x Impact, Mitigation und Contingency pro Risiko. Risk-Review-Prozess in Sprint Reviews und Mentor-Terminen. Mapping zu Handlungs-Kompetenzen B5.4, B5.7, B5.9. R-S02 (Sprint-0-Verzug) bereits eingetreten und mitigiert. |
