from __future__ import annotations

import numpy as np

from harness import BenchResult, current_rss_mb, report, time_call


BYTES_PER_COMPLEX128 = 16


def statevector_bytes(n_qubits: int) -> int:
    return BYTES_PER_COMPLEX128 * (1 << n_qubits)


def route_dense_statevector(n_qubits: int, budget_bytes: int, safety_factor: float = 0.5) -> tuple[str, int]:
    need = statevector_bytes(n_qubits)
    if need <= budget_bytes * safety_factor:
        return "dense", need
    return "QPU_REQUIRED", need


def run() -> list[BenchResult]:
    results: list[BenchResult] = []
    budget = 2 * 1024**3

    t = time_call(lambda: route_dense_statevector(40, budget), repeats=101, warmup=10)
    results.append(BenchResult(
        "reject_40q_latency",
        "PASS" if t["ms_median"] < 1.0 else "FAIL",
        {"ms_median": round(t["ms_median"], 8)},
        f"reject={t['ms_median'] * 1000:.2f}us",
    ))

    rss_before = current_rss_mb()
    route_dense_statevector(40, budget)
    rss_after = current_rss_mb()
    delta = rss_after - rss_before
    results.append(BenchResult(
        "reject_40q_rss_delta",
        "PASS" if delta < 1.0 else "FAIL",
        {"rss_delta_mb": round(delta, 6)},
        f"rss_delta={delta:.6f}MB",
    ))

    r26, _ = route_dense_statevector(26, budget)
    r27, _ = route_dense_statevector(27, budget)
    results.append(BenchResult(
        "safe_threshold_26_vs_27",
        "PASS" if (r26 == "dense" and r27 == "QPU_REQUIRED") else "FAIL",
        {"q26": r26, "q27": r27, "safety_factor": 0.5},
        f"26q->{r26}, 27q->{r27} under 2GB budget with 0.5 safety",
    ))

    def allocate_10q():
        psi = np.zeros(1 << 10, dtype=np.complex128)
        psi[0] = 1.0
        return psi

    route, _ = route_dense_statevector(10, budget)
    psi = allocate_10q()
    results.append(BenchResult(
        "accept_10q_runs",
        "PASS" if route == "dense" and psi.shape == (1024,) else "FAIL",
        {"route": route, "shape": psi.shape},
        f"10q->{route}, shape={psi.shape}",
    ))

    return report("Benchmark 4 revised: memory guard", results)


if __name__ == "__main__":
    run()
