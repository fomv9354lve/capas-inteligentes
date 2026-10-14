# World sweep 2026 — Wave 2 (Cabo Verde → Ethiopia)

Date run: 2026-10-14. Agent: wave-2 sweep agent. Brief followed: `BRIEF.md`.

**Coverage note (read first).** Run 1 (2026-10-14): the session-wide WebSearch budget ran out after the 24th query,
mid-China; 8 of 30 countries were searched and 22 marked NOT SEARCHED. Run 2 (same day, resumed): WebSearch answered 3
more queries (Denmark) and refused again; Bing result pages via WebFetch proved non-functional (empty or off-topic even
for exact entity names, 12 attempts), so the remaining countries and the four pending China items were covered through
primary-source APIs that WebFetch can read — OpenAlex (country-filtered works 2024–2026; its search matches full text,
so only title-level on-topic items are cited), the arXiv API, Europe PMC, Zenodo, openstd.samr.gov.cn and institutional
pages. Status now: all 30 countries have an entry; none is NOT SEARCHED. Depth differs: deep dives (Canada, China,
Denmark, Czechia, Estonia, Colombia, Croatia) had 5–12 source calls; small states 1–2 OpenAlex queries. Primary URLs
verified by direct fetch in run 2 include the DeepSeek-R1 HTML, DeepSeek-Prover-V2, Kimina, Master-RM, Kirsch 2607.14137,
the GB/T catalogue (twice), ufsn.dk Code 2026, danish-repro, crorin.hr, etag.ee, Zenodo BEYOND/Uusberg/AIMLS/ARI², and
Europe PMC abstracts (Brodeur, Pottegård, Ropovik, Pejdo, Hailu).

---

### Cabo Verde
- Direct (2026 SOTA): none found.
- Adjacent: none found; the query returned only generic research-integrity material (UK Commons reproducibility report,
  EU TIER2/OSIRIS, US ORI 2025 NOFO) with no Cabo Verde reference.
- Epistemics / gap framing: no national material surfaced.
- Institutions & people: none surfaced (follow-up: search in Portuguese for the national research/higher-education
  ministry).
- Take / Ahead: take: nothing | ahead: n/a.
- Confidence: high that nothing surfaced in one English query; low that nothing exists in Portuguese. | Queries:
  "Cabo Verde research integrity reproducibility science policy 2025".
- **NOTHING FOUND (queries: 1, English only).**

### Cambodia
- Direct (2026 SOTA): none found.
- Adjacent: only national AI-policy documents — "Artificial Intelligence Landscape in Cambodia" (MISTI, 2023)
  https://asianews.network/1st-scholarly-report-on-ai-in-cambodia-made-public/ ; a 2025 "Cambodia AI Readiness
  Assessment Report" and a "National Research Agenda 2025" listed on Open Development Mekong without content
  https://data.opendevelopmentmekong.net/my/library_record/national-research-agenda-2025 . No integrity/reproducibility
  or verification work.
- Epistemics / gap framing: readiness/capacity framing, not evidence-grading.
- Institutions & people: Ministry of Industry, Science, Technology and Innovation (MISTI).
- Take / Ahead: take: nothing | ahead: everything; no verification stance exists to compare against.
- Confidence: medium (one query). | Queries: "Cambodia research integrity metascience reproducibility AI research 2025".
- **NOTHING FOUND (queries: 1).**

### Cameroon
- Direct (2026 SOTA): none found.
- Adjacent: no Cameroon-specific results; closest is a 2025 *Trends in Scholarly Publishing* piece on predatory publishing
  in the Global South (no Cameroon mention in the excerpt) https://tsp.scione.com/cms/fulltext.php?id=137 and a 2025
  systematic review of paper mills 2010–2025 (Kamel & Barghi) https://tsp.scione.com/cms/pdf.php?artid=137 .
- Epistemics / gap framing: not surfaced.
- Institutions & people: none surfaced (follow-up: National Ethics Committee for Human Health Research, CNERSH).
- Take / Ahead: take: nothing | ahead: n/a.
- Confidence: medium (one query). | Queries: "Cameroon research integrity paper mills predatory publishing
  reproducibility 2025".
- **NOTHING FOUND (queries: 1).**

### Canada
- Direct (2026 SOTA): no Canadian system doing deterministic/fail-closed gating of scientific claims was found. Closest
  items are (a) the **NeurIPS 2026 workshop "AI for Science: Verification in the Age of AI Scientists"** (12 Dec 2026,
  organizers Ada Fang, Yuanqi Du, Ana Rivera Him, Anvita Bhagavathula, Emilien Dupont, Priya L. Donti, Marinka Zitnik —
  not Canadian-led, verified by fetch) whose three settings are hypothesis generation, imperfect simulators/surrogate
  verifiers, and cost/uncertainty/safety constraints; accepted papers include "Verify Before You Build: Executable
  Dependency Gates for Agent-Generated Science" and "When Scientific Simulators Disagree: A Falsifiable Audit for
  Surrogate Verification" https://neurips.cc/virtual/2026/workshop/137492 (high); (b) **AutoPyVerifier** (Pezeshkpour &
  Hruschka, arXiv 2604.22937, 24 Apr 2026): frames exactly CAPAS's dichotomy — LLM verifiers "expressive but hard to
  control and prone to error", deterministic executable verifiers "reliable and interpretable but limited" — and learns
  compact (1–6 function) executable Python verifiers, +55 F1 over LLM-written sets
  https://www.emergentmind.com/papers/2604.22937 (medium; affiliation not confirmed, likely Megagon Labs, US). Neither
  is Canadian; no Mila/Vector/Amii claim-verification project surfaced.
- Adjacent: **Tri-Agency Framework: Responsible Conduct of Research** — University Affairs reports a 2026 review/update
  with advice sought on researchers' AI use; the official page still links the 2021 text and says nothing about 2026, AI,
  reproducibility or preregistration (verified by fetch) https://science.gc.ca/eic/site/063.nsf/eng/h_FB527335.html ,
  https://universityaffairs.ca/news/granting-agencies-grapple-with-scientific-fraud/ (medium). **Research on Research
  Joint Initiative** (SSHRC + CIHR + Michael Smith Health Research BC + RoRI): C$2.7M to 14 researchers, Nov 2025;
  SSHRC Connection Grant to convene the Canadian meta-research community (deadline 2 Feb 2026)
  https://researchonresearch.org/new-initiative-supporting-research-on-research-in-canada/ ,
  https://www.lakeheadu.ca/research-and-innovation/research-services/funding-prizes/funding-db/node/346998 (high).
  **Metascience 2027** in Montreal, 14–16 Jun 2027 (McGill Tanenbaum Open Science Institute + COS)
  https://www.cos.io/blog/save-the-date-metascience-2027-set-for-montreal (high). **CAISI Research Program** (CIFAR,
  $27M; 12 projects/$2.4M in 2025; Vector study of 11 models' reliability for high-stakes use; 2025-26 priorities = risk
  assessment, real-world behaviour, safety techniques; ISED July-2026 note on *reporting AI evaluation results*)
  https://cifar.ca/cifarnews/2026/01/21/a-year-of-impact-for-ai-safety-in-canada/ ,
  https://ised-isde.canada.ca/site/ised/canadian-artificial-intelligence-safety-institute (medium). **Health Canada
  pre-market guidance for ML-enabled medical devices** with Predetermined Change Control Plans; sources disagree on
  finalisation (Feb 2025 vs 1 Apr 2026 republication) https://www.blg.com/en/insights/2025/02/health-canadas-evolving-regulatory-framework-for-machine-learning-enabled-medical-devices ,
  https://nsf.org/life-science-regulatory-news/new-health-canada-guidance-documents-medical-devices-published-march-april-2026
  (medium). **Quantum**: ISED Quantum Champions Program with NRC technical due diligence, "benchmarking-led", Phase 1
  = technical validation; Xanadu up to C$23M; Xanadu/Photonic/Nord Quantique in DARPA QBI (Xanadu at Stage B)
  https://www.hpcwire.com/off-the-wire/xanadu-selected-for-canadas-quantum-champions-program-secures-up-to-cad-23m/ ,
  https://betakit.com/three-canadian-quantum-startups-selected-for-us-military-backed-quantum-race-program/ (high).
- Epistemics / gap framing: policy-level "rigour and reproducibility needs a coordinated national network" (Thibault,
  Munafò, Moher, *Facets* 2022) https://purl.stanford.edu/zx950pj6479 ; AI-safety framing is evaluation-reporting
  ("so findings are understood and trusted"), not admissibility. Quantum: third-party benchmarking as the gate for
  public money — closest Canadian analogue to a fail-closed stance.
- Institutions & people: SRCR/Tri-Agency; SSHRC/CIHR; RoRI; Tanenbaum OSI (McGill); David Moher (Ottawa); CIFAR/CAISI;
  Vector, Mila (Bengio), Amii; NRC; Health Canada; Xanadu.
- Take / Ahead: take: NRC's "neutral benchmarking before funding" pattern and Health Canada PCCP (declared change bands
  → pre-registered re-validation) map directly onto CAPAS's declared-scope/HOLD logic; the NeurIPS workshop's
  "executable dependency gates" paper is a must-read for positioning | ahead: no Canadian artefact does sealed blind
  evaluation, a proof ledger, or no-model-in-verdict gating; CAISI evaluates models, not claims.
- Confidence: medium-high. | Queries (7): "Canada AI for science verification deterministic verifier LLM-as-judge
  2026"; "Canada metascience reproducibility registered reports Tri-Agency research integrity 2025 2026"; "Mila Vector
  Institute automated scientific claim verification formal verification 2026"; "Canadian AI Safety Institute CAISI
  research program 2026 evaluation verification scientific claims"; "Health Canada guidance AI machine learning medical
  device evidence 2025 2026 …"; "Canada quantum computing benchmarking standards Xanadu D-Wave …"; "Canada 'research on
  research' metascience 2026 preregistration replication …"; "Mila 'AI for science' 2026 verification … guardrails".

### Central African Republic
- Direct (2026 SOTA): none found.
- Adjacent: Nature Index counts 2 articles for CAR (Jun 2025–May 2026)
  https://www.nature.com/nature-index/country-outputs/Central%20African%20Republic ; regional only — FRESAC higher-ed
  forum (Libreville, Nov 2025) https://fr.allafrica.com/stories/202511080084.html and the ECCAS RESIRAC research
  network secretariat (Aug 2025) https://gabonmediatime.com/ceeac-le-resirac-prend-ses-quartiers-desormais-a-luil/ ;
  CAR not named in either excerpt.
- Epistemics / gap framing: not surfaced.
- Institutions & people: none national surfaced.
- Take / Ahead: take: nothing | ahead: n/a.
- Confidence: medium (one query). | Queries: "Central African Republic science research policy integrity university 2025".
- **NOTHING FOUND (queries: 1).**

### Chad
- Direct (2026 SOTA): none found.
- Adjacent: GDN/CRESPO "Doing Research in Chad" country report (2026; research concentrated in the capital, weak
  infrastructure/funding/dissemination) https://www.gdn.int/sites/default/files/Doing%20Research%20in%20Chad%20-%20Executive%20Summary%20%28English%29.pdf ;
  CRESPO workshop N'Djamena Apr 2025 https://tchadinfos.com/2025/04/17/tchad-vulgarisation-dune-etude-sur-les-systemes-de-recherche-en-sciences-sociales/ ;
  "TCHAD IA 2025" first AI science days at the Centre National de Recherche pour le Développement (29–30 Dec 2025),
  framed as digital sovereignty https://www.digitalbusiness.africa/tchad-ia-2025-le-gouvernement-place-la-recherche-scientifique-au-coeur-de-la-souverainete-numerique/ .
- Epistemics / gap framing: capacity/system diagnosis, no verification or integrity framing.
- Institutions & people: CNRD; CRESPO; Ministère de l'Enseignement supérieur.
- Take / Ahead: take: nothing | ahead: n/a.
- Confidence: medium. | Queries: "Chad Tchad recherche scientifique intégrité politique 2025".
- NOTHING relevant to CAPAS found (queries: 1); system-diagnosis material only.

### Chile
- Direct (2026 SOTA): none found; no verification/gating or LLM-judge-vs-deterministic work surfaced.
- Adjacent: ANID Open Access Policy in force since 2022, ANID joined CoARA in 2023; green-route adoption slow, metadata
  and data-management-plan guidelines published https://www.elmostrador.cl/noticias/opinion/columnas/2025/02/10/politica-de-acceso-abierto-en-chile-avances-desafios-y-oportunidades/ ;
  "Espacio Ciencia" open catalogue of state-funded research https://www.meteored.cl/noticias/actualidad/espacio-ciencia-el-gran-catalogo-abierto-que-ordena-la-ciencia-chilena-en-un-mismo-lugar.html ;
  UACh open-science days Dec 2025 https://diario.uach.cl/con-invitadas-internacionales-se-realizo-la-segunda-jornada-de-ciencia-abierta-uach/ .
  AI: draft "Ley que regula los sistemas de IA" (entered May 2024, still in the Chamber as of Sep 2025; sandboxes +
  technical council) https://www.ecija.com/actualidad-insights/avanza-el-proyecto-de-ley-de-ia-en-chile/ ; CENIA (ANID-
  funded, LatamGPT) https://es.hispanopedia.com/wiki/Centro_Nacional_de_Inteligencia_Artificial . Regulated submissions:
  ISP authorised 147 trials in 2024, ICH-based general guidance May 2024, processing backlog and a June-2025 cyberattack
  https://www.latercera.com/nacional/noticia/las-razones-que-ponen-a-chile-como-lider-de-la-region-en-estudios-clinicos-147-aprobados-en-2024-y-26-en-lo-que-va-de-ano/ ,
  https://www.meganoticias.cl/nacional/533578-cae-inversion-laboratorios-internacionales-chile-rezago-09-10-2026.html .
  A CASRAI page dated 30 Jul 2026 on ANID OA expansion looked unreliable (mixed vendor content) — not used.
- Epistemics / gap framing: open-access/assessment-reform framing (CoARA), not evidence grading; no reproducibility or
  statistics-checking infrastructure surfaced.
- Institutions & people: ANID; CENIA (Mónica Soto, dir.); ISP; UACh, U. de Chile.
- Take / Ahead: take: ANID's metadata/interoperability directives as a model for machine-readable evidence declarations |
  ahead: Chile has no claim-level gate, no preregistration infrastructure, no blind-evaluation practice surfaced.
- Confidence: medium (3 queries, no metascience hit). | Queries: "Chile ciencia abierta reproducibilidad integridad
  científica ANID 2025 2026"; "Chile CENIA inteligencia artificial ciencia verificación ley de IA 2025 2026"; "Chile ISP
  registro ensayos clínicos estadística evidencia regulatoria 2025 preregistro metaciencia". Not run (budget): replication/
  preregistration in Chilean psychology.

### China (run 1: 5 searches; run 2: 4 pending items completed below)
- Direct (2026 SOTA): no deterministic/fail-closed claim-gating system surfaced. Model-based verification is the dominant
  Chinese stance: **SCI-Verifier / SCI-VerifyBench** (Zheng, Huang, … Lei Bai, Ganqu Cui, Peng Ye — Shanghai AI Lab
  group by author list; affiliations not on the abstract page), arXiv 29 Sep 2025, accepted ICLR 2026: a reasoning-
  augmented *model* verifier for scientific answers across math/physics/biology/chemistry, explicitly positioned
  against "heavy reliance on cumbersome rule design"; no head-to-head vs deterministic verifiers (verified by fetch)
  https://arxiv.org/abs/2509.24285 , https://proceedings.iclr.cc/paper_files/paper/2026/hash/7d60bfd8458b67acbbaf18b892338d00-Abstract-Conference.html (high).
  This is the anti-pole of CAPAS: China's SOTA puts a model in the verdict.
- Adjacent: **AI4S national programme** — MOST special deployment since 2023; 2026 Government Work Report lists ultra-
  large AI4S clusters under "AI+"; 60,000-chip Sugon AI4S cluster at Zhengzhou (Apr 2026); 2026 Science Intelligence
  Conference Beijing 21–22 Aug ("AI from tool to partner") https://english.henan.gov.cn/2026/04-21/3344578.html ,
  https://www.ncsti.gov.cn/kjdt/ztbd/2026kxzndh/202608/t20260821_254170.html ,
  https://www.news.cn/tech/20260822/d8084713b4a444348bc435efdd100c2d/c.html , analysis
  https://ucigcc.org/blog/inside-chinas-ai-for-science-strategy/ (high on existence; no verification stance stated).
  **Research integrity**: MOST generative-AI guidelines (ban on direct AI use in funding applications; labelling of
  AI content) https://etico.iiep.unesco.org/en/new-generative-ai-guidelines-aim-curb-research-misconduct (medium;
  primary fetch failed); Yuyuantan Conference on Research Integrity v3.0 guideline on AI-generated content in academic
  publishing https://letsdatascience.com/news/china-issues-ai-guidelines-for-academic-publishing-1f75c378 (low,
  aggregator); **CNKI removing papers listing AI (DeepSeek, Gemini) as authors**, 23 Jul 2026 (verified by fetch)
  https://www.mlex.com/mlex/articles/2504762 (high); CCTV investigation of AI-powered paper mills (30+ articles/
  worker/week), Oct 2025 https://www.scmp.com/tech/tech-trends/article/3328966/ai-powered-fraud-chinese-paper-mills-are-mass-producing-fake-academic-research (medium);
  MoE-ordered retraction audits (2026) https://academicjobs.com/cn/research-publication-news/china-paper-mills-retractions-surge-spurs-university-reforms-academicjobs-26627 (low).
  **Quantum**: Zuchongzhi-3 (USTC/CAS, Pan Jianwei), 105 qubits, PRL Mar 2025, RCS 83q×32 layers, 1q 99.90% / 2q 99.62%
  / readout 99.13% / T ≈ 72 µs; the CAS page reports no calibration-snapshot or independent verification beyond peer
  review (verified by fetch) https://bcas.cas.cn/highlight/202504/t20250424_1041936.html (high); Origin Quantum "Origin
  Pilot" open-source QC OS, Feb 2026 (secondary). No national quantum-benchmarking admissibility standard surfaced.
  **Metascience**: only the Chinese Open Science Network's replication-crisis explainer https://osf.io/vdu4s (undated).
- Epistemics / gap framing: integrity is handled by *provenance rules and sanctions* (labelling, author bans, case
  databases), not by claim-level evidence admissibility; AI4S is framed as acceleration, with novelty/bias concerns
  raised by outsiders (UCIGCC). Quantum advantage claims rest on RCS benchmarks + peer review, no frozen-calibration gate.
- Institutions & people: MOST; MoE; CNKI; Shanghai AI Lab (Lei Bai, Peng Ye, Ganqu Cui); USTC/CAS (Pan Jianwei, Zhu
  Xiaobo, Peng Chengzhi); Origin Quantum; Chinese Open Science Network.
- Take / Ahead: take: SCI-VerifyBench's equivalence-transformation taxonomy (how equivalent answers are judged) could
  seed CAPAS's REWRITE rules for structured fields; Zuchongzhi-3's published fidelity set is a ready Atlas/CAPAS
  invariant test case | ahead: CAPAS has no model in the verdict, sealed blind rates, machine-ingested calibration
  snapshots with per-parameter dates; China's integrity stack is provenance/sanction-based and its verifiers are LLMs.
- Confidence: medium (partial). | Queries run (5): "China AI for science verification AI4S national program 2026
  scientific claim verification"; "China research integrity 2025 2026 paper mills MOST regulations AI-generated papers";
  "Chinese metascience meta-research reproducibility replication crisis China 2025"; "China quantum computing
  benchmarking standard Zuchongzhi Origin Quantum calibration verification 2025 2026"; (Canada query that surfaced
  SCI-Verifier). **Not run (budget)**: DeepSeek-Prover/Kimina Lean autoformalization; Shanghai AI Lab/Tsinghua rule-based
  reward vs LLM-judge (RLVR); Chinese-language 科研诚信/可重复性/预注册; national quantum benchmark standard (GB/T, CESI).
- **Extension (resumed run, 4 pending items):**
  - *Lean / formal verification.* **DeepSeek-Prover-V2** (Ren, Shao et al., arXiv 2504.21801, Apr 2025, rev. Jul 2025):
    Lean 4 proofs, 88.9% on miniF2F-test, 49/658 PutnamBench https://arxiv.org/abs/2504.21801 ; **Kimina-Prover Preview**
    (Wang, Unsal, Lin et al., arXiv 2504.11354, Apr 2025): Qwen2.5-72B + RL, 80.7% miniF2F pass@8192
    https://arxiv.org/abs/2504.11354 (affiliations not on abstract pages; medium). The Lean kernel is a deterministic
    verifier — China's closest practice to "no model in the verdict", but for theorems, not empirical claims. The Sep–Oct
    2026 arXiv stream (AxQM: 1,019 Lean tasks "graded deterministically by the Lean kernel"; SpecGuard; Choir's
    "deterministic merge gate") shows the pattern spreading; Chinese affiliation not confirmed for those.
  - *RLVR: rule-based rewards vs LLM-judge.* **DeepSeek-R1** (arXiv 2501.12948, Jan 2025; *Nature* Sep 2025
    https://doi.org/10.1038/s41586-025-09422-z ) §2.2.2, verified from the arXiv HTML: "we adopt a rule-based reward
    system… We do not apply the outcome or process neural reward model in developing DeepSeek-R1-Zero… the neural reward
    model may suffer from reward hacking in the large-scale reinforcement learning process"
    https://arxiv.org/html/2501.12948v1 (high). **Tencent AI Lab, "One Token to Fool LLM-as-a-Judge"** (Zhao, Liu, Yu…
    Dong Yu; arXiv 2507.08794, Jul 2025, v3 Jun 2026): generative reward models in RLVR give false-positive rewards to
    "master key" inputs (a colon, "Thought process:") across GPT-o1 and Claude-4; fix = Master-RM trained with truncated
    adversarial negatives https://arxiv.org/abs/2507.08794 (high; Tencent affiliation via OpenAlex). The generative-judge
    line continues regardless: Think-J (Alibaba/Nanjing 2025) https://doi.org/10.48550/arxiv.2505.14268 ; Open Rubric
    System (Alibaba/BUPT/CAS 2026) https://doi.org/10.48550/arxiv.2602.14069 ; Multimodal Reward Hacking (CAS ICT 2026)
    https://doi.org/10.48550/arxiv.2607.09492 . Reading: China's frontier is split — rule-based verifiable rewards where
    ground truth is checkable (DeepSeek), model judges elsewhere (Alibaba, Tencent, Shanghai AI Lab's SCI-Verifier) —
    and the strongest evidence that model judges fail comes from inside.
  - *Chinese-language 科研诚信 / 人工智能生成论文核查 2026.* Bing failed; OpenAlex Chinese-language search (≈2,900 full-text
    hits) surfaced only education-journal pieces, e.g. "Evidence Crisis, Process Verification, and Institutional
    Reconstruction of University Education Evaluation in the Generative AI Era" (2026)
    https://doi.org/10.70693/202607148328 and "Building a New Paradigm of University Students' Academic Integrity in the
    Context of Generative AI" (2025) https://doi.org/10.71411/jyyjx.2025.v1i6.746 . No MOST/CAS primary document on
    AI-paper checking was reached (low; follow-up: fetch most.gov.cn / cas.cn directly).
  - *GB/T quantum standards.* The national catalogue (openstd.samr.gov.cn) lists five recommended standards for 量子计算:
    GB/T 42565-2023 terms and definitions (eff. 2023-12-01); GB/T 47176-2026 ultra-low-temperature/low-noise system for
    superconducting QC (pub. 2026-02-27, eff. 2026-09-01); GB/T 47177.1-2026 QC service platform — architecture and
    functional requirements (eff. 2026-09-01); GB/T 47177.2-2026 Part 2 — performance evaluation (pub. 2026-04-30, eff.
    2026-11-01); **GB/T 47468-2026 量子计算系统性能测试方法 "Test methods for quantum computing system performance" (pub.
    2026-04-30, eff. 2026-11-01)**, confirmed by a second catalogue query
    https://openstd.samr.gov.cn/bzgk/gb/std_list?p.p2=GB%2FT+47468 (high on existence/dates; text not read). This
    corrects the earlier "no national quantum-benchmarking standard surfaced". Take: map Atlas/CAPAS calibration
    invariants to GB/T 47468-2026's test methods and expose a conformance field | ahead: a test method prescribes
    measurement, not admissibility of a reported number against a frozen, dated snapshot.
- Confidence (whole entry): medium-high. | Queries (resumed): arXiv API ×2; arXiv abs/html ×4; OpenAlex CN ×4 (RLVR/judge
  ×2, quantum standards ×2); OpenAlex Chinese-language ×2; openstd.samr.gov.cn ×2; Bing ×3 (failed).


### Colombia
- Direct (2026 SOTA): none found. Closest: Colombian co-authors (Universidad del Rosario, Universidad de los Andes) on
  **Brodeur et al., PNAS Jun 2026** — 288 researchers in 103 teams: reproduction rate human-only 94%, AI-assisted
  (ChatGPT as tool) 91%, AI-led (minimal oversight) 37%; AI-led teams found fewer major coding errors and ran weaker
  robustness checks (abstract read via Europe PMC) https://doi.org/10.1073/pnas.2524747123 (high). Empirical support for
  "no model in the verdict": a model *leading* verification collapses the result.
- Adjacent: meta-research cluster at Universidad de la Costa (Iván David Lozada-Martínez): "Why is it important to implement
  meta-research in universities…" (2025) https://doi.org/10.3389/frma.2025.1497280 ; "Meta-Research in Neuroscience" (JCM
  2025) https://doi.org/10.3390/jcm14238552 ; "Institutional Use of Meta-Research to Manage Conflict of Interest" (2026)
  https://doi.org/10.1007/978-3-032-27479-3_7 . Juan David Leongómez (Universidad El Bosque), preregistration/registered
  reports, *Human Ethology* Jul 2025 https://doi.org/10.22330/001c.141550 . Apptainer reproducibility training (Universidad
  Antonio Nariño, arXiv 2604.06244) https://doi.org/10.48550/arxiv.2604.06244 . Minciencias open-science page returned 404;
  no policy document verified.
- Epistemics / gap framing: meta-research framed as institutional quality management (conflict of interest, reliability),
  not claim admissibility; no national preregistration or statistics-checking infrastructure surfaced.
- Institutions & people: Minciencias (unverified); Universidad de la Costa (Lozada-Martínez); El Bosque (Leongómez);
  Rosario, Andes (Brodeur co-authors); Universidad Nacional.
- Take / Ahead: take: cite Brodeur 2026 as the measured cost of AI-led verification | ahead: no Colombian claim-level
  gate, no blind evaluation, no proof ledger.
- Confidence: medium. | Queries: WebSearch ×2 (refused, budget); Bing ×1 (no results); OpenAlex CO ×3
  (integrity/reproducibility/metascience; claim verification/LLM-judge; ciencia abierta/Minciencias); Minciencias page fetch.

### Comoros
- Direct (2026 SOTA): none. Adjacent: OpenAlex (2024–26, Comoros affiliation) returns 13 works, all Midocean University
  (Moroni; raw affiliations often say UAE); only one on research ethics, "The Ethical Responsibilities of Researchers in
  Light of … AI" (2024) https://doi.org/10.70082/esiculture.vi.805 .
- Epistemics / Institutions / Take: nothing national surfaced.
- Confidence: medium. | Queries: OpenAlex KM ×1 (integrity OR reproducibility OR misconduct OR plagiarism OR preregistration).
- **NOTHING FOUND.**

### Republic of the Congo
- Direct (2026 SOTA): none. Adjacent: OpenAlex CG 2024–26 (176 hits, full-text matches) shows only IRD (French institute
  tagged CG) reproducibility packages on Zenodo and one Marien Ngouabi University workflow record; no integrity policy or
  tooling.
- Epistemics / Institutions / Take: nothing national surfaced (Université Marien Ngouabi only as affiliation).
- Confidence: medium. | Queries: OpenAlex CG ×1.
- **NOTHING FOUND.**

### Democratic Republic of the Congo
- Direct (2026 SOTA): none. Adjacent (ethics governance only): "The Role of Academic Institutions in Establishing AI Research
  Ethical Committees: Case of Universities in the DRC" (ISP Bukavu, 2025) https://doi.org/10.36948/ijfmr.2025.v07i06.64765 ;
  African Journal Partnership Program guidance on AI in scholarly publishing (Univ. Kinshasa co-author, 2024)
  https://doi.org/10.4314/ejhs.v34i2.1 ; "Assessing Teaching and Scientific Research in Higher Education in the Era of
  Generative AI" (Univ. Lubumbashi, 2026) https://doi.org/10.5281/zenodo.23258770 .
- Epistemics / gap framing: ethics-committee and AI-labelling framing; no verification stance.
- Institutions & people: ISP Bukavu; Université de Kinshasa; Université de Lubumbashi.
- Take / Ahead: take: nothing | ahead: n/a.
- Confidence: medium. | Queries: OpenAlex CD ×1.
- **NOTHING FOUND (adjacent ethics-committee material only).**

### Costa Rica
- Direct (2026 SOTA): none. Adjacent: **AIMLS — AI Manuscript Labelling System** (UNED Unidad de Ciencia Abierta, v29, 4 Oct
  2026): an open notation plus single-file browser tool that emits a graphic label and matching prose declaration of AI
  use per the STM nine-activity classification; fixed code, composition rules, automated tests, no server; whether it is
  rule-based is implied, not stated https://doi.org/10.5281/zenodo.23139496 (medium). TECdatos research-data repository at
  Tecnológico de Costa Rica (2026) https://doi.org/10.15517/tjhrz483 ; "Vaccines, Bias, and the Perils of Non-peer-reviewed
  Studies" (UCIMED/CCSS, *CID* 2026) https://doi.org/10.1093/cid/ciag403 ; open-access bibliometrics (UCR 2025)
  https://doi.org/10.38202/journal21.2 . MICITT/CONARE not reached.
- Epistemics / gap framing: declaration/labelling of AI use (provenance), open data — not evidence admissibility.
- Institutions & people: UNED Unidad de Ciencia Abierta (Alexander Chinchilla Serrano); TEC; UCR; UCIMED.
- Take / Ahead: take: AIMLS's machine-readable AI-use declaration is a field CAPAS could ingest as declared provenance |
  ahead: no gate, no blind evaluation.
- Confidence: medium. | Queries: OpenAlex CR ×2 (integrity set; open science/registration set).

### Côte d'Ivoire
- Direct (2026 SOTA): none. Adjacent: "Équité et performances dans les modèles d'IA : proposition d'un système métrique
  inclusif et reproductible" (Université Virtuelle de Côte d'Ivoire, 2025) https://doi.org/10.71655/uvcibv.y8bys-b3h21 ;
  "Ethical Implications of Generative AI in Academic Writing" (Institut Universitaire d'Abidjan, 2026, no DOI); UFHB
  co-authored reproducibility packages (flood models, Zenodo 2026) https://doi.org/10.5281/zenodo.22687798 .
- Epistemics / Institutions: no national framing surfaced; UFHB, UVCI, Nangui Abrogoua as affiliations only.
- Take / Ahead: take: nothing | ahead: n/a.
- Confidence: medium. | Queries: OpenAlex CI ×2.
- **NOTHING FOUND (adjacent-only).**

### Croatia
- Direct (2026 SOTA): none.
- Adjacent (strong metascience): **CroRIN — Croatian Reproducibility and Integrity Network** (Univ. of Split School of
  Medicine; Adris Foundation 2022 call; partners UKRN, Cochrane Croatia, ST-OPEN, Null Hypothesis) https://crorin.hr/ ,
  listed by UKRN https://www.ukrn.org/international-networks/ . Ana Marušić group: "Primer on Reproducibility" (2025)
  https://doi.org/10.1002/cpz1.70299 ; **iRISE Delphi** (Pejdo, Buljan, Marušić, *RIPR* Jul 2026): 73 panellists / 34
  countries; 8 consensus measures — methodological quality, reporting quality, code/data availability, computational
  reproducibility, transparency of the research plan, reproducible workflows, trial registration, materials availability
  https://doi.org/10.1186/s41073-026-00217-y (high); "Gen AI and research integrity: where to now?" (*EMBO Rep* 2025)
  https://doi.org/10.1038/s44319-025-00424-6 ; COI-driven retractions in Retraction Watch (2026)
  https://doi.org/10.1186/s41073-026-00236-9 ; Puljak & Buljan "a cultural evolution is needed to move from ideals we
  celebrate to implementation" (2026) https://doi.org/10.1186/s12874-026-02964-4 ; Borovečki ten-country CEE integrity
  survey (*Sci Rep* 2026) https://doi.org/10.1038/s41598-026-39928-z ; ethics experts on AI review (Split 2026)
  https://doi.org/10.1080/08989621.2026.2744222 ; Rijeka Centre for Open Science (2025) https://doi.org/10.37083/bosn.2025.30.330 .
- Epistemics / gap framing: consensus lists and culture change; Puljak's own title concedes the implementation gap.
- Institutions & people: Univ. of Split (Marušić, Buljan, Pejdo, Pranić); Catholic Univ. of Croatia (Puljak); Univ. of
  Zagreb (Borovečki); Ruđer Bošković Institute; Univ. of Rijeka.
- Take / Ahead: take: map CAPAS evidence fields onto the 8 iRISE consensus measures and say which are mechanically
  checkable | ahead: Croatia prioritises; CAPAS enforces (fail-closed, hashed).
- Confidence: medium-high. | Queries: UKRN list fetch; crorin.hr fetch; OpenAlex HR ×2; Europe PMC ×1.

### Cuba
- Direct (2026 SOTA): none. Adjacent: "Ética y malas conductas en el proceso de la publicación científica" (UCM La Habana,
  2026) https://doi.org/10.56712/latam.v7i4.6345 ; "Desafíos éticos de la IA para la integridad científica" (Villa Clara,
  2025) https://doi.org/10.5281/zenodo.17956604 ; **policy–implementation gap in Cuban (Ecimed) medical journals**, cross-
  sectional, SciELO Preprints 17 Sep 2026 (no numbers in abstract) https://doi.org/10.1590/scielopreprints.17423 ;
  "Propuesta Marco Regulatorio para la Ciencia Abierta en las instituciones adscritas al MES" (UCLV/Camagüey 2026)
  https://doi.org/10.5281/zenodo.20466264 . CITMA/CECMED not reached.
- Epistemics / gap framing: open-science policy exists on paper; the national literature itself measures the gap to practice.
- Institutions & people: UCM Habana/Guantánamo/Matanzas; CNICM; UCLV; Ministerio de Educación Superior.
- Take / Ahead: take: nothing mechanical | ahead: CAPAS closes exactly the policy→practice gap these studies describe.
- Confidence: medium. | Queries: OpenAlex CU ×2; SciELO preprint fetch.

### Cyprus
- Direct (2026 SOTA): none. Adjacent: UCLan Cyprus (Kalypso Iordanou) is a node of Horizon Europe **BEYOND** ("Beyond Bad
  Apples", grant 101094714): BEYOND Guidelines for Preventing and Addressing Research Misconduct (v2, 2026)
  https://doi.org/10.5281/zenodo.17720038 ; Best Practices Manual (2026) https://doi.org/10.5281/zenodo.21098383 ;
  "Behavioral insights for improving research integrity" (Dec 2025; online experiment n=634: value/consequence reminders
  raise high-integrity choices only on the first vignette) https://doi.org/10.5281/zenodo.17871645 (high). CHANGER policy
  brief on research security (Open Univ. of Cyprus 2025) https://doi.org/10.5281/zenodo.19366949 ; "Researching retraction:
  more rules or more honesty?" (EMU 2026) https://doi.org/10.1080/08989621.2026.2683838 ; reproducibility best practices
  for experimental economists (Univ. of Cyprus 2025) https://doi.org/10.1016/j.socec.2025.102472 . RIF/CYENS not reached.
- Epistemics / gap framing: misconduct as systemic ("beyond bad apples"); remedies are behavioural and organisational.
- Institutions & people: UCLan Cyprus (Iordanou, Antoniou); Open University of Cyprus; Univ. of Cyprus; EMU.
- Take / Ahead: take: the decay of nudges after first exposure (BEYOND) is an argument for mechanical gates | ahead:
  nothing mechanical in Cyprus.
- Confidence: medium-high. | Queries: OpenAlex CY ×2; Zenodo ×2.

### Czechia
- Direct (2026 SOTA): no claim-level gate. Closest architectural sibling: **Kirsch (CTU Prague / Salzburg), "Untrusted
  Authors, Trusted Answers: A Calculus of Fidelity-Graded Translations", arXiv 2607.14137, Jul 2026** — the LLM-built
  plane is "untrusted by construction"; witness-carrying answers are self-certifying by replay at the source; universal
  answers rest on fidelity grades, independent branches and certificates re-checked by a formally verified checker; core
  mechanised in Lean 4 https://arxiv.org/abs/2607.14137 (high; abstract read). Same shape as CAPAS (untrusted proposer,
  mechanical disposer) applied to programs, not empirical claims. AI theorem proving: OpenProver (Charles Univ., Kripner &
  Straka, 2026) https://doi.org/10.1007/978-3-032-38214-6_21 ; Janota (CTU) "Proving at Scale for Universal Algebra"
  arXiv 2610.02500 ; Cerna (CAS) ITP tactic-prediction rules (2025) https://doi.org/10.1007/978-3-032-09087-4_7 .
- Adjacent: Charles University / CAS Institute of Psychology meta-research (Ivan Ropovik, Matúš Adamkovič, Artem Buts):
  **"Automating data extraction in meta-research: a multi-model benchmark"** (*Behav Res Methods*, May 2026): five LLMs
  (Claude 4.6 Opus → GPT-5 mini) on 43 papers, 79.6–91.3% accuracy, high for verbatim fields (n, preregistration status),
  low for inferential ones https://doi.org/10.3758/s13428-026-03052-7 (high); Adamkovič co-author of the *Nature* 2026
  replicability study https://doi.org/10.1038/s41586-026-10203-5 ; Foltýnek (Masaryk, ENAI) "Maintaining research
  integrity in the age of GenAI" (*IJEI* 2025) https://doi.org/10.1007/s40979-025-00191-w ; GAČR "GACR and Open Science"
  (19 Nov 2024; open data costs eligible) https://gacr.cz/en/gacr-and-open-science/ . No Czech reproducibility network on
  the UKRN list (Slovakia has one).
- Epistemics / gap framing: formal-methods culture (certificates, replay, kernel-checked) alongside a metascience
  community that measures LLM extraction error rather than gating on it.
- Institutions & people: CTU/CIIRC (Kirsch, Janota); Charles Univ. (Straka, Ropovik, Adamkovič); CAS (Cerna); Masaryk
  (Foltýnek); GAČR.
- Take / Ahead: take: Kirsch's assurance classes as a vocabulary for CLOSED/BACKED/SCOPED; Ropovik's verbatim-vs-
  inferential split confirms CAPAS's ingest-from-files rule | ahead: no sealed blind rates, no claim-level verdicts.
- Confidence: medium-high. | Queries: WebSearch ×2 (refused); Bing ×3 (empty/off-topic); OpenAlex CZ ×2; arXiv abs ×1;
  Europe PMC ×1; GAČR site search ×1; UKRN list.

### Denmark
- Direct (2026 SOTA): none. No Danish deterministic-verification or LLM-judge-vs-verifier work surfaced; Pioneer Centre
  for AI (Serge Belongie; seven collaboratories, none on verification) https://aicentre.dk/ .
- Adjacent: **Danish Code of Conduct for Research Integrity, Jan 2026** (replaces 2014; motivated by open science and AI;
  institutional endorsement list) https://ufsn.dk/english/publications/2026/januar/danish-code-of-conduct-for-research-integrity/ ,
  PDF https://ufsn.dk/media/5iejum3i/kodeksforskningintegritet_06012026_www_uk.pdf ; Agency page on AI-in-research guidelines
  (ALLEA 2023, EU living guidelines 2025, UNESCO 2023)
  https://ufsn.dk/english/research-and-innovation/framework-for-research-and-innovation/integrity-in-research/international-guidelines-on-the-use-of-artificial-intelligence-ai-in-research/ ;
  Danish Committee on Research Misconduct (2017 Act; decisions page)
  https://ufm.dk/en/research-and-innovation/councils-and-commissions/The-Danish-Board-on-Research-Misconduct/decisions (high).
  **DKRN** (launched 24 Aug 2023; chairs Derksen, Dam, Wildgaard, Vinding; 10 Jun 2026 national event with DeiC asking how
  to use AI "in a reproducible way"; RAISE label) https://danish-repro.github.io/ ,
  https://www.bibliotek.dtu.dk/en/newsarchive/2026/05/national-reproducibility-og-research-data-event (high).
  **Preregistration for real-world evidence** (Simonsen, Wang, Kildegaard, Pottegård, SDU, *PDS* Sep 2025; OSF RWE
  Registry) https://doi.org/10.1002/pds.70215 (high); registration of observational studies meta-research (Jespersen,
  Hróbjartsson, SDU/OUH, *RIPR* 2026; abstract not retrieved) https://doi.org/10.1186/s41073-026-00258-3 (medium); UCPH
  *Research Integrity* textbook materials (2026) https://doi.org/10.5281/zenodo.20623471 ; Aarhus study of organisational
  RI-policy efficacy (Fuglsang, Sørensen, Mejlgaard 2026) https://doi.org/10.1080/08989621.2026.2679561 ; UCPH co-authors
  on "Advancing Trustworthy AI in Healthcare Through Meta-Research" (arXiv 2603.13286, Feb 2026)
  https://arxiv.org/abs/2603.13286 ; Warren (UCPH) "Show Me the Work" — fact-checkers' requirements for explainable
  automated fact-checking (CHI 2025) https://doi.org/10.1145/3706598.3713277 . Regulator: Danish Medicines Agency
  evidence page (2020) — evidence pyramid, "not proof or one truth", convergence of independent studies; no AI, RWE or
  pre-specification https://laegemiddelstyrelsen.dk/en/licensing/-how-to-evaluate-evidence-of-the-efficacy-of-medicines/ .
  Quantum: NQCP (NBI) site states no benchmarking/verification stance https://nqcp.ku.dk/ .
- Epistemics / gap framing: code-of-conduct plus statutory misconduct committee; AI handled by declaration; the regulator
  frames evidence as provisional and convergent. Nothing fail-closed.
- Institutions & people: Danish Agency for Higher Education and Science; Committee on Research Misconduct; DKRN; SDU
  (Pottegård, Hróbjartsson); UCPH (Engelhardt, Porsdam Mann, Warren); Aarhus (Mejlgaard); Pioneer Centre (Belongie); NQCP.
- Take / Ahead: take: ingest OSF RWE-Registry preregistrations as declared bands (Pottegård) and use registration-
  prevalence baselines (Hróbjartsson) in the pharma beachhead pitch | ahead: no mechanical gate, blind rates or ledger.
- Confidence: medium-high. | Queries: WebSearch ×3 (2 answered, 1 refused); Bing ×3 (empty/off-topic); OpenAlex DK ×2;
  fetches: danish-repro, aicentre, nqcp, ufsn, DMA ×2, arXiv, Europe PMC ×2.

### Djibouti
- Direct (2026 SOTA): none. Adjacent: OpenAlex DJ 2024–26 (25 hits) = CERD climate/hydrology papers and one Univ. of
  Djibouti essay on AI and literary interpretation; nothing on integrity or verification.
- Confidence: medium. | Queries: OpenAlex DJ ×1.
- **NOTHING FOUND.**

### Dominica
- Direct (2026 SOTA): none. Adjacent: OpenAlex DM 2024–26 = 3 hits; one All Saints University neurosurgery survey, two
  mis-tagged Dominican Republic records.
- Confidence: medium. | Queries: OpenAlex DM ×1.
- **NOTHING FOUND.**

### Dominican Republic
- Direct (2026 SOTA): none. Adjacent (thin): UASD "Master Reproducibility Package" for a LightGBM mortality model (2026)
  https://doi.org/10.5281/zenodo.23089897 ; UASD "Incidencia del plagio en el ámbito académico y profesional" (2026)
  https://doi.org/10.5281/zenodo.23196825 ; UNPHU "Evidence in the Age of Algorithms: Redefining Emergency Medicine
  Research" (2026) https://doi.org/10.2147/oaem.s657506 ; an unreviewed UASD Lean 4 formalisation upload (2026)
  https://doi.org/10.5281/zenodo.21581767 . MESCYT not reached.
- Institutions & people: UASD; UNPHU; UAPA.
- Confidence: medium. | Queries: OpenAlex DO ×2.
- **NOTHING FOUND (adjacent-only).**

### Ecuador
- Direct (2026 SOTA): none. Adjacent: "Ciencia Abierta en Ecuador: evolución y nuevos desafíos" (UTE / Fundación Openlab,
  chapter, Nov 2025) https://doi.org/10.5281/zenodo.17527843 ; "Avances, tensiones y desafíos de la Ciencia Abierta en
  América Latina" (2026) https://doi.org/10.24215/26183188e154 ; RERCIE collaborative editorial governance (UPS 2026)
  https://doi.org/10.38202/journal22.2 ; open-science outreach model (Univ. of Guayaquil 2026) https://doi.org/10.36390/telos281.18 .
  SENESCYT / ARCSA not reached.
- Epistemics / gap framing: open-access and editorial-governance framing; no evidence grading.
- Institutions & people: Universidad UTE; Fundación Openlab Ecuador; Universidad Politécnica Salesiana.
- Take / Ahead: take: nothing | ahead: everything mechanical.
- Confidence: medium. | Queries: OpenAlex EC ×2; Zenodo ×1.

### Egypt
- Direct (2026 SOTA): none. No AI-verification or LLM-judge work with Egyptian affiliation surfaced (query returned only
  GBD mortality papers).
- Adjacent (retraction forensics, author-level risk): **Kelleni (Minia Univ.) ARI² — Author Research Integrity Risk Index**,
  code plus "verified dataset", reports AUC (v1.1, 6 May 2026) https://doi.org/10.5281/zenodo.20018816 and "Commercial
  Authorship and Content Fraud Leave Distinct Bibliometric Signatures" (SSRN 2026) https://doi.org/10.2139/ssrn.6844802
  (medium); Saqr (AASTMT) "Dissecting AI-related Paper Retraction Across Countries and Institutions" (Preprints.org Jan
  2026; page 403, metadata only) https://doi.org/10.20944/preprints202601.0314.v1 (low); NRC co-authored paper-mills
  systematic review (2025) https://doi.org/10.21124/tsp.2025.81.87 ; pediatric-literature retractions bibliometrics
  (Zagazig/Kafrelsheikh 2025) https://doi.org/10.1007/s00431-025-06578-8 ; "Stop Reducing Us into Simplistic Numbers"
  (Cairo Univ. 2026) https://doi.org/10.25259/stn_13_2026 . ASRT / EKB / Egyptian Drug Authority not reached.
- Epistemics / gap framing: fraud detection by bibliometric signature and author scoring — the stance CAPAS measured it
  cannot deliver (888 clean vs 6,348 retracted: no separation at claim level).
- Institutions & people: Minia Univ. (Mina Kelleni); AASTMT (Khalid Saqr); National Research Centre; Zagazig; Cairo Univ.
- Take / Ahead: take: ARI² as a comparator — does author-level signal separate where claim-level fields do not? | ahead:
  CAPAS gates claims, not people, and states its GIGO ceiling.
- Confidence: medium. | Queries: OpenAlex EG ×3; Zenodo ×1; Preprints.org ×1 (403).

### El Salvador
- Direct (2026 SOTA): none. Adjacent (thin): Universidad Salvadoreña Alberto Masferrer "IA responsable en el ciclo de la
  investigación" (2025) https://doi.org/10.65880/ba5myc15 and "IA generativa en la investigación académica: revisión
  desde la ética" (2026) https://doi.org/10.5377/ce.v13i1.23404 ; replication materials for an AI text-indicator study
  (2026) https://doi.org/10.5281/zenodo.20709089 .
- Confidence: medium. | Queries: OpenAlex SV ×2.
- **NOTHING FOUND (adjacent-only).**

### Equatorial Guinea
- Direct (2026 SOTA): none. Adjacent: OpenAlex GQ 2024–26 = 6 hits (UNGE literature/education, AAUCA economics); none
  on-topic.
- Confidence: medium. | Queries: OpenAlex GQ ×1.
- **NOTHING FOUND.**

### Eritrea
- Direct (2026 SOTA): none. Adjacent: OpenAlex ER 2024–26 = 7 hits, all University of Asmara / Orotta clinical or
  pharmaceutics papers; none on-topic.
- Confidence: medium. | Queries: OpenAlex ER ×1.
- **NOTHING FOUND.**

### Estonia
- Direct (2026 SOTA): none. No Estonian AI-for-science verification work; TalTech formal verification is domain-specific
  (COLREG constraint-programming verification 2025 https://doi.org/10.1109/joe.2025.3592285 ; formal foundation for ZK
  rollups 2025 https://doi.org/10.1145/3719027.3765115 ).
- Adjacent: Estonian Code of Conduct for Research Integrity agreement signed by 21 institutions, 7 Nov 2017
  https://etag.ee/en/news/21-research-institutions-signed-the-research-integrity-agreement/ ; ETAG integrity pages
  https://etag.ee/en/research-culture/research-integrity/ ; ETAG open-science page stops at the 2016 principles and 2017
  surveys — no reproducibility, preregistration or AI https://etag.ee/en/research-culture/open-science/ (high). University
  of Tartu in Horizon Europe **BEYOND**: Kadri Simm co-author of the BEYOND Guidelines (2026) https://doi.org/10.5281/zenodo.17720038 ;
  Uusberg & Andres (Tartu Psychology) "Behavioral insights for improving research integrity" (Dec 2025, n=634)
  https://doi.org/10.5281/zenodo.17871645 ; Tammeleht & Parder, RI leadership in national surveys (Estonia a case,
  *Accountability in Research* 2025) https://doi.org/10.1080/08989621.2025.2481940 ; Tartu "Agentic-J" containerised
  multi-agent reproducible bioimage analysis (2026) https://doi.org/10.5281/zenodo.20443684 ; Sancar & Bardone "Towards
  More Ethical Research in AI Era: Free Science Approach" (2026) https://doi.org/10.5281/zenodo.20068649 ; "Who Checks the
  Checkers? Community Notes credibility" (Tartu 2026) https://doi.org/10.1007/s42001-025-00455-y . Not on the UKRN list.
- Epistemics / gap framing: code-of-conduct governance plus behavioural RI research; no evidence-grading or
  statistics-checking infrastructure.
- Institutions & people: ETAG; Univ. of Tartu Centre for Ethics (Simm, Tammeleht, Parder) and Psychology (Uusberg);
  TalTech.
- Take / Ahead: take: Uusberg's decay-of-nudges result as a motivation slide for mechanical enforcement | ahead: all of
  CAPAS's mechanics.
- Confidence: medium-high. | Queries: WebSearch ×2 (refused); Bing ×3 (empty/off-topic); OpenAlex EE ×3; ETAG site
  search + open-science page; Zenodo ×2.

### Eswatini
- Direct (2026 SOTA): none. Adjacent: OpenAlex SZ 2024–26 = 50 hits (UNESWA); only "The Rise of LLMs in Academic Research:
  Opportunities and Challenges" (2024) https://doi.org/10.54433/jdiis.2024100043 is tangential.
- Confidence: medium. | Queries: OpenAlex SZ ×1.
- **NOTHING FOUND.**

### Ethiopia
- Direct (2026 SOTA): none. Adjacent: **Hailu et al., F1000Research 2025** (Ethiopian Defence Univ. / Addis Ababa Univ. /
  Johns Hopkins Berman): 244 researchers (82% response); 37.7% (95% CI 31.6–44.1) report at least one misconduct form;
  authorship misconduct 47.5%, fabrication/falsification 40.6%; publication pressure AOR 3.18 (1.02–9.95)
  https://doi.org/10.12688/f1000research.159997.2 (high); Hawassa "Graduate Research in African Universities: The State of
  Research Integrity" (2025) https://doi.org/10.1007/978-3-031-92909-0_10 ; Bule Hora "Impact of Research Integrity
  Challenges on Research Productivity" (2025) https://doi.org/10.4018/979-8-3373-3291-8.ch013 . MoE / Ethiopian Academy
  of Sciences policy not reached.
- Epistemics / gap framing: prevalence measured by self-report survey; no tooling or admissibility concept.
- Institutions & people: Addis Ababa Univ.; Ethiopian Defence Univ.; Hawassa Univ.
- Take / Ahead: take: nothing mechanical | ahead: n/a (different problem: prevalence, not verification).
- Confidence: medium. | Queries: OpenAlex ET ×2; Europe PMC ×1.

---

## Wave summary

**Method note for the whole wave.** First run: 24 WebSearch calls before the shared budget ended. Resumed run: 3 more
WebSearch answers (Denmark) and then refusal again; Bing results pages fetched with WebFetch were non-functional (empty or
off-topic for exact entity names, 12 attempts), so the remaining 22 countries and the four China items were covered with
primary-source APIs the tool can read directly — OpenAlex (country-filtered works, 2024–2026; note its search matches
full text, so hit counts are inflated and only title-level on-topic items are cited), the arXiv API, Europe PMC, Zenodo,
openstd.samr.gov.cn and institutional pages. Every country now has an entry; nothing is marked NOT SEARCHED.

**Top 5 findings for CAPAS:**
1. **NeurIPS 2026 workshop "AI for Science: Verification in the Age of AI Scientists"** (12 Dec 2026) names CAPAS's
   problem and has accepted papers on *executable dependency gates* and *falsifiable audits of surrogate verifiers*.
   https://neurips.cc/virtual/2026/workshop/137492
2. **GB/T 47468-2026 "Test methods for quantum computing system performance"** (量子计算系统性能测试方法), published
   30 Apr 2026, in force 1 Nov 2026, alongside GB/T 47177.2-2026 (QC service platform performance evaluation) and GB/T
   42565-2023 (terms). China now has a national test-method standard that Atlas/CAPAS calibration invariants should be
   mapped against; a test method says how to measure, not whether a reported number is admissible against a frozen
   snapshot — that remains CAPAS's ground. https://openstd.samr.gov.cn/bzgk/gb/std_list?p.p2=GB%2FT+47468
3. **Brodeur et al., PNAS Jun 2026** (Colombian co-authors): AI-led verification teams reproduced 37% vs 94% human-only;
   the measured cost of putting a model in charge of the verdict. https://doi.org/10.1073/pnas.2524747123
4. **China's own labs state the CAPAS thesis**: DeepSeek-R1 "we adopt a rule-based reward system… the neural reward model
   may suffer from reward hacking" (arXiv 2501.12948 §2.2.2); Tencent AI Lab "One Token to Fool LLM-as-a-Judge" (generative
   judges in RLVR fooled by a colon); Lean-kernel-verified provers (DeepSeek-Prover-V2, Kimina). Against this, Shanghai AI
   Lab's SCI-Verifier and the Alibaba/CAS generative-judge line put a model in the verdict. The split is the positioning
   map. https://arxiv.org/html/2501.12948v1 , https://arxiv.org/abs/2507.08794 , https://arxiv.org/abs/2504.21801
5. **Kirsch (CTU Prague), "Untrusted Authors, Trusted Answers" (Jul 2026)** — untrusted LLM plane, witness replay,
   certificates re-checked by a verified checker, Lean 4 core: the closest architectural sibling found in this wave, with a
   vocabulary (assurance classes, fidelity grades) CAPAS can borrow for CLOSED/BACKED/SCOPED. https://arxiv.org/abs/2607.14137
   Runners-up: AutoPyVerifier (Apr 2026); Ropovik et al. LLM-extraction benchmark (verbatim fields reliable, inferential
   not — supports ingest-from-files); Croatia's iRISE Delphi 8-measure consensus; Denmark's Jan-2026 Code and Pottegård's
   RWE preregistration registry; Egypt's ARI² author-risk index as a fraud-detection comparator.

**3 countries with the strongest direct work:** China (rule-based RLVR, Lean provers, judge-hacking evidence, GB/T
quantum test standard — and the opposite pole, SCI-Verifier), Canada (NeurIPS-workshop ecosystem, benchmarking-gated
quantum funding, Health Canada PCCPs), Czechia (Kirsch's fidelity-graded calculus, Charles/CTU theorem proving, Ropovik
meta-research). Next tier: Denmark, Croatia, Cyprus/Estonia (BEYOND).

**NOTHING FOUND (16):** Cabo Verde, Cambodia, Cameroon, Central African Republic, Chad, Comoros, Republic of the Congo,
DR Congo (adjacent-only), Côte d'Ivoire (adjacent-only), Djibouti, Dominica, Dominican Republic (adjacent-only),
El Salvador (adjacent-only), Equatorial Guinea, Eritrea, Eswatini.
**Adjacent-only, not counted as NOTHING FOUND:** Chile, Costa Rica, Cuba, Ecuador, Egypt, Ethiopia.
**NOT SEARCHED:** none.
