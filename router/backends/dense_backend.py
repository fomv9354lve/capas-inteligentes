from __future__ import annotations

import numpy as np

from router.cost_model import dense_route_viability
from router.types import RouteDecision, Workload


H = np.array([[1, 1], [1, -1]], dtype=np.complex128) / np.sqrt(2)
S = np.array([[1, 0], [0, 1j]], dtype=np.complex128)
X = np.array([[0, 1], [1, 0]], dtype=np.complex128)
Y = np.array([[0, -1j], [1j, 0]], dtype=np.complex128)
Z = np.array([[1, 0], [0, -1]], dtype=np.complex128)
T = np.array([[1, 0], [0, np.exp(1j * np.pi / 4)]], dtype=np.complex128)
ONE_QUBIT = {"H": H, "S": S, "X": X, "Y": Y, "Z": Z, "T": T}


def _apply_one_qubit(psi: np.ndarray, gate: np.ndarray, q: int, n_qubits: int) -> np.ndarray:
    state = psi.reshape((2,) * n_qubits)
    state = np.moveaxis(state, q, 0)
    state = np.tensordot(gate, state, axes=([1], [0]))
    state = np.moveaxis(state, 0, q)
    return state.reshape(-1)


def _apply_cnot(psi: np.ndarray, control: int, target: int, n_qubits: int) -> np.ndarray:
    out = np.empty_like(psi)
    for idx in range(psi.size):
        if (idx >> (n_qubits - 1 - control)) & 1:
            out[idx ^ (1 << (n_qubits - 1 - target))] = psi[idx]
        else:
            out[idx] = psi[idx]
    return out


def simulate_dense_ops(ops, n_qubits: int) -> np.ndarray:
    psi = np.zeros(1 << n_qubits, dtype=np.complex128)
    psi[0] = 1.0
    for item in ops:
        if not isinstance(item, tuple) or len(item) < 2:
            raise ValueError(f"Unsupported op format for dense backend: {item!r}")
        gate = str(item[0]).upper()
        qubits = tuple(item[1])
        if gate in {"CNOT", "CX"}:
            psi = _apply_cnot(psi, qubits[0], qubits[1], n_qubits)
        elif gate in ONE_QUBIT:
            psi = _apply_one_qubit(psi, ONE_QUBIT[gate], qubits[0], n_qubits)
        elif gate in {"M", "MEASURE"}:
            continue
        else:
            raise NotImplementedError(f"Dense backend does not implement gate {gate!r}")
    return psi


def execute_dense_circuit(workload: Workload, decision: RouteDecision) -> np.ndarray:
    if decision.route != "dense":
        raise ValueError(f"Dense backend received route {decision.route!r}")
    if workload.n_qubits is None:
        raise ValueError("Dense backend requires n_qubits")
    if not dense_route_viability(workload.n_qubits, decision.budget)["memory_viable"]:
        raise MemoryError("Dense route no longer fits the active memory budget")
    if workload.kind == "dense":
        psi = np.zeros(1 << workload.n_qubits, dtype=np.complex128)
        psi[0] = 1.0
        return psi
    if workload.kind == "circuit" and workload.circuit is not None:
        return simulate_dense_ops(workload.circuit, workload.n_qubits)
    raise ValueError("Dense backend requires a dense or circuit workload")
