# Evidence: PQC-28 (AUT-1) - User-Store mit SQLAlchemy 2.0 und Argon2id

**Story:** PQC-28, AUT-1, "User-Store mit SQLAlchemy und SQLite"
**Sprint:** PQC Sprint 1 (23.05.2026 - 30.05.2026)
**Datum der Verifikation:** 28.05.2026
**Maschine:** Windows mit Docker Desktop, Git Bash (MINGW64)
**Verifiziert durch:** Dodoe (User), zusammen mit Implementation-Chat

## Was diese Evidence beweist

Der Auth-Service hat jetzt eine persistente User-Schicht:
- SQLite-Datenbank im persistierten `auth-data` Docker-Volume
- SQLAlchemy 2.0 async-API mit `Mapped[]`-Typing
- Alembic-Migrations mit idempotentem Auto-Apply beim Container-Start
- Argon2id-Password-Hashing mit Story-AC-4-Default-Parametern (m=64MB, t=3, p=4)
- UserRepository-Klasse mit Geschaeftsregel-Validierung (local-XOR-federated,
  Email-Normalisierung, Duplicate-Detection)
- PasswordHasher mit `verify`, `needs_rehash`, `dummy_verify` (AUT-4-vorbereitet)

Damit ist die Foundation fuer AUT-2 (Admin-CLI), AUT-3 (Login-Endpoint),
BRK-4 (Broker-Login mit federated users) gelegt.

## Ausgefuehrte Befehle (User-Maschine)

```bash
cd infra
docker compose down
docker compose up --build -d
docker compose logs auth-service --tail 60
docker compose exec auth-service python -c "..."  # End-to-End CRUD-Demo
```

## Output: Container-Logs (Lifespan-Init mit 3 neuen Events)

```json
{"event": "service.start", ...}
{"event": "crypto.registry.initialized", ...}
{"event": "crypto.signing_key.loaded", ...}
{"event": "crypto.facade.initialized", ...}
{"event": "token.service.initialized", ...}
{"event": "db.engine.created", "url": "sqlite+aiosqlite:////data/auth.sqlite", "echo": false, ...}
{"event": "password_hasher.initialized", "type": "argon2id", "memory_cost_kb": 65536, "time_cost": 3, "parallelism": 4, "salt_length": 16, "hash_length": 32, ...}
{"event": "db.session_factory.initialized", "async_url_scheme": "sqlite+aiosqlite", ...}
{"event": "Application startup complete.", ...}
```

**Wichtigster Beleg:** drei neue Events `db.engine.created`,
`password_hasher.initialized` und `db.session_factory.initialized` zeigen die
korrekte Lifespan-Sequenz mit den Story-AC-4 Argon2-Parametern.

Plus: implizit ausgefuehrte Alembic-Migration beim Container-Start
(CMD ist `sh -c "alembic upgrade head && python main.py"`). Bestaetigung
durch die Tatsache, dass das spaetere User-Insert funktioniert.

## Output: End-to-End CRUD-Demo (6 Szenarien)

```text
=== 1. Existierende Migration-Tabelle ===
  UserRepository instantiiert OK

=== 2. Local-User anlegen ===
{"user_id": "ae2e89f8-003a-4b24-91d0-79e162edecdb", "auth_method": "local", "external_sub_present": false, "event": "user.created", ...}
  created: id=ae2e89f8..., email=alice@example.com, hash_prefix=$argon2id$v=19$m=65536,t=3,p=4...

=== 3. find_by_email case-insensitive ===
  lowercase find: alice@example.com (ae2e89f8...)
  uppercase find: alice@example.com (ae2e89f8...)

=== 4. Argon2id Verify ===
  correct password: True
  wrong password: False

=== 5. Federated User anlegen ===
{"user_id": "1521faf5-...", "auth_method": "google", "external_sub_present": true, "event": "user.created", ...}
  created: id=1521faf5..., auth_method=google, external_sub=google|abc123

=== 6. Duplicate Email rejected ===
  OK rejected: user with email 'alice@example.com' already exists

ALL CRUD-DEMO SCENARIOS PASSED
```

## AC-Verifikation

| AC | Anforderung | Beweis |
|---|---|---|
| AC-1 | `models/user.py` definiert User-Model (id UUID, email unique, password_hash, auth_method, external_sub, created_at, updated_at) | Live-Demo Szenario 2: alle 7 Felder im erzeugten User-Record. Migration-File listet sie alle. |
| AC-2 | Alembic-Migration legt Tabelle an, DB ist im persistent Docker-Volume auth-data | `alembic/versions/65d6577e4bf6_initial_users_table.py` enthaelt `op.create_table('users', ...)`. Container-CMD ruft `alembic upgrade head` beim Start. DB-Datei in `/data/auth.sqlite` (=auth-data Volume). |
| AC-3 | Async-Repository-Pattern mit aiosqlite und SQLAlchemy 2.0 async API | `db/repositories/user_repository.py::UserRepository` nimmt `AsyncSession` per DI, alle Methoden `async def`. `db/engine.py` nutzt `create_async_engine` mit `sqlite+aiosqlite://`. Live-Demo zeigt async-Aufrufe gegen echten Container. |
| AC-4 | Argon2id-Parameter (m=64MB, t=3, p=4) in Konfiguration definiert | `config.py::Argon2Config` Defaults: `memory_cost_kb=65536` (=64MiB), `time_cost=3`, `parallelism=4`. `config.yaml` setzt sie explizit. Live-Log `password_hasher.initialized` zeigt diese Werte. |
| AC-5 | Unit-Tests: User anlegen, finden via email, password-hash-vergleich | 35 Tests in `tests/test_user_repository.py` (24 Tests) plus `tests/test_password.py` (11 Tests). Alle gruen im Sandbox (51 passed gesamt). |

Zusatzlich (ueber AC-5 hinaus):
- Geschaeftsregel-Validation: local-ohne-Hash, federated-mit-Hash, unsupported auth_method
- Email-Lowercase-Normalisierung im Repository
- Duplicate-Email case-insensitive (durch lowercase-stored)
- find_by_external fuer Broker-Lookups vorbereitet

## Code-Review-Findings (Closing-Review)

**0 Must, 0 neue Tier-1. 5 neue Tier-2-Findings:**

| ID | Titel | Severity | Tier |
|---|---|---|---|
| F-034 | email-Logging fehlt bei user.created (Privacy-by-Design vs Debug-Forensik) | Info | 2 |
| F-035 | DB-URL-Logging volle URL auf INFO (bei SQLite OK) | Info | 2 |
| F-037 | Dependency-Versions Minor-Floats moeglich, lockfile sichert reproducibility | Info | 2 |
| F-038 | dummy_verify als Methode vs FastAPI-Depends bei AUT-4 | Info | 2 |
| F-039 | PasswordHasher hat keinen Pepper (OWASP-Empfehlung fuer hochsicherheits-Setups) | Should | 2 |

F-012 (Health-Endpoint braucht DB-Ping) wird durch AUT-1 jetzt relevant aber
bleibt im bestehenden Tracking. F-036 ist Duplikat von F-012, daher entfallen.

Alle Findings in `docs/13_deferred_findings.md` getrackt.

## Bewusste Design-Entscheidungen

- **`Mapped[]`-Annotations + DeclarativeBase** statt klassischer `Column()`-Style: 2026-Standard, Python-Typing-First, ORM und mypy harmonisieren.
- **Sync-env.py** fuer Alembic statt async: Standard-Boilerplate, App bleibt async, Migration laeuft als kurzes Sync-Kommando. Alembic-Doku-konformer Weg.
- **UserRepository-Klasse** statt Module-Funktionen: konsistent mit TokenService/CryptoFacade-Pattern. Mocking via gleiche Klasse einfacher.
- **UUID-String** als Primary Key: portabel SQLite/Postgres, keine native-UUID-Column-Issues bei Migration.
- **Lowercase-Email-Normalisierung im Repository**, NICHT als DB-CHECK: SQLite Check-Constraint-Support limitiert; bei Postgres-Migration nachziehbar. Geschaeftsregel ist klar im Code.
- **`password_hash` nullable**: federated users (Google, Microsoft) haben keinen, lokales Passwort-Hash. Konsistent zu auth_method.
- **Pre-computed Dummy-Hash** als Modul-Konstante: einmal beim Modul-Load erzeugt, dann konstant pro Prozess. Vermeidet Random-Salt-Variation bei jedem dummy_verify-Call.
- **`server_default + python default`** doppelt fuer Timestamps: SQL-Side-Default UND Python-Side. Doppelt sicher gegen Migration-Drifts.
- **expire_on_commit=False** in async_sessionmaker: erlaubt Zugriff auf Attribute nach commit ohne lazy-load-Falle.
- **Argon2-Tuning aus Config**, nicht hardcoded: Story-AC-4-Werte sind sicherer als OWASP-2024-Default, aber bei "zu langsamem Login" runter-tunable ohne Code-Change.
- **Migration im Container-CMD**: `alembic upgrade head && python main.py` ist idempotent. Bei mehreren Replikas waere Race-Condition zu beachten (alembic hat advisory-locks), aber Sprint-1-Setup hat eine Replika.

## Bewusste Limitationen

- **email wird nicht bei user.created geloggt** (F-034) - bewusste Privacy-Wahl, bei AUT-3 Login-Debug-Forensik ggf. neu entscheiden.
- **Kein Pepper** (F-039) - OWASP-Polish vor Production.
- **Kein DB-Healthcheck-Ping** in /health (F-012) - kommt mit AUT-3.
- **Single-Replika-Setup** - Alembic-Race-Conditions waeren bei Multi-Replika neu zu beachten.
- **CHECK-Constraints nur im Code, nicht in DB** - Postgres-Migration kann das nachziehen.

## Files in dieser Story

- erweitert: `server/pyproject.toml` (sqlalchemy[asyncio], aiosqlite, alembic, argon2-cffi deps + only-include erweitert)
- erweitert: `server/config.py` (Argon2Config + DatabaseConfig)
- erweitert: `server/config.yaml` (argon2-section + database-section)
- neu: `server/models/__init__.py`, `server/models/base.py`, `server/models/user.py`
- neu: `server/db/__init__.py`, `server/db/engine.py`
- neu: `server/db/repositories/__init__.py`, `server/db/repositories/user_repository.py`
- neu: `server/auth/__init__.py`, `server/auth/password.py`
- erweitert: `server/main.py` (Lifespan: db_engine, session_factory, password_hasher in app.state)
- neu: `server/alembic.ini`, `server/alembic/env.py`, `server/alembic/script.py.mako`
- neu: `server/alembic/versions/65d6577e4bf6_initial_users_table.py`
- erweitert: `server/Dockerfile` (COPY models, db, auth, alembic, alembic.ini; CMD inklusive alembic upgrade head)
- neu: `server/tests/test_password.py` (11 Tests)
- neu: `server/tests/test_user_repository.py` (24 Tests)
- erweitert: `docs/13_deferred_findings.md` (PQC-28 Sektion mit F-034-F-039)
- neu: diese Evidence-Datei

## Folge-Tasks

- **PQC-29 (AUT-2 Admin-CLI):** kann jetzt UserRepository.create(email, password_hash, "local") aufrufen. Argon2-Hash via PasswordHasher.hash.
- **PQC-30 (AUT-3 Login):** kann jetzt UserRepository.find_by_email + PasswordHasher.verify zusammen ausfuehren. Plus TokenService.issue("local") nach Erfolg. Logging-Hardening-Bundle (F-021/F-026/F-031/F-034) vorab adressieren.
- **PQC-31 (AUT-4 Enumeration-Schutz):** kann PasswordHasher.dummy_verify() bei unbekannter Email aufrufen fuer Constant-Time-Response.
- **BRK-4:** kann find_by_external nutzen fuer federated-User-Lookup.

## Quellen und Referenzen

- Jira: https://rumidesigns.atlassian.net/browse/PQC-28
- Story-Bezug: FR-Auth-1, Design 5.3 (User-ERD)
- Vorgaenger (Done): PQC-19 (SKL-1), PQC-22 (CRY-2), PQC-32 (TOK-1), PQC-33 (TOK-2)
- SQLAlchemy 2.0 docs: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- argon2-cffi: https://argon2-cffi.readthedocs.io/
- OWASP Argon2 Cheatsheet 2024
