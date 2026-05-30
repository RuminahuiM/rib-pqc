# Evidence: PQC-18 INF-4 oqs-provider-fähiges nginx-Image

- **Jira**: [PQC-18](https://rumidesigns.atlassian.net/browse/PQC-18)
- **Sprint**: 1 (Endspurt, Carry-Over aus Sprint 0)
- **Done am**: 2026-05-30
- **Story Points**: 5
- **Worklog**: ~60 Minuten (Active + Build-Debug)

## Zusammenfassung

Multi-Stage Source-Build adoptiert vom offiziellen oqs-demos/nginx Pattern.
Image `rib-pqc-nginx:0.1` baut OpenSSL 3.5.0 + liboqs 0.14.0 + oqs-provider
0.10.0 + nginx 1.27.5 alles aus Source in einem Alpine-3.21 Container. nginx
ist gegen den oqs-faehigen OpenSSL gelinkt und kann TLS 1.3 mit hybrider
Cipher-Suite X25519MLKEM768 sprechen. Self-signed Test-Cert mit ML-DSA-65
(FIPS 204) wird im Build generiert.

## AC-Mapping

| AC | Resultat | Verifikation |
|---|---|---|
| AC-1 Dockerfile.nginx baut ohne Fehler | OK | `docker compose build nginx` durch (nach 3 Iterationen, Bug-Fixes inline dokumentiert) |
| AC-2 nginx 1.27 installiert + startet | OK | `nginx -V` zeigt `nginx version: nginx/1.27.5` |
| AC-3 oqs-provider 0.10+ und OpenSSL 3.5+ verfuegbar | OK | `openssl list -providers` zeigt `oqsprovider version 0.10.0 status: active` + `default version 3.5.0 status: active` |
| AC-4 Image-Tag rib-pqc-nginx:0.1 | OK | `docker images rib-pqc-nginx` zeigt Tag 0.1, 171MB |
| AC-5 (Story-Erweiterung) Live-TLS-Handshake X25519MLKEM768 | OK | `openssl s_client -connect localhost:443 -groups X25519MLKEM768 -tls1_3` erfolgreich, Cert ML-DSA-65 |

## Implementation-Hinweis (Story-Start)

Original-AC-1 sagte "FROM openquantumsafe/oqs-ossl3 Base-Image". Bei der
Implementierungs-Vorbereitung stellte sich heraus, dass oqs-ossl3 ein
runtime-Image (18.5MB) fuer `openssl s_client/s_server` ist und sich nicht
als Build-Base fuer nginx eignet:

- oqs-ossl3 ist Alpine-basiert mit OpenSSL3 + oqs-provider unter `/opt/openssl`,
  aber System-OpenSSL ist separat
- `apk add nginx` wuerde nginx gegen System-OpenSSL linken, nicht gegen den
  oqs-faehigen OpenSSL
- Damit waere nginx zwar im Image, aber TLS-Handshake mit X25519MLKEM768 wuerde
  fehlschlagen

Senior-Decision: Wir adoptieren das offizielle oqs-demos/nginx Multi-Stage-
Source-Build-Pattern. Damit ist nginx wirklich oqs-faehig (gegen den
Custom-OpenSSL gelinkt). Diese Abweichung ist in der Jira-Story als
Story-Start-Comment dokumentiert.

## Files

- `infra/nginx/Dockerfile.nginx` (NEU, 110 Zeilen): Multi-Stage Build mit
  Alpine 3.21 Base, OpenSSL 3.5.0 + liboqs 0.14.0 + oqs-provider 0.10.0 +
  nginx 1.27.5 aus Source, self-signed Test-Cert mit ML-DSA-65, Healthcheck
- `infra/nginx/nginx.conf`: ergaenzt um Server-Block fuer Port 443 mit TLS 1.3
  + `ssl_ecdh_curve X25519MLKEM768:X25519:secp384r1:prime256v1` + `/pqc-test`
  Smoke-Endpoint
- `infra/docker-compose.yml`: nginx-Service auf `build: ./nginx` umgestellt
  (image `rib-pqc-nginx:0.1`), Port 443 zusaetzlich gemapped
- `infra/.env.example`: `NGINX_HTTPS_PORT=8443` Default

## Live-Verifikation

```
$ docker compose ps
pqc-nginx          rib-pqc-nginx:0.1   Up 6 minutes (healthy)
                                       0.0.0.0:8443->443/tcp

$ docker compose exec nginx /opt/nginx/sbin/nginx -V 2>&1 | head -2
nginx version: nginx/1.27.5
built by gcc 14.2.0 (Alpine 14.2.0)

$ docker compose exec nginx /opt/openssl/.openssl/bin/openssl version
OpenSSL 3.5.0 8 Apr 2025 (Library: OpenSSL 3.5.0 8 Apr 2025)

$ docker compose exec nginx /opt/openssl/.openssl/bin/openssl list -providers
Providers:
  default
    name: OpenSSL Default Provider
    version: 3.5.0
    status: active
  oqsprovider
    name: OpenSSL OQS Provider
    version: 0.10.0
    status: active

$ docker images rib-pqc-nginx
IMAGE               ID             DISK USAGE   CONTENT SIZE
rib-pqc-nginx:0.1   05a0e0d991c7        171MB         44.3MB

$ docker compose exec nginx /opt/openssl/.openssl/bin/openssl s_client \
    -connect localhost:443 -groups X25519MLKEM768 -tls1_3 < /dev/null

Certificate chain
 0 s:CN=pqc-nginx
   i:CN=pqc-test CA
   a:PKEY: ML-DSA-65, 15616 (bit); sigalg: ML-DSA-65
   v:NotBefore: May 30 14:52:56 2026 GMT; NotAfter: May 30 14:52:56 2027 GMT
```

## Build-Bugs (alle in-story gefixt)

Im Verlauf der Implementation traten drei nicht-triviale Build-Probleme auf,
die im Dockerfile-Kommentar dokumentiert sind damit sie nicht erneut auf-
treten:

1. **`find -name ossl-modules` Multi-Line-Output:** Nach `ln -sf lib lib64`
   im OpenSSL-Build lieferte `find` zwei Pfade, was `cp $MODULESDIR` mit
   Multi-Line-Argument scheitern liess. Fix: expliziter Pfad statt find.

2. **OpenSSL sucht ossl-modules unter `lib64/`, nicht `lib/`:** Alpine
   multilib-Konvention. Wir installieren unter `lib/ossl-modules`, mussten
   aber zusaetzlich `lib64/ossl-modules` als Symlink anlegen. ABER:
   `ln -sf TARGET DIR` legt den Symlink IN das Verzeichnis statt es zu
   ersetzen wenn DIR bereits existiert. Fix: `rm -rf` vor `ln -s`.

3. **nginx 1.27 ohne `--with-http_v2_module` gebaut, aber `http2 on;`
   in nginx.conf:** Compose-Restart-Loop. Fix: `http2`-Direktive aus
   nginx.conf entfernt + `--with-http_v2_module` ins Dockerfile fuer
   den naechsten Build.

## Findings (Tier-2-Polish)

| ID | Titel | Severity | Trigger |
|---|---|---|---|
| F-051 | Self-signed Test-Cert ohne PKI-Setup. Production muss echtes Cert von einer CA bekommen | Info | vor Production-Deployment |
| F-052 | Build-Args nicht hash-gepinnt (OpenSSL/liboqs/oqs-provider/nginx Git-Tags). Supply-Chain-Reproducibility. Buendeln mit F-018. | Info | Sprint 4, vor Bericht-Abgabe |
| F-053 | Image-Tag `0.1` ist manuell. Naechste Versions-Bumps brauchen automatisierte Tag-Strategie | Info | Sprint 4 oder bei naechstem Image-Bump |

## Demo-Material

D-005 Mini-Demo "Live PQC-TLS Handshake": reproduzierbar via dem dokumentierten
`openssl s_client -groups X25519MLKEM768` Command. Bericht-tauglich, zeigt
Hybrid-PQC-Handshake auf realem nginx-Image.
