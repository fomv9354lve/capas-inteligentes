from __future__ import annotations

import argparse
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


VALIDATION_COMMANDS = [
    ("external input schema", ["benchmarks/verify_external_input_schema.py"]),
    ("standalone pipeline MVP", ["benchmarks/verify_standalone_pipeline.py"]),
    ("claim gate UI", ["benchmarks/verify_claim_gate_ui.py"]),
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
}

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
                        "maxLength": 4000,
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
    if isinstance(claim.get("text"), str) and len(claim["text"]) > 4000:
        errors.append("claim.text must be at most 4000 characters")
    _validate_no_angle_like(claim.get("text"), "claim.text", errors)

    claim_type = claim.get("type")
    if isinstance(claim_type, str) and claim_type not in REQUIRED_DECISION_FIELDS:
        errors.append(
            "claim.type must be one of: "
            + ", ".join(sorted(REQUIRED_DECISION_FIELDS))
        )

    numeric_fields = ["abs_error", "tolerance"]
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
            elif value < 0:
                errors.append(f"evidence.{field} must be >= 0")

    bool_fields = [
        "within_chemical_accuracy",
        "local_property_tests_pass",
        "universal_anchor_pass",
        "upgrade_evidence_present",
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
<title>CAPAS Claim Gate</title>
<style>
  *, *::before, *::after { box-sizing: border-box; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    margin: 0;
    padding: 20px 28px;
    max-width: 1200px;
    background: #0f1117;
    color: #e2e8f0;
    min-height: 100vh;
  }
  .header { margin-bottom: 20px; }
  .header h1 { font-size: 20px; font-weight: 700; margin: 0 0 4px 0; color: #f8fafc; }
  .header p { margin: 0; font-size: 13px; color: #64748b; }
  .header code { background: #1e2535; color: #94a3b8; padding: 1px 5px; border-radius: 4px; font-size: 12px; }
  .samples-bar { display: flex; gap: 8px; margin-bottom: 16px; flex-wrap: wrap; align-items: center; }
  .samples-bar span { font-size: 12px; color: #64748b; font-weight: 600; margin-right: 4px; }
  .sample-btn {
    padding: 5px 14px;
    border-radius: 6px;
    border: 1px solid;
    font-size: 12px;
    font-weight: 700;
    cursor: pointer;
    transition: opacity 0.15s, transform 0.1s;
    background: transparent;
  }
  .sample-btn:hover { opacity: 0.75; transform: translateY(-1px); }
  .sample-btn:active { transform: translateY(0); }
  .sample-btn:focus-visible, .decide-btn:focus-visible, .copy-btn:focus-visible, .history-item:focus-visible, #input:focus-visible {
    outline: 2px solid #60a5fa;
    outline-offset: 2px;
  }
  .sample-btn.accept { color: #4ade80; border-color: #4ade80; }
  .sample-btn.rewrite { color: #fb923c; border-color: #fb923c; }
  .sample-btn.hold { color: #94a3b8; border-color: #94a3b8; }
  .sample-btn.invalid { color: #f87171; border-color: #f87171; }
  .grid { display: grid; grid-template-columns: minmax(380px, 40%) minmax(0, 1fr); gap: 20px; align-items: start; }
  @media (max-width: 800px) { .grid { grid-template-columns: 1fr; } }
  .panel { background: #1a1f2e; border: 1px solid #2d3748; border-radius: 10px; overflow: hidden; }
  .panel, .output-section { min-width: 0; }
  .panel-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 14px;
    background: #151a27;
    border-bottom: 1px solid #2d3748;
  }
  .panel-title { font-size: 11px; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.8px; }
  .panel-tag { font-size: 11px; color: #64748b; }
  #input {
    width: 100%;
    min-height: 360px;
    background: #1a1f2e;
    color: #e2e8f0;
    border: none;
    outline: none;
    resize: vertical;
    font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
    font-size: 13px;
    line-height: 1.6;
    padding: 14px;
    display: block;
    transition: box-shadow 0.2s;
  }
  #input.ok-border { box-shadow: inset 0 0 0 2px #4ade8033; }
  #input.error-border { box-shadow: inset 0 0 0 2px #f8717155; }
  .json-status {
    padding: 6px 14px;
    font-size: 11px;
    font-weight: 600;
    border-top: 1px solid #2d3748;
    min-height: 28px;
    display: flex;
    align-items: center;
    gap: 5px;
    color: #64748b;
  }
  .json-status.valid { color: #4ade80; }
  .json-status.invalid { color: #f87171; }
  .decide-btn {
    width: 100%;
    padding: 11px;
    background: #3b82f6;
    color: white;
    border: none;
    font-size: 14px;
    font-weight: 700;
    cursor: pointer;
    transition: background 0.15s;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
  }
  .decide-btn:hover { background: #2563eb; }
  .decide-btn:active { transform: translateY(1px); }
  .decide-btn.processing { background: #1d4ed8; }
  .decide-hint { font-size: 11px; opacity: 0.6; font-weight: 500; background: #ffffff18; padding: 1px 6px; border-radius: 4px; }
  .verdict-banner { padding: 14px 16px; display: flex; align-items: center; gap: 14px; border-bottom: 1px solid #2d3748; }
  .verdict-badge { font-size: 13px; font-weight: 800; padding: 4px 14px; border-radius: 20px; letter-spacing: 1px; flex-shrink: 0; white-space: nowrap; }
  .verdict-badge.ACCEPT { background: #14532d; color: #4ade80; border: 1px solid #166534; }
  .verdict-badge.REJECT { background: #450a0a; color: #f87171; border: 1px solid #7f1d1d; }
  .verdict-badge.REWRITE { background: #431407; color: #fb923c; border: 1px solid #7c2d12; }
  .verdict-badge.HOLD { background: #1e293b; color: #94a3b8; border: 1px solid #334155; }
  .verdict-reason { font-size: 13px; color: #cbd5e1; line-height: 1.4; }
  .alert-block { margin: 10px 14px; padding: 10px 12px; border-radius: 7px; font-size: 12px; line-height: 1.6; }
  .alert-block.missing { background: #1c1000; border: 1px solid #78350f; color: #fbbf24; }
  .alert-block.errors { background: #160404; border: 1px solid #7f1d1d; color: #fca5a5; }
  .alert-title { font-weight: 800; margin-bottom: 5px; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; }
  .alert-block ul { margin: 4px 0 0 0; padding-left: 16px; }
  .rewrite-block { margin: 10px 14px; padding: 10px 12px; border-radius: 7px; background: #140e00; border: 1px solid #92400e; font-size: 12px; color: #fcd34d; }
  .rewrite-text { font-style: italic; color: #fbbf24; margin-top: 4px; }
  .output-section { padding: 10px 14px 14px; }
  .output-label { font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.8px; color: #64748b; margin-bottom: 6px; display: flex; justify-content: space-between; align-items: center; }
  .copy-btn { background: #2d3748; color: #94a3b8; border: none; border-radius: 4px; padding: 3px 8px; font-size: 10px; cursor: pointer; font-weight: 700; transition: background 0.15s, color 0.15s; }
  .copy-btn:hover { background: #3b82f6; color: white; }
  .copy-btn.copied { background: #14532d; color: #4ade80; }
  .copy-btn:disabled { opacity: 0.45; cursor: not-allowed; }
  pre#output {
    background: #0a0d14;
    border: 1px solid #2d3748;
    border-radius: 6px;
    padding: 12px;
    font-size: 12px;
    font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
    overflow: auto;
    overflow-x: auto;
    max-height: 340px;
    margin: 0;
    color: #94a3b8;
    line-height: 1.6;
  }
  .history-section { margin-top: 28px; padding-bottom: 40px; }
  .history-header { display: flex; align-items: baseline; justify-content: space-between; gap: 12px; margin-bottom: 10px; }
  .history-section h3 { font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.8px; margin: 0; }
  .history-count { font-size: 11px; color: #64748b; }
  .history-list { display: flex; flex-direction: column; gap: 6px; }
  .history-item { width: 100%; background: #1a1f2e; border: 1px solid #2d3748; border-radius: 7px; padding: 8px 12px; display: flex; align-items: center; gap: 10px; font-size: 12px; cursor: pointer; text-align: left; }
  .history-item:hover { border-color: #3b82f6; }
  .history-badge { font-size: 10px; font-weight: 800; padding: 2px 8px; border-radius: 10px; flex-shrink: 0; }
  .history-badge.ACCEPT { background: #14532d; color: #4ade80; }
  .history-badge.REJECT { background: #450a0a; color: #f87171; }
  .history-badge.REWRITE { background: #431407; color: #fb923c; }
  .history-badge.HOLD { background: #1e293b; color: #94a3b8; }
  .history-id { color: #64748b; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; flex-shrink: 0; }
  .history-reason { color: #94a3b8; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .empty-state { color: #475569; font-size: 12px; font-style: italic; }
  .no-decision { padding: 32px 16px; text-align: center; color: #475569; font-size: 13px; }
  @media (prefers-color-scheme: light) {
    body { background: #f8fafc; color: #0f172a; }
    .panel, #input { background: #ffffff; color: #0f172a; border-color: #cbd5e1; }
    .panel-header { background: #f1f5f9; border-bottom-color: #cbd5e1; }
    pre#output { background: #f8fafc; color: #334155; border-color: #cbd5e1; }
    .history-item { background: #ffffff; border-color: #cbd5e1; }
  }
</style>
</head>
<body>

<div class="header">
  <h1>CAPAS Claim Gate</h1>
  <p>Paste a claim/evidence JSON. Decisions are rule-based via <code>capas.py decide</code>. Schema errors surface as <code>HOLD</code>, never as guesses.</p>
</div>

<div class="samples-bar">
  <span>Load sample:</span>
  <button class="sample-btn accept" title="ACCEPT sample" aria-label="Load ACCEPT sample" onclick="loadSample('ACCEPT')">&#10003; ACCEPT</button>
  <button class="sample-btn rewrite" title="REWRITE sample" aria-label="Load REWRITE sample" onclick="loadSample('REWRITE')">&#8634; REWRITE</button>
  <button class="sample-btn hold" title="HOLD sample" aria-label="Load HOLD sample" onclick="loadSample('HOLD')">&#9646; HOLD</button>
  <button class="sample-btn invalid" title="INVALID sample" aria-label="Load INVALID sample" onclick="loadSample('INVALID')">&#10005; INVALID</button>
</div>

<div class="grid">
  <div>
    <div class="panel">
      <div class="panel-header">
        <span class="panel-title">Input JSON</span>
        <span class="panel-tag" id="type-label"></span>
      </div>
      <textarea id="input" spellcheck="false" aria-label="Claim and evidence JSON input" aria-describedby="json-status" oninput="onInputChange()">__SAMPLE_JSON__</textarea>
      <div class="json-status" id="json-status">Waiting for input...</div>
      <button class="decide-btn" id="decide-btn" aria-label="Decide claim verdict" onclick="decide()">Decide <span class="decide-hint">⌘↵</span></button>
    </div>
  </div>

  <div>
    <div class="panel">
      <div class="panel-header">
        <span class="panel-title">Decision</span>
        <button class="copy-btn" id="copy-btn" aria-label="Copy decision JSON" onclick="copyOutput()" disabled>Copy JSON</button>
      </div>
      <div id="verdict-area"><div class="no-decision">Run a decision to see results.</div></div>
      <div class="output-section">
        <div class="output-label"><span>Full output</span></div>
      <pre id="output"></pre>
      </div>
    </div>
  </div>
</div>

<div class="history-section">
  <div class="history-header">
    <h3>Recent decisions</h3>
    <span class="history-count" id="history-count">0/50 saved</span>
  </div>
  <div class="history-list" id="history-list">
    <div class="empty-state">No decisions yet.</div>
  </div>
</div>

<script>
    const sample = __SAMPLE_COMPACT_JSON__;
    const samples = __SAMPLES_JSON__;
    const disallowedAngleRegex = /[<>\u02c2\u02c3\u2039\u203a\u2329-\u232a\u276c-\u276d\u27e8-\u27e9\u29fc-\u29fd\u3008-\u3009\ufe64-\ufe65\uff1c-\uff1e]/u;
    const required = {
      exact_model_solution: ["abs_error", "tolerance"],
      physical_accuracy: ["within_chemical_accuracy"],
      universal_anchor_claim: ["anchor_mode", "local_property_tests_pass", "universal_anchor_pass"],
      claim_transition: ["upgrade_evidence_present"]
    };
    const claimTypes = Object.keys(required).sort();
    const historyLimit = 50;
    const historyStorageKey = "capas_decision_history_v1";
    let decisionHistory = loadHistory();

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
      if (typeof safeClaim.text === "string" && safeClaim.text.length > 4000) {
        errors.push("claim.text must be at most 4000 characters");
      }
      if (typeof safeClaim.text === "string" && containsAngleLikeCharacter(safeClaim.text)) {
        errors.push("claim.text must not contain angle brackets or Unicode angle-bracket homoglyphs");
      }
      if (typeof safeClaim.type === "string" && !required[safeClaim.type]) {
        errors.push(`claim.type must be one of: ${claimTypes.join(", ")}`);
      }
      const safeEvidence = evidence && typeof evidence === "object" && !Array.isArray(evidence) ? evidence : {};
      for (const field of ["abs_error", "tolerance"]) {
        if (Object.prototype.hasOwnProperty.call(safeEvidence, field) && typeof safeEvidence[field] !== "number") {
          errors.push(`evidence.${field} must be a number`);
        } else if (Object.prototype.hasOwnProperty.call(safeEvidence, field)) {
          if (!Number.isFinite(safeEvidence[field])) {
            errors.push(`evidence.${field} must be finite`);
          } else if (safeEvidence[field] < 0) {
            errors.push(`evidence.${field} must be >= 0`);
          }
        }
      }
      for (const field of ["within_chemical_accuracy", "local_property_tests_pass", "universal_anchor_pass", "upgrade_evidence_present"]) {
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
          input_claim: claim,
          verdict: "HOLD",
          reason: "input payload failed CAPAS schema validation",
          licensed_claim: claim.text,
          rewrite: null,
          missing_fields: [],
          required_fields: [],
          schema_errors: schemaErrors,
          fine_tune_ready: false,
          non_claim: "This decision is rule-based over supplied evidence fields, not an LLM judgment."
        };
      }
      const fields = required[claim.type];
      let missing = [];
      if (fields) {
        missing = fields.filter((field) => evidence[field] === undefined || evidence[field] === null || evidence[field] === "unknown");
      }
      let result = {
        input_claim: claim,
        verdict: "HOLD",
        reason: "unsupported claim type or missing evidence",
        licensed_claim: claim.text,
        rewrite: null,
        missing_fields: missing,
        required_fields: fields || [],
        schema_errors: [],
        fine_tune_ready: false,
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
      }
      return result;
    }

    function renderVerdict(result) {
      const verdict = result.verdict;
      let html = `<div class="verdict-banner"><span class="verdict-badge ${verdict}">${verdict}</span><span class="verdict-reason">${escHtml(result.reason)}</span></div>`;
      if (result.schema_errors && result.schema_errors.length) {
        html += `<div class="alert-block errors"><div class="alert-title">Schema errors</div><ul>${result.schema_errors.map((e) => `<li>${escHtml(e)}</li>`).join("")}</ul></div>`;
      }
      if (result.missing_fields && result.missing_fields.length) {
        html += `<div class="alert-block missing"><div class="alert-title">Missing required fields</div><ul>${result.missing_fields.map((f) => `<li><code>${escHtml(f)}</code></li>`).join("")}</ul></div>`;
      }
      if (result.rewrite) {
        html += `<div class="rewrite-block"><div class="alert-title">Licensed rewrite</div><div class="rewrite-text">"${escHtml(result.rewrite)}"</div></div>`;
      }
      document.getElementById("verdict-area").innerHTML = html;
    }

    function setCopyEnabled(enabled) {
      document.getElementById("copy-btn").disabled = !enabled;
    }

    function loadHistory() {
      try {
        const raw = localStorage.getItem(historyStorageKey);
        const parsed = raw ? JSON.parse(raw) : [];
        return Array.isArray(parsed) ? parsed.slice(0, historyLimit) : [];
      } catch (_) {
        return [];
      }
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
        `<button type="button" class="history-item" onclick="restoreHistory(${index})" aria-label="Restore decision ${escHtml(item.id)}">` +
        `<span class="history-badge ${item.verdict}">${item.verdict}</span>` +
        `<span class="history-id">${escHtml(item.id)}</span>` +
        `<span class="history-reason">${escHtml(item.reason)}</span>` +
        `</button>`
      )).join("");
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
      document.getElementById("output").textContent = JSON.stringify(item.decision, null, 2);
      setCopyEnabled(true);
    }

    function escHtml(value) {
      return String(value).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
    }

    function onInputChange() {
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
        status.textContent = "Valid JSON";
        status.className = "json-status valid";
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
          document.getElementById("output").textContent = "";
          setCopyEnabled(false);
          return;
        }
        button.classList.add("processing");
        const payload = JSON.parse(raw);
        const result = rule(payload);
        renderVerdict(result);
        document.getElementById("output").textContent = JSON.stringify(result, null, 2);
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
        document.getElementById("output").textContent = "";
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

    document.addEventListener("keydown", (event) => {
      if ((event.metaKey || event.ctrlKey) && event.key === "Enter") {
        event.preventDefault();
        decide();
      }
    });

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
