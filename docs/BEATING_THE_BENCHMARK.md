# Beating the benchmark — how CAPAS wins IBM's game with IBM's own numbers

*2026-06-22. Honest scope. Re-derivable: `capas_quantum_physics.complete_error_budget`,
`mitigation_prescription`, `estimate_kappa`; kingston data in `/tmp/xeb_results.json`.*

## The game, and where it's winnable

We cannot build better qubits. But IBM's *published* numbers — RB/IRB error, CLOPS, median
T1/T2 — are designed to **compare processors**, not to **predict your circuit**. The deep
hardware literature is unambiguous: the RB number is an **optimistic lower bound**; for
structured (repeated) circuits the real error is **3–10× higher** (Proctor et al., *Nat. Phys.*
2022). That gap is the opening.

CAPAS wins three ways, **from what we already have**:

- **By design** — deterministic, composable, auditable. IBM's RB number is *not* re-derivable by
  you; CAPAS's complete budget *is*, from IBM's own calibration fields.
- **By understanding** — we encode the physics the headline averages away (dephasing, ZZ-idle,
  leakage, thermal SPAM, the structured-circuit amplification).
- **By inference** — from published T1/T2/readout/CZ/ZZ we re-derive what IBM withholds: Γφ,
  thermal population, the **complete error budget**, and (by direct measurement) the
  coherent/incoherent split.

## The result: the headline number is optimistic, and we prove it

`complete_error_budget` on the real ibm_fez pair q9–q10 (every input from IBM's panel):

| | value | source |
|---|---|---|
| IBM headline (CZ/RB) | **1.63e-3** | published |
| Re-derivable **complete floor** | **1.86e-2** (**11.4×**) | composed from published fields |
| dominant omitted term | **dephasing** (q9 T2=33.9µs) | from published T1,T2 |
| structured-circuit band | up to **1.86e-1** | Proctor 2022 (literature range, cited) |

Every term except `leakage` (a literature estimate) and the structured band (a cited range) is
**exact re-derivation from IBM's own data**. The headline says 0.16%; the honest, auditable floor
is 1.9% — because the published number hides a dephasing-limited qubit.

## We measured it directly too (and corrected our own error)

The kingston XEB run (edges 82-83 diamond, 6-7 moderate) gave per-layer error from the **slope of
log(XEB) vs depth** — which, crucially, **separates the per-layer gate error from the depth-
independent SPAM/readout prefactor**. Our first estimator took single-depth `eff_err` and folded
SPAM in, inflating κ to ~10 on the diamond edge. Corrected:

| edge | published CZ+SX | measured per-layer (slope) | κ | reading |
|---|---|---|---|---|
| 6-7 (moderate) | 1.02% | 1.08% | **1.05** | the published number is **accurate** here |
| 82-83 (diamond) | 0.14% | 0.35% | **2.53** | IBM **under-states 2.5×** on its best edge |

**The honest punchline:** the gap between IBM's headline and reality is *largest exactly where its
number looks best* — on the diamond edge, the tiny CZ (8e-4) is swamped by a ~0.3% per-layer floor
(SPAM/dephasing/crosstalk) the headline ignores. And the error is **incoherent** (speckle purity),
so this is *not* the κ̂=0.401 coherent-discount hypothesis — that was an artifact of a too-
pessimistic inference baseline; direct measurement shows the published number is optimistic, not
pessimistic.

## Operationalized: error correction, re-derived

`mitigation_prescription` turns the same calibration row into actions IBM's panel does not hand
you — each with its re-derived reason:

- **dynamical decoupling (XY-8/CPMG)** when Tφ < 50µs (q9: Tφ=35.9µs) — with the honest caveat
  that it only helps for low-frequency TLS.
- **rep_delay ≥ 5·T1** (q9: 1498µs) — the default 250µs leaves ~57% relaxation, contaminating
  state prep.
- **active reset** when P(1|prep0) ≫ thermal (residual excitation).
- **explicit readout correction** (the assignment matrix is asymmetric → systematic bias).

## The honest line

CAPAS does not measure the qubit better than IBM — IBM has the device. What CAPAS does is
**refuse to let an optimistic summary statistic stand as the admissible error**, and re-derive the
complete, auditable number from the vendor's own published fields. That is the GRIM/statcheck move,
applied to a hardware benchmark: the headline is real but optimistic; the complete floor is
re-derivable; we say exactly which terms are exact, which are estimated, and which are a cited
literature range. We win by honesty and auditability, not by hardware.
