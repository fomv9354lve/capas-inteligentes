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
| `combinatorial_optimization_function_level` | `benchmarks/gold_traces/trace_019.json` | `benchmarks/ro_crates/trace_019/ro-crate-metadata.json` | `present` | Small assignment-to-Ising optimum checked by brute force |
| `combinatorial_optimization_degenerate_function_level` | `benchmarks/gold_traces/trace_020.json` | `benchmarks/ro_crates/trace_020/ro-crate-metadata.json` | `present` | Small assignment-to-Ising optimum set checked by brute force |
| `quantum_chemistry_experimental_reference` | `benchmarks/gold_traces/trace_021.json` | `benchmarks/ro_crates/trace_021/ro-crate-metadata.json` | `present` | H2/STO-3G FCI compared with measured H2 dissociation energy |
| `quantum_chemistry_experimental_reference_improved_basis` | `benchmarks/gold_traces/trace_022.json` | `benchmarks/ro_crates/trace_022/ro-crate-metadata.json` | `present` | H2/cc-pVDZ FCI compared with measured H2 dissociation energy |
| `quantum_chemistry_experimental_reference_larger_basis` | `benchmarks/gold_traces/trace_023.json` | `benchmarks/ro_crates/trace_023/ro-crate-metadata.json` | `present` | H2/cc-pVTZ FCI compared with measured H2 dissociation energy |
| `quantum_chemistry_reference_definition_corrected` | `benchmarks/gold_traces/trace_024.json` | `benchmarks/ro_crates/trace_024/ro-crate-metadata.json` | `present` | H2/cc-pVTZ electronic binding energy compared with D0 plus same-model harmonic ZPE |
| `quantum_chemistry_polyatomic_electronic_vibrational` | `benchmarks/gold_traces/trace_025.json` | `benchmarks/ro_crates/trace_025/ro-crate-metadata.json` | `present` | H2O/STO-3G exact model solve with harmonic ZPE and atomization reference |
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
- `combinatorial_optimization_function_level`: 1
- `combinatorial_optimization_degenerate_function_level`: 1
- `quantum_chemistry_experimental_reference`: 1
- `quantum_chemistry_experimental_reference_improved_basis`: 1
- `quantum_chemistry_experimental_reference_larger_basis`: 1
- `quantum_chemistry_reference_definition_corrected`: 1
- `quantum_chemistry_polyatomic_electronic_vibrational`: 1
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
trace_019: ok (combinatorial_optimization_function_level, present)
trace_020: ok (combinatorial_optimization_degenerate_function_level, present)
trace_021: ok (quantum_chemistry_experimental_reference, present)
trace_022: ok (quantum_chemistry_experimental_reference_improved_basis, present)
trace_023: ok (quantum_chemistry_experimental_reference_larger_basis, present)
trace_024: ok (quantum_chemistry_reference_definition_corrected, present)
trace_025: ok (quantum_chemistry_polyatomic_electronic_vibrational, present)
trace_012: ok (no_evidence_success, none_declared)
trace_013: ok (backend_failed, not_applicable_failed)
trace_014: ok (rejected_by_router, not_applicable_rejected)
trace_015: ok (estimated_bound_candidate, present)
trace_016: ok (formal_bound_success, present)
trace_017: ok (formal_bound_composition_success, present)
validate_ro_crates passed
```
