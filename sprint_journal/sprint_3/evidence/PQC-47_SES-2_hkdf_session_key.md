# Evidence: PQC-47 SES-2 HKDF-Session-Key-Ableitung

**Story:** PQC-47 SES-2 (2 SP, S-Size)
**Sprint:** 3
**Status:** Ready for Review
**Datum:** 2026-06-18

## Ziel und Acceptance Criteria

Server-Helper der HKDF-SHA256 mit SES-2-Konvention wrapped: ML-KEM-shared_secret
als IKM, ``settings.session.hkdf_info`` als Domain-Separation-Info, session_id
als ASCII-Salt. Output ist der 32-Byte AES-256-GCM-Session-Key.

| AC | Status | Evidenz |
| --- | --- | --- |
| AC-1 Server leitet session_key = HKDF(shared_secret, info=app-session-v1, salt=session_id) ab | OK | `services/session_key_derivation.py::derive_session_key` wrapped `facade.hkdf` mit hkdf_info aus SessionConfig + salt=session_id.encode("ascii"). Test `test_derive_session_key_matches_direct_facade_hkdf` sichert Pass-Through-Identitaet. |
| AC-2 App-Seite tut dasselbe nach kem.decaps | **deferred zu PQC-26 CRY-6** | Cross-Doku im Modul-Docstring von `session_key_derivation.py` (Sektion App-Seite). Deterministischer Test-Vektor in `test_session_key_derivation.py` als Cross-Validation-Basis. |
| AC-3 Server und App identische 32-Byte-Keys | Server-Seite OK, App-Side-Verifikation in PQC-26 | `SESSION_KEY_LENGTH_BYTES = 32` Konstante. Test `test_derive_session_key_returns_32_bytes` plus `test_derive_session_key_is_deterministic` belegen Determinismus. RFC 5869 HKDF-SHA256 ist mathematisch deterministisch ueber Implementations-Grenzen hinweg. |

## In PQC-47 implementiert

**Neue Files:**

- `server/services/session_key_derivation.py` (91 Zeilen): Modul-Helper
  ``derive_session_key(facade, *, shared_secret, session_id, hkdf_info)``.
  Konvention explizit im Modul-Docstring: HKDF-SHA256 mit
  IKM=shared_secret, info=hkdf_info, salt=session_id-ASCII-bytes, length=32.
- `server/tests/test_session_key_derivation.py` (183 Zeilen): 7 Tests fuer
  Determinismus, Domain-Separation (info, salt, IKM), 32-Byte-Output,
  ASCII-Salt-Konvention, Pass-Through-Sanity.

## Architektur-Entscheidungen

**Salt = session_id.encode("ascii"):** session_id ist als urlsafe-base64-
String (22 chars) bereits Server- und App-bekannt. ASCII-encoding ist die
einfachste, eindeutig-rekonstruierbare Form auf beiden Seiten. Alternative
waere base64-decode auf 16 Byte rohe Bytes - mehr Schritte, gleicher
Security-Effekt, mehr Fehlerquellen.

**hkdf_info als Parameter (nicht hardcoded):** ermoeglicht Domain-Separation
ohne Code-Aenderung wenn das Protokoll auf v2 inkrementiert. Default kommt
aus SessionConfig.hkdf_info.

**Modul-Funktion statt Service-Klasse:** zustandslos, eine Funktion. Kein
Service-Lifecycle noetig. Mit explizitem Parameter facade einfach
testbar (Mock-/PlaceholderSignature-Registry).

**App-Seiten-Konvention explizit im Modul-Docstring:** App-Side
(PQC-26 CRY-6) muss exakt dieselben Inputs verwenden. Cross-Validation
ueber den deterministischen Test-Vektor (bytes(range(32)),
"test-session-id-22ch", b"app-session-v1") zur PQC-26-Verifikation.

## Tests + Verifikation

- `pytest tests/test_session_key_derivation.py -v` 7 passed.
- `pytest --no-cov -q` 234 passed, 5 skipped (7 mehr als nach PQC-48).
- `ruff check` + `ruff format`: all clean.

## Closing-Review-Findings

10 Kategorien tief geprueft. Standard-Compliance verifiziert (RFC 5869
HKDF-SHA256). Output-Laenge 32 Byte = AES-256-GCM-Key.

**Findings:**

| ID | Severity | Beschreibung | Status nach PQC-47 |
| --- | --- | --- | --- |
| F-091 | Info | HKDF-Aufrufkonvention (info=b"app-session-v1", salt=session_id) in SES-2 dokumentieren | **resolved** in dieser Story (Modul-Docstring + Code + Tests) |
| F-098 | Info | Bei PQC-26 CRY-6 Cross-Validation-Test ergaenzen, der den deterministischen Test-Vektor aus test_session_key_derivation.py app-seitig reproduziert um Byte-Identitaet ueber Sprachen-Grenzen zu sichern. | **open**, Trigger PQC-26 Story-Start |

Keine Must-/Should-Fixes.

## Story-Aufwand

- Story-Points: 2
- T-Shirt: S (3h Schaetzung)
- Tatsaechliche Zeit: tba (User)
- AI-Multiplier-Beobachtung: hoch. Pattern-Replikation aus CRY-3
  (facade.hkdf existiert bereits) + reiner Helper-Wrap. Hauptzeit ging
  in Tests + Konventions-Dokumentation.

## Folgestories

- **PQC-46 SES-1 POST /session/init (8 SP):** Erster Consumer.
  Verkettet: kem_encaps -> derive_session_key -> session_service.create.
- **PQC-26 CRY-6 Client-Side Crypto (5 SP):** App-Side HKDF-SHA256 mit
  identischen Parametern. Cross-Validation-Test gegen den Test-Vektor.
