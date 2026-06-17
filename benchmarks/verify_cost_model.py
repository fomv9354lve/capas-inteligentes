from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from router.cost_model import (  # noqa: E402
    CostBudget,
    dense_route_viability,
    magic_estimate,
    statevector_bytes,
    tensor_route_viability,
)


def assert_equal(actual, expected, label: str) -> None:
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected!r}, got {actual!r}")


def main() -> None:
    budget_2gb = CostBudget(memory_budget_bytes=2 * 1024**3, safety_factor=0.5)
    assert_equal(statevector_bytes(10), 16 * 2**10, "statevector_bytes")
    assert_equal(dense_route_viability(26, budget_2gb)["route"], "dense", "26q dense")
    assert_equal(dense_route_viability(27, budget_2gb)["route"], "QPU_REQUIRED", "27q guard")

    clifford = [("H", (0,)), ("CNOT", (0, 1)), ("S", (1,))]
    non_clifford = [("H", (0,)), ("T", (0,)), ("CNOT", (0, 1))]
    assert_equal(magic_estimate(clifford).is_clifford, True, "clifford estimate")
    assert_equal(magic_estimate(non_clifford).t_count, 1, "T count")

    inputs = [("a",), ("a", "b"), ("b",)]
    shapes = [(2,), (2, 2), (2,)]
    tensor = tensor_route_viability(inputs, shapes=shapes)
    assert_equal(tensor["route"], "tensor", "small tensor route")

    memory_block = tensor_route_viability(
        [("a", "b")],
        output=("a", "b"),
        shapes=[(6000, 6000)],
        budget=CostBudget(memory_budget_bytes=8 * 1024**2, safety_factor=0.5),
    )
    assert_equal(memory_block["route"], "TENSOR_REQUIRED", "tensor memory gate")
    assert_equal(memory_block["memory_viable"], False, "tensor memory viability")

    time_block = tensor_route_viability(
        [("a", "b"), ("b", "c"), ("c", "d")],
        output=("a", "d"),
        shapes=[(64, 64), (64, 64), (64, 64)],
        budget=CostBudget(memory_budget_bytes=512 * 1024**2, safety_factor=0.5, flops_ceiling=1),
    )
    assert_equal(time_block["route"], "TENSOR_TOO_SLOW", "tensor time gate")
    assert_equal(time_block["memory_viable"], True, "tensor time gate memory ok")
    assert_equal(time_block["time_viable"], False, "tensor time viability")

    print("cost_model verification passed")


if __name__ == "__main__":
    main()
