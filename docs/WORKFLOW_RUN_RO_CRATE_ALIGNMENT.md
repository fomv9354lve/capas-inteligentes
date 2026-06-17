# CAPAS Alignment With Workflow Run RO-Crate

CAPAS does not define a new workflow provenance container. It uses RO-Crate and
aligns its exported crates with the Workflow Run RO-Crate shape, then adds a
small CAPAS profile for physical evidence.

Reference: Workflow Run RO-Crate, "Recording provenance of workflow runs with
RO-Crate" (arXiv:2312.07852).

## What CAPAS Aligns To

Each exported CAPAS crate contains:

- a root `Dataset` for the crate
- `ro-crate-metadata.json` as the metadata descriptor
- a `ComputationalWorkflow` node for the CAPAS costurero workflow
- a `CreateAction` node for the traced run
- a workload input entity
- a result output entity when a result exists
- a sealed `runtrace.json`
- a PROV-shaped `runtrace.prov.json`
- event `Action` nodes for each recorded pipeline step

The `CreateAction` records:

- `agent`: the CAPAS costurero software
- `instrument`: the CAPAS workflow plan
- `object`: the workload entity
- `result`: the result entity, when execution produced one
- `actionStatus`: completed or failed
- `startTime` and `endTime`
- CAPAS routing and evidence status metadata

## What CAPAS Adds

CAPAS adds `capas:PhysicalEvidence` as a domain-specific evidence entity. This
entity records:

- `physicalEvidenceLevel`
- `verificationIndependence`
- `referenceTruth`
- `benchmarkFamily`
- `observable`
- `expected`, `value`, and `absError`
- `certificationStatus`
- `sourceLabel`

This is the part CAPAS contributes over generic workflow provenance: the run is
not only described as a workflow execution, it also carries explicit evidence
about whether the scientific result was physically checked, how, and how
independent the witness was.

## Current Status

Current status is shape-compatible export plus external RO-Crate validation, not
official CAPAS profile registration.

The local validator checks that representative traces contain the expected
Workflow Run RO-Crate structure and the CAPAS evidence extension. It does not
claim that CAPAS has passed an external Workflow Run RO-Crate validator or that
the CAPAS profile is registered in the RO-Crate profile registry.

The external ResearchObject `rocrateValidator` package validates the generated
crates as RO-Crates. The current result is `valid_with_warning` because the
validator's workflow extension list does not recognize `.py` workflow
descriptors. CAPAS keeps the descriptor as Python because it points at the real
implementation shape instead of pretending to be a CWL, Galaxy, or KNIME
workflow.

## Remaining Work

- Run an external RO-Crate / Workflow Run RO-Crate validator when selected.
- Replace the provisional CAPAS profile URI with a stable registered profile
  URI if the profile is submitted.
- Add distributed provenance only if CAPAS starts recording multi-location
  executions.
- Add richer workflow parameter metadata if a target community requests it.
