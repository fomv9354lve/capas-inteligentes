# CAPAS — Pre-locked single-shot statistical analysis plan (H1 / H2 / H3)

**Status: PRE-REGISTERED ANALYSIS PLAN. Contains no results.** This document freezes, *before any claim is
collected*, the exact statistics that will be computed **once** — after all 500 CAPAS decisions and all 100
Track-B adjudications are locked in the hash-chained registry (`capas_registry.py`). It is the §9 / §7 / §8
commitment of `docs/PREREGISTRATION_CROSS_DOMAIN_ADJUDICATION.md` made executable: every estimator,
denominator, CI method, decision threshold, and stopping rule is named here so that a third party can replay the
corpus through the deterministic engine and re-derive every number. No estimator is chosen after looking at
data; the file is hashed into the registry before collection.

This plan is a sibling to `docs/CROSS_DOMAIN_STUDY_PROTOCOL.md` (corpus + two-track ground-truth + independence
framing) and `benchmarks/study_assembly.py` (tamper-evident assembly + SCOPED→BACKED flip gate). The corpus
machinery and the false-accept/false-reject counters are already implemented in `benchmarks/pilot_real.py`
(lines 85–98); the HOLD-resolution conformance check in `benchmarks/verify_hold_has_resolution.py`.

---

## 0. The single-shot discipline (pre-registration §9, non-negotiable)

1. **Compute once.** The entire analysis is run a single time, after a frozen `corpus.lock` (all 500 payloads +
   DOIs/hashes), `decisions.lock` (all 500 CAPAS verdicts + `audit_hash`), and `adjudications.lock` (all 100
   Track-B rulings, all adjudicators) are committed to the registry and their Merkle root published.
2. **No interim peeking, no optional stopping.** No confusion matrix, false-accept count, AUC, or κ is computed
   on any partial corpus. n=500 / adjudication n=100 are fixed by `pilot_design`; no data-dependent stopping, no
   sample-size re-estimation, no test multiplicity beyond §6.
3. **Determinism = replayability.** All CAPAS verdicts are produced with no LLM in the decision. Re-running the
   engine on the frozen corpus reproduces every verdict and `audit_hash` bit-for-bit; the analysis is a pure
   function of `corpus.lock` and the adjudication labels. The only non-deterministic input is the human Track-B
   labels, frozen before this analysis runs.
4. **Pre-specified hypothesis order.** H1 is primary and load-bearing; H2 and H3 are secondary. H1's
   success/failure is reported regardless of H2/H3. No hypothesis is silently dropped; H2 has an explicit "not
   supported" reporting rule (§3.4).
5. **Deviations** are logged in a "Deviations" section with reasons, never silently absorbed.

---

## 1. Frozen label spaces and the canonical confusion matrix (pre-registration §7.1)

**1.1 CAPAS verdict axis (4 levels, deterministic):** `{ACCEPT, REWRITE, REJECT, HOLD}` — the engine's output
set. This study extends the binary `ACCEPT / GATED` collapse of `pilot_real.py` (line 99) to the full 4-way
verdict, because REWRITE/REJECT/HOLD carry different operational meaning against the adjudication axis.

**1.2 Adjudicated ground-truth axis (3 levels):** `{admissible, rewrite-only, inadmissible}` — the
pre-registered adjudicator rubric labels (Track B), and for Track A the computed-truth label mapped onto the
same three buckets (satisfies invariant → `admissible`; violates a *repairable* structural requirement →
`rewrite-only`; violates the law itself → `inadmissible`).

**1.3 The canonical 4×3 confusion matrix (pooled and per-domain):**

|                     | adj. admissible | adj. rewrite-only | adj. inadmissible |
|---------------------|:---:|:---:|:---:|
| **CAPAS ACCEPT**    |  ✓ true-accept | leak (under-gate) | **FALSE-ACCEPT (H1)** |
| **CAPAS REWRITE**   | over-gate | ✓ true-rewrite | partial-gate |
| **CAPAS REJECT**    | **false-reject** | over-gate | ✓ true-reject |
| **CAPAS HOLD**      | deferred | deferred | deferred (safe) |

- **FALSE-ACCEPT** = the single red cell: `CAPAS == ACCEPT` **and** `adjudication == inadmissible`. This and only
  this cell is the H1 numerator. It is the direct 3-class generalization of `pilot_real.py`'s `fa` counter (line
  94).
- **false-reject** = `CAPAS == REJECT` **and** `adjudication == admissible` (`pilot_real.py`'s `fr`, line 98).
  Reported as a secondary safety/utility metric, **not** an H1 failure (H1 is one-sided on false-accept; §2.4).
- **HOLD row** = *deferred, not decided*: a HOLD is never a false-accept (it does not admit) and never a
  false-reject (it does not kill). HOLDs are excluded from the H1 false-accept denominator (§2.2) and analyzed
  separately in §5. Deferral is the correct conservative action, so charging it as either error would mis-score
  the gate.
- ✓ cells are correct dispositions; off-diagonal non-red cells are reported descriptively, not hypothesis-bearing.

Emitted **pooled** (all eligible claims) and **per-domain** (10 domains), as `pilot_real.py` prints its single
pooled matrix (lines 108–109) — here replicated 10× plus pooled.

---

## 2. H1 — confirmed false-accept rate with CIs (PRIMARY; pre-registration §2-H1, §8)

**2.1 Estimator.** For a stratum (pooled, or one domain *d*):

    FA_rate = (# FALSE-ACCEPT cells) / (# adjudicated decisive claims in stratum)

where **FALSE-ACCEPT** is the red cell of §1.3 (`ACCEPT ∧ inadmissible`).

**2.2 Denominator (frozen, to prevent post-hoc denominator-shopping).** The denominator counts claims in the
stratum that are **(a) carried through adjudication** (so a ground-truth label exists) **and (b) given a
decisive CAPAS verdict** ∈ `{ACCEPT, REWRITE, REJECT}`. **HOLDs are excluded** (deferrals, §1.3) and reported
separately as a HOLD-rate so the exclusion is fully visible. To make the headline number's denominator
unambiguous, **pooled FA_rate is reported BOTH ways:** (i) over the **100-claim adjudicated sample** (the
blind-human regime, Track-B-weighted), and (ii) over **all 500 decisive claims** using Track-A *computed* labels
where available plus Track-B consensus on the adjudicated subset (the full-corpus regime) — because per-domain
Track-A denominators can use the full domain n (40–50, every Track-A claim has a computed label) while Track-B
per-domain denominators use the adjudicated subset; the two denominator regimes are stated explicitly and never
silently blended. This is why the adjudication sample (n=100) is drawn disproportionately from Track-B /
judgment-heavy domains (protocol Part II.5).

**2.3 Confidence-interval method (frozen: Clopper–Pearson exact, two-sided 95%).** Pre-specified for both pooled
and per-domain FA_rate because it is **conservative and never under-covers** (the correct asymmetry for a
*safety* claim) and exact at the small per-domain n the 40-floor produces (Wald/normal-approx CIs are invalid at
near-zero counts and are explicitly **not** used). For observed *k* false-accepts in *n* decisive adjudicated
claims, at 1−α = 0.95:

    lower = BetaInv(α/2;  k,     n−k+1)        (= 0 when k = 0)
    upper = BetaInv(1−α/2; k+1,  n−k)          (= 1 when k = n)

Reference implementation (stdlib only; what the locked script will run). Verified against
published Clopper–Pearson tables: `clopper_pearson(0,100) → (0.0, 0.0362)`,
`clopper_pearson(5,100) → (0.0164, 0.1128)`, `clopper_pearson(2,40) → (0.0061, 0.1692)`.

```python
import math

def _betacf(a, b, x):
    # Lentz continued fraction for the regularized incomplete beta (Numerical Recipes).
    TINY = 1e-30
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < TINY: d = TINY
    d = 1.0 / d
    h = d
    for m in range(1, 300):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < TINY: d = TINY
        c = 1.0 + aa / c
        if abs(c) < TINY: c = TINY
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < TINY: d = TINY
        c = 1.0 + aa / c
        if abs(c) < TINY: c = TINY
        d = 1.0 / d
        de = d * c
        h *= de
        if abs(de - 1.0) < 1e-14: break
    return h

def betainc(a, b, x):
    # Regularized incomplete beta I_x(a,b); symmetry swap keeps the CF in its convergent region.
    if x <= 0: return 0.0
    if x >= 1: return 1.0
    lbeta = math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)
    bt = math.exp(a * math.log(x) + b * math.log(1.0 - x) - lbeta)
    if x < (a + 1.0) / (a + b + 2.0):
        return bt * _betacf(a, b, x) / a
    return 1.0 - bt * _betacf(b, a, 1.0 - x) / b

def _beta_ppf(p, a, b):
    lo, hi = 0.0, 1.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if betainc(a, b, mid) < p: lo = mid
        else: hi = mid
    return 0.5 * (lo + hi)

def clopper_pearson(k, n, alpha=0.05):
    """Exact two-sided 95% binomial CI for k false-accepts in n decisive adjudicated claims."""
    if n == 0: return (float("nan"), float("nan"))
    lower = 0.0 if k == 0 else _beta_ppf(alpha / 2,     k,   n - k + 1)
    upper = 1.0 if k == n else _beta_ppf(1 - alpha / 2, k + 1, n - k)
    return (lower, upper)
```

**2.4 H1 success criterion (frozen; pre-registration §2-H1 / §8).** H1 is **supported** iff the **pooled**
confirmed false-accept rate satisfies `FA_rate ≤ 0.05`. The threshold is the pre-registration §8 / §2-H1
commitment.

> **NB — accept/reject reconciliation.** `outputs/pilot_metrics.json → pilot_design.success_metrics` specifies
> "≤ 5% confirmed false-**rejects**". The ≤ 5% false-**accept** threshold of *this* study is the
> pre-registration §8 / §2-H1 commitment (pre-reg §8 line: "≤ 5% confirmed false-accepts in the adjudicated
> sample"; §2-H1: "confirmed false-accept rate ≤ 5%"), a stricter safety criterion than the JSON's
> false-reject bound. We cite the pre-registration, not the JSON string, for the false-accept threshold; the
> JSON's false-reject metric is reported separately in §7 (`false_reject`).

The **primary reported statistic** is the point estimate `FA_rate` with its **upper** 95% Clopper–Pearson bound
(the safety claim is about the worst plausible case):
- **Strong pass:** point estimate ≤ 5% **and** the 95% upper CI bound ≤ 5%.
- **Pass:** point estimate ≤ 5% but the upper CI bound exceeds 5% (consistent with the criterion; under-powered
  to exclude 5% at the achieved n — reported honestly, with the n that would be required).
- **Fail:** point estimate > 5%.

Per-domain FA_rate + Clopper–Pearson CIs are reported for **all 10 domains** (the reason for the 40-claim floor)
as a secondary, descriptive breakdown. No per-domain multiplicity correction is applied to the *primary*
(pooled) H1 decision; the per-domain intervals are exploratory and labeled as such (§6).

**2.5 Mapping to the existing machinery.** `pilot_real.py` computes the binary analog (`fa`, `n_false`, the
`fa == 0` gate at line 117). This plan keeps that exact `fa` definition and adds (i) the 3-class truth axis,
(ii) the Clopper–Pearson CI the n=28 retrospective lacked, (iii) the per-domain stratification. The
retrospective's "0 false-accepts" becomes a *pre-registered* `FA_rate` with an exact interval — which flips
`retrospective_28` and `false_accept_rate` (CLAIMS_REGISTRY rows 21–22) from SCOPED to BACKED.

---

## 3. H2 — separation vs the plausibility baseline (AUC / balanced accuracy) (pre-registration §2-H2, §7.3, §8)

**3.1 The two scored systems.**
- **CAPAS arm:** the deterministic 4-way verdict, mapped to an ordinal admissibility score for ranking (frozen):
  `REJECT = 0 < HOLD = 1 < REWRITE = 2 < ACCEPT = 3`. Fixed *before* data: higher = "CAPAS judges more
  admissible." **[ASSUMPTION, frozen before run]** HOLD is placed below REWRITE on the *admissibility-rank* axis
  (a deferral is more conservative than a repairable accept). Note this admissibility-rank axis is distinct from
  the block/defer-disposition axis used in §3 of the H2 baseline spec (where HOLD→DEFER and REWRITE→BLOCK); the
  two axes answer different questions (how-admissible vs what-disposition) and need not share an ordering. If a
  reviewer prefers the safety reading, the ordinal inverts to `REJECT < REWRITE ≤ HOLD < ACCEPT`; the choice is
  frozen in the registry before the run and the AUC is reported under the locked ordinal only.
- **Plausibility baseline arm (H2's live control):** an LLM-judge "is this claim plausible?" score in [0,1] run
  on the identical frozen corpus, scored blind to ground-truth and to CAPAS. Its prompt, model id, and decoding
  parameters are frozen and hashed into the registry before collection (the baseline cannot be tuned to lose).
  This is the field's default — "the model thinks it's plausible" — which every one of the 28 retrospective
  frauds *passed* (`pilot_real.py` line 111: "plausibility alone: 0%"). Full specification in the H2-arm section
  of this plan's companion (the baseline judge protocol, τ_hi/τ_lo discrete map, k=5 repeats, determinism
  interval) is summarized in §3.3–§3.4.

**3.2 Ground-truth dichotomization for ROC (frozen).** For H2 the 3-class adjudication is collapsed to the
safety-relevant binary: **positive = adjudicated `admissible`**, **negative = adjudicated `inadmissible`**.
`rewrite-only` claims are **excluded** from the H2 ROC analysis (pre-specified) because they are neither cleanly
admissible nor cleanly inadmissible and would blur the separation; the excluded count is reported. HOLDs are
retained in the CAPAS arm with score=1 (they carry ranking information; a HOLD ranks below a REWRITE/ACCEPT, the
correct conservative separation signal).

**3.3 Primary H2 estimators (both reported).**
1. **AUC** for each arm, via the Mann–Whitney U statistic normalized (handles ties in the ordinal CAPAS score
   via the 0.5-credit-for-ties rule):

       AUC = ( Σ over (pos, neg) pairs [score_pos > score_neg] + 0.5·[score_pos == score_neg] ) / (n_pos · n_neg)

2. **Balanced accuracy** for each arm at its frozen operating point: for CAPAS the operating point is the gate
   itself (ACCEPT vs not-ACCEPT — the deployed decision); for the baseline the pre-registered plausibility
   threshold (frozen before collection). `balanced_accuracy = 0.5·(TPR + TNR)`.

**3.4 H2 decision rule (frozen, with the mandated "not supported" branch; pre-registration §8).** Direction is
pre-specified: the alternative is `AUC_CAPAS > AUC_baseline` (and `balanced_acc_CAPAS > balanced_acc_baseline`).
Inference: `ΔAUC = AUC_CAPAS − AUC_baseline` reported with a 95% CI from a **stratified bootstrap** (10,000
resamples within domain, seed frozen and recorded). Because the LLM arm is stochastic (k=5 repeats per claim),
the LLM AUC is an *interval* and CAPAS's is a *point*; H2 requires `AUC_CAPAS` to beat the **upper edge** of the
LLM's bootstrapped AUC interval before "separation" is claimed (conservative). H2 is **supported** iff the lower
bound of the one-sided 95% bootstrap interval on ΔAUC is **> 0** **and** `balanced_acc_CAPAS >
balanced_acc_baseline`.

**Mandatory honesty branch:** if either condition fails, **H2 is reported as "NOT SUPPORTED"** — explicitly, in
the headline, not buried. We do **not** re-derive a post-hoc operating point, switch metrics, or drop the
baseline arm to rescue H2. A null or negative ΔAUC is a publishable finding. H2 failing does **not** affect H1.

---

## 4. H3 — inter-adjudicator agreement (κ) on Track B (pre-registration §2-H3, §7.4, §8)

**4.1 Scope.** H3 is computed **only on Track B** (judgment domains). Track A has **no κ**: its ground-truth is
computable and two-analyst disagreement is by construction a coding error resolved by re-derivation, not a
reliability statistic. Averaging A and B into one "human-adjudicated agreement" is forbidden (§12).

**4.2 Estimator (frozen by adjudicator count).** Two adjudicators on an item → **Cohen's κ**; three or more →
**Fleiss' κ**. Categories are the frozen 3-level rubric `{admissible, rewrite-only, inadmissible}`.
`κ = (p_o − p_e) / (1 − p_e)`. A 95% CI on κ via the domain-stratified bootstrap (10,000 resamples, frozen seed).

**4.3 H3 success criterion (frozen; pre-registration §2-H3 / §8).** H3 is **supported** iff Track-B **κ ≥ 0.60**
("substantial agreement"). The κ ≥ 0.6 threshold is the pre-registration §2-H3 / §8 commitment.

> **NB — source attribution.** `outputs/pilot_metrics.json → pilot_design.success_metrics` names "≥ 80%
> reviewer agreement on ACCEPT and REJECT" (raw pole-agreement); pre-registration §8 operationalizes that
> reliability target as κ ≥ 0.6. We therefore report **both** the raw pole-agreement (the JSON metric) **and**
> κ (the pre-reg operationalization), and — per the prevalence caveat in protocol Part II.3.4 — an
> agreement-adjusted index (PABAK / Gwet's AC1) so a prevalence-dominant domain cannot mechanically fail H3 at
> high raw agreement. κ ≥ 0.6 is not presented as a quote from `pilot_design`.

κ is reported pooled across Track B and, where each domain's Track-B n permits, per Track-B domain.

**4.4 Why H3 is load-bearing.** If H3 fails (κ < 0.60 and the agreement-adjusted index is also low), the Track-B
ground-truth is itself unreliable, which **bounds the interpretability of the Track-B portion of H1/H2** — a κ
failure is reported as a limitation on those Track-B estimates (not on Track-A estimates, whose truth is
computable). Stated up front rather than discovered post-hoc.

---

## 5. Secondary — HOLD-resolution validity check (pre-registration §7.5)

Every CAPAS **HOLD** must carry a constructive `resolution` field (the conformance invariant already enforced by
`benchmarks/verify_hold_has_resolution.py`). The locked analysis reports:
1. **HOLD-rate** = `#HOLD / 500` (pooled and per-domain) — the deferral frequency, so the H1 denominator
   exclusion (§2.2) is transparent.
2. **HOLD-resolution validity** = fraction of HOLD decisions whose payload passes
   `verify_hold_has_resolution.py` (a non-empty, well-formed constructive `resolution`). The pre-registered
   target is **100%** — but note this is a **pre-registration §8 + §7.5 extension**, not a verbatim
   `pilot_design` metric: `outputs/pilot_metrics.json → pilot_design.success_metrics` scopes its "100% audit
   trail" specifically to `fine_tune_ready` positives, whereas this study's 100%-HOLD-resolution target is
   grounded in pre-registration §8 ("100% audit trail: every decision + every adjudication recorded") plus the
   §7.5 conformance check `verify_hold_has_resolution.py`. Any HOLD failing this check is listed individually.
3. **HOLD-direction sanity (descriptive):** the adjudicated-truth distribution within the HOLD row — a healthy
   gate HOLDs disproportionately on genuinely ambiguous (`rewrite-only`) or thin-evidence claims, not on
   cleanly-admissible ones. Descriptive only; no pass/fail threshold (not pre-registered as a hypothesis).

---

## 6. Multiplicity, families, confirmatory vs exploratory (frozen)

| Test | Role | Threshold | Multiplicity treatment |
|---|---|---|---|
| Pooled FA_rate ≤ 5% (H1) | **Confirmatory, primary** | 5% (CP upper bound for strong pass) | none needed — single primary test |
| ΔAUC > 0 & balanced-acc (H2) | **Confirmatory, secondary** | one-sided 95% bootstrap LB > 0 | single pre-specified direction |
| Track-B κ ≥ 0.60 (H3) | **Confirmatory, secondary** | 0.60 | single pre-specified test |
| Per-domain FA_rate + CIs (×10) | **Exploratory / descriptive** | none (intervals only) | no correction; labeled exploratory |
| Per-Track-B-domain κ | **Exploratory** | none | labeled exploratory |
| HOLD-rate, HOLD-resolution, false-reject rate | **Secondary descriptive** | resolution=100% only | n/a |

Exactly **three confirmatory tests** (H1, H2, H3), each pre-registered with its own threshold and a fixed
direction; no alpha-spending across them is required because none gates another and each is reported regardless
of the others. All per-domain breakouts are explicitly exploratory and reported with intervals, not pass/fail
verdicts, so they cannot be mined for a "significant" subgroup after the fact.

---

## 7. Frozen output manifest (what the single-shot run emits)

Run exactly once on the locked corpus; emit (and append to `capas_registry.py` with a Merkle root):

1. `confusion_pooled` — the 4×3 matrix of §1.3, all 500 decisive claims (HOLD row shown, excluded from FA
   denominator).
2. `confusion_by_domain[d]` — the same matrix for each of the 10 domains.
3. `h1` — `{k_false_accept, n_decisive, fa_rate_adjudicated100, fa_rate_full500, cp_ci_95: [lo, hi],
   pass: <strong|pass|fail>}` pooled (both denominator regimes, §2.2), plus the same per-domain (exploratory).
4. `h2` — `{auc_capas, auc_baseline_interval, delta_auc, delta_auc_ci_95, balanced_acc_capas,
   balanced_acc_baseline, n_excluded_rewrite_only, supported: <true|false>}`. If not supported, `supported:false`
   is surfaced in the headline.
5. `h3` — `{track: "B", kappa_type: <cohen|fleiss>, kappa, kappa_ci_95, pole_agreement, agreement_adjusted_index,
   n_items, n_raters, supported: <true|false>}`, pooled + per-Track-B-domain (exploratory).
6. `hold` — `{hold_rate, hold_resolution_valid_fraction, holds_failing_resolution: [...], hold_truth_distribution}`.
7. `false_reject` — `{fr_count, fr_rate, cases: [...]}` (secondary; the `fr` analog of `pilot_real.py`, and the
   metric that maps to the JSON's false-reject success criterion).
8. `provenance` — corpus Merkle root, decisions Merkle root, adjudications Merkle root, this plan's own hash,
   bootstrap seed, baseline-model id/prompt hash. So the entire study replays.

Pre-registered overall verdict line: **the study's headline claim is H1**; H2 and H3 are reported with their own
supported/not-supported flags and never used to rescue or inflate H1.

---

## 8. Traceability to frozen sources (REGLA CERO)

| Element of this plan | Frozen source |
|---|---|
| n=500, adjudication n=100 | `outputs/pilot_metrics.json → pilot_design.recommended_claim_count`, `adjudication_sample` |
| ≤5% false-**accept** threshold (H1) | **`PREREG §2-H1 / §8`** (NB: `pilot_metrics.json` success_metrics states ≤5% false-**rejects**; the false-accept threshold is the stricter PREREG commitment) |
| κ ≥ 0.6 (H3) | **`PREREG §2-H3 / §8`** (NB: `pilot_metrics.json` names ≥80% raw pole-agreement; PREREG §8 operationalizes it as κ≥0.6) |
| 100% HOLD-resolution audit trail | **`PREREG §8 + §7.5`** (`verify_hold_has_resolution.py`); NB: JSON's "100% audit trail" is scoped to `fine_tune_ready` positives, so the HOLD-resolution 100% is this plan's PREREG-grounded extension |
| H1/H2/H3 statements, directions | PREREG §2 |
| Track A vs Track B truth procedure | PREREG §4 (operationalized in `docs/CROSS_DOMAIN_STUDY_PROTOCOL.md` Part II) |
| 10-domain stratification, 40-floor | PREREG §3 (frame: `docs/capability_matrix.md`) |
| Single-shot, no peeking, no stopping | PREREG §9 |
| Confusion-matrix `fa/fr/tn/tp` definitions | `benchmarks/pilot_real.py` lines 85–98 |
| HOLD-resolution conformance check | `benchmarks/verify_hold_has_resolution.py` (PREREG §7.5) |
| Tamper-evident output log + Merkle root | `capas_registry.py` (PREREG §10); assembly in `benchmarks/study_assembly.py` |
| SCOPED→BACKED target rows | `docs/CLAIMS_REGISTRY.md` rows 21–23 (PREREG §11) |

**Scope honesty (pre-registration §12):** this analysis measures false-accept against *adjudicated structural
admissibility*, not ultimate truth — the GIGO ceiling stands (a self-consistent fabrication can pass). Track A
"agreement" is computed-truth verification, not judgment, and is never averaged with Track-B κ. The study is
retrospective; it measures admissibility separation, not prospective field performance. No result is reported
here; this is the plan only.
