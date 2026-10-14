# SPDX-License-Identifier: Apache-2.0
"""External audit 2026-10-14, items 2–4: the cases the auditor ran, locked as regressions."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import capas, capas_pharma as ph


def _d(text, ct, ev):
    return capas.decide_external_claim({"schema_version": "capas-claim-payload-v3", "claim": {"id": "a", "type": ct, "text": text}, "evidence": ev})


def test_subgroup_to_all_patients_is_not_accepted():
    r = _d("Treatment benefits all patients.", "statistical_confidence", {"p_value": 0.01, "alpha": 0.05, "effect_direction_confirmed": True})
    assert r["verdict"] == "REWRITE"


def test_financial_attribution_is_not_licensed():
    r = _d("Net assets grew 40% and prove the turnaround strategy worked.", "financial_metric_claim",
           {"reported_value": 1000, "reference_value": 1000, "tolerance": 0.5, "metric_period_match": True})
    assert r["verdict"] == "REWRITE"


def test_accept_never_licenses_raw_text():
    r = _d("The biomarker effect is significant in this cohort.", "statistical_confidence", {"p_value": 0.01, "alpha": 0.05, "effect_direction_confirmed": True})
    assert r["verdict"] == "ACCEPT" and r["text_licensed_as_written"] is False and r["licensed_claim"].startswith("Licensed on the declared")
    assert "biomarker" not in r["licensed_claim"]          # the raw sentence is never carried


def test_alpha_one_is_not_a_threshold():
    r = _d("Significant.", "statistical_confidence", {"p_value": 0.5, "alpha": 1.0, "effect_direction_confirmed": True})
    assert r["verdict"] == "HOLD"


FULL = dict(claim_kind="confirmatory", asserts_significant=True, p_value=0.01, alpha=0.05, n_comparisons=3, multiplicity_adjustment="holm",
            endpoint_type="primary", prespecified=True, ci_low=0.1, ci_high=0.5, observed_direction="benefit", claimed_direction="benefit",
            effect_measure="mean_difference", ci_level=0.95, ci_sides=2, p_sides=2)


def test_pharma_empty_evidence_holds():
    assert ph.gate_pharma_stat_claim({})["verdict"] == "HOLD"


def test_pharma_missing_alpha_or_prespecified_holds():
    assert ph.gate_pharma_stat_claim({k: v for k, v in FULL.items() if k != "alpha"})["verdict"] == "HOLD"
    assert ph.gate_pharma_stat_claim({k: v for k, v in FULL.items() if k != "prespecified"})["verdict"] == "HOLD"


def test_pharma_no_adjustment_string_is_unadjusted():
    assert ph.gate_pharma_stat_claim({**FULL, "multiplicity_adjustment": "no"})["verdict"] == "REWRITE"
    assert ph.gate_pharma_stat_claim({**FULL, "multiplicity_adjustment": "maybe"})["verdict"] == "HOLD"
    assert ph.gate_pharma_stat_claim(FULL)["verdict"] == "ACCEPT"


# ---- re-audit 2026-10-14 (pharma)
def test_pharma_ratio_null_is_one():
    hr = {**FULL, "effect_measure": "hr", "ci_low": 0.85, "ci_high": 1.20}
    assert ph.gate_pharma_stat_claim(hr)["verdict"] in ("REJECT", "REWRITE")
    assert ph.gate_pharma_stat_claim({k: v for k, v in FULL.items() if k != "effect_measure"})["verdict"] == "HOLD"


def test_pharma_claim_kind_endpoint_and_count_are_validated():
    assert ph.gate_pharma_stat_claim({**FULL, "claim_kind": "Confirmatory"})["verdict"] == "HOLD"
    assert ph.gate_pharma_stat_claim({**FULL, "claim_kind": "exploratory"})["verdict"] == "HOLD"
    assert ph.gate_pharma_stat_claim({**FULL, "endpoint_type": "key secondary"})["verdict"] == "HOLD"
    assert ph.gate_pharma_stat_claim({**FULL, "n_comparisons": "5"})["verdict"] == "HOLD"


def test_pharma_confirmatory_must_assert_something_and_direction_none_is_caught():
    assert ph.gate_pharma_stat_claim({**FULL, "asserts_significant": False, "p_value": 0.9})["verdict"] == "REWRITE"
    assert ph.gate_pharma_stat_claim({**FULL, "observed_direction": "none"})["verdict"] == "REWRITE"


# ---- re-audit 2026-10-14 (text variants): the fixed pattern list, closed by construction, downgrade-only
import pytest
SC = {"p_value": 0.01, "alpha": 0.05, "effect_direction_confirmed": True}
FIN = {"reported_value": 1000, "reference_value": 1000, "tolerance": 0.5, "metric_period_match": True}


@pytest.mark.parametrize("t", ["The treatment benefits everyone.", "Works regardless of subgroup.", "Effective in 100% of patients.",
                               "The drug leads to recovery.", "The program drives retention.", "The vaccine eliminates infection.",
                               "The treatment causes the improvement."])
def test_statistical_text_variants_are_not_accepted(t):
    assert _d(t, "statistical_confidence", SC)["verdict"] == "REWRITE"


@pytest.mark.parametrize("t", ["The numbers show the strategy succeeded.", "Net assets match in all future periods."])
def test_financial_text_variants_are_not_accepted(t):
    assert _d(t, "financial_metric_claim", FIN)["verdict"] == "REWRITE"


def test_no_type_carries_the_raw_sentence_on_accept():
    r = _d("Artifact reproduced by an independent lab.", "reproducibility_check", {"artifact_available": True, "independent_reproduction_pass": True})
    assert r["verdict"] == "ACCEPT" and "independent lab" not in r["licensed_claim"]


# ---- re-audit 3 (pharma)
def test_pharma_descriptive_accept_is_not_confirmatory():
    r = ph.gate_pharma_stat_claim({"claim_kind": "descriptive", "asserts_significant": False, "alpha": 0.05, "prespecified": False, "multiplicity_adjustment": "none"})
    assert r["licensed_reuse"] != "confirmatory efficacy"


def test_pharma_effect_without_significance_and_incoherent_p_ci():
    r = ph.gate_pharma_stat_claim({**FULL, "asserts_significant": False, "asserts_effect": True, "p_value": 0.9, "effect_measure": "hr", "ci_low": 0.6, "ci_high": 0.9})
    assert r["verdict"] != "ACCEPT"
    r = ph.gate_pharma_stat_claim({**FULL, "p_value": 0.2})                      # 95% CI excludes 0 but p = 0.2 > 0.05
    assert r["verdict"] == "REJECT"


def test_pharma_p_range():
    assert ph.gate_pharma_stat_claim({**FULL, "p_value": -0.1})["verdict"] == "HOLD"
    assert ph.gate_pharma_stat_claim({**FULL, "p_value": 1.5})["verdict"] == "HOLD"


def test_home_script_runs_from_a_fresh_clone():
    import subprocess, os
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    r = subprocess.run([sys.executable, "-I", str(ROOT / "benchmarks" / "home_gate_decisions.py")], capture_output=True, text=True, cwd="/", env=env, timeout=120)
    assert r.returncode == 0, r.stderr[-300:]


# ---- re-audit 4: p and CI compared at the declared level; boundary -> HOLD, never REJECT
def test_pharma_alpha_differs_from_ci_level_is_not_reject():
    r = ph.gate_pharma_stat_claim({**FULL, "alpha": 0.01, "p_value": 0.03, "effect_measure": "hr", "ci_low": 0.60, "ci_high": 0.95,
                                   "asserts_significant": False, "asserts_effect": True})
    assert r["verdict"] == "REWRITE"


def test_pharma_boundary_is_hold_not_reject():
    r = ph.gate_pharma_stat_claim({**FULL, "p_value": 0.049, "effect_measure": "hr", "ci_low": 1.00, "ci_high": 1.45})
    assert r["verdict"] == "HOLD"


def test_pharma_undeclared_level_or_sides_is_hold():
    assert ph.gate_pharma_stat_claim({k: v for k, v in FULL.items() if k != "ci_level"})["verdict"] == "HOLD"
    assert ph.gate_pharma_stat_claim({**FULL, "ci_sides": 1})["verdict"] == "HOLD"
