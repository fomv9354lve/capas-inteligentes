# Experiment: does CAPAS add value on top of an AI that already has the tests? (AI vs AI + CAPAS)

Written 2026-10-15 before any case exists. Engine frozen at commit 91c20a6 (main). Design proposed by Osvaldo's reviewer;
this file fixes it so it cannot be tuned after the results are seen. Its sha256 goes into SEAL.json with the cases.

## Question
For claims whose truth can be established by execution or arithmetic, does adding CAPAS to an AI that already holds
the same evidence reduce the incorrect claims that reach its final answer, and at what cost in false blocks and effort?

## Cases (held out, written by an agent that does not read the engine)
- 100 cases, two CAPAS-supported families: `programming_language_behavior_claim` (Python snippets) and
  `financial_metric_claim` (a metric over raw ledger rows). About half each.
- Four categories, 25 each, assigned by construction:
  - **valid**: the claim is true and the bundle contains everything needed to see that it is true;
  - **false**: the claim contradicts the bundle (the run log or the ledger arithmetic);
  - **exaggerated**: the bundle supports a narrower statement than the claim (one runtime vs "every version",
    one period vs "every quarter", "always" from one run);
  - **incomplete**: the bundle lacks something the claim needs (no execution log, a log from another snippet or
    version, ledger rows missing for part of the period).
- Run logs are produced by actually executing the snippets (python3); ledger figures are computed by the oracle.
- The case author writes `oracle/labels.json` (category, correct action, why) and `oracle/oracle.py`, which re-derives
  every label from the bundles by execution or arithmetic and fails if a label disagrees. CAPAS is never consulted.

## Correct action per category (explicit rule, not CAPAS)
valid -> `state_as_written`; false -> `withhold`; exaggerated -> `narrow` or `withhold`; incomplete -> `withhold`.

## Arms (same model, same bundles, same order, same instructions except the CAPAS paragraph)
- **A, AI alone**: reads each bundle and outputs one decision per case: `state_as_written`, `narrow` (with the
  narrowed text) or `withhold`, plus the evidence it relied on. No code execution; the tests are the logs in the bundle.
- **B, AI + CAPAS**: identical, plus: for each case it must build a CAPAS payload from the bundle and call the engine
  (`research/exp_capas_addon/capas_call.py`); it decides after seeing the verdict and may disagree with it, saying why.
- Fresh subagents, model `sonnet`, two agents per arm (cases 1-50, 51-100). They read only `cases/`; the oracle
  directory is off limits (instructed; disclosed as a residual risk).

## Measures
1. **Primary**: incorrect claims in the final answer per 100 cases = non-valid cases decided `state_as_written`.
   Effect = A minus B, with the exact McNemar test on the paired cases.
2. False blocks per 100 = valid cases not decided `state_as_written`.
3. Effort: tokens and wall time per arm (from the agent run), CAPAS calls, CAPAS alerts the agent had to resolve.
4. Reproducibility: share of decisions whose cited evidence resolves (a bundle file and line that exists; in B also an
   `audit_hash` that `verify_audit_hash` reproduces).
5. Secondary, descriptive only: `narrow` texts on exaggerated cases (spot-checked, not scored).
Headline: "CAPAS avoids X additional errors per 100 cases at the cost of Y false blocks and Z extra tokens".

## Limits declared in advance
- One model, 100 cases, two families where truth is mechanical: the result does not transfer to prose claims.
- The engine's author designed the protocol and ran the arms; the cases and oracle come from a separate agent that
  did not read the engine. Scoring is a deterministic script. This is not an independent replication.
- If arm A already makes ~0 errors, the honest result is "no measurable benefit at this difficulty".

## Deviations (declared after sealing)
- 2026-10-15 13:05, before the Codex replication's arm B ran: `capas_call.py` routes agents whose name starts with
  `C` (Codex CB1/CB2) to `codex/arm_B/calls.jsonl`. Raised by Codex (its lane is `codex/`). Claude's run and its
  log are untouched; the engine call and output are unchanged. The sealed sha256 of these two files no longer match.
