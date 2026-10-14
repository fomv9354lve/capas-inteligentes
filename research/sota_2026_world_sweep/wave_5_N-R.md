# World sweep 2026 — Wave 5 (N–R): Namibia → Rwanda

Date: 2026-10-14 · Agent: wave-5 (two passes: initial + resume) · Brief: `BRIEF.md` (followed verbatim).

**Coverage caveat (honest):** this session's shared WebSearch budget (200 calls across all wave agents) ran out after
this wave's 36th search, mid-batch. Netherlands, Norway, New Zealand, Nigeria, Pakistan, Poland, Portugal and Russia
received real searches in pass 1. **Resume pass (same day):** exactly one more WebSearch ran (Peru) before the budget
was exhausted again. The harness's budget notice explicitly forbids working around the limit by querying search
engines through other tools, so the suggested "Bing results page via WebFetch" route was **not** used. Everything
added in the resume pass comes from direct WebFetch of primary sites (~70 fetches: concytec/gob.pe press and law
coverage, dost.gov.ph, up.edu.ph, nrcp.dost.gov.ph, uefiscdi.gov.ro ×5, open-science.ro, rewire-hub.eu, cnatdcu.ro,
ideas-ncbr.pl, pan.pl, gov.pl/ncbr, pllum.org.pl ×2, nask.pl, inesctec.pt ×2, inesc-id.pt, fct.pt ×2, ptrn.pt,
ciencia-aberta.pt, dissernet.org, antiplagiat.ru, rscf.ru, ispras.ru, airi.net, arxiv.org (Fanar), fanar.qa,
huggingface.co (Fanar 2.0), hbku.edu.qa ×2, qrdi.org.qa, mon.gov.mk, manu.edu.mk, mohe.pna.ps ×2, pngnri.org,
upng.ac.pg, palaugov.pw, unan.edu.ni, nhrc.gov.np, nast.gov.np, naurugov.nr, uam.ne, conicyt.gob.ni, ...).
Entries carry one of four status words: **searched**, **fetch-only** (primary site read, no web search),
**UNREACHABLE** (every primary fetch failed — DNS/TLS/418/504 — so nothing was read; this is not NOTHING FOUND), or
**NOTHING FOUND** (something was actually read and nothing relevant to CAPAS was in it). Nothing below is from
memory alone; every tool/paper claim has a URL that was returned by a tool.

**Pass 3 (2026-10-14, WebSearch budget restored):** live searches for the four UNREACHABLE countries (Nauru 1, Nepal 1,
Niger 1, North Korea 1) and for Peru 2, Philippines 2, Romania 2, plus 12 primary fetches (one PDF via pdftotext).
Additions are marked "pass 3". Not re-run: the rest of the wave.

---

### Namibia
- Direct (2026 SOTA): none found.
- Adjacent: NCRST (National Commission on Research, Science and Technology) homepage read directly: mission text only,
  no research-integrity, open-science, reproducibility or AI-policy content; the only outlets are the Acts page and the
  *Namibian Journal for Research, Science and Technology* (https://njrst.ncrst.na/index.php/njrst). Site last
  updated 2021–2022.
- Epistemics / gap framing: not visible.
- Institutions & people: NCRST https://ncrst.na/ (fetch-only).
- Take / Ahead: take: nothing | ahead: everything (no verification layer exists at agency level).
- Confidence: low | Queries: fetch-only (ncrst.na). **NOTHING FOUND** on the primary site; no web search possible.

### Nauru (pass 3: searched, 1 query)
- Direct (2026 SOTA): none. Nauru has no national research council; the government portal was the only candidate.
- Adjacent: run 2 fetches failed (https://naurugov.nr/ TLS altname error; https://nauru.gov.nr/ empty). Pass 3 query
  ("Nauru research OR science policy OR university 2026 department of education research ethics") returned **no
  Nauru-specific item**; the only regional hook is WHO/SPC/Pacific Academy of Sciences "Strengthening Research Ethics
  Governance in the Pacific Island Countries" (Nadi, 1–3 May 2025; 24 representatives from 13 PICs; participant list not on
  the landing page, so Nauru's attendance is unverified) — https://www.who.int/publications/i/item/RS-2025-GE-10-FIJI (read).
- Epistemics / gap framing: not visible.
- Institutions & people: none identified.
- Take / Ahead: take: nothing | ahead: n/a.
- Confidence: low | Queries: 1 (pass 3) + 2 failed fetches (run 2) + who.int. **NOTHING FOUND (searched)** — was UNREACHABLE.

### Nepal (pass 3: searched, 1 query)
- Direct (2026 SOTA): none found.
- Adjacent: NHRC https://nhrc.gov.np/ and NAST https://nast.gov.np/ were unreachable in run 2 (header/TLS errors). Pass 3
  query surfaced the **NHRC eLibrary**: National Ethical Guidelines for Health Research (2022 edition; ERB Guideline 2019
  PDF https://elibrary.nhrc.gov.np/bitstream/20.500.14356/2484/1/ERB_Guideline_2019.pdf); an NHRC RCR presentation
  "Responsible Conduct of Research in Nepal: Identifying and Addressing the Gaps" (Namita Ghimire, 18 Jul 2023,
  https://elibrary.nhrc.gov.np/bitstream/20.500.14356/2272/1/Ms.%20Namita%20Ghimire_RCR_18%20July%202023.pdf) and a
  title-only item "Emerging Avenue of Artificial Intelligence and Ethical Considerations" (Bishesh Khanal, Jul 2023);
  a 2025 commentary "Challenges in Healthcare Research in Nepal: What is the way forward?" (Sah et al., *Nepal J.
  Epidemiology*) that asks NHRC to lead on research integrity — https://www.nepjol.info/index.php/NJE/article/view/75978
  (PMC copy behind a bot wall; snippets only). No AI-in-research guideline, reproducibility or statistics-check item.
- Epistemics / gap framing: human-subjects ethics (ERB) is the integrity frame; nothing at claim level.
- Institutions & people: NHRC (ERB); NAST (site only).
- Take / Ahead: take: nothing | ahead: all mechanical.
- Confidence: low-medium (snippets) | Queries: 1 (pass 3) + 4 failed fetches (run 2). **Adjacent-only (searched)** — was
  UNREACHABLE.

### Netherlands (rich — searched, 13 queries + 8 primary fetches)
- Direct (2026 SOTA):
  - **metacheck** (formerly *papercheck*) — automated pre-publication checks of manuscripts, built at TU/e + VU
    Amsterdam + Glasgow; beta launched 5 June 2026 by Cristian Mesquida at the *AI in Peer Review* conference, TU/e;
    manual published 3 Oct 2026 by Daniël Lakens. 26+ modules: StatCheck, exact/non-significant p-values, effect sizes,
    power analysis, preregistration check + **RegCheck (paper-vs-preregistration comparison)**, ethics/funding/COI
    statements, open practices, repository/code/data/codebook/Psych-DS checks, reproducibility check, reference
    accuracy, cross-refs to Retraction Watch / PubPeer / FLoRA replication DB. Stance: regex/rules first, "optional LLM
    queries" opt-in and declared, limited to classifying existing text; "assist, not replace, human expertise";
    "will never support automated quality assessments, rankings, or scoring". AGPL-3. Funded by NWO TDCC-SSH
    (#ICT.001.TDCC.018), PI Rene Bekkers (VU). https://www.scienceverse.org/metacheck/ ·
    https://github.com/scienceverse/metacheck · https://www.scienceverse.org/metacheck_book/ ·
    https://rogue-scholar.org/records/rjbs2-kky48 (July 2026). Confidence high. **Closest thing in this wave to CAPAS.**
  - **ReproHub** (Tilburg, Hannes Datta; Open Science NL infrastructure award, 16 Dec 2025): four reproducibility tools
    incl. *ReproBuddy* (AI tool for reproducibility packages) and **ReproRun (validation system for results)**.
    https://www.openscience.nl/en/news/45-projects-strengthen-dutch-open-science-infrastructure (medium; project page
    not yet public).
  - **statcheck** v1.6.1.9000 (dev build 26 Jan 2026; release 1.6.0 Feb 2025), Michèle Nuijten, Tilburg — the
    deterministic recompute-p-from-test-statistic ancestor of CAPAS's structured checks.
    https://michelenuijten.r-universe.dev/statcheck/DESCRIPTION · https://statcheck.io. 2024 AMPPS paper: statcheck in
    peer review cut reporting errors (https://mbnuijten.com/publications/). No 2025–26 paper found.
- Adjacent: **Open Science NL** work programme 2026–27 approved 14 Nov 2025, 13 instruments incl. AI, replication,
  infrastructure (https://tagteam.harvard.edu/hub_feeds/4669/feed_items/17027636); €35.5 M infrastructure round, 45
  projects, 16 Dec 2025 — also *OpenML Next* and *Project Hippocampus* (TU/e, Joaquin Vanschoren: full experiment
  tracking so AI results can be verified), *FAIR for AI / Djehuty* (TU Delft), *PRIOR* (Amsterdam UMC: preregistration
  platform for animal studies); 27 replication grants Jan 2026 (https://www.rug.nl/research/openscience/news/26-funding-awarded-for-open-science).
  Lakens: Full Professor of Metascience, TU/e, 1 Dec 2025; 2026 papers "Rethinking Type S and Type M errors" (AMPPS,
  June 2026), "There is only one correct analysis" (preprint, June 2026), "How to analyze a replication study"
  (April 2026) (https://www.researchgate.net/scientific-contributions/Daniel-Lakens-29111742, medium); co-editor of
  Springer collection *Severity and Learning from Error* (deadline 15 Dec 2026,
  https://link.springer.com/collections/ebjdhfadcd). Netherlands Reproducibility Network (NWO €250k, 2023). LOWI
  annual reports only through 2024 (https://lowi.nl/en/about-lowi/); no 2025 paper-mill/AI statement found.
- Epistemics / gap framing: explicitly severity-based (Mayo/Lakens): preregistration is valued because it lets others
  judge *how severely* a claim was tested (https://www.tandfonline.com/doi/full/10.1080/2833373X.2024.2376046). The
  metacheck team refuses verdicts/scores by design — a human-in-the-loop, advisory stance, the opposite of CAPAS's
  fail-closed single verdict.
- Institutions & people: Tilburg Meta-Research Center (Wicherts, Nuijten, van Aert, van Lissa, Haven)
  https://metaresearch.nl/; TU/e Human-Technology Interaction (Lakens, Mesquida); VU Amsterdam (Bekkers); Glasgow
  (DeBruine); Open Science NL https://www.openscience.nl/en; LOWI; TNO (Dutch AI Factory, Groningen, supercomputer
  2028 — no verification programme found).
- Take / Ahead: take: metacheck's RegCheck (paper-vs-prereg diff) and Retraction-Watch/PubPeer reference cross-checks
  as additional structure-checkable rules; its explicit "LLM opt-in, declared, classification-only" disclosure
  wording | ahead: CAPAS issues a sealed, hash-re-derivable verdict and measures its own blind rate; metacheck is
  advisory, unscored, no sealed evaluation, no instrument-file ingestion, no proof ledger.
- Confidence: high (metacheck, statcheck, Open Science NL); medium (Lakens 2026 papers via ResearchGate) | Queries:
  "Netherlands metascience 2026 reproducibility verification"; "Open Science NL 2026 programme"; "statcheck Nuijten
  Tilburg 2025 2026"; "Eindhoven TU/e Amsterdam UvA AI verification scientific claims"; "LOWI paper mills image
  forensics"; "registered reports Peer Community In Wicherts"; "TNO CWI verification trustworthy AI"; "Lean
  autoformalization Nijmegen Eindhoven"; "Daniël Lakens Eindhoven 2026 severe testing"; "Open Science NL 45 projects AI
  tools"; "Michèle Nuijten 2025 2026 statcheck"; "LOWI annual report 2025"; "UvA VU 2026 AI scientist verification".

### New Zealand (searched, 3 queries + 3 fetches)
- Direct (2026 SOTA): **SciTrue — Evidence-Grounded Claim Verification in Science**, Neşet Özkan Tan, Minghao Li,
  Mark Gahegan, Dept. of Computer Science, University of Auckland; EACL 2026 System Demonstrations, pp. 397–406
  (Rabat, 24–29 Mar 2026). Agentic LLM pipeline (claim refined → papers retrieved → evidence extracted → summary
  decomposed into sub-claims) with per-component source attribution; human eval of 300 attributions beats
  GPT-4o-search-preview and Perplexity Sonar Pro. Verdict labels: Supported / Partially supported / Overstated /
  Contradicted / Not addressed / Citation not found. The verdict is model-produced (LLM in the loop); no sealed
  evaluation, no determinism claim. https://aclanthology.org/2026.eacl-demo.27 · https://scitrue.ai/. Confidence high
  (affiliations read from the PDF).
- Adjacent: Medsafe **Verification Pathway** for new medicines — rules adopted 20 May 2026, in force 3 July 2026
  (Medicines Amendment Act 2025, ss 22A–22F): approval if ≥2 recognised regulators (FDA, TGA, HC, MHRA, EMA-centralised,
  HSA, Swissmedic) authorised within 4 years; evidence = two full assessment reports + primary CTD; **no independent
  statistical re-analysis** — NZ relies on overseas verdicts. Part 2 guidelines pending.
  https://www.medsafe.govt.nz/consultations/verification-pathway-rules-outcome.pdf ·
  https://www.raps.org/resource/asia-pacific-roundup-new-zealand-adopts-verification-pathway-rules-following-industry-consultation.html.
  Royal Society Te Apārangi *Guidelines for the best-practice use of generative AI in research* (themes: Te Tiriti,
  Indigenous data sovereignty, research integrity) cited in UoA ResBaz 2026 material
  (https://resbaz.auckland.ac.nz/assets/resbaz-2026/responsible-ai.pdf). 2023 Megataxa editorial (Auckland) calling
  for preregistration in taxonomy (https://www.mapress.com/mt/article/view/megataxa.10.1.2).
- Epistemics / gap framing: regulatory "verification" means trust-transfer from other regulators, not re-derivation;
  research framing adds Indigenous data sovereignty as an integrity axis.
- Institutions & people: UoA CS (Gahegan, Tan); Medsafe; Royal Society Te Apārangi.
- Take / Ahead: take: SciTrue's six-label vocabulary (esp. *Overstated* and *Citation not found*) as REWRITE/HOLD
  sub-reasons; Medsafe pathway as a concrete "reliance" evidence spec | ahead: no model in CAPAS's verdict; sealed blind
  rates; CAPAS does not read prose but SciTrue cannot be hash-re-derived.
- Confidence: high | Queries: "New Zealand reproducibility metascience research integrity 2026 preregistration";
  "Royal Society Te Apārangi research integrity AI policy 2026 Auckland Otago"; "Medsafe Pharmac evidence standards
  statistical submission AI verification 2026".

### Nicaragua (fetch-only)
- Direct (2026 SOTA): none found.
- Adjacent: CONICYT https://www.conicyt.gob.ni/ → ECONNRESET. UNAN-Managua https://www.unan.edu.ni/ read (first
  200k chars of a 305k-char page): Hackathon Nicaragua 2026 win, Rally Latinoamericano de Innovación 2026, degree
  study plans; no integridad científica, ética de la investigación, ciencia abierta, reproducibilidad or AI-policy text.
- Epistemics / gap framing: innovation-contest framing only.
- Institutions & people: CONICYT (site down); UNAN-Managua.
- Take / Ahead: take: nothing | ahead: everything.
- Confidence: low | Queries: fetch-only (conicyt.gob.ni failed; unan.edu.ni read ×2). **NOTHING FOUND.**

### Niger (pass 3: searched, 1 query)
- Direct (2026 SOTA): none found.
- Adjacent: Université Abdou Moumouni https://www.uam.ne/ → DNS not found (run 2). Pass 3 query ("Niger recherche
  scientifique éthique intelligence artificielle université Abdou Moumouni 2025 2026") returned only infrastructure news
  (UAM modernisation works, ~50,000 students, Feb 2025 — https://www.afrique-sur7.fr/niger-modernisation-de-luniversite-abdou-moumouni ,
  snippet), a 2006 IRD/CODESRIA history of research at UAM, and off-target Nigeria/Algeria items. No ethics, AI or
  integrity policy.
- Epistemics / gap framing: not visible.
- Institutions & people: UAM (site unreachable).
- Take / Ahead: take: nothing | ahead: n/a.
- Confidence: low | Queries: 1 (pass 3) + 1 DNS failure (run 2). **NOTHING FOUND (searched)** — was UNREACHABLE.

### Nigeria (searched, 3 queries)
- Direct (2026 SOTA): none found.
- Adjacent: predatory-publishing burden — >1/3 of Nigerian education papers 2010–2018 in predatory outlets, highest in
  SSA (https://www.researchprofessionalnews.com/?p=236845); 2025 Global-South perspective piece citing a 2022 survey
  where >30% of early-career Nigerian researchers unknowingly published in predatory journals
  (https://tsp.scione.com/cms/fulltext.php?id=140); Nigerian Academy of Science calls for quality-over-quantity
  appraisal. **African Reproducibility Network (AREN)** + Center for Open Science partnership (Sept 2025;
  https://www.cos.io/blog/cos-and-african-reproducibility-network-partner-to-advance-open-scholarship-practices-in-local-contexts);
  NgREN/WACREN open-science pilot workshop at NUC Abuja, 28–29 Apr 2026 (https://ngren.edu.ng/view.php?id=23).
  TETFund 2026 cycle: AI/robotics centres, 3,000+ scholars trained in AI (https://tetfund.gov.ng/news/details/75);
  calls for a statutory national AI policy in higher education (2025 AI Awareness Day,
  https://nounnews.nou.edu.ng/index.php/node/1688). No NUC journal-quality or AI-detection rule found.
- Epistemics / gap framing: integrity debate framed around venue legitimacy (predatory journals) and incentives, not
  claim-level verification.
- Institutions & people: NUC, TETFund, Nigerian Academy of Science, NgREN, AREN (continental).
- Take / Ahead: take: nothing technical; AREN/COS is a distribution channel for a low-cost gate | ahead: all of it.
- Confidence: medium | Queries: "Nigeria research integrity paper mills predatory journals 2026"; "TETFund NUC
  national journal policy 2026 AI detection"; "African Reproducibility Network Nigeria 2025 2026".

### North Korea (pass 3: searched, 1 query)
- Direct (2026 SOTA): none found.
- Adjacent (outside analysis only; 38north.org fetches returned 403, so snippets): 38 North, "North Korea's Artificial
  Intelligence Research: Trends and Potential Civilian and Military Applications" (Jan 2024,
  https://www.38north.org/2024/01/north-koreas-artificial-intelligence-research-trends-and-potential-civilian-and-military-applications/)
  and "North Korea's International Network for AI Research" (Aug 2024,
  https://www.38north.org/2024/08/north-koreas-international-network-for-artificial-intelligence-research/): an AI
  Research Institute, legal/institutional reform and AI education, co-authorship with researchers in China, the US and
  South Korea, ML applied to wargaming/surveillance; Korea JoongAng Daily: AI output "among the lowest in the world",
  domestic journals (e.g. *Journal of Kim Il Sung University*) not indexed —
  https://www.koreajoongangdaily.com/korea/despite-ban-north-koreas-global-ai-collaborations-grow/11730519 ; Jul 2026 state
  media: Kim Jong Un declares AI a "top priority" for weapons/drones (secondary). No research-integrity, verification or
  reproducibility item exists or is observable.
- Epistemics / gap framing: not observable from outside.
- Institutions & people: State Academy of Sciences; Kim Il Sung University; AI Research Institute (per 38 North).
- Take / Ahead: take: nothing | ahead: n/a.
- Confidence: low (snippets of secondary analyses) | Queries: 1 (pass 3); 38north ×2 (403). **NOTHING FOUND for CAPAS
  (searched)** — was UNREACHABLE.

### North Macedonia (fetch-only)
- Direct (2026 SOTA): none found.
- Adjacent: MANU (Academy) https://manu.edu.mk/ is a placeholder ("currently being updated"). Ministry of Education
  and Science https://mon.gov.mk/: 8 Oct 2026 press release on teachers completing AI training
  (https://mon.gov.mk/mk-MK/odnosi-so-javnost/soopstenija/dodeleni-priznanija-na-nastavnici-za-zavrsena-obuka-za-vestacka-inteligencija);
  an AI guide for teachers/students (PDF on portal.mdt.gov.mk); "AI in the classroom" call (https://next.edu.mk/ai-at-schools/);
  and a quick link to a **national plagiarism portal** http://plagijati.mon.gov.mk/ (connection refused on fetch —
  existence confirmed from the ministry page, contents unverified). No integrity, reproducibility or open-science item.
- Epistemics / gap framing: AI framed as classroom literacy; integrity = plagiarism portal (text-level).
- Institutions & people: MON (Minister Janevska); MANU.
- Take / Ahead: take: nothing | ahead: everything.
- Confidence: low | Queries: fetch-only (manu.edu.mk, mon.gov.mk read; plagijati.mon.gov.mk refused). **NOTHING FOUND**
  relevant to claim verification.

### Norway (searched, 4 queries + 2 fetches)
- Direct (2026 SOTA): none found. (The arXiv 2608.23644 "Ethical LLM-Assisted Research" framework — O/V/R/M/E
  constructs, "epistemic audit" record of delegation/verification/provenance — surfaced in the Norway query but lists
  no affiliation; not attributable to Norway. https://arxiv.org/abs/2608.23644, 24 Aug 2026.)
- Adjacent: **NORRN** (Norwegian Reproducibility Network): pre-registration course, stakeholder group incl. Foundation
  Dam (which *requires* preregistration in funding applications) — last substantive update Nov 2024
  (https://norrn.substack.com/p/norrn-november-update). Research Council open-science policy since 2020; from 2023
  referees score open-science practice (preprints, transparency/reproducibility) in Researcher/Collaborative projects
  (https://www.forskningsradet.no/en/research-policy-strategy/open-science/policy/); joined Open Research Europe,
  April 2026 relaunch Sept 2026. Forskningsetikk.no: *Forum for Research Ethics 2026* (17 Sept 2026, "how can
  institutions develop systems to safeguard trust in research?"), unofficial English translation of the Research
  Ethics Act (https://www.forskningsetikk.no/en/). Cristin retired 2025 → Sikt's NVA. RINO 2018 baseline: FFP 0.2–0.3%,
  QRPs ~40% (https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8692305/). No automated-check or AI-verification work found.
- Epistemics / gap framing: "as open as possible, as closed as necessary"; integrity handled through law
  (Research Ethics Act) and committees, not tooling.
- Institutions & people: NORRN; Research Council of Norway; Sikt; Forskningsetiske komiteene / Granskingsutvalget;
  Foundation Dam (Hans Christian Lillehagen).
- Take / Ahead: take: funder-side preregistration requirement (Dam) as a market signal for prereg-aware gating | ahead:
  no deterministic verifier, no sealed evaluation anywhere in the Norwegian stack found.
- Confidence: medium | Queries: "Norway metascience reproducibility 2026 automated checks"; "SimulaMet NTNU UiO
  AI-generated scientific claims verification 2026"; "Research Council Norway pre-registration NORRN"; "Sikt NTNU
  registered reports Bergen metascience"; "Oslo image manipulation Forskningsetiske komiteene 2025 2026 AI".

### Oman
- Direct/Adjacent: MoHERI homepage (fetch-only): Open Data portal, research platforms (orp.trc.gov.om, omren.om,
  masader.om); no integrity, ethics, reproducibility or AI-policy text (https://www.moheri.gov.om/).
- Confidence: low | Queries: fetch-only. **NOTHING FOUND** on primary site; web search not possible.

### Pakistan (searched, 3 queries)
- Direct (2026 SOTA): none found.
- Adjacent: **HEC draft GenAI policy** (metadata-dated 22 Aug 2025; press Aug 2026): disclosure of AI use; fabricated
  references, invented data and "AI-generated false results" classed as serious misconduct; students cannot be
  penalised solely on an AI-detector report; universities must create AI committees and report annually
  (https://propakistani.pk/2026/08/04/hec-shares-plan-to-stop-students-from-using-ai/ ·
  https://letsdatascience.com/news/pakistan-hec-drafts-university-generative-ai-rules-4c58e8fb). Journals enforce
  HEC-style thresholds: similarity ≤19%, single source ≤5%, **AI-content score ≤19%**
  (https://jrh.pu.edu.pk/index.php/Journal/plagiarism-policy). Open-science awareness: COMSATS dissertation (Sheikh,
  defended 19 Sept 2025, 12 universities) — preregistration and open data lag; awareness is the gap
  (https://edoc.hu-berlin.de/18452/35660). DRAP: 2024 Clinical Research Guidelines 2nd ed. (ICH-GCP aligned), 2025
  revision open for comment to 5 June 2025, GCP-inspection guideline 3rd ed. May 2025 — no statistical-review annex
  found (https://www.dra.gov.pk/?p=70731).
- Epistemics / gap framing: integrity = plagiarism/AI-similarity percentages (detector-score thresholds), i.e. a
  fail-open text heuristic, exactly the GIGO surface CAPAS declines to use.
- Institutions & people: HEC; DRAP; COMSATS (Arslan Sheikh).
- Take / Ahead: take: HEC's "no penalty on a detector score alone" is a useful *anti*-pattern statement for the
  honest-limits page | ahead: structured evidence fields vs similarity percentages.
- Confidence: medium | Queries: "Pakistan research integrity HEC plagiarism AI-generated papers 2026"; "Pakistan
  reproducibility open science preregistration LUMS NUST"; "DRAP clinical trial evidence statistical review 2025 2026".

### Palau (fetch-only)
- Direct (2026 SOTA): none found.
- Adjacent: https://www.palaugov.pw/ read: no research, science-policy, research-ethics or AI-policy items; only EQPB
  environmental permit applications and statistical publications.
- Epistemics / gap framing: not visible.
- Institutions & people: none identified.
- Take / Ahead: take: nothing | ahead: n/a.
- Confidence: low | Queries: fetch-only (palaugov.pw read). **NOTHING FOUND.**

### Palestine (fetch-only)
- Direct (2026 SOTA): none found.
- Adjacent: Ministry of Higher Education and Scientific Research https://www.mohe.pna.ps/ read; its **Scientific
  Research Council** (est. 1998 under Higher Education Law 11/1998; presidential decree 28 Feb 2013; reconstituted by
  Council of Ministers Decision 5/2019) lists "instilling the culture and ethics of research" as a general objective —
  no code, policy or procedure on integrity, reproducibility or open science
  (https://www.mohe.pna.ps/Councils-and-Commissions/Scientific-Research-Council). Research portal https://researchgate.ps/.
  One news item on a Beirut regional conference on AI in higher education (https://www.mohe.pna.ps/news?p=articles&news=9433).
  https://www.hec.ps/ → DNS not found; Birzeit https://www.birzeit.edu/en → 403.
- Epistemics / gap framing: mandate-level ethics language only.
- Institutions & people: MoHESR Scientific Research Council; DG of Development & Scientific Research.
- Take / Ahead: take: nothing | ahead: everything.
- Confidence: low | Queries: fetch-only (mohe.pna.ps ×2 read; hec.ps, birzeit.edu failed). **NOTHING FOUND** relevant.

### Panama
- Adjacent: SENACYT homepage (fetch-only): PENCYT 2025–2029 plan link, UNESCO AI-capacity diagnostic publication,
  open-data dataset; no integrity/reproducibility/evidence-standard content (https://www.senacyt.gob.pa/).
- Confidence: low | Queries: fetch-only. **NOTHING FOUND** on primary site; web search not possible.

### Papua New Guinea (fetch-only)
- Direct (2026 SOTA): none found.
- Adjacent: **PNG National Research Institute** media release 3 Jun 2026, "The misuse of AI poses a significant threat
  and it must be addressed" (Spotlight Vol. 19 Issue 5, author Kebet Liven, Assistant Librarian; released by Director
  Osborne Sanida): AI-generated content (deepfakes, fabricated images/text) threatens "the integrity of information";
  misinformation "often eluding detection and verification by users"; PNG lacks AI-specific legislation; calls for AI
  regulatory frameworks, digital literacy, platform accountability
  (https://pngnri.org/images/Press-Releases/Misuse_of_artificial_intelligence_Final.pdf — text read via pdftotext;
  https://pngnri.org/images/Publications/Spotlight_Vol_19_Issue_5-Addressing_the_rise_of_AI-generated_content_and_its_impact_on_human_creativity_trust_and_information_integrity_in_Papua_New_Guinea.pdf).
  Spotlight 19(3), 7 Apr 2026: AI adoption after AI Summit 2026. UPNG research page: no ethics/integrity content
  (https://www.upng.ac.pg/research). pngsciencetech.gov.pg → DNS not found.
- Epistemics / gap framing: information-integrity = deepfake/misinformation regulation; nothing on research claims.
- Institutions & people: PNG NRI (Osborne Sanida, Kebet Liven); UPNG Research Office.
- Take / Ahead: take: nothing technical | ahead: everything.
- Confidence: medium (primary PDF read) | Queries: fetch-only (pngnri.org ×2, upng.ac.pg ×2 read; pngsciencetech failed).

### Paraguay
- Adjacent: CONACYT homepage (fetch-only, Oct 2026 items): internal-control (MECIP) workshop 8 Oct 2026; ONA
  accreditation "gestión de imparcialidad" and proficiency-testing policy (metrology admissibility, not research
  claims); institutional repository 2024; open-data portal https://datos.conacyt.gov.py/ (https://www.conacyt.gov.py/).
- Confidence: low | Queries: fetch-only. **NOTHING FOUND** relevant; web search not possible.

### Peru (searched: 1 query + 9 fetches; 2 further queries blocked by budget)
- Direct (2026 SOTA): none found. The one planned item is a **plan, not a system**: on 22 Jul 2024 Concytec president
  Sixto Sánchez told the Congress science commission that Concytec would "crear una unidad de integridad científica",
  "automatizar los procesos de calificación de RENACYT" and "implementar un sistema de Inteligencia Artificial para
  prevenir y detectar el fraude científico" (https://proactivo.com.pe/concytec-planteara-la-creacion-del-fondo-nacional-de-ciencia-innovacion-y-tecnologia/).
  No specification, evaluation or launch of that AI system was found; at the 8 Sep 2025 commission session Concytec
  announced a Dirección de Integridad Científica and a complaints register, and legislators asked for figures on
  researchers sanctioned/removed from RENACYT — none were given (https://comunicaciones.congreso.gob.pe/?p=422144).
- Adjacent: **DS 062-2024-PCM (23 Jun 2024)**, regulation of Ley 31250 (SINACTI): sanctions regime + a public
  *Registro de Sanciones*; buying/selling authorship = very serious infraction → permanent expulsion from SINACTI
  and/or fine up to 320 UIT (~S/ 1.65 M) (https://gestion.pe/peru/concytec-investigadores-que-compren-autorias-seran-expulsados-y-multados-por-el-sinacti-noticia/).
  Origin: Nov–Dec 2023 authorship-for-sale scandal — Concytec met 53 universities (29 Nov 2023), notified Elsevier of 8
  journals with fraud signs, opened RENACYT-exclusion procedures to be published on its site, drafted new RENACYT and
  sanctions regulations (https://elperuano.pe/noticia/229132-concytec-53-universidades-del-pais-se-comprometen-con-la-integridad-cientifica;
  https://proactivo.com.pe/concytec-y-los-institutos-publicos-de-investigacion-se-reunen-para-fortalecer-la-integridad-cientifica-en-el-pais/, 14 Dec 2023).
  2026 essay: Garcia Tarazona, Lopez Malqui & Mañaccasa Vásquez, *Rev. Iberoamericana de Innovación Científica JA
  TUAIDA* 3(1):77–95, 30 Jan 2026 — authorship must be "respaldada con evidencias de trazabilidad", journals need
  internal/external audits, data/methods opened "a la replicabilidad y reproducibilidad"; "el fraude científico en el
  sistema RENACYT plantea una tensión insalvable" (https://doi.org/10.59722/riic.v3i1.1112, PDF read). Concytec Nota
  Técnica 003-2026-DIE, bibliometrics 2018–2024 (https://repositorio.concytec.gob.pe/, 2026). gob.pe/concytec → 418
  bot block; portal.concytec.gob.pe → empty.
- Pass 3 (2 searches, 2 fetches): **Código Nacional de Integridad Científica**, Resolución N° 028-2024-CONCYTEC-P (cited
  by a URP journal article; resolution text not fetched —
  https://revistas.urp.edu.pe/index.php/RFMH/article/download/6501/11684?inline=1 , snippet). **CONCYTEC Dirección de
  Evaluación y Gestión del Conocimiento, "Integridad Científica para el SINACTI" — Módulo III** slide deck (created 4 Dec
  2025; 17 pp; PDF read): §7 "Estrategias para prevenir y detectar el uso de la IA en la investigación" restates ICMJE
  (Apr 2025), COPE (2023) and WAME (2023): disclose tool and version, "la secuencia de comandos completa utilizada para
  generar los resultados de la investigación, la hora y la fecha de la consulta"; "Los editores requieren herramientas
  adecuadas para evaluar los contenidos, detectar contenidos generados o alterados por IA" — **no tool named, no
  reproducibility or statistics content** — https://lms.concytec.gob.pe/mod/resource/view.php?id=37 . **Reglamento of
  Ley 31814 (DS 115-2025-PCM, El Peruano 9 Sep 2025)**: high-risk systems in health, education, justice, finance and
  access to basic services need human supervision; algorithmic-transparency mechanisms, security audits, privacy by
  design; PCM/Secretaría de Gobierno y Transformación Digital as authority; CNIDIA experimentation environment open to
  research centres; **no provision on verification of research or AI-generated claims** —
  https://andina.pe/agencia/noticia-gobierno-aprobo-reglamento-ley-promueve-uso-inteligencia-artificial-1044279.aspx
  (read). A CELE report (Jun 2026) flags "ambigüedades conceptuales y vacíos regulatorios" (snippet). The promised
  "AI to detect scientific fraud" still has no public trace.
- Epistemics / gap framing: integrity = authorship fraud and incentive gaming in a researcher registry; remedy = law,
  sanctions register and a promised AI fraud detector (fail-open text/behaviour heuristic, unevaluated). No
  preregistration, replication or statistics-check policy visible.
- Institutions & people: Concytec (Sixto Sánchez, president; predecessor Benjamín Marticorena); RENACYT; Congress
  Comisión de Ciencia (Carlos Zeballos, Ernesto Bustamante).
- Take / Ahead: take: the public sanctions/exclusion register as an institutional proof-ledger analogue; the
  traceability-of-authorship demand maps onto CAPAS provenance (read/declared/derived) | ahead: Concytec's "AI to
  detect fraud" is exactly the claim CAPAS measured and declined (no separation on 888 clean vs 6,348 retracted);
  CAPAS publishes blind rates, Peru publishes none.
- Confidence: medium (press + primary law coverage + journal PDF) | Queries: "Peru CONCYTEC integridad científica
  reproducibilidad 2026" (ran); "Concytec unidad de integridad científica inteligencia artificial detección fraude
  RENACYT 2026" and "Peru Red Peruana de Reproducibilidad preregistro ciencia abierta metaciencia" (blocked); fetches above.
  Pass 3: "Perú CONCYTEC integridad científica IA reproducibilidad 2026 lineamientos"; "Perú ley IA reglamento 2025 2026
  Ley 31814 investigación científica"; fetches lms.concytec.gob.pe PDF (pdftotext), andina.pe.

### Philippines (fetch-only, 10 fetches; 2 queries blocked by budget)
- Direct (2026 SOTA): none found.
- Adjacent: DOST, 9 Oct 2026: Philippines hosted the 2nd meeting of the **ASEAN Working Committee on AI for Health
  S&T** (28–29 Sep 2026, Manila/Laguna; Priority Economic Deliverable 14 of the 2026 ASEAN chairship; aligned to the
  ASEAN Responsible AI Roadmap 2025–2030 and APASTI 2026–2035); outputs = a "Validated Landscape Assessment" of AI
  readiness, draft regional action plan and policy recommendations for COSTI Q4 2026; Sec. Renato Solidum Jr.: AI
  "harnessed ethically and inclusively"; **no tool-validation, verification or evidence standard**
  (https://www.dost.gov.ph/knowledge-resources/news/4542-philippines-hosts-asean-regional-meetings-on-ai-for-health-s-t.html).
  **UP Principles for Responsible AI** (15 principles; R&D set: Meaningful Human Control, Transparency — "individuals
  should be informed if AI-enabled tools are used", Fairness, Safety; AIAC to draft an AI code of conduct; no adoption
  date on page) (https://up.edu.ph/up-principles-for-responsible-artificial-intelligence/). NRCP homepage: no
  integrity/ethics items (https://nrcp.dost.gov.ph/). Unreachable: PCHRD (TLS), PHREB ethics.healthresearch.ph
  (TLS, https and http), PHRR registry (TLS), CHED (403), Philippine Journal of Science (403), healthresearch.ph (TLS).
- Pass 3 (2 searches, 3 fetches): **House "Artificial Intelligence Development and Regulation Act"** substitute bill —
  26 House bills + 3 resolutions + 1 privilege speech consolidated by the TWG under Rep. Javier Miguel Benitez;
  registration and safety checks only for high-risk systems (loans, jobs, health); "funds computing access for Filipino
  researchers"; amendments open to 20 Jul 2026, not yet committee-approved —
  https://www.philstar.com/opinion/2026/07/14/2542095/proposed-ai-bill-gains-momentum-congress (read); Senate **AIRA /
  SBN-25** (introduced 2 Jul 2025; National AI Commission to certify and monitor risks; under deliberation —
  https://digitalpolicyalert.org/event/32489-artificial-intelligence-regulation-act-s-25-including-authorisation-of-goods-or-services-was-introduced-in-senate ,
  snippet). **DOST-PCHRD × PAMJE forum on the EQUATOR Network's AI reporting extensions** (Solidum: updated guidelines so
  methods and findings are reported clearly) — https://www.pchrd.dost.gov.ph/news_and_updates/dost-pchrd-pamje-updates-health-researchers-editors-on-equator-network-ai-reporting-guidance/
  (TLS error on fetch; snippet, date garbled on the index). **Central Philippine University webinar for DOST scholars,
  2 May 2026** (Ananias Sabijon Jr.; read): "verification-first mindset", AI-Assisted Research Disclosure Templates
  "aligned with UNESCO's 2026 guidance", DOI checks and a "can't find rule", a manuscript that passed peer review with
  ~80% non-existent references — https://cpu.edu.ph/the-centralian-link/prof-dr-sabijon-speaks-to-dost-scholars-on-ethical-use-of-ai-in-research/ .
  UP Manila ORI (Jean Anne Toral) reproducibility/QRP session, S&T Week 2024 (snippet). No DOST/PCHRD AI-integrity
  circular, no statistics-check or reproducibility infrastructure.
- Epistemics / gap framing: governance/readiness and "meaningful human control" framing; nothing at claim level; the
  pedagogy ("verify every citation") is the closest Philippine articulation of fail-closed.
- Institutions & people: DOST (Solidum), DOST-PCHRD (Jaime Montoya), NRCP, PHREB, CHED, UP AI Advisory Committee, UP
  Manila ORI (Toral), House ICT Committee TWG (Benitez), CPU (Sabijon).
- Take / Ahead: take: nothing technical; the ASEAN AI-for-health action plan is a venue where a regulated-submission
  gate could be proposed | ahead: all of it.
- Confidence: low-medium (two primary pages read; health-research sites unreachable) | Queries: "Philippines DOST
  PCHRD research integrity reproducibility preregistration 2026" and "Philippines CHED AI-generated research misconduct
  policy 2026 universities" (both blocked); fetches above. Pass 3: "Philippines DOST research integrity AI guidelines 2026
  PCHRD reproducibility"; "Philippines AI regulation bill 2026 Senate … CHED research universities"; fetches philstar,
  cpu.edu.ph, pchrd.dost.gov.ph (TLS).

### Poland (searched, 2 queries + 2 fetches)
- Direct (2026 SOTA): none found. IDEAS NCBR (the national AI research institute) **merged into Akces NCBR on
  12 Dec 2025 and ceased operations**; "there is currently no Scientific Council" (https://ideas-ncbr.pl/en/).
- Adjacent: NCN open-science policy — DMPs since 2019 (expert-reviewed); **OA mandate dropped 26 June 2025 (Order
  39/2025)**, now recommended only; data sharing still required; no AI policy, no replication instrument
  (https://www.ncn.gov.pl/en/finansowanie-nauki/otwarta-nauka). NCN caps proposals per PI (18 Sept 2026). No Polish
  Reproducibility Network found; Path2Integrity notes the ECoC was only adopted in 2020 and no RI-training certificate
  is required (https://www.path2integrity.eu/news/5336_path2integrity-supports-its-polish-partners-in-the-mission-to-raise-awareness-towards-research-integrity-and-ethics/);
  PAN Institute of Law Studies' Centre for Research on Reliability in Science (2018, https://inp.pan.pl/?p=41719).
- Deepening (resume pass, fetch-only): IDEAS NCBR's research page (Oct 2026) lists only five PRELUDIUM-23 projects
  (continual learning ×2, online algorithms, test-time adaptation, LLM-driven robot design) — **no formal verification,
  theorem proving or reproducibility group**; "other research groups: (none)" (https://ideas-ncbr.pl/en/research/).
  PAN homepage: a proposal for a new research evaluation/funding system that "abandons the emphasis on producing a
  bulk of academic output"; no integrity or AI statement (https://pan.pl/en/); PAN ethics-committee page DNS-failed.
  NCBR English site is an archive (last items 2020); gov.pl/ncbr lists Akces NCBR (https://akces-ncbr.pl/ refused
  connection). RDN (degree council) TLS-failed. **PLLuM** (NASK; Ministry of Digital Affairs grant HIVE 2 no.
  4/WII/DBI/2026, 5.999 M PLN; models expanded 21 May 2026): open code "umożliwia pełny audyt", RAG grounding, a 2024
  post warning the model "zmyśli coś"; **no accuracy or hallucination figures** (https://pllum.org.pl/). **PoVisLE**
  (NASK NLP dept., 18 Sep 2026): Polish vision-language benchmark, 1,117 images / 2,366 hand-written QA pairs, 16 VLMs
  run with no randomness; a multiple-choice item counts as correct **only if the model picks the right option under
  every shuffle of the options** — a permutation-invariance admissibility rule; open-answer judging method unstated
  (https://pllum.org.pl/blog/posts/povisle). **PSNC** (Poznań, IChB PAN) is the Polish partner in Horizon Europe
  **REWIRE** (reproducibility management plans, GNU Guix rebuildable environments, RO-Crate packages; 2026–2029)
  (https://uefiscdi.gov.ro/rewire-project; https://rewire-hub.eu/). NASK homepage: no AI-safety/evaluation items.
- Epistemics / gap framing: policy moving *away* from hard mandates (OA relaxed), integrity framed legally/ethically;
  the national LLM programme discloses audit-ability, not measured error.
- Institutions & people: NCN; Akces NCBR (ex-IDEAS); PAN; NASK (PLLuM, PoVisLE); PSNC.
- Take / Ahead: take: PoVisLE's "correct under every option ordering" rule as a structure-checkable admissibility
  criterion for benchmark claims; PSNC/REWIRE Guix+RO-Crate artefacts as ingestible reproducibility evidence | ahead:
  no deterministic verifier, no sealed evaluation, no published blind rates anywhere in the Polish stack found.
- Confidence: medium | Queries: "Poland metascience reproducibility 2026 Polish Reproducibility Network"; "Poland AI
  verification scientific claims Warsaw IDEAS NCBR 2026 deterministic verifier"; fetches ncn.gov.pl, ideas-ncbr.pl ×2,
  pan.pl, instytucja.pan.pl (DNS fail), gov.pl/web/ncbr, archiwum.ncbr.gov.pl, akces-ncbr.pl (refused), rdn.gov.pl
  (TLS), nask.pl, pllum.org.pl ×2, rewire-hub.eu.

### Portugal (searched, 2 queries + 1 PDF)
- Direct (2026 SOTA): none found (Portuguese-*language* fact-checking work found is Brazilian — Goiás, FEVER 2025,
  https://preview.aclanthology.org/display_plenaries/2025.fever-1.3.pdf — not Portugal).
- Adjacent: **Portuguese Reproducibility Network (PTRN)**, www.ptrn.pt — founded ~2021 by Alessandra S. Souza (FPCE,
  U. Porto), Susana Magalhães (i3S, U. Porto), Pedro Príncipe (U. Minho); aim: local reproducibility nuclei + national
  network (Forum GDI 2021 abstract,
  https://forumgdi.rcaap.pt/wp-content/uploads/2021/10/08_20210928_8ForumGDI_Proposta_flashtalks_SouzaMagalhaesPrincipe.pdf).
  No INESC/INESC TEC claim-verification work surfaced.
- Deepening (resume pass, fetch-only): **PTRN is alive but thin** — https://www.ptrn.pt/en/ read: founded 15 Jun
  2021, peer-led, coordinates with UKRN, SWISSRN, DERN; 2026 activity = a PTRN listserv (Sep 2026) and the 2nd edition
  of "Systematic Reviews and Meta-Analysis in R", U. Coimbra, 19–23 Oct 2026; no members list, no tools, and much of
  the site is template filler (lorem-ipsum testimonials). **FCT**: open-science = OA-to-publications policy; a UNESCO
  AI-ethics MOOC listed for H2 2026; reporting channels page (updated 15 Nov 2024) covers Law 93/2021 whistleblowing and
  harassment — **no research-integrity office, code or procedure named** (https://www.fct.pt/en/;
  https://www.fct.pt/en/sobre/politicas-de-transparencia/canais-de-denuncias/). ciencia-aberta.pt is stale (last items
  2018; the national open-science policy still "being prepared"). INESC TEC news Sep–Oct 2026 (2 pages): privacy-in-AI
  network (João Vilela, 12 Oct 2026), a best paper on AI vs traditional DB methods — nothing on verification,
  fact-checking or reproducibility (https://www.inesctec.pt/en/news). INESC-ID: ADRF 2026 forum 13 Oct 2026, nothing on
  verification (https://www.inesc-id.pt/).
- Epistemics / gap framing: "the greatest cause of irreproducibility is scientist behaviour" (PTRN) — behavioural,
  training-and-community framing; integrity handled as generic whistleblowing law.
- Institutions & people: PTRN (Souza, Magalhães, Príncipe); FCT; INESC TEC; INESC-ID.
- Take / Ahead: take: nothing technical | ahead: all of it.
- Confidence: medium (primary sites read) | Queries: "Portugal reproducibility network metascience 2026"; "Portugal
  INESC Lisbon Porto AI scientific claim verification 2026"; fetches ptrn.pt ×3, fct.pt ×2, ciencia-aberta.pt,
  inesctec.pt ×2, inesc-id.pt.

### Qatar (fetch-only, 4 primary fetches)
- Direct (2026 SOTA): none found on primary pages.
- Adjacent: QCRI (HBKU) — **Fanar 2.0** Arabic sovereign GenAI platform released 12 Feb 2026 with "advanced reasoning";
  announcement gives **no benchmark, evaluation or verification statement**
  (https://www.hbku.edu.qa/en/news/hbku-releases-enhanced-flagship-generative-ai-platform). QCRI groups: Arabic
  Language Technologies (Farasa, TweetMogaz), Cyber Security, QCAI (https://www.hbku.edu.qa/en/qcri/). QCRI's earlier
  fact-checking line (Tanbih) is not on the current pages; not verifiable here. HBKU–Boeing "safe AI" convening
  9 Feb 2026; MLDAS 2026 symposium 8–9 Feb.
- Deepening (resume pass, fetch-only): **Fanar technical report** arXiv:2501.13944 (18 Jan 2025; "Fanar Team", 41
  authors incl. Firoj Alam, Kareem Darwish, Ahmed Ali; QCRI/HBKU, sponsored by Qatar MCIT): Fanar Star 7B (from
  scratch) + Fanar Prime 9B (from Gemma-2), orchestrator, Islamic RAG, Recency RAG, and an **"attribution service that
  can be used to verify the authenticity of fact based generated content"**; abstract claims "best in the class on
  well established benchmarks" with no numbers in the abstract (https://arxiv.org/abs/2501.13944). **Fanar 2.0**:
  arXiv:2603.16397 "Fanar 2.0: Arabic Generative AI Stack" (17 Mar 2026); HF collection QCRI/fanar-20
  (Fanar-2-27B-Instruct, Oryx-IVU 8B, Oryx-IG, Diwan; updated 25 Mar 2026; no evaluation text on the collection page)
  (https://huggingface.co/collections/QCRI/fanar-20). fanar.qa: "backed by reliable sources via RAG", Fanar-Sadiq
  retrieval model "verifies" Islamic answers; **no benchmark, hallucination or error-rate data on the site**
  (https://fanar.qa/). MLDAS 2026 (8–9 Feb 2026, CMU-Q; QCRI + Boeing): Elmagarmid — "performance alone no longer
  measures AI progress", "strong focus on safety and reliability"; no V&V, certification or evaluation-standard content
  (https://www.hbku.edu.qa/en/news/hbku-and-boeing-advance-safe-and-sustainable-ai). QRDI Council (ex-QNRF,
  https://qrdi.org.qa/): 12 Nov 2025 "Qatar's AI future" item; no integrity, open-science or evidence-standard
  content. Tanbih (tanbih.qcri.org) certificate expired on https and http — the fact-checking line is unverifiable
  here; QCRI publications page 404.
- Epistemics / gap framing: sovereignty and capability framing; the single verification artefact (attribution
  service) is model-side and publicly unevaluated; "reliability" is asserted, not measured.
- Institutions & people: QCRI (Ahmed Elmagarmid; Fanar team: Firoj Alam, Kareem Darwish, Ahmed Ali); HBKU; QRDI Council.
- Take / Ahead: take: Fanar's attribution-service framing (attribution ≠ verdict) as the thing CAPAS's
  read/declared/derived provenance split makes explicit | ahead: Fanar ships with no public eval; CAPAS ships blind
  rates and keeps the model out of the verdict.
- Confidence: medium (arXiv + primary HBKU/fanar pages) | Queries: web search blocked; fetched qcri.org (→ hbku),
  hbku.edu.qa/qcri ×2, qcai, ALT pages, hbku Boeing news, fanar.qa, arxiv 2501.13944, huggingface QCRI/fanar-20,
  qnrf.org (→ qrdi.org.qa), tanbih.qcri.org ×2 (cert expired).

### Romania (fetch-only, 9 fetches; 2 queries blocked by budget)
- Direct (2026 SOTA): none found.
- Adjacent: **REWIRE** — "Reproducibility Enablement for Widespread Implementation, Reuse and Evidence in the ERA",
  Horizon Europe GA 101287431, €1.9 M, 1 Sep 2026 – 31 Aug 2029, coordinator Athena RC (Greece), 12 partners incl.
  OpenAIRE, Manchester, Inria, CNRS/Episciences, Masaryk, PSNC (PL), Latvian Council of Science, LifeWatch ERIC,
  ELIXIR-CZ, UEFISCDI (RO); interventions: **Reproducibility Management Plans** (planning), **GNU Guix rebuildable
  computational environments** (execution), **RO-Crate FAIR publication packages** (publishing); 8 pilots + 1
  mini-pilot; UEFISCDI pilots "Policy Implementation" with the Latvian funder — co-creates and tests an RMP template
  with two volunteer organisations (STEM + SSH) and drafts funder policy proposals; kick-off Athens 17–18 Sep 2026;
  contacts Alina Irimia, Ioana Trif (https://uefiscdi.gov.ro/rewire-project;
  https://uefiscdi.gov.ro/news-rewire-un-nou-proiect-european-pentru-integrarea-reproductibilitatii-in-practica-de-cercetare;
  https://rewire-hub.eu/ — "validated workflows" with no stated validation method). **ARION** (Horizon Europe, same
  dates, OpenAIRE coordinator): responsible research assessment; UEFISCDI co-creates the narrative-CV intervention
  (https://uefiscdi.gov.ro/arion-project). **RO-NOSCI** (EOSC national coalition, launched 2021 by UEFISCDI + ICI
  Bucharest, co-coordinated by IFIN-HH; assemblies to Dec 2023): no reproducibility/integrity activity
  (https://uefiscdi.gov.ro/ro-nosci). Open Science Knowledge Hub / White Book 2023–2030: integrity appears only as an
  EU pillar, no commitment described (https://www.open-science.ro/). UEFISCDI open-science feed Jul–Oct 2026: EOSC
  Federation operational (Oct 2026), Science Europe webinar on assessment reform 22 Oct 2026, EC consultation on AI &
  copyright (https://uefiscdi.gov.ro/noutati-open-science). CNATDCU (doctoral-thesis plagiarism body): since Law
  199/2023 UEFISCDI no longer handles plagiarism complaints; no 2025–26 decisions visible, no anti-plagiarism or AI
  software named (https://www.cnatdcu.ro/). research.gov.ro → TLS failure.
- Pass 3 (2 searches, 2 fetches): **CNECSDTI** (national consultative body under the Research Authority / Ministry of
  Education and Research) will co-organise the **ENRIO Congress 2027** with the University of Bucharest (CARFIA), Bucharest
  7–9 Sep 2027; track record ">300 cases, >50 decisions" in 20 years; CARFIA lists a "Raportul de similitudine" service —
  https://carfia.unibuc.ro/enrio-congress-2027/ (read). **CEE AI Index 2026** (AI Chamber / The Recursive / European Cloud;
  Forbes.ro 8 Jun 2026, read): Romania 7th of 11 (Estonia, Slovenia, Lithuania lead); 5.21% of firms use advanced AI;
  national AI strategy 2024–2027; EuroHPC AI Factory status; HRIA hub €64 M 2025–29; **recommends a regulatory sandbox
  (none exists)** — https://www.forbes.ro/?p=505314 . Romanian AI Committee + Scientific and Ethics Council for AI under
  the Ministry of Research (2023; agerpres snippet); UMFST Târgu Mureș law-faculty student AI guide (7 Jul 2026, snippet).
  **No 2026 rule on AI disclosure or verification in research publications, no CNATDCU AI-check rule.**
- Epistemics / gap framing: reproducibility is arriving as a *planning artefact* (RMP) via EU project policy, not as
  verification; integrity remains legal/plagiarism-level (ENRIO-style case handling).
- Institutions & people: UEFISCDI (Alina Irimia, Ioana Trif); CNATDCU; ICI Bucharest; IFIN-HH.
- Take / Ahead: take: the RMP template + RO-Crate package + Guix environment hash as a declared-artefact schema that
  CAPAS's reproducibility fields can ingest (machine-context ingestion, not typed numbers) | ahead: REWIRE's
  "validated" workflows have no stated validation; CAPAS has sealed blind rates and a hash-re-derivable verdict.
- Confidence: medium (primary UEFISCDI/REWIRE pages) | Queries: "Romania UEFISCDI CNECSDTI integritate cercetare
  reproducibilitate 2026 AI" and "Romania Babeș-Bolyai Bucharest metascience reproducibility network registered
  reports 2025 2026" (both blocked); fetches cnatdcu.ro ×2, uefiscdi.gov.ro ×5, open-science.ro, rewire-hub.eu,
  research.gov.ro (TLS). Pass 3: "Romania CNECSDTI OR UEFISCDI research integrity AI 2026 reproducibility"; "România lege
  inteligență artificială 2026 cercetare științifică verificare integritate academică"; fetches carfia.unibuc.ro,
  forbes.ro.

### Russia (searched, 1 query + 3 fetches)
- Direct (2026 SOTA): none found (second query on HSE/MIPT/Sber/Yandex verification blocked by budget).
- Adjacent: **Dissernet** — live in 2026: 18 Apr 2026 "fake ZoLUS" notice + new medical collection; 29 Jan 2026 medical
  falsification archive; 30 Dec 2025 year review "100:44 in favour of science"; Tatarstan stripped 7 degrees Dec 2025.
  Counters: 14,054 dissertations with improper borrowings, 6,482 translated-plagiarism articles, 2,388 degree-revocation
  applications, 1,801 degrees revoked, 1,527 articles withdrawn, journals that "published tables with substituted data"
  tracked; method = Rostovtsev's "dissertorubka" semi-automatic text/link analysis, explicitly not Antiplagiat
  (https://www.dissernet.org/). Rostovtsev July 2025 overview: 80% success on >2,000 revocation applications
  (https://cisrus.org/2025/07/04/corruption — 404 on fetch; from search snippet, medium). Paper-mill genesis traced to
  2011–12 evaluation rules rewarding indexed publications (https://arxiv.org/pdf/2112.13322). RAS anti-falsification
  commission site (kpfran.ru) is dead (hosting error page).
- Deepening (resume pass, fetch-only): Dissernet re-read 14 Oct 2026 — additional counters: 2,970 defences of its
  position at dissertation councils/VAK, 1,465 journals removed from the violators list after fixing violations, 1,059
  organisations with violations; **no item on AI-generated dissertations** (https://www.dissernet.org/).
  **Antiplagiat** (https://www.antiplagiat.ru/, the national similarity vendor): AI-generation detector with a
  marketing claim that "accuracy reaches 99%" and **no published method or evaluation**; since 25 Sep 2026 reports
  state **which AI-detector model checked the text** (a model-provenance disclosure line); 9 Oct 2026 analysis of
  universities' local AI-use regulations; image-uniqueness check, translated-borrowing and duplicate detection; free
  partial checks since Apr 2026; **no fabricated-data or statistics checks**. RSF (https://rscf.ru/en/): no
  integrity/reproducibility/AI items in 2026 news. ISP RAS homepage: "verification and software testing technologies",
  Linux Verification Center — software formal methods, nothing on scientific claims (https://www.ispras.ru/en/;
  research page TLS-failed). AIRI (airi.net) → 504/TLS; Yandex Research → 404; RAS anti-falsification commission
  (kpfran.ru) dead. The HSE/MIPT/Sber AI-for-science verification query stayed blocked.
- Epistemics / gap framing: integrity as adversarial civil-society audit against state degree-granting (Dissernet)
  plus vendor AI-text percentages (Antiplagiat) — text-level, fail-open heuristics; a 99% detector claim with no
  evaluation is precisely the kind of number CAPAS would HOLD.
- Institutions & people: Dissernet (Andrei Rostovtsev, IITP RAS); Antiplagiat; RAS Commission (status unclear); VAK;
  ISP RAS (software verification); RSF.
- Take / Ahead: take: Dissernet's public per-case ledger with counters is a proof-ledger analogue at institutional
  scale; "tables with substituted data" is a structure-checkable signal CAPAS could encode; Antiplagiat's "which model
  checked this" report line is a minimal model-provenance disclosure worth matching in certificates | ahead: CAPAS
  checks numeric/evidence consistency, not borrowed or AI-flavoured text, and publishes blind rates instead of a 99%.
- Confidence: medium | Queries: "Russia Dissernet research integrity paper mills 2025 2026 RAS metascience";
  (blocked) "Russia AI science verification Sber Yandex HSE MIPT 2026"; fetches dissernet.org ×2, antiplagiat.ru,
  rscf.ru, ispras.ru ×2, airi.net ×2 (failed), research.yandex.com ×2 (404), kpfran.ru (dead).

### Rwanda (fetch-only)
- Adjacent: NCST site (https://www.ncst.gov.rw/): reviewer-registration call 9 Oct 2026, funding calls June–Aug 2026,
  Research & Innovation Repository; no integrity, reproducibility, ethics-guideline or AI-policy content.
- Confidence: low | Queries: fetch-only. **NOTHING FOUND** on primary site; web search not possible.

---

## Wave summary

**Top 5 findings for CAPAS**
1. **metacheck (NL, TU/e + VU + Glasgow; beta 5 Jun 2026, manual 3 Oct 2026)** — the nearest thing to CAPAS found in
   this wave: 26+ rule-first manuscript checks (StatCheck, RegCheck paper-vs-prereg, p-value/effect-size/power
   reporting, Retraction Watch/PubPeer/replication-DB cross-refs), LLM opt-in and declared, and an explicit refusal
   to score or rank. https://www.scienceverse.org/metacheck/ · https://www.scienceverse.org/metacheck_book/ ·
   https://github.com/scienceverse/metacheck. Position: CAPAS = fail-closed *verdict* with sealed blind rates;
   metacheck = advisory *report*. Complementary, and the RegCheck + reference cross-check modules are importable rules.
2. **Open Science NL €35.5 M infrastructure round (16 Dec 2025)** funds ReproHub/**ReproRun** (Tilburg, result
   validation), OpenML Next + Project Hippocampus (TU/e, full experiment tracking "so AI-driven results can be
   verified"), FAIR-for-AI/Djehuty (Delft), PRIOR (animal-study preregistration). A funded national stack converging on
   machine-readable verification context — the kind of ingestion CAPAS already does from instrument files.
   https://www.openscience.nl/en/news/45-projects-strengthen-dutch-open-science-infrastructure
3. **SciTrue (NZ, U. Auckland, EACL 2026 demo)** — LLM-agentic scientific claim verifier with per-component attribution
   and a six-label verdict set (Supported / Partially / Overstated / Contradicted / Not addressed / Citation not found),
   human-evaluated on 300 attributions. Model in the verdict, no sealed eval: the clean foil for CAPAS's "no model in
   the verdict". https://aclanthology.org/2026.eacl-demo.27 · https://scitrue.ai/
4. **NZ Medsafe Verification Pathway (in force 3 Jul 2026)** — a regulator defining "verification" as reliance on two
   overseas authorisations plus full assessment reports and CTD, with no statistical re-analysis. A concrete,
   dated evidence spec for the pharma beachhead and a clear statement of what regulators *don't* re-derive.
   https://www.medsafe.govt.nz/consultations/verification-pathway-rules-outcome.pdf
5. **Dissernet (Russia) public ledger, active through Apr 2026** — 14,054 dissertations, 6,482 articles, 1,801 degrees
   revoked, journals flagged for "tables with substituted data"; a civil-society proof ledger at national scale, and a
   structure-level signal (substituted tables) worth encoding. https://www.dissernet.org/
   Honourable mention: Lakens (TU/e, full professor of metascience from 1 Dec 2025) co-editing *Severity and Learning
   from Error* (Springer, 2026) — the severity vocabulary CAPAS's "measured blind rate" speaks natively.
   https://link.springer.com/collections/ebjdhfadcd

   Resume-pass additions worth a line each: **REWIRE (Horizon Europe 2026–29; UEFISCDI/Romania + PSNC/Poland)** —
   Reproducibility Management Plans + GNU Guix rebuildable environments + RO-Crate packages = a machine-actionable
   reproducibility artefact set CAPAS could ingest as declared evidence (https://uefiscdi.gov.ro/rewire-project,
   https://rewire-hub.eu/); **Peru's DS 062-2024-PCM sanctions register and the still-unbuilt "AI to detect scientific
   fraud"** promised to Congress in July 2024 — the fraud-detector claim CAPAS measured and declined
   (https://proactivo.com.pe/concytec-planteara-la-creacion-del-fondo-nacional-de-ciencia-innovacion-y-tecnologia/);
   **PoVisLE (NASK, Poland, 18 Sep 2026)** — a multiple-choice item counts only if correct under every option
   ordering, a permutation-invariance admissibility rule (https://pllum.org.pl/blog/posts/povisle); **Antiplagiat
   (Russia)** — a "99% accurate" AI-text detector with no published evaluation, but reports since 25 Sep 2026 name the
   detector model that ran (https://www.antiplagiat.ru/); **Fanar (Qatar)** — an "attribution service to verify the
   authenticity of fact based generated content", model-side and publicly unevaluated (https://arxiv.org/abs/2501.13944).

**3 countries with the strongest direct work:** Netherlands (metacheck, statcheck, ReproRun, Open Science NL);
New Zealand (SciTrue + Medsafe verification pathway); Russia (Dissernet ledger + Antiplagiat — adjacent-direct,
text-level). Runner-up on adjacent infrastructure: Romania/Poland via REWIRE.

**Coverage after the resume pass:** every country N–R now has an entry in the template. Status counts:
- **NOTHING FOUND (something was read, nothing relevant to CAPAS):** Namibia, Oman, Panama, Paraguay, Rwanda,
  Nicaragua, Palau, Palestine, North Macedonia, **+ pass 3 (searched): Nauru, Niger, North Korea** — **12**.
- **UNREACHABLE: 0** (pass 3 ran one live search each for Nauru, Nepal, Niger and North Korea; Nepal moved to
  adjacent-only, the other three to NOTHING FOUND).
- **Adjacent-only, nothing direct:** Nepal, Nigeria, Norway, Pakistan, Papua New Guinea, Peru, Philippines, Poland,
  Portugal, Qatar, Romania. Pass 3 added for Peru the CONCYTEC "Integridad Científica" module (ICMJE/COPE/WAME restated,
  no tool) and DS 115-2025-PCM; for the Philippines the House AI bill TWG (Jul 2026) and the CPU "verification-first"
  pedagogy; for Romania CNECSDTI/ENRIO 2027 and the CEE AI Index 2026. **Ranking unchanged.**
- **Direct work found:** Netherlands, New Zealand; Russia (text-level).
- Web searches that ran in this wave: 47 (36 in pass 1, 1 in the resume pass, 10 in pass 3); 8 were blocked in pass 2.
  No search-engine workaround was used.
