from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "outputs"
CLAIM_REPORT = ROOT / "benchmarks" / "evidence_claim_validation_report.json"
ANCHOR_REPORT = ROOT / "benchmarks" / "universal_anchor_matrix_report.json"
TRACE_DIR = ROOT / "benchmarks" / "gold_traces"


VALIDATION_COMMANDS = [
    ("claim gate", ["benchmarks/validate_evidence_claims.py"]),
    ("universal anchor matrix", ["benchmarks/validate_universal_anchor_matrix.py"]),
    ("CAPAS profile", ["benchmarks/validate_capas_profile.py"]),
    ("RO-Crate coverage", ["benchmarks/validate_ro_crates.py"]),
]


EXAMPLE_KEYS = [
    ("ACCEPT", "trace_039", "claim_transition_gate"),
    ("REWRITE", "debunk10_gpt3_fewshot", "gpt3_implies_agi_or_reliable_reasoner"),
    ("REJECT", "debunk10_retracted_superconductor", "room_temp_superconductor_established"),
    ("HOLD", "regional_cono_sur_ambiguous_experiment", "matches_experiment"),
]


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _claim_checks(report: dict[str, Any]) -> list[dict[str, Any]]:
    checks = report.get("checks", [])
    if not isinstance(checks, list):
        raise ValueError(f"{CLAIM_REPORT} has no checks list")
    return checks


def _find_check(checks: list[dict[str, Any]], trace_id: str, claim_id: str) -> dict[str, Any]:
    for check in checks:
        if check.get("trace_id") == trace_id and check.get("claim_id") == claim_id:
            return check
    raise ValueError(f"missing claim check {trace_id}::{claim_id}")


def _trace_summary(trace_id: str) -> dict[str, Any]:
    payload = _load_json(TRACE_DIR / f"{trace_id}.json")
    result = payload["result"]["result"]
    return {
        "trace_id": trace_id,
        "coverage_case": payload.get("coverage_case"),
        "physical_evidence_level": result.get("physical_evidence_level"),
        "verification_independence": result.get("verification_independence"),
        "anchor_mode": result.get("anchor_mode"),
        "local_property_tests_pass": result.get("local_property_tests_pass"),
        "universal_anchor_pass": result.get("universal_anchor_pass"),
        "claim_scope": result.get("claim_scope"),
        "attempted_claim": result.get("attempted_claim"),
        "current_claim": result.get("current_claim"),
        "upgrade_evidence_present": result.get("upgrade_evidence_present"),
    }


def build_demo_report() -> dict[str, Any]:
    claim_report = _load_json(CLAIM_REPORT)
    anchor_report = _load_json(ANCHOR_REPORT)
    checks = _claim_checks(claim_report)
    verdict_counts = Counter(check["actual_verdict"] for check in checks)
    examples = []
    for expected, trace_id, claim_id in EXAMPLE_KEYS:
        check = _find_check(checks, trace_id, claim_id)
        if check.get("actual_verdict") != expected:
            raise AssertionError(
                f"{trace_id}::{claim_id} expected {expected}, got {check.get('actual_verdict')}"
            )
        examples.append(check)

    trace_039 = _trace_summary("trace_039")
    allowed_claim = anchor_report["allowed_claim"]
    forbidden_claims = anchor_report["forbidden_claims"]
    matrix_status = anchor_report["matrix_status"]
    licensed_claim = anchor_report["licensed_claim"]
    cell_counts = anchor_report["cell_counts"]

    return {
        "product_name": "CAPAS Claim Gate",
        "product_claim": (
            "CAPAS turns scientific computation traces into evidence-typed claim "
            "decisions: ACCEPT, REWRITE, REJECT, or HOLD."
        ),
        "non_claims": [
            "does not prove AGI or broad reliable LLM reasoning",
            "does not replace Metamorphic Testing or local/property checks",
            "does not make fine-tune data ready without blind inference review",
            "does not certify physical truth when evidence is none/estimated/failed",
        ],
        "claim_gate_summary": claim_report["summary"],
        "claim_verdict_counts": dict(sorted(verdict_counts.items())),
        "claim_examples": examples,
        "universal_anchor_matrix": {
            "matrix_status": matrix_status,
            "licensed_claim": licensed_claim,
            "cell_counts": cell_counts,
            "allowed_claim": allowed_claim,
            "forbidden_claims": forbidden_claims,
        },
        "motor_backed_trace": trace_039,
        "fine_tune_ready": False,
        "demo_verdict": "PASS",
    }


def _render_markdown(report: dict[str, Any]) -> str:
    examples = "\n".join(
        "- `{actual_verdict}` `{trace_id}::{claim_id}`: {reason}".format(**check)
        for check in report["claim_examples"]
    )
    cells = "\n".join(
        f"- `{cell}`: {count}"
        for cell, count in report["universal_anchor_matrix"]["cell_counts"].items()
    )
    forbidden = "\n".join(
        f"- {claim}" for claim in report["universal_anchor_matrix"]["forbidden_claims"]
    )
    trace = report["motor_backed_trace"]
    return f"""# CAPAS Product Demo Report

Status: `{report['demo_verdict']}`

## Product

{report['product_claim']}

## Claim Gate Summary

- checks: `{report['claim_gate_summary']['checks']}`
- passed: `{report['claim_gate_summary']['passed']}`
- failed: `{report['claim_gate_summary']['failed']}`
- verdict counts: `{report['claim_verdict_counts']}`
- fine_tune_ready: `{report['fine_tune_ready']}`

## Decision Examples

{examples}

## Universal Anchor Matrix

- matrix status: `{report['universal_anchor_matrix']['matrix_status']}`
- licensed claim: `{report['universal_anchor_matrix']['licensed_claim']}`

{cells}

Allowed claim:

> {report['universal_anchor_matrix']['allowed_claim']}

Forbidden claims:

{forbidden}

## Motor-Backed Positive Control

- trace: `{trace['trace_id']}`
- coverage: `{trace['coverage_case']}`
- current claim: `{trace['current_claim']}`
- attempted claim: `{trace['attempted_claim']}`
- physical evidence: `{trace['physical_evidence_level']}`
- anchor mode: `{trace['anchor_mode']}`
- local checks pass: `{trace['local_property_tests_pass']}`
- universal anchor pass: `{trace['universal_anchor_pass']}`
- upgrade evidence present: `{trace['upgrade_evidence_present']}`
- scope: {trace['claim_scope']}

## Non-Claims

{chr(10).join(f"- {item}" for item in report['non_claims'])}
"""


def cmd_demo(args: argparse.Namespace) -> int:
    report = build_demo_report()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = OUT_DIR / "capas_product_demo_report.json"
    md_path = OUT_DIR / "capas_product_demo_report.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(_render_markdown(report), encoding="utf-8")
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"CAPAS product demo: {report['demo_verdict']}")
        print(f"claim checks: {report['claim_gate_summary']['passed']}/{report['claim_gate_summary']['checks']}")
        print(f"D11 licensed claim: {report['universal_anchor_matrix']['licensed_claim']}")
        print(f"wrote {json_path}")
        print(f"wrote {md_path}")
    return 0


def cmd_validate(_: argparse.Namespace) -> int:
    for label, command in VALIDATION_COMMANDS:
        print(f"\n=== {label} ===")
        proc = subprocess.run([sys.executable, *command], cwd=ROOT)
        if proc.returncode:
            return proc.returncode
    print("\nCAPAS product validation passed")
    return 0


def cmd_inspect(args: argparse.Namespace) -> int:
    trace = _trace_summary(args.trace_id)
    print(json.dumps(trace, indent=2, sort_keys=True))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="CAPAS evidence-typed scientific claim gate")
    subparsers = parser.add_subparsers(dest="command", required=True)

    demo = subparsers.add_parser("demo", help="write and print the product demo report")
    demo.add_argument("--json", action="store_true", help="print the full JSON report")
    demo.set_defaults(func=cmd_demo)

    validate = subparsers.add_parser("validate", help="run product validation gates")
    validate.set_defaults(func=cmd_validate)

    inspect = subparsers.add_parser("inspect", help="print a trace summary")
    inspect.add_argument("trace_id", help="trace id such as trace_039")
    inspect.set_defaults(func=cmd_inspect)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
