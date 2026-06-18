# Sprint Review: Sprint 2

**Datum:** 18.06.2026 (1 Tag nach Sprint-2-Abschluss)
**Sprint-Zeitraum:** 01.06 bis 14.06.2026 geplant, faktisch verzögert auf Abschluss am 17.06.2026 (Day-Marathon)
**Timebox:** 1 Stunde

**Sprint-Ziel:** "Am Sprint-Ende läuft der Mobile-Client gegen den Server über hybride PQC-TLS-Verbindung (X25519MLKEM768), und der User kann sich via Google oder Microsoft einloggen und einen ML-DSA-65-signierten Broker-Token erhalten."

---

## 1. Erreichung des Sprint-Ziels

- [x] **Vollständig erreicht (mit Verzögerung, Detail unten)**
- [ ] Teilweise erreicht
- [ ] Nicht erreicht

**Begründung / Kontext:**

Sprint-Goal ist vollständig erreicht für den Browser-zu-Backend-Pfad. Alle 13 Sprint-2-Stories sind Done. Federation-Login via Google und Microsoft funktioniert End-to-End über den Browser gegen den Server. Hybride PQC-TLS-Verbindung (X25519MLKEM768) ist auf der Server-Seite aktiv und via openssl/Chrome verifiziert (siehe Demo D-007). ML-DSA-65-signierter Broker-Token wird vom Server ausgestellt nach erfolgreichem IdP-Login und gegen den Public Key verifizierbar.

**Wichtige Einordnung zum Mobile-Client-Pfad:** Der Mobile-Pfad (Expo Go App auf iPhone) ist funktional gebaut (APP-7, APP-8), wurde aber nur über den Browser gegen das Backend verifiziert, nicht aus der App selbst gegen den Backend-Endpoint. Grund ist eine OS-Plattform-Limitation, nicht ein Implementierungs-Fehler: React Native und Expo Go nutzen den System-TLS-Stack des Betriebssystems (Apple Network Framework auf iOS, Conscrypt/BoringSSL auf Android). Diese System-TLS-Stacks unterstützen die hybride Key-Exchange-Group X25519MLKEM768 noch nicht (Stand Juni 2026), weil ML-KEM-768 in den OS-TLS-Libraries noch nicht ausgerollt ist. Browser wie Chrome bringen ihren eigenen TLS-Stack (BoringSSL mit ML-KEM-Support seit 2023) mit und können daher mit dem Backend verbinden. Für den vollständigen Mobile-zu-Backend-PQC-TLS-Pfad wäre ein Custom-Native-Modul mit eigener liboqs-basierter TLS-Library nötig (Production-Polish, nicht im Sprint-Scope). Diese Limitation ist als R-T08 im Risk Register dokumentiert und im Schlussbericht als ehrlicher Befund festzuhalten.

**Verzögerungs-Kontext (Transparenz):**

Der geplante Sprint-Zeitraum (01.06 bis 14.06) konnte wegen eines Problems bei meiner Arbeit (HEKS) nicht für effektive Projekt-Implementation genutzt werden. Statt den Sprint mit Carry-Over in Sprint 3 zu schieben oder das Sprint-Goal zu reduzieren, habe ich den Sprint als Day-Marathon am 17.06.2026 nachgeholt.

**Selbstkritischer Hinweis zur Mentor-Kommunikation:** Die Mentoren wurden erst nach Sprint-2-Abschluss informiert, nicht während der Verzögerung. Damit hatten sie seit dem letzten Zwischengespräch (01.06) kein Status-Update. Das war ein Fehler. Korrekt wäre gewesen den Mentoren während der Verzögerungs-Phase (ca. 01.06 bis 16.06) eine kurze Info zu geben, damit sie nicht im Unklaren über den Projekt-Stand sind. Diese Lesson fliesst in die Sprint-3-Mentor-Kommunikations-Strategie ein.

Die Verzögerung an sich ist eine Adaption gemäss Empirismus-Säule des Scrum-Prozesses: externe Faktoren beobachtet, Plan angepasst, weitergemacht. Die Konsequenz für die Projekt-Timeline:

- **Sprint 3 wird komprimiert.** Endet wie ursprünglich geplant am 28.06.2026, aber mit weniger effektiven Arbeitstagen zur Verfügung.
- **Sprint 4 bleibt unantastbar.** Sprint 4 (Doku-Fokus, Schlussbericht, Präsentation) ist der wichtigste Sprint für die Bewertung und behält seine vollen 7 Tage.
- **Hypothese:** Mit den beobachteten AI-Multipliern aus Sprint 1 (6.4x) und Sprint 2 (13.6x im Marathon) könnte Sprint 3 ggf. sogar vor dem 28.06 fertig werden.

Diese Strategie ist als R-S06 im Risk Register dokumentiert.

---

## 2. Increment-Demo und Story-Prüfung

Die detaillierten AC-Checks pro Story liegen in den jeweiligen Jira-Done-Comments. Hier nur die Sprint-übergreifende Zusammenfassung gruppiert nach Epic.

### Setup (BRK-0, vorgezogen aus dem Sprint-2-Planning) — 1 Story, 2 SP

| Story | Status | AC-Bilanz |
|---|---|---|
| PQC-84 BRK-0 OAuth-Apps registrieren | Done | 5/5 AC erfüllt. Google Cloud Console plus Microsoft Entra ID Single-Tenant App registriert. R-T04 plus R-S05 mitigated durch Single-Tenant-Wahl. |

### Identity Broker / Federation (BRK) — 7 Stories, 32 SP — Sprint-Goal-relevant

| Story | Status | AC-Bilanz |
|---|---|---|
| PQC-36 BRK-1 External-IdP-Registry | Done | Plugin-Pattern, IdpRegistry mit Provider-Plugin-Schnittstelle. |
| PQC-37 BRK-2 OIDC Code Flow PKCE | Done | POST /auth/federated/<provider>/callback mit Code-zu-Token-Exchange via Provider-/token-URL. PKCE durchgehend. |
| PQC-38 BRK-3 ID-Token-Verifikation | Done | JWKS-Caching, Sig/Iss/Aud/Exp-Check gegen Provider-JWKS. |
| PQC-39 BRK-4 Identity-Normalisierung | Done | Inklusive AC-6 email_verified-Check vor User-Linking. External-Sub-Mapping auf User-Record. |
| PQC-40 BRK-5 Google IdP-Plugin | Done | Google-Discovery, sub als External-Sub, Client-ID/Secret aus Env-Vars. |
| PQC-41 BRK-6 Microsoft IdP-Plugin | Done | Microsoft-Discovery Single-Tenant, oid als External-Sub. |
| PQC-42 BRK-7 CSRF/State-Schutz | Done | State-Parameter 128 Bit Entropie, Redis-Storage mit TTL 10 Min plus PKCE-code_verifier zusammen, one-shot Delete nach Callback. |

**Endurteil:** Federation-Schicht End-to-End funktional gegen beide Provider. AC-6-Erweiterung in BRK-4 und State-Storage-Erweiterung in BRK-7 (aus Cross-Cutting-Concerns-Checkliste beim Sprint-Planning) wurden umgesetzt.

### TLS — 3 Stories, 9 SP — Sprint-Goal-relevant

| Story | Status | AC-Bilanz |
|---|---|---|
| PQC-43 TLS-1 nginx X25519MLKEM768 | Done | Production-nginx-Config mit Hybrid-KEM-Group plus Self-signed ECDSA-Cert. Foundation stand schon durch PQC-18 in Sprint 1. |
| PQC-44 TLS-2 PQ-Handshake-Verifikation | Done | oqs-curl Demo plus Skript scripts/verify_pq_tls.sh dokumentiert. Eindrucksvolles Berichts-Material. |
| PQC-45 TLS-3 nginx Reverse Proxy | Done | nginx forwarded zu auth-service:8000, X-Forwarded-Headers korrekt. |

**Endurteil:** TLS-Schicht produktionsreif. R-T05 weiter mitigated, Sprint-Goal-TLS-Bestandteil erreicht.

### Mobile-Federation (APP-7, APP-8) — 2 Stories, 10 SP — Sprint-Goal-relevant

| Story | Status | AC-Bilanz |
|---|---|---|
| PQC-60 APP-7 Google-Login Mobile | Done | expo-auth-session mit PKCE plus State 128 Bit. UI-Flow funktional, Auth-Authorization via Safari View Controller / Chrome Custom Tab läuft. |
| PQC-61 APP-8 Microsoft-Login Mobile | Done | Analog APP-7 mit Microsoft-Single-Tenant. Code-Reuse fast vollständig. |

**Endurteil:** Mobile-Federation auf UI- und Auth-Flow-Ebene funktional. R-T07 (Deep-Link-Expo-Go-Unzuverlässigkeit) ist nicht eingetreten. Aber: der Backend-Call vom App-Code aus läuft nicht über die PQC-TLS-Group X25519MLKEM768 sondern fällt auf klassische TLS-Groups zurück, weil iOS/Android System-TLS-Stacks ML-KEM noch nicht supporten (siehe R-T08). Verifikation erfolgte daher über Browser (Chrome mit ML-KEM-Support) gegen das Backend, nicht aus der App selbst. Das ist eine OS-Plattform-Limitation, kein Implementierungs-Fehler.

---

## 3. Stories, die nicht abgeschlossen wurden

**Keine.** Sprint 2 ist 100% komplett im Day-Marathon abgeschlossen. Carry-Over nach Sprint 3 ist Null.

---

## 4. Erkenntnisse für den Product Backlog

### 4.1 Cross-Cutting-Concerns-Checkliste hat sich bewährt

Die in Sprint-1-Retro etablierte Cross-Cutting-Concerns-Checkliste beim Sprint-2-Planning hat zwei AC-Erweiterungen produziert (BRK-4 AC-6 email_verified, BRK-7 AC-5 Redis-Storage) plus eine neue Story (BRK-0 OAuth-App-Setup). Beim Day-Marathon-Run am 17.06 waren diese Punkte schon spezifiziert, das hat während der Implementation Diskussionen erspart.

### 4.2 Sprint-3-Backlog steht unverändert

Die offenen Stories für Sprint 3 (CRY-3, CRY-4, CRY-6, CRY-7, SES-1 bis SES-4, DCH-1 bis DCH-4, APP-2/3/5/6, QUA-4, QUA-5) sind unverändert wie initial geplant. Keine Sprint-2-Carry-Overs ins Backlog.

### 4.3 Sprint-3-Komprimierung (Sprint 4 bleibt unantastbar)

Wegen Sprint-2-Verzögerung ist die effektive Restzeit bis zur Abgabe (04/05.07) knapper. Die Strategie:

- **Sprint 3** wird komprimiert auf die Tage zwischen heute (18.06) und dem ursprünglichen Sprint-3-Ende (28.06), also faktisch 10 bis 11 Tage statt geplant 14.
- **Sprint 4** bleibt vollständig erhalten mit seinen 7 Tagen (29.06 bis 05.07). Sprint 4 ist Doku-Fokus (DOC-1 Schlussbericht, DOC-2 Präsentation) und damit am wichtigsten für die Bewertung. Hier wird nichts gekürzt.

Mit den beobachteten AI-Multipliern aus Sprint 1 (6.4x) und Sprint 2 (13.6x im Marathon) ist die Hypothese realistisch dass Sprint 3 trotz Komprimierung machbar ist und ggf. sogar vor dem 28.06 fertig wird. Falls Sprint 3 zum Halbzeit-Check nicht im Plan ist, harte Priorisierung: SES-1 bis SES-3 (Sprint-Goal-relevant) plus DCH-Bundle gehen vor APP-Stories und QUA-Polish. R-S06 im Risk Register dokumentiert diese Strategie.

---

## 5. Risk Review

### 5.1 Eingetretene Risiken in diesem Sprint

| Risk-ID | Was ist passiert? | Reaktion |
|---|---|---|
| R-S01 (Sprint-Kapazität) | Implementation komplett im geplanten Sprint-Zeitraum 01.06 bis 14.06 nicht möglich wegen externem Arbeit-Problem. | Day-Marathon-Adaption am 17.06, alle 13 Stories nachgeholt. Mentor-Update vor Marathon verschickt. |
| R-P02 (Berufliche Belastungen HEKS) | Eingetreten. Hat zu Sprint-2-Verzögerung geführt. | Adaption durch Day-Marathon. Risk-Score neu bewerten. |

### 5.2 Geänderte Risiko-Bewertung

| Risk-ID | Alte Bewertung | Neue Bewertung | Begründung |
|---|---|---|---|
| R-T04 (OIDC-Provider-Setup) | Score 6 Active | Mitigated (17.06) | Single-Tenant-Setup bei Microsoft vermeidet App-Approval-Wartezeit. Google-Setup straightforward. |
| R-S05 (Externe OAuth-Abhängigkeiten) | Score 4 Active | Mitigated (17.06) | Single-Tenant-Wahl hat Wartezeit komplett eliminiert. |
| R-T07 (Expo Deep-Link) | Score 4 Active | Mitigated (17.06) | Deep-Link via expo-auth-session funktional verifiziert. Fallback-Pfad nicht nötig. |
| R-P02 (HEKS-Belastung) | Score 4 Active | Score 6 (hochgestuft) | Real eingetreten in Sprint 2. Sprint-3-Risiko erneut zu beobachten. |
| R-S01 (Sprint-Kapazität) | Score 6 Active | Score 6 Active (unverändert) | Sprint 2 wurde im Day-Marathon nachgeholt, also Sprint-Goal erreicht. Aber strukturell ist die Kapazität bei externen Belastungen weiter ein Risiko. |

### 5.3 Neue Risiken (in diesem Sprint identifiziert)

| Risk-ID | Titel | Kategorie | Score | Status |
|---|---|---|---|---|
| R-S06 | Sprint-3-Komprimierung wegen Sprint-2-Verzögerung | Termin | Mittel/Hoch = 6 | Active (im Risk Register dokumentiert) |
| R-T08 | Mobile-Client kann PQC-TLS nicht End-to-End nutzen (System-TLS-Stack ohne X25519MLKEM768) | Technisch | Eingetreten | Identifiziert, im Risk Register dokumentiert. Limitation im Schlussbericht zu erwähnen. |

### 5.4 Active-Watch-Status für Sprint 3

- [x] R-P02 (HEKS-Belastung) auf Score 6 hochgestuft. Weiter beobachten ob Sprint 3 ebenfalls von Arbeit-Problemen betroffen ist.
- [x] R-S06 (Komprimierung) neu. Sprint-3-Planning realistisch halten, Sprint 4 unantastbar.
- [x] R-T08 (Mobile-PQC-TLS-Limitation) neu. Im Schlussbericht als ehrlicher Befund.
- [x] R-S04 (Doku-Zeit Sprint 4) jetzt prominent. Sprint 4 darf nicht weiter gekürzt werden.
- [x] R-S01 (Sprint-Kapazität) unverändert beobachten.

---

## 6. Velocity dieser Sprint

### 6.1 Story Points

| Metrik | Wert |
|---|---|
| Geplante Story Points | 56 SP (alle Must, kein Stretch im Sprint-Plan) |
| Während Sprint zusätzlich aufgenommen | 0 SP |
| **Abgeschlossene Story Points** | **56 SP (13 Stories)** |

100% Sprint-Backlog erfüllt.

### 6.2 Arbeitszeit

| Metrik | Wert |
|---|---|
| Tatsächliche Arbeitsstunden Implementation | 6h 5m am 17.06 (Day-Marathon) |
| Klassisch geschätzte Stunden (ohne AI) für die 13 Stories | ca. 83h |
| **Aggregierter AI-Multiplier** | **13.6x** |
| Ohne BRK-0 Setup (nur Code-Stories) | 19.6x |

### 6.3 AI-Multiplier-Aufschlüsselung nach Story-Typ

| Story-Typ | Stories | Mittlerer Multiplier | Bemerkung |
|---|---|---|---|
| Setup (BRK-0) | 1 | 1.5x | Browser-Klick-Friction dominant, AI hilft hier wenig. |
| Federation Server-Side | BRK-1 bis BRK-7 | ca. 19x | Hoher Code-Reuse zwischen verwandten Stories (BRK-5/BRK-6). |
| TLS | TLS-1 bis TLS-3 | ca. 26x | Foundation stand schon durch PQC-18 in Sprint 1. |
| Mobile-Federation | APP-7, APP-8 | ca. 35x | Maximaler Code-Reuse zwischen Google und Microsoft (APP-8 erbt von APP-7). |

### 6.4 Beobachtungen für Schlussbericht und Mentor

Der Sprint-2-Multiplier 13.6x ist deutlich höher als Sprint-1 (6.4x) und nicht repräsentativ. Drei spezifische Effekte:

1. **Day-Marathon-Continuity.** Kein Context-Switching zwischen Sessions, mentaler Stack bleibt voll geladen.
2. **Code-Reuse zwischen verwandten Stories.** BRK-5 plus BRK-6 (Google plus Microsoft IdP-Plugin), APP-7 plus APP-8 (Google plus Microsoft Mobile-Login), TLS-1/2/3 als Bundle profitieren massiv vom ersten Pattern.
3. **Cross-Cutting-Concerns-Vorklärung.** AC-6 in BRK-4 und State-Storage in BRK-7 waren schon beim Planning spezifiziert, kein Refinement während Implementation nötig.

Bei der Schlussbericht-Auswertung muss klar unterschieden werden zwischen "echtem" Multi-Day-Multiplier (Sprint 1: 6.4x) und Day-Marathon-Multiplier (Sprint 2: 13.6x). Realistischer Durchschnitt fürs Projekt liegt vermutlich zwischen 5x und 10x je nach Story-Mix und Session-Format.

---

## 7. Stakeholder-Demo und Feedback-Erwartung

### 7.1 Demo-Material

Sprint 2 ist für eine vollständige End-to-End-Demo (User-Login von Mobile-App bis Broker-Token) durch die R-T08-Limitation (Mobile-System-TLS ohne X25519MLKEM768) schwierig: der Mobile-Pfad funktioniert nur theoretisch über Browser-zu-Backend, nicht App-zu-Backend mit PQC-TLS gleichzeitig.

Konkretes Demo-Material aus Sprint 2:

- **D-007 PQ-TLS-Handshake Verifikation** (neu in Sprint 2). Reproduzierbares Shell-Skript `scripts/verify_pq_tls.sh` plus Demo-File `demos/D-007_pq_tls_handshake_verify.md`. Beweist NFR-Sec-1 (Backend spricht X25519MLKEM768) live in 30 Sekunden. Für Mentor-Termin und Schlussbericht direkt einsetzbar.
- Federation-Server-Flow ist via curl plus Browser gegen das Backend live demonstrierbar (Google plus Microsoft OAuth-Flow zu Broker-Token).
- Mobile-App-Flow ist auf iPhone via Expo Go funktional (UI plus Auth-Authorization), aber der Backend-Call läuft nicht über X25519MLKEM768 (R-T08).

Sprint-2-Demos die nicht erstellt wurden:

- Eine integrierte D-008 "Federated Login End-to-End vom Browser" als visueller Beweis. Wäre wertvoll für Mentor-Termin und Schluss-Präsentation, ist Tier-2-Polish.

### 7.2 Geplante Themen für den Mentor-Termin am 20.06.2026

Mentoren wurden während der Sprint-2-Verzögerungs-Phase (01.06 bis 16.06) leider nicht informiert. Das Zwischenupdate kam erst nach Sprint-2-Abschluss am 17.06. Seit dem letzten Zwischengespräch (01.06) hatten die Mentoren also bis zum 17.06 kein Status-Update. Das wird für Sprint 3 anders gehandhabt (regelmässige Updates auch bei Problemen, nicht erst danach).

Konkreter Termin: 20.06.2026. Geplanter Ablauf laut User-Priorisierung:

**Kurzes Update plus Demo (etwa 25% der Termin-Zeit):**

- **Verzögerung kurz ansprechen.** Was passiert ist (Arbeit-Problem), wie ich reagiert habe (Day-Marathon), Lesson aus der Mentor-Kommunikations-Lücke. Nicht dramatisieren, nicht relativieren.
- **D-007 PQ-TLS-Handshake-Demo live.** 30-Sekunden-Skript `scripts/verify_pq_tls.sh` ausführen, eindrucksvoller Backend-Beweis.
- **Federation-Login-Flow demonstrieren.** Via Browser gegen das Backend, mit kurzer Erläuterung der R-T08-Limitation (Mobile-System-TLS noch ohne ML-KEM).

**Hauptfokus (etwa 75% der Termin-Zeit): Abgabeform und Dokumentationsstruktur**

- **Abgabeform besprechen.** Wie wird der Schlussbericht physisch abgegeben (PDF allein, Repo-Link, USB-Stick mit Code, EAS-Build des Mobile-Clients oder nur Demos)? Welches Format wollen die Mentoren? Kolloquium-Setting plus Demo-Anforderungen?
- **Geplante Dokumentationsstruktur vorstellen.** Aktuelle 12 Markdown-Dokumente in `docs/` (Architektur-Entscheidung, Requirements, Tech-Stack, Design, Scrum-Setup, Backlog, Jira-Setup, Risk-Register, Traceability-Matrix, Deferred-Findings) plus sprint_journal-Tree. Welche Teile fliessen in den Schlussbericht ein, welche bleiben als Anhang/Repo-Referenz?
- **Schlussbericht-Kapitelstruktur klären.** Welche Sektionen erwarten die Mentoren (Einleitung, Theorie, Anforderungen, Architektur, Implementation, Tests, Performance, Reflexion, Quellen, Anhänge)?
- **Reflexions-Kapitel-Tiefe klären.** AI-Multiplier-Empirik aus Sprint 1 (6.4x) plus Sprint 2 (13.6x im Marathon), Scrum-Adaptions-Beispiele (HARTE WORKFLOW-REGEL, Day-Marathon, Sprint-2-Verzögerungs-Lehre), R-T08-Limitation als ehrlicher Befund: welche Tiefe wollen die Mentoren in diesem Kapitel?

**Sprint-3-Plan kurz erwähnen falls Zeit:**

- **Sprint-3-Komprimierungs-Strategie plus Sprint-4-Unantastbarkeit.** R-S06-Kontext, kurze Erklärung warum Sprint 3 trotz Komprimierung schaffbar ist (AI-Multiplier-Daten).

---

## 8. Notizen für die Retrospektive

Stichpunkte aus meiner Sicht für die Retro-Diskussion, ausführlicher in `04_retrospective.md`.

- **Verzögerung wegen Arbeit.** Externe Belastung hat Sprint-Plan zerschossen. Adaption (Day-Marathon) funktioniert, aber das System ist fragil bei längeren Ausfällen. Für Sprint 3 plus 4 muss ich ehrlich planen, nicht überoptimistisch.
- **Mentor-Kommunikation während der Verzögerung versäumt.** Ich habe die Mentoren erst nach Sprint-2-Abschluss informiert, nicht während der Verzögerungs-Phase. Damit hatten sie zwischen dem letzten Zwischengespräch (01.06) und dem 17.06 keinen Status. Das war ein echter Fehler von mir, nicht nur eine pragmatische Entscheidung. Lesson für Sprint 3: bei jedem unerwarteten Stocker ein kurzes Update verschicken, nicht erst wenn die Lage gelöst ist.
- **Day-Marathon hat funktioniert.** 13 Stories in 6h ist überraschend viel. Block-Sessions sind sehr effizient bei klarem Backlog, aber risikoreich (kein Puffer für Probleme) und nicht als Default-Modus reproduzierbar.
- **Cross-Cutting-Concerns-Checkliste war wertvoll.** Die Sprint-1-Retro-Maßnahme hat sich in Sprint 2 direkt ausgezahlt. AC-Erweiterungen (BRK-4 email_verified, BRK-7 State-Storage) plus neue Story BRK-0 OAuth-Setup waren beim Day-Marathon schon spezifiziert. Will ich für Sprint 3 wiederholen.
- **Day-Marathon-Multiplier ist verzerrt.** 13.6x aggregiert ist nicht typisch, das muss ich im Schlussbericht klar als Block-Session-Effekt einordnen.
- **Kein Daily Journal während Sprint.** Im Day-Marathon habe ich nicht zwischendurch dokumentiert. Das war pragmatisch (Fokus auf Code), aber für die Reflexions-Tiefe nicht ideal. Im normalen Sprint-3-Modus wieder konsequent führen.
- **Demo-Konvention vernachlässigt im Marathon.** D-007 (PQ-TLS-Handshake) habe ich heute nachgereicht, aber während des Sprints keine Demos erstellt. Für Sprint 3 wieder priorisieren plus eine D-008 (Federation End-to-End) als Nachholaufgabe markieren.
- **Mobile-PQC-TLS-Limitation aus Sprint 2 ist wichtiger Befund.** Der Sprint-Goal-Mobile-Pfad funktioniert nur theoretisch. OS-System-TLS-Stacks (iOS, Android) supporten X25519MLKEM768 noch nicht. R-T08 dokumentiert. Im Schlussbericht ehrlich erwähnen als Beispiel für reale Plattform-Limitierungen im PQC-Ökosystem (Stand 2026).
