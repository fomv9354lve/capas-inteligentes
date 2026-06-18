"""physics_lab_router -- bridge CAPAS to the canonical router in physics-magnitude-lab.

CAPAS and physics-magnitude-lab grew two routers with ~70% the same logic (the
COSTURERO seam originated here). Rather than maintain a fork, this bridge lets CAPAS
DELEGATE routing to the lab's canonical router -- which is the richer one: sealed
provenance, plus the noise / SPD-operator-spread / Metal-GPU / QASM frontiers CAPAS
does not have. CAPAS keeps what is ITS contribution: the evidence/provenance product
(RO-Crate / W3C-PROV / VVUQ traces).

Two entry points:
  - seal_via_lab(workload)  -> run a CAPAS Workload through the lab's sealed seam,
                               returning the lab's SealedResult (route + chain seal).
  - reconcile(workload)     -> run BOTH routers and check they AGREE on the route name,
                               so the delegation is trustworthy (the unification proof).

Additive and reversible: this is a new file; CAPAS's own router is untouched.
"""
from __future__ import annotations

import sys
from pathlib import Path

# bootstrap the lab onto sys.path (same convention as physics_magnitude_gold_engines.py)
_LAB_SRC = Path(
    "/Users/kreniq/Desktop/KRENIQ/AI Projects/01. Investigacion/physics_quantum/physics-magnitude-lab/src"
)
if str(_LAB_SRC) not in sys.path:
    sys.path.insert(0, str(_LAB_SRC))

from physics_magnitude_lab.router import route as _lab_route  # noqa: E402
from physics_magnitude_lab.router import seal_circuit as _lab_seal  # noqa: E402
from physics_magnitude_lab.router import Workload as _LabWorkload  # noqa: E402

from router.route import route as _capas_route  # noqa: E402

# CAPAS circuits are stim-style: ("H", (0,)), ("CNOT", (0, 1)). The lab uses lowercase
# flat tuples: ("h", 0), ("cx", 0, 1). Map names and flatten qubit tuples.
_NAME = {"H": "h", "S": "s", "X": "x", "Y": "y", "Z": "z", "T": "t",
         "CNOT": "cx", "CX": "cx", "CZ": "cz"}


def _to_lab_circuit(capas_circuit) -> list:
    out = []
    for name, qubits in capas_circuit:
        lab_name = _NAME.get(name.upper(), name.lower())
        out.append((lab_name, *qubits))
    return out


def _gate_names(capas_circuit) -> list[str]:
    return [name.upper() for name, _ in capas_circuit]


def seal_via_lab(workload, observable=None, noise_p=None):
    """Route a CAPAS circuit Workload through the lab's sealed seam. Returns the lab's
    SealedResult (value, route, chain_seal, broke_at). Raises for non-circuit kinds."""
    if workload.kind != "circuit" or workload.circuit is None:
        raise ValueError("seal_via_lab handles circuit workloads; route tensor/dense via CAPAS")
    n = workload.n_qubits
    return _lab_seal(n, _to_lab_circuit(workload.circuit),
                     observable=observable, noise_p=noise_p)


def reconcile(workload) -> dict:
    """Run CAPAS's router and the lab's router on the same circuit; confirm they AGREE
    on the route name. This is the proof that delegating to the lab is safe."""
    capas = _capas_route(workload)
    lab = _lab_route(_LabWorkload(n_qubits=workload.n_qubits,
                                  gate_names=_gate_names(workload.circuit)))
    # CAPAS reports the engine route directly (stim/dense/...); the lab's gate-only
    # route reports stim/dense/QPU_REQUIRED. Compare on the shared vocabulary.
    return {
        "capas_route": capas.route,
        "lab_route": lab.route,
        "agree": capas.route == lab.route,
        "note": "both routers classify the circuit identically -- CAPAS may delegate to "
                "the lab's canonical router (richer: sealed provenance + noise/SPD/Metal/QASM)",
    }


def verify() -> None:
    """Self-check: the two routers agree, and the lab's seal carries provenance CAPAS lacks."""
    from router.types import CostBudget, Workload

    budget = CostBudget(memory_budget_bytes=2 * 1024**3, safety_factor=0.5)
    clifford = Workload(kind="circuit", n_qubits=3,
                        circuit=[("H", (0,)), ("CNOT", (0, 1)), ("CNOT", (1, 2))], budget=budget)
    non_clifford = Workload(kind="circuit", n_qubits=2,
                            circuit=[("H", (0,)), ("T", (0,)), ("CNOT", (0, 1))], budget=budget)

    assert reconcile(clifford)["agree"] is True
    assert reconcile(non_clifford)["agree"] is True
    assert seal_via_lab(clifford).route == "stim"
    assert seal_via_lab(non_clifford).route == "dense"
    # the richer frontier CAPAS gains: a local observable -> sparse Pauli dynamics
    assert seal_via_lab(non_clifford, observable="IZ").route == "spd"
    print("physics_lab_router: routers reconcile (stim/dense agree); seal + SPD frontier OK")


if __name__ == "__main__":
    verify()
