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

Larger-basis stress trace:

```text
trace_023
coverage_case = quantum_chemistry_experimental_reference_larger_basis
molecule = H2
geometry = R(H-H) = 0.7414 Angstrom
basis = cc-pVTZ
solver = PySCF FCI
physical_evidence_level = experimental
```

Reference-definition corrected trace:

```text
trace_024
coverage_case = quantum_chemistry_reference_definition_corrected
molecule = H2
geometry = R(H-H) = 0.7414 Angstrom
basis = cc-pVTZ
solver = PySCF FCI
physical_evidence_level = experimental
reference_definition_match = corrected_approximate_D0_plus_ZPE_to_match_electronic_De
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

Reference-definition correction:

- The raw experimental value above is a dissociation energy `D0`, while the
  clamped-nuclei electronic calculation is a `D_e`-like electronic well depth.
- `trace_024` uses an approximate H2 zero-point energy of `0.26 eV` to compare
  like with like: `D_e approx D0 + ZPE`.
- Source for the approximate ZPE: Gross and Scheffler,
  "Ab initio quantum and molecular dynamics of the dissociative adsorption of
  hydrogen on Pd(100)", arXiv:cond-mat/9702090.

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

4. `reference_definition_error_hartree`

   Error introduced by comparing quantities with different physical
   definitions, for example electronic `D_e`-like binding energy versus
   experimental `D0` with zero-point vibration included.

5. `reference_definition_corrected_error_hartree`

   Remaining error after applying the declared reference-definition correction.
   In `trace_024`, this is the error after comparing cc-pVTZ electronic binding
   energy against `D0 + approximate ZPE`.

For `trace_021`, the solver error is zero for the model, while the model error is
large. This is not a failure of the trace. It is the point of the trace.

For `trace_022`, the solver error is still zero for the declared model, but the
larger cc-pVDZ basis reduces the model error against the same experimental D0
reference. This shows the axis doing real work: the trace can distinguish an
exact but poor model from an exact and materially better model.

For `trace_023`, the basis is larger again, but the model error for this simple
electronic binding-energy comparison gets worse than `trace_022`. This is not
hidden. The trace records that "larger model" is not the same thing as "closer
to the chosen measured reference" when other physical corrections and reference
definitions are not being audited.

For `trace_024`, CAPAS records the missing distinction explicitly: `trace_023`
compared an electronic `D_e`-like quantity to experimental `D0`. Adding an
approximate ZPE correction to the reference turns the comparison into
electronic `D_e` versus approximate experimental `D_e`. This is not a new
solver result; it is a corrected definition of what the solver result is being
compared against.

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
- reference-definition error: did we compare the computed quantity to the same
  physical quantity in the experiment?

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
| `trace_023` | cc-pVTZ | 0.0 | 0.008689903240270247 | false |
| `trace_024` | cc-pVTZ + D0/ZPE definition correction | 0.0 | 0.0008649205254178116 | true |

For `trace_024`, the raw D0 comparison error remains
`0.008689903240252483 Hartree`; the corrected error above is after adding
`0.009554823765670298 Hartree` of approximate ZPE to the experimental reference.

Do not read this as a claim that cc-pVDZ fully solves H2 spectroscopy. It only
shows that the trace grammar preserves the improvement in model error when the
declared model improves.

Do not read `trace_023` as a solver failure. It is exact for its declared model.
The useful fact is that CAPAS records a model/reference mismatch instead of
forcing a monotonic "bigger basis is better" story.

Do not read `trace_024` as full H2 spectroscopy. Its ZPE correction is
approximate. The trace is valuable because it records the correction and its
scope instead of silently treating `D0` and `D_e` as the same physical quantity.
