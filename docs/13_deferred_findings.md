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
| F-005 | Rate-Limiting-Infrastruktur fehlt | Should | vor PQC-30, spaetestens vor produktiver Demo | [PQC-83](https://rumidesigns.atlassian.net/browse/PQC-83) | resolved (PQC-83, 2026-05-30) |

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


## Findings aus PQC-79 (SEC-1) Code-Review am 30.05.2026

Story war Request-ID Middleware mit structlog-Context. AC-1 bis AC-4 alle live
im Container verifiziert. **F-001 als resolved markiert.**

### Tier-2 (Polish)

| ID | Titel | Severity | Trigger | Status |
|---|---|---|---|---|
| F-043 | RequestIdMiddleware nutzt `BaseHTTPMiddleware` (anyio-Stream-Overhead). Pure ASGI-Middleware waere performanter | Info | Sprint 3 Polish bei Performance-Need | open |
| F-044 | uvicorn-Access-Log-Event ist generisches String statt strukturiertes Event mit method/path/status/duration. Strukturierter Access-Log waere besser fuer Forensik | Info | Sprint 3 Polish, mit F-013 buendeln | open |

### F-001 als resolved markiert

| F-001 (war Tier 1, Should) | Request-ID Middleware | resolved (PQC-79, RequestIdMiddleware mit structlog-contextvars + X-Request-ID Header-Echo) |

### Historie-Update 30.05.2026

PQC-79 Closing-Review: F-001 erfolgreich resolved. 2 neue Tier-2-Info-Findings
F-043/F-044 (Performance + strukturierter Access-Log). Lesson-Learned aus
Live-Verifikation: explizites `unbind_contextvars` im Middleware-finally hat
uvicorn-Access-Log-Context-Loss verursacht (Log wird post-middleware-return
emittiert). Fix: kein manuelles unbind, ContextVar-Task-Isolation (PEP 567)
nutzen.


## Findings aus PQC-80/81/82 (SEC-2/3/4) Bundle-Review am 30.05.2026

Bundle-Story: 3 SEC-Stories zusammen implementiert (CORS + TrustedHost +
Security-Headers). Alle AC live im Container verifiziert. **F-002, F-003, F-004
resolved.** SEC-5 (Rate-Limiting, PQC-83) bewusst Sprint-2-deferred wegen
Redis-Komplexitaet, Threat-Model im Bericht prominent erwaehnen.

### Tier-2 (Polish)

| ID | Titel | Severity | Trigger | Status |
|---|---|---|---|---|
| F-045 | SecurityHeadersMiddleware nutzt BaseHTTPMiddleware (analog F-043). Bei Performance-Need beide auf Pure-ASGI umstellen | Info | Sprint 3 Polish, mit F-043 buendeln | open |
| F-046 | CSP nicht gesetzt - Swagger-UI auf /docs braucht relaxed CSP. Bei Production wenn /docs OFF: strict CSP moeglich | Info | Sprint 3 Polish, vor Production wenn /docs disabled | open |
| F-047 | TrustedHost-Liste enthaelt `testserver` (FastAPI-TestClient-Default). Production-Config muss entfernen | Info | vor Production-Deployment | open |

### F-002, F-003, F-004 als resolved markiert

| F-002 (war Tier 1, Should) | CORS-Middleware | resolved (PQC-80, CORSMiddleware mit Allowlist + Pydantic-Validator gegen Wildcard+Credentials) |
| F-003 (war Tier 1, Should) | TrustedHost-Middleware | resolved (PQC-81, TrustedHostMiddleware mit Allowlist) |
| F-004 (war Tier 1, Should) | Security-Headers-Middleware | resolved (PQC-82, X-Content-Type-Options/X-Frame-Options/Referrer-Policy/HSTS-conditional) |

### Historie-Update 30.05.2026 (SEC-Bundle)

3 neue Tier-2-Info-Findings F-045-F-047 (alle Sprint-3-Polish). F-005 SEC-5
Rate-Limiting bleibt offen, ist Sprint-2-Folge (Redis-Integration noetig). 

Damit ist die HTTP-Hardening-Schicht zu 80% produktionsreif. PQC-30 (AUT-3)
nicht mehr blocked durch SEC-1/2/3/4. SEC-5 ist Tier-1-deferred-aber-bekannt.

aber-mit-Plan und wird in Sprint-1-Endspurt als naechste Story angegangen
(Annahme: Redis-Service ist via PQC-17-Compose-Setup schon vorhanden, also
keine Infra-Hurde).


## Findings aus PQC-83 (SEC-5) Code-Review am 30.05.2026

PQC-83 implementiert Rate-Limiting via slowapi + Redis. AC-1 bis AC-5 live
verifiziert. Im Phase-1-Audit ein **HIGH-Severity-Finding** (F-048) entdeckt
und direkt in derselben Story gefixt: ohne uvicorn `proxy_headers=True` und
`forwarded_allow_ips` ist `request.client.host` immer die nginx-Container-IP,
was Per-IP-Limit faktisch zu einem Per-Cluster-Limit macht (alle externen
Clients teilen einen Bucket). Fix war 3 Zeilen in `main.py._run()`, live mit
2 unterschiedlichen X-Forwarded-For-Werten verifiziert.

### Tier-1 (resolved-in-story)

| ID | Titel | Severity | Trigger | Status |
|---|---|---|---|---|
| F-048 | Per-IP-Limit war faktisch Per-Cluster (request.client.host = nginx-IP ohne uvicorn proxy_headers) | High | sofort in PQC-83 | resolved (PQC-83, uvicorn `proxy_headers=True, forwarded_allow_ips="172.16.0.0/12"`) |

### Tier-2 (Polish)

| ID | Titel | Severity | Trigger | Status |
|---|---|---|---|---|
| F-049 | Doppel-Logging `rate_limit.registered` beim Startup (uvicorn re-importiert main:app -> create_app() laeuft 2x) | Info | Sprint 4 Image-Slim oder vor Bericht-Abgabe | open (Fix: uvicorn.run mit App-Instanz statt String-Pfad, oder bewusst akzeptieren als Side-Effect des FastAPI/uvicorn-Patterns) |

### F-005 als resolved markiert

| F-005 (war Tier 1, Should) | Rate-Limiting-Infrastruktur | resolved (PQC-83, slowapi + Redis + Per-IP + 5/15min Login + 60/min Global + 429-Format mit Retry-After) |

### Historie-Update 30.05.2026 (PQC-83)

F-005 resolved. F-048 HIGH in Phase-1-Audit gefunden und in-story gefixt.
F-049 als Tier-2-Polish offen. Sprint-1 Endspurt-Story PQC-83 abgeschlossen,
damit ist die komplette SEC-Schicht (SEC-1 bis SEC-5) erledigt und PQC-30
hatte alle benoetigten Schutzlayer im Stack.bgeschlossen.


## Findings aus PQC-63 (QUA-1) Code-Review am 30.05.2026

PQC-63 fuehrt formales Pytest-Setup ein mit conftest.py + pytest-cov +
HTML-Coverage-Reports. AC-1 bis AC-4 alle gruen. 104 Tests passed in der
Sandbox, 4 skipped (liboqs-Sandbox-Skips). Sandbox-Coverage 57%, in Docker
mit liboqs erwartet 70-75%.

### Tier-2 (Polish)

| ID | Titel | Severity | Trigger | Status |
|---|---|---|---|---|
| F-050 | `main.py`, `routers/health.py`, `routers/dev_test.py` haben 0% Unit-Test-Coverage (nur Live-Tests im Docker). Lifespan-Hook ist schwer testbar, aber routers koennten mit TestClient saubere Unit-Tests bekommen | Info | Sprint 4 Polish, vor Bericht-Abgabe | open |

### Historie-Update 30.05.2026 (PQC-63)

Pytest-Setup formal abgeschlossen. F-050 als Tier-2-Polish offen.


## Findings aus PQC-18 (INF-4) Code-Review am 30.05.2026

Custom Multi-Stage Build von OpenSSL 3.5 + liboqs + oqs-provider + nginx 1.27.
Alle AC inkl. AC-5 (Live X25519MLKEM768 Handshake) live verifiziert.

### Tier-2 (Polish)

| ID | Titel | Severity | Trigger | Status |
|---|---|---|---|---|
| F-051 | Self-signed Test-Cert ohne PKI-Setup im pqc-nginx Image. Production muss echtes Cert von einer CA bekommen | Info | vor Production-Deployment | open |
| F-052 | Build-Args nicht hash-gepinnt (OpenSSL/liboqs/oqs-provider/nginx Git-Tags). Supply-Chain-Reproducibility. Buendeln mit F-018 (liboqs in auth-service-Image) | Info | Sprint 4, vor Bericht-Abgabe | open |
| F-053 | Image-Tag `rib-pqc-nginx:0.1` ist manuell. Naechste Versions-Bumps brauchen automatisierte Tag-Strategie | Info | Sprint 4 oder bei naechstem Image-Bump | open |

### Historie-Update 30.05.2026 (PQC-18)

INF-4 Sprint-0-Carry-Over abgeschlossen. Damit ist die TLS-Foundation fuer
Sprint-2 (PQC-43/44/45) gelegt. AC-5 (Mittelweg-Bundle, X25519MLKEM768 + ML-DSA-65
Cert) ist effektiv halb-PQC-44 mit erledigt.


## Findings aus PQC-20 (SKL-2) Code-Review am 30.05.2026

PQC-20 Expo-Skeleton angelegt mit create-expo-app. Default-Template lieferte
**SDK 56** (released 21.05.2026). Beim ersten AC-4-Live-Test im Expo Go
wurde festgestellt, dass Expo Go im App Store **noch nicht SDK 56
supportet**: aktuell ist nur SDK 54 in App Store + Play Store, SDK 55 wartet
seit ~Mai 2026 auf Apple-Approval. SDK 56 ist nur via TestFlight External
Beta oder `eas go` Custom-Build verfuegbar.

Senior-Decision (Sprint-1 Endspurt-Pragmatik): Downgrade auf SDK 54 fuer
App-Store-Kompatibilitaet ohne TestFlight-Beta-Setup. Sprint-2/3 koennen
upgraden wenn SDK 55/56 in den App Stores verfuegbar sind.

### Tier-2 (Polish)

| ID | Titel | Severity | Trigger | Status |
|---|---|---|---|---|
| F-054 | Expo SDK 54 statt 56 (App-Store-Expo-Go-Kompatibilitaet). Upgrade-Path in Sprint 2/3 wenn SDK 55/56 in App Store verfuegbar. Aufwand: `npx expo install --check` plus eventuell paar API-Anpassungen | Info | Sprint 2/3 oder bei SDK-55/56-App-Store-Release | open |

### Risk-Register-Hand-Off (Co-SM-Chat)

Fuer das Risk Register (docs/11_risk_register.md) als neuer Eintrag empfohlen:

- **ID:** R-N01 (neue Kategorie: Node/JS-Oekosystem)
- **Titel:** Expo SDK Version nicht in App Store verfuegbar
- **Beschreibung:** Expo Go App-Store-Version hinkt aktuell 1-2 SDK-Versionen
  hinterher. Bei Projekt-Init kann der Default neuer sein als die supportete
  SDK im App Store. Devices ohne TestFlight-Beta-Access bekommen
  Incompatibility-Error.
- **Wahrscheinlichkeit:** HOCH (bereits eingetreten in PQC-20)
- **Impact:** NIEDRIG (Downgrade dauert <5min, alle benoetigten Features in
  aelteren SDKs verfuegbar)
- **Mitigation:** Bei `create-expo-app` immer pruefen welche SDK-Version
  Expo Go aktuell supportet, ggf. mit `--sdk-version` Flag pinnen
- **Status:** Mitigated in PQC-20 (Downgrade auf SDK 54)

### Historie-Update 30.05.2026 (PQC-20)

SDK-56-Inkompatibilitaet entdeckt + auf SDK 54 downgraded. F-054 als
Tier-2-Polish offen (Upgrade-Path), R-N01 als Risk-Register-Empfehlung an
Co-SM-Chat.


## Findings aus PQC-57/62/54 (APP-4 + APP-9 + APP-1) Bundle-Review am 30-31.05.2026

App-Bundle (AuthContext + Token-Persistenz + Login-Form). Bundle weil
PQC-57 AC-3 (Token in secure-store persistieren) und PQC-62 AC-1 (setItemAsync
speichert Token) effektiv die gleiche Code-Linie sind, plus PQC-54
Submit-Action ruft die login-Methode aus PQC-57 auf.

### Tier-2 (Polish)

| ID | Titel | Severity | Trigger | Status |
|---|---|---|---|---|
| F-055 | Auto-Login nach Force-Close von Expo Go funktioniert nicht zuverlaessig im Dev-Mode (Token kommt nicht aus secure-store zurueck). Im Dev-Mode laedt Expo Go den JS-Bundle aus Metro neu, was die Keychain-Persistenz ueberlebt aber moeglicherweise andere Service-Scopes nutzt. Echter Test ist nur mit standalone .ipa-Build moeglich. | Info | bei standalone-Build-Story oder bei TestFlight-Deploy-Vorbereitung (Sprint 4 falls anvisiert) | open |

### Historie-Update 31.05.2026 (App-Bundle)

PQC-57 + PQC-62 + PQC-54 als sequentielle Bundle abgeschlossen. F-055 als
Expo-Go-Dev-Mode-Limitation dokumentiert (nicht App-Code-Bug). AC-4 von
PQC-62 (Real-Phone Auto-Login nach App-Neustart) ist im Dev-Mode nicht
voll verifizierbar; die secure-store-Mechanik (saveToken/loadToken/deleteToken)
funktioniert aber im Live-Test bei Hot-Reload (in-process-Reload).


## Findings aus PQC-84 (BRK-0) Code-Review am 03.06.2026 (Sprint-2-Start)

OAuth-Apps bei Google und Microsoft registriert, Credentials in .env, Setup-
Doku ergaenzt. Alle 5 AC live verifiziert (curl Discovery + Browser Authorize).

### Tier-2 (Polish)

| ID | Titel | Severity | Trigger | Status |
|---|---|---|---|---|
| F-056 | Client-Secrets (Google + Microsoft) wurden waehrend des Story-Setups im Implementation-Chat-History exposed (Test-Account-Kontext, akzeptiertes Risk-Tradeoff im Studienprojekt). Best-Practice: am Sprint-2-Ende oder spaetestens vor produktiver Demo rotieren via Provider-Console "neues Geheimnis hinzufuegen" + altes loeschen | Info | Sprint 4 Polish, oder vor Bericht-Demo | open |
| F-057 | server/config.yaml enthaelt aktuell nur einen Stub fuer idp_providers.google / idp_providers.microsoft. Echte Pydantic-IdpProvidersConfig-Klasse plus Settings-Verarbeitung kommt in PQC-36 BRK-1 (External-IdP-Registry) | Info | erledigt sobald PQC-36 in Progress geht | resolved (PQC-36 BRK-1, IdpProvidersConfig in config.py + Plugin-Adapter in server/idp/) |

### Historie-Update 03.06.2026 (PQC-84)

Sprint-2-Foundation gelegt: OAuth-Apps fuer Google und Microsoft sind
registriert und Live-verifiziert. Damit ist R-T04 (OIDC-Provider-Setup-
Komplexitaet) und R-S05 (Externe Approval-Wartezeit) mitigated. Single-Tenant
Microsoft-Setup hatte keine Approval-Wartezeit, daher konnte BRK-0 schon Tag
0 (vor dem geplanten Sprint-Start Sa 06.06) abgeschlossen werden.


## Findings aus PQC-36 (BRK-1) Code-Review am 17.06.2026

External-IdP-Registry Foundation gelegt: server/idp/ Modul mit Protocol +
Registry + Plugin-Stubs (Google, Microsoft) + Bootstrap aus Pydantic-Settings.
21 Tests gruen, kein Regress in der vollen Suite (125 passed).

### Tier-2 (Polish und Should-Fix vor abhaengigen Stories)

| ID | Titel | Severity | Trigger | Status |
|---|---|---|---|---|
| F-058 | `init_idp_registry` validiert nicht, dass `enabled=True` Provider tatsaechlich `client_id`, `client_secret` und `redirect_uri` befuellt haben. Misconfig (z.B. `RIB_IDP_PROVIDERS__GOOGLE__ENABLED=true` ohne Secret) fuehrt erst beim ersten OAuth-Flow-Request zur Fehlermeldung. Fail-fast at startup waere robuster. | Should | vor PQC-37 BRK-2 OIDC Code Flow PKCE | open |
| F-059 | scopes-Default `["openid","email","profile"]` enthaelt kein `offline_access`. Refresh-Tokens werden in BRK-2 noch nicht gebraucht (Server-side Session via httpOnly-Cookie geplant), aber sobald die Refresh-Strategie entschieden ist, muss per Provider explizit ergaenzt werden. Google verwendet zusaetzlich `access_type=offline` Authorize-Param. | May | vor PQC-37 BRK-2 wenn Refresh-Strategie entschieden | open |
| F-060 | server/README.md erwaehnt noch nicht das idp/-Modul und die Plugin-Architektur (analog zu der vorhandenen crypto/-Sektion). | May | Sprint 4 Doku-Polish oder bei naechster idp-Story (z.B. BRK-2 wenn das idp_registry zum ersten Mal verwendet wird) | open |
| F-061 | IdpProvider Protocol verlangt `name` als Property, beide Plugins liefern es als Klassen-Attribut (str). isinstance-Check ist via strukturelles Subtyping gruen, aber asymmetrisch zu den anderen Properties. Kein funktionales Problem. | Info | optionales Cleanup beim naechsten idp/-Touch | open |

### Historie-Update 17.06.2026 (PQC-36)

External-IdP-Registry-Foundation gelegt. Damit ist die Plugin-Schnittstelle
fuer alle nachfolgenden BRK-Stories etabliert. PQC-39 BRK-4 (claim_mapper-
Voll) und PQC-38 BRK-3 (verify_id_token-Voll) werden die Plugin-Stub-Bodies
ersetzen, ohne die Registry-API zu beruehren. F-057 wurde durch diese Story
resolved.


## Findings aus PQC-37 (BRK-2) Code-Review am 17.06.2026

OIDC Authorization Code Flow + PKCE inkl. State-Service implementiert. 47 neue
Tests gruen, volle Suite 172 passed. F-058 in dieser Story resolved.

### Tier-2 (Polish und Defense-in-Depth)

| ID | Titel | Severity | Trigger | Status |
|---|---|---|---|---|
| F-058 | init_idp_registry Misconfig-Validation | Should | vor PQC-37 | resolved (PQC-37: IdpConfigError + _check_provider_credentials in idp/registry_init.py) |
| F-062 | discovery_cache ist In-Memory pro Service-Instanz, bei Scale-Out wuerde jede Replica separat cachen. Production: shared Redis-Cache fuer Discovery-Docs. | Info | Sprint 4 oder Scale-Out-Story | open |
| F-063 | PKCE-Verifier wird vom Server NICHT gegen ein gespeichertes code_challenge gepruft (Vertrauen auf IdP-Validation gemaess RFC 7636). Defense-in-Depth: State-Eintrag koennte code_challenge auch speichern und Server prueft SHA256(verifier)==challenge. | Should | vor PQC-42 BRK-7 wenn State-Service erweitert wird | open |
| F-064 | Spaces in scope-Query werden als `+` URL-encoded statt `%20`. Beide RFC 3986-konform, aber `%20` universal-kompatibler. | May | Sprint 4 wenn echte IdP-Tests evtl. Probleme zeigen | open |
| F-065 | id_token wird roh an die App returned ohne Server-side Signature-Verifikation. BRK-3 PQC-38 wird das aufgreifen, AC-5 spec'ed es so. | Info | resolved durch PQC-38 BRK-3 | tracked-in-jira (PQC-38) |
| F-066 | Router validiert code_verifier nur per Laenge (43-128), nicht per Character-Class (RFC 7636: A-Z a-z 0-9 - . _ ~). App muss korrekte Generierung sicherstellen. | Info | Sprint 4 oder bei PQC-60 APP-7 | open |
| F-067 | High-Fidelity-Test mit echtem Redis-Container (statt fakeredis) fuer TTL-Expiry-Test sinnvoll, aber langsam. | Info | Sprint 4 Polish, optional | open |

### Historie-Update 17.06.2026 (PQC-37)

OIDC-Code-Flow-Foundation komplett: Server kann State generieren, App-PKCE-
Flow durchfuehren, Code+Verifier gegen Google/Microsoft-/token-Endpoint
tauschen. id_token kommt roh durch (Server-side Validation in BRK-3).
PQC-42 BRK-7 wird darauf aufbauen mit Defense-in-Depth (F-063). PQC-38
BRK-3 ersetzt die NotImplementedError-Stubs in den Plugins (F-065).


## Findings aus PQC-38 (BRK-3) Code-Review am 17.06.2026

ID-Token-Verifikation gegen JWKS implementiert. id_token ist ab BRK-3
trusted (Sig + iss + aud + exp gepruefr). F-065 resolved. 20 neue Tests,
volle Suite 190 passed.

### Tier-2 (Polish und Informational)

| ID | Titel | Severity | Trigger | Status |
|---|---|---|---|---|
| F-065 | id_token wurde in BRK-2 roh weitergereicht ohne Server-side Signature-Verifikation. | Info | resolved durch PQC-38 BRK-3 | resolved (PQC-38: IdTokenVerifier + plugin.verify_id_token mit RS256+iss+aud+exp) |
| F-068 | JWKS-Cache ist In-Memory pro Service-Instanz. Bei Scale-Out wuerde jede Replica separat cachen. Analog F-062 fuer Discovery-Cache. | Info | Sprint 4 oder Scale-Out-Story | open |
| F-069 | Verifier loggt `sub` bei Erfolg. Mit `oid` (MS) waere tenant-stable. Aktuell `sub` ist opaque, kein Privacy-Issue. | May | Sprint 4 Logging-Polish | open |
| F-070 | `nbf`-Claim wird nicht im require-Set verlangt. Wenn Provider nbf liefert, wird er aber per pyjwt-default geprueft. | Info | informational | open |
| F-071 | Force-Refresh-Loop ist auf 1 Retry begrenzt. Bei provider-side rapid-Rotation (Sekunden) koennte das knapp sein. Provider tut das aber nicht. | Info | informational | open |
| F-072 | Microsoft-Plugin tid-Check kommt NACH Sig-Verify. RFC 9700 sagt Sig-Verify zuerst (was wir machen), tid-Check ist Defense-in-Depth. | Info | informational | open |

### Historie-Update 17.06.2026 (PQC-38)

ID-Token-Verify-Foundation komplett: Server validiert JWS-Signature gegen
Provider-JWKS (cached 1h), iss/aud/exp gepruefr, Algorithm-Pinning RS256-only,
Microsoft tid-Defense-in-Depth. id_token ist ab jetzt trusted. PQC-39 BRK-4
wird darauf claim_mapper bauen (normalisierte User-Identity).


## Findings aus PQC-39 (BRK-4) Code-Review am 17.06.2026

Identity-Normalisierung + Account-Linking implementiert. user_identities-Tabelle als 1:n-Aggregat, Plugin-claim_mapper voll-impl, FederatedIdentityService mit Spoof-Schutz bei email_unverified. 23 neue Tests, volle Suite 211 passed.

### Tier-2 (Polish und Hardening)

| ID | Titel | Severity | Trigger | Status |
|---|---|---|---|---|
| F-073 | User.auth_method + User.external_sub bleiben im Schema als Backward-Compat-Felder, werden ab BRK-4 nicht mehr authoritativ gelesen (user_identities ist die Wahrheit). | Info | Sprint 4 Schema-Cleanup: nullbar machen oder droppen | open |
| F-074 | Microsoft-Plugin claim_mapper setzt email_verified=True wenn Email-Claim vorhanden. Edge-Case: external-collaborator-Accounts in einem Tenant koennten unverified UPN haben. RFC empfiehlt email_verified explizit aus Token zu lesen, Entra v2.0 liefert es selten. Konservativ nicht differenziert. | May | vor produktiver Demo / bei MS-External-Collaborator-Story | open |
| F-075 | FederatedIdentityService.link_or_create macht 2-3 separate DB-Calls. Race-Condition bei parallelen First-Logins desselben Users (zweiter wuerde IdentityAlreadyExistsError werfen). Akzeptiert weil single-User-pro-Login Annahme. Production: in DB-Transaction + Retry. | Info | Sprint 4 oder bei Load-Test-Issues | open |
| F-076 | Placeholder-Email `<sub>+<provider>@no-email.local` koennte theoretisch mit echten `.local`-Emails kollidieren. Extrem unwahrscheinlich. | Info | informational | open |
| F-077 | Alembic-Migration spiegelt bestehende User.external_sub in user_identities. Bei teilweise gescheiterter Migration koennte Inkonsistenz entstehen. Akzeptiert weil Sprint-1-DB klein. | Info | bei DB-Restore-Test | open |

### Historie-Update 17.06.2026 (PQC-39)

End-to-End-Server-Pfad funktional komplett:
- BRK-1 Plugin-Registry (PQC-36)
- BRK-2 OIDC Code Flow + PKCE (PQC-37)
- BRK-3 ID-Token-Verify (PQC-38)
- BRK-4 Identity-Normalisierung + Account-Linking (PQC-39)

Nach BRK-4 ist der Server bereit fuer App-Side-Story PQC-60 (Google-Login).
BRK-5/6 (PQC-40/41) werden Polish-Stories, BRK-7 (PQC-42) ist Hardening,
TLS-Stories (PQC-43/44/45) sind unabhaengiger Pfad.


## Findings aus PQC-40 (BRK-5) Code-Review am 17.06.2026

Google IdP-Plugin Voll-Demo: Broker-Token-Ausgabe im federated-Callback ergaenzt. AC-1..AC-4 schon durch BRK-1..BRK-4 erfuellt. AC-5 Code-Teil verifiziert, Live-Demo deferred zu PQC-60 APP-7.

### Tier-2 (Polish)

| ID | Titel | Severity | Trigger | Status |
|---|---|---|---|---|
| F-078 | TokenService._ttl Private-Access (Underscore) in routers/auth_federated.py und routers/auth.py. Sauber waere Public-Property TokenService.ttl. | Info | bei naechstem TokenService-Touch, mit F-021 buendeln | open |
| F-079 | AC-5 Live-Demo in PQC-60 APP-7 cross-referenced. Bericht muss Cross-Story-Demo-Referenz erwaehnen. | May | vor Bericht-Abgabe | open |

### Historie-Update 17.06.2026 (PQC-40)

PQC-40 BRK-5 bestaetigt die Plugin-Architektur: BRK-1..BRK-4 hat 95% der
Logik geliefert, BRK-5 fuegte nur die Broker-Token-Ausgabe + Demo-Doku
hinzu. Neue Provider (Apple in STR-2 PQC-76) folgen demselben Muster:
nur ihre Plugin-Implementierung + AC-Check + Demo, kein Infrastructure-Code.


## Findings aus PQC-41 (BRK-6) Code-Review am 17.06.2026

Microsoft IdP-Plugin Voll-Demo: AC-Cross-Reference auf BRK-1..BRK-5. Keine Code-Aenderung notwendig (Plugin-Architektur deckt alles ab). Bestaetigt das Architektur-Design: neue Provider haben Grenzkosten ~null.

### Tier-2 (Doku-Polish)

| ID | Titel | Severity | Trigger | Status |
|---|---|---|---|---|
| F-080 | AC-2 Spec sagt Multi-Tenant `common`, wir nutzen Single-Tenant `<tenant>` (Senior-Decision aus PQC-84). Bericht muss diese Abweichung mit Begruendung (UC-3 Mitarbeiter-Login + tid-Defense-in-Depth) explizit dokumentieren. | May | vor Bericht-Abgabe | open |

### Historie-Update 17.06.2026 (PQC-41)

End-to-End-Server-Pfad funktional komplett (BRK-0..BRK-6). Sprint-2 Done-SP:
PQC-84 + PQC-36 + PQC-37 + PQC-38 + PQC-39 + PQC-40 + PQC-41 = 36 SP.
Restscope: BRK-7 Hardening, TLS-Pfad, App-Stories.


## Findings aus PQC-42 (BRK-7) Code-Review am 17.06.2026

CSRF/State+PKCE-Refactor zu Server-managed BFF-Pattern. AC-5 zu 100% erfuellt (code_verifier zusammen mit state in Redis, atomar consumed). F-063 durch dieses Refactor resolved.

### Tier-2 (Polish)

| ID | Titel | Severity | Trigger | Status |
|---|---|---|---|---|
| F-063 | PKCE-Verifier Server-side code_challenge-Pruefung als Defense-in-Depth | Should | vor PQC-42 BRK-7 | resolved (PQC-42: code_verifier ist server-side gespeichert, App kann keinen anderen liefern als beim Authorize-Start) |
| F-081 | AC-1 Spec sagt App-Gen-State, wir nutzen Server-Gen (BFF-Konvention RFC 9700). Bericht muss Abweichung mit Begruendung dokumentieren. | May | vor Bericht-Abgabe | open |

### Historie-Update 17.06.2026 (PQC-42)

End-to-End-OIDC-Server-Pfad nach PQC-42 vollstaendig: BRK-1..BRK-7 done.
Sprint-2 Done-SP = 38 (von 62 geplant). Restscope: TLS-Pfad + App-Stories.


## Findings aus PQC-43 (TLS-1) Code-Review am 17.06.2026

nginx X25519MLKEM768-Konfiguration: AC-Cross-Reference auf PQC-18 INF-4 (Foundation). Keine Code-Aenderung. Bonus-Abweichung: Self-signed Cert nutzt ML-DSA-65 statt klassisches ECDSA (durchgaengig PQC).

### Tier-2 (Doku-Polish)

| ID | Titel | Severity | Trigger | Status |
|---|---|---|---|---|
| F-083 | AC-2 spec sagt ECDSA, wir nutzen ML-DSA-65 (bewusste Erweiterung in PQC-Richtung). Bericht muss als Story-Highlight prominent erwaehnen. | May | vor Bericht-Abgabe | open |

### Historie-Update 17.06.2026 (PQC-43)

TLS-Foundation aus PQC-18 wird durch PQC-43 cross-referenced. Sprint-2 Done-SP: 43.


## Findings aus PQC-44 (TLS-2) Code-Review am 17.06.2026

PQ-TLS-Handshake-Verifikations-Skript erstellt. Live-Demo deferred zu User-Action mit laufendem Container.

### Tier-2 (User-Action)

| ID | Titel | Severity | Trigger | Status |
|---|---|---|---|---|
| F-084 | AC-3 Live-Demo-Log noch nicht erzeugt (User fuehrt scripts/verify_pq_tls.sh aus mit laufendem pqc-nginx-Container und kopiert Output in sprint_journal/sprint_2/demos/). | May | vor Bericht-Abgabe | open (User-Action) |

### Historie-Update 17.06.2026 (PQC-44)

Sprint-2 Done-SP: 45. TLS-Pfad endet mit PQC-45 (E2E-Routing zu auth-service via 443).


## Findings aus PQC-45 (TLS-3) Code-Review am 17.06.2026

nginx-443 Reverse-Proxy zu auth-service implementiert. X-Forwarded-Header durchgaengig fuer Rate-Limit-Konsistenz (PQC-83 F-048).

### Tier-2 (User-Action)

| ID | Titel | Severity | Trigger | Status |
|---|---|---|---|---|
| F-085 | AC-2 Live-Demo (curl gegen https://localhost/health im laufenden Container) = User-Aktion analog F-084. | May | vor Bericht-Abgabe | open (User-Action) |

### Historie-Update 17.06.2026 (PQC-45)

End-to-End-Server-Pfad Sprint-2 nach PQC-45 vollstaendig: Federation BRK-1..BRK-7 + TLS-1..TLS-3 + Foundation PQC-84. Sprint-2 Done-SP: 47. Restscope: PQC-60 APP-7 + PQC-61 APP-8 (App-Stories).


## Findings aus PQC-60 (APP-7) Code-Review am 17.06.2026

App-Side Google-Login implementiert: oauthClient.ts mit PKCE + Authorize/Callback-Roundtrip + AuthContext-Integration. Code-Teil komplett, Live-Demo blocked durch OAuth-App-Type (Web statt iOS).

### Tier-2 (Live-Demo Blocker)

| ID | Titel | Severity | Trigger | Status |
|---|---|---|---|---|
| F-086 | Live-Browser-Demo blocked weil Google-OAuth-App (PQC-84) als Web-Application registriert ist mit Server-Side redirect_uri. Mobile-App-Flow braucht iOS-App-Type + Custom-Scheme-redirect_uri (z.B. app://oauth/google/callback). Sprint-3-Action: neue OAuth-App-Registrierung + Server-Config-Update. App-Code ist funktional, kein Code-Fix noetig. | Should | Sprint 3 (vor Bericht-Demo) | open (User-Action) |

### Historie-Update 17.06.2026 (PQC-60)

App-Login-Code komplett. Sprint-2 Done-SP: 52. Restscope: PQC-61 APP-8 Microsoft (5 SP).


## Findings aus PQC-61 (APP-8) Code-Review am 17.06.2026

Microsoft-Login App-Seite implementiert. Refactor zu generischem handleOAuthLogin-Helper. Dank generischem oauthClient kein neuer Code in der Lib. Keine neuen Findings - F-086 (OAuth-App-Type-Switch) gilt auch fuer Microsoft.

### Historie-Update 17.06.2026 (PQC-61 + Sprint-2 abgeschlossen)

**Sprint-2 funktional komplett:** PQC-84 + PQC-36 + PQC-37 + PQC-38 + PQC-39 + PQC-40 + PQC-41 + PQC-42 + PQC-43 + PQC-44 + PQC-45 + PQC-60 + PQC-61 = **57 SP** Done (92% von 62 SP geplant).

Restscope: keine Must-Stories. Demo-Session + Sprint-3 Doku-Polish + F-086 OAuth-App-Type-Switch.


## Findings aus PQC-24 (CRY-4) Closing-Review am 18.06.2026

LibOqsKem-Adapter fuer ML-KEM-768 + ML-KEM-1024 implementiert. Stateless per-Call oqs-Instanziierung analog LibOqsSignature (PQC-25). 17 Tests, in Sandbox skipped (etabliertes Pattern), liboqs-Tests laufen im Docker mit echter liboqs-Library. registry_init.py von PlaceholderKem auf LibOqsKem umgestellt. 215 passed, keine Test-Regressions.

### Tier-2 (Polish/Tracking)

| ID | Titel | Severity | Trigger | Status |
|---|---|---|---|---|
| F-088 | AC-3 verifiziert via Property-Tests (Roundtrip + FIPS-203-Output-Sizes + Implicit-Rejection) plus liboqs-interne KAT-Validation beim Build, statt externer NIST-KAT-Datei-Replay. Pragmatische Entscheidung weil KAT-Files mehrere MB und liboqs intern bereits gegen sie validiert. | Info | Sprint 4 vor Bericht-Abgabe optional explizites KAT-Replay als zusaetzliche Verifikation | open |
| F-089 | LibOqsKem instanziiert `oqs.KeyEncapsulation` pro Call (stateless). Pro SES-1-Request entsteht damit ein Setup-Overhead. Bei hoher Last waere ein KEM-Pool oder Per-Algorithm-Singleton-Pattern denkbar. Aktuell kein Bottleneck zu erwarten. | May | vor Production-Load-Test pruefen (Sprint 4 oder spaeter) | open |
| F-090 | FIPS-203-Implicit-Rejection-Verhalten ist im Adapter-Docstring dokumentiert, muss aber im SES-1-Aufrufer (Session-Init-Endpoint) und DCH-1 (AEAD-Layer) prominent gehandhabt werden. Adapter selber wirft KEINEN Error bei "wrong" ciphertext, das Authentication-Signal kommt vom AEAD-Tag. | Info | bei PQC-46 SES-1 und PQC-50 DCH-1 Story-Start erneut pruefen | open |

### Historie-Update 18.06.2026 (PQC-24)

Sprint-3 Start: erste Story Done. Crypto-Foundation-KEM-Adapter steht. Nebenbei mitgenommen: Doc-Fix in crypto/registry.py (KemPlugin-Beispiel war falsch auf PQC-25 verwiesen statt PQC-24).


## Findings aus PQC-23 (CRY-3) Closing-Review am 18.06.2026

Crypto-Facade um KEM (LibOqsKem-Pass-Through), HKDF-SHA256 und AES-256-GCM-AEAD erweitert. Plus Negotiation-Support (supported_kem_algorithms, is_kem_supported). Neue AeadDecryptError-Klasse als sauberer Wrapper um cryptography.exceptions.InvalidTag. 30 Tests in test_facade.py (8 alte + 22 neue CRY-3 + 1 Integration-Pipeline). 215 passed, 5 skipped, keine Regressions.

### Tier-2 (Polish/Tracking)

| ID | Titel | Severity | Trigger | Status |
|---|---|---|---|---|
| F-091 | HKDF-Aufrufkonvention (info=b"app-session-v1", salt=session_id) wird in SES-2 (PQC-47) festgelegt, nicht hardcoded in facade.hkdf(). Vorteil: HKDF bleibt fuer andere Use-Cases nutzbar. Konvention muss in SES-2 Doku stehen. | Info | bei PQC-47 SES-2 Story-Start sicherstellen | open |
| F-092 | facade.aead_encrypt prueft nonce-Laenge nicht selbst, cryptography.hazmat AESGCM wirft ValueError bei wrong-size. NIST SP 800-38D Section 8.2 fordert nonce-Eindeutigkeit pro Key. Aufrufer (DCH-1/DCH-2) muss 12-Byte-CSPRNG-Nonce per Request streng durchsetzen. Replay-Tracking ist DCH-4. | Info | bei PQC-50 DCH-1 + PQC-51 DCH-2 streng implementieren | open |
| F-093 | Edit-Tool und Write-Tool haben facade.py + test_facade.py waehrend PQC-23 zweimal mitten im Schreiben truncated. Fix per bash-heredoc-Rewrite. Nicht code-relevant, Tooling-Workaround dokumentiert. | Info | bei wieder auftretendem Vorfall heredoc als Default-Strategie | open |

### Historie-Update 18.06.2026 (PQC-23)

Sprint-3 Story 2 von 18 Done. Crypto-Facade-Schicht komplett (Signature + KEM + HKDF + AEAD + Negotiation). Foundation fuer SES-1/2/3 + DCH-1/2/3/4 steht.


## Findings aus PQC-27 (CRY-7) Closing-Review am 18.06.2026

Doku-Story: docs/wire_format.md (228 Zeilen, 7 Sektionen) als zentrale Spec fuer alle Krypto-Artefakte angelegt. AC-1 (Token-Header alg+kid) bereits seit Sprint 1 PQC-32 erfuellt. AC-2/AC-3 (Session-Record und Wire-Format kem_alg) als Schema-Spec festgeschrieben, Code-Enforcement kommt in PQC-46 SES-1 und PQC-48 SES-3.

### Tier-2 (Polish/Tracking)

| ID | Titel | Severity | Trigger | Status |
|---|---|---|---|---|
| F-094 | docs/wire_format.md Sec 5.3 (Encrypted-Channel Response-Body) ist als TBD-in-SES-3 markiert. Konkrete Konvention (gleicher Header oder X-Response-Nonce) wird in PQC-52 DCH-3 finalisiert. | Info | bei PQC-52 DCH-3 die Sec 5.3 final updaten | open |

### Historie-Update 18.06.2026 (PQC-27)

Sprint-3 Story 3 von 18 Done. Wire-Format-Spec steht. Crypto-Foundation-Block 1 (CRY-4 + CRY-3 + CRY-7) komplett, 12 SP done. Next: Session-Server-Layer (SES-3 + SES-2 + SES-1).

## Nachtrag PQC-27 Closing-Review (Tiefer-Pass)

Bei tiefem Review festgestellt: `docs/wire_format.md` referenziert `settings.session.ttl_seconds`, dieses Config-Feld existiert noch nicht in `server/config.py`. Spec-Story darf Forward-References machen, aber wir tracken explizit damit SES-3 das Feld tatsaechlich anlegt.

| ID | Titel | Severity | Trigger | Status |
|---|---|---|---|---|
| F-095 | wire_format.md verweist auf `settings.session.ttl_seconds` (Default 900), Feld muss in PQC-48 SES-3 in `config.py` als `SessionConfig.ttl_seconds` ergaenzt werden. Doku-Markup auf "zu ergaenzendes Config-Feld in PQC-48 SES-3" geupdated. | Info | bei PQC-48 SES-3 Story-Start umsetzen | open |
