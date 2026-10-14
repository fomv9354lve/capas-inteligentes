# World sweep 2026 — Wave 6 (S): Saint Kitts and Nevis → Syria

Date of sweep: 2026-10-14. Agent: wave-6. Brief followed: `BRIEF.md` (same directory).

**Coverage caveat (read first).** The session-wide WebSearch budget (200 calls shared by every wave agent) ran out
after the 39th query of this wave, while the Singapore block was in flight. Per the tool's instruction I did not wait
for the refill and did not route searches through curl/proxies. For the countries after that point I could only
fetch *known primary URLs* directly (institution home pages, arXiv HTML for affiliation checks). Entries are therefore
labelled one of three ways, and the difference is deliberate:

- **searched** — WebSearch queries ran (listed under Queries).
- **NOTHING FOUND (queries: …)** — queries ran, nothing relevant to CAPAS came back.
- **NOT SEARCHED (budget exhausted) — primary-URL fetch only** (pass-1 label, superseded in pass 2) — no query ran; only what a direct fetch of a known
  institutional page showed. This is *not* "nothing exists"; it is "not examined". A re-run of those countries is a
  stated debt at the end of this file.

Confidence scale: high = primary source read; medium = secondary summary or home page only; low = inference.

**Pass 2 (same date, resumed).** WebSearch allowed 2 live queries (both on South Korea) and then refused again.
Bing results pages fetched through WebFetch returned only generic first-token pages (20 attempts, all unusable) and
DuckDuckGo served a bot challenge, so no general web search ran for the remaining countries. Pass 2 therefore relies
on **direct fetches of primary sources** — institutional, funder and regulator pages, the UKRN list of national
reproducibility networks, and arXiv's own listing search by topic with affiliations verified on each candidate paper's
HTML. Entries updated in pass 2 say so in their Queries line. "NOT SEARCHED" no longer appears; the residual debt is
stated in the Wave summary.

---

### Saint Kitts and Nevis
- Direct (2026 SOTA): none.
- Adjacent: none. Results returned only generic AI-reproducibility material from other countries (NTNU, US National
  Academies CAST standing committee on AI and research trustworthiness —
  https://www.nationalacademies.org/units/CAST-STPL-26-05 — not SKN).
- Epistemics / gap framing: no national research-integrity or evidence framework surfaced.
- Institutions & people: none surfaced (regional route would be UWI / CARICOM).
- Take / Ahead: take: nothing | ahead: n/a.
- Confidence: high that nothing surfaced; low on existence. | Queries: "Saint Kitts and Nevis research integrity
  reproducibility AI science policy". **NOTHING FOUND (queries: 1).**

### Saint Lucia
- Direct (2026 SOTA): none.
- Adjacent: none specific. Only generic items (Falling Walls science-integrity panel; Institute for Replication PNAS
  study on AI-assisted reproducibility teams, via a LinkedIn summary) — none Saint Lucian.
- Epistemics / gap framing: nothing.
- Institutions & people: none surfaced (UWI Open Campus Saint Lucia / Sir Arthur Lewis CC would be the places to check).
- Take / Ahead: take: nothing | ahead: n/a.
- Confidence: high that nothing surfaced. | Queries: "Saint Lucia research integrity reproducibility AI science
  university". **NOTHING FOUND (queries: 1).**

### Saint Vincent and the Grenadines
- Direct (2026 SOTA): none.
- Adjacent: a draft national STI policy workshop (Oct 2023, with ECLAC, at UWI Global Campus SVG —
  https://nbcsvg.com/2023/10/04/workshop-on-the-development-of-national-draft-science-technology-and-innovation-policy-has-commenced);
  a UWI Caribbean-SIDS research series session on SVG (14 May 2026, https://sta.uwi.edu/news/ecalendar/event.asp?id=4690).
  Nothing on verification, reproducibility or evidence standards.
- Epistemics / gap framing: none.
- Institutions & people: UWI Global Campus SVG.
- Take / Ahead: take: nothing | ahead: n/a.
- Confidence: high that nothing relevant surfaced. | Queries: "Saint Vincent and the Grenadines research science
  policy university AI". **NOTHING FOUND (queries: 1)** for CAPAS-relevant work.

### Samoa
- Direct (2026 SOTA): none.
- Adjacent: the Pacific Academy of Sciences was launched at the National University of Samoa during CHOGM 2024 (reported
  in a Solomon Islands National University bulletin, https://www.sinu.edu.sb/wp-content/uploads/2024/11/UNIVOIS-VOLUME-3-ISSUE-10.pdf).
  No integrity/reproducibility/verification content.
- Epistemics / gap framing: regional AI-governance language is about relationality and collective wellbeing (Otago NZ
  policy, not Samoan).
- Institutions & people: National University of Samoa; Pacific Academy of Sciences.
- Take / Ahead: take: nothing | ahead: n/a.
- Confidence: high that nothing relevant surfaced. | Queries: "Samoa National University research integrity AI science
  policy Pacific". **NOTHING FOUND (queries: 1).**

### San Marino
- Direct (2026 SOTA): none. Adjacent: none (results were generic AI-reproducibility literature; the only institutional
  hit was Univ. of Insubria, Italy).
- Epistemics / gap framing: none. Institutions & people: none surfaced (University of San Marino not in results).
- Take / Ahead: take: nothing | ahead: n/a.
- Confidence: high that nothing surfaced. | Queries: "San Marino university research AI reproducibility science".
  **NOTHING FOUND (queries: 1).**

### São Tomé and Príncipe
- Direct (2026 SOTA): none.
- Adjacent: University of São Tomé e Príncipe (public since 2014, ~2,000 students,
  https://en.wikipedia.org/wiki/University_of_S%C3%A3o_Tom%C3%A9_and_Pr%C3%ADncipe); a 2026 Uni-CV mission on scientific
  writing and research ethics (https://inforpress.cv/en/article-9838); a new scientific research association
  (https://rtpafrica.rtp.pt/noticias/sao-tome-e-principe-nova-associacao-cientifica-da-visibilidade-a-investigacao-no-arquipelago).
  Nothing on verification or evidence standards.
- Epistemics / gap framing: none. Institutions & people: USTP.
- Take / Ahead: take: nothing | ahead: n/a.
- Confidence: high that nothing relevant surfaced. | Queries: "São Tomé and Príncipe research science policy university
  AI". **NOTHING FOUND (queries: 1).**

### Saudi Arabia (searched: 3 queries + 2 primary fetches)
- Direct (2026 SOTA): none found from KAUST, SDAIA or KACST. KAUST's Center of Excellence for Generative AI page
  (chair Bernard Ghanem, co-chair Jürgen Schmidhuber; https://www.kaust.edu.sa/en/research/generative-ai) lists a "GenAI
  Factory" feeding four application pillars and a Rising Stars in AI Symposium (9–11 Feb 2026) but says nothing about
  verification, reproducibility or LLM evaluation (high confidence on the page; medium on KAUST overall, since the
  search for KAUST-specific 2026 verification work returned only non-Saudi papers).
- Adjacent (regulatory, strongest Saudi item): SFDA's *Guidance on the Review and Approval of AI and Big-Data based
  Medical Devices* (MDS-G010ML) requires analytical + clinical validation and, for in-scope devices, an *independent
  review of the clinical evaluation* by someone not involved in development; SFDA strongly recommends local clinical
  studies and states that EU approvals do not supersede Saudi requirements (secondary summaries:
  https://tamimi.com/law-update-articles/new-guidance-for-ai-and-big-data-medical-devices-in-saudi-arabia,
  https://www.regdesk.co/?p=19901; a 2026 note refers to a newer MDS-G27 digital-health guidance,
  https://meddeviceguide.com/blog/digital-health-ai-medical-device-regulation-mena-sfda-ede-titck-guide). The SFDA news
  URL from search (sfda.gov.sa/en/news/3880273) returned 404 on fetch. Medium confidence; dates not confirmed as 2025.
- Epistemics / gap framing: regulator-driven ("show accuracy, validate locally, independent reviewer"); no
  metascience/reproducibility community surfaced.
- Institutions & people: KAUST GenAI CoE (Ghanem, Schmidhuber, Xin Gao); SFDA; SDAIA (no integrity framework found);
  KACST (site unreachable at fetch time).
- Take / Ahead: take: SFDA's "independent reviewer not involved in development" is the human analogue of CAPAS §6
  counter-signature — cite it when pitching the regulated-submission beachhead in the Gulf | ahead: nothing Saudi is
  deterministic or fail-closed; no sealed-blind protocol anywhere in the material.
- Confidence: medium | Queries: "KAUST 2026 AI for science verification reproducibility LLM scientific claims";
  "Saudi Arabia SDAIA 2025 2026 AI research integrity evaluation framework scientific"; "Saudi FDA SFDA AI medical
  device guidance 2025 clinical evidence requirements".

### Senegal
- Direct (2026 SOTA): none.
- Adjacent: UCAD accelerating AI in teaching (https://www.osiris.sn/l-ucad-veut-accelerer-l-integration-de-l-ia-dans-ses-enseignements.html);
  10th AUAO conference at UCAD on AI and multidisciplinary research (Feb 2025); a multidisciplinary measurement centre
  with ten labs opened Feb 2026 (https://www.ndarinfo.com/tags/Centre+de+mesure+UCAD/); presidential statement (Jan 2024)
  calling for "permanent evaluation and monitoring" of AI ethics/transparency. Nothing on reproducibility, statistics
  checks, or evidence standards.
- Epistemics / gap framing: policy-level ethics language only.
- Institutions & people: UCAD (Dakar).
- Take / Ahead: take: nothing | ahead: n/a.
- Confidence: high that nothing relevant surfaced. | Queries: "Senegal research integrity reproducibility AI science
  Dakar UCAD 2025". **NOTHING FOUND (queries: 1)** for CAPAS-relevant work.

### Serbia (searched: 2 queries + 2 primary fetches)
- Direct (2026 SOTA): none.
- Adjacent: Mathematical Institute SANU (70+ researchers; automated-reasoning tradition — Janičić's overview
  https://www.mi.sanu.ac.rs/conferences/ARinSerbia.pdf; AI4TrustBC Science Fund project on AI for blockchain trust,
  PDF unreadable on fetch, 2020 metadata). Institute for AI R&D of Serbia (IVI, Novi Sad, founded 2021; groups:
  CV/remote sensing, green AI, AI in health, HCI, smart factory — https://westernbalkans-infohub.eu/?p=10309). Government
  AI office (https://www.ai.gov.rs/): ethical guidelines + compliance questionnaire (undated); national Serbian LLM
  protocol with 11 institutions (29 Apr 2026); DAR Sandbox for testing AI/robotics at Belgrade STP (24 Aug 2026);
  Oxford Insights readiness rank 39/195 (31 Dec 2025).
- Epistemics / gap framing: strategy and capacity building; no reproducibility/verification stance surfaced.
- Institutions & people: MI SANU; IVI (Novi Sad); ai.gov.rs; Predrag Janičić (Univ. Belgrade, automated reasoning).
- Take / Ahead: take: nothing direct; Janičić's group is a potential formal-methods partner for autoformalizing CAPAS
  rules | ahead: Serbia has no claim-gating, sealed evaluation or proof-ledger work in view.
- Confidence: medium | Queries: "Serbia Mathematical Institute SANU AI verification formal methods reproducibility
  2025 2026"; "Serbia Institute for Artificial Intelligence Research and Development Novi Sad 2026 science AI".

### Seychelles
- Direct (2026 SOTA): none.
- Adjacent: UniSey seminar on redefining academic writing in the AI age (May 2025,
  https://nation.sc//articles/26215/dr-klymenko-proposes-redefining-academic-writing-for-seychelles-in-ai-age); UNCTAD STI
  Policy Review (2022–23, https://unctad.org/publication/science-technology-and-innovation-policy-review-seychelles);
  NISTI umbrella body (undated). 2020 presidential line: rely on MBZUAI (UAE) rather than build AI education.
- Epistemics / gap framing: none. Institutions & people: University of Seychelles; NISTI.
- Take / Ahead: take: nothing | ahead: n/a.
- Confidence: high that nothing relevant surfaced. | Queries: "Seychelles research science policy university AI".
  **NOTHING FOUND (queries: 1)** for CAPAS-relevant work.

### Sierra Leone
- Direct (2026 SOTA): none.
- Adjacent: Nigeria–Sierra Leone AI research/talent/model-localisation partnership signed 22 Nov 2025
  (https://digitalpolicyalert.org/change/19917); minister's call for "rigorous, credible" research at the 11th AWAU
  conference, Freetown (https://www.usl.edu.sl/news-detail.php?id=35). No integrity/verification policy.
- Epistemics / gap framing: none. Institutions & people: Njala University; Fourah Bay College (USL).
- Take / Ahead: take: nothing | ahead: n/a.
- Confidence: high that nothing relevant surfaced. | Queries: "Sierra Leone research integrity AI science Njala
  University Fourah Bay 2025". **NOTHING FOUND (queries: 1).**

### Singapore (pass 2: 2 WebSearch refused; 14 primary-source fetches)
- Direct (2026 SOTA): none Singapore-affiliated found. The arXiv listings for "scientific claim verification" and
  "AI scientist" + verification (26 papers, 2025–26) contain no NUS/NTU/A*STAR/SMU paper; SciLens (checked because of
  Simon See) is HKUST + NVIDIA Santa Clara, not Singapore (https://arxiv.org/html/2606.20873). A*STAR CFAR (director
  Ivor Tsang; pillars AI4TranS, ETAI, ASI, OAI; 11 NeurIPS 2026 + 12 EMNLP 2026 papers —
  https://www.a-star.edu.sg/cfar) lists no verification/reproducibility line.
- Adjacent (strongest): **AI Verify Testing Framework**, extended to generative AI on 29 May 2025; 11 principles incl.
  **Reproducibility**; each outcome = process checks (Yes/No/N/A + documentary evidence) + technical tests via the AI
  Verify Toolkit / Project Moonshot; crosswalks NIST AI RMF (Oct 2023), ISO/IEC 42001 (21 Jul 2025) —
  https://aiverifyfoundation.sg/what-is-ai-verify/. **Moonshot's metric catalogue is mixed: ~9 LLM-as-judge metrics
  (GPT-4o annotators, LlamaGuard, FlagJudge, "General Judge LLM") beside deterministic ones (ExactStrMatch, BLEU/ROUGE,
  LeakageRate, spaCy EntityProcessor for hallucinated entities)** —
  https://aiverify-foundation.github.io/moonshot/resources/metrics/ (README v0.7.6,
  https://github.com/aiverify-foundation/moonshot). Global AI Assurance Sandbox/Pilot pages 404 on fetch. Regulatory:
  **MFDS–HSA joint "Guiding Principles for conducting Clinical Trial for Machine-Learning-enabled Medical Devices"**
  (registered 11 Dec 2024; https://www.mfds.go.kr/eng/brd/m_40/view.do?seq=72637; PDF not read). HSA SaMD guidance
  list as in pass 1. Quantum: **NQCH** (CQT + A*STAR IHPC + NSCC): Quantinuum strategic partnership 6 Nov 2025, NVQLink
  19 Nov 2025, Pasqal collaboration 26 Nov 2025 ("improving the accuracy of quantum computation"), RIKEN R-CCS MoU 2 Mar
  2026; **no benchmarking/verification programme named** (https://www.nqch.sg/). NRF: RIE2030 Plan (31 Aug 2026), no
  integrity/reproducibility items (https://www.nrf.gov.sg/). Historic anchor: Singapore Statement on Research Integrity
  (22 Sep 2010, WCRI-2; https://www.wcrif.org/guidance/singapore-statement).
- Epistemics / gap framing: assurance-by-testing plus process documentation; "Reproducibility" is a governance
  principle answered with Yes/No evidence boxes, not a numeric gate; LLM judges are admitted as evaluators.
- Institutions & people: AI Verify Foundation / IMDA; HSA; A*STAR CFAR (Ivor Tsang); NQCH; NUS/NTU integrity pages
  unreachable (empty / 404).
- Take / Ahead: take: the Moonshot judge-vs-deterministic split is a ready-made positioning slide (CAPAS = the
  deterministic column only); the MFDS–HSA joint ML-device trial guidance is the bilateral regulatory document to cite
  for the device/pharma beachhead in Asia | ahead: nothing Singaporean returns a fail-closed verdict over structured
  evidence; no sealed-blind rate; no proof ledger.
- Confidence: medium-high (pages read). | Queries: WebSearch refused (A*STAR AI-for-science verification; NUS/NTU
  claim-verification benchmark; IMDA sandbox findings; HSA AI guidance; quantum benchmarking); Bing-via-WebFetch
  unusable (see caveat); fetches: aiverifyfoundation.sg (3; sandbox + pilot 404), moonshot docs + README, a-star.edu.sg
  (cfar; research-integrity 404), nrf.gov.sg, nqch.sg, cqt.sg (empty ×2), nus.edu.sg (empty), ntu.edu.sg (404),
  wcrif.org, arXiv listings ×3 + HTML ×1.

### Slovakia (pass 2: 4 primary-source fetches)
- Direct (2026 SOTA): none.
- Adjacent: **Slovak Reproducibility Network (SkRN, https://skrn.sk/)** — hosted by the Institute of Experimental
  Psychology, Centre of Social and Psychological Sciences SAS; GFRN member; Slovak textbook "Statistics for reproducible
  research in the social sciences", first-preregistration write-up (24 Feb 2025), repository of Slovak psychological
  instruments; no 2026 posts. SAS home: LUMI-Q quantum-computer colloquium (23 Oct 2026), disinformation-language
  conference 20–21 Oct 2026; nothing on integrity or verification (https://www.sav.sk/?lang=en). APVV: Annual report
  2025, GRANTED project (gender in grant allocation); nothing on integrity (https://www.apvv.sk/?lang=en). KInIT as in
  pass 1 (fact-checked-claim retrieval; Šimko, Pikuliak, Vykopal).
- Epistemics / gap framing: psychology-led open-science reproducibility (preregistration, Meehl); disinformation lens
  at KInIT; no evidence-admissibility framing.
- Institutions & people: SkRN (SAS IEP); KInIT; SAS; APVV.
- Take / Ahead: take: SkRN is a small GFRN-connected audience for a Slovak-language "mechanical enforcement" demo;
  KInIT prior-verdict retrieval as before | ahead: no gating, ledger or blind protocol.
- Confidence: medium-high. | Queries: WebSearch refused; fetches skrn.sk, sav.sk, apvv.sk, ukrn.org/international-networks.

### Slovenia (pass 2: 4 primary-source fetches)
- Direct (2026 SOTA): none.
- Adjacent: University of Ljubljana *Ethics and integrity in research*: European Code of Conduct for Research
  Integrity (2023 ed.) binding; UL Recommendations on using AI in force since 19 Sep 2022 + UL AI guidelines (Slovenian
  only); links the EU living guidelines on generative AI in research; conflict-of-interest rules from 2 Apr 2025; open
  science / FAIR section — https://www.uni-lj.si/en/research/ethics-and-integrity-in-research. ARIS: "Research culture,
  open science and evaluations" unit; peer review by national + international experts; EUR 365.2M research budget
  2025 (https://www.aris-rs.si/en/). No Slovenian node in the UKRN/GFRN list. IRCAI / JSI items as in pass 1.
- Epistemics / gap framing: ALLEA-code compliance and "ethical by design" AI; nothing on evidence sufficiency or
  fail-closed defaults.
- Institutions & people: UL; ARIS; IRCAI; JSI (Marko Grobelnik).
- Take / Ahead: take: UNESCO channel via IRCAI (as before) | ahead: no deterministic gating anywhere in view.
- Confidence: medium. | Queries: WebSearch refused; fetches uni-lj.si (2), aris-rs.si (home; /odpdostop 404), ukrn.org list.

### Solomon Islands
- Direct / Adjacent: none. SINU home shows only an "Office of Research and Postgraduate Studies" menu entry; no
  integrity, AI or reproducibility content (https://www.sinu.edu.sb/). Pacific Academy of Sciences item as in pass 1.
- Confidence: high that nothing surfaced; low on existence. | Queries: WebSearch refused; primary fetch sinu.edu.sb.
  **NOTHING FOUND (primary fetches: 1).**

### Somalia
- Direct / Adjacent: none. Somali National University lists a "Research Ethics" page and a Somali National
  Artificial Intelligence Centre (SNAIC) in its menus, undated and without content (https://snu.edu.so/).
- Confidence: high that nothing surfaced. | Queries: WebSearch refused; primary fetch snu.edu.so.
  **NOTHING FOUND (primary fetches: 1).**

### South Africa (pass 2: 11 primary-source fetches)
- Direct (2026 SOTA): none.
- Adjacent: **SAMRC** — Research Integrity Office + misconduct portal (transgression.samrc.ac.za), Pan African Clinical
  Trials Registry (pactr.samrc.ac.za), Cochrane South Africa, Biostatistical Analysis unit ("strengthens research
  credibility"), REDCap Africa Symposium 21–22 Oct 2026, "AI for African Population Health" unit
  (https://www.samrc.ac.za/). **SAHPRA** guidelines board: SAHPGL-MD-16 Clinical Evaluation of Medical Devices, MD-17
  Clinical Investigation, MD-18 PMS/PMCF (all v1, 9 Sep 2025), MD-22 Reliance (25 Feb 2026); **no SaMD/AI guideline
  listed** (https://www.sahpra.org.za/guidelines-notice-board/). **Stellenbosch CREST** (est. 1995; hosts the DSI-NRF
  SciSTIP Centre of Excellence; scientometrics + research evaluation; STI funding-flows study 10 Apr 2026) — the
  country's metascience centre, no integrity-tech line visible (https://www0.sun.ac.za/crest/). **African
  Reproducibility Network (AREN)**, Ghana-registered non-profit: 150+ institutions in 29 countries, 28 local networks,
  2026 LNL training programme (6 Feb 2026); no South African member named on the page (https://africanrn.org/). CSIR
  2026 news: language-technology/NLP only (https://www.csir.co.za/). CAIR (Meyer, de Waal) as in pass 1. NRF (TLS
  error), Wits integrity (404 ×2), ASSAf integrity (404) unreachable.
- Epistemics / gap framing: registry + Cochrane evidence-grading culture (PACTR, Cochrane SA); the regulator leans on
  clinical-evaluation guidelines rather than algorithmic checks.
- Institutions & people: SAMRC; SAHPRA; CREST/SciSTIP; CAIR (Tommie Meyer, Alta de Waal); AREN.
- Take / Ahead: take: PACTR is a pre-registration source CAPAS could ingest as a machine-context file (as with
  atlas_prereg) for African trial claims; CAIR defeasible reasoning for the downgrade-only invariant semantics |
  ahead: no claim-gate, blind protocol or ledger.
- Confidence: medium-high. | Queries: WebSearch refused; fetches samrc.ac.za, sahpra.org.za (3), csir.co.za,
  sun.ac.za/crest, africanrn.org, nrf.ac.za (TLS), wits.ac.za (404 ×2), assaf.org.za/research-integrity (404).

### South Korea (pass 2: 2 live WebSearch + 14 primary-source fetches) — RICH
- Direct (2026 SOTA): **"YouRA: A Persistent-State Architecture for Evidence-Traceable Autonomous Research Agents"**
  — Yoonkyu Woo, Woojin Lee, Jin-Xia Huang, **ETRI + University of Science and Technology (Korea)**, arXiv 1 Oct 2026,
  accepted AACL-IJCNLP 2026 main — https://arxiv.org/abs/2610.01097 (affiliations verified on the HTML). Verification
  State Architecture (YAML state with hypotheses, **MUST_WORK gates**, evidence pointers); Independent Controller
  separated from execution; Evidence Check stage labelling each prediction supported / partially supported / refuted /
  inconclusive; independent validator + detector for mock data and hard-coded results; manuscript numbers must come
  from recorded state. MLR-Bench (10 tasks): overall 4.20–5.05 vs AI Scientist V2 3.62–4.28 (four LLM judges);
  provenance: 27/30 papers real-data-based vs 11/30 (MLR-Agent) and 17/30 (AI Scientist V2); hallucination diagnostic
  ~75% human-confirmed; **no significant hallucination difference vs AI Scientist V2** (authors: absence of evidence,
  not equivalence). High confidence. The paper does not state whether the gates are rule-based or LLM-judged; the
  evaluation is LLM-judged. The one live WebSearch found no KAIST/SNU claim-gating system; SNU GSDS (Taesup Kim)
  "Hallucination as Commitment Failure" (ICML 2026 MI workshop) and KAIST Whang-lab ERBench (NeurIPS 2024) are
  hallucination evaluation, not claim admissibility.
- Adjacent: **AI Basic Act** (Act on the Development of AI and Establishment of Trust; passed Dec 2024, in force Jan
  2026; high-impact and generative-AI duties: risk assessment, safety measures, local representative; legal basis for
  the AI Safety Institute and a national AI "control tower"; MSIT drafting the decree, "minimal regulation" line
  reaffirmed Apr 2025) — https://www.trade.gov/market-intelligence/south-korea-artificial-intelligence-ai-basic-act;
  Korean text on law.go.kr (인공지능기본법, Act 20676, 21 Jan 2025). **AI Safety Institute (AISI; Seongnam; MSIT +
  ETRI)**: AI Safety Policy, AI Safety Evaluation Office, AI Safety Research Lab; the home page names no benchmark or
  method (https://www.aisi.re.kr/eng/). MSIT: National AI Safety Master Plan (1 Oct 2026). **MFDS–HSA joint "Guiding
  Principles for conducting Clinical Trial for Machine-Learning-enabled Medical Devices"** (Digital Health Regulatory
  Support Division; registered 11 Dec 2024) — https://www.mfds.go.kr/eng/brd/m_40/view.do?seq=72637 (PDF not read).
  **KRISS**: Center for Superconducting Quantum Computing System; strontium frequency redetermined with ~50× better
  precision (7 Oct 2026); room-temperature plug-and-play single-photon source (2 Jul 2026); quantum-AI "digital
  sovereignty" National Assembly forum (11 Sep 2026) — https://www.kriss.re.kr/eng/; no qubit-benchmark admissibility
  item. NRF Korea English site 404 (×2); KISTI connection refused; CRE DNS failure (cre.or.kr is an unrelated blog);
  ETRI news: only a cybersecurity-share item (16 Jul 2025); KAIST news feed hung up (×2).
- Epistemics / gap framing: law-first "trust" framing (AI Basic Act) with a light-touch enforcement stance; the
  engineering statement in YouRA — a claim must trace to executed evidence or be labelled refuted/inconclusive — is the
  closest Korean articulation of a fail-closed default, applied inside the agent and scored by LLM judges.
- Institutions & people: ETRI/UST (Jin-Xia Huang, Yoonkyu Woo, Woojin Lee); AISI; MSIT; MFDS Digital Health
  Regulatory Support Division; KRISS; SNU GSDS (Taesup Kim); KAIST (Steven Euijong Whang).
- Take / Ahead: take: YouRA's **MUST_WORK gates + mock-data detector + "numbers only from recorded state"** are
  CAPAS-shaped controls inside an agent — cite as convergent design and offer CAPAS as the external, LLM-free gate the
  paper lacks; the MFDS–HSA joint guidance is the Asian regulatory hook | ahead: YouRA's verdicts and evaluation are
  LLM-judged and in-loop; no sealed-blind false-accept rate; no re-derivable hash; no public ledger; no cross-company
  counter-signature.
- Confidence: high (YouRA, Act, MFDS), medium (AISI, KRISS). | Queries: WebSearch (ran): "KAIST 2026 verification of
  AI-generated scientific claims reproducibility deterministic verifier"; "KAIST OR SNU 2026 AI scientist / AI for
  science verification hallucination scientific claims" — 5 further queries refused (AISI/AI Basic Act; NRF research
  integrity generative AI; MFDS AI device guidance; KRISS/ETRI quantum benchmarking; KISTI reproducibility). arXiv
  listing searches ("AI scientist" verification; "scientific claim verification"; KAIST/SNU in all fields → 0).
  Fetches: aisi.re.kr (2), trade.gov, mfds.go.kr (2), kriss.re.kr, msit.go.kr press list, etri.re.kr, nrf.re.kr (404 ×2),
  kisti.re.kr (refused), news.kaist.ac.kr (hang-up ×2), cre.or.kr, Wikipedia regulation page (3 ranges).

### South Sudan
- Direct / Adjacent: none. University of Juba: "AI Day" (filed 2024) and a workshop on AI in higher education (filed
  2025); no integrity or research-policy content (https://www.uoj.edu.ss/).
- Confidence: high that nothing surfaced. | Queries: WebSearch refused; primary fetch uoj.edu.ss.
  **NOTHING FOUND (primary fetches: 1).**

### Spain (pass 2: 17 primary-source fetches) — moderately rich
- Direct (2026 SOTA): **"AI Scientists as Engines of Discovery: A Case for Development within Reformed Institutions"**
  — Raul Jimenez & Licia Verde (ICCUB, Universitat de Barcelona / ICREA) with Cambridge, Flatiron, JHU, LMU
  co-authors; arXiv 22 Jun 2026 — https://arxiv.org/abs/2606.22859 (affiliations verified). Position: machine-readable
  provenance records + executable pipelines for independent re-runs; **automated checks in peer review for code
  execution, data integrity, statistics and citation accuracy, with open benchmarking of hybrid human–machine
  review**; pre-deployment evaluations, capability gating, audit logs; logged human authorization for physical or
  irreversible actions; funding for adversarial replication and independent re-implementations. No blinding; no
  verification standard defined. High confidence; proposed, not built.
- Adjacent: **Spanish Reproducibility Network (SPRN, https://sprn.es/)** — founded 2023 (impulse: OpenScienceLab
  UC3M), GFRN node; first workshop on reproducible, ethical science 9 Sep 2026; member-survey results presented 5 Oct
  2026; 2025 chapter "De la reutilización de datos a la reproducibilidad de la ciencia" (17 authors incl. Pablo
  Sánchez-Núñez, Javier de la Cueva); members page 404. **AEI** joined the Barcelona Declaration on Open Research
  Information on 9 Oct 2026; no integrity/reproducibility or AI-in-proposals content on the home page
  (https://www.aei.gob.es/en). **AESIA**: EU-AI-Act supervision body; "Laboratorio de Ideas" advisory committee
  constituted 9 Apr 2026 (women & AI, disinformation & AI); advising Poland/Lithuania 30 Sep 2026; **no sandbox,
  conformity-assessment or test-bench content reachable** (EN site and /supervision read "en construcción") —
  https://aesia.digital.gob.es/es. **BSC**: AI Institute lists a "Trustworthiness and Evaluation" unit and a
  "Provenance, Metadata and Reproducibility" group as names only (no group pages reachable) —
  https://www.bsc.es/research-and-development/research-areas/artificial-intelligence. CSIC: Ethics Committee,
  integrity/good-practice page and complaints channel listed; no reproducibility content. AEMPS: "Remedios siempre con
  evidencia científica" campaign; no AI or statistics guidance on the home page (https://www.aemps.gob.es/). No
  statcheck-like Spanish tool surfaced (could not search).
- Epistemics / gap framing: reproducibility-network + open-research-information framing (SPRN, Barcelona Declaration);
  AI governance is rights/compliance-centric (AESIA). Jimenez–Verde state the gap: institutions must be redesigned so
  AI claims are verifiable — and stop at "automated checks" without a fail-closed rule.
- Institutions & people: ICCUB/ICREA (Jimenez, Verde); SPRN (UC3M OpenScienceLab); AEI; AESIA; BSC (Alfonso
  Valencia; T&E unit); CSIC; AEMPS.
- Take / Ahead: take: Jimenez–Verde's "automated verification in peer review + open benchmarking of hybrid review" is
  the policy ask CAPAS answers — offer the sealed-blind benchmark as its first entry; SPRN workshops as the
  Spanish-language venue | ahead: nothing Spanish returns a deterministic verdict with a hash; SPRN is training and
  surveys, not enforcement; AESIA shows no technical test bench.
- Confidence: high (Jimenez–Verde, SPRN), medium (AESIA/BSC). | Queries: WebSearch refused (Red Española de
  Reproducibilidad; BSC trustworthiness & evaluation; AESIA sandbox); fetches sprn.es (2), aei.gob.es, aesia (4), bsc.es
  (3), csic.es (4; 3 ×404), aemps.gob.es, mineco sandbox (404), reproducibilidad.es (empty index), arXiv listing + HTML.

### Sri Lanka (pass 2: 3 primary-source fetches)
- Direct / Adjacent: NRC Sri Lanka — workshop with the Sri Lanka Clinical Trials Registry on interventional research
  (10 Jul 2026); economic-impact assessment of public research with Peradeniya (22 Jun 2026); President's Award for
  best papers (18 Dec 2025); "Prioritization of Research for Sri Lanka – 2026" (https://www.nrc.gov.lk/). UCSC: "ML
  and AI Nexus 2025", ICTer 2025, Ethics Review Committee (https://www.ucsc.cmb.ac.lk/). NSF items as in pass 1. No
  verification, reproducibility or statistics-check work.
- Institutions & people: NRC; NSF; UCSC; SLCTR.
- Take / Ahead: take: SLCTR is one more pre-registration source | ahead: n/a.
- Confidence: medium-high that nothing relevant surfaced. | Queries: WebSearch refused; fetches nrc.gov.lk,
  ucsc.cmb.ac.lk, nsf.gov.lk. **NOTHING FOUND (primary fetches: 3)** for CAPAS-relevant work.

### Sudan
- Direct / Adjacent: none. University of Khartoum: admissions, exams, staff and campus items only (https://uofk.edu/).
- Confidence: high that nothing surfaced. | Queries: WebSearch refused; primary fetch uofk.edu.
  **NOTHING FOUND (primary fetches: 1).**

### Suriname
- Direct / Adjacent: none. Anton de Kom Universiteit (https://www.uvs.edu/): US–Suriname research-capacity workshop
  call (18 Dec 2024); no integrity or AI content; adekus.sr DNS failed.
- Confidence: high that nothing surfaced. | Queries: WebSearch refused; primary fetches uvs.edu, adekus.sr (DNS).
  **NOTHING FOUND (primary fetches: 2).**

### Sweden (pass 2: 13 primary-source fetches)
- Direct (2026 SOTA): **Chalmers / Gothenburg / Cambridge, "Agentic AI integrated with scientific knowledge:
  laboratory validation in systems biology"** (Brunnsåker, Gower, Naval, Bjurström, Kronström, Tiukova, Ross D. King;
  *J. R. Soc. Interface*; WASP news 1 Oct 2026) — closed-loop AI laboratory on brewer's yeast that proposes questions,
  designs experiments and updates its model; discoveries validated by wet-lab experiment; humans set priorities and
  interpret; **no statement on hallucination or error rates on the page** —
  https://wasp-sweden.org/ai-scientist-makes-biological-discoveries-autonomously/. High on the page, medium on the
  paper (not read).
- Adjacent: WASP long-term funding secured (17 Sep 2026); Luc De Raedt (neuro-symbolic) EurAI award 25 Sep 2026;
  "Measuring What Matters" 3–6 Nov 2026 (no description) — https://wasp-sweden.org/news/. Swedish Research Council
  Ethics section (updated 3 Jul 2025) links "Good Research Practice – new edition"; no reproducibility or AI text on
  the landing page (https://www.vr.se/english/mandates/ethics.html). National misconduct board: oredlighetsprovning.se
  redirects to npof.se (certificate error on fetch; not read). **Swedish Reproducibility Network listed by UKRN as
  swern.org — DNS failed (swern.se too)**: existence confirmed only through the UKRN list
  (https://www.ukrn.org/international-networks/). AI Sweden / VR open-science items as in pass 1. RISE trustworthy-AI
  page behind a bot wall; Läkemedelsverket AI page 404; Karolinska integrity page 404; Chalmers news feed returned 0
  hits on fetch.
- Epistemics / gap framing: autonomous discovery with the wet lab as oracle (King's Robot Scientist lineage) — an
  external-oracle design, but reliability is not quantified publicly; the policy layer is good-research-practice
  guidance plus a statutory misconduct board.
- Institutions & people: Chalmers (Ross D. King, Daniel Brunnsåker); WASP; VR; Npof; AI Sweden; SweRN (unreachable).
- Take / Ahead: take: the King-lab closed loop is this wave's strongest "external oracle in the loop" precedent — cite
  it against the Ding et al. survey claim and propose CAPAS as the admissibility layer between hypothesis and lab run |
  ahead: no fail-closed gate on statistical evidence, no sealed-blind rate, no ledger; verification is by experiment,
  not by declared-evidence rules.
- Confidence: medium. | Queries: WebSearch refused (Chalmers AI scientist verification; SweRN; KTH/Uppsala tools;
  Läkemedelsverket AI; WASP-DDLS); fetches wasp-sweden.org (3), vr.se (3; 2 ×404), npof.se (cert), swern.org / swern.se
  (DNS), ri.se (bot wall), lakemedelsverket.se (404), ki.se (404), chalmers.se, ukrn.org list.

### Switzerland (searched: 12 queries + 6 primary fetches) — RICH
- Direct (2026 SOTA):
  1. **Kohler, Zollikofer, Einsiedler, Hoyle, Ash (ETH Zurich / Basel), "Read the Paper, Write the Code: Agentic
     Reproduction of Social-Science Results", arXiv 23 Apr 2026** — https://arxiv.org/abs/2604.21965. Agents are
     *isolated from the original code, results and paper*; outputs compared cell-by-cell; discrepancies traced to root
     cause; 48 papers with human-verified reproducibility × 4 scaffolds × 4 LLMs; failures split between agent error and
     paper under-specification. High confidence. This is the closest Swiss analogue to CAPAS's blind discipline
     (isolation of the evaluator from the answer), but the judge of "match" is cell comparison, not a fail-closed gate.
  2. **AI for Math @ EPFL (Kunčak, Viazovska, Bosselut; Poiroux, Milikic)** — https://aiformath.epfl.ch. Document-level
     autoformalization into Lean: LeanFlow agent (ICML 2026 AI-for-Math workshop; two previously unformalized results),
     **LeanProbe** (MCP server/CLI/API giving agents *verifiable* Lean feedback, Jun 2026), Lean Interact v0.10 (Nov
     2025); Apertus fine-tuned to emit Lean proofs (Mar 2026); 8-dim sphere-packing autoformalization report (Apr 2026).
     Funded by Renaissance Philanthropy's AI for Math Fund (Oct 2025). High confidence. The verdict here is the Lean
     kernel — a true "no model in the verdict" verifier for mathematics.
  3. **Apertus 1.5 (ETH/EPFL/CSCS, 24 Jul 2026)** — https://www.cscs.ch/science/computer-science-hpc/2026/apertus-15-building-the-next-generation-of-open-ai-infrastructure.
     Fully open weights/data/code (Apache-2.0), multimodal, 16 "Mini" distilled models; MeditronFO medical framework
     built on it. Transparency of provenance, *not* verification of outputs. High confidence.
- Adjacent:
  - **SwissRN** runs the Coordinating Office of the Global Federation of Reproducibility Networks since Jan 2026 (23
    member networks) — https://crsuzh.pages.uzh.ch/swissrn/contents/news/posts/2026-04-22b/GFRN.html (fetch of the page
    failed; search snippet, medium). Annual Report 2025 (Zenodo, 4 May 2026, https://zenodo.org/records/19877599);
    OPeR-RA workshops on computational reproducibility, preregistration, ORDM (May–Jul 2026,
    https://crsuzh.pages.uzh.ch/swissrn/contents/activities/operra/index.html); 4th annual meeting 5 Dec 2025 (Basel,
    with SNSF's Katrin Milzow and Anne Scheel); Computational Reproducibility Hackathon 2025 paper
    (https://sonar.unidistance.ch/fernuni/documents/335897).
  - **UZH Center for Reproducible Science** (chair Leonhard Held) being made permanent as "Center for Reproducible
    Science and Research Synthesis"; replication games 19 Jan 2026; Research-on-Research event 29–30 Jan 2026
    (https://www.crs.uzh.ch/en/news/2025.html; newsletter PDFs unreadable by fetch). Medium-high.
  - **SNSF**: ORD policy since Oct 2017 (DMP, FAIR repositories, data for reproducibility) — https://www.snf.ch/en/dMILj9t4LNk8NwyR/topic/open-science;
    nothing new dated 2025–26 surfaced. Medium.
  - **Swiss Data Science Center / Renku**: provenance knowledge graph linking data, code executions and results;
    re-runnable workflows (https://renku.readthedocs.io/en/0.18.1/topic-guides/provenance.html). No 2025–26 release
    surfaced. Medium.
  - **CERN-adjacent verification culture**: CMS practice — two independent teams, sign-off before unblinding
    (https://cms.cern/node/1378); PADME X17 blind procedure (JHEP Jun 2025,
    https://link.springer.com/article/10.1007/JHEP06(2025)040); blinding taxonomy note (arXiv 2112.09548). The 2026
    PHYSTAT/VERaiPHY review "Are We Ready for AI-Driven Discovery? AI Verification Before the Next Fundamental Physics
    Breakthrough" (Grosso MIT/IAIFI, Mikuni Nagoya, Heinrich TU Munich; arXiv 10 Jul 2026,
    https://arxiv.org/abs/2607.10039) is CERN-community but not Swiss-affiliated: calibration on independent data,
    coverage/calibration validation for SBI, uncertainty propagation "non-negotiable", agentic systems optimise only on
    simulation and touch observed data only at the final test, look-elsewhere correction. High confidence on content.
    Semafor (2 Mar 2026) on CERN using AI to stress-test theories; Edinburgh seminar on ATLAS LLM tooling (Apr 2026).
  - **Swissmedic**: 2026 post-market surveillance campaign (Class IIa–III), swissdamed UDI mandatory 1 Jul 2026; no AI
    or statistical-evidence guidance surfaced (https://www.baerkarrer.ch/en/publications/healthcare-medical-devices-2025). Low-medium.
  - ETH SRI Lab (Vechev) and ETH Quantum Device Lab (Wallraff): no 2026 verification/benchmark item surfaced in the
    queries run (search returned only background). Low.
- Epistemics / gap framing: Swiss framing is *reproducibility-infrastructure first* (SwissRN/CRS/SNSF/Renku) and, in
  physics, *blind-by-construction* (CMS two-team unblinding; VERaiPHY "data only at the final test"). Formal
  verification (Lean) is treated as the gold standard where it applies (math). Nobody in the Swiss material frames a
  fail-closed default for *statistical research claims* in general; CRS/SwissRN work is training + meta-research, not
  enforcement.
- Institutions & people: ETH Zurich (Elliott Ash, Alexander Hoyle; Imanol Schlag), EPFL (Viktor Kunčak, Maryna
  Viazovska, Antoine Bosselut, Martin Jaggi, Auguste Poiroux, Lazar Milikic), CSCS, UZH CRS (Leonhard Held), SwissRN
  (GFRN coordinating office), SNSF (Katrin Milzow), SDSC (Renku), CMS/CERN, Swissmedic.
- Take / Ahead: take: (a) LeanProbe's "verifiable feedback to agents" pattern = CAPAS as an MCP verifier inside agent
  loops (already partly built — cite them as convergent design); (b) Ash-group isolation protocol (agent never sees
  original code/results) as a published precedent for CAPAS's sealed-blind batches; (c) VERaiPHY's explicit list
  (independent-data calibration, coverage checks, final-test-only data contact) as additional structure-checkable rules
  for the Atlas/quantum gate | ahead: no Swiss system returns a single fail-closed verdict with a re-derivable hash over
  structured statistical evidence; no public proof ledger; no cross-company counter-signature; blind rates in the Ash
  paper are agent-recovery rates, not gate false-accept/false-reject rates.
- Confidence: high (direct items), medium (adjacent). | Queries: "ETH Zurich 2026 verification of AI-generated
  scientific claims deterministic verifier"; "EPFL 2025 2026 formal verification autoformalization Lean mathematical
  claims LLM"; "SNSF ... reproducibility replication 2025 2026 open research data policy"; "Swiss Reproducibility
  Network SwissRN 2025 2026"; "Swiss AI Initiative Apertus 2025 2026 AI for science verification ETH EPFL"; "CERN blind
  analysis unblinding policy statistical procedure 2025"; "ETH Zurich Center for Reproducible Science UZH Leonhard Held
  replication 2026"; "ETH Zurich SRI Lab Martin Vechev 2026 LLM verification formal guarantees"; "Swissmedic 2025 2026
  AI guidance medical device statistical evidence standards"; "ETH Zurich quantum computing benchmarking calibration
  verification Wallraff 2026"; "ETH AI Center 2026 'AI for science' hypothesis verification reproducibility agents"
  (extended); "'Read the Paper, Write the Code' ... ETH Zurich Ash 2026"; "Swiss Data Science Center RenkuLab
  reproducibility provenance 2025 2026"; "Viktor Kunčak EPFL LLM Lean verified proof 2026 Stainless"; "CERN AI physics
  'verification' LLM hallucination 2026 ...".

### Syria
- Direct / Adjacent: none examinable. Damascus University (connection refused) and HIAST (certificate error) were
  unreachable; no other primary URL known for this topic.
- Confidence: n/a. | Queries: WebSearch refused; primary fetches damascusuniversity.edu.sy, hiast.edu.sy (both
  failed). **NOTHING FOUND (primary fetches: 2, both unreachable).**

---

## Cross-country 2026 items surfaced by the Swiss/Saudi queries (not attributable to this wave's countries — for the global ledger)
All affiliations verified by fetching the arXiv HTML; none are from an S-country, so they are listed here only so the
parent does not lose them:
- **"The Verification Bottleneck: Managing Trust in Post-AGI Science"** — A. M. Renganathan, ICLR 2026 Post-AGI
  Science & Society workshop poster, https://iclr.cc/virtual/2026/10022086. Cites 21% recall of AI at catching
  manuscript errors; proposes epistemic triage, *verification cascades* (epistemic status assigned by verification
  depth) and provisional-knowledge status for AI claims. Affiliation not shown. Medium.
- **"Autonomous Research Agents: A Survey of AI Scientists and the Verification Gap"** — Ding, Nannapaneni, Liu,
  Zhang, arXiv 29 Jun 2026, https://arxiv.org/abs/2608.05179. 24 runnable systems: 83% release code, 38% release
  seeds/traces, 38% report any novelty-verification method; **"no LLM-era system in the corpus demonstrates an
  externally validated in-loop oracle"** (external-oracle rule: an outside source, not the system's own score, decides
  whether a result changes the next hypothesis). Affiliations not shown. High on content. Directly supports CAPAS's
  "external oracle or HOLD" invariant.
- **"The Calibration Turn in AI-Assisted Research: ... Evidence-Licensed Claims"** — Hongmin Li (Institute of Science
  Tokyo / U. Tokyo, Japan), arXiv 30 Jun 2026, https://arxiv.org/abs/2606.31273. Three principles: no claim without
  licence; validation does not set claim level; automation amplifies the need for calibration. Conceptual + synthetic
  sim only. High. Vocabulary ("evidence licenses speech") maps 1:1 onto ACCEPT/REWRITE/HOLD.
- **"Toward Auditable AI Scientists: A Hypothesis Evolution Protocol"** — Takahara, Mizoguchi (U. Tokyo), arXiv 10 Jul
  2026, https://arxiv.org/abs/2607.09195. Persistent hypothesis registry; belief changes only via attached evidence. High.
- **"Beyond the Text: ReAgent — verifying agent-written papers are backed by artifacts"** — Shen et al., arXiv 18 Aug
  2026, https://arxiv.org/abs/2609.22111 (affiliations not shown; likely China). Static analysis + execution against
  the repo. Medium.
- **SciIntegrity-Bench** (Yang, Liu, Xu; Tübingen/PKU/Tongji; arXiv v2 3 Jun 2026, https://arxiv.org/abs/2605.10246):
  34.2% integrity-problem rate over 231 runs × 7 LLMs; all 7 models synthesise data when data are missing. High.
- **IntegrityBench** (Tripathi et al.; JUIT India, NYU Shanghai, Berkeley, Oxford; arXiv 3 Jun 2026,
  https://arxiv.org/abs/2608.12345): 18 model variants, 32,400 evaluations; ~1 in 3 integrity-critical decisions fail
  under peak pressure. High.
- **AutoVerifier** (Du, Dinh, Zhang, Li; arXiv 3 Apr 2026, https://arxiv.org/abs/2604.02617): LLM-agentic six-layer
  claim verification demonstrated on a contested quantum-computing claim — LLM in the verdict, the opposite design.
- **DeepSciVerify** (FirstPrinciples / SFU Canada; arXiv 26 May 2026, https://arxiv.org/abs/2605.27710): claim–citation
  alignment, 86.7 micro-F1 on SCitance; LLM-driven.
- **NeurIPS 2026 workshop "AI for Science: Verification in the Age of AI Scientists"** (12 Dec 2026; organisers incl.
  Marinka Zitnik, Priya Donti, Yuanqi Du) — https://neurips.cc/virtual/2026/workshop/137492. "The ability to generate
  scientific outputs is advancing faster than the ability to verify them." Natural submission venue for CAPAS.
- **Google "Science One Framework" (Jul 2026)** — https://research.google/blog/science-one-framework-a-verifiable-autonomous-research-framework-via-chain-of-evidence/ — chain-of-evidence audit; baseline systems hallucinate up to 21% of references.


Added in pass 2 (from the arXiv listing searches; affiliations verified on the HTML unless noted):
- **Triage-PiEvo: Evidence Admission for Principle-Evolving Scientific Agents** — Li, Pu, Xu, Cui, Gao, Lin
  (Westlake University / Kuaishou / Zhejiang; China), arXiv 10 Oct 2026, https://arxiv.org/abs/2610.14683. A
  **rule-based evidence-admission gate with no LLM judge**: anomalies are withheld from scores and principle updates
  until they pass C1 (same-channel repeat), C2 (independent channel), C3 (independent evaluator on held-out inputs);
  a principle is Accepted only with zero contradicting admissible records and k=2 supporting ones; one contradicting
  record retracts it and the retraction propagates. Stress tests: ungated variants admit 100% of unreliable evidence,
  Triage-PiEvo 0%, 144/144 planted mechanisms recovered; +7.5–11.8% solution quality; +13.6% wall-clock. High
  confidence. The closest published analogue to CAPAS's downgrade-only, fail-closed admission in this sweep.
- **"Position: Correct Answer, Wrong Mechanism — When AI Scientists Defend General Claims Their Own Data
  Contradicts"** — Steven Young Eulig (Harvard LPPC), arXiv 22 Jun 2026, https://arxiv.org/abs/2606.23175. Two
  one-sided checks (regime-shift prediction test; companion recomputation of a known-correct observable) flag 7/7 CAWM
  episodes **in-sample, post hoc — the author states this is not a prospective detection rate** (same leakage
  discipline CAPAS applies to rules written from failures). High.
- Listed in the "AI scientist" + verification arXiv listing, affiliations not checked: "Beyond Execution: Auditing
  Experimental Fidelity in LLM-Driven Scientific Research" (https://arxiv.org/abs/2608.26753, 27 Aug 2026);
  "When Should an AI Scientist Stop? … CARTOGRAPH" (https://arxiv.org/abs/2606.07576, 26 May 2026, refuses claims when
  the model library is inadequate); HalluCiteChecker (NAIST Japan, https://arxiv.org/abs/2604.26835, 29 Apr 2026);
  "Benchmarking Agents for Proving Theorems in Quantum Algorithms and Quantum Information" (two Lean 4 benchmarks,
  https://arxiv.org/abs/2607.21533, 23 Jul 2026).
- SciLens (https://arxiv.org/abs/2606.20873, HKUST + NVIDIA; 18 Jun 2026): atomic-claim entailment against tables and
  figures, **verdict from an LLM resolver** (Qwen3-VL) with heuristic guards; 79.2 macro-F1 on SciClaimEval dev —
  the opposite design, listed for the differentiation ledger.

---

## Wave summary

**Top 5 findings for CAPAS (this wave, after pass 2)**
1. **EPFL LeanProbe / LeanFlow (Jun 2026, Switzerland)** — a verifier that gives agents *verifiable* Lean feedback via
   MCP; the architectural shape CAPAS has for statistical evidence, with the Lean kernel as the no-model verdict.
   https://aiformath.epfl.ch
2. **YouRA (ETRI/UST, South Korea; AACL-IJCNLP 2026)** — MUST_WORK gates, independent validator, mock-data detector,
   manuscript numbers only from recorded state; provenance 27/30 real-data papers vs 11–17/30 for baselines, but no
   hallucination advantage and LLM-judged throughout. Convergent design; CAPAS is the external LLM-free gate it lacks.
   https://arxiv.org/abs/2610.01097
3. **ETH Zurich "Read the Paper, Write the Code" (Apr 2026)** — isolation of the reproducing agent from code/results,
   cell-by-cell comparison, 48 human-verified papers: published precedent for sealed-blind reproduction.
   https://arxiv.org/abs/2604.21965
4. **Jimenez & Verde (ICCUB/ICREA Barcelona, Jun 2026)** — the institutional-reform ask that CAPAS answers: automated
   checks of code execution, data integrity, statistics and citations in peer review, with open benchmarking of hybrid
   review, provenance records and executable pipelines. https://arxiv.org/abs/2606.22859
5. **Chalmers/King closed-loop AI laboratory (J. R. Soc. Interface; WASP 1 Oct 2026, Sweden)** — the wave's only
   production "external oracle in the loop" (wet lab), with no public reliability figures: the slot for an
   admissibility layer between hypothesis and experiment.
   https://wasp-sweden.org/ai-scientist-makes-biological-discoveries-autonomously/
   (Runners-up: **Triage-PiEvo**, China — rule-based evidence admission, 0% unreliable evidence admitted vs 100%
   ungated, https://arxiv.org/abs/2610.14683 — the nearest published analogue to CAPAS's fail-closed admission;
   Singapore's Moonshot metric catalogue, which cleanly separates LLM-judge from deterministic metrics,
   https://aiverify-foundation.github.io/moonshot/resources/metrics/; "Autonomous Research Agents … Verification
   Gap", https://arxiv.org/abs/2608.05179; VERaiPHY, https://arxiv.org/abs/2607.10039.)

**3 countries with the strongest direct work:** Switzerland (clearly: Lean verifiers, isolated reproduction, SwissRN /
GFRN office), **South Korea** (YouRA; AI Basic Act in force Jan 2026; AISI; MFDS–HSA joint ML-device trial guidance),
**Spain** (Jimenez–Verde position paper; SPRN since 2023; AEI in the Barcelona Declaration). Next: Sweden (King-lab
closed loop, WASP) and Singapore (AI Verify framework with "Reproducibility" principle, Moonshot, NQCH, joint MFDS–HSA
guidance). Saudi Arabia drops to regulatory-only.

**NOTHING FOUND (queries or primary fetches ran, nothing CAPAS-relevant): 16** — Saint Kitts and Nevis, Saint Lucia,
Saint Vincent and the Grenadines, Samoa, San Marino, São Tomé and Príncipe, Senegal, Seychelles, Sierra Leone (pass 1,
WebSearch); Solomon Islands, Somalia, South Sudan, Sri Lanka, Sudan, Suriname, Syria (pass 2, primary fetches only;
Syria's two URLs were unreachable).

**NOT SEARCHED: 0.** Every S-country now has an entry. Residual debt: for the 12 pass-2 countries no general web
search ran (WebSearch budget; Bing-via-WebFetch unusable), so coverage is primary-source fetches plus arXiv listing
searches. A later WebSearch pass on South Korea (KAIST/SNU labs, KISTI, NRF integrity guidance), Spain (statcheck-like
tools, AESIA sandbox, BSC T&E group), Sweden (SweRN, Npof, Chalmers paper text) and Singapore (sandbox report, NUS/NTU
integrity) could still add items; it is unlikely to change the ranking.
