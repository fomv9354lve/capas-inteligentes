# CAPAS Physical Evidence Profile

Status: draft, local, not registered.

Profile URI:

```text
https://example.org/capas-inteligentes/ro-crate/physical-evidence/0.1
```

This profile is an extension over RO-Crate / Workflow Run RO-Crate-style run
metadata. It does not define a new workflow provenance container. It adds a
domain-specific evidence object for scientific result credibility.

References:

- RO-Crate 1.1: `https://w3id.org/ro/crate/1.1`
- Process Run Crate 0.5: `https://w3id.org/ro/wfrun/process/0.5`
- Workflow Run Crate 0.5: `https://w3id.org/ro/wfrun/workflow/0.5`
- Workflow RO-Crate 1.0: `https://w3id.org/workflowhub/workflow-ro-crate/1.0`
- CAPAS draft profile: `https://example.org/capas-inteligentes/ro-crate/physical-evidence/0.1`

## Required Shape

A CAPAS crate must contain the normal RO-Crate metadata graph plus:

- root `Dataset`
- one `ComputationalWorkflow`
- one top-level `CreateAction` run
- `mainEntity` from the root dataset to the workflow
- `mentions` from the root dataset to the run action
- `instrument` from the run action to the workflow
- workload entity realizing `parameter:workload`
- optional result entity realizing `parameter:result`
- `capas:evidenceStatus` on root dataset and run action

When `capas:evidenceStatus = present`, the crate must contain exactly one
`capas:PhysicalEvidence` entity linked from the result.

## Evidence Status

Allowed values:

| Value | Meaning |
|---|---|
| `present` | A result exists and carries physical evidence metadata. |
| `none_declared` | A result exists, but no physical witness is claimed. |
| `not_applicable_failed` | The backend failed; no result evidence applies. |
| `not_applicable_rejected` | The router rejected/skipped execution; no result evidence applies. |

## Physical Evidence Entity

Minimum required fields when evidence is present:

| Field | Meaning |
|---|---|
| `capas:physicalEvidenceLevel` | Strength/type of evidence, e.g. `analytic`, `cross_sim`, `experimental`, `formal_bound`, `estimated_bound`, `none`. |
| `capas:verificationIndependence` | Relationship between producer and witness, e.g. analytic no-solver, same runtime, different method, different library. |
| `capas:referenceTruth` | The reference used to judge the result, if any. |

Common optional fields:

| Field | Meaning |
|---|---|
| `capas:absError` | Numeric distance to the reference. |
| `capas:boundScope` | Scope where a bound applies. |
| `capas:evidenceStatusDetail` | More specific status label. |
| `capas:witnessStack` | Human-readable or structured description of the producer/witness relationship. |
| `capas:withinChemicalAccuracy` | Chemistry threshold judgment, when applicable. |
| `capas:convergencePoints` | Basis/model convergence curve, when applicable. |
| `capas:localPropertyTests` | Local/generic property checks used as a weaker oracle, when applicable. |
| `capas:localPropertyTestsPass` | Whether local property checks passed. |
| `capas:localOracleCaught` | Whether the local oracle caught the error. |
| `capas:universalAnchor` | Analytic or universal invariant used as independent anchor. |
| `capas:universalAnchorPass` | Whether the generated result satisfies the universal anchor. |
| `capas:invariantCaught` | Whether the universal anchor caught an error missed by the local oracle. |
| `capas:generatorError` | Declared injected or diagnosed generator error, when applicable. |
| `capas:structureMapping` | Relationship-preserving map between generator artifact, local oracle, and universal oracle. |
| `capas:preRegisteredSuccessCriterion` | Criterion declared before interpreting the trace. |
| `capas:claimScope` | Narrow scope of what the trace supports. |

## Robustness Semantics

CAPAS distinguishes threshold success from robust success. A result may be:

- `false`: outside threshold,
- `true_not_robust`: inside threshold but too close to the boundary,
- `true_robust`: inside threshold with declared margin.

This is domain-specific evidence, not generic provenance.

## Universal Invariant Anchoring

CAPAS may record a universal/analytic invariant as an independent oracle for a
generated scientific artifact. The profile distinguishes:

- generic local property checks,
- whether those checks passed,
- the universal anchor,
- whether the anchor passed,
- whether the anchor caught an error missed by the local oracle.

This does not make failed generated output training gold. Adversarial invariant
traces should remain `reject` in the audit unless a separate blind review says
otherwise.

## Non-Claims

This profile does not claim:

- official RO-Crate profile registration,
- official Workflow Run RO-Crate validation,
- a replacement for PROV,
- a replacement for Workflow Run RO-Crate,
- physical correctness when `evidenceStatus` is not `present`,
- independence when the witness runs in the same runtime.
- novelty of universal invariants as physics.
- that one adversarial invariant trace proves general LLM-verification utility.

## Local Validation

Use:

```bash
python3 benchmarks/validate_capas_profile.py
```

This validates the local CAPAS profile shape over the generated corpus. It is
not an external standards-body validation.
