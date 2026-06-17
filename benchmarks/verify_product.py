from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from router import CostBudget, TensorSpec, Workload, execute, route  # noqa: E402


def main() -> None:
    budget = CostBudget(memory_budget_bytes=2 * 1024**3, safety_factor=0.5)

    clifford = Workload(
        kind="circuit",
        n_qubits=3,
        circuit=[("H", (0,)), ("CNOT", (0, 1)), ("CNOT", (1, 2))],
        budget=budget,
    )
    decision = route(clifford)
    assert decision.route == "stim"
    samples = execute(clifford, decision, shots=4)
    assert samples.shape == (4, 3)

    non_clifford = Workload(
        kind="circuit",
        n_qubits=2,
        circuit=[("H", (0,)), ("T", (0,)), ("CNOT", (0, 1))],
        budget=budget,
    )
    decision = route(non_clifford)
    assert decision.route == "dense"
    state = execute(non_clifford, decision)
    assert state.shape == (4,)
    assert np.isclose(np.linalg.norm(state), 1.0)

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
    decision = route(tensor)
    assert decision.route == "tensor"
    value = execute(tensor, decision)
    assert np.isclose(value, a @ m @ b)

    impossible = Workload(
        kind="circuit",
        n_qubits=60,
        circuit=[("H", (0,)), ("T", (0,))],
        budget=budget,
    )
    decision = route(impossible)
    assert decision.route == "QPU_REQUIRED"

    print("verify_product passed")


if __name__ == "__main__":
    main()
