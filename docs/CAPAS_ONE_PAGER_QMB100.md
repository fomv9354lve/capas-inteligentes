# CAPAS One-Pager for QMB100 / PhysVEC

## Problem

AI scientific agents can generate code, run tools, and produce numerical
results, but a label like "verified" can hide several different questions:

- Did the code run?
- Did it pass local programming checks?
- Did the result satisfy a physical reference?
- Was the reference independent of the generator?
- What claim is the result actually allowed to support?

For scientific-computation traces, these distinctions matter. A result may be
correct for a model but not physically accurate, verified by the same runtime
but not by an independent witness, or useful only after rewriting the claim.

## CAPAS Proposal

CAPAS is a small open-source evidence-typed claim gate for scientific
computation.

It packages computation outputs as RO-Crate/PROV-style traces and adds one
domain-specific evidence object:

```text
capas:PhysicalEvidence
```

CAPAS does not replace scientific verifiers, benchmarks, or workflow provenance.
It tries to make the evidence behind a result explicit enough that downstream
users can decide which claim is licensed.

Repository:

```text
https://github.com/fomv9354lve/capas-inteligentes
```

Release:

```text
https://github.com/fomv9354lve/capas-inteligentes/releases/tag/v0.1.0
```

## What CAPAS Records

A CAPAS trace can record:

- `physicalEvidenceLevel`: e.g. `analytic`, `cross_sim`, `experimental`,
  `formal_bound`, `estimated_bound`, `scaling_law_anchor`, `none`
- `verificationIndependence`: relationship between producer and witness
- `referenceTruth`: analytic, experimental, benchmark, or declared reference
- `absError` / `boundScope`: error or scope of a bound
- `evidenceStatus`: `present`, `none_declared`,
  `not_applicable_failed`, `not_applicable_rejected`
- claim verdict: `ACCEPT`, `REWRITE`, `REJECT`, or `HOLD`

Example distinction:

```text
local checks pass, but universal physical anchor fails
=> REWRITE, not ACCEPT
```

This prevents a trace from licensing a stronger claim than its evidence supports.

## Why QMB100 / PhysVEC Is the Closest Use Case

QMB100 / PhysVEC targets verifiable and self-correcting AI physicists for
quantum many-body simulations. That is the closest use case CAPAS has found:

- AI-generated scientific computation,
- programming correctness,
- physical validity,
- human-auditable evidence,
- task-level benchmark outputs.

CAPAS is not a competing verifier. The question is whether evidence produced by
a system like PhysVEC should also be packaged as a portable evidence object that
records how the result was verified and what claim it supports.

## Concrete Validation Question

Would a CAPAS-style trace help audit or exchange one QMB100 / PhysVEC task
result?

In particular, are these fields useful or already covered by current artifacts?

```text
physicalEvidenceLevel
verificationIndependence
referenceTruth
absError
boundScope
evidenceStatus
claim verdict: ACCEPT / REWRITE / REJECT / HOLD
```

## What Would Count as Useful Feedback

A useful answer can be short:

1. "Yes, this would help for [specific QMB100/PhysVEC workflow]."
2. "No, PhysVEC already captures this as [specific artifact/field]."
3. "The missing field would be [specific field]."
4. "This is not useful because [specific reason]."

CAPAS will treat any of these as real validation input. Generic praise does not
count.

## Non-Claims

CAPAS does not claim:

- to replace QMB100 or PhysVEC,
- to invent scientific verification,
- to invent RO-Crate/PROV provenance,
- to prove broad LLM scientific reliability,
- to make failed generated outputs training gold,
- to certify physical truth when evidence is `none`, `estimated`, failed, or
  rejected.

## Current State

CAPAS v0.1.0 is public and CI-validated. It remains local-MVP level:

- package-installable CLI,
- static UI,
- external JSON claim/evidence input schema,
- RO-Crate physical-evidence profile draft,
- release published,
- external RO-Crate profile review requested,
- external practitioner utility validation still pending.
