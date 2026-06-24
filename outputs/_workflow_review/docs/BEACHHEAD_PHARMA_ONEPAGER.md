# CAPAS for FDA/PMDA Submissions — Statistical-Claim Admissibility, Beside Pinnacle 21

*One-page beachhead brief for biostatistics / regulatory-submission leads at sponsors and CROs.*
*Every quantitative claim below is either re-derivable from a named repo artifact or explicitly marked DRAFT/ESTIMATE.*

---

## The problem you already own

Your submission has a date. Before it ships, your SDTM/ADaM/define.xml datasets **must** pass
validation — and Pinnacle 21 (Certara) is the same platform FDA and PMDA use, so you already license it
and already run it on every study (FACT — FDA publishes the validation rules; see `docs/MARKET_VALIDATION.md`
Threads 1 & Synthesis).

But Pinnacle 21 checks **structural CDISC conformance** — *is the dataset well-formed?* It does **not**
check **statistical-claim admissibility** — *does the evidence in this dataset actually license the
statistic your CSR/SAP reports?* That second question is the one a reviewer, an adjudication committee, or
opposing counsel asks. Today it lives in manual SAP review and PROC output cross-checks. It is the open
slot beside the tool you already pay for.

Concretely, the deficiencies that pass a structural validator but should never license a confirmatory
claim (each is a coded rule in `capas_pharma.py`):

- a "statistically significant" claim where **p > alpha**
- an asserted effect whose **confidence interval still spans the null**
- a significance claim across **multiple comparisons/endpoints with no multiplicity adjustment** (inflated type-I)
- a **claimed effect direction that contradicts the observed direction**
- a **secondary/exploratory endpoint licensing a confirmatory claim** without pre-specification
- a **reported p-value that does not match the p recomputed from the raw data**

## What CAPAS does

You hand CAPAS a reported statistic plus its **structured evidence fields** (p-value, alpha, CI bounds,
n_comparisons, multiplicity flag, endpoint type, pre-specification flag, claimed vs observed direction).
CAPAS returns one of **ACCEPT / REWRITE / REJECT / HOLD**, deterministically, **fail-closed**, with **no
LLM in the verdict** — the same claim and evidence always return the same disposition, and you can re-run
the exact open tool the reviewer would (`capas_pharma.gate_pharma_stat_claim`). It runs **beside** Pinnacle 21,
not instead of it: P21 owns structural conformance; CAPAS owns statistical admissibility.

## Measurable outcome

1. **Contamination rate found** — run your reported claims through the gate; CAPAS reports how many are
   ACCEPT vs hard-gated (REWRITE/REJECT/HOLD). In the synthetic contract corpus
   (`benchmarks/generate_pharma_corpus.py`, n=3024 cases), **136 ACCEPT, 764 REWRITE, 2124 REJECT, 0 HOLD**
   — i.e. ~95% of the deficient-claim space is caught before it can be asserted (re-derive: run the script;
   it writes `outputs/pharma_corpus.json`).
2. **Claims rewritten** — every REWRITE/REJECT comes with the rule fired and the why-string (e.g. *"p=0.08 >
   alpha=0.05; rewrite to 'no significant difference at alpha=0.05'"*), so the fix is mechanical, not a
   debate (re-derive: `capas_pharma.py` finding messages).
3. **Audit trail exported** — a re-derivable record (claim → evidence → rule → verdict) a reviewer or
   auditor can re-run independently and get the identical result. Determinism *is* the audit trail.

## Honest scope (read this before you buy)

- **CAPAS gates the *declared evidence*, not reality.** It checks whether the evidence fields license the
  claim — not whether the trial was run honestly or the data are real. Garbage in still produces a
  well-formed verdict on garbage (the **GIGO ceiling**, stated plainly across the engine and in
  `capas_pharma.py`). It raises the cost of an inadmissible claim; it does not certify truth.
- **ACCEPT ≠ "true."** ACCEPT means *the evidence licenses this statistic*, nothing more.
- **The corpus is SYNTHETIC contract coverage**, not a measured production false-accept rate. It proves the
  gate's logic exhausts its verdict space deterministically (0 deficient claims ACCEPTed across 3024 cases —
  the fail-closed property), per the module docstring in `benchmarks/generate_pharma_corpus.py`. Your real
  false-accept rate is a study-specific empirical question a design partner establishes.
- **CAPAS does not replace your statistician, your SAP, or Pinnacle 21.** It is a deterministic second pair
  of eyes on a narrow, high-consequence slice the structural validator skips.

## Why now (the wedge)

This is the single beachhead with **budget + urgency + a hard dated trigger**, per
`docs/MARKET_VALIDATION.md` (Synthesis): budget is FACT (sponsors/CROs already license P21); the trigger is
FACT (FDA/PMDA require validated datasets — the deadline *is* the submission); the open slot is
well-grounded (P21 owns structural CDISC conformance, not deep statistical-claim admissibility). CAPAS lands
as a **thin adapter beside Pinnacle 21**, not a new platform to adopt.

## Commercial frame (all figures DRAFT / ESTIMATE — not yet re-derivable)

- **DRAFT pricing anchor:** adjacent regulated-validation spend runs enterprise-scale — Workiva XBRL
  ~$100k–$300k/yr midcap, $1M+ large; SOC 2 audits ~$20k–$150k+/yr (FACT anchors in
  `docs/MARKET_VALIDATION.md` Threads 1–2). CAPAS pricing power *vs* P21 is explicitly listed there as
  **unobtainable / un-validated** — treat any number as an ESTIMATE pending a design-partner deal.
- **DRAFT ROI thesis:** one inadmissible statistical claim caught pre-submission (avoided
  information-request cycle, re-analysis, or review delay) is the unit of value. The dollar figure is an
  ASSUMPTION until a design partner quantifies it.
- **DRAFT GTM motion:** land **one CRO/sponsor design partner with an imminent submission**; run CAPAS on
  their reported claims; report the contamination rate found. Then pre-commit the certification mark to
  neutral governance before adoption (`docs/MARKET_VALIDATION.md` Synthesis, highest-leverage move).

---

*Sources: `benchmarks/generate_pharma_corpus.py` (corpus + fail-closed contract), `capas_pharma.py` (gate
rules + GIGO scope), `docs/MARKET_VALIDATION.md` (market FACTs, buyer ranking, wedge, DRAFT-grade limits).
Market/ROI numbers are DRAFT/ESTIMATE and labeled as such.*
