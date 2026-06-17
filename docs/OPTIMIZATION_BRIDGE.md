# Optimization Bridge

This experiment is deliberately small. It tests whether CAPAS can seal a
function-level bridge:

```text
assignment problem -> Ising Hamiltonian -> exact simulator -> brute-force witness -> CAPAS evidence trace
```

It does not claim an optimization speedup.

## Instance

Eight tasks are assigned to two people:

```text
s_i = -1 -> Ada
s_i = +1 -> Ben
```

The assignment space has `2^8 = 256` configurations, so the true optimum is
verifiable by exhaustive enumeration.

Tasks:

1. `data_cleaning`
2. `api_integration`
3. `ux_copy`
4. `model_eval`
5. `dashboard`
6. `vendor_followup`
7. `qa_pass`
8. `deployment_notes`

## Hamiltonian

CAPAS uses the Ising objective:

```text
E(s) = C + sum_i h_i s_i + sum_{i<j} J_ij s_i s_j
```

The constant offset `C` is retained so the Hamiltonian energy equals the original
business objective, not just an equivalent argmin.

## Term Mapping

### Individual Affinity

Each task has an Ada cost and a Ben cost. Lower cost means stronger affinity.

For task `i`:

```text
cost_i(s_i) = ((c_ben + c_ada) / 2) + ((c_ben - c_ada) / 2) s_i
```

So:

```text
C += (c_ben + c_ada) / 2
h_i += (c_ben - c_ada) / 2
```

### Load Balance

Balance is represented as:

```text
lambda * (sum_i s_i)^2
```

Since `s_i^2 = 1`:

```text
lambda * (sum_i s_i)^2 = lambda * N + 2 lambda * sum_{i<j} s_i s_j
```

So:

```text
C += lambda * N
J_ij += 2 lambda for all pairs
```

### Pair Conflicts

For tasks that should not be assigned to the same person:

```text
gamma_ij * (1 + s_i s_j) / 2
```

This is `gamma_ij` when the two spins are equal and `0` when they differ.

So:

```text
C += gamma_ij / 2
J_ij += gamma_ij / 2
```

## Verification

`trace_019` solves the instance in two ways:

1. Primary path: exact diagonalization of the diagonal Ising Hamiltonian.
2. Witness path: exhaustive enumeration of all 256 assignments.

The trace is valid only if:

```text
solver_energy == brute_force_energy
solver_assignment in brute_force_optimal_assignments
```

The trace also records `degeneracy_count`, because several assignments can be
equally optimal.

## CAPAS Evidence

`trace_019` records:

```text
coverage_case = combinatorial_optimization_function_level
physical_evidence_level = analytic
verification_independence = different_method_same_runtime
reference_truth = exact_brute_force_enumeration_2^8_assignments
bound_scope = exact_small_instance_brute_force_verified
```

The `analytic` label is justified here because exhaustive enumeration gives the
exact optimum for the entire finite function.

## Falsification Notes

These are recorded in the trace:

1. No artificial terms are added beyond affinity, load balance, and stated
   conflict penalties.
2. At `N=8`, brute force is trivial. The simulator adds no speed at this scale.
3. The defended claim is sealed optimality evidence, not superior optimization
   performance.

## Non-Degradation Rule

Do not generalize this trace to larger optimization performance claims. It proves
that CAPAS can seal an exactly verified small optimization bridge. It does not
prove that the simulator is a better optimizer.

## Degenerate Instance

`trace_020` repeats the same function-level bridge with a deliberately
degenerate assignment problem.

Two tasks are symmetric:

```text
documentation_polish
release_notes
```

Both have equal Ada/Ben cost and enter the same balance/conflict structure. The
brute-force witness therefore returns more than one optimal assignment. CAPAS
records `degeneracy_count` and the full `optimal_assignments` set.

This is the operational meaning:

```text
if degeneracy_count > 1:
    mathematics found an optimal set, not a unique decision
    choosing one member requires an external/business criterion
```

The trace still has:

```text
physical_evidence_level = analytic
verification_independence = different_method_same_runtime
bound_scope = exact_small_instance_brute_force_verified
```

The stronger claim is not performance. The stronger claim is that CAPAS can seal
when the optimizer's answer is a set of equivalent decisions rather than a single
decision.
