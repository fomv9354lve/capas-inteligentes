# CAPAS on quantum hardware — what is proven, what is trivial, what needs a stress test

*2026-06-22. Honest scope. Every result below is re-derivable: `examples/kingston_live_audit.py`,
`benchmarks/demo_quantum_physics.py`, `benchmarks/kingston_real_bell_verdict.json`.*

## Three layers (don't conflate them)

1. **Physical-consistency gates on REPORTED calibration** (text↔text, deterministic, no device).
   T2≤2T1, P01≥P10, CZ~RZZ, Γφ≥0, gate-error coherence floor, residual ZZ. These catch a
   *reported* number that violates physics. — **Proven** (13/13 on real atlas numbers).
2. **Live calibration audit** — run layer 1 over the device's live calibration.
   CAPAS independently re-found Q121 (the one T2>2T1 qubit) and the 12-edge TLS cluster, with
   **0 false flags** on honest vendor data. — **Proven** (`kingston_live_audit.py`).
3. **Measurement vs calibrated noise model** (text↔**reality**, two oracles: ideal re-derivation
   + IBM's Aer noise model). This is the only layer that crosses to the physical world. — see below.

## The real-hardware result (layer 3)

A live Bell on ibm_kingston Q0-Q1 returned `{00:503, 11:475, 01:43, 10:3}` (1024 shots, 4.5%
off the ideal {00,11}). Both gates → **ADMISSIBLE**:
- first-order: 4.5% within the [0.6%, 6.1%] band around the 2.0% floor;
- calibration-grade: noise signature 0.0449 vs Aer-predicted 0.0206, within the 1024-shot
  margin (0.0938). The gate **honestly reports** 'too clean' is not resolvable at this shot count.
- The 43-vs-3 error asymmetry is readout relaxation asymmetry (P01≫P10), consistent with the
  thermal invariant — the numbers close on each other.

## Was this test trivial? — Largely YES, and it matters.

A 2-qubit Bell on the **best edge** is the easiest possible circuit. It proved exactly one thing:
the gate **admits an honest measurement** — a true-negative, no false positive. It did **NOT**
exercise the gate's discriminating power, for two reasons:
- the only failing verdict reachable by a clean Bell is TOO_NOISY, and a clean Bell isn't noisy;
- 'too clean' was **statistically unresolvable** at 1024 shots, so the fabrication-direction
  could not have fired even if warranted.

So layer 3's **FLAG path is untested on real hardware.** We have proven CAPAS doesn't cry wolf;
we have **not** yet proven it catches a wolf on a live measurement.

## What a real stress test is (and why your hard-20% run IS it)

The validation is a 2×2: true-negative (admit honest) AND true-positive (flag anomalous).
The easy 80% of the QPU gives the first; **the hard 20% gives the second.** Concretely:

| Stress axis | How | CAPAS should return | Tests |
|---|---|---|---|
| Bad-edge measurement | Bell forced onto a TLS-degraded edge (111-112 CZ 18.5%, 116-121 7.5%) | **FLAG_TOO_NOISY** | layer-3 true-positive on real HW |
| Wrong-device claim | a good-edge-looking result actually run on a bad edge | **FLAG_TOO_NOISY** | "ran somewhere else than claimed" |
| Fabrication / too-clean | clean Bell at **100k+ shots**, then post-select/filter | **FLAG_TOO_CLEAN** (now resolvable) | fabrication direction |
| Deep circuit | GHZ / depth-D, claim a fidelity | budget gate ADMISSIBLE/FLAG | `gate_circuit_fidelity_claim` on real HW |
| Anomalous qubit | measure on Q121 (T1=11µs) | **FLAG_TOO_NOISY** | the frozen/anomalous case |

**How the hard-20% impacts CAPAS:** it closes the missing half of the ROC. CAPAS already
PREDICTED, from calibration, which 12 edges are TLS-degraded — so those edges are **labeled
ground truth**. Running real circuits there and confirming CAPAS flags them turns the showcase
from "it admits honest data" into "it discriminates honest from anomalous on real hardware."
That is the result worth having; the Bell alone is not.

**Do we want more tests here?** Yes — but only the discriminating ones. More clean Bells add
nothing. The two highest-value, lowest-cost next runs: (1) a Bell on edge 116-121 or 111-112
(expect FLAG_TOO_NOISY), and (2) a clean Bell at ≥100k shots (makes 'too clean' resolvable, so a
filtered/fabricated variant can be caught). `examples/kingston_stress_test.py` is ready to fire
both when you have queue budget.
