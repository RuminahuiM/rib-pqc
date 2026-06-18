# Sprint Planning: Sprint 3

**Datum:** 18.06.2026
**Sprint-Zeitraum:** 18.06 bis 28.06.2026 (11 Kalendertage, komprimiert wegen Sprint-2-Verzögerung, ursprünglich 14 Tage geplant)
**Timebox Planning:** 1 Stunde

---

## 1. Sprint-Ziel (Warum ist dieser Sprint wertvoll?)

> Demo-orientiert formuliert.

**Sprint Goal:** Am Sprint-Ende ist der Mobile-Pfad End-to-End funktional auf iPhone via Expo Go: User öffnet Profile-Screen, App etabliert eine PQ-Session zum Server (ML-KEM-768 Key-Encapsulation, HKDF-Session-Key-Ableitung), ruft `/api/profile` über die etablierte Session AES-256-GCM-verschlüsselt auf, Server entschlüsselt, antwortet verschlüsselt zurück, Profile-Daten werden in der App angezeigt. End-to-End-Demo D-008 reproduzierbar.

**Implizit dazu:**

- Server-seitige Crypto-Foundation für ML-KEM plus HKDF plus AEAD steht (CRY-3, CRY-4, CRY-7).
- Server-seitiger Session-Layer mit Redis-Persistenz steht (SES-1, SES-2, SES-3).
- Server-seitiger Data-Channel mit Header-Routing plus Replay-Schutz steht (DCH-1 bis DCH-4).
- Client-seitige Crypto-Abstraction via `@noble/post-quantum` plus `@noble/ciphers` plus `@noble/hashes` steht (CRY-6).
- App hat SessionContext, secureClient.ts, Home-Screen, Profile-Screen (APP-2, APP-3, APP-5, APP-6).

**Anmerkung zur Plattform-Limitation:** Die PQ-Session wird auf der Application-Layer (ML-KEM-Encap im App-Code, AES-GCM-Verschlüsselung als Payload) etabliert, nicht auf TLS-Layer. Der TLS-Transport zwischen App und Server läuft mit klassischer ECDHE-Group, weil iOS/Android System-TLS-Stacks X25519MLKEM768 noch nicht unterstützen (R-T08 aus Sprint 2). Das macht Sprint 3 möglich obwohl R-T08 existiert, weil die PQ-Crypto auf der App-Layer und nicht auf der TLS-Layer passiert.

---

## 2. Ausgewählte Backlog-Items

Reihenfolge basiert auf Dependencies-Analyse vom Implementation-Chat-Agent. Sprint 3 hat 18 Stories mit total 79 SP.

### Critical Path (Highest, Sprint-Goal-erfüllend, 63 SP)

| Jira-Key | Story | T-Shirt | SP | Block |
|---|---|---|---|---|
| PQC-24 | CRY-4: liboqs-python ML-KEM-Wrapper (Server) | M | 5 | Crypto-Foundation Server |
| PQC-23 | CRY-3: Crypto-Facade KEM/HKDF/AEAD (Server) | M | 5 | Crypto-Foundation Server |
| PQC-27 | CRY-7: Algorithmus-Identifier in Krypto-Artefakten | S | 2 | Crypto-Foundation Server |
| PQC-48 | SES-3: Session-Store mit TTL (Redis) | M | 5 | Session-Server |
| PQC-47 | SES-2: HKDF-Session-Key-Ableitung | S | 2 | Session-Server |
| PQC-46 | SES-1: POST /session/init mit ML-KEM-Encap | L | 8 | Session-Server |
| PQC-50 | DCH-1: AES-256-GCM Encrypt/Decrypt Wrapper | S | 2 | Data-Channel Server |
| PQC-51 | DCH-2: Header-basiertes Session-Routing | M | 5 | Data-Channel Server |
| PQC-53 | DCH-4: Replay-Schutz via Nonce-Tracking | M | 5 | Data-Channel Server |
| PQC-52 | DCH-3: Geschützter API-Endpoint /api/profile | M | 5 | Data-Channel Server |
| PQC-26 | CRY-6: Client-Side Crypto-Abstraction (App) | M | 5 | Crypto-Foundation Client |
| PQC-58 | APP-5: SessionContext (globaler Session-State, in-memory) | S | 2 | App-Side |
| PQC-59 | APP-6: secureClient.ts (HTTP-Wrapper mit auto-encrypt) | M | 5 | App-Side |
| PQC-55 | APP-2: Home-Screen mit Logout | S | 2 | App-Side |
| PQC-56 | APP-3: Profile-Screen mit /api/profile-Aufruf | M | 5 | App-Side, Sprint-Goal-Demo |

**Summe Critical Path:** 63 SP. Mobile-Demo D-008 möglich nach APP-3.

### Defer-Kandidaten (High, Defer falls Sprint überzeichnet, 16 SP)

| Jira-Key | Story | T-Shirt | SP | Defer-Logik |
|---|---|---|---|---|
| PQC-49 | SES-4: Algorithmus-Negotiation | S | 3 | Should-Priorität laut Original-Backlog. Defer als erste falls Engpass. |
| PQC-66 | QUA-4: Integration-Tests Broker-Flow | M | 5 | Tests können in Sprint 4 als Polish nachgeholt werden. |
| PQC-67 | QUA-5: End-to-End-Integration-Test | L | 8 | Analog QUA-4. Falls Sprint-Goal-Demo D-008 manuell läuft, sind formelle E2E-Tests Sprint-4-Material. |

**Summe Defer-Kandidaten:** 16 SP.

**Sprint-Total (Critical Path plus Defer-Kandidaten):** 79 SP geplant.

### Sprint-Level-Stretch

Keine. Sprint 3 ist mit 79 SP bei 11 Tagen Komprimierung schon ambitioniert.

---

## 3. Cross-Cutting-Concerns-Checkliste

Aus Sprint-1-Retro Maßnahme 1, erweitert mit Sprint-2-Retro Maßnahme 2 (Plattform-Capability-Check).

| Concern | Status | Aktion |
|---|---|---|
| ML-KEM-Implementierung Server-Side via liboqs-python | Vorhanden | CRY-4 deckt Wrapper, CRY-3 deckt Facade |
| ML-KEM-Implementierung Client-Side via @noble/post-quantum | Vorhanden | CRY-6 deckt App-Side |
| HKDF-Session-Key-Ableitung Server plus Client identisch | Vorhanden | SES-2 (Server) plus CRY-6 (App) müssen mit identischen Parametern arbeiten (info, salt). Bei SES-2-Story-Start klären |
| Session-Store TTL plus Cleanup | Vorhanden | SES-3 deckt Redis-Store mit TTL, Lookup, Refresh, Invalidierung |
| Replay-Schutz Trade-off Stateful vs Timestamp | Vorhanden | DCH-4 fordert Trade-Off-Dokumentation. Entscheidung beim DCH-4-Story-Start |
| AES-GCM Nonce-Management Client plus Server | Vorhanden | DCH-1 plus DCH-2. Bei Story-Start klären: pro-Request-Nonce ist Standard, nicht Counter-basiert |
| Algorithmus-Identifier-Konsistenz | Vorhanden | CRY-7 als eigene Story |
| Plattform-Capability-Check (aus Sprint-2-Retro) | Erforderlich | Mobile-Side: @noble/post-quantum ist JavaScript-Lib, läuft im React-Native-JS-Bundle ohne Native-Modul-Dependency. Bestätigt verfügbar auf iOS plus Android Expo Go. Kein PQ-TLS auf Mobile-Transport (R-T08), aber PQ auf Application-Layer funktioniert weil reines JS. |
| Token-Verifikation für /session/init | Vorhanden | SES-1 fordert Authorization-Bearer-Token-Validierung. Nutzt TokenService aus Sprint 1 |
| Session-Key wird nicht persistiert (Sicherheit) | Vorhanden | APP-5 (SessionContext nur in-memory) plus SES-3 (Server-Side Redis mit TTL). Session-Key ist nur im Speicher, nicht in secure-store |
| Error-Handling bei Session-Ablauf | Vorhanden | APP-6 secureClient triggert Re-Auth bei 401/expired |

**Beobachtung:** Mit der Plattform-Capability-Erweiterung (Top-3-Maßnahme aus Sprint-2-Retro) ist erkannt dass die PQ-Session auf Application-Layer (JavaScript) implementiert wird, nicht auf TLS-Layer. Das war im Original-Design (`07_design.md`) so vorgesehen, aber explizit beim Sprint-3-Planning verifiziert.

---

## 4. Umsetzungsplan (Arbeitstag-basiert)

Sprint-3-Zeitraum: 18.06 bis 28.06.2026 (11 Kalendertage).
Standard-Schedule: Wochenenden plus Mittwoch.
Effektive Arbeitstage: **4 reguläre Tage** (So 21.06, Mi 24.06, Sa 27.06, So 28.06).
Plus: Mentor-Termin am 20.06 (kein voller Arbeitstag).
Plus: heute 18.06 als Planning-Tag im Strategie-Chat.

Mit aggregiertem AI-Multiplier aus Sprint 1 (6.4x) und Sprint 2 (13.6x Block-Session) und 63 SP Critical Path entspricht das klassisch ca. 90 SP-Stunden. Mit erwartetem 5x bis 8x Multiplier für Crypto-Implementation sind das 11 bis 18h tatsächliche Arbeit. Verteilt auf 4 Arbeitstage ca. 3 bis 5h pro Tag.

| Tag | Datum | Geplante Stories | SP | Begründung |
|---|---|---|---|---|
| Tag 1 | So 21.06 | CRY-4, CRY-3, CRY-7 | 12 | Crypto-Foundation Server: Wrapper plus Facade plus Identifier. Alles weitere baut darauf auf. |
| Tag 2 | Mi 24.06 | SES-3, SES-2, SES-1 | 15 | Session-Server-Layer: Redis-Store, HKDF, /session/init. SES-1 ist L=8 SP, deshalb mit den kleineren SES-Stories kombiniert für Bundle-Effekt. |
| Tag 3 | Sa 27.06 | DCH-1, DCH-2, DCH-4, DCH-3, CRY-6 | 22 | Data-Channel Server plus Client-Crypto-Foundation. Längster Slot, viele M-Stories aber mit hohem Code-Reuse-Potential. |
| Tag 4 | So 28.06 | APP-5, APP-6, APP-2, APP-3, plus Sprint Review/Retro plus D-008 Demo | 14 | App-Side End-to-End plus Sprint-Goal-Demo. Sprint Review plus Retro am Tagesende. |

**Halbzeit-Check:** Mi 24.06 nach Tag 2. Wenn CRY-Foundation plus mindestens SES-3/SES-2 nicht Done sind: harte Scope-Cut-Entscheidung. SES-4, QUA-4, QUA-5 sofort nach Sprint 4 verschieben (als Polish-Material falls Zeit).

**Defer-Pfad bei Verzug:**

- Falls Tag 2 nicht durch: SES-4 sofort defer (Should), QUA-4 plus QUA-5 als Sprint-4-Polish markieren.
- Falls Tag 3 nicht durch: APP-2 (Home-Screen) als reduzierbar markieren (Home-Screen ist nicht Sprint-Goal-blockierend).
- Falls Tag 4 nicht durch: D-008-Demo manuell statt automatisiert. Sprint Review plus Retro trotzdem am 28.06 abend.

---

## 5. Sprint-Risiken und Critical Path

**Active Risks aus dem Risk Register die in Sprint 3 direkt relevant sind:**

| Risk-ID | Titel | Score | Sprint-3-Relevanz |
|---|---|---|---|
| R-S06 | Sprint-3-Komprimierung wegen Sprint-2-Verzögerung | 6 (Active) | Direkt relevant. 11 statt 14 Tage. Aggressive Defer-Strategie falls Halbzeit-Check rot. |
| R-P02 | Berufliche Belastungen HEKS | 6 (Active, hochgestuft in Sprint 2) | Real eingetreten in Sprint 2. Falls Sprint 3 ebenfalls von Arbeit-Problem getroffen wird: Mentor-Update binnen 48h. |
| R-T03 | Mobile-OS-spezifische Crypto-Quirks | 4 (Active) | Direkt relevant für CRY-6 (Client-Crypto), APP-6 (secureClient). @noble-Library plus iOS-Quirks. |
| R-T02 | @noble/post-quantum API-Instabilität | 4 (Active) | Direkt relevant für CRY-6. Version pinning Pflicht. |
| R-T06 | Redis-Session-Store Bugs | 2 (Monitor) | Direkt relevant für SES-3. Integration-Tests mit echtem Redis bei Story-Start |
| R-S04 | Doku-Zeit Sprint 4 zu kurz | 4 (Active) | Sprint-4-Doku darf nicht durch Sprint-3-Carry-Over reduziert werden. Sprint 4 unantastbar. |

**Critical-Path-Definition für Sprint 3 (Sprint-Goal Variante C):**

CRY-4 → CRY-3 → SES-3 → SES-2 → SES-1 → DCH-1 → DCH-2 → DCH-3 → CRY-6 → APP-5 → APP-6 → APP-3

= 12 Stories Critical Path. CRY-7 plus DCH-4 plus APP-2 sind Quality-of-Life aber nicht strikt Sprint-Goal-blockierend.

**Sprint-Abbruch-Kriterien:**

- Falls am Halbzeit-Check 24.06 die CRY-Foundation nicht Done ist: Sprint-Goal auf reduziert "Server-Side Session plus Data-Channel ohne Mobile-Demo" anpassen, Mobile-Stories in Sprint 4 als Polish.
- Falls Sprint 3 nicht bis 28.06 fertig wird: harte Carry-Over-Entscheidung mit Schwerpunkt auf D-008-Demo. Sprint 4 startet trotzdem am 29.06 mit Doku-Fokus. Maximaler Sprint-3-Carry-Over: 2 Stories.

---

## 6. Definition-of-Done-Check und Sprint-Anmerkungen

**Definition of Done für Sprint 3:** unverändert gegenüber Sprint 1/2, dokumentiert in `../../docs/08_scrum_setup.md` Sektion 5.3, plus seit dem Jira-Custom-Field-Setup als 11-Punkte-Checkliste pro Story im Field "DoD - Globale Definition of Done".

**Plus Sprint-1-und-2-etablierte Konventionen:**

- HARTE WORKFLOW-REGEL: Done-Transition nur nach explizitem User-OK.
- Closing-Review-Prozedur mit 7 Phasen plus Phase 8 Demo-Check.
- 4-Tier-Findings-Klassifikation.
- D-NNN-Demo-Konvention.
- Evidence-File pro Story plus Zeit-Tracking pro Story.

**Sprint-spezifische Anmerkungen:**

- **Block-Session vs verteilte Sessions.** Nach Sprint-2-Erfahrung (Block-Session ergab 13.6x Multiplier aber Konventionen wurden ausgesetzt) plane ich Sprint 3 explizit auf verteilte Arbeitstage. Wenn doch eine Block-Session nötig wird, beim Sprint-Start im Implementation-Chat bewusst entscheiden welche Konventionen pausieren und das dokumentieren.
- **Mentor-Update-Reflex.** Aus Sprint-2-Retro-Maßnahme 1: bei jedem unerwarteten Stocker innerhalb 24-48h kurzes Mentor-Update verschicken. Adressiert das Versäumnis aus Sprint 2.
- **AI-Multiplier-Hypothese-Update.** Sprint 1 ergab 6.4x heterogen, Sprint 2 ergab 13.6x Block-Effekt. Für Sprint 3 mit echter Crypto-Implementation (KEM, HKDF, AEAD) erwarte ich 5x bis 8x. Daten weiter tracken pro Story.
- **Mobile-Demo-Strategie.** D-008 ist Sprint-Goal-Demo plus Material für Mentor-Schluss-Termin plus Schlussbericht. Reproduzierbarkeit hat Priorität, das Skript muss am Sprint-Ende ohne Hand-Tuning laufen.
- **Sprint 4 unantastbar.** Egal was in Sprint 3 passiert, Sprint 4 startet am 29.06 mit Doku-Fokus. Wenn Sprint 3 nicht fertig: maximal 2 Carry-Over-Stories ins Sprint 4, alles andere wird gestrichen oder als Project-Limitation dokumentiert.
