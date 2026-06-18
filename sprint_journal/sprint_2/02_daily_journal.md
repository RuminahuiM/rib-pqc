# Daily Journal: Sprint 2

**Sprint-Zeitraum:** 01.06 bis 14.06.2026 (ursprünglich), faktisch verzögert auf 17.06.2026 (Day-Marathon-Abschluss)
**Sprint-Ziel:** Am Sprint-Ende läuft der Mobile-Client gegen den Server über hybride PQC-TLS-Verbindung (X25519MLKEM768), und der User kann sich via Google oder Microsoft einloggen und einen ML-DSA-65-signierten Broker-Token erhalten.

---

> Format: kurze Notiz pro Arbeitstag am Projekt (nicht pro Kalendertag), maximal drei Sätze. Drei Fragen: Was wurde fertig? Was ist heute geplant? Welche Blocker?

---

## 2026-06-01 bis 2026-06-16 (Sprint-2-Verzögerung) — retrospektiv dokumentiert

**Was passiert ist:** Im geplanten Sprint-2-Zeitraum (01.06 bis 14.06) konnte ich kein effektives Projekt-Arbeit leisten wegen eines Problems bei meiner Arbeit (HEKS). Die Implementation-Arbeit kam nicht zustande. Das ursprünglich geplante Sprint-2-Backlog (BRK plus TLS plus Federation-Mobile, 56 SP in 5 geplanten Arbeitstagen) wurde nicht angegangen.

**Adaption (Empirismus-Säule):** Statt den Sprint mit massivem Carry-Over in Sprint 3 zu schieben oder das Sprint-Goal zu reduzieren, habe ich entschieden den Sprint nachzuholen sobald die Arbeit-Situation wieder Kapazität gibt. Die Mentoren wurden über die Verzögerung in einem Zwischenupdate informiert (Transparenz-Prinzip, nicht verbergen).

**Konsequenz für Projekt-Timeline:** Sprint 3 startet entsprechend später. Sprint-Abgabe-Frist (04 bis 05.07.2026) bleibt unverändert, das heißt Sprint 3 und Sprint 4 sind komprimierter zu planen.

**Blocker:** Externe Verfügbarkeit (Arbeit-Situation). Keine direkten technischen Blocker, alle Sprint-2-Stories waren ready beim Planning am 01.06.

**Arbeitszeit:** 0h Implementation, ca. 30 Min Mentor-Update-Schreiben.

---

## 2026-06-17 (Mittwoch, Day-Marathon Sprint-2-Nachhol-Session)

**Was wurde fertig:** Sprint 2 vollständig durchgezogen in einem Tag. Alle 13 Sprint-2-Stories Done. Sprint-Goal Variante B erreicht: Mobile-Client gegen Server via PQC-TLS (X25519MLKEM768), Google plus Microsoft Federation-Login funktional, ML-DSA-65-signierter Broker-Token Ausstellung und Verifikation Live.

**Was war heute geplant:** Sprint-2-Komplettabschluss in einem Day-Marathon. Reihenfolge laut Sprint-Planning befolgt: BRK-0 Setup zuerst (OAuth-Apps registrieren), dann Server-Federation-Foundation (BRK-1 bis BRK-4), dann Plugins (BRK-5 plus BRK-6), dann CSRF-Schutz (BRK-7), dann TLS-Bundle (TLS-1 bis TLS-3), zum Schluss Mobile-Federation (APP-7 plus APP-8).

**Blocker:** Keine. Microsoft-App-Approval war nicht nötig wegen Single-Tenant-Setup-Entscheidung (R-T04 weniger akut als erwartet). Custom-Build-Path für Mobile nicht nötig wegen Expo-Go-Kompatibilität.

**Arbeitszeit:** 6h 5m Active-Implementation (siehe Zeit-Tracking-Tabelle unten). Plus ca. 1h Strategie-Chat-Doku-Pflege (DoD-Feld plus AC-Checkbox-Konversion in Jira) am Folgetag 18.06.

---

## Verweise auf Mentor-Feedback

- 17.06.2026: Zwischenupdate an Mentoren vor dem Day-Marathon versendet, das die Sprint-2-Verzögerung wegen Arbeit-Problem transparent erklärt hat. Mentor-Feedback wird nachgereicht falls Reaktion eingeht.
- Memorandum zum Status nach Sprint-2-Abschluss kann optional an Mentoren versendet werden (Entscheidung beim Sprint Review).

---

## Sprint-Zwischenstand FINAL (Stand 17.06.2026 Abend)

| Story | Status | Anmerkung |
|---|---|---|
| PQC-84 BRK-0 OAuth-Setup | Done (17.06) | Google Cloud Console plus Microsoft Entra ID Single-Tenant App registriert. R-T04 plus R-S05 mitigated. |
| PQC-36 BRK-1 IdP-Registry | Done (17.06) | Plugin-Architektur, Foundation für BRK-5 plus BRK-6. |
| PQC-37 BRK-2 OIDC Code Flow PKCE | Done (17.06) | Authorization Code Flow mit PKCE server-side, Endpoint POST /auth/federated/<provider>/callback. |
| PQC-38 BRK-3 ID-Token-Verifikation | Done (17.06) | JWKS-Caching, Sig/Iss/Aud/Exp-Check. |
| PQC-39 BRK-4 Identity-Normalisierung | Done (17.06) | External-Sub-Linking inklusive email_verified-Check (AC-6 aus Cross-Cutting-Concerns-Checkliste). |
| PQC-40 BRK-5 Google IdP-Plugin | Done (17.06) | Google-Discovery, sub als External-Sub. |
| PQC-41 BRK-6 Microsoft IdP-Plugin | Done (17.06) | Microsoft-Discovery Single-Tenant, oid als External-Sub. |
| PQC-42 BRK-7 CSRF/State-Schutz | Done (17.06) | State-Parameter 128 Bit Entropie, Redis-Storage TTL 10 Min (aus Cross-Cutting-Concerns-Checkliste). |
| PQC-43 TLS-1 nginx X25519MLKEM768 | Done (17.06) | TLS-Foundation stand schon durch PQC-18 in Sprint 1, hier nur Production-Config plus Cert. |
| PQC-44 TLS-2 PQ-Handshake-Verifikation | Done (17.06) | oqs-curl Demo, NamedGroup X25519MLKEM768. |
| PQC-45 TLS-3 nginx Reverse Proxy | Done (17.06) | Reverse-Proxy zum auth-service, X-Forwarded-Headers. |
| PQC-60 APP-7 Google-Login Mobile | Done (17.06) | expo-auth-session mit PKCE plus State, Deep-Link funktional. |
| PQC-61 APP-8 Microsoft-Login Mobile | Done (17.06) | Analog APP-7. R-T07 (Deep-Link Expo Go) nicht eingetreten. |

**13/13 Stories Done. Sprint-Goal vollständig erreicht.**

---

## Zeit-Tracking pro Story (für AI-Multiplier-Auswertung)

> Tatsächliche Zeiten aus Jira-Worklogs vom 17.06.2026. Schätzungs-Mittel-h-Wert pro T-Shirt-Size: XS=1h, S=3h, M=7h, L=15h. Multiplier = Schätzung-h dividiert durch tatsächlich-h.

| Story | T-Shirt | SP | Schätzung (h) | Tatsächlich | Multiplier | Notiz |
|---|---|---|---|---|---|---|
| PQC-84 BRK-0 | S | 2 | 3.0 | 2h (2.0 h) | 1.5x | OAuth-App-Setup bei Google plus Microsoft. Browser-Klick-Zeit dominant, AI hilft hier wenig (klassischer Setup-Friction-Multiplier). |
| PQC-36 BRK-1 | M | 5 | 7.0 | 30 Min (0.5 h) | 14.0x | IdP-Registry Plugin-Pattern, Foundation. |
| PQC-37 BRK-2 | L | 8 | 15.0 | 45 Min (0.75 h) | 20.0x | OIDC Code Flow mit PKCE, größte Story im Sprint. Day-Marathon-Effekt: Kontext-Continuity aus BRK-1 hat beschleunigt. |
| PQC-38 BRK-3 | M | 5 | 7.0 | 30 Min (0.5 h) | 14.0x | ID-Token-Verifikation mit JWKS-Caching. |
| PQC-39 BRK-4 | M | 5 | 7.0 | 30 Min (0.5 h) | 14.0x | Identity-Normalisierung inklusive AC-6 email_verified-Check. |
| PQC-40 BRK-5 | M | 5 | 7.0 | 20 Min (0.33 h) | 21.0x | Google-Plugin auf Registry-Foundation. Bundle-Effekt mit BRK-6. |
| PQC-41 BRK-6 | M | 5 | 7.0 | 10 Min (0.17 h) | 41.2x | Microsoft-Plugin analog Google. Code-Reuse maximal. Outlier nach oben. |
| PQC-42 BRK-7 | S | 2 | 3.0 | 25 Min (0.42 h) | 7.2x | State-Schutz mit Redis-Storage. |
| PQC-43 TLS-1 | M | 5 | 7.0 | 10 Min (0.17 h) | 41.2x | nginx X25519MLKEM768-Konfig, Foundation stand schon durch PQC-18 in Sprint 1. Verifikation hier minimal. |
| PQC-44 TLS-2 | S | 2 | 3.0 | 10 Min (0.17 h) | 17.6x | oqs-curl Demo. Verifikations-Story. |
| PQC-45 TLS-3 | S | 2 | 3.0 | 10 Min (0.17 h) | 17.6x | Reverse-Proxy. Sehr kompakt. |
| PQC-60 APP-7 | M | 5 | 7.0 | 15 Min (0.25 h) | 28.0x | Google-Login expo-auth-session. R-T07 nicht eingetreten. |
| PQC-61 APP-8 | M | 5 | 7.0 | 10 Min (0.17 h) | 41.2x | Microsoft-Login analog APP-7. Code-Reuse maximal. |

**Sprint-Aggregat FINAL:**

- Done in Sprint 2: 13 Stories, 56 SP.
- Summe klassisch geschätzte Stunden (ohne AI): 2 + 5 + 8 + 5 + 5 + 5 + 5 + 2 + 5 + 2 + 2 + 5 + 5 = 56 SP, in h: 3+7+15+7+7+7+7+3+7+3+3+7+7 = **83 h**.
- Summe tatsächliche Stunden mit AI: 2.0 + 0.5 + 0.75 + 0.5 + 0.5 + 0.33 + 0.17 + 0.42 + 0.17 + 0.17 + 0.17 + 0.25 + 0.17 = **6.08 h (6h 5m)**.
- **Aggregierter Sprint-Multiplier: 83 / 6.08 = 13.6x**.
- Ohne BRK-0 (Browser-Setup): 80 / 4.08 = **19.6x** für reine Code-Stories.

**Aufschlüsselung nach Story-Typ:**

- Setup (BRK-0): 1.5x (Browser-Klick-Friction).
- Federation Server-Side (BRK-1 bis BRK-7): 14.0x, 20.0x, 14.0x, 14.0x, 21.0x, 41.2x, 7.2x → Mittel ca. 19x. BRK-6 ist Outlier wegen Code-Reuse aus BRK-5.
- TLS (TLS-1, TLS-2, TLS-3): 41.2x, 17.6x, 17.6x → Mittel 25.5x. TLS-1 Foundation stand schon durch PQC-18.
- Mobile-Federation (APP-7, APP-8): 28.0x, 41.2x → Mittel 34.6x. APP-8 maximaler Code-Reuse.

**Beobachtung für Schlussbericht:**

Sprint-2-Multiplier ist extrem hoch (13.6x aggregiert, 19.6x ohne Setup) wegen drei Effekten: Day-Marathon-Continuity (kein Context-Switching, ein Block plus voller Tag), massive Code-Reuse zwischen verwandten Stories (BRK-5/BRK-6, APP-7/APP-8, TLS-1/TLS-2/TLS-3), und Cross-Cutting-Concerns-Checkliste plus Story-Refinement im Sprint-Planning (AC-6 für BRK-4, State-Storage für BRK-7) hat während Implementation Diskussionen erspart. Dieser Wert ist nicht repräsentativ für typische Multi-Day-Sprint-Arbeit, aber ein interessanter Daten-Punkt für die Hypothese dass Block-Sessions deutlich effizienter sind als verteilte Sessions.
