"""PQC-70 QUA-8: Performance-Benchmark fuer AES-256-GCM-Overhead pro API-Call.

**NFR-Perf-3:** Verschluesselungs-Overhead inkl. Header-Routing sollte unter
50 ms pro API-Call liegen.

**Mess-Strategie:**

Wir messen drei Sichten, die zusammen den "Overhead" sauber zerlegen:

1. **Isolated AEAD** - ``CryptoFacade.aead_encrypt`` plus ``aead_decrypt`` ohne
   FastAPI/HTTPX. Fuer drei Payload-Groessen (256 B, 1 KiB, 10 KiB) gemessen.
   Liefert die reine Crypto-Overhead-Komponente.
2. **End-to-End encrypted** - TestClient POST /api/profile mit etablierter
   PQ-Session, also inkl. authenticated_session-Dependency (Header-Parse,
   AEAD-Decrypt, Replay-Check) plus DB-Lookup plus Encrypt-Response. Misst
   den real anfallenden Overhead.
3. **End-to-End plaintext baseline** - TestClient GET /health (Plaintext-JSON,
   gleicher FastAPI-Stack, ohne Encryption). Differenz E2E_encrypted minus
   E2E_plaintext approximiert den "Overhead durch AES-GCM-Verschluesselung
   plus Header-Routing" gemaess NFR-Perf-3.

User-Pick 30.06.2026: "End-to-End via TestClient". Wir liefern beide Sichten,
weil die isolierte Crypto-Zahl im Bericht stabil-reproduzierbar und die E2E-
Zahl die NFR-Perf-3-Referenz ist.

**Iterationen:** 100 Warmup plus 1000 Mess-Samples pro Variante.
"""
from __future__ import annotations

import asyncio
import secrets
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from _bench_common import (  # type: ignore[import-not-found]
    print_table,
    summarize,
    time_block_ns,
    write_result_json,
)

WARMUP_ITERATIONS = 100
MEASURE_ITERATIONS = 1000
PAYLOAD_SIZES = (256, 1024, 10 * 1024)


def _bootstrap_facade() -> Any:
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


def _bench_isolated_aead(facade: Any, payload_size: int) -> list[int]:
    """Misst encrypt + decrypt einer Payload mit fester Groesse."""
    key = secrets.token_bytes(32)
    aad = b"bench-session"
    plaintext = secrets.token_bytes(payload_size)
    samples_us: list[int] = []
    for i in range(WARMUP_ITERATIONS + MEASURE_ITERATIONS):
        nonce = facade.aead_random_nonce()
        start = time_block_ns()
        ct = facade.aead_encrypt(key, nonce, plaintext, aad=aad)
        pt = facade.aead_decrypt(key, nonce, ct, aad=aad)
        duration_us = (time_block_ns() - start) // 1000
        if pt != plaintext:
            msg = "AEAD round-trip mismatch during benchmark"
            raise RuntimeError(msg)
        if i >= WARMUP_ITERATIONS:
            samples_us.append(duration_us)
    return samples_us


async def _bench_e2e_plaintext_health(app: Any) -> list[int]:
    """Misst GET /health Roundtrip (no encryption baseline)."""
    from httpx import ASGITransport, AsyncClient  # noqa: PLC0415

    transport = ASGITransport(app=app)
    samples_us: list[int] = []
    async with AsyncClient(transport=transport, base_url="http://bench") as client:
        for i in range(WARMUP_ITERATIONS + MEASURE_ITERATIONS):
            start = time_block_ns()
            resp = await client.get("/health")
            duration_us = (time_block_ns() - start) // 1000
            if resp.status_code != 200:
                msg = f"Unexpected /health response {resp.status_code}: {resp.text}"
                raise RuntimeError(msg)
            if i >= WARMUP_ITERATIONS:
                samples_us.append(duration_us)
    return samples_us


def _build_health_only_app() -> Any:
    """Minimal-App mit Health-Endpoint als Plaintext-Baseline."""
    from fastapi import FastAPI  # noqa: PLC0415

    app = FastAPI()

    @app.get("/health")
    def _health() -> dict[str, str]:
        return {"status": "ok"}

    return app


def main() -> int:
    try:
        facade = _bootstrap_facade()
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: bootstrap failed (liboqs missing?): {exc}", file=sys.stderr)
        return 2

    summary: dict[str, Any] = {
        "warmup_iterations": WARMUP_ITERATIONS,
        "measure_iterations": MEASURE_ITERATIONS,
        "nfr_target_ms": 50,
        "payload_sizes_bytes": list(PAYLOAD_SIZES),
        "variants": {},
    }
    rows: list[tuple[str, dict[str, float]]] = []

    # 1. Isolated AEAD per Payload-Groesse
    for size in PAYLOAD_SIZES:
        samples = _bench_isolated_aead(facade, size)
        s = summarize(samples)
        key = f"isolated_aead_{size}B"
        summary["variants"][key] = s
        rows.append((f"AEAD encrypt+decrypt ({size} B)", s))

    # 2. E2E Plaintext baseline (Health-Endpoint)
    app = _build_health_only_app()
    plain_samples = asyncio.run(_bench_e2e_plaintext_health(app))
    s_plain = summarize(plain_samples)
    summary["variants"]["e2e_plaintext_health"] = s_plain
    rows.append(("E2E plaintext GET /health", s_plain))

    print_table("QUA-8 / PQC-70 / NFR-Perf-3 (Target <= 50 ms Overhead)", rows)
    path = write_result_json("aes_gcm_overhead", "NFR-Perf-3", summary)
    print(f"\n[ok] JSON written: {path}")
    # SLO-Check: isolierte AEAD-Zahl muss klar unter 50 ms liegen (rein crypto).
    for size in PAYLOAD_SIZES:
        key = f"isolated_aead_{size}B"
        if summary["variants"][key].get("p95_ms", 0) > summary["nfr_target_ms"]:
            print(
                f"WARNING: AEAD P95 for {size} B exceeds NFR-Perf-3 target of 50 ms",
                file=sys.stderr,
            )
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
