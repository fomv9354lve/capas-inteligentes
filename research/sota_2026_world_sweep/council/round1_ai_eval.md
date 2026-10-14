# Round 1 — AI-evaluation scientist (UK AISI / US tradition)

## 1. Giants I bring

1. **AISI, "LLM judges on trial"** (2025-07) — https://www.aisi.gov.uk/blog/llm-judges-on-trial-a-new-statistical-framework-to-assess-autograders.
   Inherits: a judge is a measurement instrument whose bias is estimated per task (Bayesian GLM) before use.
2. **"Reliability without Validity"** (arXiv 2606.19544) — inherits the distinction: determinism is reliability; validity
   needs an external label.
3. **Bańka & Chudziak, Predictive Value of Pass** (arXiv 2610.05547) — inherits the number: minimum verification budget for
   a target PVP.
4. **Ding et al., verification-gap survey** (arXiv 2608.05179) — inherits the checklist dimensions (seeds, traces,
   in-loop oracle) and the 38 % baseline.
5. **SOCpilot** (arXiv 2605.05501) / **AutoPyVerifier** (arXiv 2604.22937) — inherits the typed violation trace per run.
6. **Epistemological Fault Lines** (arXiv 2512.19466) / **Do LLMs Know What They Don't Know II** (arXiv 2609.07879) —
   inherits the rule: abstention is scored as correct-or-not, never as free.

## 2. Critique of the 5-action plan

**A1 PVP budget — KEEP, change the unit.** `capas_ingest.results` already splits provenance into `read` / `declared` /
`derived`; the budget per sealed batch is the share of fields `read` from a hashed artifact. Enforce it at release, **not**
in the verdict (a new HOLD changes the frozen engine). Test: `verification_budget` = the
three counts per batch; release fails if absent; the scorer prints it beside the blind rate.

**A2 adapters 5–6 — CHANGE: defer.** Two new formats before adapter 4 (today the runner checks hashes, the verdict does not)
is scope growth without validity gain. Test for adapter 4: a payload whose `meta.sources` sha256 mismatches →
HOLD from the engine. DCC/RO-Crate after the next sealed batch.

**A3 re-verifiable certificate — KEEP, sharpen.** The audit-hash body (`capas.py:569–577`) is {schema, claim, verdict,
reason, required_fields, invariant verdict}: no engine commit, no rule trace. A third party confirms the hash, not that the
verdict follows from the evidence. PICID-grade needs `engine_commit` plus an ordered
`rules_fired: [{rule_id, fields_read, comparison, outcome}]`, and a checker that verifies each step and the composition
**without selecting rules** — otherwise it is a second replica (`replica_parity`: 130/233).
Test: CI replays every sealed verdict file; divergence breaks the build.

**A4 CAPAS vs LLM judge — KEEP; three changes.** (i) Brodeur's 37 % vs 94 % measures AI-led *reproduction*, not judge bias:
cite as context, declare a weak prior. (ii) Run the judge k ≥ 5 times with field-order permutations
(test-retest, position bias), on the structured payload and on a prose rendering, pre-registered.
(iii) Labels must be Atlas's sealed outcomes (a separate project), not Ginibre's "project's own later corrections" (ledger
scope). `head_to_head` (SCOPED, n = 10, modeled arms) retires.
Test: prereg hash before coding; both rates with Wilson intervals plus the bias posterior; ledger entry `judge_comparison`.

**A5 cheap rules — CHANGE: split.** Paper-vs-prereg diff: keep — the prereg adapter yields the skeletons; test = regression
tests plus declared in-sample cost on X1–X5. Retraction lookup: move from the
verdict to ingestion — `cited_dois` would be hand-typed, and the project's own audit (888 vs 6,348) shows
recomputable signals do not separate. A feed lookup is provenance, not admissibility.

**Missing 1 — score HOLD.** `ginibre_sealed_scores.json` reports only bad-not-ACCEPT and good-not-REJECT. HOLD counts as
a success on both sides: an engine that always HOLDs scores 100/100. The Atlas pilot (12/12 HOLD) showed it.
Test: the scorer reports the verdict mix and the informative rate (ACCEPT+REJECT share) per batch, with a HOLD-correctness
label (field truly absent vs engine gap, as phase 2a distinguished); ledger and `verify_page_matches_ledger.py` carry it.

**Missing 2 — measure the coder.** CAPAS moved the judge from the verdict to the coding step, not out. The
session that fills fields is the autograder AISI would measure. Test: two independent coders on the same sealed batch;
inter-coder verdict agreement published next to the blind rate.

## 3. Integration order (90 days, tool only)

Weeks 1–2: Missing 1 and A1 counts. Weeks 3–5: A3 trace plus independent checker in CI. Weeks 5–7: adapter 4 and A5 prereg
diff. Weeks 6–10: A4 pre-registered and sealed; X6 coded by two coders (Missing 2). Weeks 11–13: next sealed batch scored
with all of the above; A2 after that.

## 4. Ahead / behind

**Ahead.** My tradition measures judges; it does not pre-register the instrument. Inspect scorers are versioned code, never
frozen at a tag with verdicts sealed before outcomes open; no eval I know publishes its own leakage. The survey's
"no externally validated in-loop oracle" has a counter-example here: Atlas E4, clean 1/1.

**Behind.** Validity. Determinism gives CAPAS test-retest of 1 and nothing more; its labels are self-corrections, its
judge comparison is n = 10 with modeled arms, and abstention is unscored. CAPAS has not yet estimated bias for its own coder or its own HOLD.

## 5. Red lines

1. No blind rate published without the HOLD share and the informative rate beside it.
2. No "CAPAS vs LLM judge" number from a single judge run or a modeled arm.
3. No rule written from X1–X5 failures credited toward a blind rate (already policy; I will not sign a release that breaks it).

## 6. Positioning as a reference

Leaders sit in the AISI science-of-evaluations hub, Inspect / inspect_evals (METR, Apollo, government bodies), the NIST AI
Consortium measurement task group, and the NeurIPS 2026 verification workshop. One step: ship CAPAS as an **Inspect scorer** (`capas_sdk` wrapped as a `@scorer`) over the
sealed Ginibre batch. The NeurIPS submission then cites a runnable scorer.
