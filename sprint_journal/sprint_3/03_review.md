# Sprint Review: Sprint 3

**Datum:** 28.06.2026
**Sprint-Zeitraum:** 18.06 bis 28.06.2026 (11 Kalendertage, komprimiert wegen Sprint-2-Verzögerung)
**Timebox:** 1 Stunde

**Sprint-Ziel:** "Am Sprint-Ende ist der Mobile-Pfad End-to-End funktional auf iPhone via Expo Go: User öffnet Profile-Screen, App etabliert eine PQ-Session zum Server (ML-KEM-768 plus HKDF), ruft `/api/profile` AES-256-GCM-verschlüsselt auf, Profile-Daten werden angezeigt. D-008 reproduzierbar."

---

## 1. Erreichung des Sprint-Ziels

- [ ] Vollständig erreicht
- [x] **Teilweise erreicht (Detail unten)**
- [ ] Nicht erreicht

**Begründung / Kontext:**

Der Server-Pfad des Sprint-Goals ist vollständig erreicht: PQ-Session-Etablierung via ML-KEM-768 (SES-1), HKDF-Session-Key-Ableitung (SES-2), Redis-Persistenz mit TTL (SES-3), AES-256-GCM-Data-Channel mit Header-Routing und Nonce-Replay-Schutz (DCH-1 bis DCH-4), geschützter `/api/profile`-Endpoint mit Encrypted-Roundtrip (DCH-3). Mini-Demo D-008 ist live im Container ausführbar (`server/scripts/demo_d008.py`) und zeigt den 8-Schritt-Roundtrip Login → Session-Etablierung → HKDF → Encrypted-Profile → Decrypt-Response → Replay-Test-400. Alle Server-Side Foundation-Stories (Crypto-Layer, Session, Data-Channel) sind Done, plus die Client-Side Crypto-Abstraction (CRY-6).

Der Mobile-Pfad des Sprint-Goals ist nicht erreicht: die vier APP-Stories (APP-5 SessionContext, APP-6 secureClient, APP-2 Home-Screen, APP-3 Profile-Screen) sind nicht angefangen. Damit ist die End-to-End-Demo aus der iPhone-App heraus nicht möglich. R-T08 hätte den Mobile-Pfad sowieso auf "theoretisch funktional" begrenzt (System-TLS-Stack ohne X25519MLKEM768), aber die App-Layer-Crypto-Pipeline ist im Mobile-Client jetzt überhaupt nicht implementiert.

**Ferien-Kontext (Transparenz):** Sprint 3 fiel in meine Ferien. Ich habe mir nicht so viel Zeit für das Schulprojekt genommen wie ursprünglich geplant. Das ist meine eigene Verantwortung als Solo-Developer und Solo-PM, nicht externe Belastung wie in Sprint 2. Lesson für die nächste Projekt-Planung: Ferien als echte Ferien einplanen, ohne Projektarbeit. Die Projekt-Arbeitszeit muss rund um die Ferien-Phasen geplant werden, nicht in sie hinein. Versuche während Ferien zu arbeiten haben in diesem Sprint nachweisbar weniger Output erzeugt als der Standard-Schedule (Wochenenden plus Mittwoch).

**Konsequenz für Sprint 4:** 27 SP Carry-Over (4 APP-Stories plus QUA-4/QUA-5) müssen mit den geplanten Doku-Stories konkurrieren. Sprint 4 wird zum Hybrid-Sprint, das sollte ursprünglich vermieden werden. R-S04 (Doku-Zeit Sprint 4 zu kurz) ist damit aggressiv eingetreten.

---

## 2. Increment-Demo und Story-Prüfung

Die detaillierten AC-Checks pro Story liegen in den jeweiligen Jira-Done-Comments. Hier nur die Sprint-übergreifende Zusammenfassung gruppiert nach Epic.

### Crypto-Foundation (CRY) — 4 Stories, 17 SP

| Story | Status | AC-Bilanz |
|---|---|---|
| PQC-24 CRY-4 liboqs ML-KEM-Wrapper (Server) | Done | LibOqsKem-Adapter, registry_init hot-fixed |
| PQC-23 CRY-3 Crypto-Facade KEM/HKDF/AEAD | Done | CryptoFacade-Erweiterung um KEM/HKDF/AEAD/Negotiation, cryptography.hazmat als Backend |
| PQC-27 CRY-7 Algorithmus-Identifier in Artefakten | Done | docs/wire_format.md (230 Zeilen) als zentrale Wire-Format-Spec |
| PQC-26 CRY-6 Client-Side Crypto-Abstraction | Done | 7 TypeScript-Module mit @noble/post-quantum, @noble/ciphers, @noble/hashes plus Jest-Setup. F-098 plus F-106 in-Story-resolved |

**Endurteil:** Crypto-Foundation Server plus Client komplett.

### Session-Server (SES) — 4 Stories, 18 SP — Sprint-Goal-relevant

| Story | Status | AC-Bilanz |
|---|---|---|
| PQC-48 SES-3 Session-Store Redis | Done | SessionService mit TTL plus Lookup plus Refresh plus Invalidierung. F-101 API-Erweiterung in PQC-46 |
| PQC-47 SES-2 HKDF-Session-Key-Ableitung | Done | derive_session_key plus F-098 Cross-Validation-Vector zwischen Server und Client |
| PQC-46 SES-1 POST /session/init mit ML-KEM-Encap | Done | 12 Tests, Audit-Roundtrip, F-101 plus F-102 in-Story-resolved |
| PQC-49 SES-4 Algorithmus-Negotiation (High) | Done | Server-Logik in PQC-46 schon erfüllt, hier nur 2 Tests plus Doku |

**Endurteil:** Session-Layer Server-Side komplett, inkl. SES-4 (war Defer-Kandidat, wurde im Bundle mit SES-1 erledigt).

### Data-Channel (DCH) — 4 Stories, 17 SP — Sprint-Goal-relevant

| Story | Status | AC-Bilanz |
|---|---|---|
| PQC-50 DCH-1 AES-256-GCM Wrapper | Done | Server-Wrapper plus aead_random_nonce-Helper, 4 Server-Tests plus 2 App-Tests |
| PQC-51 DCH-2 Header-basiertes Session-Routing | Done | FastAPI-Dependency `authenticated_session`, 13 Tests. Wire-Format-Spec v0.3. F-108 plus F-109 |
| PQC-53 DCH-4 Replay-Schutz Nonce-Tracking | Done | RedisNonceTracker atomar SET NX EX, eigene DB=4. Race-Condition aus DCH-2 mitgeschlossen. Wire-Format-Spec v0.4 mit Trade-Off-Tabelle. NFR-Sec-2 erfüllt |
| PQC-52 DCH-3 Geschützter /api/profile-Endpoint | Done | POST /api/profile mit Depends(authenticated_session), Response-Encryption fresh Nonce. Wire-Format-Spec v0.5. **Mini-Demo D-008 8-Schritte-Roundtrip live im Container** |

**Endurteil:** Data-Channel-Schicht produktionsreif. Sprint-Goal-Server-Pfad erfüllt durch DCH-3 plus Mini-Demo D-008.

### Mobile-App (APP) — 4 Stories, 14 SP — NICHT angefangen

| Story | Status | AC-Bilanz |
|---|---|---|
| PQC-58 APP-5 SessionContext | nicht angefangen | Carry-Over Sprint 4 |
| PQC-59 APP-6 secureClient.ts | nicht angefangen | Carry-Over Sprint 4 |
| PQC-55 APP-2 Home-Screen | nicht angefangen | Carry-Over Sprint 4 |
| PQC-56 APP-3 Profile-Screen | nicht angefangen | Carry-Over Sprint 4 |

**Endurteil:** Mobile-Pfad blockiert für Sprint-Goal-Erreichung. 14 SP Carry-Over nach Sprint 4.

### Quality (QUA) — 2 Stories, 13 SP — NICHT angefangen

| Story | Status | AC-Bilanz |
|---|---|---|
| PQC-66 QUA-4 Integration-Tests Broker-Flow (High) | nicht angefangen | Carry-Over Sprint 4 |
| PQC-67 QUA-5 End-to-End-Integration-Test (High) | nicht angefangen | Carry-Over Sprint 4 |

**Endurteil:** Tests-Schicht offen. 13 SP Carry-Over nach Sprint 4.

---

## 3. Stories, die nicht abgeschlossen wurden

6 Stories wurden nicht abgeschlossen, alle als Carry-Over nach Sprint 4 (laut Carry-Over-Strategie-Entscheidung beim Sprint-Closure).

| Story | T-Shirt | SP | Anteil fertig | Aktion | Begründung |
|---|---|---|---|---|---|
| PQC-58 APP-5 SessionContext | S | 2 | 0% | Carry-Over Sprint 4 | Voraussetzung für APP-6, blockiert Mobile-Demo |
| PQC-59 APP-6 secureClient.ts | M | 5 | 0% | Carry-Over Sprint 4 | Voraussetzung für APP-3, blockiert Mobile-Demo |
| PQC-55 APP-2 Home-Screen | S | 2 | 0% | Carry-Over Sprint 4 | UI-Story für Mobile-Demo |
| PQC-56 APP-3 Profile-Screen | M | 5 | 0% | Carry-Over Sprint 4 | Sprint-3-Goal-Demo-Story, das eigentliche Endziel |
| PQC-66 QUA-4 Integration-Tests Broker-Flow | M | 5 | 0% | Carry-Over Sprint 4 | Tests fehlen, Broker-Flow steht aber schon aus Sprint 2 |
| PQC-67 QUA-5 End-to-End-Integration-Test | L | 8 | 0% | Carry-Over Sprint 4 | E2E-Tests fehlen, sind aber wegen R-T08-Mobile-Limitation sowieso eingeschränkt automatisierbar |

**Summe Carry-Over:** 27 SP in 6 Stories.

**Konsequenz für Sprint 4:** Sprint 4 sollte ursprünglich reiner Doku-Sprint sein (R-S04 als Argument). Mit 27 SP Carry-Over wird Sprint 4 ein Hybrid-Sprint. Das verschärft R-S04 deutlich. Strategie für Sprint 4 wird im Sprint-4-Planning detailliert: Doku-Stories (DOC-1 Schlussbericht, DOC-2 Präsentation, DOC-3 README, DOC-4 ADRs) plus Performance-Benchmarks (QUA-6/QUA-7/QUA-8) haben harte Priorität, die Carry-Over-Stories werden in Reihenfolge der Sprint-Goal-Mobile-Demo-Relevanz priorisiert (APP-5 → APP-6 → APP-3, dann erst APP-2 und QUA-4/5).

---

## 4. Erkenntnisse für den Product Backlog

### 4.1 Neue Artefakte im Repo (aus Sprint 3)

- **`docs/wire_format.md`** als zentrale Protokoll-Spezifikation. Eine Wire-Format-Spec dokumentiert wie die Datenpakete zwischen zwei Systemen genau aussehen, also welche Felder ein Request hat, in welcher Reihenfolge und in welchem Format. Diese Datei legt das fest für die Schnittstelle zwischen Mobile-App und Server: Login-Token-Format, Session-Initialisierungs-Request-Felder (mit ML-KEM-Encapsulation-Daten), HTTP-Header für authentifizierte Session-Calls (X-Session-Id, X-Nonce), Replay-Schutz-Strategie mit Trade-Off-Begründung, und das Format der AES-GCM-verschlüsselten Server-Antworten. Während Sprint 3 mehrfach erweitert: CRY-7 hat das Skelett angelegt, DCH-2 hat die Data-Channel-Header ergänzt (v0.3), DCH-4 hat den Replay-Schutz dokumentiert (v0.4), DCH-3 hat das Encrypted-Response-Format finalisiert (v0.5). Wird in den Schlussbericht-Anhang eingebunden, weil es die Schnittstellen-Vereinbarung zwischen Server und Client kompakt festhält.
- **`server/scripts/demo_d008.py`** als reproduzierbares End-to-End-Demo-Script (Login → Session-Etablierung → HKDF → Encrypted-Profile → Decrypt-Response → Replay-Test-400). Mentor-Material plus Schlussbericht-Anhang.

### 4.2 Findings-Tracking aus Sprint 3

Mehrere Findings sind in den Stories selbst resolved worden (F-098 Cross-Validation-Vector, F-101 SES-3-API-Erweiterung, F-102 in PQC-46, F-109 in PQC-51). Zwei Findings als Hotfix-Recovery aus Sprint-2-Edit-Truncation-Schäden (F-106 login.tsx, F-108 main.py plus wire_format.md). F-107 Sandbox-Constraint (kein npm install im Container-Sandbox) als Tier-2-Polish dokumentiert.

### 4.3 Backlog-Adjustments für Sprint 4

Sprint 4 muss zwei Story-Sets balancieren:

- **Ursprünglich geplant für Sprint 4:** DOC-1 Schlussbericht (L, 13 SP), DOC-2 Präsentation (M, 8 SP), DOC-3 README (S, 2 SP), DOC-4 ADRs (S, 3 SP), QUA-6 Performance-Benchmark PQ-Session (S, 2 SP), QUA-7 Performance-Benchmark Token-Verifikation (S, 2 SP), QUA-8 Performance-Benchmark AES-GCM-Overhead (S, 2 SP), TOK-3 Schlüssel-Rotation (M, 5 SP, Should), TOK-4 JWKS-Endpoint (S, 2 SP, Should). Total: ca. 39 SP geplant.
- **Carry-Over aus Sprint 3:** 27 SP (4 APP plus 2 QUA).

**Gesamt-Belastung Sprint 4:** 39 + 27 = **66 SP** in 7 Tagen. Mit AI-Multiplier-Bandbreite 5x bis 14x ist das machbar aber sehr eng. Im Sprint-4-Planning muss aggressive Priorisierung erfolgen: Doku-Stories sind unverhandelbar (Bewertungs-relevant), Sprint-Goal-Mobile-Demo zweite Priorität, QUA-4/5 plus TOK-3/4 als Defer-Kandidaten.

### 4.4 Multiplier-Aufschlüsselung als Daten-Punkt

Sprint 3 hat 12 Stories Done mit aggregiertem Multiplier 10.4x (siehe Daily Journal Sprint-Aggregat). Aufschlüsselung wird in Sektion 6 detailliert. Wichtigster Befund: Hook-First-Pattern bei DCH-2 hat DCH-3 auf 14x getrieben, weil 80% der Logik schon im Vorgänger steckte. Solche Daten-Punkte fließen in das Reflexions-Kapitel des Schlussberichts.

---

## 5. Risk Review

### 5.1 Eingetretene Risiken in diesem Sprint

| Risk-ID | Was ist passiert? | Reaktion |
|---|---|---|
| R-S06 (Sprint-3-Komprimierung) | Sprint 3 wurde nur teilweise abgeschlossen (66% der SP). Die 4 APP-Stories plus QUA-4/5 sind nicht angefangen. | Carry-Over nach Sprint 4 statt Scope-Cut. Konsequenz: Sprint 4 wird Hybrid-Sprint, R-S04 verschärft. |
| R-P02 (Belastung) | Nicht eingetreten als Arbeit-Problem, aber faktisch eingetreten als "Ferien-Phase ohne aktive Projekt-Zeit". | Lesson für künftige Planung: Ferien-Phasen müssen klar als nicht-Arbeit-Phasen markiert werden, Projektzeit drum herum geplant. |
| Hook-First-Pattern in DCH-Bundle | Positive Beobachtung: DCH-2 hat 80% der Logik für DCH-3 hingelegt, DCH-3 lief in 30 Min durch. | Pattern bewusst weitergenutzt in Sprint-4-Carry-Over-Planung: APP-5 → APP-6 → APP-3 als sequentieller Stack ähnlich behandeln. |

### 5.2 Geänderte Risiko-Bewertung

| Risk-ID | Alte Bewertung | Neue Bewertung | Begründung |
|---|---|---|---|
| R-S04 (Doku-Zeit Sprint 4) | Score 6 Active | Score 9 (kritisch) | Sprint 4 hat jetzt 66 SP statt 39 SP geplant. Doku-Stories konkurrieren mit Carry-Over. |
| R-T02 (@noble API-Instabilität) | Score 4 Active | Score 2 Monitor | CRY-6 hat @noble erfolgreich integriert, keine Breaking Changes erlebt. Library stabiler als befürchtet. |
| R-T03 (Mobile-OS-Crypto-Quirks) | Score 4 Active | Score 4 Active (unverändert) | Nicht angefangen wegen Carry-Over. Wird in Sprint 4 bei APP-Stories real getestet. |
| R-T06 (Redis-Bugs) | Score 2 Monitor | Mitigated (28.06) | SES-3 plus DCH-4 mit Redis stabil. RedisNonceTracker mit atomarem SET NX EX funktioniert. |

### 5.3 Neue Risiken (in diesem Sprint identifiziert)

Keine neuen Risiken im Sprint 3 aufgetreten. R-T08 (Mobile-PQC-TLS-Limitation aus Sprint 2) wurde durch die Application-Layer-Crypto-Strategie umgangen (PQ-Crypto im JavaScript, nicht im TLS-Stack), bleibt aber als Befund im Risk Register.

### 5.4 Active-Watch-Status für Sprint 4

- [x] **R-S04 (Doku-Zeit Sprint 4 zu kurz)** auf Score 9 kritisch hochgestuft. Höchste Priorität in Sprint 4. Doku-Stories DOC-1/2/3/4 dürfen nicht durch Carry-Over weiter rutschen.
- [x] R-T03 (Mobile-OS-Crypto-Quirks) bleibt Active. APP-Stories werden in Sprint 4 angegangen, OS-spezifische Probleme können dort auftreten.
- [x] R-P02 (Belastung) unverändert beobachten. Sprint-3-Ferien-Lesson dokumentiert.
- [x] R-T08 (Mobile-PQC-TLS-Limitation) als Schlussbericht-Befund vorgemerkt.

---

## 6. Velocity dieser Sprint

### 6.1 Story Points

| Metrik | Wert |
|---|---|
| Geplante Story Points (Must Critical Path) | 63 SP |
| Geplante Story Points (Defer-Kandidaten High) | 16 SP |
| Geplante Story Points (Total Sprint Backlog) | 79 SP |
| **Abgeschlossene Story Points** | **52 SP (12 Stories, 66% von 79)** |
| Carry-Over nach Sprint 4 | 27 SP (6 Stories) |

Done: 11 von 15 Critical-Path-Stories plus 1 von 3 Defer-Kandidaten (SES-4, war im Bundle mit SES-1).

### 6.2 Arbeitszeit

| Metrik | Wert |
|---|---|
| Tatsächliche Arbeitsstunden Implementation | ca. 7.34h über drei Sessions (18-19.06 Block, 26.06 Session, 28.06 Catch-up) |
| Klassisch geschätzte Stunden (ohne AI) für die 12 Done-Stories | ca. 76h |
| **Aggregierter AI-Multiplier** | **10.4x** |

### 6.3 AI-Multiplier-Aufschlüsselung nach Story-Typ

| Story-Typ | Stories | Mittlerer Multiplier | Bemerkung |
|---|---|---|---|
| Crypto-Foundation | CRY-4, CRY-3, CRY-7, CRY-6 | 9.5x | Pattern-Replikation aus PQC-25 (Sprint 1), cryptography.hazmat als bekannte Standard-Lib |
| Session-Server | SES-3, SES-2, SES-1, SES-4 | 15.0x | SES-1 mit 22x als Outlier (Router plus Audit plus 2 in-Story-Findings-Fixes). SES-4 mit 18x weil Server-Logik schon in SES-1 erfüllt war |
| Data-Channel | DCH-1, DCH-2, DCH-4, DCH-3 | 9.5x | DCH-3 mit 14x als Hook-First-Pattern-Beispiel (DCH-2-Dependency lieferte 80% Vorarbeit) |

### 6.4 Beobachtungen für Schlussbericht und Mentor

Sprint-3-Multiplier 10.4x liegt zwischen Sprint 1 (6.4x verteilte Sessions) und Sprint 2 (13.6x Day-Marathon). Erklärung: Sprint 3 war eine Mischung aus Block-Sessions (18-19.06 plus 26.06 jeweils mehrstündig) und einer kurzen Catch-up-Session (28.06). Block-Anteil hat den Multiplier nach oben getrieben.

Wichtigste Befunde:

1. **Hook-First-Pattern.** Wenn eine vorherige Story (DCH-2) die Architektur und Dependencies sauber aufsetzt, kann die nachfolgende Story (DCH-3) auf einem hohen Multiplier laufen. Das ist ein dokumentierbares Pattern für die Sprint-Planung: Foundation-Stories vor Anwendungs-Stories sequenzieren.
2. **Bundle-Effekt mit Sub-Stories.** SES-4 (Algorithmus-Negotiation, Defer-Kandidat) lief in 10 Min weil die Logik schon in SES-1 mit-implementiert war. Defer-Kandidaten werden im Sprint manchmal "geschenkt" mitgenommen wenn sie eng an Critical-Path-Stories hängen.
3. **Pattern-Replikation aus früheren Sprints.** CRY-4 lief schnell weil LibOqsSignature aus Sprint 1 (PQC-25) als Vorlage diente. Sprint-1-Investitionen zahlen sich in Sprint 3 weiter aus.
4. **Workflow-Overhead nicht in Story-Zeit.** Audits, Hotfix-Recoveries (F-106, F-108 Edit-Truncation), Memory-Updates und Closing-Reviews sind nicht in den Story-Worklogs erfasst, addieren aber zur realen Session-Dauer. Reale Session-Dauer ca. 30 bis 60% länger als reine Story-Zeit.

Für das Reflexions-Kapitel des Schlussberichts ist der Hook-First-Pattern-Befund wichtig: er zeigt dass die AI-Effizienz nicht nur vom Session-Format abhängt sondern auch von der Story-Sequenzierungs-Strategie.

---

## 7. Stakeholder-Demo und Feedback-Erwartung

### 7.1 Demo-Material

Sprint 3 hat eine neue reproduzierbare Demo erstellt:

- **D-008 End-to-End-Roundtrip (Server-Side)** in `server/scripts/demo_d008.py`. 8-Schritt-Pipeline: Login → ML-KEM-Handshake → HKDF-Session-Key-Ableitung → Encrypted `/api/profile`-Request → Decrypt-Response → Replay-Test mit 400-Antwort. Läuft im Docker-Container, ca. 30 Sekunden Demo-Zeit. Mentor-Material plus Schlussbericht-Anhang.

Bestand aus früheren Sprints (relevant für Sprint 4 plus Schluss-Präsentation):

- D-001 Crypto-Foundation, D-002 Broker-Token-Ausstellung, D-003 Broker-Token-Verify, D-004 Local-Login-Pipeline aus Sprint 1.
- D-005 PQC-TLS-Handshake X25519MLKEM768, D-006 Mobile-Login-Flow aus Sprint 1 plus Sprint 2.
- D-007 PQ-TLS-Handshake-Verifikation (Backend-Demo) aus Sprint 2.

Sprint-3-Lücke: **keine D-NNN-Demo für Mobile-End-to-End-Pfad**, weil die APP-Stories nicht angegangen wurden. Wenn Mobile-Demo in Sprint 4 nachgeholt wird, kommt D-009 dazu.

### 7.2 Mentor-Termin vom 20.06.2026 (Feedback-Notizen)

Der Mentor-Termin am 20.06 wurde durchgeführt. Konkrete Feedback-Punkte aus dem Gespräch:

- **Demo-Struktur kurz besprochen.** Der Mentor hat auf das Beispiel eines Mitschülers hingewiesen das ich als Referenz für Aufbau und Tiefe der Demo-Doku nutzen kann.
- **Commit-Nachvollziehbarkeit als Schwachstelle.** Der Mentor hat darauf hingewiesen dass ich wegen meiner AI-getriebenen Arbeitsweise viel weniger und weniger nachvollziehbare Commits mache als ein klassischer Solo-Workflow es erzeugt hätte. Das ist ein wichtiger Befund weil die Commit-Historie ein zentrales Bewertungs-Element ist (Nachvollziehbarkeit der Implementation-Schritte über Zeit).

**Mein Learning daraus für das nächste Schulprojekt:** Ich möchte beim nächsten Projekt weniger AI einsetzen und stattdessen ein kleineres Projekt machen. Dadurch werde ich den technischen Teil besser lernen und auch ein klareres, nachvollziehbares Vorgehen vorweisen können, was für die Kommunikation mit den Stakeholdern wichtig ist.

### 7.3 Geplante Themen für den nächsten Mentor-Termin

Der nächste Mentor-Termin findet vor der Abgabe (04/05.07.2026) statt. Bei diesem Termin sollte alles inhaltlich fertig sein. Mein Ziel ist es, gezielt Input darüber einzuholen **was noch fehlt** bevor die Abgabe erfolgt. Konkret:

- Schlussbericht in vorletzter Fassung vorzeigen, Lücken identifizieren lassen.
- Demos (D-001 bis D-008 plus D-009 falls Mobile-Demo geschafft) live vorführen, ggf. Verbesserungs-Hinweise sammeln.
- Abgabe-Logistik final klären (Format, Repo-Zugang, Demo-Setup für Kolloquium).
- R-T08 Mobile-PQC-TLS-Limitation als Befund präsentieren und prüfen ob Mentor das als ausreichend dokumentiert hält.

---

## 8. Notizen für die Retrospektive

Stichpunkte für die Retro-Diskussion, ausführlicher in `04_retrospective.md`.

- **Ferien-Phase als Projekt-Stocker.** Ich war in den Ferien und habe mir nicht so viel Zeit fürs Projekt genommen wie geplant. Lesson: Ferien als echte Ferien planen, Projekt-Arbeitszeit drum herum. Versuche während Ferien zu arbeiten funktionieren bei mir nicht zuverlässig.
- **Mentor-Update während Sprint 3 ausgelassen.** Aus Sprint-2-Retro war eigentlich die Regel "bei jedem Stocker innerhalb 24-48h Update verschicken". Sprint 3 hatte zwar keinen plötzlichen Stocker wie Sprint 2, aber die Ferien-bedingte Reduzierung war auch ein Status den die Mentoren hätten wissen können. Update wird zwei Tage nach Sprint-Ende nachgeholt. Lesson noch nicht vollständig verinnerlicht, aber sichtbar besser als in Sprint 2.
- **Hook-First-Pattern als bewusste Architektur-Strategie.** DCH-2 hat die Foundation gelegt, DCH-3 lief in 30 Min. Ähnlich für SES-1 zu SES-4. Will ich für Sprint-4-Carry-Over (APP-5 → APP-6 → APP-3) wiederholen.
- **AI-Less-Learning für nächstes Schulprojekt.** Mentor hat darauf hingewiesen dass meine AI-getriebene Arbeitsweise viel weniger und weniger nachvollziehbare Commits produziert als klassischer Solo-Workflow. Für das nächste Projekt: weniger AI, kleineres Projekt, technisch besser lernen, klareres Vorgehen für Stakeholder-Kommunikation. Wichtiger Punkt fürs Reflexions-Kapitel im Schlussbericht (AI als Werkzeug, nicht als Selbstläufer).
- **Multiplier 10.4x mit Hook-First-Pattern.** Sprint 3 lag zwischen Sprint 1 und Sprint 2 in Bezug auf Multiplier. Datenpunkt für die Reflexion: Multiplier hängt von Session-Format plus Story-Sequenzierung ab. Wichtig im Schlussbericht ehrlich zu unterscheiden zwischen Coding-Output-Multiplier und tatsächlichem Lern-Effekt für mich als Entwickler.
- **Sprint-4-Hybrid-Risiko.** R-S04 ist jetzt kritisch (Score 9). Doku muss Vorrang vor Carry-Over haben. Schulprojekt-Bewertung steht und fällt mit dem Schlussbericht plus Präsentation, nicht mit der App-Demo-Vollständigkeit.
- **Wire-Format-Spec als Architektur-Artefakt.** docs/wire_format.md ist über Sprint 3 organisch gewachsen (v0 bis v0.5), mit Architektur-Entscheidungen direkt im File dokumentiert. Schönes Beispiel für gelebte Architektur-Doku.
