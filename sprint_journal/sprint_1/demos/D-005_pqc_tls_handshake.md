# Demo D-005: PQC-TLS-Handshake X25519MLKEM768

**Demo-ID:** D-005
**Datum:** 30.05.2026
**Stories integriert:** PQC-17 (INF-3 nginx Reverse-Proxy), PQC-18 (INF-4 oqs-provider-faehiges nginx-Image)
**Maschine:** Windows mit Docker Desktop, Git Bash (MINGW64)
**Vorgaenger-Demos:** D-001 bis D-004 (Application-Layer). D-005 ist die erste Transport-Layer-Demo.
**Status:** funktional, Mentor-tauglich. Belegt die Transport-Ebene (Ebene 1) der Architektur.

## Was diese Demo zeigt

Live-Beweis, dass die Transport-Ebene des Systems einen hybriden Post-Quantum-TLS-Handshake sprechen kann. Das Custom-nginx-Image `rib-pqc-nginx:0.1` baut OpenSSL 3.5.0, liboqs 0.14.0, oqs-provider 0.10.0 und nginx 1.27.5 aus Source und ist gegen den oqs-faehigen OpenSSL gelinkt. nginx terminiert TLS 1.3 mit der hybriden Schluesseltausch-Gruppe X25519MLKEM768 und praesentiert ein self-signed Server-Zertifikat, das mit ML-DSA-65 (FIPS 204) signiert ist.

Diese Demo ist bewusst von D-004 getrennt: D-004 (Local-Login-Pipeline) laeuft ueber HTTP und zeigt die Application-Ebene (ML-DSA-65-signierte Token). D-005 zeigt die Transport-Ebene (hybrider PQ-TLS-Handshake). Zusammen decken die beiden Demos beide Post-Quantum-Ebenen der Architektur ab.

## Ausgefuehrte Befehle

```bash
# 0. Container-Status pruefen
docker compose ps

# 1. nginx-Version verifizieren
docker compose exec nginx /opt/nginx/sbin/nginx -V 2>&1 | head -2

# 2. OpenSSL-Version (muss 3.5+ sein fuer PQC-Hybrid)
docker compose exec nginx /opt/openssl/.openssl/bin/openssl version

# 3. oqs-provider als aktiver OpenSSL-Provider
docker compose exec nginx /opt/openssl/.openssl/bin/openssl list -providers

# 4. Live-Handshake mit X25519MLKEM768 erzwingen
docker compose exec nginx /opt/openssl/.openssl/bin/openssl s_client \
    -connect localhost:443 -groups X25519MLKEM768 -tls1_3 < /dev/null

# 5. Smoke-Endpoint ueber TLS (gibt ausgehandelte Cipher zurueck)
#    von der Host-Seite gegen den gemappten Port 8443
curl -k https://localhost:8443/pqc-test
```

## Output (gekuerzt)

```text
# === Schritt 0: Container-Status ===
$ docker compose ps
pqc-nginx          rib-pqc-nginx:0.1   Up 6 minutes (healthy)
                                       0.0.0.0:8443->443/tcp

# === Schritt 1: nginx-Version ===
nginx version: nginx/1.27.5
built by gcc 14.2.0 (Alpine 14.2.0)

# === Schritt 2: OpenSSL-Version ===
OpenSSL 3.5.0 8 Apr 2025 (Library: OpenSSL 3.5.0 8 Apr 2025)

# === Schritt 3: aktive Provider ===
Providers:
  default
    name: OpenSSL Default Provider
    version: 3.5.0
    status: active
  oqsprovider
    name: OpenSSL OQS Provider
    version: 0.10.0
    status: active

# === Schritt 4: Live-Handshake X25519MLKEM768 ===
Certificate chain
 0 s:CN=pqc-nginx
   i:CN=pqc-test CA
   a:PKEY: ML-DSA-65, 15616 (bit); sigalg: ML-DSA-65
   v:NotBefore: May 30 14:52:56 2026 GMT; NotAfter: May 30 14:52:56 2027 GMT
```

## Interpretation

| Beleg | Bedeutung |
|---|---|
| **oqsprovider status: active** | OpenSSL 3.5.0 hat den oqs-provider geladen. Ohne ihn koennte nginx die hybriden PQ-Gruppen gar nicht anbieten. Beweis, dass das Image korrekt gebaut und gelinkt ist. |
| **Handshake mit -groups X25519MLKEM768 erfolgreich** | Der Server akzeptiert die hybride Gruppe und der TLS-1.3-Handshake kommt zustande. X25519MLKEM768 kombiniert das klassische X25519 mit dem post-quantum ML-KEM-768. Der Sitzungsschluessel ist nur dann unsicher, wenn beide Verfahren gebrochen werden. |
| **sigalg: ML-DSA-65** | Das Server-Zertifikat ist mit ML-DSA-65 (FIPS 204) signiert, also auch die Authentisierung des Servers ist post-quantum. PKEY 15616 bit ist die ML-DSA-65-Schluesselgroesse. |
| **TLS 1.3 only** | Aeltere TLS-Versionen unterstuetzen die hybriden PQ-KEM-Gruppen technisch nicht. Der Server-Block erzwingt deshalb TLSv1.3. |

## Was D-005 bedeutet und was nicht

Bedeutet: Die Infrastruktur fuer Post-Quantum-Transport-Sicherheit steht und funktioniert auf einem realen nginx-Image. Der Handshake ist hybrid (klassisch plus PQ) und das Server-Cert ist PQ-signiert.

Bedeutet nicht: Der Auth-Service ist ueber Port 443 noch nicht angebunden. Aktuell terminiert nginx auf 443 nur die Smoke-Endpoints `/pqc-test` und `/health`. Das Routing der echten Auth-Endpoints ueber TLS kommt in Sprint 2 (PQC-45 TLS-3). Ausserdem ist das Zertifikat self-signed (Test-Cert), eine echte CA-Anbindung ist Production-Thema (Finding F-051). Und: dieser TLS-Schutz greift zwischen Client und nginx, nicht auf dem mobilen Pfad, weil iOS und Android die TLS-Gruppen nicht kontrollieren lassen. Genau deshalb gibt es die Application-Layer-PQ als zweite Ebene.

## Bewusste Limitations und Findings

- F-051: Self-signed Test-Cert ohne PKI-Setup. Production braucht ein echtes Cert von einer CA. Trigger: vor Production-Deployment.
- F-052: Build-Args (OpenSSL, liboqs, oqs-provider, nginx Git-Tags) nicht hash-gepinnt. Supply-Chain-Reproducibility. Trigger: Sprint 4, vor Bericht-Abgabe.
- F-053: Image-Tag `0.1` ist manuell vergeben. Trigger: Sprint 4 oder naechster Image-Bump.

## Mentor-Hinweis fuer 01.06.2026 Termin

Diese Demo ist der Transport-Ebenen-Beleg neben D-004. Reproduzierbar live in unter einer Minute via dem dokumentierten `openssl s_client -groups X25519MLKEM768`-Command. Bewertungs-relevant: zeigt einen echten hybriden PQ-TLS-Handshake plus ein ML-DSA-65-signiertes Server-Cert auf einem aus Source gebauten nginx, nicht in einer Simulation. Gutes Material, um die Zwei-Ebenen-Architektur konkret zu machen.

## Quellen und Referenzen

- Story PQC-18: https://rumidesigns.atlassian.net/browse/PQC-18
- Evidence: `sprint_journal/sprint_1/evidence/PQC-18_INF-4_oqs_nginx.md`
- Config: `infra/nginx/nginx.conf` (Server-Block Port 443), `infra/nginx/Dockerfile.nginx`
- IETF Draft: draft-ietf-tls-ecdhe-mlkem (Hybrid ECDHE-MLKEM Key Agreement for TLS 1.3, Stand 2026 noch kein RFC)
- NIST FIPS 203 (ML-KEM), FIPS 204 (ML-DSA)
