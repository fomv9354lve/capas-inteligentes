# PCM / Closest-SotA Audit

Date: 2026-06-17

Purpose: test whether CAPAS is only a mirror of an existing provenance/correctness
system, or whether it is a narrow extension over existing systems.

## Search Result

Targeted searches for a canonical project named `PCM` in the intersection of:

- scientific workflow provenance,
- correctness / verification of scientific results,
- RO-Crate / PROV packaging,
- physical evidence or physical correctness metadata,

did not identify a single dominant `PCM` project occupying the CAPAS position.

The closest state of the art is not one system. It is a set of neighboring
systems that each cover part of the space.

## Closest Neighbors

### Workflow Run RO-Crate

Reference: "Recording provenance of workflow runs with RO-Crate"
(`arXiv:2312.07852`).

Covers:

- workflow run provenance,
- RO-Crate packaging,
- W3C PROV alignment,
- execution metadata across workflow systems.

Does not appear to cover:

- first-class physical evidence levels,
- reference-truth semantics,
- witness-independence levels,
- robust versus marginal scientific correctness.

Verdict: CAPAS should align with this, not compete with it.

### HyProv

Reference: "HyProv: Hybrid Provenance Management for Scientific Workflows"
(`arXiv:2511.07574`).

Covers:

- scalable workflow provenance,
- online/federated provenance querying,
- workflow-aware execution monitoring.

Does not appear to cover:

- domain physical correctness of outputs,
- analytic/cross-sim/formal/estimated/no-evidence taxonomy,
- scientific threshold status such as `true_not_robust` versus `true_robust`.

Verdict: strong provenance infrastructure neighbor, not a physical evidence
profile.

### FAIR Data Pipeline

Reference: "FAIR Data Pipeline: provenance-driven data management for traceable
scientific workflows" (`arXiv:2110.07117`).

Covers:

- traceable data use,
- policy-facing reproducibility,
- provenance through data/code paths.

Does not appear to cover:

- physical correctness against analytic or experimental truth,
- witness independence,
- explicit result-evidence states.

Verdict: close on transparent scientific evidence chains, but output correctness
semantics remain outside its core layer.

### SciAgentGym / SciAgentBench

Reference: "SciAgentGym: Benchmarking Multi-Step Scientific Tool-use in LLM
Agents" (`arXiv:2602.12984`).

Covers:

- structured scientific tool-use traces,
- many scientific tools,
- execution-grounded benchmark trajectories,
- error/recovery behavior for agents.

Does not appear from the paper abstract/available positioning to cover:

- RO-Crate / PROV per trace,
- first-class `physical_evidence_level`,
- `verification_independence`,
- `reference_truth`,
- `true_not_robust` / `true_robust` threshold semantics.

Verdict: strongest neighbor for scientific traces. CAPAS must not claim
"scientific traces" or "golden traces" as new.

### QMB100 / PhysVEC

Reference: "Towards Verifiable and Self-Correcting AI Physicists for Quantum
Many-Body Simulations" (`arXiv:2604.00149`).

Covers:

- quantum-many-body verification,
- programming verifier,
- scientific verifier,
- human-auditable evidence for AI physics tasks,
- 100 research-level QMB tasks.

Does not appear from the paper abstract/available positioning to cover:

- per-run RO-Crate/PROV packaging,
- a reusable physical-evidence profile,
- witness-independence taxonomy,
- evidence states for no-evidence / failed / rejected runs.

Verdict: closest domain neighbor. CAPAS is complementary only if it wraps or
exports evidence artifacts around this kind of task; it is not a competing
benchmark.

### SciMLBenchmarks

Covers:

- reference solutions,
- error metrics,
- solver failures,
- reproducible benchmark documentation.

Does not appear to cover:

- per-run RO-Crate / PROV evidence packages,
- physical evidence entities,
- witness-independence levels as trace fields,
- robust threshold semantics.

Verdict: strong correctness benchmark neighbor. CAPAS must not claim reference
error measurement as new.

## Capability Matrix

| Capability | Workflow Run RO-Crate | HyProv | FAIR Data Pipeline | SciAgentGym | QMB100/PhysVEC | SciMLBenchmarks | CAPAS |
|---|---|---|---|---|---|---|---|
| Workflow/run provenance | yes | yes | yes | yes | yes | partial | yes |
| RO-Crate/PROV packaging | yes | no/unclear | provenance-oriented | no/unclear | no/unclear | no/unclear | yes |
| Scientific/reference error | no | no | no | execution-verified | yes | yes | yes |
| Domain physical evidence level | no | no | no | no/unclear | no/unclear | no | yes |
| Witness independence as field | no | no | no | no/unclear | no/unclear | partial discussion | yes |
| Failed/rejected/no-evidence states | generic status | execution status | workflow/data status | yes | verifier failure | solver failure | yes |
| Robust vs marginal correctness | no | no | no | no | no/unclear | threshold-dependent but not trace-fielded | yes |
| Quantum/chemistry evidence traces | no | no | no | broad science | quantum many-body | numerical methods | seed corpus |

## Updated CAPAS Position

CAPAS is not:

- a new provenance system,
- a workflow execution engine,
- a scientific benchmark suite,
- a replacement for Workflow Run RO-Crate,
- a replacement for QMB100/PhysVEC,
- a replacement for SciMLBenchmarks.

CAPAS is:

> a physical-evidence profile layered over RO-Crate/PROV-style scientific traces,
> with explicit reference truth, witness independence, evidence status, and
> robust/marginal correctness semantics.

## What Would Falsify The CAPAS Gap

Revise or drop the CAPAS positioning if a public system provides all of:

- per-run RO-Crate or PROV export,
- first-class physical evidence entity,
- explicit reference truth,
- explicit witness-independence classification,
- evidence states for success / no-evidence / failure / rejection,
- threshold status distinguishing marginal from robust correctness,
- scientific-domain examples comparable to CAPAS chemistry/quantum traces.

## Next Technical Move

Do not add another chemistry trace.

The next useful implementation step is interop:

1. Take one CAPAS trace bundle.
2. Compare its RO-Crate shape against Workflow Run RO-Crate expectations.
3. Add a small `docs/profile/` or JSON-LD context draft for CAPAS physical
   evidence fields.
4. Prepare a minimal example crate for external review.

The next non-technical move is validation by a real user or standards community.
