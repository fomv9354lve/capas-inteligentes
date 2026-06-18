# US/UK Canonical Falsifiable Claim Gate

Date: 2026-06-17

Purpose: run CAPAS over top-tier US/UK or US/UK-linked scientific claims across
canonical domains, focusing on falsifiable inference and verifiable controls.

This is not a literature review. It is a gate test: for each source, CAPAS
accepts the claim licensed by the evidence and rewrites the stronger overclaim.

## Domains Covered

| Domain | Source | Control / falsification anchor |
|---|---|---|
| Clinical therapeutics | UK RECOVERY dexamethasone trial | randomized usual-care control, 28-day mortality, subgroup interaction |
| Vaccine efficacy | BNT162b2 mRNA vaccine trial | randomized placebo, observer-blind design, symptomatic cases |
| Astrophysics detection | LIGO GW150914 | two detectors, matched filtering, false-alarm rate, noise controls |
| AI structural biology | AlphaFold CASP14 | blind benchmark against withheld experimental structures |
| Planetary defense | NASA DART | controlled impact, pre/post orbital period, independent measurement approaches |

## Source 1: RECOVERY Dexamethasone Trial

Source:

- RECOVERY Collaborative Group, "Dexamethasone in Hospitalized Patients with
  Covid-19", New England Journal of Medicine, 2021.
- PubMed: https://pubmed.ncbi.nlm.nih.gov/32678530/

Extracted evidence:

```text
study_design: randomized_controlled_trial
control_group: usual_care
primary_endpoint: 28_day_mortality
overall_rate_ratio: 0.83
overall_ci: [0.75, 0.93]
primary_endpoint_met: true
subgroups:
  invasive_mechanical_ventilation: benefit, CI excludes null
  oxygen_without_invasive_ventilation: benefit, CI excludes null
  no_respiratory_support: no benefit, CI includes null
```

Gate outcomes:

| Claim | Verdict | Reason |
|---|---|---|
| `rct_primary_endpoint_supported` | ACCEPT | Randomized trial, usual-care control, primary endpoint, CI excludes null. |
| `treatment_benefits_all_subgroups` | REWRITE | The no-respiratory-support subgroup does not show licensed benefit. |

The useful CAPAS behavior is not to deny the RCT. It accepts the mortality
claim and blocks the overclaim that the treatment benefits every subgroup.

## Source 2: BNT162b2 mRNA Vaccine Trial

Source:

- Polack et al., "Safety and Efficacy of the BNT162b2 mRNA Covid-19 Vaccine",
  New England Journal of Medicine, 2020.
- DOI endpoint: https://www.nejm.org/doi/full/10.1056/NEJMoa2034577
- Public summary cross-check: https://www.theguardian.com/world/2020/nov/18/pfizer-covid-19-vaccine-95-effective-and-safe-further-tests-show

Extracted evidence:

```text
study_design: randomized_placebo_trial
observer_blind: true
endpoint: symptomatic_covid_after_second_dose
vaccine_cases: 8
placebo_cases: 162
vaccine_efficacy_percent: 95.0
```

Gate outcomes:

| Claim | Verdict | Reason |
|---|---|---|
| `vaccine_efficacy_trial_supported` | ACCEPT | Observer-blind placebo trial supports symptomatic-disease efficacy. |
| `vaccine_prevents_all_infection_or_transmission` | REWRITE | Symptomatic endpoint does not license sterilizing immunity or transmission blocking. |

CAPAS separates the strong trial result from a common broader public overclaim.

## Source 3: LIGO GW150914

Source:

- LIGO/Virgo Collaboration, "Observation of Gravitational Waves from a Binary
  Black Hole Merger", Physical Review Letters / arXiv, 2016.
- arXiv: https://arxiv.org/abs/1602.03837
- Search paper: https://arxiv.org/abs/1602.03839
- Calibration/noise controls: https://arxiv.org/abs/1602.03845 and
  https://arxiv.org/abs/1602.03844

Extracted evidence:

```text
detectors: 2
matched_filter_snr: 24
false_alarm_years: 203000
noise_controls_pass: true
population_rate_credible_interval: [2, 600]
```

Gate outcomes:

| Claim | Verdict | Reason |
|---|---|---|
| `gravitational_wave_detection_supported` | ACCEPT | Two-detector matched-filter detection clears false-alarm and noise-control thresholds. |
| `gravitational_wave_population_rate_precise` | REWRITE | Single-event evidence licenses detection/source claims, not a precise population rate. |

CAPAS accepts the discovery and blocks an inference that outruns a single event.

## Source 4: AlphaFold CASP14

Source:

- Jumper et al., "Highly accurate protein structure prediction with AlphaFold",
  Nature, 2021.
- Nature: https://www.nature.com/articles/s41586-021-03819-2

Extracted evidence:

```text
benchmark: CASP14
blind_benchmark: true
median_backbone_rmsd95_angstrom: 0.96
rmsd95_threshold_angstrom: 1.5
confidence_intervals_reported: true
scope: single_chain_structure_prediction_many_targets
```

Gate outcomes:

| Claim | Verdict | Reason |
|---|---|---|
| `alphafold_casp14_accuracy_supported` | ACCEPT | Blind CASP14 benchmark supports near-experimental structure accuracy for many targets. |
| `alphafold_solves_full_protein_folding` | REWRITE | CASP14 does not license folding mechanism, all contexts, disorder, complexes, or dynamics. |

CAPAS lets the benchmark be strong without letting "accurate structure
prediction" collapse into "solved protein folding."

## Source 5: NASA DART / Dimorphos

Source:

- Thomas et al., "Orbital period change of Dimorphos due to the DART kinetic
  impact", Nature, 2023.
- Nature: https://www.nature.com/articles/s41586-023-05805-2
- arXiv: https://arxiv.org/abs/2303.02077

Extracted evidence:

```text
controlled_impact: true
pre_post_orbit_measured: true
independent_measurement_methods_agree: true
orbital_period_change_minutes: -33.0
orbital_period_change_sigma_minutes: 1.0
```

Gate outcomes:

| Claim | Verdict | Reason |
|---|---|---|
| `dart_orbit_change_supported` | ACCEPT | Controlled impact has pre/post orbit measurements and independent agreement. |
| `dart_solves_planetary_defense` | REWRITE | One binary-asteroid controlled case does not solve planetary defense generally. |

CAPAS accepts the falsifiable experiment and blocks the global deployment
overclaim.

## Cross-Domain Pattern

Across five canonical domains, the gate does the same thing:

```text
top-tier evidence
  -> accept the exact falsifiable claim
  -> rewrite the broader story claim
```

This is the product behavior CAPAS needs:

- It does not debunk strong papers.
- It protects their real claims from being inflated.
- It converts authority into field-specific evidence types.
- It records controls, thresholds, scopes, and overclaim boundaries.

## Implementation

The checks live in:

```text
benchmarks/validate_evidence_claims.py
```

Current validation:

```text
python3 benchmarks/validate_evidence_claims.py
```

passes:

```text
39/39 checks
10 US/UK canonical checks
5 domains
```

## Next Debt

The next version should add one climate/earth-system case and one social-science
replication case. Those domains are harder because the controls are less
single-experiment-like, so they are the right next stress test for CAPAS.

