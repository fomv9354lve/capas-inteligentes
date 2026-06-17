# QMB100 Integration Plan

Status: no public QMB100 repository or task dataset found through targeted
search. Current plan is based on the public paper:

- https://arxiv.org/abs/2604.00149

## Decision

Prioritize QMB100 integration before `certified_bound`.

Reason:

- QMB100 is the closest known work in CAPAS' target domain.
- It has real users/authors and a clear benchmark framing.
- If CAPAS can wrap QMB100 attempts into RO-Crate/PROV evidence traces, CAPAS
  becomes complementary rather than speculative.

`certified_bound` remains a second track because it may be more original but is
more research-risky.

## What CAPAS Should Wrap

For each QMB100 task attempt, CAPAS should emit:

- original task id / paper id / task category
- selected engine or solver
- route/cost-model decision
- programming-verifier result
- scientific-verifier result
- physical assertions used
- convergence tests used
- numerical result
- reference result, if present
- discrepancy/error
- `physical_evidence_level`
- `verification_independence`
- `evidenceStatus`
- PROV export
- RO-Crate export

## Proposed Mapping

| QMB100 / PhysVEC concept | CAPAS field |
|---|---|
| task id | `workload_summary.task_id` |
| category: DMRG/NQS/qsim/DFT | `workload_summary.benchmark_family` |
| programming verifier pass/fail | trace event `programming_verifier` |
| scientific verifier pass/fail | trace event `scientific_verifier` |
| physical assertion test | `physical_evidence_level=invariant` or `analytic` |
| convergence test | `physical_evidence_level=cross_sim` or `invariant` |
| reference value | `reference_truth` |
| measured discrepancy | `abs_error` |
| failed task attempt | `evidenceStatus=not_applicable_failed` |
| skipped/rejected task | `evidenceStatus=not_applicable_rejected` |

## Integration Modes

### Mode A: Dataset Available

If QMB100 publishes task JSON/code, implement:

```text
qmb100 task -> CAPAS Workload -> run_with_trace -> PROV -> RO-Crate
```

Then run a small subset:

- one DMRG task,
- one qsim task,
- one NQS task,
- one failed/rejected task.

Success criterion:

```text
all attempts emit valid RO-Crate
scientific-verifier evidence appears as CAPAS PhysicalEvidence
failed/rejected attempts do not fake evidence
```

### Mode B: Dataset Not Available

Create a paper-level compatibility shim:

- manually encode one toy QMB100-like task per category,
- store `source_status=paper_level_mock`,
- do not present it as a QMB100 benchmark result.

Purpose:

- verify the CAPAS schema can represent PhysVEC-style verifier outputs,
- not claim reproduction of QMB100.

## Falsation

CAPAS' complementary value weakens if QMB100 releases per-run traces that already
include all of:

- RO-Crate or PROV export,
- first-class physical evidence entity,
- witness-independence metadata,
- reference-truth metadata,
- explicit no-evidence / failed / rejected states.

If that happens, CAPAS becomes an adapter or implementation variant, not a
distinct evidence profile.

## Second Track: Bounds

Investigate after QMB100 wrapping.

Hypothesis:

> Tensor-network truncation/error bounds can become a stronger
> `physical_evidence_level` inside CAPAS.

This is potentially more original but must be grounded in specific algorithms
and libraries.

Current status:

- Quimb `CircuitMPS.fidelity_estimate()` is documented as an estimate, not a
  formal certificate.
- CAPAS therefore uses `physical_evidence_level=estimated_bound` for the current
  trace.
- A future `formal_bound` level requires a documented mathematical bound, not
  quimb's fidelity estimate wording.

See `docs/QUIMB_FIDELITY_ESTIMATE_AUDIT.md`.
