# CAPAS Formal-Bound Evidence Axis

`formal_bound` is the strongest non-analytic evidence level CAPAS currently
records. It must mean a mathematical certificate, not a heuristic estimate.

## What Is Implemented Now

`trace_016` records a single-cut Schmidt/SVD truncation certificate.

For a normalized state reshaped across one bipartition, the Schmidt
decomposition gives singular values `s_i`. Truncating to rank `k` discards

```text
sum_{i > k} s_i^2
```

By the Eckart-Young theorem and orthogonality of the Schmidt components, that
discarded weight is exactly the squared 2-norm error of the optimal rank-`k`
state approximation across that cut.

CAPAS records this as:

```text
physical_evidence_level = formal_bound
certification_status = formal_single_cut_state_norm_bound
formal_bound_status = established_for_single_schmidt_truncation_not_global_dmrg
bound_scope = single_bipartition_state_truncation
```

This is a real formal certificate, but it is deliberately narrow.

## What Is Not Implemented Yet

This is **not** a global DMRG certificate.

The local DMRG implementation in `physics-magnitude-lab` performs SVD
truncations inside `_optimize_bond`, so local discarded weights are accessible
in principle. However, CAPAS does not yet claim a global DMRG state bound or an
observable bound because that requires explicit assumptions about canonical
form, normalization, truncation composition across sweeps, and how state-norm
error transfers to the observable being reported.

Until those assumptions are encoded and tested, DMRG-wide truncation data should
remain `estimated_bound` or `formal_bound_candidate`, not `formal_bound`.

## Evidence Axis

Current non-failure evidence levels:

- `analytic`: exact closed-form truth.
- `cross_sim`: independent computational witness.
- `formal_bound`: mathematical error certificate for a declared scope.
- `estimated_bound`: useful estimator without formal certificate.
- `none`: no attached evidence.

The point of this axis is not to say every result is equally verified. It is to
make the strength and scope of the evidence explicit in the trace.
