# CAPAS Technical Note

## Abstract

CAPAS is a small evidence-typed claim gate for scientific computation traces.
It does not replace simulators, scientific verifiers, RO-Crate/PROV,
metamorphic testing, or VVUQ methodology. Its narrower purpose is to package
the evidence behind a scientific computation result so that downstream users can
see which claim the result is allowed to support.

In a hybrid AI-for-science pipeline, CAPAS is the deterministic middle layer:
an upstream LLM, extractor, or scientific verifier supplies structured
claim/evidence JSON; CAPAS decides whether that structured evidence licenses
`ACCEPT`, `REWRITE`, `REJECT`, or `HOLD`.

The current prototype represents a trace as a standards-aligned provenance
object plus a domain evidence object, `capas:PhysicalEvidence`. That object
records the evidence level, witness independence, declared reference truth,
error or bound scope, failure/rejection status, and the claim decision:
`ACCEPT`, `REWRITE`, `REJECT`, or `HOLD`.

## Motivation

Scientific-agent outputs can pass local programming checks while still
overstating the scientific claim they license. A result can be:

- correct for a model but not accurate against experiment,
- verified by the same runtime but not by an independent witness,
- supported only by an estimated bound,
- failed, rejected, or missing physical evidence,
- useful only after rewriting the claim.

CAPAS makes those distinctions explicit.

## Evidence Object

The current public schema records:

- `physicalEvidenceLevel`: analytic, cross-simulation, experimental,
  formal-bound, estimated-bound, scaling-law anchor, none, or related levels.
- `verificationIndependence`: how independent the witness is from the producer.
- `referenceTruth`: the declared reference being used.
- `absError` and `boundScope`: the measured error or the exact scope over which
  a bound applies.
- `evidenceStatus`: present, none declared, failed, or rejected.
- `claim decision`: ACCEPT, REWRITE, REJECT, or HOLD.

The key product behavior is not "verified or not verified." It is claim
alignment: whether the supplied evidence supports the proposed claim, supports a
weaker claim, contradicts it, or requires hold.

## Closest Neighbors

CAPAS is adjacent to several mature areas:

- RO-Crate/PROV and Workflow Run RO-Crate for provenance packaging.
- VVUQ for verification, validation, and uncertainty discipline.
- Metamorphic testing for property-based scientific software checks.
- QMB100/PhysVEC for verifiable AI physicists in quantum many-body simulation.
- SciAgentGym and related scientific-agent trace datasets.

The current CAPAS claim is deliberately narrower than those fields:

> CAPAS is a profile-style evidence object over existing provenance traces that
> records physical evidence strength, witness independence, failure/rejection
> states, and claim licensing.

## Non-Claims

CAPAS does not claim:

- to invent provenance,
- to invent scientific verification,
- to retrieve evidence from papers or code,
- to semantically verify arbitrary free-text claim prose,
- to replace QMB100/PhysVEC, SciAgentGym, VVUQ, or RO-Crate,
- to benchmark simulators,
- to prove broad LLM scientific reasoning,
- to make failed traces training gold,
- to have external user validation yet.

## Current Validation State

The public MVP has:

- a package-installable CLI,
- static UI generation,
- external JSON claim/evidence input schema,
- trace inspection and claim-decision commands,
- RO-Crate/PROV-shaped evidence exports,
- public release `v0.1.1`.

The remaining live question is external utility:

> Would practitioners working on scientific-agent verification, quantum
> many-body benchmarks, or workflow provenance use a CAPAS-style evidence object,
> or do their existing artifacts already capture these distinctions?

That question is being asked as validation, not assumed as solved.

The next product module is a semantic alignment checker that verifies whether
`claim.text`, `claim.type`, and the supplied evidence fields describe the same
scientific assertion. That module should sit upstream or beside CAPAS; the final
CAPAS verdict should remain deterministic.
