# Request for Feedback: CAPAS Evidence-Typed Scientific Traces

CAPAS is a small open-source evidence-typed claim gate for scientific
computation traces.

Repository:

```text
https://github.com/fomv9354lve/capas-inteligentes
```

Release:

```text
https://github.com/fomv9354lve/capas-inteligentes/releases/tag/v0.1.1
```

## What CAPAS Tries To Do

CAPAS packages scientific-computation outputs as RO-Crate/PROV-style traces and
adds an explicit evidence object for claim licensing.

The object records:

- `physicalEvidenceLevel`
- `verificationIndependence`
- `referenceTruth`
- `absError` / `boundScope`
- `evidenceStatus`: present, none, failed, rejected
- claim decision: `ACCEPT`, `REWRITE`, `REJECT`, `HOLD`

CAPAS is not a new workflow engine, simulator benchmark, provenance standard, or
scientific verifier. It is a small layer for saying what claim a result is
allowed to support.

## Feedback Requested

I am trying to validate whether this evidence/claim split is useful to people
working on scientific-agent verification, quantum many-body benchmarks, or
workflow provenance.

A useful answer can be short:

1. "Yes, this would help for [specific workflow]."
2. "No, our existing artifact already captures this as [specific field]."
3. "The missing field would be [specific field]."
4. "This is not useful because [specific reason]."

Generic praise is less useful than a concrete yes/no/field-level answer.

## Closest Current Use Case

The closest current use case found so far is QMB100 / PhysVEC: AI-generated
quantum many-body computations where programming correctness and physical
validity both need to be auditable.

Focused one-pager:

```text
docs/CAPAS_ONE_PAGER_QMB100.md
```

## Non-Claims

CAPAS does not claim:

- to replace QMB100/PhysVEC, SciAgentGym, VVUQ, or RO-Crate,
- to invent scientific traces or provenance,
- to prove broad LLM scientific reasoning,
- to be fine-tune ready,
- to have external user validation yet.

The current goal is to find out whether the evidence fields are useful to
practitioners, or whether the project should narrow further.
