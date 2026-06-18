# VVUQ x Quantum Many-Body Audit

Status: literature-level audit.

This document checks whether CAPAS is reinventing Verification, Validation, and
Uncertainty Quantification (VVUQ), and whether VVUQ already occupies the exact
CAPAS intersection: quantum many-body simulation + sealed provenance trace +
RO-Crate/PROV packaging + physical evidence levels.

## Findings

### 1. VVUQ Is Established And Must Not Be Reclaimed

Verification, validation, and uncertainty quantification are mature fields in
computational modeling and simulation. ASME V&V standards and engineering VVUQ
literature already define the core vocabulary:

- verification: was the model/code implemented correctly?
- validation: does the model adequately represent the target system for an
  intended use?
- uncertainty quantification: what uncertainty remains in inputs, model,
  numerics, observations, and predictions?

CAPAS must not claim novelty for evidence hierarchy, model credibility, or
uncertainty methodology in general.

Relevant background:

- https://en.wikipedia.org/wiki/Verification_and_validation_of_computer_simulation_models
- https://en.wikipedia.org/wiki/Uncertainty_quantification
- https://en.wikipedia.org/wiki/Quantification_of_margins_and_uncertainties

### 2. VVUQ Does Appear In Quantum Many-Body Work

VVUQ is not absent from quantum many-body. A direct example is AFDMC emulator
work for nuclear many-body systems, which explicitly states that validation,
verification, and uncertainty quantification of expensive quantum many-body
models require fast and accurate emulators.

Relevant source:

- Emulators for scarce and noisy data: application to auxiliary field diffusion
  Monte Carlo for the deuteron, https://arxiv.org/abs/2404.11566

This means CAPAS must not claim that VVUQ has never reached quantum many-body.
It has.

### 3. What Was Not Found

In the searches performed, I did not find a system that combines all of:

- quantum many-body / quantum simulation VVUQ,
- per-run sealed trace,
- RO-Crate or PROV export,
- explicit evidence level per result,
- explicit witness-independence metadata,
- honest no-evidence / failed / rejected states,
- result-level physical evidence entity.

VVUQ appears as methodology, emulator validation, uncertainty modeling, and
model credibility practice. CAPAS is instead packaging evidence state into an
auditable trace object.

This is not proof of absence. It is the current evidence from targeted search.

## Positioning Impact

CAPAS should not invent its own evidence vocabulary in isolation. It should map
its fields onto VVUQ language:

| CAPAS field | VVUQ interpretation |
|---|---|
| `physical_evidence_level=analytic` | verification against closed-form solution |
| `physical_evidence_level=cross_sim` | code-to-code verification / benchmark validation |
| `physical_evidence_level=invariant` | verification against conserved law or invariant |
| `physical_evidence_level=none` | no validation evidence attached |
| `verification_independence` | strength of independent witness / benchmark independence |
| `abs_error` | quantitative discrepancy against reference |
| `evidenceStatus=not_applicable_failed` | failed execution; no validation claim |
| `evidenceStatus=not_applicable_rejected` | non-execution due credibility/resource gate |

## Defensible Claim After VVUQ Audit

CAPAS is not a new VVUQ methodology.

CAPAS is a trace/profile layer that encodes VVUQ-style evidence semantics into
RO-Crate/PROV artifacts for scientific/quantum computation runs.

Short version:

> CAPAS is an evidence-typed claim gate over scientific-computation traces.

Long version:

> CAPAS reads or packages RO-Crate/PROV-aligned traces with explicit VVUQ-style
> result evidence: evidence level, reference truth, witness independence,
> discrepancy, and honest no-evidence/failure/rejection states. It then decides
> whether that evidence licenses ACCEPT, REWRITE, REJECT, or HOLD.

## Falsation Condition

Revise the CAPAS claim if a system is found that already exports quantum
many-body or scientific simulation VVUQ as per-run RO-Crate/PROV traces with
first-class evidence entities, witness-independence metadata, and failed/rejected
evidence states.
