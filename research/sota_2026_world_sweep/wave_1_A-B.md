# World sweep 2026 — Wave 1 (A–B): Afghanistan … Burundi

Date run: 2026-10-14. Agent: Claude (Fable 5.1), following `BRIEF.md`.

**Method note (honest limits).** 31 WebSearch calls were made before the session-wide WebSearch budget ran out (200
calls shared across agents). The small states and Australia (7 searches) were covered by WebSearch. Austria, Belgium,
Brazil and Argentina were then covered by direct WebFetch of primary institutional pages and the Europe PMC REST API
(affiliation-filtered literature queries, 2025–2026), not by a general search engine. Where a planned source returned
404/TLS error it is named as such. Confidence is marked per entry; "medium" usually means "primary page read, but the
coverage of that country is incomplete because search was unavailable".
**Depth pass (same day, resumed session).** Two further WebSearch calls succeeded (BRI 2026; FAPESP/CNPq AI policy)
before the budget closed again. Bing results pages fetched through WebFetch returned unrelated bot-fodder (Spotify,
Windows help) for every query and were discarded. The depth pass therefore used: Europe PMC REST (affiliation and DOI
queries, `resultType=core` for abstracts/affiliations), the arXiv API (author queries), institutional site searches
(conicet.gov.ar, gov.br/cnpq), the eLife API, and ~45 primary-page fetches; the ÖAWI 2026 guideline PDF was read with
pdftotext. Paywalled Nature/Springer/BMJ pages were read via their Europe PMC records. The DOU gazette (in.gov.br)
hung on three attempts, so Portaria CNPq 2664/2026 is cited through the CNPq news page that links it.

---

### Afghanistan
- Direct (2026 SOTA): NOTHING FOUND.
- Adjacent: nothing Afghanistan-specific. Search returned only global items (IFP "Replication Engine" proposal,
  Elsevier Confidence in Research 2025).
- Epistemics / gap framing: no source.
- Institutions & people: none surfaced.
- Take / Ahead: take: — | ahead: — (no comparator).
- Confidence: high that nothing surfaced in English (one query) | Queries: "Afghanistan research integrity
  reproducibility AI verification 2025".

### Albania
- Direct (2026 SOTA): NOTHING FOUND.
- Adjacent: new Law on Science and Scientific Research (Dec 2024) mandating open access/reusability for publicly
  funded research and creating a National Council (ERA Country Report 2024, pub. June 2025:
  https://european-research-area.ec.europa.eu/sites/default/files/documents/2025-06/ERA%20Country%20Report%202024%20Albania.pdf).
  RASH (Albanian Academic Network) + NASRI ran ~20 Open Science / FAIR trainings (June 2025:
  https://rash.al/en/news-main/news/2025/06/20/building-capacity-open-science-albania/ ; EOSC interview with
  Arjan Xhelaj: https://eosc.eu/news/building-capacity-for-open-science-in-albania-insights-from-arjan-xhelaj-of-rash/).
  Western-Balkans RRI recommendations name reproducibility as "a fundamental stumbling block of trust in science"
  (regional, undated: https://wbc-rti.archiv.zsi.at/object/news/23445/attach/WBC_RRI_NET__Recommendations.pdf).
- Epistemics / gap framing: legal/capacity stage; no claim-level evidence standard or AI-integrity position found.
- Institutions & people: RASH (Arjan Xhelaj), NASRI, National Council for Science.
- Take / Ahead: take: nothing operational | ahead: CAPAS already has machine-checkable rules; Albania is at policy level.
- Confidence: medium | Queries: "Albania research integrity open science reproducibility AI 2025".

### Algeria
- Direct (2026 SOTA): NOTHING FOUND.
- Adjacent: 2026 *Aleph* survey of 204 Algerian faculty (Feb–Jul 2025) on AI in research and the "research robot"
  substitution worry; notes universities "beginning to formalise institutional policies for AI use"
  (https://aleph.edinum.org/16438). Perceptions study only, no verification tooling.
- Epistemics / gap framing: ethics-of-use framing, not evidence admissibility.
- Institutions & people: Algerian universities (authors on the Aleph page).
- Take / Ahead: take: — | ahead: CAPAS measures its gate blind; Algeria's literature is attitudinal.
- Confidence: medium | Queries: "Algeria research integrity reproducibility AI verification scientific claims 2025".

### Andorra
- Direct (2026 SOTA): NOTHING FOUND.
- Adjacent: none Andorra-specific; only EU-level hits (ERA Action 14 "AI in science":
  https://community.era.gv.at/era/era-policy-agenda/ongoing-era-actions/ai-in-science/).
- Epistemics / gap framing: no source.
- Institutions & people: none surfaced.
- Take / Ahead: — | —.
- Confidence: high that nothing surfaced | Queries: "Andorra research science policy AI reproducibility 2025".

### Angola
- Direct (2026 SOTA): NOTHING FOUND.
- Adjacent: 1st National Conference of the National Scientific Research Center, Luanda, 29–30 May 2025, with an
  invited lecture on research ethics/integrity (record only:
  https://pure.ulster.ac.uk/en/activities/1st-national-conference-of-the-national-scientific-research-cente/).
  UNESCO Readiness Assessment Methodology (RAM) for AI started (OSIRIS, March 2026, French:
  https://osiris.sn/l-angola-prepare-un-cadre-ethique-pour-l-intelligence-artificielle.html).
- Epistemics / gap framing: national AI-ethics readiness; nothing on scientific evidence standards.
- Institutions & people: Centro Nacional de Investigação Científica (CNIC).
- Take / Ahead: — | —.
- Confidence: medium | Queries: "Angola research integrity science reproducibility AI 2025".

### Antigua and Barbuda
- Direct (2026 SOTA): NOTHING FOUND.
- Adjacent: UWI Five Islands 2nd annual 5IR AI Research Conference, 23–24 June 2025
  (https://global.uwi.edu/media/news/high-level-caribbean-policy-discussions-agenda-uwi-five-islands-2025-ai-conference);
  UNESCO RAM pilot led by the ICT ministry (https://abstvradio.com/ab-makes-strides-toward-ethical-use-of-artificial-intelligence/);
  AI regulation listed as a 2025 legislative priority (https://antiguaobserver.com/?p=300126) — passage not confirmed.
- Epistemics / gap framing: AI-adoption ethics; no research-verification stance.
- Institutions & people: UWI Five Islands; Ministry of ICT.
- Take / Ahead: — | —.
- Confidence: medium | Queries: "Antigua and Barbuda research science AI policy 2025".

### Argentina
- Direct (2026 SOTA): NOTHING FOUND on deterministic/fail-closed claim gating, LLM-vs-deterministic verifiers, or
  sealed evaluation, after the depth pass (CONICET site search, Europe PMC, arXiv author queries). Nearest item is
  **Barrera-Lemarchand, …, Sigman, Navajas (UTDT / CONICET / UBA-ICC), "Collective problem decomposition improves
  the wisdom of deliberative crowds", Nat Commun, 5 Aug 2026** — 1,140 online group deliberations (N=500/240/160):
  groups that decompose a problem into intermediate estimates ("Collective Fermi Estimation") have lower error; causal
  in Study 2; the authors "provide tools to detect and promote it" (https://doi.org/10.1038/s41467-026-76365-y). A
  human-elicitation accuracy mechanism, not a verifier.
- Adjacent: (1) Debat (INTA Córdoba) & Amaral, eLife, 1 Sep 2025 — scholar-led diamond-OA publishing as integrity
  infrastructure (https://doi.org/10.7554/elife.108426). (2) **CONICET launched a Comisión Asesora de Inteligencia
  Artificial, 28 Sep 2026** — scope is institutional management (continues 2025 pilots that included possible use in
  scientific evaluation); members include Laura Ación, Carlos Chesñevar, Silvia Schiaffino, Florencia Luna (ethics);
  no integrity/verification mandate and no guidance for researchers
  (https://www.conicet.gov.ar/el-conicet-puso-en-marcha-su-comision-asesora-de-inteligencia-artificial-para-la-mejora-de-la-gestion-institucional/).
  (3) Open-science policy is still the 2022 "Diagnóstico y lineamientos para una política nacional de Ciencia Abierta"
  (Comité Asesor, Fernanda Beigel; Ley 26.899 of 2013 on repositories) — CONICET's page shows nothing newer
  (https://www.conicet.gov.ar/ciencia-abierta/); site searches for "ciencia abierta" and "inteligencia artificial
  integridad" return no 2025–26 policy item. (4) Disposición 2/2023 "IA Fiable" (JGM) — no evidence requirement
  (https://www.boletinoficial.gob.ar/detalleAviso/primera/287679/20230602). (5) Argentine authorship in the
  large-scale replication literature: Ignacio Pavez (Univ. de San Andrés) in Tyner et al., "Investigating the
  replicability of the social and behavioural sciences", Nature, 1 Apr 2026 (274 claims / 164 papers; 55.1% of claims
  replicated; r 0.25→0.10; 13 methods give 28.6–74.8%) (https://doi.org/10.1038/s41586-025-10078-y). Flores-Kanter
  (Univ. Siglo 21, Córdoba), commentary on the QRP "bestiary", Front Psychol, 16 Feb 2026
  (https://doi.org/10.3389/fpsyg.2026.1692416). Khan KS et al. trial-integrity consensus with Argentine co-author,
  Account Res, 25 Mar 2026 (https://doi.org/10.1080/08989621.2026.2647346). (6) **MetaDocencia** (Laura Ación &
  Nicolás Palopoli, co-executive directors; founded 2020): Latin-American open-science capacity building, >1,700
  trained, >240 Zenodo documents; no 2025–26 verification item on its home page (https://www.metadocencia.org/en/).
  (7) CONICET "Normativa" has no integrity/open-data/AI rule (https://www.conicet.gov.ar/normativa/); CECTE pages 404;
  not among the national Reproducibility Networks listed by UKRN (https://www.ukrn.org/international-networks/).
  UBA / Instituto Balseiro: no AI-verification item surfaced (arXiv author queries Navajas/Carrillo/Sigman returned 0).
- Epistemics / gap framing: AI framed as management efficiency and ethics; accuracy pursued through collective human
  deliberation (Sigman/Navajas line), not through structural claim checks; no fail-closed language found.
- Institutions & people: CONICET (Comisión Asesora IA: Ación, Chesñevar, Schiaffino, Luna); UTDT Laboratorio de
  Neurociencia (Sigman, Navajas); UBA-ICC (Carrillo); INTA (Debat); MetaDocencia (Ación, Palopoli); Beigel (Comité
  Asesor Ciencia Abierta); Univ. Siglo 21 (Flores-Kanter).
- Take / Ahead: take: Debat/Amaral's "free for authors AND readers" (CAPAS open-core aligns); Collective Fermi
  Estimation as a declared, decomposed human-prior field that a sealed batch could ingest beside repliCATS-style
  elicitation | ahead: no Argentine artifact gates claims, seals verdicts, or publishes a proof ledger; CONICET's AI
  body is for management, not for evidence.
- Confidence: medium (site searches + literature APIs; no general search) | Queries: WebSearch (budget-blocked):
  "CONICET ciencia abierta política 2026", "CONICET integridad científica IA lineamientos", "Argentina metaciencia UBA
  Balseiro verificación IA 2026"; WebFetch conicet.gov.ar/?s=ciencia+abierta, /?s=inteligencia+artificial,
  /?s=inteligencia+artificial+integridad, /ciencia-abierta/, CONICET AI-commission item, argentina.gob.ar/jefatura/
  innovacion-ciencia-y-tecnologia, metadocencia.org, ukrn.org/international-networks; Europe PMC AFF:Argentina AND
  (preregistration|registered report|metascience|replication crisis|QRP) 2025–26 (36 hits), AFF:Argentina AND
  (LLM|AI|open science) AND (verification|integrity|reproducibility) (187, mostly off-topic); DOI cores
  10.1038/s41467-026-76365-y, 10.1038/s41586-025-10078-y, 10.3389/fpsyg.2026.1692416; arXiv au:Navajas|Carrillo|Sigman (0).

### Armenia
- Direct (2026 SOTA): NOTHING FOUND.
- Adjacent: APRI Armenia statement on ethical GenAI use, 13 Mar 2026, anchored to the ALLEA Code; commits to
  disclosure and forbids "extensive or significant" GenAI in research outputs
  (https://apri.institute/statement-on-ethical-genai-use/). 2025 *Armenian Economic Review* article arguing Armenian
  science law lacks definitions of "scientific result" and does not address AI (https://arar.sci.am/publication/460800).
- Epistemics / gap framing: disclosure-based; no evidence-admissibility concept.
- Institutions & people: APRI Armenia; NAS RA repository (arar.sci.am).
- Take / Ahead: — | ahead: CAPAS enforces by structure, not by disclosure pledge.
- Confidence: medium | Queries: "Armenia research integrity AI science verification reproducibility 2025".

### Australia
- Direct (2026 SOTA): no Australian deterministic or fail-closed claim-gating system found. Closest direct items:
  (1) **repliCATS / IDEA protocol** (U. Melbourne, Fiona Fidler) — structured elicitation predicting replication;
  reported AUC >0.75 / 73.8% accuracy on 60 outcomes (Feb 2021 figure); SMART program with COS (2023–) aims at
  "automated confidence evaluation of research claims"; page shows no 2024–2026 project milestones
  (https://replicats.research.unimelb.edu.au/). (2) Australians (Lachlan Deer, Melbourne; Dan Liu, ANU; Keaton
  Ellis, Monash; others) are co-authors of Brodeur et al., PNAS, June 2026: 288 researchers / 103 teams;
  reproduction rate 94% human-only, 91% AI-assisted, **37% AI-led**; AI-led teams found fewer major coding errors
  (https://doi.org/10.1073/pnas.2524747123). (3) ARC Policy on Use of Generative AI 2026.1 (approved April 2026):
  assessments with suspected inappropriate GenAI use are removed; applicants certify authorship
  (https://www.arc.gov.au/system/files/2026-04/arc-ai-policy-2026.1-1.pdf).
- Adjacent: CSIRO Science Digital / **Sciansa** AI-for-science platform states need for "trust, provenance,
  reproducibility, security"; benchmarks genomics workflows for reproducibility
  (https://www.csiro.au/en/research/technology-space/ai/science-digital). **AUS-RN** (Fidler, Nakagawa, Barbour,
  Hoffmann, Holcombe, Page, Beaudry, Mol) — AIMOS 2025, 19–21 Nov 2025, Sydney, with Ivan Oransky and Lisa Bero
  (https://www.aus-rn.org/); present at the UKRN national-networks meeting, July 2025. **TGA** Feb 2026 guidance on
  AI-enabled software as a medical device: synthetic data accepted only as a supplement, generation rationale must
  be documented; post-market monitoring of model accuracy; SaMD a 2026–27 enforcement priority
  (https://www.tga.gov.au/node/514668 ; summary https://regask.com/australia-tga-updates-guidance-on-ai-enabled-medical-device-software-and-artg-evidence-requirements/).
  **Diraq** advanced to Stage C of DARPA's Quantum Benchmarking Initiative — DARPA independent V&V team assesses
  design/performance; Albuquerque lab for verifying multi-qubit gate fidelities (bring-up by end-2026)
  (https://www.diraq.com/newsdesk/7x26ihiuojz3nah33t60jefkg2pdz9).
- Epistemics / gap framing: strong metascience culture (MetaMelb: Vazire + Fidler, "credibility" and self-correction
  framing; https://arts.unimelb.edu.au/school-of-historical-and-philosophical-studies/our-research/metamelb). Regulator
  default is evidence-to-same-standard-as-any-device (TGA). Calls for a national research-integrity body remain
  unmet (Adelaide DVC note: https://www.adelaide.edu.au/staff/news/news/list/2024/02/19/deputy-vice-chancellors-message).
- Institutions & people: MetaMelb / repliCATS (Fidler, Vazire); AUS-RN; CSIRO Science Digital; ARC; TGA; Diraq;
  Brodeur PNAS Australian co-authors.
- Take / Ahead: take: repliCATS' calibrated human-elicitation layer (IDEA) as a declared, hash-sealed prior that CAPAS
  could ingest as an evidence field; PNAS 2026 numbers (37% AI-led) as citable support for "no model in the verdict";
  TGA's "synthetic data only as supplement + documented generation" as a SCOPED rule for the pharma beachhead |
  ahead: nobody in Australia publishes a frozen-engine, hash-sealed blind rate or a proof ledger; repliCATS predicts,
  CAPAS gates.
- Confidence: medium-high | Queries (7 WebSearch + 3 WebFetch): "Australia automated verification of scientific claims
  AI-generated research deterministic verifier 2026"; "CSIRO AI for science verification reproducibility program 2026";
  "Australian Reproducibility Network metascience 2025 2026 registered reports"; "Australia research integrity office
  ARIC code 2025 AI generated papers paper mills policy"; "Australian university fact-checking scientific claims
  LLM-as-judge versus verifiable rewards neuro-symbolic 2025 2026 arXiv"; "TGA Australia AI medical device evidence
  requirements clinical evidence guidance 2025 2026"; "Australia quantum benchmarking calibration verification …";
  "Simine Vazire Melbourne MetaMelb …"; WebFetch replicats, aus-rn.org, PNAS record.

### Austria
- Direct (2026 SOTA): no Austrian system gates scientific claims deterministically, but the depth pass found two
  direct-adjacent items. (1) **ÖAWI "Richtlinie zur guten wissenschaftlichen Praxis, Stand 2026"** (adopted at an
  extraordinary general assembly, 18 Jun 2026; PDF https://oeawi.at/wp-content/uploads/2026/07/OAWI-Richtlinie-2026.pdf
  ; page https://oeawi.at/en/guidelines/) — §3.5(a): when AI applications are used in review/evaluation this must be
  disclosed; material under review may not be uploaded to insufficiently protected AI systems; **"Für die eigentliche
  Urteilsfindung sind KI-Anwendungen nicht zulässig"** (AI applications are not permissible for the actual judgment).
  §3.1(g): with AI applications, responsibility for all related steps, results and consequences lies with the user;
  §3.1(h): AI use disclosed per disciplinary standards; §4.1(e): AI use contrary to disciplinary standards is listed
  as a breach of good scientific practice, beside (a) inventing/falsifying sources, data or results; §3.2: FAIR data
  "as open as possible, as closed as necessary", complete third-party-traceable documentation of primary data and every
  processing step; §5.1: institutions must build "KI-Kompetenz" (defined via Art. 3(56) of the EU AI Act). Cites
  DFG 2026 "KI in der wissenschaftlichen Begutachtung" (https://doi.org/10.5281/zenodo.18886257). This is the clearest
  national-level "no model in the verdict" rule found in this wave — a policy, not a system. (2) **ISTA Henzinger
  group — formal runtime verification of learned systems (2025–26)**: "Alignment Monitoring" (28 Jul 2025,
  https://arxiv.org/abs/2508.00021) — verification guarantees hold only if the model matches reality, so a monitor
  maintains a high-probability interval on model–system alignment via sequential forecasting; "Formal Verification of
  Neural Certificates Done Dynamically" (16 Jul 2025, https://arxiv.org/abs/2507.11987); "Monitoring Robustness and
  Individual Fairness" (tool Clemont, 31 May 2025, https://arxiv.org/abs/2506.00496); "Monitoring Hyperproperties over
  Observed and Constructed Traces" (Aug 2025, https://arxiv.org/abs/2508.02301); "Monitoring Discounted Sum
  Properties" (24 Jun 2026, https://arxiv.org/abs/2606.25979). Deterministic monitors with statistical error bounds,
  no LLM; the interval verdict is not stated as fail-closed. Still: **FWF AI-in-applications policy** (7 Jul 2026)
  (https://www.fwf.ac.at/en/news/detail/ai-in-funding-applications-transparency-and-accountability); **Bilateral AI**
  neuro-symbolic cluster (https://www.bilateral-ai.net/).
- Adjacent: **Labenbacher et al. (Med Uni Graz), "Performance of AI Tools in Citing Retracted Literature", JMIR,
  1 May 2026** — 9 free GenAI tools (ChatGPT 4/5, Claude, Gemini, Perplexity, Copilot, SciSpace, ScienceOS, Consensus),
  15 Retraction Watch articles, 5 questions ×2: no tool consistent; best ChatGPT 5 fully correct for 8/15 (53.3%);
  research-focused tools produced no fully correct set; retracted papers appear in overviews without warning, error
  >40% for several tools; "until retraction-aware verification is built in, researchers should independently check"
  (https://doi.org/10.2196/88766). Praschk et al. (PMU Salzburg), audit of chain-of-thought failures in o4-mini /
  Gemini 2.5 stance classification: 14.9% dual errors, 88.8% same wrong label, rationales inconsistent with labels;
  propose "label–rationale coherence" as a readiness metric (J Med Syst, 8 Aug 2026,
  https://doi.org/10.1007/s10916-026-02449-3). TU Wien FORSYTE (Laura Kovács): automated reasoning/verification
  (Vampire), "Lazy Testing of Machine-Learning Models" (IJCAI 2025), FWF doctoral program on automated reasoning
  2025–29 (https://informatics.tuwien.ac.at/orgs/e192-04). TIER2 (ended 31 Dec 2025; https://tier2-project.eu/);
  Cole, Account Res, 24 Aug 2026 (https://doi.org/10.1080/08989621.2026.2721689); Sharifan, reverse fragility index,
  J Clin Epidemiol, 21 Apr 2026 (https://doi.org/10.1016/j.jclinepi.2026.112285). **No Austrian Reproducibility
  Network** exists on UKRN's list of national networks (https://www.ukrn.org/international-networks/); ÖAWI's own
  news lists only new commission members (Oefner Dec 2025, Schmücker Mar 2026) and the May 2025 annual conference
  (https://oeawi.at/en/news-events-en/). FWF 2026 news (Oct) carries nothing further on AI/integrity.
- Epistemics / gap framing: accountability stays with the human user regardless of AI share (ÖAWI, FWF); the judgment
  step is reserved for humans by rule; formal-methods community frames trust as runtime monitoring with error bounds
  (model ≠ reality is the default assumption); measurement papers (Graz, Salzburg) document that GenAI tools fail
  silently on retraction status and rationale coherence.
- Institutions & people: ÖAWI; FWF; ISTA (Thomas Henzinger, Konstantin Kueffner, Ege Saraç); TU Wien FORSYTE
  (Kovács) and VCLA (Ciabattoni, Szeider); Bilateral AI (Locatello, Legenstein); Med Uni Graz (Labenbacher,
  Bornemann-Cimenti); PMU Salzburg (Wiesinger); Know-Center Graz (Cole).
- Take / Ahead: take: cite ÖAWI 2026 §3.5(a) verbatim as a national integrity rule that matches CAPAS's "no language
  model in the verdict"; Henzinger's alignment monitoring as the model for a declared model↔instrument alignment field
  with an interval instead of a point (Atlas calibration snapshots); Labenbacher's retraction test as a cheap
  structural check CAPAS could add (cited DOI ∈ Retraction Watch → HOLD) | ahead: Austria states the rule and monitors
  running systems; nobody there ships a claim-level gate with sealed blind rates or a proof ledger.
- Confidence: medium-high (primary PDF read; literature APIs; no general search) | Queries: WebSearch
  (budget-blocked): "FWF Reproduzierbarkeit 2026", "ISTA Henzinger TU Wien neural network verification", "Austrian
  Reproducibility Network", "ÖAWI KI Empfehlung 2025 2026"; WebFetch oeawi.at (/en/, /en/guidelines/, /en/news-events-en/,
  2026 PDF via pdftotext), fwf.ac.at/en/news, fwf.ac.at sitemap (project links only), informatics.tuwien.ac.at
  /orgs/e192-04 and /research-groups/ (404), caiml.org (domain parked), oana.at (casino squatter, not OANA),
  ista.ac.at/en/research/henzinger-group/ (404), arXiv au:Henzinger_Thomas AND (neural|monitor|language model) (42,
  10 read), arXiv au:Bartocci|Szeider|Ciabattoni (0); Europe PMC AFF:Austria AND (neural network verification|formal
  verification|LLM AND (verification|hallucination|integrity)) 2025-06→ (26); DOI cores 10.2196/88766,
  10.1007/s10916-026-02449-3; ukrn.org/international-networks.

### Azerbaijan
- Direct (2026 SOTA): NOTHING FOUND.
- Adjacent: AI Strategy of the Republic of Azerbaijan 2025–2028 (presidential decree, March 2025) with attention to
  academic research (https://isi.az/en/news/6339); Nakhchivan State University training on AI tools in research,
  Dec 2025 (https://ndu.edu.az/xeberler/elmi-tedqiqatlarda-suni-intellekt-aletlerinden-istifade-adli-telim-kecirilib).
- Epistemics / gap framing: adoption/strategy framing.
- Institutions & people: ANAS; Nakhchivan State University; Azerbaijan Technical University Open Science Office (older).
- Take / Ahead: — | —.
- Confidence: medium | Queries: "Azerbaijan research integrity AI science reproducibility 2025".

### Bahamas
- Direct (2026 SOTA): NOTHING FOUND.
- Adjacent: national AI policy / white paper being drafted (2025 budget debate;
  https://www.tribune242.com/news/2025/jun/19/govt-targets-white-paper-to-be-ai-caribbean-leader).
- Epistemics / gap framing: none.
- Institutions & people: Ministry of Economic Affairs.
- Take / Ahead: — | —.
- Confidence: medium | Queries: "Bahamas research science AI policy reproducibility 2025".

### Bahrain
- Direct (2026 SOTA): NOTHING FOUND.
- Adjacent: University of Bahrain AI Usage Regulation v01/2025 (council-approved 27 Mar 2025; scope academic,
  research, students) (https://governance.uob.edu.bh/wp-content/uploads/gravity_forms/1-5c61521fd6ccc367f92ae7eb104b9326/2025/04/64-AI_Usage_Regulation_En.pdf);
  workshop "Ethics of using AI in research and education", 29 Mar 2026
  (https://www.uob.edu.bh/university-of-bahrain-holds-virtual-workshop-on-ethics-of-using-ai-in-research-and-education/).
- Epistemics / gap framing: transparent documentation of AI assistance; no verification layer.
- Institutions & people: University of Bahrain.
- Take / Ahead: — | ahead: CAPAS verifies; UoB regulates use.
- Confidence: medium | Queries: "Bahrain AI research integrity science verification 2025 university".

### Bangladesh
- Direct (2026 SOTA): NOTHING FOUND.
- Adjacent: Prothom Alo dataset of ≥325 retractions linked to Bangladeshi institutions 2019–Jun 2026 (Daffodil IU 44,
  North South U 42, 26 by one researcher); causes include peer-review manipulation, paper mills, data inconsistencies,
  and AI-generated content at Islamic University Kushtia
  (https://www.plagiarismtoday.com/2026/08/12/bangladeshs-325-paper-retraction-crisis/ ;
  https://casrai.org/news/bangladesh-325-retracted-papers-university-investigations-2026). Press-derived numbers, not
  independently verified.
- Epistemics / gap framing: integrity crisis reported by journalism, not by an institutional ledger.
- Institutions & people: UGC Bangladesh (investigations), Daffodil IU, North South U.
- Take / Ahead: take: a live case where a public, re-derivable ledger of institutional claims would matter | ahead:
  CAPAS states it is NOT a fraud detector; Bangladesh's problem is fraud, so CAPAS should not oversell here.
- Confidence: medium | Queries: "Bangladesh research integrity paper mills reproducibility AI verification 2025".

### Barbados
- Direct (2026 SOTA): NOTHING FOUND.
- Adjacent: UWI Cave Hill CIBC Caribbean Research Grants 2025–27 prioritising AI/ML (notice 10 Dec 2025:
  https://sta.uwi.edu/news/notices/notice.asp?id=27833); UWI AI Innovation Centre (Dec 2025) and CAIF 2026
  (https://sta.uwi.edu/news/releases/release.asp?id=23165); Deloitte "Barbados at the AI crossroads"
  (https://www.deloitte.com/content/dam/assets-zone3/cbc/en/docs/about/2025/bb-at-the-ai-crossroads.pdf).
- Epistemics / gap framing: none on evidence standards.
- Institutions & people: UWI Cave Hill; Justin Robinson (UWI Five Islands).
- Take / Ahead: — | —.
- Confidence: medium | Queries: "Barbados research AI policy science UWI Cave Hill 2025".

### Belarus
- Direct (2026 SOTA): NOTHING FOUND.
- Adjacent: none; only a 2021 pravo.by science-plan item surfaced (https://pravo.by/novosti/obshchestvenno-politicheskie-i-v-oblasti-prava/2021/mart/60802/).
- Epistemics / gap framing: no source.
- Institutions & people: NAS Belarus, Higher Attestation Commission (not searched directly).
- Take / Ahead: — | —.
- Confidence: high that nothing surfaced in English | Queries: "Belarus research integrity AI science reproducibility 2025".

### Belgium
- Direct (2026 SOTA): NOTHING FOUND built in Belgium that gates claims deterministically. Closest: Belgian
  co-authors (Hasselt — Stephan Bruns; Liège — HEC; Ghent) in Brodeur et al., PNAS June 2026 (AI-assisted 91% vs AI-led
  37% vs human 94% reproduction; https://doi.org/10.1073/pnas.2524747123) — the strongest 2026 datum this wave that
  "model-in-the-loop" verification underperforms humans when unsupervised.
- Adjacent: **Belgian Reproducibility Network (BE-RN)** — correct site https://reproducibilitynetwork.be/ (the
  earlier reproducibility.be was a wrong domain); peer-led, kick-off online 10 Nov 2022; steering group Roosmarijn
  Vandenbroucke (UGent/VIB), Christophe Phillips (FRS-FNRS / ULiège), Rrita Bajraktari (ULB); local nodes ULiège
  (Biernaux), UGent (Cummins), ITM Antwerp (Verdonck); ReproducibiliTea Leuven; open meetings every 4th Tuesday; 2025
  activity is a humanities roundtable "Can we reproduce the past?" (9 Sep 2025); its activities page lists OSIRIS
  (KU Leuven partner) and TIER2 but **no statistics-checking, pre-registration or AI tooling**
  (https://reproducibilitynetwork.be/members/ ; https://reproducibilitynetwork.be/activities-in-belgium/). Attended the
  July 2025 UKRN meeting; listed by UKRN (https://www.ukrn.org/international-networks/). **KU Leuven "Responsible use
  of GenAI" research guidance, last updated 3 Sep 2026** — living document; GenAI use must be reported in publications,
  project applications and doctoral theses "whenever new output is generated"; defers principles to kuleuven.be/genai
  and the ERA Forum EU guidelines; no verification rule and no stated prohibitions on the page
  (https://research.kuleuven.be/en/integrity-ethics/integrity/practices/genai/genAI). **FNRS open science**: green OA
  mandatory (board decision 12 Dec 2023), diamond encouraged; DMPs required for PDR/WELBIO/WEL-T; funds Peer Community
  In from 2025; optional open-science narrative in applications since the 2025 call, explicitly "not a compulsory
  evaluation criterion"; PeriScops portal 2025; no AI, reproducibility or pre-registration clause
  (https://www.frs-fnrs.be/en/our-commitments/open-science); FNRS integrity page names a Higher Committee for
  Scientific Integrity (CSIS), no AI (https://www.frs-fnrs.be/en/our-commitments/scientific-integrity). **FWO** research
  policy lists integrity, open access, DMP pages; no AI or reproducibility item
  (https://www.fwo.be/en/about-fwo/research-policy/). **VCWI** (chair Gert Storms) — no AI advice (https://www.vcwi.be/en).
  Belgian authorship in 2026 AI-disclosure work: Steve Coppens (UZ/KU Leuven) in Fettiplace et al., modified-Delphi
  recommendations for AI disclosure in scientific writing/peer review (endorses AI-detection software for reviewers,
  checklists for AI-driven research), Reg Anesth Pain Med, 5 Jun 2026 (https://doi.org/10.1136/rapm-2025-106852);
  Deschepper (UGent), expert consensus evaluation of GPT-4o clinical-letter summaries, JMIR Med Inform, 11 May 2026
  (https://doi.org/10.2196/90374). Earlier items stand: Ambrosj/Dierickx, Account Res, 31 Jan 2026
  (https://doi.org/10.1080/08989621.2026.2622302); Van Den Bossche (Ghent/VIB), Microbiome, 23 Jul 2026
  (https://doi.org/10.1186/s40168-026-02455-0); Guyatt, Res Integr Peer Rev, 30 Jun 2026
  (https://doi.org/10.1186/s41073-026-00235-w); Pinheiro, Clin Pharmacol Ther, 13 Aug 2026
  (https://doi.org/10.1002/cpt.70400); FARI (https://www.fari.brussels/); KCE no item. Flanders AI Research Program
  page returned title only; Ghent integrity/open-science URLs 404 (three variants).
- Epistemics / gap framing: disclosure-first (KU Leuven, FNRS, Delphi); open science is rewarded narratively, not
  gated; reproducibility is a volunteer network agenda; the value-free/value-laden tension is debated explicitly
  (Ambrosj); FARI frames law→ML as a translation problem.
- Institutions & people: BE-RN (Vandenbroucke, Phillips, Bajraktari, Cummins); VCWI (Storms); KU Leuven (Dierickx,
  Ambrosj, Coppens); UGent (Deschepper, Van Den Bossche); Hasselt (Bruns); FARI (Nowé, Bersini, Lewkowicz); FNRS CSIS.
- Take / Ahead: take: cite PNAS 2026 as external evidence for "no LLM in the verdict"; FNRS's "narrative, not a
  criterion" is the fail-open default CAPAS inverts (declare → gate); the Delphi's "AI-driven research checklist" as a
  field-schema source | ahead: no Belgian artifact publishes a frozen, hash-sealed verdict set or a proof ledger;
  BE-RN has no tooling.
- Confidence: medium-high (primary pages read; no general search) | Queries: WebSearch (budget-blocked): "Belgian
  Reproducibility Network", "FWO FNRS research integrity generative AI 2025 2026", "KU Leuven Ghent statcheck
  reproducibility", "Belgium AI verification scientific claims LLM judge deterministic 2026"; WebFetch
  reproducibilitynetwork.be (/, /news/, /news/kick-off/, /members/, /activities-in-belgium/, 2025 roundtable),
  research.kuleuven.be practices + genAI pages, frs-fnrs.be (home, scientific-integrity, open-science), fwo.be (home,
  research-policy, research-integrity 404), ugent.be integrity (404 ×3), flandersairesearch.be (title only), vcwi.be,
  fari.brussels, kce.fgov.be, ukrn.org/international-networks; Europe PMC AFF:Belgium AND (statcheck|statistical
  reporting errors|LLM AND (verification|hallucination|integrity|peer review)) 2025-06→ (45); DOI cores
  10.1136/rapm-2025-106852, 10.2196/90374; PNAS record.

### Belize
- Direct (2026 SOTA): NOTHING FOUND.
- Adjacent: University of Belize Research Policy (26 Feb 2025; ethics + data management, no AI clause)
  (https://ub.edu.bz/wp-content/uploads/2025/08/University-of-Belize-Research-Policy-rev-0.pdf); Belize contribution to
  UN CSTD 2025–26 "STI in the age of AI" (17 Nov 2025:
  https://unctad.org/system/files/non-official-document/cstd2025-26_ai_c03_belize_en.pdf); national AI policy in early
  stages (https://digitalagenda.gov.bz/?p=5717).
- Epistemics / gap framing: none on evidence standards.
- Institutions & people: University of Belize; Ministry of E-Governance.
- Take / Ahead: — | —.
- Confidence: medium | Queries: "Belize research science AI policy 2025".

### Benin
- Direct (2026 SOTA): NOTHING FOUND.
- Adjacent: nothing Benin-specific surfaced (only global items).
- Epistemics / gap framing: no source.
- Institutions & people: none surfaced (Université d'Abomey-Calavi not searched directly).
- Take / Ahead: — | —.
- Confidence: high that nothing surfaced in English | Queries: "Benin research integrity AI science reproducibility 2025".

### Bhutan
- Direct (2026 SOTA): NOTHING FOUND.
- Adjacent: National AI Strategy 2025 (GovTech; https://tech.gov.bt/wp-content/uploads/2025/10/National-AI-Strategy-2025.pdf);
  UNDP AI Readiness Assessment 2024 flagging "limited monitoring mechanisms and underdeveloped concepts of
  explainability" (https://www.undp.org/node/504856); Bhutan–Canada AI governance workshop, Jan 2026
  (https://asianews.network/?p=250716).
- Epistemics / gap framing: GNH-aligned "AI as human tool"; no research-evidence standard.
- Institutions & people: GovTech Agency; PM Tshering Tobgay (Feb 2026 statement, single aggregator source).
- Take / Ahead: — | —.
- Confidence: medium | Queries: "Bhutan research AI policy science integrity 2025".

### Bolivia
- Direct (2026 SOTA): NOTHING FOUND.
- Adjacent: BITSS project "Disseminating research transparency in Peru, Bolivia and Chile" (undated page, execution
  unconfirmed: https://www.bitss.org/projects/disseminating-research-transparency-in-peru-bolivia-and-chile/); FES
  "Bolivia en la era de la IA" on infrastructure gaps and need for responsible-AI debate
  (https://collections.fes.de/publikationen/content/titleinfo/1953697).
- Epistemics / gap framing: sovereignty/infrastructure framing.
- Institutions & people: UMSA; Viceministerio de Ciencia y Tecnología (not searched directly).
- Take / Ahead: — | —.
- Confidence: medium | Queries: "Bolivia integridad científica reproducibilidad inteligencia artificial investigación 2025".

### Bosnia and Herzegovina
- Direct (2026 SOTA): NOTHING FOUND.
- Adjacent: ERA Country Report 2024 (pub. June 2025): fragmented state/entity/canton governance, R&D ≈0.19% GDP
  (https://european-research-area.ec.europa.eu/sites/default/files/documents/2025-06/ERA%20Country%20Report%202024%20BiH.pdf);
  Greljo, Delalić, Mehonić (Sarajevo-linked) 2025 arXiv on evaluating research institutes in small countries with AI
  focus (https://arxiv.org/abs/2501.14773); no national open-science policy (WB RRI recommendations).
- Epistemics / gap framing: institutional-evaluation framing.
- Institutions & people: University of Sarajevo.
- Take / Ahead: — | —.
- Confidence: medium | Queries: "Bosnia and Herzegovina research integrity AI science reproducibility 2025".

### Botswana
- Direct (2026 SOTA): NOTHING FOUND.
- Adjacent: 2025 *Journal of Ethics in Higher Education* two-part student survey on research ethics/integrity
  knowledge-practice gap (https://jehe.globethics.net/article/view/8444); UB scholars at World Congress of Bioethics,
  July 2026, on AI in health data and externally generated bias
  (https://www.ub.bw/news/ub-scholars-bring-african-perspectives-global-bioethics-debate).
- Epistemics / gap framing: ethics/training framing.
- Institutions & people: University of Botswana.
- Take / Ahead: — | —.
- Confidence: medium | Queries: "Botswana research integrity AI science reproducibility 2025".

### Brazil
- Direct (2026 SOTA): no deterministic claim gate found, but Brazil is this wave's strongest **adjacent-direct**
  country. (1) **Brazilian Reproducibility Initiative (BRI)** — now an **eLife Reviewed Preprint v1, 10 Jul 2026**,
  eLife assessment "important" / "convincing" (https://elifesciences.org/reviewed-preprints/111001 ; DOI
  https://doi.org/10.1101/2025.04.02.645026). Protocols pre-registered on OSF before experiments; per-method
  validation committees, each experiment judged by three members blind to replication results; 143 replications of
  56 experiments (MTT, RT-PCR, elevated plus maze) by 56 labs; **53 invalidated** (protocol deviations, documentation,
  sample size) → 90 valid replications of 45 experiments. Five pre-declared criteria: (a) original inside the
  replication 95% prediction interval 17/39 = 44%; (b) replication estimate inside original CI 13/45 = 29% (26% at
  replication level); (c) fixed-effects p<0.05 same sign 9/45 = 20%; (d) ≥half of replications significant same
  direction 22%; (e) ≥half of labs judged success 42%; **27% met at least half of the applicable criteria**. 91% of
  replication effects smaller than original (median relative difference 80% → 8%); CV ratio original/replication median
  0.55 (PCR 0.28); sign errors 2/45; original–replication r = 0.82 driven by one outlier, 0.22 without it. Discussion
  asks for consensus taxonomies of design terms, pre-registration only after pilot work, independent post-experiment
  validation; "solutions will be elaborated in a future article". Funded by Serrapilheira, FAPERJ, CNPq (Amaral).
  Lessons paper, MetaArXiv 19 May 2026 (https://doi.org/10.31222/osf.io/8y3tg_v1); JoVE account (20 May 2026): 7 years,
  ~US$240k, failures traced to operational drift not "the science" (https://blog.jove.com/what-a-7-year-replication-project-says-about-your-lab-2026).
  Fanelli, Tan, Amaral, compression metric predicting reproducibility, R Soc Open Sci, 9 Jul 2025
  (https://doi.org/10.1098/rsos.241446). (2) **Portaria CNPq nº 2.664, 6 Mar 2026 — Política de Integridade na
  Atividade Científica** (news page updated 6 Jul 2026, linking the DOU text
  https://www.in.gov.br/web/dou/-/portaria-cnpq-n-2.664-de-6-de-marco-de-2026-691779232 ;
  https://www.gov.br/cnpq/pt-br/assuntos/noticias/cnpq-em-acao/cnpq-publica-portaria-que-institui-politica-de-integridade-na-atividade-cientifica):
  generative-AI use allowed but must be declared for any tool and any phase (tool + purpose); submitting AI output as
  human-authored prohibited; author fully responsible for AI-introduced errors; AI "not recommended" for writing
  pareceres; CIAC decides cases; sanctions minor/serious/very serious up to repayment, debarment and revocation of a
  grant "obtained through unfounded claims"; ten-principle code of conduct merged in. A secondary legal blog (3 Apr
  2026) reads it as "using AI to create data not actually collected is scientific fraud"
  (https://doutoranathalia.com.br/blog/portaria-cnpq-2664-2026-ia-pesquisa/) — treat that wording as secondary.
- Adjacent: **Rede Brasileira de Reprodutibilidade (RBR)** — https://www.reprodutibilidade.org/ (UKRN-listed; members
  directory, ambassador program, "Guias práticos" 28 Jul 2025; no AI item); paper in An Acad Bras Cienc, 15 Jun 2026
  (https://doi.org/10.1590/0001-3765202620251108). **FAPESP**: seven strategic axes 2026–28 (approved 18 Mar 2026)
  include "digital transition and AI" and quantum, with R$400M extra; projects must include "advanced data management
  using AI"; no integrity/reproducibility clause
  (https://agencia.fapesp.br/fapesp-define-sete-eixos-estrategicos-de-pesquisa-para-o-periodo-2026-2028/57582);
  Code of Good Scientific Practice is still the 2014 edition, no AI clause (https://fapesp.br/boaspraticas); open
  science page: DMPs mandatory for all modalities, OA Portaria CTA 01/2019, data-repository network since Dec 2019,
  computational-process openness "helps others verify reproducibility", no pre-registration or AI
  (https://fapesp.br/openscience/); FAPESP's 2025 guidance on AI in thematic-project reports is reported only by the
  secondary blog (not located on fapesp.br). **BRISPE VII** (Dec 2024, UFRJ, Sonia Vasconcelos): "research integrity and
  generative AI" (https://revistapesquisa.fapesp.br/impactos-da-inteligencia-artificial-generativa/). Amaral in
  "eleven paths forward" (MetaArXiv 30 Jul 2026, https://doi.org/10.31222/osf.io/g57pk_v1) and CORTRE Stage-1 RR
  (https://doi.org/10.31222/osf.io/6wj82_v1); Debat & Amaral, eLife 1 Sep 2025 (https://doi.org/10.7554/elife.108426);
  Galdino-Santos spin review, J Dent, 19 Aug 2026 (https://doi.org/10.1016/j.jdent.2026.106988); TOP 2025 update
  (https://doi.org/10.1186/s41073-026-00223-0). **USP C4AI** (USP–IBM–FAPESP) lists AI-for-science lines (ocean,
  climate) and an AI observatory, **no verification/reproducibility line**; page footer 2020–24
  (https://c4ai.inova.usp.br/). Unicamp AI-for-science verification: NOTHING FOUND (no reachable primary page; Europe
  PMC AFF:Brazil AND LLM AND (integrity|hallucination|verification) 2025–26 gave 235 hits, none on verification of
  research claims). ABEC site 403; SciELO blog 403; reprodutibilidade.bio.br TLS error; PBIA page captcha.
- Epistemics / gap framing: replicability reported as a range over pre-declared criteria plus a "≥half of criteria"
  summary; invalidation before unsealing is itself a published number (53/143); funder policy moves from
  disclosure (FAPESP 2014 code) to declared-use-with-sanctions (CNPq 2026); AI-for-science programs frame AI as data
  management, not as something to be verified.
- Institutions & people: IBqM-UFRJ (Olavo Amaral, Clarissa Carneiro, Kleber Neves); RBR; Instituto Serrapilheira;
  CNPq (CIAC); FAPESP; USP C4AI; UFRJ (Sonia Vasconcelos, BRISPE); SciELO; Fanelli (collab.).
- Take / Ahead: take: BRI's five-criteria range + "≥half of criteria" summary + published invalidation count as the
  reporting template for CAPAS sealed batches (declare criteria before unsealing; publish what was excluded and why);
  CORTRE as the write-up template; CNPq 2664/2026 "grant obtained through unfounded claims → revocation" and
  "AI output must be declared with tool + purpose" as policy anchors for the regulated-submission beachhead; Fanelli's
  compression metric as a declared-prior field | ahead: BRI replicates over 7 years with 56 labs; CAPAS gates in
  seconds with a re-derivable hash and a public ledger and already runs sealed-before-outcomes per batch; no Brazilian
  funder or center ships a structural check behind its AI-disclosure rule.
- Confidence: high for BRI/CNPq (primary records read), medium for USP/Unicamp/FAPESP-AI (pages partial or absent) |
  Queries: WebSearch "Brazilian Reproducibility Initiative 2026 results replicability Amaral", "FAPESP política IA
  pesquisa integridade boas práticas 2026" (3 more budget-blocked: CNPq diretrizes IA 2026; USP Unicamp IA ciência
  verificação; Ciência Aberta Brasil 2026; integrity tools/paper mills SciELO ABEC); WebFetch eLife API 111001 (3
  offsets), blog.jove.com, Pesquisa FAPESP (2018 network article; 2024 BRISPE), agencia.fapesp.br eixos, fapesp.br
  /boaspraticas and /openscience/, gov.br/cnpq search + integrity-policy news page, in.gov.br DOU (hung ×3),
  reprodutibilidade.org, c4ai.inova.usp.br, abecbrasil.org.br (403), reprodutibilidade.bio.br (TLS); Europe PMC
  AFF:Brazil AND (LLM|generative AI) AND (integrity|hallucination|fabricated references|verification) 2025–26 (235),
  AUTH:Beigel|Vasconcelos (27, none topical); earlier Europe PMC queries as in wave 1.

### Brunei
- Direct (2026 SOTA): NOTHING FOUND.
- Adjacent: AITI voluntary Guide on AI Governance and Ethics (11 Apr 2025; accountability + integrity principles)
  (https://usasean.org/article/brunei-releases-voluntary-ai-guidelines-enhance-responsibility-and-trust); UBD first
  government institution with an AI policy; UBD–Baiduri AI research MoU, 4 Nov 2025
  (https://ubd.edu.bn/2025/11/04/ubd-and-baiduri-bank-to-advance-ai-research-and-talent-development).
- Epistemics / gap framing: governance/ethics; no research verification.
- Institutions & people: AITI; UBD; MTIC (AI strategy under development).
- Take / Ahead: — | —.
- Confidence: medium | Queries: "Brunei research AI policy science integrity university 2025".

### Bulgaria
- Direct (2026 SOTA): nearest direct item is **COMPL-AI** (Guldimann … Vechev; arXiv 2410.07959, v2 3 Feb 2025) — a
  technical interpretation of the EU AI Act into measurable checks plus an open benchmarking suite; evaluated 12 LLMs;
  INSAIT (Sofia) is a co-developer per BTA/LinkedIn secondary sources, affiliations not listed on the arXiv page
  (https://arxiv.org/abs/2410.07959). It is a benchmark harness for models, not a gate for scientific claims, but the
  "regulation → measurable technical requirement" move is the same shape as CAPAS's field schema.
- Adjacent: INSAIT (Sofia University unit; CSRankings 14th in Europe, 1st in Eastern Europe as of March 2026; MIT CSAIL
  joint programme July 2025) (https://insait.ai/ ; https://www.bta.bg/en/news/bulgaria/922771-insait-mit-csail-launch-joint-research-programme-to-advance-ai-and-computer-sci).
  Nothing found on Bulgarian research-integrity or reproducibility policy.
- Epistemics / gap framing: compliance-as-benchmark; no fail-closed semantics (a model "scores", it is not refused).
- Institutions & people: INSAIT (Martin Vechev); Sofia University; LatticeFlow.
- Take / Ahead: take: COMPL-AI's mapping of legal text to technical checks as a template for mapping ICH/FDA statistical
  guidance to CAPAS fields | ahead: COMPL-AI scores models fail-open (a score is always produced); CAPAS refuses what
  is undeclared.
- Confidence: medium | Queries: "Bulgaria research integrity AI verification reproducibility INSAIT 2025 2026";
  WebFetch compl-ai.org (title only), arxiv 2410.07959.

### Burkina Faso
- Direct (2026 SOTA): NOTHING FOUND.
- Adjacent: BITSS catalyst training at Thomas Sankara University / CEDRES, Ouagadougou on transparent and reproducible
  methods (undated: https://www.bitss.org/?p=10831); earlier BITSS Ouagadougou workshop, April 2018, on pre-analysis
  plans and p-hacking (https://www.bitss.org/?p=6506).
- Epistemics / gap framing: pre-registration pedagogy.
- Institutions & people: Université Thomas Sankara; CEDRES; CNRST (not searched directly).
- Take / Ahead: — | —.
- Confidence: medium | Queries: "Burkina Faso research integrity AI science reproducibility 2025".

### Burundi
- Direct (2026 SOTA): NOTHING FOUND.
- Adjacent: National AI Strategy validated 22 Apr 2026 (period reported as 2025–2030 or 2026–2030, sources conflict);
  six pillars incl. training/research and ethics (https://www.digitalbusiness.africa/burundi-la-strategie-nationale-de-lintelligence-artificielle-validee-axes-et-objectifs/ ;
  https://www.undp.org/fr/node/559771); National Data Governance Strategy validated Nov 2025.
- Epistemics / gap framing: foundations (connectivity, data) first.
- Institutions & people: Ministry of Finance (lead), UNDP.
- Take / Ahead: — | —.
- Confidence: medium | Queries: "Burundi research science AI policy integrity 2025".

---

## Wave summary

**Top 5 findings for CAPAS**
1. **Brodeur et al., PNAS (June 2026)** — randomized 288 researchers / 103 teams: reproduction 94% human-only, 91%
   AI-assisted, **37% AI-led**; AI-led teams found fewer major coding errors. Australian and Belgian co-authors.
   External, large-n support for "no model in the verdict". https://doi.org/10.1073/pnas.2524747123
2. **Brazilian Reproducibility Initiative — eLife Reviewed Preprint v1, 10 Jul 2026 ("important", "convincing")** —
   pre-registered on OSF, validation committees blind to results, 143 replications → 53 invalidated → 90 valid of 45
   experiments; five pre-declared criteria give **20–44%**, **27% meet ≥half of criteria**; 91% of effects smaller.
   Template for CAPAS sealed-batch reporting (declare criteria before unsealing, publish the invalidation count).
   https://elifesciences.org/reviewed-preprints/111001 · https://doi.org/10.1101/2025.04.02.645026 · lessons:
   https://doi.org/10.31222/osf.io/8y3tg_v1
3. **ÖAWI (Austria) Richtlinie 2026 (adopted 18 Jun 2026)** — §3.5(a) "Für die eigentliche Urteilsfindung sind
   KI-Anwendungen nicht zulässig" (AI not permissible for the actual judgment in review/evaluation); AI use disclosed;
   responsibility stays with the user (§3.1g); AI use against disciplinary standards listed as misconduct (§4.1e).
   The clearest national "no model in the verdict" rule in this wave — a policy CAPAS implements mechanically.
   https://oeawi.at/wp-content/uploads/2026/07/OAWI-Richtlinie-2026.pdf · Companion funder rules: **FWF** 7 Jul 2026
   (https://www.fwf.ac.at/en/news/detail/ai-in-funding-applications-transparency-and-accountability) and **CNPq Portaria
   2.664/2026** (6 Mar 2026: AI use declared with tool + purpose; AI output as human-authored prohibited; sanctions up to
   repayment/revocation for grants "obtained through unfounded claims")
   (https://www.gov.br/cnpq/pt-br/assuntos/noticias/cnpq-em-acao/cnpq-publica-portaria-que-institui-politica-de-integridade-na-atividade-cientifica).
4. **ISTA Henzinger group — runtime verification of learned systems (2025–26)**: "Alignment Monitoring" (interval on
   model↔reality alignment via sequential forecasting, https://arxiv.org/abs/2508.00021), dynamic verification of
   neural certificates (https://arxiv.org/abs/2507.11987), Clemont robustness/fairness monitors
   (https://arxiv.org/abs/2506.00496). Deterministic, bounded-error, no LLM — the formal-methods analogue of CAPAS's
   instrument-snapshot admissibility; not stated as fail-closed.
5. **repliCATS / IDEA protocol (Melbourne)** — structured elicitation predicting replication (AUC >0.75 on 60 outcomes),
   SMART program toward automated confidence evaluation; a declared human-prior field CAPAS could ingest and seal
   (https://replicats.research.unimelb.edu.au/). Same family: Argentina's **Collective Fermi Estimation** (Nat Commun,
   5 Aug 2026, https://doi.org/10.1038/s41467-026-76365-y).
   Runners-up: **Labenbacher et al. (Graz), JMIR 1 May 2026** — 9 GenAI tools, none reliably flags retracted
   literature, best 8/15 (https://doi.org/10.2196/88766) → a cheap structural rule (cited DOI ∈ Retraction Watch →
   HOLD); **COMPL-AI** (https://arxiv.org/abs/2410.07959); **TGA Feb 2026** AI-SaMD guidance
   (https://www.tga.gov.au/node/514668).

**3 countries with the strongest direct work (ranking changed in the depth pass):** Brazil (BRI eLife 2026 + CNPq
2664/2026), Australia (repliCATS/MetaMelb, PNAS co-authors, TGA, Diraq under DARPA V&V), **Austria** (ÖAWI 2026
no-AI-in-judgment rule, FWF policy, ISTA runtime verification, Graz/Salzburg measurement papers, Bilateral AI, TIER2).
Belgium moves to fourth (PNAS co-authors, BE-RN without tooling, KU Leuven GenAI guidance updated 3 Sep 2026, FNRS
open-science narrative "not a criterion", FARI). Argentina stays in the NOTHING-FOUND (direct) group but gains a
direct-adjacent item (UTDT/CONICET collective estimation) and a CONICET AI commission scoped to management. No country
in this wave has a deterministic, fail-closed claim gate with sealed blind metrics or a proof ledger.

**NOTHING FOUND (Direct) — 25 of 28 countries:** Afghanistan, Albania, Algeria, Andorra, Angola, Antigua and Barbuda,
Argentina, Armenia, Austria, Azerbaijan, Bahamas, Bahrain, Bangladesh, Barbados, Belarus, Belgium, Belize, Benin,
Bhutan, Bolivia, Bosnia and Herzegovina, Botswana, Brunei, Burkina Faso, Burundi (Austria/Belgium/Argentina have
adjacent work but no direct item). **Entirely empty (no adjacent item either):** Afghanistan, Andorra, Belarus, Benin.
Countries with a direct-adjacent item: Australia, Brazil, Bulgaria, (Belgium via PNAS).
