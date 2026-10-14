# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""CAPAS pharma adapter — statistical-claim admissibility for regulated trial submissions.

The market-validated beachhead: Pinnacle 21 owns STRUCTURAL CDISC conformance (is the dataset well-formed
per SDTM/ADaM); it does NOT gate the ADMISSIBILITY of a statistical CLAIM. This adapter does — given a
reported trial statistic + its structured evidence, does the evidence LICENSE the claim? Deterministic,
re-derivable, fail-closed, downgrade-only. It reuses the engine's p-value re-derivation and adds the
pharma invariants P21 skips:

  - significance vs alpha       (claims "significant" but p >= alpha            -> REJECT)
  - multiplicity adjustment      (>1 comparison/endpoint, unadjusted, confirmatory -> REWRITE)
  - CI excludes the null         (CI spans the null while asserting an effect    -> REJECT)
  - effect direction             (claimed direction != observed                 -> REWRITE)
  - endpoint pre-specification    (exploratory/secondary licensing a confirmatory claim -> REWRITE)
  - recompute vs declared p       (raw data disagrees with the reported p        -> REJECT)

Verdicts (fail-closed, take the most severe): REJECT > REWRITE > HOLD > ACCEPT.
ACCEPT = the evidence licenses the claim; it is NOT a statement that the claim is true (GIGO ceiling).
"""
from __future__ import annotations

from typing import Any

# severity order so the worst finding wins (fail-closed / downgrade-only)
_SEV = {"REJECT": 3, "REWRITE": 2, "HOLD": 1, "ACCEPT": 0}


def _num(x):
    return float(x) if isinstance(x, (int, float)) else None


def gate_pharma_stat_claim(evidence: dict[str, Any]) -> dict[str, Any]:
    """Gate a reported pharma statistical claim. `evidence` fields (all optional; missing required ->
    HOLD): p_value, alpha (default 0.05), asserts_significant (bool), n_comparisons (int>=1),
    multiplicity_adjustment (bool/str), endpoint_type ('primary'|'secondary'|'exploratory'),
    prespecified (bool), claim_kind ('confirmatory'|'descriptive'), ci_low, ci_high, ci_null (default 0),
    asserts_effect (bool), observed_direction ('benefit'|'harm'|'none'), claimed_direction,
    rederived_p_match (bool|None — from the engine's raw-data recompute)."""
    if not isinstance(evidence, dict):
        return {"verdict": "HOLD", "why": "no structured evidence supplied", "findings": []}

    findings: list[dict] = []

    def add(v, rule, why):
        findings.append({"verdict": v, "rule": rule, "why": why})

    # External audit 2026-10-14: an EMPTY evidence dict returned ACCEPT "confirmatory efficacy"; a missing alpha
    # defaulted silently to 0.05; multiplicity_adjustment "no" counted as adjusted (bool("no") is True); a missing
    # prespecified passed. Rule since: every field a confirmatory claim depends on must be DECLARED; missing -> HOLD.
    _REQUIRED = ("claim_kind", "asserts_significant", "p_value", "alpha", "n_comparisons", "multiplicity_adjustment",
                 "endpoint_type", "prespecified", "ci_low", "ci_high", "observed_direction", "claimed_direction")
    _missing = [k for k in _REQUIRED if evidence.get(k) is None]
    if evidence.get("claim_kind") == "descriptive":
        _missing = [k for k in ("claim_kind", "asserts_significant") if evidence.get(k) is None]
        if evidence.get("asserts_significant") is True:
            return {"verdict": "REWRITE", "why": "a descriptive claim cannot assert significance; declare claim_kind "
                    "'confirmatory' with its evidence, or drop the significance wording", "findings": [],
                    "licensed_reuse": "descriptive only", "domain": "pharma_statistics", "alpha": _num(evidence.get("alpha"))}
    if _missing:
        return {"verdict": "HOLD", "why": f"missing declared fields: {_missing}; a confirmatory statistical claim is "
                "judged only on declared evidence (nothing is defaulted)", "findings": [],
                "licensed_reuse": "none until the missing fields are declared", "domain": "pharma_statistics", "alpha": None}
    # Re-audit 2026-10-14: claim_kind, endpoint_type and n_comparisons are validated, the effect measure fixes the null
    # (0 for differences, 1 for ratios: an HR CI [0.85, 1.20] includes 1), and a confirmatory claim must assert something.
    _hold = lambda why: {"verdict": "HOLD", "why": why, "findings": [], "licensed_reuse": "none", "domain": "pharma_statistics",
                         "alpha": _num(evidence.get("alpha"))}
    if evidence.get("claim_kind") not in ("confirmatory", "descriptive"):
        return _hold(f"claim_kind {evidence.get('claim_kind')!r} must be 'confirmatory' or 'descriptive' (exact)")
    if evidence.get("claim_kind") == "confirmatory":
        if evidence.get("endpoint_type") not in ("primary", "secondary", "exploratory"):
            return _hold(f"endpoint_type {evidence.get('endpoint_type')!r} must be 'primary', 'secondary' or 'exploratory'")
        _nc = evidence.get("n_comparisons")
        if not isinstance(_nc, int) or isinstance(_nc, bool) or _nc < 1:
            return _hold(f"n_comparisons {_nc!r} must be an integer >= 1 (text is not read as a number)")
        _RATIO = {"hr", "or", "rr", "ratio", "hazard_ratio", "odds_ratio", "risk_ratio", "rate_ratio"}
        _DIFF = {"difference", "mean_difference", "risk_difference", "md", "rd", "smd", "absolute_difference"}
        _em = str(evidence.get("effect_measure", "") or "").strip().lower()
        if _em not in _RATIO | _DIFF:
            return _hold(f"effect_measure {evidence.get('effect_measure')!r} must be declared (a difference or a ratio): it fixes the null")
        _null_expected = 1.0 if _em in _RATIO else 0.0
        if evidence.get("ci_null") is not None and _num(evidence.get("ci_null")) != _null_expected:
            return _hold(f"ci_null {evidence.get('ci_null')!r} contradicts effect_measure {_em!r} (null {_null_expected:g})")
        evidence = {**evidence, "ci_null": _null_expected}
        if evidence.get("asserts_significant") is not True and evidence.get("asserts_effect") is not True:
            return {"verdict": "REWRITE", "why": "a confirmatory claim that asserts neither significance nor an effect licenses no "
                    "confirmatory reuse; declare what it asserts, or label it descriptive", "findings": [],
                    "licensed_reuse": "descriptive only", "domain": "pharma_statistics", "alpha": _num(evidence.get("alpha"))}
        if evidence.get("observed_direction") not in ("benefit", "harm", "none") or evidence.get("claimed_direction") not in ("benefit", "harm", "none"):
            return _hold("observed_direction and claimed_direction must be 'benefit', 'harm' or 'none'")
    alpha = _num(evidence.get("alpha"))
    if alpha is None or not (0.0 < alpha <= 0.10):
        return {"verdict": "HOLD", "why": f"alpha {evidence.get('alpha')!r} is not a significance threshold in (0, 0.10]",
                "findings": [], "licensed_reuse": "none", "domain": "pharma_statistics", "alpha": alpha}
    if not isinstance(evidence.get("prespecified"), bool) or not isinstance(evidence.get("asserts_significant"), bool):
        return {"verdict": "HOLD", "why": "prespecified and asserts_significant must be declared as true/false",
                "findings": [], "licensed_reuse": "none", "domain": "pharma_statistics", "alpha": alpha}
    p = _num(evidence.get("p_value"))
    if p is not None and not (0.0 <= p <= 1.0):
        return _hold(f"p_value {evidence.get('p_value')!r} is not a probability in [0, 1]")
    asserts_sig = evidence.get("asserts_significant") is True
    asserts_eff = bool(evidence.get("asserts_effect", asserts_sig))
    confirmatory = (evidence.get("claim_kind") == "confirmatory")

    # 0. recompute vs declared (the P21-skipped re-derivation): hard contradiction
    if evidence.get("rederived_p_match") is False:
        add("REJECT", "pvalue_rederivation",
            "the p-value recomputed from the supplied raw data does not match the reported p-value")

    # 1. significance vs alpha
    if asserts_sig:
        if p is None:
            add("HOLD", "missing_pvalue", "claim asserts statistical significance but no p-value is supplied")
        elif p > alpha:
            add("REJECT", "significance_vs_alpha",
                f"claim asserts significance but p={p:g} > alpha={alpha:g}; the evidence does not license a "
                f"'significant' claim (rewrite to 'no significant difference at alpha={alpha:g}')")

    # 2. multiplicity: many comparisons, unadjusted, confirmatory significance claim
    nc = evidence.get("n_comparisons")
    nc = int(nc) if isinstance(nc, (int, float)) else 1
    _ma = evidence.get("multiplicity_adjustment")
    _ADJ = {"bonferroni", "holm", "hochberg", "hommel", "fdr", "bh", "benjamini-hochberg", "hierarchical", "gatekeeping",
            "fixed-sequence", "fallback", "dunnett", "graphical", "sidak", "šidák"}
    _NOT = {"no", "none", "false", "unadjusted", "n/a", "na", ""}
    if isinstance(_ma, bool):
        adjusted = _ma
    elif isinstance(_ma, str) and _ma.strip().lower() in _ADJ:
        adjusted = True
    elif isinstance(_ma, str) and _ma.strip().lower() in _NOT:
        adjusted = False
    else:
        return {"verdict": "HOLD", "why": f"multiplicity_adjustment {_ma!r} is not a recognised method or true/false",
                "findings": [], "licensed_reuse": "none", "domain": "pharma_statistics", "alpha": alpha}
    if asserts_sig and confirmatory and nc > 1 and not adjusted:
        add("REWRITE", "multiplicity_unadjusted",
            f"{nc} comparisons/endpoints tested with no multiplicity adjustment; an unadjusted p-value does "
            f"not license a confirmatory significance claim (inflated type-I) — adjust or label exploratory")

    # 3. confidence interval excludes the null
    lo, hi = _num(evidence.get("ci_low")), _num(evidence.get("ci_high"))
    null = _num(evidence.get("ci_null"))
    if null is None:
        null = 0.0
    if asserts_eff and lo is not None and hi is not None:
        if min(lo, hi) <= null <= max(lo, hi):
            add("REJECT", "ci_includes_null",
                f"the {100 * (1 - alpha):.0f}% CI [{lo:g}, {hi:g}] includes the null ({null:g}); the interval "
                f"does not license an effect claim")

    # 4. effect direction matches the data
    obs = evidence.get("observed_direction")
    claimed = evidence.get("claimed_direction")
    if obs == "none" and claimed in ("benefit", "harm"):
        add("REWRITE", "effect_direction",
            f"claim states a '{claimed}' effect but no effect direction was observed; rewrite to 'no observed effect'")
    if obs and claimed and obs != "none" and claimed != obs:
        add("REWRITE", "effect_direction",
            f"claim states a '{claimed}' effect but the observed direction is '{obs}'; rewrite to match the data")

    # 5. endpoint pre-specification for a confirmatory claim
    etype = evidence.get("endpoint_type")
    prespec = evidence.get("prespecified")
    if confirmatory and asserts_eff and etype in ("secondary", "exploratory") and prespec is not True:
        add("REWRITE", "endpoint_not_prespecified",
            f"a non-prespecified {etype} endpoint cannot license a confirmatory efficacy claim; label it "
            f"hypothesis-generating")

    # 6. nothing asserted + nothing to check -> need the basics
    if asserts_sig and p is None and not findings:
        add("HOLD", "missing_pvalue", "no p-value supplied for a significance claim")

    # Re-audit 3 (2026-10-14): p and CI must agree, and only a significance claim licenses confirmatory efficacy.
    if confirmatory and p is not None and lo is not None and hi is not None:
        _excl = not (min(lo, hi) <= null <= max(lo, hi))
        if _excl and p > alpha:
            add("REJECT", "p_ci_incoherent", f"the CI [{lo:g}, {hi:g}] excludes the null ({null:g}) but p={p:g} > alpha={alpha:g}: "
                "the reported p and interval disagree")
        elif not _excl and p <= alpha:
            add("REJECT", "p_ci_incoherent", f"p={p:g} <= alpha={alpha:g} but the CI [{lo:g}, {hi:g}] includes the null ({null:g}): "
                "the reported p and interval disagree")
    if confirmatory and not asserts_sig and asserts_eff:
        add("REWRITE", "effect_without_significance", "a confirmatory effect claim that does not assert significance licenses the "
            "effect estimate as descriptive, not confirmatory efficacy")
    if not findings:
        verdict = "ACCEPT"
        why = "the supplied evidence licenses the claim: p<alpha, CI excludes the null, direction matches, " \
              "multiplicity handled, endpoint admissible (ACCEPT licenses the claim, it does not assert truth)"
    else:
        worst = max(findings, key=lambda f: _SEV[f["verdict"]])
        verdict = worst["verdict"]
        why = worst["why"]

    return {"verdict": verdict, "why": why, "findings": findings,
            "licensed_reuse": ("confirmatory efficacy" if (verdict == "ACCEPT" and confirmatory and asserts_sig)
                               else "descriptive only" if verdict == "ACCEPT"
                               else "downgraded: see findings"),
            "domain": "pharma_statistics", "alpha": alpha}


# convenience: a CAPAS-style external decision shape (verdict mapped to ACCEPT/REWRITE/REJECT/HOLD already)
def decide(evidence: dict[str, Any]) -> dict[str, Any]:
    return gate_pharma_stat_claim(evidence or {})
