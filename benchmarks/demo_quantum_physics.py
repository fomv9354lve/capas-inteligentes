"""Demo + check: CAPAS gates quantum CALIBRATION/RESULT claims against textbook physics —
no device needed. Driven by REAL ibm_kingston atlas numbers (22/06/2026 calibration snapshot).

Every assertion is a deterministic re-derivation (record<->text): a claim that violates a
physical invariant is flagged WITHOUT measuring anything. This is CAPAS's exact-GATE domain
applied to quantum claims.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import capas_quantum_physics as P


def run() -> int:
    checks = []

    # 1. Coherence: Q121 has T1=11.2, T2=23.44 -> T2/T1=2.09 > 2. Undeclared method -> FLAG.
    q121 = P.check_coherence(11.2, 23.44, method="ramsey")
    checks.append(("Q121 T2/T1=2.09 (undeclared) -> FLAG_INCONSISTENT (active TLS / hidden CPMG)",
                   q121["verdict"] == "FLAG_INCONSISTENT"))
    # ...same numbers, but DECLARED as CPMG -> ADMISSIBLE (DD lifts the bound honestly)
    q121_dd = P.check_coherence(11.2, 23.44, method="CPMG")
    checks.append(("Q121 same numbers but method=CPMG -> ADMISSIBLE (DD refocuses TLS, honest)",
                   q121_dd["verdict"] == "ADMISSIBLE"))
    # ...a normal qubit Q0 T1=327 T2=420 -> ratio 1.28 -> ADMISSIBLE
    q0c = P.check_coherence(327.36, 420.31)
    checks.append(("Q0 T2/T1=1.28 -> ADMISSIBLE (normal Markovian qubit)",
                   q0c["verdict"] == "ADMISSIBLE"))

    # 2. Thermal: Q2 P01=0.01172 P10=0.00342 -> n_th~0.41 (cold, atlas) -> ADMISSIBLE
    q2t = P.check_thermal(0.01172, 0.00342)
    checks.append((f"Q2 P01>P10 -> ADMISSIBLE, n_th={q2t['n_thermal']} photons (cold qubit, re-derived)",
                   q2t["verdict"] == "ADMISSIBLE"))
    # ...Q0 P01=0.0127 P10=0.00684 -> n_th~1.17 -> FLAG_HOT (atlas: "elevado, chip caliente")
    q0t = P.check_thermal(0.0127, 0.00684)
    checks.append((f"Q0 n_th={q0t['n_thermal']} photons -> FLAG_HOT (atlas agrees: resonator mis-thermalized)",
                   q0t["verdict"] == "FLAG_HOT"))
    # ...an inverted/fabricated row P10>P01 -> negative thermal population -> FLAG_UNPHYSICAL
    bad = P.check_thermal(0.004, 0.012)
    checks.append(("inverted readout P10>P01 -> FLAG_UNPHYSICAL (negative thermal population)",
                   bad["verdict"] == "FLAG_UNPHYSICAL"))

    # 3. Parallel readout: Q80 isolated MEAS=0.24% but MEAS_2=17.4% -> the floor blows up 71x.
    basis = P.check_readout_floor_basis([2.44e-3, 2.44e-3], [0.174, 0.174])
    checks.append((f"Q80 readout basis: parallel floor {basis['parallel_floor']:.1%} is "
                   f"{basis['blowup_x']}x isolated -> USE_PARALLEL (real circuits measure at once)",
                   basis["verdict"] == "USE_PARALLEL" and basis["blowup_x"] > 10))

    # 4. Circuit fidelity claim (atlas example: 20 qubits, 10 CZ layers, ~10 CZ + 20 SX/layer,
    #    zone-good errors). Budget predicts ~34% error -> ceiling ~0.66.
    budget = P.circuit_success_budget(20, 10, 10, 20, 2.02e-3, 2.675e-4, 7.935e-3)
    checks.append((f"20q/10-layer budget: predicted error {budget['predicted_error']:.1%} "
                   f"(atlas hand-calc ~33.7%) — multiplicative model re-derived",
                   0.28 < budget["predicted_error"] < 0.40))
    # ...a paper claiming 0.95 fidelity on that circuit is physically impossible -> FLAG_TOO_CLEAN
    claim = P.gate_circuit_fidelity_claim(0.95, 20, 10, 10, 20, 2.02e-3, 2.675e-4, 7.935e-3)
    checks.append(("claim of 0.95 fidelity on 20q/10-layer -> FLAG_TOO_CLEAN (above physical ceiling)",
                   claim["verdict"] == "FLAG_TOO_CLEAN"))
    # ...a claim of 0.66 (≈ ceiling) -> ADMISSIBLE
    ok_claim = P.gate_circuit_fidelity_claim(0.64, 20, 10, 10, 20, 2.02e-3, 2.675e-4, 7.935e-3)
    checks.append((f"claim of 0.64 on same circuit -> {ok_claim['verdict']} (matches ceiling "
                   f"{ok_claim['predicted_ceiling']:.2f})", ok_claim["verdict"] == "ADMISSIBLE"))

    # 5. Edge TLS: 111_112 CZ=0.185 RZZ=0.0019 -> RZZ/CZ=0.01 -> amplitude-resonant TLS -> FLAG.
    edge = P.check_edge_tls(0.1853, 1.887e-3)
    checks.append(("edge 111_112 CZ=18.5% but RZZ=0.19% -> FLAG_TLS_RESONANT_EDGE (CZ untrustworthy)",
                   edge["verdict"] == "FLAG_TLS_RESONANT_EDGE"))
    # ...best edge 82_83 CZ=9.1E-4 RZZ=8.46E-4 -> healthy
    good_edge = P.check_edge_tls(9.125e-4, 8.46e-4)
    checks.append(("best edge 82_83 CZ~RZZ -> ADMISSIBLE (no TLS signature)",
                   good_edge["verdict"] == "ADMISSIBLE"))

    # 6. Combined row audit: fail-closed — any flag dominates.
    audit = P.audit_calibration_row({
        "t1_us": 11.2, "t2_us": 23.44, "t2_method": "ramsey",
        "cz_error": 0.1853, "rzz_error": 1.887e-3,
    })
    checks.append((f"combined audit of Q121/111_112 row -> FLAG ({len(audit['flags'])} invariants), "
                   f"fail-closed", audit["verdict"] == "FLAG" and len(audit["flags"]) == 2))

    ok = all(c for _, c in checks)
    for label, c in checks:
        print(f"{'OK ' if c else 'XX '}{label}")
    print("QUANTUM-PHYSICS GATE (deterministic invariants, no device): pass" if ok
          else "QUANTUM-PHYSICS: FAILURES")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(run())
