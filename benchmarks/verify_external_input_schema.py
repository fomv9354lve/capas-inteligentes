from __future__ import annotations

import copy
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
    ROOT / "examples" / "external_claim_fine_tune_ready.json",
]
INVALID_EXAMPLE = ROOT / "examples" / "external_claim_invalid.json"
SCHEMA_VERSION = capas.CAPAS_CLAIM_SCHEMA_VERSION


def _with_schema(payload: dict) -> dict:
    payload = copy.deepcopy(payload)
    payload.setdefault("schema_version", SCHEMA_VERSION)
    return payload


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
        "training_evidence_boolean_string",
        {
            "claim": {
                "id": "training_evidence_boolean_string",
                "type": "exact_model_solution",
                "text": "Training evidence flags must be typed booleans.",
            },
            "evidence": {
                "abs_error": 0.0,
                "tolerance": 0.01,
            },
            "training_evidence": {
                "source_backed_evidence": "yes",
                "external_review": True,
                "semantic_alignment": True,
                "witness_independence": True,
            },
        },
        "training_evidence.source_backed_evidence must be a boolean",
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
    (
        "p_value_out_of_range",
        {
            "claim": {
                "id": "p_value_out_of_range",
                "type": "statistical_confidence",
                "text": "A p-value outside probability bounds must not license a statistical claim.",
            },
            "evidence": {
                "p_value": 1.2,
                "alpha": 0.05,
                "effect_direction_confirmed": True,
            },
        },
        "evidence.p_value must be between 0 and 1",
    ),
    (
        "supporting_sources_must_be_strings",
        {
            "claim": {
                "id": "supporting_sources_must_be_strings",
                "type": "evidence_conflict_claim",
                "text": "Source arrays must not contain untyped objects.",
            },
            "evidence": {
                "supporting_sources": [{"id": "source_a"}],
                "contradicting_sources": ["source_b"],
                "conflict_resolution_method": "pre-registered hierarchy",
                "resolution_pre_registered": True,
            },
        },
        "evidence.supporting_sources must be an array of strings",
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
    (
        "statistical_confidence_accept",
        {
            "claim": {
                "id": "statistical_confidence_accept",
                "type": "statistical_confidence",
                "text": "The observed effect is statistically significant at alpha 0.05.",
            },
            "evidence": {
                "p_value": 0.01,
                "alpha": 0.05,
                "effect_direction_confirmed": True,
            },
        },
        "ACCEPT",
        "effect direction is confirmed",
    ),
    (
        "reproducibility_check_rewrite",
        {
            "claim": {
                "id": "reproducibility_check_rewrite",
                "type": "reproducibility_check",
                "text": "The reported result is independently reproducible.",
            },
            "evidence": {
                "artifact_available": True,
                "independent_reproduction_pass": False,
            },
        },
        "REWRITE",
        "independent reproduction has not passed",
    ),
    (
        "financial_metric_claim_accept",
        {
            "claim": {
                "id": "financial_metric_claim_accept",
                "type": "financial_metric_claim",
                "text": "The reported financial metric matches the reference for the same period.",
            },
            "evidence": {
                "reported_value": 101.2,
                "reference_value": 101.0,
                "tolerance": 0.5,
                "metric_period_match": True,
            },
        },
        "ACCEPT",
        "period matches",
    ),
    (
        "causal_mechanism_claim_accept",
        {
            "claim": {
                "id": "causal_mechanism_claim_accept",
                "type": "causal_mechanism_claim",
                "text": "The intervention causally changes the outcome through the declared mechanism.",
            },
            "evidence": {
                "intervention_or_natural_experiment": True,
                "temporal_order_established": True,
                "confounders_controlled": True,
                "mechanism_evidence_present": True,
            },
        },
        "ACCEPT",
        "mechanism evidence all pass",
    ),
    (
        "systematic_review_claim_rewrite",
        {
            "claim": {
                "id": "systematic_review_claim_rewrite",
                "type": "systematic_review_claim",
                "text": "The systematic review supports the reported effect across included studies.",
            },
            "evidence": {
                "protocol_registered": True,
                "inclusion_criteria_declared": True,
                "risk_of_bias_assessed": False,
                "effect_consistency": False,
            },
        },
        "REWRITE",
        "bias/consistency evidence is incomplete",
    ),
    (
        "evidence_conflict_claim_accept",
        {
            "claim": {
                "id": "evidence_conflict_claim_accept",
                "type": "evidence_conflict_claim",
                "text": "The conflicting evidence is resolved by the declared pre-registered method.",
            },
            "evidence": {
                "supporting_sources": ["source_a"],
                "contradicting_sources": ["source_b"],
                "conflict_resolution_method": "pre-registered hierarchy",
                "resolution_pre_registered": True,
            },
        },
        "ACCEPT",
        "pre-registered conflict-resolution method",
    ),
    (
        "multimodal_evidence_claim_accept",
        {
            "claim": {
                "id": "multimodal_evidence_claim_accept",
                "type": "multimodal_evidence_claim",
                "text": "The multimodal evidence supports the extracted claim.",
            },
            "evidence": {
                "modality": "table",
                "source_hashes_verified": True,
                "cross_modal_alignment": True,
                "extraction_method_declared": True,
            },
        },
        "ACCEPT",
        "cross-modal alignment",
    ),
    (
        "fine_tune_ready_positive",
        json.loads((ROOT / "examples" / "external_claim_fine_tune_ready.json").read_text(encoding="utf-8")),
        "ACCEPT",
        '"fine_tune_ready": true',
    ),
    (
        "fine_tune_ready_blocked_without_review",
        {
            "claim": {
                "id": "fine_tune_ready_blocked_without_review",
                "type": "universal_anchor_claim",
                "text": "The generated scaling result is physically consistent with the universal z=1 anchor.",
            },
            "evidence": {
                "anchor_mode": "absolute_anchor",
                "local_property_tests_pass": True,
                "universal_anchor_pass": True,
            },
            "training_evidence": {
                "source_backed_evidence": True,
                "external_review": False,
                "semantic_alignment": True,
                "witness_independence": True,
                "provenance": {
                    "sources": ["benchmarks/gold_traces/trace_039.json"],
                    "review_id": "external-review-trace-039-v1",
                    "witness_id": "theory_scaling_law_no_solver",
                },
            },
        },
        "ACCEPT",
        "external review is not attached",
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

    base_schema_payload = _with_schema({
        "claim": {
            "id": "schema_version_control",
            "type": "exact_model_solution",
            "text": "The model solution is within tolerance.",
        },
        "evidence": {"abs_error": 0.0, "tolerance": 0.1},
    })
    for name, payload in [
        ("missing_schema_version", {key: value for key, value in base_schema_payload.items() if key != "schema_version"}),
        ("wrong_schema_version", {**base_schema_payload, "schema_version": "capas-claim-payload-v2"}),
    ]:
        errors = capas.validate_external_payload(payload)
        decision = capas.decide_external_claim(payload)
        expected_error = f"schema_version must be {SCHEMA_VERSION}"
        checks.append({
            "check": f"schema_version_enforced:{name}",
            "passed": expected_error in errors and decision["verdict"] == "HOLD" and expected_error in decision["schema_errors"],
            "expected_error": expected_error,
            "errors": errors,
            "decision": decision,
        })

    for name, payload, expected_error in ADVERSARIAL_PAYLOADS:
        payload = _with_schema(payload)
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
        payload = _with_schema(payload)
        decision = capas.decide_external_claim(payload)
        checks.append({
            "check": f"semantic_payload:{name}",
            "passed": (
                decision["verdict"] == expected_verdict
                and (
                    expected_detail in decision["reason"]
                    or expected_detail in decision.get("missing_fields", [])
                    or expected_detail in decision.get("fine_tune_blockers", [])
                    or expected_detail in json.dumps(decision, sort_keys=True)
                    or expected_detail in json.dumps(decision.get("fine_tune_criteria", {}), sort_keys=True)
                )
            ),
            "expected_verdict": expected_verdict,
            "expected_detail": expected_detail,
            "decision": decision,
        })

    ready_payload = _load(ROOT / "examples" / "external_claim_fine_tune_ready.json")
    fine_tune_negative_cases = [
        (
            "review_hash_mismatch",
            ("review_sha256", "0" * 64),
            "review_hash_verified",
            "external review hash is missing or does not match review_packet",
        ),
        (
            "source_hash_mismatch",
            ("source_hashes", {"file://benchmarks/gold_traces/trace_039.json": "0" * 64}),
            "source_urls_recoverable_hashable",
            "source URLs are not recoverable with matching hashes",
        ),
        (
            "witness_not_in_registry",
            ("witness_id", "missing_witness"),
            "witness_registry_resolved",
            "witness_id is not resolvable in the witness registry",
        ),
        (
            "ro_crate_hash_mismatch",
            ("ro_crate_sha256", "0" * 64),
            "ro_crate_validated",
            "RO-Crate provenance packet is missing, invalid, or hash-mismatched",
        ),
        (
            "reviewer_attestation_hash_mismatch",
            ("reviewer.attestation_sha256", "0" * 64),
            "reviewer_attestation_verified",
            "reviewer identity or attestation is not verifiable",
        ),
    ]
    for name, (field_path, value), expected_criterion, expected_blocker in fine_tune_negative_cases:
        payload = copy.deepcopy(ready_payload)
        provenance = payload["training_evidence"]["provenance"]
        if field_path == "reviewer.attestation_sha256":
            provenance["reviewer"]["attestation_sha256"] = value
        else:
            provenance[field_path] = value
        decision = capas.decide_external_claim(payload)
        criteria = decision.get("fine_tune_criteria", {})
        blockers = decision.get("fine_tune_blockers", [])
        checks.append({
            "check": f"fine_tune_external_verification:{name}",
            "passed": (
                decision["verdict"] == "ACCEPT"
                and decision["fine_tune_ready"] is False
                and criteria.get(expected_criterion) is False
                and expected_blocker in blockers
            ),
            "expected_criterion": expected_criterion,
            "expected_blocker": expected_blocker,
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
