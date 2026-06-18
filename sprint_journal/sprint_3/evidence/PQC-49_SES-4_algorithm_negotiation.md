# Evidence: PQC-49 SES-4 Algorithmus-Negotiation

**Story:** PQC-49 SES-4 (3 SP, S-Size, Should-Prio)
**Sprint:** 3
**Status:** Ready for Review
**Datum:** 2026-06-18

## Ziel und Acceptance Criteria

Algorithmus-Negotiation: wenn der Client einen nicht-unterstuetzten kem_alg
anfragt, soll der Server mit 406 plus supported_algorithms-Liste antworten,
damit der Client einen unterstuetzten Algorithmus waehlen und retried.

| AC | Status | Evidenz |
| --- | --- | --- |
| AC-1 Server liefert 406 mit supported_algorithms-Liste | OK (in PQC-46 erfuellt) | `routers/session.py` Z. 213ff liefert 406 mit `{error, requested, supported_algorithms}`. Dezidierte SES-4-Tests `test_ses4_mismatch_response_includes_supported_algorithms_list` + `test_ses4_client_retry_after_406_succeeds` belegen das. |
| AC-2 App reagiert auf 406 und retried | **deferred zu PQC-26 CRY-6** | Server-Side simuliert im Test `test_ses4_client_retry_after_406_succeeds` (zwei aufeinanderfolgende Requests). App-Code (Retry-Loop in TypeScript) gehoert zur App-Crypto-Schicht PQC-26 CRY-6, dort wird er konkret. |
| AC-3 Test mit explizit konfigurierter Mismatch-Situation | OK | 2 dezidierte Tests mit Mock-Facade.supported=["ML-KEM-768"] und Client-Request "Kyber768" / "ML-KEM-1024". |

## In PQC-49 implementiert

**Aenderungen:**
- `server/tests/test_session_router.py`: 2 neue dezidierte SES-4-Tests
  am Ende der Datei (in einer eigenen Section):
  - `test_ses4_mismatch_response_includes_supported_algorithms_list`:
    Server-supported=[ML-KEM-768], Client-request=Kyber768, prueft 406
    plus vollstaendige supported_algorithms-Liste.
  - `test_ses4_client_retry_after_406_succeeds`: Zwei-Stufen-Test der das
    Negotiation-Pattern explizit macht (erst 406 mit Liste, dann
    erfolgreicher Retry mit Server-vorgeschlagenem alg).

Keine Server-Code-Aenderung: die 406-Logik aus PQC-46 (Z. 213-225 in
`routers/session.py`) ist bereits SES-4-konform. PQC-49 ist primaer
Test-Coverage-Erweiterung plus Doku.

## Architektur-Entscheidungen

**Bei 406 bleiben + Stretch-Note F-105:** WebSearch (Phase-1) zeigte dass
HTTP 406 strikt fuer Accept-Header-Negotiation gedacht ist (RFC 7231 Sec
6.5.6). Body-Payload-Negotiation waere semantisch korrekter als 422
Unprocessable Entity. Story-Spec sagt aber explizit 406, und wire_format.md
Sec 3.3 ist konsistent. Bewusste Spec-Konformitaet gewinnt, semantischer
Stretch wird im Bericht als Lessons-Learned dokumentiert.

**AC-2 deferred zu PQC-26 CRY-6:** Etabliertes Pattern (vgl. PQC-47 SES-2 das
AC-2 ebenfalls zu CRY-6 verschob). Server-Side beweist im 2-Stufen-Test
dass Retry-Pattern moeglich ist; App-Side-Code (TypeScript-Loop) gehoert
in die App-Crypto-Schicht.

## Tests + Verifikation

- `pytest --no-cov -q` 248 passed, 5 skipped (2 mehr als nach PQC-46).
- `ruff check + format` clean.
- Phase-1 WebSearch (HTTP 406 Content-Negotiation 2026): Trail of Bits,
  MDN, asoasis.tech bestaetigen dass 406-Body bei API-Negotiation die
  Liste der akzeptablen Repraesentationen enthalten sollte. Unser Body
  matched die Best-Practice.

## Closing-Review (10 Kategorien)

| Kategorie | Befund |
| --- | --- |
| 1 AC | AC-1 + AC-3 erfuellt; AC-2 explizit deferred zu PQC-26 mit Cross-Ref |
| 2 Code-Quality | ruff clean, nur Test-Code-Aenderung |
| 3 Test-Coverage | 2 neue Tests, Total 14 fuer Session-Router |
| 4 Security | Kein neuer Code, Sicherheits-Verhalten unveraendert (Server leakt nur Whitelist, keine internen Details) |
| 5 Cross-Impact | keine API-Aenderung, nur Test-File + Evidence-File |
| 6 Documentation | wire_format.md Sec 3.3 ist konsistent, F-105 als Stretch-Note dokumentiert |
| 7 Error-Handling | unveraendert; SES-4 ist die 406-Logik die schon implementiert war |
| 8 Performance | unveraendert |
| 9 Standard-Compliance | 406 ist Story-Spec-konform, RFC-7231-Strict-Konformitaet als F-105-Stretch dokumentiert |
| 10 Demo/Evidence | Demo-Trigger weiterhin nach SES-4 erreichbar (Mini-Demo aus F-100) |

Phase 1 (vor Review): WebSearch HTTP 406 2026 Best-Practices + Grep nach
Secrets/TODOs in Test-File (keine).

Phase 8 Demo-Trigger: erreicht. Mini-Demo "End-to-End Session-Init plus
Negotiation" empfiehlt sich jetzt sinnvoll vor DCH-1.

## Findings

**Neu:**

| ID | Severity | Beschreibung | Tracking |
|---|---|---|---|
| F-105 | Info | HTTP 406 ist strikt fuer Accept-Header-Negotiation (RFC 7231). Wir nutzen 406 fuer Body-Payload-kem_alg-Negotiation (semantischer Stretch). RFC-7231-konformer waere 422 Unprocessable Entity oder OAuth-style 400 mit error-Code. Bewusst Spec-konform gehalten, im Bericht als Lessons-Learned-Story dokumentieren. | im Bericht erwaehnen, kein Code-Change | open |

Keine Must-/Should-Fixes.

## Story-Aufwand

- Story-Points: 3 (S-Size, 3h Schaetzung)
- Tatsaechliche Zeit: tba (User entscheidet)
- AI-Multiplier hoch: AC-1 + AC-3 schon in PQC-46 erfuellt, hier nur 2
  dezidierte Tests + Evidence + Stretch-Note + WebSearch fuer 406-Begruendung.

## Folgestories

- **PQC-26 CRY-6 Client-Side Crypto-Abstraction (5 SP):** App-Side-Retry-
  Loop fuer AC-2. Konsumiert SES-4-Spec aus wire_format.md Sec 3.3.
- **Mini-Demo D-008-Vorlaeufer:** mit SES-1 + SES-2 + SES-3 + SES-4 ist
  der Session-Server-Block voll. Container + curl-Demo mit
  Negotiation-Roundtrip ist jetzt sinnvoll vor DCH-Start.
