# CAPAS — Market, Competition & Go-to-Market Validation

*Cited, evidence-based assessment (June 2026). Fact vs conjecture labeled throughout. 40+ sources; two
load-bearing facts independently re-verified (Certified Kubernetes/Sonobuoy mark mechanics; FDA-mandated
Pinnacle 21 dataset validation). Produced by a multi-source web-research pass.*

CAPAS = open-core (Apache-2.0), open-standard engine: claim + structured evidence → ACCEPT / REWRITE /
REJECT / HOLD. It does not adjudicate truth, only whether the evidence **licenses** the claim —
deterministically, no LLM in the verdict, re-derivably. Gates structured evidence fields, never free text.
Mark/certification reserved.

## Executive summary (go/no-go)

There **is a fundable wedge — but not the one the category name implies.** "Deterministic admissibility
checking" is not an existing budget line; at the level of any *single* check it is a relabel of work
incumbents already do (Pinnacle 21 for pharma, statcheck for stats, XBRL validators for finance, OPA for
policy, Great Expectations for data). What is undefended is the **composition**: a cross-domain,
fail-closed, re-derivable verdict engine + a **reserved certification mark** that lets a buyer say "this
passed an independent admissibility gate."

The single beachhead with **budget + urgency + a hard dated trigger NOW** is **regulated submissions —
specifically pharma trial-statistics admissibility**, riding the *existing mandatory* FDA/PMDA
dataset-validation motion that Pinnacle 21 already owns. CAPAS's slot there: **statistical-claim
admissibility beyond structural CDISC conformance** (gating p-values / effect sizes / multiplicity /
calibration invariants that P21 does not deeply check).

The moat (trusted re-derivable reference standard + reserved mark in a regulated niche) **is defensible in
principle** — **SOC 2** and **Certified Kubernetes** prove the pattern — but only if mark/standard
governance is **separated from the commercial entity early**. Conflating "owns engine + owns mark + sells
product" is the exact configuration that forked every relicensed open-core project (OpenTofu, Valkey,
OpenSearch).

**Verdict: GO, narrowly.** Fund one vertical wedge (pharma statistical admissibility); pre-commit the
mark to neutral governance; treat AI-training-data and quantum as high-ceiling *future* markets, not the
beachhead. Thinnest evidence is where the largest TAM is (AI/RAG); hardest trigger is where the smallest
greenfield is (pharma).

## Thread 1 — Market gap, buyer, competition

Real spend exists in adjacent categories, captured by incumbents (FACT): Great Expectations (~$65M),
Soda (~$28–41M, acquired NannyML Jun 2025); research-integrity land-grab ("50+ vendors", Elsevier
investing tens of millions, Wiley paper-mill detector flagged 10–13% across 270 journals); **Pinnacle 21
(Certara) is the same platform FDA/PMDA use** — sponsors MUST validate SDTM/ADaM/define.xml before
submission (verified: FDA publishes the validation rules); Workiva XBRL ~$100k–$300k/yr midcap, $1M+ large.

Buyer ranking (budget × urgency × trigger):
1. **Regulated submissions** (pharma stats + financial reporting) — hard non-optional trigger; uses
   Pinnacle 21 / XBRL validators; pays enterprise-scale (FACT). Gap = *statistical-claim* admissibility
   beyond structural conformance (incumbent owns the structural slot).
2. **Journals / data editors** — rising (paper-mill crisis); uses **statcheck** (in peer review at
   *Psychological Science*/*JESP*, cuts error rates — Nuijten & Wicherts 2024), GRIM/GRIMMER/SPRITE,
   **SciScore** ($39.99/$49.99 per 3 credits), Ripeta, Penelope.ai; proven WTP but low budget + 50+
   competitors.
3. **AI labs / enterprises** gating third-party claims into training/RAG/reports — mostly nothing
   deterministic today; budgets huge, trigger soft (FACT). Highest ceiling, most greenfield, hardest sale.

"Admissibility" is **differentiated as a frame/architecture** (nobody sells a single deterministic,
re-derivable, LLM-free, cross-domain claim→evidence gate with a reserved mark) but **a relabel at the
single-check level** (statcheck, GRIM, Great Expectations, and **OPA/Styra** — the architectural twin —
already exist). Defensible story = composition + fail-closed verdict + reserved mark, not the rungs.
*Cautionary FACT:* standalone open-core policy-engine value capture struggled — **Styra acqui-hired by
Apple (Aug 2025), enterprise product wound into upstream OPA; the standard survived, the company's capture
did not.* (Prophy was mis-grouped in the brief — it is reviewer-matching, not numeric integrity.)

*Honest limits:* no clean "research-integrity software market size"; $15–18B "data integrity" figures are
enterprise-pipeline, NOT CAPAS TAM. SciScore/Ripeta ARR unobtainable. The AI-lab trigger is the
weakest-evidenced claim.

## Thread 2 — Open-core / open-standard GTM

Two value-capture archetypes (FACT): (a) free standard + paid platform (OPA, Sigstore, OpenTelemetry);
(b) **open standard + restricted right-to-attest** (SOC 2 — only AICPA CPA firms may issue, audits
~$20k–$150k+/yr; Certified Kubernetes). **CAPAS's reserved-mark plan is archetype (b).**

**Certified Kubernetes is the directly copyable mechanic (verified):** code open; the mark may be used
only by passing a conformance test run with the *same open tool (Sonobuoy)* users run themselves;
submitted by PR + community review; **yearly re-certification**; mark owned by the Linux Foundation. Maps
~1:1 to CAPAS ("open engine + run-it-yourself determinism + reserved mark"). CAPAS's determinism is
*better* suited than SOC 2 (no human auditor → Sonobuoy-style self-certification). But CAPAS lacks SOC 2's
legal moat (CPA licensure); its gatekeeping rests on certification-mark trademark law — enforceable but
weaker (CONJECTURE).

**Failure modes (FACT — the strongest cautionary corpus):** MongoDB (AGPL→SSPL, OSI ruled non-open),
Elastic (→SSPL→AWS OpenSearch fork→reverted to AGPL 2024), HashiCorp (→BSL→OpenTofu/OpenBao), Redis
(→SSPL→Valkey, ~83% of large users testing within a year→reverted 2025, "bridges burned"). Lessons:
relicensing the core to grab value is the #1 trust-killer; it reliably triggers a neutral-foundation fork;
reversals don't restore trust; **separate value capture from standard ownership** so the company can be
acquired (Styra→Apple) without taking the standard down. **Highest-leverage de-risking move: pre-commit
the CAPAS mark to a neutral foundation / irrevocable certification-mark charter BEFORE adoption.**

## Thread 3 — Quantum-advantage claim refutation

Demand for an independent "classically-reproducible-at-claimed-depth" defeater is **factually
demonstrated, but filled by academia + one government program, not a product** (FACT). Every
first-gen advantage claim eroded: Google Sycamore (2019) classically sampled (Pan & Zhang, PRL 2022) →
seconds by 2023–24 → *Leapfrogging Sycamore* (arXiv:2406.18889). **IBM "Utility" 127-qubit (Nature 618,
2023)** neutralized within weeks by Tindall/Flatiron (tensor-network + belief propagation, *more accurate
than the device on a laptop*, PRX Quantum 5 010308) and Begušić & Chan (sparse Pauli dynamics, one laptop
core). Rebuttals are scattered with **no unified verdict** — exactly the gap a standardized defeater
certificate compresses. Newest claims contested in real time: Google **Willow** (Dec 2024) rests on
extrapolation not direct verification; **"Quantum Echoes"/OTOC** (Oct 2025) "first verifiable advantage"
disputed (OTOC complexity class not understood; classical counter arXiv:2510.06324).

Consumers: **DARPA QBI** is a funded, explicitly skeptical third-party IV&V program ("Our opening position
is skepticism"; 11 of ~18 advanced to Stage B Nov 2025; IBM advanced Nov 6 2025) — *the manual
institutional version of what CAPAS automates*. Investors real but soft. Journals: gap real, adoption
unproven. *Honest limit:* the defeater is itself frontier research — CAPAS can encode *known* failure
modes but not *discover* a novel classical algorithm (GIGO ceiling); spoofing is often partial → a graded
**HOLD** is the honest verdict (fits fail-closed). For newest OTOC claims there may be no settled oracle →
**HOLD, not refutation.** DARPA fills the skeptic niche free; the likely *paying* customer is a **vendor
wanting a defensible "passed an independent admissibility check" certificate** (offense-as-defense).

## Thread 4 — AI training-data / RAG admissibility & provenance (2026)

Pain is real and acute (FACT): Data Provenance Initiative found license omission >70%, license error >50%
across 1,800+ datasets; RAG hallucination 15–30%+; **OWASP LLM04:2025 Data & Model Poisoning** spans
pre-training, fine-tuning, AND RAG; **Anthropic + UK AISI + Turing (Oct 2025, arXiv:2510.07192): ~250
malicious documents** suffice to backdoor models 600M–13B (near-constant regardless of scale → pre-ingestion
screening matters more). Regulation in force (FACT — strongest part): **EU AI Act GPAI obligations applied
Aug 2 2025**; providers must publish a training-content summary on the EC's **mandatory template (Jul 24
2025)**; **AI Office enforcement Aug 2 2026**, fines up to **€15M or 3% turnover**; **C2PA** v2.3 +
Conformance Program late 2025, **CISA endorsed Content Credentials Jan 2025**.

*Critical limit (FACT):* the EU AI Act mandates **disclosure, not deterministic admissibility
verification** (the AI Office "will not perform content-level audits") — so mandated demand for a
*verification gate* is softer than the headline. C2PA is creation-time media provenance (metadata often
stripped), not a dataset/claim-admissibility standard. Tools fragmented (provenance audits, datasheets,
contamination detection, poisoning defenses). OWASP recommends **"data validation gates before ingestion"
as a *practice*, not a product** — CAPAS's fail-closed, downgrade-only design maps almost exactly onto it.
Enterprise AI Governance & Compliance market ~$2.5B (2025)→$3.4B (2026), ~39% CAGR (estimate-grade), but
**no consolidated buyer, no budget line called "admissibility gate," no standard.** Position as a
**feature within AI-governance compliance + OWASP LLM04 supply-chain + RAG grounding**, not a market of
its own — yet.

## Synthesis — founder go/no-go

- **Fundable wedge? Yes, narrow.** Not "the admissibility market" (no budget line) but a specific
  deterministic check a regulated buyer already pays adjacent work on, wrapped in a reserved mark whose
  precedent (SOC 2, Certified Kubernetes) is proven.
- **Beachhead NOW: pharma trial-statistics admissibility, sold into the FDA/PMDA dataset-validation
  motion.** Budget FACT (sponsors/CROs license P21); trigger FACT (FDA requires validated datasets, the
  deadline is the submission); greenfield CONJECTURE-well-grounded (P21 checks *structural* CDISC
  conformance, not deep *statistical-claim* admissibility — CAPAS's slot: "the evidence licenses the
  reported statistic," re-derivably). Not journals (low budget, 50+ competitors, statcheck already
  deterministic); not AI/RAG (softest trigger); not quantum (research-grade defeaters, DARPA free).
- **Moat defensible in principle (FACT precedent), conditional in practice (CONJECTURE).** It is the
  trust/certification position, NOT the rungs (every check copyable). Self-runnable conformance
  (Sonobuoy-style) is cheaper than SOC 2's human audit. **Fails if the mark + core stay inside the
  commercial entity** — the configuration that forked every relicensed project.
- **Highest-leverage first moves:** (1) build the pharma statistical-admissibility wedge as a thin
  adapter *beside* Pinnacle 21, land one CRO/sponsor design partner with an imminent submission; (2)
  **pre-commit the CAPAS mark to neutral governance before adoption** — the single cheapest, highest-
  leverage de-risking act; (3) ship a **Sonobuoy-equivalent run-it-yourself conformance harness** —
  determinism is the structural advantage; make self-certification the distribution mechanism.
- **Thin evidence (explicit):** thinnest = AI/RAG "admissibility gate" *as a market* (pain + regulation
  FACT; consolidated buyer + budget CONJECTURE); soft = quantum *paying* demand; unobtainable = clean
  research-integrity TAM + SciScore/Ripeta ARR + CAPAS pricing power vs P21; forward-dated/uncertain =
  an OpenTelemetry "2026 graduation" dateline. Strongest primary-grade facts = FDA-mandated dataset
  validation, EU AI Act dates/template/fines, the open-core relicense→fork record, the IBM/Nature
  classical-rebuttal episode, the Certified Kubernetes / SOC 2 mark-governance mechanics.

*(Full source list — 40+ URLs across the four threads — is in the research transcript.)*
