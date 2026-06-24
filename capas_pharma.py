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

    alpha = _num(evidence.get("alpha"))
    if alpha is None:
        alpha = 0.05
    p = _num(evidence.get("p_value"))
    asserts_sig = bool(evidence.get("asserts_significant"))
    asserts_eff = bool(evidence.get("asserts_effect", asserts_sig))
    confirmatory = (evidence.get("claim_kind", "confirmatory") == "confirmatory")

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
    adjusted = bool(evidence.get("multiplicity_adjustment"))
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
    if obs and claimed and obs != "none" and claimed != obs:
        add("REWRITE", "effect_direction",
            f"claim states a '{claimed}' effect but the observed direction is '{obs}'; rewrite to match the data")

    # 5. endpoint pre-specification for a confirmatory claim
    etype = evidence.get("endpoint_type")
    prespec = evidence.get("prespecified")
    if confirmatory and asserts_eff and etype in ("secondary", "exploratory") and prespec is False:
        add("REWRITE", "endpoint_not_prespecified",
            f"a non-prespecified {etype} endpoint cannot license a confirmatory efficacy claim; label it "
            f"hypothesis-generating")

    # 6. nothing asserted + nothing to check -> need the basics
    if asserts_sig and p is None and not findings:
        add("HOLD", "missing_pvalue", "no p-value supplied for a significance claim")

    if not findings:
        verdict = "ACCEPT"
        why = "the supplied evidence licenses the claim: p<alpha, CI excludes the null, direction matches, " \
              "multiplicity handled, endpoint admissible (ACCEPT licenses the claim, it does not assert truth)"
    else:
        worst = max(findings, key=lambda f: _SEV[f["verdict"]])
        verdict = worst["verdict"]
        why = worst["why"]

    return {"verdict": verdict, "why": why, "findings": findings,
            "licensed_reuse": ("confirmatory efficacy" if verdict == "ACCEPT"
                               else "downgraded — see findings"),
            "domain": "pharma_statistics", "alpha": alpha}


# convenience: a CAPAS-style external decision shape (verdict mapped to ACCEPT/REWRITE/REJECT/HOLD already)
def decide(evidence: dict[str, Any]) -> dict[str, Any]:
    return gate_pharma_stat_claim(evidence or {})
