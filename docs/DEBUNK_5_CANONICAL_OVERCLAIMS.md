# Debunk 5: Canonical Overclaims

Date: 2026-06-17

Purpose: explicitly debunk five common overclaims that can be made from strong
US/UK top-tier evidence. This does not attack the original papers. It protects
their real, falsifiable claims from being inflated into broader claims the
evidence does not license.

Source implementation:

```text
benchmarks/validate_evidence_claims.py
benchmarks/evidence_claim_validation_report.json
```

Validation:

```text
python3 benchmarks/validate_evidence_claims.py
```

Current result:

```text
39/39 checks pass
5/5 canonical overclaims receive REWRITE
```

## Debunk 1: Dexamethasone Benefits All Hospitalized COVID Subgroups

Source:

- RECOVERY Collaborative Group, "Dexamethasone in Hospitalized Patients with
  Covid-19", NEJM / PubMed: https://pubmed.ncbi.nlm.nih.gov/32678530/

Strong claim licensed:

```text
In the RECOVERY randomized trial, dexamethasone reduced 28-day mortality in the
overall hospitalized population, with benefit concentrated in patients receiving
respiratory support.
```

Overclaim debunked:

```text
Dexamethasone benefits all hospitalized COVID subgroups.
```

CAPAS verdict:

```text
REWRITE
```

Why:

The trace records benefit with invasive mechanical ventilation and oxygen
without invasive ventilation, but the `no_respiratory_support` subgroup has
rate ratio `1.19` with CI `[0.92, 1.55]`, so the confidence interval includes
null and the direction is not licensed as benefit.

What evidence would be needed to upgrade:

```text
subgroup_effects.no_respiratory_support.ci_excludes_null = true
subgroup_effects.no_respiratory_support.direction = benefit
```

## Debunk 2: BNT162b2 Prevents All Infection or Transmission

Source:

- Polack et al., "Safety and Efficacy of the BNT162b2 mRNA Covid-19 Vaccine",
  NEJM: https://www.nejm.org/doi/full/10.1056/NEJMoa2034577

Strong claim licensed:

```text
In the observer-blind randomized placebo trial, BNT162b2 showed high efficacy
against the trial endpoint of symptomatic COVID after vaccination.
```

Overclaim debunked:

```text
BNT162b2 prevents all infection or transmission.
```

CAPAS verdict:

```text
REWRITE
```

Why:

The encoded endpoint is `symptomatic_covid_after_second_dose`, with `8` vaccine
cases versus `162` placebo cases and `95%` efficacy for that endpoint. That
does not license sterilizing immunity, all infection prevention, or transmission
blocking.

What evidence would be needed to upgrade:

```text
endpoint includes asymptomatic infection and/or transmission
transmission_or_asymptomatic_evidence is present
```

## Debunk 3: GW150914 Gives a Precise Black-Hole Merger Population Rate

Source:

- LIGO/Virgo Collaboration, "Observation of Gravitational Waves from a Binary
  Black Hole Merger", PRL / arXiv: https://arxiv.org/abs/1602.03837

Strong claim licensed:

```text
GW150914 is a gravitational-wave detection supported by two detectors,
matched-filter SNR, false-alarm controls, and noise checks.
```

Overclaim debunked:

```text
GW150914 alone gives a precise black-hole merger population rate.
```

CAPAS verdict:

```text
REWRITE
```

Why:

The trace records a strong detection, but the population-rate interval is
`[2, 600]`, which is broad. A single event licenses detection/source claims, not
a precise population-rate claim.

What evidence would be needed to upgrade:

```text
larger event population
narrow population_rate_credible_interval
selection effects modeled over the observed population
```

## Debunk 4: AlphaFold Solves Full Protein Folding

Source:

- Jumper et al., "Highly accurate protein structure prediction with AlphaFold",
  Nature: https://www.nature.com/articles/s41586-021-03819-2

Strong claim licensed:

```text
AlphaFold achieved near-experimental accuracy for many targets in the CASP14
blind structure-prediction benchmark.
```

Overclaim debunked:

```text
AlphaFold solved full protein folding.
```

CAPAS verdict:

```text
REWRITE
```

Why:

The trace is scoped to `CASP14`, `blind_benchmark = true`, and
`single_chain_structure_prediction_many_targets`. That licenses structure
prediction accuracy in the benchmark scope. It does not license folding
mechanism, dynamics, disorder, complexes, every cellular context, or universal
protein behavior.

What evidence would be needed to upgrade:

```text
mechanistic_folding_evidence
all_contexts_validation
dynamic/disordered/complex targets validated under declared tolerances
```

## Debunk 5: DART Solves Planetary Defense

Source:

- Thomas et al., "Orbital period change of Dimorphos due to the DART kinetic
  impact", Nature: https://www.nature.com/articles/s41586-023-05805-2
- arXiv: https://arxiv.org/abs/2303.02077

Strong claim licensed:

```text
DART changed Dimorphos' orbital period in one controlled kinetic-impact
experiment, with pre/post measurements and independent measurement agreement.
```

Overclaim debunked:

```text
DART solves planetary defense.
```

CAPAS verdict:

```text
REWRITE
```

Why:

The trace records one controlled binary-asteroid kinetic-impact case with an
orbital-period change of about `-33` minutes and uncertainty about `1` minute.
That licenses the specific deflection result. It does not license all asteroid
classes, all warning times, all compositions, all impact geometries, or a
complete planetary-defense system.

What evidence would be needed to upgrade:

```text
multiple_target_classes
hazardous_asteroid_generalization
mission-design constraints across warning times/compositions/geometries
deployment and detection pipeline evidence
```

## Cross-Domain Result

The debunk pattern is stable across five domains:

```text
strong evidence -> exact falsifiable claim accepted
same evidence -> broader story claim rewritten
```

This is the CAPAS product behavior:

- do not debunk the paper
- debunk the inflation around the paper
- preserve the strong claim
- expose the missing evidence for the stronger claim

