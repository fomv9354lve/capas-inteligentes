# CAPAS for Pharma — Value & ROI Instrument

*Statistical-claim admissibility, beside Pinnacle 21. For a biostatistics / regulatory-submission lead and the enterprise counsel signing off on the spend.*

**Read the labeling rule first.** This document deliberately carries **no measured production numbers.** The only fully re-derivable figure here is a **SYNTHETIC contract-coverage** result (run the named script and reproduce it byte-for-byte). Every economic figure is tagged **[DRAFT]**, **[ESTIMATE]**, or **[ASSUMPTION]** and stays that way until a design partner measures it on their own claims. This is the same honesty discipline CAPAS applies to its AI-governance planning artifact (`outputs/pilot_metrics.json`: `"simulated_case_study": true`, and the `non_claim` disclaimer that its ROI values are *"planning assumptions for customer discovery and business-case framing, not measured production results"*). **We reuse that discipline; we do NOT reuse those numbers** — they are for a different vertical (`"vertical": "AI governance training-data review"`) and a different unit of work, and importing them here would be exactly the contamination this instrument exists to refuse.

---

## 1. The unit of value

**One inadmissible statistical claim caught before the submission ships.**

Not "claims processed," not "hours of review," not a model score. The unit is a single avoided downstream event: a reported statistic that the trial's own declared evidence does not license, intercepted *before* it reaches a reviewer. Each such interception avoids one (or more) of:

- an **information-request / deficiency cycle** (the regulator asks the sponsor to justify or correct the claim post-submission),
- a **re-analysis** (re-running the SAP-defined analysis and re-deriving the affected tables/figures/listings),
- a **review-clock delay** (calendar time added to an FDA/PMDA review while the above resolves).

The dollar value of one avoided event is **not asserted here.** It is study-specific, sponsor-specific, and program-specific, and it is precisely what a design partner is asked to quantify (Section 5). What this instrument *does* provide is (a) a defensible **definition** of the unit, (b) a **re-derivable measurement** of how much of the deficient-claim space the gate actually intercepts, and (c) an **explicitly bounded** set of cost drivers that the unit avoids — so the business case is built on the partner's own numbers, not ours.

---

## 2. The one re-derivable number — and exactly what it is and is not

CAPAS ships a combinatorial **synthetic** corpus that exercises the pharma gate (`capas_pharma.gate_pharma_stat_claim`) across every realistic combination of the evidence axes (p-value vs alpha, multiplicity, CI position, claimed-vs-observed direction, endpoint type / pre-specification). Re-derive it yourself:

```
python3 benchmarks/generate_pharma_corpus.py   # builds, verifies, writes outputs/pharma_corpus.json
```

**Result on disk (`outputs/pharma_corpus.json`), reproduced verbatim by the run above:**

| Verdict | Count | Share |
|---|---|---|
| ACCEPT | 136 | 4.5% |
| REWRITE | 764 | 25.3% |
| REJECT | 2,124 | 70.2% |
| HOLD | 0 | 0.0% |
| **Total cases (n)** | **3,024** | 100% |
| **Hard-gated (REWRITE+REJECT+HOLD)** | **2,888** | **95.5%** |
| **False-accepts (deficient claim ACCEPTed)** | **0** | 0.0% |

*(Re-derivation note: `benchmarks/generate_pharma_corpus.py` reports "500+ cases" in its docstring; the realized combinatorial grid lands at n=3,024 in the written artifact. The number to cite is the one the script writes — 3,024 — not the docstring's lower-bound prose. The grid is deliberately deficiency-weighted: the generator (`build()`, lines 49-61) holds `asserts_significant=True`, `asserts_effect=True`, and `claim_kind="confirmatory"` constant and varies only the deficiency axes via `itertools.product`, so the 70% REJECT / 95.5% hard-gated share is a property of a stress corpus, not a forecast of a real study's claim mix.)*

**What this number IS — a contamination-detection coverage measurement, and a fail-closed contract proof:**

- The **95.5% hard-gated share** is the fraction of this *synthetically constructed* deficient/edge-case space that the gate refuses to wave through. It demonstrates the gate's logic **exhausts its verdict space** — every constructed case lands in a defined disposition, deterministically.
- The **0 false-accepts** is the load-bearing safety property: across all 3,024 cases, **no claim that is structurally insufficient to license a confirmatory significance result was ever ACCEPTed.** That is the *fail-closed* contract, verified in-script by an independent ground-truth oracle (`_deficient(...)` in the same file), not asserted by us.

**What this number is NOT — and this separation is the whole point of the instrument:**

- It is **NOT a production false-accept rate.** It is **SYNTHETIC contract coverage** — "every realistic evidence combination," per the module docstring (*"The corpus is SYNTHETIC contract coverage … NOT a production false-accept rate. It proves the gate's logic exhausts its verdict space deterministically."*). Your real-world rate of caught claims depends entirely on the contamination present in *your* claims, which no synthetic grid can tell you.
- The **95.5% is NOT "95.5% of your claims will be rejected."** The corpus is intentionally weighted toward deficient and boundary cases to stress the contract; a real study's claim set is not drawn from that distribution. **Do not present the 95.5% as an expected production rejection rate** — it is a coverage property of a stress corpus, the pharma analog of a unit-test matrix, not a forecast of your study.
- It says **nothing about whether the underlying trial is sound.** See Section 6 (GIGO ceiling).

This is the only number in this document a counsel can rely on as re-derivable. Everything economic below is explicitly downgraded.

---

## 3. Cost drivers the unit of value avoids (qualitative, named, un-priced)

Each cost driver below is a **real and named** consequence of an inadmissible confirmatory claim reaching a regulator. **None is assigned a dollar figure here** — the magnitudes are a design-partner measurement (Section 5). They are listed to make the value mechanism legible, not to imply a quantified return.

1. **Information-request / deficiency-response cycle.** When a reviewer challenges a statistical claim the data don't license (e.g., significance asserted at p > alpha, or a confirmatory conclusion drawn from an unprespecified secondary endpoint), the sponsor must respond formally. **[ASSUMPTION]** this consumes biostatistics + regulatory + medical-writing effort and calendar time; the size is partner-specific.
2. **Re-analysis and document re-derivation.** Correcting a claim can force re-running the analysis and regenerating the affected TLFs, the relevant CSR sections, and sometimes the SAP narrative. **[ASSUMPTION]** the cost scales with how late it is caught — cheapest pre-submission, most expensive mid-review.
3. **Review-clock / approval-timeline delay.** For a program where time-to-decision has real commercial value, added review calendar time is the dominant cost line. **[ASSUMPTION / out of scope to quantify here]** — this is program-economics the sponsor already models internally; CAPAS does not estimate it.
4. **Credibility / re-review tax.** One demonstrably inadmissible claim invites closer scrutiny of adjacent claims. **[ASSUMPTION]** unquantified, directional only.

The honest economic posture: **CAPAS converts a class of late, expensive, calendar-bearing corrections into early, mechanical, pre-submission ones.** The *direction* of value is defensible from the cost drivers above; the *magnitude* is deliberately left to the partner.

---

## 4. Why the mechanism is credible even before a dollar figure exists

Two structural properties let a regulatory/biostat lead trust the *mechanism* independent of any ROI number:

- **The correction is mechanical, not a debate.** Every REWRITE/REJECT carries the rule fired and a why-string. For example, the `significance_vs_alpha` finding emits, verbatim (`capas_pharma.py` lines 65-66): *"claim asserts significance but p={p:g} > alpha={alpha:g}; the evidence does not license a 'significant' claim (rewrite to 'no significant difference at alpha={alpha:g}')"*. The fix is specified, not adjudicated, which is why catching pre-submission is cheap.
- **The verdict is deterministic and LLM-free.** The same claim + evidence always returns the same disposition; **no language model is in the verdict** (`capas_pharma.gate_pharma_stat_claim`, fail-closed). Determinism *is* the audit trail: a reviewer, an adjudication committee, or opposing counsel can re-run the exact open gate and obtain the identical result. This is what lets a sponsor/CRO eventually attest "passed an independent admissibility gate" rather than "an AI reviewed it."

These properties are **FACT-grade** (re-derivable from the named modules). They establish that the value mechanism is real; they do **not** by themselves establish the value *magnitude*.

---

## 5. The measurement plan — how the [ESTIMATE]/[ASSUMPTION] figures get retired

The instrument is designed to **convert its own DRAFT labels into measured numbers** through a single design-partner engagement, and not before. Borrowing only the *structure* of the AI-governance pilot design in `outputs/pilot_metrics.json` (`pilot_design` block) — not its targets — the pharma measurement is:

- **Input:** one CRO/sponsor design partner with an imminent FDA/PMDA submission runs CAPAS on **their own reported statistical claims** (the run-it-yourself conformance motion `docs/MARKET_VALIDATION.md` flags as highest-leverage; the runnable path is `docs/PHARMA_CONFORMANCE_ONBOARDING.md`).
- **Primary measurable — contamination rate found:** of the partner's real reported claims, the share returned ACCEPT vs hard-gated (REWRITE/REJECT/HOLD). **This, not the 95.5% synthetic figure, is the real number.** It is unknown until measured and is **[TO BE MEASURED]**.
- **Adjudicated correctness:** a biostatistician reviews a sample of the gate's REWRITE/REJECT verdicts and confirms each fired rule is correct (target/threshold set *with the partner*, not pre-asserted here — explicitly avoiding importing the AI-governance pilot's `">= 80% reviewer agreement"` / `"<= 5% confirmed false rejects"` numbers, which are for a different task).
- **Unit-value calibration:** for each genuinely caught inadmissible claim, the partner estimates the avoided cost using *their own* program economics across the Section-3 drivers. This is what retires the **[ASSUMPTION]** on the dollar value of the unit.

Until this runs, the correct statement to a buyer is: *"The gate's contract coverage is proven and re-derivable; the production catch-rate and per-claim value are what we measure together in the pilot."*

---

## 6. Honest scope — the value ceiling, stated plainly

Counsel and a biostat lead should see these limits before any number is discussed:

- **GIGO ceiling.** CAPAS gates the **declared evidence**, not reality. It checks whether the evidence fields license the claim — not whether the trial was conducted honestly or the data are genuine. A fabricated-but-internally-consistent submission still yields a well-formed verdict. CAPAS **raises the cost of asserting an inadmissible claim; it does not certify truth** (`capas_pharma.py` line 17).
- **ACCEPT ≠ true.** ACCEPT means *the declared evidence licenses this statistic* — nothing more (`capas_pharma.py` line 110).
- **Not a replacement.** CAPAS does **not** replace your statistician, your SAP, your CSR authors, or Pinnacle 21. P21 owns structural CDISC conformance; CAPAS owns the narrow, high-consequence statistical-admissibility slice the structural validator skips. It is a deterministic second pair of eyes, not a platform migration.
- **The synthetic/production wall.** The only proven number (Section 2) is contract coverage on constructed cases. **Any production claim about catch-rate or ROI before a design-partner measurement would be a fabricated number — and is omitted here on purpose.**

---

## 7. Commercial frame — explicitly un-validated

Consistent with `docs/BEACHHEAD_PHARMA_ONEPAGER.md` ("Commercial frame") and `docs/MARKET_VALIDATION.md`:

- **[DRAFT] pricing anchor.** Adjacent regulated-validation spend is enterprise-scale (Workiva XBRL ~$100k–$300k/yr midcap; SOC 2 audits ~$20k–$150k+/yr — dollar anchors in `docs/MARKET_VALIDATION.md`).¹ **CAPAS pricing power *vs* Pinnacle 21 is listed there as `unobtainable` / un-validated.** Treat any price as an **[ESTIMATE]** pending a design-partner deal.
- **[ASSUMPTION] ROI thesis.** One inadmissible claim caught pre-submission is the unit of value (Section 1). The dollar figure per unit is an **[ASSUMPTION]** until a partner quantifies it (Section 5).
- **[DRAFT] GTM precondition.** Before adoption, pre-commit the CAPAS certification mark to **neutral governance** so a sponsor/CRO can attest "passed an independent admissibility gate" (`docs/MARKET_VALIDATION.md` Synthesis: the single cheapest, highest-leverage de-risking act; the pharma instantiation is `docs/PHARMA_CERTIFICATION_MARK_PRECONDITION.md`). The value of the *certificate* is contingent on that governance existing; without it, CAPAS is a useful internal check but not an attestable external standard.

¹ *The Workiva / SOC 2 dollar anchors in `docs/MARKET_VALIDATION.md` are web-research-grade figures (per that file's stated provenance), not repo-re-derivable measurements. They bound the adjacent market; they are not a CAPAS measurement and are not used to derive any CAPAS number here.*

---

*Sources (all figures re-derivable or explicitly DRAFT/ESTIMATE/ASSUMPTION): `outputs/pharma_corpus.json` + `benchmarks/generate_pharma_corpus.py` (the one re-derivable number — SYNTHETIC contract coverage, 3,024 cases, 95.5% hard-gated, 0 false-accepts; explicitly NOT a production rate); `capas_pharma.py` (gate rules, the verbatim `significance_vs_alpha` why-string lines 65-66, GIGO scope line 17, ACCEPT≠true line 110, LLM-free determinism); `docs/BEACHHEAD_PHARMA_ONEPAGER.md` (Measurable outcome, Commercial frame — DRAFT labels carried forward); `docs/MARKET_VALIDATION.md` (pricing power vs P21 = un-validated; web-research dollar anchors; run-it-yourself + neutral-governance moves). Honesty discipline (simulated/planning-assumption labeling, `non_claim` disclaimer pattern) reused from `outputs/pilot_metrics.json`; its AI-governance numbers are deliberately NOT inherited.*
