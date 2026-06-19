from __future__ import annotations

import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen


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
CAPAS_CLAIM_SCHEMA_VERSION = "capas-claim-payload-v2"
CAPAS_UI_VERSION = "v11 · schema v2 pipelines"


VALIDATION_COMMANDS = [
    ("external input schema", ["benchmarks/verify_external_input_schema.py"]),
    ("standalone pipeline MVP", ["benchmarks/verify_standalone_pipeline.py"]),
    ("claim gate UI", ["benchmarks/verify_claim_gate_ui.py"]),
    ("claim gate browser E2E", ["benchmarks/verify_claim_gate_ui_browser.py"]),
    ("batch and API surfaces", ["benchmarks/verify_batch_and_api.py"]),
    ("external user validation packet", ["benchmarks/verify_external_user_validation.py"]),
    ("profile registration packet", ["benchmarks/verify_profile_registration_packet.py"]),
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
    "statistical_confidence": ["p_value", "alpha", "effect_direction_confirmed"],
    "reproducibility_check": ["artifact_available", "independent_reproduction_pass"],
    "financial_metric_claim": ["reported_value", "reference_value", "tolerance", "metric_period_match"],
}

FINE_TUNE_BLOCKERS = [
    "no blind or external inference review is attached",
    "CAPAS gates supplied structured evidence; it does not infer hidden evidence",
    "training readiness requires source-backed evidence, semantic alignment, witness independence, and review",
]

CLAIM_TYPE_TERMS = {
    "exact_model_solution": [
        "exact",
        "model",
        "solution",
        "error",
        "tolerance",
        "hamiltonian",
        "fci",
    ],
    "physical_accuracy": [
        "physical",
        "experiment",
        "experimental",
        "accuracy",
        "chemical",
        "real",
    ],
    "universal_anchor_claim": [
        "universal",
        "anchor",
        "invariant",
        "scaling",
        "physical",
        "consistent",
    ],
    "claim_transition": [
        "claim",
        "evidence",
        "upgrade",
        "supports",
        "rewrite",
        "stronger",
    ],
    "statistical_confidence": [
        "p-value",
        "alpha",
        "confidence",
        "significant",
        "statistical",
    ],
    "reproducibility_check": [
        "reproduce",
        "reproducible",
        "artifact",
        "replication",
        "independent",
    ],
    "financial_metric_claim": [
        "financial",
        "metric",
        "reported",
        "reference",
        "period",
        "tolerance",
    ],
}

STRONG_PHYSICAL_PATTERNS = [
    r"\bphysically correct\b",
    r"\bphysical correctness\b",
    r"\bproves?\b",
    r"\bguarantees?\b",
    r"\bcertif(?:y|ies|ied)\b",
    r"\bmatches? experiment\b",
    r"\bexperimental(?:ly)? accurate\b",
    r"\btrue in the real molecule\b",
]

MODEL_SCOPE_PATTERNS = [
    r"\bmodel\b",
    r"\bhamiltonian\b",
    r"\bfci\b",
    r"\bexact diagonalization\b",
]

EXPERIMENT_SCOPE_PATTERNS = [
    r"\bexperiment\b",
    r"\bexperimental\b",
    r"\breal world\b",
    r"\breal molecule\b",
    r"\blaboratory\b",
    r"\bchemical accuracy\b",
]

NUMBER_PATTERN = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?"
BOOLEAN_PATTERN = r"(true|false|yes|no|pass|fail|passed|failed|1|0)"
WEB_FETCH_TIMEOUT_SECONDS = 15
DISALLOWED_ANGLE_CHARS = "<>\u02c2\u02c3\u2039\u203a"
DISALLOWED_ANGLE_RANGES = "\u2329-\u232a\u276c-\u276d\u27e8-\u27e9\u29fc-\u29fd\u3008-\u3009\ufe64-\ufe65\uff1c-\uff1e"
DISALLOWED_ANGLE_REGEX = re.compile(f"[{re.escape(DISALLOWED_ANGLE_CHARS)}{DISALLOWED_ANGLE_RANGES}]")
NO_ANGLE_PATTERN = f"^[^{re.escape(DISALLOWED_ANGLE_CHARS)}{DISALLOWED_ANGLE_RANGES}]*$"


def _contains_angle_like_character(value: str) -> bool:
    return bool(DISALLOWED_ANGLE_REGEX.search(value))


def _validate_no_angle_like(value: Any, field_name: str, errors: list[str]) -> None:
    if isinstance(value, str) and _contains_angle_like_character(value):
        errors.append(f"{field_name} must not contain angle brackets or Unicode angle-bracket homoglyphs")


def external_claim_payload_schema() -> dict[str, Any]:
    claim_types = sorted(REQUIRED_DECISION_FIELDS)
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://capas.local/schema/capas_claim_payload.schema.json",
        "title": "CAPAS external claim/evidence payload",
        "x-capas-schema-version": CAPAS_CLAIM_SCHEMA_VERSION,
        "type": "object",
        "additionalProperties": True,
        "required": ["claim", "evidence"],
        "properties": {
            "claim": {
                "type": "object",
                "additionalProperties": True,
                "required": ["id", "type", "text"],
                "properties": {
                    "id": {
                        "type": "string",
                        "minLength": 1,
                        "maxLength": 256,
                        "pattern": NO_ANGLE_PATTERN,
                        "description": "Claim ids must not contain HTML angle brackets or common Unicode angle-bracket homoglyphs.",
                    },
                    "type": {"type": "string", "enum": claim_types},
                    "text": {
                        "type": "string",
                        "minLength": 1,
                        "maxLength": 2000,
                        "pattern": NO_ANGLE_PATTERN,
                        "description": "Claim text must not contain HTML angle brackets or common Unicode angle-bracket homoglyphs because payloads may be displayed by downstream consumers.",
                    },
                },
            },
            "evidence": {
                "type": "object",
                "additionalProperties": True,
                "description": "Evidence fields are claim-type dependent; unsupported or missing evidence yields HOLD.",
                "properties": {
                    "abs_error": {"type": "number", "minimum": 0},
                    "tolerance": {"type": "number", "minimum": 0},
                    "within_chemical_accuracy": {"type": "boolean"},
                    "anchor_mode": {
                        "type": "string",
                        "pattern": NO_ANGLE_PATTERN,
                    },
                    "local_property_tests_pass": {"type": "boolean"},
                    "universal_anchor_pass": {"type": "boolean"},
                    "upgrade_evidence_present": {"type": "boolean"},
                    "p_value": {"type": "number", "minimum": 0, "maximum": 1},
                    "alpha": {"type": "number", "minimum": 0, "maximum": 1},
                    "effect_direction_confirmed": {"type": "boolean"},
                    "artifact_available": {"type": "boolean"},
                    "independent_reproduction_pass": {"type": "boolean"},
                    "reported_value": {"type": "number"},
                    "reference_value": {"type": "number"},
                    "metric_period_match": {"type": "boolean"},
                    "physical_evidence_level": {
                        "type": "string",
                        "pattern": NO_ANGLE_PATTERN,
                    },
                    "verification_independence": {
                        "type": "string",
                        "pattern": NO_ANGLE_PATTERN,
                    },
                    "reference_truth": {},
                    "current_claim": {
                        "type": "string",
                        "maxLength": 4000,
                        "pattern": NO_ANGLE_PATTERN,
                        "description": "Optional weaker claim text for REWRITE. HTML angle brackets and common Unicode angle-bracket homoglyphs are rejected because this value can be displayed by downstream consumers.",
                    },
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
    if isinstance(claim.get("id"), str) and len(claim["id"]) > 256:
        errors.append("claim.id must be at most 256 characters")
    _validate_no_angle_like(claim.get("id"), "claim.id", errors)
    if isinstance(claim.get("text"), str) and len(claim["text"]) > 2000:
        errors.append("claim.text must be at most 2000 characters")
    _validate_no_angle_like(claim.get("text"), "claim.text", errors)

    claim_type = claim.get("type")
    if isinstance(claim_type, str) and claim_type not in REQUIRED_DECISION_FIELDS:
        errors.append(
            "claim.type must be one of: "
            + ", ".join(sorted(REQUIRED_DECISION_FIELDS))
        )

    numeric_fields = ["abs_error", "tolerance", "p_value", "alpha", "reported_value", "reference_value"]
    for field in numeric_fields:
        if field in evidence and (
            isinstance(evidence[field], bool)
            or not isinstance(evidence[field], (int, float))
        ):
            errors.append(f"evidence.{field} must be a number")
        elif field in evidence:
            value = float(evidence[field])
            if not (value == value and value not in (float("inf"), float("-inf"))):
                errors.append(f"evidence.{field} must be finite")
            elif field in {"abs_error", "tolerance"} and value < 0:
                errors.append(f"evidence.{field} must be >= 0")
            elif field in {"p_value", "alpha"} and not 0 <= value <= 1:
                errors.append(f"evidence.{field} must be between 0 and 1")

    bool_fields = [
        "within_chemical_accuracy",
        "local_property_tests_pass",
        "universal_anchor_pass",
        "upgrade_evidence_present",
        "effect_direction_confirmed",
        "artifact_available",
        "independent_reproduction_pass",
        "metric_period_match",
    ]
    for field in bool_fields:
        if field in evidence and not isinstance(evidence[field], bool):
            errors.append(f"evidence.{field} must be a boolean")

    string_fields = [
        "anchor_mode",
        "physical_evidence_level",
        "verification_independence",
    ]
    for field in string_fields:
        if field in evidence and not isinstance(evidence[field], str):
            errors.append(f"evidence.{field} must be a string")
        _validate_no_angle_like(evidence.get(field), f"evidence.{field}", errors)
    if "current_claim" in evidence:
        current_claim = evidence["current_claim"]
        if not isinstance(current_claim, str):
            errors.append("evidence.current_claim must be a string")
        else:
            if len(current_claim) > 4000:
                errors.append("evidence.current_claim must be at most 4000 characters")
            _validate_no_angle_like(current_claim, "evidence.current_claim", errors)
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
            "schema_version": CAPAS_CLAIM_SCHEMA_VERSION,
            "input_claim": claim if isinstance(claim, dict) else {},
            "verdict": "HOLD",
            "reason": "input payload failed CAPAS schema validation",
            "licensed_claim": claim.get("text") if isinstance(claim, dict) else None,
            "rewrite": None,
            "missing_fields": [],
            "required_fields": [],
            "schema_errors": schema_errors,
            "fine_tune_ready": False,
            "fine_tune_blockers": FINE_TUNE_BLOCKERS,
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
    elif claim_type == "statistical_confidence":
        p_value = float(evidence["p_value"])
        alpha = float(evidence["alpha"])
        if p_value <= alpha and evidence["effect_direction_confirmed"] is True:
            verdict = "ACCEPT"
            reason = f"p_value {p_value} <= alpha {alpha} and effect direction is confirmed"
        elif p_value <= alpha:
            verdict = "REWRITE"
            reason = "statistical threshold passes, but effect direction is not licensed"
            rewrite = "statistical threshold only; directional or causal wording is not licensed"
            licensed_claim = rewrite
        else:
            verdict = "REJECT"
            reason = f"p_value {p_value} > alpha {alpha}"
    elif claim_type == "reproducibility_check":
        artifact_available = evidence["artifact_available"] is True
        reproduced = evidence["independent_reproduction_pass"] is True
        if artifact_available and reproduced:
            verdict = "ACCEPT"
            reason = "artifact is available and independent reproduction passed"
        elif artifact_available and not reproduced:
            verdict = "REWRITE"
            reason = "artifact exists, but independent reproduction has not passed"
            rewrite = "artifact available; independent reproduction is not yet licensed"
            licensed_claim = rewrite
        else:
            verdict = "REJECT"
            reason = "required artifact is not available for reproducibility"
    elif claim_type == "financial_metric_claim":
        reported_value = float(evidence["reported_value"])
        reference_value = float(evidence["reference_value"])
        tolerance = float(evidence["tolerance"])
        delta = abs(reported_value - reference_value)
        if delta <= tolerance and evidence["metric_period_match"] is True:
            verdict = "ACCEPT"
            reason = f"reported_value differs from reference_value by {delta}, within tolerance {tolerance}, and period matches"
        elif delta <= tolerance:
            verdict = "REWRITE"
            reason = "numeric metric matches tolerance, but period alignment is not licensed"
            rewrite = "numeric metric matches reference tolerance; period-specific claim is not licensed"
            licensed_claim = rewrite
        else:
            verdict = "REJECT"
            reason = f"reported_value differs from reference_value by {delta}, above tolerance {tolerance}"

    return {
        "schema_version": CAPAS_CLAIM_SCHEMA_VERSION,
        "input_claim": claim,
        "verdict": verdict,
        "reason": reason,
        "licensed_claim": licensed_claim,
        "rewrite": rewrite,
        "missing_fields": missing,
        "required_fields": required or [],
        "schema_errors": [],
        "fine_tune_ready": False,
        "fine_tune_blockers": FINE_TUNE_BLOCKERS,
        "non_claim": "This decision is rule-based over supplied evidence fields, not an LLM judgment.",
    }


def _batch_items(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        items = payload
    elif isinstance(payload, dict) and isinstance(payload.get("items"), list):
        items = payload["items"]
    elif isinstance(payload, dict) and isinstance(payload.get("claims"), list):
        items = payload["claims"]
    elif isinstance(payload, dict) and isinstance(payload.get("claim"), dict) and isinstance(payload.get("evidence"), dict):
        items = [payload]
    else:
        raise ValueError("batch input must be a JSON array, an object with items/claims array, or one claim/evidence payload")
    if not all(isinstance(item, dict) for item in items):
        raise ValueError("every batch item must be a JSON object")
    return items


def run_batch(payload: Any, *, mode: str = "decide", allow_web: bool = False) -> dict[str, Any]:
    items = _batch_items(payload)
    results: list[dict[str, Any]] = []
    for index, item in enumerate(items):
        if mode == "decide":
            result = decide_external_claim(item)
        elif mode == "align":
            result = align_claim_text(item)
        elif mode == "pipeline":
            result = standalone_pipeline(item, allow_web=allow_web)
        else:
            raise ValueError(f"unsupported batch mode {mode!r}")
        results.append({"index": index, "result": result})

    verdicts = Counter()
    for entry in results:
        result = entry["result"]
        verdict = result.get("verdict") or result.get("final_decision", {}).get("verdict") or result.get("alignment_status")
        verdicts[str(verdict)] += 1

    return {
        "schema_version": CAPAS_CLAIM_SCHEMA_VERSION,
        "batch_mode": mode,
        "item_count": len(items),
        "results": results,
        "summary": dict(sorted(verdicts.items())),
        "fine_tune_ready": False,
        "fine_tune_blockers": [
            "batch decisions are not blind-reviewed",
            "CAPAS gates supplied structured evidence; it does not infer hidden evidence",
        ],
        "non_claim": "Batch mode applies the same deterministic per-claim gates; it does not create new scientific evidence.",
    }


def _lower_words(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def _contains_any(text: str, patterns: list[str]) -> list[str]:
    found: list[str] = []
    for pattern in patterns:
        if re.search(pattern, text):
            found.append(pattern)
    return found


def align_claim_text(payload: dict[str, Any]) -> dict[str, Any]:
    """Check whether claim prose is aligned with the structured CAPAS payload.

    This is deliberately a small deterministic guardrail, not general semantic
    understanding. It catches common overclaims before a structurally valid JSON
    can be mistaken for a semantically valid scientific claim.
    """

    schema_errors = validate_external_payload(payload)
    claim = payload.get("claim", {}) if isinstance(payload, dict) else {}
    evidence = payload.get("evidence", {}) if isinstance(payload, dict) else {}
    if schema_errors:
        return {
            "alignment_status": "HOLD_SCHEMA",
            "alignment_pass": False,
            "reason": "input payload failed CAPAS schema validation before semantic alignment",
            "issues": schema_errors,
            "claim_type_terms_found": [],
            "non_claim": "This is deterministic lexical/scope alignment, not broad language understanding.",
        }

    claim_type = str(claim.get("type"))
    text = _lower_words(str(claim.get("text", "")))
    issues: list[str] = []
    warnings: list[str] = []
    terms = CLAIM_TYPE_TERMS.get(claim_type, [])
    terms_found = [term for term in terms if term in text]
    strong_patterns = _contains_any(text, STRONG_PHYSICAL_PATTERNS)
    model_terms = _contains_any(text, MODEL_SCOPE_PATTERNS)
    experiment_terms = _contains_any(text, EXPERIMENT_SCOPE_PATTERNS)

    if not terms_found:
        warnings.append(
            f"claim.text does not mention expected concepts for {claim_type}: {terms}"
        )

    if claim_type == "exact_model_solution" and experiment_terms:
        issues.append(
            "claim.type exact_model_solution licenses truth within a model, but claim.text uses experimental/real-world scope"
        )

    if claim_type == "physical_accuracy" and model_terms and not experiment_terms:
        warnings.append(
            "physical_accuracy claim text mentions model scope but does not clearly mention experiment or physical accuracy"
        )

    if claim_type == "universal_anchor_claim":
        anchor_pass = evidence.get("universal_anchor_pass")
        local_pass = evidence.get("local_property_tests_pass")
        if local_pass is True and anchor_pass is False and strong_patterns:
            issues.append(
                "claim.text uses strong physical-correctness language, but universal_anchor_pass is false"
            )
        if evidence.get("anchor_mode") != "absolute_anchor":
            warnings.append(
                "universal_anchor_claim is strongest when anchor_mode is absolute_anchor"
            )

    if claim_type == "claim_transition":
        if evidence.get("upgrade_evidence_present") is False and strong_patterns:
            issues.append(
                "claim.text uses proof/certification language, but upgrade_evidence_present is false"
            )

    if issues:
        status = "MISALIGNED"
        reason = "claim.text overstates or changes the scope licensed by structured evidence"
    elif warnings:
        status = "WARN"
        reason = "claim.text is structurally usable but weakly aligned with expected claim vocabulary"
    else:
        status = "ALIGNED"
        reason = "claim.text is aligned with claim.type and supplied evidence scope"

    return {
        "alignment_status": status,
        "alignment_pass": not issues,
        "reason": reason,
        "issues": issues,
        "warnings": warnings,
        "claim_type_terms_found": terms_found,
        "strong_physical_patterns_found": strong_patterns,
        "model_scope_patterns_found": model_terms,
        "experiment_scope_patterns_found": experiment_terms,
        "non_claim": "This is deterministic lexical/scope alignment, not broad language understanding.",
    }


def _source_text(payload: dict[str, Any], *, allow_web: bool = False) -> str:
    return "\n".join(source["text"] for source in _source_records(payload, allow_web=allow_web))


def _read_source_path(path_value: str) -> str:
    path = (ROOT / path_value).resolve()
    try:
        path.relative_to(ROOT.resolve())
    except ValueError:
        raise ValueError("source.path must stay inside the CAPAS repository")
    return path.read_text(encoding="utf-8")


def _read_pdf_source_path(path_value: str) -> tuple[str, str | None]:
    path = (ROOT / path_value).resolve()
    try:
        path.relative_to(ROOT.resolve())
    except ValueError:
        raise ValueError("source.path must stay inside the CAPAS repository")
    try:
        from pypdf import PdfReader  # type: ignore
    except ImportError:
        return "", "PDF source requires optional dependency pypdf; install with capas-claim-gate[standalone]"
    try:
        reader = PdfReader(str(path))
        pages = [page.extract_text() or "" for page in reader.pages]
    except Exception as exc:  # pragma: no cover - parser errors depend on PDF internals
        return "", f"PDF parser failed for {path_value}: {exc}"
    return "\n".join(pages), None


def _read_url_source(url: str, *, allow_web: bool) -> tuple[str, str | None]:
    if not allow_web:
        return "", "web source declared but --allow-web was not set"
    if not url.startswith(("http://", "https://")):
        return "", "source.url must use http:// or https://"
    request = Request(url, headers={"User-Agent": "CAPAS-Claim-Gate/0.1"})
    try:
        with urlopen(request, timeout=WEB_FETCH_TIMEOUT_SECONDS) as response:
            content_type = response.headers.get("content-type", "")
            raw = response.read(2_000_000)
    except (OSError, URLError) as exc:
        return "", f"web retrieval failed for {url}: {exc}"
    if "pdf" in content_type.lower() or url.lower().endswith(".pdf"):
        return "", "web PDF retrieval is detected but PDF parsing from remote bytes is not enabled in this MVP"
    return raw.decode("utf-8", errors="replace"), None


def _source_records(payload: dict[str, Any], *, allow_web: bool = False) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []

    def add_record(item: dict[str, Any], idx: int) -> None:
        source_id = str(item.get("id") or item.get("path") or item.get("url") or f"source_{idx}")
        kind = str(item.get("kind") or "text")
        retrieval_status = "present"
        note = ""
        text = ""
        if isinstance(item.get("text"), str):
            text = item["text"]
        elif isinstance(item.get("url"), str):
            kind = kind if kind != "text" else "web"
            text, maybe_note = _read_url_source(item["url"], allow_web=allow_web)
            retrieval_status = "retrieved" if text else "not_retrieved"
            note = maybe_note or ""
        elif isinstance(item.get("path"), str):
            path = str(item["path"])
            if path.lower().endswith(".pdf") or kind == "pdf":
                kind = "pdf"
                text, maybe_note = _read_pdf_source_path(path)
                retrieval_status = "parsed" if text else "not_parsed"
                note = maybe_note or ""
            else:
                text = _read_source_path(path)
                retrieval_status = "read"
        records.append(
            {
                "source_id": source_id,
                "kind": kind,
                "text": text,
                "retrieval_status": retrieval_status,
                "retrieval_note": note,
            }
        )

    source = payload.get("source")
    if isinstance(source, dict):
        add_record(source, 0)
    sources = payload.get("sources")
    if isinstance(sources, list):
        for idx, item in enumerate(sources):
            if isinstance(item, dict):
                add_record(item, idx)
    return records


def _field_pattern(field: str) -> str:
    return field.replace("_", r"[_\s-]?")


def _span(source: dict[str, str], line_number: int, line: str, field: str, parser: str) -> dict[str, Any]:
    return {
        "field": field,
        "source_id": source["source_id"],
        "source_kind": source["kind"],
        "line": line_number,
        "snippet": line.strip(),
        "parser": parser,
    }


def _extract_number(text: str, field: str) -> float | None:
    field_pattern = _field_pattern(field)
    match = re.search(rf"\b{field_pattern}\b\s*[:=]\s*({NUMBER_PATTERN})", text, re.IGNORECASE)
    if not match:
        return None
    return float(match.group(1))


def _parse_bool(raw: str) -> bool:
    return raw.lower() in {"true", "yes", "pass", "passed", "1"}


def _extract_bool(text: str, field: str) -> bool | None:
    field_pattern = _field_pattern(field)
    match = re.search(rf"\b{field_pattern}\b\s*[:=]\s*{BOOLEAN_PATTERN}", text, re.IGNORECASE)
    if not match:
        return None
    return _parse_bool(match.group(1))


def _extract_string(text: str, field: str) -> str | None:
    field_pattern = _field_pattern(field)
    match = re.search(
        rf"\b{field_pattern}\b\s*[:=]\s*([A-Za-z0-9_.:/-]+)",
        text,
        re.IGNORECASE,
    )
    if not match:
        return None
    return match.group(1)


def _extract_field_from_sources(
    sources: list[dict[str, str]],
    field: str,
    parser: str,
) -> tuple[Any, dict[str, Any] | None]:
    field_pattern = _field_pattern(field)
    if parser == "number":
        pattern = rf"\b{field_pattern}\b\s*[:=]\s*({NUMBER_PATTERN})"
    elif parser == "boolean":
        pattern = rf"\b{field_pattern}\b\s*[:=]\s*{BOOLEAN_PATTERN}"
    else:
        pattern = rf"\b{field_pattern}\b\s*[:=]\s*([A-Za-z0-9_.:/-]+)"

    for source in sources:
        for line_number, line in enumerate(source["text"].splitlines(), start=1):
            match = re.search(pattern, line, re.IGNORECASE)
            if not match:
                continue
            raw = match.group(1)
            if parser == "number":
                value: Any = float(raw)
            elif parser == "boolean":
                value = _parse_bool(raw)
            else:
                value = raw.rstrip(".,;)")
            return value, _span(source, line_number, line, field, parser)
    return None, None


def retrieve_evidence_snippets(payload: dict[str, Any], *, allow_web: bool = False) -> list[dict[str, Any]]:
    """Return local source lines likely relevant to required evidence fields."""

    claim = payload.get("claim", {}) if isinstance(payload, dict) else {}
    claim_type = claim.get("type") if isinstance(claim, dict) else None
    fields = REQUIRED_DECISION_FIELDS.get(str(claim_type), [])
    snippets: list[dict[str, Any]] = []
    for source in _source_records(payload, allow_web=allow_web):
        if source.get("retrieval_note"):
            snippets.append(
                {
                    "source_id": source["source_id"],
                    "source_kind": source["kind"],
                    "line": None,
                    "snippet": "",
                    "matched_fields": [],
                    "retrieval_status": source.get("retrieval_status"),
                    "retrieval_note": source.get("retrieval_note"),
                }
            )
            continue
        for line_number, line in enumerate(source["text"].splitlines(), start=1):
            lowered = line.lower()
            matched = [field for field in fields if re.search(rf"\b{_field_pattern(field)}\b", lowered)]
            if matched:
                snippets.append(
                    {
                        "source_id": source["source_id"],
                        "source_kind": source["kind"],
                        "line": line_number,
                        "snippet": line.strip(),
                        "matched_fields": matched,
                        "retrieval_status": source.get("retrieval_status"),
                    }
                )
    return snippets


def extract_evidence(payload: dict[str, Any], *, allow_web: bool = False) -> dict[str, Any]:
    """Extract explicit evidence assignments from local text/code/log sources."""

    claim = payload.get("claim", {}) if isinstance(payload, dict) else {}
    sources = _source_records(payload, allow_web=allow_web)
    extracted: dict[str, Any] = {}
    evidence_spans: dict[str, dict[str, Any]] = {}
    extraction_notes: list[str] = [
        source["retrieval_note"]
        for source in sources
        if source.get("retrieval_note")
    ]

    for field in ("abs_error", "tolerance"):
        value, span = _extract_field_from_sources(sources, field, "number")
        if span is not None:
            extracted[field] = value
            evidence_spans[field] = span

    for field in (
        "within_chemical_accuracy",
        "local_property_tests_pass",
        "universal_anchor_pass",
        "upgrade_evidence_present",
    ):
        value, span = _extract_field_from_sources(sources, field, "boolean")
        if span is not None:
            extracted[field] = value
            evidence_spans[field] = span

    for field in (
        "anchor_mode",
        "physical_evidence_level",
        "verification_independence",
        "bound_scope",
    ):
        value, span = _extract_field_from_sources(sources, field, "string")
        if span is not None:
            extracted[field] = value
            evidence_spans[field] = span

    if not sources:
        extraction_notes.append("no source text was supplied")

    claim_type = claim.get("type") if isinstance(claim, dict) else None
    required = REQUIRED_DECISION_FIELDS.get(str(claim_type), [])
    missing = [
        field
        for field in required
        if field not in extracted or extracted.get(field) in {None, "unknown"}
    ]
    if not extracted:
        status = "none"
    elif missing:
        status = "partial"
    else:
        status = "complete"

    candidate_payload = {
        "claim": claim,
        "evidence": {
            **(payload.get("evidence", {}) if isinstance(payload.get("evidence"), dict) else {}),
            **extracted,
        },
    }

    return {
        "extraction_status": status,
        "extracted_evidence": extracted,
        "evidence_spans": evidence_spans,
        "retrieved_snippets": retrieve_evidence_snippets(payload, allow_web=allow_web),
        "candidate_payload": candidate_payload,
        "required_fields": required,
        "missing_fields_after_extraction": missing,
        "extraction_notes": extraction_notes,
        "non_claim": "This parser extracts explicit local assignments only; it does not retrieve literature or infer hidden evidence.",
    }


def scientific_reasoning_report(
    candidate_payload: dict[str, Any],
    extraction: dict[str, Any],
    alignment: dict[str, Any],
    gate_decision: dict[str, Any],
) -> dict[str, Any]:
    """A deterministic scientific-reasoning checklist over CAPAS outputs.

    This is not a scientific oracle. It names obvious scope, evidence, and
    independence risks so the final gate is not confused with broad reasoning.
    """

    claim = candidate_payload.get("claim", {}) if isinstance(candidate_payload, dict) else {}
    evidence = candidate_payload.get("evidence", {}) if isinstance(candidate_payload, dict) else {}
    claim_type = claim.get("type") if isinstance(claim, dict) else None
    risks: list[str] = []
    recommendations: list[str] = []

    if extraction["extraction_status"] != "complete":
        risks.append("required evidence is not completely extracted")
        recommendations.append("HOLD until required evidence fields are present with source spans")

    missing_spans = [
        field
        for field in extraction.get("required_fields", [])
        if field not in extraction.get("evidence_spans", {})
    ]
    if missing_spans:
        risks.append(f"required fields lack auditable source spans: {missing_spans}")
        recommendations.append("do not accept claims whose required evidence cannot be traced to source snippets")

    if alignment["alignment_status"] == "MISALIGNED":
        risks.append("claim prose overstates or changes evidence scope")
        recommendations.append("rewrite claim text to the strongest scope licensed by structured evidence")

    if claim_type == "exact_model_solution" and evidence.get("physical_evidence_level") == "experimental":
        risks.append("exact_model_solution is mixed with experimental evidence level")
        recommendations.append("separate exact model correctness from physical/experimental accuracy")

    if claim_type == "physical_accuracy" and "reference_truth" not in evidence:
        risks.append("physical_accuracy claim lacks declared reference_truth")
        recommendations.append("declare experimental/reference truth before accepting physical accuracy")

    if claim_type == "universal_anchor_claim" and evidence.get("anchor_mode") != "absolute_anchor":
        risks.append("universal anchor claim lacks absolute_anchor mode")
        recommendations.append("downgrade to local/property plausibility unless an absolute anchor is declared")

    if evidence.get("verification_independence") in {None, "unknown", "same_runtime"}:
        risks.append("verification independence is weak or undeclared")
        recommendations.append("prefer independent witness, analytic reference, or no-solver theoretical anchor")

    if gate_decision["verdict"] == "ACCEPT" and risks:
        status = "BLOCK_ACCEPT"
    elif risks:
        status = "WARN"
    else:
        status = "CLEAR"

    return {
        "reasoning_status": status,
        "risks": risks,
        "recommendations": recommendations,
        "non_claim": "This is a deterministic checklist for scope/evidence risks, not broad scientific reasoning or literature understanding.",
    }


def standalone_pipeline(payload: dict[str, Any], *, allow_web: bool = False) -> dict[str, Any]:
    """Run the local standalone MVP: extract -> align -> deterministic gate."""

    extraction = extract_evidence(payload, allow_web=allow_web)
    candidate = extraction["candidate_payload"]
    alignment = align_claim_text(candidate)
    gate_decision = decide_external_claim(candidate)
    reasoning = scientific_reasoning_report(candidate, extraction, alignment, gate_decision)

    final_decision = dict(gate_decision)
    if alignment["alignment_status"] == "MISALIGNED" and gate_decision["verdict"] == "ACCEPT":
        final_decision.update(
            {
                "verdict": "HOLD",
                "reason": "semantic alignment failed before an ACCEPT claim can be licensed",
                "licensed_claim": None,
                "rewrite": None,
            }
        )
    elif alignment["alignment_status"] == "MISALIGNED" and gate_decision["verdict"] == "REWRITE":
        final_decision["reason"] = f"{gate_decision['reason']}; semantic alignment also found overclaim"
    elif reasoning["reasoning_status"] == "BLOCK_ACCEPT" and gate_decision["verdict"] == "ACCEPT":
        final_decision.update(
            {
                "verdict": "HOLD",
                "reason": "scientific reasoning checklist found unresolved evidence/scope risks before ACCEPT",
                "licensed_claim": None,
                "rewrite": None,
            }
        )

    return {
        "pipeline_status": "PASS" if final_decision["verdict"] in {"ACCEPT", "REWRITE", "REJECT", "HOLD"} else "ERROR",
        "extraction": extraction,
        "semantic_alignment": alignment,
        "scientific_reasoning": reasoning,
        "capas_gate_decision": gate_decision,
        "final_decision": final_decision,
        "fine_tune_ready": False,
        "non_claims": [
            "local extraction is regex-based and explicit-only",
            "semantic alignment is deterministic lexical/scope checking, not general scientific reasoning",
            "CAPAS still requires external scientific witnesses for new claim types",
        ],
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


def _ui_samples() -> dict[str, dict[str, Any]]:
    return {
        "ACCEPT": _sample_external_claim(),
        "REWRITE": {
            "claim": {
                "id": "sample_scaling_claim_rewrite",
                "type": "universal_anchor_claim",
                "text": "Local monotonicity proves universal physical correctness.",
            },
            "evidence": {
                "anchor_mode": "absolute_anchor",
                "local_property_tests_pass": True,
                "universal_anchor_pass": False,
                "physical_evidence_level": "scaling_law_anchor",
                "verification_independence": "theory_scaling_law_no_solver",
            },
        },
        "REJECT": {
            "claim": {
                "id": "sample_scaling_claim_reject",
                "type": "universal_anchor_claim",
                "text": "The generated result is physically consistent.",
            },
            "evidence": {
                "anchor_mode": "absolute_anchor",
                "local_property_tests_pass": False,
                "universal_anchor_pass": False,
                "physical_evidence_level": "failed_local_checks",
                "verification_independence": "local_properties_no_anchor_needed",
            },
        },
        "HOLD": {
            "claim": {
                "id": "sample_experiment_hold",
                "type": "physical_accuracy",
                "text": "The simulation matches experiment.",
            },
            "evidence": {
                "physical_evidence_level": "experimental",
                "reference_truth": "external experimental reference supplied without tolerance verdict",
            },
        },
        "INVALID": {
            "claim": {
                "id": "",
                "type": "unsupported_claim_type",
                "text": "This payload is structurally invalid because the claim id is empty.",
            },
            "evidence": "not an object",
        },
    }


def _render_ui(sample: dict[str, Any]) -> str:
    samples = _ui_samples()
    sample_json = json.dumps(sample, indent=2, sort_keys=True)
    samples_json = json.dumps(samples, sort_keys=True)
    html = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="CAPAS Claim Gate deterministically checks structured scientific claims and returns ACCEPT, REJECT, REWRITE, or HOLD without an LLM at decision time.">
<meta property="og:title" content="CAPAS Claim Gate">
<meta property="og:description" content="A deterministic gate for structured scientific claims with schema validation, licensed rewrites, and evidence-aware HOLD decisions.">
<meta property="og:type" content="website">
<meta property="og:url" content="https://fomv9354lve.github.io/capas-inteligentes/">
<meta property="og:image" content="https://fomv9354lve.github.io/capas-inteligentes/capas-social-card.svg">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="CAPAS Claim Gate">
<meta name="twitter:description" content="Deterministic ACCEPT / REJECT / REWRITE / HOLD decisions for structured scientific claims.">
<meta name="twitter:image" content="https://fomv9354lve.github.io/capas-inteligentes/capas-social-card.svg">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; img-src 'self' data:; style-src 'unsafe-inline'; script-src 'unsafe-inline'; object-src 'none'; base-uri 'none'; form-action 'none'; connect-src 'none'">
<title>CAPAS Claim Gate</title>
<style>
  /* CAPAS Claim Gate - Design System v11 */
  :root {
    --bg: #09090b;
    --bg-2: #111113;
    --bg-3: #18181b;
    --bg-4: #1c1c1f;
    --border: #27272a;
    --border-2: #3f3f46;
    --text-1: #fafafa;
    --text-2: #a1a1aa;
    --text-3: #8d8d99;
    --accent: #7c7fff;
    --accent-hover: #818cf8;
    --accent-glow: rgba(99, 102, 241, 0.15);
    --accent-start: #6366f1;
    --accent-end: #8b5cf6;
    --green: #22c55e;
    --green-bg: rgba(34, 197, 94, 0.08);
    --green-border: rgba(34, 197, 94, 0.2);
    --orange: #f97316;
    --orange-bg: rgba(249, 115, 22, 0.08);
    --orange-border: rgba(249, 115, 22, 0.2);
    --red: #ef4444;
    --red-bg: rgba(239, 68, 68, 0.08);
    --red-border: rgba(239, 68, 68, 0.2);
    --slate: #94a3b8;
    --slate-bg: rgba(148, 163, 184, 0.08);
    --slate-border: rgba(148, 163, 184, 0.15);
    --draft: #f59e0b;
    --warning: #fbbf24;
    --error-soft: #fca5a5;
    --assist-text: #c7d2fe;
    --json-key: #93c5fd;
    --json-string: #86efac;
    --json-number: #fbbf24;
    --json-boolean: #c4b5fd;
    --json-null: #fca5a5;
    --radius-sm: 6px;
    --radius: 10px;
    --radius-lg: 14px;
    --shadow: 0 4px 16px rgba(0, 0, 0, 0.5);
    --font: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    --mono: ui-monospace, "SF Mono", "Fira Code", Menlo, monospace;
    --t: 0.15s cubic-bezier(0.4, 0, 0.2, 1);
  }
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    margin: 0;
    padding: 0;
    max-width: none;
    font-family: var(--font);
    background: var(--bg);
    color: var(--text-1);
    line-height: 1.5;
    -webkit-font-smoothing: antialiased;
  }
  html[data-theme="dark"] {
    color-scheme: dark;
  }
  html[data-theme="light"] {
    --bg: #ffffff;
    --bg-2: #fafafa;
    --bg-3: #f4f4f5;
    --bg-4: #e4e4e7;
    --border: #e4e4e7;
    --border-2: #d4d4d8;
    --text-1: #09090b;
    --text-2: #52525b;
    --text-3: #6f6f7a;
    --accent: #4f46e5;
    --green: #15803d;
    --draft: #b45309;
    --json-key: #1d4ed8;
    --json-string: #15803d;
    --json-number: #b45309;
    --json-boolean: #7c3aed;
    --json-null: #dc2626;
    --shadow: 0 4px 16px rgba(24, 24, 27, 0.08);
    color-scheme: light;
  }
  .skip-link {
    position: absolute;
    left: 12px;
    top: 8px;
    z-index: 100;
    transform: translateY(-140%);
    background: var(--accent);
    color: white;
    border-radius: var(--radius-sm);
    padding: 8px 12px;
    font-size: 12px;
    font-weight: 700;
    text-decoration: none;
    transition: transform var(--t);
  }
  .skip-link:focus { transform: translateY(0); }
  .topbar {
    position: sticky;
    top: 0;
    z-index: 50;
    height: 52px;
    padding: 0 28px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    background: rgba(9, 9, 11, 0.85);
    backdrop-filter: blur(12px);
    border-bottom: 1px solid var(--border);
  }
  .topbar-left { display: flex; align-items: center; gap: 12px; min-width: 0; }
  .topbar-logo { display: flex; align-items: center; gap: 8px; font-size: 14px; font-weight: 800; color: var(--text-1); white-space: nowrap; }
  .topbar-logo-icon {
    width: 26px;
    height: 26px;
    border-radius: 7px;
    background: linear-gradient(135deg, var(--accent-start), var(--accent-end));
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    font-weight: 800;
    color: white;
    box-shadow: 0 2px 8px rgba(99, 102, 241, 0.4);
  }
  .topbar-divider { width: 1px; height: 18px; background: var(--border); flex-shrink: 0; }
  .topbar-subtitle { font-size: 12px; color: var(--text-3); font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .topbar-subtitle code { color: var(--text-2); background: var(--bg-3); padding: 1px 5px; border-radius: 4px; }
  .topbar-badge {
    font-size: 10px;
    font-weight: 700;
    color: var(--accent-hover);
    background: var(--accent-glow);
    border: 1px solid rgba(99, 102, 241, 0.25);
    padding: 2px 8px;
    border-radius: 20px;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    white-space: nowrap;
  }
  .app-body { max-width: 1280px; margin: 0 auto; padding: 24px 28px 60px; }
  .samples-bar { display: flex; flex-wrap: wrap; align-items: center; gap: 6px; margin-bottom: 20px; }
  .samples-bar > span { font-size: 11px; color: var(--text-3); text-transform: uppercase; letter-spacing: 0.6px; }
  .sample-btn {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 5px 13px;
    border-radius: var(--radius-sm);
    border: 1px solid var(--border);
    background: var(--bg-3);
    font-family: var(--font);
    font-size: 11px;
    color: var(--text-2);
    cursor: pointer;
    transition: all var(--t);
  }
  .sample-btn:hover { border-color: var(--border-2); color: var(--text-1); background: var(--bg-4); box-shadow: 0 1px 2px rgba(0, 0, 0, 0.4); }
  .sample-btn.accept { color: var(--green); border-color: var(--green-border); background: var(--green-bg); }
  .sample-btn.rewrite { color: var(--orange); border-color: var(--orange-border); background: var(--orange-bg); }
  .sample-btn.hold { color: var(--slate); border-color: var(--slate-border); background: var(--slate-bg); }
  .sample-btn.invalid { color: var(--red); border-color: var(--red-border); background: var(--red-bg); }
  .grid { display: grid; grid-template-columns: minmax(380px, 42%) minmax(0, 1fr); gap: 16px; align-items: start; }
  .grid > div { min-width: 0; }
  .panel {
    background: var(--bg-2);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow);
    transition: border-color var(--t);
    overflow: hidden;
  }
  .panel, .output-section { min-width: 0; }
  .panel:focus-within { border-color: var(--border-2); }
  .panel-header { display: flex; align-items: center; justify-content: space-between; padding: 10px 16px; min-height: 42px; background: var(--bg-3); border-bottom: 1px solid var(--border); }
  .panel-title { font-size: 11px; font-weight: 700; color: var(--text-3); letter-spacing: 0.7px; }
  .panel-tag {
    font-size: 11px;
    font-weight: 500;
    color: var(--accent-hover);
    background: var(--accent-glow);
    border: 1px solid rgba(99, 102, 241, 0.2);
    padding: 2px 8px;
    border-radius: 20px;
    font-family: var(--mono);
    max-width: 220px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .panel-tag:empty { display: none; }
  #input {
    width: 100%;
    min-width: 0;
    max-width: 100%;
    min-height: 380px;
    background: transparent;
    color: var(--text-1);
    font-family: var(--mono);
    font-size: 12.5px;
    line-height: 1.7;
    padding: 16px;
    caret-color: var(--accent);
    border: none;
    outline: none;
    resize: vertical;
    display: block;
    transition: box-shadow var(--t);
  }
  #input.ok-border { box-shadow: inset 3px 0 0 var(--green); }
  #input.error-border { box-shadow: inset 3px 0 0 var(--red); }
  .json-status { min-height: 32px; padding: 7px 16px; color: var(--text-3); border-top: 1px solid var(--border); display: flex; align-items: center; gap: 6px; font-size: 11px; font-weight: 600; }
  .json-status::before { content: "●"; font-size: 8px; }
  .json-status.valid { color: var(--green); }
  .json-status.invalid { color: var(--red); }
  .json-status.draft { color: var(--draft); }
  .json-status.draft::before { content: "◐"; }
  .action-row { display: grid; grid-template-columns: 1fr 2fr; border-top: 1px solid var(--border); }
  .draft-btn {
    width: 100%;
    padding: 13px;
    background: var(--bg-4);
    color: var(--text-2);
    border: none;
    border-right: 1px solid var(--border);
    font-family: var(--font);
    font-size: 13px;
    font-weight: 700;
    cursor: pointer;
    transition: all var(--t);
  }
  .draft-btn:hover { background: var(--bg-3); color: var(--text-1); }
  .decide-btn {
    width: 100%;
    padding: 13px;
    background: linear-gradient(135deg, var(--accent), var(--accent-end));
    color: white;
    border: none;
    border-top: 1px solid rgba(255, 255, 255, 0.05);
    font-family: var(--font);
    font-size: 13px;
    font-weight: 700;
    position: relative;
    overflow: hidden;
    transition: all var(--t);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
  }
  .decide-btn::before { content: ""; position: absolute; inset: 0; background: linear-gradient(135deg, rgba(255, 255, 255, 0.1), transparent); opacity: 0; transition: opacity var(--t); }
  .decide-btn:hover::before { opacity: 1; }
  .decide-btn:hover { box-shadow: 0 4px 20px rgba(99, 102, 241, 0.35); }
  .decide-btn.processing { animation: pulse-btn 1s ease-in-out infinite; }
  @keyframes pulse-btn {
    0%, 100% { box-shadow: 0 0 0 0 rgba(99, 102, 241, 0.4); }
    50% { box-shadow: 0 0 0 6px rgba(99, 102, 241, 0); }
  }
  .decide-hint { font-size: 10px; opacity: 0.55; background: rgba(255, 255, 255, 0.1); border-radius: 4px; padding: 2px 6px; }
  .copy-btn { display: inline-flex; align-items: center; gap: 5px; padding: 4px 12px; background: var(--bg-4); border: 1px solid var(--border); border-radius: var(--radius-sm); color: var(--text-2); font-family: var(--font); font-size: 11px; font-weight: 600; cursor: pointer; transition: all var(--t); }
  .copy-btn:not(:disabled):hover { background: var(--bg-3); border-color: var(--border-2); color: var(--text-1); }
  .copy-btn:disabled { opacity: 0.35; cursor: not-allowed; }
  .copy-btn.copied { background: var(--green-bg); border-color: var(--green-border); color: var(--green); }
  .topbar-actions { display: flex; align-items: center; gap: 8px; flex-shrink: 0; }
  .history-actions { display: flex; align-items: center; gap: 8px; }
  .verdict-banner { display: flex; align-items: center; gap: 14px; padding: 16px 18px; border-bottom: 1px solid var(--border); }
  .verdict-badge { font-size: 11px; font-weight: 800; letter-spacing: 1.2px; border: 1px solid transparent; text-transform: uppercase; padding: 4px 13px; border-radius: 20px; white-space: nowrap; flex-shrink: 0; }
  .verdict-badge.ACCEPT { background: var(--green-bg); color: var(--green); border-color: var(--green-border); }
  .verdict-badge.REJECT { background: var(--red-bg); color: var(--red); border-color: var(--red-border); }
  .verdict-badge.REWRITE { background: var(--orange-bg); color: var(--orange); border-color: var(--orange-border); }
  .verdict-badge.HOLD { background: var(--slate-bg); color: var(--slate); border-color: var(--slate-border); }
  .verdict-reason { color: var(--text-2); }
  .alert-block { margin: 12px 16px; padding: 12px 14px; border-radius: var(--radius); border: 1px solid; font-size: 12px; line-height: 1.7; }
  .alert-block.missing { background: rgba(251, 191, 36, 0.06); border-color: rgba(251, 191, 36, 0.2); color: var(--warning); }
  .alert-block.errors { background: var(--red-bg); border-color: var(--red-border); color: var(--error-soft); }
  .assist-block { margin: 12px 16px; padding: 12px 14px; border-radius: var(--radius); background: var(--accent-glow); border-color: rgba(99, 102, 241, 0.24); color: var(--assist-text); }
  .assist-block pre { background: var(--bg); border-color: rgba(99, 102, 241, 0.24); color: var(--assist-text); }
  .batch-progress { margin-top: 10px; height: 8px; overflow: hidden; border: 1px solid var(--border); border-radius: 999px; background: var(--bg); }
  .batch-progress-fill { height: 100%; width: var(--batch-progress, 100%); background: linear-gradient(90deg, var(--accent), var(--green)); }
  .batch-progress-label { margin-top: 6px; color: var(--text-3); font-size: 11px; font-weight: 600; }
  .batch-table { display: grid; gap: 6px; margin-top: 12px; }
  .batch-row { border: 1px solid var(--border); border-radius: var(--radius-sm); background: var(--bg); overflow: hidden; }
  .batch-row summary { display: grid; grid-template-columns: auto minmax(0, 1fr) minmax(0, 1.4fr); gap: 8px; align-items: center; padding: 8px 10px; cursor: pointer; list-style: none; }
  .batch-row summary::-webkit-details-marker { display: none; }
  .batch-row-id, .batch-row-reason { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .batch-row-id { color: var(--text-1); font-family: var(--mono); font-size: 11px; }
  .batch-row-reason { color: var(--text-3); font-size: 11px; }
  .batch-row pre { margin: 0; border-top: 1px solid var(--border); border-radius: 0; max-height: 220px; overflow: auto; }
  .rewrite-block { margin: 12px 16px; padding: 12px 14px; border-radius: var(--radius); background: var(--orange-bg); border-color: var(--orange-border); }
  .rewrite-text { color: var(--text-1); }
  .rewrite-diff { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 10px; }
  .rewrite-pane { background: var(--bg); border: 1px solid var(--orange-border); border-radius: var(--radius-sm); padding: 10px; min-width: 0; }
  .rewrite-pane-label { font-size: 10px; font-weight: 700; color: var(--orange); text-transform: uppercase; letter-spacing: 0.7px; margin-bottom: 5px; }
  .rewrite-pane-text { font-size: 12px; color: var(--text-2); line-height: 1.5; overflow-wrap: anywhere; }
  .output-section { padding: 12px 16px; }
  .output-label { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.7px; color: var(--text-3); }
  .output-label::after { content: ""; flex: 1; height: 1px; background: var(--border); }
  pre#output { background: var(--bg); border: 1px solid var(--border); border-radius: var(--radius); color: var(--text-2); max-width: 100%; min-width: 0; max-height: 360px; padding: 14px; font-size: 11.5px; font-family: var(--mono); line-height: 1.7; overflow: auto; white-space: pre; }
  .json-key { color: var(--json-key); }
  .json-string { color: var(--json-string); }
  .json-number { color: var(--json-number); }
  .json-boolean { color: var(--json-boolean); }
  .json-null { color: var(--json-null); }
  pre#output::-webkit-scrollbar { width: 6px; height: 6px; }
  pre#output::-webkit-scrollbar-track { background: transparent; }
  pre#output::-webkit-scrollbar-thumb { background: var(--border-2); border-radius: 3px; }
  .history-section { margin-top: 24px; }
  .history-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; }
  .history-heading { color: var(--text-3); font-size: 11px; font-weight: 700; letter-spacing: 0.7px; text-transform: uppercase; }
  .history-list { display: flex; flex-direction: column; gap: 4px; }
  .history-count { color: var(--text-3); }
  .history-row { display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 6px; align-items: stretch; }
  .history-item { display: flex; align-items: center; gap: 10px; width: 100%; padding: 9px 14px; background: var(--bg-2); border: 1px solid var(--border); border-radius: var(--radius); color: var(--text-1); font-family: var(--font); transition: all var(--t); cursor: pointer; text-align: left; }
  .history-item:hover { background: var(--bg-3); border-color: var(--border-2); transform: translateX(2px); }
  .history-delete { padding: 0 10px; border: 1px solid var(--border); border-radius: var(--radius); background: var(--bg-2); color: var(--text-3); font-family: var(--font); font-size: 11px; font-weight: 700; cursor: pointer; }
  .history-delete:hover { color: var(--red); border-color: var(--red-border); background: var(--red-bg); }
  .history-badge { border: 1px solid; }
  .history-badge.ACCEPT { color: var(--green); background: var(--green-bg); border-color: var(--green-border); }
  .history-badge.REJECT { color: var(--red); background: var(--red-bg); border-color: var(--red-border); }
  .history-badge.REWRITE { color: var(--orange); background: var(--orange-bg); border-color: var(--orange-border); }
  .history-badge.HOLD { color: var(--slate); background: var(--slate-bg); border-color: var(--slate-border); }
  .history-id { color: var(--text-1); }
  .history-reason { color: var(--text-3); }
  .history-ts { margin-left: auto; color: var(--text-3); font-size: 10px; font-variant-numeric: tabular-nums; white-space: nowrap; }
  .empty-state, .no-decision { color: var(--text-3); font-size: 13px; }
  .no-decision { padding: 32px 16px; text-align: center; }
  .modal-backdrop {
    position: fixed;
    inset: 0;
    z-index: 80;
    display: none;
    align-items: center;
    justify-content: center;
    padding: 20px;
    background: rgba(0, 0, 0, 0.55);
  }
  .modal-backdrop.open { display: flex; }
  .help-modal {
    width: min(680px, 100%);
    max-height: 86vh;
    overflow: auto;
    background: var(--bg-2);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow);
    padding: 18px;
  }
  .help-modal h2 { font-size: 15px; margin-bottom: 10px; }
  .help-modal h3 { font-size: 11px; color: var(--text-3); letter-spacing: 0.7px; text-transform: uppercase; margin: 16px 0 6px; }
  .help-modal p, .help-modal li { color: var(--text-2); font-size: 13px; line-height: 1.6; }
  .help-modal ul { padding-left: 18px; }
  .claim-type-list { display: grid; gap: 6px; margin-top: 8px; padding-left: 0; list-style: none; }
  .claim-type-list li { padding: 8px 10px; border: 1px solid var(--border); border-radius: var(--radius-sm); background: var(--bg); }
  .help-modal code { background: var(--bg-3); color: var(--text-1); padding: 1px 5px; border-radius: 4px; }
  .app-footer {
    margin-top: 28px;
    padding-top: 16px;
    border-top: 1px solid var(--border);
    color: var(--text-3);
    font-size: 11px;
    line-height: 1.6;
  }
  :focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
  @media (prefers-color-scheme: light) {
    :root {
      --bg: #ffffff;
      --bg-2: #fafafa;
      --bg-3: #f4f4f5;
      --bg-4: #e4e4e7;
      --border: #e4e4e7;
      --border-2: #d4d4d8;
      --text-1: #09090b;
      --text-2: #52525b;
      --text-3: #6f6f7a;
      --accent: #4f46e5;
      --green: #15803d;
      --draft: #b45309;
      --json-key: #1d4ed8;
      --json-string: #15803d;
      --json-number: #b45309;
      --json-boolean: #7c3aed;
      --json-null: #dc2626;
      --shadow: 0 4px 16px rgba(24, 24, 27, 0.08);
    }
    .topbar { background: rgba(255, 255, 255, 0.9); }
    pre#output { background: var(--bg-3); }
  }
  html[data-theme="light"] .topbar { background: rgba(255, 255, 255, 0.9); }
  html[data-theme="light"] pre#output { background: var(--bg-3); }
  @media (max-width: 860px) {
    .app-body { padding: 16px 16px 60px; }
    .topbar {
      height: auto;
      min-height: 52px;
      align-items: flex-start;
      flex-wrap: wrap;
      gap: 8px;
      padding: 8px 16px;
    }
    .topbar-left { flex: 1 1 auto; max-width: 100%; }
    .topbar-actions {
      order: 2;
      flex: 1 0 100%;
      width: 100%;
      min-width: 0;
      max-width: 100%;
      justify-content: flex-start;
      overflow-x: auto;
      padding-bottom: 2px;
      scrollbar-width: none;
    }
    .topbar-actions::-webkit-scrollbar { display: none; }
    .topbar-subtitle { display: none; }
    .topbar-badge, .topbar-actions .copy-btn { flex: 0 0 auto; }
    .samples-bar {
      flex-wrap: nowrap;
      overflow-x: auto;
      padding-bottom: 4px;
      scrollbar-width: none;
    }
    .samples-bar::-webkit-scrollbar { display: none; }
    .sample-btn { flex: 0 0 auto; }
    .grid { grid-template-columns: 1fr; }
    #input { min-height: 260px; }
    pre#output { max-height: 280px; }
    .rewrite-diff { grid-template-columns: 1fr; }
    .modal-backdrop { align-items: stretch; padding: 12px; }
    .help-modal { width: 100%; max-height: calc(100vh - 24px); }
    .history-header { align-items: flex-start; gap: 12px; }
    .history-actions { flex-wrap: wrap; justify-content: flex-end; }
    .history-item { align-items: flex-start; flex-wrap: wrap; }
    .history-reason { flex-basis: 100%; overflow-wrap: anywhere; }
  }
  @media (max-width: 560px) {
    .app-body { padding: 12px 12px 48px; }
    .topbar-logo { font-size: 13px; }
    .topbar-logo-icon { width: 24px; height: 24px; }
    .panel-header { padding: 9px 12px; }
    #input { min-height: 220px; padding: 12px; font-size: 12px; }
    .action-row { grid-template-columns: 1fr; }
    .draft-btn { border-right: 0; border-bottom: 1px solid var(--border); }
    .decide-btn, .draft-btn { min-height: 44px; }
    .verdict-banner { align-items: flex-start; flex-direction: column; gap: 8px; padding: 14px; }
    .alert-block, .assist-block, .rewrite-block, .output-section { margin-left: 12px; margin-right: 12px; }
    .output-section { padding: 12px; }
    pre#output { max-height: 240px; padding: 12px; font-size: 11px; }
    .help-modal { padding: 14px; border-radius: var(--radius); }
  }
</style>
</head>
<body>

<a class="skip-link" href="#main">Skip to claim gate</a>
<header class="topbar">
  <div class="topbar-left">
    <h1 class="topbar-logo" aria-label="CAPAS Claim Gate">
      <div class="topbar-logo-icon" aria-hidden="true">CG</div>
      CAPAS Claim Gate
    </h1>
    <div class="topbar-divider"></div>
    <span class="topbar-subtitle">Rule-based via <code>capas.py decide</code> · schema errors → <code>HOLD</code></span>
  </div>
  <div class="topbar-actions">
    <button class="copy-btn" id="help-btn" aria-label="Open keyboard shortcut and pipeline help" aria-expanded="false" onclick="openHelpModal(this)">Help</button>
    <button class="copy-btn" id="theme-toggle" aria-label="Toggle light and dark theme" onclick="toggleTheme()">Theme</button>
    <span class="topbar-badge" id="schema-version-badge">schema v2</span>
    <span class="topbar-badge" id="shared-payload-badge" hidden>shared payload</span>
    <span class="topbar-badge">__UI_VERSION__</span>
  </div>
</header>

<main class="app-body" id="main">
<div class="samples-bar">
  <span>Load sample:</span>
  <button class="sample-btn accept" title="ACCEPT sample" aria-label="Load ACCEPT sample" onclick="loadSample('ACCEPT')">&#10003; ACCEPT</button>
  <button class="sample-btn rewrite" title="REWRITE sample" aria-label="Load REWRITE sample" onclick="loadSample('REWRITE')">&#8634; REWRITE</button>
  <button class="sample-btn invalid" title="REJECT sample" aria-label="Load REJECT sample" onclick="loadSample('REJECT')">&#10005; REJECT</button>
  <button class="sample-btn hold" title="HOLD sample" aria-label="Load HOLD sample" onclick="loadSample('HOLD')">&#9646; HOLD</button>
  <button class="sample-btn invalid" title="Invalid schema sample that resolves to HOLD" aria-label="Load INVALID schema sample" onclick="loadSample('INVALID')">&#9888; INVALID</button>
</div>

<div class="grid">
  <div>
    <div class="panel">
      <div class="panel-header">
        <span class="panel-title">Input JSON</span>
        <span class="panel-tag" id="type-label"></span>
      </div>
      <textarea id="input" spellcheck="false" aria-label="Claim and evidence JSON input" aria-describedby="json-status" oninput="scheduleInputChange()">__SAMPLE_JSON__</textarea>
      <div class="json-status" id="json-status">Waiting for input...</div>
      <div class="action-row">
        <button class="draft-btn" id="draft-btn" aria-label="Build draft claim JSON without deciding" onclick="buildDraft()">Build Draft</button>
        <button class="decide-btn" id="decide-btn" aria-label="Decide claim verdict" onclick="decide()">Decide <span class="decide-hint">⌘↵</span></button>
      </div>
      <button class="draft-btn" id="batch-btn" title="Batch input: JSON array, object with items/claims, or one claim payload auto-wrapped as a one-item batch" aria-label="Evaluate a batch of claim payloads" onclick="decideBatch()">Batch</button>
    </div>
  </div>

  <div>
    <div class="panel">
      <div class="panel-header">
        <span class="panel-title">Decision</span>
        <button class="copy-btn" id="copy-btn" aria-label="Copy decision JSON" onclick="copyOutput()" disabled>Copy JSON</button>
      </div>
      <div id="verdict-area" aria-live="polite" aria-atomic="true"><div class="no-decision">Run a decision to see results.</div></div>
      <div class="output-section">
        <div class="output-label"><span>Full output</span></div>
      <pre id="output"></pre>
      </div>
    </div>
  </div>
</div>

<div class="history-section">
  <div class="history-header">
    <h2 class="history-heading">Recent decisions</h2>
    <div class="history-actions">
      <button class="copy-btn" id="share-btn" aria-label="Copy shareable URL for current input. The payload is embedded in the URL; do not share sensitive claims." title="The payload is embedded in the URL; do not share sensitive claims." onclick="copyShareUrl()">Share URL</button>
      <button class="copy-btn" id="export-btn" aria-label="Export decision history as CSV" onclick="exportHistoryCsv()">Export CSV</button>
      <button class="copy-btn" id="clear-history-btn" aria-label="Clear local decision history" onclick="clearHistory()">Clear</button>
      <span class="history-count" id="history-count" aria-live="polite" aria-atomic="true">0/50 saved</span>
    </div>
  </div>
  <div class="history-list" id="history-list">
    <div class="empty-state">No decisions yet.</div>
  </div>
</div>
<footer class="app-footer">
  CAPAS structures and gates supplied claim evidence. It does not infer hidden evidence or certify broad scientific truth.
</footer>
</main>
<div class="modal-backdrop" id="help-modal-backdrop" onclick="closeHelpModal(event)">
  <div class="help-modal" id="help-modal" role="dialog" aria-modal="true" aria-labelledby="help-modal-title" tabindex="-1" onclick="event.stopPropagation()" onkeydown="handleHelpModalKey(event)">
    <div class="panel-header">
      <h2 id="help-modal-title">CAPAS shortcuts and pipeline modes</h2>
      <button class="copy-btn" aria-label="Close help modal" onclick="closeHelpModal()">Close</button>
    </div>
    <h3>Shortcuts</h3>
    <ul>
      <li><code>Cmd/Ctrl + Enter</code>: run Decide on one claim.</li>
      <li><code>?</code>: open or close this help modal.</li>
      <li><code>Enter</code> or <code>Space</code> on a history item: restore it.</li>
    </ul>
    <h3>Batch mode</h3>
    <p>Paste a JSON array, an object with <code>items</code> or <code>claims</code>, or one claim/evidence payload. Batch applies the same deterministic rule to every item and returns a summary. It does not infer missing evidence.</p>
    <h3>Pipeline surfaces</h3>
    <p>The CLI/API support <code>decide</code>, <code>batch</code>, and standalone <code>retrieve → extract → align → reason → pipeline</code>. Retrieval and parsing prepare candidate evidence; the final CAPAS verdict still comes from the deterministic gate.</p>
    <h3>Fine-tune readiness</h3>
    <p><code>fine_tune_ready</code> stays <code>false</code> unless an external review layer supplies source-backed evidence, semantic alignment, witness independence, and review metadata. CAPAS gates claims; it does not silently certify training data.</p>
    <h3>Schema</h3>
    <p>Current payload schema: <code>capas-claim-payload-v2</code>. Outputs include <code>schema_version</code> for audit trails.</p>
    <p>Supported claim types and minimum evidence fields:</p>
    <ul class="claim-type-list">
      <li><code>claim_transition</code>: <code>upgrade_evidence_present</code></li>
      <li><code>exact_model_solution</code>: <code>abs_error</code>, <code>tolerance</code></li>
      <li><code>financial_metric_claim</code>: <code>reported_value</code>, <code>reference_value</code>, <code>tolerance</code>, <code>metric_period_match</code></li>
      <li><code>physical_accuracy</code>: <code>within_chemical_accuracy</code></li>
      <li><code>reproducibility_check</code>: <code>artifact_available</code>, <code>independent_reproduction_pass</code></li>
      <li><code>statistical_confidence</code>: <code>p_value</code>, <code>alpha</code>, <code>effect_direction_confirmed</code></li>
      <li><code>universal_anchor_claim</code>: <code>anchor_mode</code>, <code>local_property_tests_pass</code>, <code>universal_anchor_pass</code></li>
    </ul>
  </div>
</div>

<script>
    const sample = __SAMPLE_COMPACT_JSON__;
    const samples = __SAMPLES_JSON__;
    const capasSchemaVersion = "capas-claim-payload-v2";
    const disallowedAngleRegex = /[<>\u02c2\u02c3\u2039\u203a\u2329-\u232a\u276c-\u276d\u27e8-\u27e9\u29fc-\u29fd\u3008-\u3009\ufe64-\ufe65\uff1c-\uff1e]/u;
    const required = {
      exact_model_solution: ["abs_error", "tolerance"],
      physical_accuracy: ["within_chemical_accuracy"],
      universal_anchor_claim: ["anchor_mode", "local_property_tests_pass", "universal_anchor_pass"],
      claim_transition: ["upgrade_evidence_present"],
      statistical_confidence: ["p_value", "alpha", "effect_direction_confirmed"],
      reproducibility_check: ["artifact_available", "independent_reproduction_pass"],
      financial_metric_claim: ["reported_value", "reference_value", "tolerance", "metric_period_match"]
    };
    const claimTypes = Object.keys(required).sort();
    const historyLimit = 50;
    const historyStorageKey = "capas_decision_history_v1";
    const themeStorageKey = "capas_theme_v1";
    let decisionHistory = loadHistory();
    let lastOutputJson = "";
    let inputChangeTimer = null;
    let lastFocusedBeforeHelp = null;
    const fineTuneBlockers = [
      "no blind or external inference review is attached",
      "CAPAS gates supplied structured evidence; it does not infer hidden evidence",
      "training readiness requires source-backed evidence, semantic alignment, witness independence, and review"
    ];

    const fieldHelp = {
      "payload": "Paste one JSON object at the root, not an array or loose text, before the strict gate can decide.",
      "claim": "Add a claim object with id, type, and text. CAPAS decides claims, not raw prose.",
      "evidence": "Add an evidence object with the measured fields that support or limit the claim.",
      "claim.id": "Give this claim a stable non-empty identifier so the decision can be audited later.",
      "claim.type": `Choose one supported claim type: ${claimTypes.join(", ")}.`,
      "claim.text": "Write the exact sentence the evidence is allowed to license.",
      "abs_error": "Numerical absolute error between the computed value and the declared reference.",
      "tolerance": "Maximum allowed error for this exact-model claim.",
      "within_chemical_accuracy": "Boolean verdict from the chemistry evidence layer; true only when the threshold was actually met.",
      "anchor_mode": "Use absolute_anchor only when the witness is a fixed theoretical value or scaling law, not another guess.",
      "local_property_tests_pass": "Whether local/problem-specific checks passed.",
      "universal_anchor_pass": "Whether the independent universal anchor passed.",
      "upgrade_evidence_present": "Whether explicit evidence exists to license the stronger upgraded claim.",
      "p_value": "Observed p-value for a statistical threshold claim. Must be between 0 and 1.",
      "alpha": "Declared significance threshold. Must be between 0 and 1.",
      "effect_direction_confirmed": "Whether the measured effect direction matches the claim wording.",
      "artifact_available": "Whether the code/data/model artifact required for reproduction is available.",
      "independent_reproduction_pass": "Whether an independent reproduction attempt passed.",
      "reported_value": "Numeric value stated by the claim.",
      "reference_value": "Trusted numeric reference value used for comparison.",
      "metric_period_match": "Whether the reported metric and reference are from the same reporting period."
    };

    const minimalExamples = {
      exact_model_solution: {
        claim: { id: "draft_exact_model_solution", type: "exact_model_solution", text: "The model solution is within the declared tolerance." },
        evidence: { abs_error: 0.0002, tolerance: 0.0016 }
      },
      physical_accuracy: {
        claim: { id: "draft_physical_accuracy", type: "physical_accuracy", text: "The calculation is within the declared physical accuracy threshold." },
        evidence: { within_chemical_accuracy: true }
      },
      universal_anchor_claim: {
        claim: { id: "draft_universal_anchor", type: "universal_anchor_claim", text: "The generated result is consistent with the universal anchor." },
        evidence: { anchor_mode: "absolute_anchor", local_property_tests_pass: true, universal_anchor_pass: true }
      },
      claim_transition: {
        claim: { id: "draft_claim_transition", type: "claim_transition", text: "The stronger claim is licensed by explicit upgrade evidence." },
        evidence: { upgrade_evidence_present: false, current_claim: "weaker current claim only" }
      },
      statistical_confidence: {
        claim: { id: "draft_statistical_confidence", type: "statistical_confidence", text: "The observed effect is statistically significant at the declared alpha." },
        evidence: { p_value: 0.01, alpha: 0.05, effect_direction_confirmed: true }
      },
      reproducibility_check: {
        claim: { id: "draft_reproducibility_check", type: "reproducibility_check", text: "The reported result is independently reproducible from the supplied artifact." },
        evidence: { artifact_available: true, independent_reproduction_pass: true }
      },
      financial_metric_claim: {
        claim: { id: "draft_financial_metric", type: "financial_metric_claim", text: "The reported financial metric matches the reference for the same period." },
        evidence: { reported_value: 101.2, reference_value: 101.0, tolerance: 0.5, metric_period_match: true }
      }
    };

    function containsAngleLikeCharacter(value) {
      return disallowedAngleRegex.test(value);
    }

    function validatePayload(payload) {
      const errors = [];
      if (payload === null || typeof payload !== "object" || Array.isArray(payload)) {
        return ["payload must be a JSON object"];
      }
      const claim = payload.claim;
      const evidence = payload.evidence;
      if (claim === null || typeof claim !== "object" || Array.isArray(claim)) {
        errors.push("claim must be an object");
      }
      if (evidence === null || typeof evidence !== "object" || Array.isArray(evidence)) {
        errors.push("evidence must be an object");
      }
      const safeClaim = claim && typeof claim === "object" && !Array.isArray(claim) ? claim : {};
      for (const field of ["id", "type", "text"]) {
        if (typeof safeClaim[field] !== "string" || safeClaim[field].trim() === "") {
          errors.push(`claim.${field} must be a non-empty string`);
        }
      }
      if (typeof safeClaim.id === "string" && safeClaim.id.length > 256) {
        errors.push("claim.id must be at most 256 characters");
      }
      if (typeof safeClaim.id === "string" && containsAngleLikeCharacter(safeClaim.id)) {
        errors.push("claim.id must not contain angle brackets or Unicode angle-bracket homoglyphs");
      }
      if (typeof safeClaim.text === "string" && safeClaim.text.length > 2000) {
        errors.push("claim.text must be at most 2000 characters");
      }
      if (typeof safeClaim.text === "string" && containsAngleLikeCharacter(safeClaim.text)) {
        errors.push("claim.text must not contain angle brackets or Unicode angle-bracket homoglyphs");
      }
      if (typeof safeClaim.type === "string" && !required[safeClaim.type]) {
        errors.push(`claim.type must be one of: ${claimTypes.join(", ")}`);
      }
      const safeEvidence = evidence && typeof evidence === "object" && !Array.isArray(evidence) ? evidence : {};
      for (const field of ["abs_error", "tolerance", "p_value", "alpha", "reported_value", "reference_value"]) {
        if (Object.prototype.hasOwnProperty.call(safeEvidence, field) && typeof safeEvidence[field] !== "number") {
          errors.push(`evidence.${field} must be a number`);
        } else if (Object.prototype.hasOwnProperty.call(safeEvidence, field)) {
          if (!Number.isFinite(safeEvidence[field])) {
            errors.push(`evidence.${field} must be finite`);
          } else if (["abs_error", "tolerance"].includes(field) && safeEvidence[field] < 0) {
            errors.push(`evidence.${field} must be >= 0`);
          } else if (["p_value", "alpha"].includes(field) && (safeEvidence[field] < 0 || safeEvidence[field] > 1)) {
            errors.push(`evidence.${field} must be between 0 and 1`);
          }
        }
      }
      for (const field of ["within_chemical_accuracy", "local_property_tests_pass", "universal_anchor_pass", "upgrade_evidence_present", "effect_direction_confirmed", "artifact_available", "independent_reproduction_pass", "metric_period_match"]) {
        if (Object.prototype.hasOwnProperty.call(safeEvidence, field) && typeof safeEvidence[field] !== "boolean") {
          errors.push(`evidence.${field} must be a boolean`);
        }
      }
      for (const field of ["anchor_mode", "physical_evidence_level", "verification_independence"]) {
        if (Object.prototype.hasOwnProperty.call(safeEvidence, field) && typeof safeEvidence[field] !== "string") {
          errors.push(`evidence.${field} must be a string`);
        }
        if (typeof safeEvidence[field] === "string" && containsAngleLikeCharacter(safeEvidence[field])) {
          errors.push(`evidence.${field} must not contain angle brackets or Unicode angle-bracket homoglyphs`);
        }
      }
      if (Object.prototype.hasOwnProperty.call(safeEvidence, "current_claim")) {
        if (typeof safeEvidence.current_claim !== "string") {
          errors.push("evidence.current_claim must be a string");
        } else {
          if (safeEvidence.current_claim.length > 4000) {
            errors.push("evidence.current_claim must be at most 4000 characters");
          }
          if (containsAngleLikeCharacter(safeEvidence.current_claim)) {
            errors.push("evidence.current_claim must not contain angle brackets or Unicode angle-bracket homoglyphs");
          }
        }
      }
      return errors;
    }

    function rule(payload) {
      const schemaErrors = validatePayload(payload);
      const claim = payload && typeof payload.claim === "object" && !Array.isArray(payload.claim) ? payload.claim : {};
      const evidence = payload && typeof payload.evidence === "object" && !Array.isArray(payload.evidence) ? payload.evidence : {};
      if (schemaErrors.length) {
        return {
          schema_version: capasSchemaVersion,
          input_claim: claim,
          verdict: "HOLD",
          reason: "input payload failed CAPAS schema validation",
          licensed_claim: claim.text,
          rewrite: null,
          missing_fields: [],
          required_fields: [],
          schema_errors: schemaErrors,
          fine_tune_ready: false,
          fine_tune_blockers: fineTuneBlockers,
          non_claim: "This decision is rule-based over supplied evidence fields, not an LLM judgment."
        };
      }
      const fields = required[claim.type];
      let missing = [];
      if (fields) {
        missing = fields.filter((field) => evidence[field] === undefined || evidence[field] === null || evidence[field] === "unknown");
      }
      let result = {
        schema_version: capasSchemaVersion,
        input_claim: claim,
        verdict: "HOLD",
        reason: "unsupported claim type or missing evidence",
        licensed_claim: claim.text,
        rewrite: null,
        missing_fields: missing,
        required_fields: fields || [],
        schema_errors: [],
        fine_tune_ready: false,
        fine_tune_blockers: fineTuneBlockers,
        non_claim: "This decision is rule-based over supplied evidence fields, not an LLM judgment."
      };
      if (!fields) {
        result.reason = `unsupported claim type ${claim.type}; no rule was applied`;
      } else if (missing.length) {
        result.reason = `missing required evidence fields: ${missing.join(", ")}`;
      } else if (claim.type === "exact_model_solution") {
        result.verdict = Number(evidence.abs_error) <= Number(evidence.tolerance) ? "ACCEPT" : "REJECT";
        result.reason = `abs_error ${evidence.abs_error} vs tolerance ${evidence.tolerance}`;
      } else if (claim.type === "physical_accuracy") {
        result.verdict = evidence.within_chemical_accuracy === true ? "ACCEPT" : "REJECT";
        result.reason = `within_chemical_accuracy is ${evidence.within_chemical_accuracy}`;
      } else if (claim.type === "universal_anchor_claim") {
        if (evidence.anchor_mode !== "absolute_anchor") {
          result.verdict = "HOLD";
          result.reason = "claim requires an absolute_anchor, but evidence has another anchor mode";
        } else if (evidence.local_property_tests_pass === true && evidence.universal_anchor_pass === true) {
          result.verdict = "ACCEPT";
          result.reason = "local checks and universal anchor both pass";
        } else if (evidence.local_property_tests_pass === true && evidence.universal_anchor_pass !== true) {
          result.verdict = "REWRITE";
          result.reason = "local checks pass, but the universal anchor fails";
          result.rewrite = "local plausibility only; universal physical correctness is not licensed";
          result.licensed_claim = result.rewrite;
        } else {
          result.verdict = "REJECT";
          result.reason = "local checks fail before the universal-anchor claim is licensed";
        }
      } else if (claim.type === "claim_transition") {
        if (evidence.upgrade_evidence_present === true) {
          result.verdict = "ACCEPT";
          result.reason = "upgrade evidence is explicitly present";
        } else {
          result.verdict = "REWRITE";
          result.reason = "upgrade evidence is absent; stronger claim is not licensed";
          result.rewrite = evidence.current_claim || "weaker current claim only";
          result.licensed_claim = result.rewrite;
        }
      } else if (claim.type === "statistical_confidence") {
        if (Number(evidence.p_value) <= Number(evidence.alpha) && evidence.effect_direction_confirmed === true) {
          result.verdict = "ACCEPT";
          result.reason = `p_value ${evidence.p_value} <= alpha ${evidence.alpha} and effect direction is confirmed`;
        } else if (Number(evidence.p_value) <= Number(evidence.alpha)) {
          result.verdict = "REWRITE";
          result.reason = "statistical threshold passes, but effect direction is not licensed";
          result.rewrite = "statistical threshold only; directional or causal wording is not licensed";
          result.licensed_claim = result.rewrite;
        } else {
          result.verdict = "REJECT";
          result.reason = `p_value ${evidence.p_value} > alpha ${evidence.alpha}`;
        }
      } else if (claim.type === "reproducibility_check") {
        if (evidence.artifact_available === true && evidence.independent_reproduction_pass === true) {
          result.verdict = "ACCEPT";
          result.reason = "artifact is available and independent reproduction passed";
        } else if (evidence.artifact_available === true) {
          result.verdict = "REWRITE";
          result.reason = "artifact exists, but independent reproduction has not passed";
          result.rewrite = "artifact available; independent reproduction is not yet licensed";
          result.licensed_claim = result.rewrite;
        } else {
          result.verdict = "REJECT";
          result.reason = "required artifact is not available for reproducibility";
        }
      } else if (claim.type === "financial_metric_claim") {
        const delta = Math.abs(Number(evidence.reported_value) - Number(evidence.reference_value));
        if (delta <= Number(evidence.tolerance) && evidence.metric_period_match === true) {
          result.verdict = "ACCEPT";
          result.reason = `reported_value differs from reference_value by ${delta}, within tolerance ${evidence.tolerance}, and period matches`;
        } else if (delta <= Number(evidence.tolerance)) {
          result.verdict = "REWRITE";
          result.reason = "numeric metric matches tolerance, but period alignment is not licensed";
          result.rewrite = "numeric metric matches reference tolerance; period-specific claim is not licensed";
          result.licensed_claim = result.rewrite;
        } else {
          result.verdict = "REJECT";
          result.reason = `reported_value differs from reference_value by ${delta}, above tolerance ${evidence.tolerance}`;
        }
      }
      return result;
    }

    function renderVerdict(result) {
      const verdict = result.verdict;
      let html = `<div class="verdict-banner"><span class="verdict-badge ${verdict}">${verdict}</span><span class="verdict-reason">${escHtml(result.reason)}</span></div>`;
      if (result.schema_errors && result.schema_errors.length) {
        html += `<div class="alert-block errors"><div class="alert-title">Schema errors</div><ul>${result.schema_errors.map((e) => `<li>${escHtml(e)}</li>`).join("")}</ul></div>`;
        html += renderSchemaAssistant(result.schema_errors);
      }
      if (result.missing_fields && result.missing_fields.length) {
        html += `<div class="alert-block missing"><div class="alert-title">Missing required fields</div><ul>${result.missing_fields.map((f) => `<li><code>${escHtml(f)}</code></li>`).join("")}</ul></div>`;
        html += renderMissingAssistant(result);
      }
      if (result.rewrite) {
        html += (
          `<div class="rewrite-block"><div class="alert-title">Licensed rewrite</div><div class="rewrite-text">"${escHtml(result.rewrite)}"</div>` +
          `<div class="rewrite-diff">` +
          `<div class="rewrite-pane"><div class="rewrite-pane-label">Original claim</div><div class="rewrite-pane-text">${escHtml(result.input_claim?.text || "")}</div></div>` +
          `<div class="rewrite-pane"><div class="rewrite-pane-label">Licensed claim</div><div class="rewrite-pane-text">${escHtml(result.licensed_claim || result.rewrite)}</div></div>` +
          `</div></div>`
        );
      }
      document.getElementById("verdict-area").innerHTML = html;
    }

    function batchItems(payload) {
      if (Array.isArray(payload)) return payload;
      if (payload && Array.isArray(payload.items)) return payload.items;
      if (payload && Array.isArray(payload.claims)) return payload.claims;
      if (payload && typeof payload === "object" && payload.claim && payload.evidence) return [payload];
      throw new Error("Batch input must be a JSON array or an object with items/claims array.");
    }

    function runBatch(payload) {
      const items = batchItems(payload);
      const results = items.map((item, index) => ({ index, result: rule(item) }));
      const summary = {};
      for (const entry of results) {
        const verdict = entry.result.verdict || "UNKNOWN";
        summary[verdict] = (summary[verdict] || 0) + 1;
      }
      return {
        schema_version: capasSchemaVersion,
        batch_mode: "decide",
        item_count: items.length,
        results,
        summary,
        fine_tune_ready: false,
        fine_tune_blockers: [
          "batch decisions are not blind-reviewed",
          "CAPAS gates supplied structured evidence; it does not infer hidden evidence"
        ],
        non_claim: "Batch mode applies the same deterministic per-claim gates; it does not create new scientific evidence."
      };
    }

    function renderBatch(result) {
      const summary = Object.entries(result.summary).map(([verdict, count]) => `<span class="verdict-badge ${escHtml(verdict)}">${escHtml(verdict)} ${count}</span>`).join("");
      const rows = result.results.map((entry) => {
        const claim = entry.result.input_claim || {};
        const verdict = entry.result.verdict || "UNKNOWN";
        const id = claim.id || `item_${entry.index + 1}`;
        return (
          `<details class="batch-row">` +
          `<summary><span class="verdict-badge ${escHtml(verdict)}">${escHtml(verdict)}</span><span class="batch-row-id">#${entry.index + 1} ${escHtml(id)}</span><span class="batch-row-reason">${escHtml(entry.result.reason || "")}</span></summary>` +
          `<pre>${escHtml(JSON.stringify(entry.result, null, 2))}</pre>` +
          `</details>`
        );
      }).join("");
      document.getElementById("verdict-area").innerHTML =
        `<div class="verdict-banner"><span class="verdict-badge HOLD">BATCH</span><span class="verdict-reason">${result.item_count} items evaluated with deterministic CAPAS gates.</span></div>` +
        `<div class="assist-block"><div class="alert-title">Batch summary</div><div style="display:flex;gap:8px;flex-wrap:wrap">${summary}</div>` +
        `<div class="batch-progress" aria-hidden="true"><div class="batch-progress-fill" style="--batch-progress:100%"></div></div>` +
        `<div class="batch-progress-label">${result.item_count}/${result.item_count} claims processed · deterministic gate complete</div>` +
        `<div class="batch-table" aria-label="Batch per-item decisions">${rows}</div></div>`;
    }

    function hasNullEvidence(payload) {
      const evidence = payload?.evidence;
      if (!evidence || typeof evidence !== "object" || Array.isArray(evidence)) return false;
      return Object.values(evidence).some((value) => value === null);
    }

    function setOutputJson(value) {
      const json = JSON.stringify(value, null, 2);
      const output = document.getElementById("output");
      if (json === lastOutputJson) {
        output.scrollTop = 0;
        output.scrollLeft = 0;
        return;
      }
      lastOutputJson = json;
      if (json.length > 5000) {
        output.textContent = json;
        output.scrollTop = 0;
        output.scrollLeft = 0;
        return;
      }
      output.innerHTML = syntaxHighlight(json);
      output.scrollTop = 0;
      output.scrollLeft = 0;
    }

    function setOutputEmpty() {
      lastOutputJson = "";
      document.getElementById("output").textContent = "";
    }

    function syntaxHighlight(json) {
      return escHtml(json).replace(/(&quot;(?:\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\&])*&quot;(\s*:)?|\btrue\b|\bfalse\b|\bnull\b|-?\d+(?:\.\d+)?(?:[eE][+\-]?\d+)?)/g, (match) => {
        let cls = "json-number";
        if (match.startsWith("&quot;")) {
          cls = match.endsWith(":") ? "json-key" : "json-string";
        } else if (match === "true" || match === "false") {
          cls = "json-boolean";
        } else if (match === "null") {
          cls = "json-null";
        }
        return `<span class="${cls}">${match}</span>`;
      });
    }

    function renderSchemaAssistant(errors) {
      const tips = errors.map((error) => `<li>${escHtml(explainSchemaError(error))}</li>`).join("");
      const example = minimalExamples.exact_model_solution;
      return (
        `<div class="assist-block"><div class="alert-title">How to make this evaluable</div>` +
        `<div class="assist-muted">This is still a HOLD. The assistant only explains structure; it does not license the claim.</div>` +
        `<ul>${tips}</ul>` +
        `<pre>${escHtml(JSON.stringify(example, null, 2))}</pre></div>`
      );
    }

    function renderMissingAssistant(result) {
      const type = result.input_claim?.type;
      const example = minimalExamples[type] || minimalExamples.exact_model_solution;
      const tips = result.missing_fields.map((field) => `<li><code>${escHtml(field)}</code>: ${escHtml(fieldHelp[field] || "Required evidence field for this claim type.")}</li>`).join("");
      return (
        `<div class="assist-block"><div class="alert-title">Missing field assistant</div>` +
        `<div class="assist-muted">Fill these fields, then run Decide again. CAPAS will not infer them.</div>` +
        `<ul>${tips}</ul>` +
        `<pre>${escHtml(JSON.stringify(example, null, 2))}</pre></div>`
      );
    }

    function explainSchemaError(error) {
      if (error.includes("payload must be a JSON object")) return fieldHelp.payload;
      if (error.includes("claim must be an object")) return fieldHelp.claim;
      if (error.includes("evidence must be an object")) return fieldHelp.evidence;
      if (error.includes("claim.id must be a non-empty string")) return fieldHelp["claim.id"];
      if (error.includes("claim.type must be a non-empty string")) return fieldHelp["claim.type"];
      if (error.includes("claim.type must be one of")) return fieldHelp["claim.type"];
      if (error.includes("claim.text must be a non-empty string")) return fieldHelp["claim.text"];
      if (error.includes("abs_error")) return fieldHelp.abs_error;
      if (error.includes("tolerance")) return fieldHelp.tolerance;
      if (error.includes("within_chemical_accuracy")) return fieldHelp.within_chemical_accuracy;
      if (error.includes("anchor_mode")) return fieldHelp.anchor_mode;
      if (error.includes("local_property_tests_pass")) return fieldHelp.local_property_tests_pass;
      if (error.includes("universal_anchor_pass")) return fieldHelp.universal_anchor_pass;
      if (error.includes("upgrade_evidence_present")) return fieldHelp.upgrade_evidence_present;
      return "Fix this schema issue before the strict gate can evaluate the claim.";
    }

    function inferClaimType(raw, parsed) {
      const text = `${raw} ${JSON.stringify(parsed || {})}`.toLowerCase();
      if (text.includes("universal") || text.includes("anchor") || text.includes("local_property")) return "universal_anchor_claim";
      if (text.includes("upgrade") || text.includes("stronger claim") || text.includes("current_claim")) return "claim_transition";
      if (text.includes("chemical accuracy") || text.includes("within_chemical_accuracy") || text.includes("experiment")) return "physical_accuracy";
      if (text.includes("abs_error") || text.includes("tolerance") || text.includes("error") || text.includes("ground state")) return "exact_model_solution";
      return "exact_model_solution";
    }

    function extractNumbers(raw) {
      const matches = raw.match(/-?\d+(?:\.\d+)?(?:e[+-]?\d+)?/gi) || [];
      return matches.map(Number).filter(Number.isFinite);
    }

    function buildDraft() {
      const raw = document.getElementById("input").value.trim();
      let parsed = null;
      try {
        parsed = raw ? JSON.parse(raw) : null;
      } catch (_) {
        parsed = null;
      }
      const type = parsed?.claim?.type && required[parsed.claim.type] ? parsed.claim.type : inferClaimType(raw, parsed);
      const numbers = extractNumbers(raw);
      const draft = {
        claim: {
          id: parsed?.claim?.id || "draft_claim_001",
          type,
          text: parsed?.claim?.text || (raw && !parsed ? raw.slice(0, 2000) : minimalExamples[type].claim.text)
        },
        evidence: {}
      };
      const sourceEvidence = parsed?.evidence && typeof parsed.evidence === "object" && !Array.isArray(parsed.evidence) ? parsed.evidence : {};
      for (const field of required[type]) {
        if (Object.prototype.hasOwnProperty.call(sourceEvidence, field)) {
          draft.evidence[field] = sourceEvidence[field];
        } else if (field === "abs_error" && numbers.length > 0) {
          draft.evidence[field] = Math.abs(numbers[0]);
        } else if (field === "tolerance" && numbers.length > 1) {
          draft.evidence[field] = Math.abs(numbers[1]);
        } else if (field === "anchor_mode") {
          draft.evidence[field] = "absolute_anchor";
        } else if (field === "upgrade_evidence_present") {
          draft.evidence[field] = false;
        } else {
          draft.evidence[field] = null;
        }
      }
      if (type === "claim_transition" && !Object.prototype.hasOwnProperty.call(draft.evidence, "current_claim")) {
        draft.evidence.current_claim = sourceEvidence.current_claim || "weaker current claim only";
      }
      document.getElementById("input").value = JSON.stringify(draft, null, 2);
      onInputChange();
      const missing = required[type].filter((field) => draft.evidence[field] === null || draft.evidence[field] === "unknown");
      document.getElementById("verdict-area").innerHTML =
        `<div class="assist-block"><div class="alert-title">Draft built, not decided</div>` +
        `<div>CAPAS prepared a candidate <code>${escHtml(type)}</code> payload. Run Decide only after the missing evidence is real.</div>` +
        (missing.length ? `<ul>${missing.map((field) => `<li><code>${escHtml(field)}</code>: ${escHtml(fieldHelp[field])}</li>`).join("")}</ul>` : `<div class="assist-muted">No required fields are null; the strict gate can now evaluate it.</div>`) +
        `</div>`;
      setOutputEmpty();
      setCopyEnabled(false);
    }

    function setCopyEnabled(enabled) {
      document.getElementById("copy-btn").disabled = !enabled;
    }

    function loadHistory() {
      try {
        const raw = localStorage.getItem(historyStorageKey);
        const parsed = raw ? JSON.parse(raw) : [];
        const clean = Array.isArray(parsed) ? parsed.filter(isSafeHistoryEntry).slice(0, historyLimit) : [];
        if (Array.isArray(parsed) && clean.length !== parsed.length) {
          localStorage.setItem(historyStorageKey, JSON.stringify(clean));
        }
        return clean;
      } catch (_) {
        return [];
      }
    }

    function isSafeHistoryEntry(entry) {
      if (!entry || typeof entry !== "object") return false;
      if (typeof entry.id === "string" && containsAngleLikeCharacter(entry.id)) return false;
      try {
        const payload = typeof entry.payload === "string" ? JSON.parse(entry.payload) : null;
        const claim = payload && typeof payload.claim === "object" && !Array.isArray(payload.claim) ? payload.claim : {};
        if (typeof claim.id === "string" && containsAngleLikeCharacter(claim.id)) return false;
        if (typeof claim.text === "string" && containsAngleLikeCharacter(claim.text)) return false;
      } catch (_) {
        return false;
      }
      return true;
    }

    function saveHistory() {
      try {
        localStorage.setItem(historyStorageKey, JSON.stringify(decisionHistory.slice(0, historyLimit)));
      } catch (_) {}
    }

    function renderHistory() {
      const list = document.getElementById("history-list");
      document.getElementById("history-count").textContent = `${decisionHistory.length}/${historyLimit} saved`;
      if (!decisionHistory.length) {
        list.innerHTML = `<div class="empty-state">No decisions yet.</div>`;
        return;
      }
      list.innerHTML = decisionHistory.map((item, index) => (
        `<div class="history-row">` +
        `<button type="button" class="history-item" onclick="restoreHistory(${index})" onkeydown="handleHistoryKey(event, ${index})" aria-label="Restore decision ${escHtml(item.id)} from ${escHtml(formatHistoryTimestamp(item.timestamp))}">` +
        `<span class="history-badge ${item.verdict}">${item.verdict}</span>` +
        `<span class="history-id">${escHtml(item.id)}</span>` +
        `<span class="history-reason">${escHtml(item.reason)}</span>` +
        `<time class="history-ts" datetime="${escHtml(item.timestamp || "")}">${escHtml(formatHistoryTimestamp(item.timestamp))}</time>` +
        `</button>` +
        `<button type="button" class="history-delete" aria-label="Delete decision ${escHtml(item.id)}" onclick="deleteHistory(${index}, event)">Delete</button>` +
        `</div>`
      )).join("");
    }

    function formatHistoryTimestamp(value) {
      if (!value) return "no timestamp";
      const date = new Date(value);
      if (Number.isNaN(date.getTime())) return "invalid time";
      return date.toLocaleString(undefined, {
        month: "short",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit"
      });
    }

    function clearHistory() {
      decisionHistory = [];
      saveHistory();
      renderHistory();
    }

    function deleteHistory(index, event) {
      if (event) event.stopPropagation();
      decisionHistory.splice(index, 1);
      saveHistory();
      renderHistory();
    }

    function addToHistory(result) {
      decisionHistory.unshift({
        verdict: result.verdict,
        id: result.input_claim?.id || "-",
        reason: result.reason,
        payload: document.getElementById("input").value,
        decision: result,
        timestamp: new Date().toISOString()
      });
      decisionHistory = decisionHistory.slice(0, historyLimit);
      saveHistory();
      renderHistory();
    }

    function restoreHistory(index) {
      const item = decisionHistory[index];
      if (!item) return;
      document.getElementById("input").value = item.payload;
      onInputChange();
      renderVerdict(item.decision);
      setOutputJson(item.decision);
      setCopyEnabled(true);
    }

    function handleHistoryKey(event, index) {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        restoreHistory(index);
      }
    }

    function encodeBase64Url(value) {
      const bytes = new TextEncoder().encode(value);
      let binary = "";
      bytes.forEach((byte) => { binary += String.fromCharCode(byte); });
      return btoa(binary).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/g, "");
    }

    function decodeBase64Url(value) {
      const padded = value.replace(/-/g, "+").replace(/_/g, "/").padEnd(Math.ceil(value.length / 4) * 4, "=");
      const binary = atob(padded);
      const bytes = Uint8Array.from(binary, (char) => char.charCodeAt(0));
      return new TextDecoder().decode(bytes);
    }

    function maybeLoadSharedPayload() {
      const params = new URLSearchParams(window.location.search);
      const encoded = params.get("p");
      if (!encoded) return false;
      try {
        const raw = decodeBase64Url(encoded);
        JSON.parse(raw);
        document.getElementById("input").value = raw;
        document.getElementById("shared-payload-badge").hidden = false;
        return true;
      } catch (error) {
        document.getElementById("verdict-area").innerHTML =
          `<div class="alert-block errors"><div class="alert-title">Shared payload error</div>${escHtml(error.message)}</div>`;
        return false;
      }
    }

    function copyShareUrl() {
      const raw = document.getElementById("input").value.trim();
      if (!raw) return;
      try {
        JSON.parse(raw);
        const url = `${window.location.origin}${window.location.pathname}?p=${encodeBase64Url(raw)}`;
        navigator.clipboard.writeText(url).then(() => {
          const button = document.getElementById("share-btn");
          button.textContent = "URL copied";
          button.classList.add("copied");
          const existing = document.getElementById("share-privacy-warning");
          if (existing) existing.remove();
          document.getElementById("verdict-area").insertAdjacentHTML(
            "beforeend",
            `<div class="assist-block" id="share-privacy-warning"><div class="alert-title">Share URL privacy</div>The current payload is embedded in the URL. Do not share links that contain sensitive claims or private evidence.</div>`
          );
          setTimeout(() => {
            button.textContent = "Share URL";
            button.classList.remove("copied");
          }, 1600);
        });
      } catch (_) {
        document.getElementById("verdict-area").innerHTML =
          `<div class="alert-block errors"><div class="alert-title">Share URL error</div>Only valid JSON payloads can be shared.</div>`;
      }
    }

    function csvCell(value) {
      return `"${String(value ?? "").replace(/"/g, '""')}"`;
    }

    function exportHistoryCsv() {
      const header = ["timestamp", "verdict", "id", "reason", "payload", "decision"];
      const rows = decisionHistory.map((item) => [
        item.timestamp,
        item.verdict,
        item.id,
        item.reason,
        item.payload,
        JSON.stringify(item.decision)
      ]);
      const csv = [header, ...rows].map((row) => row.map(csvCell).join(",")).join("\n");
      const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "capas_decision_history.csv";
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
    }

    function applyTheme(theme) {
      const normalized = theme === "light" || theme === "dark" ? theme : "";
      if (normalized) {
        document.documentElement.dataset.theme = normalized;
      } else {
        delete document.documentElement.dataset.theme;
      }
      const button = document.getElementById("theme-toggle");
      if (button) {
        const label = normalized === "light" ? "Light" : normalized === "dark" ? "Dark" : "System";
        button.textContent = label;
        button.setAttribute("aria-label", `Current theme: ${label}. Toggle light, dark, and system theme.`);
      }
    }

    function toggleTheme() {
      const current = document.documentElement.dataset.theme || "";
      const next = current === "light" ? "dark" : current === "dark" ? "" : "light";
      if (next) {
        localStorage.setItem(themeStorageKey, next);
      } else {
        localStorage.removeItem(themeStorageKey);
      }
      applyTheme(next);
    }

    function initTheme() {
      applyTheme(localStorage.getItem(themeStorageKey) || "");
    }

    function escHtml(value) {
      return String(value).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
    }

    function scheduleInputChange() {
      clearTimeout(inputChangeTimer);
      inputChangeTimer = setTimeout(onInputChange, 300);
    }

    function onInputChange() {
      clearTimeout(inputChangeTimer);
      const raw = document.getElementById("input").value.trim();
      const status = document.getElementById("json-status");
      const input = document.getElementById("input");
      const typeLabel = document.getElementById("type-label");
      if (!raw) {
        status.textContent = "Waiting for input...";
        status.className = "json-status";
        input.className = "";
        typeLabel.textContent = "";
        setCopyEnabled(false);
        return;
      }
      try {
        const payload = JSON.parse(raw);
        input.className = "ok-border";
        if (hasNullEvidence(payload)) {
          status.textContent = "Draft - fill null values before deciding";
          status.className = "json-status draft";
        } else {
          status.textContent = "Valid JSON";
          status.className = "json-status valid";
        }
        typeLabel.textContent = payload?.claim?.type || "";
      } catch (error) {
        input.className = "error-border";
        status.textContent = error.message;
        status.className = "json-status invalid";
        typeLabel.textContent = "";
      }
    }

    function decide(recordHistory = true) {
      const button = document.getElementById("decide-btn");
      try {
        const raw = document.getElementById("input").value.trim();
        if (!raw) {
          document.getElementById("verdict-area").innerHTML = `<div class="alert-block errors"><div class="alert-title">Input required</div>Please paste a JSON claim/evidence payload first.</div>`;
          setOutputEmpty();
          setCopyEnabled(false);
          return;
        }
        button.classList.add("processing");
        const payload = JSON.parse(raw);
        const result = rule(payload);
        renderVerdict(result);
        setOutputJson(result);
        if (recordHistory) {
          addToHistory(result);
        }
        const copy = document.getElementById("copy-btn");
        copy.textContent = "Copy JSON";
        copy.classList.remove("copied");
        setCopyEnabled(true);
        setTimeout(() => button.classList.remove("processing"), 150);
      } catch (error) {
        button.classList.remove("processing");
        document.getElementById("verdict-area").innerHTML = `<div class="alert-block errors"><div class="alert-title">JSON parse error</div>${escHtml(error.message)}</div>`;
        setOutputEmpty();
        setCopyEnabled(false);
      }
    }

    function decideBatch() {
      try {
        const raw = document.getElementById("input").value.trim();
        if (!raw) {
          document.getElementById("verdict-area").innerHTML = `<div class="alert-block errors"><div class="alert-title">Input required</div>Please paste a JSON array or items/claims batch first.</div>`;
          setOutputEmpty();
          setCopyEnabled(false);
          return;
        }
        const payload = JSON.parse(raw);
        const result = runBatch(payload);
        renderBatch(result);
        setOutputJson(result);
        setCopyEnabled(true);
      } catch (error) {
        document.getElementById("verdict-area").innerHTML = `<div class="alert-block errors"><div class="alert-title">Batch error</div>${escHtml(error.message)}</div>`;
        setOutputEmpty();
        setCopyEnabled(false);
      }
    }

    function resetSample() {
      document.getElementById("input").value = JSON.stringify(sample, null, 2);
      onInputChange();
      decide();
    }

    function loadSample(name) {
      document.getElementById("input").value = JSON.stringify(samples[name], null, 2);
      onInputChange();
      decide();
    }

    function copyOutput() {
      const text = document.getElementById("output").textContent;
      if (!text) return;
      navigator.clipboard.writeText(text).then(() => {
        const button = document.getElementById("copy-btn");
        button.textContent = "Copied";
        button.classList.add("copied");
        setTimeout(() => {
          button.textContent = "Copy JSON";
          button.classList.remove("copied");
        }, 1600);
      });
    }

    function openHelpModal(trigger) {
      lastFocusedBeforeHelp = trigger || document.getElementById("help-btn") || document.activeElement;
      document.getElementById("help-modal-backdrop").classList.add("open");
      document.getElementById("help-btn").setAttribute("aria-expanded", "true");
      const closeButton = document.querySelector("#help-modal .copy-btn");
      (closeButton || document.getElementById("help-modal")).focus();
    }

    function closeHelpModal(event) {
      if (event && event.type === "click" && event.target.id !== "help-modal-backdrop") return;
      document.getElementById("help-modal-backdrop").classList.remove("open");
      document.getElementById("help-btn").setAttribute("aria-expanded", "false");
      if (lastFocusedBeforeHelp && document.contains(lastFocusedBeforeHelp) && typeof lastFocusedBeforeHelp.focus === "function") {
        lastFocusedBeforeHelp.focus();
      }
    }

    function focusableHelpElements() {
      return Array.from(document.querySelectorAll("#help-modal button, #help-modal [href], #help-modal [tabindex]:not([tabindex='-1'])"))
        .filter((element) => !element.disabled && element.offsetParent !== null);
    }

    function handleHelpModalKey(event) {
      if (event.key === "Escape") {
        event.preventDefault();
        closeHelpModal();
        return;
      }
      if (event.key !== "Tab") return;
      const focusable = focusableHelpElements();
      if (!focusable.length) {
        event.preventDefault();
        document.getElementById("help-modal").focus();
        return;
      }
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    }

    document.addEventListener("keydown", (event) => {
      if ((event.metaKey || event.ctrlKey) && event.key === "Enter") {
        event.preventDefault();
        decide();
      } else if (event.key === "?" && !["INPUT", "TEXTAREA"].includes(document.activeElement?.tagName || "")) {
        event.preventDefault();
        const modal = document.getElementById("help-modal-backdrop");
        if (modal.classList.contains("open")) closeHelpModal();
        else openHelpModal(document.getElementById("help-btn"));
      } else if (event.key === "Escape") {
        closeHelpModal();
      }
    });

    initTheme();
    maybeLoadSharedPayload();
    onInputChange();
    renderHistory();
    decide(false);
</script>
</body>
</html>
"""
    return (
        html.replace("__SAMPLE_JSON__", sample_json)
        .replace("__SAMPLE_COMPACT_JSON__", json.dumps(sample, sort_keys=True))
        .replace("__SAMPLES_JSON__", samples_json)
        .replace("__UI_VERSION__", CAPAS_UI_VERSION)
    )


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


def cmd_batch(args: argparse.Namespace) -> int:
    payload = _load_json(Path(args.input))
    try:
        report = run_batch(payload, mode=args.mode, allow_web=args.allow_web)
    except ValueError as exc:
        report = {
            "batch_mode": args.mode,
            "item_count": 0,
            "results": [],
            "summary": {"ERROR": 1},
            "error": str(exc),
            "fine_tune_ready": False,
        }
        exit_code = 1
    else:
        exit_code = 0
    if args.output:
        _write_json(Path(args.output), report)
    if args.json or not args.output:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"batch {report['batch_mode']}: {report['item_count']} items")
        print(f"summary: {report['summary']}")
        print(f"wrote {args.output}")
    return exit_code


def _read_request_json(handler: BaseHTTPRequestHandler) -> Any:
    length = int(handler.headers.get("content-length", "0"))
    raw = handler.rfile.read(length) if length else b"{}"
    return json.loads(raw.decode("utf-8"))


def _write_response_json(handler: BaseHTTPRequestHandler, status: int, payload: dict[str, Any]) -> None:
    body = json.dumps(payload, indent=2, sort_keys=True).encode("utf-8")
    handler.send_response(status)
    handler.send_header("content-type", "application/json; charset=utf-8")
    handler.send_header("content-length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


class CapasApiHandler(BaseHTTPRequestHandler):
    server_version = "CAPASClaimGate/0.1"

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003 - stdlib callback name
        return

    def do_GET(self) -> None:  # noqa: N802 - stdlib callback name
        if self.path == "/health":
            _write_response_json(self, 200, {"status": "ok", "service": "capas-claim-gate", "schema_version": CAPAS_CLAIM_SCHEMA_VERSION})
        else:
            _write_response_json(self, 404, {"error": "not found", "available": ["/health", "/decide", "/batch"]})

    def do_POST(self) -> None:  # noqa: N802 - stdlib callback name
        try:
            payload = _read_request_json(self)
            if self.path == "/decide":
                if not isinstance(payload, dict):
                    raise ValueError("/decide expects one JSON object")
                _write_response_json(self, 200, decide_external_claim(payload))
            elif self.path == "/batch":
                _write_response_json(self, 200, run_batch(payload, mode="decide"))
            else:
                _write_response_json(self, 404, {"error": "not found", "available": ["/health", "/decide", "/batch"]})
        except (json.JSONDecodeError, ValueError) as exc:
            _write_response_json(self, 400, {"error": str(exc), "fine_tune_ready": False})


def cmd_serve(args: argparse.Namespace) -> int:
    server = HTTPServer((args.host, args.port), CapasApiHandler)
    print(f"CAPAS API listening on http://{args.host}:{args.port}")
    print("endpoints: GET /health, POST /decide, POST /batch")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nshutting down")
    finally:
        server.server_close()
    return 0


def cmd_align(args: argparse.Namespace) -> int:
    payload = _load_json(Path(args.input))
    if not isinstance(payload.get("evidence"), dict) and (
        isinstance(payload.get("source"), dict) or isinstance(payload.get("sources"), list)
    ):
        payload = extract_evidence(payload, allow_web=args.allow_web)["candidate_payload"]
    report = align_claim_text(payload)
    if args.output:
        _write_json(Path(args.output), report)
    if args.json or not args.output:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"{report['alignment_status']}: {report['reason']}")
        print(f"wrote {args.output}")
    return 0


def cmd_extract(args: argparse.Namespace) -> int:
    payload = _load_json(Path(args.input))
    report = extract_evidence(payload, allow_web=args.allow_web)
    if args.output:
        _write_json(Path(args.output), report)
    if args.json or not args.output:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        fields = ", ".join(sorted(report["extracted_evidence"])) or "none"
        print(f"{report['extraction_status']}: extracted {fields}")
        print(f"wrote {args.output}")
    return 0


def cmd_retrieve(args: argparse.Namespace) -> int:
    payload = _load_json(Path(args.input))
    report = {
        "retrieved_snippets": retrieve_evidence_snippets(payload, allow_web=args.allow_web),
        "non_claim": "This retrieves source lines matching required evidence fields; web retrieval requires --allow-web.",
    }
    if args.output:
        _write_json(Path(args.output), report)
    if args.json or not args.output:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"retrieved {len(report['retrieved_snippets'])} snippets")
        print(f"wrote {args.output}")
    return 0


def cmd_reason(args: argparse.Namespace) -> int:
    payload = _load_json(Path(args.input))
    extraction = extract_evidence(payload, allow_web=args.allow_web)
    candidate = extraction["candidate_payload"]
    alignment = align_claim_text(candidate)
    gate_decision = decide_external_claim(candidate)
    report = scientific_reasoning_report(candidate, extraction, alignment, gate_decision)
    if args.output:
        _write_json(Path(args.output), report)
    if args.json or not args.output:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"{report['reasoning_status']}: {', '.join(report['risks']) or 'clear'}")
        print(f"wrote {args.output}")
    return 0


def cmd_pipeline(args: argparse.Namespace) -> int:
    payload = _load_json(Path(args.input))
    report = standalone_pipeline(payload, allow_web=args.allow_web)
    if args.output:
        _write_json(Path(args.output), report)
    if args.json or not args.output:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        decision = report["final_decision"]
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

    batch = subparsers.add_parser("batch", help="run deterministic gates over multiple claim/evidence JSON objects")
    batch.add_argument("--input", required=True, help="path to JSON array or object with items/claims array")
    batch.add_argument("--output", help="optional batch report path")
    batch.add_argument("--mode", choices=["decide", "align", "pipeline"], default="decide", help="per-item operation")
    batch.add_argument("--json", action="store_true", help="print JSON even when --output is supplied")
    batch.add_argument("--allow-web", action="store_true", help="allow fetching source.url for pipeline mode")
    batch.set_defaults(func=cmd_batch)

    serve = subparsers.add_parser("serve", help="run a local HTTP API for /decide and /batch")
    serve.add_argument("--host", default="127.0.0.1", help="bind host")
    serve.add_argument("--port", type=int, default=8765, help="bind port")
    serve.set_defaults(func=cmd_serve)

    align = subparsers.add_parser("align", help="check claim.text alignment against structured evidence")
    align.add_argument("--input", required=True, help="path to claim/evidence JSON")
    align.add_argument("--output", help="optional alignment report path")
    align.add_argument("--json", action="store_true", help="print JSON even when --output is supplied")
    align.add_argument("--allow-web", action="store_true", help="allow fetching source.url before alignment")
    align.set_defaults(func=cmd_align)

    extract = subparsers.add_parser("extract", help="extract explicit evidence assignments from local text/code/log input")
    extract.add_argument("--input", required=True, help="path to extraction input JSON")
    extract.add_argument("--output", help="optional extraction report path")
    extract.add_argument("--json", action="store_true", help="print JSON even when --output is supplied")
    extract.add_argument("--allow-web", action="store_true", help="allow fetching source.url")
    extract.set_defaults(func=cmd_extract)

    retrieve = subparsers.add_parser("retrieve", help="retrieve local evidence lines for the claim type")
    retrieve.add_argument("--input", required=True, help="path to standalone pipeline input JSON")
    retrieve.add_argument("--output", help="optional retrieval report path")
    retrieve.add_argument("--json", action="store_true", help="print JSON even when --output is supplied")
    retrieve.add_argument("--allow-web", action="store_true", help="allow fetching source.url")
    retrieve.set_defaults(func=cmd_retrieve)

    reason = subparsers.add_parser("reason", help="run deterministic scientific evidence/scope checklist")
    reason.add_argument("--input", required=True, help="path to standalone pipeline input JSON")
    reason.add_argument("--output", help="optional reasoning report path")
    reason.add_argument("--json", action="store_true", help="print JSON even when --output is supplied")
    reason.add_argument("--allow-web", action="store_true", help="allow fetching source.url")
    reason.set_defaults(func=cmd_reason)

    pipeline = subparsers.add_parser("pipeline", help="run extract -> semantic alignment -> deterministic claim gate")
    pipeline.add_argument("--input", required=True, help="path to standalone pipeline input JSON")
    pipeline.add_argument("--output", help="optional pipeline report path")
    pipeline.add_argument("--json", action="store_true", help="print JSON even when --output is supplied")
    pipeline.add_argument("--allow-web", action="store_true", help="allow fetching source.url")
    pipeline.set_defaults(func=cmd_pipeline)

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
