# CAPAS — Pre-registration: cross-domain, blind-adjudicated admissibility study

**Status: PRE-REGISTRATION DRAFT.** This document is written to be registered (OSF / AsPredicted) **before**
any claim is collected or adjudicated. It contains no results. It exists to convert CAPAS from a technical
demo into a citable *method*: a corpus of **real claims**, across **all CAPAS domains**, where the
ground-truth is fixed by **independent human adjudicators blind to the CAPAS verdict**, with the full
confusion matrix published. Everything here builds on artifacts already in the repo (see §11) — the only
missing layer this protocol adds is **independent human adjudication**, which the existing pilot
(`benchmarks/pilot_real.py`) explicitly names as "the next step."

---

## 1. The specific gap this closes

The current empirical corpus is honest but insufficient for citation (see `docs/CLAIMS_REGISTRY.md`, which
already SCOPES this): the n=28 retrospective (`pilot_real.py`) uses real claims with known ground-truth but
is **agent-coded, not human-adjudicated**; the pharma/decision-mix corpora are **synthetic contract
coverage**. No blind, pre-registered, human-adjudicated, cross-domain confusion matrix exists. This study
produces exactly that.

## 2. Hypotheses (pre-specified, primary first)

- **H1 (primary — false-accept):** On real claims whose ground-truth admissibility is fixed by blind
  independent adjudication, CAPAS's confirmed **false-accept rate ≤ 5%** (an ACCEPT on a claim the
  adjudicators rule structurally inadmissible). This is the load-bearing safety claim.
- **H2 (separation):** CAPAS's verdict separates adjudicator-admissible from adjudicator-inadmissible claims
  better than a plausibility baseline (an LLM-judge "is this claim plausible?" score), measured by AUC /
  balanced accuracy. Direction pre-specified: CAPAS > plausibility.
- **H3 (agreement):** Where ground-truth is a judgment (Track B, §4), inter-adjudicator agreement is
  substantial (Cohen's/Fleiss' κ ≥ 0.6) — i.e. the ground-truth itself is reliable, not noise.

## 3. Design

Cross-domain, retrospective, **n = 500** real claims, **stratified across all 10 CAPAS domains**
(`docs/capability_matrix.md`). Adjudication sub-sample **n = 100** (the subset carried through full blind
human adjudication; pre-specified in `outputs/pilot_metrics.json → pilot_design`). Single-gate per claim;
each claim is one structured payload (schema v3) decided by the open engine.

### Stratification (n = 500 across 10 domains)

Floor of 40 claims/domain so every domain yields a per-domain false-accept interval, with the remainder
weighted to the **judgment-heavy** domains where H1/H2 are most at risk:

| Domain | n | Track | Ground-truth source (real claims) |
|---|---|---|---|
| statistics / inference | 80 | **B** | published result tables + Retraction Watch (p-vs-α, direction, multiplicity overreach) |
| epidemiology | 70 | A+B | published 2×2 tables, VE/RR/OR claims; retracted vs replicated where applicable |
| biology / medicine | 60 | **B** | Retraction Watch (retracted) vs replication/meta-analysis records (valid) |
| quantum | 50 | A | published device calibration rows vs fabricated/inverted rows |
| chemistry | 45 | A | balanced vs unbalanced reactions, mole/mass trios from textbooks/papers |
| physics | 45 | A | dimensional/bounds claims from published equations vs seeded violations |
| finance | 40 | A+B | accounting identities + reported-vs-reference metric claims |
| mathematics | 40 | A | declared solutions/roots that do/don't satisfy their own equation |
| engineering | 40 | A | Ohm/power claims, consistent vs violating |
| universal | 30 | A | probability-bound / conservation claims |
| **Total** | **500** | | |

(Adjudication sample n=100 is drawn **disproportionately from Track B** — see §4 — since that is where human
adjudication is load-bearing; Track A claims are verified deterministically and need fewer human hours.)

## 4. Two adjudication tracks (the design that survives external review)

CAPAS spans domains with **two different kinds of ground-truth**; conflating them would let a reviewer
dismiss the whole study ("blind-adjudicating *V=IR* is trivial"). So ground-truth is fixed per track:

- **Track A — deterministic-truth domains** (quantum, chemistry, physics, mathematics, engineering,
  universal, accounting identities). Ground-truth is the law itself and is **computable**. Two analysts
  independently compute whether the claim violates the invariant; disagreement is impossible in principle
  and any disagreement is a coding error, resolved by re-derivation. The human role here is verifying the
  GROUND-TRUTH (does the claim actually violate the law), **not** judging CAPAS. Metric: CAPAS verdict vs
  computed truth → accuracy + false-accept.

- **Track B — judgment domains** (statistical inference, causal mechanism, reproducibility, evidence
  conflict, systematic review, retraction status). Ground-truth is a **human/world judgment**. Here the
  real test lives: 2–3 domain adjudicators independently rule each claim *admissible / rewrite-only /
  inadmissible* **blind to CAPAS's verdict and to each other**, on a pre-registered rubric. Ground-truth =
  adjudicator consensus (majority; ties → inadmissible, fail-closed). Metric: CAPAS vs consensus confusion
  matrix + κ (H3).

## 5. Sampling frame & claim construction

- Each claim is sourced from a **real published artifact** (paper, retraction notice, calibration table,
  filing), cited by DOI/URL + retrieval hash. No synthetic claims in this corpus.
- For each Track-B claim, the evidence payload is built from **what was available at the claim's publication
  time** (no post-hoc evidence), so CAPAS is tested under the information state a real reviewer had.
- Inclusion/exclusion criteria, the adjudicator rubric, and the payload-construction rules are frozen and
  hashed **before** collection. Corpus is assembled by coders **blind to CAPAS verdicts**.

## 6. Blinding & independence (non-negotiable)

- Adjudicators are **external** to the CAPAS authors, recruited from the relevant fields (meta-science /
  replication for B-bio/stats; subject experts for B-epi/finance).
- Adjudicators never see CAPAS's verdict, reason_code, or audit_hash before submitting their ruling.
- The person running CAPAS does not adjudicate; the adjudicators do not run CAPAS. Roles are disjoint and
  recorded.
- Adjudication happens **before** the confusion matrix is computed; no verdict is revealed mid-study.

## 7. Outcome measures

1. **Confusion matrix** (CAPAS ACCEPT/REWRITE/REJECT/HOLD × adjudicated admissible/rewrite/inadmissible),
   per-domain and pooled.
2. **Confirmed false-accept rate** (primary, H1) with 95% CI.
3. **Separation vs plausibility baseline** (H2): AUC / balanced accuracy, CAPAS vs LLM-judge.
4. **Inter-adjudicator κ** (H3, Track B).
5. Secondary: HOLD-rate and its resolution path validity (every HOLD must carry a constructive
   `resolution`, already conformance-gated by `verify_hold_has_resolution.py`).

## 8. Pre-specified success criteria (from `pilot_design`, frozen)

- ≥ 80% adjudicator agreement on the ACCEPT and REJECT poles (κ ≥ 0.6).
- ≤ 5% confirmed false-accepts in the adjudicated sample (H1).
- 100% audit trail: every decision + every adjudication recorded in the hash-chained registry (§10).
- CAPAS separation strictly above the plausibility baseline (H2), or H2 is reported as not supported.

## 9. Analysis plan & stopping rules

- Primary analysis is the pooled false-accept CI and the per-domain matrix; computed **once**, after all
  500 decisions and all 100 adjudications are locked. No interim peeking, no optional stopping.
- All four verdicts are deterministic (`no LLM in the verdict`); re-running the engine on the frozen corpus
  reproduces every verdict and `audit_hash` exactly — a third party can replay the entire study.
- Deviations from this protocol will be logged and reported in a "Deviations" section, with reasons.

## 10. Tamper-evidence (already built)

Every CAPAS decision and every adjudication entry is appended to the **append-only, hash-chained,
Merkle-rooted signed registry** (`capas_registry.py`), so the corpus, the verdicts, and the human rulings
are individually verifiable and the ordering cannot be rewritten after the fact. The published artifact
includes the Merkle root; `POST /api/gate/verify` re-derives any verdict's `audit_hash`.

## 11. What this reuses from the repo (not greenfield)

- `benchmarks/pilot_real.py` — the n=28 real-claim retrospective + confusion-matrix machinery; the corpus
  scales from here. (Its docstring names human adjudication as "the next step" — this is that step.)
- `outputs/pilot_metrics.json → pilot_design` — n=500, adjudication sample 100, the success metrics in §8.
- `docs/capability_matrix.md` — the 10-domain / 26-gate stratification frame (§3).
- `capas_registry.py` — the tamper-evident adjudication + decision log (§10).
- `docs/CLAIMS_REGISTRY.md` — already marks `false_accept_rate` / `retrospective_28` as SCOPED with this
  study as the named upgrade artifact; on completion those rows move SCOPED → BACKED.

## 12. Limitations (stated up front)

- Retrospective: claims are historical; this measures admissibility separation, not prospective field
  performance. A prospective deployment is a separate study.
- The GIGO ceiling stands: a self-consistent fabrication can pass; CAPAS gates structure, not truth. This
  study measures false-accept against *adjudicated structural admissibility*, not against ultimate truth.
- Track A "human adjudication" is verification of computable truth, not judgment; we report A and B
  separately and never average them into a single misleading "human-adjudicated accuracy."

---

*On completion, this pre-registration + the published confusion matrix is the artifact that converts the
`false_accept_rate` and `retrospective_28` rows in `CLAIMS_REGISTRY.md` from SCOPED to BACKED — i.e. from
"declared estimate" to "cited method." Register this file (OSF/AsPredicted) before collecting claim #1.*
