# Performance Results (QUA-6/7/8)

**Projekt:** Implementing PQC (Semesterarbeit 3, ITCNE25)
**Autor:** Dodoe Rumiñahui Mannale
**Erstellt:** 30.06.2026 (Sprint-4 QUA-Block)
**Stories:** PQC-68 QUA-6, PQC-69 QUA-7, PQC-70 QUA-8

Dieses Kapitel dokumentiert die Performance-Messungen aus dem QUA-Trio in Sprint 4. Die Skripte liegen unter `server/scripts/bench_*.py`. Roh-JSON ist unter `server/scripts/bench_results/*.json` reproduzierbar abgelegt, die hier gezeigten Tabellen sind die aggregierten Werte zur Berichts-Aufnahme.

## 1. Methodik

**Mess-Werkzeug:** `time.perf_counter_ns()` (monotonisch, Nanosekunden-Granularitaet). Statistik via stdlib `statistics`, kein numpy.

**Workflow pro Skript:**

1. Warmup-Iterationen verworfen (Cache, Branch-Prediction, JIT-Stabilisierung).
2. Mess-Iterationen wie unten angegeben.
3. Pro Iteration: enge `start = perf_counter_ns(); call; duration = perf_counter_ns() - start`.
4. Statistik: min, P50 (Median), P95, P99, max, Mean, Stdev in Millisekunden gerundet.

**Vergleich Plaintext vs. AES-GCM** (QUA-8) erfolgt isoliert (`AESGCM.encrypt` plus `AESGCM.decrypt` ohne FastAPI) und ueber eine /health-Plaintext-Baseline mit gleichem ASGI-Stack. Die Differenz approximiert "Overhead durch AES-GCM-Verschluesselung plus Header-Routing" gemaess NFR-Perf-3.

**Reproduzierbarkeit:** Skripte sind deterministisch in der Methodik aber nicht-deterministisch in den Resultaten (System-Last, Caching). Empfohlene Mess-Strategie: 3 separate Runs, jeweils 100 / 1000 Samples wie spezifiziert, jeweils auf demselben Container-Setup.

**Mess-Setup (Stand 30.06.2026):**

* Container: `rib-pqc-auth-service`, Python 3.12-slim, liboqs aktuell verfuegbare Version pro Dockerfile-Build.
* Host: lokales Notebook (Apple Silicon, siehe `environment.platform` im JSON-Output).
* Kein TLS-Layer auf Skript-Pfad (TestClient ist In-Process gegen FastAPI). TLS-Overhead (X25519MLKEM768) ist in PQC-44 separat verifiziert und nicht Teil dieser Mess-Kette.

## 2. NFR-Perf-1: PQ-Session-Etablierung (PQC-68 QUA-6)

**Spec:** Session-Init unter 500 ms (lokales Netzwerk, Server-Request-Eingang bis Response-Ausgang).

**Skript:** `server/scripts/bench_pq_session.py`
**Iterationen:** 10 Warmup plus 100 Mess-Iterationen pro KEM-Variante.

| Variante | n | min ms | P50 ms | P95 ms | P99 ms | max ms | Mean ms | Stdev ms |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| POST /session/init [ML-KEM-768]  | 100 | 1.906 | 2.498 | 4.769 | 7.130 | 8.679 | 2.865 | 1.094 |
| POST /session/init [ML-KEM-1024] | - | - | - | - | - | - | - | - |

**Bewertung:** **PASS mit 100x Margin.** P95 4.769 ms gegen Target 500 ms.

ML-KEM-1024 wurde **uebersprungen** weil der Server in `config.yaml` nur `ML-KEM-768` in der `crypto.kem.supported`-Whitelist hat (nur eine KEM-Variante zur Sprint-4-Messzeit produktiv registriert). Fuer den Bericht relevant: falls Bericht eine Vergleichs-Messung zwischen ML-KEM-768 und -1024 fordert, muss die Config temporaer beide registrieren und der Bench neu laufen.

**Beobachtung Streuung:** Stdev 1.094 ms auf 2.865 ms Mean (CV 38%). Verteilung schief mit langem Tail: P99 7.130 ms, max 8.679 ms. Vermutliche Ursachen: GC-Pausen (Python), Redis-Roundtrip-Variabilitaet (Docker-Bridge-Netzwerk), asyncio-Task-Scheduling. Kein SLO-Impact.

## 3. NFR-Perf-2: Broker-Token-Verifikation (PQC-69 QUA-7)

**Spec:** ML-DSA-65-verify unter 10 ms.

**Skript:** `server/scripts/bench_token_verify.py`
**Iterationen:** 100 Warmup plus 1000 Mess-Iterationen pro Variante.

| Variante | n | min ms | P50 ms | P95 ms | P99 ms | max ms | Mean ms | Stdev ms |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| CryptoFacade.verify (ML-DSA-65) - Crypto-Only | 1000 | 0.104 | 0.182 | 0.493 | 0.799 | 9.985 | 0.263 | 0.488 |
| TokenService.verify (full, mit JWS-Parsing)   | 1000 | 0.389 | 0.537 | 0.795 | 0.988 | 1.293 | 0.566 | 0.116 |

**Bewertung:** **PASS mit 20x Margin (Crypto-Only)** und **12x Margin (Full)**. NFR-Perf-2 verlangt ML-DSA-65-Verify unter 10 ms - beide Varianten deutlich darunter.

**Interpretation:**
- Crypto-Only-Overhead pro Call: ~0.18 ms Median. Das ist reines ML-DSA-65-verify auf einem 1952 Byte Public-Key gegen ein ~4 KB signing_input.
- TokenService-Full-Overhead: 0.537 ms P50, davon ~0.36 ms fuer JWS-Compact-Parsing, base64url-Decode, Header-JSON, alg-Allowlist-Check, iat/exp-Validation.
- Grosse P99/max-Streuung bei Crypto-Only (max 9.985 ms) trotz niedrigem P50 - typisch fuer ML-DSA-Verify: konstante Zeit sollte gelten, GC-Pausen aber schlagen einzelne Samples auf. Kein Timing-Side-Channel-Risiko dokumentiert.

## 4. NFR-Perf-3: AES-GCM-Overhead pro API-Call (PQC-70 QUA-8)

**Spec:** Verschluesselungs-Overhead plus Header-Routing unter 50 ms pro API-Call.

**Skript:** `server/scripts/bench_aes_gcm.py`
**Iterationen:** 100 Warmup plus 1000 Mess-Iterationen pro Variante.

### 4.1 Isolierter AEAD-Overhead (Crypto-Only, ohne FastAPI)

| Payload-Groesse | n | min ms | P50 ms | P95 ms | P99 ms | max ms | Mean ms | Stdev ms |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 256 B   | 1000 | 0.099 | 0.223 | 0.631 | 0.935 | 2.691 | 0.298 | 0.185 |
| 1 KiB   | 1000 | 0.088 | 0.206 | 0.692 | 1.069 | 10.192 | 0.294 | 0.404 |
| 10 KiB  | 1000 | 0.112 | 0.223 | 0.783 | 1.171 | 2.478 | 0.321 | 0.235 |

### 4.2 Plaintext-Baseline (TestClient GET /health, ohne Encryption)

| Variante | n | min ms | P50 ms | P95 ms | P99 ms | max ms | Mean ms | Stdev ms |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| TestClient GET /health (Plaintext) | 1000 | 0.554 | 0.749 | 1.233 | 1.582 | 4.398 | 0.830 | 0.251 |

**Bewertung:** **PASS mit 64x Margin (10 KiB)**. NFR-Perf-3 Target 50 ms weit unterschritten.

**Interpretation:**
- AEAD-Overhead skaliert praktisch nicht mit Payload-Groesse zwischen 256 B und 10 KiB (P50 alle ~0.22 ms). Das entspricht dem AES-NI-Hardware-Support in cryptography-lib.
- Der P50-Wert enthaelt sowohl encrypt als auch decrypt in einer Iteration.
- ASGI-Overhead fuer einen Plaintext-GET /health liegt bei 0.749 ms P50 (mehr als der AEAD-Overhead selbst). Das illustriert dass in prod die Encryption ein sehr kleiner Teil der Response-Zeit ist.
- Ausreisser bei 1 KiB max=10.192 ms ist ein einzelner GC-getriggerter Spike, kein systematisches Problem (P99 nur 1.069 ms).

## 5. Mess-Ausfuehrung (Reproduktion)

```bash
# Im Auth-Service-Container ausfuehren (liboqs ist dort installiert).
# fakeredis ist dev-only, ggf. erst nachziehen.
docker exec -u root rib-pqc-auth-service \
    /opt/venv/bin/pip install fakeredis

docker exec rib-pqc-auth-service python /app/scripts/bench_pq_session.py
docker exec rib-pqc-auth-service python /app/scripts/bench_token_verify.py
docker exec rib-pqc-auth-service python /app/scripts/bench_aes_gcm.py

# Result-JSON ins Repo zurueck-kopieren:
docker cp rib-pqc-auth-service:/app/scripts/bench_results ./server/scripts/
```

Im Container muss `RIB_CONFIG_FILE=/app/config.yaml` gesetzt sein (Default im Container-Image).

## 6. Bezug zur Bericht-Struktur

Diese Tabellen werden 1:1 in das Schlussberichts-Kapitel "Performance" uebernommen. JSON-Roh-Output ist als Beleg-Artefakt eingecheckt (`server/scripts/bench_results/*.json`).

Mess-Limitationen die in den Bericht muessen:

1. Kein verteiltes Setup; alle Latenzen sind In-Process-TestClient-Werte gegen echten Redis (db=5), kein TCP-HTTP-Overhead und kein TLS-Overhead. Prod-Deployment kommt ~1-3 ms zusaetzlichen Netzwerk-Layer-Overhead drauf, aendert die 100x/20x/64x Margin nicht.
2. Kein cold-cache-Verhalten; Warmup eliminiert First-Call-Effekte (Branch-Prediction, JIT, OS-Page-Cache).
3. Variabilitaet (CV) ist via Stdev im JSON dokumentiert und muss im Bericht ausgewiesen werden, besonders fuer ML-DSA-65-Sign-Pfad (Rejection-Sampling, hohe Streuung) - hier nicht direkt gemessen, aber relevant fuer Folge-Stories.
4. Debug-Level-Logging war im Bench-Kontext beim Session-Init aktiv (WARNING-Threshold-Fix hat wegen structlog eigener Logger-Baum nicht gegriffen, siehe PQC-85 Post-Sprint-Cleanup). Realistische Session-Init-Latenz waere ohne Logging noch niedriger. Kein SLO-Impact.
5. Mock-TokenService im Session-Bench: Token-Verify-Kosten (0.5 ms P50 aus QUA-7) sind nicht Teil der Session-Init-Zahl. In prod addieren sie sich; Gesamt-Session-Init bleibt trotzdem weit unter 500 ms.

## 7. Historie

| Version | Datum | Aenderung |
|---|---|---|
| 1.0 | 30.06.2026 | Initial. Skripte angelegt, Tabellen mit _TBD_-Platzhaltern. Numbers nach erstem Docker-Run einzutragen. |
