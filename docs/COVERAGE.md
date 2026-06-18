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
| `quantum_chemistry_larger_polyatomic_electronic_vibrational` | `benchmarks/gold_traces/trace_026.json` | `benchmarks/ro_crates/trace_026/ro-crate-metadata.json` | `present` | CH4/STO-3G exact model solve with harmonic ZPE and atomization reference |
| `quantum_chemistry_basis_convergence_to_experiment` | `benchmarks/gold_traces/trace_027.json` | `benchmarks/ro_crates/trace_027/ro-crate-metadata.json` | `present` | H2 basis ladder to experimental D0 with robust threshold crossing |
| `universal_invariant_adversarial_failure` | `benchmarks/gold_traces/trace_028.json` | `benchmarks/ro_crates/trace_028/ro-crate-metadata.json` | `present` | Wrong-sign Heisenberg generator output passes local properties but fails analytic universal invariant |
| `universal_invariant_local_catches_anchor_not_needed` | `benchmarks/gold_traces/trace_029.json` | `benchmarks/ro_crates/trace_029/ro-crate-metadata.json` | `present` | Non-Hermitian Hamiltonian caught by local oracle before universal anchor is needed |
| `universal_invariant_both_oracles_catch` | `benchmarks/gold_traces/trace_030.json` | `benchmarks/ro_crates/trace_030/ro-crate-metadata.json` | `present` | Wrong coupling magnitude caught by both local parameter check and analytic invariant |
| `universal_invariant_non_heisenberg_adversarial_failure` | `benchmarks/gold_traces/trace_031.json` | `benchmarks/ro_crates/trace_031/ro-crate-metadata.json` | `present` | Valid product state passes local checks but fails Bell entropy invariant |
| `universal_invariant_no_anchor_control` | `benchmarks/gold_traces/trace_032.json` | `benchmarks/ro_crates/trace_032/ro-crate-metadata.json` | `present` | Valid arbitrary state with no claimed universal anchor |
| `universal_invariant_scaling_law_adversarial_failure` | `benchmarks/gold_traces/trace_033.json` | `benchmarks/ro_crates/trace_033/ro-crate-metadata.json` | `present` | Plausible decreasing Ising gaps fit wrong exponent `z=0.5` instead of `z=1` |
| `universal_invariant_scaling_law_positive_control` | `benchmarks/gold_traces/trace_034.json` | `benchmarks/ro_crates/trace_034/ro-crate-metadata.json` | `present` | Noisy decreasing Ising gaps fit `z=1` within preregistered tolerance |
| `universal_invariant_scaling_law_local_catches` | `benchmarks/gold_traces/trace_035.json` | `benchmarks/ro_crates/trace_035/ro-crate-metadata.json` | `present` | Constant gap sequence rejected by local monotonicity before exponent anchor is credited |
| `universal_invariant_scaling_law_simulation_generated` | `benchmarks/gold_traces/trace_036.json` | `benchmarks/ro_crates/trace_036/ro-crate-metadata.json` | `present` | Exact-diagonalization TFIM gaps fit `z=0.917`, within preregistered tolerance |
| `universal_invariant_scaling_law_randomized_adversarial` | `benchmarks/gold_traces/trace_037.json` | `benchmarks/ro_crates/trace_037/ro-crate-metadata.json` | `present` | Eight randomized plausible decreasing Ising gap sequences all miss `z=1` beyond preregistered tolerance |
| `universal_invariant_scaling_law_agent_generated_adversarial` | `benchmarks/gold_traces/trace_038.json` | `benchmarks/ro_crates/trace_038/ro-crate-metadata.json` | `present` | Scripted-agent plausible decreasing Ising gaps fit `z=0.5`, violating the `z=1` anchor |
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
- `quantum_chemistry_larger_polyatomic_electronic_vibrational`: 1
- `quantum_chemistry_basis_convergence_to_experiment`: 1
- `universal_invariant_adversarial_failure`: 1
- `universal_invariant_local_catches_anchor_not_needed`: 1
- `universal_invariant_both_oracles_catch`: 1
- `universal_invariant_non_heisenberg_adversarial_failure`: 1
- `universal_invariant_no_anchor_control`: 1
- `universal_invariant_scaling_law_adversarial_failure`: 1
- `universal_invariant_scaling_law_positive_control`: 1
- `universal_invariant_scaling_law_local_catches`: 1
- `universal_invariant_scaling_law_simulation_generated`: 1
- `universal_invariant_scaling_law_randomized_adversarial`: 1
- `universal_invariant_scaling_law_agent_generated_adversarial`: 1
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
trace_026: ok (quantum_chemistry_larger_polyatomic_electronic_vibrational, present)
trace_027: ok (quantum_chemistry_basis_convergence_to_experiment, present)
trace_028: ok (universal_invariant_adversarial_failure, present)
trace_029: ok (universal_invariant_local_catches_anchor_not_needed, present)
trace_030: ok (universal_invariant_both_oracles_catch, present)
trace_031: ok (universal_invariant_non_heisenberg_adversarial_failure, present)
trace_032: ok (universal_invariant_no_anchor_control, present)
trace_033: ok (universal_invariant_scaling_law_adversarial_failure, present)
trace_034: ok (universal_invariant_scaling_law_positive_control, present)
trace_035: ok (universal_invariant_scaling_law_local_catches, present)
trace_036: ok (universal_invariant_scaling_law_simulation_generated, present)
trace_037: ok (universal_invariant_scaling_law_randomized_adversarial, present)
trace_038: ok (universal_invariant_scaling_law_agent_generated_adversarial, present)
trace_012: ok (no_evidence_success, none_declared)
trace_013: ok (backend_failed, not_applicable_failed)
trace_014: ok (rejected_by_router, not_applicable_rejected)
trace_015: ok (estimated_bound_candidate, present)
trace_016: ok (formal_bound_success, present)
trace_017: ok (formal_bound_composition_success, present)
validate_ro_crates passed
```
