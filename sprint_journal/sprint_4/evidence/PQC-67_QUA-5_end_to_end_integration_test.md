# Evidence PQC-67 QUA-5: End-to-End-Integration-Test

**Story:** PQC-67 (QUA-5)
**Datum:** 2026-07-07
**T-Shirt:** L | **SP:** 8 | **Sprint:** 4 (Carry-Over aus Sprint 3)

## Was wurde gebaut

`server/tests/test_integration_e2e_flow.py` (358 Zeilen): voll-integrierter End-to-End-Test der kompletten Kette Local Login → PQ-Session → Encrypted Channel, wie sie der Mobile-Client fährt. Einziger Mock ist fakeredis, alles andere echt: Argon2id-Hasher (fast-mode), UserRepository gegen in-memory SQLite, CryptoFacade mit liboqs (ML-DSA-65 plus ML-KEM-768), SessionService, RedisNonceTracker, TokenService, Auth- plus Session- plus Api-Router.

Client-Seite wird im Test nachgebaut (liboqs-Keypair, KEM-Decaps, HKDF mit salt=session_id / info=`app-session-v1`, AES-256-GCM mit AAD=session_id), wire-format-konform zu `docs/wire_format.md` Sec 3 und 5.

## Tests

1. **Happy-Path (6 Schritte):** Login → broker_token, ML-KEM-768-Keypair, /session/init → session_id plus ciphertext, Decaps plus HKDF → 32-Byte-Key, AES-256-GCM-Request an /api/profile, Response-Decrypt → korrektes Profile-JSON.
2. **Replay-Detection:** gleiche Nonce zweimal → 400 `nonce_reused`.
3. **Unknown Session:** fabrizierte session_id → 401.
4. **Multi-Session-Isolation:** 2 parallele Sessions, unterschiedliche Keys, Cross-Use → 400 `aead_decrypt_failed` (dokumentierter Verweis auf F-142 / PQC-86 SEC-6).

## Verifikation

```bash
cd infra
docker compose build auth-service-test
docker compose run --rm auth-service-test
# 420 passed, 0 failed in 22.85s; die 4 QUA-5-Tests liefen ab dem ersten
# Container-Run gruen (Failures im Suite-Run betrafen QUA-4 plus 2 Alt-Tests)
```

## Bedeutung fürs Kolloquium (08.07.2026)

Dieser Test ist die automatisierte Absicherung des Demo-Pfads (D-008/D-009): exakt die Kette, die die Expo-App live vorführt, ist jetzt reproduzierbar im Container verifiziert. R-T08-Einschränkung bleibt: Transport-TLS-Schicht ist hier nicht Teil der Test-Kette (TestClient in-process), PQ-TLS ist separat via PQC-44/D-007 verifiziert.

## Bezug

- Erfolgskriterien: `docs/05_requirements.md` Sec 2.3.
- Jira: [PQC-67](https://rumidesigns.atlassian.net/browse/PQC-67).
