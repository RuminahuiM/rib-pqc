# Jira Story Drafts: Tier-1 Findings aus PQC-19 Code-Review

**Erstellt:** 25.05.2026 nach PQC-19 Done
**Autor:** Implementation-Chat plus Dodoe
**Status:** Drafts. Werden in Jira angelegt sobald MCP-Verbindung wieder steht.

## Hintergrund

Im Code-Review nach PQC-19 (SKL-1) entstanden 13 Findings (siehe
`docs/13_deferred_findings.md`). Davon sind 5 als Tier-1 klassifiziert, d.h.
sie brauchen je eine eigene Jira-Story, weil sie:

- konkret-actionable sind
- eine Story-Dependency haben (alle blocken PQC-30 AUT-3, da sie vor dem ersten
  echten Auth-Endpoint produktiv da sein muessen)
- nicht in PQC-19 selbst gepasst haetten (Scope-Creep)

Alle fuenf Stories sollten ein neues Epic bekommen: **EPIC SEC: Security
Infrastructure**. Begruendung: HTTP-Security-Middleware ist konzeptionell
keine Skeleton-Sache (SKL) und keine Authentifizierungs-Logik (AUT). Es ist
eine eigene Schicht. Mentor-/Bericht-tauglich.

## Story 1: SEC-1 (Request-ID Middleware)

**Titel:** `SEC-1: Request-ID Middleware mit structlog-Context`

**Story-Block:**

```markdown
**Story-ID (Markdown):** SEC-1
**Bezug:** docs/13_deferred_findings.md F-001, docs/06_tech_stack.md Abschnitt 2.5
**Prioritaet:** Must
**T-Shirt:** S | **Story Points:** 2 | **Sprint:** 1 oder 2 (vor PQC-30)
**Blockt:** PQC-30 (AUT-3)

**Story:**
Als Server-Entwickler moechte ich, dass jeder Request eine eindeutige Request-ID
bekommt, die in allen Log-Eintraegen mitgeschrieben wird, damit ich Logs eines
Calls quer durch Auth-, Token- und Session-Module zusammenhaengen kann.

**Akzeptanzkriterien:**

* AC-1: Eine FastAPI-Middleware setzt fuer jeden Request eine UUID4 als
  `request_id` in `structlog.contextvars`.
* AC-2: Falls der Request bereits einen `X-Request-ID`-Header mitbringt, wird
  dieser uebernommen, sonst eine neue UUID4 generiert.
* AC-3: Antwort enthaelt ebenfalls `X-Request-ID`-Header (Client-side Korrelation).
* AC-4: Mindestens ein Test demonstriert, dass alle Logs eines /health-Calls
  dieselbe request_id tragen.

**Definition of Done:**

* Middleware-Modul `server/middleware/request_id.py` plus Registrierung in
  `main.py:create_app`.
* Pytest-Coverage fuer den oben genannten Test.
* Done-Comment mit Hinweis dass Finding F-001 geschlossen ist.
```

## Story 2: SEC-2 (CORS-Konfiguration)

**Titel:** `SEC-2: CORS-Middleware mit Allowlist-Konfiguration`

**Story-Block:**

```markdown
**Story-ID (Markdown):** SEC-2
**Bezug:** docs/13_deferred_findings.md F-002, FastAPI Tutorial CORS
**Prioritaet:** Must
**T-Shirt:** S | **Story Points:** 2 | **Sprint:** 1 oder 2 (vor PQC-30)
**Blockt:** PQC-30 (AUT-3)

**Story:**
Als Server-Entwickler moechte ich, dass nur explizit erlaubte Origins
Cross-Origin-Calls machen koennen, damit Browser-basierte Angriffe
unterbunden werden und das Swagger-UI nutzbar bleibt.

**Akzeptanzkriterien:**

* AC-1: `starlette.middleware.cors.CORSMiddleware` ist in `create_app()`
  registriert.
* AC-2: Allowed-Origins kommen aus Settings (neuer Feld `cors_allowed_origins:
  list[str]`), default fuer Dev sind `["http://localhost:8081", "http://localhost:8080"]`
  (Expo-Dev-Server plus nginx-Reverse-Proxy).
* AC-3: Keine Wildcards `"*"` in der Default-Konfig. Wildcards verboten wenn
  `allow_credentials=True` (Validation in Settings).
* AC-4: Allowed-Methods: GET, POST, OPTIONS. Allowed-Headers: `Authorization`,
  `Content-Type`, `X-Request-ID`.
* AC-5: Preflight-OPTIONS-Test gegen /health zeigt korrekte Headers.

**Definition of Done:**

* CORS-Konfiguration in `config.py` und `config.yaml`.
* Pytest-Coverage fuer Allowed-Origin und blockierten Origin.
* Done-Comment mit Hinweis dass Finding F-002 geschlossen ist.
```

## Story 3: SEC-3 (TrustedHost-Middleware)

**Titel:** `SEC-3: TrustedHostMiddleware gegen Host-Header-Injection`

**Story-Block:**

```markdown
**Story-ID (Markdown):** SEC-3
**Bezug:** docs/13_deferred_findings.md F-003
**Prioritaet:** Must
**T-Shirt:** S | **Story Points:** 1 | **Sprint:** 1 oder 2 (vor PQC-30)
**Blockt:** PQC-30 (AUT-3)

**Story:**
Als Server-Entwickler moechte ich, dass die App nur mit definierten Host-Werten
in `Host`-Headern angesprochen werden kann, damit Host-Header-Injection-Angriffe
(z.B. spaetere Token-Subject-Manipulation) unterbunden werden.

**Akzeptanzkriterien:**

* AC-1: `starlette.middleware.trustedhost.TrustedHostMiddleware` ist in
  `create_app()` registriert.
* AC-2: Allowed-Hosts kommen aus Settings (neuer Feld `trusted_hosts:
  list[str]`), default `["localhost", "127.0.0.1", "auth-service"]`.
* AC-3: Request mit Host-Header `evil.com` returned 400 Invalid Host.

**Definition of Done:**

* Konfiguration in `config.py` und `config.yaml`.
* Pytest-Coverage fuer erlaubten und abgelehnten Host.
* Done-Comment mit Hinweis dass Finding F-003 geschlossen ist.
```

## Story 4: SEC-4 (Security-Headers-Middleware)

**Titel:** `SEC-4: Security-Headers-Middleware (X-Frame-Options, X-Content-Type-Options, HSTS, CSP)`

**Story-Block:**

```markdown
**Story-ID (Markdown):** SEC-4
**Bezug:** docs/13_deferred_findings.md F-004, OWASP Secure Headers Project
**Prioritaet:** Should
**T-Shirt:** S | **Story Points:** 2 | **Sprint:** 1 oder 2 (vor PQC-30)
**Blockt:** PQC-30 (AUT-3)

**Story:**
Als Server-Entwickler moechte ich, dass jede HTTP-Antwort defensive Headers
mitbringt, damit XSS, Clickjacking und MIME-Sniffing erschwert werden und
die Bericht-Story sauber ist.

**Akzeptanzkriterien:**

* AC-1: Eine Middleware setzt mindestens folgende Response-Headers:
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY`
  - `Referrer-Policy: no-referrer`
  - `Strict-Transport-Security: max-age=31536000; includeSubDomains` (nur wenn
    `environment != "dev"`, da lokal kein TLS aktiv)
* AC-2: Optional in Sprint 1: einfache `Content-Security-Policy: default-src 'self'`
  fuer JSON-Endpoints. CSP fuer /docs Swagger-UI braucht separate Anpassung.
* AC-3: Pytest-Coverage prueft die Headers auf /health.

**Definition of Done:**

* Middleware-Modul `server/middleware/security_headers.py` plus Registrierung.
* Pytest-Coverage fuer Header-Anwesenheit.
* Done-Comment mit Hinweis dass Finding F-004 geschlossen ist.
```

## Story 5: SEC-5 (Rate-Limiting-Infrastruktur)

**Titel:** `SEC-5: Rate-Limiting-Infrastruktur via Redis und slowapi`

**Story-Block:**

```markdown
**Story-ID (Markdown):** SEC-5
**Bezug:** docs/13_deferred_findings.md F-005, OWASP Authentication Cheat Sheet
**Prioritaet:** Must (fuer AUT-3), Should (fuer /health)
**T-Shirt:** M | **Story Points:** 3 | **Sprint:** 2 (vor PQC-30 AUT-3)
**Blockt:** PQC-30 (AUT-3)

**Story:**
Als Server-Entwickler moechte ich pro Endpoint Rate-Limits einstellbar haben,
damit Brute-Force-Angriffe auf /auth/local/login unterbunden werden.

**Akzeptanzkriterien:**

* AC-1: Rate-Limit-Infrastruktur (`slowapi` mit Redis als Backend) ist
  registriert. Redis ist schon vorhanden seit PQC-17.
* AC-2: Globaler Default ist `60 requests / minute` pro IP.
* AC-3: Pro-Endpoint-Override moeglich via Decorator (vorbereitet fuer
  `/auth/local/login` mit `5 / minute`).
* AC-4: Bei Limit-Hit liefert die App 429 Too Many Requests plus
  `Retry-After`-Header.
* AC-5: Test demonstriert Limit-Hit-Verhalten auf einem dedizierten
  /rate-limit-test-Endpoint (nur in `environment=dev`).

**Definition of Done:**

* Konfiguration in `config.py` und `config.yaml`.
* Endpoint-Decorator-Infrastruktur, Beispiel-Verwendung dokumentiert.
* Pytest-Coverage fuer Limit-Hit.
* Done-Comment mit Hinweis dass Finding F-005 geschlossen ist.
```

## Anlege-Reihenfolge wenn MCP zurueck ist

1. Neues Epic anlegen: **SEC: Security Infrastructure**.
2. Stories SEC-1 bis SEC-5 unter dem Epic anlegen.
3. Fuer jede SEC-Story: `blocks PQC-30`-Issue-Link setzen.
4. Sprint-Zuweisung: alle in Sprint 1 oder Sprint 2 (Co-SM-Chat entscheidet,
   ich kann fuer Sprint 1 nur SEC-1, SEC-2, SEC-3 empfehlen weil zeitlich
   passend, SEC-4 und SEC-5 sind groesser).
5. `docs/13_deferred_findings.md` updaten: die TBD-Eintraege durch echte
   PQC-Keys ersetzen.

## Stretch-Optionen die wir noch ueberlegen koennten

- SEC-4 koennte in zwei Stories aufgespalten werden, falls CSP fuer /docs
  Swagger-UI mehr Arbeit ist als erwartet.
- SEC-5 koennte mit einem Stretch-AC zur Distributed-Rate-Limit-Lockout
  erweitert werden, dafuer kuerzere AC-Liste in PQC-31 (AUT-4 User-Enumeration).
