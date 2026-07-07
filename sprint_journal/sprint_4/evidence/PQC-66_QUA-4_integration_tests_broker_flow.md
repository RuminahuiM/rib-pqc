# Evidence PQC-66 QUA-4: Integration-Tests Broker-Flow

**Story:** PQC-66 (QUA-4)
**Datum:** 2026-07-07
**T-Shirt:** M | **SP:** 5 | **Sprint:** 4 (Carry-Over aus Sprint 3)

## Was wurde gebaut

`server/tests/test_integration_broker_flow.py` (539 Zeilen): 5 Integration-Tests für den kompletten OIDC-Broker-Flow (BRK-2 bis BRK-6). Mock-IdP via respx (Discovery-Doc plus Token-Endpoint), alle anderen Services ECHT: OidcStateService (fakeredis), OidcExchangeService (echter httpx), FederatedIdentityService (in-memory SQLite), TokenService mit echter ML-DSA-65-CryptoFacade (liboqs), IdpRegistry mit Test-Plugins deren `verify_id_token` injectable ist (RS256-JWKS-Verify ist separat in `test_id_token_verifier.py` gedeckt).

Dazu Test-Runner-Infrastruktur, damit die liboqs-abhängigen Tests reproduzierbar laufen:

- `server/Dockerfile`: neuer Multi-Stage-Target `test` (erbt von `runtime`, ergänzt dev-Deps plus `tests/`).
- `infra/docker-compose.yml`: Service `auth-service-test` (Profile `test`, one-shot pytest-Runner, depends_on redis).

## Tests

1. Google Full-Flow: authorize → callback → User created plus Broker-Token (JWS-Compact, 3 Segmente).
2. Microsoft Full-Flow mit tid-Check (Single-Tenant Defense, RFC 9700 4.6).
3. Existing-User-Link: zweiter Login mit gleichem external_sub erzeugt KEINEN neuen User.
4. Unknown State → 400 `invalid_state`.
5. IdP-Token-Endpoint 400 → 400 `code_exchange_failed`.

## Verifikation

```bash
cd infra
docker compose build auth-service-test
docker compose run --rm auth-service-test
# 420 passed, 0 failed in 22.85s (voller Suite-Run im Container, liboqs echt)
```

## Abweichungen und Debug-Historie (07.07.2026)

- **F-145 (Test-Infra):** `uv sync` ohne Flags installiert `[project.optional-dependencies].dev` NICHT (nur PEP-735 dependency-groups). Test-Image hatte kein pytest. Fix: `uv sync --extra dev` im Dockerfile-test-Stage.
- **Test-Erwartungs-Fixes nach erstem Container-Run:** (a) Authorize-Endpoint verlangt `code_verifier` zwingend (BFF-Pattern, RFC 7636 43-128 chars), Test-Konstante `TEST_CODE_VERIFIER` ergänzt. (b) `invalid_state` ist 400, nicht 401 (Router-Konvention, konsistent mit `test_callback_state_mismatch_returns_400`). (c) IdP-Exchange-Fehler mappt auf `code_exchange_failed`, nicht `provider_error`.
- **Beifang, weil der Container-Run die Sandbox-Skips aufgehoben hat:** F-143 (Timing-Oracle im Enumeration-Schutz) und F-144 (case-insensitive alg-Allowlist scheitert an case-sensitiver CryptoRegistry). Beide in-Session gefixt, Details in `docs/13_deferred_findings.md`.

## Bezug

- Requirements: `docs/05_requirements.md` (BRK-Block), Traceability: `docs/12_traceability_matrix.md`.
- Jira: [PQC-66](https://rumidesigns.atlassian.net/browse/PQC-66).
