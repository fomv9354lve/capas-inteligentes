# CAPAS SotA Positioning

This document is intentionally hostile to overclaiming. It distinguishes what
CAPAS must not claim from the narrower integration that remains defensible.

## Claims To Avoid

Do not claim CAPAS invented:

- structured scientific traces
- golden scientific traces
- exportable provenance
- reference-error benchmarking
- workflow provenance
- RO-Crate or PROV packaging
- verification, validation, and uncertainty quantification (VVUQ)
- evidence hierarchy for computational model credibility
- quantum circuit simulation cost prediction
- family-aware simulator threshold/runtime prediction
- metamorphic testing / oracle-free property-based testing

Those areas are already populated by SciMLBenchmarks, SciAgentGym, QMB100/PhysVEC,
PROV, RO-Crate, Taverna/Kepler, ASME V&V/VVUQ, Metamorphic Testing,
Xing et al. 2606.11620, and related scientific workflow, LLM-testing, SciML,
and quantum simulation systems.

## Defensible Claim

CAPAS is a RO-Crate/PROV profile for verifiable physical evidence in scientific
computation. It does not compete with SciMLBenchmarks or SciAgentGym as a trace
or benchmark system, and it does not replace VVUQ methodology. It adds an
explicit VVUQ-style evidence layer over scientific traces:

- `physical_evidence_level`
- `verification_independence`
- `reference_truth`
- `evidenceStatus`
- `abs_error`, `expected`, `value`, `observable`
- explicit handling of success, no-evidence, backend failure, and router rejection

Short formulation:

> CAPAS does not invent scientific traces. CAPAS proposes a physical-evidence
> profile over existing trace/provenance formats, explicitly distinguishing
> physical correctness, witness type, and witness independence.

VVUQ-aware formulation:

> CAPAS is an evidence-typed claim gate over scientific-computation traces. It
> reads or packages provenance-aligned VVUQ-style evidence and decides whether
> that evidence licenses ACCEPT, REWRITE, REJECT, or HOLD.

## Comparison Matrix

| System | Reference error | Structured trace | PROV/RO-Crate | Explicit `physical_evidence_level` | Explicit `verification_independence` | Failed/rejected `evidenceStatus` |
|---|---:|---:|---:|---:|---:|---:|
| SciMLBenchmarks | yes | partial/output-centric | no/unclear | no | partial/reference-method discussion | failures handled in benchmark docs |
| SciAgentGym | yes/verified | yes | not found in paper | not found in paper | not found in paper | yes, error/recovery traces |
| QMB100 / PhysVEC | yes/scientific verifier | yes/research workflow evidence | not found in paper | physical assertions, but no CAPAS field found | not found in paper | verifier/error-correction workflow |
| Xing et al. 2606.11620 | simulation threshold/runtime prediction | no/performance predictor | no | no | no | no |
| Metamorphic Testing / SciML MT | oracle-free property/relation checks | sometimes | not the core contribution | relation validity, not CAPAS field | varies | varies |
| PROV / RO-Crate / TavernaProv | generic provenance | yes | yes | no domain field | no domain field | generic workflow status |
| CAPAS | yes | yes | yes | yes | yes | yes |

## Evidence Notes

### SciMLBenchmarks

SciMLBenchmarks already handles reference solutions, error measurement,
reproducibility context, hardware/software metadata, and failed benchmark cases.
This means CAPAS should not claim novelty for reference-based scientific
benchmarking.

Relevant source:

- https://github.com/SciML/SciMLBenchmarks.jl

Open question for deeper audit:

- Does SciMLBenchmarks export per-result provenance as PROV/RO-Crate?
- Does it attach physical evidence as a first-class typed object, or only report
  numerical error against a reference?

### SciAgentGym

SciAgentGym is close to CAPAS in spirit: it uses structured scientific traces,
tool execution, validation, and golden traces across many scientific tools. This
means CAPAS should not claim novelty for "scientific golden traces" in general.

Relevant source:

- https://arxiv.org/abs/2602.12984
- Local paper-level audit: `docs/SCIAGENTGYM_AUDIT.md`

Open question for deeper audit:

- Do its verified golden traces distinguish analytic, cross-sim, none, failed,
  and rejected evidence states?
- Do they explicitly record witness independence and physical reference truth?
- Do they export each trace as RO-Crate/PROV?

Current paper-level audit result:

- SciAgentGym is close SotA for structured scientific traces and execution-grounded golden traces.
- The paper does not show first-class physical evidence entities, evidence taxonomy, witness independence, reference truth, or RO-Crate/PROV export per trace.
- This is not proof of absence in an unpublished codebase or dataset; it is the current evidence from the public paper.

### QMB100 / PhysVEC

QMB100/PhysVEC is the closest known work in the target domain: quantum many-body
simulation. It provides end-to-end research-level tasks, programming and
scientific verifiers, physical assertion tests, convergence tests, and
human-auditable evidence.

Relevant source:

- https://arxiv.org/abs/2604.00149
- Local paper-level audit: `docs/QMB100_AUDIT.md`

Current paper-level audit result:

- QMB100/PhysVEC occupies quantum-many-body verification/error-correction for AI physicists.
- The paper does not show per-run RO-Crate/PROV packaging with first-class
  physical evidence entities, witness independence, and explicit no-evidence,
  failed, and rejected states.
- CAPAS is best positioned as a packaging/profile layer that could complement
  QMB100/PhysVEC, not as a competing benchmark.

### Xing et al. 2606.11620

Xing et al. are direct SotA for the predictive routing/cost-model side of
quantum circuit simulation. Their model predicts the tensor-network
approximation threshold needed to reach target fidelity and the expected
wall-clock runtime from OpenQASM and execution context.

Relevant source:

- https://arxiv.org/abs/2606.11620
- Local paper-level audit: `docs/XING_2606_11620_AUDIT.md`

Current paper-level audit result:

- Xing et al. occupy family-aware simulator threshold/runtime prediction.
- CAPAS must not claim novelty for OpenQASM-to-cost prediction, algorithm-family
  cost modeling, or replacement of trial-and-error tensor threshold selection.
- The paper does not show per-run RO-Crate/PROV evidence artifacts, physical
  evidence entities, witness independence, reference truth, or failed/rejected
  evidence states.
- CAPAS is therefore complementary only as an evidence/profile layer that can
  wrap predictions and executions, not as a rival predictor.

### Metamorphic Testing

Metamorphic Testing is the parent field for oracle-free property/relation
testing. It already covers scientific software and current LLM/scientific-ML
testing work.

Relevant sources:

- https://en.wikipedia.org/wiki/Metamorphic_testing
- https://eprints.whiterose.ac.uk/id/eprint/172370/
- https://arxiv.org/abs/2603.24774
- https://arxiv.org/abs/2605.23965
- https://arxiv.org/abs/2606.17529
- Local audit: `docs/METAMORPHIC_TESTING_POSITIONING.md`

Current audit result:

- CAPAS must not claim novelty for invariant/property-based testing, seeded
  scientific faults, or the pattern where local tests miss and an
  invariant-like property catches.
- D11's defensible angle is narrower: absolute theory-known physical anchors
  sealed as first-class evidence in RO-Crate/PROV traces, with local-oracle
  outcome, universal-anchor outcome, witness independence, claim scope, and
  no-anchor controls.
- This supports complementarity, not dominance over MT.

### PROV / RO-Crate / TavernaProv

Workflow provenance and research-object packaging already exist. CAPAS should
build on them, not replace them.

Relevant sources:

- RO-Crate paper: https://arxiv.org/abs/2108.06503
- Workflow Run RO-Crate: https://arxiv.org/abs/2312.07852
- Closest-SotA / PCM audit: `docs/PCM_SOTA_AUDIT.md`

### VVUQ

Verification, Validation, and Uncertainty Quantification already provide the
core credibility vocabulary. CAPAS should reuse that vocabulary rather than
inventing a parallel one.

Relevant local audit:

- `docs/VVUQ_QUANTUM_AUDIT.md`

Current audit result:

- VVUQ exists in computational science and has entered quantum many-body work.
- I did not find per-run RO-Crate/PROV VVUQ evidence traces with first-class
  physical evidence, witness independence, and failed/rejected evidence states.
- Therefore CAPAS is positioned as trace packaging for VVUQ-style evidence, not
  as a new VVUQ method.

## CAPAS Coverage Demonstrated Locally

Current CAPAS traces demonstrate the evidence profile over heterogeneous cases:

| Coverage case | Example | Evidence status |
|---|---|---|
| `analytic_success` | Heisenberg dimer, Bell entropy, oscillator, particle in a box | `present` |
| `cross_sim_success` | Bell entropy checked by independent reduced-density eigenspectrum | `present` |
| `no_evidence_success` | Toy variational energy with no witness | `none_declared` |
| `backend_failed` | Intentional failing engine | `not_applicable_failed` |
| `rejected_by_router` | Dense statevector rejected by memory guard | `not_applicable_rejected` |

Generated artifacts:

- `benchmarks/gold_traces/*.json`
- `benchmarks/gold_traces/*.prov.json`
- `benchmarks/ro_crates/*/ro-crate-metadata.json`

## Final Position

CAPAS is not a new provenance standard, not a new benchmark suite, not a new
scientific workflow engine, and not a new quantum simulation cost-prediction
model.

CAPAS is an evidence profile and costurero over existing standards and VVUQ
vocabulary:

> RO-Crate/PROV packaging + sealed route/result trace + VVUQ-style physical
> evidence + explicit witness independence + honest no-evidence/failure/rejection
> states.

That is the defensible integration.

After the PCM / closest-SotA audit, the next non-degradable formulation is:

> CAPAS is a physical-evidence profile layered over RO-Crate/PROV-style
> scientific traces, with explicit reference truth, witness independence,
> evidence status, and robust/marginal correctness semantics.

This should be revised if a public system is found that provides all of those
fields as first-class per-run artifacts over comparable scientific examples.
