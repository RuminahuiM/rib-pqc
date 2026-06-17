# Sprint Planning: Sprint 2

**Datum:** 01.06.2026
**Sprint-Zeitraum:** 01.06 bis 14.06.2026 (14 Kalendertage)
**Timebox Planning:** 1 Stunde

---

## 1. Sprint-Ziel (Warum ist dieser Sprint wertvoll?)

> Demo-orientiert formuliert.

**Sprint Goal:** Am Sprint-Ende läuft der Mobile-Client gegen den Server über hybride PQC-TLS-Verbindung (X25519MLKEM768), und der User kann sich via Google oder Microsoft einloggen und einen ML-DSA-65-signierten Broker-Token erhalten.

**Implizit dazu:**

- Identity-Broker-Federation-Logik läuft End-to-End (OAuth2-Flow gegen externe IdPs, Token-Exchange, User-Linking External-Sub zu lokalem User).
- Hybride PQC-TLS-Verbindung X25519MLKEM768 ist auf dem Server (nginx mit oqs-provider) und im Mobile-Client (über Expo-Networking) aktiv.
- OAuth-Apps bei Google Cloud Console und Microsoft Azure AD sind registriert und konfiguriert.

---

## 2. Ausgewählte Backlog-Items

### Critical Path (Highest, blockiert Sprint-Goal-Erfüllung, 39 SP)

| Jira-Key | Story | Bezug | T-Shirt | SP | Abhängigkeiten |
|---|---|---|---|---|---|
| PQC-84 | BRK-0: OAuth-Apps registrieren | UC-2/3, R-T04, R-S05 | S | 2 | Sprint-2-Start, blockt BRK-5, BRK-6 |
| PQC-36 | BRK-1: External-IdP-Registry | FR-Broker-1 | M | 5 | blockt BRK-5, BRK-6 |
| PQC-37 | BRK-2: OIDC Code Flow mit PKCE | UC-2/3, FR-Broker-2 | L | 8 | hängt von BRK-1 ab |
| PQC-38 | BRK-3: ID-Token-Verifikation gegen JWKS | FR-Broker-3 | M | 5 | hängt von BRK-2 ab |
| PQC-39 | BRK-4: Identity-Normalisierung plus email_verified | FR-Broker-4 | M | 5 | hängt von BRK-3, AUT-1 ab |
| PQC-40 | BRK-5: Google IdP-Plugin | UC-2, FR-Broker-1 | M | 5 | hängt von BRK-0, BRK-1 ab |
| PQC-42 | BRK-7: CSRF/State-Schutz plus Redis-Storage | NFR-Sec-5 | S | 2 | hängt von BRK-2 ab |
| PQC-60 | APP-7: Google-Login via expo-auth-session | UC-2 | M | 5 | hängt von APP-1, BRK-5 ab |
| PQC-43 | TLS-1: nginx X25519MLKEM768 | NFR-Sec-1, Design 3.1 | M | 5 | hängt von INF-4 ab (schon done in Sprint 1) |

**Summe Critical Path:** 42 SP (Korrektur: 2+5+8+5+5+5+2+5+5 = 42 SP)

### Must non-blocking, Defer-Kandidaten falls Sprint überzeichnet (14 SP)

| Jira-Key | Story | Bezug | T-Shirt | SP | Defer-Logik |
|---|---|---|---|---|---|
| PQC-41 | BRK-6: Microsoft IdP-Plugin | UC-3, FR-Broker-1 | M | 5 | Sprint-Goal mit nur Google noch erfüllbar (Variante B leicht reduziert) |
| PQC-61 | APP-8: Microsoft-Login via expo-auth-session | UC-3 | M | 5 | analog APP-7-Defer-Logik |
| PQC-44 | TLS-2: PQ-Handshake-Verifikation mit oqs-curl | NFR-Sec-1 | S | 2 | Verifikations-Story, kann als Demo-Story nach TLS-1 |
| PQC-45 | TLS-3: nginx Reverse Proxy | Design 3.1 | S | 2 | Falls Auth-Service direkt auf TLS-Port lauscht, weniger kritisch |

**Summe Must non-blocking:** 14 SP

**Sprint-Total (Must Critical Path plus non-blocking):** 56 SP geplant.

### Sprint-Level-Stretch

Keine. Sprint 1 hat alle App-Bundle-Stretch-Stories vorgezogen (APP-1, APP-4, APP-9 sind Done). Sprint 2 hat keine Stretch-Stories im Backlog.

---

---

## 3. Cross-Cutting-Concerns-Checkliste

Aus Sprint-1-Retro Top-Maßnahme 1. Vor Sprint-Start durchgegangen, Lücken in Story-ACs adressiert.

| Concern | Status | Aktion erledigt |
|---|---|---|
| OAuth-State-Parameter gegen CSRF | Vorhanden | BRK-7 (PQC-42) plus APP-7 AC-3, Storage in BRK-7 AC-5 ergänzt |
| PKCE im Mobile-Flow | Vorhanden | BRK-2 AC-3 server-side, APP-7 AC-2 client-side, APP-8 erbt von APP-7 |
| ID-Token-Verifikation (Sig, Iss, Aud, Exp) | Vorhanden | BRK-3 AC-2 plus JWKS-Caching mit TTL |
| Identity-Normalisierung (External-Sub-Linking) | Vorhanden | BRK-4 deckt First-Login, Repeat-Login, Email-Konflikt-Linking |
| Provider-spezifische Sub-Convention | Vorhanden | BRK-5 Google `sub`, BRK-6 Microsoft `oid` |
| TLS-Cert-Handling | Akzeptabel | TLS-1 AC-2 self-signed ECDSA für Sprint 2, ML-DSA-Cert via Stretch STR-3 |
| OAuth-App-Registrierung | Lücke geschlossen | Neue Story BRK-0 (PQC-84) angelegt mit blocks BRK-5/BRK-6, Priority Highest |
| State plus PKCE-Verifier-Storage server-side | Lücke geschlossen | BRK-7 AC-5 ergänzt: Redis mit TTL 10 Min, PKCE-code_verifier zusammen mit State, one-shot Delete nach Callback |
| Email-Verifikation Claim (`email_verified`) | Lücke geschlossen | BRK-4 AC-6 ergänzt: User-Linking nur bei `email_verified=true`, sonst neuer Record ohne Linking, Log-Event `auth.federated.email_unverified` |
| TLS-1/TLS-2 vs PQC-18 Überlappung | Hinweis im Sprint-Start | PQC-18 hat X25519MLKEM768-Handshake schon live demonstriert (D-005). Beim Sprint-Start im Implementation-Chat klären ob TLS-1 SP reduziert wird oder TLS-2 in Closing-Review von TLS-1 gefaltet wird. |
| Mobile-Federation-PKCE | Vorhanden | APP-7 AC-2 plus APP-8 erbt |

---

## 4. Umsetzungsplan (Arbeitstag-basiert)

Sprint-2-Zeitraum: 01.06 bis 14.06.2026 (14 Kalendertage).
Standard-Schedule: Wochenenden plus Mittwoch.
Effektive Arbeitstage: **5 Tage** (Sa 06.06, So 07.06, Mi 10.06, Sa 13.06, So 14.06).

| Tag | Datum | Geplante Stories | SP | Begründung |
|---|---|---|---|---|
| Tag 1 | Sa 06.06 | BRK-0 (Setup), BRK-1, BRK-7 | 9 | Foundation-Tag: OAuth-Apps registrieren (Microsoft-Approval-Wartezeit-Risiko früh anstossen), Registry-Foundation, State-Schutz mit Redis-Storage |
| Tag 2 | So 07.06 | BRK-2, BRK-3 | 13 | Server-Core: OIDC Code Flow mit PKCE plus ID-Token-Verifikation. Längster Slot wegen BRK-2 (L=8 SP) |
| Tag 3 | Mi 10.06 | BRK-4, BRK-5 | 10 | User-Linking mit email_verified-Check plus Google-Plugin. Kürzerer Mittwoch-Abend-Slot |
| Tag 4 | Sa 13.06 | APP-7, TLS-1, TLS-2, TLS-3 | 14 | Mobile-Google-Login plus TLS-Bundle. TLS-Stories kompakt da PQC-18 schon vieles vorgemacht. Sprint-Goal-Demo D-007 (Mobile-Google plus PQC-TLS) am Tagesende möglich |
| Tag 5 | So 14.06 | BRK-6, APP-8, plus Sprint Review/Retro | 10 | Microsoft-Federation als finale Erweiterung. Sprint Review plus Retro am Tagesende |

**Defer-Pfad bei Verzug:**

- Falls Tag 3 nicht komplett durch: BRK-6 und APP-8 in Sprint 3 schieben. Sprint-Goal Variante B bleibt mit Google-Federation erfüllbar.
- Falls Tag 4 nicht durch: TLS-2 plus TLS-3 in Sprint 3 schieben.
- Falls Tag 5 nicht durch: BRK-6 plus APP-8 sind die letzten Defer-Kandidaten, Sprint Review/Retro müssen aber stattfinden.

**Risiko-Anmerkung:** BRK-2 mit L=8 SP an Tag 2 ist die grösste Einzel-Schätzung im Sprint. L-Stories überziehen häufig. Falls am Halbzeit-Check (Mittwoch 10.06) BRK-2 plus BRK-3 nicht beide Done sind, sollten BRK-6 und APP-8 sofort als Defer markiert werden.

---

## 5. Sprint-Risiken und Critical Path

**Active Risks aus dem Risk Register die in Sprint 2 direkt relevant sind:**

| Risk-ID | Titel | Score | Sprint-2-Relevanz |
|---|---|---|---|
| R-T04 | OIDC-Provider-Setup-Komplexität | 6 (Active) | Direkt relevant für BRK-0 (vorgezogenes Setup) und BRK-5/BRK-6. Microsoft App-Approval-Wartezeit ist konkret befürchtet. |
| R-S05 | Externe Abhängigkeiten OAuth-App-Setup verzögern | 4 (Active) | Adressiert durch BRK-0 als erste Story. Falls Microsoft trotzdem blockt, BRK-6/APP-8 defer-pfad nutzen. |
| R-S01 | Sprint-Kapazität wird überschritten | 6 (Active) | 56 SP in 5 Arbeitstagen ist ambitioniert. AI-Multiplier-Annahme 6.4x ist optimistisch für Federation-Stories (eher 3-5x erwartet). |
| R-T02 | @noble/post-quantum API-Instabilität | 4 (Active) | Bei APP-7/APP-8 wenn das Mobile-Client-Crypto über @noble läuft. Aktuell Stretch-relevant, in Sprint 2 nur Federation-Stories die nicht direkt von Noble-PQ abhängen. |
| R-T07 | Expo Deep-Link für OAuth-Callback im Expo Go nicht zuverlässig | 4 (Active, neu in Sprint 2) | APP-7/APP-8 Deep-Link-Pfad. Mitigation: Fallback auf manuelles Code-Copy in der Demo. Siehe Risk Register R-T07. |

**Critical-Path-Definition für Sprint 2:**

Der minimale Critical Path für Sprint-Goal-Erfüllung (Variante B reduziert auf Google-Federation plus PQC-TLS):

BRK-0 → BRK-1 → BRK-2 → BRK-3 → BRK-4 → BRK-5 → BRK-7 → APP-7 → TLS-1

Falls eine dieser 9 Stories bis Tag 4 (Sa 13.06) nicht Done ist, Sprint-Goal in Gefahr. Halbzeit-Check am Mittwoch 10.06 muss BRK-1 bis BRK-3 Done zeigen, sonst Eskalation (defer alle High-Stories sofort).

**Sprint-Abbruch-Kriterien:**

- Microsoft OAuth-App-Approval länger als 5 Arbeitstage Wartezeit: BRK-6/APP-8 definitiv in Sprint 3.
- TLS-1 funktioniert nicht trotz PQC-18-Foundation: TLS-Aspekt aus Sprint-Goal streichen, Variante B auf Variante A reduzieren (Federation-only).
- BRK-2 (OIDC Code Flow mit PKCE) zieht länger als 2 Arbeitstage: Sprint massiv reduzieren, eventuell Sprint-Verlängerung erwägen (Adaption).

---

## 6. Definition-of-Done-Check und Sprint-Anmerkungen

**Definition of Done für Sprint 2:** unverändert gegenüber Sprint 1, dokumentiert in `../../docs/08_scrum_setup.md` Sektion 5.3. Das umfasst:

- Code in main gemergt mit atomic commits.
- Pytest-Coverage für Happy-Path plus mindestens einen Fehlerfall bei funktionalen Änderungen.
- AC nachprüfbar erfüllt.
- Keine offenen kritischen Warnungen im Sprint-Scope-Code.
- Doku aktualisiert (README, relevante Markdowns).
- Quellen in `04_quellen.md`.
- Evidence-File angelegt im `evidence/`-Ordner.
- Jira-Done-Comment mit strukturierter Erledigt/Abweichungen/Links.

**Plus die Sprint-1-etablierten Konventionen:**

- HARTE WORKFLOW-REGEL: Done-Transition nur nach explizitem User-OK, nie eigenständig von der AI.
- Closing-Review-Prozedur mit 7 Phasen plus Phase 8 Demo-Check.
- 4-Tier-Findings-Klassifikation (Tier 0 in-Story-resolved, Tier 1 neue Jira-Story, Tier 2 deferred in `13_deferred_findings.md`, Tier 3 Memory).
- D-NNN-Demo-Konvention mit Trigger Sprint-Goal-Meilenstein, Mentor-Termin, Session-Ende.
- Zeit-Tracking pro Story in Daily-Journal-Tabelle plus Jira-Worklog mit Coding plus Recherche plus Closing-Review plus Demo-Erstellung.

**Sprint-spezifische Anmerkungen:**

- **AI-Multiplier-Hypothese-Test.** Sprint 2 ist nach der Sprint-1-Retro der Test ob der aggregierte Multiplier bei echter Crypto- und Federation-Interaktion auf 3x bis 5x runtergeht (Sprint 1 war 6.4x, aber heterogen verteilt mit hohen Outliern). Pro Story konsequent Zeit-Tracking führen plus am Sprint-Ende nach Story-Typ aggregieren.
- **OAuth-Sandbox-Daten.** Für Demos sind Google-Test-Account (z.B. `rib-pqc-test@gmail.com`) plus Microsoft-Test-Account (eigener Test-Tenant in Azure AD) nötig. Falls Microsoft App in "Testing"-Phase bleibt, Test-User Allowlist im Azure-AD-Portal pflegen.
- **Demo-Plan.** D-007 (Sprint-Goal-Demo Mobile-Google plus PQC-TLS) Ziel am Sa 13.06 Abend. D-008 (Microsoft-Federation) Ziel am So 14.06.
- **Mentor-Termin.** Kein fixer Mentor-Termin im Sprint-2-Zeitraum eingeplant, R-S03 unverändert. Nach Sprint-2-Closure prüfen ob ein Status-Update an Mentoren sinnvoll ist.
- **Strategie-Chat-Anteil.** Sprint-2-Closure (Review, Retro, Sprint-3-Planning, Mentor-Update) plus Story-Pflege wird in den Worklogs der jeweiligen Stories mitgerechnet, nicht als eigene Process-Story (wie in Sprint-1-Retro entschieden).
