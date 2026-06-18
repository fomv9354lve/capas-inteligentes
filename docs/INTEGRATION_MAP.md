# CAPAS Integration Map

Date: 2026-06-17

Purpose: convert the SotA and regional research into construction material.
This document is deliberately not another "taken/not taken" audit. Every
neighbor must answer:

```text
what it removes from our claims
what it contributes to CAPAS
how CAPAS integrates it
what experiment follows
```

## Current North Star

CAPAS should not be framed as a replacement for provenance, VVUQ, workflow
systems, scientific benchmarks, or agent traces.

CAPAS should be framed as:

> a typed evidence gate for scientific computation traces.

The trace is the substrate. The contribution is the mechanical rule that says:

```text
this evidence type licenses this claim
this weaker evidence type does not license that stronger claim
```

## Integration Principle

Every occupied field becomes useful if it is assigned the right role:

- standards become the container
- VVUQ becomes vocabulary
- workflows become execution substrate
- agents become claim producers
- regional proceedings become corpus
- fact-checking becomes the contrast class
- evidence type checking becomes CAPAS

## Neighbor-to-CAPAS Integration Table

| Neighbor | What it removes | What it gives CAPAS | Integration path | Next experiment |
|---|---|---|---|---|
| PROV / RO-Crate | We did not invent provenance or packaging | Standard artifact model and interoperability | Export CAPAS `PhysicalEvidence` as profile/extension, not custom universe | Keep validating RO-Crates; align future fields with existing terms first |
| Workflow Run RO-Crate | We did not invent workflow-run traces | Execution-run shape, workflow/action vocabulary | Treat CAPAS as evidence profile over Workflow Run Crate | Check each new trace can map to workflow run + CAPAS evidence entity |
| VVUQ / ASME V&V / NASA model credibility | We did not invent verification/validation/credibility | Strong vocabulary: verification, validation, uncertainty, credibility, scope | Encode VVUQ distinctions as evidence requirements and claim gates | Add `model_validated_for_domain` claim with strict required fields |
| SciFact / MultiVerS / SciClaimEval | We did not invent scientific claim verification | Contrast between text evidence and computation-native evidence | Position CAPAS as computation evidence type checker, not literature verifier | Add examples where text claim is fluent but trace evidence rejects it |
| RAG provenance / ProvenanceGuard / agent trace trust | We did not invent source-aware factuality or agent provenance | Claim decomposition and trace trust framing | Use these as upstream claim producers; CAPAS checks computation-native evidence | Feed a produced claim into CAPAS gate and reject overclaim mechanically |
| SciAgentGym / scientific agents | We did not invent golden scientific traces | Agent task traces and failure/recovery vocabulary | CAPAS adds typed physical evidence and claim licensing over agent-produced runs | Compare one SciAgentGym-style trace to CAPAS required evidence fields |
| Metamorphic testing | We did not invent oracle-free testing | Property/invariant testing vocabulary | CAPAS separates `metamorphic_relation` from `absolute_anchor` evidence | Label future invariant cases by anchor mode and claim license |
| Scientific ML / PINN UQ | We did not invent uncertainty quantification | Uncertainty formats and interval evidence | CAPAS records whether uncertainty is enough for a stated claim | Add claim gate: `prediction_within_interval` vs `model_validated` |
| F# units / dimensional analysis | We did not invent type checks | Analogy for mechanical rejection before runtime | Present CAPAS as evidence type checking, not truth oracle | Keep checker rule-based; no LLM judge |
| Nanopublications / argumentation | We did not invent atomic claims or warrants | Claim/warrant/result decomposition | Use claim-level packaging if CAPAS exports atomic evidence claims later | Optional future: CAPAS nanopublication export |
| BioCompute Object | We did not invent domain computation packaging | Example of successful domain-specific profile | CAPAS can be domain profile for physical/scientific evidence | Keep CAPAS as profile, not general replacement |
| OpenTelemetry GenAI | We did not invent telemetry | Runtime trace vocabulary | CAPAS can ingest telemetry but must add evidence semantics | Do not confuse telemetry with evidence |

## China as Construction Material

China is valuable to CAPAS because it produces fast-moving scientific agents and
AI-for-science infrastructure. That makes it a stress test for overclaiming.

### China Integration Table

| Source cluster | What it removes | What it gives CAPAS | Integration path | Next experiment |
|---|---|---|---|---|
| Rongzai / AgentBuild Rietveld refinement | We are not the first scientific agent around refinement | A concrete agent output where fit improvement can be overclaimed as physical structure correctness | CAPAS gates `fit_improved` separately from `structure_validated` | R1: Rietveld evidence gate |
| ScienceDB AI / Sciverse | We are not building the scientific data infrastructure | Data discovery and recommender context | CAPAS can sit after discovery, typing evidence for produced claims | Use data platform output as source metadata in trace |
| SciGLM / ChemLLM / ChemDFM / ChemVLM | We are not building the chemistry/materials foundation model | Claim-producing LLMs in scientific domains | Treat model outputs as claims needing evidence licenses | Create sample chemistry claim and require model-vs-experiment evidence |
| Deep Potential / DeePMD-kit / DeepXDE | We are not inventing simulation tooling | Mature computational backends | CAPAS wraps results from these tools and gates claims about them | Future backend candidate: learned-potential claim gate |
| CHEF / CFEVER / CIBER | We are not inventing Chinese fact-checking | Chinese claim verification vocabulary | CAPAS distinguishes text fact-checking from computation evidence checking | Use as positioning contrast, not implementation target |
| Chinese AI regulation and governance | We are not inventing trust pressure | External reason why trace/evidence discipline matters | Supports motivation, not technical novelty | Do not overuse as technical evidence |

### R1: China Rietveld Evidence Gate

Hypothesis:

```text
An agent can improve a refinement metric without licensing the stronger claim
that the recovered structure is physically validated.
```

Claim types:

| Claim | Minimum evidence |
|---|---|
| `fit_improved` | lower residual / better refinement metric |
| `structure_plausible` | fit improvement + physical constraints satisfied |
| `structure_validated` | held-out diffraction, independent reference, or external validation |

CAPAS adds value if it mechanically rejects:

```text
lower residual => structure validated
```

## Cono Sur as Construction Material

Cono Sur is valuable because it supplies real, practical, non-glamorous
scientific simulation claims in Spanish and regional venues. This is exactly
where an evidence type checker can prove usefulness without needing a top-tier
benchmark.

### Cono Sur Integration Table

| Source cluster | What it removes | What it gives CAPAS | Integration path | Next experiment |
|---|---|---|---|---|
| AMCA/CIMEC validation and simulation proceedings | We did not invent simulation validation | Spanish-language corpus of applied model claims | Encode central claims as evidence requirements | R2: AMCA validation claim gate |
| CONICET simulation + experiment cases | We did not invent experiment comparison | Regional cases with likely measured references | Type `matches_experiment` vs `model_validated` | Pick 2 cases with explicit experimental reference |
| UNCuyo workflow runtime prediction | We did not invent scientific workflow prediction | Runtime/cost evidence vocabulary | Keep routing/cost claims separate from physical correctness | Gate `runtime_predicted` vs `scientific_result_validated` |
| Galaxy/Jupyter/Docker regional workflows | We did not invent reproducible workflow tooling | Reproducibility substrate | CAPAS consumes reproducible workflow traces and adds evidence type | Use as workflow provenance contrast |
| UQ arterial network model | We did not invent UQ | Regional UQ case | Gate claims requiring uncertainty bounds | Add `uq_interval_supports_claim` example |
| Open Science Drone Toolkit / autonomous Ypacarai Lake monitoring | We did not invent open instrumentation | Instrumental data provenance cases | Distinguish data capture integrity from model validity | Gate `data_captured` vs `environmental_claim_supported` |

### R2: Cono Sur AMCA Validation Claim Gate

Hypothesis:

```text
Regional simulation papers contain claims that are stronger than the evidence
metadata they explicitly expose.
```

Claim types:

| Claim | Minimum evidence |
|---|---|
| `simulation_ran` | code/method/provenance |
| `numerical_solution_converged` | mesh/time-step/residual/convergence evidence |
| `matches_experiment` | experimental reference + tolerance + definition match |
| `model_validated_for_case` | match to reference under declared scope |
| `model_validated_for_domain` | multiple cases + UQ/sensitivity + domain scope |

CAPAS adds value if it mechanically downgrades:

```text
one simulation matched one case => model validated for domain
```

## Global Baseline as Construction Material

The global baseline gives CAPAS the right ceiling. It prevents us from claiming
too much, but it also gives the pieces CAPAS should reuse.

### Reusable Vocabulary

| Field | Import from neighbor | CAPAS usage |
|---|---|---|
| `provenance` | PROV/RO-Crate | where the artifact came from |
| `workflow_run` | Workflow Run RO-Crate | what executed |
| `claim` | fact-checking / Toulmin / nanopubs | what is being asserted |
| `evidence_type` | VVUQ + CAPAS corpus | what kind of evidence supports the result |
| `evidence_scope` | VVUQ / formal bounds | where the evidence applies |
| `verification_independence` | SciML/reference concerns | how independent the witness is |
| `evidence_status` | failure/rejection/no-evidence traces | whether evidence succeeded, failed, or is absent |
| `claim_license` | CAPAS type checker | whether the evidence permits the claim |

## Product Translation

The product is not:

```text
another scientific agent
another workflow system
another provenance format
another benchmark corpus
another VVUQ methodology
```

The product is:

```text
a claim/evidence gate that sits on top of scientific traces and says:
  accepted: this evidence licenses this claim
  rewrite: this evidence licenses a weaker claim
  reject: this claim exceeds the evidence
  hold: the evidence type is ambiguous or incomplete
```

This directly connects back to the audit categories already used in CAPAS:

- `accept`
- `rewrite`
- `reject`
- `hold`

## Integration Backlog

### I1: Regional Claim Matrix

Create a machine-readable matrix of regional claim types:

```text
simulation_ran
numerical_solution_converged
matches_experiment
model_validated_for_case
model_validated_for_domain
fit_improved
structure_plausible
structure_validated
runtime_predicted
uq_interval_supports_claim
```

Each claim must list required fields.

### I2: Extend `validate_evidence_claims.py`

Add 6-10 new claim checks drawn from the regional matrix:

- accept weak claim from weak evidence
- reject strong claim from weak evidence
- rewrite strong claim to weaker allowed claim
- hold when evidence is missing or ambiguous

### I3: Build Two Regional Mini-Cases

1. China Rietveld mini-case:
   - residual improved
   - structure validation not proven
   - CAPAS rejects overclaim
2. Cono Sur simulation mini-case:
   - simulation result exists
   - maybe one validation reference exists
   - CAPAS distinguishes case validation from domain validation

### I4: Keep the Atlas Alive

Update `REGIONAL_RESEARCH_CHINA_CONO_SUR_ATLAS.md` only when a source changes
the construction plan. Otherwise, new research should flow into experiments,
not more source accumulation.

## Falsation Conditions

This integration map fails if:

1. Existing systems already implement claim-to-evidence type checking over
   scientific computation traces.
2. Regional papers do not expose enough evidence metadata to type claims even
   manually.
3. CAPAS cannot reject a real overclaim that provenance or a local benchmark
   would otherwise allow.
4. The claim matrix becomes subjective LLM judgment instead of rule-based field
   checking.

If any of these happens, CAPAS should downgrade to a documentation/profile tool,
not an evidence gate.

