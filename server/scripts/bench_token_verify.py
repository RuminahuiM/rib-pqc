"""PQC-69 QUA-7: Performance-Benchmark fuer die Broker-Token-Verifikation.

**NFR-Perf-2:** ML-DSA-65-verify sollte unter 10 ms liegen.

**Mess-Strategie:**

Der Bericht erlaubt zwei Sichten:

1. **Isolated** - direkte ``CryptoFacade.verify(payload, signature, alg, kid)``
   in einer engen Schleife. Misst das reine ML-DSA-65-Verify ohne Token-Parsing,
   JSON-Encoding oder JWS-Strip. Diese Zahl wird im Bericht als "Crypto-Only"
   ausgewiesen und ist die NFR-Perf-2-Referenz.
2. **Token-Service** - ``TokenService.verify(token_str)`` inkl. JWS-Compact-
   Decoder, Claims-Parsing, Header-Validation, Allowlist-Check, Clock-Skew.
   Diese Zahl ist die realistische "End-to-End"-Sicht fuer einen API-Call,
   der einen Broker-Token-Header bekommt.

User-Pick 30.06.2026: "End-to-End via TestClient" - aber NFR-Perf-2 spec'd
"ML-DSA-65 verify", was strikt das Crypto-Only ist. Pragmatik: beide Pfade
messen, beide im Bericht ausweisen, Crypto-Only ist die SLO-Referenz.

**Iterationen:** 100 Warmup plus 1000 Mess-Samples (Akzeptanzkriterium).
"""
from __future__ import annotations

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


def _bootstrap() -> tuple[Any, Any, str]:
    """Initialisiert Facade plus TokenService plus signiertes Test-Token."""
    from config import get_settings  # noqa: PLC0415
    from crypto.facade import CryptoFacade  # noqa: PLC0415
    from crypto.registry import CryptoRegistry  # noqa: PLC0415
    from crypto.registry_init import init_crypto_registry  # noqa: PLC0415
    from services.token_service import TokenService  # noqa: PLC0415

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

    facade = CryptoFacade(
        registry=registry,
        default_signature_alg=sig_alg,
        signing_kid=active_kid,
        signing_secret_key=priv,
        verifying_keys_by_kid={active_kid: pub},
    )

    token_service = TokenService(
        crypto_facade=facade,
        issuer="bench",
        ttl_seconds=3600,
        allowed_algs=settings.token.allowed_algs,
        exp_leeway_seconds=30,
    )

    # Signed-Token fuer den Verify-Loop. TokenService.issue liefert nur str.
    token_str = token_service.issue(user_id="bench-user", auth_method="local")
    return facade, token_service, token_str


def _bench_crypto_only(facade: Any, payload: bytes, signature: bytes, alg: str, kid: str) -> list[int]:
    samples_us: list[int] = []
    for i in range(WARMUP_ITERATIONS + MEASURE_ITERATIONS):
        start = time_block_ns()
        ok = facade.verify(payload, signature, alg, kid)
        duration_us = (time_block_ns() - start) // 1000
        if not ok:
            msg = "Unexpected verify failure during benchmark"
            raise RuntimeError(msg)
        if i >= WARMUP_ITERATIONS:
            samples_us.append(duration_us)
    return samples_us


def _bench_token_service(token_service: Any, token_str: str) -> list[int]:
    samples_us: list[int] = []
    for i in range(WARMUP_ITERATIONS + MEASURE_ITERATIONS):
        start = time_block_ns()
        token_service.verify(token_str)
        duration_us = (time_block_ns() - start) // 1000
        if i >= WARMUP_ITERATIONS:
            samples_us.append(duration_us)
    return samples_us


def _decompose_token(token_str: str) -> tuple[bytes, bytes, str, str]:
    """Zerlegt einen JWS-Compact-Token in (payload-Bytes, signature, alg, kid).

    Spiegelung der internen Aufruf-Reihenfolge in ``TokenService.verify`` ohne
    Claims-Parsing.
    """
    import base64  # noqa: PLC0415
    import json  # noqa: PLC0415

    h_b64, p_b64, s_b64 = token_str.split(".")

    def _b64url_pad(s: str) -> bytes:
        # base64url decode mit konditionellem Padding (analog token_service._b64url_decode).
        return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))

    header = json.loads(_b64url_pad(h_b64).decode("utf-8"))
    payload_bytes = f"{h_b64}.{p_b64}".encode("ascii")
    signature = _b64url_pad(s_b64)
    return payload_bytes, signature, header["alg"], header["kid"]


def main() -> int:
    try:
        facade, token_service, token_str = _bootstrap()
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: bootstrap failed (liboqs missing?): {exc}", file=sys.stderr)
        return 2

    payload_bytes, signature, alg, kid = _decompose_token(token_str)

    summary: dict[str, Any] = {
        "warmup_iterations": WARMUP_ITERATIONS,
        "measure_iterations": MEASURE_ITERATIONS,
        "nfr_target_ms": 10,
        "variants": {},
    }
    rows: list[tuple[str, dict[str, float]]] = []

    crypto_samples = _bench_crypto_only(facade, payload_bytes, signature, alg, kid)
    s_crypto = summarize(crypto_samples)
    summary["variants"]["crypto_only_ml_dsa_65_verify"] = s_crypto
    rows.append(("CryptoFacade.verify (ML-DSA-65)", s_crypto))

    tok_samples = _bench_token_service(token_service, token_str)
    s_tok = summarize(tok_samples)
    summary["variants"]["token_service_verify_full"] = s_tok
    rows.append(("TokenService.verify (full)", s_tok))

    print_table("QUA-7 / PQC-69 / NFR-Perf-2 (Target <= 10 ms)", rows)
    path = write_result_json("token_verify", "NFR-Perf-2", summary)
    print(f"\n[ok] JSON written: {path}")

    if s_crypto.get("p95_ms", 0) > summary["nfr_target_ms"]:
        print("WARNING: Crypto-Only P95 exceeds NFR-Perf-2 target of 10 ms", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
