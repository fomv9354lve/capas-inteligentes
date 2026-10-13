# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""Discriminating levers from the 18 residual misses of the Ginibre blind corpus (2026-10-13).
Each fires on a declarable trait of the document, not as a blanket downgrade."""
import capas_sdk as C
def _g(ctype, ev, text="x"): return C.gate(ctype, ev, claim_text=text)

# A. "within k·SE" estimates need replicates: tolerance in SE units + n_replicates < 8 -> REWRITE
def test_within_se_single_seed_rewrites():
    r = _g("exact_model_solution", {"abs_error": 1.9, "tolerance": 2.0, "tolerance_unit": "se", "n_replicates": 1},
           text="row x=0.75 sits 1.9 SE above the limit")
    assert r["verdict"] == "REWRITE" and "replicate" in r["reason"].lower()
def test_within_se_many_seeds_accepts():
    r = _g("exact_model_solution", {"abs_error": 0.58, "tolerance": 2.0, "tolerance_unit": "se", "n_replicates": 16})
    assert r["verdict"] == "ACCEPT"
def test_absolute_tolerance_unaffected():
    assert _g("exact_model_solution", {"abs_error": 1e-9, "tolerance": 1e-6})["verdict"] == "ACCEPT"

# B. convergence/saturation claims need >= 3 points and a rejected alternative
def test_two_point_convergence_rewrites():
    r = _g("exact_model_solution", {"abs_error": 0.0249, "tolerance": 0.042, "n_points": 2},
           text="d converge entre k=96 y k=128: +1.19 SE. CONVERGE.")
    assert r["verdict"] == "REWRITE" and "point" in r["reason"].lower()
def test_convergence_with_points_and_alternative_accepts():
    r = _g("exact_model_solution", {"abs_error": 0.0249, "tolerance": 0.042, "n_points": 4, "alternative_model_rejected": True},
           text="d converges with k")
    assert r["verdict"] == "ACCEPT"
def test_convergence_alternative_not_rejected_rewrites():
    r = _g("exact_model_solution", {"abs_error": 0.0249, "tolerance": 0.042, "n_points": 4, "alternative_model_rejected": False},
           text="d saturates at k=128")
    assert r["verdict"] == "REWRITE"

# C. statistical_confidence with mechanism wording needs a null control
STAT = {"p_value": 1e-5, "alpha": 0.05, "effect_direction_confirmed": True}
def test_mechanism_wording_without_null_control_rewrites():
    r = _g("statistical_confidence", STAT, text="Es un sesgo sistemático a la baja, compatible con k finito")
    assert r["verdict"] == "REWRITE" and "mechanism" in r["reason"].lower()
def test_mechanism_wording_with_null_control_accepts():
    r = _g("statistical_confidence", {**STAT, "null_control_passed": True}, text="la brecha es real y decrece con k")
    assert r["verdict"] == "ACCEPT"
def test_plain_association_unaffected():
    assert _g("statistical_confidence", STAT, text="the correlation is significant")["verdict"] == "ACCEPT"

# D. a failed null control is a REJECT in any type
def test_null_control_failed_rejects():
    r = _g("statistical_confidence", {**STAT, "null_control_passed": False}, text="η explains 11% of transferability")
    assert r["verdict"] == "REJECT" and "null" in r["reason"].lower()

# E. quantifier in text (n of m / all / formalized) needs scope_count_verified
REP = {"artifact_available": True, "independent_reproduction_pass": True}
def test_count_claim_without_verification_rewrites():
    r = _g("reproducibility_check", REP, text="source verification of twelve of the thirteen external citations")
    assert r["verdict"] == "REWRITE" and "count" in r["reason"].lower()
def test_count_claim_verified_accepts():
    r = _g("reproducibility_check", {**REP, "scope_count_verified": True}, text="12 of 13 citations verified")
    assert r["verdict"] == "ACCEPT"
def test_formalized_claim_needs_count():
    r = _g("reproducibility_check", REP, text="the identities have been formalized in Lean")
    assert r["verdict"] == "REWRITE"
