# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from router.cost_model import CostBudget, dense_route_viability, magic_estimate
from router.route import route
from router.types import Workload


@dataclass(frozen=True)
class CorpusCase:
    name: str
    family: str
    n_qubits: int
    ops: list[tuple[str, tuple[int, ...]]]


@dataclass(frozen=True)
class ClaimRow:
    name: str
    family: str
    n_qubits: int
    n_gates: int
    t_count: int
    router_route: str
    dense_viable: bool
    rescued_from_dense_failure: bool
    low_magic_gap_candidate: bool
    resolved_by_current_router: bool


def ghz(n: int) -> list[tuple[str, tuple[int, ...]]]:
    return [("H", (0,))] + [("CNOT", (i, i + 1)) for i in range(n - 1)]


def random_clifford_like(n: int, depth: int) -> list[tuple[str, tuple[int, ...]]]:
    one = ["H", "S", "X", "Z"]
    ops: list[tuple[str, tuple[int, ...]]] = []
    for d in range(depth):
        for q in range(n):
            ops.append((one[(q + d) % len(one)], (q,)))
        for q in range(d % 2, n - 1, 2):
            ops.append(("CNOT", (q, q + 1)))
    return ops


def clifford_t_low_density(n: int, depth: int, t_count: int) -> list[tuple[str, tuple[int, ...]]]:
    ops = random_clifford_like(n, depth)
    out = list(ops)
    stride = max(1, len(out) // max(1, t_count))
    inserted = 0
    pos = 0
    while inserted < t_count:
        out.insert(min(pos, len(out)), ("T", (inserted % n,)))
        inserted += 1
        pos += stride
    return out


def qaoa_like(n: int, layers: int) -> list[tuple[str, tuple[int, ...]]]:
    ops: list[tuple[str, tuple[int, ...]]] = [("H", (q,)) for q in range(n)]
    for layer in range(layers):
        for q in range(n - 1):
            ops.append(("CNOT", (q, q + 1)))
            ops.append(("RZ", (q + 1,)))
            ops.append(("CNOT", (q, q + 1)))
        for q in range(n):
            ops.append(("RX", (q,)))
    return ops


def qft_approx_like(n: int, cutoff: int) -> list[tuple[str, tuple[int, ...]]]:
    ops: list[tuple[str, tuple[int, ...]]] = []
    for q in range(n):
        ops.append(("H", (q,)))
        for k in range(1, min(cutoff, n - q)):
            # Controlled phase rotations are non-Clifford for generic angles.
            ops.append(("RZ", (q + k,)))
            ops.append(("CNOT", (q, q + k)))
    return ops


def trotter_like(n: int, steps: int) -> list[tuple[str, tuple[int, ...]]]:
    ops: list[tuple[str, tuple[int, ...]]] = []
    for _ in range(steps):
        for q in range(n - 1):
            ops.append(("CNOT", (q, q + 1)))
            ops.append(("RZ", (q + 1,)))
            ops.append(("CNOT", (q, q + 1)))
        for q in range(n):
            ops.append(("RX", (q,)))
    return ops


def build_corpus() -> list[CorpusCase]:
    cases: list[CorpusCase] = []
    for n in [8, 20, 32, 60]:
        cases.append(CorpusCase(f"ghz_{n}q", "ghz_clifford", n, ghz(n)))
        cases.append(CorpusCase(f"clifford_{n}q", "random_clifford", n, random_clifford_like(n, depth=4)))
    for n in [20, 32, 60]:
        for t in [1, 2, 4, 8, 16]:
            cases.append(CorpusCase(f"clifford_t_{n}q_T{t}", "low_density_clifford_t", n, clifford_t_low_density(n, depth=4, t_count=t)))
    for n in [12, 20, 32]:
        cases.append(CorpusCase(f"qaoa_{n}q_L2", "qaoa_like", n, qaoa_like(n, layers=2)))
        cases.append(CorpusCase(f"qft_approx_{n}q_c4", "qft_approx_like", n, qft_approx_like(n, cutoff=4)))
        cases.append(CorpusCase(f"trotter_{n}q_s2", "trotter_like", n, trotter_like(n, steps=2)))
    return cases


def analyze_case(case: CorpusCase, budget: CostBudget) -> ClaimRow:
    magic = magic_estimate(case.ops)
    dense = dense_route_viability(case.n_qubits, budget)
    decision = route(Workload(kind="circuit", n_qubits=case.n_qubits, circuit=case.ops, budget=budget))
    rescued = (not dense["memory_viable"]) and decision.executable
    low_magic_gap = (not dense["memory_viable"]) and (0 < magic.t_count <= 16)
    return ClaimRow(
        name=case.name,
        family=case.family,
        n_qubits=case.n_qubits,
        n_gates=magic.n_gates,
        t_count=magic.t_count,
        router_route=decision.route,
        dense_viable=bool(dense["memory_viable"]),
        rescued_from_dense_failure=rescued,
        low_magic_gap_candidate=low_magic_gap,
        resolved_by_current_router=decision.executable,
    )


def main() -> int:
    budget = CostBudget(memory_budget_bytes=2 * 1024**3, safety_factor=0.5)
    rows = [analyze_case(c, budget) for c in build_corpus()]

    n = len(rows)
    rescued = sum(r.rescued_from_dense_failure for r in rows)
    low_magic_gap = sum(r.low_magic_gap_candidate for r in rows)
    low_magic_resolved = sum(r.low_magic_gap_candidate and r.resolved_by_current_router for r in rows)
    rejected = sum(not r.resolved_by_current_router for r in rows)
    by_route: dict[str, int] = {}
    for r in rows:
        by_route[r.router_route] = by_route.get(r.router_route, 0) + 1

    out = {
        "summary": {
            "n_cases": n,
            "rescued_from_dense_failure": rescued,
            "rescued_fraction": rescued / n,
            "low_magic_gap_candidates": low_magic_gap,
            "low_magic_gap_resolved_by_current_router": low_magic_resolved,
            "rejected_or_unresolved": rejected,
            "by_route": by_route,
        },
        "rows": [asdict(r) for r in rows],
    }
    path = ROOT / "benchmarks" / "claim_frequency_results.json"
    path.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps(out["summary"], indent=2, sort_keys=True))
    if low_magic_gap and low_magic_resolved == 0:
        print("VERDICT: current router finds a low-magic large-n gap, but does not solve it.")
    elif rescued / n < 0.25:
        print("VERDICT: current router is useful engineering, not enough for the large claim.")
    else:
        print("VERDICT: corpus frequency may justify a larger routing/simulation claim.")
    print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
