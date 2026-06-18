# Witness Independence Axis

Sprint 2 plants the second evidence coordinate: not only whether a result has
evidence, but how independent the witness is from the producing computation.

This document is deliberately conservative. A certificate can be mathematically
strong while still not being an independent witness. CAPAS records both facts
instead of collapsing them into a single "verified" label.

## Levels

| Level | Strength | Meaning | Current coverage |
|---|---:|---|---|
| `analytic_no_solver` | 5 | Closed-form truth, no computational witness. | analytic traces |
| `theory_scaling_law_no_solver` | 5 | Theory-known scaling law or universal exponent; no computational witness, but fit/tolerance applies. | `trace_033`, `trace_034`, `trace_035` |
| `different_library_same_runtime` | 4 | Different library checks the result inside the same Python/runtime process. | `trace_018` |
| `different_method_same_runtime` | 4 | Different computational method checks the result inside the same runtime. | `trace_019` |
| `same_runtime_exact_fci_with_external_experimental_reference` | 4 | Same-runtime exact model solve compared with external measured reference. | `trace_021` |
| `different_algorithm_same_runtime` | 3 | Different algorithmic calculation in the same runtime/library family. | `trace_011` |
| `algorithmic_certificate_exact_svd_same_runtime` | 3 | Formal mathematical certificate emitted in the same runtime; strong evidence, not independent witness. | `trace_016`, `trace_017` |
| `algorithmic_error_certificate_same_runtime` | 2 | Same-runtime non-formal error estimate. | `trace_015` |
| `none` | 0 | No witness or certificate attached. | no-evidence, failed, rejected traces |

## Seed Trace

`trace_018` checks Bell-pair entanglement entropy:

- primary value: `physics_magnitude_lab.quantum_engine.entanglement_entropy`
- witness: explicit reduced density matrix diagonalized with `scipy.linalg.eigh`
- evidence level: `cross_sim`
- witness independence: `different_library_same_runtime`

This is stronger than the NumPy-only `trace_011`, but it is still same-runtime
evidence. It does not prove cross-BLAS, cross-runtime, or cross-hardware
independence.

`trace_019` checks a tiny assignment-to-Ising bridge:

- primary value: exact diagonalization of the Ising Hamiltonian
- witness: exhaustive enumeration of all `2^8` assignments
- evidence level: `analytic`
- witness independence: `different_method_same_runtime`

This certifies optimality for the small instance only. It does not show an
optimization speedup.

## Non-Degradation Rules

1. Do not treat same-runtime certificates as independent witnesses.
2. Do not collapse `algorithmic_certificate_exact_svd_same_runtime` into
   `different_library_same_runtime`; the former can be formal without being
   independent.
3. Do not claim cross-runtime or cross-BLAS evidence until a trace actually runs
   across distinct runtimes/BLAS stacks and records both stacks.
4. Any new `verification_independence` value must be added to
   `benchmarks/validate_witness_independence.py` and covered by at least one
   trace or listed as explicit debt.
5. Do not collapse `theory_scaling_law_no_solver` into `analytic_no_solver`:
   scaling-law evidence needs finite-size points, fit method, and a
   preregistered tolerance.

## Open Debt

The seed fact for this axis remains the Accelerate-vs-OpenBLAS divergence found
earlier in the project. That result motivates a future stronger level, but it is
not yet encoded as a CAPAS trace.

Next levels to build:

1. `different_blas_same_method`: same method, distinct BLAS/LAPACK stack.
2. `different_runtime_same_method`: same method across separate Python/runtime
   environments.
3. `different_method_different_runtime`: different solver family across separate
   runtime stack.

The current Sprint 2 result is the first runnable taxonomy and one cross-library
seed, not the complete independence ladder.
