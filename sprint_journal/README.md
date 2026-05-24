# Sprint-Journal

Dieser Ordner enthält die laufende Dokumentation der Scrum-Praxis in der Semesterarbeit "Implementing PQC". Aufbau:

- `_templates/` enthält die Vorlagen für die wiederkehrenden Sprint-Dokumente.
- Pro Sprint gibt es einen Unterordner `sprint_<N>/` mit den ausgefüllten Dokumenten dieses Sprints.
- `mentor_meetings/` sammelt die Status-Dokumente und Protokolle der drei offiziellen Mentor-Termine. Diese sind **separat** vom Sprint-Journal, weil Mentor-Termine externe Reviews sind und nicht Teil der Scrum-Events.

## Verhältnis Sprint Review zu Mentor-Termin

Wichtig: Diese beiden Events sind getrennt.

| Event | Wann | Zweck | Template |
|---|---|---|---|
| Sprint Review | Letzter Tag jedes Sprints | Selbst-Inspektion: Akzeptanzkriterien und DoD pro Story prüfen, Backlog aktualisieren | `_templates/sprint_review_template.md` |
| Mentor-Termin | Drei feste Termine pro Semester | Externes Stakeholder-Review: Architektur-, PQC- und Prozess-Feedback | `_templates/mentor_meeting_template.md` |

Details siehe `../08_scrum_setup.md` Abschnitt 9.

## Workflow pro Sprint

1. **Sprint Planning (Tag 1)**: `sprint_<N>/01_planning.md` aus dem Planning-Template anlegen, gemeinsam ausfüllen.
2. **Daily Journal (täglich)**: `sprint_<N>/02_daily_journal.md` mit kurzen Tagesnotizen pflegen.
3. **Sprint Review (letzter Tag)**: `sprint_<N>/03_review.md` aus dem Review-Template anlegen, Increment gegen Akzeptanzkriterien und DoD prüfen.
4. **Sprint Retrospective (letzter Tag, nach Review)**: `sprint_<N>/04_retrospective.md` aus dem Retro-Template anlegen, drei Reflexions-Achsen durchgehen.

## Workflow pro Mentor-Termin

1. **Vorbereitung (ca. 2 bis 3 Tage vorher)**: Status-Dokument aus `mentor_meeting_template.md` anlegen, Demo vorbereiten.
2. **Termin**: Demo plus Diskussion, Feedback direkt im Dokument festhalten.
3. **Nachbereitung**: Action Items im Backlog erfassen, Verweis aus dem aktuellen Sprint-Daily-Journal auf das Mentor-Termin-Dokument.

## Bewertungs-Bezug

Diese Sprint-Journal-Ordnerstruktur ist Teil der Erfüllung von Handlungs-Kompetenz B5.9 (Dokumente für Projektfortschritts-Überwachung erstellen und pflegen, KN:3). Sie liefert die Datengrundlage für die Reflexionstiefe im Schlussbericht (Bewertungs-Kriterium 5).
