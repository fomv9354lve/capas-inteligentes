# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""A sum of ESTIMATES must be judged against their stated uncertainty, not as exact accounting."""
import capas_invariants as ci

def test_exact_sum_still_exact():
    assert ci.audit({"parts": [0.107, 0.110, 0.008], "total": 0.225})["verdict"] == "PASS"
    assert ci.audit({"parts": [0.107, 0.110, 0.008], "total": 0.240})["verdict"] == "FLAG"

def test_ginibre_fitted_limits_within_se_pass():
    # 0.1066 + 0.124 - 0.008 = 0.2226 vs declared 0.227; each term has SE ~0.005 -> within noise
    ev = {"parts": [0.1066, 0.124, -0.008], "parts_se": [0.005, 0.005, 0.005],
          "total": 0.227, "total_se": 0.005}
    assert ci.audit(ev)["verdict"] == "PASS"

def test_discrepancy_beyond_k_sigma_flags():
    ev = {"parts": [0.1066, 0.124, -0.008], "parts_se": [0.001, 0.001, 0.001],
          "total": 0.227, "total_se": 0.001}
    assert ci.audit(ev)["verdict"] == "FLAG"

def test_malformed_se_length_flags():
    ev = {"parts": [1, 2], "parts_se": [0.1], "total": 3}
    assert ci.audit(ev)["verdict"] == "FLAG"


def test_rmt_bounds_rho_and_F():
    assert ci.audit({"bounds": {"rho": 0.93}})["verdict"] == "PASS"
    assert ci.audit({"bounds": {"rho": 1.2}})["verdict"] == "FLAG"
    assert ci.audit({"bounds": {"F": 0.31}})["verdict"] == "PASS"
    assert ci.audit({"bounds": {"F": -0.02}})["verdict"] == "FLAG"
