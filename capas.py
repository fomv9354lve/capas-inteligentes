from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any


def _discover_root() -> Path:
    if os.environ.get("CAPAS_ROOT"):
        return Path(os.environ["CAPAS_ROOT"]).resolve()
    cwd = Path.cwd().resolve()
    if (cwd / "benchmarks" / "evidence_claim_validation_report.json").exists():
        return cwd
    return Path(__file__).resolve().parent


ROOT = _discover_root()
OUT_DIR = ROOT / "outputs"
CLAIM_REPORT = ROOT / "benchmarks" / "evidence_claim_validation_report.json"
ANCHOR_REPORT = ROOT / "benchmarks" / "universal_anchor_matrix_report.json"
TRACE_DIR = ROOT / "benchmarks" / "gold_traces"
EXTERNAL_CLAIM_SCHEMA_PATH = ROOT / "docs" / "schema" / "capas_claim_payload.schema.json"


VALIDATION_COMMANDS = [
    ("external input schema", ["benchmarks/verify_external_input_schema.py"]),
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

REQUIRED_DECISION_FIELDS = {
    "exact_model_solution": ["abs_error", "tolerance"],
    "physical_accuracy": ["within_chemical_accuracy"],
    "universal_anchor_claim": ["anchor_mode", "local_property_tests_pass", "universal_anchor_pass"],
    "claim_transition": ["upgrade_evidence_present"],
}


def external_claim_payload_schema() -> dict[str, Any]:
    claim_types = sorted(REQUIRED_DECISION_FIELDS)
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://capas.local/schema/capas_claim_payload.schema.json",
        "title": "CAPAS external claim/evidence payload",
        "type": "object",
        "additionalProperties": True,
        "required": ["claim", "evidence"],
        "properties": {
            "claim": {
                "type": "object",
                "additionalProperties": True,
                "required": ["id", "type", "text"],
                "properties": {
                    "id": {"type": "string", "minLength": 1},
                    "type": {"type": "string", "enum": claim_types},
                    "text": {"type": "string", "minLength": 1},
                },
            },
            "evidence": {
                "type": "object",
                "additionalProperties": True,
                "description": "Evidence fields are claim-type dependent; unsupported or missing evidence yields HOLD.",
                "properties": {
                    "abs_error": {"type": "number"},
                    "tolerance": {"type": "number"},
                    "within_chemical_accuracy": {"type": "boolean"},
                    "anchor_mode": {"type": "string"},
                    "local_property_tests_pass": {"type": "boolean"},
                    "universal_anchor_pass": {"type": "boolean"},
                    "upgrade_evidence_present": {"type": "boolean"},
                    "physical_evidence_level": {"type": "string"},
                    "verification_independence": {"type": "string"},
                    "reference_truth": {},
                    "current_claim": {"type": "string"},
                },
            },
        },
    }


def validate_external_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["payload must be a JSON object"]
    claim = payload.get("claim")
    evidence = payload.get("evidence")
    if not isinstance(claim, dict):
        errors.append("claim must be an object")
        claim = {}
    if not isinstance(evidence, dict):
        errors.append("evidence must be an object")
        evidence = {}

    for field in ("id", "type", "text"):
        value = claim.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"claim.{field} must be a non-empty string")

    claim_type = claim.get("type")
    if isinstance(claim_type, str) and claim_type not in REQUIRED_DECISION_FIELDS:
        errors.append(
            "claim.type must be one of: "
            + ", ".join(sorted(REQUIRED_DECISION_FIELDS))
        )

    numeric_fields = ["abs_error", "tolerance"]
    for field in numeric_fields:
        if field in evidence and not isinstance(evidence[field], (int, float)):
            errors.append(f"evidence.{field} must be a number")

    bool_fields = [
        "within_chemical_accuracy",
        "local_property_tests_pass",
        "universal_anchor_pass",
        "upgrade_evidence_present",
    ]
    for field in bool_fields:
        if field in evidence and not isinstance(evidence[field], bool):
            errors.append(f"evidence.{field} must be a boolean")

    if "anchor_mode" in evidence and not isinstance(evidence["anchor_mode"], str):
        errors.append("evidence.anchor_mode must be a string")
    return errors


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


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


def decide_external_claim(payload: dict[str, Any]) -> dict[str, Any]:
    """Decide a user-supplied claim against explicit evidence fields.

    This is intentionally small and transparent. It is the external product
    surface, not a hidden judge: unsupported claim types HOLD instead of being
    inferred heuristically.
    """

    schema_errors = validate_external_payload(payload)
    claim = payload.get("claim", {}) if isinstance(payload, dict) else {}
    evidence = payload.get("evidence", {}) if isinstance(payload, dict) else {}
    if schema_errors:
        return {
            "input_claim": claim if isinstance(claim, dict) else {},
            "verdict": "HOLD",
            "reason": "input payload failed CAPAS schema validation",
            "licensed_claim": claim.get("text") if isinstance(claim, dict) else None,
            "rewrite": None,
            "missing_fields": [],
            "required_fields": [],
            "schema_errors": schema_errors,
            "fine_tune_ready": False,
            "non_claim": "This decision is rule-based over supplied evidence fields, not an LLM judgment.",
        }

    claim_type = claim.get("type")
    required = REQUIRED_DECISION_FIELDS.get(str(claim_type))
    missing = [
        field
        for field in (required or [])
        if field not in evidence or evidence.get(field) in {None, "unknown"}
    ]

    verdict = "HOLD"
    reason = "unsupported claim type or missing evidence"
    licensed_claim = claim.get("text")
    rewrite = None

    if required is None:
        reason = f"unsupported claim type {claim_type!r}; no rule was applied"
    elif missing:
        reason = f"missing required evidence fields: {missing}"
    elif claim_type == "exact_model_solution":
        abs_error = float(evidence["abs_error"])
        tolerance = float(evidence["tolerance"])
        if abs_error <= tolerance:
            verdict = "ACCEPT"
            reason = f"abs_error {abs_error} <= tolerance {tolerance}"
        else:
            verdict = "REJECT"
            reason = f"abs_error {abs_error} > tolerance {tolerance}"
    elif claim_type == "physical_accuracy":
        if evidence["within_chemical_accuracy"] is True:
            verdict = "ACCEPT"
            reason = "within_chemical_accuracy is true"
        else:
            verdict = "REJECT"
            reason = "within_chemical_accuracy is false"
    elif claim_type == "universal_anchor_claim":
        local_pass = evidence["local_property_tests_pass"] is True
        anchor_pass = evidence["universal_anchor_pass"] is True
        if evidence["anchor_mode"] != "absolute_anchor":
            verdict = "HOLD"
            reason = "claim requires an absolute_anchor, but evidence has another anchor mode"
        elif local_pass and anchor_pass:
            verdict = "ACCEPT"
            reason = "local checks and universal anchor both pass"
        elif local_pass and not anchor_pass:
            verdict = "REWRITE"
            reason = "local checks pass, but the universal anchor fails"
            rewrite = "local plausibility only; universal physical correctness is not licensed"
            licensed_claim = rewrite
        else:
            verdict = "REJECT"
            reason = "local checks fail before the universal-anchor claim is licensed"
    elif claim_type == "claim_transition":
        if evidence["upgrade_evidence_present"] is True:
            verdict = "ACCEPT"
            reason = "upgrade evidence is explicitly present"
        else:
            verdict = "REWRITE"
            reason = "upgrade evidence is absent; stronger claim is not licensed"
            rewrite = evidence.get("current_claim", "weaker current claim only")
            licensed_claim = rewrite

    return {
        "input_claim": claim,
        "verdict": verdict,
        "reason": reason,
        "licensed_claim": licensed_claim,
        "rewrite": rewrite,
        "missing_fields": missing,
        "required_fields": required or [],
        "schema_errors": [],
        "fine_tune_ready": False,
        "non_claim": "This decision is rule-based over supplied evidence fields, not an LLM judgment.",
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


def _sample_external_claim() -> dict[str, Any]:
    return {
        "claim": {
            "id": "sample_scaling_claim",
            "type": "universal_anchor_claim",
            "text": "The generated scaling result is physically consistent with the universal z=1 anchor.",
        },
        "evidence": {
            "anchor_mode": "absolute_anchor",
            "local_property_tests_pass": True,
            "universal_anchor_pass": True,
            "physical_evidence_level": "scaling_law_anchor",
            "verification_independence": "theory_scaling_law_no_solver",
        },
    }


def _render_ui(sample: dict[str, Any]) -> str:
    sample_json = json.dumps(sample, indent=2, sort_keys=True)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>CAPAS Claim Gate</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 32px; max-width: 1120px; }}
    textarea {{ width: 100%; min-height: 360px; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 13px; }}
    pre {{ background: #f5f5f5; padding: 16px; overflow: auto; }}
    button {{ padding: 8px 12px; margin: 8px 8px 8px 0; }}
    .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }}
    @media (max-width: 800px) {{ .grid {{ grid-template-columns: 1fr; }} }}
  </style>
</head>
<body>
  <h1>CAPAS Claim Gate</h1>
  <p>Paste a claim/evidence JSON object. This static UI mirrors the small external rule gate in <code>capas.py decide</code>.</p>
  <div class="grid">
    <section>
      <h2>Input</h2>
      <textarea id="input">{sample_json}</textarea>
      <button onclick="decide()">Decide</button>
      <button onclick="resetSample()">Reset sample</button>
    </section>
    <section>
      <h2>Decision</h2>
      <pre id="output"></pre>
    </section>
  </div>
  <script>
    const sample = {json.dumps(sample)};
    const required = {{
      exact_model_solution: ["abs_error", "tolerance"],
      physical_accuracy: ["within_chemical_accuracy"],
      universal_anchor_claim: ["anchor_mode", "local_property_tests_pass", "universal_anchor_pass"],
      claim_transition: ["upgrade_evidence_present"]
    }};
    function rule(payload) {{
      const claim = payload.claim || {{}};
      const evidence = payload.evidence || {{}};
      const fields = required[claim.type];
      let missing = [];
      if (fields) {{
        missing = fields.filter((field) => evidence[field] === undefined || evidence[field] === null || evidence[field] === "unknown");
      }}
      let result = {{
        input_claim: claim,
        verdict: "HOLD",
        reason: "unsupported claim type or missing evidence",
        licensed_claim: claim.text,
        rewrite: null,
        missing_fields: missing,
        required_fields: fields || [],
        fine_tune_ready: false,
        non_claim: "This decision is rule-based over supplied evidence fields, not an LLM judgment."
      }};
      if (!fields) {{
        result.reason = `unsupported claim type ${{claim.type}}; no rule was applied`;
      }} else if (missing.length) {{
        result.reason = `missing required evidence fields: ${{missing.join(", ")}}`;
      }} else if (claim.type === "exact_model_solution") {{
        result.verdict = Number(evidence.abs_error) <= Number(evidence.tolerance) ? "ACCEPT" : "REJECT";
        result.reason = `abs_error ${{evidence.abs_error}} vs tolerance ${{evidence.tolerance}}`;
      }} else if (claim.type === "physical_accuracy") {{
        result.verdict = evidence.within_chemical_accuracy === true ? "ACCEPT" : "REJECT";
        result.reason = `within_chemical_accuracy is ${{evidence.within_chemical_accuracy}}`;
      }} else if (claim.type === "universal_anchor_claim") {{
        if (evidence.anchor_mode !== "absolute_anchor") {{
          result.verdict = "HOLD";
          result.reason = "claim requires an absolute_anchor, but evidence has another anchor mode";
        }} else if (evidence.local_property_tests_pass === true && evidence.universal_anchor_pass === true) {{
          result.verdict = "ACCEPT";
          result.reason = "local checks and universal anchor both pass";
        }} else if (evidence.local_property_tests_pass === true && evidence.universal_anchor_pass !== true) {{
          result.verdict = "REWRITE";
          result.reason = "local checks pass, but the universal anchor fails";
          result.rewrite = "local plausibility only; universal physical correctness is not licensed";
          result.licensed_claim = result.rewrite;
        }} else {{
          result.verdict = "REJECT";
          result.reason = "local checks fail before the universal-anchor claim is licensed";
        }}
      }} else if (claim.type === "claim_transition") {{
        if (evidence.upgrade_evidence_present === true) {{
          result.verdict = "ACCEPT";
          result.reason = "upgrade evidence is explicitly present";
        }} else {{
          result.verdict = "REWRITE";
          result.reason = "upgrade evidence is absent; stronger claim is not licensed";
          result.rewrite = evidence.current_claim || "weaker current claim only";
          result.licensed_claim = result.rewrite;
        }}
      }}
      return result;
    }}
    function decide() {{
      try {{
        const payload = JSON.parse(document.getElementById("input").value);
        document.getElementById("output").textContent = JSON.stringify(rule(payload), null, 2);
      }} catch (error) {{
        document.getElementById("output").textContent = String(error);
      }}
    }}
    function resetSample() {{
      document.getElementById("input").value = JSON.stringify(sample, null, 2);
      decide();
    }}
    decide();
  </script>
</body>
</html>
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


def cmd_decide(args: argparse.Namespace) -> int:
    payload = _load_json(Path(args.input))
    decision = decide_external_claim(payload)
    if args.output:
        _write_json(Path(args.output), decision)
    if args.json or not args.output:
        print(json.dumps(decision, indent=2, sort_keys=True))
    else:
        print(f"{decision['verdict']}: {decision['reason']}")
        print(f"wrote {args.output}")
    return 0


def cmd_schema(args: argparse.Namespace) -> int:
    schema = external_claim_payload_schema()
    if args.output:
        _write_json(Path(args.output), schema)
        print(f"wrote {args.output}")
    else:
        print(json.dumps(schema, indent=2, sort_keys=True))
    return 0


def cmd_check_input(args: argparse.Namespace) -> int:
    payload = _load_json(Path(args.input))
    errors = validate_external_payload(payload)
    result = {
        "input": args.input,
        "valid": not errors,
        "errors": errors,
        "schema": "docs/schema/capas_claim_payload.schema.json",
    }
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif errors:
        print(f"INVALID: {args.input}")
        for error in errors:
            print(f"- {error}")
    else:
        print(f"VALID: {args.input}")
    return 0 if not errors else 1


def cmd_ui(args: argparse.Namespace) -> int:
    sample = _sample_external_claim()
    path = Path(args.output) if args.output else OUT_DIR / "capas_claim_gate_ui.html"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_render_ui(sample), encoding="utf-8")
    print(f"wrote {path}")
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

    decide = subparsers.add_parser("decide", help="decide an external claim/evidence JSON file")
    decide.add_argument("--input", required=True, help="path to claim/evidence JSON")
    decide.add_argument("--output", help="optional path for decision JSON")
    decide.add_argument("--json", action="store_true", help="print JSON even when --output is supplied")
    decide.set_defaults(func=cmd_decide)

    schema = subparsers.add_parser("schema", help="print or write the external claim/evidence JSON schema")
    schema.add_argument("--output", help="optional schema output path")
    schema.set_defaults(func=cmd_schema)

    check_input = subparsers.add_parser("check-input", help="validate an external claim/evidence JSON file")
    check_input.add_argument("--input", required=True, help="path to claim/evidence JSON")
    check_input.add_argument("--json", action="store_true", help="print machine-readable validation result")
    check_input.set_defaults(func=cmd_check_input)

    ui = subparsers.add_parser("ui", help="write a static local claim-gate UI")
    ui.add_argument("--output", help="optional HTML output path")
    ui.set_defaults(func=cmd_ui)

    validate = subparsers.add_parser("validate", help="run product validation gates")
    validate.set_defaults(func=cmd_validate)

    inspect = subparsers.add_parser("inspect", help="print a trace summary")
    inspect.add_argument("trace_id", help="trace id such as trace_039")
    inspect.set_defaults(func=cmd_inspect)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
