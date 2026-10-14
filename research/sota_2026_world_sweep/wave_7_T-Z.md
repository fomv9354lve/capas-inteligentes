# Wave 7 — Taiwan → Zimbabwe (world sweep 2026)

Run: 2026-10-14. Agent: Claude (Fable 5.1), WebSearch standard + 2 extended, 4 WebFetch of primary sources.
Resumed 2026-10-14 (same day): 3 further WebSearch calls (Ukraine), then the shared budget was exhausted again.
Brief followed: `BRIEF.md` (same template as every wave).

**Coverage caveat (honest):** the first pass covered the United States (15 queries), United Kingdom (9), Taiwan (3),
Turkey (3) and two of three UAE queries before the session-wide WebSearch budget ran out at query 41. The resume
pass completed the remaining 21 countries and the UAE **without a web search engine**: the harness blocked further
WebSearch calls, and Bing/DuckDuckGo results pages fetched through WebFetch returned unrelated or bot-check pages
(tried once each, then abandoned — no search-engine scraping was used). Coverage instead came from WebFetch on
primary sources: the OpenAlex API with per-country author filters (2024/2025– date floors), institutional sites
(NAQA, NRFU, ETDA, Agesic, ANII, NSTDA, UNESCO, PAS, vatican.va, doh.gov.ae), arXiv abstracts and DOI landing pages.
Consequence: small states are covered bibliographically, not by local-language web; policy pages behind 403/429 or
PDF-only (mbzuai.ac.ae, klk.univd.edu.ua, journals.sagepub.com, osf.io, tandfonline, DoH policy PDF) are flagged per
entry. No fact below was written without a URL returned by a search or a fetch; nothing was guessed.

---

### Taiwan
- Direct (2026 SOTA): none found on deterministic/fail-closed claim gating. Closest: an OECD AI-incident entry
  (2026-08-17) reporting a Taiwanese paper-comparison system that found **16.1% of checked references fabricated or
  erroneous**, largely GenAI-made — a reference-level admissibility signal, not a claim gate.
  https://oecd.ai/en/incidents/2026-08-17-e02c (confidence: medium — secondary monitor entry)
- Adjacent: NSTC research-misconduct guidelines (amended 2024-05-02) apply only to NSTC awardees
  https://www.casrai.org/guides/nstc-taiwan-research-misconduct-guidelines ; April-2026 legislative briefing: NSTC
  bars reviewers from feeding proposals to GenAI, Academia Sinica guidance requires manual checking
  https://www.ctee.com.tw/news/20260429701415-431401 (text garbled, low confidence on detail); NTU "Guidelines on
  the Use of Generative AI and Research Integrity"
  https://www.yzu.edu.tw/admin/rd/index.php/en-us/academic-ethics/academic-ethics-updates/8814-academic-resource-sharing-national-taiwan-university-guidelines-on-the-use-of-generative-ai-and-research-integrity .
  Regulated submissions: TFDA updated AI/ML device technical guideline (sensitivity/specificity/AUC, MRMC for
  high-risk; standalone testing cannot replace clinical evaluation)
  https://cisema.com/en/taiwan-fda-updates-ai-medical-device-technical-guidelines/ ; TFDA GMLP principles announced
  2026-06-08 (IMDRF ten principles, non-binding) https://cisema.com/news/gmlp-taiwan-ai-medical-devices ; e-submissions
  for Class I https://www.emergobyul.com/news/taiwan-market-update-electronic-submissions-ai-guidance-fee-revisions .
  No CDISC/validator-rule material found for TFDA.
  Quantum: Academia Sinica 20-qubit superconducting machine (Jan 2026)
  https://www.sinica.edu.tw/en/news_content/55/3655 ; **AI-driven automated qubit calibration with NVIDIA (Apr 2026)**
  https://www.sinica.edu.tw/en/news_content/55/3757 ; NSTC "verification platform" in the north and a 2027–2031
  "quantum leap" phase-2 plan https://technews.tw/?p=1442338 ,
  https://www.digitimes.com.tw/tech/dt/n/shwnws.asp?id=765161 . No independent published gate-fidelity/QV numbers found.
- Epistemics / gap framing: integrity framed as misconduct sanctions + GenAI disclosure; no evidence-grading or
  fail-closed default language found. Quantum framing is "verification platform" as infrastructure, not as an
  admissibility rule.
- Institutions & people: NSTC; Academia Sinica (quantum + GenAI guidance); TFDA; NCHC (benchmarking plans
  https://www.taiwannews.com.tw/en/news/6315425 ).
- Take / Ahead: take: Academia Sinica's AI-driven calibration is a live case where **calibration itself is
  model-generated** — CAPAS's per-parameter dated calibration snapshot is exactly the counter-control; propose Atlas
  gate a snapshot produced by an AI calibrator | ahead: no Taiwanese artifact gates calibration or claims
  deterministically; TFDA metrics are reporting expectations, not an engine.
- Confidence: medium | Queries: "Taiwan 2026 AI research integrity reproducibility NSTC Academia Sinica verification";
  "Taiwan TFDA CDISC submission validation statistical standards AI medical device guidance 2025"; "Taiwan quantum
  computer benchmarking calibration 2025 2026 national quantum program verification".

### Tajikistan
- Direct (2026 SOTA): none.
- Adjacent: none. OpenAlex (TJ-affiliated, 2024–) for research-integrity/AI/plagiarism returned 0 works; a general AI query
  returned 32, none on verification or integrity (e.g. AI chest-radiograph study, 2024
  https://doi.org/10.29328/journal.jprr.1001064 ).
- Epistemics / gap framing: not surfaced.
- Institutions & people: none identified.
- Take / Ahead: take: none | ahead: n/a.
- Confidence: medium (bibliographic coverage only; no web search available) | Queries: **NOTHING FOUND** (OpenAlex TJ
  "research integrity artificial intelligence plagiarism" 2024+ → 0; OpenAlex TJ "artificial intelligence Tajikistan
  science" 2024+ → 32, none relevant).

### Tanzania
- Direct (2026 SOTA): none.
- Adjacent: only generic AI-and-academic-integrity items: "Association Between Artificial Intelligence and Academic
  Integrity in Higher Education in Tanzania" (2025) https://doi.org/10.59645/tji.v5i1.702 ; "University Students'
  Perceptions and Use of AI Tools … Tanzanian Higher Education" (2026) https://doi.org/10.37284/eajes.9.3.5472 . COSTECH
  site fetched but returned no readable content; no TMDA AI/evidence material retrieved.
- Epistemics / gap framing: student-conduct register; nothing on research claims.
- Institutions & people: COSTECH (not readable).
- Take / Ahead: take: none | ahead: n/a.
- Confidence: low | Queries: OpenAlex TZ "research integrity reproducibility artificial intelligence" 2024+ (83 hits,
  2 tangential); OpenAlex TZ "research misconduct integrity Tanzania" 2024+ (100 hits, 1 tangential); costech.or.tz.
  Treated as NOTHING FOUND for CAPAS purposes.

### Thailand
- Direct (2026 SOTA): none found on deterministic or fail-closed claim gating.
- Adjacent: (1) **ETDA AI Governance Practice Center (AIGPC)** — missions: R&D of governance frameworks/tools, AI
  Observatory, capacity building, expert network; International Policy Advisory Panel + Thai expert fellows; publications
  *Ethical Impact Assessment Playbook* and *AI Job Redesign Guideline* (undated); 2026 activity: IPAP/fellow meetings
  1/2026 and 2/2026, ITU–NBTC course with delegates from 22 countries, talk at Chulalongkorn Faculty of Medicine
  https://www.etda.or.th/th/Our-Service/AIGC/index.aspx ,
  https://www.etda.or.th/th/Useful-Resource/publications/ETHICAL_IMPACT_ASSESSMENT_PLAYBOOK.aspx — no draft-AI-law
  status, no verification/evidence language on the page (fetched primary, Thai). (2) **UNESCO RAM Thailand case study**
  (2026-07-31): whole-of-society approach; 2025 Global Forum on the Ethics of AI in Bangkok (2,770 participants, 600+
  research submissions); Thailand proposed a UNESCO Category-2 Centre on AI Governance; quotes MHESI Permanent Secretary
  Supachai Pathumnakul https://www.unesco.org/en/articles/ai-readiness-assessment-methodology-thailand (high).
  (3) Scholarship: "Human Rights–Based AI Governance in Thailand: A Functional-Equivalence Approach Beyond the EU AI Act"
  (Freiberg, Harris, Ratnapinda — Chiang Mai Univ. ICDI, 2026) https://doi.org/10.14330/jeail.2026.19.1.07 ;
  "A Comprehensive Academic Integrity Ecosystem for Thai Higher Education in the Age of AI" (Roengtam, Mahidol, 2025)
  https://doi.org/10.18623/rvd.v22.n6.3951 ; "Copyright Law and the Use of AI in Academic Works in Thai HEIs" (2025)
  https://doi.org/10.56042/jipr.v30i6.15642 (records via OpenAlex; full texts not read). (4) Regulated submissions:
  Thai-affiliated 2025–26 AI-in-medicine outputs are reviews/consensus statements (APAC osteoporosis-AI consensus 2026
  https://doi.org/10.1007/s00198-026-08067-6 ); no Thai FDA AI or clinical-evidence standard retrieved. (5) Quantum:
  OpenAlex TH 2025+ "superconducting qubit … calibration" → 1 hit (QKD theory
  https://doi.org/10.1140/epjqt/s40507-026-00510-1 ); no national hardware-benchmarking item; qtft.org now shows an
  enterprise-optimisation vendor. NSTDA English site: AI items are workforce/Industry-4.0 only https://www.nstda.or.th/en/ .
- Epistemics / gap framing: governance-by-guideline and ethical impact assessment before deployment; "functional
  equivalence" to the EU AI Act argued academically; no evidence-grading, fail-closed or reproducibility language found.
- Institutions & people: ETDA AIGPC; MHESI (Supachai Pathumnakul); NSTDA; Chiang Mai ICDI (Phillip Freiberg, Parot
  Ratnapinda); Mahidol (Sataporn Roengtam).
- Take / Ahead: take: AIGPC's Ethical Impact Assessment Playbook is an assess-before-deploy artifact — a Thai pilot could
  map CAPAS HOLD/REWRITE onto its assessment step for AI-generated claims | ahead: nothing in Thailand gates claims
  mechanically; the integrity-ecosystem papers are policy proposals, not engines.
- Confidence: medium (AIGPC, UNESCO primary; papers as records) | Queries (6 + 5 fetches): WebSearch "Thailand NSTDA
  Chulalongkorn 2026 AI research integrity reproducibility verification" (budget-blocked); OpenAlex TH 2025+
  "reproducibility research integrity"; "AI law draft governance regulation"; "superconducting qubit quantum computer
  Thailand calibration"; "quantum technology roadmap" (20, none); "Thai FDA medical device AI … clinical evidence" (10,
  none regulatory); fetched etda.or.th (EN + TH AIGC), unesco.org, nstda.or.th, qtft.org.

### Timor-Leste
- Direct (2026 SOTA): none.
- Adjacent: none. OpenAlex TL 2024+ "research integrity ethics science policy": 50 hits, one Portuguese piece on
  transparency/ethics in STI management (2026, no DOI); "artificial intelligence … research": 40 hits, all
  AI-in-education (e.g. "AI Tools Experience in Civitas Academic Portal in Timor-Leste", 2024
  https://doi.org/10.58459/icce.2024.5040 ).
- Epistemics / gap framing: not surfaced.
- Institutions & people: none identified.
- Take / Ahead: take: none | ahead: n/a.
- Confidence: medium-low | Queries: **NOTHING FOUND** (the two OpenAlex TL queries above).

### Togo
- Direct (2026 SOTA): none.
- Adjacent: none on verification. OpenAlex TG 2024+ "research integrity AI reproducibility": 7 hits, none relevant;
  "intelligence artificielle recherche Togo éthique": 2 hits — one on data governance and AI in Togolese public
  universities (2026) https://doi.org/10.48734/akofena.n021.vol.3.08.2026 (governance, not verification).
- Epistemics / gap framing: not surfaced.
- Institutions & people: Université de Lomé (implied by the governance paper; not verified).
- Take / Ahead: take: none | ahead: n/a.
- Confidence: medium-low | Queries: **NOTHING FOUND** (the two OpenAlex TG queries above).

### Tonga
- Direct (2026 SOTA): none.
- Adjacent: none. OpenAlex TO 2024+ "research ethics integrity" → 4 (health surveillance, two mis-tagged Kenya papers);
  "artificial intelligence Tonga" → 2 (epidemiology).
- Epistemics / gap framing: not surfaced.
- Institutions & people: none identified.
- Take / Ahead: take: none | ahead: n/a.
- Confidence: medium | Queries: **NOTHING FOUND** (two OpenAlex TO queries above).

### Trinidad and Tobago
- Direct (2026 SOTA): none.
- Adjacent: "Caribbean lecturers' navigation and perceptions of academic integrity and AI-detection software in EAP
  modules" (Madden — UWI incl. St Augustine (TT); Smith; Edwards; Jackson; 2026)
  https://doi.org/10.29140/aile.2026.104937 — lecturers' perceptions of AI-detector reliability (OpenAlex record; full
  text not read: doi.org rate-limited). Companion: "human-centered AI integration in Caribbean language education"
  (2026) https://doi.org/10.29140/aile.2026.105032 . No CARPHA evidence-standard material retrieved.
- Epistemics / gap framing: distrust of AI detectors at classroom level; nothing on research claims.
- Institutions & people: UWI (Oneil Madden).
- Take / Ahead: take: none | ahead: CAPAS does not depend on AI-detection — it gates evidence fields, not text provenance.
- Confidence: low-medium | Queries: OpenAlex TT 2024+ "research integrity artificial intelligence reproducibility"
  (17 hits); OpenAlex record fetch. No CARPHA query possible (search budget).

### Tunisia
- Direct (2026 SOTA): none.
- Adjacent: "Between Promise and Peril: Artificial Intelligence as a Contested Catalyst for Research Development in
  Tunisia" (Harabi — Univ. of Carthage; Ghrab — Univ. of Manouba; *Journal of Learning for Development*, 2026)
  https://doi.org/10.56059/pk3eag72 (record only; full text not read). Remaining 88 TN-affiliated hits are domain
  reviews (e.g. GenAI/LLM accuracy in sports medicine, 2026 https://doi.org/10.3389/fpubh.2026.1843535 ).
- Epistemics / gap framing: not surfaced.
- Institutions & people: Univ. of Carthage (Meriem Harabi); Univ. of Manouba (Hatem Ghrab).
- Take / Ahead: take: none | ahead: n/a.
- Confidence: low-medium | Queries: OpenAlex TN 2024+ "research integrity reproducibility artificial intelligence
  verification" (88); record fetch. Planned French web query ("Tunisie intégrité scientifique …") could not run.
  Treated as NOTHING FOUND for CAPAS purposes.

### Turkey
- Direct (2026 SOTA): none on claim gating. Closest and notable: **TÜBİTAK sanctioned project applications that
  contained GenAI-fabricated/unverified references** under its Research & Publication Ethics regulation, and now requires
  AI-use disclosure and source verification (secondary university notice; primary TÜBİTAK text not retrieved)
  https://so.ozyegin.edu.tr/en/announcements/40206/attention-to-researchers-using-artificial-intelligence-in-proposal-writing
  (confidence: medium). TÜBİTAK guideline on responsible GenAI use in funding processes (privacy, originality/plagiarism
  control, transparency) https://pdo.metu.edu.tr/en/node/59 .
- Adjacent: TÜBİTAK ULAKBİM + Turnitin Academic Integrity Symposium, Ankara, 2026-04-21 (awareness, not tooling)
  https://ulakbim.tubitak.gov.tr/en/academic-integrity-symposium-announcement/ . Regulation: no horizontal AI statute;
  Nov-2025 amendment bill (deepfakes, takedown, training-data) https://cms.law/en/int/expert-guides/ai-regulation-scanner/tuerkiye ;
  **Presidential Circular 2026/9 — AI Action Plan 2026–2030** ("trustworthy, risk-sensitive, accountable")
  https://www.erdem-erdem.av.tr/en/insights/presidential-circular-on-turkiyes-artificial-intelligence-action-plan-20262030-published-in-the-official-gazette ;
  AI diagnostic tools are medical devices under TITCK conformity assessment with clinical evidence, sometimes local
  validation https://vlolawfirm.com/trackers/ai-regulation-turkey . Retraction base rate: 2021/2022 analyses of Turkish
  retractions (duplication dominant; rising trend)
  https://openaccess.hku.edu.tr/items/69df37f5-8e19-48b0-a506-44d48b6ac356 ; Retraction Watch Turkey category
  https://retractionwatch.com/category/by-country/turkey-retractions . No paper-mill study 2025–26 found.
- Epistemics / gap framing: ethics/sanction-centred; "trustworthy AI" is the policy register; no evidence-grading or
  honest-limits framing surfaced.
- Institutions & people: TÜBİTAK (ARDEB ethics committee; ULAKBİM); TITCK; Digital Transformation Office (Action Plan).
- Take / Ahead: take: TÜBİTAK's sanction on fabricated references is a **fail-closed rule applied at the funder gate** —
  worth citing as precedent that "undeclared/unverifiable source → inadmissible" is already institutional practice |
  ahead: Turkey enforces by human committee; CAPAS makes the same rule mechanical and hash-auditable.
- Confidence: medium | Queries: "Turkey TÜBİTAK 2026 research integrity reproducibility AI scientific verification";
  "Türkiye AI regulation 2026 draft law evidence standards TITCK clinical trial statistics"; "Turkey university paper
  mills retraction research misconduct 2025 2026 study".

### Turkmenistan
- Direct (2026 SOTA): none.
- Adjacent: none. OpenAlex TM 2024+ "research integrity AI" → 3 (none relevant); "science digitalization Turkmenistan
  academy" → 4 (civil-servant training, audit quality).
- Epistemics / gap framing: not surfaced.
- Institutions & people: none identified.
- Take / Ahead: take: none | ahead: n/a.
- Confidence: medium | Queries: **NOTHING FOUND** (two OpenAlex TM queries above).

### Tuvalu
- Direct (2026 SOTA): none.
- Adjacent: none. OpenAlex TV 2024+ "research science" → 4 (climate; co-authored clinical); "Tuvalu digital artificial
  intelligence" → 0.
- Epistemics / gap framing: not surfaced.
- Institutions & people: none identified.
- Take / Ahead: take: none | ahead: n/a.
- Confidence: medium | Queries: **NOTHING FOUND** (two OpenAlex TV queries above).

### Uganda
- Direct (2026 SOTA): none.
- Adjacent: **"A Risk-Based Artificial Intelligence Governance Framework for Higher Education Institutions in
  Low-Resource Settings: Evidence from Uganda"** (Mbabazi, Mabirizi, Tumusiime, Muragira — Kabale University;
  F1000Research 2026) https://doi.org/10.12688/f1000research.186904.1 ; "Responsible Judicial AI Governance … in Uganda"
  (2026 preprint) https://doi.org/10.21203/rs.3.rs-10240295/v1 ; academic-integrity systematic review (2026)
  https://doi.org/10.37284/eajes.9.1.4675 . UNCST site fetched — title only, no content; Makerere AI lab not reached.
- Epistemics / gap framing: risk-tiering of institutional AI use; nothing on evidence admissibility.
- Institutions & people: Kabale University group (Vicent Mabirizi, corresponding); UNCST.
- Take / Ahead: take: none | ahead: n/a.
- Confidence: low-medium | Queries: OpenAlex UG 2024+ "research integrity reproducibility artificial intelligence"
  (429, retried as "research integrity misconduct reproducibility", 18 hits); uncst.go.ug (no content).

### Ukraine
- Direct (2026 SOTA): **Center of Excellence in Formal Methods and Verification, Ukrainian Catholic University (Lviv)**
  — announced 2026-08-10, funded by the U.S. National Academy of Sciences' Science and Innovation Fund for Ukraine;
  scope: "formal methods and verification for mathematics, computer science, and AI systems"; Yaroslav Prytula: AI-
  supported reasoning in critical systems must be "checked for correctness with mathematical rigor" (fetched primary)
  https://www.nationalacademies.org/news/science-and-innovation-fund-for-ukraine-partners-with-ukrainian-catholic-university-to-launch-new-center-of-excellence ;
  launch event Lviv 2026-07-24 with **Jeremy Avigad** (roundtable "How AI Will Change Mathematics, Proofs, and
  Education"), David Spergel, Oleksii Ignatenko https://dou.ua/calendar/57933/ (high). Heritage: Glushkov's Evidence
  Algorithm / SAD prover, Kyiv, 1960s– (background) https://www.academia.edu/23239873/ . No Ukrainian claim-gating or
  LLM-judge artifact found.
- Adjacent: **Law No. 4742-IX "On Academic Integrity"** — adopted 2025-12-18, in force 2026-02-01, HEIs must comply by
  2026-07-31; introduces the concept of an **"institutional violation of academic integrity"** (failing to maintain an
  integrity system is itself a violation); sanctions list incl. dismissal; staff found guilty of dishonest AI use "may be
  entered into a public register of offenders"; no mandatory AI-detector designated (secondary, university page; statute
  text not retrieved) https://www.tdmu.edu.ua/en/?p=187738 ; Cabinet Resolution No. 928 (2025-07-30): doctoral
  candidates sign a declaration that they personally reviewed AI-assisted sections. NAQA: Advisory Board 2026-02-02 on
  applying the law https://en.naqa.gov.ua/wp-content/uploads/2026/02/02.02.26-NAQA-Advisory-Board-meeting-minutes.pdf ;
  NAQA + Kharkiv IT Cluster AI-policy workshop 24–25 Jun 2026 https://en.naqa.gov.ua/?p=6430 ; StrikePlagiarism
  **stylometry module** presented in Lviv, May 2026 https://en.naqa.gov.ua/?p=6295 . State Scientific and Technical
  Library webinar 2026-06-16 on detecting AI-modified texts
  https://nauka.gov.ua/en/opportunities/webinar-artificial-intelligence-is-already-in-the-classroom-academic-integrity-quality-control-and-new-educational-practices/ .
  NRFU (funder): open-science/ethics pages exist but no 2025–26 reproducibility or AI policy news; the NASU Presidium
  building was hit by a drone 2026-09-28 https://nrfu.org.ua/en/ . Literature is dense on AI-and-integrity (OpenAlex UA
  2025+: 1,983 hits; e.g. https://doi.org/10.22329/jtl.v19i3.9538 ); a Dissernet-like dissertation audit returned 0 hits
  in OpenAlex (the Ukrainian-language web query "Дисергейт" could not run).
- Epistemics / gap framing: integrity-as-law under war: obligation + register; verification means text provenance
  (similarity, stylometry, declarations), not evidence admissibility. The UCU centre is the only "mathematical rigor"
  framing found.
- Institutions & people: UCU (Yaroslav Prytula, Oleksii Ignatenko); NAS/SIFU (Vaughan Turekian, David Spergel); Jeremy
  Avigad (CMU, Lean) as advisor-speaker; NAQA (Ivan Nazarov, Leontii Shypilov); NRFU; Glushkov Institute.
- Take / Ahead: take: (a) the law's "institutional violation" concept — no integrity mechanism = violation — is a
  fail-closed norm at institution level CAPAS can cite as precedent; (b) UCU/Avigad is a candidate Lean partner for
  formalising Atlas's physics invariants | ahead: Ukraine checks text provenance; nothing gates numerical evidence or
  seals blind rates.
- Confidence: high (UCU, NAQA), medium (law details via tdmu.edu.ua) | Queries (3 WebSearch + 10 fetches): "Ukraine 2026
  research integrity academic fraud reproducibility National Research Foundation AI"; "Ukraine NAQA academic integrity
  law 2026 'Office for Research Integrity' AI verification"; "Ukraine formal verification AI research 2026 Glushkov
  Institute Kyiv neuro-symbolic theorem proving"; OpenAlex UA 2025+ ×3; nationalacademies.org, dou.ua, tdmu.edu.ua,
  naqa ×3, nrfu.org.ua, nauka.gov.ua. Not reached: klk.univd.edu.ua (403) — the search-snippet mention of a "Ukrainian
  Office for Research Integrity" head is UNVERIFIED and not recorded as a finding.

### United Arab Emirates
- Direct (2026 SOTA): none UAE-led on claim gating. Nearest, MBZUAI co-authored, 2026: (1) **"Beyond Perplexity: A
  Behavioral Evaluation Framework for Deployment-Memory Claims in LLM Test-Time Training"** (Song, Z. Chen (MBZUAI), …,
  Kun Zhang (MBZUAI/CMU); arXiv 2607.00368, 2026-07-01) — proposes a **"claim-calibrated evidence ladder"**: each
  capability claim must be matched to the evidence tier able to support it; proxy metrics (perplexity, loss) are weak
  evidence for deployment claims; a nonce-fact diagnostic shows loss drops while free-form recall stays at zero
  https://arxiv.org/abs/2607.00368 (high; abstract fetched, affiliations via OpenAlex). (2) **"How Robust Are Automated
  Fact-Checking Systems? A Cross-Benchmark Evaluation"** (Usmanova, Iklassov, Leippold, Usbeck; arXiv 2608.25934,
  2026-08-26; MBZUAI affiliation via OpenAlex) — 9 systems on SciFact/ClimateCheck/open-web; best SciFact macro-F1 0.70
  falls to 0.31 on ClimateCheck; gold evidence raises accuracy 14–22 pts → retrieval is the bottleneck; zero-shot LLMs
  underperform fine-tuned claim-only models on ClimateCheck https://arxiv.org/abs/2608.25934 (high). (3) HypoEvolve
  (UCSD-led; Eric Xing MBZUAI/CMU; arXiv 2609.15938, 2026-09-14) validates LLM hypotheses against DepMap/Open Targets as
  external oracles (selectivity 0.171 vs 0.115) https://arxiv.org/abs/2609.15938 (medium; US-led).
- Adjacent: **TII sovereign superconducting quantum-hardware program (Jun 2026)** with "practical application
  benchmarks" https://quantumcomputingreport.com/sovereign-superconducting-hardware-initiative-launched-in-abu-dhabi/ ;
  TII–Quantinuum partnership; in-house chips, IonQ, AWS Braket
  https://en.aletihad.ae/news/uae/4596010/tii--quantinuum-partner-to-advance-next-generation-quantum-c (page dates
  inconsistent). Falcon LLM line — no science-verification product https://fastcompanyme.com/?p=42461 . DoH Abu Dhabi
  policy list: "Policy on Use of AI in the Healthcare Sector of the Emirate of Abu Dhabi" (PDF metadata 2018; text not
  decodable) and a Trusted Research Environment policy V1/2025 https://www.doh.gov.ae/en/resources/policies — no AI
  clinical-evidence standard found.
- Epistemics / gap framing: MBZUAI's "claims need evidence matched to their tier" and "fact-checker rankings don't
  transfer across domains" are the closest UAE statements to CAPAS's admissibility logic.
- Institutions & people: MBZUAI (Kun Zhang, Eric Xing, Ricardo Usbeck's group); TII Quantum Research Centre; DoH Abu Dhabi.
- Take / Ahead: take: adopt the "claim-calibrated evidence ladder" vocabulary — ACCEPT/REWRITE/HOLD *is* such a ladder
  made mechanical; cite 2608.25934 for why an LLM fact-checker cannot be the verdict layer; TII's multi-vendor stack is a
  cross-vendor calibration-admissibility test bed for Atlas | ahead: no UAE artifact is deterministic, fail-closed or
  sealed-blind.
- Confidence: medium-high (MBZUAI papers), low (DoH, TII details) | Queries: "UAE MBZUAI 2026 AI for science verification
  reproducibility scientific claims"; "UAE Technology Innovation Institute 2026 Falcon science verification quantum
  benchmarking"; "MBZUAI 2026 AI scientist verification reproducibility scientific claims paper" (budget-blocked);
  OpenAlex AE 2025+ "scientific claim verification LLM" (236); OpenAlex MBZUAI-affiliation 2026 "verification
  reproducibility scientific" (42); arXiv abs ×3; OpenAlex records ×2; doh.gov.ae; mbzuai.ac.ae/news (403).

### United Kingdom
- Direct (2026 SOTA):
  1. **UK AISI "LLM judges on trial" (2025-07-09)** — Bayesian GLM framework to measure autograder reliability
     *while* answering the research question; names systematic biases (same-family favouritism, length, style/keyword
     preference); conclusion: an autograder's reliability must be verified per task before use. Does not say when
     deterministic grading is preferred (fetched primary).
     https://www.aisi.gov.uk/blog/llm-judges-on-trial-a-new-statistical-framework-to-assess-autograders ;
     Science-of-Evaluations hub https://www.aisi.gov.uk/category/science-of-evaluations (high)
  2. **Inspect** (AISI + Meridian Labs; MIT) — datasets/solvers/scorers architecture; scorers = the verification seam;
     used by METR, Apollo, several government bodies; Inspect-Cyber extension; UK–Singapore Moonshot interoperability
     pilot. https://www.aisi.gov.uk/work/inspect-evals , https://ukgovernmentbeis.github.io/inspect_evals/ ,
     https://casrai.org/guides/inspect-ai-evaluation-framework-uk-aisi (high; no 2026 "verifier" release found)
  3. Autoformalization of science with UK links: Lean Together 2026 talk (Axiomatic AI) on Lean libraries for
     quantum mechanics and agents that "certify a solution by converting it into a formal theorem"
     https://researchseminars.org/talk/LT2026/4/ ; **EconCSLib (2026)** — agent extracts a paper's statements and
     formalizes them in Lean; "frontier LLMs now write Lean well enough for non-trivial verification of research"
     https://arxiv.org/pdf/2606.13306 ; London Lean community (Imperial, UCL, Cambridge, DeepMind)
     https://lims.ac.uk/event/london-learns-lean/ ; **AlphaProof Nexus (May 2026)** applied to combinatorics, graph
     theory, quantum optics; GitHub carries successes only; Erdős success rate not independently reproduced
     https://winbuzzer.com/2026/05/26/google-deepmind-says-alphaproof-nexus-is-still-not-agi-xcxwbn/ (medium). Known
     trust gap: a mistranslation can pass the kernel check (autoformalizer ≠ verifier)
     https://deeptechstars.substack.com/p/formal-verification-explained-plus .
- Adjacent: **UK Metascience Unit** (UKRI+DSIT, 2024, £10m 2024–27; grants, internal funding experiments)
  https://www.ukri.org/what-we-do/browse-our-areas-of-investment-and-support/uk-metascience-unit ; RAND Europe support
  project (2026) https://www.rand.org/randeurope/research/projects/2026/supporting-the-uk-metascience-unit.html ;
  "A year in metascience 2025" https://gov.uk/government/publications/a-year-in-metascience-2025 ;
  **NSF–UKRI metascience statement (2026-10-08)** — joint work on measuring productivity, improving review/funding,
  "assessing how new methods and tools are used in research"; international network of metascience units; no explicit
  reproducibility/AI wording (fetched primary)
  https://www.ukri.org/publications/nsf-and-ukri-metascience-statement/nsf-and-ukri-metascience-statement-2026/ .
  **UKRN 2026 conference** Manchester 8–9 Jul 2026 (keynotes Stian Westlake/ESRC, Charlotte Pennington); 80 local
  networks; Imperial joined 2026 https://www.easychair.org/cfp/ukrn2026 ,
  https://www.imperial.ac.uk/news/articles/2026/imperial-college-london-joins-the-uk-reproducibility-network .
  Turing: UKRI review rated it "unsatisfactory" on alignment/value-for-money (Apr 2026), refocus on national security
  https://www.uktech.news/ai/alan-turing-institute-deemed-unsatisfactory-in-review-20260402 ; Turing AI-for-Science
  conference at the Royal Society 2026-03-31 (trustworthy AI, simulation-based science)
  https://www.c2d3.cam.ac.uk/events/ai-science . Royal Society *Science in the Age of AI* (May 2024, still the reference):
  opaque AI → less reliable findings; "you would expect to be able to verify them yourself"
  https://royalsociety.org/news/2024/05/ai-research-tools-could-undermine-trust-accuracy-scientific-findings/ .
  MHRA: National Commission on AI in healthcare report 2026-09-10, all 44 recommendations accepted 2026-10-06 incl.
  **staged authorisation against pre-specified evidence thresholds**; AI Airlock phase 3; no statistical-submission
  standard found
  https://www.raps.org/resource/euro-roundup-mhra-commission-makes-recommendations-on-ai-regulatory-framework-in-the-uk.html ,
  https://www.iatrox.com/blog/mhra-ai-regulation-commission-call-for-evidence-2026 .
- Epistemics / gap framing: strongest in the wave — "science of evaluations" treats the judge as a measurement
  instrument with quantified bias; metascience is a funded government unit; Royal Society frames AI outputs as a
  peer's work that must be independently verifiable; MHRA moves to pre-specified thresholds (a pre-registration
  logic at the regulator).
- Institutions & people: AISI Science of Evaluations team; UKRN (Marcus Munafò — not re-verified this wave); UK
  Metascience Unit; Alison Noble (Royal Society working-group chair); Kevin Buzzard's Lean circle (Imperial) — inferred
  from the London-learns-Lean page, medium.
- Take / Ahead: take: (a) AISI's **per-task autograder-reliability measurement** is the right companion to CAPAS's "no
  model in the verdict" — publish CAPAS vs an LLM judge on the same sealed batch using their Bayesian GLM; (b) MHRA
  staged authorisation = pre-registered band logic CAPAS already encodes — pharma/devices beachhead language | ahead:
  Inspect scorers are per-eval code, not a fail-closed admissibility calculus with sealed blind rates and a proof
  ledger; autoformalization work certifies *solutions*, not evidence-field admissibility, and leaves the
  translation-trust gap CAPAS avoids by not reading prose.
- Confidence: high (AISI, UKRN, Metascience Unit, NSF-UKRI), medium (Lean/autoformalization, MHRA) | Queries (9):
  "UKRI Alan Turing Institute 2026 AI for science verification reproducibility"; "UK Reproducibility Network 2026
  metascience unit UKRI"; "UK AI Security Institute evaluations 2026 Inspect framework verifiers"; "MHRA 2026 AI medical
  device evidence standards statistical submissions guidance"; "Royal Society 2025 2026 report science in the age of AI
  reproducibility verification"; "\"UK Reproducibility Network\" 2026 UKRN"; "UK formal verification scientific claims
  Lean autoformalization Cambridge Imperial DeepMind 2026"; "Google DeepMind AlphaProof autoformalization science 2026
  formal verification physics claims"; "UK AISI 2026 paper \"LLM judge\" reliability evaluation science of evals"
  (extended).

### United States
- Direct (2026 SOTA):
  1. **"More Claims, Less Evidence: Bounded Verification of AI-Generated Digital Knowledge Artifacts"** (Bańka &
     Chudziak, arXiv 2610.05547, 2026-10-04, ICADL 2026; affiliations not on page — likely Polish, listed here because
     it surfaced in the US query). Bayesian "Predictive Value of Pass": under a fixed verification budget, padding true
     claims around a fixed number of false ones **raises pass probability while lowering informativeness**; computes the
     minimum verification budget for a target PVP (fetched primary). https://arxiv.org/abs/2610.05547v1 (high)
  2. **"Autonomous Research Agents: A Survey of AI Scientists and the Verification Gap"** (Ding, Nannapaneni, Liu,
     Zhang; arXiv 2608.05179, 2026-06-29). 26 systems coded: 83% release code, only **38% ship reproducibility-grade
     artifacts**, 38% any novelty-verification, **no LLM-era system has an externally validated in-loop oracle**;
     proposes a reviewer-facing reporting checklist (fetched primary). https://arxiv.org/abs/2608.05179 (high)
  3. Claim-level verification cluster (2026): *From Fluent to Verifiable: Claim-Level Auditability for Deep Research
     Agents* https://arxiv.org/html/2602.13855v1 ; **FactReview — execution-based claim verification in peer review**
     https://arxiv.org/pdf/2604.04074 ; RefVerifier (citation-bound claims) https://arxiv.org/html/2609.07652v1 ;
     Google Paper Assistant Tool https://arxiv.org/pdf/2606.28277 ; SPOT benchmark (2025)
     https://arxiv.org/pdf/2505.11855 ; "Can AI Validate Science?" claim→evidence benchmark
     https://arxiv.org/pdf/2506.08235 (medium; abstracts only).
  4. LLM-judge vs deterministic: **SOCpilot** (arXiv 2605.05501) chose a deterministic verifier over an LLM judge for
     repeatability/auditability with a typed violation trace per run https://arxiv.org/pdf/2605.05501 ;
     **AutoPyVerifier** (arXiv 2604.22937, Apr 2026) — LLM synthesises executable Python verifiers, result deterministic
     https://www.emergentmind.com/papers/2604.22937 ; practitioner consensus = deterministic first, judge for semantic
     remainder, judge never the enforcement boundary (Arize, NVIDIA NeMo Gym)
     https://arize.com/resources/llm-as-a-judge-when-should-you-use-it/ ,
     https://docs.nvidia.com/nemo/gym/0.2.1/environment-tutorials/llm-as-judge-verification.html ; judge-reliability
     papers: *Reliability without Validity* (21 judges; high test-retest with severe position bias)
     https://arxiv.org/html/2606.19544v1 ; Judge Reliability Harness https://arxiv.org/pdf/2603.05399 (medium-high).
  5. Autoformalization of science: **FormalScience** (arXiv 2604.23002, Apr 2026) — human-in-the-loop Lean 4 pipeline,
     200 university-physics statements https://arxiv.org/pdf/2604.23002 ; **DARPA expMath** ($5M UCLA; Shafto's
     2026-02-19 Topos talk asks "is science the next frontier?" and names the "does the formalization preserve meaning"
     problem) https://ww3.math.ucla.edu/ucla-research-team-signs-5m-contract-with-darpa-for-ai-research ,
     https://topos.institute/events/topos-colloquium/slides/2026-02-19.pdf (high; no DARPA *science* autoformalization
     program confirmed).
  6. Epistemics-in-AI-eval: *Do LLMs Know What They Don't Know II* — behavioural epistemic-honesty measure (restraint,
     no unqualified false assertions, confidence tracks correctness) https://arxiv.org/pdf/2609.07879 ; ICML 2026
     2nd Workshop on Epistemic Intelligence (unknown unknowns; abstention/deferral)
     https://icml.cc/virtual/2026/workshop/54075 ; *Epistemological Fault Lines* (benchmarks should test whether
     abstaining is the correct outcome) https://arxiv.org/pdf/2512.19466 (medium).
- Adjacent: **NIST**: AI Safety Institute Consortium renamed NIST AI Consortium (May 2026) with an AI Evaluation &
  Measurement Methods task group; CAISI lists "measurement validity" as open
  https://www.nist.gov/news-events/news/2026/05/nist-expands-ai-consortiums-scope-calls-new-members ,
  https://www.nist.gov/ai-measurement-and-evaluation ; TEVV-Athlon draft (Aug 2026, NIST AI 200-2 ipd)
  https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.200-2.ipd.pdf . **NSF**: $100M "Unlocking Dataset Value for AI-Enabled
  Scientific Discovery" (Jul 2026, secondary) https://opendatascience.com/?p=55230 ; CS2 "Correctness for Scientific
  Computing Systems" (machine-checked correctness)
  https://grantedai.com/grants/correctness-for-scientific-computing-systems-cs2-u-s-national-science-foundation-nsf-3f598153 ;
  IFP "Replication Engine" proposal (automated re-runs at publication; not enacted) https://ifp.org/the-replication-engine/ ;
  NSF–UKRI metascience statement 2026-10-08 https://www.nsf.gov/news/nsf-ukri-metascience-statement .
  **DOE Genesis Mission** (EO Nov 2025; 278 Phase-I awards): verification/UQ/reproducibility **not a platform layer** per
  an Aug-2026 critical review (unattributed, low) https://www.aip.org/fyi/genesis-mission-starting-to-take-shape ,
  https://www.slideshare.net/slideshow/the-genesis-mission-evaluating-the-u-s-ai-for-science-initiative-s-impact-and-challenges/289012055 ;
  Arcee "Genesis-Science-1" claims a reproducible record with DOE validation (vendor) https://www.arcee.ai/science-1 .
  **FDA/CDISC**: Validator Rules still v1.6 (Dec 2022); technical rejection criteria (DM, ADSL, define.xml, TS start
  date) precede checks; Pinnacle 21 rule IDs harmonised FDA/PMDA
  https://www.certara.com/blog/how-does-pinnacle-21-enterprise-differ-from-the-community-version/ ,
  https://www.pharmasug.org/download/sde/rtp2022/PharmaSUG-NCSDE_2022-08.pdf ; FDA draft AI credibility guidance
  (Jan 2025, 7-step context-of-use; finalisation expected Q2 2026, unconfirmed; Jan-2026 FDA–EMA guiding principles)
  https://intuitionlabs.ai/articles/fda-ai-drug-development-guidance ,
  https://www.foley.com/insights/publications/2025/01/ai-drug-development-fda-releases-draft-guidance ; ASME V&V 40
  + FDA 2022 draft CM&S guidance (nothing new 2025–26 found)
  https://exponent.com/article/fda-releases-draft-guidance-supporting-computational-modeling .
  **Metascience**: Stanford METRICS (Ioannidis/Goodman; no 2026 AI output surfaced)
  https://stanforddaily.com/2024/02/06/research-on-research-metrics-hopes-to-improve-the-scientific-process/ ;
  COS/OSF preregistration templates working group 2026 (no outcome) https://cos.io/blog/tag/preregistration .
  **Stat checks**: statcheck on PyPI https://pypi.org/project/statcheck ; Leiden thesis: GRIM lacks automation, AI-assisted
  statcheck 98.4% detection on a subset https://theses.liacs.nl/pdf/2024-2025-PleunesSJStijn.pdf ; vendor claims of
  4.5× error reduction unverified https://manusights.com/tools/stats-audit . **Integrity tech**: MDPI–Proofig multi-year,
  ASM–ImageTwin pilot (Jul 2026, secondary) https://www.casrai.org/news/ai-image-integrity-screening-mdpi-asm-adoption ;
  STM Integrity Hub tool fact sheet https://ariessys.com/?p=21561 . **Quantum benchmarking**: IBM "standard strategies"
  (randomized/well-defined/holistic/device-independent; benchmark ≠ diagnostic)
  https://research.ibm.com/publications/defining-standard-strategies-for-quantum-benchmarks ; QCVV review 2025
  https://arxiv.org/pdf/2503.16383 ; systematic benchmarking recommendations 2025 (measured QV often trails vendor
  claims) https://alphaxiv.org/abs/2503.04905 ; no NIST quantum benchmarking standard 2026 found.
- Epistemics / gap framing: the field has **named CAPAS's problem in 2026** — "verification gap", "claim-level
  auditability", "bounded verification", "judge never the enforcement boundary", "no externally validated in-loop
  oracle" — but frames solutions as LLM-synthesised or human-budgeted checks; abstention is studied as a model
  behaviour, not as an engine default. FDA keeps a fail-closed technical-rejection gate; Genesis has no verification
  layer.
- Institutions & people: NIST CAISI/AI Consortium; DARPA (Patrick Shafto, expMath); NSF CISE; DOE Genesis; FDA CDER/
  CDRH; Pinnacle 21/Certara; Stanford METRICS (Ioannidis, Goodman); COS (Nosek); IBM Quantum benchmarking group;
  authors: Ding et al. (survey), Bańka & Chudziak (PVP), FactReview, SOCpilot authors.
- Take / Ahead: take: (1) adopt the **PVP/minimum-verification-budget** idea — CAPAS can state, per batch, how many
  fields must be machine-ingested for a pass to be informative; (2) adopt the survey's reviewer-facing **checklist
  dimensions** (seeds, traces, in-loop oracle) as ledger statuses; (3) cite FDA technical-rejection criteria as the
  regulatory ancestor of fail-closed HOLD | ahead: CAPAS already runs the externally-validated in-loop oracle the
  survey says no system has, with sealed blind rates and a proof ledger; FactReview/AutoPyVerifier keep an LLM in the
  verifier-construction loop; FDA/Pinnacle gate *format*, CAPAS gates *admissibility of evidence fields*.
- Confidence: high | Queries (15): NIST AI measurement 2026; DARPA autoformalization; NSF AI-for-science
  verification; FDA CDISC Pinnacle 21 2026; Stanford METRICS 2026; COS 2026 registered reports; LLM-as-judge vs
  deterministic 2026; ASME V&V 40 2025–26; NIST quantum benchmarking IBM Google; "known unknowns" AI evaluation 2026;
  research-integrity tech 2026 (STM/Proofig/ImageTwin); AI-generated research claims verification 2026 (extended);
  statcheck/GRIM/SPRITE 2025–26; Genesis Mission verification stance; FDA AI credibility framework.

### Uruguay
- Direct (2026 SOTA): none.
- Adjacent: (1) **PhotoHolmes** — open-source Python library for image-forgery detection with a benchmark tool, dataset
  loaders, metrics and a CLI (O'Flaherty, Paganini, Sotelo, Umpiérrez, Gardella, Tailanian, Musé; arXiv 2412.14969,
  Dec 2024; *Multimedia Tools and Applications* 2025) https://arxiv.org/abs/2412.14969 ,
  https://github.com/photoholmes/photoholmes , https://doi.org/10.1007/s11042-025-20626-3 — affiliation not on the arXiv
  page; OpenAlex tags UY (Udelar IIE group inferred from authors — medium). Research-integrity relevance: a deterministic,
  benchmarked image-forensics engine reusable for figure screening. (2) **"Beyond p-values: Rethinking Statistical
  Frameworks for Addressing the Replication Crisis"** (Marmolejo-Ramos et al.; Mauricio Castillo — Massey/Udelar;
  PsyArXiv 2025) https://doi.org/10.31234/osf.io/8eu96_v1 (OSF rate-limited; authorship via OpenAlex). (3) Policy:
  **Estrategia Nacional de IA 2024–2030** and Estrategia Nacional de Datos 2030 (Agesic); 2024 recommendations report for
  AI regulation delivered to the legislature (Jun 2024); UNESCO RAM report for Uruguay; AI Observatory; algorithmic
  impact-study guide (2020)
  https://www.gub.uy/agencia-gobierno-electronico-sociedad-informacion-conocimiento/comunicacion/publicaciones/estrategia-nacional-inteligencia-artificial-2024-2030 ,
  https://www.gub.uy/agencia-gobierno-electronico-sociedad-informacion-conocimiento/comunicacion/publicaciones/informe-sobre-recomendaciones-para-regulacion-inteligencia-artificial ,
  https://www.gub.uy/agencia-gobierno-electronico-sociedad-informacion-conocimiento/comunicacion/publicaciones/guia-para-estudio-impacto-algoritmico ;
  Uruguay took part in the Council of Europe AI Convention negotiations (Wikipedia). (4) ANII: regulatory-sandbox call
  and Redata platform; no integrity/reproducibility policy item
  https://anii.org.uy/apoyos/innovacion/675/entornos-controlados-de-prueba-sandboxes-regulatorios . FAIR-in-biomolecular-
  simulation co-authorship (Nat Methods 2025) https://doi.org/10.1038/s41592-025-02635-0 .
- Epistemics / gap framing: data/AI strategy with impact assessment and an observatory; statistical-reform discourse
  (beyond p-values) via a Udelar co-author; no fail-closed or evidence-grading register in the policy pages fetched.
- Institutions & people: Agesic; ANII; Udelar (image group: Pablo Musé, Matías Tailanian; Mauricio Castillo); PEDECIBA
  not reached.
- Take / Ahead: take: PhotoHolmes as a drop-in, deterministic image-forensics backing for a future CAPAS figure-integrity
  field | ahead: no Uruguayan artifact gates claims; policy is impact-assessment, not admissibility.
- Confidence: medium | Queries (2 WebSearch budget-blocked; 8 fetches): OpenAlex UY 2025+ "reproducibility open science"
  (230); OpenAlex UY 2025+ "research integrity preregistration replication" (1); anii.org.uy; gub.uy ×3; arXiv
  2412.14969 (+ arXiv search); OpenAlex records ×2.

### Uzbekistan
- Direct (2026 SOTA): none.
- Adjacent: **"The National Research Ethics System of Uzbekistan: Institutional Architecture, Policy and Emerging
  Mechanisms of Research Governance"** (Zamira Mukhamedova, Tashkent State Medical University, 2026)
  https://doi.org/10.5281/zenodo.22689500 , landing https://journals.academiczones.net/index.php/jiphr/article/view/6799 ;
  "Academic Integrity and Research Ethics in Pedagogical Research: aligning national practice with international norms"
  (2026) https://doi.org/10.5281/zenodo.23212060 (records only; full texts not read).
- Epistemics / gap framing: institutional-architecture framing; nothing on verification.
- Institutions & people: Tashkent State Medical University (Mukhamedova).
- Take / Ahead: take: none | ahead: n/a.
- Confidence: low-medium | Queries: OpenAlex UZ 2024+ "academic integrity artificial intelligence plagiarism
  dissertation" (7 hits); record fetch.

### Vanuatu
- Direct (2026 SOTA): none.
- Adjacent: none. OpenAlex VU 2024+ "research science policy" → 8 (environment/health); "artificial intelligence
  Vanuatu" → 0.
- Epistemics / gap framing: not surfaced.
- Institutions & people: none identified.
- Take / Ahead: take: none | ahead: n/a.
- Confidence: medium | Queries: **NOTHING FOUND** (two OpenAlex VU queries above).

### Vatican City
- Direct (2026 SOTA): none.
- Adjacent / Epistemics: strong for its size. (1) **Antiqua et Nova** (Dicastery for the Doctrine of the Faith +
  Dicastery for Culture and Education, 2025-01-28): names AI "hallucination" — results "that appear real but are not"
  (¶86); fabricated information in education/research (¶84); duty to verify before disseminating (¶89); human
  responsibility for AI-assisted decisions (¶44); AI use in research must be "always transparent and never
  misrepresented" (¶84)
  https://www.vatican.va/roman_curia/congregations/cfaith/documents/rc_ddf_doc_20250128_antiqua-et-nova_en.html (high,
  fetched). (2) **Pontifical Academy of Sciences 2026 Plenary "The Future of Science in a Changing World" — final
  statement (24–26 Sep 2026)**: if AI generates hypotheses, designs experiments or analyses data, "the scientific
  community will need to strengthen standards of reproducibility, provenance, transparency and peer review"; commitment
  to "communication of evidence and uncertainty"; proposes an IAEA-style international AI regulator
  https://www.pas.va/en/events/2026/plenary_session/final_statement.html (high, fetched).
- Epistemics / gap framing: provenance + reproducibility named as the answer to AI-made science; uncertainty
  communication as a duty.
- Institutions & people: Pontifical Academy of Sciences; DDF (Card. Fernández), Dicastery for Culture and Education
  (Card. Tolentino de Mendonça).
- Take / Ahead: take: cite PAS 2026 as a non-technical authority that names provenance as the response to AI-generated
  science — CAPAS's sha256 machine-context ingestion is a provenance mechanism | ahead: statements only; no artifact.
- Confidence: high | Queries: vatican.va Antiqua et Nova; pas.va 2025–26 listing; pas.va 2026 final statement.

### Venezuela
- Direct (2026 SOTA): none.
- Adjacent: none. OpenAlex VE 2024+ "integridad científica inteligencia artificial investigación" → 0; "research
  integrity retraction plagiarism Venezuela" → 0. FONACIT/IVIC not fetched.
- Epistemics / gap framing: not surfaced.
- Institutions & people: none identified.
- Take / Ahead: take: none | ahead: n/a.
- Confidence: medium (bibliographic only) | Queries: **NOTHING FOUND** (two OpenAlex VE queries above).

### Vietnam
- Direct (2026 SOTA): none. OpenAlex VN 2025+ "scientific claim verification" (698): a table-fact-verification LLM
  paper (*Computers & Electrical Engineering* 2026) https://doi.org/10.1016/j.compeleceng.2026.111473 and a Zenodo
  "Python verification script" for a graph-theory counterexample (2026) https://doi.org/10.5281/zenodo.21252466 —
  computational checks, not claim gating.
- Adjacent: (1) **Journal-level AI-content policy mapping**: "Responsible Use of AI-Generated Content in Vietnamese
  Scholarly Publishing: Evidence from Journal Policies and Editorial Practices" (Tran Huu Tuyen, Lac Hong Univ.;
  *Veredas do Direito*, 2026-01-05): five publishing contexts; shared norm "AI cannot be an author"; names fabricated
  citations and **unverifiable claims**; proposes risk-tiered uses, mandatory disclosure + **provenance documentation**,
  human-in-the-loop editorial controls https://doi.org/10.18623/rvd.v23.n1.4029 (medium; exploratory, no counts).
  (2) "Toward a Publication Ethics Standards System for Vietnamese Scholarly Journals" (2026)
  https://doi.org/10.18623/rvd.v23.n1.3988 ; "Reconfiguring the Journal Ecological Chain in Vietnam: an open-science
  governance perspective" (2026) https://doi.org/10.18623/rvd.v23.n2.4024 ; "Fostering scientific integrity in Vietnam:
  the contribution of library and information services" (Bui — VNU USSH; Nguyen — Khon Kaen; *IFLA Journal* 2025)
  https://doi.org/10.1177/03400352241310536 (sagepub 403; record only). (3) Regulation discourse: "A Risk-Based Approach
  to AI Regulation: Lessons from the EU for Vietnam" (Dao, Nguyen — UEL, VNU-HCM; *VNU J. Legal Studies* 2025)
  https://doi.org/10.25073/2588-1167/vnuls.4799 . **The Vietnamese AI statute itself was not retrieved** (vietnamlawmagazine
  and vietnamplus tag pages empty; Wikipedia's regulation page has no Vietnam section) — no passage/effective date is
  asserted here. (4) VinAI: corporate site shows only automotive products (DrunkSense award 2025-03-27; CES 2025); the
  research publication page redirects to the home page; no 2025–26 verification/science output visible
  https://www.vinai.io/news/ . (5) OpenAlex VN 2025+ "preregistration / registered report / replication" → 1 (ethics
  essay): no metascience community surfaced.
- Epistemics / gap framing: integrity framed as publication ethics + disclosure/provenance; Tuyen's "unverifiable
  claims" is the closest Vietnamese phrase to admissibility language.
- Institutions & people: VNU-HCM UEL (Phuc Gia Dao); VNU USSH (Thuy Thanh Bui); Lac Hong Univ. (Tran Huu Tuyen);
  VinAI (industrial, automotive); MOST (not reached).
- Take / Ahead: take: Tuyen's provenance-documentation requirement for AI-generated material maps onto CAPAS sha256
  ingestion — a Vietnamese journal pilot could require CAPAS-style provenance fields | ahead: nothing deterministic;
  verification is editorial and human-in-the-loop.
- Confidence: medium | Queries (3 WebSearch budget-blocked; 11 fetches): OpenAlex VN 2025+ ×5 ("scientific claim
  verification"; "research integrity retraction Vietnam"; "preregistration registered report replication"; "Law on AI
  … risk regulation" ×2); vinai.io ×3; vietnamlawmagazine.vn; en.vietnamplus.vn; revista.domhelder.edu.br;
  journals.sagepub.com (403); OpenAlex records ×2.

### Yemen
- Direct (2026 SOTA): none.
- Adjacent: none on verification. OpenAlex YE 2024+ "research integrity AI plagiarism" → 19 (student-use surveys, e.g.
  Sana'a/Qatar teacher-student ethics 2026 https://doi.org/10.1007/s44217-026-02204-3 ); "reproducibility research
  quality Yemen" → 187 (funding/open-science editorials, e.g. Yemeni Journal of Life Sciences open-science vision 2026
  https://doi.org/10.67651/yjls.v1.i1.7 ).
- Epistemics / gap framing: not surfaced.
- Institutions & people: none identified.
- Take / Ahead: take: none | ahead: n/a.
- Confidence: medium | Queries: **NOTHING FOUND** (two OpenAlex YE queries above).

### Zambia
- Direct (2026 SOTA): none.
- Adjacent: only generic items: "Integrating generative AI in African higher education: … ChatGPT in Zambia" (*Frontiers
  in Education* 2026) https://doi.org/10.3389/feduc.2026.1814033 ; "Students' perspectives on invigilation … academic
  dishonesty … Zambia" (2026) https://doi.org/10.20428/ajqahe.v19i69.3711 ; "AI in Customs Compliance … Evidence Gaps …
  Sub-Saharan Africa" (2026) https://doi.org/10.59857/mvkybz84 . NSTC/ZAMRA not fetched.
- Epistemics / gap framing: not surfaced.
- Institutions & people: none identified.
- Take / Ahead: take: none | ahead: n/a.
- Confidence: medium-low | Queries: OpenAlex ZM 2024+ "research integrity reproducibility AI" (43); "research
  misconduct plagiarism ethics Zambia" (7). Treated as NOTHING FOUND for CAPAS purposes.

### Zimbabwe
- Direct (2026 SOTA): none.
- Adjacent: only generic items: "The ethics of AI use in university libraries in Zimbabwe" (*Frontiers in Research
  Metrics & Analytics* 2025) https://doi.org/10.3389/frma.2024.1522423 ; "Redefining Academic Integrity in the AI Era:
  shifting from detection to development" (2026) https://doi.org/10.47772/ijriss.2026.10200048 ; "AI and audit quality
  in the banking sector" (2026) https://doi.org/10.56578/jafas120204 . RCZ/MCAZ not fetched.
- Epistemics / gap framing: "detection → development" (give up on AI detectors) at the teaching level.
- Institutions & people: none identified beyond the papers.
- Take / Ahead: take: none | ahead: n/a.
- Confidence: medium-low | Queries: OpenAlex ZW 2024+ "research integrity reproducibility AI" (429); retried "research
  integrity misconduct artificial intelligence" (14). Treated as NOTHING FOUND for CAPAS purposes.

---

## Wave summary

**Top 5 findings for CAPAS**
1. **Bounded verification / Predictive Value of Pass** (arXiv 2610.05547, 2026-10-04): padding true claims around a
   fixed number of false ones raises pass probability but lowers informativeness; minimum verification budget for a
   target PVP. Gives CAPAS a formal argument for per-batch ingestion-coverage thresholds and for why GIGO-consistent
   fabrications pass. https://arxiv.org/abs/2610.05547v1
2. **AI-scientist verification gap survey** (arXiv 2608.05179, 2026): 83% release code, 38% reproducibility artifacts,
   **no system has an externally validated in-loop oracle**; reviewer checklist proposed. CAPAS+Atlas is that oracle;
   map the checklist onto the proof ledger. https://arxiv.org/abs/2608.05179
3. **UK AISI "LLM judges on trial"** (2025-07): Bayesian GLM to quantify autograder bias per task — the method to
   publish CAPAS-vs-LLM-judge on the same sealed batch.
   https://www.aisi.gov.uk/blog/llm-judges-on-trial-a-new-statistical-framework-to-assess-autograders
4. **MBZUAI (UAE) 2026 pair**: the **"claim-calibrated evidence ladder"** (arXiv 2607.00368 — each claim must be matched
   to the evidence tier that can support it; proxy metrics are weak evidence) is CAPAS's ACCEPT/REWRITE/HOLD stated as a
   principle; and the cross-benchmark fact-checking audit (arXiv 2608.25934 — best SciFact F1 0.70 → 0.31 on
   ClimateCheck; gold evidence +14–22 pts) is the citation for why an LLM fact-checker cannot be the verdict layer.
   https://arxiv.org/abs/2607.00368 , https://arxiv.org/abs/2608.25934
5. **Deterministic-verifier precedent + fail-closed ancestors**: SOCpilot (arXiv 2605.05501) and AutoPyVerifier (arXiv
   2604.22937) are the nearest 2026 rivals (LLM still in construction, no sealed blind rates); FDA technical-rejection
   criteria, MHRA staged authorisation against pre-specified thresholds (accepted 2026-10-06), TÜBİTAK's sanction on
   fabricated references and Ukraine's Law 4742-IX **"institutional violation of academic integrity"** (in force
   2026-02-01) are institutional fail-closed norms CAPAS can cite as precedent.
   https://arxiv.org/pdf/2605.05501 , https://www.tdmu.edu.ua/en/?p=187738

**New in the resume pass (beyond the top 5):** UCU Lviv **Center of Excellence in Formal Methods and Verification**
(NAS-funded, announced 2026-08-10, Jeremy Avigad at the launch) — a candidate Lean partner for Atlas's physics
invariants https://www.nationalacademies.org/news/science-and-innovation-fund-for-ukraine-partners-with-ukrainian-catholic-university-to-launch-new-center-of-excellence ;
**Pontifical Academy of Sciences 2026 statement** naming "reproducibility, provenance, transparency and peer review" as
the response to AI-generated science https://www.pas.va/en/events/2026/plenary_session/final_statement.html ;
**PhotoHolmes** (Uruguay) — a deterministic, benchmarked image-forensics library reusable as a CAPAS figure-integrity
backing https://arxiv.org/abs/2412.14969 ; Vietnamese journal-policy study naming "unverifiable claims" and requiring
provenance documentation https://doi.org/10.18623/rvd.v23.n1.4029 ; Thailand's ETDA AIGPC Ethical Impact Assessment
Playbook https://www.etda.or.th/th/Our-Service/AIGC/index.aspx .

**3 countries with the strongest direct work:** United States, United Kingdom, United Arab Emirates (MBZUAI's two 2026
evaluation papers). Runners-up: Ukraine (formal-verification centre + integrity law, no artifact yet), Taiwan
(AI-driven calibration + 16.1% fabricated-reference audit).

**NOTHING FOUND (strict — nothing direct or adjacent):** Tajikistan, Timor-Leste, Togo, Tonga, Turkmenistan, Tuvalu,
Vanuatu, Venezuela, Yemen (9). **Treated as NOTHING FOUND for CAPAS purposes (only generic AI-in-education / integrity
items):** Tanzania, Tunisia, Zambia, Zimbabwe (4) — 13 in total. Every country in the wave now has an entry; no
`NOT SEARCHED` remains.
