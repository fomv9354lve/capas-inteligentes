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
    assert r["verdict"] == "ACCEPT" and r["text_licensed_as_written"] is False and r["licensed_claim"].startswith("[licensed on the declared")


def test_alpha_one_is_not_a_threshold():
    r = _d("Significant.", "statistical_confidence", {"p_value": 0.5, "alpha": 1.0, "effect_direction_confirmed": True})
    assert r["verdict"] == "HOLD"


FULL = dict(claim_kind="confirmatory", asserts_significant=True, p_value=0.01, alpha=0.05, n_comparisons=3, multiplicity_adjustment="holm",
            endpoint_type="primary", prespecified=True, ci_low=0.1, ci_high=0.5, observed_direction="benefit", claimed_direction="benefit")


def test_pharma_empty_evidence_holds():
    assert ph.gate_pharma_stat_claim({})["verdict"] == "HOLD"


def test_pharma_missing_alpha_or_prespecified_holds():
    assert ph.gate_pharma_stat_claim({k: v for k, v in FULL.items() if k != "alpha"})["verdict"] == "HOLD"
    assert ph.gate_pharma_stat_claim({k: v for k, v in FULL.items() if k != "prespecified"})["verdict"] == "HOLD"


def test_pharma_no_adjustment_string_is_unadjusted():
    assert ph.gate_pharma_stat_claim({**FULL, "multiplicity_adjustment": "no"})["verdict"] == "REWRITE"
    assert ph.gate_pharma_stat_claim({**FULL, "multiplicity_adjustment": "maybe"})["verdict"] == "HOLD"
    assert ph.gate_pharma_stat_claim(FULL)["verdict"] == "ACCEPT"
