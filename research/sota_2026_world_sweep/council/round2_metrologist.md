# Round 2 — the metrologist

**Verdict: AGREE WITH CONDITIONS.**

## (a) Red line still crossed

Red lines 2 (hash = integrity, signature = authenticity) and 3 (no GB/T 47468-2026 conformance sentence) are folded
in. Red line 1 is not: PLAN v2 attaches `*_u`, `coverage_factor` and the guard-band HOLD to **A3d, after day 90**.
Until then the calibration law keeps emitting FLAG/PASS on bare point values (edge > 1e-2, T1 < 60 µs) — and the next
sealed batch (A4, ≥ 20/20) will be frozen with that law inside it. By the regulator's own red line 3 ("no rule change
between freeze and open"), a decision rule that arrives after the freeze cannot be credited to that batch. So the plan
produces one more sealed batch whose snapshot verdicts are, in my tradition's words, not conformity statements.

## (b) The single change I still demand

Decouple the **uncertainty field and decision rule from the DCC adapter**. The DCC/D-SI XML adapter can wait for a
producer (A3d, after day 90 — I accept that). The schema and law change is small and producer-independent: optional
`*_u` and `coverage_factor` per parameter in `calibration_snapshot`; |value − threshold| < k·u → HOLD "not decidable";
absent `u` → notice `uncertainty: not declared` (the `field_freshness: not evaluable` precedent), never silence. Land it
in **day 45–60**, before the A4 tag is frozen, with fixtures and a ledger entry. Add the quantum member's
`method_standard` / measurand slot in the same commit; absent → notice, never cross-device comparison.

## (c) Where I was wrong

I scheduled the DCC adapter for weeks 5–8 and called it the natural next ingestion target. The quantum member and
the Mexico member were right: no quantum device, no Mexican laboratory and no pharma-statistics sponsor issues a DCC
today; Boehringer deploys in 2027. I argued for the format before a producer existed. What CAPAS needs now is the
**D-SI quadruple** (value, unit, uncertainty, date) in its own schema, not the XML. The formalist also corrected my
action 2: "invalid signature → HOLD" without a declared trust root is theatre; PLAN v2's wording is the right one.
