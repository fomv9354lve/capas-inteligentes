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
reference_definition_match = corrected_model_harmonic_D0_plus_ZPE_to_match_electronic_De
```

Polyatomic electronic/vibrational trace:

```text
trace_025
coverage_case = quantum_chemistry_polyatomic_electronic_vibrational
molecule = H2O
geometry = bent H2O, STO-3G demo geometry
basis = STO-3G
solver = PySCF FCI
physical_evidence_level = experimental
reference_definition_match = corrected_model_harmonic_electronic_atomization_minus_ZPE_to_match_D0_atomization
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

- The raw H2 experimental value above is a dissociation energy `D0`, while the
  clamped-nuclei electronic calculation is a `D_e`-like electronic well depth.
- `trace_024` computes a same-model harmonic ZPE with PySCF and compares like
  with like: `D_e approx D0 + ZPE_harmonic(model)`.
- `trace_025` computes a same-model harmonic ZPE for H2O and compares the
  resulting `D0`-like atomization energy against a tabulated atomization
  reference assembled from O-H dissociation energies.
- Source for the relation between `D0` and `D_e`: standard bond-dissociation
  terminology, where `D0 = D_e - epsilon_0`.

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
   energy against `D0 + same-model harmonic ZPE`.

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
compared an electronic `D_e`-like quantity to experimental `D0`. Adding the
same-model harmonic ZPE to the reference turns the comparison into electronic
`D_e` versus model-harmonic experimental `D_e`. This is not a new solver result;
it is a corrected definition of what the solver result is being compared
against.

For `trace_025`, CAPAS applies the same protocol to a polyatomic molecule. H2O
has three positive harmonic vibrational modes in the local STO-3G model. The
trace records the electronic atomization energy, the model-harmonic ZPE, the
ZPE-corrected atomization energy, and the remaining gap to experiment.

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
| `trace_024` | cc-pVTZ + model-harmonic D0/ZPE definition correction | 0.0 | 0.0015326709489927315 | true |
| `trace_025` | H2O/STO-3G + model-harmonic ZPE | 0.0 | 0.10200295763719147 | false |

For `trace_024`, the raw D0 comparison error remains
`0.008689903240252483 Hartree`; the corrected error above is after adding
`0.010222574189245201 Hartree` of same-model harmonic ZPE to the experimental
reference.

For `trace_025`, the raw electronic atomization mismatch is
`0.07621529052225856 Hartree`; after subtracting model-harmonic ZPE
(`0.025787667114932907 Hartree`) the remaining mismatch is
`0.10200295763719147 Hartree`. The correction makes the reference definition
clear, but the minimal-basis model remains poor.

Do not read this as a claim that cc-pVDZ fully solves H2 spectroscopy. It only
shows that the trace grammar preserves the improvement in model error when the
declared model improves.

Do not read `trace_023` as a solver failure. It is exact for its declared model.
The useful fact is that CAPAS records a model/reference mismatch instead of
forcing a monotonic "bigger basis is better" story.

Do not read `trace_024` or `trace_025` as full spectroscopy. Their ZPE
corrections are same-model harmonic corrections, not anharmonic spectroscopic
constants. The traces are valuable because they record the correction and its
scope instead of silently treating `D0` and `D_e` as the same physical quantity.
