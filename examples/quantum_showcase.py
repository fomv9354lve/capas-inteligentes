"""CAPAS x real quantum hardware — the one point where CAPAS touches physical reality.

A Bell circuit on a real IBM QPU. CAPAS RE-DERIVES the ideal output (GATE, exact classical
simulation) and ingests the noisy HARDWARE measurement as a real-world response (ATTEST),
measuring the noise as the residual. Ideal = GATE (re-derivable). Hardware = ATTEST (the
world responding, not re-derivable). The gap = measured noise.

Reads the IBM token from ~/Downloads/apikey (1).json (never printed/committed).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import capas_quantum

TOKEN = json.load(open("/Users/kreniq/Downloads/apikey (1).json"))["apikey"]


def run() -> int:
    from qiskit import QuantumCircuit, transpile
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2

    svc = QiskitRuntimeService(channel="ibm_quantum_platform", token=TOKEN)
    backend = svc.least_busy(operational=True, simulator=False)
    print(f"backend: {backend.name} ({backend.num_qubits} qubits) | queue: {backend.status().pending_jobs} jobs")

    qc = QuantumCircuit(2)
    qc.h(0); qc.cx(0, 1); qc.measure_all()
    tqc = transpile(qc, backend, optimization_level=1)

    print("submitting Bell (1024 shots) to REAL hardware... (queue wait, ~seconds of QPU)")
    sampler = SamplerV2(mode=backend)
    job = sampler.run([tqc], shots=1024)
    print("job id:", job.job_id())
    res = job.result()
    counts = res[0].data.meas.get_counts()
    total = sum(counts.values())
    print(f"\nHARDWARE measurement (noisy, real): {counts}")

    # CAPAS re-derives the IDEAL Bell distribution (GATE — exact classical simulation)
    ideal_state = capas_quantum.simulate({"qubits": 2, "gates": [{"gate": "H", "qubits": [0]}, {"gate": "CX", "qubits": [0, 1]}]})
    import numpy as np
    ideal_probs = {f"{i:02b}": float(abs(ideal_state[i]) ** 2) for i in range(4)}
    ideal_support = {k for k, p in ideal_probs.items() if p > 1e-9}      # {'00','11'}
    print(f"IDEAL (CAPAS re-derived, GATE): {{k: round(v,3) for k,v in ideal_probs.items() if v>1e-9}}")

    # residual = fraction of shots OUTSIDE the ideal support = measured noise
    off = sum(v for k, v in counts.items() if k.replace(" ", "") not in ideal_support)
    noise = off / total
    print("\n=== CAPAS verdict on a REAL physical measurement ===")
    print(f"  GATE  (ideal, re-derived):   support {sorted(ideal_support)}, exact")
    print(f"  ATTEST (hardware, the world): measured on {backend.name}, NOT re-derivable")
    print(f"  RESIDUAL (noise): {noise:.1%} of shots fell outside the ideal support")
    print(f"  -> the world responded; CAPAS placed it: ideal is GATEd, hardware is ATTESTed, noise measured.")
    print(f"     This is the only place CAPAS crosses text<->reality with a real measurement.")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
