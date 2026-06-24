# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""CLOSE the structural behavior of the quantum-advantage / commitment-depth gate.

The physics (validated same-device in physics-magnitude-lab): noise forces a circuit to COMMIT from
quantum to classical at a measured depth. The gate turns that into admissibility: a quantum-advantage
claim at a depth PAST the commitment depth is licensed only as a classically-reproducible result. This
pins the contract (not the empirical frontier, which is SCOPED): the defeater fires iff the claim
asserts hardness AND the claimed depth exceeds the commitment depth.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import capas_quantum_physics as Q


def run() -> int:
    G = Q.gate_quantum_advantage_claim
    checks = [
        ("advantage past commitment depth -> flagged classically reproducible",
         G(claimed_circuit_depth=24, commitment_depth=8).get("verdict") == "FLAG_CLASSICALLY_REPRODUCIBLE"),
        ("advantage within commitment depth -> admissible",
         G(claimed_circuit_depth=6, commitment_depth=8).get("verdict") == "ADMISSIBLE"),
        ("no hardness asserted -> commitment depth does not bound the claim",
         G(claimed_circuit_depth=24, commitment_depth=8, asserts_quantum_hardness=False).get("verdict") == "ADMISSIBLE"),
        ("exactly at commitment depth -> admissible (not past it)",
         G(claimed_circuit_depth=8, commitment_depth=8).get("verdict") == "ADMISSIBLE"),
        # monotone in noise: a shallower commitment depth (noisier device) flags MORE claims, never fewer
        ("monotone: noisier (earlier commit) defeats at least as many claims",
         all(G(claimed_circuit_depth=10, commitment_depth=c)["committed_before_claim"] for c in (4, 6, 8))
         and not G(claimed_circuit_depth=10, commitment_depth=12)["committed_before_claim"]),
    ]
    ok = all(c for _, c in checks)
    for label, c in checks:
        print(f"{'OK ' if c else 'XX '}{label}")
    print("QUANTUM COMMITMENT GATE: pass — the commitment-depth defeater fires exactly when a hardness "
          "claim runs past the depth the device stays uncommitted. (Empirical frontier is SCOPED: "
          "same-device validated; cross-device pending.)" if ok
          else "QUANTUM COMMITMENT GATE: FAILURES — fix before relying on it.")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(run())
