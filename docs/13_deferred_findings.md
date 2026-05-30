# Deferred Findings

**Projekt:** Implementing PQC (Semesterarbeit 3, ITCNE25)
**Autor:** Dodoe Rumiñahui Mannale
**Erstellt:** 25.05.2026
**Status:** Initial-Version (v1.0)

**Bezug:** Tier-2-Tracking-Liste fuer Code-Review-Findings, die bewusst nicht
sofort gefixt wurden. Komplement zu Jira (Tier 1, konkrete Stories mit Story-
Dependency) und zu `11_risk_register.md` (Tier 2 fuer echte Projekt-Risiken).

## Wie diese Liste funktioniert

- Findings entstehen typischerweise in Code-Reviews am Story-Ende.
- Jedes Finding bekommt eine ID (F-NNN), Severity, Trigger und Status.
- **Trigger** beschreibt wann das Finding adressiert werden soll. Beispiele:
  "vor PQC-30", "Sprint 4 Polish", "vor Bericht-Abgabe", "bei Touch dieses Files".
- Die Story-Start-Checklist im Implementation-Chat-Memory verpflichtet mich,
  diese Liste bei jeder neuen Story zu konsultieren wenn der Story-Scope einen
  hier gelisteten Bereich beruehrt.
- Status: `open` = noch offen, `in-progress` = in einer laufenden Story, `resolved` = erledigt.
- Findings die zu konkreten Jira-Stories werden, behalten ihren Eintrag hier
  mit Status `resolved` und Verweis auf die Jira-Story die sie geschlossen hat.

## Findings aus PQC-19 (SKL-1) Code-Review am 25.05.2026

### Tier-1 (haben oder bekommen Jira-Story, deshalb hier nur Verweis)

| ID | Titel | Severity | Trigger | Jira | Status |
|---|---|---|---|---|---|
| F-001 | Request-ID-Middleware fehlt | Should | vor PQC-30 | [PQC-79](https://rumidesigns.atlassian.net/browse/PQC-79) | tracked-in-jira |
| F-002 | CORS-Middleware nicht konfiguriert | Should | vor PQC-30 | [PQC-80](https://rumidesigns.atlassian.net/browse/PQC-80) | tracked-in-jira |
| F-003 | TrustedHost-Middleware nicht konfiguriert | Should | vor PQC-30 | [PQC-81](https://rumidesigns.atlassian.net/browse/PQC-81) | tracked-in-jira |
| F-004 | Security-Headers-Middleware fehlt | Should | vor PQC-30 | [PQC-82](https://rumidesigns.atlassian.net/browse/PQC-82) | tracked-in-jira |
| F-005 | Rate-Limiting-Infrastruktur fehlt | Should | vor PQC-30, spaetestens vor produktiver Demo | [PQC-83](https://rumidesigns.atlassian.net/browse/PQC-83) | tracked-in-jira |

### Tier-2 (Polish, Code-Hygiene, keine eigene Story)

| ID | Titel | Severity | Trigger | Status |
|---|---|---|---|---|
| F-006 | Docker-Images mit Tags statt Digests gepinnt | May | Sprint 4, vor Bericht-Abgabe | open |
| F-007 | curl im Auth-Service-Image installiert, aber nicht zwingend genutzt | May | Sprint 4 Image-Slim | open |
| F-008 | `fastapi[standard]` zieht `fastapi-cloud-cli` mit (unbenoetigt) | May | Sprint 4 Image-Slim, vor Bericht | open |
| F-009 | `/docs` und `/openapi.json` ohne Flag immer offen | May | vor produktiver Demo | open |
| F-010 | `os.environ.get("RIB_CONFIG_FILE")` als String-Literal in config.py | Info | bei naechstem Config-Touch | resolved (PQC-21, Class-Konstante `_CONFIG_FILE_ENV`) |
| F-011 | Tech-Stack-Doku-Versionen drift (structlog 25.x installed vs Doku "24.x+") | Info | Sprint 4 Doku-Polish | open |
| F-012 | NFR-Ops-3 Health-Endpoint braucht uptime/registry/503-Cases | Should | wenn Redis und SQLite live eingebaut werden (AUT-1, Session-Stories) | open |
| F-013 | Access-Log koennte sensitive Daten (Email im Path/Query) leaken | Should | vor PQC-30 AUT-3, Filtering einbauen | open (inline TODO in main.py) |

## Historie

| Version | Datum | Aenderung |
|---|---|---|
| 1.0 | 25.05.2026 | Initial. 13 Findings aus PQC-19 SKL-1 Review. |


## Historie-Update 25.05.2026 abends

Tier-1-Findings F-001 bis F-005 sind als Jira-Stories unter dem neuen Epic
[PQC-78 EPIC SEC: Security Infrastructure](https://rumidesigns.atlassian.net/browse/PQC-78) angelegt:

| Finding | Story | Titel | Story Points |
|---|---|---|---|
| F-001 | [PQC-79](https://rumidesigns.atlassian.net/browse/PQC-79) | SEC-1 Request-ID Middleware | 2 |
| F-002 | [PQC-80](https://rumidesigns.atlassian.net/browse/PQC-80) | SEC-2 CORS-Middleware | 2 |
| F-003 | [PQC-81](https://rumidesigns.atlassian.net/browse/PQC-81) | SEC-3 TrustedHost-Middleware | 1 |
| F-004 | [PQC-82](https://rumidesigns.atlassian.net/browse/PQC-82) | SEC-4 Security-Headers | 2 |
| F-005 | [PQC-83](https://rumidesigns.atlassian.net/browse/PQC-83) | SEC-5 Rate-Limiting | 3 |

Alle fuenf Stories haben einen "Blocks PQC-30 (AUT-3)"-Issue-Link in Jira.
Sprint-Label ist `sprint-2`. Finale Sprint-Zuteilung obliegt dem PM-Agent /
Co-SM-Chat.


## Findings aus PQC-25 (CRY-5) Code-Review am 25.05.2026

Keine Tier-1-Findings (alle Should-Items waren mit kleinem Aufwand fixbar oder
schon abgedeckt). 7 Tier-2-Findings, 1 davon noch in der Story selbst gefixt.

### Tier-2 (Polish, Code-Hygiene, keine eigene Story)

| ID | Titel | Severity | Trigger | Status |
|---|---|---|---|---|
| F-014 | Secret Key lebt als bytes-Objekt im Python-Memory ueber Service-Lifetime | Should | vor produktiver Demo, Bericht-Limitation | open (Pure-Python-Limitation, im Bericht erwaehnen) |
| F-015 | LibOqsSignature.verify faengt zu breit (except Exception -> False) | Info | bei naechstem Touch von liboqs_signature.py | resolved (PQC-22, eng auf (RuntimeError, ValueError) eingegrenzt) |
| F-016 | Dev-Setup-Doku: liboqs-python braucht Internet beim ersten Import | Info | Sprint 4 Doku-Polish | open |
| F-017 | Docker-Image enthaelt Build-Tools (gcc, cmake, ninja-build, git, libssl-dev) im Runtime | May | Sprint 4, Multi-Stage-Build mit Bericht-Gewinn | open |
| F-018 | liboqs C-Source-Download im Build nicht hash-gepinnt (Supply-Chain-Reproducibility) | May | Sprint 4, vor Bericht-Abgabe | open |
| F-019 | Tech-Stack-Doku Abschnitt 2.3 sagt liboqs-python 0.10+, installiert ist 0.12+ | Info | Sprint 4 Doku-Polish (mit F-011 buendeln) | open |
| K-3 (war Should) | Auto-Keygen erforderte nur environment=dev, ohne expliziten zweiten Flag | Should | bei naechstem Touch | resolved (PQC-25, neues Feld crypto.signature.allow_autogen_in_dev, doppelter Flag-Check in _ensure_signing_keypair) |

### Historie-Update 25.05.2026 abends-spaet

Findings F-014 bis F-019 plus K-3-Resolution aus dem Senior-Closing-Review von
PQC-25 (CRY-5) ergaenzt. R-T01 (Risk Register) ist durch PQC-25 erfolgreich
gemitigated, sollte vom Co-SM-Chat im Risk Register entsprechend dokumentiert
werden.



## Findings aus PQC-22 (CRY-2) Code-Review am 27.05.2026

Story war ein Skeleton-Sprint mit klar definierten AC. Im Closing-Review nur
ein neues Finding plus ein bestehendes geloest.

### Tier-2 (Polish, Code-Hygiene, keine eigene Story)

| ID | Titel | Severity | Trigger | Status |
|---|---|---|---|---|
| F-020 | CryptoFacade.sign purpose-Parameter wird Sprint 1 nur geloggt, nicht semantisch verarbeitet | Info | wenn zweiter sign-Use-Case (z.B. Session-Handshake) oder Keys-pro-Purpose noetig | open (in Doku festgehalten, Facade-API tauglich fuer Erweiterung) |
| F-021 | CryptoFacade.sign/verify loggen jeden Call auf INFO-Level | Should | vor PQC-30 oder vor produktiver Demo, wenn Token-Flow hochfrequent wird | open (auf DEBUG-Level oder Sampling reduzieren) |
| F-022 | crypto.facade.verify loggt result True/False pro Call (Side-Channel-Concern via Log-Aggregator) | Info | vor produktiver Demo, mit F-021 zusammen abhandeln | open |
| F-023 | Single-kid-Setup, Multi-Key-Pflege fuer Key-Rotation noch nicht implementiert | Info | Sprint 3 Polish, oder bei JWKS-Endpoint-Bedarf | open |
| F-024 | app.state.crypto_facade ist untyped; FastAPI-Dependency-Helper waere type-safer | Info | bei PQC-30 (AUT-3) wenn erster Endpoint die Facade nutzt | open |
| F-015 (war Info) | LibOqsSignature.verify faengt zu breit | Info | bei naechstem Touch | resolved (PQC-22, siehe oben) |

### Historie-Update 27.05.2026

PQC-22 Closing-Review: F-015 in der Story selbst geloest (Exception-Klausel
eingegrenzt). Vier neue Tier-2-Findings F-020 bis F-024:
- F-020: purpose-Parameter funktional inaktiv in Sprint 1
- F-021: Log-Frequency auf sign/verify (Should, vor PQC-30)
- F-022: verify-result-Logging (Info, mit F-021 zusammen)
- F-023: Multi-Kid-Rotation (Sprint 3 Polish)
- F-024: Typed app.state-Helper (bei PQC-30)


## Findings aus PQC-32 (TOK-1) Code-Review am 28.05.2026

Story war Broker-Token-Ausstellung im JWS-Compact-Format mit ML-DSA-65.
Acceptance Criteria 1-5 alle in Live-Container-Demo verifiziert. Eine
Should-Finding hat einen klaren Story-Trigger (PQC-33 TOK-2 AC-Erweiterung),
die uebrigen Tier-2-Polish.

### Tier-1 (haben oder bekommen Jira-Story)

| ID | Titel | Severity | Trigger | Jira | Status |
|---|---|---|---|---|---|
| F-028 | alg-Allowlist-Check (RFC 8725 BCP gegen alg-confusion und alg=none) | Should | direkt in PQC-33 (TOK-2) AC aufnehmen | [PQC-33](https://rumidesigns.atlassian.net/browse/PQC-33) | to-add-to-PQC-33-AC |

### Tier-2 (Polish, Code-Hygiene, keine eigene Story)

| ID | Titel | Severity | Trigger | Status |
|---|---|---|---|---|
| F-025 | `AuthMethod` Literal deklariert aber `issue()` nutzt `str` plus Runtime-Whitelist | Info | bei naechstem Touch von token_service.py | open |
| F-026 | `sub`-Claim wird auf INFO-Level pro Issue geloggt (Privacy plus Volume bei AUT-3) | Should | vor PQC-30, mit F-021 buendeln | open |
| F-027 | Kein `jti` (JWT ID) im Token, RFC 8725 BCP empfiehlt fuer Replay-Protection | May | vor produktiver Demo wenn Replay-Risiko relevant | open |
| F-029 | `python -c "from main import app"` ohne TestClient triggert FastAPI-Lifespan nicht. docker-exec-Demos brauchen TestClient-Wrapper oder manuelle Lifespan-Rekonstruktion. | Info | Memory-Update in pqc-demo-convention | open (auch Tier 3) |
| F-030 | server/README.md erwaehnt das neue `services/`-Subpackage noch nicht | Info | Sprint 4 Doku-Polish, mit F-011/F-019 buendeln | open |

### Historie-Update 28.05.2026

PQC-32 Closing-Review: 6 neue Findings F-025 bis F-030. Highlights:
- **F-028 (Tier 1):** TOK-2 (PQC-33) muss alg-Allowlist haben. Wird beim PQC-33-
  Story-Start als zusaetzlicher AC eingebaut (RFC 8725 BCP-Konformitaet). Auch
  als Tier-2-Notiz hier, damit Doku-Spur erhalten bleibt.
- **F-026 (Should):** sub-Logging auf INFO-Level. Bei TOK-1 noch low-volume,
  aber bei AUT-3 wird Token-Ausstellung hochfrequent. Zusammen mit F-021
  (sign/verify INFO-Level) als Bundle vor PQC-30 angehen.
- **F-029 (Tier 3):** Lessons-Learned aus Demo-Verifikation - das
  `from main import app` Anti-Pattern wandert ins Memory der Demo-Konvention.


## Findings aus PQC-33 (TOK-2) Code-Review am 28.05.2026

Story war Broker-Token-Verifikation mit RFC 8725 BCP alg-Allowlist.
F-028 wurde als AC-6 in die Story-Description integriert und ist mit der
Story selber resolved. Acceptance Criteria 1 bis 6 alle live im Container
verifiziert (7 Verify-Szenarien). 3 neue Tier-2-Polish-Findings.

### Tier-1 (haben oder bekommen Jira-Story)

(keine neuen Tier-1-Findings)

### Tier-2 (Polish, Code-Hygiene, keine eigene Story)

| ID | Titel | Severity | Trigger | Status |
|---|---|---|---|---|
| F-031 | verify-Errors werden nicht als Audit-Log-Event geloggt; nur der Caller sieht die Exception. Bei AUT-3 Login-Versuche ist Forensik-Logging wertvoll | Should | vor PQC-30, mit F-021/F-026 als Logging-Bundle | open |
| F-032 | verify validiert `iat` nicht ("Token nicht in der Zukunft"-Plausibilitaets-Check fehlt). RFC 7519 sagt iat optional, RFC 8725 empfiehlt Sanity-Check | Info | Sprint 3 Polish | open |
| F-033 | `typ`-Header wird beim Verify nicht geprueft. Wenn vorhanden, sollte gegen `"JWT"` matchen | Info | Sprint 3 Polish, mit F-032 buendeln | open |

### F-028 als resolved markieren

| F-028 (war Tier 1, Should) | alg-Allowlist-Check (RFC 8725 BCP) | resolved (PQC-33, als AC-6 implementiert: `_VALID_TOKEN_CHARS`-Filter, case-insensitive Allowlist, expliziter none-Block) |

### Historie-Update 28.05.2026 (PQC-33 abends)

PQC-33 Closing-Review: F-028 in der Story selbst resolved (als AC-6
implementiert), 3 neue Tier-2-Findings F-031 bis F-033. Highlights:
- **F-031 (Should):** Audit-Logging fuer Verify-Errors fehlt. Bundle mit
  F-021 (sign/verify INFO Frequenz) und F-026 (sub-Logging) ergibt ein
  konsistentes "Logging-Hardening"-Paket vor PQC-30.
- **F-032 plus F-033 (Info):** Sprint-3-Polish, optional. Aktueller Code
  ist RFC-konform aber nicht maximal-streng. Wuerde bei einem strengen
  Audit-Penetration-Test wahrscheinlich nicht durchfallen.


## Findings aus PQC-28 (AUT-1) Code-Review am 28.05.2026

Story war User-Store mit SQLAlchemy 2.0 async, Argon2id-Hashing und Alembic-
Migrations. AC-1 bis AC-5 alle erfuellt plus zusaetzliche Live-Container-
CRUD-Demo (6 Szenarien gruen). 5 neue Tier-2-Findings, keine Tier-1.

### Tier-1 (keine neuen)

(F-012 ist durch AUT-1 jetzt erreicht und sollte bei Touch von routers/health.py
adressiert werden.)

### Tier-2 (Polish, Code-Hygiene)

| ID | Titel | Severity | Trigger | Status |
|---|---|---|---|---|
| F-034 | email-Logging fehlt bei `user.created`-Event. Privacy-by-Design positiv, aber bei AUT-3 ggf. Debug-Forensik gewuenscht | Info | bei PQC-30 AUT-3, bewusste Entscheidung treffen | open |
| F-035 | `db.engine.created` loggt volle URL auf INFO. Bei SQLite OK, bei Postgres-Migration greift `_redact_url` | Info | bei Postgres-Migration | open |
| F-037 | SQLAlchemy/argon2-cffi/alembic Minor-Floats moeglich. uv.lock macht reproducible builds | Info | Sprint 4 Polish, mit F-006 buendeln | open |
| F-038 | `dummy_verify()` ist Methode auf PasswordHasher. Bei PQC-31 AUT-4 koennte sie via FastAPI-Depends injiziert werden fuer Tracing | Info | bei PQC-31 AUT-4 | open |
| F-039 | PasswordHasher hat keinen "Pepper" (server-side secret zusaetzlich zum Salt). OWASP empfiehlt fuer hochsicherheits-Setups | Should | Sprint 3 Polish, vor Production-Demo | open |

### Historie-Update 28.05.2026 (PQC-28 spaet abends)

PQC-28 Closing-Review: 5 neue Tier-2-Findings F-034-F-039 (F-036 ist Duplikat
von F-012, daher uebersprungen). Highlights:
- **F-039 (Should):** Password-Pepper als Sprint-3-Polish vor Production
  hinzufuegen. Aktuell sind die Salts (16 Bytes random pro Hash) bereits
  starke Defense, aber ein Pepper waere zusaetzliche Tiefe.
- **F-034 / F-038 sind PQC-30-related** und sollten dort entschieden werden.
- Logging-Hardening-Bundle waechst: F-021, F-026, F-031, F-034. Vor PQC-30
  als ein zusammenhaengender Refactoring-Pass.


## Findings aus PQC-29 (AUT-2) Code-Review am 28.05.2026

Story war Admin-CLI fuer User-Provisioning. AC-1 bis AC-5 alle live im
Container verifiziert. 0 Must, 0 Tier-1, 3 neue Tier-2-Findings (alle Info).

### Tier-1 (keine neuen)

### Tier-2 (Polish, Code-Hygiene)

| ID | Titel | Severity | Trigger | Status |
|---|---|---|---|---|
| F-040 | CLI macht Engine+Hasher-Init pro Command. Multi-Command-Session-Use waere effizienter mit Singleton-Pattern | Info | Sprint 3 Polish, wenn Library-Use-Case kommt | open |
| F-041 | Admin-CLI hat keine Confirmation-Prompts fuer destructive Actions. Aktuell keine destructiven Commands, aber bei `delete-user`-Erweiterung relevant | Info | bei CLI-Erweiterung um destructive Commands | open |
| F-042 | `list-users` hat keine Pagination - bei wachsender User-Base unhandlich. Im `UserRepository.list_all`-Docstring schon dokumentiert | Info | wenn User-Base 100+ wird | open |

### Historie-Update 28.05.2026 (PQC-29 abends)

PQC-29 Closing-Review: alle Findings sind Info-Level Sprint-3-Polish-Items.
Code ist sauber, CLI ist OWASP-konform (kein `--password <plain>` argv,
getpass + stdin-Pipe). Keine Tier-1-Trigger.


## Logging-Hardening-Refactor 28.05.2026 spaet abends

Vor PQC-30 (AUT-3) als kleiner Refactor-Pass durchgezogen:

| Finding | Vorher | Nachher | Status |
|---|---|---|---|
| F-021 | `crypto.facade.sign/verify` auf INFO | erfolgreich auf DEBUG, sign auf DEBUG, verify-failed auf WARNING mit reason | resolved |
| F-026 | `token.issued/verified` mit `sub` im Payload | `sub` entfernt aus INFO-Logs, kid+iat fuer Forensik-Lookup | resolved |
| F-031 | verify-Errors nicht als Audit-Event | Facade.verify_failed jetzt WARNING. TokenService-Exceptions werden vom Caller (AUT-3) als Audit-Event geloggt (Verantwortung bei der Endpoint-Schicht) | resolved (Tier-1-Hinweis fuer AUT-3) |
| F-034 | email-Logging bei `user.created` | bewusste Entscheidung: NICHT loggen (Privacy-by-Design, user_id reicht fuer Forensik via DB-Lookup) | resolved (decision documented) |

**Restliche offene Logging-Findings:**
- F-022 (verify-result True/False weiterhin geloggt): bewusst behalten, hilft bei Forensik (Side-Channel via Log-Aggregator ist Sprint-3-Polish wenn Real-Production-Deployment).
