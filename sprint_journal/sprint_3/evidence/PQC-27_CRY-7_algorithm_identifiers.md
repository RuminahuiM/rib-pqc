# Evidence: PQC-27 CRY-7 Algorithmus-Identifier in Krypto-Artefakten

**Story:** PQC-27 CRY-7 (2 SP, S-Size)
**Sprint:** 3
**Status:** Ready for Review
**Datum:** 2026-06-18

## Ziel und Acceptance Criteria

Crypto-Agility-Prinzip durchsetzen: jeder Krypto-Artefakt fuehrt seinen
Algorithmus selbst mit. Wire-Format und Session-Record als Schema-Spec
dokumentiert.

| AC | Status | Evidenz |
| --- | --- | --- |
| AC-1 Token-Header enthaelt alg + kid | OK (bereits seit Sprint 1 PQC-32 TOK-1) | `services/token_service.py` baut JWS-Header `{"alg": "ML-DSA-65", "typ": "JWT", "kid": <kid>}` und Sprint-1 TOK-1/TOK-2-Tests pruefen Header-Felder. In docs/wire_format.md Section 2 dokumentiert. |
| AC-2 Session-Record enthaelt kem_alg | OK (Schema-Spec, Code in SES-3) | docs/wire_format.md Section 4: Redis-Schluessel `session:<id>` mit JSON-Feld `kem_alg`. Concrete Implementation in PQC-48 SES-3. |
| AC-3 Wire-Format Session-Init enthaelt kem_alg | OK (Schema-Spec, Code in SES-1) | docs/wire_format.md Section 3.1 + 3.2: Request + Response enthalten `kem_alg`. Concrete Implementation in PQC-46 SES-1. |
| AC-4 Documentation in docs/wire_format.md | OK | Neue Datei `docs/wire_format.md` (228 Zeilen) mit 7 Sektionen. |

## In PQC-27 implementiert

**Neue Files:**

- `docs/wire_format.md` (228 Zeilen): zentrale Spec fuer alle Krypto-
  Artefakte. 7 Sektionen:
  - Sec 1: Algorithmus-Whitelisten mit Quell-Refs (registry_init.py).
  - Sec 2: Broker-Token JWS-Compact-Format (bereits live seit Sprint 1).
  - Sec 3: Session-Init Wire-Format (Request, Response 200, 406 SES-4).
  - Sec 4: Session-Record Redis-Schema (Schluessel, TTL, JSON-Felder).
  - Sec 5: Encrypted-Channel-Wire-Format (Headers, Body, Fehler-Responses).
  - Sec 6: Algorithmus-Wechsel-Mechanik (3 Wechsel-Pfade fuer
    Crypto-Agility).
  - Sec 7: Aenderungs-Historie.

**Keine Code-Aenderungen:** Story ist primaer Spec-/Doku-Arbeit. AC-1
ist durch Sprint-1-Code bereits erfuellt; AC-2 und AC-3 spec'en das
Schema das in SES-1/SES-3 dann konkret implementiert wird.

## Architektur-Entscheidungen

**`kem_alg` im Session-Record (nicht nur im Init-Request):** auch nach
dem Init muss klar sein welcher KEM verwendet wurde. Erlaubt
Algorithmus-Wechsel pro Session, Mischbetrieb verschiedener KEMs
gleichzeitig.

**Schema-Spec vor Code-Implementation:** AC-2 und AC-3 sind Spec-Items
die in SES-1 und SES-3 konkret umgesetzt werden. CRY-7 schliesst sich
ab nachdem die Spec steht, nicht erst wenn SES-1/SES-3 implementiert
sind. Begruendung: Wire-Format-Doku stabilisiert das Schema vorab,
SES-1/SES-3 setzen dann ohne Diskussion um.

**AAD = session_id in Encrypted-Channel (Sec 5.2):** Defense-in-Depth.
Bindet jede AEAD-Operation an die Session, verhindert Cross-Session-
Replay zusaetzlich zum DCH-4 Nonce-Tracking.

## Tests + Verifikation

- AC-1-Verifikation: bestehende Token-Tests aus Sprint 1 (PQC-32/33)
  pruefen Header-Felder. Keine neuen Tests in CRY-7 noetig.
- AC-2/AC-3-Verifikation: Spec liegt vor, Code-Verifikation kommt mit
  SES-1/SES-3.
- `pytest --no-cov -q` 215 passed, 5 skipped (unveraendert seit
  PQC-23, keine Regressions).
- Markdown-Syntax: docs/wire_format.md rendert sauber (Tabellen, Code-
  Bloecke, Hierarchie konsistent).

## Closing-Review-Findings

10 Kategorien, 4 Severities, 4-Tier-Tracking.

| Kategorie | Befund | Severity |
| --- | --- | --- |
| 1 AC | Alle 4 AC erfuellt (AC-1 Code+Doku, AC-2/3 Schema-Spec, AC-4 Doku) | OK |
| 2 Code-Quality | Keine Code-Aenderung in dieser Story | OK |
| 3 Test-Coverage | AC-1 durch Sprint-1-Tests abgedeckt, AC-2/3 via SES-1/3 | OK |
| 4 Security | Crypto-Agility-Prinzip durchgesetzt, RFC 8725 BCP (no-alg) referenziert | OK |
| 5 Dependencies | Verweist auf existierende Whitelisten in registry_init.py | OK |
| 6 Documentation | Spec ist DIE Story | OK |
| 7 Error-Handling | 406 SES-4 und 400/401 DCH-Fehler-Responses dokumentiert | OK |
| 8 Performance | Nicht relevant | OK |
| 9 Standard-Compliance | FIPS 203/204, RFC 5869, RFC 8725, NIST SP 800-38D referenziert | OK |
| 10 Demo / Evidence | Doku selbst plus Evidence-File | OK |

**Neue Findings:**

| ID | Severity | Beschreibung | Tracking |
| --- | --- | --- | --- |
| F-094 | Info | docs/wire_format.md Sec 5.3 (Response-Body) ist als TBD-in-SES-3 markiert. Konkrete Konvention (gleicher Header oder X-Response-Nonce) wird in PQC-52 DCH-3 finalisiert. | bei PQC-52 DCH-3 die Sec 5.3 final updaten |

Keine Must-/Should-Fixes. Ein Info-Finding fuer Folge-Update der Doku.

## Story-Aufwand

- Story-Points: 2
- T-Shirt: S
- Schaetzung: 3h
- Tatsaechliche Zeit: tba (User entscheidet)
- AI-Multiplier-Beobachtung: hoch. Spec-Synthese aus bereits vorliegenden
  Sprint-1-Token-Format plus Design-Doc 6.1 plus jetzt-frisch
  implementierte CRY-3-Facade-API. Doku zum geistigen Konsolidieren des
  Datenflusses bevor SES-1/SES-3 ihn implementieren.

## Folgestories

- **PQC-48 SES-3 Session-Store mit TTL (Redis):** implementiert das in
  docs/wire_format.md Sec 4 spezifizierte Schema.
- **PQC-46 SES-1 POST /session/init:** implementiert das in Sec 3.1/3.2
  spezifizierte Wire-Format.
- **PQC-52 DCH-3 Geschuetzter /api/profile-Endpoint:** finalisiert Sec 5.3
  (Response-Body-Format).
