# R1 China Rietveld Real Claim Gate

Date: 2026-06-17

Purpose: test CAPAS on real China-linked AI-for-science/Rietveld sources, using
the evidence gate to separate refinement quality, structure validation, and
workflow/contract scope.

This is not a claim that CAPAS beats the Rietveld agents. It is a claim that
CAPAS can prevent their reported metrics from being overinterpreted.

## Sources Used

### C35: Rongzai Rietveld agent

Source:

- Qingmeng Li et al., "Rongzai agent: A Large Language Model-Based Autonomous
  Assistant for Rietveld Refinement of Neutron Diffraction Data", arXiv:2605.13911.
- URL: https://arxiv.org/abs/2605.13911

Facts extracted:

```text
method: llm_agent_gsas_ii_rietveld_refinement
samples: 5
agent_rwp_wins: 3
rwp_pairs_agent_vs_specialist:
  - 2.88 vs 4.42
  - 5.06 vs 5.40
  - 7.60 vs 9.00
independent_structure_reference: false
held_out_validation: false
```

CAPAS gate outcomes:

| Claim | Verdict | Reason |
|---|---|---|
| `agent_refinement_beats_specialist_rwp` | ACCEPT | The source reports lower Rwp than specialists on `3/5` samples. |
| `rwp_improvement_implies_structure_validated` | REWRITE | Lower Rwp licenses a fit-quality claim, not independent structure validation. |

This is the core R1 behavior. CAPAS does not deny the reported performance. It
accepts the metric claim and blocks the stronger physical claim unless
independent structure validation is present.

### C36: AgentBuild for Rietveld refinement

Source:

- Woong Shin, Craig A. Bridges, Marshall T. McDonnell, Rafael Ferreira da Silva,
  "Fantastic Scientific Agents and How to Build Them: AgentBuild for Rietveld
  Refinement", arXiv:2606.12834.
- URL: https://arxiv.org/abs/2606.12834

Facts extracted:

```text
scientist_authored_contract: true
rubric_driven_judge: true
frontier_case_status: contract_failure
physical_validation_status: not_established
```

CAPAS gate outcomes:

| Claim | Verdict | Reason |
|---|---|---|
| `scientist_contract_recorded` | ACCEPT | The source records a scientist-authored contract and rubric-driven judge. |
| `contract_failure_not_physical_failure` | ACCEPT | The frontier is framed as workflow/contract failure, not physical invalidity. |

This is a complementary source. AgentBuild already performs an important
judgment-preserving move: it keeps the scientist's authored contract explicit.
CAPAS can integrate that contract as upstream evidence and then type which
scientific claims the resulting trace licenses.

## What This Proves

R1 shows CAPAS can add value without competing with the Rietveld agents:

```text
agent output metric
  -> evidence type
  -> claim requested
  -> accept metric claim / rewrite physical overclaim
```

The useful distinction is:

```text
better fit quality != independently validated crystal structure
```

This is exactly the kind of overclaim a scientific-agent ecosystem can generate:
the metric is real, but the stronger physical interpretation needs stronger
evidence.

## What This Does Not Prove

This does not prove the Rongzai structures are wrong.

This does not prove AgentBuild is insufficient.

This does not prove CAPAS can parse arbitrary Rietveld papers automatically.

It proves a smaller thing: given explicitly extracted Rietveld-agent evidence,
CAPAS can mechanically license a fit-quality claim while refusing to license
independent structure validation.

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
29/29 checks
4 real China/Rietveld checks
```

## Next R1 Debt

The stronger version should inspect the full Rietveld outputs and add fields:

```text
physical_constraints_pass
held_out_validation
independent_structure_reference
uncertainty_on_refined_parameters
fit_residuals_by_sample
```

Only then can CAPAS distinguish:

```text
fit_improved
structure_plausible
structure_validated
```

with more than abstract-level evidence.

