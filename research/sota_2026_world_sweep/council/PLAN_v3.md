# PLAN v3 — ADOPTED 2026-10-14 (ratified 8/8: metrologist, metascientist, formalist, AI-eval, regulator, rule-RL, quantum, Mexico)

Two wording notes from the AI-eval member, accepted at ratification: in A4, JuStRank and Brodeur enter the sealed
pre-registration as *context*, never as a prior; and `hold_share` is published with a **HOLD-correctness label**
(field truly absent vs engine gap) so a HOLD caused by a missing rule is never counted as a correct abstention.

Round-2 result: 8 × AGREE WITH CONDITIONS, 0 × DISAGREE. Every condition is folded in below; none is deferred.
Changes vs v2 are marked **[v3]** with the member who asked.

## Vocabulary and publication rules (unchanged from v2, plus)
- **[v3, formalist]** The page-vs-ledger check names the **engine tag per published rate**; a rate without its tag fails.
- **[v3, Mexico]** Every batch report (A7) and every `verification_budget` entry (A2) carries `sealed_by` and `run_by`
  (institution). When both are Krenn·IQ the page shows **"self-run"** beside the rate. **"Independent"** is reserved
  for the first batch whose `run_by` is a member institution (e.g. CIMAT/UNAM) that executed `capas_check.py` itself,
  with the checker's hash in the entry. The sealed corpus is therefore opened **under agreement** to that institution
  even while private to the public.
- **[v3, regulator]** A false-accept bound from fewer than 40 bad records is labelled **"pilot-grade"** and never
  migrates to the home page.
- **[v3, metascientist, timing]** `hold_share`, `informative_rate`, the exclusion count and the scoring rule ship
  together at day 0–30; for X1–X3 the exclusion count may read "not reconstructible", declared as such.

## A1 — Re-verifiable verdict certificate (first)
As v2, plus **[v3]**:
- **[rule-RL]** CI runs a **mutated-trace suite**: for each sealed verdict, k mutations (a rule removed from
  `rules_fired`, outcome flipped, `engine_tag` altered, an input hash changed, a rule version bumped); the build fails
  unless `capas_check.py` rejects every one (checker false-accept 0 / k·n). Ledger entry `checker_rejects_mutations`
  must be CLOSED **before** `attest_conformance` is promoted.
- **[formalist]** The certificate names `rule_table_sha256` (the rule table is data); the checker's sha256 is sealed in
  the next pre-registration beside the engine tag **[rule-RL]**.

## A2 — Verification budget per sealed batch
As v2, plus `sealed_by` / `run_by` **[Mexico]**.

## A3 — Provenance and adapters
- 3a adapter 4 inside `decide()`; 3b RO-Crate + save raw BackendProperties at the next Atlas job — as v2.
- **[v3, quantum]** The `backend_properties` adapter records **`calibrator`** provenance (`human | automated | ai_model`,
  tool name) in `calibration_snapshot`; absent → notice, never silence; the value enters the audit hash.
- **[v3, metrologist]** The **uncertainty field and the guard-band rule are decoupled from the DCC adapter** and land
  at day 45–60, before the next batch's tag is frozen: optional `*_u` and `coverage_factor` on every calibration
  parameter, plus a `method_standard` / measurand slot; HOLD "not decidable" when a value sits inside the guard band.
  **[quantum]** The guard band applies **only when `*_u` is declared** (IBM BackendProperties carries no uncertainty;
  otherwise every Atlas snapshot would HOLD); absent `u` → notice "uncertainty: not declared".
- 3c pharma validator-report adapter; 3d DCC/D-SI XML adapter **after day 90**; 3e OSF prereg import after day 90.

## A4 — CAPAS vs LLM-judge on a sealed batch
As v2, plus **[v3]**:
- **[regulator]** The sealed pre-registration carries a **pre-specified pass/fail threshold on CAPAS's own false-accept
  Wilson-95 % upper bound** (the pilot packet's FA ≤ 30 %, FR ≤ 25 %, ≥ 40/40 is the template); two rates with
  intervals is a description, not evidence.
- **[AI-eval, metascientist, formalist]** **`coder_agreement`**: from X6 on, two independent blind coders (the
  network's, not Krenn·IQ's) code the same claims; field-level and verdict-level agreement is published as a ledger
  entry beside the blind rate and the HOLD share; a disagreement on a **required field** is recorded as an exclusion in
  the A7 report (→ HOLD), never resolved silently. Target day 75, **before A4 seals**. Without it the next batch is a
  single-rater study and its rate is not signed.

## A5 — Structural rules
As v2, with **[v3, formalist]** the word "offline" struck: a retraction snapshot that is absent or unreadable → HOLD,
full stop; and `cited_doi_retracted` only ever downgrades.

## A6 — `ai_use_declared {tool, purpose, phase}` required; A7 — BRI-template batch report (as v2, plus `sealed_by`/`run_by`).

## Order for the next 90 days (v3)
- Day 0–30: vocabulary fixes; `hold_share` + `informative_rate` + exclusion count + scoring rule in `score_sealed.py`
  and on the pages; A1 (certificate body, rule table as data, `capas_check.py` written by a session that did not write
  `capas.py`, mutated-trace suite in CI).
- Day 30–45: A2 (`verification_budget` with provenance counts, tier histogram, `sealed_by`/`run_by`).
- Day 45–60: A3a (provenance HOLD in `decide()`), A3b (RO-Crate; `calibrator` field; save raw BackendProperties),
  uncertainty fields + guard band (declared-only), A6.
- Day 60–75: A5 first three items (retraction snapshot field, field-level prereg adherence, statcheck recompute), A7
  retroactive report, `coder_agreement` protocol with the network's two coders.
- Day 75–90: A3c (pharma validator adapter), A4 pre-registration co-signed by the other-family model, thresholds and
  checker hash sealed, judge arms specified; then run on the next sealed batch (≥ 20 bad, ≥ 20 good; "pilot-grade"
  label below 40/40).
- After 90: A3d DCC/D-SI, A3e OSF import, remaining A5 items (VERaiPHY fields, equivalence normalizers, retraction
  propagation in the ledger), CAPAS-Bench with the Atlas corpus.

## Positioning (as v2): Red Mexicana de Reproducibilidad founded by people and institutions, Osvaldo as founding
researcher not vendor, the network runs the next sealed batch; NeurIPS 2026 workshop; GFRN by consensus; credits page.

## Ratification question
Reply with one word, AGREE or DISAGREE. If DISAGREE, one sentence naming the condition of yours that is still missing.
