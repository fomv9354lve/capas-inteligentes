# World sweep 2026 — Wave 3 (Fiji → Italy)

Date run: 2026-10-14. Agent: wave-3 sweep agent (Claude). Brief: `BRIEF.md` (same folder).

## Coverage note (read first)
The session-wide WebSearch budget (200 calls shared by all agents) was exhausted after my 31st query, in the
middle of the Hungary/Iceland/India batch. Per the tool's instruction I did not wait for the refill and did not
route searches through curl/proxies. I used WebFetch on known primary URLs to verify what I could. Three honest
labels are used below and must not be conflated:

- **NOTHING FOUND (queries: …)** — searches ran, nothing relevant surfaced.
- **NOT SEARCHED — budget exhausted** — zero or near-zero queries ran; any content is prior knowledge, marked
  "unverified this wave" and carries only URLs I am confident exist. These entries need a re-run.
- Normal entries — searched (count in Queries), with URLs from results or fetched pages.

Depth achieved vs. brief: Germany 8 searches + 4 fetches (target met); France 6 searches + 4 fetches (met);
Finland 4 + 1 fetch (met, thin results); Greece 2 (below target); India 1 + 1 fetch (far below); Israel, Italy,
Ireland, Hungary 0 searches (Italy 1 fetch). Small states Fiji, Gabon, Gambia, Georgia, Ghana, Grenada,
Guatemala, Guinea: 1–2 searches each (met).

**Re-run (same day, later session):** the 13 "NOT SEARCHED" entries were completed. WebSearch was retried once and
was still exhausted; its notice forbids working around the limit through other search channels, so the re-run used
**WebFetch on primary sources and their own catalogs only** (arXiv search pages, Retraction Watch site search, Europe
PMC REST API, institutional sites). Those entries carry "0 searches + N fetches" and a fourth label applies to them:
- **fetched-only** — discovery limited to known sites; absence means "not on the sites fetched", not "does not exist".
Depth achieved on re-run: India 13 fetches, Israel 11, Italy 11, Hungary 8, Ireland 8, Indonesia 4, Honduras 3,
Iceland 3, Iran 2, Iraq 2, Guyana 2, Haiti 2, Guinea-Bissau 1. The "NOT SEARCHED — budget exhausted" label no longer
applies to any country.

---

### Fiji
- Direct (2026 SOTA): NOTHING FOUND (queries: "Fiji research integrity reproducibility verification AI science
  2025"; "University of the South Pacific research misconduct policy data integrity 2024 2025"). Second query
  returned only same-named institutions elsewhere (Pacific University, Oregon; St George's London).
- Adjacent: none Fiji-specific. Regional context only: NSTDA (Thailand) proposed international standards for
  citation validation at the RIL 2025 Kyoto summit —
  https://www.nstda.or.th/en/news/news-years-2025/nstda-joins-ril-2025-in-kyoto,-highlighting-confidence-in-science-in-the-ai-era.html
- Epistemics / gap framing: no national framing located.
- Institutions & people: University of the South Pacific (usp.ac.fj) — no integrity/reproducibility material
  surfaced in results.
- Take / Ahead: take: nothing | ahead: everything in the brief.
- Confidence: high that nothing surfaced; low that nothing exists (USP domain not crawled). | Queries: 2

### Finland
- Direct (2026 SOTA): NOTHING FOUND for deterministic/fail-closed claim gating, LLM-judge-vs-verifier, or
  autoformalization from Finnish institutions (queries listed below). The FCAI event "Searching for structure in
  unfalsifiable claims" (Aalto) is the only Finnish item touching claim epistemics —
  https://www.aalto.fi/en/events/searching-for-structure-in-unfalsifiable-claims (date not shown; low relevance).
- Adjacent: **Finnish Reproducibility Network (FIRN)**, founded summer 2021, peer-led, all disciplines —
  https://finnish-rn.org (fetched; no 2025–26 events listed on the landing page) and the 2023 JRN paper
  (Voikar et al., DOI 10.36850/jrn.2023.e47) https://jrn.trialanderror.org/pub/finnish-reproducibility-network.
  FIRN is an affiliate of the German RN (https://reproducibilitynetwork.de) and listed in UKRN's global
  directory (https://www.ukrn.org/global-networks/), but was NOT among the 15 RNs at the July 2025 Metascience
  meeting (https://www.ukrn.org/2025/07/09/in-person-meeting-of-national-reproducibility-network-representatives).
  Quantum: VTT hosts a 53-qubit IQM system; 150-qubit due end-2026, 300-qubit 2027; VTT builds in-house
  "benchmarking and characterization protocols" (job posting,
  https://academicpositions.com/ad/vtt/2026/research-scientist-quantum-algorithms-and-software/252809?locale=en);
  IQM's 20-qubit benchmark white paper https://arxiv.org/pdf/2408.12433 (2024, vendor). No published Finnish
  calibration-admissibility standard found.
- Epistemics / gap framing: bottom-up, institution-pedagogy framing (FIRN); no fail-closed/admissibility language.
- Institutions & people: FIRN (contact@finnish-rn.org; Vootele Voikar, Univ. Helsinki); FCAI (Aalto/Helsinki/VTT);
  VTT quantum; TENK (national integrity board — not surfaced in results).
- Take / Ahead: take: FIRN's national-node model for distribution of a hygiene tool | ahead: CAPAS has a
  machine-checkable calibration-snapshot admissibility rule; VTT/IQM publish fidelity numbers with no admissibility gate.
- Confidence: medium (thin results; FIRN page fetched) | Queries: 4 + 1 fetch

### France
- Direct (2026 SOTA): no fail-closed scientific-claim gate found. Closest: **Inria "Leaning and Rocq'ing"**
  (Renaissance Philanthropy-funded; Baudart, Cohen, Tabareau, Lelarge) — LLM translation of statements/proofs
  between Lean ↔ Rocq and Lean 3 → 4, toward a unified formal library; page says nothing about faithfulness
  checking of autoformalized statements — https://www.renaissancephilanthropy.org/leaning-and-rocqing (fetched).
  Related: an ICML 2026 Rocq case study "Library Before Proof" https://icml.cc/virtual/2026/74804 (affiliation
  not confirmed as French). The faithfulness gap ("kernel certifies proof ⊢ statement, never statement ⊨ intent")
  is the exact seam CAPAS's declared-scope field addresses.
- Adjacent: **Problematic Paper Screener** (Cabanac/Labbé/Magazinov, IRIT Toulouse; est. 2021-02-27; last
  update 2026-09-21; detectors: Tortured, SCIgen, Mathgen, Citejacked, Annulled, Feet of Clay, Seek&Blastn,
  Problematic Cell Lines) — https://dbrech.irit.fr/pls/apex/f?p=9999 (fetched). Reported >14,000 flagged papers
  by 2026 and criticised for false positives (secondary: https://casrai.org/news/paper-mills-tortured-phrases-integrity-crisis-2026).
  **Réseau Français de la Recherche Reproductible** (~400 members, ≥30 disciplines; 2025 activity report;
  webinars 2026-04-03 "Replication Games", 2026-09-18, 2026-10-08; national Open Science Strategy 2026–2033
  published 2026-09-16) — https://www.recherche-reproductible.fr (fetched); origin seminar Institut Pasteur
  March 2023 https://www.ouvrirlascience.fr/working-towards-the-national-organisation-of-research-reproducibility/.
  **Guix + Software Heritage** reproducible computational environments (Courtès, Inria Bordeaux) —
  https://www.arxiv.org/pdf/2405.15516 (2024). **LNE LE.IA** AI-evaluation lab: repeatability/reproducibility
  protocols, voluntary AI-process certification aligned to AI Act/ISO 42001; no uncertainty statement for AI
  performance — https://www.lne.fr/en/offers/thematic/articial-intelligence (fetched); 2022 slides
  https://inrs.fr/dam/jcr:146a28b9-e011-4c1c-b593-2321ffdda045/6%20Delaborde.pdf.
  IRIT seminar March 2026 on LLM misuse in article production
  https://www.cemes.fr/en/external-seminar-misuse-of-llm-for-the-production-of-scientific-articles.
- Epistemics / gap framing: France frames the problem as (a) reproducible environments (Guix: bit-reproducible
  builds) and (b) post-hoc literature screening (PPS). Neither is a pre-publication admissibility gate; PPS is
  detection (what CAPAS explicitly is not). Open Science Strategy 2026–2033 is policy, not mechanism.
- Institutions & people: Inria (Baudart, Cohen, Tabareau, Lelarge, Courtès); IRIT Toulouse (Guillaume Cabanac,
  Cyril Labbé — Grenoble); Software Heritage (Roberto Di Cosmo, Morane Gruenpeter); LNE (LE.IA); Comité pour la
  science ouverte; GRICAD Grenoble (RRN host, FNSO-funded 2025
  https://gricad.univ-grenoble-alpes.fr/en/news/2024/2024-02-07/).
- Take / Ahead: take: Guix-style bit-reproducible environment hashes as a `reproducibility artifact` field; PPS
  "Citejacked/Annulled" reference checks as a cheap deterministic pre-gate on bibliographies | ahead: CAPAS gates
  before publication, fail-closed, no model in verdict; France's tools are post-hoc detectors or build systems.
- Confidence: high on PPS/RRN/Inria (fetched), medium on LNE | Queries: 6 + 4 fetches

### Gabon
- Direct (2026 SOTA): NOTHING FOUND (queries: "Gabon science research integrity reproducibility 2025").
- Adjacent: national STI strategy (SNRI) under validation (Gabonreview,
  https://www.gabonreview.com/sciences-technologie-et-innovation-vers-lelaboration-dune-politique-de-recherche-nationale/);
  AD Scientific Index 2026 counts 27 indexed Gabonese scientists
  (https://gabonmediatime.com/ads-index-gabon-9e-pays-africain-avec-le-moins-de-scientifiques-en-2026/). Regional
  review of integrity in sub-Saharan Africa (2022) https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10008683/.
- Epistemics / gap framing: none located.
- Institutions & people: CENAREST (not surfaced).
- Take / Ahead: take: nothing | ahead: all.
- Confidence: high nothing surfaced | Queries: 1

### Gambia
- Direct (2026 SOTA): NOTHING FOUND (queries: "Gambia research integrity reproducibility MRC Unit 2025").
- Adjacent: MRC Unit The Gambia at LSHTM — data management & sharing training (Bamako, 2025-04-30)
  https://www.lshtm.ac.uk/research/units/mrc-gambia/news/457566/strengthening-west-africas-research-infrastructure-through-data-management-and;
  Scientific Coordinating Committee reviews methodology https://www.mrc.gm/about-us/.
- Epistemics / gap framing: institutional governance language ("integrity, quality"), no mechanism.
- Institutions & people: MRCG at LSHTM.
- Take / Ahead: take: nothing | ahead: all.
- Confidence: high nothing surfaced | Queries: 1

### Georgia
- Direct (2026 SOTA): NOTHING FOUND for AI/verification.
- Adjacent: **Georgian Reproducibility Network (GeoRN)** kick-off 2025-06-18 at Tbilisi State Medical University,
  via the EU TIER2 project awards (with Ukraine, Serbia) —
  https://www.the-microbiologist.com/news/georgia-and-ukraine-launch-national-reproducibility-networks-with-support-from-the-tier2-project/6530.article
  (fetch returned empty body; listed in UKRN directory with reproducibility@tsmu.edu). **ETHICS** Erasmus+
  project (2023-02 → 2027-01; Ilia State Univ. coordinator; Shota Rustaveli NSF partner): integrity MOOC,
  integrity-officer training, national workshop Telavi 2025-06-23/24, final conference Batumi 2026-09-14/16 —
  https://rustaveli.org.ge/eng/ETHICS ; https://www.academicintegrity.eu/wp/ethics-project/.
- Epistemics / gap framing: capacity-building (ethics, integrity officers); no mechanism.
- Institutions & people: TSMU, Ilia State University, Shota Rustaveli National Science Foundation.
- Take / Ahead: take: nothing | ahead: all.
- Confidence: high | Queries: 1 + 1 fetch

### Germany
- Direct (2026 SOTA): NOTHING FOUND that is a deterministic/fail-closed gate for scientific claims. Formal
  verification: only an MPI-SWS (Saarbrücken) postdoc on LLM + Lean proof generation with TU Wien
  (https://researchersjob.com/postdoctoral-position-at-mpi-sws-in-collaboration-with-tu-wien-m-f-d-max-planck-institute-germany/)
  and an MPI-SWS Lean 2026 event https://dynamics.mpi-sws.org/lean-2026/. Mario Krenn (MPI Science of Light)
  appears only as a speaker on AI for discovery (https://gutenberg-workshops.uni-mainz.de/ai-for-scientific-discovery/).
  No Helmholtz/Tübingen/DFKI claim-checker surfaced.
- Adjacent: **Fraunhofer IAIS AI Assessment Catalog** (6 dimensions: fairness, autonomy & control, transparency,
  reliability, safety & security, data protection; free; aimed at auditors/certification) —
  https://www.iais.fraunhofer.de/en/publications/studies/2023/ai-assessment-catalog.html (the /research/… URL 404s);
  BSI/KI.NRW origin https://www.computer-automation.de/engineering-en/images/a-test-catalog-for-the-certification-of-ai-1.htm.
  Two independent applications (Autischer, Waxnegger, Kowald — affiliation not shown; likely Know-Center Graz, AT):
  PMLR v294 2025 "cumbersome and slow… structures the evaluation" https://proceedings.mlr.press/v294/autischer25a.html;
  arXiv 2601.08295 (2026-01-13) self-certification, "complements rather than replaces formal compliance"
  https://arxiv.org/abs/2601.08295. **PTB**: "AI and Metrology" competence centre (AI-Met) established 2025-01-17
  and flagship **AI.Cert** (AI-supported conformity assessment, starting with weighing instruments) — both
  surfaced via search snippets of ptb.de; **Digital Calibration Certificate (DCC)**: DCC Conference Feb 2026,
  DCC2Ind Jan 2026, "DCC-Launch 2027" with Boehringer Ingelheim adopting DCCs for ~150,000 calibrations/yr
  (https://www.ptb.de/news/dcc, via https://www.dmet.ptb.de/); D-SI metadata model extensions representing
  uncertainty distributions and dependencies (IMEKO TC6 2025, https://imeko.org/publications/tc6-2025/IMEKO-TC6-2025-003.pdf,
  https://imeko.org/publications/tc6-2025/IMEKO-TC6-2025-010.pdf). (Note: arXiv 2406.10117 "Trustworthy AI in
  metrology" is NPL/UK, not PTB.) **DFG** generative-AI statement (Sept 2023; disclosure of model/purpose/extent;
  permitted in proposals, not in reviews; page last modified 2026-03 with 2023 text) —
  https://www.dfg.de/en/service/press/press-releases/2023/press-release-no-39 ;
  https://wissenschaftliche-integritaet.de/en/use-generative-models/. **German Reproducibility Network** (founded
  2021-01; founding members incl. QUEST/BIH, Helmholtz, Helmholtz-AI, LMU OSC, ZBW, DGPs, BUA, NOSI) —
  https://reproducibilitynetwork.de (fetched); GRN's Maximilian Frank leads the Global Federation of RNs effort
  (UKRN 2025-07-09 post). **BIH QUEST**: Dirnagl retired 2025; steering board (Ulf Tölch spokesperson, Sarah
  McCann deputy; McCann presents EU project iRISE) https://quest-surveys.bihealth.org/article/home.html.
  EMA AI reflection paper (adopted CHMP/CVMP Sept 2024; NDSG AI workplan 2025–2028) governs German pharma
  submissions — https://www.ema.europa.eu/nl/about-us/how-we-work/data-regulation-big-data-other-sources/artificial-intelligence;
  BfArM-specific guidance not found.
- Epistemics / gap framing: Germany's strongest native move is **metrological**: DCC/D-SI make uncertainty a
  machine-readable, dated, signed object; AI.Cert pushes conformity assessment toward machine evidence. The AI
  side (Fraunhofer catalogue) is checklist/documentation, explicitly "not legal compliance". Research integrity
  (DFG) is disclosure-based, human-accountable, fail-open (no mechanism).
- Institutions & people: PTB (AI-Met, AI.Cert, DCC working groups); Fraunhofer IAIS (catalogue); DFG; GRN
  (Maximilian Frank); BIH QUEST (Tölch, McCann); MPI-SWS (Ouaknine); Helmholtz AI; Guillaume Cabanac's PPS has
  German co-use via the GAUSS Göttingen paper-mill webinar 2026-06-26 https://news.uni-goettingen.de/gauss-career/?p=3303.
- Take / Ahead: take: ingest **DCC/D-SI** as a calibration-snapshot source (signed XML with per-parameter
  uncertainty distributions and dates — a direct analog of CAPAS's Qiskit BackendProperties adapter, but for every
  physical instrument) and align the Atlas calibration-snapshot schema to D-SI | ahead: no German system returns
  a fail-closed verdict on a claim; Fraunhofer's catalogue is a questionnaire, AI.Cert is instrument conformity,
  DFG is disclosure. CAPAS's sealed-blind numbers and proof ledger have no counterpart here.
- Confidence: high on PTB/DCC, Fraunhofer, DFG, GRN (fetched or primary); medium on AI-Met/AI.Cert (snippets)
  | Queries: 8 + 4 fetches

### Ghana
- Direct (2026 SOTA): NOTHING FOUND.
- Adjacent: University of Ghana revised plagiarism/misconduct policy to cover AI (June 2026, policy not yet
  public; aggregator source — unconfirmed)
  https://ghanaremembers.com/stories/history/university-of-ghana-the-first-university-established-on-gold-coast-by-ordinance-in-1948.html;
  NYU–UG Research Integrity Training Program phase 2 (2023–28), scope includes reproducibility
  https://med.nyu.edu/departments-institutes/population-health/divisions-sections-centers/medical-ethics/research/nyu-university-ghana-research-integrity-training-program;
  Laar et al. 2020 baseline https://pure.ug.edu.gh/en/publications/institutional-approaches-to-research-integrity-in-ghana-3/.
  African Reproducibility Network (africanrn.org) listed in UKRN directory.
- Epistemics / gap framing: training/policy; no mechanism.
- Institutions & people: University of Ghana; NYU Grossman; AfricanRN.
- Take / Ahead: take: nothing | ahead: all.
- Confidence: medium | Queries: 1

### Greece
- Direct (2026 SOTA): NOTHING FOUND from Greek institutions (queries: "Greece research integrity reproducibility
  metascience 2025 2026 Ioannidis…"; "Greece LLM claim verification … Demokritos Thessaloniki"). General claim-
  verification results (non-Greek): CLAIMCHECK https://arxiv.org/abs/2503.21717v1 (2025: frontier LLMs "significant
  limitations" as claim verifiers), DeepSciVerify https://arxiv.org/abs/2605.27710 (2026-05), CEUR 2025 humans-vs-LLMs
  benchmark https://ceur-ws.org/Vol-4161/paper1.pdf ("not sufficient for reliable scientific claim verification").
- Adjacent: ABACUS national research-data platform (HEAL-Link + OpenAIRE; LinkedIn-sourced, secondary);
  REWIRE computational-reproducibility project kick-off in Athens (LinkedIn mention only; could not verify —
  budget exhausted before follow-up). No Greek RN in the UKRN directory.
- Epistemics / gap framing: Ioannidis's metascience framing (methods/reporting/reproducibility/evaluation/
  incentives) is Greek-born but Stanford-based; Zacharias Maniadis (ERA Chair, Cyprus/Southampton) 2024 talk
  https://www.ucy.ac.cy/sinnopsis/?p=2373.
- Institutions & people: OpenAIRE (Athens-based); HEAL-Link; NCSR Demokritos (no hits).
- Take / Ahead: take: nothing concrete | ahead: all. Note the three LLM-verifier benchmarks above independently
  support CAPAS's "no model in the verdict" stance.
- Confidence: medium-low (2 queries, 4–6 targeted) | Queries: 2

### Grenada
- Direct (2026 SOTA): NOTHING FOUND (queries: "Grenada St. George's University research integrity reproducibility
  2025" — all hits were St George's, University of London).
- Adjacent / Epistemics / Institutions: none for Grenada.
- Take / Ahead: take: nothing | ahead: all.
- Confidence: high nothing surfaced | Queries: 1

### Guatemala
- Direct (2026 SOTA): NOTHING FOUND.
- Adjacent: SENACYT provides iThenticate free to registered researchers (undated)
  https://agn.gt/senacyt-promueve-integridad-por-medio-de-plataforma-ithenticate/embed/; 2025 SENACYT work plan;
  CLACSO open-science note https://biblioteca-repositorio.clacso.edu.ar/bitstream/CLACSO/277459/1/09-Ciencia-GT.pdf.
- Epistemics / gap framing: similarity-checking = integrity; no reproducibility mechanism.
- Institutions & people: SENACYT, CONCYT, USAC-DIGI (not surfaced).
- Take / Ahead: take: nothing | ahead: all.
- Confidence: high | Queries: 1

### Guinea
- Direct (2026 SOTA): NOTHING FOUND (queries: "Guinea Conakry recherche intégrité scientifique reproductibilité 2025").
- Adjacent: new research & innovation law (Minister Alpha Bacar Barry; 2026 = operationalisation)
  https://guineenews.org/2025/12/03/recherche-et-innovation-la-guinee-affirme-son-leadership-scientifique-en-accueillant-deux-congres-denvergure/?amp=1;
  Cité des Sciences plans a national scientific-data centre
  https://afrique.le360.ma/economie/cite-des-sciences-et-de-linnovation-de-conakry-visite-de-ce-temple-ou-se-batira-lavenir-et-se-creera_BRVJHLIVCRE6XOSIA65Z5XO5TI/.
- Epistemics / gap framing: none.
- Institutions & people: Université Gamal Abdel Nasser; WASCAL (Guinea chairs council 2025).
- Take / Ahead: take: nothing | ahead: all.
- Confidence: high | Queries: 1

### Guinea-Bissau
- Direct (2026 SOTA): NOTHING FOUND (no search engine available — see coverage note; fetched: https://bandim.org/).
- Adjacent: **Bandim Health Project** — health & demographic surveillance of >200,000 people, formally under INASA
  (Instituto Nacional de Saúde Pública) with the University of Southern Denmark; a "Data sharing" area and an
  ERC-data access subpage exist, but the landing page states no registration/integrity stance and is © 2021 —
  https://bandim.org/. INEP not reachable this wave.
- Epistemics / gap framing: none located.
- Institutions & people: INASA, Bandim Health Project (SDU).
- Take / Ahead: take: nothing | ahead: all.
- Confidence: medium that nothing surfaced; low that nothing exists | Queries: 0 searches + 1 fetch

### Guyana
- Direct (2026 SOTA): NOTHING FOUND (fetched: https://uog.edu.gy/ ; https://researchandinnovation.uog.edu.gy/ethics-review/
  — the Ethics Review page is a heading with no policy text, © 2026).
- Adjacent: University of Guyana has an Institute of Research, Innovation and Entrepreneurship (http://ugirie.uog.edu.gy/),
  a School of Graduate Studies and Research, and UG Press (https://www.press.uog.edu.gy/); no integrity, reproducibility
  or open-science policy visible.
- Epistemics / gap framing: none located.
- Institutions & people: University of Guyana (Blueprint 2040).
- Take / Ahead: take: nothing | ahead: all.
- Confidence: medium (institutional pages fetched, no search engine) | Queries: 0 searches + 2 fetches

### Haiti
- Direct (2026 SOTA): NOTHING FOUND (fetched: https://www.ueh.edu.ht/ → https://anciensite.ueh.edu.ht/).
- Adjacent: Université d'État d'Haïti lists a Direction de la recherche, a Conseil scientifique, two in-house journals
  (RED sciences pures et appliquées; CHANTIERS SHS), an institutional repository (http://numeris.ueh.edu.ht:4000) and a
  call for research missions abroad (2026-02-24). The "Comité d'Éthique" menu item links to a placeholder (`#`) — no
  ethics/integrity text is published.
- Epistemics / gap framing: none located.
- Institutions & people: UEH (Vice-rectorat à la recherche).
- Take / Ahead: take: nothing | ahead: all.
- Confidence: medium | Queries: 0 searches + 2 fetches

### Honduras
- Direct (2026 SOTA): NOTHING FOUND for integrity/reproducibility/verification (fetched: https://www.unah.edu.hn/ →
  https://diciht.unah.edu.hn/ , page updated 2026-09-29; ihcieti.gob.hn and dicu.unah.edu.hn do not resolve).
- Adjacent: UNAH's research directorate (DICIHT) publishes a "Política y Normativa de Investigación"
  (https://diciht.unah.edu.hn/politica-y-normativa-de-investigacion/), launched an institutional research-management
  system (SGI-UNAH, circular CGI-001), and runs **"Pago por publicación de artículos Scopus 2026"** and
  "Reconocimiento por publicación en revistas Scopus 2026" (https://diciht.unah.edu.hn/convocatorias/pago-por-publicacion-articulos-scopus-2026/)
  — a pay-per-Scopus-paper incentive, the same structure that the Iraq/India cases below show feeding retractions.
- Epistemics / gap framing: output-count incentives; no integrity mechanism visible.
- Institutions & people: UNAH DICIHT, Consejo General de Investigación; IHCIETI (unreachable).
- Take / Ahead: take: nothing | ahead: all.
- Confidence: medium | Queries: 0 searches + 3 fetches

### Hungary
- Direct (2026 SOTA): NOTHING FOUND for claim gating/autoformalization. HUN-REN runs an **AI4Science / AI4Impact**
  programme (training, "personal AI support", AI Symposium 2026-06-15) and the Neumann Programme (AI, quantum) —
  https://hun-ren.hu/ai4science-programme ; SZTAKI lists no formal-verification or AI-safety group (closest: Csáji
  keynote on robust uncertainty quantification in ML, 2026) — https://sztaki.hun-ren.hu/en. MTA English site: no
  integrity code surfaced.
- Adjacent (strong): **ELTE metascience**. Balázs Aczél is coauthor of Tyner et al., *Nature* 652:143–150 (2026,
  DOI 10.1038/s41586-025-10078-y): 274 claims from 164 papers (2009–2018, 54 journals), **151 replicated (55.1%,
  95% CI 49.2–60.9%)**, median r 0.25 → 0.10, 13 evaluation methods giving 28.6–74.8% — a measured baseline for what
  "good claim" means; first author of "Investigating the analytical robustness of the social and behavioural
  sciences" (*Nature*, DOI 10.1038/s41586-025-09844-9); coauthor of "Core principles of responsible generative AI
  usage in research" (*AI and Ethics* 5:6371–6377, 2025; 8 principles incl. Quality Control, Accountability,
  Transparency; DOI 10.1007/s43681-025-00768-8). **Zoltán Kekecs (ELTE) — Transparent Psi Project** (*R Soc Open Sci*
  10(2), 2023, DOI 10.1098/rsos.191375; 30 authors): consensus design co-written by proponents and opponents, direct
  data deposition, **born-open data, real-time research reports**, video-documented sessions, external research
  auditors; result 49.89% vs Bem's 53.07%. Its successor, the AMP/TPP replication (Walleczek … Kekecs, *PLoS ONE*
  20(11):e0335330, 2025): exploratory effect confirmed at N=127,000 (p=0.013) then not replicated at N=217,800
  (p=0.496) → "method-derived anomaly more plausible". No Hungarian RN in the UKRN directory.
- Epistemics / gap framing: the most "sealed-protocol" tradition in this wave — adversarial co-design, data that is
  open the moment it is born, independent auditors, and credit only after a confirmatory run.
- Institutions & people: ELTE (Aczél, Kekecs, Szaszi, Kovács); HUN-REN (AI4Science); SZTAKI.
- Take / Ahead: take: born-open / real-time data registration as an ingest source (data hashed at creation, before
  analysis) and AMP's "confirmatory protocol for an exploratory result" as the human form of CAPAS's
  credit-only-on-next-sealed-batch rule; the 55.1% baseline as a prior for pilot power calculations | ahead: TPP is
  per-study and human-audited; CAPAS mechanises the audit and returns a verdict.
- Confidence: high (Europe PMC records fetched) | Queries: 0 searches + 8 fetches (aczellab.com unresolved;
  royalsocietypublishing 403)

### Iceland
- Direct (2026 SOTA): NOTHING FOUND (fetched: Rannís via https://island.is/redirects/www.rannis.is/english/ — only a
  Horizon Europe proposal workshop 2026-10-28 and an Innovation Congress 2026-10-29; https://english.hi.is/ — policy
  menu only; the National Bioethics Committee redirect https://island.is/redirects/vsn.is/en returns 404).
- Adjacent: none located. Not in the UKRN RN directory (verified earlier).
- Epistemics / gap framing: none located.
- Institutions & people: Rannís; University of Iceland; VSN.
- Take / Ahead: take: nothing | ahead: all.
- Confidence: medium that nothing surfaced; low that nothing exists (deCODE/HÍ not crawled) | Queries: 0 searches + 3 fetches

### India
- Direct (2026 SOTA): NOTHING FOUND for deterministic/fail-closed claim gating or autoformalization from Indian
  institutions. arXiv catalog: "autoformalization Lean Indian Institute" → 0 results; "India reproducibility
  replication research integrity" → 1 (arXiv 2402.08796, 2024: survey of 430 professors in the USA and India on
  reproducibility — "culturally-centered" solutions). **FMIndia** (Madhavan Mukund, CMI; https://fmindia.cmi.ac.in/):
  classical formal methods community — FM Update Meeting 2026 (Krea, 2–3 July), ATVA 2025 Bangalore, FSTTCS 2026 IIT
  Delhi; no Lean/AI-claim verification listed. IISc KIAC (https://kiac.iisc.ac.in/): AI-for-science (neural operators,
  materials), "Agyeya AI Interpretability & Safety Workshop" Sept–Oct 2026, no verification programme. IIT Madras CeRAI
  (https://cerai.iitm.ac.in/): governance/self-regulation ("Making AI Self-Regulation Work… Perspectives from India"),
  Industry Conclave on AI Governance 2026; no evaluation mechanism.
- Adjacent: **ANRF "AI for Science & Engineering"** (with MeitY; grants up to ₹30 crore/3 yr, ₹50 crore exceptional):
  every proposal must state "accuracy, speed, and robustness measured on peer-reviewed benchmarks" or on
  **pre-agreed data**, release code, checkpoints, datasets and **reproducibility scripts**, hit TRL milestones and
  contribute ≥1 benchmark task — https://anrfonline.in/ANRF/aise_anrf?HomePage=New (no launch date on page). **NAAC/NIRF
  retraction penalty**: announced 2025-07-11 by Anil Sahasrabudhe (NAAC EC chair) — negative marks for retracted papers
  from NIRF 2025 (pilot, symbolic; stricter from 2026); India had 2,737 retractions in 2023, third after China and the
  US — https://theprint.in/science/institutes-universities-will-face-negative-marks-for-retracted-papers-in-nirf-rankings/2687273/
  (via https://retractionwatch.com/2025/07/19/…). Retraction Watch 2025–26: Woxsen rankings-boosting scheme (2026-06-16),
  ex-acting director CSIR-IICB 9 retractions (2026-07-06), authorship-for-fee (2025-12-22), Saveetha/Cureus channel
  (2025-04-08) — https://retractionwatch.com/?s=India. Perception study: Chakravorti, Wu, Koneru, Rajtmajer, "AI for
  research assessment: opportunities and challenges from India", *Information Research* 31 (iConference 2026),
  2026-03-20, DOI 10.47989/ir31iConf64130 (19 Indian faculty/PhD interviews; hybrid human–AI, explainability, infra
  barriers). INSA "Guidelines on Ethical Conduct in the Practice of Science" (undated PDF, https://www.insaindia.res.in/).
- Epistemics / gap framing: enforcement is post-hoc and incentive-based (ranking penalties) plus funder-side artefact
  mandates (ANRF); researcher preference is human-in-the-loop, fail-open; no admissibility language anywhere.
- Institutions & people: ANRF, MeitY, NAAC/NIRF, CeRAI (IIT Madras), KIAC (IISc), CMI (Mukund), INSA.
- Take / Ahead: take: ANRF's "benchmark-or-pre-agreed-data + reproducibility scripts" clause as a funder-side evidence
  schema CAPAS can ingest; the NIRF penalty is a demand signal for pre-publication gating in Indian institutions |
  ahead: no Indian mechanism returns a verdict; penalties act after retraction, CAPAS acts before submission.
- Confidence: medium-high (primary pages fetched; no search engine for discovery) | Queries: 1 search + 13 fetches
  (IndiaAI and DST NQM pages returned empty)

### Indonesia
- Direct (2026 SOTA): NOTHING FOUND (fetched: https://brin.go.id/en — navigation only; /en/news did not load;
  etik.brin.go.id unresolved; https://retractionwatch.com/?s=Indonesia pages 1–2).
- Adjacent: Retraction Watch — Universitas Nasional dean Kumba Digdowiseiso dismissed and barred up to 3 years after
  listing Universiti Malaysia Terengganu academics as coauthors without consent (institutional fact-finding team;
  no ministry/LLDIKTI action reported) https://retractionwatch.com/2024/05/30/indonesian-university-dean-dismissed-barred-from-teaching-asked-to-apologize/ ;
  2026-03-12 IJS/Agha case mentions an Indonesian submitter pressed to cite the editor
  https://retractionwatch.com/2026/03/12/riaz-agha-international-journal-surgery-research-registry-wolters-kluwer/.
  No national policy response or reproducibility network located.
- Epistemics / gap framing: institution-level discipline after exposure; no mechanism.
- Institutions & people: BRIN; Universitas Nasional (case).
- Take / Ahead: take: nothing | ahead: all.
- Confidence: low-medium (BRIN content unreachable) | Queries: 0 searches + 4 fetches

### Iran
- Direct (2026 SOTA): NOTHING FOUND (fetched: https://retractionwatch.com/?s=Iran and the 2024 investigation post).
- Adjacent: **Jahrom University of Medical Sciences** cancer researchers (Kavoosi, Sanaei): papers cite ~70 cell lines
  "from the Pasteur Institute of Iran", which says only 3 were available in a decade; university stopped accepting
  their proposals and referred the file to the Iran National Committee for Ethics in Biomedical Research (post
  2024-10-09, updated 2025-11-26) — https://retractionwatch.com/2024/10/09/exclusive-cancer-researchers-in-iran-under-investigation-as-questions-swirl-around-dozens-of-studies/ ;
  Noora COVID-vaccine first-in-human paper retracted (2024-03-07); science minister Zolfigol 4 retractions (2022).
  No Iranian metascience/RN or formal-verification-of-claims work surfaced.
- Epistemics / gap framing: provenance of materials is the recurring failure (declared source ≠ verifiable source) —
  a CAPAS-shaped problem, handled today by journalists and ethics committees.
- Institutions & people: Jahrom UMS; Pasteur Institute of Iran; Iran National Committee for Ethics in Biomedical Research.
- Take / Ahead: take: a structure-checkable **materials-provenance field** (cell line + supplier record + date) |
  ahead: CAPAS would HOLD undeclared provenance; Iran's handling is post-hoc.
- Confidence: medium (cases verified; policy landscape unsearched) | Queries: 0 searches + 2 fetches

### Iraq
- Direct (2026 SOTA): NOTHING FOUND (fetched: https://retractionwatch.com/?s=Iraq and the 2025-12-01 post).
- Adjacent (dense 2025–26 record): Scopus delisted three Iraqi journals for coercive citation — Medical Journal of
  Babylon, Diyala Journal of Medicine, Iraqi Journal of Agricultural Sciences (the last also dropped from WoS ESCI,
  2025-11-17) https://retractionwatch.com/2025/12/01/iraqi-journals-coercion-delisted-scopus-web-of-science-citation-databases/ ;
  University of Technology Baghdad requires graduate students to cite its journals (2025-10-17); Mustansiriyah
  requires citing colleagues (2025-10-27); Clarivate-branded ministry awards (2025-10-31); Mosul dean retractions
  (2025-10-14); fired physicist with a fake Columbia affiliation (2026-06-29). Ministry policy = indexing and rankings
  (Clarivate agreement); no integrity mechanism.
- Epistemics / gap framing: metrics-maximising, fail-open; the citation-coercion pattern is a bibliography-level
  signal the PPS "Citejacked"-style detector (France) would catch.
- Institutions & people: Ministry of Higher Education; Univ. of Babylon, Diyala, Baghdad, Technology, Mustansiriyah, Mosul.
- Take / Ahead: take: nothing mechanical; a case study for why post-hoc indexing sanctions arrive years late |
  ahead: all.
- Confidence: high on cases | Queries: 0 searches + 2 fetches

### Ireland
- Direct (2026 SOTA): NOTHING FOUND. Lero (SFI centre) claims "formal methods" expertise but publishes no
  verification/AI-assurance line (https://lero.ie/research); its Open Science Charter follows the EU's 8 ambitions
  (PDF uploaded Oct 2025, no preregistration/reproducibility commitments visible —
  https://lero.ie/open-science/open-science-charter/). ADAPT (TCD, €42M): EU AI Act industry case study, no claim
  verification (https://www.adaptcentre.ie/). Research Ireland: integrity and open-research policies "in development";
  no GenAI policy — https://www.researchireland.ie/funding-policies/.
- Adjacent: **National Policy Statement on Ensuring Research Integrity in Ireland** revised Dec 2024; **National
  Research Integrity Forum** (IUA/THEA; Steering Group chaired by Anita Maguire, UCC) publishes **annual misconduct
  statistics** (2023 report issued July 2025) — https://www.iua.ie/ourwork/research-innovation/research-integrity/.
  NORF National Action Plan for Open Research 2022–2030; Responsible Use of Research Metrics resource (2025); Sonraí
  data-stewardship micro-credential workshop 2026-10-01; Diamond Ireland summit 2026-12-09 — https://norf.ie/.
  HRB: Responsible Research Assessment (https://www.hrb.ie/funding/responsible-research-assessment/); HRB Open
  Research platform not fetchable (403) — prior knowledge, unverified: F1000-style open peer review.
- Epistemics / gap framing: policy + published counts + open-research culture; no mechanism; fail-open.
- Institutions & people: NRIF (Maguire), IUA/THEA, NORF/DRI/RIA, Research Ireland, HRB, Lero, ADAPT.
- Take / Ahead: take: NRIF's habit of publishing annual misconduct statistics as a national proof-ledger analogue |
  ahead: all mechanism.
- Confidence: medium-high (primary pages fetched) | Queries: 0 searches + 8 fetches (2 returned 403)

### Israel
- Direct (2026 SOTA): no scientific-claim gate, but the closest **proof-carrying verifier** in this wave: **Katz Lab,
  Hebrew University of Jerusalem** (Guy Katz; "formally verifying systems with machine-learned components", incl. LLMs
  — https://www.katz-lab.com/). **PICID** (Isac, Refaeli, Wu, Barrett, Katz; FMCAD 2026; arXiv 2503.12083, v3
  2026-09-21): the DNN verifier emits proofs in the Alethe SMT format for an **independent checker**, "so users need
  not rely solely on the verifier's output" — https://arxiv.org/abs/2503.12083 ; lineage: certified checker in Imandra
  (2405.10611), proof production (2206.00512); 2026 Marabou papers 2603.12232, 2605.30155, 2607.17290.
  **JuStRank** (Gera, Boni, Perlitz, Bar-Haim, Eden, Yehudai — IBM Research; ACL 2025; arXiv 2412.09569): 48 judge
  realizations × 63 systems ≈ 1.5M judgments; judge **bias** and **decisiveness** each distort system rankings and are
  uncorrelated with each other — https://arxiv.org/html/2412.09569 (Israel lab inferred from the author group; the
  page says only "IBM Research").
- Adjacent: **Benjamini/Heller (Tel Aviv) replicability analysis** — r-value (arXiv 1502.00088), replicability in
  systematic reviews (1907.06856), partial-conjunction tests — statistical replicability as a formal quantity.
  **Qedma** (QESEM error mitigation; IBM Qiskit Functions partner): "Output Integrity… quantifiable confidence", but
  unqualified marketing numbers ("99% fidelity", "1st validated advantage"); Sept 2026 chemistry benchmark with HQC²
  — https://qedma.com/. Quantum Machines (403) and IQCC (unresolved) not verified. ISF site is script-only; no
  integrity policy located. arXiv catalog "Technion formal verification LLM 2026" → 0.
- Epistemics / gap framing: Israel's native strength is formal — proof objects that an outsider can re-check (Katz)
  and selective-inference-aware replicability (Benjamini); the industry quantum layer is fail-open marketing.
- Institutions & people: HUJI (Katz, Isac, Refaeli); IBM Research (Gera, Bar-Haim, Perlitz); TAU (Benjamini, Heller);
  Qedma; Weizmann AI Center (page unreachable twice).
- Take / Ahead: take: make the CAPAS audit hash a **checkable certificate** (PICID/Alethe model: verdict + replayable
  proof an independent checker validates), and add Benjamini's r-value as a replicability evidence field; cite JuStRank
  as measured evidence for "no model in the verdict" | ahead: CAPAS gates claims end-to-end with sealed blind numbers;
  Israeli work verifies networks or ranks judges; Qedma's "quantifiable confidence" has no admissibility rule (CAPAS's
  calibration-snapshot gate would HOLD an undated "99%").
- Confidence: high on PICID/JuStRank/Benjamini (arXiv fetched); low on quantum vendors | Queries: 0 searches + 11 fetches

### Italy
- Direct (2026 SOTA): NOTHING FOUND for claim gating. Formal methods: **FBK Trento FM unit** — nuXmv 2.2.0 released
  2026-06-04; railway (RFI ACC3-OPERA, Dec 2025), space, avionics; no AI-claim verification (Tonetta, Griggio, Bozzano,
  Cavada) — https://fm.fbk.eu/. **Law 132/2025** (23 Sept 2025, GU 223 of 25 Sept, in force 10 Oct 2025): national AI
  law, "dimensione antropocentrica", aligned to Reg. 2024/1689; sector chapter arts 7–18 not retrieved —
  https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:legge:2025-09-23;132.
- Adjacent: **ITRN** 2027 conference hosted by INRiM (Turin, 15–16 Feb) — http://www.itrn.org/. **INRiM** projects
  (4 pages fetched): optical clocks (Arcsecond, CoCoRICO, QuRIOUS), SI-traceable diamond quantum sensors (NoQTeS),
  QUANTIFY photonic sensors, APULEIO "trustworthy, quality-assured quantitative MRI", DI-Vision traceable machine vision
  — https://www.inrim.it/en/research/projects ; **no DCC or AI-metrology project listed** (contrast PTB); Open Science
  working group since 2020, METRICA repository — https://www.inrim.it/en/research/open-science. **CNR Research Ethics
  and Integrity Committee**: guidelines 2015/2019; 1st National Congress on Research Integrity Jan 2025 and the 2025
  "Rome statement on research integrity"; 2nd congress 9–11 March 2027 — https://www.cnr.it/en/ethics. Integrity
  cases: **Italian ob-gyn review mill** (Bishop, Aquarius, Oviedo-García; medRxiv 10.1101/2025.10.20.25338343,
  2025-10-23): 195 suspect reviews of 170 articles, 186 with coercive self-citation (control 4/59), names at Sapienza
  and Palermo — https://retractionwatch.com/2025/11/04/review-mill-italy-ob-gyn-journals-medrxiv-bishop-aquarius-oviedo-garcia/ ;
  serial duplications (2025-08-18, 2026-02-17).
- Epistemics / gap framing: governance-by-committee plus metrological traceability; the review-mill finding shows
  peer review itself is an attack surface — a deterministic gate reads evidence fields, not reviews.
- Institutions & people: INRiM; ITRN; CNR committee; FBK FM; Sapienza/Palermo (as cases); Enrico Bucci (image
  forensics — prior knowledge, not fetched).
- Take / Ahead: take: INRiM SI-traceability projects as a route to DCC-like calibration provenance for Atlas; CNR's
  2027 congress as a venue; the review-mill dataset as a test that a gate is immune to who reviewed | ahead: nothing
  Italian returns a verdict; Italy's integrity response is post-hoc and human.
- Confidence: medium-high (all cited pages fetched; law text partial) | Queries: 0 searches + 11 fetches

---

## Wave summary

**Method note for the re-run (2026-10-14, later session):** the shared WebSearch budget was exhausted again on the
first retry, and the tool's own notice forbids routing searches through other channels, so the 13 outstanding
countries were completed with **WebFetch on primary sources and their native catalogs only** (arXiv search pages,
Retraction Watch site search, Europe PMC REST, institutional sites). This finds what is on known sites; it cannot
discover unknown actors. Entries say "0 searches + N fetches" where that applies.

**Top 5 findings for CAPAS (whole wave):**
1. **PTB Digital Calibration Certificate + D-SI (Germany)** — signed, machine-readable calibration certificates with
   per-parameter uncertainty distributions and dates; DCC Conference Feb 2026; Boehringer ~150k calibrations/yr from
   2027. The direct ingestion target for CAPAS's calibration-snapshot adapter beyond Qiskit —
   https://www.ptb.de/news/dcc , https://imeko.org/publications/tc6-2025/IMEKO-TC6-2025-003.pdf
2. **PICID — proof-carrying neural-network verification (HUJI Katz Lab, Israel; FMCAD 2026)** — the verifier itself
   emits Alethe proofs an independent checker validates "so users need not rely solely on the verifier's output".
   Applied to CAPAS: turn the audit hash into a replayable, independently checkable certificate —
   https://arxiv.org/abs/2503.12083
3. **Transparent Psi Project / AMP (ELTE, Hungary)** — adversarial consensus design, born-open data, real-time
   research reports, external auditors; AMP's confirm-then-replicate at N=127k/218k. The human protocol CAPAS
   mechanises; plus the *Nature* 2026 baseline of 55.1% replicability (274 claims) for power calculations —
   DOI 10.1098/rsos.191375 , 10.1371/journal.pone.0335330 , 10.1038/s41586-025-10078-y
4. **ANRF AI-for-Science mandates + NIRF retraction penalty (India)** — a funder requiring benchmark-or-pre-agreed-data
   results, reproducibility scripts and open checkpoints (an evidence schema CAPAS can ingest) and a national ranking
   that now penalises retractions (demand for pre-publication gating) —
   https://anrfonline.in/ANRF/aise_anrf?HomePage=New , https://theprint.in/science/institutes-universities-will-face-negative-marks-for-retracted-papers-in-nirf-rankings/2687273/
5. **Problematic Paper Screener + Inria autoformalization (France)** — deterministic post-hoc detectors (Citejacked /
   Annulled) as a cheap bibliography pre-gate, and the statement ⊨ intent faithfulness gap that CAPAS's declared-scope
   field addresses — https://dbrech.irit.fr/pls/apex/f?p=9999 , https://www.renaissancephilanthropy.org/leaning-and-rocqing
   Also: **JuStRank (IBM Research, ACL 2025)** — 1.5M judgments showing LLM-judge bias and decisiveness distort
   rankings: measured support for "no model in the verdict" (https://arxiv.org/abs/2412.09569); Fraunhofer catalogue
   field tests (checklists yield no verdict); ITRN 2027 at INRiM (metrology inside a reproducibility network); the
   Italian review-mill dataset (peer review as attack surface); Iraq/Honduras/India pay-or-rank incentives as the
   demand side for a gate.

**3 countries with the strongest direct work:** Germany (PTB DCC/D-SI, AI-Met/AI.Cert, Fraunhofer catalogue),
Israel (HUJI proof-carrying verification, IBM judge benchmarking, TAU replicability statistics), France (Inria
autoformalization, PPS, Guix/Software Heritage, LNE). Strongest *adjacent* work: Hungary (ELTE sealed-protocol
metascience), then Italy (INRiM/ITRN, CNR congresses) and India (ANRF mandates). No country in this wave has a
fail-closed, no-model-in-the-verdict claim gate with sealed blind evaluation and a public proof ledger.

**NOTHING FOUND (searched or fetched, nothing relevant):** Fiji, Gabon, Gambia, Grenada, Guatemala, Guinea,
Guinea-Bissau, Guyana, Haiti, Honduras, Iceland — **11 countries**. (Georgia, Ghana, Indonesia, Iran, Iraq: nothing
direct, but adjacent integrity activity found and recorded.)

**NOT SEARCHED:** none remaining — all 25 countries of the wave (Fiji → Italy) now have an entry.
