"""CAPAS — quantum re-derivation rung (deterministic classical verification).

Lands the simulability frontier on real mathematics, not metaphor:

  * A circuit of Clifford gates + ``t`` non-Clifford (T-like) gates is classically
    simulable with cost ~ stabilizer rank of |T>^{⊗t} ≈ 2^{α t}, α≈0.40
    (Bravyi–Gosset, Quantum 2019); Clifford-only (t=0) is poly(n) (Gottesman–Knill).
  * Statevector simulation is exact but costs 2^n memory.

So a quantum-computation claim is GATEABLE by exact classical RE-SIMULATION iff it
is below the engine's simulability bound: n ≤ N_CAP (statevector) OR Clifford-only
OR T-count t ≤ T_CAP. Above that bound the engine does NOT pretend to simulate — it
routes to cryptographic Classical Verification of Quantum Computation (Mahadev,
under LWE) if a proof is supplied, else ATTEST. Deterministic, no LLM.
"""
from __future__ import annotations

import math
from typing import Any

import numpy as np

# Engine simulability bounds (the real frontier).
N_CAP = 20                 # statevector: 2^20 complex amps ≈ 16 MB
T_CAP = 40                 # stabilizer-rank sim: 2^{0.40·40} ≈ 2^16 stabilizer terms
ALPHA = 0.40               # Bravyi–Gosset stabilizer-rank exponent (≈0.396)
_EPS = 1e-6

_CLIFFORD = {"h", "x", "y", "z", "s", "sdg", "cx", "cnot", "cz", "id", "i"}
_SQRT2I = 1.0 / math.sqrt(2.0)

_GATES_1Q: dict[str, np.ndarray] = {
    "h": np.array([[_SQRT2I, _SQRT2I], [_SQRT2I, -_SQRT2I]], complex),
    "x": np.array([[0, 1], [1, 0]], complex),
    "y": np.array([[0, -1j], [1j, 0]], complex),
    "z": np.array([[1, 0], [0, -1]], complex),
    "s": np.array([[1, 0], [0, 1j]], complex),
    "sdg": np.array([[1, 0], [0, -1j]], complex),
    "t": np.array([[1, 0], [0, np.exp(1j * math.pi / 4)]], complex),
    "tdg": np.array([[1, 0], [0, np.exp(-1j * math.pi / 4)]], complex),
    "id": np.eye(2, dtype=complex),
    "i": np.eye(2, dtype=complex),
}


def _rot(axis: str, theta: float) -> np.ndarray:
    c, s = math.cos(theta / 2), math.sin(theta / 2)
    if axis == "rx":
        return np.array([[c, -1j * s], [-1j * s, c]], complex)
    if axis == "ry":
        return np.array([[c, -s], [s, c]], complex)
    return np.array([[np.exp(-1j * theta / 2), 0], [0, np.exp(1j * theta / 2)]], complex)  # rz


def _is_clifford_gate(g: dict[str, Any]) -> bool:
    name = str(g.get("gate", "")).lower()
    if name in _CLIFFORD:
        return True
    if name in ("rx", "ry", "rz"):  # Clifford only at multiples of π/2
        theta = float(g.get("theta", g.get("params", [0])[0] if g.get("params") else 0))
        k = theta / (math.pi / 2)
        return abs(k - round(k)) < 1e-9
    return False


def classify(circuit: dict[str, Any]) -> dict[str, Any]:
    n = int(circuit.get("qubits", 0))
    gates = circuit.get("gates", []) or []
    t_count = sum(0 if _is_clifford_gate(g) else 1 for g in gates)
    clifford_only = t_count == 0
    # exact-simulability cost estimate (log2): min(statevector, stabilizer-rank)
    log2_statevector = n
    log2_stabrank = ALPHA * t_count + math.log2(max(n, 1) ** 2)  # poly(n)·2^{αt}
    simulable = (n <= N_CAP) or clifford_only or (t_count <= T_CAP)
    return {
        "qubits": n, "t_count": t_count, "clifford_only": clifford_only,
        "log2_cost_statevector": round(log2_statevector, 2),
        "log2_cost_stabilizer_rank": round(log2_stabrank, 2),
        "simulable_by_engine": bool(simulable),
        "engine_statevector_runnable": n <= N_CAP,
        "frontier_basis": "Gottesman-Knill (t=0) / Bravyi-Gosset 2^{0.40 t} / statevector 2^n",
    }


# ── exact statevector simulation ──
def _apply_1q(state: np.ndarray, U: np.ndarray, q: int, n: int) -> np.ndarray:
    s = state.reshape([2] * n)
    s = np.tensordot(U, s, axes=([1], [q]))
    return np.moveaxis(s, 0, q).reshape(-1)


def _apply_2q(state: np.ndarray, U4: np.ndarray, q1: int, q2: int, n: int) -> np.ndarray:
    s = state.reshape([2] * n)
    s = np.tensordot(U4.reshape(2, 2, 2, 2), s, axes=([2, 3], [q1, q2]))
    return np.moveaxis(s, [0, 1], [q1, q2]).reshape(-1)


_CX = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]], complex)
_CZ = np.diag([1, 1, 1, -1]).astype(complex)


def simulate(circuit: dict[str, Any]) -> np.ndarray:
    n = int(circuit["qubits"])
    if n > N_CAP:
        raise ValueError(f"n={n} exceeds engine statevector cap N_CAP={N_CAP}")
    state = np.zeros(2 ** n, complex)
    state[0] = 1.0
    for g in circuit.get("gates", []):
        name = str(g.get("gate", "")).lower()
        qs = g.get("qubits", [])
        if name in ("cx", "cnot"):
            state = _apply_2q(state, _CX, qs[0], qs[1], n)
        elif name == "cz":
            state = _apply_2q(state, _CZ, qs[0], qs[1], n)
        elif name in ("rx", "ry", "rz"):
            theta = float(g.get("theta", g.get("params", [0])[0] if g.get("params") else 0))
            state = _apply_1q(state, _rot(name, theta), qs[0], n)
        elif name in _GATES_1Q:
            state = _apply_1q(state, _GATES_1Q[name], qs[0], n)
        else:
            raise ValueError(f"unknown gate '{name}'")
    return state


def _probability(state: np.ndarray, bitstring: str) -> float:
    idx = int(bitstring, 2)
    return float(abs(state[idx]) ** 2)


def _expectation_z(state: np.ndarray, qubits: list[int], n: int) -> float:
    probs = np.abs(state) ** 2
    total = 0.0
    for b in range(len(state)):
        parity = sum((b >> (n - 1 - q)) & 1 for q in qubits) % 2
        total += probs[b] * (1.0 if parity == 0 else -1.0)
    return float(total)


def rederive_quantum(evidence: dict[str, Any]) -> dict[str, Any] | None:
    """Re-simulate a quantum-circuit claim if below the frontier; else classify the
    cryptographic/attestation route. Returns match True/False/None."""
    circ = evidence.get("quantum_circuit")
    if not isinstance(circ, dict):
        return None
    cls = classify(circ)
    if not cls["engine_statevector_runnable"]:
        # Beyond exact re-simulation: route, do not fake.
        route = "cvqc-mahadev" if evidence.get("quantum_proof") else "attest"
        return {**cls, "match": None, "status": "BEYOND_FRONTIER", "route": route,
                "note": "Exact classical re-simulation infeasible; verify via Classical "
                        "Verification of Quantum Computation (LWE) or attest a real QC."}
    n = cls["qubits"]
    state = simulate(circ)
    claim = circ.get("claim", {}) or {}
    ctype, tol = claim.get("type"), float(claim.get("tolerance", 0) or 0)
    if ctype == "probability":
        val = _probability(state, str(claim["bitstring"]))
    elif ctype == "expectation":
        val = _expectation_z(state, list(claim.get("qubits", [])), n)
    elif ctype == "amplitude":
        idx = int(str(claim["bitstring"]), 2)
        val = complex(state[idx])
        declared = complex(claim.get("value"))
        return {**cls, "claim_type": ctype, "re_derived": [val.real, val.imag],
                "match": abs(val - declared) <= max(tol, _EPS)}
    else:
        return {**cls, "match": None, "status": "UNSUPPORTED_CLAIM"}
    declared = float(claim.get("value"))
    return {**cls, "claim_type": ctype, "re_derived": round(val, 8),
            "declared": declared, "match": abs(val - declared) <= max(tol, _EPS)}
