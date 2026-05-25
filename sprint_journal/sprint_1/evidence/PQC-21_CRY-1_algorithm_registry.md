# Evidence: PQC-21 (CRY-1) - Algorithm Registry fuer KEM und Signature

**Story:** PQC-21, CRY-1, "Algorithm Registry fuer KEM und Signature (Server)"
**Sprint:** PQC Sprint 1 (23.05.2026 - 30.05.2026)
**Datum der Verifikation:** 25.05.2026
**Maschine:** Windows mit Docker Desktop, Git Bash (MINGW64)
**Verifiziert durch:** Dodoe (User), zusammen mit Implementation-Chat

## Was diese Evidence beweist

Die CryptoRegistry steht als zentrale Plugin-Registry fuer KEM- und Signatur-
Algorithmen. Beim Service-Start werden alle in `config.yaml` aufgelisteten
Algorithmen mit Placeholder-Plugins registriert. Echte liboqs-Adapter folgen
in PQC-25 (CRY-5), Risiko R-T01 bleibt damit auf eine Story isoliert. Plugin-
Interface ist als `typing.Protocol` mit `@runtime_checkable` umgesetzt, was
strukturelles Duck-Typing erlaubt und ABC-Inheritance erspart.

## Ausgefuehrte Befehle

```bash
# Sandbox (Implementation-Chat)
ruff check .                             # all clean
ruff format --check .                    # 10 files formatted
pytest tests/test_registry.py            # 16/16 PASS

# User-Maschine (echter Docker-Build)
cd infra
docker compose down
docker compose up --build
docker compose ps
```

## Output: pytest (16 Tests, Sandbox)

```
tests/test_registry.py::test_register_and_get_kem_happy_path PASSED
tests/test_registry.py::test_register_and_get_signature_happy_path PASSED
tests/test_registry.py::test_supported_kem_sorted PASSED
tests/test_registry.py::test_register_kem_duplicate_raises PASSED
tests/test_registry.py::test_register_signature_duplicate_raises PASSED
tests/test_registry.py::test_get_kem_unknown_raises PASSED
tests/test_registry.py::test_get_signature_unknown_raises PASSED
tests/test_registry.py::test_placeholder_kem_satisfies_kem_protocol PASSED
tests/test_registry.py::test_placeholder_signature_satisfies_signature_protocol PASSED
tests/test_registry.py::test_placeholder_kem_methods_raise_not_implemented PASSED
tests/test_registry.py::test_placeholder_signature_methods_raise_not_implemented PASSED
tests/test_registry.py::test_init_crypto_registry_registers_configured_algorithms PASSED
tests/test_registry.py::test_init_crypto_registry_supports_multiple_algorithms PASSED
tests/test_registry.py::test_init_crypto_registry_rejects_unknown_kem PASSED
tests/test_registry.py::test_init_crypto_registry_rejects_unknown_signature PASSED
tests/test_registry.py::test_init_crypto_registry_idempotency_check_via_duplicate PASSED

================ 16 passed in 0.06s ================
```

## Output: docker compose up --build (User-Maschine)

```
#19 [runtime 10/12] COPY crypto ./crypto
#19 DONE 0.1s
...
[+] up 5/5
 v Image rib-pqc-auth-service:dev Built  49.4s
 v Network pqc-net                Created
 v Container pqc-redis            Created
 v Container pqc-auth-service     Created
 v Container pqc-nginx            Created

pqc-auth-service | {"host": "0.0.0.0", "port": 8000, "log_level": "info",
  "event": "service.start", ...}
pqc-auth-service | {"kem": ["ML-KEM-768"], "kem_default": "ML-KEM-768",
  "signature": ["ML-DSA-65"], "signature_default": "ML-DSA-65",
  "event": "crypto.registry.initialized", "level": "info", ...}
pqc-auth-service | {"event": "Application startup complete.", ...}
pqc-auth-service | {"event": "Uvicorn running on http://0.0.0.0:8000 ...", ...}
Container pqc-auth-service Healthy
Container pqc-nginx Healthy
```

`crypto.registry.initialized`-Event ist neu und beweist dass die Registry
beim Service-Start tatsaechlich befuellt wird, nicht nur statisch ausgerollt.

## Output: docker compose ps

```
NAME               IMAGE                      COMMAND            STATUS
pqc-auth-service   rib-pqc-auth-service:dev   "python main.py"   Up (healthy)
pqc-nginx          nginx:1.27-alpine          ...                Up (healthy)
pqc-redis          redis:7-alpine             ...                Up (healthy)
```

## AC-Verifikation

| AC | Anforderung | Beweis |
|---|---|---|
| AC-1 | crypto/registry.py mit CryptoRegistry-Klasse plus register_kem und register_signature | `server/crypto/registry.py` enthaelt die Klasse mit beiden Methoden plus den Protocols `KemPlugin` und `SignaturePlugin`. Tests `test_register_and_get_kem_happy_path` und `test_register_and_get_signature_happy_path` PASS. |
| AC-2 | Registry erkennt Duplikate und wirft RegistryError | `DuplicateAlgorithmError(RegistryError)` Tests `test_register_kem_duplicate_raises` und `test_register_signature_duplicate_raises` PASS. |
| AC-3 | get_kem und get_signature liefern Plugin oder werfen AlgorithmNotFoundError | `AlgorithmNotFoundError(RegistryError)` Tests `test_get_kem_unknown_raises` und `test_get_signature_unknown_raises` PASS. |
| AC-4 | Init-Function liest Config und registriert alle in crypto.kem.supported / crypto.signature.supported aufgefuehrten Algorithmen | `init_crypto_registry` in `crypto/registry_init.py`. Im Container-Log sichtbar via `crypto.registry.initialized`-Event mit `kem=["ML-KEM-768"]`, `signature=["ML-DSA-65"]` aus `config.yaml`. Test `test_init_crypto_registry_registers_configured_algorithms` PASS. |
| AC-5 | Unit-Tests decken Happy-Path und Duplikat-Erkennung ab | 16 Tests im File `server/tests/test_registry.py`, 100 Prozent Pass-Rate. Deckung geht ueber AC-Minimum hinaus (auch Not-Found, Protocol-Konformitaet, Idempotenz, unbekannte Algorithmen). |

## Bewusste Design-Entscheidungen

- **Protocol statt ABC**: Plugin-Interface ist `typing.Protocol` mit
  `@runtime_checkable`. Plugin-Adapter (in PQC-25 LibOqsKem etc.) muessen
  lediglich die richtigen Methoden haben, kein Inheritance-Zwang. Modernes
  2026-Pattern, gute Decoupling-Story fuer den Bericht.
- **Placeholder-Plugins in Sprint 1**: `PlaceholderKem` und
  `PlaceholderSignature` werfen `NotImplementedError`. Das isoliert R-T01
  (liboqs-Build) komplett auf PQC-25. CRY-1 kann ohne liboqs-Container
  getestet werden und ist vollstaendig sandbox-tauglich.
- **NIST-Standard-Namen als einzige akzeptierte Algorithmus-Identifier**:
  `_SUPPORTED_KEM_ALGORITHMS` und `_SUPPORTED_SIGNATURE_ALGORITHMS` sind
  frozensets. Pre-Standard-Namen wie "Kyber768" oder "Dilithium3" werfen
  `UnsupportedAlgorithmError` (Test-Coverage vorhanden).
- **Crypto-Registry liegt in `app.state.crypto_registry`**: Nachfolgende
  Stories (CRY-2 Facade, AUT/TOK) ziehen den Singleton aus `app.state`,
  nicht aus dem globalen Modul. Saubere Lifecycle-Bindung.
- **Frischer Hatch-only-include-Eintrag**: `crypto` muss in pyproject.toml
  enthalten sein, sonst baut der editable-Wheel-Schritt im Dockerfile
  inkonsistent. Bereits angepasst.

## Im Review entdeckte und mitgefixte Findings

- **F-010 (Class-Konstante statt String-Literal)**: war ein Tier-2-Finding
  aus PQC-19. Beim Erweitern von `config.py` um die `CryptoConfig` habe ich
  die Konstante `_CONFIG_FILE_ENV: str = "RIB_CONFIG_FILE"` eingebaut und
  die Stelle, die vorher `os.environ.get("RIB_CONFIG_FILE")` rief, aufs
  Symbol umgestellt. Damit ist F-010 resolved. Inline-TODO in `config.py`
  wurde entfernt.

## Dockerfile-Anpassung in PQC-21

- `COPY crypto ./crypto` zu Schritt 3 hinzugefuegt
- pyproject.toml `only-include` um `"crypto"` erweitert (Konsistenz mit
  Hatch-Wheel-Build)

Senior-Engineer-Hinweis: Diese zwei Aenderungen waren NICHT in der initialen
Story-Planung. Sie wurden vor User-Test entdeckt durch die Lehre aus PQC-19
("vor User-Test alle Pfade pruefen die im Docker-Build anders sein koennen").

## Bewusste Limitationen

- **Keine echten Crypto-Operationen in CRY-1**: Per Design. Placeholder
  werfen `NotImplementedError`. PQC-25 (CRY-5) bringt die liboqs-Anbindung.
- **Keine Threadsafety**: Registry wird einmal beim Service-Start befuellt
  und danach read-only verwendet. Hot-Reload kein Use-Case in diesem Sprint.

## Quellen und Referenzen

- Jira: https://rumidesigns.atlassian.net/browse/PQC-21
- Story-Bezug: FR-Crypto-1, `docs/07_design.md` Abschnitte 6.1, 6.2, 6.3
- Implementation-Files:
  - `server/crypto/__init__.py` (neu)
  - `server/crypto/registry.py` (neu, 173 LOC)
  - `server/crypto/registry_init.py` (neu, 175 LOC)
  - `server/config.py` (erweitert um CryptoConfig)
  - `server/config.yaml` (neue crypto-Section)
  - `server/main.py` (lifespan ruft init_crypto_registry)
  - `server/tests/__init__.py` (neu)
  - `server/tests/test_registry.py` (neu, 16 Tests)
  - `server/Dockerfile` (COPY crypto/)
  - `server/pyproject.toml` (only-include crypto)
- Blocks-Links in Jira gesetzt: PQC-21 blockt PQC-22 (CRY-2 Facade) und
  PQC-32 (TOK-1 Broker-Token-Ausstellung).
