# CAPAS Evidence Coverage

CAPAS coverage is not measured by the number of successful traces. It is measured
by whether the same trace/profile format handles heterogeneous evidence states
without lying.

## Coverage Cases

| Case | Trace | RO-Crate | Evidence status | Purpose |
|---|---|---|---|---|
| `analytic_success` | `benchmarks/gold_traces/trace_006.json` | `benchmarks/ro_crates/trace_006/ro-crate-metadata.json` | `present` | Closed-form physical truth, Heisenberg dimer `E0 = -3J/4` |
| `cross_sim_success` | `benchmarks/gold_traces/trace_011.json` | `benchmarks/ro_crates/trace_011/ro-crate-metadata.json` | `present` | Result checked against a different algorithmic witness |
| `cross_library_success` | `benchmarks/gold_traces/trace_018.json` | `benchmarks/ro_crates/trace_018/ro-crate-metadata.json` | `present` | Result checked against a different library in the same runtime |
| `no_evidence_success` | `benchmarks/gold_traces/trace_012.json` | `benchmarks/ro_crates/trace_012/ro-crate-metadata.json` | `none_declared` | Successful result with no attached physical witness |
| `backend_failed` | `benchmarks/gold_traces/trace_013.json` | `benchmarks/ro_crates/trace_013/ro-crate-metadata.json` | `not_applicable_failed` | Failed backend captured as provenance, not hidden |
| `rejected_by_router` | `benchmarks/gold_traces/trace_014.json` | `benchmarks/ro_crates/trace_014/ro-crate-metadata.json` | `not_applicable_rejected` | Non-execution due memory/resource guard captured as provenance |
| `estimated_bound_candidate` | `benchmarks/gold_traces/trace_015.json` | `benchmarks/ro_crates/trace_015/ro-crate-metadata.json` | `present` | Tensor-network truncation estimate, explicitly not a formal certificate |
| `formal_bound_success` | `benchmarks/gold_traces/trace_016.json` | `benchmarks/ro_crates/trace_016/ro-crate-metadata.json` | `present` | Single-cut Schmidt truncation certificate, exact for squared state-norm error |
| `formal_bound_composition_success` | `benchmarks/gold_traces/trace_017.json` | `benchmarks/ro_crates/trace_017/ro-crate-metadata.json` | `present` | Multi-step Schmidt truncation composition bound for full-state norm error |

## Current Summary

The local audit currently reports:

- `analytic_success`: 10
- `cross_sim_success`: 1
- `cross_library_success`: 1
- `no_evidence_success`: 1
- `backend_failed`: 1
- `rejected_by_router`: 1
- `estimated_bound_candidate`: 1
- `formal_bound_success`: 1
- `formal_bound_composition_success`: 1

This means `coverage_ready=True`.

It does **not** mean `fine_tune_ready=True`. Fine-tune readiness still requires
blind inference review and enough accepted traces.

## Validation Command

```bash
python3 benchmarks/validate_ro_crates.py
```

Expected high-level result:

```text
trace_001: ok (analytic_success, present)
trace_011: ok (cross_sim_success, present)
trace_018: ok (cross_library_success, present)
trace_012: ok (no_evidence_success, none_declared)
trace_013: ok (backend_failed, not_applicable_failed)
trace_014: ok (rejected_by_router, not_applicable_rejected)
trace_015: ok (estimated_bound_candidate, present)
trace_016: ok (formal_bound_success, present)
trace_017: ok (formal_bound_composition_success, present)
validate_ro_crates passed
```
