# Evidence: PQC-63 QUA-1 Pytest-Setup

- **Jira**: [PQC-63](https://rumidesigns.atlassian.net/browse/PQC-63)
- **Sprint**: 1 (Endspurt)
- **Done am**: 2026-05-30
- **Story Points**: 1
- **Worklog**: ~30 Minuten

## Zusammenfassung

Formales Pytest-Setup mit Coverage-Reporting. pytest-cov als dev-dep ergaenzt,
`tests/conftest.py` mit Hybrid-Scope angelegt (Shared Fixtures fuer DB/Auth,
Top-Level-Env-Vars damit Module-level Limiter ohne Redis instantiierbar ist),
Coverage-Konfiguration im pyproject.toml. Default-Pytest-Run liefert
term-missing und HTML-Coverage-Reports.

## AC-Mapping

| AC | Resultat |
|---|---|
| AC-1 (pytest+pytest-asyncio+httpx als deps) | OK: alle drei vorhanden, pytest-cov >=5.0,<7.0 ergaenzt |
| AC-2 (conftest.py mit TestClient-Fixture) | OK: `client_factory`, plus shared `async_engine`, `session_factory`, `async_session`, `fast_hasher` |
| AC-3 (pytest gruen) | OK: 104 passed, 4 skipped (liboqs-Sandbox-Skips, erwartet) |
| AC-4 (pytest-cov konfiguriert) | OK: `[tool.coverage.run].branch=true`, exclude_lines, HTML + term-missing |

## Files

- `server/pyproject.toml`:
  - `pytest-cov >=5.0,<7.0` in `project.optional-dependencies.dev` und `tool.uv.dev-dependencies`
  - `[tool.pytest.ini_options].addopts` um `--cov=.`, `--cov-report=term-missing:skip-covered`, `--cov-report=html` erweitert
  - `[tool.coverage.run]`: `branch=true`, `source=["."]`, `omit=tests/alembic/...`
  - `[tool.coverage.report]`: `exclude_lines` fuer TYPE_CHECKING / Boilerplate, `show_missing=true`, `precision=1`
  - `[tool.coverage.html]`: `directory="htmlcov"`
- `server/tests/conftest.py` (NEU, 146 Zeilen):
  - Top-Level: `os.environ.setdefault(...)` fuer `RIB_SECURITY__RATE_LIMIT__STORAGE_URI`, `RIB_SECURITY__RATE_LIMIT__ENABLED`, `RIB_ENVIRONMENT`
  - DB-Fixtures: `async_engine` (in-memory SQLite + Schema), `session_factory`, `async_session`
  - Auth-Fixture: `fast_hasher` (Argon2id mit niedrigen Cost-Params fuer Test-Speed)
  - Helper: `client_factory` (Generic TestClient-Wrapper)
- `server/main.py`: F-048-Section in `_run()` Docstring nach Edit-Tool-Truncation neu geschrieben (saubere Datei mit korrektem `_run()`-Body + `__main__`-Guard)

## Sandbox-Verifikation

```
============================= test session starts ==============================
collected 104 items / 4 skipped

tests/test_admin.py ..............                                       [ 13%]
tests/test_password.py .............                                     [ 25%]
tests/test_rate_limit.py ........                                        [ 33%]
tests/test_registry.py ................                                  [ 49%]
tests/test_request_id_middleware.py ..............                       [ 62%]
tests/test_security_middlewares.py .................                     [ 78%]
tests/test_user_repository.py ......................                     [100%]

================================ tests coverage ================================
Name                                  Stmts   Miss Branch BrPart  Cover
---------------------------------------------------------------------------------
admin.py                                100     22     18      4  76.3%
config.py                               108      8      6      2  91.2%
crypto/adapters/liboqs_signature.py      30     18      2      1  40.6%
crypto/facade.py                         45     32      4      0  26.5%
crypto/keys.py                           23     15      4      0  29.6%
db/engine.py                             28     19      6      0  26.5%
logging_config.py                        30     21      2      0  28.1%
main.py                                  93     93     10      0   0.0%
models/user.py                           21      1      0      0  95.2%
routers/auth.py                          45     20      4      0  51.0%
routers/dev_test.py                       9      9      0      0   0.0%
routers/health.py                        12     12      0      0   0.0%
services/token_service.py               153    127     44      0  13.2%
---------------------------------------------------------------------------------
TOTAL                                   975    397    140      7  57.0%

17 files skipped due to complete coverage.
Coverage HTML written to dir htmlcov
======================== 104 passed, 4 skipped in 2.38s ========================
```

**Notiz zum Coverage-Wert:** 57% Sandbox ist ein Untergrenz-Wert wegen
liboqs-Skips (test_token_service, test_facade, test_auth_router, test_liboqs_signature
ueberspringen alle in der Sandbox). In Docker mit liboqs laufen diese Tests,
und Coverage steigt auf vermutlich 70-75%. Die niedrigen Werte bei
`services/token_service.py` (13%), `crypto/facade.py` (26%), `crypto/keys.py`
(30%) sind direkt durch die Skips erklaerbar.

## Senior-Decisions

1. **conftest.py-Scope: Hybrid** (statt minimal): User-Wunsch "kein Zeitsparen mehr im Sprint". Shared Fixtures (DB, Auth-Hasher, Helper) landen zentral, test-spezifische bleiben pro Datei.
2. **Coverage-Report-Format: term-missing + HTML**: term-missing zeigt unkovered Zeilen direkt im Terminal, HTML in `htmlcov/` fuer Detail-Lookup (in .gitignore).
3. **Kein fail_under-Gate in Sprint 1**: Sandbox-Skips durch liboqs machen einen harten Threshold instabil. Threshold wird in Sprint 4 (Doku-Polish) nach Coverage-Stabilisierung gesetzt.

## Findings

| ID | Titel | Severity | Status |
|---|---|---|---|
| F-050 | `main.py`, `routers/health.py`, `routers/dev_test.py` haben 0% Unit-Test-Coverage (nur Live-Tests). Lifespan-Hook ist schwer unit-test-bar, health und dev_test sind sauber testbar mit TestClient | Info | open (Tier-2 Polish, Sprint 4) |

Nebenfund: pyproject.toml und main.py wurden vom Edit-Tool wiederholt
truncated. Per heredoc neu geschrieben, AST-Parse-Check anschliessend gruen.
Tool-Bug, kein Code-Bug.

## Aufwand

- conftest.py + Hybrid-Fixtures: 10min
- pyproject.toml Coverage-Config: 5min
- Sandbox-Verifikation + Edit-Tool-Reparatur (main.py truncation): 10min
- Closing-Review + Evidence: 5min
- **Total: ~30min**
