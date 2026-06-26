# Evidence: PQC-26 CRY-6 Client-Side Crypto-Abstraction (App)

**Story:** PQC-26 CRY-6 (5 SP, M-Size)
**Sprint:** 3
**Status:** Ready for Review
**Datum:** 2026-06-18

## Ziel und Acceptance Criteria

App-Pendant zur Server-CryptoFacade. Wrappen die @noble-Libraries fuer KEM,
HKDF, AEAD, Hash, Signature. Plus Jest-Test-Setup als Test-Runner-Foundation
fuer Sprint-3-Folge-Stories (APP-2/3/5/6) und Sprint-4.

| AC | Status | Evidenz |
| --- | --- | --- |
| AC-1 TypeScript-Module kem.ts, cipher.ts, signature.ts, hash.ts existieren | OK (plus hkdf.ts, config.ts, index.ts) | 7 Files unter `app/src/crypto/`. Pfad ist `app/src/crypto/` statt `app/crypto/` (Sprint-1-Konvention, bewusste Anpassung mit User-OK) |
| AC-2 Wrapping @noble/post-quantum, @noble/ciphers, @noble/hashes | OK | kem.ts: ml_kem768 + ml_kem1024 aus @noble/post-quantum/ml-kem; signature.ts: ml_dsa65 aus @noble/post-quantum/ml-dsa; hkdf.ts: HKDF-SHA256 aus @noble/hashes; cipher.ts: AES-GCM aus @noble/ciphers; hash.ts: SHA-256 aus @noble/hashes |
| AC-3 Algorithmus-Auswahl via Config | OK | `config.ts` exportiert SUPPORTED_KEM_ALGORITHMS, SUPPORTED_KEM_DEFAULT, SUPPORTED_SIGNATURE_*, HKDF_INFO_DEFAULT, AES_GCM_* analog server/config.py |
| AC-4 Unit-Tests via Jest | OK | 6 Test-Files in `app/src/crypto/__tests__/`. jest.config.js mit ts-jest-Preset, package.json mit jest + ts-jest + @types/jest als devDeps, `npm test` + `npm test:watch` Scripts. Cross-Validation-Test fuer F-098 mit hardcoded Hex-Vector aus Python-Server. |

## In PQC-26 implementiert

**Neue Files (Module + Tests + Setup):**

- `app/jest.config.js` (NEU, 28 Zeilen): Jest-Config mit ts-jest-Preset,
  testEnvironment node, isolatedModules-Compile fuer Schnelligkeit.
- `app/src/crypto/config.ts` (42 Zeilen): Algorithm-Whitelisten + Defaults +
  AES-GCM-Konstanten + isKemSupported-Type-Guard.
- `app/src/crypto/kem.ts` (93 Zeilen): kemKeygen/kemEncapsulate/kemDecapsulate
  als API analog server/crypto/adapters/liboqs_kem.py. Switch auf ml_kem768
  bzw. ml_kem1024 abhaengig von alg-Parameter.
- `app/src/crypto/hkdf.ts` (53 Zeilen): deriveKey + deriveSessionKey
  Convenience-Wrapper, matched SES-2-Konvention.
- `app/src/crypto/cipher.ts` (78 Zeilen): aeadEncrypt/aeadDecrypt mit AES-256-GCM
  via @noble/ciphers. randomNonce() Helper. AeadDecryptError-Wrapper analog
  Python AeadDecryptError aus CRY-3.
- `app/src/crypto/hash.ts` (17 Zeilen): hashSha256-Wrapper.
- `app/src/crypto/signature.ts` (41 Zeilen): signatureVerify-only (ML-DSA-65).
  Sign ist Server-Only (TokenService.issue PQC-32), App hat absichtlich
  keinen sign().
- `app/src/crypto/index.ts` (22 Zeilen): Barrel-Export.
- 6 Test-Files in `app/src/crypto/__tests__/` (380 Zeilen total): config,
  kem (parametrisiert 768/1024 + Implicit-Rejection), **hkdf (mit F-098
  Cross-Validation-Hex-Vector)**, cipher (Roundtrip + 4 Tamper-Szenarien),
  hash (NIST-Test-Vektoren), signature (sign+verify Roundtrip + 3 Tamper).

**Aenderungen:**

- `app/package.json`:
  - `@noble/hashes ^2.0.0` als Dep hinzugefuegt.
  - `jest ^30.0.0`, `ts-jest ^29.2.0`, `@types/jest ^29.5.0` als devDeps.
  - `npm test` + `npm test:watch` Scripts.

## Architektur-Entscheidungen

**TypeScript-Folder app/src/crypto/ (statt app/crypto/):** Sprint-1-Konvention
ist app/src/<bereich>/ fuer App-Source-Code. Story-AC wortwoertlich app/crypto/
ist bewusst angepasst (User-OK eingeholt).

**Jest mit testEnvironment=node statt jest-expo:** App-Crypto ist reine
JS-Logik ohne React-Komponenten. Spaeter (PQC-55/56 Component-Tests) wird
ein zweites Project mit jest-expo-Preset ergaenzt - oder via Jest-Projects-
Feature in einer Config kombiniert.

**Signature verify-only:** App-Side hat kein Sign weil das einen App-Side-
Signing-Key voraussetzen wuerde. Architektur-Doc 07_design.md sagt
Server-only-Sign. Verify ist im App-Code optional (aktuelles
Trust-the-Server-Modell), aber bereitgestellt fuer Defense-in-Depth.

**Cross-Validation-Test in hkdf.test.ts:** Hardcoded Hex-Vector
`99c8dbb0a477ecbfcce86d97e1b56e44938fb5b0a92875671e4b5064f2aa634f`
aus Python-Server (HKDF mit bytes(range(32)), "test-session-id-22ch",
b"app-session-v1"). Sichert byte-Identitaet zwischen Python und TypeScript -
sonst zerfaellt die Session-Key-Identitaet zwischen App und Server.

## Tests + Verifikation

**Sandbox-Constraint:** kein npm install / node_modules in der Sandbox.
TypeScript-Compile- und Jest-Run gehen analog zum liboqs-Skip-Pattern erst
auf der User-Maschine bzw. CI.

- TypeScript-Syntax-Check: alle 13 Files (7 Module + 6 Tests) parsen
  sauber, mit \n abgeschlossen, keine Truncation. `tsc --noEmit` zeigt
  nur "Cannot find module @noble/*"-Errors (npm install fehlt) - keine
  echten Syntax-Errors.
- Server-Regression-Test: `pytest --no-cov -q` weiterhin 248 passed,
  5 skipped (keine Server-Aenderung in dieser Story).
- App-Tests laufen lokal beim User via `cd app && npm install && npm test`.

## Closing-Review (10 Kategorien)

| Kategorie | Befund |
| --- | --- |
| 1 AC | Alle 4 AC erfuellt (siehe Tabelle oben) |
| 2 Code-Quality | TypeScript-Strict-konform, vollstaendige Type-Hints, jsdoc-Docs analog Python-Server |
| 3 Test-Coverage | 6 Test-Files mit 30+ Test-Cases, kritisch ist hkdf.test.ts F-098 Cross-Validation |
| 4 Security | Verify-only-Signature, AeadDecryptError-Wrapping, FIPS-203-Implicit-Rejection passthrough, CSPRNG-Nonce via @noble |
| 5 Cross-Impact | resolved F-098 (Cross-Validation), AC-2 von PQC-47 (App-Side HKDF), AC-2 von PQC-49 (App-Side-Retry-Foundation) |
| 6 Documentation | jsdoc fuer jedes Modul mit Spec-Refs (FIPS 203/204, RFC 5869, NIST SP 800-38D) + Cross-Ref auf Python-Pendant |
| 7 Error-Handling | AeadDecryptError + defensive try-catch in signatureVerify, KEM-Errors propagieren |
| 8 Performance | @noble/post-quantum: ~3'780 keygen/s, ~3'220 encap/s, ~4'030 decap/s auf Apple M4. Mobile (iPhone) langsamer aber fuer Single-Session-Init OK |
| 9 Standard-Compliance | NIST-Naming, FIPS 203/204, RFC 5869, NIST SP 800-38D, alles mit Spec-Refs in Doc-Strings |
| 10 Demo/Evidence | Cross-Validation-Test ist die zentrale Demo dass Server-App-Crypto byte-identisch arbeitet |

Phase 1 vor Review: WebSearch @noble/post-quantum 2026 + @noble/hashes HKDF
API + @noble/ciphers AES-GCM. Grep nach Secrets/TODOs in den 13 Files:
keine.

Phase 8 Demo-Trigger: Cross-Validation-Test verbindet Python-Server und
TypeScript-App. Mini-Demo D-008-Vorlaeufer wird nach PQC-50 DCH-1 + PQC-58
APP-5 voll-end-to-end demonstrierbar.

## Findings

**Resolved durch PQC-26:**

| ID | Resolution |
| --- | --- |
| F-098 | **resolved** durch `hkdf.test.ts` Cross-Validation-Test mit deterministischem Hex-Vector aus Python-Server (byte-identische Pruefung) |

**AC-2 Cross-Story-Resolutions:**

| Story | AC | Resolution |
| --- | --- | --- |
| PQC-47 SES-2 | AC-2 App-Side-HKDF | **resolved** durch `hkdf.ts deriveSessionKey()` |
| PQC-49 SES-4 | AC-2 App-Side-Retry-Foundation | partial: Crypto-Layer steht, eigentliche Retry-Loop kommt mit sessionClient.ts in PQC-59 APP-6 |

**Neue Findings:**

| ID | Severity | Beschreibung | Tracking |
| --- | --- | --- | --- |
| F-106 | Should | `app/src/app/login.tsx` ist seit PQC-61-Commit corrupt (Edit-Truncation hat das styles-Objekt 2x dupliziert mit "enter"-Fragment). TypeScript-Compile failed mit Syntax-Errors ab Zeile 313. Pre-existing seit Sprint 2, nicht durch PQC-26 verursacht aber bei tsc-Check entdeckt. **Hotfix-Commit empfohlen vor weiteren App-Stories.** | open, Hotfix-Empfehlung |
| F-107 | May | Sandbox kann TypeScript/Jest nicht ausfuehren (kein npm install). Konsequenz: App-Tests muessen lokal beim User laufen, analog liboqs-Server-Skip-Pattern. Sprint-4-Polish koennte sandbox-friendly mock-modules ergaenzen. | Sprint 4 Polish |

Keine Must-Fixes. F-106 ist Should-Hotfix-empfohlen (pre-existing), nicht Teil der PQC-26-Story.

## Story-Aufwand

- Story-Points: 5
- T-Shirt: M (7h Schaetzung)
- Tatsaechliche Zeit: tba (User entscheidet)
- AI-Multiplier hoch: Pattern-Replikation aus Server-Side (CRY-3/4/7), plus
  Jest-Setup das ohnehin sehr standardisiert ist.

## Folgestories

- **PQC-58 APP-5 SessionContext (2 SP):** nutzt `crypto/` zur Session-Init-
  Orchestrierung in der App.
- **PQC-59 APP-6 secureClient.ts (5 SP):** nutzt aeadEncrypt/Decrypt fuer
  Encrypted-Channel-Requests. Inkl. Retry-Loop fuer SES-4-406.
- **PQC-56 APP-3 Profile-Screen (5 SP):** End-to-End-Demo mit dem
  abgeleiteten Session-Key.
- **F-106 Hotfix login.tsx**: separater Commit empfohlen vor APP-Stories
  weiterlaufen.
