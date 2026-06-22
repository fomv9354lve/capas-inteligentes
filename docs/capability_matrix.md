# CAPAS capability matrix (re-derived by exercising each gate)

**9 live gates** across 4 domains; 2 capabilities deliberately EXCLUDED as diagnostics (model assumptions).

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

**Excluded as diagnostics (the honesty line — not gates):**
- ZZ from CZ/RZZ ratio — EXCLUDED: ±2x linear-model estimate; the published exact ZZ replaces it (was 24x off)
- loss tangent tan_d=1/(2pi f T1) — EXCLUDED: needs qubit frequency (withheld on open plan, verified live)
