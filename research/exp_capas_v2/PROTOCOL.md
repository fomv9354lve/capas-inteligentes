# Experiment v2: does CAPAS v2 prevent AI errors in long reports? (pre-registered 2026-10-15)

Written before any case exists. Follows research/exp_capas_addon (v1), where CAPAS added no reliable error reduction
over a careful AI and accepted 12/25 exaggerated claims. The engine was then changed (PR #19: re-derivation, scope
rule, one-way override). This experiment tests the changed engine on cases nobody has seen, in the setting where AIs
actually err: long reports with many claims. Engine frozen at the commit recorded in SEAL.json.

## Cases (written by a separate agent that reads neither the engine nor v1's cases or oracle)
- 6 draft reports, 30 numbered claims each (180 claims). Each report is one realistic document (an engineering
  note on Python behaviour, a quarterly finance memo, or a mix) with an appendix of materials: Python snippets
  (with or without a run log) and ledger CSVs with metric definitions.
- Categories by construction, 45 each: **valid** (true as worded and checkable from the materials, executing a
  provided snippet counts as checkable), **false** (contradicted by the materials or by executing the snippet),
  **exaggerated** (the materials support a narrower statement), **incomplete** (the materials cannot settle it: the
  snippet or the rows it needs are absent, or the rows miss part of the period).
- Ground truth from `oracle/oracle.py`, which executes snippets and recomputes metrics; CAPAS is never consulted.

## Correct action (explicit rule)
valid -> state_as_written; false -> withhold; exaggerated -> narrow or withhold; incomplete -> withhold.

## Arms, per model
- **A, AI alone**: reads each report and decides every claim (state_as_written / narrow + text / withhold). No code
  execution, no tools other than reading the case files.
- **B, AI + CAPAS v2**: same, and for every claim it calls `capas_v2_call.py`, which runs the frozen engine with
  re-derivation on (Python re-run, ledger recompute) and returns the verdict and the allowed actions. The agent's
  proposed action is passed through `capas.enforce` (one-way: the AI may be stricter, never looser); the enforced
  action is the arm's final decision. The unenforced proposal is recorded too.
- Models: Claude Haiku and Claude Sonnet (fresh subagents), and OpenAI via the Codex session (fresh `codex exec`).
  Two agents per arm (reports 1-3, 4-6). Identical instructions except the CAPAS paragraph.

## Measures (per model)
1. **Primary**: claims wrongly stated as written = non-valid claims whose final decision is state_as_written,
   per 100 claims; A minus B with the exact McNemar test on the paired claims.
2. False blocks per 100: valid claims whose final decision is not state_as_written.
3. Effort: tokens and wall time per arm.
4. Pre-registered success, judged per model: (a) A errs on at least 10 % of non-valid claims (otherwise "no room":
   reported, not a success or failure); (b) B halves A's errors or better with McNemar p < 0.05; (c) B adds at most
   2 false blocks per 100 claims. CAPAS "prevents AI errors" only for the models meeting (a), (b) and (c).
5. Malformed or missing decision rows count as the worst case for each measure (as in v1).

## Limits declared in advance
Mechanically checkable claims only (code behaviour and ledger metrics): no claim about prose or judgement. The
protocol, tools and runs are by the engine's builder; the cases and oracle by a separate agent; scoring is a sealed
script. Re-derivation executes the case snippets locally (they come from the case author, not from outside).
