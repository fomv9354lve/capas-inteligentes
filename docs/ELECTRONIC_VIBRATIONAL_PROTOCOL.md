# Electronic/Vibrational Evidence Protocol

CAPAS must not compare an electronic calculation against a vibrational
experimental reference without declaring the reference definition.

This protocol is used by the chemistry traces.

## Quantities

`D_e`

: Electronic well depth or electronic atomization energy. This is the
  clamped-nuclei quantity produced by an electronic-structure solve.

`ZPE`

: Zero-point vibrational energy. In the current local traces this is computed
  as a same-model harmonic correction:

```text
ZPE = 0.5 * sum(positive harmonic frequencies)
```

`D_0`

: Dissociation or atomization energy from the vibrational ground state. For a
  simple correction:

```text
D_0(model) ~= D_e(model) - ZPE_harmonic(model)
D_e(reference) ~= D_0(experiment) + ZPE_harmonic(model)
```

## Required Trace Fields

Every electronic/vibrational chemistry trace must record:

- `solver_error_hartree`
- `electronic_atomization_energy_hartree` or `model_binding_energy_hartree`
- `vibrational_zpe_hartree`
- `harmonic_frequencies_cm_inverse`
- `reference_definition_match`
- `reference_definition_correction`
- `reference_definition_error_hartree`
- `reference_definition_corrected_error_hartree`
- `within_chemical_accuracy`

## Non-Degradation Rules

Do not call a calculation experimentally accurate when only the electronic
Hamiltonian was solved exactly.

Do not compare raw experimental `D0` against electronic `De` without a
`reference_definition_match` field.

Do not treat same-model harmonic ZPE as an anharmonic spectroscopic constant.
It is a reproducible correction with declared scope, not full spectroscopy.

Do not hide failure after correction. A corrected trace may still be far from
experiment because the model or basis is poor.

## Current Coverage

`trace_024`

: H2/cc-pVTZ exact finite-basis electronic solve, corrected by same-model
  harmonic ZPE before comparison to the measured H2 `D0` reference.

`trace_025`

: H2O/STO-3G exact finite-basis electronic solve, same-model harmonic ZPE, and
  comparison to a tabulated atomization reference assembled from O-H
  dissociation energies.

`trace_026`

: CH4/STO-3G exact finite-basis electronic solve, same-model harmonic ZPE with
  nine positive modes, and comparison to a tabulated atomization reference
  assembled from successive C-H dissociation energies.

## What This Proves

The chemistry axis does not prove that CAPAS performs competitive quantum
chemistry.

It proves that CAPAS can seal the difference between:

- solver error,
- model or basis error,
- vibrational/reference-definition error,
- and remaining discrepancy to experiment.
