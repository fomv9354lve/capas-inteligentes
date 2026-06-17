# Experimental Evidence Axis

This axis tests whether CAPAS can seal a computation against a measured physical
reference without confusing model correctness with physical correctness.

Seed trace:

```text
trace_021
coverage_case = quantum_chemistry_experimental_reference
molecule = H2
geometry = R(H-H) = 0.7414 Angstrom
basis = STO-3G
solver = PySCF FCI
physical_evidence_level = experimental
```

Paired improved-basis trace:

```text
trace_022
coverage_case = quantum_chemistry_experimental_reference_improved_basis
molecule = H2
geometry = R(H-H) = 0.7414 Angstrom
basis = cc-pVDZ
solver = PySCF FCI
physical_evidence_level = experimental
```

## References

Model reference:

- PySCF FCI total energy for H2/STO-3G at 0.7414 Angstrom.
- PySCF is an open-source electronic-structure platform for quantum chemistry.
  See Sun et al., "The Python-based Simulations of Chemistry Framework (PySCF)",
  arXiv:1701.08223.

Experimental reference:

- H2 measured dissociation energy `D0(N=1) = 35999.582834 cm^-1`.
- Source: Hölsch et al., "Benchmarking theory with an improved measurement of
  the ionization and dissociation energies of H2", arXiv:1902.09471.

Chemical accuracy threshold:

```text
1 kcal/mol = 0.0015936 Hartree
```

## Critical Distinction

CAPAS records three different quantities:

1. `solver_error_hartree`

   Difference between the computed model energy and the exact FCI value for the
   same STO-3G Hamiltonian.

2. `model_error_hartree`

   Difference between the minimal-basis model binding energy and the measured H2
   dissociation reference.

3. `within_chemical_accuracy`

   Whether the model error is below 1 kcal/mol.

For `trace_021`, the solver error is zero for the model, while the model error is
large. This is not a failure of the trace. It is the point of the trace.

For `trace_022`, the solver error is still zero for the declared model, but the
larger cc-pVDZ basis reduces the model error against the same experimental D0
reference. This shows the axis doing real work: the trace can distinguish an
exact but poor model from an exact and materially better model.

## Non-Degradation Rule

Do not interpret:

```text
physical_evidence_level = experimental
```

as:

```text
the calculation is experimentally accurate
```

It means:

```text
the trace carries a measured physical reference and records the distance to it
```

The trace is valuable when it separates the blame:

- solver error: did the computation solve the declared model?
- model error: did the declared model represent the physical molecule?

## Scope

`trace_021` is scoped to:

```text
single_molecule_minimal_basis_equilibrium_geometry
```

`trace_022` is scoped to:

```text
single_molecule_larger_basis_equilibrium_geometry
```

It does not claim:

- competitive quantum chemistry,
- basis-set convergence,
- vibrational/relativistic/QED corrections,
- chemical accuracy for H2.

It claims only that CAPAS can seal the solver/model/experiment separation in a
single auditable trace.

## Current Pair

| Trace | Basis | Solver error (Ha) | Model error vs D0 (Ha) | Within 1 kcal/mol |
|---|---|---:|---:|---|
| `trace_021` | STO-3G | 0.0 | 0.040080307195131615 | false |
| `trace_022` | cc-pVDZ | 0.0 | 0.0008309583469347491 | true |

Do not read this as a claim that cc-pVDZ fully solves H2 spectroscopy. It only
shows that the trace grammar preserves the improvement in model error when the
declared model improves.
