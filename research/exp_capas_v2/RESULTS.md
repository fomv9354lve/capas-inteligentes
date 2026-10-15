# Results: experiment v2 (run 2026-10-15 15:27-15:50)

Protocol `PROTOCOL.md`, sealed in commit 25dcd5e before any arm ran (`SEAL.json`, 28 files, zero mismatches after
the run; the oracle was out of the repo during the run and is published now). Engine 4f987b0 (PR #19: re-derivation,
scope rule, one-way override). 6 long reports, 180 claims (45 per category), cases and oracle by a separate agent
that read neither the engine nor v1. Scored with the sealed `score.py` (`result_sealed_scorer.json`).
**GPT arms not run:** the Codex account hit its usage limit (until 2026-10-22 10:34); the task stays queued and
will be reported as a later replication under the same seal.

## Pre-registered measures (B = enforced final decision)

| | Haiku alone | Haiku + CAPAS | Sonnet alone | Sonnet + CAPAS |
|---|---:|---:|---:|---:|
| Non-valid claims stated as written (of 135) | 3 (2.2 %) | 2 (1.5 %) | 4 (3.0 %) | 3 (2.2 %) |
| Valid claims blocked (of 45) | 5 | 7 | 4 | 5 |
| Paired: only A wrong / only B wrong (McNemar p) | 1 / 0 (1.0) | | 1 / 0 (1.0) | |
| Tokens | 255,620 | 450,992 (1.8×) | 192,474 | 296,159 (1.5×) |
| Wall time, sum of agents | 361 s | 982 s (2.7×) | 248 s | 877 s (3.5×) |
| **Pre-registered verdict** | **NO ROOM** | | **NO ROOM** | |

Criterion (a) needed the AI alone to err on at least 10 % of non-valid claims. Neither model came close, even in
30-claim reports with traps; CAPAS therefore had no room to show it "prevents AI errors", and it did not.

## Sensitivity (declared after seeing the logs, not pre-registered)
Agents called CAPAS more than once per claim (probes, re-tries with a corrected payload, a call on their own
narrowed text); the sealed scorer enforces against the **last** verdict. Binding each claim to the verdict for its
**original text** instead (`result_sensitivity_original_text.json`): errors unchanged (2 and 3), false blocks rise to
**14** (Haiku) and **19** (Sonnet) of 45 valid claims. With strict binding, CAPAS v2 would fail criterion (c).

## What the logs show
- **Most CAPAS false blocks are friction, not reasoning.** Valid claims held or rejected because the agent built the
  payload wrong (expected output written as prose, fields the contract does not have, a ledger metric sent without
  the rows) or because the claim is a comparison the contract cannot express ("Q3 was below Q2", "above 38 % in every
  month"), plus one old universal-scope rule that read a bounded range ("every month from December to June") as
  universal.
- **A new engine gap:** R5#17 and R5#28 combine two entities' ledgers where one entity has a missing month. The agent
  merged the rows and CAPAS's coverage check passed, because it checks the period over all rows, not per source.
  Both are errors in the CAPAS arm.
- **Verdict shopping:** agents re-called CAPAS until an action they wanted was allowed. The one-way rule only means
  something if the verdict is bound to the exact text that will be published (the audit hash already covers
  `input_claim`; the integration has to check it).

## Reading
Across v1 and v2, three model families' worth of arms (Haiku, Sonnet, GPT in v1): careful AIs rarely state wrong
mechanically checkable claims (0-3 % of bad claims), so a gate cannot cut much; CAPAS v2 closes the exaggeration gap
it had in v1, but its cost is effort (1.5-3.5×) and, if bound strictly, false blocks. The case for CAPAS on this
evidence is the auditable record and the forced re-derivation, not error prevention by careful models.

## Limits
Two Claude models, one run, mechanically checkable claims only. Instruction ambiguity: the arm prompts did not say
that executing a provided snippet counts as evidence (the protocol does); some arm-A agents withheld snippet-only
claims, which raises A's false blocks. The engine's builder wrote the protocol, the tools and ran the arms.
