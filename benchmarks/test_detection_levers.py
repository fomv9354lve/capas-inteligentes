# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""Three detection levers from the Ginibre blind corpus (2026-10-13):
 2. a claim whose TEXT signals a citation must declare citation_hypotheses_checked (else HOLD);
 3. proof_admissibility reaches ACCEPT only with independent_reproduction_pass: True (§6), else REWRITE;
 4. statistical_confidence may carry test_statistic; a p inconsistent with it is a REJECT."""
import capas_sdk as C

def _g(ctype, ev, text="x"):
    return C.gate(ctype, ev, claim_text=text)

PROOF_OK = {"claim_scope": "bounded", "steps_all_valid": True, "load_bearing_step_identified": True,
            "uniform_bound_proven": True}

# ---- 2 ----
def test_text_citing_without_field_holds():
    r = _g("exact_model_solution", {"abs_error": 1e-9, "tolerance": 1e-6},
           text="c4 = 0.511/m, backed by Najim-Yao")
    assert r["verdict"] == "HOLD" and "citation" in r["reason"].lower()

def test_text_citing_with_field_true_unchanged():
    ev = {"abs_error": 1e-9, "tolerance": 1e-6, "citation_hypotheses_checked": True}
    assert _g("exact_model_solution", ev, text="according to Tao (2012)")["verdict"] == "ACCEPT"

def test_text_without_citation_unaffected():
    assert _g("exact_model_solution", {"abs_error": 1e-9, "tolerance": 1e-6}, text="m*tau = 1.99")["verdict"] == "ACCEPT"

# ---- 3 ----
def test_proof_accept_needs_independent_reproduction():
    r = _g("proof_admissibility", PROOF_OK)
    assert r["verdict"] == "REWRITE" and "independent" in r["reason"].lower()

def test_proof_with_independent_reproduction_accepts():
    assert _g("proof_admissibility", {**PROOF_OK, "independent_reproduction_pass": True})["verdict"] == "ACCEPT"

def test_proof_reproduction_false_rewrites_not_rejects():
    assert _g("proof_admissibility", {**PROOF_OK, "independent_reproduction_pass": False})["verdict"] == "REWRITE"

# ---- 4 ----
def test_stat_confidence_p_inconsistent_with_statistic_rejects():
    ev = {"p_value": 0.03, "alpha": 0.05, "effect_direction_confirmed": True,
          "test_statistic": {"stat": "t", "df1": 28, "value": 1.20}}   # t(28)=1.20 -> p=.24, not .03
    r = _g("statistical_confidence", ev)
    assert r["verdict"] == "REJECT" and "recomput" in r["reason"].lower()

def test_stat_confidence_p_consistent_with_statistic_accepts():
    ev = {"p_value": 0.05, "alpha": 0.05, "effect_direction_confirmed": True,
          "test_statistic": {"stat": "t", "df1": 28, "value": 2.05}}
    assert _g("statistical_confidence", ev)["verdict"] == "ACCEPT"

def test_stat_confidence_without_statistic_unchanged():
    ev = {"p_value": 0.03, "alpha": 0.05, "effect_direction_confirmed": True}
    assert _g("statistical_confidence", ev)["verdict"] == "ACCEPT"
