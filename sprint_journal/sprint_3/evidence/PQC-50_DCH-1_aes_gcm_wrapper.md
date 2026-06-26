# Evidence: PQC-50 DCH-1 AES-256-GCM Encrypt/Decrypt Wrapper

**Story:** PQC-50 DCH-1 (2 SP, S-Size)
**Sprint:** 3
**Status:** Ready for Review
**Datum:** 2026-06-19

## Ziel und Acceptance Criteria

AES-256-GCM Wrapper auf Server- und App-Seite mit 96-bit-Nonce, Tag-Mismatch
loest Exception aus, Round-Trip-Test mit zufaelligem Plaintext.

**Realitaets-Check vor Implementation:** AC-1 + AC-2 + AC-3 sind bereits in
PQC-23 CRY-3 (Server `facade.aead_encrypt/aead_decrypt`) und PQC-26 CRY-6
(App `cipher.ts aeadEncrypt/aeadDecrypt`) durch die Foundation-Arbeit
erfuellt. Eine kleine **Asymmetrie** wurde im Audit entdeckt: App hatte
einen `randomNonce()`-Modul-Helper, Server hatte keinen. PQC-50 hat diese
Asymmetrie behoben und dezidierte DCH-1-Tests ergaenzt.

| AC | Status | Evidenz |
| --- | --- | --- |
| AC-1 Server- + App-Wrapper mit 96-bit-Nonce | OK | Server: `facade.aead_encrypt/aead_decrypt` (PQC-23) plus neuer `facade.aead_random_nonce()` Static-Helper (12 Byte). App: `cipher.ts aeadEncrypt/aeadDecrypt` + `randomNonce()` aus PQC-26. |
| AC-2 Tag-Mismatch wirft Exception | OK | Server: `AeadDecryptError` bei `InvalidTag` (cryptography.hazmat). App: `AeadDecryptError`-Klasse, throw bei catch. Beide haben Klar-Naming. |
| AC-3 Round-Trip-Test mit zufaelligem Plaintext | OK | Server: `test_dch1_random_plaintext_roundtrip` mit `secrets.randbelow(1024)+1` Bytes random Laenge + `os.urandom(N)` Inhalt. App: `random-length Plaintext (1..1024 byte) roundtrip` mit `Math.random()` + `crypto.getRandomValues`. |

## In PQC-50 implementiert

**Server-Aenderungen:**
- `server/crypto/facade.py`: Neue Static-Methode `CryptoFacade.aead_random_nonce()` (17 Zeilen incl. Docstring) als symmetrisches Pendant zur App-Side `randomNonce()`. Verwendet `secrets.token_bytes(12)`. Dokumentiert NIST SP 800-38D Section 8.2-Konvention (F-092) explizit.
- `server/tests/test_facade.py`: 4 neue dezidierte DCH-1-Tests:
  - `test_dch1_aead_random_nonce_returns_12_bytes` (AC-1)
  - `test_dch1_aead_random_nonce_is_unique` (CSPRNG-Sanity)
  - `test_dch1_random_plaintext_roundtrip` (AC-3, Random-Plaintext + Random-Laenge)
  - `test_dch1_aead_decrypt_tag_mismatch_raises_exception` (AC-2, Channel-Layer-Fokus)

**App-Aenderungen:**
- `app/src/crypto/__tests__/cipher.test.ts`: 2 neue dezidierte DCH-1-Tests am Ende der Datei:
  - `random-length Plaintext (1..1024 byte) roundtrip` (AC-3)
  - `randomNonce + Server-konformer AAD-Roundtrip (session_id als bytes)` (Vorlaeufer fuer DCH-2/DCH-3-Konvention)

## Architektur-Entscheidungen

**Server-Helper `aead_random_nonce()` als Static-Methode** statt freie Funktion: ergaenzt die Facade-API symmetrisch. Aufrufer in DCH-2/DCH-3 (PQC-51/PQC-52) koennen `CryptoFacade.aead_random_nonce()` rufen ohne `secrets`-Modul direkt zu importieren. Reduziert Crypto-Boilerplate in den Konsumenten.

**`secrets.token_bytes(12)` statt `os.urandom(12)`:** `secrets` ist Python-Idiomatic-Standard fuer Crypto-CSPRNG, `os.urandom` ist die Low-Level-Variante. Beide nutzen dieselbe OS-Quelle (`/dev/urandom`), aber `secrets`-Naming sigalisiert die Intent-Klassifikation.

**Server-Test mit `secrets.randbelow(1024)+1` Random-Plaintext-Laenge:** Story-AC sagt "Round-Trip-Test mit zufaelligem Plaintext". Wir machen randoms-Inhalt UND randoms-Laenge fuer breitere Testabdeckung.

## Tests + Verifikation

- `pytest --no-cov -q` 248 passed, 5 skipped (unveraendert, kein Test-Bruch).
- `ruff check + format` clean.
- Phase-1 Verifikation:
  - WebSearch NIST SP 800-38D Nonce-Eindeutigkeit (Trail of Bits, MDN bestaetigen 12-Byte-CSPRNG = 96-bit-Random ist akzeptabel mit ~2^48 Sessions Birthday-Limit).
  - Code-Check Server: `aead_encrypt` + `aead_decrypt` + jetzt `aead_random_nonce()` korrekt.
  - Code-Check App: `aeadEncrypt` + `aeadDecrypt` + `randomNonce()` schon vorhanden.
  - Grep nach Secrets/TODOs in den geaenderten Files: keine.

## Closing-Review (10 Kategorien)

| Kategorie | Befund |
| --- | --- |
| 1 AC | Alle 3 AC erfuellt durch CRY-3 + CRY-6 + neuen Server-Helper plus 6 dezidierte DCH-1-Tests |
| 2 Code-Quality | ruff check + format clean |
| 3 Test-Coverage | 4 Server-Tests + 2 App-Tests neu, Server-Suite weiter 248 passed |
| 4 Security | `secrets`-Modul fuer CSPRNG, 12-Byte-Nonce, `AeadDecryptError` als Application-Layer-Auth-Signal (FIPS-203 F-090 Anchor) |
| 5 Cross-Impact | CRY-3 + CRY-6 ungebrochen, neue API additiv-only |
| 6 Documentation | Docstring fuer `aead_random_nonce()` mit NIST SP 800-38D + F-092-Ref. Evidence dokumentiert Cross-Story-Reuse |
| 7 Error-Handling | unveraendert, Pass-Through wie in CRY-3 |
| 8 Performance | unveraendert |
| 9 Standard-Compliance | NIST SP 800-38D 96-bit-Nonce, FIPS-203-Implicit-Rejection-Konnex F-090 referenziert |
| 10 Demo/Evidence | DCH-1 ist Bestandteil der Sprint-Goal-Demo D-008, Mini-Demo-Vorlaeufer ist schon in `sprint_journal/sprint_3/demos/D-008-vorlaeufer*.md` |

Phase 1 (vor Review): Code-Check beider Seiten, WebSearch zu NIST SP 800-38D, Grep nach Secrets.

Phase 8 Demo-Trigger: Data-Channel-Block startet. Die DCH-2 (Header-Routing) + DCH-3 (Profile-Endpoint) brauchen jetzt diesen Wrapper. Naechste Demo nach DCH-3 als Encrypted-Channel-Roundtrip.

## Findings

**Resolved durch PQC-50:**

| ID | Resolution |
| --- | --- |
| F-092 | **partial resolution**: NIST SP 800-38D Nonce-Eindeutigkeit-Konvention im `aead_random_nonce()` Docstring + `cipher.ts randomNonce()` Docstring explizit dokumentiert. Aufrufer-Pflicht (frische Nonce pro Request) bleibt in DCH-2/DCH-3 (F-092 bleibt als Tracking offen fuer die Aufrufer-Stories). |

**Keine neuen Findings.**

Keine Must-/Should-Fixes.

## Story-Aufwand

- Story-Points: 2 (S-Size, 3h Schaetzung)
- Tatsaechliche Zeit: tba (User entscheidet)
- AI-Multiplier-Beobachtung: hoch, Story wurde durch CRY-3 + CRY-6 schon 90% erledigt. Hier nur dezidierter Helper + 6 Tests + Cross-Doku.

## Folgestories

- **PQC-51 DCH-2 Header-basiertes Session-Routing (5 SP):** verwendet `aead_random_nonce()` und session_id-AAD-Konvention.
- **PQC-53 DCH-4 Replay-Schutz via Nonce-Tracking (5 SP):** das fehlende Stueck zu F-092 (Replay-Defense auf Server-Side).
- **PQC-52 DCH-3 Geschuetzter API-Endpoint /api/profile (5 SP):** End-to-End-Consumer.
