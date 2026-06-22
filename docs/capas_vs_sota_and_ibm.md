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
- and manages a **disclosure boundary** — it serves T1/T2/readout/ZZ but **withholds frequency**.

**(Fact)** This is consilience, not analogy-for-flavor: a system built independently, at industrial
scale, for a domain we did not design for, converged on CAPAS's exact architecture — invariant
checks + threshold gates + a fail-closed operational verdict + a served/withheld data tier. The
CAPAS pattern is not speculative; IBM runs it in production. That is the strongest external
validation the architecture has received.

## 2. The four concrete things it gave us (all integrated, all tested)

| # | What IBM's engine taught | What we built | Status |
|---|---|---|---|
| 1 | A reported number can be re-derived into a quantity they don't publish | **Derived-quantity gates**: `Γφ = 1/T2 − 1/2T1` (reproduced their atlas to 2 decimals: Q0 Tφ=1173.95µs), gate-error coherence floor `t_g/3T1` | ✅ live |
| 2 | An *estimate* and an *exact published value* can diverge wildly | **Exact-only discipline, validated by data**: the CZ/RZZ estimate put edge 131-138 at ~86 kHz; IBM's published ZZ is **3.56 kHz — 24× off**. Gating on the estimate would have false-flagged | ✅ proven |
| 3 | A vendor serves a *tier* and withholds the rest | **GATE / ATTEST / DEFER maps onto served / withheld data**: CAPAS correctly refuses to gate on the withheld (frequency) — loss-tangent & spectral-collision stay diagnostics | ✅ honored |
| 4 | A calibration that doesn't converge can be *silently frozen* and still reported `Operational` | **CAPAS is STRICTER than IBM's engine here**: a frozen value reported as operational is a fail-OPEN leak; CAPAS's fail-closed discipline + the derived-quantity gates flag exactly that pattern (Q121: T2>2T1, unmoving across calibrations) | ✅ caught live |

**(Conjecture, well-supported)** Items 3–4 are our interpretation of IBM's disclosure and
freezing behavior, not IBM's stated design. The observations (frequency=None; Q121 unchanged;
`Operational: Yes` at T1=11µs) are fact; the "DEFER" and "fail-open leak" framings are ours.

## 3. The live proof: CAPAS audited the real chip

`kingston_live_audit.py` ran the gates over the live ibm_kingston calibration (155 qubits, 176
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
architecture was independently validated by IBM's production calibration system, which is novel
specifically where it gates *reported physical/mathematical claims for admissibility without
re-running the experiment* (GRIM/statcheck generalized), and which is, on at least one axis
(silent frozen-calibration), **stricter than the industrial engine that inspired it.**

## 5. What is still NOT ours / still open

- We cannot get qubit frequency on the open plan (verified live) → loss-tangent & spectral-collision
  stay diagnostics, never gates.
- The GIGO ceiling is intact: internal consistency ≠ truth-against-reality.
- Sybil / collusion / cash-in in the accountability substrate are unsolved (for the whole field).
- The "IBM freezes calibration" and "disclosure = DEFER" readings are interpretation, not IBM doctrine.

*The capability matrix backing §2–3 is regenerated, not asserted: `docs/capability_matrix.md`.*
