# Where CAPAS stands — what IBM's engine gave us, and the line vs SOTA

*Stocktaking, 2026-06-22. Every capability claim here is re-derivable: run
`benchmarks/generate_capability_matrix.py` (it exercises each gate live) and
`examples/kingston_live_audit.py` (it audits the real device). Fact/conjecture lines are marked.*

---

## 1. The deepest thing knowing IBM's engine gave us

IBM's calibration system **is, structurally, a production admissibility engine for physical
claims about qubits** — the same pattern CAPAS is. For each qubit/edge it:

- measures quantities (T1, T2, gate error, readout, residual ZZ),
- checks them against physical invariants and engineering thresholds,
- emits a fail-closed decision (`Operational: Yes/No`),
- and manages a **disclosure boundary** — on the open plan it serves T1/T2/readout/ZZ but does not
  expose qubit frequency.

**(Fact + our interpretation)** A system built independently, at industrial scale, for a domain we
did not design for, exhibits the same structural pattern CAPAS uses — invariant checks + threshold
gates + a fail-closed operational verdict + a served/undisclosed data tier. We read this as
**independent architectural convergence**: evidence the pattern is sound engineering. This pattern
(measure → compare to thresholds → fail-closed verdict → data tiers) is common across quality-control
engineering, so the convergence *supports the design* — it is **not** a validation, review, or
endorsement of CAPAS by IBM.

## 2. The four concrete things it gave us (all integrated, all tested)

| # | What IBM's engine taught | What we built | Status |
|---|---|---|---|
| 1 | A reported number can be re-derived into a quantity they don't publish | **Derived-quantity gates**: `Γφ = 1/T2 − 1/2T1` (reproduced their atlas to 2 decimals: Q0 Tφ=1173.95µs), gate-error coherence floor `t_g/3T1` | ✅ live |
| 2 | An *estimate* and an *exact published value* can diverge wildly | **Exact-only discipline, validated by data**: the CZ/RZZ estimate put edge 131-138 at ~86 kHz; IBM's published ZZ is **3.56 kHz — 24× off**. Gating on the estimate would have false-flagged | ✅ proven |
| 3 | A vendor serves a *tier* and withholds the rest | **GATE / ATTEST / DEFER maps onto served / withheld data**: CAPAS correctly refuses to gate on the withheld (frequency) — loss-tangent & spectral-collision stay diagnostics | ✅ honored |
| 4 | A calibration value can remain unchanged across calibration cycles while the device is still reported `Operational` | **A more conservative disposition**: CAPAS's fail-closed discipline + the derived-quantity gates flag that pattern (Q121: T2>2T1, value unchanged across the calibrations we sampled) — a fail-closed gate treats an unchanging value more cautiously than a binary operational flag does | ✅ caught live |

**(Conjecture, well-supported)** Items 3–4 are our interpretation of publicly-served calibration
metadata, not statements about IBM's internal design or intent. The observations (frequency=None on
the open plan; Q121's value unchanged across the calibrations we sampled; `Operational: Yes` at
T1=11µs) are what the metadata shows; the "DEFER" and conservative-disposition framings are ours.

## 3. The live proof: CAPAS audited the real chip

`kingston_live_audit.py` ran the gates over the live ibm_kingston calibration (156 qubits, 176
edges, metadata only). **(Fact)** CAPAS independently re-found the atlas from the vendor's own
numbers:

- **T2 > 2·T1: exactly one qubit — Q121** (the active-TLS anomaly), found with no prior hint.
- **0 gate errors below the relaxation floor** → the vendor's numbers are self-consistent; the
  too-clean gate does **not** false-positive on honest real data (a real calibration of the gate).
- **12 CZ edges > 20× median** = the TLS cluster (111-112, 116-121, 113-119, dead edge 112-113).
- **Residual ZZ all < 10 kHz** (Heron tunable couplers null it; max 9.3 kHz). Edge 111-112 has a
  catastrophic CZ but **healthy ZZ** → CAPAS separates "the CZ gate is broken (amplitude-resonant
  TLS)" from "the static coupling is bad." Two different failures, only the exact ZZ tells them apart.

## 4. Where we stand vs SOTA

**(Fact — from the two SOTA sweeps this project ran.)**

- **Accountability substrate (truth without ground-truth):** the deep-research sweep named a
  signed-attestation + Sybil-resistant track-record (earned by surviving refutation) + peer-
  prediction/staking + adversarial-deferral stack as the field's #1 buildable piece. We built it
  (`capas_ledger`, `capas_federated`, `capas_trust`, `capas_registry`). Open problems (Sybil,
  collusion, cash-in) remain open for everyone — we did not claim to solve them.
- **Physical-admissibility gating:** the SOTA check found the five quantum relations are textbook
  physics, but **no system gates reported quantum experimental claims for physical admissibility
  without re-running them.** CAPAS's composition is the **quantum analog of GRIM/statcheck** — a
  no-re-run fabrication/anomaly gate. The novelty is the composition only; the physics is not ours.
- **Cross-domain reach:** the same mechanism now gates finance, psychology, and quantum
  fabrication with one downgrade-only fail-closed filter (`capas_invariants`). The GIGO ceiling
  still stands (a fully self-consistent liar passes) — we raise the *cost* of lying to
  "fabricate a globally-consistent world," we do not abolish it.

**The honest one-line position:** CAPAS is a cross-domain **invariant-admissibility engine** whose
architecture shows **independent convergence** with IBM's production calibration system (convergence,
not endorsement), which is novel specifically where it gates *reported physical/mathematical claims
for admissibility without re-running the experiment* (GRIM/statcheck generalized), and which, on at
least one axis (an unchanging-then-reported-operational calibration value), applies a **more
conservative, fail-closed disposition** than a binary operational flag.

## 5. What is still NOT ours / still open

- We cannot get qubit frequency on the open plan (verified live) → loss-tangent & spectral-collision
  stay diagnostics, never gates.
- The GIGO ceiling is intact: internal consistency ≠ truth-against-reality.
- Sybil / collusion / cash-in in the accountability substrate are unsolved (for the whole field).
- The unchanging-calibration and "disclosure = DEFER" readings are our interpretation of public
  metadata, not IBM doctrine.

*The capability matrix backing §2–3 is regenerated, not asserted: `docs/capability_matrix.md`.*

---

*IBM, IBM Quantum, Heron, and ibm_kingston are trademarks of International Business Machines
Corporation. This document is independent and is **not affiliated with, sponsored by, or endorsed by
IBM**. All device observations are re-derived from calibration metadata publicly served on the IBM
Quantum open plan; they reflect no knowledge of IBM's internal design or intent. Use of IBM Quantum
data is subject to IBM's terms of service. Device-specific figures (e.g. Q121, residual-ZZ values,
the estimate-vs-published divergence) are re-derivable by running the cited `kingston_live_audit.py`
against a current live calibration — confirm against a fresh run before external publication, as
calibration values change over time.*
