"""READY-TO-FIRE stress test for CAPAS's layer-3 (measurement) gate on REAL hardware — the
discriminating half the clean Bell did NOT exercise. Targets the HARD 20% of the QPU.

It submits, in one batch:
  A) a clean Bell on the BEST edge (Q0-Q1) at HIGH shots  -> makes 'too clean' resolvable
  B) a Bell forced onto a TLS-degraded edge (116-121, CZ~7.5%)  -> expect FLAG_TOO_NOISY
  C) a Bell forced onto the worst edge (111-112, CZ~18.5%)      -> expect FLAG_TOO_NOISY

then gates each measurement TWO ways:
  - against its OWN edge's calibrated floor (should be ADMISSIBLE — CAPAS tracks real physics)
  - against the GOOD-edge prediction (the false claim 'this is a clean Bell') -> FLAG_TOO_NOISY

This converts the showcase from 'admits honest data' (true-negative) into 'discriminates honest
from anomalous on real hardware' (true-positive). Needs queue budget. Token read from file,
never printed/committed. Run:  python3 examples/kingston_stress_test.py

The bad edges are LABELED GROUND TRUTH: CAPAS already predicted them from calibration
(examples/kingston_live_audit.py). A FLAG here is a confirmed true-positive, not a guess.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import capas_quantum_hw as HW

TOKEN_FILE = "/Users/kreniq/Downloads/apikey (1).json"
OUT = "/tmp/kingston_stress_verdicts.json"
HIGH_SHOTS = 100_000
BAD_SHOTS = 4096

# (label, physical qubit pair, shots, expectation)
TARGETS = [
    ("clean_best_Q0Q1_highshots", (0, 1), HIGH_SHOTS, "ADMISSIBLE + too_clean now resolvable"),
    ("bad_edge_116_121", (116, 121), BAD_SHOTS, "FLAG_TOO_NOISY"),
    ("worst_edge_111_112", (111, 112), BAD_SHOTS, "FLAG_TOO_NOISY"),
]


def _calib_for(props, a: int, b: int) -> dict:
    """Live calibration for an edge -> the dict CAPAS's first-order gate needs."""
    cz = props.gate_error("cz", [a, b])
    return {"cz_error": cz, "readout_q0": props.readout_error(a),
            "readout_q1": props.readout_error(b), "backend": "ibm_kingston",
            "edge": [a, b]}


def main() -> int:
    tok = json.load(open(TOKEN_FILE))["apikey"]
    from qiskit import QuantumCircuit, transpile
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2

    service = QiskitRuntimeService(channel="ibm_quantum_platform", token=tok)
    backend = service.backend("ibm_kingston")
    props = backend.properties()

    # build one Bell per target, pinned to its physical qubits via initial_layout
    circuits, metas = [], []
    for label, (a, b), shots, expect in TARGETS:
        qc = QuantumCircuit(2, 2)
        qc.h(0); qc.cx(0, 1); qc.measure([0, 1], [0, 1])
        tqc = transpile(qc, backend, initial_layout=[a, b], optimization_level=1)
        circuits.append(tqc)
        metas.append({"label": label, "edge": [a, b], "shots": shots, "expect": expect})

    sampler = SamplerV2(mode=backend)
    # per-circuit shots: submit separately so each gets its own shot count
    jobs = []
    for tqc, m in zip(circuits, metas):
        jobs.append((sampler.run([tqc], shots=m["shots"]), m))
    print("submitted", len(jobs), "stress circuits; waiting (this uses queue time)...")

    good_cal = _calib_for(props, 0, 1)
    good_pred_floor = HW.predicted_noise_floor(good_cal)
    verdicts = []
    for job, m in jobs:
        while job.status() not in ("DONE", "ERROR", "CANCELLED"):
            time.sleep(20)
        res = job.result()[0]
        counts = res.data.c.get_counts() if hasattr(res.data, "c") else res.data.meas.get_counts()
        own_cal = _calib_for(props, *m["edge"])
        # gate 1: against its OWN edge physics (should be ADMISSIBLE — CAPAS tracks reality)
        v_own = HW.gate_hardware_claim({"00", "11"}, counts, own_cal)
        # gate 2: against the GOOD-edge claim ('this is a clean Bell') -> bad edges FLAG_TOO_NOISY
        v_claim = HW.gate_hardware_claim({"00", "11"}, counts, good_cal)
        verdicts.append({**m, "counts": counts, "own_edge_cz": own_cal["cz_error"],
                         "vs_own_physics": v_own["verdict"],
                         "vs_good_edge_claim": v_claim["verdict"],
                         "measured_error": v_own["measured_error"]})
        print(f"  {m['label']:28s} cz={own_cal['cz_error']:.2e} err={v_own['measured_error']:.1%} "
              f"-> own:{v_own['verdict']}  as-clean-claim:{v_claim['verdict']}  (expect {m['expect']})")

    json.dump({"good_edge_floor": good_pred_floor, "verdicts": verdicts}, open(OUT, "w"), indent=2)
    flagged = [v for v in verdicts if v["vs_good_edge_claim"] == "FLAG_TOO_NOISY"]
    print(f"\nTRUE-POSITIVES (bad edges flagged when claimed as clean): {len(flagged)}/2 expected")
    print(f"saved -> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
