# Sprint Retrospektive: Sprint 3

**Datum:** 28.06.2026
**Sprint-Zeitraum:** 18.06 bis 28.06.2026
**Timebox:** 45 Minuten

---

## Achse 1: Produkt

**Sprint-Ziel:** "Mobile-Pfad End-to-End funktional auf iPhone via Expo Go mit PQ-Session (ML-KEM-768 plus HKDF) plus AES-256-GCM-Encrypted /api/profile-Call"

**Erreichungs-Grad:** teilweise erreicht. Server-Pfad komplett (Crypto-Foundation, Session-Layer, Data-Channel, Mini-Demo D-008 live). Mobile-Pfad nicht angegangen (4 APP-Stories Carry-Over). 12 von 18 Stories Done, 52 von 79 SP geliefert.

**Was hat zum Erreichen beigetragen?**

- **Hook-First-Pattern in der Story-Sequenzierung.** DCH-2 hat die Foundation für DCH-3 gelegt (Dependency, Decrypt-Pipeline, Tracker-Hook), DCH-3 lief in 30 Min durch weil 80% der Logik schon stand. Ähnlich SES-1 hat SES-4 mitgenommen. Das ist eine bewusste Architektur-Strategie die sich auszahlt.
- **Pattern-Replikation aus früheren Sprints.** CRY-4 (LibOqsKem) lief schnell weil LibOqsSignature aus Sprint 1 (PQC-25) als Vorlage diente. CRY-3 nutzte cryptography.hazmat als bekannte Standard-Library. Sprint-1-Investitionen haben sich in Sprint 3 weiter ausgezahlt.
- **Wire-Format-Spec als laufender Architektur-Kontext.** docs/wire_format.md wurde im Sprint mehrfach erweitert (v0 bis v0.5). Jede DCH-Story hat ihre Wire-Format-Entscheidung direkt dort dokumentiert. Hat Diskussionen verkürzt und ist später als Schlussbericht-Anhang nutzbar.
- **D-008 Server-Side Demo als konkretes Ergebnis.** End-to-End-Roundtrip in 8 Schritten als reproduzierbares Script. Macht die Sprint-Goal-Server-Seite vorzeigbar trotz Mobile-Lücke.

**Was hat das Erreichen behindert?**

- **Ferien-Phase hat den Sprint verschluckt.** Ich war in den Ferien und habe mir nicht so viel Zeit fürs Projekt genommen wie geplant. Versuche während Ferien zu arbeiten haben in diesem Sprint nachweisbar weniger Output erzeugt als der Standard-Schedule. Konkret: die APP-Stories sind komplett liegen geblieben.
- **Sprint-Planning hat Mobile-Stories nach hinten gestellt.** Im Umsetzungsplan war die Reihenfolge Server-Crypto → Server-Session → Server-Data-Channel → App-Side. Die App-Stories waren also am Ende. Das ist eine logische Dependency-Reihenfolge, aber bei Sprint-Verkürzung sind sie zuerst gefallen. Beim nächsten ähnlichen Sprint wäre eine alternative Reihenfolge zu prüfen wo Mobile früher angefangen wird parallel zu Server.

---

## Achse 2: Prozess (Anwendung von Scrum)

**Gut gelaufen:**

- **Cross-Cutting-Concerns-Checkliste mit Plattform-Capability-Erweiterung.** Die Sprint-2-Retro-Maßnahme hat im Sprint-3-Planning konkret geholfen: explizit geprüft dass die PQ-Crypto auf App-Layer (JavaScript via @noble/post-quantum) statt TLS-Layer gemacht werden muss, weil System-TLS-Stacks ML-KEM nicht supporten (R-T08-Workaround). Das war beim Implementieren von Anfang an klar, hat Diskussionen erspart.
- **Hook-First-Pattern als bewusste Sequenzierungs-Entscheidung im Planning.** Im Sprint-3-Umsetzungsplan war die Reihenfolge so gewählt dass Foundation-Stories (CRY-Layer) vor Konsumenten-Stories (Session, Data-Channel) kommen. Das hat sich in der Praxis durch hohe Multiplier-Werte bestätigt (CRY-3 14x, SES-1 22x, DCH-3 14x).
- **Wire-Format-Spec als laufendes Architektur-Artefakt.** Jede DCH-Story hat ihre Wire-Format-Entscheidung sofort in docs/wire_format.md dokumentiert (v0.3 nach DCH-2, v0.4 nach DCH-4, v0.5 nach DCH-3). Das ist gelebte Architektur-Doku statt nachgereichter Doku.
- **Defer-Kandidat "geschenkt" mitgenommen.** SES-4 (Should-Story) war als Defer-Kandidat im Sprint-Plan, wurde aber im Bundle mit SES-1 erfüllt (10 Min für 2 Tests plus Doku). Pattern: enge Sub-Stories an Critical-Path-Stories können oft kostenlos mitgenommen werden.

**Verbesserungsbedarf:**

- **Halbzeit-Check formal nicht abgehalten.** Der Halbzeit-Check war für den 24.06 geplant, wurde aber durch die vorgezogene Block-Session am 18-19.06 überholt. Im Daily Journal habe ich den Halbzeit-Check-Reminder zwar drin, aber nicht aktiv durchgeführt. Konsequenz: die Carry-Over-Entscheidung für die APP-Stories ist erst beim Sprint-Ende getroffen worden, nicht bei Halbzeit als rechtzeitige Adaption.
- **Closing-Reviews während Block-Session-Phasen schwer konsequent durchzuführen.** Im Day-Marathon-Modus (18-19.06 plus 26.06) ist die HARTE WORKFLOW-REGEL plus Phase-8-Demo-Check schwer konsequent zu halten. Stattdessen wurde Findings-Tracking gemacht (F-098, F-101 bis F-109) aber Demo-Erstellung wurde teilweise ausgesetzt (D-008 erst am 28.06).
- **Mentor-Update-Reflex aus Sprint-2-Retro nicht verinnerlicht.** Während Sprint 3 kein Update verschickt, obwohl die Ferien-Reduzierung absehbar war. Wird zwei Tage nach Sprint-Ende nachgeholt. Lesson sichtbar besser als in Sprint 2 (wo erst nach Sprint-Ende Update kam), aber noch nicht im 24-48h-Fenster.

---

## Achse 3: Selbstmanagement

**Zeitmanagement.** Sprint 3 war in drei Sessions aufgeteilt: 18-19.06 Block-Session (~4h 40m für 7 Stories), 26.06 Session (~2h 10m für 3 Stories), 28.06 Catch-up (~30m für 1 Story plus Demo). Total ~7.34h Story-Zeit über elf Kalendertage. Das Verteilen über drei statt vier geplante Arbeitstage hat funktioniert für die Server-Stories, aber die Mobile-Stories sind komplett liegen geblieben. Lesson: Sprint-Planning sollte Arbeitstage robuster planen, nicht erst bei Ferien-Phase merken dass die Tage fehlen.

**Fokus.** In den ersten zwei Sessions (18-19.06 plus 26.06) war der Fokus hoch und Hook-First-Pattern hat Code-Reuse beschleunigt. Catch-up-Session am 28.06 war pragmatisch kurz, hat nur die letzte Critical-Path-Story (DCH-3) plus die Demo erledigt. Ferien-Kontext hat den Fokus für längere Sessions limitiert, weniger weil ich nicht konnte sondern weil ich es nicht priorisiert habe.

**Energie und Motivation.** Sprint 3 fühlte sich entspannter an als Sprint 2 (kein externes Arbeit-Problem, kein Day-Marathon-Stress). Aber die entspannte Energie hat dazu geführt dass APP-Stories nicht angegangen wurden. Das ist ein Selbstmanagement-Problem: in Ferien-Phasen brauche ich entweder klare Projekt-Termine oder klare Ferien-Termine, nicht beides gemischt.

**Schätz-Genauigkeit und AI-Multiplier-Beobachtung.** Aggregierter Sprint-3-Multiplier 10.4x liegt zwischen Sprint 1 (6.4x verteilt) und Sprint 2 (13.6x Block). Detail: SES-1 mit 22x als höchster Outlier (Hook-First-Pattern plus Router-Pattern bekannt aus Sprint 2), DCH-3 mit 14x analog. Setup-Friction-Outlier nach unten gibt es in Sprint 3 nicht, weil die Foundation aus Sprint 1 plus 2 schon stand. Das ist eine wichtige Beobachtung für die Schlussbericht-Reflexion: die ersten Sprints "investieren" in Multiplier-Potenzial, das in späteren Sprints geerntet wird.

---

## Top 3 Maßnahmen für Sprint 4

1. **Carry-Over-Stories am ersten Sprint-4-Arbeitstag im Day-Marathon-Modus durchziehen, Doku als Fallback-Plan.** Sprint 4 startet mit einer fokussierten Block-Session auf die 27 SP Carry-Over (APP-5 → APP-6 → APP-3 als Hook-First-Stack, dann APP-2, dann QUA-4/QUA-5). Sprint 2 hat gezeigt dass 13 Stories in 6h im Block-Modus machbar sind. Wenn der Carry-Over-Rush erfolgreich ist, ist der Rest von Sprint 4 entspannte Doku-Zeit. Wenn der Rush nach dem ersten Tag nicht durch ist: sofortiger Strategie-Wechsel, Doku-Stories übernehmen Vorrang, Carry-Over wird radikal gestrichen (alle QUA, APP-2 falls noch offen). Die Entscheidung fällt damit am Ende von Tag 1 oder Tag 2, nicht erst am Halbzeit-Check.

2. **Mentor-Update-Reflex strikt einhalten (24-48h-Fenster).** Aus Sprint-2-Retro war die Regel klar, in Sprint 3 wurde sie wieder verletzt (Update kam 2 Tage nach Sprint-Ende). Für Sprint 4: aktiver Status-Update-Termin am Sprint-4-Halbzeit-Check (~01.07) plus separates Update sobald die Schlussbericht-Vorlage in lesbarem Zustand ist. Mentor-Termin für Schluss-Feedback (vor Abgabe 04/05.07) muss in den ersten Sprint-Tagen vereinbart werden, damit die Mentoren Verfügbarkeit haben.

3. **Halbzeit-Check 01.07 als harter Korrektur-Punkt nutzen, nicht überspringen wie in Sprint 3.** Am 01.07 explizit prüfen: DOC-1 (Schlussbericht) in Skelett-Form? DOC-2 (Präsentation) mit Outline? Wenn ja, weiter wie geplant. Wenn nein: alle Carry-Over-Stories (APP plus QUA) sofort streichen oder als "post-Abgabe Stretch" markieren. Sprint-4-Halbzeit-Check ist kritischer als alle vorherigen Halbzeit-Checks weil keine Reserve-Sprints folgen.

---

## Erkenntnisse fürs Schlussbericht-Kapitel "Reflexion"

- **AI-Multiplier-Heterogenität ist Pattern, nicht Ausnahme.** Über drei Sprints gemessen: Sprint 1 mit 6.4x (verteilte Sessions, heterogene Stories), Sprint 2 mit 13.6x (Block-Session mit Bundle-Effekt), Sprint 3 mit 10.4x (gemischtes Format mit Hook-First-Pattern). Die Spannweite zeigt dass der Multiplier weniger eine Eigenschaft des Werkzeugs ist (Claude/Claude Code) als der Arbeitsweise (Session-Format, Story-Sequenzierung, Pattern-Replikation aus früheren Stories). Für die Reflexion wichtig: nicht einen Mittelwert kommunizieren, sondern die Heterogenität plus ihre Ursachen.

- **Hook-First-Pattern als dokumentierbare Architektur-Strategie.** Foundation-Stories vor Konsumenten-Stories zu sequenzieren ergibt messbar höhere Multiplier (DCH-2 → DCH-3 mit 14x, SES-1 → SES-4 mit 18x). Das ist eine Best-Practice die ich aus diesem Projekt mitnehme und in künftigen Projekten anwenden kann, auch in nicht-AI-Kontexten.

- **AI-getriebene Arbeitsweise verändert die Commit-Historie messbar.** Mentor-Feedback aus dem 20.06-Termin: weniger und weniger nachvollziehbare Commits als klassischer Solo-Workflow. Das ist ein wichtiger Reflexions-Punkt: AI-Beschleunigung passiert zu Lasten der Schritt-für-Schritt-Nachvollziehbarkeit. Für künftige Schulprojekte plane ich bewusst weniger AI plus kleineren Scope, damit der Lern-Effekt und die Stakeholder-Nachvollziehbarkeit höher sind.

- **Plattform-Limitationen im PQC-Ökosystem als realer Befund.** R-T08 (System-TLS-Stacks auf iOS und Android unterstützen X25519MLKEM768 noch nicht) ist ein konkreter Datenpunkt zur PQC-Reife Stand 2026. Das Projekt hat den Workaround "PQ-Crypto auf Application-Layer statt TLS-Layer" gewählt und dokumentiert. Wichtiger Beitrag des Projekts: zeigt was funktioniert und was an OS-Limitierungen hängt.

- **Solo-Scrum-Adaptionen unter realer Belastung.** Drei konkrete Adaptions-Ereignisse: Sprint 2 mit Arbeit-Problem und Day-Marathon-Nachholung, Sprint 3 mit Ferien-Reduzierung und Carry-Over-Strategie, Mentor-Kommunikations-Lücke beidem Male als Lesson identifiziert. Solo-Scrum funktioniert, ist aber fragil bei externen Belastungen plus erfordert konsequente Stakeholder-Kommunikation als Adaptions-Voraussetzung.

- **Foundation-Investitionen in Frühsprints zahlen sich später aus.** CRY-Layer aus Sprint 1 hat in Sprint 3 die Crypto-Foundation-Stories beschleunigt. Wire-Format-Spec aus CRY-7 ist über Sprint 3 organisch gewachsen und bleibt als Architektur-Artefakt. Diese Beobachtung gilt nicht nur für AI-unterstützte Projekte, sondern ist generell ein Sprint-Planning-Pattern.

- **Ferien-Phase als reales Solo-Developer-Risiko.** Versuche während Ferien "ein bisschen zu arbeiten" haben in Sprint 3 nachweisbar weniger Output erzeugt als Standard-Schedule-Tage. Lesson: Ferien als echte Ferien planen, Projekt-Arbeitszeit drum herum. Für künftige Projekte: Ferien-Phasen aus dem Projekt-Schedule explizit ausnehmen, nicht "vielleicht-bisschen-arbeiten".
