# Regional Research Atlas: China, Cono Sur, and Adversarial SotA Baseline

Date: 2026-06-17

Purpose: collect the 100+ source regional scan requested for CAPAS, focused on
China and Cono Sur, with an adversarial state-of-the-art baseline to prevent
overclaiming.

This is not a novelty claim. It is a source ledger plus a positioning map. The
goal is to identify which functions are already occupied and which narrow
integration remains plausible for CAPAS.

## Method

Search was organized by nodes, not by product names:

1. CAPAS function: trace/provenance, evidence type, scientific computation,
   verification, claim-to-evidence licensing.
2. China node: Chinese and China-linked AI-for-science, scientific agents,
   fact-checking, scientific databases, DeepModeling, chemistry LLMs, and
   Chinese-language infrastructure.
3. Cono Sur node: working papers, proceedings, repositories, regional
   simulation/validation/UQ/workflow material, with emphasis on Argentina,
   Chile, Uruguay, Paraguay, and regional computational mechanics.
4. Adversarial global node: nearest incumbents in fact-checking, provenance,
   scientific workflow, safety cases, VVUQ, BioCompute, RO-Crate, and agent
   tracing.

Chinese-language material was searched and read directly where it mattered. No
extra local Chinese tooling was needed in this pass; the relevant pages and
abstracts were accessible through browser/search and machine-readable metadata.

Raw source count:

```text
China-focused sources: 37
Cono Sur / regional working sources: 35
Global adversarial/SotA baseline sources: 50
Total raw source records: 122
```

Not all 122 are direct competitors. Many are boundary sources: they occupy a
neighboring function, define vocabulary, or show where CAPAS should not claim
novelty.

## Executive Verdict

Do not claim:

- scientific traces
- golden traces
- provenance
- RO-Crate/PROV packaging
- simulation validation
- workflow reproducibility
- general scientific claim verification
- scientific-agent trace logging
- fact-checking for scientific text
- automatic routing or cost prediction

Those functions are occupied.

The surviving CAPAS wedge is narrower:

> CAPAS is a typed evidence gate for scientific computation claims. It packages
> scientific runs as RO-Crate/PROV-compatible traces and rejects or downgrades
> claims that exceed the evidence type attached to the result.

The regional scan strengthens that wedge:

- China is dense in AI-for-science infrastructure, chemistry/materials agents,
  scientific databases, DeepModeling, and Chinese fact-checking. It does not,
  in this scan, visibly package claim-specific scientific evidence types as a
  typed gate over computation traces.
- Cono Sur has a deep grey-literature base in computational mechanics,
  simulation, validation, UQ, workflows, and reproducibility. It looks like an
  excellent proving ground for CAPAS because the material is practical,
  regional, and heterogeneous, but it is not already a typed evidence gate.
- The global baseline confirms the same pattern: evidence, provenance,
  workflow, VVUQ, and claim verification all exist; the gap is the explicit
  typed relation between a scientific claim and the minimum evidence needed to
  license it.

## China Node

China is not empty terrain. It is one of the strongest adjacent regions.

Main occupied functions:

- AI-for-science agents and low-code AI4S platforms.
- Chemistry and materials foundation models.
- Deep potential / DeepModeling infrastructure.
- Chinese scientific fact-checking datasets and systems.
- Scientific databases and recommender/agentic infrastructure.
- Domain-specific agents for crystallography and Rietveld refinement.

CAPAS implication:

China is a competitor region for implementation speed and infrastructure, not a
reason to abandon the claim. The viable CAPAS position is not "we build a better
scientific agent." It is "we type and gate the evidence that scientific agents
are allowed to claim."

### China Source Ledger

| # | Source | Year | Function occupied | CAPAS implication |
|---:|---|---:|---|---|
| C01 | [A Survey on LLM-based Autonomous Agents](https://arxiv.org/abs/2308.11432) | 2023 | agent taxonomy | Do not claim scientific agents as new |
| C02 | [Agent4S](https://arxiv.org/abs/2506.23692) | 2025 | AI4S agent survey | China-linked AI4S agent landscape is active |
| C03 | [AI-for-Science Low-code Platform with Bayesian Adversarial Multi-Agent Framework](https://arxiv.org/abs/2603.03233) | 2026 | low-code AI4S platform | Adjacent to agent orchestration, not evidence typing |
| C04 | [Data Interpreter](https://arxiv.org/abs/2402.18679) | 2024 | data-science agent | Agentic data workflows are occupied |
| C05 | [MetaGPT](https://github.com/geekan/MetaGPT) | 2024 | multi-agent software workflow | General agent orchestration is occupied |
| C06 | [SciInstruct / SciGLM](https://arxiv.org/abs/2401.07950) | 2024 | scientific LLM training | Scientific model/data side is occupied |
| C07 | [THUDM/SciGLM GitHub](https://github.com/THUDM/SciGLM) | 2024 | open scientific LLM repo | Infrastructure, not evidence gate |
| C08 | [Sciverse scientific intelligence database](https://zh.wikipedia.org/wiki/Sciverse%E7%A7%91%E5%AD%A6%E6%99%BA%E8%83%BD%E6%95%B0%E6%8D%AE%E5%BA%93) | 2026 | scientific data platform | Scientific database infrastructure exists |
| C09 | [GeoGPT concerns / DDE](https://www.theguardian.com/technology/article/2024/jun/24/geologists-censorship-bias-chinese-chatbot-geogpt) | 2024 | domain AI governance concern | Shows trust/provenance pressure in China-linked science AI |
| C10 | [ChemDFM](https://arxiv.org/abs/2401.14818) | 2024 | chemistry foundation model | Chemistry AI is occupied |
| C11 | [ChemLLM](https://arxiv.org/abs/2402.06852) | 2024 | chemistry LLM | Chemistry reasoning/modeling is occupied |
| C12 | [ChemDFM-R](https://arxiv.org/abs/2507.21990) | 2025 | chemistry reasoning model | Do not claim chemistry-agent novelty |
| C13 | [ChemVLM](https://arxiv.org/abs/2408.07246) | 2024 | chemistry vision-language model | Multimodal chemistry AI occupied |
| C14 | [Deep Potential](https://arxiv.org/abs/1707.01478) | 2017 | learned interatomic potential | Do not claim learned simulation infrastructure |
| C15 | [DeePMD-kit](https://arxiv.org/abs/1712.03641) | 2017 | molecular dynamics toolkit | Strong Chinese-led simulation infrastructure |
| C16 | [DeePMD-kit v2](https://arxiv.org/abs/2304.09409) | 2023 | production MD toolkit | Mature infrastructure |
| C17 | [DeePMD-kit v3](https://arxiv.org/abs/2502.19161) | 2025 | updated simulation toolkit | Active, modern tooling |
| C18 | [DeepXDE](https://arxiv.org/abs/1907.04502) | 2019 | scientific ML/PINN library | PINN/SciML tooling occupied |
| C19 | [Physics-informed neural networks, Chinese page](https://zh.wikipedia.org/wiki/%E7%89%A9%E7%90%86%E4%BF%A1%E6%81%AF%E7%A5%9E%E7%BB%8F%E7%BD%91%E7%BB%9C) | 2024 | Chinese PINN vocabulary | Chinese-language SciML ecosystem active |
| C20 | [UQ in Scientific Machine Learning](https://arxiv.org/abs/2201.07766) | 2022 | UQ survey | Do not claim UQ itself |
| C21 | [UQ for noisy inputs/outputs in PINNs and neural operators](https://arxiv.org/abs/2311.11262) | 2023 | PINN/neural-operator UQ | UQ methods occupied |
| C22 | [UQ for PINNs with Extended Fiducial Inference](https://arxiv.org/abs/2505.19136) | 2025 | PINN UQ | UQ is active |
| C23 | [Conformal Prediction for UQ in PINNs](https://arxiv.org/abs/2509.13717) | 2025 | conformal UQ | Uncertainty certification adjacent |
| C24 | [CFEVER](https://arxiv.org/abs/2402.13025) | 2024 | Chinese fact verification | Textual claim checking occupied |
| C25 | [CHEF](https://arxiv.org/abs/2206.11863) | 2022 | Chinese fact checking | Chinese fact-checking benchmark occupied |
| C26 | [Language-specific fact-checking in Chinese](https://arxiv.org/abs/2401.15498) | 2024 | Chinese fact checking | Language-specific verification occupied |
| C27 | [FactISR / CHEF-EG / TrendFact](https://arxiv.org/abs/2410.15135) | 2024 | Chinese fact-checking evolution | Not scientific-computation evidence typing |
| C28 | [CIBER scientific claim verification](https://arxiv.org/abs/2503.07937) | 2025 | scientific claim verification | Close text-side neighbor |
| C29 | [Fact checking Chinese overview](https://zh.wikipedia.org/wiki/%E4%BA%8B%E5%AF%A6%E6%9F%A5%E6%A0%B8) | n/a | Chinese fact-checking context | Vocabulary context |
| C30 | [Manus AI agent](https://zh.wikipedia.org/wiki/Manus_%28AI_agent%29) | 2025 | Chinese agent platform | Agent product space occupied |
| C31 | [Generative AI Services Interim Measures](https://zh.wikipedia.org/wiki/%E7%94%9F%E6%88%90%E5%BC%8F%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD%E6%9C%8D%E5%8A%A1%E7%AE%A1%E7%90%86%E6%9A%82%E8%A1%8C%E5%8A%9E%E6%B3%95) | 2023 | regulatory context | Trust/compliance pressure |
| C32 | [China AI industry](https://zh.wikipedia.org/wiki/%E4%B8%AD%E5%9B%BD%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD%E4%BA%A7%E4%B8%9A) | n/a | ecosystem context | Broad China AI capacity |
| C33 | [ScienceDB AI](https://arxiv.org/abs/2601.01118) | 2026 | agentic scientific recommender/data platform | Scientific data infrastructure, not evidence gate |
| C34 | [MinerU](https://arxiv.org/abs/2409.18839) | 2024 | document extraction for science | Useful ingestion layer, not claim gate |
| C35 | [Rongzai: agent for Rietveld refinement](https://arxiv.org/abs/2605.13911) | 2026 | scientific domain agent | Strong China-linked target for CAPAS evidence typing |
| C36 | [AgentBuild for Rietveld refinement](https://arxiv.org/abs/2606.12834) | 2026 | agent-building for scientific refinement | Direct agentic science neighbor |
| C37 | [C-Eval](https://arxiv.org/abs/2305.08322) | 2023 | Chinese evaluation benchmark | Evaluation culture occupied; not physical evidence typing |

## Cono Sur Node

Cono Sur is not dense in LLM-agent evidence tooling, but it is rich in applied
scientific simulation, validation, workflows, and reproducibility. This matters:
CAPAS does not need a shiny benchmark to be useful. It needs heterogeneous
scientific claims whose evidence strength can be typed honestly.

Main occupied functions:

- computational mechanics simulation
- regional validation/verification practice
- CFD, hydrology, biomechanics, industrial thermal processes
- workflow runtime prediction
- reproducibility-oriented scientific tooling
- UQ in biomedical and applied models

CAPAS implication:

Cono Sur is a strong corpus source for stress-testing the evidence type system.
The likely contribution is not a new solver. It is a Spanish/Latin-American
evidence-typing layer over practical scientific simulation claims that are
currently scattered across proceedings, repositories, and local workflows.

### Cono Sur Source Ledger

| # | Source | Year | Region/institution | CAPAS implication |
|---:|---|---:|---|---|
| S01 | [Validacion de Modelos en Mecanica Computacional](https://cimec.org.ar/ojs/index.php/mc/article/view/1854) | 2001 | AMCA/CIMEC Argentina | Direct regional validation vocabulary |
| S02 | [Simulacion Numerica de la Circulacion y Frentes Termicos en los Golfos Norpatagonicos](https://cimec.org.ar/ojs/index.php/mc/article/view/1379) | 2007 | AMCA/CIMEC | Regional physical simulation claim |
| S03 | [Simulacion Computacional del Resalto Hidraulico](https://cimec.org.ar/ojs/index.php/mc/article/view/2826) | 2009 | AMCA/CIMEC | CFD/hydraulics validation target |
| S04 | [Accion del Viento Sobre Cubiertas Abovedadas Aisladas](https://cimec.org.ar/ojs/index.php/mc/article/view/373) | 2004 | AMCA/CIMEC | Structural CFD claim |
| S05 | [Sistema Computacional para Interaccion de Defectos Estructurales](https://cimec.org.ar/ojs/index.php/mc/article/view/1760) | 1999 | AMCA/CIMEC | Scientific software claim |
| S06 | [Formulacion Matematica Orientada a Objetos para Simulacion Continua](https://cimec.org.ar/ojs/index.php/mc/article/view/207) | 2005 | AMCA/CIMEC | Formal modeling/workflow vocabulary |
| S07 | [Automatizando Modelado y Simulacion con Bond Graphs](https://cimec.org.ar/ojs/index.php/mc/article/view/1646) | 2008 | AMCA/CIMEC | Automated modeling node |
| S08 | [Simulacion de Hormigones de Alta Resistencia](https://cimec.org.ar/ojs/index.php/mc/article/view/5103) | 2016 | AMCA/CIMEC | Materials model claim |
| S09 | [Simulacion numerica de la biomecanica del hombro](https://cimec.org.ar/ojs/index.php/mc/article/view/1021) | 2002 | AMCA/CIMEC | Bio-physical model claim |
| S10 | [Congelacion de Cangrejos Patagonicos](https://cimec.org.ar/ojs/index.php/mc/article/view/4182) | 2012 | AMCA/CIMEC | Heat-transfer applied model |
| S11 | [Pasteurizacion artesanal de leche](https://cimec.org.ar/ojs/index.php/mc/article/view/4921) | 2014 | AMCA/CIMEC | Thermal process model |
| S12 | [Viento sobre una cubierta abovedada](https://cimec.org.ar/ojs/index.php/mc/article/view/98) | 2005 | AMCA/CIMEC | CFD/structure repeat case |
| S13 | [Crecimiento de Microorganismos con Monte Carlo](https://cimec.org.ar/ojs/index.php/mc/article/view/614) | 2007 | AMCA/CIMEC | Probabilistic evidence case |
| S14 | [Microbalanza de Cristal de Cuarzo](https://cimec.org.ar/ojs/index.php/mc/article/view/2866) | 2009 | AMCA/CIMEC | Instrument simulation claim |
| S15 | [Sonda de Langmuir Cilindrica](https://cimec.org.ar/ojs/index.php/mc/article/view/5221) | 2016 | AMCA/CIMEC | Plasma/instrumentation simulation |
| S16 | [Solidificacion de Fundicion Ductil](https://cimec.org.ar/ojs/index.php/mc/article/view/1049) | 2002 | AMCA/CIMEC | Materials process simulation |
| S17 | [Modelo Hidrologico Distribuido](https://cimec.org.ar/ojs/index.php/mc/article/view/4026) | 2011 | AMCA/CIMEC | Hydrology workflow/model claim |
| S18 | [Ensayos mecanicos en mampuestos regionales de Misiones](http://hdl.handle.net/11336/66929) | 2014 | CONICET | Simulation compared with experiments |
| S19 | [Dispersion de particulas solidas en la atmosfera](http://hdl.handle.net/11336/18952) | 2014 | CONICET | Coupled atmospheric model |
| S20 | [Eyeccion de spray liquido para herbicidas](http://sedici.unlp.edu.ar/handle/10915/96177) | 2017 | UNLP/SEDICI | Applied simulation + experimental potential |
| S21 | [Estructuras porosas para regeneracion osea con ML y simulacion](https://doi.org/10.70567/mc.v41i17.90) | 2025 | Mecanica Computacional | ML + simulation, close evidence target |
| S22 | [Modos naturales del Motor Cohete Tronador II](https://openalex.org/W2956296898) | 2006 | Argentina | Aerospace modal verification target |
| S23 | [Operacion de un ciclon de alta eficiencia](https://openalex.org/W2885556831) | 2013 | Argentina | Industrial CFD claim |
| S24 | [Ensemble Learning of Run-Time Prediction Models for Scientific Workflows](https://doi.org/10.1007/978-3-662-45483-1_7) | 2014 | UNCuyo | Workflow runtime prediction occupied |
| S25 | [Running-time Prediction for Gene-Expression Workflows](https://doi.org/10.1109/tla.2015.7350063) | 2015 | UNCuyo | Scientific workflow modeling |
| S26 | [DES Science Portal: Computing photometric redshifts](https://doi.org/10.1016/j.ascom.2018.08.008) | 2018 | DES collaboration | Scientific portal/pipeline context |
| S27 | [Galaxy, Docker and Jupyter workflows](https://doi.org/10.1101/075457) | 2016 | regional coauthorship | Reproducible workflow tooling occupied |
| S28 | [Jupyter and Galaxy](https://doi.org/10.1371/journal.pcbi.1005425) | 2017 | regional coauthorship | Workflow reproducibility occupied |
| S29 | [Open Science Drone Toolkit, Zenodo](https://doi.org/10.5281/zenodo.7093644) | 2022 | regional-indexed | Open instrumentation/data capture |
| S30 | [Open Science Drone Toolkit, PLOS ONE](https://doi.org/10.1371/journal.pone.0284184) | 2023 | regional-indexed | Instrument workflow reproducibility |
| S31 | [IPOL Demo System](https://doi.org/10.1007/978-3-319-56414-2_1) | 2017 | Uruguay-indexed | Executable reproducible research |
| S32 | [UQ in Patient-Specific Arterial Network Model](https://doi.org/10.1115/1.4035918) | 2017 | Uruguay-indexed | Explicit UQ close neighbor |
| S33 | [Pagoo reproducible bacterial pangenomes](https://doi.org/10.1101/2020.07.29.226951) | 2020 | Uruguay-indexed | Reproducible computational biology |
| S34 | [Bayesian Optimization for Ypacarai Lake Monitoring](https://doi.org/10.1109/access.2021.3050934) | 2021 | Paraguay | Autonomous scientific data collection |
| S35 | [Cluster-based LSTM Dengue Forecast](https://doi.org/10.19153/cleiej.26.1.4) | 2023 | Paraguay/CLEI | Regional ML forecast claim |

## Global Adversarial SotA Baseline

This node prevents the regional scan from exaggerating novelty. The global
baseline shows that most CAPAS ingredients are already mature elsewhere.

Main occupied functions:

- fact verification and scientific claim verification
- RAG provenance and agent traces
- PROV, RO-Crate, Workflow Run RO-Crate
- BioCompute and reproducibility packaging
- VVUQ, safety cases, assurance arguments
- scientific workflows and workflow provenance
- units, type systems, and model reliability

CAPAS implication:

The only defensible claim is an integrator claim: scientific results should be
typed by the evidence they carry, and downstream claims should be rejected if
they demand stronger evidence than the trace provides.

### Global Source Ledger

| # | Source | Year | Function occupied | CAPAS implication |
|---:|---|---:|---|---|
| G01 | [FEVER](https://arxiv.org/abs/1803.05355) | 2018 | fact verification | General claim verification occupied |
| G02 | [SciFact](https://arxiv.org/abs/2004.14974) | 2020 | scientific claim verification | Scientific text verification occupied |
| G03 | [MultiVerS](https://arxiv.org/abs/2112.01640) | 2021 | full-document scientific verification | Text-side scientific evidence occupied |
| G04 | [Evidence Inference](https://arxiv.org/abs/1904.01606) | 2019 | clinical evidence inference | Claim/evidence extraction occupied |
| G05 | [PubMedQA](https://arxiv.org/abs/1909.06146) | 2019 | biomedical QA | Biomedical answer verification occupied |
| G06 | [HealthFC](https://arxiv.org/abs/2309.08503) | 2023 | health fact checking | Health claims occupied |
| G07 | [SciClaimHunt](https://arxiv.org/abs/2502.10003) | 2025 | scientific claim detection | Claim detection occupied |
| G08 | [MuSciClaims](https://arxiv.org/abs/2506.04585) | 2025 | multi-source scientific claims | Scientific claim benchmark occupied |
| G09 | [SciClaimEval](https://arxiv.org/abs/2602.07621) | 2026 | scientific claim evaluation | Current benchmark neighbor |
| G10 | [RAGAS](https://arxiv.org/abs/2309.15217) | 2023 | RAG evaluation | RAG faithfulness occupied |
| G11 | [Lightweight RAG provenance fact-checker](https://arxiv.org/abs/2411.01022) | 2024 | RAG provenance | Provenance in RAG occupied |
| G12 | [ProvenanceGuard](https://arxiv.org/abs/2606.18037) | 2026 | provenance guardrails | Close guardrail neighbor |
| G13 | [From Agent Traces to Trust](https://arxiv.org/abs/2606.04990) | 2026 | agent trace trust | Agent trace space occupied |
| G14 | [PROV-AGENT](https://arxiv.org/abs/2508.02866) | 2025 | agent provenance | Agent provenance occupied |
| G15 | [OpenTelemetry GenAI Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/) | 2024 | GenAI telemetry | Telemetry standards occupied |
| G16 | [NeMo Guardrails](https://arxiv.org/abs/2310.10501) | 2023 | LLM guardrails | Guardrail framework occupied |
| G17 | [LLM Risks and Guardrails](https://arxiv.org/abs/2406.12934) | 2024 | guardrail survey | Guardrail landscape occupied |
| G18 | [W3C PROV Overview](https://www.w3.org/TR/prov-overview/) | 2013 | provenance standard | Do not claim provenance invention |
| G19 | [Research Object Suite Ontologies](https://arxiv.org/abs/1401.4307) | 2014 | research object modeling | Research packaging occupied |
| G20 | [Packaging Research Artefacts with RO-Crate](https://arxiv.org/abs/2108.06503) | 2022 | RO-Crate | Packaging occupied |
| G21 | [Workflow Run RO-Crate](https://arxiv.org/abs/2312.07852) | 2023 | workflow run provenance | CAPAS should align, not compete |
| G22 | [BioCompute Object / IEEE 2791](https://opensource.ieee.org/2791-object/ieee-2791-schema/) | 2020 | bioinformatics computation packaging | Domain packaging occupied |
| G23 | [BCO + PRIMAD reproducibility](https://arxiv.org/abs/2412.07502) | 2024 | reproducibility framework | Reproducibility packaging occupied |
| G24 | [Nanopublications](https://arxiv.org/abs/1809.06532) | 2018 | atomic assertions | Claim packaging occupied |
| G25 | [Broadening Nanopublications](https://arxiv.org/abs/1303.2446) | 2013 | nanopublication model | Micro-claim packaging occupied |
| G26 | [Trusty URIs](https://arxiv.org/abs/1401.5775) | 2015 | cryptographic reference | Hash-addressed artifacts occupied |
| G27 | [Unified Nanopublication Model](https://arxiv.org/abs/2006.06348) | 2020 | nanopublication integration | Assertion packaging occupied |
| G28 | [ASME V&V 40](https://www.asme.org/codes-standards/find-codes-standards/v-v-40-assessing-credibility-computational-modeling-verification-validation-application-medical-devices) | 2018 | VVUQ standard | Do not invent VVUQ vocabulary |
| G29 | [NASA-STD-7009A](https://standards.nasa.gov/standard/nasa/nasa-std-7009) | 2016 | model credibility | Model credibility occupied |
| G30 | [Assessing Reliability of Complex Models](https://nap.nationalacademies.org/catalog/13395/assessing-the-reliability-of-complex-models-mathematical-and-statistical-foundations) | 2012 | model reliability | Reliability theory occupied |
| G31 | [Verification and Validation in Scientific Computing](https://www.cambridge.org/core/books/verification-and-validation-in-scientific-computing/039BDF820560F31F0D7F5CDAD3E9687B) | 2010 | V&V foundation | Foundational vocabulary occupied |
| G32 | [VECMAtk](https://arxiv.org/abs/2010.03923) | 2020 | VVUQ toolkit | Tooling occupied |
| G33 | [Goal Structuring Notation](https://scsc.uk/SCSC-141B) | 2021 | safety argument structure | Assurance argument format occupied |
| G34 | [AMLAS](https://arxiv.org/abs/2102.01564) | 2021 | ML assurance | ML safety case occupied |
| G35 | [Open Autonomy Safety Case Framework](https://arxiv.org/abs/2404.05444) | 2024 | autonomy safety cases | Assurance cases occupied |
| G36 | [BIG Argument for AI Safety Cases](https://arxiv.org/abs/2503.11705) | 2025 | AI safety arguments | Argument structuring occupied |
| G37 | [Argument Interchange Format](https://www.argumentinterchange.org/) | 2006 | argument representation | Argument graph format occupied |
| G38 | [Toulmin, Uses of Argument](https://www.cambridge.org/core/books/uses-of-argument/26CF801BC12004587B66778297D5567C) | 1958 | argument theory | Claim/evidence logic predates CAPAS |
| G39 | [Argument Reasoning Comprehension](https://arxiv.org/abs/1708.01425) | 2017 | argument benchmark | Argument classification occupied |
| G40 | [F# Units of Measure](https://learn.microsoft.com/en-us/dotnet/fsharp/language-reference/units-of-measure) | 2008 | type checking dimensions | Type-system analogy occupied |
| G41 | [Mars Climate Orbiter Mishap Report](https://llis.nasa.gov/llis_lib/pdf/1009464main1_0641-mr.pdf) | 1999 | unit mismatch failure | Evidence type checks are analogous, not new type theory |
| G42 | [YesWorkflow](https://arxiv.org/abs/1502.02403) | 2015 | lightweight workflow provenance | Workflow annotation occupied |
| G43 | [Common Workflow Language](https://www.commonwl.org/) | 2016 | workflow standard | Execution descriptors occupied |
| G44 | [Pegasus WMS](https://pegasus.isi.edu/) | 2015 | workflow management | Scientific workflow execution occupied |
| G45 | [Galaxy](https://galaxyproject.org/) | 2010 | scientific workflow platform | Workflow reproducibility occupied |
| G46 | [PROV-IO+](https://arxiv.org/abs/2308.00891) | 2023 | workflow/data provenance | Provenance extension occupied |
| G47 | [Workflow Provenance in Scientific ML](https://arxiv.org/abs/2010.00330) | 2020 | scientific ML provenance | Provenance in SciML occupied |
| G48 | [FAIR Guiding Principles](https://doi.org/10.1038/sdata.2016.18) | 2016 | FAIR data | FAIRness occupied |
| G49 | [Inspectable AI for Science](https://arxiv.org/abs/2604.11261) | 2026 | inspectable scientific AI | Close AI-for-science trust neighbor |
| G50 | [Agentic Science Survey](https://arxiv.org/abs/2508.14111) | 2025 | agentic science survey | Agentic science context occupied |

## Dialectical Nodes and What They Teach

### Node 1: "scientific traces"

Verdict: taken.

SciAgentGym, Workflow Run RO-Crate, PROV-AGENT, OpenTelemetry, RO-Crate, Galaxy,
Pegasus, and YesWorkflow all occupy trace/provenance space.

CAPAS translation:

Do not sell traces. Sell typed evidence constraints over traces.

### Node 2: "reference error and validation"

Verdict: taken.

VVUQ, ASME V&V 40, NASA-STD-7009A, SciML-style benchmarks, and regional AMCA
validation work all know how to compare models to reference, experiment, or
uncertainty.

CAPAS translation:

Do not sell validation. Sell a machine-readable gate that says which scientific
claim a validation result licenses.

### Node 3: "AI-for-science agents"

Verdict: taken and accelerating.

China-linked sources are especially dense here: Agent4S, ScienceDB AI, Rietveld
agents, ChemLLM/ChemDFM, SciGLM, Sciverse.

CAPAS translation:

Use agents as producers of claims. CAPAS checks whether the trace evidence
licenses those claims.

### Node 4: "regional working-paper opportunity"

Verdict: open as corpus/application terrain.

Cono Sur does not look like an empty theory space; it looks like a practical
corpus of real scientific simulation claims without a common evidence typing
layer.

CAPAS translation:

The first regional application should not be another quantum toy. It should
select 3-5 Cono Sur simulation papers and encode their central claims into
CAPAS evidence requirements.

### Node 5: "typed evidence gate"

Verdict: surviving wedge.

No source in this ledger clearly implements the following pattern as a first
class artifact:

```text
scientific computation trace
  -> attached evidence type
  -> claim demands required evidence type
  -> gate accepts / downgrades / rejects the claim
```

CAPAS has already implemented a local version of this pattern in
`benchmarks/validate_evidence_claims.py`. The regional scan suggests the next
work is not more abstract positioning; it is applying the gate to real regional
claims.

## Next Falsifiable Regional Experiments

### Experiment R1: China Rietveld Agent Evidence Gate

Input: Rongzai / AgentBuild-style Rietveld refinement claims.

Question:

Can CAPAS reject a claim like "the structure is physically correct" when the
trace only supports "the refinement residual improved"?

Evidence requirements:

- residual metrics
- physical constraints
- independent validation or held-out diffraction evidence
- claim gate distinguishing `fit_improved` from `structure_validated`

Falsation:

If the target sources already encode that distinction as a machine-readable
claim/evidence gate, CAPAS adds little.

### Experiment R2: Cono Sur AMCA Validation Claim Gate

Input: `Validacion de Modelos en Mecanica Computacional` plus 2-3 AMCA/CIMEC
simulation cases with physical/experimental reference.

Question:

Can CAPAS encode claims such as "model validated," "simulation reproduces
experiment," and "parameter sensitivity explored" with distinct evidence
requirements?

Evidence requirements:

- reference type: experiment / benchmark / analytic / numerical reference
- uncertainty or tolerance
- witness independence
- scope of validation

Falsation:

If all claims in the source papers are too informal or lack extractable evidence
metadata, CAPAS must downgrade to a documentation aid rather than a gate.

### Experiment R3: Evidence-Type Claim Matrix

Build a small matrix:

| Claim type | Minimum acceptable evidence |
|---|---|
| `result_reproducible` | provenance + environment + deterministic rerun or equivalent |
| `model_solves_equations` | solver verification / residual / analytic or manufactured solution |
| `model_matches_experiment` | experimental reference + tolerance + definition match |
| `model_validated_for_domain` | multiple validation cases + scope + UQ |
| `agent_improved_fit` | metric improvement only |
| `agent_found_physical_truth` | independent physical validation |

Falsation:

If the matrix cannot reject a plausible overclaim that the raw trace would allow,
it is only documentation, not a gate.

## Positioning Statement After 122 Sources

CAPAS should be described as:

> A typed evidence gate for scientific computation traces. It does not invent
> scientific provenance, validation, or workflow packaging. It adds a
> claim-to-evidence licensing layer that can reject, downgrade, or accept
> scientific claims according to the evidence type actually present in the run
> trace.

Regional angle:

> China shows why the gate is needed: agentic scientific infrastructure is
> accelerating faster than evidence discipline. Cono Sur shows where the gate can
> be tested: practical simulation claims exist in grey literature and regional
> proceedings without a unified machine-readable evidence layer.

## Live Debts

1. Read the closest China Rietveld agent papers in detail and extract their
   claim/evidence vocabulary.
2. Select 3 Cono Sur simulation papers with explicit validation/reference claims.
3. Encode those claims into `benchmarks/validate_evidence_claims.py` as regional
   evidence-type checks.
4. Add a regional source-quality field: `direct_competitor`, `adjacent`,
   `corpus_candidate`, `vocabulary_source`.
5. Do not claim that the regional atlas proves usefulness. Usefulness requires a
   real external reader or adoption path.
