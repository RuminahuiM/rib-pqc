# Sprint Retrospektive: Sprint 1

**Datum:** 31.05.2026
**Sprint-Zeitraum:** 24.05 bis 31.05.2026
**Timebox:** 45 Minuten

---

## Achse 1: Produkt

**Sprint-Ziel:** "End-to-End Local Login lokal durchspielen"

**Erreichungs-Grad:** vollständig erreicht plus 4 Bonus-Erfüllungen (siehe `03_review.md` Section 1).

**Was hat zum Erreichen beigetragen?**

- **AI-Unterstützung mit hohem Multiplier.** Aggregierter Sprint-Multiplier 6.4x. Speziell bei Foundation-Code (CRY-1, CRY-5, TOK-1, TOK-2) und bei Bundle-Stories (SEC-Bundle) hat AI massiv beschleunigt.
- **Saubere Story-Reihenfolge.** Erst Foundation (CRY-Layer plus Skeleton), dann Token-Schicht, dann Auth, dann SEC plus QUA, am Ende App-Stretch. Jede Story konnte auf der vorherigen aufbauen.
- **Closing-Review-Prozess mit Findings-Auslagerung.** Statt jede Story perfekt zu machen, wurden Findings in Tiers (resolved-in-story, Tier-1-als-eigene-Story, Tier-2-deferred) ausgelagert. Hat den Sprint flüssig gehalten und produktive Stories statt Perfektions-Stories produziert.
- **Demo-Konvention.** Sechs reproduzierbare Demos (D-001 bis D-006) sammeln den Fortschritt mit konkretem Output statt nur grünen Tests.

**Was hat das Erreichen behindert?**

- **Setup-Friction in den Skeleton-Stories.** SKL-1 mit ca. 30 Min Boilerplate-Schritten, SKL-2 mit 30 Min Node-Upgrade plus Expo-SDK-Downgrade. AI hilft hier weniger als bei reinem Code.
- **Premature-Done-Versuche durch die AI.** Bei PQC-25 und PQC-22 hat die AI im Implementation-Chat zweimal versucht die Done-Transition zu machen bevor das Closing-Review komplett durch war. Ich habe das jeweils zurückgedreht und beim zweiten Mal die HARTE WORKFLOW-REGEL eingebaut: Done-Transition geht nur nach explizitem OK von mir, nicht direkt von der AI. Seit der Regel ist es nicht mehr passiert.

---

## Achse 2: Prozess (Anwendung von Scrum)

**Gut gelaufen:**

- **AI-Nutzung als zentrales Arbeits-Werkzeug.** Ich arbeite mit zwei parallelen AI-Chat-Sessions: einem Strategie-Chat in der Co-Scrum-Master-Rolle (Sprint-Planning, Reviews, Retrospektiven, Daily-Journal-Pflege, Konventions-Etablierung, Risk-Register, Doku-Updates) und einem Implementation-Chat in der Senior-Engineer-Rolle (Story-Implementation, Tests, Closing-Reviews, Done-Comments). Diese Trennung hält den Kontext pro Session fokussiert und sauber. Beim Sprint-Planning hatte ich für die Schätzungen einen konservativen AI-Multiplier von 1.5x angesetzt, weil ich einen tiefen Anker wollte und austesten wollte wie viel schneller die Arbeit mit AI-Unterstützung in der Praxis tatsächlich geht. Das gemessene Ergebnis nach Sprint 1: aggregierter Multiplier 6.4x, deutlich über meiner konservativen Annahme. Ich tracke den Multiplier pro Story weiter (Daily-Journal-Tabelle plus Jira-Worklog) und beobachte über die nächsten Sprints ob der Wert sich bei realer Crypto-Interaktion (KEM, TLS, Federation) eher in den Bereich 3x bis 5x einpegelt. Die Datenbasis fliesst in die Reflexion im Schlussbericht ein.

- **Closing-Review-Prozedur etabliert.** Vor jeder Done-Transition läuft ein definierter Review-Ablauf mit 7 Phasen plus einer 8. Phase (Demo-Check). Die Phasen umfassen unter anderem Code-Read mit kritischem Blick, AC-Verifikation gegen die Story-Spec, Test-Suite-Run, Audit nach 10 Sicherheits- und Qualitäts-Kategorien (Crypto, Logging, Error-Handling, etc.), Findings-Klassifikation, Live-Verifikation im Container, Doku-Update. Findings werden in vier Tiers eingeordnet: Tier 0 (in der gleichen Story sofort gefixt), Tier 1 (eigene neue Jira-Story dafür anlegen weil substantiell), Tier 2 (in `docs/13_deferred_findings.md` mit klarem Trigger eingetragen wann das angegangen werden muss), Tier 3 (Lesson Learned ins Memory). Hat dafür gesorgt dass keine Story mit unsichtbaren offenen Punkten auf Done gerutscht ist und dass Findings systematisch weiterverarbeitet werden statt im Code untergehen.

- **Demo-Konvention mit D-NNN-Markern.** Pro Sprint werden Mini-Demos durchnummeriert (D-001, D-002 etc.) und in einem Demo-Ordner abgelegt. Jede Demo ist reproduzierbar (Befehls-Folge plus erwartete Outputs dokumentiert) und hat einen Trigger der definiert wann sie sinnvoll ist: Sprint-Goal-Meilenstein (z.B. D-004 als Beweis dass End-to-End-Login läuft), vor einem Mentor-Termin (zum Vorführen), oder Session-Ende (um den Tagesfortschritt sichtbar zu machen). Sechs Demos in Sprint 1, alle reproduzierbar. Damit habe ich konkretes Vorzeige-Material für Mentor-Termin und Schlussbericht statt nur "Tests sind grün".

- **Evidence-File-Konvention als Teil der DoD.** Pro abgeschlossener Story wird ein Markdown unter `sprint_journal/sprint_<n>/evidence/<JIRA-KEY>_*.md` angelegt mit Was-Bewiesen, Befehlen, Output, AC-für-AC-Verifikation, Closing-Review-Findings und Files-Liste. Damit kann ich beim Sprint-Review-Schreiben jede Story in 30 Sekunden nachvollziehen statt im Code zu suchen. Definition-of-Done-Pflicht: ohne Evidence-File geht keine Story auf Done.

- **HARTE WORKFLOW-REGEL als Live-Adaption etabliert.** Nachdem die AI im Implementation-Chat zweimal hintereinander (PQC-25 und PQC-22) eigenständig Done-Transitions versucht hat ohne mein OK abzuwarten, habe ich eine harte Regel ins Memory geschrieben: Stories bewegen sich strikt nur entlang To Do → In Progress → In Review → Done, und der Schritt von In Review zu Done geht ausschliesslich nach explizitem User-OK. Seit der Regel im Memory ist es nicht mehr passiert. Klassisches Beispiel für die Empirismus-Säule (beobachten, anpassen, weitermachen).

**Verbesserungsbedarf:**

- **Story-Refinement für die SEC-Stories ist erst während des Sprints passiert, nicht vorher.** Story-Refinement ist der Scrum-Schritt in dem Stories detailliert werden: Akzeptanzkriterien geschrieben, Aufwand geschätzt, Abhängigkeiten geklärt. Normalerweise passiert das im Backlog-Refinement vor dem Sprint-Planning, damit das Sprint-Backlog beim Planning ready ist. Bei mir war es so: PQC-19 (FastAPI-Skeleton) Closing-Review hat fünf fehlende Sicherheits-Middlewares aufgedeckt (Request-ID, CORS, TrustedHost, Security-Headers, Rate-Limiting). Statt diese als Tier-2 zu deferren habe ich sie als Tier-1 zu fünf neuen Stories PQC-79 bis PQC-83 gemacht und sie sind dann noch in Sprint 1 implementiert worden. Das hat funktioniert, aber sauberer wäre gewesen die Web-Security-Baseline schon beim ursprünglichen Backlog-Refinement vor Sprint 1 zu identifizieren und zu spec'en. Lehre für Sprint 2: vor Sprint-Start eine "Welche Security-, Quality- und Cross-Cutting-Concerns betrifft dieser Sprint?"-Checkliste durchgehen.

- **Sprint-Planning hat das SEC-Vorziehen nicht antizipiert.** Sprint 1 hatte 41 SP Must geplant, real geliefert wurden 47 SP (41 Must plus 5 Stretch plus 10 SEC zusätzlich plus Carry-Over INF-3/INF-4). Der Sprint-Plan war damit faktisch instabil. Das war diesmal positiv (mehr Output als geplant), aber strukturell ist es ein Planungs-Defizit weil ich die SEC-Lücke beim Planning nicht gesehen habe. Für Sprint 2 mit den Erkenntnissen aus Sprint 1 muss Planning realistischer und vollständiger werden, gleichzeitig auch nicht überoptimistisch wegen des 6.4x-Multipliers den ich gemessen habe.

---

## Achse 3: Selbstmanagement

**Zeitmanagement.** Sprint 1 hatte 8 Kalendertage, davon 6 effektive Arbeitstage gemäss meinem Standard-Schedule (zwei Wochenend-Sessions, ein Mittwoch-Slot, ein Sonntag-Sprint-Start) plus zwei Ausnahmen die ich bewusst eingeplant habe (Pfingstmontag 25.05 und Donnerstag-Sondersession 28.05). Total Implementation-Zeit über alle Stories: 14h 18m gemäss Jira-Worklogs, dazu kommt Strategie-Chat-Doku-Pflege die ich in dieselben Worklogs eingerechnet habe. Im Vergleich zu Sprint 0 (0.5 h/Tag-Schnitt) eine deutliche Steigerung der Arbeitsdichte. Funktioniert hat es weil ich die langen Slots (Samstag-Endspurt mit 11 Stories, App-Bundle am Sonntag) als Block-Phasen genutzt habe statt verteilt.

**Fokus.** Die Bundle-Strategie hat geholfen den Fokus zu halten: SEC-Stories als ein 75-Min-Block, App-Stories als 50-Min-Block. Innerhalb eines Bundles bleibt der Kontext geladen und Code-Reuse trägt von Story zu Story. Der Wechsel zwischen Strategie-Chat und Implementation-Chat war klar definiert (ich entscheide selbst wann ich umschalte), keine Reibung. Fokus-Killer war Setup-Friction: bei PQC-20 (Expo-Skeleton) habe ich 30 Min mit Node-Upgrade und SDK-Downgrade verloren, das ist Kontext-Switch-Aufwand der nicht in Code-Output umgesetzt wird.

**Energie und Motivation.** Insgesamt stabil bis hoch. Der Endspurt am Samstag 30.05 mit 11 Done-Stories war energisch und motivierend weil ich gesehen habe wie der Sprint zum Ziel kommt. Die Closing-Reviews als Disziplin-Element haben mir geholfen Stories sauber abzuschliessen statt halbfertig liegen zu lassen. Die zwei Ausnahmen vom Standard-Schedule (Pfingstmontag, Donnerstag) waren gezielte Boost-Entscheidungen weil ich Lust auf das Projekt hatte, nicht Pflicht-Sessions.

**Schätz-Genauigkeit und AI-Multiplier-Beobachtung.** T-Shirt-Sizes haben für Code-Stories grundsätzlich gut funktioniert, die klassischen Stunden-Werte (XS=1h, S=3h, M=7h, L=15h) sind realistische Anker für die "ohne AI"-Aufwände. Mit dem gemessenen AI-Multiplier von 6.4x aggregiert komme ich auf realistische Implementations-Zeiten. Aber: die Verteilung ist heterogen. Outlier nach oben (Verifikations-Stories QUA-2 plus QUA-3 mit 17.6x, Bundle-Stories PQC-80/81/82 mit 10-15x) sind nicht repräsentativ für echten Implementations-Aufwand. Outlier nach unten (Skeleton-Stories SKL-1 plus SKL-2 mit jeweils 2.0x wegen Setup-Friction) zeigen wo AI weniger hilft. Im stabilen Mittelbereich (5x bis 8x) liegen die meisten "echten" Code-Stories mit Validation-Logik plus Tests. Ich tracke den Multiplier pro Story weiter und beobachte ob er sich in Sprint 2 bei realer Crypto-Interaktion (KEM, TLS, Federation) auf 3x bis 5x reduziert wie ich vermute.

---

## Top 3 Maßnahmen für Sprint 2

1. **Cross-Cutting-Concerns-Checkliste vor Sprint-2-Start.** Bevor das Sprint-Backlog für Sprint 2 final ist, gehe ich eine kurze Checkliste durch: Welche Security-Aspekte ziehen sich durch die geplanten Sprint-Stories? Welche Logging-, Audit-, Error-Handling-Themen sind cross-cutting? Welche Quality-Gates fehlen noch? Damit nicht wie in Sprint 1 die SEC-Stories erst aus einem Closing-Review herausfallen und 10 SP unerwartetes Material in den Sprint reinrutschen. Konkrete Themen für Sprint 2: TLS-Cert-Handling (Self-Signed vs CA), Token-Storage-Security (server-side Persistenz für Federation-Sessions), OAuth-State-Parameter gegen CSRF, External-IdP-User-Data-Validation.

2. **OAuth-Setup als eigene Stories im Sprint-2-Backlog früh priorisieren.** Beim Sprint-2-Planning prüfen ob für die externe Provider-Registrierung (Google OAuth-Client in Google Cloud Console, Microsoft Azure-AD-App) eigene Stories existieren. Falls nicht, im Refinement anlegen. Diese Setup-Stories müssen am Anfang des Sprints stehen, damit die Wartezeit auf Microsoft-App-Approval (kann mehrere Stunden bis Tage dauern) die Federation-Stories (BRK-1 bis BRK-7) nicht blockiert. Adressiert die Risiken R-T04 (OIDC-Setup-Komplexität) und R-S05 (Externe Abhängigkeiten verzögern Sprint 2) durch saubere Sequenzierung im Sprint-Backlog statt durch Ad-hoc-Aktion.

3. **AI-Multiplier-Hypothese in Sprint 2 testen und dokumentieren.** Sprint 1 hat aggregiert 6.4x ergeben, ich vermute dass bei echter Crypto-Interaktion (KEM-Wrapper, TLS, Federation-Logik) der Multiplier eher zwischen 3x und 5x liegen wird. Sprint 2 ist mit überwiegend Crypto- und Federation-Stories der ideale Test. Ich tracke konsequent pro Story (Daily-Journal-Tabelle plus Jira-Worklog mit Kontext-Notiz) und aggregiere am Sprint-2-Ende nach Story-Typ. Hypothese wird verifiziert oder verworfen, Datenbasis fliesst in den Schlussbericht.

---

## Erkenntnisse fürs Schlussbericht-Kapitel "Reflexion"

- **AI-Multiplier in der Praxis ist hoch und stark heterogen.** Ich hatte im Sprint-Planning bewusst einen konservativen Multiplier von 1.5x angesetzt um einen tiefen Anker zu haben und um austesten zu können wie viel schneller die Arbeit mit AI tatsächlich wird. Sprint 1 hat 6.4x aggregiert ergeben. Aber die Verteilung pro Story-Typ ist heterogen: Verifikations-Stories und Bundle-Stories liegen bei 10x bis 18x (Setup-Effekte und Vorarbeit-Effekte), Setup-Stories mit Tool-Friction liegen bei 2x (AI hilft bei Environment-Problemen weniger), der stabile Mittelbereich bei echten Code-Stories mit Validation-Logik liegt bei 5x bis 8x. Ich tracke den Multiplier pro Story weiter und werde am Projekt-Ende eine differenzierte Aussage machen können statt nur einer aggregierten Zahl. Für das Reflexions-Kapitel ist die Heterogenität wichtiger als der Mittelwert.

- **Empirismus als Adaptions-Prinzip funktioniert in der Praxis.** Drei konkrete Beispiele aus Sprint 1: erstens die HARTE WORKFLOW-REGEL gegen Premature-Done-Versuche der AI (nach zwei Beobachtungen Regel ins Memory geschrieben, seitdem stabil), zweitens das SEC-Vorziehen (Findings aus Closing-Review wurden als neue Sprint-Stories aufgenommen statt verschoben), drittens die Zeiterfassungs-Präzisierung nach der PQC-32-Diskrepanz (Worklog umfasst jetzt Coding plus Recherche plus Closing-Review plus Demo, nicht nur Schreib-Zeit). In allen drei Fällen wurde beobachtet, dokumentiert, angepasst und persistiert. Das ist die Empirismus-Säule wie sie im Scrum Guide steht, in der Solo-Anwendung mit AI-Unterstützung.

- **Die Trennung zwischen Strategie-Chat und Implementation-Chat hat das Solo-Scrum-Setup tragfähig gemacht.** In klassischem Solo-Scrum droht das "alle Rollen bei einer Person"-Problem zu untracked work zu führen und Rollen-Konflikte zu vermischen. Bei mir hat die Trennung in zwei AI-Chat-Sessions diesen Effekt aufgefangen: Strategie-Chat als Co-Scrum-Master macht Prozess-Pflege, Implementation-Chat als Senior-Engineer macht Code. Jede Session bleibt in ihrer Rolle, kein Kontext-Switching innerhalb einer Session. Für die Bewertung der Solo-Scrum-Adaption ist das ein dokumentierbarer Mechanismus, kein bloßes "ich bin halt alle Rollen".

- **Closing-Reviews mit Tier-Klassifikation der Findings sind Voraussetzung für sauberes Solo-Scrum.** Ohne externes Review (klassischer Code Review oder QA) droht in Solo-Arbeit die "ich finde es selber gut, also ist es done"-Falle. Die Closing-Review-Prozedur mit 7 Phasen plus Demo-Check plus 4-Tier-Findings-System ersetzt das externe Review nicht vollständig, aber sie schafft einen Disziplin-Rahmen der Findings sichtbar und nachvollziehbar macht. 30 Findings in Sprint 1 dokumentiert (13 davon resolved, 5 als neue Stories ausgelagert, der Rest in `13_deferred_findings.md` mit Triggern getrackt) zeigt dass das System Findings produktiv weiterverarbeitet statt sie zu vergessen.

- **Setup-Friction limitiert AI-Effekt und sollte in der Planung berücksichtigt werden.** SKL-1 und SKL-2 mit jeweils nur 2.0x Multiplier zeigen wo AI weniger hilft: Node-Versions-Konflikte, Expo-SDK-App-Store-Kompatibilität, Docker-Desktop-Start. Diese Probleme sind spezifisch zur Entwickler-Maschine oder zum externen Tool-Ökosystem (App Store), AI kann sie nicht abkürzen weil die Validation immer auf der lokalen Maschine passiert. Für die Schätz-Praxis bedeutet das: Setup-Stories sollten in der Schätzung einen Friction-Aufschlag bekommen oder bewusst als Risk-Items markiert werden.
