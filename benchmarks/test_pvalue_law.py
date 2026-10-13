# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""statcheck as a CAPAS law: a reported p must be the p its own test statistic implies."""
import capas_invariants as ci

def _ev(stat, df1, value, p, op="=", df2=None):
    return {"pvalue_test": {"stat": stat, "df1": df1, "df2": df2, "value": value, "op": op, "p": p}}

def test_consistent_t_passes():
    # t(28) = 2.05 -> two-sided p = .0498
    assert ci.audit(_ev("t", 28, 2.05, 0.05))["verdict"] == "PASS"

def test_inconsistent_t_flags():
    # t(28) = 1.20 -> p = .24, NOT .03
    assert ci.audit(_ev("t", 28, 1.20, 0.03))["verdict"] == "FLAG"

def test_decision_error_across_05_flags():
    # F(1,50)=3.90 -> p=.054 ; reporting p<.05 crosses the threshold -> FLAG
    assert ci.audit(_ev("F", 1, 3.90, 0.05, op="<", df2=50))["verdict"] == "FLAG"

def test_inequality_consistent_passes():
    # chi2(1)=10.83 -> p=.001 ; reported p<.01 holds
    assert ci.audit(_ev("chi2", 1, 10.83, 0.01, op="<"))["verdict"] == "PASS"

def test_rounding_tolerance_passes():
    # t(100)=1.98 -> p=.0505 ; reported p=.05 within reporting precision
    assert ci.audit(_ev("t", 100, 1.98, 0.05))["verdict"] == "PASS"

def test_missing_block_does_not_apply():
    assert ci.audit({"grim": {"mean": 2.5, "n": 4}})["laws_checked"] == ["grim"] or "pvalue_test" not in ci.audit({})["laws_checked"]


def test_percent_consistent_passes():
    assert ci.audit({"reported_percent": {"k": 23, "N": 51, "pct": 45.1}})["verdict"] == "PASS"

def test_percent_inconsistent_flags():
    assert ci.audit({"reported_percent": {"k": 23, "N": 51, "pct": 52.0}})["verdict"] == "FLAG"

def test_percent_k_exceeds_N_flags():
    assert ci.audit({"reported_percent": {"k": 60, "N": 51, "pct": 117.6}})["verdict"] == "FLAG"
