# Gold Trace Audit Criteria

Purpose: separate provenance from correctness before using any trace for fine-tuning.

The hash gate only answers: "Did this output come from the registered engine bytes?"
It does not answer whether the engine is physically correct or whether the surrounding explanation is valid.

## Columns

- `hash_gate_pass`: `yes/no`. Did the trace pass the registered-engine/hash gate?
- `output_correct`: `yes/no/unknown`. Is the numeric output correct under an independent check?
- `inference_blind_judge`: `yes/no`. Was `inference_correct` judged without seeing `hash_gate_pass`, `engine_hash`, `decision`, or any prior "gold" label?
- `inference_correct`: `yes/no/unknown`. Is the natural-language conclusion drawn from the output valid?
- `physical_evidence_level`: `analytic/cross_sim/formal_bound/experimental/invariant/self_derivation/none/unknown`. What kind of evidence supports the engine/model physics for this case?
- `physical_evidence_detail`: short citation, check name, equation, independent implementation, or reviewer note.
- `verification_independence`: one of the levels in `docs/WITNESS_INDEPENDENCE_AXIS.md`. How independent is the witness or certificate from the producing computation?
- `risk_level`: `low/medium/high`. How damaging would this trace be if learned incorrectly?
- `decision`: `accept/rewrite/reject/hold`.

## Independent Evidence Rules

Use evidence outside the hash gate.

Acceptable evidence for `output_correct`:
- independent implementation,
- known analytic solution,
- published benchmark case,
- conservation/invariant check,
- dimensional/unit check plus bounded numerical tolerance.

Acceptable evidence for `inference_correct`:
- explicit logical chain from output to claim,
- threshold rule defined before seeing the result,
- comparison against baseline/control,
- human technical review with a short rationale.

Blind inference rule:
- The inference judge must not see `hash_gate_pass`, `engine_hash`, prior "gold" labels, or the proposed `decision` before judging.
- Prefer a second reviewer. If only one person is available, do a separate pass where the trace is stripped of provenance/gold labels.
- Record `inference_blind_judge=yes` only if the judgment was made under this blinded condition.

Physical evidence levels:
- `analytic`: checked against an analytic solution or exact known limiting case.
- `cross_sim`: checked against an independent implementation/simulator.
- `formal_bound`: checked by a mathematical error bound with explicit scope. This can be strong correctness evidence without being an independent witness.
- `experimental`: compared against a measured physical reference. This must separate solver error from model error when a simplified model/basis is used.
- `invariant`: checked by conservation laws, dimensional analysis, symmetry, monotonicity, or other invariant tests. Useful but weaker than `analytic` or `cross_sim`.
- `self_derivation`: derived/reviewed by the same project author without independent external check.
- `none`: no physical validation beyond the engine producing a number.
- `unknown`: not audited yet.

Acceptable physical evidence for `accept`:
- `analytic`,
- `cross_sim`,
- `formal_bound` when the claim is inside `bound_scope`,
- `experimental` when the claim is about the measured discrepancy itself, not about being physically accurate,
- or `invariant` only if the trace is low/medium risk and the invariant directly constrains the claimed result.

Witness independence rules:
- `analytic_no_solver` is strongest because no computational witness is involved.
- `different_library_same_runtime` is stronger than `different_algorithm_same_runtime`, but both remain same-runtime evidence.
- `algorithmic_certificate_exact_svd_same_runtime` is a formal certificate, not an independent witness.
- `algorithmic_error_certificate_same_runtime` is an estimate/candidate unless separately promoted by source audit.
- `none` is never acceptable for training gold, though it is required for honest coverage.

Not enough for `accept`:
- `self_derivation`,
- `none`,
- `unknown`.

Not acceptable as correctness evidence:
- hash match,
- "the engine produced it",
- LLM confidence,
- formatting quality,
- fluent explanation,
- circular definition of "gold" as "passed the gate".

## Decision Policy

- `accept`: hash passes, output correct, inference correct under blind judgment, and physical evidence is acceptable.
- `rewrite`: output correct but inference/explanation is flawed; keep the number, rewrite reasoning.
- `reject`: output wrong, inference wrong in a harmful way, or physical model contradicted by independent evidence.
- `hold`: not enough independent evidence yet.

## Fine-Tune Gate

Do not fine-tune on the 17 traces unless:

- `accept_rate >= 0.8`,
- `reject_count == 0` for high-risk traces,
- every accepted trace has non-empty `output_correct_evidence`,
- every accepted trace has non-empty `inference_correct_evidence`,
- every accepted trace has `inference_blind_judge == yes`,
- every accepted trace has `physical_evidence_level` in `analytic/cross_sim/formal_bound`, or `invariant` for low/medium-risk traces only,
- no accepted trace has `physical_evidence_level` in `self_derivation/none/unknown`,
- no accepted trace relies on hash/provenance as correctness evidence.

## Summary Metrics

After filling the CSV, compute:

- provenance pass rate: `hash_gate_pass == yes`,
- output correctness rate,
- inference correctness rate,
- blind inference judgment rate,
- physical evidence level distribution,
- accepted trace count,
- rewrite count,
- reject count,
- hold count.

Interpretation:

- High provenance + low inference correctness means the gate is working but the training data is unsafe.
- High output correctness + weak physical evidence means the engine may be numerically consistent but modeling the wrong system.
- High hash pass alone is not a fine-tune signal.
