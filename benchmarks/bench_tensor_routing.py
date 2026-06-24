# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
from __future__ import annotations

import sys
import importlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import cotengra as ct
import numpy as np

from harness import BenchResult, report, time_call
from router.cost_model import make_default_tensor_optimizer


BYTES_PER_COMPLEX128 = 16
DENSE_BUDGET = 512 * 1024**2
SAFETY_FACTOR = 0.5
FLOPS_CEILING = 1e8


H = np.array([[1, 1], [1, -1]], dtype=np.complex128) / np.sqrt(2)
T = np.array([[1, 0], [0, np.exp(1j * np.pi / 4)]], dtype=np.complex128)
I = np.eye(2, dtype=np.complex128)
CNOT = np.zeros((2, 2, 2, 2), dtype=np.complex128)
for c in range(2):
    for t in range(2):
        CNOT[c, t, c, t ^ c] = 1.0
KET0 = np.array([1.0, 0.0], dtype=np.complex128)
BRA0 = np.array([1.0, 0.0], dtype=np.complex128)


def dense_bytes(n_qubits: int) -> int:
    return BYTES_PER_COMPLEX128 * (1 << n_qubits)


def make_1d_ops(n_qubits: int, depth: int, entangling: bool) -> list[tuple[str, tuple[int, ...]]]:
    ops: list[tuple[str, tuple[int, ...]]] = []
    for layer in range(depth):
        for q in range(n_qubits):
            ops.append(("H" if (q + layer) % 2 == 0 else "T", (q,)))
        if entangling:
            start = layer % 2
            for q in range(start, n_qubits - 1, 2):
                ops.append(("CNOT", (q, q + 1)))
    return ops


def build_amplitude_network(n_qubits: int, ops: list[tuple[str, tuple[int, ...]]]):
    arrays = []
    inputs = []
    current = []
    counter = 0

    for q in range(n_qubits):
        idx = f"q{q}_{counter}"
        counter += 1
        arrays.append(KET0)
        inputs.append((idx,))
        current.append(idx)

    for gate, qubits in ops:
        if gate in {"H", "T"}:
            q = qubits[0]
            new = f"q{q}_{counter}"
            counter += 1
            arrays.append(H if gate == "H" else T)
            inputs.append((current[q], new))
            current[q] = new
        elif gate == "CNOT":
            c, t = qubits
            new_c = f"q{c}_{counter}"
            counter += 1
            new_t = f"q{t}_{counter}"
            counter += 1
            arrays.append(CNOT)
            inputs.append((current[c], current[t], new_c, new_t))
            current[c] = new_c
            current[t] = new_t
        else:
            raise ValueError(gate)

    for q in range(n_qubits):
        arrays.append(BRA0)
        inputs.append((current[q],))

    return arrays, inputs


def dense_apply_one(psi: np.ndarray, gate: np.ndarray, q: int, n_qubits: int) -> np.ndarray:
    state = psi.reshape((2,) * n_qubits)
    state = np.moveaxis(state, q, 0)
    state = np.tensordot(gate, state, axes=([1], [0]))
    state = np.moveaxis(state, 0, q)
    return state.reshape(-1)


def dense_apply_cnot(psi: np.ndarray, control: int, target: int, n_qubits: int) -> np.ndarray:
    out = np.empty_like(psi)
    for idx in range(psi.size):
        if (idx >> (n_qubits - 1 - control)) & 1:
            out[idx ^ (1 << (n_qubits - 1 - target))] = psi[idx]
        else:
            out[idx] = psi[idx]
    return out


def dense_amplitude(n_qubits: int, ops: list[tuple[str, tuple[int, ...]]]) -> complex:
    psi = np.zeros(1 << n_qubits, dtype=np.complex128)
    psi[0] = 1.0
    for gate, qubits in ops:
        if gate == "H":
            psi = dense_apply_one(psi, H, qubits[0], n_qubits)
        elif gate == "T":
            psi = dense_apply_one(psi, T, qubits[0], n_qubits)
        elif gate == "CNOT":
            psi = dense_apply_cnot(psi, qubits[0], qubits[1], n_qubits)
    return psi[0]


def tensor_amplitude(n_qubits: int, ops: list[tuple[str, tuple[int, ...]]]) -> complex:
    arrays, inputs = build_amplitude_network(n_qubits, ops)
    return ct.array_contract(arrays, inputs, output=(), optimize=make_default_tensor_optimizer())


def estimate_tensor_route(n_qubits: int, ops: list[tuple[str, tuple[int, ...]]]) -> tuple[str, dict]:
    arrays, inputs = build_amplitude_network(n_qubits, ops)
    shapes = [a.shape for a in arrays]
    tree = ct.array_contract_tree(inputs, output=(), shapes=shapes, optimize=make_default_tensor_optimizer())
    width = tree.contraction_width()
    cost = tree.contraction_cost()
    max_size = tree.max_size()
    tensor_peak_bytes = int(max_size * BYTES_PER_COMPLEX128)
    dense = dense_bytes(n_qubits)
    material_budget = DENSE_BUDGET * SAFETY_FACTOR

    memory_viable = tensor_peak_bytes <= material_budget
    time_viable = cost <= FLOPS_CEILING

    if memory_viable and time_viable:
        route = "tensor"
    elif memory_viable:
        route = "TENSOR_TOO_SLOW"
    else:
        route = "TENSOR_REQUIRED"
    return route, {
        "contraction_width_log2": round(width, 3),
        "contraction_cost": float(cost),
        "flops_ceiling": FLOPS_CEILING,
        "memory_viable": memory_viable,
        "time_viable": time_viable,
        "max_size_elements": int(max_size),
        "tensor_peak_mb": round(tensor_peak_bytes / 1024**2, 6),
        "dense_mb": round(dense / 1024**2, 3),
        "budget_mb": round(material_budget / 1024**2, 3),
        "n_tensors": len(arrays),
    }


def quimb_import_result() -> BenchResult:
    try:
        quimb = importlib.import_module("quimb")
        return BenchResult(
            "quimb_import",
            "PASS",
            {"version": getattr(quimb, "__version__", "unknown")},
            "quimb imports",
        )
    except Exception as exc:
        return BenchResult(
            "quimb_import",
            "WARN",
            {"error": type(exc).__name__, "message": str(exc)[:200]},
            f"quimb unavailable here: {type(exc).__name__}",
        )


def run() -> list[BenchResult]:
    results: list[BenchResult] = [quimb_import_result()]

    small_ops = make_1d_ops(10, depth=4, entangling=True)
    dense_t = time_call(lambda: dense_amplitude(10, small_ops), repeats=3, warmup=1)
    tensor_t = time_call(lambda: tensor_amplitude(10, small_ops), repeats=3, warmup=1)
    dense_val = dense_amplitude(10, small_ops)
    tensor_val = tensor_amplitude(10, small_ops)
    error = abs(dense_val - tensor_val)
    results.append(BenchResult(
        "tensor_matches_dense_10q",
        "PASS" if error < 1e-8 else "FAIL",
        {
            "abs_error": float(error),
            "dense_ms": round(dense_t["ms_median"], 4),
            "tensor_ms": round(tensor_t["ms_median"], 4),
        },
        f"error={error:.2e}, dense={dense_t['ms_median']:.3f}ms tensor={tensor_t['ms_median']:.3f}ms",
    ))

    big_low_ent = make_1d_ops(40, depth=3, entangling=False)
    route, metric = estimate_tensor_route(40, big_low_ent)
    tensor_t = time_call(lambda: tensor_amplitude(40, big_low_ent), repeats=3, warmup=1)
    results.append(BenchResult(
        "route_40q_low_entanglement",
        "PASS" if route == "tensor" and tensor_t["ms_median"] < 1000 else "FAIL",
        {**metric, "route": route, "tensor_ms": round(tensor_t["ms_median"], 4)},
        f"route={route}, width={metric['contraction_width_log2']}, tensor={tensor_t['ms_median']:.2f}ms",
    ))

    big_ent = make_1d_ops(24, depth=12, entangling=True)
    route, metric = estimate_tensor_route(24, big_ent)
    tensor_t = time_call(lambda: tensor_amplitude(24, big_ent), repeats=3, warmup=1)
    results.append(BenchResult(
        "route_24q_1d_entangled",
        "PASS" if route == "tensor" and tensor_t["ms_median"] < 1000 else "FAIL",
        {**metric, "route": route, "tensor_ms": round(tensor_t["ms_median"], 4)},
        f"route={route}, width={metric['contraction_width_log2']}, tensor={tensor_t['ms_median']:.2f}ms",
    ))

    return report("Benchmark 6: cotengra tensor routing", results)


if __name__ == "__main__":
    run()
