# R2 Cono Sur Real Claim Gate

Date: 2026-06-17

Purpose: replace purely synthetic regional evidence-gate examples with claims
extracted from real Cono Sur sources.

This is still a small experiment. It does not prove regional usefulness. It
proves that CAPAS can take real regional claims and mechanically distinguish
weakly licensed claims from stronger overclaims.

## Sources Used

### S01: Godoy and Dardatti, validation survey

Source:

- Luis A. Godoy and Patricia M. Dardatti, "Validacion de Modelos en Mecanica
  Computacional", Mecanica Computacional, 2001.
- HTML: https://cimec.org.ar/ojs/index.php/mc/article/view/1854
- PDF endpoint: https://cimec.org.ar/ojs/index.php/mc/article/download/1854/1819

Why it matters:

This paper gives regional vocabulary for CAPAS. It explicitly separates
verification/internal validation from external validation and classifies common
validation practices in computational mechanics.

Facts extracted into the checker:

```text
surveyed_articles: 104
experimental comparisons: 9
analytic comparisons: 33
comparisons with other authors/methods: 40
commercial package comparisons: 5
benchmarks: 1
algorithm-efficiency comparisons: 13
```

CAPAS gate outcomes:

| Claim | Verdict | Reason |
|---|---|---|
| `validation_taxonomy_observed` | ACCEPT | The source records a validation taxonomy over surveyed papers. |
| `experimental_validation_dominates_practice` | REJECT | Experimental validation appears in `9/104` surveyed papers, so dominance is not licensed. |

This is a good CAPAS case because it is not a computation result. It is a
regional evidence vocabulary source. It gives CAPAS permission to use terms like
internal verification, external validation, comparison with analytic solutions,
comparison with experiments, benchmarks, and comparison with other numerical
methods without inventing them.

### S03: Romagnoli, Portapila, and Morvan, hydraulic jump simulation

Source:

- Marta Romagnoli, Margarita Portapila, and Herve Morvan, "Simulacion
  Computacional del Resalto Hidraulico", Mecanica Computacional, 2009.
- HTML: https://cimec.org.ar/ojs/index.php/mc/article/view/2826

Why it matters:

This is a real applied Cono Sur simulation paper. The abstract states that the
work uses a 2D RANS model with a two-equation turbulence closure and VOF-type
free-surface treatment, and that simulated longitudinal velocity `U` and
turbulent kinetic energy `k` show good agreement with experimental observations.

Facts extracted into the checker:

```text
method: 2d_rans_k_epsilon_vof
reference_type: experiment
agreement_claim_type: qualitative
observables:
  - longitudinal_mean_velocity_U
  - turbulent_kinetic_energy_k
reference_definition_match: unknown
```

CAPAS gate outcomes:

| Claim | Verdict | Reason |
|---|---|---|
| `qualitative_experimental_agreement_reported` | ACCEPT | The source reports qualitative experimental agreement for declared observables. |
| `matches_experiment` | HOLD | The metadata/abstract-level extraction does not provide `reference_definition_match`, numeric `abs_error_vs_reference`, or tolerance. |

This is the important behavior. CAPAS does not reject the paper. It accepts the
weak claim the extracted evidence supports, but holds the stronger quantitative
claim until numeric comparison/tolerance information is extracted.

## What This Proves

R2 real confirms the core regional gate behavior:

```text
real source text
  -> extracted evidence fields
  -> claim requested
  -> ACCEPT / REJECT / HOLD
```

The gate can now do three useful things on real Cono Sur material:

1. Accept vocabulary/taxonomy claims from a regional validation survey.
2. Reject a false generalization about experimental validation dominance.
3. Hold a strong experimental-match claim when only qualitative agreement is
   available from the extracted source level.

## What This Does Not Prove

This does not prove that CAPAS can automatically parse arbitrary Spanish papers.
The extraction was manual and conservative.

This does not prove domain validation. The S03 hydraulic-jump source licenses
only the weak claim that qualitative agreement is reported at the extracted
level.

This does not prove regional adoption. It only proves that the gate can bite a
real regional claim without inventing evidence.

## Implementation

The real-source checks are implemented in:

```text
benchmarks/validate_evidence_claims.py
```

Current validation:

```text
python3 benchmarks/validate_evidence_claims.py
```

passes:

```text
25/25 checks
4 real regional checks
```

## Next R2 Debt

The next stronger version should extract a full-text numeric comparison from
S03 or another AMCA/CIMEC paper:

```text
reference_type = experiment
reference_definition_match = true
abs_error_vs_reference = numeric
reference_tolerance = numeric
```

Only then should CAPAS allow `matches_experiment = ACCEPT`.

