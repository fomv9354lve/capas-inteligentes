# CAPAS Product Demo Report

Status: `PASS`

## Product

CAPAS turns scientific computation traces into evidence-typed claim decisions: ACCEPT, REWRITE, REJECT, or HOLD.

## Claim Gate Summary

- checks: `69`
- passed: `69`
- failed: `0`
- verdict counts: `{'ACCEPT': 31, 'HOLD': 2, 'REJECT': 8, 'REWRITE': 28}`
- fine_tune_ready: `False`

## Decision Examples

- `ACCEPT` `trace_039::claim_transition_gate`: upgrade evidence is present, so the attempted stronger claim is licensed within declared scope
- `REWRITE` `debunk10_gpt3_fewshot::gpt3_implies_agi_or_reliable_reasoner`: few-shot NLP benchmark gains do not license AGI or reliable general reasoning
- `REJECT` `debunk10_retracted_superconductor::room_temp_superconductor_established`: claim is not licensed because the record is retracted or lacks independent replication
- `HOLD` `regional_cono_sur_ambiguous_experiment::matches_experiment`: cannot judge experimental match; missing ['reference_definition_match']

## Universal Anchor Matrix

- matrix status: `passed`
- licensed claim: `complementarity_not_dominance`

- `both_catch`: 1
- `both_pass`: 3
- `local_catch_anchor_not_needed`: 2
- `local_miss_anchor_catch`: 5
- `no_anchor_control`: 1

Allowed claim:

> Across the current D11 traces, absolute universal anchors add coverage in some locally plausible failures, while local checks remain sufficient or redundant in other cells. The evidence licenses complementarity, not dominance.

Forbidden claims:

- universal anchors dominate local/property/metamorphic testing
- local tests imply universal physical correctness
- D11 proves benchmark-level LLM-agent utility

## Motor-Backed Positive Control

- trace: `trace_039`
- coverage: `claim_transition_bounded_agent_scientific_reasoning`
- current claim: `few_shot_or_local_benchmark_gain`
- attempted claim: `bounded_reliable_scientific_reasoning_in_declared_task_family`
- physical evidence: `scaling_law_anchor`
- anchor mode: `absolute_anchor`
- local checks pass: `True`
- universal anchor pass: `True`
- upgrade evidence present: `True`
- scope: bounded scientific-computation task family only; this licenses an agent-with-physics-anchor reliability claim for critical Ising finite-size scaling seeds, not AGI or broad reliable reasoning

## Non-Claims

- does not prove AGI or broad reliable LLM reasoning
- does not replace Metamorphic Testing or local/property checks
- does not make fine-tune data ready without blind inference review
- does not certify physical truth when evidence is none/estimated/failed
