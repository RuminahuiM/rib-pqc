"""Gemeinsame Statistik- und Output-Helper fuer die QUA-Trio Benchmark-Skripte.

Stories: PQC-68 QUA-6, PQC-69 QUA-7, PQC-70 QUA-8.

**Konvention:**
- Alle Latenz-Messungen in Mikrosekunden (us, ``time.perf_counter_ns()``).
- Warmup-Phase verworfen (Cache/Branch-Prediction stabilisiert).
- P50/P95/Min/Max/Mean ueber die Messdaten, ausgegeben in **Millisekunden**.
- Output als JSON unter ``server/scripts/bench_results/<bench>.json``.
- Master-Markdown-Tabelle in ``docs/14_performance_results.md`` (vom Skript
  ``write_results_doc.py`` aggregiert oder manuell aktualisiert).

**Statistik-Wahl:**
- Median (P50) plus 95th-Percentile - Standard fuer Latenz-SLOs.
- Statistik via stdlib ``statistics`` (kein numpy-Dependency).
- P95 = 95% der Werte sind <=, berechnet via ``statistics.quantiles`` (n=20).
"""
from __future__ import annotations

import json
import platform
import statistics
import sys
import time
from pathlib import Path
from typing import Any


def time_block_ns() -> int:
    """Return current monotonic high-res counter in nanoseconds."""
    return time.perf_counter_ns()


def percentile(samples_us: list[int], p: float) -> float:
    """Linear-interpolation percentile (analog NumPy default).

    p in [0, 100]. Liefert us. Robust gegen kleine Sample-Groessen.
    """
    if not samples_us:
        msg = "empty samples"
        raise ValueError(msg)
    if len(samples_us) == 1:
        return float(samples_us[0])
    sorted_samples = sorted(samples_us)
    rank = (p / 100.0) * (len(sorted_samples) - 1)
    lo = int(rank)
    hi = min(lo + 1, len(sorted_samples) - 1)
    frac = rank - lo
    return sorted_samples[lo] * (1 - frac) + sorted_samples[hi] * frac


def summarize(samples_us: list[int]) -> dict[str, float]:
    """Aggregiert Latenz-Samples. Werte in Millisekunden (gerundet auf 3 NK).

    Returns dict mit: n, min_ms, p50_ms, p95_ms, p99_ms, max_ms, mean_ms, stdev_ms.
    """
    if not samples_us:
        return {"n": 0}
    return {
        "n": len(samples_us),
        "min_ms": round(min(samples_us) / 1000.0, 3),
        "p50_ms": round(percentile(samples_us, 50.0) / 1000.0, 3),
        "p95_ms": round(percentile(samples_us, 95.0) / 1000.0, 3),
        "p99_ms": round(percentile(samples_us, 99.0) / 1000.0, 3),
        "max_ms": round(max(samples_us) / 1000.0, 3),
        "mean_ms": round(statistics.fmean(samples_us) / 1000.0, 3),
        "stdev_ms": (
            round(statistics.stdev(samples_us) / 1000.0, 3) if len(samples_us) > 1 else 0.0
        ),
    }


def environment_meta() -> dict[str, str]:
    """Sammelt Umgebungs-Metadaten fuer das Result-JSON (Reproduzierbarkeit)."""
    return {
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor() or "n/a",
    }


def write_result_json(
    bench_name: str,
    nfr_id: str,
    summary: dict[str, Any],
    *,
    output_dir: Path | None = None,
) -> Path:
    """Schreibt das Ergebnis-JSON nach ``server/scripts/bench_results/``.

    Liefert den Pfad fuer das Logging-Statement im aufrufenden Skript.
    """
    target_dir = output_dir or Path(__file__).resolve().parent / "bench_results"
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / f"{bench_name}.json"
    payload = {
        "bench": bench_name,
        "nfr": nfr_id,
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "environment": environment_meta(),
        **summary,
    }
    target.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")
    return target


def print_table(title: str, rows: list[tuple[str, dict[str, float]]]) -> None:
    """Druckt eine Markdown-Tabelle der Summaries (Stdout-Output fuer CLI)."""
    print(f"\n=== {title} ===")
    print(f"{'Variant':<32} {'n':>5} {'min':>8} {'p50':>8} {'p95':>8} {'p99':>8} {'max':>8} {'mean':>8}")
    print("-" * 96)
    for label, s in rows:
        if s.get("n", 0) == 0:
            print(f"{label:<32} (no samples)")
            continue
        print(
            f"{label:<32} {s['n']:>5} "
            f"{s['min_ms']:>7.3f}ms {s['p50_ms']:>7.3f}ms "
            f"{s['p95_ms']:>7.3f}ms {s['p99_ms']:>7.3f}ms "
            f"{s['max_ms']:>7.3f}ms {s['mean_ms']:>7.3f}ms"
        )
