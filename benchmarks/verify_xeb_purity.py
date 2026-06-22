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

    # kappa correlation-discount consolidation (the user's 0.401 result, structurally).
    # synth: real per-layer error = 0.40 * naive -> measured XEB = (1-0.40*naive)^d. Recover kappa.
    naive_err = 0.012
    depths_k = [2, 8, 16, 24]
    meas_xeb = [(1 - 0.40 * naive_err) ** d for d in depths_k]
    ke = P.estimate_kappa(depths_k, meas_xeb, naive_err)
    checks.append((f"estimate_kappa recovers ~0.40 from a correlated curve (got {ke['kappa']})",
                   ke["kappa"] is not None and abs(ke["kappa"] - 0.40) < 0.03))
    ad = P.apply_correlation_discount(naive_err, 0.401, conformal_halfwidth=0.065, coverage=0.80)
    checks.append((f"apply_correlation_discount(0.401) -> depth ceiling {ad['depth_ceiling_multiplier']}x "
                   f"(~2.5x) + band", ad["verdict"] == "CORRECTED" and abs(ad["depth_ceiling_multiplier"] - 2.49) < 0.1
                   and ad["conformal_band"] is not None))
    bad_k = P.apply_correlation_discount(naive_err, 1.3)
    checks.append(("apply_correlation_discount: kappa>1 -> FLAG_ANTICORRELATED (not silently used)",
                   bad_k["verdict"] == "FLAG_ANTICORRELATED"))

    # PIPELINE END-TO-END on a device-faithful simulator (the 'mucho cuidado' step before kingston):
    # replicate submit->analyze with TWO edges of known-different noise across the SCRAMBLED depth
    # range, and confirm the two failure modes the ibm_fez run exposed are fixed.
    from qiskit_aer.noise import NoiseModel, depolarizing_error

    def _noise(cz_err):
        nm = NoiseModel()
        nm.add_all_qubit_quantum_error(depolarizing_error(2.7e-4, 1), ["rx", "ry", "rz"])
        nm.add_all_qubit_quantum_error(depolarizing_error(cz_err, 2), ["cz"])
        return nm

    def _sweep(cz_err, depths, ncirc=8):
        nm = _noise(cz_err)
        out = []
        for d in depths:
            fxs = []
            for s in range(ncirc):
                qc = _rand_xeb_circuit(d, s * 7 + d)
                fxs.append(P.xeb_linear_fidelity(_ideal_probs(qc), _run(qc, noise=nm, shots=4096)))
            out.append(sum(fxs) / ncirc)
        return out

    # noise levels chosen so the curves ACTUALLY DECAY (like the real ~0.73@depth24 data) — kappa
    # is only identifiable where there is real decay (a too-good edge stays ~1 and kappa is noise).
    sweep_depths = [6, 8, 12, 16, 20, 28]
    good = _sweep(0.01, sweep_depths)    # decays to ~0.8 — kappa identifiable here
    bad = _sweep(0.04, sweep_depths)     # 4x CZ, decays hard -> clear ordering
    # failure mode 1 (fixed): kappa in the scrambled regime is finite & sensible, NOT garbage (was 32.7)
    kap = P.estimate_kappa(sweep_depths, good, naive_layer_error=1 - (1 - 0.01) * (1 - 2.7e-4) ** 2, min_depth=6)
    checks.append((f"pipeline: kappa from a DECAYING scrambled curve is sane (got {kap['kappa']}, not garbage)",
                   kap["kappa"] is not None and 0.3 < kap["kappa"] < 2.0))
    # failure mode 2 (the fez cross-val failure): with a REAL 10x noise gap, good edge beats bad edge
    deep_good, deep_bad = good[-1], bad[-1]
    checks.append((f"pipeline: good edge XEB {deep_good:.3f} > bad edge {deep_bad:.3f} at depth "
                   f"{sweep_depths[-1]} (ordering holds with a real gap)", deep_good > deep_bad))

    ok = all(c for _, c in checks)
    print()
    for label, c in checks:
        print(f"{'OK ' if c else 'XX '}{label}")
    print("XEB+PURITY GATE: pass (separates coherent from incoherent — ready for QPU)" if ok
          else "XEB+PURITY GATE: FAILURES (do NOT spend QPU)")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(run())
