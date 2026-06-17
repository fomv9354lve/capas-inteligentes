# SciAgentGym Audit Against CAPAS

Status: paper-level audit. A public GitHub repository was not found through
targeted search for `SciAgentGym`, `SciAgentBench`, and `SciForge` on GitHub.
This document should be updated if a public repo appears.

Primary source:

- SciAgentGym: Benchmarking Multi-Step Scientific Tool-use in LLM Agents,
  arXiv:2602.12984, https://arxiv.org/abs/2602.12984

## What SciAgentGym Clearly Covers

SciAgentGym is a close neighbor to CAPAS and should be treated as serious SotA.
The paper states that it provides:

- 1,780 domain-specific tools across physics, chemistry, biology, and materials.
- typed tool input/output signatures.
- automatic validation through typed outputs and tool execution feedback.
- structured multi-step execution traces.
- fixed random seeds and isolated task instances for reproducibility.
- golden traces retained after complete valid execution.
- error-recovery trajectories that record failed calls and corrected retries.
- training data generated from execution-grounded verified trajectories.

This means CAPAS must not claim novelty for:

- scientific tool-use traces,
- golden scientific traces,
- execution-grounded training trajectories,
- error recovery traces,
- typed tool validation,
- multi-domain scientific tool orchestration.

## What Was Not Found In The Paper

The paper does not appear to define or require the following CAPAS-specific
fields:

- `physical_evidence_level`
- `verification_independence`
- `reference_truth`
- `evidenceStatus`
- `abs_error` specifically against physical reference truth
- analytic / cross_sim / none / failed / rejected evidence taxonomy
- RO-Crate export per trace
- W3C PROV export per trace
- first-class physical-evidence entity attached to a result

The term "verified" in SciAgentGym appears to mean execution-grounded validity:
a sampled/programmed tool sequence runs successfully, produces typed outputs,
and yields a valid trace for task construction or training. That is strong, but
it is not the same claim as CAPAS physical evidence:

> this numerical scientific result is correct against a declared physical
> reference truth, with a declared independence level for the witness.

## Direct Comparison

| Capability | SciAgentGym | CAPAS |
|---|---|---|
| Multi-step scientific traces | yes | yes |
| Golden traces | yes | yes |
| Typed tool validation | yes | currently not the focus |
| Error recovery traces | yes | failed/rejected coverage traces |
| Execution-grounded training data | yes | not claimed |
| RO-Crate packaging | not found in paper | yes |
| PROV export | not found in paper | yes |
| `physical_evidence_level` | not found in paper | yes |
| `verification_independence` | not found in paper | yes |
| `reference_truth` | not found in paper | yes |
| `evidenceStatus` for none/failed/rejected | not found in paper | yes |
| Physical evidence as first-class entity | not found in paper | yes |

## Positioning Impact

SciAgentGym narrows CAPAS substantially. CAPAS is not a general scientific agent
trace benchmark and should not be presented as one.

The remaining defensible position is narrower:

> CAPAS is a RO-Crate/PROV physical-evidence profile for scientific computation
> traces. It adds explicit evidence semantics over existing trace systems:
> physical evidence level, witness independence, reference truth, numerical
> error against the reference, and honest evidence states for success, no
> evidence, backend failure, and router rejection.

## Falsation Condition

The CAPAS positioning must be revised if a public SciAgentGym implementation or
dataset is found to include, per trace:

- a first-class physical evidence entity,
- analytic / cross_sim / none / failed / rejected taxonomy,
- witness-independence metadata,
- explicit reference-truth metadata,
- RO-Crate or PROV export with those fields.

If those exist, CAPAS is not a distinct evidence profile; it becomes an
implementation variant or adapter.
