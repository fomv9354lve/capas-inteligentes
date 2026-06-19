from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import capas


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "docs" / "schema" / "capas_claim_payload.schema.json"
REPORT_PATH = ROOT / "outputs" / "external_input_schema_report.json"


VALID_EXAMPLES = [
    ROOT / "examples" / "external_claim_accept.json",
    ROOT / "examples" / "external_claim_rewrite.json",
    ROOT / "examples" / "external_claim_hold.json",
]
INVALID_EXAMPLE = ROOT / "examples" / "external_claim_invalid.json"


ADVERSARIAL_PAYLOADS = [
    (
        "negative_abs_error",
        {
            "claim": {
                "id": "negative_abs_error",
                "type": "exact_model_solution",
                "text": "A negative absolute error should not license an exact model claim.",
            },
            "evidence": {
                "abs_error": -999.0,
                "tolerance": 0.01,
            },
        },
        "evidence.abs_error must be >= 0",
    ),
    (
        "negative_tolerance",
        {
            "claim": {
                "id": "negative_tolerance",
                "type": "exact_model_solution",
                "text": "A negative tolerance should not be accepted.",
            },
            "evidence": {
                "abs_error": 0.0,
                "tolerance": -1.0,
            },
        },
        "evidence.tolerance must be >= 0",
    ),
    (
        "double_negative_exact_solution",
        {
            "claim": {
                "id": "double_negative_exact_solution",
                "type": "exact_model_solution",
                "text": "Two negative values must not create a false ACCEPT.",
            },
            "evidence": {
                "abs_error": -5.0,
                "tolerance": -1.0,
            },
        },
        "evidence.abs_error must be >= 0",
    ),
    (
        "boolean_numeric_field",
        {
            "claim": {
                "id": "boolean_numeric_field",
                "type": "exact_model_solution",
                "text": "Boolean values must not be accepted as numeric error fields.",
            },
            "evidence": {
                "abs_error": True,
                "tolerance": 0.01,
            },
        },
        "evidence.abs_error must be a number",
    ),
    (
        "oversized_claim_id",
        {
            "claim": {
                "id": "x" * 257,
                "type": "universal_anchor_claim",
                "text": "Oversized claim ids should be rejected before decision logic.",
            },
            "evidence": {
                "anchor_mode": "absolute_anchor",
                "local_property_tests_pass": True,
                "universal_anchor_pass": True,
            },
        },
        "claim.id must be at most 256 characters",
    ),
    (
        "oversized_claim_text",
        {
            "claim": {
                "id": "oversized_claim_text",
                "type": "universal_anchor_claim",
                "text": "x" * 2001,
            },
            "evidence": {
                "anchor_mode": "absolute_anchor",
                "local_property_tests_pass": True,
                "universal_anchor_pass": True,
            },
        },
        "claim.text must be at most 2000 characters",
    ),
    (
        "current_claim_raw_html",
        {
            "claim": {
                "id": "current_claim_raw_html",
                "type": "claim_transition",
                "text": "A malicious current_claim should not flow into rewrite output.",
            },
            "evidence": {
                "upgrade_evidence_present": False,
                "current_claim": "<img src=x onerror=alert('xss')>",
            },
        },
        "evidence.current_claim must not contain angle brackets or Unicode angle-bracket homoglyphs",
    ),
    (
        "current_claim_unicode_angle_homoglyph",
        {
            "claim": {
                "id": "current_claim_unicode_angle_homoglyph",
                "type": "claim_transition",
                "text": "Unicode angle-bracket homoglyphs should not flow into rewrite output.",
            },
            "evidence": {
                "upgrade_evidence_present": False,
                "current_claim": "\uff1cscript\uff1ealert(1)\uff1c/script\uff1e",
            },
        },
        "evidence.current_claim must not contain angle brackets or Unicode angle-bracket homoglyphs",
    ),
    (
        "claim_id_raw_html",
        {
            "claim": {
                "id": "<script>",
                "type": "physical_accuracy",
                "text": "Claim ids should not carry raw HTML.",
            },
            "evidence": {
                "within_chemical_accuracy": True,
            },
        },
        "claim.id must not contain angle brackets or Unicode angle-bracket homoglyphs",
    ),
    (
        "claim_text_raw_html",
        {
            "claim": {
                "id": "claim_text_raw_html",
                "type": "physical_accuracy",
                "text": "<img src=x onerror=alert('xss')>",
            },
            "evidence": {
                "within_chemical_accuracy": True,
            },
        },
        "claim.text must not contain angle brackets or Unicode angle-bracket homoglyphs",
    ),
    (
        "claim_text_unicode_angle_homoglyph",
        {
            "claim": {
                "id": "claim_text_unicode_angle_homoglyph",
                "type": "physical_accuracy",
                "text": "\u27e8img src=x onerror=alert(1)\u27e9",
            },
            "evidence": {
                "within_chemical_accuracy": True,
            },
        },
        "claim.text must not contain angle brackets or Unicode angle-bracket homoglyphs",
    ),
    (
        "claim_text_second_generation_angle_homoglyphs",
        {
            "claim": {
                "id": "claim_text_second_generation_angle_homoglyphs",
                "type": "physical_accuracy",
                "text": "\ufe64bad\ufe65 \u276cbad\u276d \u29fcbad\u29fd \u2329bad\u232a \u3008bad\u3009",
            },
            "evidence": {
                "within_chemical_accuracy": True,
            },
        },
        "claim.text must not contain angle brackets or Unicode angle-bracket homoglyphs",
    ),
    (
        "anchor_mode_unicode_angle_homoglyph",
        {
            "claim": {
                "id": "anchor_mode_unicode_angle_homoglyph",
                "type": "universal_anchor_claim",
                "text": "Angle-like payloads should not pass through anchor_mode.",
            },
            "evidence": {
                "anchor_mode": "absolute_\uff1canchor",
                "local_property_tests_pass": True,
                "universal_anchor_pass": True,
            },
        },
        "evidence.anchor_mode must not contain angle brackets or Unicode angle-bracket homoglyphs",
    ),
    (
        "physical_evidence_level_angle_homoglyph",
        {
            "claim": {
                "id": "physical_evidence_level_angle_homoglyph",
                "type": "physical_accuracy",
                "text": "Angle-like payloads should not pass through evidence strings.",
            },
            "evidence": {
                "within_chemical_accuracy": True,
                "physical_evidence_level": "\u3008experimental\u3009",
            },
        },
        "evidence.physical_evidence_level must not contain angle brackets or Unicode angle-bracket homoglyphs",
    ),
]

SEMANTIC_PAYLOADS = [
    (
        "zero_tolerance_exact_accept",
        {
            "claim": {
                "id": "zero_tolerance_exact_accept",
                "type": "exact_model_solution",
                "text": "A zero tolerance is allowed only as an exact equality check.",
            },
            "evidence": {
                "abs_error": 0.0,
                "tolerance": 0.0,
            },
        },
        "ACCEPT",
        "abs_error 0.0 <= tolerance 0.0",
    ),
    (
        "anchor_mode_unknown_missing",
        {
            "claim": {
                "id": "anchor_mode_unknown_missing",
                "type": "universal_anchor_claim",
                "text": "An unknown anchor mode should be treated as undeclared evidence.",
            },
            "evidence": {
                "anchor_mode": "unknown",
                "local_property_tests_pass": True,
                "universal_anchor_pass": True,
            },
        },
        "HOLD",
        "anchor_mode",
    ),
]


def _run(command: list[str]) -> dict[str, object]:
    proc = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    return {
        "command": " ".join(command),
        "returncode": proc.returncode,
        "stdout_tail": proc.stdout[-2000:],
        "stderr_tail": proc.stderr[-2000:],
        "passed": proc.returncode == 0,
    }


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    published_schema = _load(SCHEMA_PATH)
    generated_schema = capas.external_claim_payload_schema()
    checks: list[dict[str, object]] = [
        {
            "check": "published_schema_matches_cli_schema",
            "passed": published_schema == generated_schema,
            "detail": str(SCHEMA_PATH.relative_to(ROOT)),
        }
    ]

    for path in VALID_EXAMPLES:
        payload = _load(path)
        errors = capas.validate_external_payload(payload)
        result = _run([sys.executable, "capas.py", "check-input", "--input", str(path.relative_to(ROOT))])
        checks.append({
            "check": f"valid_example:{path.name}",
            "passed": not errors and result["passed"],
            "errors": errors,
            "cli": result,
        })

    invalid_payload = _load(INVALID_EXAMPLE)
    invalid_errors = capas.validate_external_payload(invalid_payload)
    invalid_cli = _run([sys.executable, "capas.py", "check-input", "--input", str(INVALID_EXAMPLE.relative_to(ROOT))])
    invalid_decision = capas.decide_external_claim(invalid_payload)
    checks.append({
        "check": f"invalid_example:{INVALID_EXAMPLE.name}",
        "passed": bool(invalid_errors) and not invalid_cli["passed"] and invalid_decision["verdict"] == "HOLD",
        "errors": invalid_errors,
        "cli": invalid_cli,
        "decision": invalid_decision,
    })

    for name, payload, expected_error in ADVERSARIAL_PAYLOADS:
        errors = capas.validate_external_payload(payload)
        decision = capas.decide_external_claim(payload)
        checks.append({
            "check": f"adversarial_payload:{name}",
            "passed": (
                expected_error in errors
                and decision["verdict"] == "HOLD"
                and expected_error in decision["schema_errors"]
            ),
            "expected_error": expected_error,
            "errors": errors,
            "decision": decision,
        })

    for name, payload, expected_verdict, expected_detail in SEMANTIC_PAYLOADS:
        decision = capas.decide_external_claim(payload)
        checks.append({
            "check": f"semantic_payload:{name}",
            "passed": (
                decision["verdict"] == expected_verdict
                and (
                    expected_detail in decision["reason"]
                    or expected_detail in decision.get("missing_fields", [])
                )
            ),
            "expected_verdict": expected_verdict,
            "expected_detail": expected_detail,
            "decision": decision,
        })

    passed = all(bool(check["passed"]) for check in checks)
    report = {
        "external_input_schema_ready": passed,
        "schema": str(SCHEMA_PATH.relative_to(ROOT)),
        "valid_examples": [str(path.relative_to(ROOT)) for path in VALID_EXAMPLES],
        "invalid_example": str(INVALID_EXAMPLE.relative_to(ROOT)),
        "checks": checks,
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    for check in checks:
        status = "ok" if check["passed"] else "failed"
        print(f"{check['check']}: {status}")
    print(f"external_input_schema_ready: {passed}")
    print(f"report written to {REPORT_PATH}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
