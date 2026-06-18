# Sprint Retrospektive: Sprint 2

**Datum:** 18.06.2026
**Sprint-Zeitraum:** 01.06 bis 14.06.2026 geplant, faktisch verzögert auf Abschluss am 17.06.2026 (Day-Marathon)
**Timebox:** 45 Minuten

---

## Achse 1: Produkt

**Sprint-Ziel:** "Mobile-Client gegen Server über PQC-TLS plus Federation-Login via Google/Microsoft mit ML-DSA-65-Broker-Token"

**Erreichungs-Grad:** vollständig erreicht für den Browser-zu-Backend-Pfad, mit der ehrlichen R-T08-Einschränkung dass der reine Mobile-App-Pfad mit PQC-TLS nur theoretisch funktioniert (OS-System-TLS-Stacks unterstützen X25519MLKEM768 noch nicht).

**Was hat zum Erreichen beigetragen?**

- **Cross-Cutting-Concerns-Checkliste aus Sprint-1-Retro.** Hat dazu geführt dass beim Sprint-Start die ACs schon vollständig waren (BRK-4 email_verified, BRK-7 State-Storage spezifiziert, BRK-0 OAuth-Setup als eigene Story angelegt). Während Implementation keine Diskussionen, sondern direktes Umsetzen.
- **Single-Tenant-Entscheidung bei Microsoft.** Vermeidet die App-Approval-Wartezeit komplett, R-T04 und R-S05 damit elegant umgangen.
- **Code-Reuse zwischen verwandten Stories.** BRK-5 plus BRK-6 (Google plus Microsoft Plugins), APP-7 plus APP-8 (Google plus Microsoft Mobile-Login) profitieren massiv vom ersten Pattern. Sehr effizient.
- **Foundation aus Sprint 1.** PQC-18 (oqs-provider nginx) hat TLS-1 in Sprint 2 stark abgekürzt. Sprint-1-Investition zahlt sich aus.

**Was hat das Erreichen behindert?**

- **Arbeit-Problem bei HEKS.** Hat den geplanten Sprint-Zeitraum komplett unmöglich gemacht. Die Adaption hat funktioniert, aber strukturell ist meine Kapazität bei externen Belastungen fragil.
- **Mobile-PQC-TLS-Limitation (R-T08) zu spät entdeckt.** Beim Sprint-Planning war ich davon ausgegangen dass Mobile-Client gegen Backend über PQC-TLS funktioniert. Erst während der Implementation wurde klar dass System-TLS-Stacks ML-KEM nicht unterstützen. Damit ist das Sprint-Goal für den reinen App-Pfad nur theoretisch erfüllt. Beim Sprint-Planning wäre eine vollständigere Recherche zu Mobile-Client-TLS-Capabilities sinnvoll gewesen.

---

## Achse 2: Prozess (Anwendung von Scrum)

**Gut gelaufen:**

- **Cross-Cutting-Concerns-Checkliste aus Sprint-1-Retro hat sich konkret ausgezahlt.** Vor Sprint-Start die Liste durchgegangen, drei konkrete Adjustments umgesetzt (BRK-0 neue Story, BRK-4 AC-6 email_verified, BRK-7 AC-5 Redis-Storage). Beim Implementieren war jede Story refinement-ready. Will ich für Sprint 3 wiederholen.
- **Single-Tenant-Microsoft-Entscheidung als eleganter Risk-Workaround.** Statt mit Common-Tenant-App-Approval-Wartezeit zu rechnen, beim Sprint-Planning auf Single-Tenant entschieden. R-T04 und R-S05 dadurch praktisch gegenstandslos.
- **Risk-Tracking war konsequent.** Vier Risiken Mitigated (R-T04, R-S05, R-T07, im Risk Register dokumentiert), zwei neu identifiziert (R-T08 Mobile-PQC-TLS-Limitation, R-S06 Sprint-3-Komprimierung). Plus R-P02 nach realer Eintretung neu bewertet.
- **Code-Reuse zwischen verwandten Stories systematisch genutzt.** BRK-5/BRK-6 als Pair, APP-7/APP-8 als Pair, TLS-1/2/3 als Bundle. Bei der Story-Reihenfolge im Sprint-Planning war das schon antizipiert. Hat den Multiplier nach oben gezogen.

**Verbesserungsbedarf:**

- **Mentor-Kommunikation während der Verzögerung versäumt.** Konkretes Versäumnis: zwischen 01.06 (Zwischengespräch) und 17.06 (Sprint-Abschluss-Update) gab es kein Status-Update an die Mentoren. Hätte schon am 02.06 oder 05.06 eine kurze Info schicken können: "Sprint 2 startet wegen Arbeit-Problem verzögert, hier ist mein Plan". Lesson: bei jedem unerwarteten Stocker innerhalb von 24 bis 48 Stunden ein kurzes Mentor-Update verschicken, nicht erst wenn die Lage gelöst ist.
- **Implementation hat einige Konventionen ausgesetzt.** Daily Journal nicht parallel geführt, keine D-NNN-Demos während des Sprints (D-007 erst nachträglich), Evidence-Files nicht für jede Story angelegt. War pragmatisch unter Zeitdruck, aber strukturell hat die Reflexions-Tiefe darunter gelitten. Für Sprint 3: entweder die Konventionen einhalten oder beim Sprint-Start bewusst entscheiden welche Konventionen für diesen Sprint pausieren und das dokumentieren.
- **Mobile-TLS-Limitation hätte beim Planning auffallen können.** Bei der Cross-Cutting-Concerns-Checkliste war "TLS-Cert-Handling" als Thema gelistet, aber Mobile-Client-TLS-Capability war nicht explizit geprüft. Erst während Implementation ist die System-TLS-Stack-Limitation klar geworden (R-T08). Für Sprint 3: bei TLS- oder Crypto-Themen explizit Browser-vs-Mobile-vs-Server prüfen.

---

## Achse 3: Selbstmanagement

**Zeitmanagement.** Sprint 2 ist im geplanten Zeitraum (01.06 bis 14.06) wegen Arbeit-Problem nicht angelaufen, faktisch komplett verschoben auf 17.06. Am 17.06 habe ich in einer Block-Session 6h 5m Implementation für 13 Stories durchgezogen. Block-Sessions sind sehr effizient bei klarem Backlog, aber als Sprint-Modus risikoreich (kein Puffer, kein zwischenzeitliches Doku-Update, kein Halbzeit-Check). Für Sprint 3 plane ich auf reguläre verteilte Arbeitstage (Wochenenden plus Mittwoch).

**Fokus.** In der Block-Session war der Fokus extrem hoch, weil Code-Reuse zwischen verwandten Stories den Kontext durchgehend geladen hielt. Negative Seite: keine bewussten Pausen, weniger Distanz für Architektur-Entscheidungen, das ist ein Risiko bei komplexerer Crypto-Arbeit wie sie in Sprint 3 ansteht.

**Energie und Motivation.** Die Verzögerungs-Phase war frustrierend (Arbeit zieht Energie, Projekt liegt offen). Die Block-Session am 17.06 war im Gegensatz dazu motivierend weil sichtbarer Fortschritt in kurzer Zeit. Aber emotional anstrengend, das ist nicht als regulärer Modus tragfähig.

**Schätz-Genauigkeit und AI-Multiplier-Beobachtung.** Aggregierter Sprint-2-Multiplier 13.6x, deutlich über Sprint-1 (6.4x). Massgeblich beeinflusst durch Block-Session-Continuity und Code-Reuse-Pairs (BRK-5/6, APP-7/8). Realistischer Projekt-Mittelwert vermutlich zwischen 6x und 10x, mit einzelnen Outliern nach oben (Block-Sessions, Verifikations-Stories) und nach unten (Setup-Friction, neue Plattform-Themen). Für Sprint 3 mit echter Krypto-Implementation (KEM/HKDF/AEAD) erwarte ich eher 5x bis 8x.

---

## Top 3 Maßnahmen für Sprint 3

1. **Mentor-Update-Reflex bei unerwarteten Stockern etablieren.** Wenn in Sprint 3 ein Problem auftritt das den Plan stört (Arbeit-Belastung, technischer Blocker, Krankheit), innerhalb 24 bis 48 Stunden ein kurzes Status-Update an die Mentoren via MS Teams. Nicht erst warten bis die Lage gelöst ist. Adressiert das Versäumnis aus Sprint 2.

2. **Cross-Cutting-Concerns-Checkliste um Plattform-Capability-Check erweitern.** Bei Themen mit Crypto-Plattform-Interaktion (TLS, KEM, Signatures) explizit prüfen welche Capabilities Browser, Mobile (iOS/Android System-TLS, React-Native-Stack), Server jeweils haben. R-T08 wäre beim Sprint-2-Planning entdeckbar gewesen mit dieser Erweiterung. Adressiert die zu späte Entdeckung der Mobile-TLS-Limitation.

3. **Sprint-3-Komprimierung mit aggressivem Halbzeit-Check.** Sprint 3 hat 11 Tage statt 14. Beim Halbzeit-Check (etwa 23.06) muss klar sein wo der Critical Path steht. Falls Critical-Path-Stories (CRY-Foundation plus SES-1 bis SES-3 plus DCH-Bundle) nicht mindestens 60% Done sind: sofort Scope-Cut-Entscheidung (SES-4 Should rausstreichen, APP-2/3/5/6 ggf nach Sprint 4 als Polish, QUA-4/5 als Should). Sprint 4 bleibt unantastbar. Adressiert R-S06.

---

## Erkenntnisse fürs Schlussbericht-Kapitel "Reflexion"

- **AI-Multiplier ist stark abhängig vom Session-Format und Story-Mix.** Sprint 1 mit verteilten Arbeitstagen ergab 6.4x aggregiert (heterogen verteilt). Sprint 2 als Block-Session ergab 13.6x. Block-Sessions plus Code-Reuse-Pairs treiben den Multiplier nach oben, Setup-Friction und neue Plattform-Themen drücken ihn. Für das Schlussbericht-Kapitel ist nicht der Mittelwert wichtig, sondern die Heterogenität und die kontextuellen Faktoren die ihn beeinflussen.

- **Externe Belastung als reales Risiko in Solo-Projekten.** Sprint 2 hat gezeigt dass ein berufliches Problem ein Solo-Sprint-Plan komplett zerschiessen kann. Adaption ist möglich (Day-Marathon hat hier funktioniert), aber strukturell ist Solo-Scrum fragil bei längeren Unterbrechungen. Wichtiger Punkt für die Solo-Scrum-Adaptions-Diskussion im Reflexions-Kapitel.

- **Mentor-Kommunikation als Voraussetzung für Empirismus-Säule.** Die Adaption-Säule des Scrum-Prozesses funktioniert nur wenn Stakeholder transparent informiert sind. Sprint-2-Verzögerung war an sich legitime Adaption, aber die fehlende Mentor-Kommunikation während der Verzögerungs-Phase war ein konkretes Versäumnis. Lesson: Transparenz schlägt Schönwetter-Berichten.

- **Plattform-Limitationen im PQC-Ökosystem (Stand 2026).** Der R-T08-Befund (System-TLS-Stacks auf iOS und Android unterstützen X25519MLKEM768 noch nicht) ist ein ehrlicher Datenpunkt zur PQC-Ökosystem-Reife. ML-KEM ist seit FIPS-203-Standardisierung 2024 final, aber die Roll-Out-Geschwindigkeit in OS-TLS-Libraries ist langsam. Mobile-Client-PQC-TLS via System-Stack ist Stand Juni 2026 noch nicht möglich, nur via Custom-Native-Modul mit liboqs-Bindings. Wichtige Kontext-Information für die Architektur-Diskussion im Bericht.

- **Cross-Cutting-Concerns-Checkliste ist gelebte Empirismus.** Die Sprint-1-Retro-Maßnahme hat sich in Sprint 2 konkret bewährt (drei umgesetzte Adjustments). Klassisches Beispiel für die Inspect-Adapt-Schleife im Scrum-Prozess in der Solo-Anwendung mit AI-Unterstützung.
