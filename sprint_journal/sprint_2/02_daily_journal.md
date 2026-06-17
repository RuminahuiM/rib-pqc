# Daily Journal: Sprint 2

**Sprint-Zeitraum:** 01.06 bis 14.06.2026
**Sprint-Ziel:** Am Sprint-Ende läuft der Mobile-Client gegen den Server über hybride PQC-TLS-Verbindung (X25519MLKEM768), und der User kann sich via Google oder Microsoft einloggen und einen ML-DSA-65-signierten Broker-Token erhalten.

---

> Format: kurze Notiz pro Arbeitstag am Projekt (nicht pro Kalendertag), maximal drei Sätze. Drei Fragen: Was wurde fertig? Was ist heute geplant? Welche Blocker?

---

## Halbzeit-Check 10.06 (Tag 3 von 5 Arbeitstagen, Mittwoch Abend)

> Reminder vom SM: an diesem Tag explizit prüfen, wo der Critical Path steht. Wenn BRK-0, BRK-1, BRK-2, BRK-3 nicht alle Done sind: Scope-Cut-Entscheidung sofort (BRK-6, APP-8, TLS-2, TLS-3 streichen oder in Sprint 3 schieben).

---

## Verweise auf Mentor-Feedback (falls vorhanden)

- (noch keine in Sprint 2)

---

## Sprint-Zwischenstand (einmal pro Woche, hier mid-sprint)

> Stand der Stories aus dem Sprint Backlog. Wird am Halbzeit-Check 10.06 zum ersten Mal ausgefüllt.

| Story | Status | Anmerkung |
|---|---|---|
| PQC-84 BRK-0 OAuth-Setup | | |
| PQC-36 BRK-1 IdP-Registry | | |
| PQC-37 BRK-2 OIDC Code Flow PKCE | | |
| PQC-38 BRK-3 ID-Token-Verifikation | | |
| PQC-39 BRK-4 Identity-Normalisierung | | |
| PQC-40 BRK-5 Google IdP-Plugin | | |
| PQC-42 BRK-7 CSRF/State-Schutz | | |
| PQC-60 APP-7 Google-Login Mobile | | |
| PQC-43 TLS-1 nginx X25519MLKEM768 | | |
| PQC-41 BRK-6 Microsoft IdP-Plugin (High) | | |
| PQC-61 APP-8 Microsoft-Login Mobile (High) | | |
| PQC-44 TLS-2 PQ-Handshake-Verifikation (High) | | |
| PQC-45 TLS-3 nginx Reverse Proxy (High) | | |

---

## Zeit-Tracking pro Story (für AI-Multiplier-Auswertung)

> Pro abgeschlossener Story nach Done-Transition eintragen. Schätzungs-Mittel-h-Wert pro T-Shirt-Size: XS=1h, S=3h, M=7h, L=15h. Multiplier = Schätzung-h dividiert durch tatsächlich-h. Quelle der Konvention: `../../docs/08_scrum_setup.md` Sektion 7.4. Worklog wird zusätzlich im Jira via `addWorklogToJiraIssue` gepflegt.

| Story | T-Shirt | SP | Schätzung (h) | Tatsächlich | Multiplier | Notiz |
|---|---|---|---|---|---|---|
| PQC-84 BRK-0 | S | 2 | 3.0 | | | |
| PQC-36 BRK-1 | M | 5 | 7.0 | | | |
| PQC-37 BRK-2 | L | 8 | 15.0 | | | |
| PQC-38 BRK-3 | M | 5 | 7.0 | | | |
| PQC-39 BRK-4 | M | 5 | 7.0 | | | |
| PQC-40 BRK-5 | M | 5 | 7.0 | | | |
| PQC-42 BRK-7 | S | 2 | 3.0 | | | |
| PQC-60 APP-7 | M | 5 | 7.0 | | | |
| PQC-43 TLS-1 | M | 5 | 7.0 | | | |
| PQC-41 BRK-6 | M | 5 | 7.0 | | | |
| PQC-61 APP-8 | M | 5 | 7.0 | | | |
| PQC-44 TLS-2 | S | 2 | 3.0 | | | |
| PQC-45 TLS-3 | S | 2 | 3.0 | | | |

**Sprint-Aggregat (Zwischenstand, wird beim Sprint Review final aktualisiert):**

- Done in Sprint 2 bisher: 0 Stories, 0 SP.
- Hypothese: aggregierter Multiplier bei 3x bis 5x (gegenüber Sprint 1 mit 6.4x), weil mehr Crypto/Federation-Interaktion.
- Wird beim Halbzeit-Check 10.06 zum ersten Mal aktualisiert.
