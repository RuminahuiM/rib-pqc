"""PQC-68 QUA-6: Performance-Benchmark fuer die PQ-Session-Etablierung.

**NFR-Perf-1:** UC-4 (POST /session/init) darf auf lokalem Netzwerk nicht
laenger als 500 ms dauern (Server-Request-Eingang bis Response-Ausgang).

**Mess-Strategie (E2E via TestClient, gemaess User-Pick 30.06.2026):**

* Eine minimale FastAPI-App mit echter ``CryptoFacade`` (liboqs-basiert) und
  **echtem Redis** (db=5, per FLUSHDB isoliert). Token-Verify ist via
  Mock-TokenService gekuerzt, weil der Token-Pfad in QUA-7 separat gemessen
  wird und hier nicht in der Session-Init-Messung mit-anfaellt.
* Warum echter Redis statt fakeredis: prod-realistische Netzwerk-Roundtrip-
  Latenz fuer SETEX + GET, keine In-Process-Shortcuts. Best-Practice fuer
  Performance-Benchmarks (F-136).
* Client erzeugt vor jeder Iteration ein frisches ML-KEM-Keypair (Client-Cost
  ist im **Berichts-Kommentar** dokumentiert, NICHT Teil der Server-Latenz).
* 10 Warmup-Iterations (Cache/Branch-Prediction stabilisieren) plus 100
  Mess-Iterations gemaess Akzeptanzkriterium.
* Pro Iteration: ``time.perf_counter_ns()`` rund um den ``client.post`` call.

**Output:** ``bench_results/pq_session_init.json`` + Stdout-Tabelle.

Beide ML-KEM-768 und ML-KEM-1024 werden gemessen (Algorithmus-Vergleich
fuer den Bericht).
"""
from __future__ import annotations

import asyncio
import base64
import sys
from pathlib import Path
from typing import Any

# Ermoeglicht direkten Aufruf: ``python -m server.scripts.bench_pq_session``
# UND ``python server/scripts/bench_pq_session.py`` (aus dem Container).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from _bench_common import (  # type: ignore[import-not-found]
    print_table,
    summarize,
    time_block_ns,
    write_result_json,
)

WARMUP_ITERATIONS = 10
MEASURE_ITERATIONS = 100


def _bootstrap_facade() -> Any:
    """Initialisiert echte CryptoFacade ueber den Registry-Bootstrap.

    Imports inline, damit der Skript-Aufruf ohne FastAPI-Lifespan funktioniert.
    Settings werden ueber ``get_settings()`` aus der via ``RIB_CONFIG_FILE``
    referenzierten YAML geladen (analog main.py).
    """
    from config import get_settings  # noqa: PLC0415
    from crypto.facade import CryptoFacade  # noqa: PLC0415
    from crypto.registry import CryptoRegistry  # noqa: PLC0415
    from crypto.registry_init import init_crypto_registry  # noqa: PLC0415

    settings = get_settings()
    registry = CryptoRegistry()
    init_crypto_registry(
        registry,
        kem_supported=settings.crypto.kem.supported,
        signature_supported=settings.crypto.signature.supported,
    )
    # Frisches Ephemeral-Keypair fuer den Benchmark (kein Disk-Read).
    sig_alg = settings.crypto.signature.default
    pub, priv = registry.get_signature(sig_alg).keygen()
    active_kid = settings.crypto.signature.get_active_kid()
    return CryptoFacade(
        registry=registry,
        default_signature_alg=sig_alg,
        signing_kid=active_kid,
        signing_secret_key=priv,
        verifying_keys_by_kid={active_kid: pub},
    )


def _build_app(facade: Any, session_service: Any) -> Any:
    """Baut eine minimale FastAPI-App mit Session-Router + Mocks."""
    from fastapi import FastAPI  # noqa: PLC0415

    from config import SessionConfig  # noqa: PLC0415
    from routers.session import router as session_router  # noqa: PLC0415

    class _NoopToken:
        def verify(self, token_str: str) -> dict[str, Any]:
            del token_str
            return {"sub": "bench-user", "iss": "bench", "iat": 1, "exp": 2**31}

    app = FastAPI()

    class _Settings:
        session = SessionConfig()

    app.state.crypto_facade = facade
    app.state.session_service = session_service
    app.state.token_service = _NoopToken()
    app.state.settings = _Settings()
    app.include_router(session_router)
    return app


async def _run_bench(kem_alg: str, facade: Any, redis_url: str) -> list[int]:
    """Fuehrt Warmup + Mess-Iterations gegen die TestClient-App aus.

    Nutzt echten Redis in db=5 (per FLUSHDB isoliert). Liefert Latenz-Samples
    in Mikrosekunden (us).
    """
    from httpx import ASGITransport, AsyncClient  # noqa: PLC0415
    import redis.asyncio as aioredis  # noqa: PLC0415

    from services.session_service import SessionService  # noqa: PLC0415

    redis_client = aioredis.from_url(redis_url, decode_responses=False)
    try:
        await redis_client.flushdb()  # sauberer Start-State fuer den Bench
        session_service = SessionService(redis_client=redis_client, ttl_seconds=900)
        app = _build_app(facade, session_service)
        transport = ASGITransport(app=app)

        samples_us: list[int] = []
        async with AsyncClient(transport=transport, base_url="http://bench") as client:
            for i in range(WARMUP_ITERATIONS + MEASURE_ITERATIONS):
                # Frischer Client-Public-Key pro Iteration (FIPS 203 sieht keinen
                # Cache vor, jede Session hat ihr eigenes Keypair).
                pk, _sk = facade.kem_keygen(kem_alg)
                pk_b64 = base64.urlsafe_b64encode(pk).decode("ascii").rstrip("=")
                start = time_block_ns()
                resp = await client.post(
                    "/session/init",
                    headers={"Authorization": "Bearer bench-token"},
                    json={"kem_alg": kem_alg, "encapsulation_key": pk_b64},
                )
                duration_us = (time_block_ns() - start) // 1000
                if resp.status_code != 200:
                    msg = f"Unexpected response {resp.status_code}: {resp.text}"
                    raise RuntimeError(msg)
                if i >= WARMUP_ITERATIONS:
                    samples_us.append(duration_us)
        return samples_us
    finally:
        await redis_client.aclose()


def main() -> int:
    import logging  # noqa: PLC0415
    import os  # noqa: PLC0415

    # Log-Overhead aus der Messung raushalten: strukturiertes Logging generiert
    # pro Iteration mehrere Events, deren I/O in TestClient-Pfad reinlaeuft.
    # Prod haette diese Zeilen auf DEBUG-Level unterdrueckt; wir emulieren das
    # per WARNING-Threshold auf allen rib_pqc-Loggern.
    logging.getLogger("rib_pqc").setLevel(logging.WARNING)

    try:
        facade = _bootstrap_facade()
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: bootstrap failed (liboqs missing?): {exc}", file=sys.stderr)
        return 2

    # Bench-DB=5, damit prod-Sessions (db=3), Nonces (db=4), OIDC-State (db=2)
    # und default (db=0) unberuehrt bleiben. Overridable via env fuer Local-Dev.
    bench_redis_url = os.environ.get(
        "RIB_BENCH_REDIS_URL", "redis://redis:6379/5"
    )

    # Nur die Algorithmen benchen die auch tatsaechlich in der Config-Whitelist
    # registriert sind. Verhindert AlgorithmNotFoundError bei Setups die z.B.
    # nur ML-KEM-768 supporten.
    supported = list(facade.supported_kem_algorithms())
    candidate_variants = ("ML-KEM-768", "ML-KEM-1024")
    variants_to_bench = [alg for alg in candidate_variants if alg in supported]
    skipped = [alg for alg in candidate_variants if alg not in supported]
    if skipped:
        print(
            f"[info] Skipping unsupported KEM variants: {skipped} "
            f"(registered: {supported})",
            file=sys.stderr,
        )
    if not variants_to_bench:
        print(
           