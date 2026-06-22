"""THE DEFINITIVE TEST — submit one XEB+speckle-purity sweep to ibm_kingston.

From a SINGLE job (frugal QPU) it yields three results the clean Bell could not:
  1. the ground-truth XEB-vs-depth curve (corrects the inferred-20% error, mean 0.14);
  2. the COHERENT vs INCOHERENT split (purity is FREE from the same circuits, zero extra QPU) —
     testing the hypothesis that the inference was pessimistic because the error is partly
     coherent (recalibratable), not fundamental;
  3. cross-validation: the SAME protocol on a CAPAS-predicted-GOOD edge and a CAPAS-predicted-
     MODERATELY-BAD edge — does the XEB ordering match what CAPAS flagged from calibration alone?

One job, 2 edges x 4 depths x N circuits, shots each. Edges auto-picked from live calibration
(override: argv = "a,b a2,b2"). Token from file, never printed/committed. Saves the ideal probs +
job id to /tmp/xeb_submit.json for the analyzer.
"""
from __future__ import annotations

import json
import math
import random
import sys
from pathlib import Path

TOKEN_FILE = "/Users/kreniq/Downloads/apikey (1).json"
OUT = "/tmp/xeb_submit.json"
# 9 depth points -> max conformal coverage n/(n+1) = 90% (vs 80% at 5 / 83% max at 4-5).
# Spans 2..30 so the kappa fit and the depth-extrapolation band both have real leverage.
DEPTHS = [2, 4, 6, 8, 12, 16, 20, 25, 30]
N_CIRCUITS = 10
SHOTS = 4096


def _xeb_circuit(depth: int, seed: int):
    from qiskit import QuantumCircuit
    rng = random.Random(seed)
    qc = QuantumCircuit(2)
    for _ in range(depth):
        for q in (0, 1):
            g = rng.choice(("sx", "sy", "sw"))
            if g == "sx":
                qc.rx(math.pi / 2, q)
            elif g == "sy":
                qc.ry(math.pi / 2, q)
            else:
                qc.rz(math.pi / 4, q); qc.rx(math.pi / 2, q); qc.rz(-math.pi / 4, q)
        qc.cz(0, 1)
    return qc


def _pick_edges(props, coupling):
    """Pick a CAPAS-good edge (min CZ) and a moderately-bad one (CZ ~1e-2, the band that gives
    XEB~0.7 at depth 24), avoiding catastrophic TLS edges (>3e-2) that floor out."""
    cz = {}
    for e in sorted({tuple(sorted(x)) for x in coupling}):
        try:
            cz[e] = props.gate_error("cz", list(e))
        except Exception:
            pass
    good = min(cz, key=cz.get)
    moderate = min(cz, key=lambda e: abs(math.log10(cz[e]) - math.log10(1e-2)) if 3e-3 < cz[e] < 3e-2 else 1e9)
    return [(good, cz[good], "CAPAS-good"), (moderate, cz[moderate], "CAPAS-moderately-bad")]


def main() -> int:
    tok = json.load(open(TOKEN_FILE))["apikey"]
    from qiskit import transpile
    from qiskit.quantum_info import Statevector
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2

    import os
    bk = os.environ.get("CAPAS_QPU_BACKEND", "ibm_kingston")  # least-queued: ibm_fez
    service = QiskitRuntimeService(channel="ibm_quantum_platform", token=tok)
    backend = service.backend(bk)
    props = backend.properties()

    if len(sys.argv) > 1:
        edges = []
        for spec in sys.argv[1:]:
            a, b = (int(x) for x in spec.split(","))
            try:
                czv = props.gate_error("cz", [a, b])
            except Exception:
                czv = None
            edges.append(((a, b), czv, "user-specified"))
    else:
        edges = _pick_edges(props, backend.coupling_map)
    print("edges:", [(list(e), f"CZ={c:.2e}" if c else "?", tag) for e, c, tag in edges])

    circuits, metas = [], []
    for (a, b), czv, tag in edges:
        for depth in DEPTHS:
            for s in range(N_CIRCUITS):
                qc = _xeb_circuit(depth, s)
                ideal = {k: float(v) for k, v in Statevector(qc).probabilities_dict().items()}
                qc.measure_all()
                tqc = transpile(qc, backend, initial_layout=[a, b], optimization_level=1)
                circuits.append(tqc)
                metas.append({"edge": [a, b], "edge_cz": czv, "edge_tag": tag,
                              "depth": depth, "seed": s, "ideal_probs": ideal})

    sampler = SamplerV2(mode=backend)
    job = sampler.run(circuits, shots=SHOTS)
    jid = job.job_id()
    json.dump({"job_id": jid, "backend": bk, "shots": SHOTS,
               "depths": DEPTHS, "n_circuits": N_CIRCUITS, "metas": metas}, open(OUT, "w"))
    print(f"SUBMITTED {len(circuits)} circuits in ONE job: {jid}")
    print(f"  {len(edges)} edges x {len(DEPTHS)} depths x {N_CIRCUITS} circuits x {SHOTS} shots")
    print(f"  saved ideal probs + job id -> {OUT}")
    print("  run examples/kingston_xeb_analyze.py (or the background poller) when it completes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
