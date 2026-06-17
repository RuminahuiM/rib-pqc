# Evidence: PQC-45 TLS-3 nginx Reverse Proxy 443

**Story:** PQC-45 TLS-3 (2 SP)
**Sprint:** 2
**Status:** Ready for Review
**Datum:** 2026-06-17

## Ziel und Acceptance Criteria

nginx als Reverse Proxy zum FastAPI-Service auf Port 443. Damit ist der
TLS-1.3+PQ-Endpoint extern erreichbar, intern bleibt HTTP-Routing.

| AC | Status | Evidenz |
| --- | --- | --- |
| AC-1 nginx forwarded alle Requests an auth-service:8000 | OK | `infra/nginx/nginx.conf` Server-2 Block (Port 443), `location /` mit `proxy_pass http://auth_service` |
| AC-2 Health-Check ueber https://localhost/health liefert 200 OK | Code OK, Live-Demo User-Action | `/health` wird via Catch-all-Proxy zum FastAPI weitergeleitet (FastAPI hat `/health` aus PQC-19 SKL-1) |
| AC-3 X-Forwarded-For, X-Real-IP korrekt uebergeben | OK | nginx.conf Line 99-105: `X-Real-IP`, `X-Forwarded-For`, `X-Forwarded-Proto https`, `X-Forwarded-Host`, plus `X-TLS-Protocol` und `X-TLS-Cipher` als Bonus |

## In PQC-45 implementiert

**Aenderung an `infra/nginx/nginx.conf` Server-2 Block (Port 443):**

- **Catch-all `location /` umgestellt** von 404-Hinweis-Response auf
  `proxy_pass http://auth_service` (genau wie Port-80-Block aus PQC-17).
- **X-Forwarded-Header erweitert:**
  - `X-Real-IP $remote_addr` (echte Client-IP)
  - `X-Forwarded-For $proxy_add_x_forwarded_for` (Hop-Liste)
  - `X-Forwarded-Proto https` (Protokoll-Indikator)
  - `X-Forwarded-Host $host` (Host-Header)
- **Bonus: TLS-Metadata-Header fuer Audit/Logging:**
  - `X-TLS-Protocol $ssl_protocol`
  - `X-TLS-Cipher $ssl_cipher`
- **`/pqc-test` Endpoint bleibt** als nginx-internal TLS-Smoke (vorrangiger
  Match-Block, nicht durchgereicht).
- **Bisheriger TLS-only `/health`-Block entfernt:** ueber proxy_pass laeuft
  jetzt der echte FastAPI-`/health`-Endpoint aus PQC-19 SKL-1. Konsistent
  mit Port-80-Verhalten.

## Konsistenz zu PQC-83 SEC-5 F-048

Der `X-Real-IP` + `X-Forwarded-For` Header-Pass-Through ist
**Voraussetzung fuer Per-IP-Rate-Limit**. uvicorn ist seit PQC-83 mit
`proxy_headers=True, forwarded_allow_ips="172.16.0.0/12"` konfiguriert,
liest also `X-Forwarded-For` von nginx (Docker-Bridge-Range) und setzt
`request.client.host` korrekt auf die echte Client-IP.

Damit ist der Rate-Limit-Stack durchgaengig korrekt von nginx-TLS-443
ueber X-Forwarded-For zu slowapi-Per-IP-Limit.

## Tests

Keine neuen Unit-Tests (Infrastructure-Config). Volle Suite weiterhin
**215 passed, 4 skipped**, ruff clean. nginx.conf-Syntax wird beim
Container-Build von `nginx -t` validiert (kommt im naechsten Container-
Restart durch).

## AC-2 Live-Demo (User-Aufgabe)

```bash
cd infra && docker compose up -d --build  # rebuild damit neue nginx.conf reinkommt
cd ..
# Trust-warning ignorieren (self-signed Cert), Hybrid-TLS-Handshake erfolgt
curl -sk https://localhost/health | jq .
```

Erwartete Ausgabe: `{"status":"ok"}` (JSON von FastAPI-Health-Endpoint).
Damit ist AC-2 + AC-1 erfuellt: Health-Request lief via nginx-443 -> auth-service:8000.

## Closing-Review-Findings

Keine Must-Fix. 1 Finding:

| ID | Severity | Beschreibung | Tracking |
| --- | --- | --- | --- |
| F-085 | May | AC-2 Live-Demo-Verify (curl gegen https://localhost/health im laufenden Container) noch nicht erzeugt. User-Aktion vor Bericht-Abgabe analog F-084. | vor Bericht-Abgabe | open (User-Action) |

## Verifikation

- `infra/nginx/nginx.conf` korrekt aktualisiert (110 Zeilen, keine Duplikate)
- Volle Test-Suite gruen (kein Regress)
- Aenderung konsistent mit PQC-17 Port-80-Block

## Story-Aufwand

- Story-Points: 2 (T-Shirt S)
- Tatsaechliche Zeit: tba
- AI-Multiplier-Beobachtung: Minimaler Refactor (Catch-all-Location auf
  proxy_pass umstellen). Story-Aufwand sehr klein dank PQC-17 + PQC-18
  Vorarbeit.

## Folgestories

**End-to-End-Sprint-2-Server-Pfad nach PQC-45 vollstaendig:**

- Federation: BRK-1 + BRK-2 + BRK-3 + BRK-4 + BRK-5 + BRK-6 + BRK-7
- TLS: TLS-1 + TLS-2 + TLS-3
- Foundation: PQC-84 OAuth-App-Setup

**Sprint-2 Done-SP:** PQC-84 + PQC-36 + PQC-37 + PQC-38 + PQC-39 + PQC-40 + PQC-41 + PQC-42 + PQC-43 + PQC-44 + PQC-45 = **47 SP**.

Restscope: nur noch App-Stories (PQC-60 APP-7, PQC-61 APP-8).
