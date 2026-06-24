# The CAPAS ↔ Pinnacle 21 / CDISC Integration Seam

**Where CAPAS sits in the submission motion, and how each `capas_pharma` evidence field is sourced from real trial artifacts — without putting an LLM in the verdict.**

*Scope note (REGLA CERO): the evidence schema below is taken from `capas_pharma.py` (the `gate_pharma_stat_claim` docstring and rule bodies). The CDISC/P21 artifact names (ADSL, ADEFF/ADTTE, define.xml, SAP, TLF, CSR) are standard ICH M2/E3 + CDISC submission structures. The division of labor (P21 = structural CDISC conformance; CAPAS = statistical-claim admissibility) is grounded in `docs/BEACHHEAD_PHARMA_ONEPAGER.md` and `docs/MARKET_VALIDATION.md` (Thread 1). No clinical numbers are invented here; this document specifies a seam, not a measured result.*

*Line numbers cited against `capas_pharma.py` are pinned to the module as of the cited commit and should be re-verified after any edit to it; the rule names (`significance_vs_alpha`, `ci_includes_null`, etc.) are the stable anchors.*

---

## 1. Where the seam sits in the existing submission motion

The CDISC/FDA submission pipeline is already a fixed, dated sequence. CAPAS does not insert a new platform; it occupies one specific gap **after structural validation passes and before the statistical narrative is signed**:

```
 RAW (SDTM)
    │
    ▼
 ADaM derivation (ADSL, ADEFF/ADTTE, …)        ← biostatistics programming
    │
    ▼
 ┌──────────────────────────────────────────┐
 │  Pinnacle 21 (Certara)                    │  STRUCTURAL CDISC conformance:
 │  validate SDTM/ADaM/define.xml            │  "is the dataset well-formed?"
 │  → must pass; FDA/PMDA use same rules     │  (MARKET_VALIDATION Thread 1)
 └──────────────────────────────────────────┘
    │  P21 GREEN  (datasets structurally valid)
    ▼
 ┌──────────────────────────────────────────┐
 │  >>> CAPAS SEAM <<<                        │  STATISTICAL-CLAIM admissibility:
 │  gate_pharma_stat_claim(evidence)         │  "does the evidence in these valid
 │  per reported statistic in TLF/CSR        │   datasets LICENSE the statistic the
 │  → ACCEPT / REWRITE / REJECT / HOLD        │   CSR/SAP asserts?"  (the slot P21 skips)
 └──────────────────────────────────────────┘
    │  CAPAS disposition + re-derivable audit record
    ▼
 SAP / CSR statistical-results sign-off       ← biostat lead + medical writer
    │
    ▼
 eCTD submission (FDA / PMDA)
```

**Precise placement.** CAPAS runs *one round per reported confirmatory statistic* — i.e. once per row of the efficacy TLF shell that becomes a sentence in CSR §11 (Efficacy Evaluation). It is gated *behind* P21 deliberately: CAPAS assumes the datasets are already structurally valid (P21's job) and asks the orthogonal question P21 never asks — admissibility of the claim. The natural trigger is **at SAP/CSR statistical sign-off**, the same checkpoint where a biostatistician today does a manual "does this PROC output actually support this sentence" review. CAPAS makes that review deterministic and re-runnable instead of a judgement call.

**What CAPAS is NOT in this seam.** It is not a CDISC validator (P21 owns that), not a dataset transformer, not a p-value *calculator* (it re-checks a supplied recompute flag), and not the statistician. Per `docs/BEACHHEAD_PHARMA_ONEPAGER.md`: "CAPAS does not replace your statistician, your SAP, or Pinnacle 21. It is a deterministic second pair of eyes on a narrow, high-consequence slice the structural validator skips."

---

## 2. Field-by-field mapping: each `capas_pharma` evidence key → its real submission source

The evidence keys consumed by `gate_pharma_stat_claim` (schema from the `capas_pharma.py` docstring, rule bodies in the function) fall into two cleanly separable classes — **(M) mechanically derivable from structured artifacts** and **(D) human/structured declaration of intent**. The boundary between them is the load-bearing honesty claim of this seam and is labeled explicitly in §3.

| `capas_pharma` field | Class | Concrete submission source | How it is extracted (deterministic, no LLM in verdict) |
|---|---|---|---|
| `p_value` | **M** | The reported p in the **efficacy TLF / PROC output** (e.g. PROC MIXED / PROC LIFETEST output, or the `PVALUE`-bearing column of the results dataset feeding the TLF). | Read the numeric cell from the structured TLF results dataset (or the define.xml analysis-results metadata, ARM). A parser lifts the float; it does not interpret prose. |
| `alpha` | **M** | The pre-specified significance level in the **SAP** (e.g. "two-sided α = 0.05"), and for group-sequential designs the *spent* alpha at this analysis. | Declared once per analysis in a structured SAP config / analysis-metadata field; copied as a number. Defaults to 0.05 in code if absent (`capas_pharma.py` line 47-48). |
| `ci_low`, `ci_high` | **M** | The confidence-interval bounds in the same **TLF / results dataset** row as the estimate (e.g. lower/upper CL columns of the treatment-difference or hazard-ratio output). | Read the two numeric bounds from the structured results dataset. `ci_null` defaults to 0 in code (`capas_pharma.py` line 79-81); for a ratio metric (HR/OR) the caller must set `ci_null=1` — **[ASSUMPTION / standard convention, NOT a coded default]**. |
| `n_comparisons` | **M** | Count of confirmatory hypotheses in the **testing family** — derivable from the SAP's pre-specified multiple-testing strategy and the count of primary/key-secondary endpoints in the **define.xml analysis metadata / ADaM `PARAM` levels**. | Count the rows in the pre-specified testing family (structured SAP table or ARM "analysis" entries). Mechanical *given a declared family boundary* (the boundary itself is partly D — see note). |
| `rederived_p_match` | **M** | The result of **recomputing p from the ADaM analysis dataset** (ADEFF/ADTTE + ADSL) with the SAP-specified model, and comparing to the reported `p_value`. | A separate deterministic recompute step (independent SAS/R/Python rerun of the pre-specified analysis on the ADaM data) sets this boolean. CAPAS consumes the boolean; it does not run the model itself. `False` → REJECT (`capas_pharma.py` lines 55-57). This is the field that catches a transcription/QC error structural validation cannot see. |
| `observed_direction` | **M** | The **sign of the point estimate** in the results dataset (favouring treatment vs control; for survival, HR<1 vs >1). | Compute from the numeric estimate's sign relative to the favourable direction declared in the SAP. Mechanical once the favourable direction is declared (the declaration is D). |
| `asserts_significant`, `asserts_effect` | **mixed (M from TLF convention / D from CSR text)** | Whether the **CSR sentence / TLF footnote actually asserts "statistically significant" / "a treatment effect."** | The *safe* path is to treat these as a **structured declaration** the medical writer / biostat lead sets per claim (a checkbox: "this row is asserted as a confirmatory significant effect"). They can also be read mechanically from a TLF significance-flag column where one exists. They are NOT inferred from free CSR prose by an LLM — that would re-introduce a model into the verdict path. |
| `endpoint_type` (`primary`/`secondary`/`exploratory`) | **D** | The endpoint's **pre-specified tier in the SAP / protocol**, mirrored in **ADaM `PARAMCD`/`PARAM` + analysis-purpose flags** and define.xml analysis metadata. | Copied from the structured SAP endpoint table (a declared label), cross-checkable against the ADaM parameter metadata. A label, not a computation. |
| `prespecified` | **D** | Whether this analysis was **pre-specified in the SAP before unblinding** (the dated SAP / amendment history). | A human/structured **attestation** keyed to the dated SAP version. Cannot be derived from the result; it is a fact about the *protocol timeline*, declared by the sponsor. |
| `claimed_direction` | **D** | The **direction the CSR sentence claims** ("benefit" vs "harm"). | A structured declaration of *what the claim says*, set by the claim author — deliberately separated from `observed_direction` (which is M) so CAPAS can catch the mismatch (`capas_pharma.py` lines 89-93). |
| `claim_kind` (`confirmatory`/`descriptive`) | **D** | Whether the sentence is a **confirmatory efficacy claim or a descriptive/hypothesis-generating statement** — set by the SAP's analysis intent. | A declared label per claim (default `confirmatory`, `capas_pharma.py` line 52). Determines whether the multiplicity and pre-specification rules even fire. |

---

## 3. The honest M-vs-D boundary (this is the load-bearing claim)

The mapping above is only credible if the boundary between *mechanically derived* and *humanly declared* is stated plainly rather than papered over. Here it is, with no softening:

**Mechanically derivable (read deterministically from structured artifacts — TLF results datasets, ADaM, define.xml ARM):**
`p_value`, `alpha`, `ci_low`, `ci_high`, `observed_direction`, `n_comparisons` (given a declared family boundary), and `rederived_p_match` (output of a deterministic recompute, not of CAPAS).
→ For these, a small **structured-export parser** lifts numbers from the results dataset / analysis-results metadata. There is no language model anywhere on this path: it is field reads and sign arithmetic. This is the half that makes "CAPAS catches it before the sentence is written" mechanical, not advisory.

**Requires human / structured declaration (a fact about *intent and protocol timeline*, not present in any number):**
`prespecified`, `claim_kind`, `endpoint_type`, `claimed_direction`, and the `asserts_*` flags.
→ These cannot be computed from the data because **they encode what the trial designers intended and what the CSR sentence asserts** — information that lives in the dated SAP/protocol and in the author's claim, not in the estimate. CAPAS takes them as a **structured attestation** the biostat lead / medical writer signs per claim. This is honest, not a weakness: it forces the sponsor to *write down* the pre-specification status and the claim's intent in a form a reviewer can audit, which is exactly the information manual SAP review already (informally) checks.

**The critical invariant — why no LLM enters the verdict.** Per the CAPAS engine discipline ("CAPAS gates evidence fields, not claim text") and the one-pager's "no LLM in the verdict": the temptation is to point an LLM at the CSR prose and have it *infer* `prespecified`, `claim_kind`, or `asserts_significant`. **That path is prohibited at this seam.** The moment a model infers a verdict-determining field from free text, the disposition becomes non-deterministic and non-re-derivable, and the fail-closed property (synthetic corpus: 136 ACCEPT / 764 REWRITE / 2124 REJECT / 0 HOLD across 3,024 cases, 0 false-accepts, `benchmarks/generate_pharma_corpus.py`) is broken — a reviewer re-running the open tool would no longer get the identical result. The boundary therefore must be: **machines read numbers; humans/structured forms declare intent; the gate is pure deterministic logic over both.** An LLM may *assist a human in filling the declaration form* (a drafting aid the human signs off), but its output is never consumed directly by `gate_pharma_stat_claim`. The human attestation, not the model, is what the verdict reads.

**GIGO ceiling, restated for this seam.** Even with a perfect extraction, CAPAS gates the *declared evidence*, not reality (`capas_pharma.py` line 17; `docs/BEACHHEAD_PHARMA_ONEPAGER.md` "Honest scope"). If the sponsor falsely attests `prespecified=True`, or hands a recompute flag that wasn't honestly run, CAPAS produces a well-formed verdict on a false premise. The seam **raises the cost of an inadmissible claim and creates a dated, re-derivable record of what was attested** — it does not certify the trial was run honestly. That honesty boundary belongs to the audit/QA function and the attestation's signer, not to the gate.

---

## 4. The concrete seam artifact: a per-claim evidence packet

In practice the seam is a single structured object — call it a **claim evidence packet** — assembled once per confirmatory TLF row, half auto-populated (M) and half declared (D):

```
claim_evidence_packet:
  # --- M: auto-extracted from P21-validated artifacts (no LLM) ---
  p_value:            <- TLF results dataset, p column
  alpha:              <- SAP analysis-level α (structured)
  ci_low / ci_high:   <- TLF results dataset, CL columns
  ci_null:            <- 0 for differences, 1 for ratios (metric type, structured)
  n_comparisons:      <- count of pre-specified testing family (SAP/ARM)
  observed_direction: <- sign of point estimate vs declared favourable direction
  rederived_p_match:  <- boolean from independent ADaM recompute step
  # --- D: human/structured attestation, signed per claim ---
  asserts_significant / asserts_effect:  <- claim author declares
  endpoint_type:      <- SAP endpoint tier (declared, cross-checked vs ADaM PARAM)
  prespecified:       <- sponsor attestation keyed to dated SAP version
  claimed_direction:  <- what the CSR sentence claims
  claim_kind:         <- confirmatory | descriptive (SAP intent)
  multiplicity_adjustment: <- SAP multiple-testing strategy (declared/structured)
```

This packet is the *only* input to `gate_pharma_stat_claim`. It is the precise translation of "hand-built evidence dict" (today) into "fields sourced from the real submission" (the bridge). The M fields are populated by a structured-export parser against P21-validated outputs; the D fields are a signed attestation form. The packet itself — claim → evidence → rule → verdict — *is* the re-derivable audit record (`docs/BEACHHEAD_PHARMA_ONEPAGER.md` line 51: "Determinism *is* the audit trail"). The machine-checkable contract for this packet is implemented in `capas_pharma_schema.py`.

---

## 5. What this seam establishes, and the residual it does not close

**Closes:** the integration-seam half of the gap — exactly where CAPAS sits (after P21 green, at SAP/CSR sign-off, one round per confirmatory statistic), and a defensible, no-LLM-in-verdict field-by-field path from each evidence key to a named CDISC/CSR source, with the mechanical-vs-declared boundary labeled honestly.

**Does NOT close (out of scope, flagged so it isn't oversold):**
- A *built* structured-export parser against a real results-dataset / define.xml ARM format — this document specifies the contract the parser must satisfy (read numbers, never infer verdict fields), not a running parser.
- Validation against a *real* (non-synthetic) submission — the corpus remains SYNTHETIC contract coverage (`generate_pharma_corpus.py` docstring); the real per-study false-accept rate is a design-partner empirical question (`docs/BEACHHEAD_PHARMA_ONEPAGER.md`).
- The `rederived_p_match` recompute engine itself (the independent ADaM rerun) — CAPAS consumes its boolean output; building/validating that recompute against real ADaM is a separate component.

These belong to the conformance-path (`docs/PHARMA_CONFORMANCE_ONBOARDING.md`) and certificate-governance (`docs/PHARMA_CERTIFICATION_MARK_PRECONDITION.md`) artifacts of the same beachhead.

---

*Sources (all named, re-derivable): `capas_pharma.py` (gate signature, rule bodies, GIGO line 17); `benchmarks/generate_pharma_corpus.py` (synthetic contract corpus, 3,024 cases, 0 false-accepts); `docs/BEACHHEAD_PHARMA_ONEPAGER.md` (P21 division of labor, "Honest scope", "Determinism *is* the audit trail" line 51); `docs/MARKET_VALIDATION.md` (Thread 1, P21 positioning).*
