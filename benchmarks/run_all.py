from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

import bench_bypass_clean
import bench_cost_model_real
import bench_memory_guard
import bench_tensor_routing
from harness import write_json


def main() -> int:
    results = []
    results.extend(bench_bypass_clean.run())
    results.extend(bench_memory_guard.run())
    results.extend(bench_cost_model_real.run())
    results.extend(bench_tensor_routing.run())
    write_json(os.path.join(os.path.dirname(__file__), "latest_results.json"), results)

    n_pass = sum(r.verdict == "PASS" for r in results)
    n_fail = sum(r.verdict == "FAIL" for r in results)
    n_warn = sum(r.verdict == "WARN" for r in results)
    print("\n" + "=" * 70)
    print(f"CONSOLIDATED: {n_pass} pass / {n_warn} warn / {n_fail} fail / {len(results)} total")
    print("=" * 70)
    print("Results written to benchmarks/latest_results.json")
    return 1 if n_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
