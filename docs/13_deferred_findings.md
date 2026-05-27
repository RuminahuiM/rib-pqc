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
| F-015 | LibOqsSignature.verify faengt zu breit (except Exception -> False) | Info | bei naechstem Touch von liboqs_signature.py | open (inline TODO empfohlen) |
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
