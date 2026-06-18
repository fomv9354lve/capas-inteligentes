from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "docs" / "schema" / "external_reviewer_feedback.schema.json"
TEMPLATE_PATH = ROOT / "examples" / "external_reviewer_feedback_template.json"
VALIDATION_DIR = ROOT / "outputs" / "external_validation"
REPORT_PATH = ROOT / "outputs" / "external_user_validation_report.json"


USEFUL_DECISIONS = {"confirms_utility", "requests_schema_change", "rejects_utility"}
EXTERNAL_INDEPENDENCE = {"external_independent", "external_known"}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _validate_shape(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    reviewer = payload.get("reviewer")
    context = payload.get("review_context")
    commands = payload.get("commands_run")
    answers = payload.get("answers")

    if not isinstance(reviewer, dict):
        errors.append("reviewer must be an object")
        reviewer = {}
    if not isinstance(context, dict):
        errors.append("review_context must be an object")
        context = {}
    if not isinstance(commands, list) or not commands:
        errors.append("commands_run must be a non-empty list")
        commands = []
    if not isinstance(answers, dict):
        errors.append("answers must be an object")
        answers = {}

    for field in ("name_or_handle", "role_or_domain", "independence"):
        value = reviewer.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"reviewer.{field} must be a non-empty string")
    if reviewer.get("independence") not in {"external_independent", "external_known", "internal", "unknown"}:
        errors.append("reviewer.independence has unsupported value")

    for field in ("date", "artifact_commit", "packet_manifest"):
        value = context.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"review_context.{field} must be a non-empty string")

    for index, item in enumerate(commands):
        if not isinstance(item, dict):
            errors.append(f"commands_run[{index}] must be an object")
            continue
        if not isinstance(item.get("command"), str) or not item["command"].strip():
            errors.append(f"commands_run[{index}].command must be a non-empty string")
        if item.get("result") not in {"passed", "failed", "not_run"}:
            errors.append(f"commands_run[{index}].result has unsupported value")

    for field in (
        "helps_audit_scientific_outputs",
        "missing_field_or_category",
        "rewrite_hold_vs_binary",
        "adoption_blocker",
    ):
        value = answers.get(field)
        if not isinstance(value, str):
            errors.append(f"answers.{field} must be a string")
    if answers.get("helps_audit_scientific_outputs") not in {"yes", "no", "unclear"}:
        errors.append("answers.helps_audit_scientific_outputs has unsupported value")

    if payload.get("decision") not in {"confirms_utility", "requests_schema_change", "rejects_utility", "inconclusive"}:
        errors.append("decision has unsupported value")
    if not isinstance(payload.get("follow_up_required"), list):
        errors.append("follow_up_required must be a list")
    return errors


def _is_real_external_feedback(payload: dict[str, Any]) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    reviewer = payload.get("reviewer", {})
    context = payload.get("review_context", {})
    commands = payload.get("commands_run", [])
    decision = payload.get("decision")

    if reviewer.get("independence") not in EXTERNAL_INDEPENDENCE:
        reasons.append("reviewer is not marked external")
    if str(reviewer.get("name_or_handle", "")).startswith("PENDING"):
        reasons.append("reviewer is still a pending placeholder")
    if str(context.get("artifact_commit", "")).startswith("PENDING"):
        reasons.append("artifact_commit is still a pending placeholder")
    if decision not in USEFUL_DECISIONS:
        reasons.append("decision is not a utility-confirming/rejecting/schema-changing outcome")
    if not any(isinstance(item, dict) and item.get("result") == "passed" for item in commands):
        reasons.append("no reviewed command is marked passed")
    return not reasons, reasons


def main() -> int:
    schema_exists = SCHEMA_PATH.exists()
    template_exists = TEMPLATE_PATH.exists()
    template_errors = _validate_shape(_load(TEMPLATE_PATH)) if template_exists else ["template missing"]

    feedback_files = sorted(VALIDATION_DIR.glob("*.json")) if VALIDATION_DIR.exists() else []
    feedback_results = []
    complete = False
    for path in feedback_files:
        payload = _load(path)
        shape_errors = _validate_shape(payload)
        real, reasons = _is_real_external_feedback(payload) if not shape_errors else (False, shape_errors)
        complete = complete or real
        feedback_results.append({
            "path": str(path.relative_to(ROOT)),
            "shape_errors": shape_errors,
            "counts_as_external_validation": real,
            "blocking_reasons": reasons,
        })

    report = {
        "external_user_validation_complete": complete,
        "schema_exists": schema_exists,
        "template_exists": template_exists,
        "template_valid": not template_errors,
        "template_errors": template_errors,
        "feedback_files": feedback_results,
        "completion_rule": (
            "Complete only when outputs/external_validation contains feedback from "
            "an external reviewer with non-placeholder identity/context, at least "
            "one passed command, and a decision of confirms_utility, "
            "requests_schema_change, or rejects_utility."
        ),
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    print(f"feedback_schema: {'ok' if schema_exists else 'missing'}")
    print(f"feedback_template: {'ok' if template_exists and not template_errors else 'invalid'}")
    print(f"external_feedback_files: {len(feedback_results)}")
    print(f"external_user_validation_complete: {complete}")
    print(f"report written to {REPORT_PATH}")
    return 0 if schema_exists and template_exists and not template_errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
