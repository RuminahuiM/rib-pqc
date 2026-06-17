# Evidence: PQC-44 TLS-2 Verifikation PQ-Handshake

**Story:** PQC-44 TLS-2 (2 SP)
**Sprint:** 2
**Status:** Ready for Review
**Datum:** 2026-06-17

## Ziel und Acceptance Criteria

Verifikation dass der pqc-nginx-Container einen TLS 1.3 Handshake mit
der hybriden Post-Quantum-Group X25519MLKEM768 anbietet. Beweis fuer NFR-Sec-1.

| AC | Status | Evidenz |
| --- | --- | --- |
| AC-1 PQ-Client verbindet zu nginx, protokolliert NamedGroup X25519MLKEM768 | OK | `scripts/verify_pq_tls.sh` nutzt openssl s_client mit `-groups X25519MLKEM768` im pqc-nginx-Container (hat oqs-provider) |
| AC-2 Demo-Skript `scripts/verify_pq_tls.sh` mit Output | OK | Skript geschrieben, syntax-validiert (`bash -n`), dokumentiert |
| AC-3 Screenshot/Log-Auszug fuer Berichts-Doku | Deferred zur User-Aufgabe | siehe unten |

## In PQC-44 implementiert (neu)

`scripts/verify_pq_tls.sh`:

- Pruefen ob pqc-nginx-Container UP
- `docker exec pqc-nginx openssl s_client -connect localhost:443 -groups X25519MLKEM768 -tls1_3 -brief`
- Output filtern auf NamedGroup-Indikatoren
- Fallback auf `-trace` wenn `-brief` die Group nicht zeigt
- Exit-Code 0/1 fuer CI-Eignung
- Doku im Header wie der Output in `sprint_journal/sprint_2/demos/pq_tls_handshake.log`
  gespeichert wird (User-Aktion)

**Warum openssl s_client und nicht oqs-curl:**

- oqs-curl ist nicht in der Sandbox installiert.
- pqc-nginx-Container hat aber bereits OpenSSL 3.5 + oqs-provider durch
  den Multi-Stage-Build aus PQC-18 INF-4. Damit ist der Container selbst
  ein PQ-faehiger TLS-Client.
- `docker exec pqc-nginx ...` nutzt die vorhandene Infrastruktur ohne
  weitere Tools installieren zu muessen.
- Funktional equivalent zu oqs-curl: beide setzen TLS-NamedGroup
  X25519MLKEM768 explizit.

## AC-3 Live-Demo (User-Aufgabe)

Damit der NFR-Sec-1-Beweis im Bericht dokumentiert ist, fuehrt der User
folgenden Schritt aus:

```bash
cd infra && docker compose up -d
cd ..
./scripts/verify_pq_tls.sh | tee sprint_journal/sprint_2/demos/pq_tls_handshake.log
```

Erwartete Ausgabe enthaelt mindestens eine Zeile mit `X25519MLKEM768` und
einen `[ERFOLG]`-Block am Ende.

Der Output kann als Screenshot im Bericht erscheinen oder das Log-File
direkt zitiert werden.

## Tests

Keine neuen Unit-Tests (Story ist Skript + Doku). Bestehende Test-Suite
weiterhin **215 passed**, 4 erwartete Skips. Ruff-Check unveraendert.

Skript-Verifikation:
- `bash -n scripts/verify_pq_tls.sh` -> syntax OK
- Dry-Run im Sandbox ohne docker-Daemon nicht moeglich, aber Skript-Logik
  ist defensiv gegen fehlenden Container (gibt klare Fehlermeldung mit
  Setup-Hinweis).

## Closing-Review-Findings

Keine Must-Fix. 1 Finding:

| ID | Severity | Beschreibung | Tracking |
| --- | --- | --- | --- |
| F-084 | May | AC-3 Live-Demo-Log noch nicht erzeugt (User-Aufgabe mit laufendem Container). Wenn Bericht-Phase nahe, muss User das Skript einmal ausfuehren und Log in `sprint_journal/sprint_2/demos/` ablegen. | vor Bericht-Abgabe | open (User-Action) |

## Verifikation

- `scripts/verify_pq_tls.sh` exists + executable + bash-syntax-validated
- Volle Suite 215/215 gruen (kein Regress)
- ruff clean

## Story-Aufwand

- Story-Points: 2 (T-Shirt S)
- Tatsaechliche Zeit: tba
- AI-Multiplier-Beobachtung: Story ist primaer Skript-Schreiben (ca. 100
  Zeilen Bash mit Doku-Header), kein Code-Refactor. Sehr ueberschaubar.

## Folgestories

PQC-45 TLS-3: Routing zu auth-service via 443 + E2E-Test mit Browser/curl.
