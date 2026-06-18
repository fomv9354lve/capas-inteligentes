# Claim Upgrade Roadmap for the 10 Debunks

Date: 2026-06-17

Purpose: use the ten debunked overclaims as forward pressure. Each overclaim is
treated as a failed claim transition, not as a dead end. The question is:

> What extra evidence would close the gap without lying?

This document turns each `REWRITE` or `REJECT` into a measurable upgrade path.
The goal is not to resurrect inflated claims. The goal is to define the next
evidence object that would make a stronger claim defensible.

## Rule

For every debunked claim:

1. Keep the narrow licensed claim.
2. Name the blocker that made the broad claim invalid.
3. Define the evidence that would close that blocker.
4. State the strongest forward claim that would then be allowed.
5. Say what CAPAS could add: a sealed trace of the transition, not a magic
   substitute for missing evidence.

## Upgrade Matrix

| Case | Current Licensed Claim | Blocker | Evidence Needed To Push Forward | Stronger Defensible Claim If Closed | CAPAS Role |
|---|---|---|---|---|---|
| Sycamore | Random-circuit-sampling advantage | Benchmark task is not useful/fault-tolerant computation | Demonstrated error-corrected logical operations plus useful algorithmic workload beating best classical baseline | Fault-tolerant quantum processor demonstrates useful advantage on a defined workload | Seal task definition, classical baseline, logical-error budget, runtime, and verification witness |
| Micius QKD | Trusted-relay satellite QKD demo | Trusted relay is not untrusted quantum internet | Entanglement/repeater-based key distribution without trusted satellite node, across operational network segments | Satellite quantum network supports untrusted or device-independent key distribution over declared topology | Seal trust assumptions, topology, key rate, device assumptions, and attack model |
| GPT-3 | Few-shot NLP benchmark gains | Benchmark success is not reliable general reasoning | Pre-registered reasoning tasks with adversarial controls, calibration, causal robustness, and out-of-distribution evaluation | Model shows reliable reasoning in a declared task family under adversarial controls | Seal task generator, held-out split, local tests, universal anchors, and failure modes |
| CRISPR embryos | Embryo correction research | Editing fraction is not clinical safety | Long-term off-target/on-target safety, mosaicism controls, ethical/regulatory approval, and heritable-risk evidence | Editing protocol meets declared preclinical safety criteria for a bounded indication | Seal edit target, off-target assay, mosaicism, follow-up horizon, and regulatory scope |
| Human Genome Project | High-quality reference sequence | Reference sequence is not disease mechanism or therapy | Variant-to-function maps, causal mechanism evidence, clinical validation, and intervention trials | Specific genetic disease mechanism or therapy is validated for a declared population | Seal variant evidence, functional assay, clinical endpoint, ancestry scope, and therapeutic evidence |
| Higgs | Higgs-like boson consistent with SM | One discovery does not close all physics | Precision coupling measurements plus evidence resolving open questions such as dark matter, neutrino mass, hierarchy, gravity | Higgs sector constrained to declared precision; specific new-physics hypotheses excluded | Seal dataset, channels, uncertainty model, hypothesis space, and exclusion strength |
| Lecanemab | Slower decline in early Alzheimer's | Slowing decline is not cure/reversal/broad-stage efficacy | Durable functional benefit, stage-stratified efficacy, safety-risk net benefit, and reversal or arrest endpoint | Treatment slows or alters disease course in a declared subgroup with quantified risk | Seal population, endpoint, adverse events, subgroup scope, and clinical-meaning threshold |
| Semaglutide SELECT | MACE reduction in defined non-diabetic CVD population | One risk reduction is not solving cardiovascular disease | Mechanism-separated outcomes, broader populations, long-horizon safety, absolute risk, discontinuation effects | GLP-1 therapy reduces cardiovascular risk in specified populations with quantified absolute benefit | Seal population, endpoint, absolute/relative risk, safety, and generalization boundary |
| JWST early galaxy | High-redshift massive galaxy observation | Galaxy-formation pressure is not Big Bang refutation | Replicated spectroscopic sample, mass/systematics controls, model comparison against Lambda-CDM alternatives | Early galaxy population constrains formation models and parameter ranges | Seal redshift, mass inference, lensing/dust/systematics, model comparison, and uncertainty |
| Room-temperature superconductor | No established claim after retraction/no replication | Retraction/no replication prevents claim | Independent replication with zero resistance, Meissner effect, structure characterization, and reproducible synthesis | Material superconducts under declared pressure/temperature conditions with independent replication | Seal sample provenance, synthesis recipe, measurement setup, zero resistance, Meissner evidence, and replication lab |

## What This Adds

The debunk pass said: "this source does not license that broad claim."

This roadmap adds: "this is the exact evidence object that would license a
stronger claim."

That is the product direction for CAPAS:

> CAPAS should not only reject overclaims; it should encode the missing evidence
> boundary and produce a trace when the boundary is crossed.

## Claim Transition Types

The ten cases expose recurring claim-transition failures:

| Transition Failure | Examples | Required Upgrade |
|---|---|---|
| Task benchmark -> useful capability | Sycamore, GPT-3 | Useful workload, adversarial controls, external baseline |
| Demo topology -> deployed infrastructure | Micius QKD | Operational topology, trust model, repeaters/network evidence |
| Research signal -> clinical readiness | CRISPR, lecanemab | Safety, population, endpoint, regulatory/clinical scope |
| Map/reference -> causal mechanism | HGP | Functional validation and intervention evidence |
| Discovery -> theory closure | Higgs, JWST | Hypothesis-space controls and uncertainty model |
| Defined-population trial -> universal health claim | Semaglutide | Generalization boundary and subgroup/long-term evidence |
| Single paper -> established physical phenomenon | Room-temperature superconductor | Independent replication and measurement completeness |

## CAPAS Forward Claim

The next defensible claim to push is:

> CAPAS can represent scientific claim transitions: it records not only the
> evidence attached to a result, but the missing evidence boundary that prevents
> a stronger claim, and the exact evidence needed to cross that boundary.

This is stronger than simple debunking and weaker than pretending the broad
claims are already true.

## Executable Hook

The roadmap is implemented as a `claim_transition_gate` that takes:

- `current_claim`
- `attempted_claim`
- `blocker`
- `required_upgrade_evidence`
- `upgrade_evidence_present`

and returns:

- `ACCEPT` when the upgrade evidence is present,
- `REWRITE` when only the narrow claim is licensed,
- `HOLD` when the blocker is unresolved,
- `REJECT` when the evidence record is retracted, contradictory, or replicated
  negatively.

This would turn the current debunk gate into an upgrade gate.

In the current 10-case pass:

```text
claim transition checks: 10
REWRITE transitions: 9
REJECT transitions: 1
```

No case is upgraded to `ACCEPT` yet, because this sprint records the missing
evidence boundary. A future case should flip to `ACCEPT` only when the declared
upgrade evidence is actually present.
