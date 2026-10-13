# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""CAPAS verdict -> the CEILING a claim may carry in the corpus' 8-state vocabulary
(GOVERNANCE §2: proved · closed-local · empirical · reduced · open · refuted · stale · unknown).

A verdict is about whether the WORDING is licensed by declared evidence; it never grants an
epistemic state by itself. So the mapping yields a ceiling plus what is still required to
reach it -- never a promotion. 'proved' is never granted: it needs a §6 cross-family leg."""
from capas_claim_state import claim_state_ceiling as cs

def test_reject_by_invariant_is_refuted():
    r = cs({"verdict": "REJECT", "reason": "OVERRIDDEN by a domain invariant violation: GRIM ..."})
    assert r["ceiling"] == "refuted"

def test_reject_structural_is_unknown_not_refuted():
    r = cs({"verdict": "REJECT", "reason": "a step in the claimed proof does not re-derive"})
    assert r["ceiling"] == "unknown"

def test_hold_is_unknown():
    assert cs({"verdict": "HOLD", "reason": "missing evidence"})["ceiling"] == "unknown"

def test_rewrite_leading_order_is_closed_local():
    r = cs({"verdict": "REWRITE", "reason": "universally quantified but no uniform bound",
            "licensed_claim": "leading-order result established; remainder CONJECTURED"})
    assert r["ceiling"] == "closed-local"

def test_rewrite_generic_is_reduced():
    r = cs({"verdict": "REWRITE", "reason": "evidence licenses only a weaker claim", "licensed_claim": "x"})
    assert r["ceiling"] == "reduced"

def test_accept_numeric_is_empirical_never_proved():
    r = cs({"verdict": "ACCEPT", "claim_type": "statistical_confidence", "reason": "ok"})
    assert r["ceiling"] == "empirical"

def test_accept_proof_admissibility_caps_at_closed_local_without_section6():
    r = cs({"verdict": "ACCEPT", "claim_type": "proof_admissibility", "reason": "uniform bound proven"})
    assert r["ceiling"] == "closed-local"
    assert any("§6" in x for x in r["required_for_proved"])

def test_accept_proof_with_cross_family_certification_may_be_proved():
    r = cs({"verdict": "ACCEPT", "claim_type": "proof_admissibility", "reason": "uniform bound proven"},
           cross_family_certified=True)
    assert r["ceiling"] == "proved"

def test_stale_overrides_when_older_than_window():
    r = cs({"verdict": "ACCEPT", "claim_type": "statistical_confidence", "reason": "ok"}, age_days=400)
    assert r["ceiling"] == "stale"

def test_every_ceiling_is_a_section2_state():
    S = {"proved","closed-local","empirical","reduced","open","refuted","stale","unknown"}
    for v in ("ACCEPT","REWRITE","REJECT","HOLD"):
        assert cs({"verdict": v, "reason": ""})["ceiling"] in S
