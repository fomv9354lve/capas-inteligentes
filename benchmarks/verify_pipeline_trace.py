# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from router import CostBudget, TensorSpec, Workload  # noqa: E402
from router.pipeline import run_with_trace  # noqa: E402


def event(trace, stage: str):
    for e in trace.events:
        if e.stage == stage:
            return e
    raise AssertionError(f"missing event {stage}")


def main() -> None:
    budget = CostBudget(memory_budget_bytes=2 * 1024**3, safety_factor=0.5)

    clifford_60 = Workload(
        kind="circuit",
        n_qubits=60,
        circuit=[("H", (0,)), ("CNOT", (0, 1))],
        budget=budget,
    )
    _, trace = run_with_trace(clifford_60, execute_result=False)
    assert trace.decision_route == "stim"
    cm = event(trace, "cost_model").metrics
    assert cm["dense_statevector_bytes"] > budget.memory_budget_bytes
    assert cm["t_count"] == 0
    assert trace.result_hash is None

    impossible = Workload(
        kind="circuit",
        n_qubits=60,
        circuit=[("H", (0,)), ("T", (0,))],
        budget=budget,
    )
    _, trace = run_with_trace(impossible)
    assert trace.decision_route == "QPU_REQUIRED"
    assert event(trace, "execute").status == "skipped"
    assert event(trace, "cost_model").metrics["t_count"] == 1

    a = np.array([1.0, 2.0])
    m = np.array([[3.0, 0.0], [0.0, 5.0]])
    b = np.array([7.0, 11.0])
    tensor = Workload(
        kind="tensor",
        tensor=TensorSpec(
            arrays=[a, m, b],
            inputs=[("i",), ("i", "j"), ("j",)],
            shapes=[a.shape, m.shape, b.shape],
        ),
        budget=budget,
    )
    result, trace = run_with_trace(tensor)
    assert trace.decision_route == "tensor"
    assert np.isclose(result, a @ m @ b)
    assert trace.result_hash
    tensor_metrics = event(trace, "cost_model").metrics
    assert tensor_metrics["peak_bytes"] <= budget.usable_memory_bytes
    assert tensor_metrics["contraction_cost"] <= budget.flops_ceiling

    print("verify_pipeline_trace passed")


if __name__ == "__main__":
    main()
