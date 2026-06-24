# CAPAS Pharma Conformance Harness — Run-It-Yourself on Your Own Reported Claims

*A design-partner onboarding path for one CRO/sponsor with an imminent FDA/PMDA submission. Determinism is the distribution mechanism: you run the open gate on your own reported statistics, get the identical verdict the reviewer would, and can re-run it forever to reproduce that verdict. Every quantitative claim below is re-derivable from a named repo artifact or marked DRAFT/ESTIMATE/ASSUMPTION.*

## 0. Why this motion (the Sonobuoy analogy, grounded)

`docs/MARKET_VALIDATION.md` (Thread 2) verifies the Certified Kubernetes mechanic: *the mark may be used only by passing a conformance test run with the same open tool (Sonobuoy) users run themselves.* The same file's Synthesis names this the **highest-leverage distribution move (3): "ship a Sonobuoy-equivalent run-it-yourself conformance harness — determinism is the structural advantage; make self-certification the distribution mechanism,"** paired with move (1): **"land one CRO/sponsor design partner with an imminent submission."** CAPAS is *better* suited to this than SOC 2 because there is **no human auditor** in the loop — `capas_pharma.gate_pharma_stat_claim` is deterministic and LLM-free, so the partner runs the exact tool a reviewer would, with no trusted third party required to reproduce the verdict (`docs/MARKET_VALIDATION.md` Thread 2: *"CAPAS's determinism is better suited than SOC 2 (no human auditor → Sonobuoy-style self-certification)"*).

This document specifies **the pharma instance** of that harness: the end-to-end onboarding a single design partner runs on their own desk, on their own reported claims, before their submission ships.

## 1. The motion in one sentence

The partner exports their reported statistics into the pharma payload schema (`capas_pharma_schema.py`), runs the open `capas_pharma` gate **locally and offline**, receives the **ACCEPT / REWRITE / REJECT / HOLD** mix plus a **per-claim rule + why audit trail**, and can **independently re-run the identical tool and reproduce the identical verdict, rule, and why-string** — because the gate is a pure deterministic function (`capas_pharma.py`: *"the same claim and evidence always return the same disposition"*, per `docs/BEACHHEAD_PHARMA_ONEPAGER.md`). The partner self-certifies; CAPAS does not sit between the partner and their data.

## 2. Onboarding gate-0 — set expectations fail-closed (read BEFORE running)

These disclaimers are part of the onboarding, not the fine print. They are stated up front so the partner's expectations are calibrated to what the gate does and does not do. All are grounded in `capas_pharma.py` and `docs/BEACHHEAD_PHARMA_ONEPAGER.md` ("Honest scope"):

1. **CAPAS gates the *declared evidence*, not reality (the GIGO ceiling).** It checks whether your evidence fields license your claim — not whether the trial was run honestly, the randomization held, or the data are real. Garbage in still produces a well-formed verdict on garbage (`capas_pharma.py` docstring; `docs/BEACHHEAD_PHARMA_ONEPAGER.md` "Honest scope"). It **raises the cost of an inadmissible claim; it does not certify truth.**
2. **ACCEPT ≠ "true."** ACCEPT means *the supplied evidence licenses this statistic* — nothing more. The gate's own ACCEPT string says so verbatim: *"(ACCEPT licenses the claim, it does not assert truth)"* (`capas_pharma.py` line 110). A passed claim can still be wrong if the inputs are wrong.
3. **Downgrade-only / fail-closed.** Verdict severity is `REJECT > REWRITE > HOLD > ACCEPT` and the worst finding wins (`capas_pharma.py` `_SEV`, line 24). Missing required evidence does **not** silently pass — it **HOLDs** (e.g. a significance claim with no `p_value` → HOLD, rule `missing_pvalue`). The gate never upgrades a deficient claim to ACCEPT.
4. **This is contract coverage, not a measured production false-accept rate.** The shipped corpus re-derives live: running `benchmarks/generate_pharma_corpus.py` prints **n=3024, 136 ACCEPT / 764 REWRITE / 2124 REJECT / 0 HOLD, fail-closed OK — 0 deficient claims ACCEPTed**. That proves the gate's logic exhausts its verdict space with **0 deficient claims ACCEPTed (the fail-closed property)**. **Your real false-accept rate is a study-specific empirical question this onboarding is designed to establish — it is not the synthetic number.**
5. **CAPAS does not replace your statistician, your SAP, or Pinnacle 21.** It is a deterministic second pair of eyes on the narrow, high-consequence slice P21's structural validator skips (`docs/BEACHHEAD_PHARMA_ONEPAGER.md`).

A partner who has read and acknowledged gate-0 has correctly-set, fail-closed expectations before a single claim is run.

## 3. End-to-end onboarding steps

### Step 1 — Scope the pilot (pick the dated submission)

Per `docs/MARKET_VALIDATION.md` Synthesis move (1), the partner is **one CRO or sponsor with an imminent submission** — the dated trigger is the value. Together you pick **one study** whose CSR/SAP statistical claims are in scope, and a **bounded set of reported claims** (the primary and key secondary efficacy statistics asserted in the CSR/SAP — typically tens, not thousands). The submission date is the pilot deadline; the gate runs *before* the dataset package ships beside Pinnacle 21, not instead of it.

### Step 2 — Export reported statistics into the pharma payload schema

The partner maps each reported statistical claim into the structured evidence dict the gate consumes. The schema is the documented `evidence` contract of `gate_pharma_stat_claim` (`capas_pharma.py` docstring, lines 32-37), enforced machine-checkably by `capas_pharma_schema.py` (`python3 capas_pharma_schema.py check-input --input my_claim.json`). Fields (all optional to the gate; missing required → HOLD):

| Field | Type | Source artifact (where the partner reads it) |
|---|---|---|
| `p_value` | float | reported p in CSR/SAP / PROC output |
| `alpha` | float (default 0.05) | SAP pre-specified significance level |
| `asserts_significant` | bool | does the claim text assert "statistically significant"? |
| `asserts_effect` | bool (defaults to `asserts_significant`) | does the claim assert a treatment effect? |
| `n_comparisons` | int ≥ 1 | number of comparisons/endpoints tested (SAP analysis plan) |
| `multiplicity_adjustment` | bool/str | was a multiplicity procedure applied? (SAP) |
| `ci_low`, `ci_high`, `ci_null` (default 0) | float | reported confidence-interval bounds and the null value |
| `observed_direction` | 'benefit'\|'harm'\|'none' | direction of the effect *in the data* (ADaM-derived) |
| `claimed_direction` | 'benefit'\|'harm'\|'none' | direction the claim *asserts* (CSR text) |
| `endpoint_type` | 'primary'\|'secondary'\|'exploratory' | endpoint hierarchy (SAP/protocol) |
| `prespecified` | bool | was the endpoint pre-specified? (protocol/SAP) |
| `claim_kind` | 'confirmatory'\|'descriptive' | confirmatory vs descriptive (SAP) |
| `rederived_p_match` | bool/None | does p recomputed from the raw data match the reported p? |

**No LLM enters the verdict.** Field extraction is a human/structured-export mapping (a statistician reading the SAP/CSR/ADaM, or a deterministic exporter over structured submission outputs). Even if a partner uses an assistant to *draft* the mapping, the assistant only proposes evidence values — `capas_pharma.gate_pharma_stat_claim` disposes the verdict deterministically from those values. This preserves the engine invariant ("the LLM proposes evidence; CAPAS disposes the verdict"). The output of Step 2 is a list of evidence dicts — one per reported claim — in a single file the partner controls.

**The reliability of this extraction mapping from real submission artifacts is out of scope for this onboarding document and is owned by the integration-seam workstream (`docs/PHARMA_P21_INTEGRATION_SEAM.md`, gap item 1); this harness assumes the evidence dicts as given and gates only their internal admissibility.**

### Step 3 — Run the open gate locally

The partner runs the gate on their own machine, offline. The run-it-yourself tool is the shipped module — no service, no upload, no account:

```python
import json
import capas_pharma  # the open, Apache-2.0 gate the reviewer would run

claims = json.load(open("my_reported_claims.json"))   # list of evidence dicts from Step 2
results = [capas_pharma.decide(ev) for ev in claims]   # decide() == gate_pharma_stat_claim()

mix = {"ACCEPT": 0, "REWRITE": 0, "REJECT": 0, "HOLD": 0}
for r in results:
    mix[r["verdict"]] += 1
print(mix)
```

`capas_pharma.decide(evidence)` is the documented convenience entrypoint (`capas_pharma.py` lines 122-124) and returns, per claim:
`{"verdict", "why", "findings": [{verdict, rule, why}, …], "licensed_reuse", "domain": "pharma_statistics", "alpha"}`.

### Step 4 — Receive the verdict mix + per-claim rule/why audit trail

The partner gets, for their own study:

- **The decision mix** — how many of their reported claims are ACCEPT vs hard-gated (REWRITE/REJECT/HOLD). This is the **contamination rate found** (`docs/BEACHHEAD_PHARMA_ONEPAGER.md` "Measurable outcome" #1): the fraction of asserted statistics the evidence does not license, caught *before* the submission ships.
- **The per-claim audit trail** — each non-ACCEPT carries the **rule fired** and a **why-string** so the fix is mechanical, not a debate (`docs/BEACHHEAD_PHARMA_ONEPAGER.md` #2). The coded rules and their messages are exactly those in `capas_pharma.py`:
  - `significance_vs_alpha` (REJECT): *"claim asserts significance but p=… > alpha=…; … (rewrite to 'no significant difference at alpha=…')"*
  - `ci_includes_null` (REJECT): *"the …% CI […, …] includes the null (…); the interval does not license an effect claim"*
  - `pvalue_rederivation` (REJECT): *"the p-value recomputed from the supplied raw data does not match the reported p-value"*
  - `multiplicity_unadjusted` (REWRITE): *"… comparisons/endpoints tested with no multiplicity adjustment; … (inflated type-I) — adjust or label exploratory"*
  - `effect_direction` (REWRITE): *"claim states a '…' effect but the observed direction is '…'; rewrite to match the data"*
  - `endpoint_not_prespecified` (REWRITE): *"a non-prespecified … endpoint cannot license a confirmatory efficacy claim; label it hypothesis-generating"*
  - `missing_pvalue` (HOLD): *"claim asserts statistical significance but no p-value is supplied"*

### Step 5 — Independently re-run and reproduce the identical verdict (determinism IS the audit trail)

The defining property of the harness: the partner — or their auditor, their biostatistics QC, or an FDA/PMDA reviewer — **re-runs the same open tool on the same evidence and gets the identical verdict, rule, and why-string** (under the same pinned gate version and Python environment). No CAPAS server is consulted; nothing is trusted on faith. This is the Sonobuoy mechanic made pharma-specific: *"a re-derivable record (claim → evidence → rule → verdict) a reviewer or auditor can re-run independently and get the identical result. Determinism is the audit trail."* (`docs/BEACHHEAD_PHARMA_ONEPAGER.md` line 51). Reproducibility is verifiable mechanically — run `capas_pharma.decide` twice on the same evidence and diff the outputs; identical output is the conformance evidence (`outputs/pharma_corpus.json` is the shipped instance of this property at n=3024).

### Step 6 — Self-certification hand-off (the mark precondition)

When the pilot completes, the partner holds a re-derivable conformance record for their study's reported claims. The certificate that lets the partner *attest externally* — "this study's statistical claims passed an independent admissibility gate" — depends on the **mark-governance precondition**: `docs/MARKET_VALIDATION.md` Synthesis names pre-committing the CAPAS mark to neutral governance as the single highest-leverage de-risking act, **required before adoption** (the pharma instantiation is `docs/PHARMA_CERTIFICATION_MARK_PRECONDITION.md`). Until that neutral certification charter exists, Step 6 produces an *internal* re-derivable record (full value to the partner's own QC and submission package); the *attestable external mark* is gated on the charter. This onboarding path therefore terminates at the seam where the certificate node takes over — it does not over-claim an attestation the mark governance does not yet license. (This is itself the fail-closed discipline applied to the go-to-market.)

## 4. Success criteria — pharma adaptation of the pilot-design metric *pattern* (NOT the numbers)

`outputs/pilot_metrics.json` is explicitly a **simulated AI-governance case study** (`"simulated_case_study": true`, `"vertical": "AI governance training-data review"`, and `"non_claim": "The ROI values are planning assumptions … not measured production results"`). Its **`pilot_design` block** gives a reusable *metric pattern* — reviewer-agreement, a confirmed-false-reject ceiling, hours-avoided, and audit-trail completeness — but its **numbers must NOT be imported into pharma** (they are AI-governance, simulated, and per REGLA CERO cannot ground a pharma claim).

The pharma adaptation **borrows the four metric *shapes*** and **leaves the targets to be set with the design partner** (DRAFT — to be agreed pre-pilot, not inherited):

| Metric pattern (from `pilot_metrics.json` `pilot_design`) | Pharma adaptation | Target |
|---|---|---|
| `">= 80% reviewer agreement on ACCEPT and REJECT"` | **Biostatistician agreement** with the gate's ACCEPT/REJECT on an adjudicated sample of the partner's own claims | DRAFT — agreed with partner pre-pilot |
| `"<= 5% confirmed false rejects in adjudicated sample"` | **Confirmed-false-reject ceiling** — a claim the gate hard-gated that the partner's statistician confirms was actually admissible (a gate over-reach) | DRAFT — ceiling agreed pre-pilot |
| `"100% audit trail for fine_tune_ready positives"` | **Audit-trail completeness** — every verdict (ACCEPT and non-ACCEPT) carries a re-derivable rule/why and reproduces identically on independent re-run | **100%** — structural property, verified not estimated (verify mechanically: run `capas_pharma.decide` twice on the same evidence and diff — `outputs/pharma_corpus.json` is the shipped instance of this property at n=3024) |
| `">= 25% senior-review hours avoided"` | **Manual-review effort displaced** on the statistical-admissibility slice P21 skips | DRAFT/ASSUMPTION — `docs/BEACHHEAD_PHARMA_ONEPAGER.md` "Commercial frame" labels CAPAS-vs-P21 value as *unobtainable / un-validated*; the design partner quantifies it; do NOT carry the AI-governance `hours_avoided` / dollar figures |

Of these four, only **audit-trail completeness (100%)** is assertable today, because it follows from the gate being a deterministic, fully-logged pure function — it is the one success criterion that is *verified rather than targeted*. The other three are **partner-established empiricals**; the pilot's purpose is to *measure* them on real reported claims, replacing the GIGO-ceiling-acknowledged synthetic contract figure (0 false-accepts over the n=3024 corpus, which is contract coverage, not a field rate) with a **study-specific measured rate**.

## 5. What "done" looks like for the design partner

At pilot close, the partner has, for one dated study, all four of: (a) a **contamination rate** found on their own reported claims; (b) a **per-claim mechanical-fix audit trail** (rule + why); (c) **independent reproducibility** — anyone re-running the open gate gets the identical verdict; and (d) **measured** reviewer-agreement and false-reject numbers for *their* study (replacing the synthetic contract figure), against targets agreed up front. They reach this with **no LLM in any verdict, fail-closed throughout, GIGO ceiling and ACCEPT≠true acknowledged at gate-0**, and the path stops cleanly at the mark-governance seam — the external attestation waits on the neutral charter, and is not over-claimed here.

---

*Sources (all named, re-derivable or explicitly DRAFT/ESTIMATE/ASSUMPTION): `docs/MARKET_VALIDATION.md` (Thread 2 Sonobuoy/Certified-Kubernetes mechanic; Synthesis moves (1)/(3) and the mark-governance precondition); `capas_pharma.py` (the run-it-yourself gate — `decide`/`gate_pharma_stat_claim`, schema fields, coded rules + why-strings, `_SEV` fail-closed order line 24, ACCEPT≠true string line 110, GIGO docstring); `capas_pharma_schema.py` (the machine-checkable payload contract); `benchmarks/generate_pharma_corpus.py` (synthetic contract coverage, re-derives live to n=3024 / 136-764-2124-0 / 0 false-accepts — labeled NOT a production rate); `docs/BEACHHEAD_PHARMA_ONEPAGER.md` ("Measurable outcome" contamination-rate + audit-trail steps; "Honest scope" GIGO/ACCEPT≠true; "Determinism *is* the audit trail" line 51; commercial figures DRAFT/ESTIMATE); `outputs/pilot_metrics.json` `pilot_design` block (metric **pattern** adapted — its AI-governance simulated numbers explicitly NOT imported, per the file's own `simulated_case_study`/`non_claim` flags).*
