# World sweep 2026 — Wave 4 (Jamaica → Myanmar)

Date: 2026-10-14. Agent: wave-4 subagent. Template: BRIEF.md.

## Coverage statement (read before the entries)

**Run 1 (2026-10-14, morning).** The session-wide WebSearch budget (200 calls shared by every agent) ran out after
the 27th search, during the Laos query. Searched: Jamaica (1), Japan (12), Jordan (2), Kazakhstan (2), Kenya (3),
Kiribati (1), Kosovo (1), Kuwait (1), Kyrgyzstan (1). Fetch-only: Japan, Mexico, Malaysia, Luxembourg, Latvia.
23 countries were left NOT SEARCHED.

**Run 2 (2026-10-14, resumed).** The budget had refilled enough for **3 more WebSearch calls**, all spent on
Mexico ("SECIHTI ciencia abierta integridad científica 2026 México reproducibilidad"; "UNAM CINVESTAV IPN
metaciencia reproducibilidad crisis de replicación 2025 2026"; "'verificación' afirmaciones científicas inteligencia
artificial México 2026 investigación integridad alucinaciones"); the 4th–11th Mexico queries were refused
(COFEPRIS evidencia estadística; Principios de Chapultepec texto; Red Mexicana de Ciencia Abierta preregistro;
Ley IA México 2026; GRIM/statcheck México; Laboratorio Nacional de Supercómputo Coatlicue; and two more).
The caller suggested fetching Bing result pages instead; **I did not do that**: the budget notice attached to the tool
forbids routing around the limit through search engines, readers, proxies or archives, and the first run respected
the same rule. What I did instead, and declare here: **direct primary-source fetches only** — institutional sites,
their own site-search pages, and PDFs (downloaded with curl, text extracted with pdftotext). ~75 fetches.

Consequence for the labels below: an entry marked **NOTHING FOUND (fetch-only)** means "nothing relevant on the
primary pages reached, URLs listed"; it is weaker than a searched NOTHING FOUND and should be re-run with real
search when budget exists. No country is NOT SEARCHED any more; every one of the 36 wave-4 countries has an entry.

**Run 3 (2026-10-14, WebSearch budget restored).** Live WebSearch ran for the five countries the run-2 summary flagged:
**Mexico — all 8 planned queries ran** (SECIHTI ciencia abierta/integridad; UNAM/CINVESTAV/IPN metaciencia; "verificación
de afirmaciones científicas" IA México; COFEPRIS IA/evidencia estadística/SaMD; Red Mexicana de Ciencia Abierta /
reproducibilidad; GRIM/statcheck México; regulación IA México 2026 Senado [extended]; Coatlicue "AI for science") plus 9
primary fetches; **Lithuania 2, Malta 2, Morocco 2, Lebanon 2** queries. Every new claim below is marked "run 3" with
its URL and whether the source was read (fetched) or only seen as a search snippet. Not re-run in run 3: the other 31
wave-4 countries (their fetch-only labels stand).

Confidence labels: high = primary source read; medium = secondary source or snippet only; low = title/listing only.

---

### Jamaica
- Direct (2026 SOTA): none found.
- Adjacent: UWI joined the University of the West of Scotland's **IntegraGuard** proof-of-concept (AI-assisted
  detection + investigation workflow + policy compliance + institutional reporting) for *academic* misconduct;
  UWS delegation at Mona 23–28 Apr 2026, UWI-adapted version presented
  (https://www.cavehill.uwi.edu/news-events/ch-news/news-releases/2026-news-releases/april-2026-news-releases/uwi-to-use-ai-assisted-system-to-manage-misconduct-amid-ai-boom-in-education/, 4 May 2026).
  Student-facing, not research-claim verification. Mona Office for Research & Innovation runs research compliance
  (https://www.mona.uwi.edu/mori/services/research-compliance). UTech student handbook 2025–26 carries generic AI
  guidelines (https://utech-web-srv.utech.edu.jm/publications/studenthandbook/264/).
- Epistemics / gap framing: integrity framed as misconduct management (detect-and-adjudicate), not as evidence
  admissibility; no fail-closed language.
- Institutions & people: UWI Mona (MORI, MCREC); Dr Stephen Langston (UWS, IntegraGuard creator); Prof. Carmel Roofe
  (UWI School of Education).
- Take / Ahead: take: nothing technical | ahead: CAPAS gates evidence fields; IntegraGuard classifies text with AI
  (exactly the "LLM in the verdict" CAPAS excludes).
- Confidence: medium | Queries: "Jamaica research integrity reproducibility UWI Mona 2025 2026 AI research policy"
  + 1 fetch.

### Japan (rich entry)
- Direct (2026 SOTA):
  1. **LLM-Assisted Replication for Quantitative Social Science** (Kubota, Yakura, Coavoux, Yamada, Nakamura;
     Tohoku U / U Tokyo + FR/DE; arXiv 2602.18453, 4 Feb 2026). System re-runs statistical analyses from papers and
     flags discrepancies; loop = LLM text interpretation → code generation → execution → "discrepancy analysis";
     applications named: pre-submission checks, peer-review support, meta-scientific audits. Whether the discrepancy
     verdict is deterministic or LLM is not stated on the abstract page. Code: github kubotaso/AI_Social_Replication
     (https://arxiv.org/abs/2602.18453). Confidence high on existence, medium on method.
  2. **ReAgent — "Beyond the Text: Verifying That Agent-Written Papers Are Backed by Their Artifacts"**
     (Shen, Wu, Liu, Qi, Chen; arXiv 2609.22111, 18 Aug 2026). Static audit (methods/configs present in repo) +
     dynamic audit (re-execute experiments, collect execution evidence); catches hard-coded metrics and
     reproduce-the-number-but-not-the-method. Affiliations not shown (surfaced in a Japan query; may not be Japanese —
     flag, do not credit to Japan) (https://arxiv.org/abs/2609.22111). Confidence medium.
  3. **Prover Agent / Lean Atlas** (Kaito Baba U Tokyo, Chaoran Liu & Shuhei Kurita NII, Akiyoshi Sannai Kyoto):
     agent-based formal proof framework presented at AIPV workshop, FM 2026 Tokyo, May 2026; Lean Atlas (arXiv
     2604.16347) targets "semantic hallucination" in human-AI formalization
     (https://conf.researchr.org/profile/fm-2026/akiyoshisannai, https://arxiv.org/pdf/2604.16347). Confidence medium.
  4. **Sakana AI "AI Scientist"**: independent evaluation (Beel, Kan, Baumgart, arXiv 2502.14297, Feb 2025) found
     hallucinated numerical results and 42% of experiments failing on coding errors; the system's own reviewer rejected
     7/7 of its papers and 9/10 human papers (conservative bias)
     (https://arxiv.org/pdf/2502.14297). Secondary sources say a methodology paper appeared in Nature 26 Mar 2026 and
     that runs modified their own execution script to bypass timeouts — unverified, low confidence
     (https://blog.nicolasmeridjen.com/en/blog/2026-04-01-ai-scientist-nature-paper-automated-research/). No v3, no
     official verification sandbox found.
- Adjacent:
  - **RIKEN AGIS** (Advanced General Intelligence for Science, TRIP initiative, since Apr 2024; PD Makoto Taiji):
    science foundation models, robotic automated chemistry, "Rikyu" supercomputer (Mar 2026); June 2026 Japan–US
    cooperation on the US Genesis Mission. The 19 Jun 2026 feature contains **no discussion of verification,
    reproducibility or hallucination control** (https://www.riken.jp/pr/closeup/2026/20260619_1/index.html). High.
  - **MEXT Basic Strategic Policy for AI for Science** (31 Mar 2026) → **JST ARiSE** program (call 12 May–30 Jun 2026):
    foundation models + AI agents + AI-driven labs; verification not a stated focus in the call excerpts
    (https://www.jst.go.jp/pr/info/info1848/index_e.html). Medium.
  - **JST ↔ G-Search (Fujitsu) contract, 31 Mar 2026**: JST's bibliographic database repositioned explicitly as
    "high-quality, high-reliability structured data" *because* generative AI hallucination makes provenance-clean
    grounding data valuable; new AI services from Apr 2027 (https://www.jst.go.jp/pr/announce/20260331-2/pdf/20260331-2.pdf,
    PDF read locally). High. This is the Japanese institutional version of CAPAS's "machine-context ingestion".
  - **J-AISI Guide to Evaluation Perspectives on AI Safety v1.20** (Jul 2026; v1.00 Sep 2024), updated for AI agent
    systems; FY2025 AI Safety Evaluation Environment Task Force report (15 Apr 2026)
    (https://aisi.go.jp/output/output_framework/guide_to_evaluation_perspective_on_ai_safety/,
    https://aisi.go.jp/assets/pdf/20260415_2_aisev_taskforce_studyreport_summary_en.pdf). Determinism not addressed. High.
  - **AIST Machine Learning Quality Management Guideline** (4th JP ed. Dec 2023; 3rd EN ed. Jan 2023) + Qunomon
    testbed + ISO/IEC TR 5469:2024 work (https://www.digiarc.aist.go.jp/en/publication/aiqm/,
    https://www.ipri.aist.go.jp/cctrg/en/). No 2025–26 edition found. High.
  - **AI Promotion Act** (passed 28 May 2025, in force 1 Sep 2025, soft law, no penalties) + AI Strategic HQ
    "Guidelines for Ensuring the Appropriateness of R&D and Utilisation of AI-Related Technology" (19 Dec 2025,
    voluntary) (https://www.cliffordchance.com/content/dam/cliffordchance/briefings/2026/04/japan-ai-act-guidelines-april-2026.pdf). Medium.
  - **Quantum**: RIKEN–Fujitsu 256-qubit (Apr 2025), 1,000-qubit target 2026 (unconfirmed); Hayata & Yamamoto,
    *Quantum anomaly for benchmarking quantum computing*, PRR 22 Sep 2026 — axial anomaly coefficient reproduced on
    trapped-ion "Reimei" without error mitigation, i.e. a **textbook-invariant benchmark** of the same genus as CAPAS's
    quantum invariants (https://journals.aps.org/prresearch/abstract/10.1103/l8w6-pk4m). Osaka drift-control result
    Mar 2026 (https://qih.riken.jp/en/archive.html). No national calibration-reporting standard found. Medium.
  - **PMDA**: project team on AI guiding principles May 2026 (vendor blog only, unverified)
    (https://www.trinka.ai/blog/?p=7668). Low. No PMDA statement on AI-generated evidence found.
  - Preregistration/registered reports in Japanese psychology: nothing found in one search.
- Epistemics / gap framing: Japan's institutional answer to AI-era unreliability is **provenance of inputs**
  (JST/G-Search "evidence-based information", J-AISI evaluation perspectives, AIST quality goals) and **soft-law
  self-governance**; the flagship AI-for-Science program (AGIS/ARiSE) is fail-open by omission — verification is not
  in the mandate text found. Formal-methods community (FM 2026 in Tokyo, AIPV workshop) is where "no model in the
  verdict" lives, but it targets math proofs, not empirical claims.
- Institutions & people: RIKEN AGIS (Makoto Taiji); JST ARiSE / CRDS; J-AISI (IPA); AIST DigiARC (AIQM); NII
  (Shuhei Kurita); U Tokyo (Kaito Baba, Hiromu Yakura); Tohoku U (So Kubota); Kyoto U (Akiyoshi Sannai); Sakana AI;
  RIKEN RQC–Fujitsu; Osaka QIQB; Keio/U Tokyo (Hayata, Yamamoto).
- Take / Ahead: take: (a) ReAgent's static+dynamic repo audit is a concrete adapter pattern for CAPAS's
  "reproducibility artifact" field (run-and-compare rather than declare); (b) Kubota's replication loop is the
  social-science analogue of Atlas→CAPAS and a candidate corpus; (c) the anomaly-coefficient benchmark is a new
  textbook invariant for capas_quantum_physics | ahead: Japan has no sealed-blind protocol, no proof ledger, no
  fail-closed default anywhere found; its replication tool keeps an LLM in the loop for the discrepancy call;
  AGIS/ARiSE have no verification stance.
- Confidence: high/medium as marked | Queries (12): RIKEN AI for science verification; AIST AIQM 2025–26; JST AI for
  science reproducibility; Japan reproducibility metascience; RIKEN Fujitsu quantum benchmarking; Japan Lean
  autoformalization; Sakana peer review; J-AISI evaluation guide; arXiv 2602.18453 (ext); PMDA AI evidence; Sakana v2/v3
  sandbox (ext); Japan quantum volume/calibration standard (ext); AI Promotion Act MEXT; Japan preregistration
  psychology. + 7 fetches.

### Jordan
- Direct (2026 SOTA): none found.
- Adjacent: AI Strategy & Implementation Plan 2023–2027 (68 projects; R&D centres, AI research funding)
  (https://dig.watch/resource/jordanian-artificial-intelligence-strategy-and-implementation-plan-2023-2027);
  National AI Code of Ethics (Council of Ministers, 3 Aug 2022) — principles include transparency, "disclosure of
  system performance and limitations", performance evaluation under reliability
  (https://dig.watch/resource/the-national-artificial-intelligence-code-of-ethics-of-jordan). Royal Scientific Society
  does accredited testing (https://en.wikipedia.org/wiki/Royal_Scientific_Society) — plausible verification venue, no
  AI-specific work found. 2016–17 study on responsible-conduct training demand at U of Jordan health schools
  (https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7175529/).
- Epistemics / gap framing: limits-disclosure appears as an ethics principle (2022), no operational mechanism.
- Institutions & people: MoDEE; RSS; University of Jordan.
- Take / Ahead: take: "disclosure of performance and limitations" as a policy hook for the measured-limits section |
  ahead: everything mechanical.
- Confidence: medium | Queries: "Jordan research integrity reproducibility AI research verification 2025 2026
  university"; "Jordan AI strategy 2025 2026 Royal Scientific Society OR Jordan University AI research ethics
  verification reproducibility" (ext).

### Kazakhstan
- Direct (2026 SOTA): none found.
- Adjacent: **AI Law** passed second reading Sep 2025 (education amendments)
  (https://astanatimes.com/2025/09/kazakhstan-enacts-ai-law-parliament-weighs-opportunities-and-risks/);
  Inter-University Standard for AI use (2024): disclose tool/algorithm, author finalizes conclusions; ministry says AI
  detectors "cannot serve as indisputable proof" because probabilistic (https://timesca.com/ai-in-kazakh-universities/).
  Journal policy (ENU) requires naming technology, developer, version, access date; Order No. 127/2021 as amended
  Jan 2025 (https://tsj.enu.kz/index.php/new/Screeningforplagiarism). ISSAI (Nazarbayev U) exec director Yerbol
  Absalyamov, 16 Jan 2026: AI tools "support reproducibility" in PhD programs — vision only, no system named beyond a
  subtitle service (https://issai.nu.edu.kz/2026/01/16/issai-executive-director-presents-ai-driven-approaches-at-national-forum-in-astana/).
  Elsevier Kazakhstan research-integrity conference 7 Oct 2026 Almaty, "AI Law in science"
  (https://www.elsevier.com/de-de/events/conferences/all/kazakhstan-international-research-conference-2026).
- Epistemics / gap framing: notable: a ministry explicitly refusing probabilistic detectors as proof — a fail-closed
  instinct about *evidence of misconduct*, not about claims.
- Institutions & people: Nazarbayev U (ISSAI, Office of Research Compliance & Integrity); MoSHE (Sayasat Nurbek);
  ENU; Antiplagiat.Kazakhstan / I-Sana.
- Take / Ahead: take: the provenance-disclosure fields (tool, developer, version, date) match CAPAS's declared-source
  schema and could be a Kazakh-journal adapter | ahead: no claim-level verification at all.
- Confidence: medium | Queries: "Kazakhstan research integrity reproducibility AI science verification Nazarbayev
  University 2025 2026"; "Kazakhstan AI law 2025 2026 science research evaluation plagiarism antiplagiat higher
  education" + 1 fetch.

### Kenya
- Direct (2026 SOTA): none found.
- Adjacent: **Draft Kenya AI & Emerging Technologies Policy 2026** (full-lifecycle incl. research; carve-out for
  research-only controlled systems; consultation closed 4 Aug 2026)
  (https://ict.go.ke/sites/default/files/AI%20Policy%20Doc/draft-kenya-ai-and-emerging-technologies-policy-2026.pdf);
  separate Senate **AI Bill No. 4 of 2026** (Office of the AI Commissioner), not aligned with the policy
  (https://www.parliament.go.ke/sites/default/files/2026-04/Bill%20Digest%20-%20The%20Artificial%20Intelligence%20Bill%2C%20No.4%20of%202026.pdf,
  https://bowmanslaw.com/insights/kenya-artificial-intelligence-bill-2026-proposed-too-soon/). National AI Strategy
  2025–2030; ISC briefing Feb 2026: AI funding mostly foreign, shift toward foundational research
  (https://council.science/wp-content/uploads/2026/02/Kenya-AI.pdf). **NACOSTI Research Integrity Workshop** (posted
  10 Sep 2025; TCC Africa + Digital Science): Leslie McIntosh (Ripeta) "Trustmakers" transparency indicators; Oransky:
  retractions far below actual misconduct; KEMRI RI Committee (Bukusi); no AI or reproducibility content
  (https://www.nacosti.go.ke/2025/09/10/kenya-research-integrity-workshop/). Strathmore iLabAfrica AI+quantum forum
  May 2026 (https://ilabafrica.strathmore.edu/kenya-and-italy-convene-global-experts-to-advance-ai-and-quantum-research-agenda/).
- Epistemics / gap framing: integrity = culture + ORCID/transparency indicators (Ripeta-style "trust markers");
  regulation = governance bodies. No evidence-admissibility framing.
- Institutions & people: NACOSTI (David Ngigi); KEMRI (Elizabeth Bukusi); Strathmore iLabAfrica; Dedan Kimathi CDSAI;
  Ministry of ICT & Digital Economy.
- Take / Ahead: take: Ripeta "Trustmakers" indicators as a prose-side complement CAPAS does not do | ahead: Kenya's
  integrity stack is indicator-based and human-adjudicated; nothing deterministic.
- Confidence: medium | Queries: "Kenya research integrity reproducibility metascience AI research policy 2025 2026";
  "Kenya Artificial Intelligence policy 2026 draft bill research science NACOSTI AI guidelines" (ext); "Kenya AI
  research lab 2026 verification evaluation benchmark Nairobi…" + 1 fetch.

### Kiribati
- NOTHING FOUND (queries: "Kiribati research science policy AI 2025 2026" — results were Kenya/EU/Kazakhstan only).
- Confidence: low (1 search).

### Kosovo
- Direct (2026 SOTA): none found.
- Adjacent: 2025 qualitative study of 20 master's students (U Prishtina, Kadri Zeka) on AI in academic research
  (https://revistas.uepg.br/index.php/praxiseducativa/article/view/26164); ResearchCult project (ethics regulations,
  ethics committees, OA platform; 2020–21 era)
  (https://old.uni-prizren.com/en/researchcult-project.html).
- Epistemics / gap framing: capacity-building stage.
- Institutions & people: University of Prishtina.
- Take / Ahead: take: nothing | ahead: all.
- Confidence: medium | Queries: "Kosovo research integrity AI science verification reproducibility 2025 2026
  university Prishtina".

### Kuwait
- Direct (2026 SOTA): none found.
- Adjacent: Kuwait University "encourages the optimal use of Generative AI" in teaching and research (search-page
  snippet only) (https://www.ku.edu.kw/search?page=271); national AI strategy 2025–2028 described by a compliance
  vendor (https://digital.nemko.com/regulations/kuwait-ai-regulation). KISR: nothing current.
- Epistemics / gap framing: not visible.
- Institutions & people: Kuwait University; KISR; KFAS.
- Take / Ahead: take: nothing | ahead: all.
- Confidence: low | Queries: "Kuwait research integrity AI science reproducibility KISR Kuwait University 2025 2026
  AI strategy".

### Kyrgyzstan
- Direct (2026 SOTA): none found.
- Adjacent: Erasmus+ Kyrgyzstan: AI "still emerging", faculty retraining urgent, AI research funding ≈ US$1M/yr,
  ethics (transparency, bias) "yet to be codified"
  (https://erasmusplus.kg/en/follow-up-workshop-on-ai-in-kyrgyz-higher-education-from-insight-to-action-applying-tam-outcomes-on-ai-in-kyrgyz-higher-education/).
- Epistemics / gap framing: pre-policy.
- Institutions & people: AUCA, Osh State, Adam University.
- Take / Ahead: take: nothing | ahead: all.
- Confidence: medium | Queries: "Kyrgyzstan research integrity AI science reproducibility 2025 2026 universities
  digital".

### Laos
- Direct (2026 SOTA): none found (fetch-only).
- Adjacent: NUOL news: MoU with Lao Telecom on ICT & **AI infrastructure** (12 Oct 2026) and the 2nd Lao Social
  Science Research Seminar (8 Oct 2026) (https://nuol.edu.la/); MTC "National Digital Economy Vision, Strategy and
  Development Plan" (undated, image path Aug 2025) (https://mtc.gov.la/index.php?r=site/contents&id=29). No research
  integrity, reproducibility or AI-verification policy on either site.
- Epistemics / gap framing: infrastructure stage.
- Institutions & people: National University of Laos; Ministry of Technology and Communications.
- Take / Ahead: take: nothing | ahead: all.
- Confidence: low | Queries: none (budget) | Fetches: nuol.edu.la, mtc.gov.la. **NOTHING FOUND (fetch-only).**

### Latvia
- Direct (2026 SOTA): none found (fetch-only).
- Adjacent: Latvian Council of Science posted Science Europe's *Science Communication and Research Culture*
  guidelines (Oct 2026; integrity + AI challenges named, no reproducibility)
  (https://www.lzp.gov.lv/en/article/guidance-document-science-communication-and-research-culture); research-environment
  survey incl. open science, 12 Oct 2026
  (https://www.lzp.gov.lv/en/article/latvias-research-community-invited-share-their-views-research-environment-latvia).
- Epistemics / gap framing: research-culture framing, EU-aligned.
- Institutions & people: Latvijas Zinātnes padome.
- Take / Ahead: take: nothing | ahead: all.
- Confidence: low | Queries: none (budget); 2 fetches of lzp.gov.lv.

### Lebanon
- Direct (2026 SOTA): none found (fetch-only).
- Adjacent: **CNRS-L Charter of Ethics of Scientific Research** (dated 4 Feb 2017; PDFs re-uploaded Nov 2025:
  https://cnrs.edu.lb/wp-content/uploads/2025/11/new_Charter_of_Ethics_En.pdf) — general integrity framework, no
  data/reproducibility/AI provisions on the landing page (https://cnrs.edu.lb/publication/charter-of-ethics/).
  CNRS-L news Aug–Sep 2026 is entirely hazards/early-warning and war-damage documentation (https://cnrs.edu.lb/news/).
  **AUB Research Integrity**: misconduct policy, authorship-dispute arbitration, safe-reporting policy, COI; no AI
  policy, no RCR training listed (https://www.aub.edu.lb/urb/Pages/Researchintegrity.aspx); AUB "AI Hub" exists
  (https://www.aub.edu.lb/hub/Pages/default.aspx, no policy content).
- Run 3 (2 searches): the only Lebanese AI-and-research items are an event series by **USJ's Mission pédagogique
  universitaire with the Lebanese National Commission (UNESCO)**: roundtable "Positioning of Universities in Lebanon
  Regarding the Use of AI" (16 Dec 2025), "Rethinking the Design of Students' Research Work in Lebanese Universities in
  the Era of AI" (Apr 2026), and a Jun 2026 session on assessment "that reconcile[s] the advantages of AI tools with
  academic integrity" with AUB speakers — https://www.usj.edu.lb/intranet/actu/pdf/18123_4161.pdf (404 on fetch;
  snippet only, low-medium). Antonine University strategic plan 2025–28 "Research Advancement" (snippet). No
  reproducibility, open-science, registered-reports or AI-verification item for any Lebanese institution.
- Epistemics / gap framing: integrity = 2017 conduct charter + institutional misconduct procedure; no AI-era update
  found; research capacity is absorbed by crisis monitoring.
- Institutions & people: CNRS-L; AUB (University Research Board, Provost as misconduct officer).
- Take / Ahead: take: nothing technical | ahead: all mechanical.
- Confidence: medium-low | Queries: run 2 none (budget); run 3: "Lebanon research integrity AI policy AUB / CNRS-L /
  LAU 2025 2026"; "Lebanon reproducibility / open science / registered reports 2025 2026" | Fetches: cnrs.edu.lb ×3,
  aub.edu.lb ×3 (one 404); run 3: usj.edu.lb PDF (404).

### Lesotho
- NOTHING FOUND (fetch-only). NUL homepage shows student AI/monitoring projects only, no research-integrity, AI or
  open-science policy (https://www.nul.ls/). Confidence: low | Queries: none (budget).

### Liberia
- NOTHING FOUND (fetch-only). University of Liberia homepage links an IRB page, "UL Policies" and Turnitin; no
  integrity/AI/open-science content visible (https://www.ul.edu.lr/). Confidence: low | Queries: none (budget).

### Libya
- NOTHING FOUND (fetch-only, not reachable). University of Tripoli returned HTTP 522 twice (https://uot.edu.ly/);
  lasr.ly (Libyan Authority for Scientific Research) did not resolve. Nothing can be claimed. Confidence: none |
  Queries: none (budget).

### Liechtenstein
- Direct (2026 SOTA): none found (fetch-only).
- Adjacent: **University of Liechtenstein "Better Science Policy"** — integrity page lists honesty/transparency,
  **"verifiability and reproducibility"**, originality/authorship, ethics; Research Support Office + independent
  ombudsperson; 5-step misconduct procedure; no AI or data-management rules
  (https://www.uni.li/en/research/research-funding/research-strategy/integrity; policy text /legal?id=253.67).
  Research strategy focus: Innovation, Digitalisation, Sustainability, Responsibility
  (https://www.uni.li/en/research/research-funding/research-strategy). News 8 Oct 2026: ML stock portfolios "not
  without economic judgement" (https://www.uni.li/en/news/2026/10/when-machines-help-build-portfolio).
- Epistemics / gap framing: Swiss-style good-scientific-practice code; verifiability named as a principle, no mechanism.
- Institutions & people: University of Liechtenstein (Research Delegate Prof. Michael Hanke).
- Take / Ahead: take: nothing | ahead: all mechanical.
- Confidence: medium (pages read) | Queries: none (budget) | Fetches: uni.li ×3.

### Lithuania (strongest of the 23 re-run countries)
- Direct (2026 SOTA): none found (fetch-only; Research Council lmt.lrv.lt returns 403; VU open-science page 404).
- Adjacent: **Office of the Ombudsperson for Academic Ethics and Procedures** (Dr Reda Cimmperman) — a statutory
  national integrity body. **Guidelines on the Ethical Use of AI in Education and Research** (Aug 2024, PDF read:
  https://etikostarnyba.lt/wp-content/uploads/2024/08/Guidelines-on-the-ethical-use-of-artificial-intelligence-in-education-and-research.pdf).
  Section VIII "Evaluation and validation of AI tools": §30 before use "the soundness and reliability (validity) of
  the results the AI produces must be analysed by competent professionals… tools… **must be subject to a preliminary
  verification**"; §31 "regular audits and evaluations"; §32 validation criteria incl. **"methodological soundness
  (compliance with the basic principles of scientific methodology)"** and reliability (fake/inaccurate content →
  report, restrict or ban); §35 "additional analysis of the results"; §36 GenAI "make up facts and make errors in
  reasoning… should not rely on the information provided… fabrication of GenAI information (non-existent scientific
  publications)". Also: Crisis Navigator (Mar 2026); Guidelines for Science Communication in line with academic ethics
  (Oct 2025) (https://etikostarnyba.lt/en/recommendations/). **International conference "Open but Secure Science"
  2 Oct 2026** at the Lithuanian Academy of Sciences, with the first ENRIO meeting in Lithuania (6 Oct 2026); speakers
  Marušić, Hiney, Tsinorema, OECD; **"Responsible Science Barometer 2026": 27% of researchers encountered misconduct
  by others in 3 years**; the article notes decisions affect "other researchers' ability to verify findings"
  (https://etikostarnyba.lt/en/open-and-secure-science-can-we-achieve-both/). 1 Sep 2026: "In the AI era, what
  matters most is not prohibitions, but responsibility" (no disclosure/verification rule)
  (https://etikostarnyba.lt/en/in-the-ai-era-what-matters-most-is-not-prohibitions-but-responsibility/).
- Run 3 (2 searches): **Lithuanian Energy Institute "Academic ethics" brochure, May 2026** (project eMoDB.LT3; built on
  the Ombudsperson Guidelines + LEI Code; PDF read): "**IMPORTANT. When using AI tools, it is necessary to check all
  created content!**"; "the choice of AI tools must be transparent, justified, and declared"; authors citing GenAI results
  "should specify the generative AI tool used and the date of its use"; researchers "when making data public, should
  assess the research security risks posed by the development of generative AI" —
  https://www.lei.lt/wp-content/uploads/2026/05/Brochure_academic-ethics_LEI-2026_EN-1.pdf. LMT: the 2016 Guidelines on
  Open Access expire 2028; a KTU slide deck (Nov 2024, snippet) lists a 2026 OA action plan + monitoring procedure
  (https://data.ktu.edu/wp-content/uploads/2024/11/2024.11_Gribauskiene.pdf, not read). No Lithuanian reproducibility
  network, statcheck-type tool or 2025–26 LMT AI-integrity document surfaced; Lithuania ranks 3rd in the CEE AI Index 2026
  (Forbes.ro snippet, via the Romania query).
- Epistemics / gap framing: validation is placed on the **tool, before use, by the institution** (preliminary
  verification + audits + methodological soundness), with the human fully responsible for outputs; nothing at claim
  level, nothing deterministic; research security now framed alongside integrity.
- Institutions & people: Ombudsperson for Academic Ethics and Procedures (Reda Cimmperman); Lithuanian Academy of
  Sciences; Research Council (LMT, unreachable); ENRIO.
- Take / Ahead: take: §30–§32 is a standing national requirement that institutions verify and audit AI tools for
  "methodological soundness" — CAPAS is a mechanical way to meet it and the Barometer gives a measured base rate to
  cite; the ENRIO network is a venue | ahead: Lithuania validates tools and people; CAPAS validates claims, blind and
  sealed; no fail-closed default, no ledger there.
- Confidence: medium-high (PDF + 3 pages read) | Queries: run 2 none (budget); run 3: "Lithuania Research Council LMT
  AI research integrity guidelines 2026 open science"; "Lithuania reproducibility network / research assessment reform
  Vilnius 2025 2026" | Fetches: etikostarnyba.lt ×4 (+PDF), lmt.lrv.lt (403), vu.lt (404); run 3: lei.lt PDF.

### Luxembourg
- Direct (2026 SOTA): none found (fetch-only).
- Adjacent: **FNR Guidelines on Generative AI** (status April 2026): applicants may use GenAI, no disclosure required,
  full responsibility on applicant/institution; **reviewers barred** from AI tools (leakage, bias)
  (https://www.fnr.lu/fnr-guidelines-on-generative-artificial-intelligence-ai/). **LARI** (est. 2016; ENRIO/ENAI/CoARA
  member): prevention + investigation; no AI/reproducibility guidance dated 2025–26 (https://lari.lu/). FNR mission on
  new legal basis 29 Jul 2026 (https://www.fnr.lu/the-fnrs-mission-on-a-new-legal-basis/). LIST research page returned
  404; no trustworthy-AI group verified.
- Epistemics / gap framing: funder treats AI output as the author's liability (accountability transfer), not as
  something to verify — the opposite of a gate.
- Institutions & people: FNR; LARI; LIST (unverified); University of Luxembourg (not fetched).
- Take / Ahead: take: the asymmetric rule (authors may, judges may not) is a clean statement of "no model in the
  verdict" at policy level — quotable | ahead: CAPAS makes the verdict mechanical, FNR only forbids one kind of judge.
- Confidence: medium | Queries: none (budget); 4 fetches.

### Madagascar
- Direct (2026 SOTA): none found (fetch-only).
- Adjacent: MESUPRES runs **FOSIKA**, a platform for reporting academic fraud / fake diplomas / harassment
  (https://fosika.mesupres.mg/), the HAE accreditation platform (https://qualite.mesupres.mg/), a call for articles to
  the Revue Scientifique de Madagascar vol. 1 (20 Sep 2025) and recruitment of experts for the États Généraux de
  l'ESR (10 Sep 2025) (https://www.mesupres.gov.mg/). No AI, reproducibility or research-integrity policy text found.
- Epistemics / gap framing: integrity = fraud reporting channel (credentials), not evidence.
- Institutions & people: MESUPRES.
- Take / Ahead: take: nothing | ahead: all.
- Confidence: low | Queries: none (budget) | Fetches: mesupres.gov.mg.

### Malawi
- Direct (2026 SOTA): none found (fetch-only).
- Adjacent: **NCST** took part in the validation workshop of the **Malawi AI Readiness Assessment Methodology (RAM)
  report** (UNESCO RAM; image dated Jul 2026)
  (https://ncst.mw/ncst-takes-part-in-validation-workshop-for-the-malawi-artificial-intelligence-readiness-assessment-methodology-ram-report/);
  Technology Needs Assessment 2026 report; "Why research governance matters for Africa" (Oct 2025, Science for Africa
  Foundation); Ethics & Standards, research clearance and protocol-review pages (https://ncst.mw/ethics/).
- Epistemics / gap framing: integrity = ethics clearance of protocols; AI = readiness assessment.
- Institutions & people: NCST Malawi; Science for Africa Foundation (Evelyn Gitau).
- Take / Ahead: take: nothing technical | ahead: all mechanical.
- Confidence: low-medium | Queries: none (budget) | Fetches: ncst.mw.

### Malaysia
- Direct (2026 SOTA): none found (fetch-only).
- Adjacent: **AI Malaysia Berhad / National AI Office** launched 28 Jul 2026; **National AI Action Plan 2026–2030**
  (14 impact engines + 14 enablers)
  (https://strapi.naio.okie.my/uploads/AI_Nation_2030_National_AI_Action_Plan_2026_2030_EN_V_180826_ddf0221683.pdf).
  **MY-AISafe (Malaysia AI Safety Institute)**, announced 28 Jul 2026, delivers enabler **E12 "AI Trust Function"**:
  "tests, benchmarks and evaluation reports" against the 7 AIGE (2024) principles — reliability/safety via robustness
  testing and red teaming; accountability via "a named owner and incident reports"; Evaluation & Certification,
  Incident Monitoring & Forensics, standards (https://strapi.naio.okie.my/uploads/Malaysia_AI_Safety_Institute_Overview_1_86540498a4.pdf,
  PDF read locally; https://ai.gov.my/my-aisafe/). **AICE** AI Code of Ethics (Jul 2026, voluntary)
  (https://ai.gov.my/governance/ai-code-of-ethics-aice/). MOSTI: Malaysia Open Science Platform (https://mosp.gov.my/),
  RADARS raw-data repository (https://radars.mosti.gov.my/), MIMOS Quantum Day 2026
  (https://www.mosti.gov.my/en/berita/mimos-quantum-day-2026/). No research-integrity/reproducibility items on MOSTI.
- Epistemics / gap framing: "from responsible-AI principles to real-world evidence" — testing/certification mindset,
  incident forensics; no claim-level or scientific-evidence framing; nothing deterministic stated.
- Institutions & people: AI Malaysia Berhad (Kementerian Digital); MY-AISafe; MOSTI; MIMOS; MOSP.
- Take / Ahead: take: MY-AISafe's "named owner + incident report" accountability pair maps to CAPAS's audit hash +
  proof ledger; a certification body is a possible beachhead for the CAPAS mark | ahead: CAPAS has a running
  fail-closed engine with sealed blind numbers; MY-AISafe is a 4-page mandate as of Oct 2026.
- Confidence: medium-high (primary PDFs) | Queries: none (budget); 5 fetches.

### Maldives
- NOTHING FOUND (fetch-only). Maldives National University lists a Research Ethics page (link only), the MNJR journal
  and the Saruna repository; no integrity/AI/reproducibility content (https://mnu.edu.mv/). Confidence: low |
  Queries: none (budget).

### Mali
- NOTHING FOUND (fetch-only). USTTB Bamako homepage: news only (US official praises Malian biomedical research, 17 Jul
  2026); "Textes règlementaires" section unread (https://www.usttb.edu.ml/). Confidence: low | Queries: none (budget).

### Malta
- Direct (2026 SOTA): none found. Run 3 (2 searches) reached MDIA only through snippets (mdia.gov.mt/sandbox and the
  sustainability.gov.mt PDF both 403 on fetch): **MDIA Technology Assurance Sandbox (MDIA-TAS)** — residency up to four
  years, each phase closed by an independent assessment by an MDIA-authorised Systems Auditor, full certification at the
  end, voluntary ("recommends that the sector's lead regulator mandate certification"), aligned to the EU AI framework —
  https://mdia.gov.mt/sandbox/ , https://oecd.ai/en/dashboards/policy-initiatives/malta-digital-innovation-authoritys-technology-assurance-sandbox-8999 ;
  a **Mark of Credit** under the Technology Assurance Regulatory Framework (TARF), Assessment Level 1, to "IDPS: Smart
  Utilities AI Pilot Project" (Ministry for the Environment, Energy and Public Cleanliness), effective 1 Jan–31 Dec 2026,
  document dated 16 Apr 2026 — https://sustainability.gov.mt/wp-content/uploads/2026/05/Mark-of-Credit-MEEC-redacted_.pdf
  (snippet; medium-low). Auditor-certified assurance of *systems*, not of claims; nothing on research.
- Adjacent: **University of Malta Research Ethics Code of Practice and Procedures (May 2026)** replaces the earlier
  Research Code of Practice; **FAQ "Researcher Responsibility for Secure Data Storage and Use of AI" (Feb 2026)** —
  external AI tools (incl. transcription/analysis) mean uploading data to third parties, which "must be explicitly
  specified and consented to by participants beforehand"; **no rule on verifying AI outputs or disclosing AI in
  publications** (https://www.um.edu.mt/research/ethics/faqs/, https://www.um.edu.mt/research/ethics/whatsnew/);
  link to the EU Living Guidelines on Responsible Use of GenAI in Research (Apr 2025). **Xjenza Malta** (ex-MCST):
  call for independent expert evaluators (15 Jul 2026), €1.7M thematic R&I funding (30 Sep 2026), R&I Strategic Plan
  2023–2027; nothing on integrity/reproducibility (https://xjenzamalta.mt/).
- Epistemics / gap framing: AI is framed as a **data-protection** risk (consent, storage), not an epistemic one.
- Institutions & people: University of Malta UREC; Xjenza Malta; MDIA (unverified).
- Take / Ahead: take: nothing technical; MDIA assurance scheme worth a real search later | ahead: all mechanical.
- Confidence: medium | Queries: run 2 none (budget); run 3: "Malta MDIA AI technology assurance sandbox 2026
  certification"; "Malta research integrity University of Malta reproducibility AI research policy 2026" (UM: student
  "AI Journal" for assignments, teaching-side only; no research-AI rule) | Fetches: um.edu.mt ×3, xjenzamalta.mt,
  mdia.gov.mt ×2 (403); run 3: mdia.gov.mt/sandbox (403), sustainability.gov.mt PDF (403).

### Marshall Islands
- NOTHING FOUND (fetch-only, not reachable). College of the Marshall Islands returned HTTP 403 (https://www.cmi.edu/).
  Confidence: none | Queries: none (budget).

### Mauritania
- NOTHING FOUND (fetch-only, not reachable). Université de Nouakchott: ECONNRESET, then HTTP 404 (https://www.una.mr/).
  Confidence: none | Queries: none (budget).

### Mauritius
- NOTHING FOUND (fetch-only). MRIC homepage: National Research Week 2026, Call for Proposals 2026, GII items; no
  integrity/AI/open-science item (https://www.mric.mu/). University of Mauritius: Research Compliance page (link),
  Turnitin, data-protection policy, GenAI/agentic-AI short course 2026 — no research-AI guidance
  (https://www.uom.ac.mu/). Confidence: low | Queries: none (budget).

### Mexico (home country — run 2: 3 searches + 20 fetches; run 3: 8 searches + 9 fetches; rich entry)
- Direct (2026 SOTA): **none**. No Mexican deterministic claim-gating, statcheck/GRIM-style tooling, registered-reports
  program, LLM-vs-deterministic-verifier work, or "verification of AI-generated scientific claims" project surfaced in
  3 searches or on any primary page. The query on *verificación de afirmaciones científicas + IA + México 2026*
  returned only blogs/LinkedIn posts on hallucinations (Arsys, Universidad de Belgrano) — no Mexican system.
  The home-market competitive field is empty as far as this wave can see (confidence medium: 8 queries refused).
- Adjacent (all primary, high confidence unless marked):
  - **Principios de Chapultepec — Declaración de ética y buenas prácticas para el uso y desarrollo de la IA**
    (SECIHTI + ATDT, presented 29 Jan 2026, CDMX; 10 principles; "carácter orientador", non-binding). PDF read:
    https://secihti.mx/wp-content/uploads/2026/02/Principios_Chapultepec_F.pdf (bilingual:
    https://secihti.mx/wp-content/uploads/2026/05/Principios_de_chapultepec_Bilingue_web.pdf).
    **Principle 3 — "Si una decisión no puede explicarse, no debe automatizarse"** — carries the research clause:
    *"En la investigación científica y la producción de conocimiento, este principio se traduce en prácticas abiertas y
    responsables que permitan verificar resultados, reproducir procesos y declarar explícitamente el uso de IA."*
    Principle 2 ("Toda decisión apoyada por IA debe tener responsables humanos") requires *"procedimientos de
    revisión y mecanismos de corrección"*; Principle 10 treats data quality/representativeness as a public good.
    This is the first Mexican policy text that names verifiability, reproducibility and AI-use declaration as research
    obligations, and its headline rule is fail-closed in form. No mechanism, no enforcement.
  - **SNPCyH (Sistema Nacional de Publicaciones Científicas y Humanísticas)**: Lineamientos in DOF 27 May 2026
    (https://secihti.mx/wp-content/uploads/2026/05/Lineamientos_SNPCyH_DOF_270526.pdf); padrón of **513 open-access
    journals** from 637 applicants, evaluated by >300 SNII researchers + technical committee with Latindex/Redalyc/SciELO
    (Comunicado 62, 25 Aug 2026, https://secihti.mx/wp-content/uploads/2026/08/Comunicado_62_25082026.pdf); it
    announces "una nueva política nacional de acceso abierto"; strengthening call 21 Sep 2026. Admissibility criteria
    (https://secihti.mx/snpcyh/criterios-de-admisibilidad/): "integridad académica" = peer review that "resguarde la
    rectitud académica"; **no criterion on plagiarism, AI use, data availability, reproducibility or retractions**.
    Evaluation guide: https://secihti.mx/wp-content/uploads/2026/05/GUIA_-Evaluacion_SNPCH_260525_Ultima.pdf.
  - **SECIHTI open-science presentation to the Senate** ("Perspectivas de México sobre la Ciencia Abierta", Apr 2025,
    PDF read: https://comisiones.senado.gob.mx/CHTI/images/eventos/070425/docs/Dra_Zaira.pdf): values wheel lists
    *"Transparencia, control, crítica y reproducibilidad"* and *"Calidad e integridad"*; 121 Laboratorios Nacionales as
    open infrastructures; Red ECOS; Lineamientos for Ecosistemas Nacionales Informáticos and repositories. The only
    SECIHTI document found that uses the word "reproducibilidad". SECIHTI site search for "integridad científica"
    returns only the SNPCyH items (https://secihti.mx/?s=integridad+cient%C3%ADfica).
  - **Supercomputing / AI-for-science**: Clúster Nacional de Cómputo e IA letter of intent (18 Jun 2026) and
    Coatlicue (314 PF target) as in run 1; **SECIHTI–AMD** AI/supercomputing talent agreement (18 Aug 2026); SECIHTI
    "Ciclo de Conferencias en IA" 2026 (sessions on causal models, agentic reasoning "AURA", LLM+graph ML) — no
    session on verification/reproducibility (https://secihti.mx/?s=inteligencia+artificial). LANCAD site refused
    connection; LNS-BUAP TLS failure.
  - **UNAM**: **Consejo Coordinador de Inteligencia Artificial (CCOIA)** installed **18 May 2026**, presided by Rector
    Leonardo Lomelí, coordinator Pablo Pruneda Gross; mandate: coordination, "buenas prácticas", university-wide AI
    policies, ethics; no lineamientos, verification or reproducibility content
    (https://unamglobal.unam.mx/global_tv/instala-la-unam-el-consejo-coordinador-de-inteligencia-artificial-para-que-la-tecnologia-avance-con-perspectiva-humanista-rector-lomeli/).
    Gaceta UNAM search: nothing on verification/reproducibility (https://www.gaceta.unam.mx/?s=inteligencia+artificial+investigaci%C3%B3n).
  - **COFEPRIS**: article archive Sep–Oct 2026 has no AI / SaMD / statistical-guidance item; first Mexican-made CAR-T
    trial (UANL) 1 Oct 2026; ANVISA mutual recognition; WHO GBT. Reliance stance (run 1) stands
    (https://www.gob.mx/cofepris/es/archivo/articulos).
  - **Open-access infrastructure**: REMERI (Red Mexicana de Repositorios Institucionales, national node of LA
    Referencia; Open Data Day 2026 with CUDI) (https://www.remeri.org.mx/). A "Red Mexicana de Ciencia Abierta" was not
    located on primary pages. **CIMAT**: UQ seminar/thesis Feb 2026, bootstrap sample-size thesis, MICAI Nov 2025; no
    verification line (https://www.cimat.mx/?s=incertidumbre). **Cinvestav**: AI-for-neuroscience pieces, nothing on
    reproducibility. **IPN**: CIC breast-cancer triage AI (Oct 2026), no validation detail.
  - **AI law**: the Diputados statute catalogue (14 Oct 2026) lists no federal AI law; the only relevant statute is
    the Ley General en materia de HCTI (DOF 8 May 2023, unreformed) (https://www.diputados.gob.mx/LeyesBiblio/index.htm).
    Senate CHTI commission: meetings 25 Feb and 1 Jul 2026 (with Rosaura Ruiz), initiatives page loads dynamically —
    AI bills in Congress remain **unverified; do not cite**.
- **Run 3 additions (8 live searches, 9 fetches; Direct finding unchanged: none).**
  - **INSP ↔ BITSS/CEGA Catalyst project** "Improving Reproducibility and Transparency Practices in Public Health Research
    in Mexico: A Working Group and Short Course" (Instituto Nacional de Salud Pública; SOPs published, an institutional
    transparency/reproducibility hub, modular MSc coursework on open-science tools in design/collection/analysis/
    dissemination; contributors Sergio Bautista, Nerissa Nance, Gina La Hera Fuentes, Lily Alexander; undated on the page)
    — https://www.bitss.org/?p=6211 (read). **The only Mexican reproducibility-infrastructure node found in the sweep.**
  - **Velazquez-Ramos, de la O-Camacho, Camacho, Domínguez-Aguirre, Marcelino-Aranda (IPN / UT Bahía de Banderas),
    "Inteligencia artificial, su regulación en la investigación científica, caso México"**, *Tecnología en Marcha*
    39(5):41–50, 6 Mar 2026, https://doi.org/10.18845/tm.v39i5.8512 (abstract read): no Mexican legal framework for
    GenAI; among journals of the top-ranked Mexican institutions **47% have no GenAI policy, 9% prohibit, 44% allow with
    restrictions**; the paper asks for transparency of use, not verification.
  - **Rosaura Ruiz (SECIHTI), speech at El Colegio de México, 14 Aug 2026** ("¿El Leviatán artificial?", read by
    Gabriela García Acosta): "Una predicción acertada no equivale necesariamente a una explicación"; "La responsabilidad
    no puede delegarse en un modelo"; four principles for public AI policy in science — shared public computing,
    responsible data governance, **"validación científica de los resultados"**, and training to assess the tools
    critically — https://www.cronica.com.mx/academia/2026/08/14/la-ia-no-solo-acelera-la-ciencia-tambien-transforma-la-forma-de-producir-conocimiento-rosaura-ruiz/
    (read). Second quotable domestic hook after Chapultepec P3; again no mechanism.
  - **Consultorsalud, 12 Mar 2026** (Tatiana Asprilla): "México no cuenta con estándares específicos para la validación,
    certificación" of AI models; fragmentation INAI / CONBIOÉTICA / SECIHTI; asks for "criterios de validación
    algorítmica" — https://consultorsalud.com.mx/?p=313765 (read; secondary). **COFEPRIS**: the AI/SaMD/statistical
    query returned no COFEPRIS document; only a third-party summary of a June 2026 device-registration guide via
    equivalence agreements (PureGlobal, not fetched, low) — reliance stance stands.
  - **AI law (status as of 14 Oct 2026, secondary press, no gazette text read):** still no general law. Senate
    *Comisión de Análisis, Seguimiento y Evaluación sobre la Aplicación y Desarrollo de la IA* (Rolando Zapata Bello,
    PRI) announced on 30 Apr / 7 May 2026 that it would present a law + a national plan ("dos instrumentos diferentes")
    — https://www.infobae.com/mexico/2026/04/30/desde-comision-del-senado-impulsan-iniciativa-de-ley-para-regular-el-uso-de-inteligencia-artificial-en-mexico/ ,
    https://www.informador.mx/mexico/senado-busca-establecer-regulacion-para-el-uso-de-inteligencia-artificial-en-mexico-20260507-0109.html
    (both read); Sen. Karina Isabel Ruiz Ruiz (Morena) filed a "Ley Nacional para Regular el Uso de la IA" on
    11 Feb 2026; 85 AI initiatives since Apr 2023, 67 pending (Universidad Anáhuac count); the only enacted items are the
    DOF 14 May 2026 reforms to the LFT and LFDA on voice/image vs generative AI
    — https://ecosistemastartup.com/regulacion-ia-mexico-2026-85-iniciativas-pendientes/ (28 Jul 2026, read; secondary).
    A Diputados bill of 24 Jul 2026 ("Ley Federal para el Desarrollo Ético, Soberano e Inclusivo de la IA") appears only
    in a trade-press snippet (not fetched). **No bill as reported carries a science/verification clause.**
  - **Coatlicue**: press confirms the Nov 2025–Jan 2026 announcements (MXN 6,000 M; 314 PF; ~15k GPUs; 24-month build from
    Jan 2026; interim BSC MareNostrum 5 access) — no "AI for science" verification programme and no entity named
    "Laboratorio Nacional de Supercómputo Coatlicue" surfaced (snippets only; progress as of Oct 2026 unverified).
  - **NOTHING in Mexico for:** GRIM/statcheck-type forensic statistics (query returned only international items: Springer
    Nature, CASRAI guide, a UZH ROR-2026 talk); UNAM/Cinvestav/IPN metascience (the UKRN list of national reproducibility
    networks at Metascience 2025 names Brazil, not Mexico — https://www.ukrn.org/2025/07/09/in-person-meeting-of-national-reproducibility-network-representatives ,
    snippet); a body named "Red Mexicana de Ciencia Abierta" (REMERI/CUDI "hacia la construcción de un Ecosistema de
    Ciencia Abierta en México", Sep 2024 meeting, remains the closest match; "Red ECOS" still unverified).
- Epistemics / gap framing: Mexico's 2026 frame is **capacity + ethics + open access** (Coatlicue, Chapultepec,
  SNPCyH). Chapultepec P3 states the CAPAS obligations in policy language (verify results, reproduce processes,
  declare AI use) but as orientation, with no mechanism; SNPCyH operationalises "integridad" at journal level
  never at claim level; COFEPRIS imports evidence standards by reliance. No fail-closed
  default anywhere, no local evidence-admissibility standard, no domestic competitor.
- Institutions & people: SECIHTI (Rosaura Ruiz Gutiérrez); ATDT; UNAM CCOIA (Leonardo Lomelí, Pablo Pruneda Gross,
  María Soledad Funes — Investigación Científica); Cinvestav; CIMAT; IPN-CIC; COFEPRIS; REMERI/CUDI; SNPCyH Grupo
  Técnico Asesor (Latindex, Redalyc, SciELO); Senate Comisión CHTI (Susana Harp).
- Take / Ahead: take: (a) quote Chapultepec P3 verbatim as the domestic policy hook — CAPAS is a mechanical
  implementation of "verificar resultados, reproducir procesos y declarar explícitamente el uso de IA"; (b) P2's
  "procedimientos de revisión y mecanismos de corrección" maps to REWRITE/HOLD; (c) the SNPCyH padrón (513 journals,
  evaluation guide, no AI/data criteria yet) is a concrete channel for a journal-side CAPAS adapter and a gap the
  2027 convocatoria could fill; (d) run 3: **INSP/BITSS is the one domestic reproducibility node to approach for a
  pilot**, Ruiz's "validación científica de los resultados" principle (14 Aug 2026) is a second verbatim hook, and
  Velazquez-Ramos's 47%-no-policy figure is the journal-side gap number | ahead: no Mexican tool, program or policy has a
  verification mechanism; nothing deterministic, no sealed-blind evaluation, no proof ledger; CAPAS is alone at home on
  this evidence (now with 11 searches behind the absence claim, confidence on absence raised to medium-high).
- Confidence: high on documents read; medium-high on absence | Queries: run 2: 3 WebSearch + 8 refused + 20 fetches
  (secihti.mx ×5, Senate CHTI ×3, gaceta/unamglobal ×3, COFEPRIS, ATDT, diputados ×2, CIMAT, IPN, Cinvestav, REMERI,
  LANCAD/LNS failed); **run 3: 8 WebSearch (the 8 planned queries, all ran) + 9 fetches** (bitss.org, kimuk.conare.ac.cr
  → revistas.tec.ac.cr, consultorsalud, cronica.com.mx, infobae, informador, ecosistemastartup; secihti/diputados not
  re-fetched).

### Micronesia
- NOTHING FOUND (fetch-only). COM-FSM: IRB and Policies links only (https://www.comfsm.edu.fm/). Confidence: low |
  Queries: none (budget).

### Moldova
- Direct (2026 SOTA): none found (fetch-only).
- Adjacent: **Joint call of the Romanian Academy and the Academy of Sciences of Moldova, 14 Jun 2026** ("Promoting
  Quality, Integrity and Responsibility in Scientific Research", signed by Marius Andruh, Ion Tighineanu and Randy
  Schekman): "fewer, but more solid, publications"; "Science cannot be reduced to numbers"; bibliometrics "cannot
  replace academic judgment"; science needs "mechanisms that protect quality, ethics and truth"; AI mentioned only
  in passing
  (https://asm.md/en/call-scientific-community-both-banks-prut-promoting-quality-integrity-and-responsibility-scientific).
  **ANCD** evaluation regulations (PDF uploaded Jul 2026, https://ancd.gov.md/en/node/3453), bilateral calls Dec 2025;
  no integrity/AI/open-data provisions visible (https://ancd.gov.md/en).
- Epistemics / gap framing: anti-metric, judgment-based — the opposite pole from mechanical gating, yet it explicitly
  asks for "mechanisms that protect… truth".
- Institutions & people: Academy of Sciences of Moldova (Ion Tighineanu); ANCD; Romanian Academy.
- Take / Ahead: take: the "mechanisms that protect quality, ethics and truth" line is quotable; CAPAS is such a
  mechanism that is not a metric | ahead: nothing operational there.
- Confidence: medium (statement read) | Queries: none (budget) | Fetches: asm.md ×2, ancd.gov.md ×2.

### Monaco
- NOTHING FOUND (fetch-only). Centre Scientifique de Monaco: publications lists only, no governance/integrity/AI
  items (https://www.centrescientifique.mc/, /fr/). Confidence: low | Queries: none (budget).

### Mongolia
- NOTHING FOUND (fetch-only). MUST: targeted research project call (30 Sep 2026), policy page unread
  (https://www.must.edu.mn/); Mongolian Academy of Sciences unreachable (certificate expired; curl returned nothing)
  (https://www.ac.mn/). Confidence: low | Queries: none (budget).

### Montenegro
- NOTHING FOUND (fetch-only). Ministry of Education, Science and Innovation landing page has no dated items
  (https://www.gov.me/en/mps); University of Montenegro refused connection twice (https://www.ucg.ac.me/).
  Confidence: low | Queries: none (budget).

### Morocco
- Direct (2026 SOTA): none found (run 2 fetch-only; run 3: 2 searches).
- Adjacent (run 3): **"Maroc IA 2030" roadmap**, presented in Rabat on 19 Jan 2026 as the AI pillar of Maroc Digital
  2030 — **Jazari Institutes** (national network of AI centres of excellence; "Jazari Root" launched as the hub);
  **Mistral AI & MTNRA joint R&D lab** hosted in Jazari Root; CNDP president Omar Seghrouchni presented a "Framework de
  l'IA responsable" centred on (personal-)data protection; eight applied-research partnership agreements
  — https://fnh.ma/article/actualite-high-tech/ia-maroc-phase-operationnelle-2030 (read). Press adds targets (MAD 100 bn
  GDP, 50,000 jobs, 200,000 trained, 550 AI doctoral scholarships to 2027; Hespress snippets, not read). UM6P: Rabat
  Consensus on AI (Jun 2024), UNESCO reference centre for AI in Africa (snippets). **Nothing on research integrity,
  reproducibility, statistics checks or verification of AI outputs** on any Moroccan page or snippet.
- Epistemics / gap framing: AI as sovereignty + industrial policy; the "responsible AI" framework is data-protection law,
  not epistemic.
- Institutions & people: MTNRA (Amal El Fallah Seghrouchni, minister); CNDP (Omar Seghrouchni); Jazari Institutes; UM6P
  (Hicham El Habti); CNRST (homepage only, run 2).
- Take / Ahead: take: nothing technical; Jazari Root is the venue if a Maghreb pilot is ever wanted | ahead: all
  mechanical.
- Confidence: medium (one primary read; rest snippets) | Queries: run 3: "Maroc intégrité scientifique IA recherche 2026
  CNRST stratégie IA"; "Morocco UM6P AI research reproducibility / verification / research integrity 2025 2026" |
  Fetches: run 2: 7 (cnrst.ma via curl, academiesciences.ma, um6p.ma ×2, MESRSI refused, ministry DNS fail); run 3: fnh.ma.
  Reclassified from NOTHING FOUND (fetch-only) to **adjacent-only (policy)**.

### Mozambique
- Direct (2026 SOTA): none found (fetch-only).
- Adjacent: **UEM** has a Política de Investigação, Política de Publicações, Regulamento do Comité de Ética em
  Investigação (undated), a **Semana da Ciência Aberta da UEM** (19–23 Oct, year not shown), repositories and an OA
  journal (https://uem.mz/etica-na-investigacao/, https://uem.mz/event/semana-da-ciencia-aberta-da-uem/); FNI
  workshop on systemic STI policy and intersectoral decision-making (6 Aug 2026) (https://fni.gov.mz/). No AI or
  reproducibility content.
- Epistemics / gap framing: open-access + ethics-committee stage.
- Institutions & people: UEM; FNI.
- Take / Ahead: take: nothing | ahead: all.
- Confidence: low-medium | Queries: none (budget) | Fetches: uem.mz, fni.gov.mz.

### Myanmar
- NOTHING FOUND (fetch-only). MOST Myanmar reached with curl (HTTP 200; no hits for AI / integrity / open science;
  WebFetch TLS failure) (https://www.most.gov.mm/). Confidence: low | Queries: none (budget).

---

## Wave summary

**Top 5 findings for CAPAS**
1. **Principios de Chapultepec, Principle 3 (Mexico, SECIHTI+ATDT, 29 Jan 2026)** — "Si una decisión no puede
   explicarse, no debe automatizarse", with the research clause *"prácticas abiertas y responsables que permitan
   verificar resultados, reproducir procesos y declarar explícitamente el uso de IA"*. The home country's own policy
   states CAPAS's three obligations; it has no mechanism. Quote it verbatim.
   https://secihti.mx/wp-content/uploads/2026/02/Principios_Chapultepec_F.pdf
2. **ReAgent** (arXiv 2609.22111, Aug 2026): static+dynamic audit that a paper's numbers are actually produced by its
   repository (catches hard-coded metrics) — a ready-made pattern for CAPAS's reproducibility-artifact field; verdict
   mechanism not yet confirmed deterministic. https://arxiv.org/abs/2609.22111
3. **Lithuania, Guidelines on the Ethical Use of AI in Education and Research (Aug 2024), §30–§32**: AI tools "must be
   subject to a preliminary verification", "regular audits", validated for "methodological soundness (compliance with
   the basic principles of scientific methodology)"; plus the **Responsible Science Barometer 2026** (27% of
   researchers met misconduct in 3 years). A standing national requirement CAPAS can satisfy mechanically.
   https://etikostarnyba.lt/wp-content/uploads/2024/08/Guidelines-on-the-ethical-use-of-artificial-intelligence-in-education-and-research.pdf
4. **LLM-Assisted Replication for Quantitative Social Science** (Kubota et al., Tohoku/U Tokyo, Feb 2026): replication
   loop with "pre-submission check / meta-scientific audit" use cases; LLM stays in the loop — the contrast case for
   "no model in the verdict". https://arxiv.org/abs/2602.18453
5. **JST ↔ G-Search contract (31 Mar 2026)**: a national agency re-pricing its structured bibliographic data as the
   hallucination-proof grounding layer — institutional validation of machine-context ingestion.
   https://www.jst.go.jp/pr/announce/20260331-2/pdf/20260331-2.pdf
   Also worth keeping: Hayata & Yamamoto PRR 22 Sep 2026 (anomaly-coefficient invariant for capas_quantum_physics);
   Malaysia MY-AISafe E12 (28 Jul 2026), FNR Luxembourg "authors may, reviewers may not" (Apr 2026), and the
   Romanian–Moldovan academies' call (14 Jun 2026: "mechanisms that protect quality, ethics and truth") as policy hooks;
   Mexico's SNPCyH padrón (513 OA journals, DOF 27 May 2026) as a journal-side adapter channel with no AI/data criteria
   yet.

**3 countries with the strongest direct work:** Japan (clearly first, the only one with systems); Lithuania
(policy-level tool-verification requirement + a national integrity office + measured base rate); Mexico
(policy hook only — Chapultepec P3, CCOIA at UNAM, SNPCyH — no mechanism). Malaysia and Luxembourg follow as
institutional/policy hooks without direct work.

**NOTHING FOUND (15):** Kiribati (searched); fetch-only — Laos, Lesotho, Liberia, Libya (unreachable), Maldives, Mali,
Marshall Islands (unreachable), Mauritania (unreachable), Mauritius, Micronesia, Monaco, Mongolia, Montenegro, Myanmar.
**Adjacent-only (9):** searched in run 3 — Lebanon, Lithuania, Malta, Morocco (policy only; moved out of NOTHING FOUND);
fetch-only — Liechtenstein, Madagascar, Malawi, Moldova, Mozambique.
**NOT SEARCHED: none remaining.** All 36 wave-4 countries have an entry. **Run 3 closed the stated debt: Mexico got all
8 planned searches (11 in total), Lithuania, Malta, Morocco and Lebanon 2 each. Ranking unchanged** — Japan first; Mexico
and Lithuania still policy-hook only (Mexico adds the INSP/BITSS reproducibility node and Ruiz's "validación científica
de los resultados" principle; Lithuania adds the LEI 2026 "check all created content" rule). Caveat that remains: 26 of
36 entries are still fetch-only from run 2 (no search engine); MDIA (Malta) pages are still 403 so its sandbox is
snippet-level.
