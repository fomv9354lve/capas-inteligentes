from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import stim

from harness import BenchResult, report, time_call


BYTES_PER_COMPLEX128 = 16
DENSE_BUDGET = 512 * 1024**2


CLIFFORD_GATES = {"H", "S", "X", "Z", "CX", "CNOT"}
NON_CLIFFORD_GATES = {"T"}


@dataclass(frozen=True)
class CircuitFeatures:
    n_qubits: int
    n_gates: int
    t_count: int
    dense_bytes: int


def dense_bytes(n_qubits: int) -> int:
    return BYTES_PER_COMPLEX128 * (1 << n_qubits)


def make_circuit(n_qubits: int, depth: int, t_count: int, seed: int) -> list[tuple[str, tuple[int, ...]]]:
    rng = np.random.default_rng(seed)
    ops: list[tuple[str, tuple[int, ...]]] = []
    t_left = t_count
    for layer in range(depth):
        for q in range(n_qubits):
            if t_left and (layer + q) % max(1, depth // max(1, t_count)) == 0:
                ops.append(("T", (q,)))
                t_left -= 1
            else:
                ops.append((str(rng.choice(["H", "S", "X", "Z"])), (q,)))
        for q in range(0, n_qubits - 1, 2):
            ops.append(("CNOT", (q, q + 1)))
    q = 0
    while t_left:
        ops.append(("T", (q % n_qubits,)))
        t_left -= 1
        q += 1
    return ops


def features(ops: list[tuple[str, tuple[int, ...]]], n_qubits: int) -> CircuitFeatures:
    return CircuitFeatures(
        n_qubits=n_qubits,
        n_gates=len(ops),
        t_count=sum(1 for gate, _ in ops if gate in NON_CLIFFORD_GATES),
        dense_bytes=dense_bytes(n_qubits),
    )


def estimate_route(f: CircuitFeatures) -> str:
    if f.t_count == 0:
        return "stim"
    if f.dense_bytes <= DENSE_BUDGET:
        return "dense"
    return "QPU_OR_TENSOR_REQUIRED"


def to_stim(ops: list[tuple[str, tuple[int, ...]]], n_qubits: int) -> stim.Circuit:
    c = stim.Circuit()
    for gate, qubits in ops:
        if gate == "T":
            raise ValueError("Stim stabilizer sampler cannot consume non-Clifford T gates.")
        c.append(gate, list(qubits))
    c.append("M", list(range(n_qubits)))
    return c


def apply_one_qubit(psi: np.ndarray, mat: np.ndarray, q: int, n_qubits: int) -> np.ndarray:
    state = psi.reshape((2,) * n_qubits)
    state = np.moveaxis(state, q, 0)
    state = np.tensordot(mat, state, axes=([1], [0]))
    state = np.moveaxis(state, 0, q)
    return state.reshape(-1)


def apply_cnot(psi: np.ndarray, control: int, target: int, n_qubits: int) -> np.ndarray:
    out = psi.copy()
    for idx in range(psi.size):
        if (idx >> (n_qubits - 1 - control)) & 1:
            flipped = idx ^ (1 << (n_qubits - 1 - target))
            out[flipped] = psi[idx]
        else:
            out[idx] = psi[idx]
    return out


H = np.array([[1, 1], [1, -1]], dtype=np.complex128) / np.sqrt(2)
S = np.array([[1, 0], [0, 1j]], dtype=np.complex128)
X = np.array([[0, 1], [1, 0]], dtype=np.complex128)
Z = np.array([[1, 0], [0, -1]], dtype=np.complex128)
T = np.array([[1, 0], [0, np.exp(1j * np.pi / 4)]], dtype=np.complex128)
ONE_QUBIT = {"H": H, "S": S, "X": X, "Z": Z, "T": T}


def dense_simulate(ops: list[tuple[str, tuple[int, ...]]], n_qubits: int) -> np.ndarray:
    psi = np.zeros(1 << n_qubits, dtype=np.complex128)
    psi[0] = 1.0
    for gate, qubits in ops:
        if gate == "CNOT":
            psi = apply_cnot(psi, qubits[0], qubits[1], n_qubits)
        else:
            psi = apply_one_qubit(psi, ONE_QUBIT[gate], qubits[0], n_qubits)
    return psi


def measured_best_route(ops: list[tuple[str, tuple[int, ...]]], n_qubits: int) -> tuple[str, dict]:
    f = features(ops, n_qubits)
    if f.t_count == 0:
        c = to_stim(ops, n_qubits)
        sampler = c.compile_sampler()
        stim_t = time_call(lambda: sampler.sample(shots=64), repeats=5, warmup=1)
        return "stim", {"stim_ms": round(stim_t["ms_median"], 6)}
    if f.dense_bytes <= DENSE_BUDGET:
        dense_t = time_call(lambda: dense_simulate(ops, n_qubits), repeats=3, warmup=1)
        return "dense", {"dense_ms": round(dense_t["ms_median"], 6)}
    return "QPU_OR_TENSOR_REQUIRED", {"dense_gb": round(f.dense_bytes / 1024**3, 3)}


def run() -> list[BenchResult]:
    results: list[BenchResult] = []
    cases = [
        ("clifford_20q", 20, 8, 0, 1),
        ("clifford_60q", 60, 8, 0, 2),
        ("t_small_8q", 8, 8, 4, 3),
        ("t_mid_dense_20q", 20, 4, 8, 4),
        ("t_big_30q", 30, 4, 4, 5),
    ]

    for name, n_qubits, depth, t_count, seed in cases:
        ops = make_circuit(n_qubits, depth, t_count, seed)
        f = features(ops, n_qubits)
        estimate = estimate_route(f)
        measured, extra = measured_best_route(ops, n_qubits)
        ok = estimate == measured
        metric = {
            "estimate": estimate,
            "measured": measured,
            "n_qubits": f.n_qubits,
            "n_gates": f.n_gates,
            "t_count": f.t_count,
            "dense_mb": round(f.dense_bytes / 1024**2, 3),
            **extra,
        }
        results.append(BenchResult(
            name,
            "PASS" if ok else "FAIL",
            metric,
            f"estimate={estimate}, measured={measured}, T={f.t_count}, dense={metric['dense_mb']}MB",
        ))

    return report("Benchmark 5 revised: real Clifford+T routing", results)


if __name__ == "__main__":
    run()
