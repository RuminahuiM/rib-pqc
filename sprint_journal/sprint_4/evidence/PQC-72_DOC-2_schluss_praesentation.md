# Evidence PQC-72 DOC-2: Schluss-Präsentation (Kolloquium)

**Story:** PQC-72 (DOC-2)
**Datum:** 2026-08.07 (Erstellung 07./08.07 Nacht, Kolloquium 08.07.2026 08:30)
**T-Shirt:** M | **SP:** 8 | **Sprint:** 4

## Was wurde gebaut

`praesentation/DOC-2_Kolloquium_Pitch_v3.pptx`: 14 Folien (9 Haupt plus 5 Backup), programmatisch mit pptxgenjs erzeugt (kein MS Designer, Experten-Vorgabe), eigenes Farbschema (Navy/Mint), native PowerPoint-Shapes für alle Diagramme, vollständige Speaker-Notes mit Sprechtext und Timing-Marken auf jeder Folie.

**Aufbau nach Experten-Vorgabe (Pitch-Format, 10 Min plus 5 Min Fragen):**

1. Cold Open Harvest Now Decrypt Later (kein "Willkommen"-Einstieg, Vorgabe)
2. Problem (Shor, HNDL-Timeline)
3. Lösung mit erweiterter Architektur (Schicht-2-Klammer, TLS-Label, Datastores, auf technisches Publikum ausgelegt)
4. Zwei Schutzschichten plus Identität
5. Live-Demo-Anleitung (QR, Demo-User, Home-Screen-Screenshot)
6. Beweis (Wireshark-Mitschnitt, nginx-Log X25519MLKEM768)
7. Performance-Zahlen (QUA-6/7/8: unter 5 ms Handshake, 100x/20x/64x Margen)
8. Ehrliche Einordnung (Plattform-Rollout vs. eigene Schicht, Signal/iMessage-Referenz)
9. Abschluss
10. B1 PQ-Handshake als Sequenz-Diagramm (8 Schritte, farbcodierte Phasen)
11. B2 Qualität/Sicherheit/offene Punkte (F-142, R-T08 transparent)
12. B3 Projektvorgehen (Scrum solo, AI-Multiplier, Lessons)
13. B4 Gesamtarchitektur (App-Crypto-Layer, nginx/oqs, Service-Schichten, Redis/SQLite, IdPs)
14. B5 Algorithmen (Gitter-Didaktik, Grössenvergleich mit FIPS-Quellenangabe)

**Begleitmaterial:**

- `praesentation/QA_Fragen_Antworten.md`: 16 antizipierte Fragen mit Sprechantworten
- `praesentation/Runbook_Demo.md`: Setup-Checkliste, Demo-Ablauf, Fallback-Kaskade

## Durchführung (08.07.2026, 08:30)

Kolloquium gehalten: 10 Min Pitch plus Fragerunde, mit Live-Demo (Publikums-Handys via Expo Go gegen den lokalen Stack, Detail-Doku in `demos/D-009_mobile_end_to_end.md`).

## AC-Mapping (Planning: "PPTX-Deck bereit für Kolloquium")

| AC | Status | Verifikation |
|---|---|---|
| Deck als PPTX, Kolloquium-tauglich | erfüllt | v3 im Repo, am Kolloquium eingesetzt |
| Experten-Vorgaben (Pitch, Einstieg, Live-Demo, kreative Slides, keine MS-Designer) | erfüllt | Aufbau siehe oben, Demo Folie 5/6 |
| Zeitrahmen 10 Min | erfüllt | Timing-Marken in Notes, Summe 10:00 |

## Abweichungen

- Ursprüngliches Planning nannte 15 Slides / 15-20 Min; Experten-Input vom 07.07 (10 Min Pitch plus 5 Min Fragen) hat Format und Umfang neu definiert, Deck entsprechend auf 9 Haupt-Folien verdichtet.
- Deck-Erstellung als AI-Pair-Session in der Nacht vor dem Kolloquium (R-S04-Konsequenz), Aufwand 3.0h gegen 7.0h Schätzung (Multiplier 2.3x).

## Bezug

- Jira: [PQC-72](https://rumidesigns.atlassian.net/browse/PQC-72)
- Vorgaben: `tbz_resources/Merkblatt-A-2-SemArbeit.md` Kriterium 6, Experten-Mail 07.07.2026
