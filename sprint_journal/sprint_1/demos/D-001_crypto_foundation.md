# D-001 Crypto-Foundation Integration-Demo

**Demo-ID:** D-001
**Datum:** 27.05.2026 (Mittwoch-Abend-Session)
**Maschine:** Windows mit Docker Desktop, Git Bash (MINGW64)
**Sprint:** PQC Sprint 1
**Integriert:** PQC-21 (CRY-1 Registry), PQC-25 (CRY-5 liboqs ML-DSA-65), PQC-22 (CRY-2 CryptoFacade)
**Demo-Script:** `scripts/demos/crypto_foundation_demo.py`

## Worum geht es

Erste Integration-Demo des Projekts. Sie zeigt dass die komplette Crypto-Foundation
(Registry, liboqs-Adapter, Facade) end-to-end im laufenden Container funktioniert,
mit echtem ML-DSA-65 (FIPS 204), echtem persistierten Keypair auf dem Disk-Volume
und sauberer Schichtung durch die drei Sprint-1-Stories.

Der Demo deckt elf Pruef-Steps ab: Settings-Loading, Key-Persistenz-Verifikation,
Registry- und Facade-Aufbau, sign/verify Round-Trip, Tamper-Detection,
Unknown-Kid- und Unknown-Alg-Fehlerfaelle, plus die expliziten
NotImplementedError-Faelle fuer die KEM-Methoden die in PQC-23 (CRY-3) folgen.

## Ausgefuehrter Befehl

```bash
cd "C:/Users/WATASHII/Documents/Claude/Projects/Implementing PQC"
docker compose -f infra/docker-compose.yml exec -T auth-service python < scripts/demos/crypto_foundation_demo.py
```

## Output (vollstaendig, 11 Steps)

```
{"step": 1, "name": "settings_loaded", "app_name": "rib-pqc-auth-service", "environment": "dev", "signature_alg": "ML-DSA-65", "signing_kid": "auth-signing-key-v1", "private_key_path": "/data/keys/auth_signing_key.bin", "public_key_path": "/data/keys/auth_signing_key.pub"}
{"step": 2, "name": "keys_loaded_from_disk", "secret_key_len": 4032, "public_key_len": 1952, "fips_204_match_mldsa65": {"public_key_expected_bytes": 1952, "secret_key_expected_bytes": 4032, "match": true}}
{"step": 3, "name": "registry_built", "supported_signature": ["ML-DSA-65"]}
{"step": 4, "name": "facade_built", "default_signature_alg": "ML-DSA-65", "signing_kid": "auth-signing-key-v1"}
liboqs-python faulthandler is disabled
2026-05-27 13:21:41 [info     ] crypto.facade.sign             alg=ML-DSA-65 kid=auth-signing-key-v1 payload_len=38 purpose=demo signature_len=3309
{"step": 5, "name": "sign_round_trip", "payload_len": 38, "signature_len": 3309, "alg": "ML-DSA-65", "kid": "auth-signing-key-v1"}
2026-05-27 13:21:41 [info     ] crypto.facade.verify           alg=ML-DSA-65 kid=auth-signing-key-v1 payload_len=38 result=True signature_len=3309
{"step": 6, "name": "verify_happy_path", "result": true, "expected": true, "pass_": true}
2026-05-27 13:21:41 [info     ] crypto.facade.verify           alg=ML-DSA-65 kid=auth-signing-key-v1 payload_len=47 result=False signature_len=3309
{"step": 7, "name": "verify_tampered_payload", "result": false, "expected": false, "pass_": true}
{"step": 8, "name": "verify_unknown_kid", "raised_unknown_kid_error": true, "message": "Unknown kid 'unknown-kid'. Known: ['auth-signing-key-v1']", "pass_": true}
{"step": 9, "name": "verify_unknown_alg", "raised_algorithm_not_found": true, "message": "Signature algorithm 'Dilithium3' is not registered. Known: ['ML-DSA-65']", "pass_": true}
{"step": 10, "name": "kem_methods_not_implemented", "results": {"kem_keygen": true, "kem_encaps": true, "kem_decaps": true}, "pass_": true}
{"step": 11, "name": "summary", "all_checks_pass": true, "crypto_foundation": "ready for TOK-1 / TOK-2 / AUT-3"}
```

## Interpretation der Steps

| Step | Was es beweist |
|---|---|
| 1 | Settings werden aus `config.yaml` korrekt geladen. ML-DSA-65 als default-Signatur-Algorithmus, `auth-signing-key-v1` als kid, Keys persistieren im `/data/keys/`-Volume. |
| 2 | **Schluessel-Persistierung funktioniert.** Geladene Bytes: 4032 fuer Secret Key, 1952 fuer Public Key. Beides matched **exakt FIPS 204 ML-DSA-65 Spec**. Das ist der starke Beweis dass die Crypto echt ist, nicht stubbed. |
| 3 | CryptoRegistry mit echtem `LibOqsSignature`-Plugin (nicht Placeholder). |
| 4 | CryptoFacade wird mit identischer Konfiguration wie im Service-Lifespan aufgebaut. |
| 5 | `sign(payload, purpose="demo")` produziert eine echte 3309-Byte ML-DSA-65-Signatur. Die Logger-Zeilen von `crypto.facade.sign` zeigen dass die Facade die Operation strukturiert protokolliert. |
| 6 | **Happy-Path-Round-Trip:** verify mit gueltiger Signatur returnt True. AC-3 von PQC-25 plus AC-4 von PQC-22 in einem Step. |
| 7 | **Tamper-Detection:** identische Signatur gegen modifizierten Payload returnt False. Beweist die Crypto-Integritaets-Garantie. AC-4 von PQC-25. |
| 8 | **Unknown-Kid-Defense:** verify mit unbekanntem kid wirft `UnknownKidError` mit klarer Fehlermeldung. AC-2 von PQC-22 Negative-Case. |
| 9 | **Unknown-Alg-Defense:** verify mit Pre-Standard-Name wirft `AlgorithmNotFoundError`. AC-3 von PQC-21 plus AC-2 von PQC-22 Negative-Case. |
| 10 | **KEM-Methoden bewusst nicht implementiert:** Drei `NotImplementedError` mit Verweis auf PQC-23. Story-Scope-Disziplin sichtbar. |
| 11 | **`all_checks_pass: true`**: Alle zehn funktionalen Checks gruen. Crypto-Foundation ist `ready for TOK-1 / TOK-2 / AUT-3`. |

## Was diese Demo fuer den Bericht bedeutet

- **Echte FIPS-204-Crypto laeuft.** Key-Sizes matchen die Spec exakt. Nicht stubbed, nicht mock - das ist die echte ML-DSA-65 aus liboqs 0.15.0.
- **Crypto-Agility-Architektur funktioniert.** Application-Code (Demo-Script und spaeter Token-Module) ruft NIE eine konkrete Algorithmus-Klasse direkt auf. Stattdessen geht alles durch die `CryptoFacade`, die ihrerseits ueber die `CryptoRegistry` auf das passende Plugin zugreift. Der Wechsel von ML-DSA-65 zu z.B. ML-DSA-87 waere eine reine Config-Aenderung in `config.yaml`.
- **Drei Sprint-1-Stories integriert.** Eine Demo deckt PQC-21, PQC-25, PQC-22 zusammen ab.
- **Negative-Cases sind getestet.** Tamper-Detection, Unknown-Kid, Unknown-Alg werfen die richtigen Fehler. Defense-in-Depth.
- **Sprint-Goal-Fortschritt:** Sprint 1 Goal "Local Auth + Crypto Foundation - lokaler Login End-to-End mit ML-DSA-signiertem Broker-Token" hat hier den Crypto-Foundation-Teil komplett. Naechster Schritt: Token-Modul (PQC-32) das die Facade fuer Broker-Tokens nutzt.

## Bewusste Limitationen

- KEM-Operationen sind absichtlich noch nicht in der Facade implementiert. ML-KEM-768 fuer Session-Etablierung folgt in PQC-23 (CRY-3).
- Das Demo-Script umgeht den HTTP-Layer und nutzt die Module direkt im Container. Ein HTTP-basierter Demo-Endpoint kommt nicht in dieser Story sondern in der Token-Story-Reihe (PQC-32/33).
- Per F-014 lebt der Secret Key als Python-`bytes`-Objekt im Memory. Keine HSM-Integration, sondern File-basierte Persistenz. Bericht-Limitation.

## Mentor-Hinweis fuer 01.06.2026 Termin

Diese Demo kann als kurzer Live-Beweis verwendet werden: Container starten, Demo-Script
ausfuehren, 11 gruene Steps zeigen. Bringt PQC-Substanz auf den Tisch ohne sich in
Details der Token-Logik (die noch fehlt) zu verirren.

## Quellen und Referenzen

- Implementation-Files (alle bereits in Done-Stories):
  - `server/crypto/registry.py` (PQC-21)
  - `server/crypto/adapters/liboqs_signature.py` (PQC-25)
  - `server/crypto/facade.py` (PQC-22)
  - `server/crypto/keys.py` (PQC-25)
  - `server/main.py` lifespan (alle drei Stories)
- Story-Evidence-Files:
  - `sprint_journal/sprint_1/evidence/PQC-21_CRY-1_algorithm_registry.md`
  - `sprint_journal/sprint_1/evidence/PQC-25_CRY-5_liboqs_ml_dsa.md`
  - `sprint_journal/sprint_1/evidence/PQC-22_CRY-2_crypto_facade.md`
- Demo-Script: `scripts/demos/crypto_foundation_demo.py`
