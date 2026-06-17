from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from router.cost_model import CostBudget  # noqa: E402
from router.route import route  # noqa: E402
from router.types import TensorSpec, Workload  # noqa: E402


def assert_route(workload: Workload, expected: str, label: str, budget: CostBudget | None = None) -> None:
    decision = route(workload, budget)
    if decision.route != expected:
        raise AssertionError(f"{label}: expected {expected}, got {decision.route} ({decision.reason})")


def main() -> None:
    budget_2gb = CostBudget(memory_budget_bytes=2 * 1024**3, safety_factor=0.5)

    assert_route(
        Workload(kind="circuit", n_qubits=60, circuit=[("H", (0,)), ("CNOT", (0, 1))], budget=budget_2gb),
        "stim",
        "60q Clifford must route to Stim before dense guard",
    )

    assert_route(
        Workload(kind="circuit", n_qubits=8, circuit=[("H", (0,)), ("T", (0,))], budget=budget_2gb),
        "dense",
        "small non-Clifford circuit fits dense",
    )

    assert_route(
        Workload(kind="circuit", n_qubits=30, circuit=[("H", (0,)), ("T", (0,))], budget=budget_2gb),
        "QPU_REQUIRED",
        "large non-Clifford circuit without tensor route is rejected",
    )

    small_tensor = TensorSpec(inputs=[("a",), ("a", "b"), ("b",)], shapes=[(2,), (2, 2), (2,)])
    assert_route(
        Workload(kind="tensor", n_qubits=20, tensor=small_tensor, budget=budget_2gb),
        "tensor",
        "small tensor passes memory and FLOPs gates",
    )

    slow_tensor = TensorSpec(
        inputs=[("a", "b"), ("b", "c"), ("c", "d")],
        output=("a", "d"),
        shapes=[(64, 64), (64, 64), (64, 64)],
    )
    strict_time = CostBudget(memory_budget_bytes=2 * 1024**3, safety_factor=0.5, flops_ceiling=1)
    assert_route(
        Workload(kind="tensor", n_qubits=8, tensor=slow_tensor, budget=strict_time),
        "dense",
        "slow tensor can fall back to dense if dense fits",
    )
    assert_route(
        Workload(kind="tensor", n_qubits=30, tensor=slow_tensor, budget=strict_time),
        "TENSOR_TOO_SLOW",
        "slow tensor reports TENSOR_TOO_SLOW if dense fallback also fails",
    )

    memory_huge_tensor = TensorSpec(inputs=[("a", "b")], output=("a", "b"), shapes=[(6000, 6000)])
    assert_route(
        Workload(kind="tensor", n_qubits=30, tensor=memory_huge_tensor, budget=CostBudget(memory_budget_bytes=8 * 1024**2)),
        "TENSOR_REQUIRED",
        "tensor peak memory gate blocks oversized tensor when dense also fails",
    )

    assert_route(
        Workload(kind="dense", n_qubits=26, budget=budget_2gb),
        "dense",
        "26q dense fits with safety factor",
    )
    assert_route(
        Workload(kind="dense", n_qubits=27, budget=budget_2gb),
        "QPU_REQUIRED",
        "27q dense fails with safety factor",
    )

    print("verify_route passed")


if __name__ == "__main__":
    main()
