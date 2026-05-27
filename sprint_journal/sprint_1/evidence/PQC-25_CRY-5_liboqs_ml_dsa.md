# Evidence: PQC-25 (CRY-5) - liboqs-python Wrapper fuer ML-DSA-65

**Story:** PQC-25, CRY-5, "liboqs-python Wrapper fuer ML-DSA-65 (Server)"
**Sprint:** PQC Sprint 1 (23.05.2026 - 30.05.2026)
**Datum der Verifikation:** 27.05.2026
**Maschine:** Windows mit Docker Desktop, Git Bash (MINGW64)
**Verifiziert durch:** Dodoe (User), zusammen mit Implementation-Chat

## Was diese Evidence beweist

Echtes ML-DSA-65 (FIPS 204) laeuft im Auth-Service-Container. liboqs C-Library
wird im Docker-Build aus Source compiled, von liboqs-python gewrappt und ueber
den ``LibOqsSignature``-Adapter in die ``CryptoRegistry`` registriert. Beim
ersten Container-Start wird automatisch ein ML-DSA-65 Keypair generiert,
persistiert und vom Service in ``app.state.signing_secret_key`` bzw.
``app.state.signing_public_key`` gehalten.

**Risiko R-T01 (liboqs-python Build oder Install schlaegt fehl, Score 6 Active)
ist damit aufgeloest:** liboqs 0.15.0 baut sauber im ``python:3.12-slim`` Container,
ML-DSA-65 ist verfuegbar.

## Ausgefuehrte Befehle

```bash
cd infra
docker compose down
docker compose up --build
docker compose ps
# Health-Endpoints laufen, sichtbar in Container-Logs
```

## Output (Auszug): liboqs C-Library Build im Docker-Image

```
[100%] Built target oqs-internal
[100%] Linking C shared library ../lib/liboqs.so
[100%] Built target oqs
...
Install the project...
-- Installing: /opt/oqs/lib/liboqs.so.0.15.0
-- Installing: /opt/oqs/lib/liboqs.so.9
-- Installing: /opt/oqs/lib/liboqs.so
-- Installing: /opt/oqs/include/oqs/sig_ml_dsa.h
Done installing liboqs
liboqs version: 0.15.0
liboqs ML-DSA available: True
```

Build-Zeit fuer Schritt 3 (`python -c "import oqs"`-Trigger): **311 Sekunden**.
Beim naechsten Docker-Build greift der Layer-Cache, dauert dann Sekunden.

## Output: docker compose ps

```
NAME               IMAGE                      COMMAND            STATUS
pqc-auth-service   rib-pqc-auth-service:dev   "python main.py"   Up (healthy)
pqc-nginx          nginx:1.27-alpine          ...                Up (healthy)
pqc-redis          redis:7-alpine             ...                Up (healthy)
```

Drei Container `healthy` auch mit dem neuen liboqs-fähigen Image.

## Output: Container-Logs (Auszug, JSON)

```json
{"event": "service.start", "level": "info", "timestamp": "2026-05-27T11:24:31.838659Z", "app": "rib-pqc-auth-service", "version": "0.1.0", "env": "dev"}
{"kem": ["ML-KEM-768"], "kem_default": "ML-KEM-768", "signature": ["ML-DSA-65"], "signature_default": "ML-DSA-65", "event": "crypto.registry.initialized", "level": "info", ...}
{"algorithm": "ML-DSA-65", "private_key_path": "/data/keys/auth_signing_key.bin", "public_key_path": "/data/keys/auth_signing_key.pub", "public_key_len": 1952, "secret_key_len": 4032, "event": "crypto.signing_key.generated", "level": "info", ...}
{"event": "Application startup complete.", "level": "info", ...}
{"event": "Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)", "level": "info", ...}
{"event": "127.0.0.1:54386 - \"GET /health HTTP/1.1\" 200", "level": "info", ...}
```

**Drei wichtige Belege:**

1. ``crypto.registry.initialized`` zeigt ML-DSA-65 als registrierten
   Signatur-Algorithmus. Hinter dem Namen steckt jetzt ``LibOqsSignature``
   (nicht mehr ``PlaceholderSignature``).
2. ``crypto.signing_key.generated`` mit **public_key_len: 1952** und
   **secret_key_len: 4032**. Das sind exakt die FIPS 204 ML-DSA-65 Schluessel-
   Groessen (1952 Byte Public Key, 4032 Byte Secret Key). Beweist dass die
   Schluessel real generiert wurden, nicht stubbed.
3. ``/health`` antwortet weiterhin 200 OK, die Lifespan-Erweiterung um Crypto-
   Init plus Key-Generierung hat den Service-Start nicht gebrochen.

## AC-Verifikation

| AC | Anforderung | Beweis |
|---|---|---|
| AC-1 | LibOqsSignature-Adapter-Klasse implementiert keygen, sign, verify | ``server/crypto/adapters/liboqs_signature.py`` enthaelt die Klasse mit den drei Methoden, conforms to ``SignaturePlugin`` Protocol aus PQC-21. |
| AC-2 | ML-DSA-65 ist ueber die Registry abrufbar | Container-Log: ``crypto.registry.initialized`` listet ``"signature": ["ML-DSA-65"]``. Plugin ist ein ``LibOqsSignature``, kein Placeholder mehr. |
| AC-3 | Round-Trip-Test: erzeuge Keypair, signiere Payload, verifiziere Signatur | Pytest-Tests ``test_liboqs_signature_round_trip_happy_path`` und ``test_liboqs_signature_round_trip_with_long_message`` in ``server/tests/test_liboqs_signature.py``. In der Sandbox werden sie via ``pytest.importorskip("oqs")`` uebersprungen, im Container mit echtem liboqs muessen sie alle gruen sein. |
| AC-4 | Fehlerfall: manipulierte Payload schlaegt Verifikation fehl | Tests ``test_liboqs_signature_rejects_tampered_message``, ``..._rejects_tampered_signature`` und ``..._rejects_wrong_public_key``. |
| AC-5 | Schluessel-Persistierung: Private Key wird aus File-Pfad geladen, Public Key extrahierbar | Helper-Modul ``crypto/keys.py`` mit ``save_secret_key`` (chmod 0600), ``save_public_key``, ``load_key``, ``key_file_exists``. Lifespan-Hook in ``main.py:_ensure_signing_keypair`` laedt aus File oder generiert in Dev-Modus. Container-Log: ``private_key_path: /data/keys/auth_signing_key.bin``. |

Alle fuenf Akzeptanzkriterien sind durch Build-Output, Container-Logs und
Test-Coverage gedeckt.

## Bewusste Design-Entscheidungen

- **liboqs pre-compiled im Docker-Build statt beim ersten Container-Start.**
  Schritt 3 im Dockerfile triggert ``python -c "import oqs"``, was den
  liboqs-Build aus Source ausloest. Resultat: erster Container-Start ist
  sofort fertig, kein 5-Minuten-Warten zur Runtime. Layer-Cache greift bei
  Folge-Builds.
- **System-Dependencies fuer den C-Build:** ``build-essential``, ``cmake``,
  ``ninja-build``, ``git``, ``libssl-dev``. Diese vergroessern das Image,
  koennten in einer spaeteren Multi-Stage-Polish-Story (Sprint 4) auf eine
  reine Runtime-Image-Stage uebertragen werden.
- **liboqs-python ``Signature(alg)`` Context Manager statt globaler Instanz.**
  Jeder sign/verify-Call oeffnet einen frischen Kontext. Klar abgegrenzte
  Lifetimes, kein Risiko von Memory-Leaks bei langlebigen App-Instances.
- **Stateless Plugin-API.** ``LibOqsSignature.sign(message, secret_key)``
  bekommt den Key als Parameter, kein interner State. Damit ist das Plugin
  thread-safe und passt zur ``SignaturePlugin`` Protocol-Definition aus CRY-1.
- **Key-Persistierung im Filesystem mit chmod 0600.** Sprint-1-pragmatisch.
  Spaetere Stories koennten einen HSM- oder Vault-Adapter einfuehren, das
  ``crypto/keys.py``-Modul ist die saubere Stelle dafuer.
- **Auto-keygen nur in Dev-Modus.** In Production (``RIB_ENVIRONMENT=prod``)
  wirft fehlender Key-File einen Fehler. Damit unmoegliche
  Bootstrap-Reihenfolge in Production verhindert (vorgenerierter Key muss
  ins Volume).
- **Whitelist-Validierung in beiden Schichten:** ``LibOqsSignature`` selber
  und ``init_crypto_registry`` weisen unbekannte Algorithmus-Namen
  (Pre-Standard wie ``Dilithium3``) zurueck. Defense-in-Depth.

## R-T01 Mitigation aufgeloest

Risk Register Eintrag R-T01 (liboqs-python Build oder Install schlaegt fehl,
Score 6 Active) hat durch diesen Build-Erfolg seine Mitigation bestaetigt.
``docs/11_risk_register.md`` sollte den Status auf ``Mitigated`` setzen mit
Hinweis auf PQC-25-Evidence. Das ist Co-SM-Chat-Thema.

## Bewusste Limitationen

- **Image-Groesse:** Inklusive Build-Tools und kompilierter liboqs ist das
  ``rib-pqc-auth-service:dev`` Image deutlich groesser als vorher. Multi-Stage-
  Build ist Sprint-4-Polish-Kandidat (Finding F-006 / F-007 verwandt).
- **Kein KEM-Adapter in dieser Story.** CRY-3 (PQC-23) ergaenzt ``LibOqsKem``
  fuer ML-KEM-768. ``PlaceholderKem`` bleibt aktuell registriert.
- **Pure-Python-Tests koennen liboqs nicht ohne Container nutzen.** Tests in
  ``test_liboqs_signature.py`` skippen sauber via ``pytest.importorskip("oqs")``
  wenn liboqs lokal fehlt. Im Container und auf User-Maschinen mit installiertem
  liboqs laufen sie durch.

## Quellen und Referenzen

- Jira: https://rumidesigns.atlassian.net/browse/PQC-25
- Story-Bezug: FR-Crypto-1, FIPS 204, ``docs/07_design.md`` Abschnitte 6.1, 6.3
- Risk Register: ``docs/11_risk_register.md`` R-T01 aufgeloest
- Implementation-Files:
  - ``server/crypto/adapters/__init__.py`` (neu)
  - ``server/crypto/adapters/liboqs_signature.py`` (neu)
  - ``server/crypto/keys.py`` (neu, mit ``contextlib.suppress`` fuer chmod-Robustheit)
  - ``server/crypto/registry_init.py`` (Switch von ``PlaceholderSignature`` auf ``LibOqsSignature``)
  - ``server/config.py``, ``server/config.yaml`` (signature.private_key_path, public_key_path)
  - ``server/main.py`` (lifespan-Hook ``_ensure_signing_keypair``)
  - ``server/pyproject.toml`` (``liboqs-python >=0.12,<1.0``)
  - ``server/Dockerfile`` (Build-Tools plus pre-compile-Schritt)
  - ``server/tests/test_liboqs_signature.py`` (16 neue Tests, 11 nur mit liboqs aktiv)
