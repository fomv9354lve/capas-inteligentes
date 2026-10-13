# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""Three evidence fields from the Ginibre backtest (ac6a70f): the three misses were true-but-mute
evidence -- nothing in the declared fields named the wrong object, the unread citation, or the
ill-conditioned matrix. These fields force those three questions to be asked."""
import capas_sdk as C
import capas_invariants as ci

def _v(ctype, ev, text="x"):
    return C.gate(ctype, ev, claim_text=text)["verdict"]

# 1. object_declared is OPTIONAL (an absent field is abstention, not detection -- Ginibre's
#    objection); the teeth are object_matches_target: False -> HOLD in any claim type.
def test_exact_model_solution_without_object_declared_is_unchanged():
    assert _v("exact_model_solution", {"abs_error": 1e-15, "tolerance": 1e-12}) == "ACCEPT"

def test_exact_model_solution_with_object_declared_accepts():
    assert _v("exact_model_solution", {"abs_error": 1e-15, "tolerance": 1e-12,
                                       "object_declared": "m*tau at beta=1/2"}) == "ACCEPT"

def test_object_matches_target_false_holds_in_any_type():
    ev = {"claim_scope": "bounded", "steps_all_valid": True, "load_bearing_step_identified": True,
          "uniform_bound_proven": True, "object_matches_target": False}
    assert _v("proof_admissibility", ev) == "HOLD"

# 2. citation fields optional; either False -> REWRITE
def test_unread_load_bearing_citation_rewrites():
    ev = {"claim_scope": "leading_order", "steps_all_valid": True, "load_bearing_step_identified": True,
          "uniform_bound_proven": False, "citation_hypotheses_checked": False}
    r = C.gate("proof_admissibility", ev, claim_text="c4 = 0.511/m, backed by Najim-Yao")
    assert r["verdict"] == "REWRITE" and "not verified" in (r.get("reason") or "").lower()

def test_citation_read_true_does_not_change_verdict():
    ev = {"abs_error": 1e-15, "tolerance": 1e-12, "object_declared": "x",
          "load_bearing_citation_read": True, "citation_hypotheses_checked": True}
    assert _v("exact_model_solution", ev) == "ACCEPT"

# 3. cond_max in bounds -> invariant REJECT
def test_cond_max_bound_flags_and_rejects():
    assert ci.audit({"bounds": {"cond_max": 9e17}})["verdict"] == "FLAG"
    assert ci.audit({"bounds": {"cond_max": 3e5}})["verdict"] == "PASS"
    ev = {"abs_error": 0.002, "tolerance": 0.01, "object_declared": "table x=0.75",
          "invariants": {"bounds": {"cond_max": 9e17}}}
    assert _v("exact_model_solution", ev) == "REJECT"
