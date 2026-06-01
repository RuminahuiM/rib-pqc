# Evidence: PQC-31 (AUT-4) - User-Enumeration-Schutz

**Story:** PQC-31, AUT-4, "User-Enumeration-Schutz"
**Sprint:** PQC Sprint 1 (24.05.2026 bis 31.05.2026)
**Datum der Verifikation:** 30.05.2026
**Maschine:** Windows mit Docker Desktop, Git Bash (MINGW64)
**Verifiziert durch:** Dodoe (User), zusammen mit Implementation-Chat

## Was diese Evidence beweist

Der Login-Endpoint `POST /auth/local/login` liefert bei unbekannter Email und bei korrekter Email mit falschem Passwort dieselbe Response (HTTP 401, identischer Body) und annähernd dieselbe Response-Zeit. Damit ist User-Enumeration über den Login-Endpoint unterbunden. Das Sicherheits-Ziel von NFR-Sec-4 ist erfüllt.

Die Story baut direkt auf den Vorarbeiten von PQC-28 (AUT-1) und PQC-30 (AUT-3) auf, weil `PasswordHasher.dummy_verify()` bereits in PQC-28 vorbereitet wurde und der Login-Endpoint in PQC-30 die Stelle ist wo die Konstantzeit-Operation einhängt.

## Ausgefuehrte Befehle (User-Maschine)

```bash
# 1. Pre-Setup: bekannten User anlegen
echo "correct-pw" | docker compose exec -T auth-service \
    python -m admin create-user --email alice@example.com --password-stdin

# 2. Login mit unbekannter Email
curl -s -o /tmp/resp_unknown.json -w "status=%{http_code} time=%{time_total}s\n" \
    -X POST http://localhost:8080/auth/local/login \
    -H "Content-Type: application/json" \
    -d '{"email":"unknown@example.com","password":"anything"}'

# 3. Login mit bekannter Email aber falschem Passwort
curl -s -o /tmp/resp_wrongpw.json -w "status=%{http_code} time=%{time_total}s\n" \
    -X POST http://localhost:8080/auth/local/login \
    -H "Content-Type: application/json" \
    -d '{"email":"alice@example.com","password":"wrong-pw"}'

# 4. Bodies vergleichen
diff /tmp/resp_unknown.json /tmp/resp_wrongpw.json

# 5. Login mit korrektem Passwort (Happy-Path zur Kontrolle)
curl -s -X POST http://localhost:8080/auth/local/login \
    -H "Content-Type: application/json" \
    -d '{"email":"alice@example.com","password":"correct-pw"}' | jq -r '.broker_token' | head -c 60

# 6. Timing-Vergleich (10 Runs pro Case)
for i in $(seq 1 10); do
    curl -s -o /dev/null -w "%{time_total}\n" -X POST http://localhost:8080/auth/local/login \
        -H "Content-Type: application/json" \
        -d '{"email":"nobody@example.com","password":"x"}'
done > /tmp/timing_unknown.txt

for i in $(seq 1 10); do
    curl -s -o /dev/null -w "%{time_total}\n" -X POST http://localhost:8080/auth/local/login \
        -H "Content-Type: application/json" \
        -d '{"email":"alice@example.com","password":"x"}'
done > /tmp/timing_wrongpw.txt
```

## Output (Auszug)

```text
=== 2. Unknown Email ===
status=401 time=0.241s
Body: {"error":"invalid_credentials"}

=== 3. Wrong Password (bekannte Email) ===
status=401 time=0.247s
Body: {"error":"invalid_credentials"}

=== 4. Diff der Bodies ===
(leer, identisch)

=== 5. Happy-Path ===
eyJhbGciOiJNTC1EU0EtNjUiLCJ0eXAiOiJKV1QiLCJraWQiOiJhdXRoLXNp...

=== 6. Timing-Statistik ===
unknown email:    mean=0.244s  stdev=0.011s  min=0.231s  max=0.262s
wrong password:   mean=0.249s  stdev=0.013s  min=0.234s  max=0.272s
Differenz Mittel: 5 ms (<< 50 ms AC-3-Limit)
```

## AC-Verifikation

| AC | Anforderung | Beweis |
|---|---|---|
| AC-1 | Unbekannte Email gibt 401 mit Body `{"error":"invalid_credentials"}` | Curl-Szenario 2: status=401, Body exakt wie gefordert. |
| AC-2 | Korrekte Email mit falschem Passwort liefert identische Response | Curl-Szenario 3 plus `diff` in Szenario 4: identische Status, identische Body. |
| AC-3 | Response-Zeit-Differenz max. 50 ms (konstante Dummy-Hash-Operation bei nicht-existierendem User) | Timing-Statistik (10 Runs pro Case): Mittel-Differenz 5 ms, weit unter 50 ms. |
| AC-4 | Integration-Test mit beiden Cases | `tests/test_auth_router.py::test_login_unknown_email_returns_401_invalid_credentials` plus `test_login_wrong_password_returns_401_invalid_credentials`. Beide grün, plus ein paramaterized Timing-Test. |

## Code-Review-Findings (Closing-Review)

0 Must, 0 Tier-1. Keine neuen Findings, weil die Implementation minimal ist (eine if-Verzweigung im Login-Router plus `dummy_verify()`-Call). Closing-Review hat den bestehenden Login-Endpoint-Code aus PQC-30 nicht angefasst.

## Bewusste Design-Entscheidungen

- **`dummy_verify()` statt zufaellige Sleep.** Constant-Time-Argon2-Operation gegen einen festen Dummy-Hash ist robuster als eine Sleep-basierte Variante, weil Sleep durch Netz-Jitter und CPU-Last weniger gleichmaessig ist. Dummy-Hash war schon in PQC-28 (`PasswordHasher.dummy_verify`) vorbereitet.
- **Single Response-Body `{"error": "invalid_credentials"}`.** Keine separate Variante fuer "user not found" vs "wrong password". Konsistent mit OWASP-Empfehlung.
- **Keine Rate-Limit-Sonderlogik in dieser Story.** Rate-Limiting passiert in PQC-83 (SEC-5) auf Endpoint-Ebene. AUT-4 macht nur die Timing-Gleichheit, kein zaehlbasiertes Bremsen.
- **Logging.** `auth.login.failed` mit Reason-Tag (`unknown_email` oder `wrong_password`) wird im Server-Log getrennt geloggt, aber nicht in der Client-Response zurueckgegeben. Audit-Trail bleibt intakt, Client-seitige Enumeration trotzdem verhindert.

## Bewusste Limitationen

- **Timing-Test mit nur 10 Runs.** Fuer statistische Validitaet sollten mehr Runs gemacht werden. AC-3 mit 50-ms-Schranke ist grosszuegig genug dass 10 Runs als Sanity-Check reichen.
- **Keine Verteidigung gegen Side-Channel-Attacks bei Username-Vergleich.** Email-Lookup geht ueber SQLAlchemy `WHERE email = ?` und ist nicht Constant-Time. Akzeptabler Trade-off weil ueblicher SQL-Pattern.

## Files in dieser Story

- erweitert: `server/routers/auth.py` (Login-Endpoint um `dummy_verify`-Call bei unknown email erweitert)
- erweitert: `server/auth/password.py` (`PasswordHasher.dummy_verify` schon aus PQC-28 vorhanden, hier verwendet)
- erweitert: `server/tests/test_auth_router.py` (zwei neue Tests plus Timing-Test)
- neu: diese Evidence-Datei

## Folge-Tasks

- Demo D-004 (Local-Login-Pipeline) wurde nach AUT-4 erweitert mit Szenario "wrong password" und "unknown email", beide liefern identische 401-Response.

## Quellen und Referenzen

- Jira: https://rumidesigns.atlassian.net/browse/PQC-31
- Story-Bezug: NFR-Sec-4
- Vorgaenger (Done): PQC-28 (AUT-1, `dummy_verify` vorbereitet), PQC-30 (AUT-3 Login-Endpoint)
- OWASP Authentication Cheat Sheet 2024, Abschnitt "User Enumeration"
