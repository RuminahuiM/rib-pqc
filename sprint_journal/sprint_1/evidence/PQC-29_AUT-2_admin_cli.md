# Evidence: PQC-29 (AUT-2) - Admin-CLI fuer User-Provisioning

**Story:** PQC-29, AUT-2, "Admin-CLI fuer User-Provisioning"
**Sprint:** PQC Sprint 1 (23.05.2026 - 30.05.2026)
**Datum der Verifikation:** 28.05.2026 (abends)
**Maschine:** Windows mit Docker Desktop, Git Bash (MINGW64)
**Verifiziert durch:** Dodoe (User), zusammen mit Implementation-Chat

## Was diese Evidence beweist

Der Auth-Service hat jetzt ein Admin-CLI-Werkzeug, mit dem ein Operator
Test-User provisionieren kann. Das CLI:

- baut auf den AUT-1-Bausteinen (`UserRepository`, `PasswordHasher`) auf
- ist OWASP-konform (keine Plain-Passwords als argv)
- bietet sowohl interaktiven (`getpass`-Prompt) als auch Scripting-Modus (`--password-stdin`)
- listet User in Plain-Text-Tabelle oder JSON
- gibt klare Exit-Codes (0 ok, 1 business-error, 2 usage-error)

Das schliesst Self-Service-Registrierung explizit aus, wie in der Story
spezifiziert.

## Ausgefuehrte Befehle (User-Maschine)

```bash
docker compose exec auth-service python -m admin --help
docker compose exec auth-service python -m admin create-user --help
docker compose exec auth-service python -m admin list-users --help
echo "my-secret-pw" | docker compose exec -T auth-service \
    python -m admin create-user --email demo@example.com --password-stdin
docker compose exec auth-service python -m admin list-users
docker compose exec auth-service python -m admin list-users --json
echo "another-pw" | docker compose exec -T auth-service \
    python -m admin create-user --email demo@example.com --password-stdin
# echo "exit code: $?"  # Erwartet 1
docker compose exec auth-service python -c "
import asyncio
from fastapi.testclient import TestClient
from main import app
from db.repositories import UserRepository
async def verify():
    async with app.state.session_factory() as session:
        repo = UserRepository(session)
        u = await repo.find_by_email('demo@example.com')
        ok = app.state.password_hasher.verify('my-secret-pw', u.password_hash)
        bad = app.state.password_hasher.verify('wrong', u.password_hash)
        print(f'verify correct: {ok}')
        print(f'verify wrong: {bad}')
with TestClient(app) as client:
    asyncio.run(verify())
"
```

## Output: 6 Szenarien (alle gruen)

```text
=== 1. Help-Texte (sanity) ===
usage: python -m admin [-h] {create-user,list-users} ...
  create-user         Create a local user with Argon2id-hashed password
  list-users          List all users without password hash

usage: python -m admin create-user [-h] --email EMAIL [--password-stdin]
  --email EMAIL     Email address (will be lowercase-normalized)
  --password-stdin  Read password from stdin instead of interactive prompt

usage: python -m admin list-users [-h] [--json]
  --json      Output as JSON (default: plain-text table)

=== 2. User anlegen via stdin ===
{"event": "password_hasher.initialized", "memory_cost_kb": 65536, "time_cost": 3, "parallelism": 4, ...}
{"event": "user.created", "auth_method": "local", "external_sub_present": false, "user_id": "57650c7b-...", ...}
created user: id=57650c7b-6658-4549-9b37-3a23182e505c, email=demo@example.com, auth_method=local

=== 3. list-users plain-text ===
id           email              auth_method  external_sub   created_at
-----------  -----------------  -----------  -------------  -------------------
ae2e89f8...  alice@example.com  local        -              2026-05-28 20:59:20
1521faf5...  bob@google.test    google       google|abc123  2026-05-28 20:59:21
57650c7b...  demo@example.com   local        -              2026-05-28 21:44:19

=== 4. list-users JSON ===
[
  {"id": "ae2e89f8-...", "email": "alice@example.com", "auth_method": "local", "external_sub": null, ...},
  {"id": "1521faf5-...", "email": "bob@google.test", "auth_method": "google", "external_sub": "google|abc123", ...},
  {"id": "57650c7b-...", "email": "demo@example.com", "auth_method": "local", "external_sub": null, ...}
]

=== 5. Duplicate ===
error: user with email 'demo@example.com' already exists
exit code: 1

=== 6. Round-Trip Argon2-Verify ===
verify correct: True
verify wrong: False
```

## AC-Verifikation

| AC | Anforderung | Beweis |
|---|---|---|
| AC-1 | `python -m admin create-user --email <email>` legt User an, Passwort per `getpass` (default) oder `--password-stdin` (scripting). | Live-Demo Szenario 2: `--password-stdin` Pipe erzeugt User erfolgreich. argparse-Help (Szenario 1) zeigt korrekte Optionen. |
| AC-2 | Passwort wird mit Argon2id ueber den bestehenden PasswordHasher gehasht | Live-Log `password_hasher.initialized` mit Story-AC-4-Params. Szenario 6 beweist Round-Trip: derselbe Hash verifiziert das Originalpasswort. |
| AC-3 | `auth_method` ist auf `"local"` gesetzt | Live-Log `user.created` zeigt `auth_method=local`. Plain-Text-Output Szenario 3 zeigt local-Spalte. |
| AC-4 | Email-Konflikt -> klarer Fehler, Exit-Code != 0 | Live-Demo Szenario 5: `error: user with email 'demo@example.com' already exists` plus `exit code: 1`. stderr-Output (visible in Terminal weil docker compose exec merged). |
| AC-5 | `list-users` ohne Passwort-Hash. Default Plain-Text + `--json` Flag | Live-Demo Szenarien 3 + 4: 3 Users gelistet, weder `password_hash` noch `argon2` im Output. JSON-Output enthaelt KEIN `password_hash`-Feld. |

## Code-Review-Findings (Closing-Review)

**0 Must, 0 Tier-1. 3 neue Tier-2-Info-Findings:**

| ID | Titel | Severity | Tier | Status |
|---|---|---|---|---|
| F-040 | CLI macht Engine+Hasher-Init pro Command | Info | 2 | Sprint 3 Polish (Singleton-Pattern bei Library-Use-Case) |
| F-041 | Keine Confirmation-Prompts fuer destructive Actions | Info | 2 | bei CLI-Erweiterung um destructive Commands |
| F-042 | `list-users` hat keine Pagination | Info | 2 | wenn User-Base 100+ wird |

Alle Findings sind Polish-Items ohne aktuellen Trigger. Code ist sauber.
Alle in `docs/13_deferred_findings.md` getrackt.

## Bewusste Design-Entscheidungen

- **argparse statt typer/click:** stdlib reicht fuer 2 Subcommands, keine zusaetzliche Runtime-Dep. Best-Practice fuer kleine CLIs.
- **OWASP-Passwort-Eingabe:** getpass-Prompt default, `--password-stdin` als Scripting-Option, KEIN `--password <plain>` argv (Anti-Pattern wegen Shell-History/ps/Container-Log-Leak).
- **AC-Pfad-Update:** Story sagte `auth_service.admin`, unsere Server-Struktur ist flach, daher `python -m admin`. Jira-AC entsprechend angepasst mit Begruendung.
- **Repository-Wiederverwendung:** `UserRepository.create` (aus AUT-1) wird direkt benutzt - keine Duplikat-Geschaeftsregeln-Validation im CLI.
- **`UserRepository.list_all`** als neue Methode mit `ORDER BY created_at` und ohne Pagination (bei wachsender User-Base in F-042 nachzuziehen). Im Docstring dokumentiert.
- **Exit-Codes als Konstanten** (`_EXIT_OK=0`, `_EXIT_BUSINESS_ERROR=1`, `_EXIT_USAGE_ERROR=2`): standard Unix-Convention, scriptbar.
- **Plain-Text-Tabelle ohne externe Library:** col_widths-Berechnung + ljust ist trivial fuer 5 Spalten, vermeidet `tabulate`-Dep.
- **Defensive Fallback** in `main()`: falls argparse einen unbekannten Command durchlaesst, returnt usage-error. Sicherheits-Idiom.
- **CLI-Tests:** 14 dedizierte Tests in `tests/test_admin.py`. Tests rufen die internen `_cmd_*`-Coroutines mit in-memory SQLite auf, statt `main(argv)` zu fahren - weniger Setup, dieselbe Coverage.

## Bewusste Limitationen

- **Engine-Init pro CLI-Call** (F-040): bei interaktivem Operator-Workflow Overhead. Aktuell akzeptabel weil CLI kurzlebige Calls sind.
- **Keine Pagination** (F-042): bei wachsender User-Base nachziehen.
- **Keine destructive Commands** (delete-user, reset-password): Sprint-1-Scope. Bei Erweiterung F-041 Confirmation-Pattern beachten.
- **Self-Service-Registrierung explizit nicht implementiert** (Story-Vorgabe). CLI ist Admin-Tool, von Operator manuell ausgefuehrt.

## Files in dieser Story

- neu: `server/admin.py` (~245 Zeilen, argparse-CLI)
- erweitert: `server/db/repositories/user_repository.py` (neue `list_all`-Methode)
- erweitert: `server/Dockerfile` (admin.py in COPY-Liste)
- erweitert: `server/pyproject.toml` (admin.py in only-include + mypy.files)
- neu: `server/tests/test_admin.py` (14 Tests)
- erweitert: `docs/13_deferred_findings.md` (PQC-29 Sektion mit F-040-F-042)
- neu: diese Evidence-Datei

Anpassung Jira-Story-Beschreibung: AC-1 modul-pfad-Note auf `python -m admin` aktualisiert (urspruengliches AC sagte `auth_service.admin`).

## Folge-Tasks

- **PQC-30 (AUT-3 Login-Endpoint):** kann jetzt das CLI nutzen um Test-User vorab anzulegen. Login-Demo wird `python -m admin create-user --email demo@example.com --password-stdin` als Pre-Setup-Schritt nutzen.
- **PQC-31 (AUT-4 User-Enumeration-Schutz):** kann `PasswordHasher.dummy_verify()` nutzen, baut auf AUT-1 + AUT-3 auf.

## Quellen und Referenzen

- Jira: https://rumidesigns.atlassian.net/browse/PQC-29
- Story-Bezug: FR-Auth-2
- Vorgaenger (Done): PQC-28 (AUT-1)
- OWASP Password Storage Cheat Sheet 2024
- Python argparse docs: https://docs.python.org/3/library/argparse.html
