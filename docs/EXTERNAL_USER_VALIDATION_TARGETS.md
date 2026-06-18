# CAPAS External User Validation Targets

Status: target list for external utility validation.

This document is for closing the MVP requirement:

```text
usuario externo validando utilidad
```

It is not evidence that utility has been validated. Utility is validated only
when at least one external practitioner reviews CAPAS and returns feedback that
either confirms usefulness for their workflow or changes the schema/product.

## Best-Fit Users

### 1. Workflow Run RO-Crate / RO-Crate provenance maintainers

Why CAPAS may help:

CAPAS is not trying to replace Workflow Run RO-Crate. It adds a domain-specific
physical-evidence layer on top of workflow run provenance.

Ask:

- Is `capas:PhysicalEvidence` a reasonable profile/sub-profile extension?
- Are `evidenceStatus`, `physicalEvidenceLevel`, and
  `verificationIndependence` modeled in a way compatible with the ecosystem?
- Which validator or competency questions should CAPAS satisfy before profile
  registration?

Validation value:

This validates standards fit, not scientific user utility.

Current contact artifact:

```text
https://github.com/ResearchObject/workflow-run-crate/issues/103
```

### 2. QMB100 / PhysVEC authors and users

Why CAPAS may help:

QMB100 / PhysVEC targets verifiable, self-correcting AI physicists for quantum
many-body simulations. CAPAS is directly relevant if their benchmark outputs
need evidence objects that distinguish coding correctness, physical validity,
reference truth, witness independence, and failed/no-evidence states.

Ask:

- Would a CAPAS RO-Crate trace help audit one QMB100 task result?
- Does QMB100 already record `physicalEvidenceLevel`,
  `verificationIndependence`, `referenceTruth`, `absError`, and
  `evidenceStatus` as first-class fields?
- If not, which one field would be useful enough to adopt?

Validation value:

This is the strongest scientific-computation user validation target because it
matches the domain: AI-generated quantum many-body computation.

### 3. SciAgentGym / SciAgentBench authors and users

Why CAPAS may help:

SciAgentGym studies multi-step scientific tool use and verified trajectories.
CAPAS may add value only if their traces need stronger evidence typing than
execution success or typed tool output validation.

Ask:

- Do verified golden traces distinguish solver correctness from physical
  correctness?
- Would explicit `verificationIndependence` and `evidenceStatus` improve failure
  analysis or training-data filtering?
- Can a CAPAS decision (`ACCEPT`, `REWRITE`, `REJECT`, `HOLD`) usefully label one
  failed or partially correct trajectory?

Validation value:

This validates the AI-agent data use case. It is weaker than QMB100 for physics
specificity, but stronger for agent-workflow adoption.

### 4. SciMLBenchmarks / scientific benchmarking maintainers

Why CAPAS may help:

Scientific benchmark suites already compare results against references. CAPAS
may help if they need portable evidence objects that distinguish reference
truth, solver/runtime independence, and claim scope.

Ask:

- Is `verificationIndependence` useful when comparing solvers that may share
  libraries, BLAS, tolerances, or generated reference solutions?
- Would a RO-Crate evidence profile help export benchmark results for audit?

Validation value:

This validates whether CAPAS adds anything to mature benchmark practice rather
than reinventing reference-error reporting.

### 5. Variational quantum many-body benchmark maintainers/users

Why CAPAS may help:

Variational many-body benchmarks care about regimes where exact truth is not
available. CAPAS may help by making the evidence level explicit:
`formal_bound`, `estimated_bound`, `cross_sim`, or `none`.

Ask:

- Would explicit evidence typing help communicate which benchmark results are
  exact, bounded, estimated, or unverifiable?
- Is `boundScope` useful for avoiding overclaims from local/state-level
  certificates to global/observable claims?

Validation value:

This validates the hard case: useful evidence metadata when exact verification
is impossible.

## Who CAPAS Does Not Serve First

- Generic Kaggle-style dataset users.
- General provenance users who only need workflow lineage.
- General LLM benchmark builders with no physical reference truth.
- Optimization users who only want a faster solver.
- Quantum simulation users who only want backend routing or speed.

CAPAS serves users who need to decide what scientific claim a computation is
allowed to support.

## Minimal Validation Request

Send only a small packet:

1. `PRODUCT.md`
2. `outputs/capas_product_demo_report.md`
3. `docs/schema/capas_claim_payload.schema.json`
4. `docs/profile/CAPAS_PHYSICAL_EVIDENCE_PROFILE.md`
5. one command:

```bash
python -m pip install -e .
capas decide --input examples/external_claim_rewrite.json
capas inspect trace_039
capas validate
```

Ask exactly two questions:

1. Would this evidence/claim split help you audit outputs in your workflow?
2. Which required evidence field or decision category is missing?

## Acceptance Rule

External user validation is complete only if one of these happens:

- an external practitioner says the evidence/claim split is useful for a real
  workflow and names the workflow,
- an external practitioner requests a schema/profile change that CAPAS then
  implements,
- an external practitioner rejects the utility clearly enough that CAPAS updates
  scope or non-claims.

Silence, stars, likes, generic praise, or self-review do not count.
