# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""Rule (b) from the Ginibre X4 post-mortem: when abs_error is the MAXIMUM pull over k cells in SE
units, a fixed 2-SE tolerance is a max-test without multiplicity correction (k=6: P(max|z|>2) ~ 0.24
under the exact law). Sidak-correct the SE tolerance when the coder DECLARES error_statistic="max"
and n_cells; absent the declaration the engine keeps judging a single cell (X4 untouched).
Reference values from Ginibre (alpha = 2(1-Phi(t)), alpha' = 1-(1-alpha)^(1/k), t_k = Phi^-1(1-alpha'/2))."""
import json
import pytest
import capas

def _ev(abs_error, k=None, stat=None, tol=2.0, unit="SE", nrep=40):
    e = {"abs_error": abs_error, "tolerance": tol, "tolerance_unit": unit, "n_replicates": nrep}
    if k is not None: e["n_cells"] = k
    if stat is not None: e["error_statistic"] = stat
    return {"schema_version": capas.CAPAS_CLAIM_SCHEMA_VERSION,
            "claim": {"id": "t", "type": "exact_model_solution", "text": "F(a,b) matches the closed form within 2 SE."},
            "evidence": e}

@pytest.mark.parametrize("k,tk", [(1, 2.000), (4, 2.525), (6, 2.664), (12, 2.888)])
def test_sidak_reference_values(k, tk):
    assert round(capas.sidak_tolerance(2.0, k), 3) == tk

def test_max_over_6_cells_at_2p3_se_accepts_with_corrected_tolerance():
    d = capas.decide_external_claim(_ev(2.3, k=6, stat="max"))
    assert d["verdict"] == "ACCEPT" and "2.664" in d["reason"] and "Sidak" in d["reason"]

def test_without_error_statistic_k6_still_judges_at_2():
    d = capas.decide_external_claim(_ev(2.3, k=6))
    assert d["verdict"] == "REJECT" and "2.664" not in d["reason"]

def test_x4_026_is_not_rescued_by_b_alone():
    # 2.84 > 2.664: the multiplicity correction alone does not rescue X4-026 (rule (a), chi2/dof, would)
    assert capas.decide_external_claim(_ev(2.84, k=6, stat="max"))["verdict"] == "REJECT"

def test_rms_or_single_statistic_gets_no_correction():
    assert capas.decide_external_claim(_ev(2.3, k=6, stat="rms"))["verdict"] == "REJECT"
    assert capas.decide_external_claim(_ev(2.3, k=6, stat="single"))["verdict"] == "REJECT"

def test_absolute_units_get_no_correction():
    assert capas.decide_external_claim(_ev(2.3, k=6, stat="max", unit="absolute"))["verdict"] == "REJECT"

def test_max_without_n_cells_holds():
    d = capas.decide_external_claim(_ev(2.3, stat="max"))
    assert d["verdict"] == "HOLD" and "n_cells" in d["reason"]

def test_unknown_error_statistic_is_rejected_by_validation():
    d = capas.decide_external_claim(_ev(0.5, k=6, stat="median"))
    assert d["verdict"] == "HOLD" and "error_statistic" in json.dumps(d)  # schema errors are HOLD in this engine
