# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""RMT closed-form identities as invariants. Spec and 10-digit test values supplied by the
Ginibre session (2026-10-12). They are coherence checks between DECLARED closed-form
quantities -- not 'the echo law' -- so a declared A and C that disagree get caught.

Rules from the spec: exact identities -> relative tolerance 1e-9; an estimated quantity needs
its standard error, flags only beyond 4*SE, and without SE the verdict is HOLD, never a flag."""
import capas_invariants as ci

REL = 1e-9

def _v(ev):
    return ci.audit(ev)["verdict"]

# ---- C(x,d): u = x + 2(1-x)d^2 ; A = 1/(1 - x u) ; C = (4/pi^2) u/(1 - x u) ----
def test_cxd_declared_A_and_C_consistent():
    assert _v({"rmt_closed_form": {"x": 0.5, "d": 0.5, "A": 1.6000000000, "C": 0.4863416815}}) == "PASS"

def test_cxd_d0_reduces_to_Cx():
    assert _v({"rmt_closed_form": {"x": 0.5, "d": 0.0, "A": 1.3333333333, "C": 0.2701898230}}) == "PASS"

def test_cxd_missing_1mx_factor_flags():
    # u = x + 2 d^2 (wrong) -> A = 2, C = 0.810569 at x = d = 0.5
    assert _v({"rmt_closed_form": {"x": 0.5, "d": 0.5, "A": 2.0, "C": 0.810569}}) == "FLAG"

# ---- C(x,d,tau): u = x + 2(1-x)d^2 / ((1+tau)(1+tau x)) ----
def test_cxdtau_consistent():
    assert _v({"rmt_closed_form": {"x": 0.5, "d": 0.5, "tau": 0.3, "A": 1.5006273526, "C": 0.4057932474}}) == "PASS"

def test_cxdtau_second_case():
    assert _v({"rmt_closed_form": {"x": 0.3, "d": 0.6, "tau": -0.2, "A": 1.4105642257, "C": 0.5546513774}}) == "PASS"

def test_cxdtau_missing_1_plus_tau_x_flags():
    assert _v({"rmt_closed_form": {"x": 0.5, "d": 0.5, "tau": 0.3, "A": 1.529412}}) == "FLAG"

def test_cxdtau_domain_violation_flags():
    # d must be < 1 + tau
    assert _v({"rmt_closed_form": {"x": 0.5, "d": 1.5, "tau": 0.3, "A": 1.0}}) == "FLAG"

# ---- F(a,b,gamma): rho = a(1-l)/(1 - a b l), l = 1/gamma ; F = ((2/pi) asin rho)^2 ----
def test_F_consistent_square():
    assert _v({"rmt_F": {"a": 0.5, "b": 0.5, "gamma": 2, "rho": 0.2857142857, "F": 0.0340261048}}) == "PASS"

def test_F_consistent_rectangular():
    assert _v({"rmt_F": {"a": 0.75, "b": 0.25, "gamma": 4/3, "rho": 0.2181818182, "F": 0.0196070468}}) == "PASS"

def test_F_gamma_1_is_zero():
    assert _v({"rmt_F": {"a": 0.4, "b": 0.7, "gamma": 1, "rho": 0.0, "F": 0.0}}) == "PASS"

def test_F_without_feedback_flags():
    # rho = a(1-l) (no denominator) -> rho = 0.25, F = 0.025876 at (0.5, 0.5, 2)
    assert _v({"rmt_F": {"a": 0.5, "b": 0.5, "gamma": 2, "rho": 0.25, "F": 0.025876}}) == "FLAG"

# ---- G(a,b,1) = (4/pi^2) a/(1 - a b); a = b = x gives C(x) exactly; a != b is MEASURED ----
def test_G_square_exact():
    assert _v({"rmt_G": {"a": 0.5, "b": 0.5, "gamma": 1, "G": 0.2701898230}}) == "PASS"

def test_G_rectangular_measured_with_se_passes():
    assert _v({"rmt_G": {"a": 0.3, "b": 0.6, "gamma": 1, "G": 0.1482749029, "G_se": 0.002}}) == "PASS"

def test_G_rectangular_without_se_is_HOLD_not_flag():
    assert _v({"rmt_G": {"a": 0.3, "b": 0.6, "gamma": 1, "G": 0.1482749029}}) == "HOLD"

def test_G_square_six_sigma_off_flags():
    # declared 0.30 +/- 0.005 at a = b = 0.5: z = +6 -> FLAG even with SE
    assert _v({"rmt_G": {"a": 0.5, "b": 0.5, "gamma": 1, "G": 0.30, "G_se": 0.005}}) == "FLAG"

# ---- check_sum per spec: k = 4 by default ----
def test_check_sum_default_k_is_4():
    ev = {"parts": [0.1066, 0.124, -0.008], "parts_se": [0.005, 0.005, 0.005], "total": 0.227, "total_se": 0.005}
    assert ci.audit(ev)["results"]["sum"]["tolerance"] > 0.03   # 4*sqrt(4*0.005^2) = 0.04

# ---- audit() surfaces HOLD without turning it into a violation ----
def test_audit_hold_is_not_a_violation():
    a = ci.audit({"rmt_G": {"a": 0.3, "b": 0.6, "gamma": 1, "G": 0.148}})
    assert a["verdict"] == "HOLD" and a["violations"] == [] and "rmt_G" in a.get("holds", [])


# --- Ginibre corpus finding (2026-10-13): a declared C rounded to its reported precision is
#     not a violation; tolerance is half a unit in the last declared digit (or SE if given).
def test_cxd_rounded_C_at_declared_precision_passes():
    # exact C(0.5, d=0.5) = 0.4863416815; declared to 5 significant digits
    assert _v({"rmt_closed_form": {"x": 0.5, "d": 0.5, "C": 0.48634}}) == "PASS"
    assert _v({"rmt_closed_form": {"x": 0.5, "d": 0.5, "C": "0.48634"}}) == "PASS"

def test_cxd_wrong_C_beyond_declared_precision_still_flags():
    assert _v({"rmt_closed_form": {"x": 0.5, "d": 0.5, "C": 0.48700}}) == "FLAG"

def test_cxd_A_not_declared_is_not_a_flag():
    assert _v({"rmt_closed_form": {"x": 0.5, "d": 0.5, "C": 0.4863416815}}) == "PASS"
    assert _v({"rmt_closed_form": {"x": 0.5, "d": 0.5, "A": None, "C": 0.4863416815}}) == "PASS"

def test_rmt_F_rounded_passes():
    assert _v({"rmt_F": {"a": 0.5, "b": 0.5, "gamma": 2, "rho": 0.2857, "F": 0.0340}}) == "PASS"
