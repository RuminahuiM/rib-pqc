# Demo D-007: PQ-TLS-Handshake Verifikation via verify_pq_tls.sh

**Datum:** 17.06.2026 (Sprint 2)
**Trigger:** Sprint-2-Closure-Material plus reproduzierbare Verifikation für Mentor-Termin und Schlussbericht
**Bezug:** PQC-44 TLS-2 (AC-2 plus AC-3), NFR-Sec-1
**Sprint:** PQC Sprint 2
**Maschine:** Windows mit Docker Desktop plus pqc-nginx-Container

## Was diese Demo beweist

Der Auth-Service-Container (pqc-nginx mit oqs-provider) bietet TLS 1.3 mit der hybriden Key-Exchange-Group **X25519MLKEM768** (gemäss RFC-Draft `draft-kwiatkowski-tls-ecdhe-mlkem`, kombiniert klassisches X25519 mit Post-Quantum ML-KEM-768) auf Port 443 an. Damit ist NFR-Sec-1 (Post-Quantum-gesicherter Transport) für den Server-zu-Browser-Pfad erfüllt.

Die Demo ist als reproduzierbares Shell-Skript implementiert (`scripts/verify_pq_tls.sh`), das den Handshake durchführt und das Ergebnis ausgibt. Geeignet für Mentor-Termin (Live-Vorführung in 30 Sekunden) und für Bericht-Doku (Output-Log als Beweis).

## Voraussetzungen

- Docker Desktop läuft.
- Container-Stack ist up: `docker compose -f infra/docker-compose.yml up -d`.
- `pqc-nginx`-Container ist `Up (healthy)`.

## Reproduzierbare Befehls-Folge

```bash
# Container-Status prüfen
docker compose -f infra/docker-compose.yml ps

# Demo ausführen
./scripts/verify_pq_tls.sh

# Optional: Output für Bericht-Material in Log-Datei speichern
./scripts/verify_pq_tls.sh | tee sprint_journal/sprint_2/demos/pq_tls_handshake.log
```

## Was das Skript macht

1. **Container-Check:** Verifiziert dass `pqc-nginx` läuft, bricht sonst mit Fehlermeldung und Start-Anweisung ab.
2. **TLS-Handshake mit forced Hybrid-Group:** Führt im Container selbst `openssl s_client` aus mit den Flags:
   - `-connect localhost:443` (gegen den eigenen nginx)
   - `-groups X25519MLKEM768` (zwingt die hybride PQC-Gruppe)
   - `-tls1_3` (kein Downgrade auf TLS 1.2)
   - `-servername localhost` (SNI)
   - `-brief` (kompakte Ausgabe)
3. **Output-Verifikation:** Greppt im Output nach der `X25519MLKEM768`-Group oder fallback im detaillierten Trace.
4. **Exit-Code:** 0 bei Erfolg, 1 bei Fehler.

Der Container hat OpenSSL 3.5 plus oqs-provider installiert und kennt die hybride Group nativ.

## Erwarteter Output (Auszug, repräsentativ)

```text
==========================================
PQC-44 TLS-2 - PQ-TLS Handshake Verifikation
==========================================
Container: pqc-nginx
Target:    localhost:443
Group:     X25519MLKEM768
Datum:     2026-06-17T...

[OK] Container 'pqc-nginx' ist up.

[INFO] Starte TLS-Handshake mit forced group X25519MLKEM768 ...

--- s_client Output ---
CONNECTION ESTABLISHED
Protocol version: TLSv1.3
Ciphersuite: TLS_AES_256_GCM_SHA384
Server certificate
...
Negotiated TLS1.3 group: X25519MLKEM768
--- /s_client Output ---

[OK] Hybrid-Group X25519MLKEM768 wurde im Handshake verhandelt.

==========================================
[ERFOLG] PQ-TLS-Handshake mit X25519MLKEM768 verifiziert.
NFR-Sec-1 erfuellt.
==========================================
```

## AC-Mapping für PQC-44 (TLS-2)

| AC | Anforderung | Beweis durch diese Demo |
|---|---|---|
| AC-1 | oqs-curl oder vergleichbarer PQ-Client baut Connection mit `X25519MLKEM768` auf | openssl s_client im Container mit `-groups X25519MLKEM768` |
| AC-2 | Demo-Skript `scripts/verify_pq_tls.sh` mit dokumentiertem Output | Diese Datei plus das Skript selbst |
| AC-3 | Screenshot oder Log-Auszug für die Berichts-Doku gesichert | Output kann via `tee` in Log-Datei umgeleitet werden |

## Wichtige Einordnung (Sprint-2-Befund)

Diese Demo zeigt den **Backend-PQC-TLS-Pfad gegen Browser-fähige Clients** (Chrome, oqs-curl, openssl s_client im Container). Die hybride Group X25519MLKEM768 ist auf der Server-Seite aktiv und verhandlungsfähig.

**Wichtige Limitation für den Mobile-Client-Pfad:** React-Native / Expo-Go nutzen den System-TLS-Stack des Betriebssystems (Apple Network Framework auf iOS, Conscrypt auf Android). Diese System-TLS-Stacks unterstützen X25519MLKEM768 noch nicht (Stand Juni 2026), weil ML-KEM-768 im Apple/Google TLS-Library-Ökosystem noch nicht ausgerollt ist. Browser wie Chrome bringen ihren eigenen TLS-Stack (BoringSSL mit ML-KEM-Support) mit und können daher mit dem Backend verbinden. Diese Limitation ist als R-T08 im Risk Register dokumentiert.

Für den Sprint-2-Goal-Demo ist diese Demo zusammen mit der Browser-zu-Backend-Demo (Chrome plus Federation-Login) der Beweis dass das Backend produktiv PQC-TLS spricht. Der vollständige Mobile-zu-Backend-PQC-TLS-Pfad würde ein Custom-Native-Modul mit eigener liboqs-basierter TLS-Library erfordern (Production-Polish, nicht im Sprint-Scope).

## Files in dieser Demo

- `scripts/verify_pq_tls.sh` (das Verifikations-Skript)
- `infra/docker-compose.yml` (Container-Setup mit pqc-nginx)
- `infra/nginx/nginx.conf` (TLS-Konfiguration mit hybrid-group)
- diese Demo-Datei

## Quellen und Referenzen

- RFC-Draft `draft-kwiatkowski-tls-ecdhe-mlkem` (Hybrid-KEM in TLS 1.3)
- FIPS 203 (ML-KEM Final Standard)
- oqs-provider Project (Open Quantum Safe)
- OpenSSL 3.5 Release Notes (Provider-Plugin-Support)

## Folge-Verwendung

- Mentor-Termin Sprint-2-Closure oder Sprint-3-Start: Live-Demo in 30 Sekunden.
- Schlussbericht: Output-Log als Anhang, `verify_pq_tls.sh` als reproduzierbarer Beweis.
- Schluss-Präsentation: Screenshot des Erfolgs-Outputs als Slide.
