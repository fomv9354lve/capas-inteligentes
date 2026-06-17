# Convergence To Experiment

This experiment tests whether CAPAS can seal a positive result, not only
honest failures.

The molecule is H2 at `R = 0.7414 Angstrom`. Each basis is solved by PySCF FCI.
The electronic binding energy is compared to the measured H2 `D0` reference
after adding the same-model harmonic ZPE for that basis:

```text
D_e(reference, basis) = D0(experiment) + ZPE_harmonic(model, basis)
```

Chemical accuracy threshold:

```text
1 kcal/mol = 0.0015936 Hartree
```

Robustness rule:

```text
true_not_robust: error < threshold but margin < 5% of threshold
true_robust:     error < threshold and margin >= 5% of threshold
```

## Trace

```text
trace_027
coverage_case = quantum_chemistry_basis_convergence_to_experiment
physical_evidence_level = experimental
bound_scope = single_molecule_basis_convergence_curve_electronic_vibrational_split
```

## Curve

| Basis | Orbitals | Corrected error (Ha) | Margin (Ha) | Status |
|---|---:|---:|---:|---|
| STO-3G | 2 | 0.028646971371818652 | -0.027053371371818652 | false |
| cc-pVDZ | 10 | 0.009825356013931502 | -0.008231756013931502 | false |
| cc-pVTZ | 28 | 0.0015326709489749402 | 0.00006092905102505976 | true_not_robust |
| cc-pVQZ | 60 | 0.0003112863147403111 | 0.0012823136852596888 | true_robust |
| cc-pV5Z | 110 | 0.00002049610541435265 | 0.0015731038945856473 | true_robust |

## Result

```text
monotonic_nonincreasing_error = true
first_within_chemical_accuracy_basis = cc-pvtz
first_robust_basis = cc-pvqz
best_basis = cc-pv5z
ceiling_basis_solved = cc-pv5z
ceiling_basis_orbitals = 110
```

## Interpretation

`cc-pVTZ` crosses the chemical-accuracy threshold, but only barely. CAPAS marks
it `true_not_robust`.

`cc-pVQZ` is the first robust crossing. CAPAS marks it `true_robust`.

`cc-pV5Z` is the best and largest basis solved in this local run. It is the
current measured M4 ceiling for this exact FCI H2 ladder.

## Non-Claims

This does not claim that CAPAS performs competitive quantum chemistry.

This does not claim that H2 convergence generalizes to larger molecules.

This does claim that CAPAS can seal:

- a convergence curve,
- the exact basis where a model first becomes chemically accurate,
- whether that success is robust or merely marginal,
- and the hardware-local ceiling actually reached.
