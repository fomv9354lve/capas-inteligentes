# CAPAS capability matrix (re-derived by exercising each gate)

**26 live gates** across 10 domains; 2 capabilities deliberately EXCLUDED as diagnostics (model assumptions).

| domain | capability | class | exact | demo verdict | catches |
|---|---|---|---|---|---|
| quantum | coherence bound T2<=2*T1 | consistency-invariant | ✅ | `FLAG_INCONSISTENT` | active TLS / hidden CPMG passed off as a clean qubit |
| quantum | thermal P01>=P10 | consistency-invariant | ✅ | `FLAG_UNPHYSICAL` | negative thermal population (fabricated/inverted readout row) |
| statistics | GRIM mean reachability | consistency-invariant | ✅ | `FLAG` | fabricated/typo'd reported means in survey/clinical data |
| finance | accounting identity A=L+E | consistency-invariant | ✅ | `FLAG` | books that do not close |
| universal | probability bounds 0<=p<=1 | consistency-invariant | ✅ | `FLAG` | out-of-range probabilities / unnormalized distributions |
| quantum | pure dephasing Gamma_phi=1/T2-1/2T1 | derived-quantity | ✅ | `ADMISSIBLE` | re-derives unpublished dephasing rate; classifies dephasing- vs T1-limited |
| quantum | gate-error coherence floor t_g/3T1 | derived-quantity | ✅ | `FLAG_TOO_CLEAN` | a gate error cleaner than relaxation physically allows (fabricated fidelity) |
| quantum | residual ZZ coupling | exact-published | ✅ | `FLAG_HIGH_ZZ` | tunable coupler not nulling ZZ (always-on idle entanglement) |
| universal | conservation sum(parts)=total | consistency-invariant | ✅ | `FLAG` | declared components that do not sum to the declared whole |
| chemistry | stoichiometric atom balance | consistency-invariant | ✅ | `FLAG` | an unbalanced reaction (atoms not conserved reactants->products) |
| physics | dimensional homogeneity | consistency-invariant | ✅ | `FLAG` | an equation whose two sides have different physical dimensions |
| physics | physical bounds (eta<=1, v<=c, T>=0) | consistency-invariant | ✅ | `FLAG` | over-unity efficiency, faster-than-light, sub-absolute-zero, |r|>1 |
| mathematics | claimed root satisfies the equation | derived-quantity | ✅ | `FLAG` | a declared solution that does not satisfy its own equation |
| mathematics | linear system Ax=b solution check | derived-quantity | ✅ | `FLAG` | a declared solution vector that does not satisfy the system |
| mathematics | integer divisibility / gcd-lcm | consistency-invariant | ✅ | `FLAG` | false divisibility / gcd-lcm / quotient-remainder claims |
| chemistry | charge balance in reaction | consistency-invariant | ✅ | `FLAG` | a reaction that conserves atoms but not net charge |
| chemistry | oxidation states sum to charge | consistency-invariant | ✅ | `FLAG` | declared oxidation states inconsistent with the species charge |
| chemistry | mole/mass/amount n=m/M | derived-quantity | ✅ | `FLAG` | an inconsistent mole / mass / molar-mass trio |
| epidemiology | 2x2 metric identities (Se/Sp/PPV/...) | derived-quantity | ✅ | `FLAG` | a claimed sensitivity/specificity/PPV that the 2x2 cells do not support |
| epidemiology | Bayes PPV vs base rate | derived-quantity | ✅ | `FLAG` | the base-rate fallacy: high-sensitivity test claimed to imply high PPV for a rare disease |
| epidemiology | RR/OR/RD from 2x2 | derived-quantity | ✅ | `FLAG` | a claimed risk/odds ratio inconsistent with the cohort table |
| epidemiology | vaccine efficacy VE=1-RR, VE<=1 | consistency-invariant | ✅ | `FLAG` | a vaccine efficacy above 1 or inconsistent with the arm attack rates |
| epidemiology | count containment (num<=den) | consistency-invariant | ✅ | `FLAG` | a numerator exceeding its denominator (deaths>cases, etc.) |
| engineering | Ohm's law V=IR, P=VI | consistency-invariant | ✅ | `FLAG` | declared electrical quantities that violate V=IR or P=VI |
| biology | Lincoln-Petersen N=M*C/R | derived-quantity | ✅ | `FLAG` | a mark-recapture population estimate inconsistent with the counts |
| biology | Hardy-Weinberg internal consistency | consistency-invariant | ✅ | `FLAG` | genotype frequencies that do not sum to 1 / inconsistent allele freqs |

**Excluded as diagnostics (the honesty line — not gates):**
- ZZ from CZ/RZZ ratio — EXCLUDED: ±2x linear-model estimate; the published exact ZZ replaces it (was 24x off)
- loss tangent tan_d=1/(2pi f T1) — EXCLUDED: needs qubit frequency (withheld on open plan, verified live)
