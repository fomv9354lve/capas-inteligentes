from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "outputs" / "capas_product_demo_report.json"
MARKDOWN = ROOT / "outputs" / "capas_product_demo_report.md"


def main() -> int:
    proc = subprocess.run([sys.executable, "capas.py", "demo"], cwd=ROOT)
    if proc.returncode != 0:
        return proc.returncode

    if not REPORT.exists():
        raise AssertionError(f"missing {REPORT}")
    if not MARKDOWN.exists():
        raise AssertionError(f"missing {MARKDOWN}")

    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["demo_verdict"] == "PASS"
    assert report["fine_tune_ready"] is False
    assert report["claim_gate_summary"]["checks"] == 69
    assert report["claim_gate_summary"]["passed"] == 69
    assert report["claim_gate_summary"]["failed"] == 0

    verdicts = {check["actual_verdict"] for check in report["claim_examples"]}
    assert verdicts == {"ACCEPT", "REWRITE", "REJECT", "HOLD"}

    matrix = report["universal_anchor_matrix"]
    assert matrix["matrix_status"] == "passed"
    assert matrix["licensed_claim"] == "complementarity_not_dominance"
    assert matrix["cell_counts"]["local_miss_anchor_catch"] >= 1
    assert matrix["cell_counts"]["local_catch_anchor_not_needed"] >= 1
    assert matrix["cell_counts"]["both_catch"] >= 1
    assert matrix["cell_counts"]["both_pass"] >= 1
    assert matrix["cell_counts"]["no_anchor_control"] >= 1

    trace = report["motor_backed_trace"]
    assert trace["trace_id"] == "trace_039"
    assert trace["physical_evidence_level"] == "scaling_law_anchor"
    assert trace["anchor_mode"] == "absolute_anchor"
    assert trace["local_property_tests_pass"] is True
    assert trace["universal_anchor_pass"] is True
    assert trace["upgrade_evidence_present"] is True

    text = MARKDOWN.read_text(encoding="utf-8")
    assert "CAPAS Product Demo Report" in text
    assert "complementarity_not_dominance" in text
    assert "fine_tune_ready: `False`" in text

    print("verify_capas_product_demo passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
