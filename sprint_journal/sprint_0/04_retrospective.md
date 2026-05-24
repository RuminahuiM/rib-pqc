# Sprint Retrospektive: Sprint 0

**Datum:** 24.05.2026
**Sprint-Zeitraum:** 06.05 bis 24.05.2026
**Timebox:** 45 Minuten

---

## Achse 1: Produkt

**Sprint-Ziel:** "Scope, Architektur und Tooling-Basis ready"

**Erreichungs-Grad:** teilweise erreicht (siehe `03_review.md` Section 1).

**Was hat zum Erreichen beigetragen?**

- **Konservatives Schritt-für-Schritt Vorgehen.** Eines nach dem anderen (Requirements vor Design vor Backlog vor Jira) hat Wiederarbeit vermieden und klare Abhängigkeiten geschaffen.
- **AI-Unterstützung (Claude als Co-Pilot).** Hohe Output-Geschwindigkeit bei Markdown-Dokumenten, Backlog, Risk Register und Traceability-Matrix. Volumen der Deliverables (12 Markdowns, 76 Jira-Issues) wäre solo kaum in 10 Stunden möglich.
- **Frühe Architektur-Entscheidung (08.05.2026).** Die Entscheidung für Option 2 (Identity Broker plus PQ-Uplift) zwischen drei Alternativen hat den Scope geschnitten und nachfolgende Arbeit fokussiert.

**Was hat das Erreichen behindert?**

- **Scope-Unsicherheit zu Beginn.** Zwischen 06.05 und 08.05 war die Wahl zwischen drei Architektur-Optionen (Full-OIDC, Option 2 Identity Broker, OIDC-Lite) offen. Diese Unsicherheit hat Recherche und Diskussion erfordert, was Sprint-0-Verlängerung verursachte.
- **Tool-Setup-Untertschätzung.** INF-2 bis INF-4 wurden in Sprint 0 nicht angegangen, weil Konzeption und Doku Vorrang hatten. Diese Stories wandern als Carry-Over in Sprint 1.

---

## Achse 2: Prozess (Anwendung von Scrum)

**Gut gelaufen:**

- **Solo-Scrum-Adaption funktioniert.** Trennung der drei Rollen (Developer, Product Owner, Scrum Master) als Denkmodell ist tragfähig, auch wenn alle bei einer Person liegen.
- **Templates und Doku-Struktur bewährt.** Die Sprint-Journal-Templates sind sofort produktiv einsetzbar, kein Reibungsverlust.
- **Adaption-Säule gelebt.** Sprint 0 wurde transparent dreimal verlängert mit dokumentierten Begründungen (Risk Register R-S02, Scrum-Setup 8.1). Keine Verschleierung der Verzögerung.

**Verbesserungsbedarf:**

- **Daily Journal in Sprint 0 nicht geführt.** Wir hatten Templates aber haben sie nicht genutzt. Das hat die Velocity-Auswertung am Sprint-Ende erschwert (nachträgliche Schätzung der 10 Stunden statt täglich erfasste Werte).
- **Untracked Work substantiell.** Sprint 0 hatte 14 SP formell, aber etwa 25 bis 40 SP-Equivalent Doku- und Planungs-Arbeit wurde geliefert. Diese Diskrepanz verzerrt die Velocity-Messung und die Sprint-Goal-Erreichungs-Aussage.
- **Sprint 0 mehrfach verlängert ohne formellen Abbruch und Neustart.** Sauberer wäre gewesen, Sprint 0 nach erster Verlängerung formell abzubrechen und Sprint 0a / Sprint 0b zu starten, mit klarem neuen Sprint-Goal.

**Anti-Patterns, die aufgetaucht sind:**

- **ScrumBut: untracked work > tracked work.** Klassisches Solo-Scrum-Problem.
- **Inkonsistente tägliche Arbeit.** 0.5 h/Tag im Schnitt, keine Routine.
- **Sprint-Plan-Schleichung.** Drei Verlängerungen statt Neustart.

---

## Achse 3: Selbstmanagement

**Zeitmanagement:** Konzentriert wenn aktiv, aber zu unregelmässig. 10 Stunden über 19 Tage = 0.5 h/Tag Schnitt. In Implementations-Phasen (ab Sprint 1) wird das nicht reichen. Sprint 1 mit 53 SP in 7 Tagen würde grob 30 bis 50 effektive Stunden brauchen, also 4 bis 7 h/Tag, eine erhebliche Steigerung.

**Fokus:** Schwierig. Viele Kontextwechsel, schwer wieder reinzukommen nach Pausen. Das verstärkt das Inkonsistenz-Problem.

**Energie / Motivation:** Schwankend. Hochs (z.B. nach Architektur-Entscheidung), Tiefs (z.B. wenn Sprint 0 sich zieht). Insgesamt stabil genug, aber nicht hoch.

**Schätz-Genauigkeit:** Noch nicht aussagekräftig auswertbar, weil die INF-Code-Stories nicht angegangen wurden. Erst Sprint 1 wird zeigen, wie gut die T-Shirt-Sizes für Code-Arbeit mit AI-Unterstützung passen.

**Beobachteter AI-Multiplier in Doku/Planung:** Hoch, etwa 2.5x bis 4x (basierend auf Output-Volumen vs. 10 Stunden Input). Das ist deutlich über dem konservativen 1.5x-Wert aus `08_scrum_setup.md` Abschnitt 7.4. Sprint 1 muss zeigen ob der Multiplier auch für Code-Arbeit so hoch ausfällt.

---

## Top 3 Massnahmen für Sprint 1

1. **Daily Journal konsequent führen.** Pro Arbeitstag eine kurze Notiz in `../sprint_1/02_daily_journal.md` (Was fertig, was geplant, Blocker, Stunden). Bei null Arbeit am Tag: kein Eintrag, kein Schummeln. Ziel: ehrliche Datenbasis für Velocity-Messung und Retro.

2. **Wochenkapazität explizit reservieren.** Mindestens 3 feste Slots pro Woche fürs Projekt einplanen (z.B. Di Abend, Do Abend, Sa Vormittag). Nicht "wenn Zeit übrig". Das adressiert die Inkonsistenz und ermöglicht die nötige Steigerung von 0.5 h/Tag auf ca. 4 h/Tag.

3. **Mentor-Status-Update nach Sprint-Ende.** Nach jeder Sprint-Retro ein kurzes Update an Mentoren via MS Teams Kanal mit Stand und Hinweis auf den Sprint-Review-Eintrag im Sprint-Journal. Schafft Transparenz und holt regelmässig externes Feedback ab, auch ausserhalb der drei offiziellen Termine.

---

## Erkenntnisse fürs Schlussbericht-Kapitel "Reflexion"

- **AI-Multiplier ist nicht konstant.** Doku- und Planungs-Arbeit profitiert offenbar deutlich mehr von AI-Unterstützung als bisher angenommen (Sprint-0-Beobachtung: 2.5x bis 4x statt konservativ 1.5x). Sprint 1 wird die Hypothese für Code-Arbeit empirisch testen.
- **Solo-Scrum hat einen blinden Fleck bei untracked Doku-Arbeit.** Konzeptions- und Planungs-Arbeit landet leicht ausserhalb des Backlogs, was Velocity-Tracking unzuverlässig macht. Im Solo-Setting fehlt der externe Korrektiv-Mechanismus (PO oder Team), der das auffangen würde.
- **Iterative Adaption (Empirismus-Säule) funktioniert in der Praxis.** Sprint 0 wurde dreimal angepasst mit dokumentierten Begründungen. Aus Scrum-Master-Sicht ist das legitim, auch wenn es theoretisch sauberer gewesen wäre, einen Sprint formell abzubrechen und neu zu starten. Solo-Adaption rechtfertigt diese Vereinfachung.
- **Setup-Phasen sollten zeitlich begrenzt werden.** Sprint 0 hat sich von geplanten 6 Tagen auf real 19 Tage gestreckt. Lehre: bei zukünftigen Setup-Sprints von Anfang an einen harten Deadline-Charakter etablieren, auch wenn das Setup-Goal noch nicht 100 % erreicht ist. Setup ist "perfectible enemy of done".
- **Daily Journal als Disziplin-Tool.** Vorhandene Templates allein helfen nicht, wenn sie nicht genutzt werden. Ab Sprint 1 wird das Daily Journal als verbindlich gelebt, sonst leidet die ganze Reflexions-Tiefe (Bewertungs-Kriterium 5).
