"""Verify CAPAS's XEB + speckle-purity circuit-level coherence gate on a SIMULATOR before any
QPU time. The decisive property: it must SEPARATE coherent from incoherent error.
  - noiseless          -> F_xeb ~ 1, F_purity ~ 1
  - depolarizing       -> F_xeb ~ F_purity (gap small)  -> INCOHERENT_FUNDAMENTAL
  - coherent over-rot  -> F_purity >> F_xeb             -> FLAG_COHERENT_RECOVERABLE
This proves the test can detect WHY an inferred (incoherent) model is pessimistic for a partly-
coherent device — the hypothesis behind the hard-20% inference error.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import capas_quantum_physics as P


def _rand_xeb_circuit(depth: int, seed: int, over_rot: float = 0.0):
    """A 2-qubit XEB circuit: alternating random single-qubit gates + CZ, repeated to `depth`.
    over_rot injects a COHERENT error (a fixed extra RZ on every layer)."""
    from qiskit import QuantumCircuit
    import random
    rng = random.Random(seed)
    qc = QuantumCircuit(2)
    singles = ["sx", "sy", "sw"]  # sqrt-X, sqrt-Y, sqrt-W (Google XEB set)
    for d in range(depth):
        for q in (0, 1):
            g = rng.choice(singles)
            if g == "sx":
                qc.rx(math.pi / 2 + over_rot, q)
            elif g == "sy":
                qc.ry(math.pi / 2 + over_rot, q)
            else:
                qc.rz(math.pi / 4, q); qc.rx(math.pi / 2 + over_rot, q); qc.rz(-math.pi / 4, q)
        qc.cz(0, 1)
    return qc


def _ideal_probs(qc):
    from qiskit.quantum_info import Statevector
    return {k: float(v) for k, v in Statevector(qc).probabilities_dict().items()}


def _run(qc, noise=None, shots=8192):
    from qiskit_aer import AerSimulator
    from qiskit import transpile
    m = qc.copy(); m.measure_all()
    sim = AerSimulator(noise_model=noise)
    res = sim.run(transpile(m, sim), shots=shots).result()
    return res.get_counts()


def _avg(metric, circuits_data):
    return sum(metric(*c) for c in circuits_data) / len(circuits_data)


def run() -> int:
    from qiskit_aer.noise import NoiseModel, depolarizing_error
    checks = []
    NC, DEPTH = 8, 10
    seeds = list(range(NC))

    # depolarizing noise model (incoherent)
    nm = NoiseModel()
    nm.add_all_qubit_quantum_error(depolarizing_error(0.02, 1), ["rx", "ry", "rz"])
    nm.add_all_qubit_quantum_error(depolarizing_error(0.04, 2), ["cz"])

    def measure(over_rot, noise, tag):
        fx, fp = [], []
        for s in seeds:
            clean = _rand_xeb_circuit(DEPTH, s, over_rot=0.0)   # IDEAL = clean circuit
            ideal = _ideal_probs(clean)
            executed = _rand_xeb_circuit(DEPTH, s, over_rot=over_rot)  # injected coherent error
            counts = _run(executed, noise=noise)
            fx.append(P.xeb_linear_fidelity(ideal, counts))
            fp.append(P.speckle_purity_fidelity(counts, 2))
        F, Fp = sum(fx) / NC, sum(fp) / NC
        v = P.coherent_fraction_verdict(F, Fp, DEPTH)
        print(f"  {tag:24s} F_xeb={F:.3f} F_purity={Fp:.3f} coh={v['coherent_fraction']:.2f} -> {v['verdict']}")
        return F, Fp, v

    Fn, Fpn, _ = measure(0.0, None, "noiseless")
    checks.append(("noiseless -> F_xeb~1 and F_purity~1", Fn > 0.97 and Fpn > 0.95))

    Fd, Fpd, vd = measure(0.0, nm, "depolarizing (incoherent)")
    checks.append(("depolarizing -> F_xeb ~ F_purity (small gap)", abs(Fd - Fpd) < 0.12))
    checks.append(("depolarizing -> NOT flagged coherent", vd["verdict"] != "FLAG_COHERENT_RECOVERABLE"))

    Fc, Fpc, vc = measure(0.12, None, "coherent over-rotation")
    checks.append(("coherent -> F_purity strictly > F_xeb (gap isolates coherent error)", Fpc > Fc + 0.05))
    checks.append(("coherent -> FLAG_COHERENT_RECOVERABLE (recalibratable, not fundamental)",
                   vc["verdict"] == "FLAG_COHERENT_RECOVERABLE"))

    # consolidation: the budget-reconciliation must NOT flag a coherent-error device as too-clean,
    # and SHOULD flag a low-coherence over-clean result for investigation.
    rc_coh = P.reconcile_budget_with_measurement(0.73, 0.56, coherent_fraction=0.6, depth=24)
    rc_low = P.reconcile_budget_with_measurement(0.73, 0.56, coherent_fraction=0.1, depth=24)
    rc_in = P.reconcile_budget_with_measurement(0.55, 0.56, coherent_fraction=0.5, depth=24)
    checks.append(("reconcile: above budget + coherent -> BUDGET_PESSIMISTIC_COHERENT (not too-clean)",
                   rc_coh["verdict"] == "BUDGET_PESSIMISTIC_COHERENT"))
    checks.append(("reconcile: above budget + LOW coherent -> ABOVE_BUDGET_LOW_COHERENCE (investigate)",
                   rc_low["verdict"] == "ABOVE_BUDGET_LOW_COHERENCE"))
    checks.append(("reconcile: within budget -> WITHIN_BUDGET", rc_in["verdict"] == "WITHIN_BUDGET"))

    ok = all(c for _, c in checks)
    print()
    for label, c in checks:
        print(f"{'OK ' if c else 'XX '}{label}")
    print("XEB+PURITY GATE: pass (separates coherent from incoherent — ready for QPU)" if ok
          else "XEB+PURITY GATE: FAILURES (do NOT spend QPU)")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(run())
