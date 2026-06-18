# CAPAS External User Validation SotA Check

Status: focused SotA validation for the five external validation targets.

This document answers two questions:

1. Is the target real and active?
2. Is CAPAS plausibly useful to that target, or is the space already covered?

It does not prove that CAPAS is useful. That requires an external practitioner
response recorded under `outputs/external_validation/`.

## Summary

| Target | SotA status | CAPAS utility hypothesis | Strength |
|---|---|---|---|
| Workflow Run RO-Crate / RO-Crate | Mature and active; CAPAS must extend, not compete | Useful as a domain profile for physical evidence if community accepts modeling | High for standards fit |
| QMB100 / PhysVEC | Very close and current; explicit AI-physics verification problem | Useful if CAPAS packages their human-auditable evidence as portable evidence objects | Highest for scientific utility |
| SciAgentGym / SciAgentBench | Active agent tool-use benchmark with verified trajectories | Useful if evidence typing improves failure analysis/training filtering beyond execution traces | Medium-high |
| SciMLBenchmarks | Mature benchmark culture with error/tolerance/hardware discipline | Useful only if `verificationIndependence`/claim gate adds value beyond existing benchmark reports | Medium-low |
| Variational quantum many-body benchmarks | Active need for unverifiable/partially verifiable regimes | Useful if `formal_bound`/`estimated_bound`/`none` clarifies evidence strength | Medium-high |

## 1. Workflow Run RO-Crate / RO-Crate

Source:

- Workflow Run RO-Crate: `https://arxiv.org/abs/2312.07852`
- Community/review channel used by CAPAS:
  `https://github.com/ResearchObject/workflow-run-crate/issues/103`

What the SotA already covers:

- Workflow run provenance.
- RO-Crate packaging.
- Workflow plan/execution relationships.
- Cross-workflow-system interoperability.

What CAPAS must not claim:

- New workflow provenance.
- New RO-Crate container.
- Replacement for Workflow Run RO-Crate.

CAPAS utility hypothesis:

CAPAS may be useful as a sub-profile/application profile that adds first-class
scientific evidence metadata:

- `capas:PhysicalEvidence`
- `capas:evidenceStatus`
- `capas:physicalEvidenceLevel`
- `capas:verificationIndependence`
- `capas:referenceTruth`

What would validate utility:

- WRROC/RO-Crate maintainers say the profile model is meaningful and identify
  validator/competency checks.

What would weaken utility:

- They say all CAPAS terms should be represented with existing profile terms and
  no new evidence profile is needed.

Current status:

External review requested, not registered.

## 2. QMB100 / PhysVEC

Source:

- QMB100 / PhysVEC: `https://arxiv.org/abs/2604.00149`

What the SotA already covers:

- Verifiable and self-correcting AI physicists.
- Quantum many-body task benchmark.
- Programming verifier plus scientific verifier.
- Human-auditable evidence at each stage.

What CAPAS must not claim:

- Inventing AI-physics verification.
- Inventing scientific verifiers.
- Replacing QMB100/PhysVEC.

CAPAS utility hypothesis:

CAPAS is useful if QMB100/PhysVEC evidence needs portable, standards-aligned
trace packaging with explicit evidence typing:

- coding correctness vs physical validity,
- reference truth,
- witness independence,
- local oracle vs universal anchor,
- failed/no-evidence/rejected states.

Why this is the strongest target:

The domain and pain are aligned: AI-generated quantum many-body computation that
must be physically verified and auditable.

What would validate utility:

- A QMB100/PhysVEC author or user says a CAPAS trace would help audit a task
  result or asks for a field/schema change.

What would weaken utility:

- Their internal trace format already records CAPAS-equivalent fields as
  first-class, portable, standards-aligned metadata.

## 3. SciAgentGym / SciAgentBench

Source:

- SciAgentGym: `https://arxiv.org/abs/2602.12984`

What the SotA already covers:

- Scientific tool-use agent environment.
- 1,780 tools across natural science disciplines.
- Multi-step workflow stress tests.
- Verified/golden trajectory style evaluation and data synthesis.

What CAPAS must not claim:

- Inventing scientific agent traces.
- Inventing golden traces.
- Solving multi-step scientific tool use.

CAPAS utility hypothesis:

CAPAS may help if SciAgentGym traces need an evidence gate that distinguishes:

- tool execution success,
- typed output validity,
- solver correctness,
- physical correctness,
- witness independence,
- claim overreach.

What would validate utility:

- A SciAgentGym/SciAgentBench practitioner says CAPAS labels improve failure
  analysis or training-data filtering.

What would weaken utility:

- Their verified traces already include physical-evidence levels,
  verification-independence fields, and reject/rewrite/hold decision semantics.

## 4. SciMLBenchmarks

Source:

- SciMLBenchmarks.jl repository:
  `https://github.com/SciML/SciMLBenchmarks.jl`

What the SotA already covers:

- Scientific machine-learning and equation-solver benchmarks.
- Work-precision comparisons.
- Timing at matched error or error-tolerance diagrams.
- Hardware/package-version documentation.
- Explicit handling of omitted/failing methods.

What CAPAS must not claim:

- Inventing benchmark reproducibility.
- Inventing reference-error reporting.
- Replacing benchmark reports.

CAPAS utility hypothesis:

CAPAS is useful only if `verificationIndependence` and evidence-typed claim
decisions add something their benchmark reports do not already express.

Possible useful wedge:

- Distinguishing "benchmark result supports this solver-performance claim" from
  "benchmark result validates this scientific model/physical result".
- Recording whether reference truth is analytic, cross-solver, same-runtime, or
  generated by a shared stack.

What would validate utility:

- A SciML benchmark maintainer says the evidence/claim split would help avoid a
  recurring overclaim or ambiguity in benchmark interpretation.

What would weaken utility:

- They say existing work-precision reports and failure documentation already
  cover the practical need.

SotA verdict:

This is not the first outreach target. It is a hostile validation target.

## 5. Variational Quantum Many-Body Benchmarks

Source:

- Variational Benchmarks for Quantum Many-Body Problems:
  `https://arxiv.org/abs/2302.04919`

What the SotA already covers:

- Curated variational many-body benchmark dataset.
- V-score metric from variational energy and variance.
- Cases where classical verifiability is limited or impossible.

What CAPAS must not claim:

- Inventing variational accuracy metrics.
- Replacing V-score.
- Certifying exact truth where the benchmark says truth is unavailable.

CAPAS utility hypothesis:

CAPAS may help by packaging evidence strength and scope:

- `analytic` when exact truth exists,
- `formal_bound` when a mathematical state/bound certificate exists,
- `estimated_bound` when evidence is useful but not formal,
- `cross_sim` when an independent solver witnesses,
- `none` when no physical witness is available.

Most useful CAPAS field here:

```text
boundScope
```

Reason:

It prevents local/state-level evidence from licensing global/observable claims.

What would validate utility:

- A many-body benchmark user says explicit evidence type + bound scope improves
  communication of partial verifiability.

What would weaken utility:

- Existing V-score reporting already gives all necessary evidence strength and
  scope for their users.

## Priority Ranking

1. QMB100 / PhysVEC: strongest scientific utility target.
2. Workflow Run RO-Crate / RO-Crate: strongest standards-fit target.
3. Variational QMB benchmarks: strongest partial-verifiability target.
4. SciAgentGym / SciAgentBench: strong agent-data target, but may already have
   trace/golden machinery.
5. SciMLBenchmarks: useful hostile review target, not first validation target.

## Minimal Next Outreach

Send the repo/release plus one focused question to QMB100/PhysVEC:

```text
Would a RO-Crate trace with explicit physicalEvidenceLevel,
verificationIndependence, referenceTruth, absError, and evidenceStatus help you
audit or exchange one QMB100/PhysVEC task result?
```

If the answer is yes or requests a schema change, CAPAS has external utility
validation. If the answer is no because PhysVEC already records equivalent
fields, CAPAS must narrow scope or align to their format.
