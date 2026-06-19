# Global SotA / Market / Independent Research Audit

Status: hostile positioning audit after public `v0.1.1`.

Purpose: locate CAPAS against current research, market products, and independent
research communities without claiming uniqueness in occupied territory.

## Executive Verdict

CAPAS should not position itself as:

- a provenance standard,
- a workflow engine,
- a simulator router,
- a scientific-agent benchmark,
- a generic fact checker,
- a broad hallucination detector,
- a VVUQ methodology,
- a replacement for RO-Crate/PROV, QMB100/PhysVEC, SciAgentGym, AiiDA, OpenKIM,
  Workflow Run RO-Crate, or market ELN/LIMS/provenance systems.

The defensible position is narrower:

> CAPAS is an evidence-typed claim gate over scientific-computation traces. It
> packages or reads provenance-aligned traces and decides what claim the evidence
> licenses: ACCEPT, REWRITE, REJECT, or HOLD. Its distinctive fields are
> physical evidence level, witness independence, explicit failed/rejected/no
> evidence status, and claim-scope rewriting.

The surviving gap is not "trace everything." It is:

> make physical-evidence strength and witness independence first-class enough
> that a downstream claim can be weakened, rejected, or held instead of being
> treated as a binary verified/not-verified result.

## Functional Map

| Function | Occupied By | CAPAS Verdict |
|---|---|---|
| Provenance packaging | PROV, RO-Crate, Workflow Run RO-Crate, Taverna/Kepler lineage | Taken. CAPAS must align, not compete. |
| Workflow execution provenance | Workflow Run RO-Crate, AiiDA, Materials Cloud, Whole Tale, RRP | Taken. CAPAS can consume/export, not replace. |
| Scientific-agent benchmarks | SciAgentGym/SciAgentBench, LABBench2, QMB100/PhysVEC | Taken. CAPAS can wrap or annotate outputs. |
| Quantum simulator routing | Maestro, TensorCircuit-NG, QFw-like frameworks | Taken. CAPAS should not claim routing novelty. |
| Scientific VVUQ | Oberkampf/Trucano tradition, VECMAtk, OpenKIM UQ | Taken as methodology. CAPAS can encode evidence into traces. |
| Fact checking / claim-citation verification | ClaimCheck, Veracity, DeepSciVerify, Logically-like market | Taken for textual claims. CAPAS is not a web fact checker. |
| Content provenance / signing | C2PA, Content Credentials, SynthID, Traxia-like frameworks | Taken for origin/integrity. CAPAS targets claim licensing from scientific evidence. |
| Physical-evidence typed claim gate | Partially adjacent, no exact dominant incumbent found | CAPAS surviving position. |

## Research SotA

### QMB100 / PhysVEC

Source: `https://arxiv.org/abs/2604.00149`

QMB100/PhysVEC is the closest research neighbor. It targets verifiable,
self-correcting AI physicists for quantum many-body simulations. It includes a
programming verifier and scientific verifier and provides human-auditable
evidence at stages of the process.

What it occupies:

- AI-driven quantum many-body verification,
- scientific verifier loops,
- task-level benchmark outputs,
- physical assertions based on limiting cases, symmetries, and analytical tests.

CAPAS gap, if it survives code/artifact review:

- portable claim-decision object,
- explicit producer-vs-witness independence,
- explicit failed/rejected/no-evidence status,
- rewrite/hold as first-class outcomes,
- path-vs-result packaging.

Claim discipline:

CAPAS should not say QMB100 lacks scientific verification. It should ask whether
QMB100/PhysVEC evidence should be exported as a portable evidence object with
claim decisions and witness independence.

### SciAgentGym / SciAgentBench

Source: `https://arxiv.org/abs/2602.12984`

SciAgentGym provides a scalable environment with 1,780 scientific tools across
natural science disciplines and a tiered benchmark for scientific tool-use.

What it occupies:

- large scientific-agent tool-use environment,
- benchmark harness,
- multi-step tool workflows,
- synthetic/structured training trajectories.

CAPAS gap:

- not another agent benchmark,
- not tool orchestration,
- possible annotation layer over outputs when physical evidence and claim scope
  need typed representation.

### Workflow Run RO-Crate

Source: `https://arxiv.org/abs/2312.07852`

Workflow Run RO-Crate is the direct provenance sibling. It packages workflow-run
provenance using RO-Crate/Schema.org and aligns with W3C PROV. It is community
supported and implemented in multiple workflow systems.

What it occupies:

- interoperable workflow-run packaging,
- workflow plan/execution provenance,
- inputs, outputs, code, environment, run artifacts.

CAPAS gap:

- domain evidence profile over the workflow object,
- claim licensing over physical evidence,
- explicit status for failed/rejected/no-evidence traces.

Required stance:

CAPAS should become compatible with Workflow Run RO-Crate rather than inventing
a competing crate dialect.

### AiiDA / Materials Cloud

Sources:

- `https://arxiv.org/abs/1504.01163`
- `https://arxiv.org/abs/2003.12510`

AiiDA tracks provenance of computational science workflows as directed acyclic
graphs and supports automation, data preservation, sharing, and reproducibility.
Materials Cloud uses AiiDA to share data and provenance graphs for
computational materials science.

What it occupies:

- serious computational-science provenance,
- workflow automation and storage,
- reproducible materials pipelines.

CAPAS gap:

- not a workflow database,
- not high-throughput automation,
- possible claim gate for selected evidence outputs.

### OpenKIM / VVUQ / VECMAtk

Sources:

- `https://en.wikipedia.org/wiki/Open_Knowledgebase_of_Interatomic_Models`
- `https://arxiv.org/abs/2206.00578`
- `https://arxiv.org/abs/2010.03923`

OpenKIM is mature cyberinfrastructure for interatomic potentials, validation
tests, metadata, DOIs, reproducibility, and UQ. VECMAtk and broader VVUQ
infrastructure already address verification, validation, sensitivity analysis,
and uncertainty quantification.

What they occupy:

- validation methodology,
- uncertainty quantification,
- domain repositories,
- reproducible simulation infrastructure.

CAPAS gap:

- encode evidence strength and claim scope into a portable claim-decision object,
  especially outside OpenKIM's classical interatomic-potential domain.

### Maestro / TensorCircuit-NG / Quantum Simulation Platforms

Sources:

- `https://arxiv.org/abs/2512.04216`
- `https://arxiv.org/abs/2602.14167`

Maestro provides unified quantum circuit simulation with automatic backend
selection and predictive runtime modeling. TensorCircuit-NG provides a
tensor-native quantum platform over ML backends with scalable simulation and
differentiable workflows.

What they occupy:

- simulation backend integration,
- runtime/backend prediction,
- quantum simulation performance,
- scalable circuit/tensor execution.

CAPAS gap:

- not speed,
- not simulator selection,
- possible evidence/claim layer around outputs from these systems.

### Scientific Claim Verification / Fact Checking

Sources:

- DeepSciVerify: `https://arxiv.org/abs/2605.27710`
- ClaimCheck: `https://arxiv.org/abs/2510.01226`
- Veracity: `https://arxiv.org/abs/2506.15794`
- Traxia: `https://arxiv.org/abs/2606.08256`

These systems target claim-citation alignment, web-based fact checking,
agent-native scientific publishing, confidence scores, provenance, and
verification layers.

What they occupy:

- textual claim verification,
- citation/evidence alignment,
- public fact checking,
- agent/publisher provenance.

CAPAS gap:

- not a text fact checker,
- not a publishing platform,
- a narrow claim gate for scientific-computation traces where typed physical
  evidence and witness independence can be evaluated.

### C2PA / Content Credentials / SynthID

Sources:

- `https://en.wikipedia.org/wiki/Content_Credentials`
- `https://arxiv.org/abs/2604.24890`

C2PA and related systems address digital content origin, signing, tamper
evidence, metadata, and content authenticity. Recent independent work also
questions whether current C2PA specs achieve all claimed security goals.

What they occupy:

- origin/integrity of media assets,
- content credentials,
- cryptographic metadata.

CAPAS gap:

- not origin of media,
- not broad authenticity,
- claim licensing from scientific evidence. Cryptographic integrity is only one
  lower layer, not physical correctness.

## Market Competitor Map

| Market Segment | Examples | What They Sell | CAPAS Relation |
|---|---|---|---|
| ELN/LIMS/SDMS | Sapio Sciences, Benchling-like platforms | lab workflow management, audit trails, compliance, scientific data management | CAPAS is too small to compete; could be an evidence plug-in concept. |
| Computational reproducibility platforms | Code Ocean-like capsules, Whole Tale, Reproducible Research Platform | executable research objects, environments, re-runability | They package computation; CAPAS decides claim strength from evidence. |
| Materials informatics / provenance | AiiDA, Materials Cloud, OpenKIM | provenance graphs, model repositories, validation data | CAPAS can annotate outputs but is not infrastructure competitor. |
| AI fact-checking / disinformation | ClaimCheck, Veracity, Logically-like vendors | text/web claim checking and misinformation workflows | CAPAS is not a consumer fact-checker. |
| Content provenance | C2PA / Content Credentials ecosystem | media origin and tamper-evidence | CAPAS is about scientific claim evidence, not content origin. |
| Scientific-agent benchmarks | SciAgentGym, LABBench2, QMB100/PhysVEC | evaluation suites and agent tasks | CAPAS can be a trace/evidence layer over task outputs. |

Market implication:

CAPAS is not a standalone large SaaS as currently scoped. Its plausible market
value is as:

1. an open profile/spec extension,
2. a developer tool for scientific-agent benchmark teams,
3. an evidence gate embedded in larger platforms,
4. a review/audit artifact generator for high-stakes scientific claims.

The stronger standalone product direction is hybrid:

```text
extract/retrieve evidence -> semantic alignment -> deterministic CAPAS gate
```

CAPAS currently implements only the deterministic gate. The extraction and
semantic-alignment stages remain future work.

Weak market path:

- selling "another provenance platform."

Stronger market path:

- become the small evidence/claim object that bigger provenance and agent
  systems can adopt.

## Independent Researcher / Community Map

This project should treat the following communities as independent validators,
not as markets to replace:

| Community | Representative Work | Why They Matter |
|---|---|---|
| RO-Crate / Workflow Run RO-Crate | Soiland-Reyes, Leo, Crusoe, Goble ecosystem | determines whether CAPAS is interoperable or a private dialect. |
| QMB100 / PhysVEC | Di Luo group and coauthors | closest AI-physics verification use case. |
| SciAgentGym / SciAgentBench | Fudan/Shanghai scientific-agent benchmark group | closest broad scientific-agent benchmark environment. |
| AiiDA / Materials Cloud | Pizzi, Marzari, materials informatics community | mature computational provenance and reproducibility practice. |
| OpenKIM | Tadmor/Elliott/Karls/Wen ecosystem | mature domain validation + UQ infrastructure in neighboring materials domain. |
| VVUQ | Oberkampf/Trucano lineage, VECMA/VECMAtk community | mature verification/validation/uncertainty methodology. |
| Metamorphic testing | Chen et al., scientific software testing community | property-based oracle problem; CAPAS must not rebrand MT. |
| Claim verification / fact checking | DeepSciVerify, ClaimCheck, Veracity communities | textual claim-verification neighbor; CAPAS is computation-specific. |

## What CAPAS Can Still Claim

Strongest defensible claim:

> CAPAS adds a portable claim-decision layer over scientific-computation traces:
> it records physical evidence strength, witness independence, evidence status,
> and whether the evidence licenses ACCEPT, REWRITE, REJECT, or HOLD.

Even stronger if external users confirm:

> CAPAS fills a practical gap for scientific-agent benchmarks by turning verifier
> output into portable evidence objects that preserve witness independence and
> prevent over-strong claims.

Current claim status:

- Before external feedback: `HOLD` / "plausible gap, not validated."
- If QMB100/PhysVEC or RO-Crate maintainers say useful: `REWRITE` toward
  "validated extension candidate."
- If they say already covered: `REJECT` or narrow to implementation exercise.

## What Must Be Rewritten

| Old Claim | Rewrite |
|---|---|
| CAPAS is a new provenance standard | CAPAS is a profile-style evidence object over existing provenance standards. |
| CAPAS is a universal scientific verification framework | CAPAS is a claim gate for traces that already carry or declare evidence. |
| CAPAS competes with QMB100/PhysVEC | CAPAS may package or audit PhysVEC-like evidence outputs. |
| CAPAS proves broad LLM scientific reasoning | CAPAS can show bounded claim transitions for declared task families. |
| CAPAS is a market platform today | CAPAS is an MVP/developer artifact awaiting practitioner validation. |

## Kill Conditions

CAPAS' surviving gap should be considered closed or substantially weakened if:

1. QMB100/PhysVEC releases artifacts that already encode witness independence,
   evidence status, and claim verdicts.
2. Workflow Run RO-Crate already has a community profile that covers physical
   evidence strength and claim licensing.
3. SciAgentGym or another scientific-agent suite records failed/rejected/no
   evidence states plus claim rewrite decisions as portable evidence objects.
4. External practitioners say the distinction is not useful in their workflows.

## Next External Tests

1. Ask QMB100/PhysVEC whether CAPAS fields help exchange or audit one task
   result.
2. Ask Workflow Run RO-Crate maintainers whether `capas:PhysicalEvidence` should
   be a compatible profile, a property bundle, or not part of RO-Crate.
3. Ask one scientific-agent benchmark builder whether `ACCEPT/REWRITE/REJECT/HOLD`
   is useful compared with their current pass/fail scoring.
4. If two say no, narrow CAPAS to an internal audit tool.
5. If one says yes with a concrete workflow, implement that adapter first.

## Bottom Line

CAPAS is not alone in any component. The only defensible opportunity is the
intersection:

```text
scientific computation trace
+ physical evidence level
+ witness independence
+ failed/rejected/no-evidence status
+ claim decision / rewrite gate
+ RO-Crate/PROV compatibility
```

That intersection is plausible and narrow. It is not yet market-validated.
