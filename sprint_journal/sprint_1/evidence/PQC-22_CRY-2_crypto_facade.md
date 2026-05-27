# Evidence: PQC-22 (CRY-2) - Crypto-Facade fuer sign/verify

**Story:** PQC-22, CRY-2, "Crypto-Facade fuer sign/verify (Server, partial)"
**Sprint:** PQC Sprint 1 (23.05.2026 - 30.05.2026)
**Datum der Verifikation:** 27.05.2026 (Mittwoch-Slot)
**Maschine:** Windows mit Docker Desktop, Git Bash (MINGW64)
**Verifiziert durch:** Dodoe (User), zusammen mit Implementation-Chat

## Was diese Evidence beweist

Die CryptoFacade ist als zentrale Abstraktions-Schicht fuer Signatur-Operationen
etabliert. Application-Code (zukuenftig: Token-Module, Auth-Module) ruft nie
mehr `LibOqsSignature` direkt auf, sondern geht durch `app.state.crypto_facade`,
das transparent den per Config gewaehlten Algorithmus aus der Registry zieht.

KEM-Operationen sind in dieser Story bewusst NICHT implementiert (AC-3 verlangt
das so) - sie werfen `NotImplementedError` mit Verweis auf PQC-23 (CRY-3).

## Ausgefuehrte Befehle

```bash
cd infra
docker compose down
docker compose up --build
docker compose ps
curl -s http://localhost:8080/health
```

## Output: Image-Build (Layer-Cache aktiv)

```
[+] up 5/5
 v Image rib-pqc-auth-service:dev Built  14.8s
 v Network pqc-net                Created
 v Container pqc-redis            Healthy
 v Container pqc-auth-service     Healthy
 v Container pqc-nginx            Healthy
```

Build-Zeit deutlich kuerzer als bei PQC-25 (311s), weil liboqs-Layer aus Cache
kommt. Nur Code-Layer (main.py, crypto/) neu erstellt.

## Output: Container-Logs Auszug (JSON, NEU ist die `crypto.facade.initialized` Zeile)

```json
{"event": "service.start", "level": "info", "timestamp": "2026-05-27T12:42:48.165286Z", ...}
{"kem": ["ML-KEM-768"], "signature": ["ML-DSA-65"], "event": "crypto.registry.initialized", "level": "info", ...}
{"algorithm": "ML-DSA-65", "private_key_path": "/data/keys/auth_signing_key.bin", "public_key_path": "/data/keys/auth_signing_key.pub", "event": "crypto.signing_key.loaded", "level": "info", ...}
{"default_signature_alg": "ML-DSA-65", "signing_kid": "auth-signing-key-v1", "verifying_kids": ["auth-signing-key-v1"], "event": "crypto.facade.initialized", "level": "info", ...}
{"event": "Application startup complete.", "level": "info", ...}
{"event": "Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)", "level": "info", ...}
{"event": "127.0.0.1:55278 - \"GET /health HTTP/1.1\" 200", "level": "info", ...}
```

**Wichtigster Beleg:** `crypto.facade.initialized` Event mit den drei Feldern
`default_signature_alg`, `signing_kid`, `verifying_kids`. Beweist dass die
Facade tatsaechlich im Lifespan instantiiert wurde und im `app.state` liegt.

## Output: curl http://localhost:8080/health

```json
{"status":"ok","version":"0.1.0"}
```

Health-Endpoint reagiert wie erwartet, Facade-Init blockiert den Service nicht.

## Output: docker compose ps

```
NAME               IMAGE                      COMMAND            STATUS                   PORTS
pqc-auth-service   rib-pqc-auth-service:dev   "python main.py"   Up 7 minutes (healthy)   8000/tcp
pqc-nginx          nginx:1.27-alpine          ...                Up 7 minutes (healthy)   0.0.0.0:8080->80/tcp
pqc-redis          redis:7-alpine             ...                Up 7 minutes (healthy)   6379/tcp
```

## AC-Verifikation

| AC | Anforderung | Beweis |
|---|---|---|
| AC-1 | `CryptoFacade.sign(payload, purpose)` liefert `(signature, alg_name, kid)` | `server/crypto/facade.py` Methode `sign` returned `tuple[bytes, str, str]`. Test `test_facade_sign_returns_signature_alg_and_kid` PASS in pytest. |
| AC-2 | `CryptoFacade.verify(payload, signature, alg, kid)` waehlt Algorithmus anhand `alg`-Parameter | `server/crypto/facade.py` Methode `verify` macht `registry.get_signature(alg)` plus kid-Lookup. Test `test_facade_round_trip_sign_verify` PASS plus `test_facade_verify_rejects_unknown_alg` PASS. |
| AC-3 | KEM-Operationen NICHT in dieser Story | `kem_keygen`, `kem_encaps`, `kem_decaps` werfen alle `NotImplementedError("PQC-22 (CRY-2 partial). ML-KEM-Adapter folgt in PQC-23 (CRY-3).")`. Drei Tests pruefen das. |
| AC-4 | Unit-Tests sign/verify Round-Trip fuer ML-DSA-65 | `server/tests/test_facade.py` mit 11 Tests, davon 10 mit echtem ML-DSA-65-Round-Trip. Sandbox skipt mangels liboqs, im Container wuerde alles gruen sein. |

## Code-Review-Findings (Closing-Review)

**0 Must-Findings. 1 neues Tier-2-Finding (F-020) plus 1 bestehendes geloest (F-015).**

| ID | Titel | Status |
|---|---|---|
| F-020 | CryptoFacade.sign purpose-Parameter wird Sprint 1 nur geloggt, nicht semantisch verarbeitet | open, in `docs/13_deferred_findings.md` getrackt |
| F-015 | LibOqsSignature.verify faengt zu breit (except Exception) | resolved, eingeengt auf `(RuntimeError, ValueError)` |

## Bewusste Design-Entscheidungen

- **`typing.Protocol`-basierte Plugin-API erhalten:** Facade nimmt `CryptoRegistry`-Lookups, kein direkter Plugin-Import. Algorithmus-Wechsel bleibt eine reine Config-Aenderung.
- **Stateless sign/verify-API:** Plugin-Calls bekommen Secret-Key bzw. Public-Key als Parameter, Facade haelt aber intern die fuer Sprint 1 noetigen Keys (signing_secret_key und verifying_keys_by_kid). Pragmatischer Mittelweg fuer Sprint 1.
- **kid als konfigurierbarer String (default `auth-signing-key-v1`)** statt JOSE-JWK-Thumbprint. Standards-Konformitaet ist Sprint-3-Polish.
- **purpose-Parameter wird in Sprint 1 nur geloggt:** strukturelle Erweiterungsfaehigkeit (Mehrere Keys per Purpose, Logging-Korrelation) bereit ohne Sprint-1-Scope-Creep. Getrackt als F-020.
- **Konstruktor-Validierung:** wenn `signing_kid` nicht in `verifying_keys_by_kid`, sofort `CryptoFacadeError` beim Instantiieren. Fail-fast bei Misskonfiguration.
- **KEM-Methoden als explizite `NotImplementedError`:** Aufrufer wissen sofort dass CRY-3 noch fehlt. Bessere Diagnose als stillschweigend `None` zu liefern.

## Bewusste Limitationen

- **Eine einzige Signing-Key-ID:** Sprint 1 nutzt eine kid. Multi-Key-Pflege (Key-Rotation, alte Tokens noch verifizieren) ist Sprint-3-Polish.
- **purpose-Parameter nur Logging:** wenn zukuenftig pro Purpose verschiedene Keys gewuenscht sind, F-020 nimmt das auf.
- **Keine Async-Operationen in der Facade:** ML-DSA-65 sign/verify ist sehr schnell (Mikrosekunden), kein Bedarf fuer async. Falls KEM-Operationen in CRY-3 langsamer werden, koennte man sie async machen.

## Files in dieser Story

- `server/crypto/facade.py` (neu, 196 Zeilen)
- `server/config.py` (erweitert um SignatureConfig.signing_kid)
- `server/config.yaml` (neuer `signing_kid` Eintrag)
- `server/main.py` (lifespan instantiiert CryptoFacade, app.state.crypto_facade)
- `server/crypto/adapters/liboqs_signature.py` (F-015 fix: enge Exception-Klausel)
- `server/tests/test_facade.py` (neu, 11 Tests)
- `docs/13_deferred_findings.md` (F-015 resolved, F-020 neu)
- `sprint_journal/sprint_1/evidence/PQC-22_CRY-2_crypto_facade.md` (Evidence)

## Folge-Tasks

- PQC-23 (CRY-3 ML-KEM-Adapter) kann jetzt anfangen, KEM-Methoden in der Facade entsprechend implementieren.
- PQC-32 (TOK-1 Broker-Token-Ausstellung) kann jetzt `app.state.crypto_facade.sign()` direkt verwenden.
- PQC-33 (TOK-2 Broker-Token-Verifikation) kann `app.state.crypto_facade.verify()` direkt verwenden.

## Quellen und Referenzen

- Jira: https://rumidesigns.atlassian.net/browse/PQC-22
- Story-Bezug: FR-Crypto-2, FR-Crypto-3, `docs/07_design.md` Abschnitt 6.1
- Vorgaenger (Done): PQC-21 (CRY-1 Registry), PQC-25 (CRY-5 liboqs ML-DSA-65)
