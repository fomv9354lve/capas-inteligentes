from __future__ import annotations

from typing import Any

import stim

from router.cost_model import magic_estimate
from router.types import RouteDecision, Workload


def _append_op(circuit: stim.Circuit, gate: str, qubits: tuple[int, ...]) -> None:
    name = gate.upper()
    if name == "CX":
        name = "CNOT"
    circuit.append(name, list(qubits))


def to_stim_circuit(ops: Any, n_qubits: int) -> stim.Circuit:
    if isinstance(ops, stim.Circuit):
        return ops

    circuit = stim.Circuit()
    for item in ops:
        if not isinstance(item, tuple) or len(item) < 2:
            raise ValueError(f"Unsupported op format for Stim backend: {item!r}")
        gate, qubits = item[0], tuple(item[1])
        _append_op(circuit, str(gate), qubits)
    circuit.append("M", list(range(n_qubits)))
    return circuit


def execute_stim_circuit(workload: Workload, decision: RouteDecision, shots: int = 64):
    if decision.route != "stim":
        raise ValueError(f"Stim backend received route {decision.route!r}")
    if workload.kind != "circuit" or workload.circuit is None or workload.n_qubits is None:
        raise ValueError("Stim backend requires a circuit workload with n_qubits")
    if not magic_estimate(workload.circuit).is_clifford:
        raise ValueError("Stim backend only accepts Clifford circuits")

    circuit = to_stim_circuit(workload.circuit, workload.n_qubits)
    sampler = circuit.compile_sampler()
    return sampler.sample(shots=shots)
