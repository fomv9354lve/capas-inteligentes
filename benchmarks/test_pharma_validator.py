# SPDX-License-Identifier: Apache-2.0
"""PLAN_v3 A3c: pharma validator-report adapter. Technical rejection precedes review; form before statistics."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "benchmarks"))
import capas_ingest, capas_pharma  # noqa: E402
from test_audit_2026_10_14 import FULL  # noqa: E402

CSV_REJECT = (ROOT / "examples" / "pharma_validator_report_sample.csv").read_text()
CSV_WARN = "Source,Pinnacle 21 ID,Message,Severity,Found\nAE,SD1201,AESTDTC after AEENDTC,Warning,5\n"


def test_sample_report_parses_with_its_hash():
    r = capas_ingest.validator_report(CSV_REJECT, source_label="sample")
    assert r["counts"] == {"error": 1, "warning": 1, "reject": 1}
    assert len(r["source"]["input_sha256"]) == 64


def test_technical_rejection_precedes_statistics():
    out = capas_pharma.decide_with_validator(dict(FULL), capas_ingest.validator_report(CSV_REJECT))
    assert out["verdict"] == "REJECT" and out["stage"] == "conformance" and "technical rejection" in out["why"]


def test_validator_error_holds():
    rep = capas_ingest.validator_report("Rule ID,Message,Severity\nSD0083,Duplicate USUBJID,Error\n")
    assert capas_pharma.decide_with_validator(dict(FULL), rep)["verdict"] == "HOLD"


def test_unknown_severity_holds_and_no_report_holds():
    rep = capas_ingest.validator_report("Rule ID,Message,Severity\nX1,odd,Critical-ish\n")
    assert capas_pharma.decide_with_validator(dict(FULL), rep)["verdict"] == "HOLD"
    assert capas_pharma.decide_with_validator(dict(FULL), None)["verdict"] == "HOLD"


def test_warnings_only_hand_over_to_the_statistical_gate():
    rep = capas_ingest.validator_report(CSV_WARN)
    out = capas_pharma.decide_with_validator(dict(FULL), rep)
    assert out["verdict"] == capas_pharma.decide(dict(FULL))["verdict"]
    assert out["notices"] and out["validator_sha256"] == rep["source"]["input_sha256"]


def test_report_never_raises_a_verdict():
    bad = {**FULL, "p_value": 0.2}
    assert capas_pharma.decide(bad)["verdict"] != "ACCEPT"
    assert capas_pharma.decide_with_validator(bad, capas_ingest.validator_report(CSV_WARN))["verdict"] != "ACCEPT"


def test_no_severity_column_is_refused():
    import pytest
    with pytest.raises(ValueError):
        capas_ingest.validator_report("Rule ID,Message\nX,y\n")
