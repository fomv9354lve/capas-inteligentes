from __future__ import annotations

import argparse
import base64
import hashlib
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
CAPAS_CLAIM_SCHEMA_VERSION = "capas-claim-payload-v3"
CANONICAL_SCHEMA_ID = "https://fomv9354lve.github.io/capas-inteligentes/schema/v3/capas_claim_payload.schema.json"
CAPAS_UI_VERSION = "v13 · end-to-end gaps"


VALIDATION_COMMANDS = [
    ("external input schema", ["benchmarks/verify_external_input_schema.py"]),
    ("standalone pipeline MVP", ["benchmarks/verify_standalone_pipeline.py"]),
    ("claim gate UI", ["benchmarks/verify_claim_gate_ui.py"]),
    ("claim gate browser E2E", ["benchmarks/verify_claim_gate_ui_browser.py"]),
    ("customer product assets", ["benchmarks/verify_customer_product_assets.py"]),
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
    "causal_mechanism_claim": [
        "intervention_or_natural_experiment",
        "temporal_order_established",
        "confounders_controlled",
        "mechanism_evidence_present",
    ],
    "systematic_review_claim": [
        "protocol_registered",
        "inclusion_criteria_declared",
        "risk_of_bias_assessed",
        "effect_consistency",
    ],
    "evidence_conflict_claim": [
        "supporting_sources",
        "contradicting_sources",
        "conflict_resolution_method",
        "resolution_pre_registered",
    ],
    "multimodal_evidence_claim": [
        "modality",
        "source_hashes_verified",
        "cross_modal_alignment",
        "extraction_method_declared",
    ],
}

FINE_TUNE_BLOCKERS = [
    "no blind or external inference review is attached",
    "CAPAS gates supplied structured evidence; it does not infer hidden evidence",
    "training readiness requires source-backed evidence, semantic alignment, witness independence, and review",
]

FINE_TUNE_REQUIRED_FIELDS = [
    "source_backed_evidence",
    "external_review",
    "semantic_alignment",
    "witness_independence",
]

WITNESS_REGISTRY_PATH = ROOT / "docs" / "witness_registry.json"
REVIEWER_REGISTRY_PATH = ROOT / "docs" / "reviewer_registry.json"

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
    "causal_mechanism_claim": [
        "causal",
        "mechanism",
        "intervention",
        "confounder",
        "temporal",
    ],
    "systematic_review_claim": [
        "systematic",
        "review",
        "protocol",
        "inclusion",
        "bias",
    ],
    "evidence_conflict_claim": [
        "conflict",
        "contradict",
        "support",
        "resolution",
        "source",
    ],
    "multimodal_evidence_claim": [
        "multimodal",
        "image",
        "table",
        "video",
        "alignment",
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
        "$id": CANONICAL_SCHEMA_ID,
        "title": "CAPAS external claim/evidence payload",
        "x-capas-schema-version": CAPAS_CLAIM_SCHEMA_VERSION,
        "type": "object",
        "additionalProperties": True,
        "required": ["schema_version", "claim", "evidence"],
        "properties": {
            "schema_version": {
                "type": "string",
                "const": CAPAS_CLAIM_SCHEMA_VERSION,
                "description": "Payload schema version required for migration-safe CAPAS decisions.",
            },
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
                    "intervention_or_natural_experiment": {"type": "boolean"},
                    "temporal_order_established": {"type": "boolean"},
                    "confounders_controlled": {"type": "boolean"},
                    "mechanism_evidence_present": {"type": "boolean"},
                    "protocol_registered": {"type": "boolean"},
                    "inclusion_criteria_declared": {"type": "boolean"},
                    "risk_of_bias_assessed": {"type": "boolean"},
                    "effect_consistency": {"type": "boolean"},
                    "supporting_sources": {"type": "array", "items": {"type": "string"}},
                    "contradicting_sources": {"type": "array", "items": {"type": "string"}},
                    "conflict_resolution_method": {"type": "string", "pattern": NO_ANGLE_PATTERN},
                    "resolution_pre_registered": {"type": "boolean"},
                    "modality": {"type": "string", "pattern": NO_ANGLE_PATTERN},
                    "source_hashes_verified": {"type": "boolean"},
                    "cross_modal_alignment": {"type": "boolean"},
                    "extraction_method_declared": {"type": "boolean"},
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
            "training_evidence": {
                "type": "object",
                "additionalProperties": True,
                "description": "Optional positive-readiness packet. It never changes ACCEPT/REJECT/REWRITE/HOLD; it only controls fine_tune_ready after an ACCEPT verdict.",
                "properties": {
                    "source_backed_evidence": {"type": "boolean"},
                    "external_review": {"type": "boolean"},
                    "semantic_alignment": {"type": "boolean"},
                    "witness_independence": {"type": "boolean"},
                    "provenance": {
                        "type": "object",
                        "additionalProperties": True,
                        "properties": {
                            "sources": {"type": "array", "items": {"type": "string"}},
                            "source_urls": {"type": "array", "items": {"type": "string"}},
                            "source_hashes": {
                                "type": "object",
                                "additionalProperties": {"type": "string"},
                            },
                            "review_id": {"type": "string", "minLength": 1},
                            "review_sha256": {"type": "string", "minLength": 64, "maxLength": 64},
                            "review_hash": {"type": "string", "minLength": 64, "maxLength": 64},
                            "review_packet": {"type": "object", "additionalProperties": True},
                            "witness_id": {"type": "string", "minLength": 1},
                            "witness_registry_path": {"type": "string"},
                            "witness_registry_sha256": {"type": "string", "minLength": 64, "maxLength": 64},
                            "ro_crate_path": {"type": "string"},
                            "ro_crate_sha256": {"type": "string", "minLength": 64, "maxLength": 64},
                            "reviewer": {
                                "type": "object",
                                "additionalProperties": True,
                                "properties": {
                                    "reviewer_id": {"type": "string", "minLength": 1},
                                    "attestation": {"type": "string", "minLength": 1},
                                    "attestation_sha256": {"type": "string", "minLength": 64, "maxLength": 64},
                                },
                            },
                            "reviewer_registry_path": {"type": "string"},
                            "reviewer_registry_sha256": {"type": "string", "minLength": 64, "maxLength": 64},
                        },
                    },
                },
            },
        },
    }


def validate_external_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["payload must be a JSON object"]
    if payload.get("schema_version") != CAPAS_CLAIM_SCHEMA_VERSION:
        errors.append(f"schema_version must be {CAPAS_CLAIM_SCHEMA_VERSION}")
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
        "intervention_or_natural_experiment",
        "temporal_order_established",
        "confounders_controlled",
        "mechanism_evidence_present",
        "protocol_registered",
        "inclusion_criteria_declared",
        "risk_of_bias_assessed",
        "effect_consistency",
        "resolution_pre_registered",
        "source_hashes_verified",
        "cross_modal_alignment",
        "extraction_method_declared",
    ]
    for field in bool_fields:
        if field in evidence and not isinstance(evidence[field], bool):
            errors.append(f"evidence.{field} must be a boolean")

    string_fields = [
        "anchor_mode",
        "physical_evidence_level",
        "verification_independence",
        "conflict_resolution_method",
        "modality",
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
    for field in ("supporting_sources", "contradicting_sources"):
        if field in evidence:
            value = evidence[field]
            if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
                errors.append(f"evidence.{field} must be an array of strings")
            else:
                for index, item in enumerate(value):
                    _validate_no_angle_like(item, f"evidence.{field}[{index}]", errors)
    training_evidence = payload.get("training_evidence") if isinstance(payload, dict) else None
    if training_evidence is not None:
        if not isinstance(training_evidence, dict) or isinstance(training_evidence, list):
            errors.append("training_evidence must be an object")
        else:
            for field in FINE_TUNE_REQUIRED_FIELDS:
                if field in training_evidence and not isinstance(training_evidence[field], bool):
                    errors.append(f"training_evidence.{field} must be a boolean")
            provenance = training_evidence.get("provenance")
            if provenance is not None and (not isinstance(provenance, dict) or isinstance(provenance, list)):
                errors.append("training_evidence.provenance must be an object")
            elif isinstance(provenance, dict):
                for field in (
                    "review_id",
                    "review_sha256",
                    "review_hash",
                    "witness_id",
                    "witness_registry_path",
                    "witness_registry_sha256",
                    "ro_crate_path",
                    "ro_crate_sha256",
                    "reviewer_registry_path",
                    "reviewer_registry_sha256",
                ):
                    if field in provenance and not isinstance(provenance[field], str):
                        errors.append(f"training_evidence.provenance.{field} must be a string")
                for field in ("sources", "source_urls"):
                    if field in provenance and (
                        not isinstance(provenance[field], list)
                        or not all(isinstance(item, str) for item in provenance[field])
                    ):
                        errors.append(f"training_evidence.provenance.{field} must be an array of strings")
                if "source_hashes" in provenance and not isinstance(provenance["source_hashes"], dict):
                    errors.append("training_evidence.provenance.source_hashes must be an object")
                if "review_packet" in provenance and not isinstance(provenance["review_packet"], dict):
                    errors.append("training_evidence.provenance.review_packet must be an object")
                reviewer = provenance.get("reviewer")
                if reviewer is not None:
                    if not isinstance(reviewer, dict) or isinstance(reviewer, list):
                        errors.append("training_evidence.provenance.reviewer must be an object")
                    else:
                        for field in ("reviewer_id", "attestation", "attestation_sha256"):
                            if field in reviewer and not isinstance(reviewer[field], str):
                                errors.append(f"training_evidence.provenance.reviewer.{field} must be a string")
    return errors


def _stable_json_hash(value: Any) -> str:
    data = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _safe_local_path(value: str) -> Path | None:
    if value.startswith("file://"):
        value = value.removeprefix("file://")
    path = Path(value)
    if not path.is_absolute():
        path = ROOT / path
    try:
        resolved = path.resolve()
        resolved.relative_to(ROOT)
    except (ValueError, OSError):
        return None
    return resolved


def _load_json_if_exists(path: Path) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _source_url_verified(source: str, expected_hash: str | None) -> bool:
    if not expected_hash:
        return False
    if source.startswith(("http://", "https://")):
        if os.environ.get("CAPAS_VERIFY_REMOTE_SOURCES") != "1":
            return False
        try:
            request = Request(source, headers={"User-Agent": "CAPAS-Claim-Gate/1.0"})
            with urlopen(request, timeout=10) as response:
                return _sha256_bytes(response.read()) == expected_hash
        except (OSError, URLError):
            return False
    path = _safe_local_path(source)
    if not path or not path.exists() or not path.is_file():
        return False
    return _sha256_bytes(path.read_bytes()) == expected_hash


def _verify_review_hash(provenance: dict[str, Any]) -> bool:
    review_packet = provenance.get("review_packet")
    review_sha256 = provenance.get("review_sha256") or provenance.get("review_hash")
    return (
        isinstance(review_packet, dict)
        and isinstance(review_sha256, str)
        and _stable_json_hash(review_packet) == review_sha256
    )


def _verify_sources(provenance: dict[str, Any]) -> bool:
    source_urls = provenance.get("source_urls", provenance.get("sources", []))
    source_hashes = provenance.get("source_hashes", {})
    if not isinstance(source_urls, list) or not isinstance(source_hashes, dict) or not source_urls:
        return False
    for source in source_urls:
        if not isinstance(source, str) or not source.strip():
            return False
        expected_hash = source_hashes.get(source) or source_hashes.get(source.removeprefix("file://"))
        if not isinstance(expected_hash, str) or not _source_url_verified(source, expected_hash):
            return False
    return True


def _verify_witness_registry(provenance: dict[str, Any]) -> bool:
    witness_id = provenance.get("witness_id")
    registry_path_value = provenance.get("witness_registry_path", str(WITNESS_REGISTRY_PATH.relative_to(ROOT)))
    registry_sha256 = provenance.get("witness_registry_sha256")
    if not isinstance(witness_id, str) or not witness_id.strip():
        return False
    registry_path = _safe_local_path(str(registry_path_value))
    if not registry_path or not registry_path.exists() or not registry_path.is_file():
        return False
    if isinstance(registry_sha256, str) and _sha256_bytes(registry_path.read_bytes()) != registry_sha256:
        return False
    registry = _load_json_if_exists(registry_path)
    witnesses = registry.get("witnesses") if isinstance(registry, dict) else None
    return isinstance(witnesses, dict) and witness_id in witnesses


def _verify_ro_crate(provenance: dict[str, Any]) -> bool:
    crate_path_value = provenance.get("ro_crate_path")
    crate_sha256 = provenance.get("ro_crate_sha256")
    if not isinstance(crate_path_value, str) or not isinstance(crate_sha256, str):
        return False
    crate_path = _safe_local_path(crate_path_value)
    if not crate_path or not crate_path.exists() or not crate_path.is_file():
        return False
    if _sha256_bytes(crate_path.read_bytes()) != crate_sha256:
        return False
    crate = _load_json_if_exists(crate_path)
    if not isinstance(crate, dict):
        return False
    graph = crate.get("@graph")
    if not isinstance(graph, list):
        return False
    ids = {node.get("@id") for node in graph if isinstance(node, dict)}
    return "ro-crate-metadata.json" in ids and "./" in ids


def _verify_reviewer_attestation(provenance: dict[str, Any]) -> bool:
    reviewer = provenance.get("reviewer")
    if not isinstance(reviewer, dict):
        return False
    reviewer_id = reviewer.get("reviewer_id")
    attestation = reviewer.get("attestation")
    attestation_sha256 = reviewer.get("attestation_sha256")
    if not all(isinstance(value, str) and value.strip() for value in (reviewer_id, attestation, attestation_sha256)):
        return False
    if _sha256_bytes(attestation.encode("utf-8")) != attestation_sha256:
        return False
    registry_path_value = provenance.get("reviewer_registry_path", str(REVIEWER_REGISTRY_PATH.relative_to(ROOT)))
    registry_sha256 = provenance.get("reviewer_registry_sha256")
    registry_path = _safe_local_path(str(registry_path_value))
    if not registry_path or not registry_path.exists() or not registry_path.is_file():
        return False
    if isinstance(registry_sha256, str) and _sha256_bytes(registry_path.read_bytes()) != registry_sha256:
        return False
    registry = _load_json_if_exists(registry_path)
    reviewers = registry.get("reviewers") if isinstance(registry, dict) else None
    return isinstance(reviewers, dict) and reviewer_id in reviewers


def evaluate_fine_tune_readiness(
    payload: dict[str, Any],
    *,
    verdict: str,
    missing_fields: list[str],
    schema_errors: list[str],
) -> dict[str, Any]:
    training_evidence = payload.get("training_evidence")
    if not isinstance(training_evidence, dict):
        training_evidence = {}
    provenance = training_evidence.get("provenance")
    if not isinstance(provenance, dict):
        provenance = {}

    source_candidates = provenance.get("source_urls", provenance.get("sources", []))
    has_sources = (
        isinstance(source_candidates, list)
        and any(isinstance(source, str) and source.strip() for source in source_candidates)
    )
    criteria = {
        "verdict_accept": verdict == "ACCEPT",
        "schema_clean": not schema_errors and not missing_fields,
        "source_backed_evidence": training_evidence.get("source_backed_evidence") is True,
        "external_review": training_evidence.get("external_review") is True,
        "semantic_alignment": training_evidence.get("semantic_alignment") is True,
        "witness_independence": training_evidence.get("witness_independence") is True,
        "provenance_sources": has_sources,
        "review_hash_verified": _verify_review_hash(provenance),
        "source_urls_recoverable_hashable": _verify_sources(provenance),
        "witness_registry_resolved": _verify_witness_registry(provenance),
        "ro_crate_validated": _verify_ro_crate(provenance),
        "reviewer_attestation_verified": _verify_reviewer_attestation(provenance),
        "review_id_present": isinstance(provenance.get("review_id"), str) and bool(provenance["review_id"].strip()),
        "witness_id_present": isinstance(provenance.get("witness_id"), str) and bool(provenance["witness_id"].strip()),
    }
    blocker_labels = {
        "verdict_accept": "claim verdict is not ACCEPT",
        "schema_clean": "schema or required-field blockers remain",
        "source_backed_evidence": "source-backed evidence is not attached",
        "external_review": "external review is not attached",
        "semantic_alignment": "claim.text semantic alignment is not externally certified",
        "witness_independence": "witness independence is not externally certified",
        "provenance_sources": "provenance.sources or provenance.source_urls is empty",
        "review_hash_verified": "external review hash is missing or does not match review_packet",
        "source_urls_recoverable_hashable": "source URLs are not recoverable with matching hashes",
        "witness_registry_resolved": "witness_id is not resolvable in the witness registry",
        "ro_crate_validated": "RO-Crate provenance packet is missing, invalid, or hash-mismatched",
        "reviewer_attestation_verified": "reviewer identity or attestation is not verifiable",
        "review_id_present": "provenance.review_id is missing",
        "witness_id_present": "provenance.witness_id is missing",
    }
    blockers = [blocker_labels[key] for key, passed in criteria.items() if not passed]
    return {
        "fine_tune_ready": not blockers,
        "fine_tune_blockers": blockers,
        "fine_tune_criteria": criteria,
    }


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
        fine_tune = evaluate_fine_tune_readiness(
            payload if isinstance(payload, dict) else {},
            verdict="HOLD",
            missing_fields=[],
            schema_errors=schema_errors,
        )
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
            **fine_tune,
            "non_claim": "This decision is rule-based over supplied evidence fields, not an LLM judgment.",
        }

    claim_type = claim.get("type")
    required = REQUIRED_DECISION_FIELDS.get(str(claim_type))
    missing = [
        field
        for field in (required or [])
        if field not in evidence or evidence.get(field) is None or evidence.get(field) == "unknown"
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
    elif claim_type == "causal_mechanism_claim":
        intervention = evidence["intervention_or_natural_experiment"] is True
        temporal = evidence["temporal_order_established"] is True
        confounders = evidence["confounders_controlled"] is True
        mechanism = evidence["mechanism_evidence_present"] is True
        if intervention and temporal and confounders and mechanism:
            verdict = "ACCEPT"
            reason = "intervention/natural experiment, temporal order, confounder controls, and mechanism evidence all pass"
        elif intervention and temporal:
            verdict = "REWRITE"
            reason = "causal design and temporal order are present, but full causal mechanism licensing is incomplete"
            rewrite = "association with causal design support; full causal mechanism wording is not licensed"
            licensed_claim = rewrite
        else:
            verdict = "REJECT"
            reason = "causal claim lacks intervention/natural experiment evidence or temporal order"
    elif claim_type == "systematic_review_claim":
        protocol = evidence["protocol_registered"] is True
        inclusion = evidence["inclusion_criteria_declared"] is True
        bias = evidence["risk_of_bias_assessed"] is True
        consistency = evidence["effect_consistency"] is True
        if protocol and inclusion and bias and consistency:
            verdict = "ACCEPT"
            reason = "protocol, inclusion criteria, risk-of-bias assessment, and effect consistency all pass"
        elif protocol and inclusion:
            verdict = "REWRITE"
            reason = "review protocol and inclusion criteria are present, but bias/consistency evidence is incomplete"
            rewrite = "systematic review process is documented; strength or consistency of effect is not fully licensed"
            licensed_claim = rewrite
        else:
            verdict = "REJECT"
            reason = "systematic review claim lacks registered protocol or declared inclusion criteria"
    elif claim_type == "evidence_conflict_claim":
        supporting = evidence["supporting_sources"]
        contradicting = evidence["contradicting_sources"]
        method = str(evidence["conflict_resolution_method"]).strip()
        pre_registered = evidence["resolution_pre_registered"] is True
        if supporting and contradicting and method and pre_registered:
            verdict = "ACCEPT"
            reason = "supporting and contradicting sources are disclosed with a pre-registered conflict-resolution method"
        elif supporting and contradicting and method:
            verdict = "REWRITE"
            reason = "conflicting evidence is disclosed, but conflict resolution was not pre-registered"
            rewrite = "evidence conflict is disclosed; resolved conclusion is not fully licensed"
            licensed_claim = rewrite
        else:
            verdict = "REJECT"
            reason = "evidence conflict claim lacks supporting/contradicting source sets or a resolution method"
    elif claim_type == "multimodal_evidence_claim":
        if (
            evidence["source_hashes_verified"] is True
            and evidence["cross_modal_alignment"] is True
            and evidence["extraction_method_declared"] is True
            and str(evidence["modality"]).strip()
        ):
            verdict = "ACCEPT"
            reason = "modality, source hashes, cross-modal alignment, and extraction method are declared"
        elif evidence["source_hashes_verified"] is True and str(evidence["modality"]).strip():
            verdict = "REWRITE"
            reason = "multimodal source identity is verified, but alignment or extraction method is not fully licensed"
            rewrite = "multimodal evidence is identified; cross-modal claim is not fully licensed"
            licensed_claim = rewrite
        else:
            verdict = "REJECT"
            reason = "multimodal claim lacks verified source hashes or declared modality"

    fine_tune = evaluate_fine_tune_readiness(
        payload,
        verdict=verdict,
        missing_fields=missing,
        schema_errors=[],
    )

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
        **fine_tune,
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

    batch_blockers = []
    if not results:
        batch_blockers.append("batch has no items")
    if any(entry["result"].get("fine_tune_ready") is not True for entry in results):
        batch_blockers.append("one or more batch items are not fine_tune_ready")
    if mode != "decide":
        batch_blockers.append("fine-tune readiness is only emitted for deterministic decide batches")

    return {
        "schema_version": CAPAS_CLAIM_SCHEMA_VERSION,
        "batch_mode": mode,
        "item_count": len(items),
        "results": results,
        "summary": dict(sorted(verdicts.items())),
        "fine_tune_ready": not batch_blockers,
        "fine_tune_blockers": batch_blockers,
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

    if claim_type == "causal_mechanism_claim":
        if evidence.get("intervention_or_natural_experiment") is False and "causal" in text:
            issues.append("claim.text uses causal wording without intervention or natural-experiment evidence")
        if evidence.get("confounders_controlled") is False and "causal" in text:
            warnings.append("causal wording is weaker when confounder controls are false")

    if claim_type == "systematic_review_claim" and "systematic" in text:
        if evidence.get("protocol_registered") is False:
            issues.append("systematic review wording requires a registered protocol")

    if claim_type == "evidence_conflict_claim":
        if not evidence.get("contradicting_sources"):
            warnings.append("evidence_conflict_claim should disclose contradicting_sources")

    if claim_type == "multimodal_evidence_claim":
        if evidence.get("cross_modal_alignment") is False:
            issues.append("multimodal claim requires cross-modal alignment")

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


def _corpus_query_terms(payload: dict[str, Any]) -> list[str]:
    claim = payload.get("claim", {}) if isinstance(payload, dict) else {}
    claim_type = str(claim.get("type", ""))
    text = str(claim.get("text", "")).lower()
    terms = set(REQUIRED_DECISION_FIELDS.get(claim_type, []))
    terms.update(CLAIM_TYPE_TERMS.get(claim_type, []))
    for token in re.findall(r"[a-zA-Z][a-zA-Z0-9_-]{4,}", text):
        terms.add(token.lower())
    return sorted(term for term in terms if term)


def _read_corpus_source_path(path_value: str, payload: dict[str, Any]) -> tuple[str, str | None]:
    path = (ROOT / path_value).resolve()
    try:
        path.relative_to(ROOT.resolve())
    except ValueError:
        raise ValueError("source.path must stay inside the CAPAS repository")
    if not path.exists():
        return "", f"corpus source not found: {path_value}"
    query_terms = _corpus_query_terms(payload)

    def record_text(record: Any, index: int) -> str:
        if isinstance(record, str):
            return record
        if isinstance(record, dict):
            parts = [
                str(record.get(key, ""))
                for key in ("id", "title", "abstract", "text", "snippet", "source")
                if record.get(key) is not None
            ]
            return "\n".join(parts)
        return str(record)

    documents: list[str] = []
    if path.is_dir():
        for item in sorted(path.iterdir()):
            if item.is_file() and item.suffix.lower() in {".txt", ".md", ".json", ".jsonl"}:
                text, note = _read_corpus_source_path(str(item.relative_to(ROOT)), payload)
                if text:
                    documents.append(text)
                elif note:
                    documents.append(f"# {note}")
    elif path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        records = data if isinstance(data, list) else data.get("documents", []) if isinstance(data, dict) else []
        documents = [record_text(record, index) for index, record in enumerate(records)]
    elif path.suffix.lower() == ".jsonl":
        documents = [
            record_text(json.loads(line), index)
            for index, line in enumerate(path.read_text(encoding="utf-8").splitlines())
            if line.strip()
        ]
    else:
        documents = [path.read_text(encoding="utf-8")]

    selected = []
    for document in documents:
        lowered = document.lower()
        score = sum(1 for term in query_terms if term.lower() in lowered)
        if score:
            selected.append((score, document))
    selected.sort(key=lambda pair: pair[0], reverse=True)
    if not selected:
        return "", "corpus source had no deterministic matches for claim terms or required fields"
    return "\n\n--- corpus match ---\n\n".join(document for _, document in selected[:5]), None


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
        elif kind == "corpus" and isinstance(item.get("path"), str):
            text, maybe_note = _read_corpus_source_path(str(item["path"]), payload)
            retrieval_status = "corpus_matched" if text else "not_retrieved"
            note = maybe_note or ""
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
        "intervention_or_natural_experiment",
        "temporal_order_established",
        "confounders_controlled",
        "mechanism_evidence_present",
        "protocol_registered",
        "inclusion_criteria_declared",
        "risk_of_bias_assessed",
        "effect_consistency",
        "resolution_pre_registered",
        "source_hashes_verified",
        "cross_modal_alignment",
        "extraction_method_declared",
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
        "conflict_resolution_method",
        "modality",
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
        "schema_version": CAPAS_CLAIM_SCHEMA_VERSION,
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
        "schema_version": CAPAS_CLAIM_SCHEMA_VERSION,
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
            "schema_version": CAPAS_CLAIM_SCHEMA_VERSION,
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
            "schema_version": CAPAS_CLAIM_SCHEMA_VERSION,
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
            "schema_version": CAPAS_CLAIM_SCHEMA_VERSION,
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
            "schema_version": CAPAS_CLAIM_SCHEMA_VERSION,
            "claim": {
                "id": "",
                "type": "unsupported_claim_type",
                "text": "This payload is structurally invalid because the claim id is empty.",
            },
            "evidence": "not an object",
        },
        "CAUSAL": {
            "schema_version": CAPAS_CLAIM_SCHEMA_VERSION,
            "claim": {
                "id": "sample_causal_mechanism",
                "type": "causal_mechanism_claim",
                "text": "The intervention causally changes the measured outcome through the declared mechanism.",
            },
            "evidence": {
                "intervention_or_natural_experiment": True,
                "temporal_order_established": True,
                "confounders_controlled": True,
                "mechanism_evidence_present": True,
            },
        },
        "SYSTEMATIC": {
            "schema_version": CAPAS_CLAIM_SCHEMA_VERSION,
            "claim": {
                "id": "sample_systematic_review",
                "type": "systematic_review_claim",
                "text": "The systematic review supports the reported effect across included studies.",
            },
            "evidence": {
                "protocol_registered": True,
                "inclusion_criteria_declared": True,
                "risk_of_bias_assessed": True,
                "effect_consistency": True,
            },
        },
        "CONFLICT": {
            "schema_version": CAPAS_CLAIM_SCHEMA_VERSION,
            "claim": {
                "id": "sample_evidence_conflict",
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
        "MULTIMODAL": {
            "schema_version": CAPAS_CLAIM_SCHEMA_VERSION,
            "claim": {
                "id": "sample_multimodal_evidence",
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
    }


def _csp_sha256(value: str) -> str:
    digest = hashlib.sha256(value.encode("utf-8")).digest()
    return "'sha256-" + base64.b64encode(digest).decode("ascii") + "'"


def _apply_inline_csp_hashes(html: str) -> str:
    style_blocks = re.findall(r"<style>(.*?)</style>", html, flags=re.S)
    script_blocks = re.findall(r"<script>(.*?)</script>", html, flags=re.S)
    event_handlers = re.findall(r'\son(?:click|input|keydown)="([^"]+)"', html)
    style_attrs = re.findall(r'\sstyle="([^"]+)"', html)

    script_hashes = sorted({_csp_sha256(block) for block in script_blocks} | {_csp_sha256(handler) for handler in event_handlers})
    style_hashes = sorted({_csp_sha256(block) for block in style_blocks} | {_csp_sha256(attr) for attr in style_attrs})
    csp = (
        "default-src 'self'; "
        "img-src 'self' data:; "
        f"style-src 'self' 'unsafe-hashes' {' '.join(style_hashes)}; "
        f"script-src 'self' 'unsafe-hashes' {' '.join(script_hashes)}; "
        "object-src 'none'; base-uri 'none'; form-action 'none'; connect-src 'none'"
    )
    return re.sub(
        r'<meta http-equiv="Content-Security-Policy" content="[^"]+">',
        f'<meta http-equiv="Content-Security-Policy" content="{csp}">',
        html,
        count=1,
    )


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
  /* CAPAS Claim Gate - Design System v12 */
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
  .product-hero {
    display: grid;
    grid-template-columns: minmax(0, 1.05fr) minmax(320px, 0.95fr);
    gap: 18px;
    align-items: stretch;
    margin-bottom: 22px;
  }
  .hero-copy {
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    background: linear-gradient(180deg, var(--bg-2), var(--bg));
    box-shadow: var(--shadow);
    padding: 22px;
  }
  .hero-eyebrow {
    color: var(--accent-hover);
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0.9px;
    text-transform: uppercase;
    margin-bottom: 8px;
  }
  .hero-copy h2 {
    color: var(--text-1);
    font-size: 28px;
    line-height: 1.1;
    margin-bottom: 10px;
    letter-spacing: 0;
  }
  .hero-copy p { color: var(--text-2); font-size: 14px; max-width: 700px; }
  .hero-actions { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 16px; }
  .hero-primary {
    background: var(--accent);
    border-color: var(--accent);
    color: white;
    box-shadow: 0 6px 18px rgba(124, 127, 255, 0.25);
  }
  .hero-primary:hover { background: var(--accent-hover); border-color: var(--accent-hover); }
  .hero-link { text-decoration: none; }
  .hero-metrics { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 8px; margin-top: 18px; }
  .hero-metric { border: 1px solid var(--border); border-radius: var(--radius); background: var(--bg-2); padding: 10px; }
  .hero-metric strong { display: block; color: var(--text-1); font-size: 18px; line-height: 1.2; }
  .hero-metric span { color: var(--text-3); font-size: 11px; }
  .hero-shot {
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    background: var(--bg-2);
    box-shadow: var(--shadow);
    overflow: hidden;
  }
  .shot-top { display: flex; gap: 6px; align-items: center; height: 34px; padding: 0 12px; border-bottom: 1px solid var(--border); background: var(--bg-3); }
  .shot-dot { width: 7px; height: 7px; border-radius: 50%; background: var(--border-2); }
  .shot-body { padding: 14px; display: grid; gap: 10px; }
  .shot-row { display: grid; grid-template-columns: auto minmax(0, 1fr) auto; gap: 8px; align-items: center; border: 1px solid var(--border); border-radius: var(--radius-sm); padding: 8px; background: var(--bg); }
  .shot-row span { color: var(--text-3); font-size: 11px; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }
  .workflow-strip {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 10px;
    margin-bottom: 18px;
  }
  .workflow-step, .exec-card {
    border: 1px solid var(--border);
    border-radius: var(--radius);
    background: var(--bg-2);
    padding: 12px;
  }
  .workflow-step strong, .exec-card strong { display: block; color: var(--text-1); font-size: 13px; margin-bottom: 4px; }
  .workflow-step span, .exec-card span { color: var(--text-3); font-size: 11px; line-height: 1.4; }
  .exec-dashboard {
    display: grid;
    grid-template-columns: repeat(6, minmax(0, 1fr));
    gap: 8px;
    margin: 0 0 18px;
  }
  .exec-card strong { font-size: 20px; font-variant-numeric: tabular-nums; }
  .business-system {
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(320px, 0.85fr);
    gap: 16px;
    margin-bottom: 18px;
  }
  .workflow-board {
    display: grid;
    grid-template-columns: repeat(5, minmax(0, 1fr));
    gap: 8px;
    padding: 14px;
  }
  .workflow-stage {
    border: 1px solid var(--border);
    border-radius: var(--radius);
    background: var(--bg);
    padding: 10px;
    min-height: 112px;
  }
  .workflow-stage strong { display: block; color: var(--text-1); font-size: 12px; margin-bottom: 5px; }
  .workflow-stage span { display: block; color: var(--text-3); font-size: 11px; line-height: 1.45; }
  .roi-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 10px;
    padding: 14px;
  }
  .roi-result {
    grid-column: 1 / -1;
    border: 1px solid var(--green-border);
    border-radius: var(--radius);
    background: var(--green-bg);
    padding: 12px;
  }
  .roi-result strong { display: block; color: var(--green); font-size: 24px; font-variant-numeric: tabular-nums; }
  .roi-result span { color: var(--text-2); font-size: 12px; }
  .guided-panel { margin-bottom: 16px; }
  .guided-body { padding: 14px 16px; display: grid; gap: 12px; }
  .starter-guide {
    display: grid;
    gap: 8px;
    border: 1px solid rgba(124, 127, 255, 0.28);
    border-radius: var(--radius);
    background: var(--accent-glow);
    padding: 12px;
    color: var(--text-2);
    font-size: 12px;
    line-height: 1.55;
  }
  .starter-guide strong { color: var(--text-1); font-size: 13px; }
  .starter-steps {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 8px;
  }
  .starter-step {
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    background: var(--bg-2);
    padding: 8px;
  }
  .starter-step span { display: block; color: var(--accent); font-size: 10px; font-weight: 800; letter-spacing: 0.5px; text-transform: uppercase; }
  .flow-section {
    display: grid;
    gap: 10px;
    border: 1px solid var(--border);
    border-radius: var(--radius);
    background: var(--bg-2);
    padding: 12px;
  }
  .flow-section + .flow-section { margin-top: 2px; }
  .flow-title {
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 0;
    color: var(--text-1);
    font-size: 12px;
    font-weight: 900;
    letter-spacing: 0.4px;
    text-transform: uppercase;
  }
  .flow-step-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 22px;
    height: 22px;
    border-radius: 999px;
    background: var(--accent);
    color: white;
    font-size: 11px;
    font-weight: 900;
    font-variant-numeric: tabular-nums;
    flex: 0 0 auto;
  }
  .flow-copy {
    margin: -4px 0 0;
    color: var(--text-3);
    font-size: 11px;
    line-height: 1.5;
  }
  .builder-shell { display: grid; grid-template-columns: minmax(0, 1.3fr) minmax(250px, 0.7fr); gap: 14px; align-items: start; }
  .builder-main, .builder-rail { display: grid; gap: 12px; min-width: 0; }
  .builder-rail {
    border: 1px solid var(--border);
    border-radius: var(--radius);
    background: var(--bg);
    padding: 12px;
  }
  .builder-rail h3 {
    margin: 0;
    color: var(--text-1);
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 0.4px;
  }
  .builder-rail p, .builder-rail li { color: var(--text-2); font-size: 12px; line-height: 1.55; }
  .builder-rail ul { margin: 0; padding-left: 18px; }
  .builder-contract {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 8px;
  }
  .contract-pill {
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    background: var(--bg-2);
    padding: 8px;
  }
  .contract-pill strong { display: block; color: var(--text-1); font-size: 11px; margin-bottom: 2px; }
  .contract-pill span { color: var(--text-3); font-size: 10px; }
  .contract-progress {
    grid-column: 1 / -1;
    border: 1px solid var(--green-border);
    border-radius: var(--radius-sm);
    background: var(--green-bg);
    padding: 8px;
    color: var(--green);
    font-size: 11px;
    font-weight: 800;
  }
  .builder-preview {
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    background: var(--bg-2);
    padding: 10px;
    color: var(--text-2);
    font-family: var(--mono);
    font-size: 11px;
    line-height: 1.55;
    overflow-wrap: anywhere;
  }
  .guided-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }
  .guided-field { display: grid; gap: 5px; min-width: 0; }
  .guided-field label { color: var(--text-3); font-size: 10px; font-weight: 800; letter-spacing: 0.6px; text-transform: uppercase; }
  .type-help {
    grid-column: 1 / -1;
    color: var(--text-2);
    font-size: 12px;
    line-height: 1.5;
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    background: var(--bg);
    padding: 8px 9px;
  }
  .guided-field input, .guided-field textarea, .guided-field select {
    width: 100%;
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    background: var(--bg);
    color: var(--text-1);
    font-family: var(--font);
    font-size: 12px;
    padding: 8px 9px;
  }
  .guided-field textarea { min-height: 72px; resize: vertical; }
  .guided-field.full { grid-column: 1 / -1; }
  .ingest-panel { margin-bottom: 16px; }
  .ingest-toolbar { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
  .ingest-report {
    border: 1px solid var(--border);
    border-radius: var(--radius);
    background: var(--bg);
    padding: 10px 12px;
    color: var(--text-2);
    font-size: 12px;
  }
  .candidate-table { display: grid; gap: 8px; }
  .candidate-row {
    border: 1px solid var(--border);
    border-radius: var(--radius);
    background: var(--bg);
    padding: 10px;
  }
  .candidate-summary { display: grid; grid-template-columns: auto minmax(0, 1fr) auto; gap: 10px; align-items: center; }
  .candidate-text { color: var(--text-2); font-size: 12px; overflow-wrap: anywhere; }
  .candidate-spans { margin-top: 8px; display: grid; gap: 5px; }
  .candidate-span {
    border-left: 3px solid var(--accent);
    background: var(--bg-2);
    border-radius: var(--radius-sm);
    padding: 7px 9px;
    color: var(--text-3);
    font-family: var(--mono);
    font-size: 11px;
    overflow-wrap: anywhere;
  }
  .sensitive-active {
    border-color: var(--warning);
    background: rgba(251, 191, 36, 0.06);
    color: var(--warning);
  }
  .samples-bar { display: flex; flex-wrap: wrap; align-items: center; gap: 6px; margin-bottom: 20px; }
  .samples-bar > span { font-size: 11px; color: var(--text-3); text-transform: uppercase; letter-spacing: 0.6px; }
  .mode-tabs { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 8px; margin-bottom: 16px; }
  .mode-tab {
    min-height: 40px;
    padding: 9px 12px;
    border: 1px solid var(--border);
    border-radius: var(--radius);
    background: var(--bg-2);
    color: var(--text-2);
    font-family: var(--font);
    font-size: 12px;
    font-weight: 800;
    cursor: pointer;
    transition: all var(--t);
  }
  .mode-tab:hover { background: var(--bg-3); border-color: var(--border-2); color: var(--text-1); }
  .mode-tab[aria-selected="true"] { color: var(--accent); border-color: rgba(124, 127, 255, 0.36); background: var(--accent-glow); }
  .advanced-badge {
    display: inline-flex;
    margin-left: 6px;
    padding: 1px 6px;
    border: 1px solid var(--border);
    border-radius: 999px;
    color: var(--text-3);
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 0.4px;
    text-transform: uppercase;
  }
  .mode-note { margin: -8px 0 16px; color: var(--text-3); font-size: 12px; }
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
  .topbar-source { text-decoration: none; }
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
  .fine-tune-block { margin: 12px 16px; padding: 12px 14px; border-radius: var(--radius); border: 1px solid var(--border); background: var(--bg); }
  .fine-tune-head { display: flex; align-items: center; justify-content: space-between; gap: 10px; margin-bottom: 8px; }
  .fine-tune-title { color: var(--text-1); font-size: 11px; font-weight: 800; letter-spacing: 0.7px; text-transform: uppercase; }
  .fine-tune-status { border: 1px solid; border-radius: 999px; padding: 2px 8px; font-size: 10px; font-weight: 800; white-space: nowrap; }
  .fine-tune-status.ready { color: var(--green); background: var(--green-bg); border-color: var(--green-border); }
  .fine-tune-status.blocked { color: var(--warning); background: rgba(251, 191, 36, 0.06); border-color: rgba(251, 191, 36, 0.2); }
  .fine-tune-summary { color: var(--text-2); font-size: 12px; line-height: 1.6; }
  .fine-tune-block ul { margin-top: 8px; padding-left: 18px; color: var(--text-2); font-size: 12px; line-height: 1.6; }
  .batch-row-ft { justify-self: end; color: var(--text-3); font-size: 10px; font-weight: 800; letter-spacing: 0.4px; text-transform: uppercase; white-space: nowrap; }
  .assist-block { margin: 12px 16px; padding: 12px 14px; border-radius: var(--radius); background: var(--accent-glow); border-color: rgba(99, 102, 241, 0.24); color: var(--assist-text); }
  .assist-block pre { background: var(--bg); border-color: rgba(99, 102, 241, 0.24); color: var(--assist-text); }
  .batch-progress { margin-top: 10px; height: 8px; overflow: hidden; border: 1px solid var(--border); border-radius: 999px; background: var(--bg); }
  .batch-progress-fill { height: 100%; width: var(--batch-progress, 100%); background: linear-gradient(90deg, var(--accent), var(--green)); }
  .batch-progress-label { margin-top: 6px; color: var(--text-3); font-size: 11px; font-weight: 600; }
  .batch-table { display: grid; gap: 6px; margin-top: 12px; }
  .batch-row { border: 1px solid var(--border); border-radius: var(--radius-sm); background: var(--bg); overflow: hidden; }
  .batch-row summary { display: grid; grid-template-columns: auto minmax(0, 1fr) minmax(0, 1.4fr) auto; gap: 8px; align-items: center; padding: 8px 10px; cursor: pointer; list-style: none; }
  .batch-row summary::-webkit-details-marker { display: none; }
  .batch-row-id, .batch-row-reason { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .batch-row-id { color: var(--text-1); font-family: var(--mono); font-size: 11px; }
  .batch-row-reason { color: var(--text-3); font-size: 11px; }
  .batch-row pre { margin: 0; border-top: 1px solid var(--border); border-radius: 0; max-height: 220px; overflow: auto; }
  .output-inspector { display: grid; gap: 8px; margin-bottom: 10px; }
  .inspector-card { border: 1px solid var(--border); border-radius: var(--radius); background: var(--bg); overflow: hidden; }
  .inspector-card summary { display: flex; align-items: center; justify-content: space-between; gap: 10px; min-height: 36px; padding: 9px 12px; color: var(--text-2); font-size: 11px; font-weight: 800; letter-spacing: 0.6px; text-transform: uppercase; cursor: pointer; list-style: none; }
  .inspector-card summary::-webkit-details-marker { display: none; }
  .inspector-card summary::after { content: "Open"; color: var(--text-3); font-size: 10px; }
  .inspector-card[open] summary { border-bottom: 1px solid var(--border); }
  .inspector-card[open] summary::after { content: "Close"; }
  .inspector-body { padding: 10px 12px; color: var(--text-2); font-size: 12px; line-height: 1.6; }
  .inspector-body dl { display: grid; grid-template-columns: minmax(110px, 0.45fr) minmax(0, 1fr); gap: 6px 10px; margin: 0; }
  .inspector-body dt { color: var(--text-3); font-weight: 800; text-transform: uppercase; font-size: 10px; letter-spacing: 0.5px; }
  .inspector-body dd { margin: 0; overflow-wrap: anywhere; }
  .inspector-body ul { margin: 0; padding-left: 18px; }
  .inspector-empty { color: var(--text-3); }
  .rewrite-block { margin: 12px 16px; padding: 12px 14px; border-radius: var(--radius); background: var(--orange-bg); border-color: var(--orange-border); }
  .rewrite-text { color: var(--text-1); }
  .rewrite-diff { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 10px; }
  .rewrite-pane { background: var(--bg); border: 1px solid var(--orange-border); border-radius: var(--radius-sm); padding: 10px; min-width: 0; }
  .rewrite-pane-label { font-size: 10px; font-weight: 700; color: var(--orange); text-transform: uppercase; letter-spacing: 0.7px; margin-bottom: 5px; }
  .rewrite-pane-text { font-size: 12px; color: var(--text-2); line-height: 1.5; overflow-wrap: anywhere; }
  .output-section { padding: 12px 16px; }
  .output-label { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.7px; color: var(--text-3); }
  .output-label::after { content: ""; flex: 1; height: 1px; background: var(--border); }
  .output-details { border: 1px solid var(--border); border-radius: var(--radius); background: var(--bg); overflow: hidden; }
  .output-details summary {
    display: flex;
    align-items: center;
    justify-content: space-between;
    min-height: 36px;
    padding: 9px 12px;
    color: var(--text-2);
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0.6px;
    text-transform: uppercase;
    cursor: pointer;
  }
  .output-details summary::after { content: "Expand"; color: var(--text-3); font-size: 10px; font-weight: 700; }
  .output-details[open] summary { border-bottom: 1px solid var(--border); }
  .output-details[open] summary::after { content: "Collapse"; }
  pre#output { background: var(--bg); border: 1px solid var(--border); border-radius: var(--radius); color: var(--text-2); max-width: 100%; min-width: 0; max-height: 360px; padding: 14px; font-size: 11.5px; font-family: var(--mono); line-height: 1.7; overflow: auto; white-space: pre; }
  .output-details pre#output { border: 0; border-radius: 0; margin: 0; }
  .gate-section { scroll-margin-top: 76px; }
  #input.payload-flash { animation: payload-flash 1.1s ease-out; }
  @keyframes payload-flash {
    0% { box-shadow: inset 0 0 0 999px rgba(124, 127, 255, 0.10), inset 3px 0 0 var(--accent); }
    100% { box-shadow: inset 3px 0 0 var(--green); }
  }
  .payload-loaded-badge {
    display: none;
    padding: 3px 8px;
    border: 1px solid var(--green-border);
    border-radius: 999px;
    background: var(--green-bg);
    color: var(--green);
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 0.5px;
    text-transform: uppercase;
  }
  .payload-loaded-badge.show { display: inline-flex; }
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
  .history-heading { color: var(--text-2); font-size: 12px; font-weight: 800; letter-spacing: 0.7px; text-transform: uppercase; }
  .history-tools { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; margin-bottom: 10px; }
  .history-filter, .history-select { min-height: 28px; border: 1px solid var(--border); border-radius: var(--radius-sm); background: var(--bg-2); color: var(--text-2); font-family: var(--font); font-size: 11px; font-weight: 600; }
  .history-filter { flex: 1 1 220px; min-width: 0; padding: 5px 9px; }
  .history-select { padding: 5px 8px; }
  .history-list { display: flex; flex-direction: column; gap: 4px; overflow-x: auto; scrollbar-width: thin; }
  .history-count { color: var(--text-3); }
  .audit-table { display: grid; gap: 4px; min-width: 820px; }
  .audit-row { display: grid; grid-template-columns: 92px minmax(140px, 1fr) 150px minmax(190px, 1.5fr) 116px 110px; gap: 8px; align-items: stretch; }
  .audit-row.header { padding: 0 8px; color: var(--text-3); font-size: 10px; font-weight: 800; letter-spacing: 0.6px; text-transform: uppercase; }
  .history-row { display: contents; }
  .history-item { display: grid; grid-template-columns: subgrid; grid-column: 1 / 6; align-items: center; gap: 8px; width: 100%; padding: 9px 8px; background: var(--bg-2); border: 1px solid var(--border); border-radius: var(--radius); color: var(--text-1); font-family: var(--font); transition: all var(--t); cursor: pointer; text-align: left; }
  .history-item:hover { background: var(--bg-3); border-color: var(--border-2); transform: translateX(2px); }
  .history-delete { padding: 0 10px; border: 1px solid var(--border); border-radius: var(--radius); background: var(--bg-2); color: var(--text-3); font-family: var(--font); font-size: 11px; font-weight: 700; cursor: pointer; }
  .history-delete:hover { color: var(--red); border-color: var(--red-border); background: var(--red-bg); }
  .history-badge { border: 1px solid; }
  .history-badge.ACCEPT { color: var(--green); background: var(--green-bg); border-color: var(--green-border); }
  .history-badge.REJECT { color: var(--red); background: var(--red-bg); border-color: var(--red-border); }
  .history-badge.REWRITE { color: var(--orange); background: var(--orange-bg); border-color: var(--orange-border); }
  .history-badge.HOLD { color: var(--slate); background: var(--slate-bg); border-color: var(--slate-border); }
  .history-id { color: var(--text-1); }
  .history-type { color: var(--text-3); font-family: var(--mono); font-size: 10px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .history-reason { color: var(--text-3); }
  .history-ts { margin-left: auto; color: var(--text-3); font-size: 10px; font-variant-numeric: tabular-nums; white-space: nowrap; }
  .empty-state, .no-decision { color: var(--text-3); font-size: 13px; }
  .no-decision { padding: 32px 16px; text-align: center; line-height: 1.65; }
  .no-decision strong { display: block; color: var(--text-1); font-size: 14px; margin-bottom: 4px; }
  .action-helper {
    border-top: 1px solid var(--border);
    background: var(--bg-2);
    color: var(--text-3);
    font-size: 11px;
    line-height: 1.45;
    padding: 7px 14px;
  }
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
  .app-footer a { color: var(--accent); text-decoration: none; }
  .app-footer a:hover { text-decoration: underline; }
  .footer-links { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 8px; }
  .sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
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
    .product-hero, .business-system { grid-template-columns: 1fr; }
    .hero-metrics, .exec-dashboard, .workflow-strip, .workflow-board { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .guided-grid { grid-template-columns: 1fr; }
    .builder-shell, .builder-contract { grid-template-columns: 1fr; }
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
    .mode-tabs { grid-template-columns: 1fr; }
    .grid { grid-template-columns: 1fr; }
    #input { min-height: 260px; }
    pre#output { max-height: 280px; }
    .rewrite-diff { grid-template-columns: 1fr; }
    .modal-backdrop { align-items: stretch; padding: 12px; }
    .help-modal { width: 100%; max-height: calc(100vh - 24px); }
    .history-header { align-items: flex-start; gap: 12px; }
    .history-actions { flex-wrap: wrap; justify-content: flex-end; }
    .audit-row { grid-template-columns: 1fr; }
    .audit-row.header { display: none; }
    .history-item { grid-template-columns: 1fr; grid-column: auto; align-items: flex-start; }
    .history-reason { overflow-wrap: anywhere; }
  }
  @media (max-width: 560px) {
    .app-body { padding: 12px 12px 48px; }
    .hero-copy { padding: 16px; }
    .hero-copy h2 { font-size: 22px; }
    .hero-metrics, .exec-dashboard, .workflow-strip, .workflow-board, .roi-grid { grid-template-columns: 1fr; }
    .roi-result { grid-column: auto; }
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

  /* ================================================================
     CAPAS Professional Redesign v14
     Aesthetic: IBM Carbon / Linear / Raycast
     Goal: app-shell architecture; gate visible in first screen.
     ================================================================ */
  body { max-width: 1100px; margin: 0 auto; }
  main.app-body { display: flex; flex-direction: column; gap: 0; padding: 0; }
  .topbar {
    height: 44px;
    padding: 0 20px;
    background: var(--bg);
    backdrop-filter: none;
  }
  .topbar-divider, .topbar-subtitle { display: none; }
  .topbar-logo { font-size: 13px; font-weight: 700; }
  .topbar-logo-icon { width: 22px; height: 22px; border-radius: 5px; font-size: 10px; }
  .topbar-actions { gap: 2px; }
  .topbar-actions .copy-btn { min-height: 28px; padding: 4px 10px; font-size: 12px; }
  .topbar-badge { font-size: 10px; padding: 2px 7px; }
  .topbar-source,
  #schema-version-badge,
  .topbar-actions > .topbar-badge:not(#shared-payload-badge) { display: none; }
  .topbar-home {
    border-color: rgba(124, 127, 255, 0.32);
    background: var(--accent-glow);
    color: var(--accent-hover);
  }
  .topbar-site-link {
    display: inline-flex;
  }

  .product-hero { order: 1; }
  .samples-bar { order: 2; }
  .guided-panel { order: 3; }
  .mode-tabs { order: 4; }
  .mode-note { order: 5; }
  .gate-section { order: 6; }
  .ingest-panel { order: 7; }
  .history-section { order: 99; display: none; }
  .workflow-strip { order: 9; }
  .exec-dashboard, .business-system { order: 99; display: none; }
  footer, .app-footer { order: 100; }

  body.onboarded .product-hero {
    padding-top: 6px;
    padding-bottom: 6px;
  }
  body.onboarded .product-hero h2 { color: var(--text-2); font-size: 12px; }
  body.onboarded .product-hero p { display: none; }

  .product-hero {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 10px 20px;
    margin: 0;
    background: var(--bg);
    border-bottom: 1px solid var(--border);
    border-radius: 0;
  }
  .hero-copy {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
    padding: 0;
    border: 0;
    border-radius: 0;
    background: transparent;
    box-shadow: none;
  }
  .hero-eyebrow, .hero-metrics, .hero-shot { display: none; }
  .hero-copy > h2 {
    max-width: 760px;
    margin: 0;
    font-size: 22px;
    font-weight: 750;
    line-height: 1.14;
    letter-spacing: 0;
  }
  .hero-copy > p {
    display: block;
    max-width: 760px;
    color: var(--text-2);
    font-size: 13px;
    line-height: 1.5;
  }
  .hero-actions {
    flex-shrink: 0;
    display: flex;
    align-items: center;
    flex-wrap: nowrap;
    gap: 6px;
    margin-top: 0;
    overflow-x: auto;
    scrollbar-width: none;
  }
  .hero-actions::-webkit-scrollbar { display: none; }
  .hero-actions a, .hero-actions button {
    height: 28px;
    padding: 5px 12px;
    font-size: 11px;
    white-space: nowrap;
  }
  .hero-actions .hero-primary {
    color: white;
    background: var(--accent);
    border-color: transparent;
    font-weight: 700;
  }
  .hero-actions > :not(.hero-primary) { display: none; }

  .workflow-strip {
    display: flex;
    margin: 0;
    padding: 0;
    overflow-x: auto;
    border-bottom: 1px solid var(--border);
    background: var(--bg);
    scrollbar-width: none;
  }
  .workflow-strip::-webkit-scrollbar { display: none; }
  .workflow-step {
    flex: 1 1 0;
    min-width: 0;
    max-height: 52px;
    overflow: hidden;
    padding: 6px 14px;
    border: 0;
    border-right: 1px solid var(--border);
    border-radius: 0;
    background: transparent;
  }
  .workflow-step:last-child { border-right: 0; }
  .workflow-step strong {
    display: block;
    margin-bottom: 1px;
    color: var(--accent);
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 0.3px;
  }
  .workflow-step span {
    display: -webkit-box;
    -webkit-line-clamp: 1;
    -webkit-box-orient: vertical;
    overflow: hidden;
    margin: 0;
    color: var(--text-3);
    font-size: 10px;
    line-height: 1.4;
  }

  .samples-bar {
    flex-wrap: nowrap;
    gap: 4px;
    margin-bottom: 0;
    padding: 6px 20px;
    overflow-x: auto;
    border-bottom: 1px solid var(--border);
    background: var(--bg);
    scrollbar-width: none;
  }
  .samples-bar::before {
    content: "Try an example:";
    flex: 0 0 auto;
    align-self: center;
    color: var(--text-3);
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 0.6px;
    text-transform: uppercase;
  }
  .samples-bar::-webkit-scrollbar { display: none; }
  .samples-bar .sample-btn, .sample-btn {
    flex-shrink: 0;
    height: 22px;
    padding: 3px 9px;
    border-radius: 4px;
    font-size: 10px;
    white-space: nowrap;
  }
  .mode-tabs {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0;
    margin: 0;
    padding: 0 20px;
    border-bottom: 1px solid var(--border);
    background: var(--bg);
  }
  .mode-tab {
    min-height: 30px;
    border-radius: 0;
    border: 0;
    border-right: 1px solid var(--border);
    background: transparent;
    font-size: 11px;
  }
  .mode-tab:last-child { border-right: 0; }
  .mode-tab[aria-selected="true"] { background: var(--accent-glow); }
  .mode-note { margin: 0; padding: 5px 20px; border-bottom: 1px solid var(--border); background: var(--bg); font-size: 11px; }

  .gate-section {
    margin-bottom: 12px;
    padding: 12px 20px 0;
    scroll-margin-top: 44px;
    background: var(--bg);
  }
  .grid {
    grid-template-columns: 1fr;
    gap: 0;
    overflow: hidden;
    margin: 0;
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    background: var(--bg-2);
  }
  .grid > div { border-right: 0; border-bottom: 1px solid var(--border); }
  .grid > div:last-child { border-bottom: 0; }
  .gate-section .panel {
    border: 0;
    border-radius: 0;
    box-shadow: none;
    background: var(--bg-2);
  }
  .workspace-panel[hidden] { display: none; }
  .panel-header {
    min-height: 38px;
    height: 38px;
    padding: 0 14px;
    border-radius: 0;
    background: var(--bg-3);
  }
  .panel-title {
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 0.8px;
    text-transform: uppercase;
  }
  #input {
    min-height: 260px;
    padding: 14px;
    border-radius: 0;
    background: var(--bg-2);
    font-size: 12px;
    line-height: 1.6;
  }
  .json-status {
    min-height: 0;
    padding: 4px 14px;
    border-top: 1px solid var(--border);
    background: var(--bg-3);
    font-size: 10px;
  }
  .gate-flow-title {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 14px;
    border-bottom: 1px solid var(--border);
    background: var(--bg-3);
    color: var(--text-1);
    font-size: 11px;
    font-weight: 900;
    letter-spacing: 0.5px;
    text-transform: uppercase;
  }
  .action-row { gap: 0; padding: 0; border-top: 1px solid var(--border); background: var(--bg-3); }
  .draft-btn#draft-btn {
    height: 40px;
    padding: 10px 12px;
    border: 0;
    border-right: 1px solid var(--border);
    border-radius: 0;
    background: var(--bg-4);
    color: var(--text-1);
    font-size: 12px;
    font-weight: 650;
  }
  .decide-btn {
    height: 40px;
    padding: 10px 12px;
    border: 0;
    border-radius: 0;
    background: var(--accent);
    color: white;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0;
  }
  .decide-btn:hover { background: var(--accent-hover); }
  #batch-btn {
    width: 100%;
    height: 32px;
    padding: 0 14px;
    border: 0;
    border-top: 1px solid var(--border);
    border-radius: 0;
    background: var(--bg-3);
    color: var(--text-3);
    font-size: 11px;
    font-weight: 600;
    text-align: left;
  }
  #batch-btn:hover { color: var(--text-1); background: var(--bg-4); }

  #verdict-area { min-height: 110px; padding: 18px 16px 12px; }
  .verdict-banner { padding: 0 0 12px; border-bottom: 0; }
  .verdict-badge {
    padding: 4px 12px;
    border-radius: 5px;
    font-size: 13px;
    font-weight: 800;
  }
  .fine-tune-block {
    margin: 10px 0 0;
    padding: 10px 14px;
    border-top: 1px solid var(--border);
    background: var(--bg-3);
  }
  .output-section {
    max-height: 240px;
    overflow-y: auto;
    padding: 10px 12px;
    border-top: 1px solid var(--border);
    scrollbar-width: thin;
  }
  .output-section pre, #output {
    margin: 0;
    padding: 12px 14px;
    border: 0;
    background: transparent;
    font-size: 11px;
    line-height: 1.55;
    white-space: pre-wrap;
    word-break: break-word;
  }

  section.guided-panel, section.ingest-panel {
    margin: 0 20px 12px;
    overflow: hidden;
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
  }
  .guided-panel {
    border-color: rgba(124, 127, 255, 0.30);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.20);
  }
  .guided-panel .panel-header {
    background: linear-gradient(180deg, var(--bg-3), var(--bg-2));
  }
  .mode-tabs .mode-tab:first-child::before { content: "Guided Form · "; color: var(--accent); }
  .mode-tabs .mode-tab:nth-child(2)::before { content: "Raw JSON · "; color: var(--text-3); }
  .history-section {
    margin: 0 20px 12px;
    overflow: hidden;
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    background: var(--bg-2);
  }
  .history-section:not(.history-open) .history-tools,
  .history-section:not(.history-open) .history-list { display: none; }
  .history-section:not(.history-open) {
    opacity: 0.88;
  }
  .history-header {
    min-height: 38px;
    margin-bottom: 0;
    padding: 0 14px;
    border-bottom: 1px solid var(--border);
    background: var(--bg-3);
  }
  .history-tools { padding: 8px 14px; margin-bottom: 0; border-bottom: 1px solid var(--border); }
  .history-item {
    padding: 8px 10px;
    border-radius: 0;
    border-width: 0 0 1px;
    font-size: 12px;
  }
  .history-delete { border-radius: 0; border-width: 0 0 1px; }
  .history-ts { font-size: 10px; }
  footer, .app-footer {
    margin: 0;
    padding: 12px 20px;
    border-top: 1px solid var(--border);
    background: var(--bg);
    color: var(--text-3);
    font-size: 10px;
  }

  @media (max-width: 860px) {
    body { max-width: none; }
    .topbar { height: auto; padding: 8px 16px; }
    .product-hero { align-items: flex-start; padding: 10px 16px; }
    .hero-copy { align-items: flex-start; flex-direction: column; gap: 8px; }
    .hero-copy > h2 { max-width: none; -webkit-line-clamp: 2; }
    .workflow-step { min-width: 190px; flex: 0 0 190px; }
    .samples-bar, .mode-tabs, .mode-note { padding-left: 16px; padding-right: 16px; }
    .mode-tabs { grid-template-columns: 1fr; }
    .mode-tab { border-right: 0; border-bottom: 1px solid var(--border); }
    .gate-section { padding: 12px 16px 0; }
    .grid { grid-template-columns: 1fr; }
    .grid > div { border-right: 0; border-bottom: 1px solid var(--border); }
    .grid > div:last-child { border-bottom: 0; }
    section.guided-panel, section.ingest-panel, .history-section { margin-left: 16px; margin-right: 16px; }
  }
  /* ================================================================ */
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
    <a class="copy-btn topbar-home" href="index.html" aria-label="Open CAPAS home page">Home</a>
    <button class="copy-btn topbar-site-link" type="button" aria-label="Jump to the CAPAS gate app workspace" onclick="scrollToGate()">Gate app</button>
    <a class="copy-btn topbar-site-link" href="customer-brief.html" aria-label="Open CAPAS customer brief">Customer brief</a>
    <a class="copy-btn topbar-site-link" href="pilot-packet.html" aria-label="Open CAPAS pilot packet">Pilot packet</a>
    <a class="copy-btn topbar-site-link" href="product.html" aria-label="Open CAPAS product story">Product story</a>
    <button class="copy-btn" id="help-btn" aria-label="Open keyboard shortcut and pipeline help" aria-expanded="false" aria-controls="help-modal" onclick="openHelpModal(this)">Help</button>
    <a class="copy-btn topbar-site-link" id="history-toggle" href="audit.html" aria-label="Open audit log page">Audit log</a>
    <a class="copy-btn topbar-source" href="product.html" aria-label="Open CAPAS product story and business case">Product</a>
    <a class="copy-btn topbar-source" href="https://github.com/fomv9354lve/capas-inteligentes" target="_blank" rel="noopener noreferrer" aria-label="Open CAPAS Claim Gate source repository">Source</a>
    <button class="copy-btn" id="theme-toggle" aria-label="Toggle light and dark theme" onclick="toggleTheme()">Theme</button>
    <span class="topbar-badge" id="schema-version-badge">schema v3</span>
    <span class="topbar-badge" id="shared-payload-badge" hidden>shared payload</span>
    <span class="topbar-badge">__UI_VERSION__</span>
  </div>
</header>

<main class="app-body" id="main">
<section class="product-hero" aria-labelledby="product-hero-title">
  <div class="hero-copy">
    <div class="hero-eyebrow">Scientific claim governance for AI training data</div>
    <h2 id="product-hero-title">CAPAS is the deterministic quality gate before claims enter reports, datasets, or fine-tuning.</h2>
    <p>Instead of asking a reviewer to re-read every paper, CAPAS turns supplied evidence into an auditable ACCEPT, REWRITE, REJECT, or HOLD decision with schema versioning, provenance blockers, and batch economics.</p>
    <div class="hero-actions">
      <button class="sample-btn accept hero-primary" type="button" onclick="loadSample('CAUSAL')">Try the gate with a sample claim →</button>
      <a class="sample-btn accept hero-link" href="https://github.com/fomv9354lve/capas-inteligentes/issues/new?title=CAPAS%20pilot%20conversation" target="_blank" rel="noopener noreferrer">Talk to pilot owner</a>
      <a class="sample-btn hold hero-link" href="customer-brief.html">Open customer brief</a>
      <a class="sample-btn rewrite hero-link" href="pilot-packet.html">Open pilot packet</a>
      <button class="sample-btn hold" type="button" onclick="document.getElementById('roi-calculator-title').scrollIntoView({behavior:'smooth', block:'start'})">See business case</button>
      <a class="sample-btn accept hero-link" href="product.html">Read product story</a>
      <button class="sample-btn rewrite" type="button" onclick="document.getElementById('guided-claim-id').focus()">Start no-code claim</button>
    </div>
    <div class="hero-metrics" aria-label="Illustrative pilot metrics">
      <div class="hero-metric"><strong>10k</strong><span>structured evidence records stress-tested</span></div>
      <div class="hero-metric"><strong>34%</strong><span>rewritten or rejected before reuse</span></div>
      <div class="hero-metric"><strong>417h</strong><span>review capacity modeled</span></div>
    </div>
  </div>
  <div class="hero-shot" aria-label="CAPAS decision screenshot mock">
    <div class="shot-top"><span class="shot-dot"></span><span class="shot-dot"></span><span class="shot-dot"></span></div>
    <div class="shot-body">
      <div class="shot-row"><span class="verdict-badge ACCEPT">ACCEPT</span><span>statistical_confidence: p=0.03 <= alpha=0.05</span><strong>schema v3</strong></div>
      <div class="shot-row"><span class="verdict-badge REWRITE">REWRITE</span><span>direction not independently licensed</span><strong>FT 7/14</strong></div>
      <div class="shot-row"><span class="verdict-badge REJECT">REJECT</span><span>artifact unavailable for reproducibility</span><strong>audit trail</strong></div>
      <div class="shot-row"><span class="verdict-badge HOLD">HOLD</span><span>RO-Crate and reviewer attestation pending CLI verification</span><strong>no LLM</strong></div>
    </div>
  </div>
</section>

<section class="workflow-strip" aria-label="Before and after workflow">
  <div class="workflow-step"><strong>Before CAPAS</strong><span>Researchers paste evidence into spreadsheets, reviewers debate wording, and training data enters pipelines with weak traceability.</span></div>
  <div class="workflow-step"><strong>CAPAS gate</strong><span>Each claim is typed, checked against required evidence, and given a deterministic license boundary.</span></div>
  <div class="workflow-step"><strong>Executive output</strong><span>Batch summaries show rewrite/reject rates, provenance gaps, and fine-tune blockers.</span></div>
  <div class="workflow-step"><strong>Business case</strong><span>Run a 500-record pilot, measure reviewer agreement, and quantify review capacity redirected before enterprise rollout.</span></div>
</section>

<section class="exec-dashboard" aria-label="Executive batch and provenance dashboard">
  <div class="exec-card"><strong id="metric-total">0</strong><span>claims in local audit trail</span></div>
  <div class="exec-card"><strong id="metric-accept">0</strong><span>ACCEPT</span></div>
  <div class="exec-card"><strong id="metric-rewrite">0</strong><span>REWRITE</span></div>
  <div class="exec-card"><strong id="metric-reject">0</strong><span>REJECT</span></div>
  <div class="exec-card"><strong id="metric-ft-ready">0</strong><span>fine-tune ready</span></div>
  <div class="exec-card"><strong id="metric-provenance">0</strong><span>provenance-blocked</span></div>
</section>

<section class="business-system" aria-label="Training data assurance business system">
  <div class="panel" aria-labelledby="workflow-view-title">
    <div class="panel-header">
      <h2 class="panel-title" id="workflow-view-title">Training data assurance workflow</h2>
      <span class="panel-tag">extracted to ready</span>
    </div>
    <div class="workflow-board" aria-label="Operational claim review stages">
      <div class="workflow-stage"><strong>1. Ingest</strong><span>Paste paper text, theorem notes, metadata exports, or local corpus snippets.</span></div>
      <div class="workflow-stage"><strong>2. Confirm</strong><span>Human reviewer accepts candidate spans before CAPAS will decide.</span></div>
      <div class="workflow-stage"><strong>3. Gate</strong><span>Schema v3 and claim-type rules return ACCEPT, REWRITE, REJECT, or HOLD.</span></div>
      <div class="workflow-stage"><strong>4. Provenance</strong><span>Review hash, witness registry, source URLs, RO-Crate, and attestation blockers surface before training.</span></div>
      <div class="workflow-stage"><strong>5. Approve</strong><span>Only fine-tune-ready claims move into governed datasets or downstream reports.</span></div>
    </div>
  </div>
  <div class="panel" aria-labelledby="roi-calculator-title">
    <div class="panel-header">
      <h2 class="panel-title" id="roi-calculator-title">Pilot ROI calculator</h2>
      <span class="panel-tag">review hours</span>
    </div>
    <div class="roi-grid">
      <div class="guided-field">
        <label for="roi-claims">Candidate claims</label>
        <input id="roi-claims" type="number" min="1" value="1000" aria-label="ROI candidate claim count" oninput="updateRoiCalculator()">
      </div>
      <div class="guided-field">
        <label for="roi-manual">Manual min / claim</label>
        <input id="roi-manual" type="number" min="1" value="30" aria-label="Manual review minutes per claim" oninput="updateRoiCalculator()">
      </div>
      <div class="guided-field">
        <label for="roi-triage">CAPAS min / claim</label>
        <input id="roi-triage" type="number" min="1" value="5" aria-label="CAPAS triage minutes per claim" oninput="updateRoiCalculator()">
      </div>
      <div class="guided-field">
        <label for="roi-rate">Expert rate / hour</label>
        <input id="roi-rate" type="number" min="1" value="180" aria-label="Expert reviewer hourly rate" oninput="updateRoiCalculator()">
      </div>
      <div class="roi-result" role="status" aria-live="polite">
        <strong id="roi-hours">417h</strong>
        <span id="roi-value">~$75,060 senior-review capacity avoided in the pilot model.</span>
      </div>
    </div>
  </div>
</section>

<section class="panel guided-panel" aria-labelledby="guided-title">
  <div class="panel-header">
    <h2 class="panel-title" id="guided-title">Guided evidence constructor</h2>
    <button class="copy-btn" type="button" onclick="buildGuidedPayload()">Build JSON from form</button>
  </div>
  <div class="guided-body">
    <div class="starter-guide" role="note" aria-label="CAPAS quick start">
      <strong>Start here if you are new: build a claim in the form, then run the gate.</strong>
      <div class="starter-steps">
        <div class="starter-step"><span>1. Choose</span>Pick the claim type that matches the evidence you have.</div>
        <div class="starter-step"><span>2. Complete</span>Fill the required evidence fields shown in the contract.</div>
        <div class="starter-step"><span>3. Gate</span>Use guided form, then press Run Gate to get ACCEPT, REWRITE, REJECT, or HOLD.</div>
      </div>
    </div>
    <div class="builder-shell">
      <div class="builder-main">
        <section class="flow-section" aria-labelledby="flow-choose-title">
          <h3 class="flow-title" id="flow-choose-title"><span class="flow-step-badge">1</span> Choose the claim</h3>
          <p class="flow-copy">Pick the scientific claim type and write the exact sentence CAPAS is allowed to gate.</p>
          <div class="guided-grid">
            <div class="guided-field">
              <label for="guided-type">Claim type</label>
              <select id="guided-type" onchange="renderGuidedFields()" aria-label="Choose claim type for guided builder"></select>
            </div>
            <div class="type-help" id="guided-type-help" role="status" aria-live="polite">Choose a claim type to see what CAPAS checks.</div>
            <div class="guided-field">
              <label for="guided-claim-id">Record ID</label>
              <input id="guided-claim-id" value="pilot_record_001" aria-label="Guided record ID">
            </div>
            <div class="guided-field full">
              <label for="guided-claim-text">Claim wording</label>
              <textarea id="guided-claim-text" aria-label="Guided claim text">The structured evidence record is ready for deterministic CAPAS gating.</textarea>
            </div>
          </div>
        </section>
        <section class="flow-section" aria-labelledby="flow-complete-title">
          <h3 class="flow-title" id="flow-complete-title"><span class="flow-step-badge">2</span> Complete evidence</h3>
          <p class="flow-copy">Fill only the evidence fields required by the selected type. The contract on the right updates as you work.</p>
          <div class="guided-grid" id="guided-fields" aria-label="Evidence fields for selected claim type"></div>
          <div class="hero-actions">
            <button class="sample-btn accept" type="button" onclick="loadVerticalDemo('AI_GOVERNANCE')">AI governance demo</button>
            <button class="sample-btn rewrite" type="button" onclick="loadVerticalDemo('PHARMA')">Pharma demo</button>
            <button class="sample-btn hold" type="button" onclick="buildGuidedPayload()">Use guided form</button>
          </div>
        </section>
      </div>
      <aside class="builder-rail" aria-labelledby="builder-rail-title">
        <h3 id="builder-rail-title">Evidence contract</h3>
        <div class="builder-contract" id="builder-contract" aria-live="polite">
          <div class="contract-pill"><strong>Type</strong><span>Choose a claim type</span></div>
          <div class="contract-pill"><strong>Fields</strong><span>Required evidence appears here</span></div>
          <div class="contract-pill"><strong>Gate</strong><span>ACCEPT / REWRITE / REJECT / HOLD</span></div>
          <div class="contract-pill"><strong>Training</strong><span>Provenance required for fine-tune readiness</span></div>
        </div>
        <div class="builder-preview" id="builder-preview" role="status" aria-live="polite">Select a type to preview the evidence contract before writing JSON.</div>
        <ul>
          <li>CAPAS will not infer missing evidence.</li>
          <li>Wrong types become schema errors.</li>
          <li>Training readiness requires external provenance verification.</li>
        </ul>
      </aside>
      </div>
    </div>
</section>

<div class="samples-bar">
  <span>Examples with deterministic outcomes:</span>
  <button class="sample-btn accept" title="ACCEPT sample" aria-label="Load ACCEPT sample" onclick="loadSample('ACCEPT')">&#10003; ACCEPT</button>
  <button class="sample-btn rewrite" title="REWRITE sample" aria-label="Load REWRITE sample" onclick="loadSample('REWRITE')">&#8634; REWRITE</button>
  <button class="sample-btn invalid" title="REJECT sample" aria-label="Load REJECT sample" onclick="loadSample('REJECT')">&#10005; REJECT</button>
  <button class="sample-btn hold" title="HOLD sample" aria-label="Load HOLD sample" onclick="loadSample('HOLD')">&#9646; HOLD</button>
  <button class="sample-btn invalid" title="Invalid schema sample that resolves to HOLD" aria-label="Load INVALID schema sample" onclick="loadSample('INVALID')">&#9888; INVALID</button>
  <button class="sample-btn accept" title="Causal mechanism sample" aria-label="Load CAUSAL sample" onclick="loadSample('CAUSAL')">Causal</button>
  <button class="sample-btn accept" title="Systematic review sample" aria-label="Load SYSTEMATIC sample" onclick="loadSample('SYSTEMATIC')">Review</button>
  <button class="sample-btn accept" title="Evidence conflict sample" aria-label="Load CONFLICT sample" onclick="loadSample('CONFLICT')">Conflict</button>
  <button class="sample-btn accept" title="Multimodal evidence sample" aria-label="Load MULTIMODAL sample" onclick="loadSample('MULTIMODAL')">Multimodal</button>
  <button class="sample-btn hold" title="Batch demo with multiple claim types" aria-label="Load batch demo sample" onclick="loadBatchDemo()">Batch demo</button>
</div>

<div class="mode-tabs" role="tablist" aria-label="CAPAS operating modes">
  <button class="mode-tab" id="mode-single" role="tab" aria-selected="true" type="button" onclick="setGateMode('single')">Build one claim</button>
  <button class="mode-tab" id="mode-batch" role="tab" aria-selected="false" type="button" onclick="setGateMode('batch')">Evaluate batch <span class="advanced-badge">advanced</span></button>
  <button class="mode-tab" id="mode-ingestion" role="tab" aria-selected="false" type="button" onclick="setGateMode('ingestion')">Ingestion</button>
</div>
<div class="mode-note" id="mode-note" role="status" aria-live="polite">Guided Form is the default path. Raw JSON remains available below for advanced users.</div>

<section class="gate-section" id="gate" aria-labelledby="gate-title">
<h2 class="sr-only" id="gate-title">CAPAS deterministic claim gate</h2>
<div class="grid">
  <div>
    <div class="panel workspace-panel" id="raw-workspace">
      <div class="gate-flow-title"><span class="flow-step-badge">3</span> Gate the payload</div>
      <div class="panel-header">
        <span class="panel-title">Raw JSON (Advanced)</span>
        <span class="panel-tag" id="type-label" role="status" aria-live="polite" aria-atomic="true"></span>
      </div>
      <textarea id="input" spellcheck="false" aria-label="Claim and evidence JSON input" aria-describedby="json-status" oninput="scheduleInputChange()">__SAMPLE_JSON__</textarea>
      <div class="json-status" id="json-status" role="status" aria-live="polite" aria-atomic="true">Waiting for input...</div>
      <div class="action-row">
        <button class="draft-btn" id="draft-btn" aria-label="Build a schema draft without deciding the claim" title="Build Draft fills a valid schema scaffold. It does not evaluate the claim." onclick="buildDraft()">Build Draft</button>
        <button class="decide-btn" id="decide-btn" aria-label="Run deterministic CAPAS gate" onclick="decide()">Run Gate <span class="decide-hint">⌘↵</span></button>
      </div>
      <div class="action-helper">Build Draft fills missing schema structure. Run Gate evaluates the current payload and writes the decision on the right.</div>
      <button class="draft-btn" id="batch-btn" title="Batch input: JSON array, object with items/claims, or one claim payload auto-wrapped as a one-item batch" aria-label="Evaluate a batch of claim payloads" onclick="decideBatch()">Run Batch</button>
      <div class="json-status"><span class="payload-loaded-badge" id="payload-loaded-badge" role="status" aria-live="polite">Payload loaded</span></div>
    </div>
    <section class="panel workspace-panel ingest-panel" id="ingestion-workspace" aria-labelledby="ingest-title" hidden>
      <div class="gate-flow-title"><span class="flow-step-badge">3</span> Ingest text into candidate claims</div>
      <div class="panel-header">
        <h2 class="panel-title" id="ingest-title">Paper / text ingestion</h2>
        <span class="panel-tag">human-confirmed candidates</span>
      </div>
      <div class="guided-body">
        <div class="guided-grid">
          <div class="guided-field">
            <label for="ingest-source-id">Source ID</label>
            <input id="ingest-source-id" value="paper_demo_001" aria-label="Ingest source ID">
          </div>
          <div class="guided-field">
            <label for="ingest-doi">DOI / external ID</label>
            <input id="ingest-doi" value="10.0000/capas-demo" aria-label="Ingest DOI or external metadata ID">
          </div>
          <div class="guided-field full">
            <label for="ingest-title-field">Paper title</label>
            <input id="ingest-title-field" value="Demo paper for CAPAS candidate claim extraction" aria-label="Ingest paper title">
          </div>
          <div class="guided-field full">
            <label for="ingest-source-text">Paper, abstract, theorem note, or evidence text</label>
            <textarea id="ingest-source-text" aria-label="Paste paper or theory text for candidate claim extraction">We report a statistical effect with p_value: 0.03, alpha: 0.05, and effect_direction_confirmed: true. The artifact_available: true and independent_reproduction_pass: true support reproducibility. For the theoretical scaling claim, anchor_mode: absolute_anchor, local_property_tests_pass: true, universal_anchor_pass: true.</textarea>
          </div>
        </div>
        <div class="ingest-toolbar">
          <input id="ingest-file" type="file" accept=".txt,.md,.json,.jsonl,.pdf" aria-label="Upload local text, markdown, JSON, JSONL, or PDF metadata file" onchange="loadIngestFile(event)">
          <button class="sample-btn accept" type="button" onclick="extractCandidateClaims()">Extract candidate claims</button>
          <button class="sample-btn hold" type="button" onclick="buildIngestionReport()">Build ingestion report</button>
        </div>
        <div class="ingest-report" id="ingest-report-summary" role="status" aria-live="polite">Paste text, upload a local file, then extract candidates. PDF files are declared for provenance; browser PDF text parsing remains a CLI/standalone path.</div>
        <div class="candidate-table" id="candidate-claims-list" role="list" aria-label="candidate claims extracted from paper or text"></div>
      </div>
    </section>
  </div>

  <div>
    <div class="panel">
      <div class="panel-header">
        <span class="panel-title">Decision</span>
        <button class="copy-btn" id="copy-btn" aria-label="Copy decision JSON" onclick="copyOutput()" disabled>Copy JSON</button>
      </div>
      <div id="verdict-area" aria-live="polite" aria-atomic="true"><div class="no-decision"><strong>No decision yet.</strong>Complete the guided form, choose <em>Use guided form</em>, then press <em>Run Gate</em> to see the verdict here.</div></div>
      <div class="output-section">
        <div class="output-inspector" id="output-inspector" aria-label="Decision inspector">
          <div class="empty-state">Decision inspector will summarize the verdict, fine-tune readiness, schema errors, provenance, and raw JSON.</div>
        </div>
        <details class="output-details" id="output-details">
          <summary>Full output JSON</summary>
          <pre id="output" role="log" aria-live="polite" aria-atomic="true" tabindex="0" aria-label="Full CAPAS decision JSON output"></pre>
        </details>
      </div>
    </div>
  </div>
</div>
</section>

<div class="history-section" id="history-section">
  <div class="history-header">
    <h2 class="history-heading">Audit log</h2>
    <div class="history-actions">
      <button class="copy-btn" id="share-btn" aria-label="Copy shareable URL for current input. The payload is embedded in the URL; do not share sensitive claims." title="The payload is embedded in the URL; do not share sensitive claims." onclick="copyShareUrl()">Share URL</button>
      <button class="copy-btn" id="share-app-btn" aria-label="Copy app URL without embedding the current payload" title="Copy the app URL only, without embedding claim or provenance data." onclick="copyAppUrl()">Share App</button>
      <button class="copy-btn" id="sensitive-mode-toggle" aria-label="Toggle sensitive data mode for share and export" title="Sensitive mode copies app-only links and redacts payloads in CSV export." onclick="toggleSensitiveMode()">Sensitive: Off</button>
      <button class="copy-btn" id="export-btn" aria-label="Export decision history as CSV" onclick="exportHistoryCsv()">Export CSV</button>
      <button class="copy-btn" id="clear-history-btn" aria-label="Clear local decision history" onclick="clearHistory()">Clear</button>
      <span class="history-count" id="history-count" aria-live="polite" aria-atomic="true">0/50 saved</span>
    </div>
  </div>
  <div class="history-tools" aria-label="History filters">
    <input class="history-filter" id="history-filter" type="search" placeholder="Search claim ID, type, reason" aria-label="Search decision history by claim ID, type, or reason" oninput="renderHistory()">
    <select class="history-select" id="history-verdict-filter" aria-label="Filter decision history by verdict" onchange="renderHistory()">
      <option value="">All verdicts</option>
      <option value="ACCEPT">ACCEPT</option>
      <option value="REWRITE">REWRITE</option>
      <option value="REJECT">REJECT</option>
      <option value="HOLD">HOLD</option>
    </select>
  </div>
  <div class="history-list" id="history-list" role="list" aria-label="Decision history">
    <div class="empty-state">No decisions yet.</div>
  </div>
</div>
<footer class="app-footer">
  CAPAS structures and gates supplied claim evidence. It does not infer hidden evidence or certify broad scientific truth.
  <div class="footer-links" aria-label="Project links">
    <a href="https://github.com/fomv9354lve/capas-inteligentes" target="_blank" rel="noopener noreferrer">Source repository</a>
    <a href="product.html">Product story</a>
    <a href="customer-brief.html">Customer brief</a>
    <a href="pilot-packet.html">Pilot packet</a>
    <a href="https://github.com/fomv9354lve/capas-inteligentes/issues" target="_blank" rel="noopener noreferrer">Issues</a>
    <a href="https://github.com/fomv9354lve/capas-inteligentes/releases/tag/v0.1.1" target="_blank" rel="noopener noreferrer">Release v0.1.1</a>
    <span>License: proprietary research prototype</span>
  </div>
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
    <h3>Paper/text ingestion</h3>
    <p>The browser ingestion panel accepts pasted paper text, abstracts, theorem notes, local text/Markdown/JSON files, and PDF provenance metadata. It proposes candidate claims with source spans, but a human must click <code>Confirm & build payload</code> before the candidate can be decided. This is an explicit extraction aid, not broad paper understanding or theorem proving.</p>
    <p>For richer ingestion, use the CLI <code>retrieve</code>, <code>extract</code>, <code>align</code>, and <code>pipeline</code> commands. Local corpus adapters can stand in for Semantic Scholar, PubMed, Elicit, or internal metadata exports before CAPAS applies the deterministic final gate.</p>
    <h3>Guided claim builder</h3>
    <p>The no-code builder redraws required evidence fields whenever the claim type changes. It creates a schema v3 payload with the minimum evidence fields for that type plus a <code>training_evidence</code> scaffold, so paper or theorem candidates can be promoted into editable CAPAS payloads without hand-writing JSON.</p>
    <h3>Fine-tune readiness</h3>
    <p><code>fine_tune_ready</code> is a strict positive gate. It becomes <code>true</code> only after an <code>ACCEPT</code> verdict plus source-backed evidence, semantic alignment, witness independence, a hash-verified external review packet, recoverable/hashable source URLs, a resolvable witness registry entry, a valid RO-Crate provenance packet, and a verifiable reviewer attestation. CAPAS gates claims; it does not silently certify training data.</p>
    <p>The static browser UI previews these criteria but cannot perform active provenance I/O. The five provenance gates require <code>capas.py</code> CLI/API verification to resolve registries, hash sources, and validate RO-Crate packets.</p>
    <h3>Schema</h3>
    <p>Current payload schema: <code>capas-claim-payload-v3</code>. Outputs include <code>schema_version</code> for audit trails.</p>
    <p>Supported claim types and minimum evidence fields:</p>
    <ul class="claim-type-list">
      <li><code>claim_transition</code>: <code>upgrade_evidence_present</code></li>
      <li><code>exact_model_solution</code>: <code>abs_error</code>, <code>tolerance</code></li>
      <li><code>financial_metric_claim</code>: <code>reported_value</code>, <code>reference_value</code>, <code>tolerance</code>, <code>metric_period_match</code></li>
      <li><code>physical_accuracy</code>: <code>within_chemical_accuracy</code></li>
      <li><code>reproducibility_check</code>: <code>artifact_available</code>, <code>independent_reproduction_pass</code></li>
      <li><code>statistical_confidence</code>: <code>p_value</code>, <code>alpha</code>, <code>effect_direction_confirmed</code></li>
      <li><code>universal_anchor_claim</code>: <code>anchor_mode</code>, <code>local_property_tests_pass</code>, <code>universal_anchor_pass</code></li>
      <li><code>causal_mechanism_claim</code>: <code>intervention_or_natural_experiment</code>, <code>temporal_order_established</code>, <code>confounders_controlled</code>, <code>mechanism_evidence_present</code></li>
      <li><code>systematic_review_claim</code>: <code>protocol_registered</code>, <code>inclusion_criteria_declared</code>, <code>risk_of_bias_assessed</code>, <code>effect_consistency</code></li>
      <li><code>evidence_conflict_claim</code>: <code>supporting_sources</code>, <code>contradicting_sources</code>, <code>conflict_resolution_method</code>, <code>resolution_pre_registered</code></li>
      <li><code>multimodal_evidence_claim</code>: <code>modality</code>, <code>source_hashes_verified</code>, <code>cross_modal_alignment</code>, <code>extraction_method_declared</code></li>
    </ul>
    <p>Numeric validation ranges: <code>p_value</code> and <code>alpha</code> must be between <code>0</code> and <code>1</code>; <code>abs_error</code> and <code>tolerance</code> must be greater than or equal to <code>0</code>.</p>
    <p><code>training_evidence.source_backed_evidence</code>, <code>external_review</code>, <code>semantic_alignment</code>, and <code>witness_independence</code> must be booleans. Wrong types produce schema errors instead of silent blockers.</p>
    <p><code>universal_anchor_claim</code> currently supports <code>absolute_anchor</code>. Other anchor modes remain <code>HOLD</code> until their witness semantics are defined.</p>
  </div>
</div>

<script>
    const sample = __SAMPLE_COMPACT_JSON__;
    const samples = __SAMPLES_JSON__;
    const capasSchemaVersion = "capas-claim-payload-v3";
    const disallowedAngleRegex = /[<>\u02c2\u02c3\u2039\u203a\u2329-\u232a\u276c-\u276d\u27e8-\u27e9\u29fc-\u29fd\u3008-\u3009\ufe64-\ufe65\uff1c-\uff1e]/u;
    const required = {
      exact_model_solution: ["abs_error", "tolerance"],
      physical_accuracy: ["within_chemical_accuracy"],
      universal_anchor_claim: ["anchor_mode", "local_property_tests_pass", "universal_anchor_pass"],
      claim_transition: ["upgrade_evidence_present"],
      statistical_confidence: ["p_value", "alpha", "effect_direction_confirmed"],
      reproducibility_check: ["artifact_available", "independent_reproduction_pass"],
      financial_metric_claim: ["reported_value", "reference_value", "tolerance", "metric_period_match"],
      causal_mechanism_claim: ["intervention_or_natural_experiment", "temporal_order_established", "confounders_controlled", "mechanism_evidence_present"],
      systematic_review_claim: ["protocol_registered", "inclusion_criteria_declared", "risk_of_bias_assessed", "effect_consistency"],
      evidence_conflict_claim: ["supporting_sources", "contradicting_sources", "conflict_resolution_method", "resolution_pre_registered"],
      multimodal_evidence_claim: ["modality", "source_hashes_verified", "cross_modal_alignment", "extraction_method_declared"]
    };
    const claimTypes = Object.keys(required).sort();
    const claimTypeHelp = {
      causal_mechanism_claim: "Use for claims that assert a mechanism causes an outcome. CAPAS expects intervention or natural experiment evidence, temporal order, confounder control, and mechanism evidence.",
      claim_transition: "Use when a weaker claim is being upgraded to a stronger claim. CAPAS checks whether explicit upgrade evidence is present.",
      evidence_conflict_claim: "Use when sources disagree. CAPAS checks that supporting and contradicting sources are present and that the conflict-resolution method is declared.",
      exact_model_solution: "Use for numerical or formal model outputs where the claim depends on an absolute error being within tolerance.",
      financial_metric_claim: "Use for reported financial metrics. CAPAS compares reported and reference values within tolerance and checks period alignment.",
      multimodal_evidence_claim: "Use when evidence comes from multiple modalities such as text, table, image, or extracted artifact. CAPAS checks hashes, alignment, and extraction method.",
      physical_accuracy: "Use for physical or chemistry accuracy claims where the evidence layer already determined whether the relevant accuracy threshold was met.",
      reproducibility_check: "Use for reproducibility claims. CAPAS checks that artifacts are available and independent reproduction passed.",
      statistical_confidence: "Use for statistical claims. CAPAS checks p-value, alpha, and whether the effect direction matches the claim wording.",
      systematic_review_claim: "Use for systematic-review claims. CAPAS checks protocol, inclusion criteria, risk-of-bias assessment, and effect consistency.",
      universal_anchor_claim: "Use for claims that require an absolute anchor or invariant witness beyond local checks. CAPAS only supports absolute_anchor here."
    };
    const historyLimit = 50;
    const historyStorageKey = "capas_decision_history_v1";
    const themeStorageKey = "capas_theme_v1";
    const sensitiveModeStorageKey = "capas_sensitive_mode_v1";
    let decisionHistory = loadHistory();
    let lastOutputJson = "";
    let inputChangeTimer = null;
    let lastFocusedBeforeHelp = null;
    let sensitiveMode = localStorage.getItem(sensitiveModeStorageKey) === "true";
    let ingestCandidates = [];
    const fineTuneBlockers = [
      "no blind or external inference review is attached",
      "CAPAS gates supplied structured evidence; it does not infer hidden evidence",
      "training readiness requires source-backed evidence, semantic alignment, witness independence, and review"
    ];
    const fineTuneRequiredFields = [
      "source_backed_evidence",
      "external_review",
      "semantic_alignment",
      "witness_independence"
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
      "metric_period_match": "Whether the reported metric and reference are from the same reporting period.",
      "current_claim": "Exact weaker claim text currently licensed before the proposed upgrade.",
      "intervention_or_natural_experiment": "Whether the claim is backed by an intervention, randomized design, or credible natural experiment.",
      "temporal_order_established": "Whether the proposed cause is observed before the effect.",
      "confounders_controlled": "Whether declared confounders are controlled or ruled out.",
      "mechanism_evidence_present": "Whether independent mechanism evidence supports the causal pathway.",
      "protocol_registered": "Whether the systematic review protocol was registered before analysis.",
      "inclusion_criteria_declared": "Whether inclusion/exclusion criteria are explicit and auditable.",
      "risk_of_bias_assessed": "Whether included evidence has a declared risk-of-bias assessment.",
      "effect_consistency": "Whether the reported effect direction is consistent across included evidence.",
      "supporting_sources": "Array of source IDs or URLs that support the claim.",
      "contradicting_sources": "Array of source IDs or URLs that contradict or limit the claim.",
      "conflict_resolution_method": "Declared method for resolving source conflicts.",
      "resolution_pre_registered": "Whether conflict-resolution rules were declared before inspecting outcomes.",
      "modality": "Primary evidence modality, such as image, table, audio, video, or figure.",
      "source_hashes_verified": "Whether source media/data hashes match declared provenance.",
      "cross_modal_alignment": "Whether text, table, image, or other modalities align with each other.",
      "extraction_method_declared": "Whether the method used to extract multimodal evidence is declared."
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
        evidence: { upgrade_evidence_present: false, current_claim: "Replace with the exact weaker claim text currently licensed." }
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
      },
      causal_mechanism_claim: {
        claim: { id: "draft_causal_mechanism", type: "causal_mechanism_claim", text: "The intervention causally changes the measured outcome through the declared mechanism." },
        evidence: { intervention_or_natural_experiment: true, temporal_order_established: true, confounders_controlled: true, mechanism_evidence_present: true }
      },
      systematic_review_claim: {
        claim: { id: "draft_systematic_review", type: "systematic_review_claim", text: "The systematic review supports the reported effect across included studies." },
        evidence: { protocol_registered: true, inclusion_criteria_declared: true, risk_of_bias_assessed: true, effect_consistency: true }
      },
      evidence_conflict_claim: {
        claim: { id: "draft_evidence_conflict", type: "evidence_conflict_claim", text: "The conflicting evidence is resolved by the declared pre-registered method." },
        evidence: { supporting_sources: ["source_a"], contradicting_sources: ["source_b"], conflict_resolution_method: "pre-registered hierarchy", resolution_pre_registered: true }
      },
      multimodal_evidence_claim: {
        claim: { id: "draft_multimodal_evidence", type: "multimodal_evidence_claim", text: "The multimodal evidence supports the extracted claim." },
        evidence: { modality: "table", source_hashes_verified: true, cross_modal_alignment: true, extraction_method_declared: true }
      }
    };

    const verticalDemos = {
      AI_GOVERNANCE: {
        schema_version: capasSchemaVersion,
        claim: { id: "ai_gov_training_claim_001", type: "reproducibility_check", text: "This training candidate is reproducible from the attached artifact before model fine-tuning." },
        evidence: { artifact_available: true, independent_reproduction_pass: true },
        training_evidence: buildTrainingEvidenceDraft({})
      },
      PHARMA: {
        schema_version: capasSchemaVersion,
        claim: { id: "pharma_stat_claim_001", type: "statistical_confidence", text: "The candidate biomarker effect is statistically significant at the declared alpha." },
        evidence: { p_value: 0.03, alpha: 0.05, effect_direction_confirmed: true },
        training_evidence: buildTrainingEvidenceDraft({})
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
      if (payload.schema_version !== capasSchemaVersion) {
        errors.push(`schema_version must be ${capasSchemaVersion}`);
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
      for (const field of ["intervention_or_natural_experiment", "temporal_order_established", "confounders_controlled", "mechanism_evidence_present", "protocol_registered", "inclusion_criteria_declared", "risk_of_bias_assessed", "effect_consistency", "resolution_pre_registered", "source_hashes_verified", "cross_modal_alignment", "extraction_method_declared"]) {
        if (Object.prototype.hasOwnProperty.call(safeEvidence, field) && typeof safeEvidence[field] !== "boolean") {
          errors.push(`evidence.${field} must be a boolean`);
        }
      }
      for (const field of ["anchor_mode", "physical_evidence_level", "verification_independence", "conflict_resolution_method", "modality"]) {
        if (Object.prototype.hasOwnProperty.call(safeEvidence, field) && typeof safeEvidence[field] !== "string") {
          errors.push(`evidence.${field} must be a string`);
        }
        if (typeof safeEvidence[field] === "string" && containsAngleLikeCharacter(safeEvidence[field])) {
          errors.push(`evidence.${field} must not contain angle brackets or Unicode angle-bracket homoglyphs`);
        }
      }
      for (const field of ["supporting_sources", "contradicting_sources"]) {
        if (Object.prototype.hasOwnProperty.call(safeEvidence, field)) {
          const value = safeEvidence[field];
          if (!Array.isArray(value) || value.some((item) => typeof item !== "string")) {
            errors.push(`evidence.${field} must be an array of strings`);
          } else if (value.some((item) => containsAngleLikeCharacter(item))) {
            errors.push(`evidence.${field} must not contain angle brackets or Unicode angle-bracket homoglyphs`);
          }
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
      if (Object.prototype.hasOwnProperty.call(payload, "training_evidence")) {
        if (payload.training_evidence === null || typeof payload.training_evidence !== "object" || Array.isArray(payload.training_evidence)) {
          errors.push("training_evidence must be an object");
        } else {
          for (const field of fineTuneRequiredFields) {
            if (Object.prototype.hasOwnProperty.call(payload.training_evidence, field) && typeof payload.training_evidence[field] !== "boolean") {
              errors.push(`training_evidence.${field} must be a boolean`);
            }
          }
          if (Object.prototype.hasOwnProperty.call(payload.training_evidence, "provenance")) {
            const provenance = payload.training_evidence.provenance;
            if (provenance === null || typeof provenance !== "object" || Array.isArray(provenance)) {
              errors.push("training_evidence.provenance must be an object");
            }
          }
        }
      }
      return errors;
    }

    function evaluateFineTuneReadiness(payload, result) {
      const trainingEvidence = payload && typeof payload.training_evidence === "object" && !Array.isArray(payload.training_evidence)
        ? payload.training_evidence
        : {};
      const provenance = trainingEvidence.provenance && typeof trainingEvidence.provenance === "object" && !Array.isArray(trainingEvidence.provenance)
        ? trainingEvidence.provenance
        : {};
      const sourceCandidates = Array.isArray(provenance.sources)
        ? provenance.sources
        : Array.isArray(provenance.source_urls)
          ? provenance.source_urls
          : [];
      const sourceHashes = provenance.source_hashes && typeof provenance.source_hashes === "object" && !Array.isArray(provenance.source_hashes)
        ? provenance.source_hashes
        : {};
      const reviewer = provenance.reviewer && typeof provenance.reviewer === "object" && !Array.isArray(provenance.reviewer)
        ? provenance.reviewer
        : {};
      const criteria = {
        verdict_accept: result.verdict === "ACCEPT",
        schema_clean: !(result.schema_errors && result.schema_errors.length) && !(result.missing_fields && result.missing_fields.length),
        source_backed_evidence: trainingEvidence.source_backed_evidence === true,
        external_review: trainingEvidence.external_review === true,
        semantic_alignment: trainingEvidence.semantic_alignment === true,
        witness_independence: trainingEvidence.witness_independence === true,
        provenance_sources: sourceCandidates.some((source) => typeof source === "string" && source.trim() !== ""),
        review_hash_verified: false,
        source_urls_recoverable_hashable: false,
        witness_registry_resolved: false,
        ro_crate_validated: false,
        reviewer_attestation_verified: false,
        review_id_present: typeof provenance.review_id === "string" && provenance.review_id.trim() !== "",
        witness_id_present: typeof provenance.witness_id === "string" && provenance.witness_id.trim() !== ""
      };
      const labels = {
        verdict_accept: "claim verdict is not ACCEPT",
        schema_clean: "schema or required-field blockers remain",
        source_backed_evidence: "source-backed evidence is not attached",
        external_review: "external review is not attached",
        semantic_alignment: "claim.text semantic alignment is not externally certified",
        witness_independence: "witness independence is not externally certified",
        provenance_sources: "provenance.sources or provenance.source_urls is empty",
        review_hash_verified: "external review hash is missing or does not match review_packet",
        source_urls_recoverable_hashable: "source URLs are not recoverable with matching hashes",
        witness_registry_resolved: "witness_id is not resolvable in the witness registry",
        ro_crate_validated: "RO-Crate provenance packet is missing, invalid, or hash-mismatched",
        reviewer_attestation_verified: "reviewer identity or attestation is not verifiable",
        review_id_present: "provenance.review_id is missing",
        witness_id_present: "provenance.witness_id is missing"
      };
      const blockers = Object.entries(criteria)
        .filter(([, passed]) => !passed)
        .map(([key]) => labels[key]);
      return {
        fine_tune_ready: blockers.length === 0,
        fine_tune_blockers: blockers,
        fine_tune_criteria: criteria,
        fine_tune_verification_surface: "static_browser_preview",
        fine_tune_note: "Active provenance gates require capas.py CLI/API verification; the static browser UI cannot hash sources or resolve registries."
      };
    }

    function rule(payload) {
      const schemaErrors = validatePayload(payload);
      const claim = payload && typeof payload.claim === "object" && !Array.isArray(payload.claim) ? payload.claim : {};
      const evidence = payload && typeof payload.evidence === "object" && !Array.isArray(payload.evidence) ? payload.evidence : {};
      if (schemaErrors.length) {
        const invalidResult = {
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
        return { ...invalidResult, ...evaluateFineTuneReadiness(payload, invalidResult) };
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
      } else if (claim.type === "causal_mechanism_claim") {
        if (evidence.intervention_or_natural_experiment === true && evidence.temporal_order_established === true && evidence.confounders_controlled === true && evidence.mechanism_evidence_present === true) {
          result.verdict = "ACCEPT";
          result.reason = "intervention/natural experiment, temporal order, confounder controls, and mechanism evidence all pass";
        } else if (evidence.intervention_or_natural_experiment === true && evidence.temporal_order_established === true) {
          result.verdict = "REWRITE";
          result.reason = "causal design and temporal order are present, but full causal mechanism licensing is incomplete";
          result.rewrite = "association with causal design support; full causal mechanism wording is not licensed";
          result.licensed_claim = result.rewrite;
        } else {
          result.verdict = "REJECT";
          result.reason = "causal claim lacks intervention/natural experiment evidence or temporal order";
        }
      } else if (claim.type === "systematic_review_claim") {
        if (evidence.protocol_registered === true && evidence.inclusion_criteria_declared === true && evidence.risk_of_bias_assessed === true && evidence.effect_consistency === true) {
          result.verdict = "ACCEPT";
          result.reason = "protocol, inclusion criteria, risk-of-bias assessment, and effect consistency all pass";
        } else if (evidence.protocol_registered === true && evidence.inclusion_criteria_declared === true) {
          result.verdict = "REWRITE";
          result.reason = "review protocol and inclusion criteria are present, but bias/consistency evidence is incomplete";
          result.rewrite = "systematic review process is documented; strength or consistency of effect is not fully licensed";
          result.licensed_claim = result.rewrite;
        } else {
          result.verdict = "REJECT";
          result.reason = "systematic review claim lacks registered protocol or declared inclusion criteria";
        }
      } else if (claim.type === "evidence_conflict_claim") {
        const supporting = evidence.supporting_sources || [];
        const contradicting = evidence.contradicting_sources || [];
        const method = String(evidence.conflict_resolution_method || "").trim();
        if (supporting.length && contradicting.length && method && evidence.resolution_pre_registered === true) {
          result.verdict = "ACCEPT";
          result.reason = "supporting and contradicting sources are disclosed with a pre-registered conflict-resolution method";
        } else if (supporting.length && contradicting.length && method) {
          result.verdict = "REWRITE";
          result.reason = "conflicting evidence is disclosed, but conflict resolution was not pre-registered";
          result.rewrite = "evidence conflict is disclosed; resolved conclusion is not fully licensed";
          result.licensed_claim = result.rewrite;
        } else {
          result.verdict = "REJECT";
          result.reason = "evidence conflict claim lacks supporting/contradicting source sets or a resolution method";
        }
      } else if (claim.type === "multimodal_evidence_claim") {
        const modality = String(evidence.modality || "").trim();
        if (modality && evidence.source_hashes_verified === true && evidence.cross_modal_alignment === true && evidence.extraction_method_declared === true) {
          result.verdict = "ACCEPT";
          result.reason = "modality, source hashes, cross-modal alignment, and extraction method are declared";
        } else if (modality && evidence.source_hashes_verified === true) {
          result.verdict = "REWRITE";
          result.reason = "multimodal source identity is verified, but alignment or extraction method is not fully licensed";
          result.rewrite = "multimodal evidence is identified; cross-modal claim is not fully licensed";
          result.licensed_claim = result.rewrite;
        } else {
          result.verdict = "REJECT";
          result.reason = "multimodal claim lacks verified source hashes or declared modality";
        }
      }
      return { ...result, ...evaluateFineTuneReadiness(payload, result) };
    }

    function renderVerdict(result) {
      const verdict = result.verdict;
      let html = `<div class="verdict-banner"><span class="verdict-badge ${verdict}">${verdict}</span><span class="verdict-reason">${escHtml(result.reason)}</span></div>`;
      html += renderFineTuneStatus(result);
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
        fine_tune_ready: results.length > 0 && results.every((entry) => entry.result.fine_tune_ready === true),
        fine_tune_blockers: results.length > 0 && results.every((entry) => entry.result.fine_tune_ready === true)
          ? []
          : ["one or more batch items are not fine_tune_ready"],
        non_claim: "Batch mode applies the same deterministic per-claim gates; it does not create new scientific evidence."
      };
    }

    function renderBatch(result) {
      const summary = Object.entries(result.summary).map(([verdict, count]) => `<span class="verdict-badge ${escHtml(verdict)}">${escHtml(verdict)} ${count}</span>`).join("");
      const rows = result.results.map((entry) => {
        const claim = entry.result.input_claim || {};
        const verdict = entry.result.verdict || "UNKNOWN";
        const id = claim.id || `item_${entry.index + 1}`;
        const ft = fineTuneSummary(entry.result);
        const ftLabel = entry.result.fine_tune_ready ? "FT READY" : `FT ${ft.passed}/${ft.total}`;
        return (
          `<details class="batch-row" role="listitem">` +
          `<summary aria-label="Batch item ${entry.index + 1}: ${escHtml(verdict)} for ${escHtml(id)}; fine-tune ${escHtml(ftLabel)}">` +
          `<span class="verdict-badge ${escHtml(verdict)}">${escHtml(verdict)}</span><span class="batch-row-id">#${entry.index + 1} ${escHtml(id)}</span><span class="batch-row-reason">${escHtml(entry.result.reason || "")}</span><span class="batch-row-ft">${escHtml(ftLabel)}</span></summary>` +
          `<pre>${escHtml(JSON.stringify(entry.result, null, 2))}</pre>` +
          `</details>`
        );
      }).join("");
      document.getElementById("verdict-area").innerHTML =
        `<div class="verdict-banner"><span class="verdict-badge HOLD">BATCH</span><span class="verdict-reason">${result.item_count} items evaluated with deterministic CAPAS gates.</span></div>` +
        `<div class="assist-block"><div class="alert-title">Batch summary</div><div style="display:flex;gap:8px;flex-wrap:wrap">${summary}</div>` +
        `<div class="batch-progress" aria-hidden="true"><div class="batch-progress-fill" style="--batch-progress:100%"></div></div>` +
        `<div class="batch-progress-label">${result.item_count}/${result.item_count} claims processed · deterministic gate complete</div>` +
        `<div class="batch-table" role="list" aria-label="Batch per-item decisions">${rows}</div></div>` +
        renderBatchFineTuneStatus(result);
      renderExecutiveDashboard(result.results.map((entry) => entry.result));
    }

    function inspectorList(items, emptyText) {
      const values = (items || []).filter(Boolean);
      if (!values.length) return `<div class="inspector-empty">${escHtml(emptyText)}</div>`;
      return `<ul>${values.map((item) => `<li>${escHtml(item)}</li>`).join("")}</ul>`;
    }

    function inspectorDl(rows) {
      return `<dl>${rows.map(([key, value]) => `<dt>${escHtml(key)}</dt><dd>${escHtml(value ?? "-")}</dd>`).join("")}</dl>`;
    }

    function renderInspectorCard(title, body, open = false) {
      return `<details class="inspector-card"${open ? " open" : ""}><summary>${escHtml(title)}</summary><div class="inspector-body">${body}</div></details>`;
    }

    function renderOutputInspector(value) {
      const inspector = document.getElementById("output-inspector");
      if (!inspector) return;
      if (!value || typeof value !== "object") {
        inspector.innerHTML = `<div class="empty-state">Decision inspector will summarize the verdict, fine-tune readiness, schema errors, provenance, and raw JSON.</div>`;
        return;
      }
      const firstResult = Array.isArray(value.results) ? value.results[0]?.result : value;
      const claim = firstResult?.input_claim || {};
      const criteria = firstResult?.fine_tune_criteria || {};
      const criteriaPassed = Object.values(criteria).filter(Boolean).length;
      const criteriaTotal = Object.keys(criteria).length;
      const provenance = firstResult?.training_evidence?.provenance || {};
      const schemaErrors = firstResult?.schema_errors || [];
      const missingFields = firstResult?.missing_fields || [];
      const cards = [];
      cards.push(renderInspectorCard("Decision", inspectorDl([
        ["mode", value.batch_mode ? `batch · ${value.item_count} items` : "single claim"],
        ["verdict", firstResult?.verdict || value.report_type || "-"],
        ["claim id", claim.id || "-"],
        ["claim type", claim.type || "-"],
        ["reason", firstResult?.reason || value.non_claim || "-"]
      ]), true));
      cards.push(renderInspectorCard("Fine-tune readiness", inspectorDl([
        ["ready", value.batch_mode ? String(value.fine_tune_ready === true) : String(firstResult?.fine_tune_ready === true)],
        ["criteria", criteriaTotal ? `${criteriaPassed}/${criteriaTotal}` : value.batch_mode ? "batch AND-gate; expand per item for criteria" : "-"],
        ["blockers", (value.fine_tune_blockers || firstResult?.fine_tune_blockers || []).length]
      ]) + inspectorList(value.fine_tune_blockers || firstResult?.fine_tune_blockers || [], "No active fine-tune blockers.")));
      cards.push(renderInspectorCard("Schema errors", inspectorList(schemaErrors.concat(missingFields.map((field) => `missing field: ${field}`)), "No schema errors or missing fields.")));
      cards.push(renderInspectorCard("Provenance", inspectorDl([
        ["review id", provenance.review_id || "-"],
        ["review hash", provenance.review_sha256 || "-"],
        ["witness id", provenance.witness_id || "-"],
        ["RO-Crate", provenance.ro_crate_path || "-"],
        ["source URLs", Array.isArray(provenance.source_urls) ? provenance.source_urls.length : 0]
      ])));
      cards.push(renderInspectorCard("Raw JSON", `<div class="inspector-empty">Full structured output remains available below for copy/export.</div>`));
      inspector.innerHTML = cards.join("");
    }

    function hasNullEvidence(payload) {
      const evidence = payload?.evidence;
      if (!evidence || typeof evidence !== "object" || Array.isArray(evidence)) return false;
      return Object.values(evidence).some((value) => value === null);
    }

    function setOutputJson(value) {
      renderOutputInspector(value);
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
      renderOutputInspector(null);
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
      if (error.includes("training_evidence")) return "Use typed training_evidence fields: readiness flags must be booleans and provenance must be an object.";
      return "Fix this schema issue before the strict gate can evaluate the claim.";
    }

    function fineTuneSummary(result) {
      const criteria = result.fine_tune_criteria || {};
      const total = Object.keys(criteria).length;
      const passed = Object.values(criteria).filter(Boolean).length;
      return { total, passed };
    }

    function renderFineTuneStatus(result) {
      if (!result || typeof result.fine_tune_ready !== "boolean") return "";
      const summary = fineTuneSummary(result);
      const blockers = Array.isArray(result.fine_tune_blockers) ? result.fine_tune_blockers : [];
      const statusClass = result.fine_tune_ready ? "ready" : "blocked";
      const statusText = result.fine_tune_ready ? "READY" : "NOT READY";
      const body = result.fine_tune_ready
        ? `<div class="fine-tune-summary">All ${summary.total} fine-tune readiness criteria passed.</div>`
        : `<div class="fine-tune-summary">${summary.passed}/${summary.total} fine-tune readiness criteria passed. ${escHtml(result.fine_tune_note || "Review blockers before using this output for training.")}</div>` +
          (blockers.length ? `<ul>${blockers.slice(0, 5).map((blocker) => `<li>${escHtml(blocker)}</li>`).join("")}${blockers.length > 5 ? `<li>${blockers.length - 5} more blockers in Full output JSON.</li>` : ""}</ul>` : "");
      return (
        `<div class="fine-tune-block" role="status" aria-live="polite" aria-atomic="true" tabindex="0" aria-label="Fine-tune readiness status">` +
        `<div class="fine-tune-head"><div class="fine-tune-title">Fine-tune readiness</div><div class="fine-tune-status ${statusClass}">${statusText}</div></div>` +
        body +
        `</div>`
      );
    }

    function renderBatchFineTuneStatus(result) {
      const itemResults = Array.isArray(result?.results) ? result.results.map((entry) => entry.result) : [];
      const readyCount = itemResults.filter((entry) => entry?.fine_tune_ready === true).length;
      const total = itemResults.length;
      const provenanceBlocked = itemResults.filter(isProvenanceBlocked).length;
      const blockers = Array.isArray(result.fine_tune_blockers) ? result.fine_tune_blockers : [];
      const statusClass = result.fine_tune_ready ? "ready" : "blocked";
      const statusText = result.fine_tune_ready ? "READY" : "NOT READY";
      const body = result.fine_tune_ready
        ? `<div class="fine-tune-summary">All ${total} batch items are fine-tune ready.</div>`
        : `<div class="fine-tune-summary">${readyCount}/${total} batch items are fine-tune ready. ${provenanceBlocked} items have active provenance blockers.</div>` +
          (blockers.length ? `<ul>${blockers.map((blocker) => `<li>${escHtml(blocker)}</li>`).join("")}</ul>` : "");
      return (
        `<div class="fine-tune-block" role="status" aria-live="polite" aria-atomic="true" tabindex="0" aria-label="Batch fine-tune readiness status">` +
        `<div class="fine-tune-head"><div class="fine-tune-title">Batch fine-tune readiness</div><div class="fine-tune-status ${statusClass}">${statusText}</div></div>` +
        body +
        `</div>`
      );
    }

    function inferClaimType(raw, parsed) {
      const text = `${raw} ${JSON.stringify(parsed || {})}`.toLowerCase();
      if (text.includes("universal") || text.includes("anchor") || text.includes("local_property")) return "universal_anchor_claim";
      if (text.includes("upgrade") || text.includes("stronger claim") || text.includes("current_claim")) return "claim_transition";
      if (text.includes("chemical accuracy") || text.includes("within_chemical_accuracy") || text.includes("experiment")) return "physical_accuracy";
      if (text.includes("causal") || text.includes("confounder") || text.includes("mechanism")) return "causal_mechanism_claim";
      if (text.includes("systematic review") || text.includes("risk_of_bias") || text.includes("inclusion criteria")) return "systematic_review_claim";
      if (text.includes("contradict") || text.includes("conflict_resolution") || text.includes("supporting_sources")) return "evidence_conflict_claim";
      if (text.includes("multimodal") || text.includes("cross_modal") || text.includes("modality")) return "multimodal_evidence_claim";
      if (text.includes("abs_error") || text.includes("tolerance") || text.includes("error") || text.includes("ground state")) return "exact_model_solution";
      return "exact_model_solution";
    }

    function extractNumbers(raw) {
      const matches = raw.match(/-?\d+(?:\.\d+)?(?:e[+-]?\d+)?/gi) || [];
      return matches.map(Number).filter(Number.isFinite);
    }

    function buildTrainingEvidenceDraft(existing) {
      const source = existing && typeof existing === "object" && !Array.isArray(existing) ? existing : {};
      const provenance = source.provenance && typeof source.provenance === "object" && !Array.isArray(source.provenance) ? source.provenance : {};
      const reviewer = provenance.reviewer && typeof provenance.reviewer === "object" && !Array.isArray(provenance.reviewer) ? provenance.reviewer : {};
      return {
        source_backed_evidence: typeof source.source_backed_evidence === "boolean" ? source.source_backed_evidence : false,
        external_review: typeof source.external_review === "boolean" ? source.external_review : false,
        semantic_alignment: typeof source.semantic_alignment === "boolean" ? source.semantic_alignment : false,
        witness_independence: typeof source.witness_independence === "boolean" ? source.witness_independence : false,
        provenance: {
          source_urls: Array.isArray(provenance.source_urls) ? provenance.source_urls : [],
          source_hashes: provenance.source_hashes && typeof provenance.source_hashes === "object" && !Array.isArray(provenance.source_hashes) ? provenance.source_hashes : {},
          review_id: typeof provenance.review_id === "string" ? provenance.review_id : "",
          review_sha256: typeof provenance.review_sha256 === "string" ? provenance.review_sha256 : "",
          review_packet: provenance.review_packet && typeof provenance.review_packet === "object" && !Array.isArray(provenance.review_packet) ? provenance.review_packet : {},
          witness_id: typeof provenance.witness_id === "string" ? provenance.witness_id : "",
          witness_registry_path: typeof provenance.witness_registry_path === "string" ? provenance.witness_registry_path : "docs/witness_registry.json",
          witness_registry_sha256: typeof provenance.witness_registry_sha256 === "string" ? provenance.witness_registry_sha256 : "",
          ro_crate_path: typeof provenance.ro_crate_path === "string" ? provenance.ro_crate_path : "",
          ro_crate_sha256: typeof provenance.ro_crate_sha256 === "string" ? provenance.ro_crate_sha256 : "",
          reviewer: {
            reviewer_id: typeof reviewer.reviewer_id === "string" ? reviewer.reviewer_id : "",
            attestation: typeof reviewer.attestation === "string" ? reviewer.attestation : "",
            attestation_sha256: typeof reviewer.attestation_sha256 === "string" ? reviewer.attestation_sha256 : ""
          },
          reviewer_registry_path: typeof provenance.reviewer_registry_path === "string" ? provenance.reviewer_registry_path : "docs/reviewer_registry.json",
          reviewer_registry_sha256: typeof provenance.reviewer_registry_sha256 === "string" ? provenance.reviewer_registry_sha256 : ""
        }
      };
    }

    let lastGuidedType = "";

    function guidedFieldComplete(element) {
      if (!element) return false;
      if (element.dataset.kind === "boolean") return element.value === "true" || element.value === "false";
      if (element.dataset.kind === "number") return element.value !== "" && Number.isFinite(Number(element.value));
      return String(element.value || "").trim().length > 0;
    }

    function updateGuidedProgress() {
      const typeSelect = document.getElementById("guided-type");
      const contract = document.getElementById("builder-contract");
      const help = document.getElementById("guided-type-help");
      if (!typeSelect || !contract) return;
      const type = typeSelect.value || "statistical_confidence";
      const fieldsForType = required[type] || [];
      const complete = fieldsForType.filter((field) => guidedFieldComplete(document.getElementById(`guided-field-${field}`))).length;
      const progress = contract.querySelector("[data-contract-progress]");
      if (progress) {
        progress.textContent = `${complete}/${fieldsForType.length} required evidence fields complete`;
      }
      if (help) {
        help.textContent = claimTypeHelp[type] || "CAPAS checks the required evidence fields for the selected claim type.";
      }
    }

    function renderGuidedFields() {
      const typeSelect = document.getElementById("guided-type");
      const fields = document.getElementById("guided-fields");
      if (!typeSelect || !fields) return;
      if (!typeSelect.options.length) {
        typeSelect.innerHTML = claimTypes.map((type) => `<option value="${escHtml(type)}">${escHtml(type)}</option>`).join("");
        typeSelect.value = "statistical_confidence";
      }
      const type = typeSelect.value;
      const example = minimalExamples[type] || minimalExamples.exact_model_solution;
      const idInput = document.getElementById("guided-claim-id");
      const textInput = document.getElementById("guided-claim-text");
      const typeChanged = lastGuidedType && lastGuidedType !== type;
      if (!idInput.value || typeChanged) {
        idInput.value = example.claim.id;
      }
      if (!textInput.value.trim() || typeChanged) {
        textInput.value = example.claim.text;
      }
      lastGuidedType = type;
      fields.dataset.claimType = type;
      const contract = document.getElementById("builder-contract");
      const preview = document.getElementById("builder-preview");
      const help = document.getElementById("guided-type-help");
      if (help) {
        help.textContent = claimTypeHelp[type] || "CAPAS checks the required evidence fields for the selected claim type.";
      }
      if (contract) {
        contract.innerHTML =
          `<div class="contract-pill"><strong>Type</strong><span>${escHtml(type)}</span></div>` +
          `<div class="contract-pill"><strong>Fields</strong><span>${required[type].length} required</span></div>` +
          `<div class="contract-pill"><strong>Gate</strong><span>${escHtml((example.claim.text || "").slice(0, 54))}${example.claim.text.length > 54 ? "..." : ""}</span></div>` +
          `<div class="contract-pill"><strong>Training</strong><span>14 readiness criteria after ACCEPT</span></div>` +
          `<div class="contract-progress" data-contract-progress>${required[type].length}/${required[type].length} required evidence fields complete</div>`;
      }
      if (preview) {
        preview.textContent = `${type}: ${required[type].join(", ")}. CAPAS emits schema v3 JSON and will HOLD if required evidence is missing or typed incorrectly.`;
      }
      fields.innerHTML = required[type].map((field) => {
        const value = example.evidence[field];
        const inputType = typeof value === "number" ? "number" : "text";
        const serialized = Array.isArray(value) ? value.join(", ") : String(value ?? "");
        const fieldLabel = `${field} evidence field for ${type}`;
        const control = typeof value === "boolean"
          ? `<select id="guided-field-${escHtml(field)}" data-field="${escHtml(field)}" data-kind="boolean" aria-label="${escHtml(fieldLabel)}" onchange="updateGuidedProgress()"><option value="true"${value ? " selected" : ""}>true</option><option value="false"${!value ? " selected" : ""}>false</option></select>`
          : `<input id="guided-field-${escHtml(field)}" data-field="${escHtml(field)}" data-kind="${Array.isArray(value) ? "array" : inputType}" type="${inputType}" value="${escHtml(serialized)}" aria-label="${escHtml(fieldLabel)}" oninput="updateGuidedProgress()">`;
        return `<div class="guided-field"><label for="guided-field-${escHtml(field)}">${escHtml(field)}</label>${control}<span class="assist-muted">${escHtml(fieldHelp[field] || "Required evidence field.")}</span></div>`;
      }).join("");
      updateGuidedProgress();
    }

    function coerceGuidedValue(element) {
      const kind = element.dataset.kind;
      if (kind === "boolean") return element.value === "true";
      if (kind === "number") return Number(element.value);
      if (kind === "array") return element.value.split(",").map((item) => item.trim()).filter(Boolean);
      return element.value;
    }

    function scrollToGate() {
      const gate = document.getElementById("gate");
      if (gate) gate.scrollIntoView({ behavior: "smooth", block: "start" });
    }

    function scrollToGuidedBuilder() {
      const guided = document.querySelector(".guided-panel");
      if (guided) guided.scrollIntoView({ behavior: "smooth", block: "start" });
    }

    function markOnboarded() {
      document.body.classList.add("onboarded");
      try { localStorage.setItem("capas_onboarded_v1", "1"); } catch (_) {}
    }

    function initOnboardingState() {
      try {
        if (localStorage.getItem("capas_onboarded_v1") === "1") document.body.classList.add("onboarded");
      } catch (_) {}
    }

    function toggleHistoryPanel(forceOpen) {
      window.location.href = "audit.html";
    }

    function setGateMode(mode) {
      const labels = {
        single: "Single claim mode: start with the Guided Form, then run the deterministic CAPAS gate.",
        batch: "Batch claims mode: use Raw JSON (Advanced) with an array or object containing items/claims.",
        ingestion: "Ingestion mode: extract candidate claims from paper text, confirm spans, then gate the payload."
      };
      for (const key of Object.keys(labels)) {
        const tab = document.getElementById(`mode-${key}`);
        if (tab) tab.setAttribute("aria-selected", key === mode ? "true" : "false");
      }
      const note = document.getElementById("mode-note");
      if (note) note.textContent = labels[mode] || labels.single;
      const raw = document.getElementById("raw-workspace");
      const ingestion = document.getElementById("ingestion-workspace");
      if (raw) raw.hidden = mode === "ingestion";
      if (ingestion) ingestion.hidden = mode !== "ingestion";
      document.body.dataset.gateMode = mode;
    }

    function markPayloadLoaded({ scroll = true } = {}) {
      const input = document.getElementById("input");
      const badge = document.getElementById("payload-loaded-badge");
      if (badge) {
        badge.classList.add("show");
        setTimeout(() => badge.classList.remove("show"), 2600);
      }
      if (input) {
        input.classList.remove("payload-flash");
        void input.offsetWidth;
        input.classList.add("payload-flash");
      }
      markOnboarded();
      if (scroll) scrollToGate();
    }

    function buildGuidedPayload() {
      const type = document.getElementById("guided-type").value || "statistical_confidence";
      const fields = document.getElementById("guided-fields");
      if (fields && fields.dataset.claimType !== type) {
        renderGuidedFields();
      }
      const evidence = {};
      document.querySelectorAll("#guided-fields [data-field]").forEach((element) => {
        evidence[element.dataset.field] = coerceGuidedValue(element);
      });
      const payload = {
        schema_version: capasSchemaVersion,
        claim: {
          id: document.getElementById("guided-claim-id").value.trim() || `guided_${type}`,
          type,
          text: document.getElementById("guided-claim-text").value.trim() || minimalExamples[type].claim.text
        },
        evidence,
        training_evidence: buildTrainingEvidenceDraft({})
      };
      document.getElementById("input").value = JSON.stringify(payload, null, 2);
      onInputChange();
      markPayloadLoaded();
      document.getElementById("verdict-area").innerHTML =
        `<div class="assist-block"><div class="alert-title">Guided payload built</div>` +
        `<div>The no-code form generated a <code>${escHtml(type)}</code> payload. Run Decide or Batch to apply the deterministic gate.</div></div>`;
      setOutputEmpty();
      setCopyEnabled(false);
    }

    function loadVerticalDemo(name) {
      const payload = verticalDemos[name] || verticalDemos.AI_GOVERNANCE;
      document.getElementById("input").value = JSON.stringify(payload, null, 2);
      markPayloadLoaded({ scroll: false });
      const typeSelect = document.getElementById("guided-type");
      if (typeSelect) typeSelect.value = payload.claim.type;
      document.getElementById("guided-claim-id").value = payload.claim.id;
      document.getElementById("guided-claim-text").value = payload.claim.text;
      renderGuidedFields();
      for (const [field, value] of Object.entries(payload.evidence)) {
        const element = document.getElementById(`guided-field-${field}`);
        if (element) element.value = Array.isArray(value) ? value.join(", ") : String(value);
      }
      onInputChange();
      decide();
    }

    function ingestMetadata() {
      return {
        source_id: document.getElementById("ingest-source-id")?.value.trim() || "paper_source",
        doi: document.getElementById("ingest-doi")?.value.trim() || "",
        title: document.getElementById("ingest-title-field")?.value.trim() || "Untitled source",
        adapter: "local_semantic_scholar_pubmed_metadata_adapter"
      };
    }

    function normalizeLocalMetadataExport(raw) {
      try {
        const parsed = JSON.parse(raw);
        const record = Array.isArray(parsed)
          ? parsed[0]
          : Array.isArray(parsed.documents)
            ? parsed.documents[0]
            : parsed;
        if (!record || typeof record !== "object") return null;
        const externalIds = record.externalIds && typeof record.externalIds === "object" ? record.externalIds : {};
        const title = record.title || record.articleTitle || record.name || "";
        const abstract = record.abstract || record.summary || record.text || record.snippet || "";
        const doi = externalIds.DOI || record.doi || record.DOI || record.pmid || record.PMID || "";
        const sourceId = record.paperId || record.corpusId || record.pmid || record.PMID || record.id || "metadata_record";
        if (!title && !abstract) return null;
        return {
          source_id: String(sourceId).replace(/\W+/g, "_").slice(0, 80),
          doi: String(doi),
          title: String(title || "Untitled metadata record"),
          text: [title, abstract].filter(Boolean).join(". ")
        };
      } catch (_) {
        return null;
      }
    }

    function loadIngestFile(event) {
      const file = event.target.files && event.target.files[0];
      if (!file) return;
      document.getElementById("ingest-source-id").value = file.name.replace(/\W+/g, "_").slice(0, 80) || "uploaded_source";
      if (file.name.toLowerCase().endsWith(".pdf")) {
        document.getElementById("ingest-report-summary").textContent =
          "PDF selected. Browser UI records PDF provenance metadata; use capas.py extract/pipeline with the standalone PDF parser to extract text.";
        return;
      }
      const reader = new FileReader();
      reader.onload = () => {
        document.getElementById("ingest-source-text").value = String(reader.result || "");
        document.getElementById("ingest-report-summary").textContent = `Loaded ${file.name}; extract candidates when ready.`;
      };
      reader.readAsText(file);
    }

    function splitSourceSentences(text) {
      return text
        .split(/(?<=[.!?])\s+|\n+/)
        .map((sentence) => sentence.trim())
        .filter((sentence) => sentence.length > 24)
        .slice(0, 80);
    }

    function inferCandidateType(sentence) {
      const text = sentence.toLowerCase();
      if (text.includes("p_value") || text.includes("alpha") || text.includes("statistical")) return "statistical_confidence";
      if (text.includes("artifact") || text.includes("reproduction") || text.includes("reproducib")) return "reproducibility_check";
      if (text.includes("anchor") || text.includes("scaling") || text.includes("theorem") || text.includes("universal")) return "universal_anchor_claim";
      if (text.includes("causal") || text.includes("intervention") || text.includes("confounder")) return "causal_mechanism_claim";
      if (text.includes("systematic review") || text.includes("risk_of_bias") || text.includes("inclusion")) return "systematic_review_claim";
      if (text.includes("conflict") || text.includes("contradict")) return "evidence_conflict_claim";
      if (text.includes("figure") || text.includes("table") || text.includes("image") || text.includes("multimodal")) return "multimodal_evidence_claim";
      if (text.includes("metric") || text.includes("reported_value") || text.includes("reference_value")) return "financial_metric_claim";
      if (text.includes("abs_error") || text.includes("tolerance") || text.includes("accuracy")) return "exact_model_solution";
      return "claim_transition";
    }

    function normalizeEvidenceText(text) {
      return String(text || "")
        .replace(/[，؛；]/g, ",")
        .replace(/[。]/g, ".")
        .replace(/[“”]/g, '"')
        .replace(/[‘’]/g, "'");
    }

    function evidenceFieldPattern(field) {
      return field.replace(/_/g, "[_\\\\s-]?");
    }

    function parseBooleanEvidenceValue(raw) {
      const value = String(raw || "").trim().toLowerCase();
      if (/^(true|yes|pass|passed|1|present|available|confirmed|verified|established|controlled)$/i.test(value)) return true;
      if (/^(false|no|fail|failed|0|absent|unavailable|unconfirmed|unverified|not\\s+established|not\\s+controlled)$/i.test(value)) return false;
      return null;
    }

    function explicitValueFromText(text, field, exampleValue) {
      const normalized = normalizeEvidenceText(text);
      const fieldName = evidenceFieldPattern(field);
      if (typeof exampleValue === "boolean") {
        const booleanPattern = new RegExp(`\\b${fieldName}\\b\\s*(?:[:=]|is|was|=)?\\s*(true|false|yes|no|pass|passed|fail|failed|0|1|present|available|confirmed|verified|established|controlled|absent|unavailable|unconfirmed|unverified|not\\s+established|not\\s+controlled)\\b`, "i");
        const booleanMatch = normalized.match(booleanPattern);
        return booleanMatch ? parseBooleanEvidenceValue(booleanMatch[1]) : null;
      }
      if (typeof exampleValue === "number") {
        const numberPattern = new RegExp(`\\b${fieldName}\\b\\s*(?:[:=]|is|was|=)?\\s*(-?\\d+(?:\\.\\d+)?(?:e[+-]?\\d+)?)`, "i");
        const numberMatch = normalized.match(numberPattern);
        if (!numberMatch) return null;
        const value = parseFloat(numberMatch[1]);
        return Number.isFinite(value) ? value : null;
      }
      const pattern = new RegExp(`\\b${fieldName}\\b\\s*(?:[:=]|is|was|=)\\s*([^.;\\n]+)`, "i");
      const match = normalized.match(pattern);
      if (!match) return null;
      const raw = match[1].split(/\\s+(?:and|while|with)\\s+/i)[0].replace(/,$/, "").trim();
      if (Array.isArray(exampleValue)) return raw.split(/[|,]/).map((item) => item.trim()).filter(Boolean);
      return raw.replace(/^["']|["']$/g, "");
    }

    function evidenceFromCandidate(sentence, type) {
      const example = minimalExamples[type] || minimalExamples.exact_model_solution;
      const evidence = {};
      const spans = [];
      const lines = document.getElementById("ingest-source-text").value.split(/\n/);
      for (const field of required[type]) {
        const explicit = explicitValueFromText(sentence, field, example.evidence[field]);
        evidence[field] = explicit === null ? null : explicit;
        const lineIndex = lines.findIndex((line) => line.toLowerCase().includes(field.toLowerCase()) || line.includes(sentence.slice(0, 32)));
        if (lineIndex >= 0) {
          spans.push({
            field,
            line: lineIndex + 1,
            snippet: lines[lineIndex].trim().slice(0, 280),
            parser: explicit === null ? "candidate_sentence_match" : "explicit_assignment"
          });
        }
      }
      return { evidence, spans };
    }

    function extractCandidateClaims() {
      let sourceText = document.getElementById("ingest-source-text").value.trim();
      const adapted = normalizeLocalMetadataExport(sourceText);
      if (adapted) {
        document.getElementById("ingest-source-id").value = adapted.source_id;
        document.getElementById("ingest-doi").value = adapted.doi;
        document.getElementById("ingest-title-field").value = adapted.title;
        document.getElementById("ingest-source-text").value = adapted.text;
        sourceText = adapted.text;
      }
      const summary = document.getElementById("ingest-report-summary");
      if (!sourceText) {
        summary.textContent = "No source text supplied.";
        ingestCandidates = [];
        renderCandidateClaims();
        return;
      }
      const metadata = ingestMetadata();
      ingestCandidates = splitSourceSentences(sourceText)
        .map((sentence, index) => {
          const type = inferCandidateType(sentence);
          const extracted = evidenceFromCandidate(sentence, type);
          return {
            index,
            confirmed: false,
            claim: {
              id: `${metadata.source_id}_candidate_${index + 1}`,
              type,
              text: sentence.slice(0, 2000)
            },
            evidence: extracted.evidence,
            evidence_spans: extracted.spans,
            source_metadata: metadata
          };
        })
        .filter((candidate) => candidate.evidence_spans.length || candidate.claim.type !== "claim_transition")
        .slice(0, 8);
      summary.textContent = `${ingestCandidates.length} candidate claims extracted from ${metadata.title}. Confirm a row to build a CAPAS payload; CAPAS will not decide unconfirmed candidates.`;
      renderCandidateClaims();
    }

    function renderCandidateClaims() {
      const list = document.getElementById("candidate-claims-list");
      if (!list) return;
      if (!ingestCandidates.length) {
        list.innerHTML = `<div class="empty-state">No candidate claims extracted yet.</div>`;
        return;
      }
      list.innerHTML = ingestCandidates.map((candidate, index) => {
        const spanHtml = candidate.evidence_spans.length
          ? candidate.evidence_spans.map((span) => `<div class="candidate-span">line ${span.line} · ${escHtml(span.field)} · ${escHtml(span.parser)}<br>${escHtml(span.snippet)}</div>`).join("")
          : `<div class="candidate-span">No explicit evidence span found. This candidate should remain HOLD until evidence is supplied.</div>`;
        return (
          `<div class="candidate-row" role="listitem">` +
          `<div class="candidate-summary"><span class="verdict-badge HOLD">${escHtml(candidate.claim.type)}</span><span class="candidate-text">${escHtml(candidate.claim.text)}</span>` +
          `<button class="copy-btn" type="button" onclick="confirmCandidateClaim(${index})">Confirm & build payload</button></div>` +
          `<details class="candidate-spans" aria-label="Evidence spans for candidate ${index + 1}" open><summary>Evidence spans</summary>${spanHtml}</details>` +
          `</div>`
        );
      }).join("");
    }

    function payloadFromCandidate(candidate) {
      return {
        schema_version: capasSchemaVersion,
        claim: candidate.claim,
        evidence: candidate.evidence,
        source: {
          id: candidate.source_metadata.source_id,
          kind: "paper_text",
          title: candidate.source_metadata.title,
          doi: candidate.source_metadata.doi,
          text: document.getElementById("ingest-source-text").value
        },
        ingestion: {
          human_confirmed: candidate.confirmed === true,
          adapter: candidate.source_metadata.adapter,
          evidence_spans: candidate.evidence_spans
        },
        training_evidence: buildTrainingEvidenceDraft({})
      };
    }

    function confirmCandidateClaim(index) {
      const candidate = ingestCandidates[index];
      if (!candidate) return;
      candidate.confirmed = true;
      const payload = payloadFromCandidate(candidate);
      document.getElementById("input").value = JSON.stringify(payload, null, 2);
      onInputChange();
      markPayloadLoaded();
      renderCandidateClaims();
      document.getElementById("verdict-area").innerHTML =
        `<div class="assist-block"><div class="alert-title">Candidate confirmed</div>` +
        `<div>CAPAS built a payload from the paper/text candidate with ${candidate.evidence_spans.length} evidence spans. Run Decide only after reviewing the extracted fields.</div></div>`;
      setOutputEmpty();
      setCopyEnabled(false);
    }

    function buildIngestionReport() {
      if (!ingestCandidates.length) extractCandidateClaims();
      const report = {
        schema_version: capasSchemaVersion,
        report_type: "paper_ingestion_preview",
        source_metadata: ingestMetadata(),
        candidate_count: ingestCandidates.length,
        confirmed_count: ingestCandidates.filter((candidate) => candidate.confirmed).length,
        candidates: ingestCandidates.map((candidate) => ({
          claim: candidate.claim,
          evidence: candidate.evidence,
          evidence_spans: candidate.evidence_spans,
          human_confirmed: candidate.confirmed
        })),
        non_claim: "This browser ingestion report proposes candidate claims from explicit text spans; it does not perform broad paper understanding or theorem proving."
      };
      setOutputJson(report);
      setCopyEnabled(true);
      document.getElementById("verdict-area").innerHTML =
        `<div class="verdict-banner"><span class="verdict-badge HOLD">INGEST</span><span class="verdict-reason">${report.candidate_count} candidate claims prepared for human confirmation.</span></div>` +
        `<div class="assist-block"><div class="alert-title">Paper ingestion report</div>Use Confirm & build payload on a candidate before running Decide. Source spans remain visible for audit.</div>`;
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
        schema_version: capasSchemaVersion,
        claim: {
          id: parsed?.claim?.id || "draft_claim_001",
          type,
          text: parsed?.claim?.text || (raw && !parsed ? raw.slice(0, 2000) : minimalExamples[type].claim.text)
        },
        evidence: {},
        training_evidence: buildTrainingEvidenceDraft(parsed?.training_evidence)
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
        draft.evidence.current_claim = sourceEvidence.current_claim || "Replace with the exact weaker claim text currently licensed.";
      }
      document.getElementById("input").value = JSON.stringify(draft, null, 2);
      onInputChange();
      markPayloadLoaded();
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

    function isProvenanceBlocked(result) {
      const blockers = result?.fine_tune_blockers || [];
      return blockers.some((blocker) => /provenance|hash|source|witness|RO-Crate|reviewer|attestation|registry/i.test(blocker));
    }

    function renderExecutiveDashboard(sourceResults) {
      const results = Array.isArray(sourceResults)
        ? sourceResults
        : decisionHistory.map((item) => item.decision).filter(Boolean);
      const counts = { ACCEPT: 0, REWRITE: 0, REJECT: 0, HOLD: 0 };
      let fineTuneReady = 0;
      let provenanceBlocked = 0;
      for (const result of results) {
        const verdict = result?.verdict || "HOLD";
        counts[verdict] = (counts[verdict] || 0) + 1;
        if (result?.fine_tune_ready === true) fineTuneReady += 1;
        if (isProvenanceBlocked(result)) provenanceBlocked += 1;
      }
      const set = (id, value) => {
        const node = document.getElementById(id);
        if (node) node.textContent = String(value);
      };
      set("metric-total", results.length);
      set("metric-accept", counts.ACCEPT || 0);
      set("metric-rewrite", counts.REWRITE || 0);
      set("metric-reject", counts.REJECT || 0);
      set("metric-ft-ready", fineTuneReady);
      set("metric-provenance", provenanceBlocked);
    }

    function updateRoiCalculator() {
      const readNumber = (id, fallback) => {
        const value = Number(document.getElementById(id)?.value);
        return Number.isFinite(value) && value >= 0 ? value : fallback;
      };
      const claims = readNumber("roi-claims", 1000);
      const manualMinutes = readNumber("roi-manual", 30);
      const capasMinutes = readNumber("roi-triage", 5);
      const hourlyRate = readNumber("roi-rate", 180);
      const avoidedMinutes = Math.max(0, claims * (manualMinutes - capasMinutes));
      const avoidedHours = avoidedMinutes / 60;
      const avoidedValue = avoidedHours * hourlyRate;
      const hoursNode = document.getElementById("roi-hours");
      const valueNode = document.getElementById("roi-value");
      if (hoursNode) hoursNode.textContent = `${Math.round(avoidedHours).toLocaleString()}h`;
      if (valueNode) valueNode.textContent = `~$${Math.round(avoidedValue).toLocaleString()} senior-review capacity avoided in the pilot model.`;
    }

    function historyFilters() {
      return {
        query: (document.getElementById("history-filter")?.value || "").trim().toLowerCase(),
        verdict: document.getElementById("history-verdict-filter")?.value || ""
      };
    }

    function historyMatches(item, filters) {
      if (filters.verdict && item.verdict !== filters.verdict) return false;
      if (!filters.query) return true;
      const payloadType = item.decision?.input_claim?.type || "";
      const haystack = `${item.id} ${payloadType} ${item.verdict} ${item.reason}`.toLowerCase();
      return haystack.includes(filters.query);
    }

    function renderHistory() {
      const list = document.getElementById("history-list");
      document.getElementById("history-count").textContent = `${decisionHistory.length}/${historyLimit} saved`;
      renderExecutiveDashboard();
      if (!decisionHistory.length) {
        list.innerHTML = `<div class="empty-state">No decisions yet.</div>`;
        return;
      }
      const filters = historyFilters();
      const visible = decisionHistory
        .map((item, index) => ({ item, index }))
        .filter(({ item }) => historyMatches(item, filters));
      if (!visible.length) {
        list.innerHTML = `<div class="empty-state">No matching decisions.</div>`;
        return;
      }
      const rows = visible.map(({ item, index }) => {
        let payloadType = "-";
        try {
          const parsed = JSON.parse(item.payload || "{}");
          payloadType = parsed?.claim?.type || "-";
        } catch (_) {}
        return (
        `<div class="history-row" role="listitem">` +
        `<button type="button" class="history-item" data-history-index="${index}" aria-label="Restore decision ${escHtml(item.id)} from ${escHtml(formatHistoryTimestamp(item.timestamp))}">` +
        `<span class="history-badge ${item.verdict}">${item.verdict}</span>` +
        `<span class="history-id">${escHtml(item.id)}</span>` +
        `<span class="history-type">${escHtml(payloadType)}</span>` +
        `<span class="history-reason">${escHtml(item.reason)}</span>` +
        `<time class="history-ts" datetime="${escHtml(item.timestamp || "")}">${escHtml(formatHistoryTimestamp(item.timestamp))}</time>` +
        `</button>` +
        `<button type="button" class="history-delete" data-history-index="${index}" aria-label="Delete decision ${escHtml(item.id)}">Delete</button>` +
        `</div>`
        );
      }).join("");
      list.innerHTML =
        `<div class="audit-table" role="table" aria-label="Governance decision audit log">` +
        `<div class="audit-row header" role="row"><span>Verdict</span><span>Claim ID</span><span>Type</span><span>Reason</span><span>Timestamp</span><span>Actions</span></div>` +
        rows +
        `</div>`;
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
      renderExecutiveDashboard();
    }

    function handleHistoryKey(event, index) {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        restoreHistory(index);
      }
    }

    function historyIndexFromEvent(event, selector) {
      const target = event.target.closest(selector);
      if (!target) return null;
      const index = Number(target.dataset.historyIndex);
      return Number.isInteger(index) ? index : null;
    }

    function handleHistoryListClick(event) {
      const deleteIndex = historyIndexFromEvent(event, ".history-delete");
      if (deleteIndex !== null) {
        deleteHistory(deleteIndex, event);
        return;
      }
      const restoreIndex = historyIndexFromEvent(event, ".history-item");
      if (restoreIndex !== null) restoreHistory(restoreIndex);
    }

    function handleHistoryListKeydown(event) {
      const restoreIndex = historyIndexFromEvent(event, ".history-item");
      if (restoreIndex !== null) handleHistoryKey(event, restoreIndex);
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
        if (sensitiveMode) {
          copyAppUrl("Sensitive mode copied app URL");
          const existing = document.getElementById("share-privacy-warning");
          if (existing) existing.remove();
          document.getElementById("verdict-area").insertAdjacentHTML(
            "beforeend",
            `<div class="assist-block" id="share-privacy-warning"><div class="alert-title">Sensitive data mode</div>Payload embedding is disabled. CAPAS copied only the app URL, with no claim or provenance data.</div>`
          );
          return;
        }
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

    function copyAppUrl(label = "App URL copied") {
      const url = `${window.location.origin}${window.location.pathname}`;
      navigator.clipboard.writeText(url).then(() => {
        const button = document.getElementById("share-app-btn");
        button.textContent = label;
        button.classList.add("copied");
        setTimeout(() => {
          button.textContent = "Share App";
          button.classList.remove("copied");
        }, 1600);
      });
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
        sensitiveMode ? "[redacted in sensitive data mode]" : item.payload,
        sensitiveMode ? "[redacted in sensitive data mode]" : JSON.stringify(item.decision)
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

    function applySensitiveMode() {
      const button = document.getElementById("sensitive-mode-toggle");
      if (!button) return;
      button.textContent = sensitiveMode ? "Sensitive: On" : "Sensitive: Off";
      button.classList.toggle("sensitive-active", sensitiveMode);
      button.setAttribute(
        "aria-label",
        sensitiveMode
          ? "Sensitive data mode is on. Share URL will not embed payload and CSV export will redact payload fields."
          : "Sensitive data mode is off. Share URL embeds payload and CSV export includes payload fields."
      );
    }

    function toggleSensitiveMode() {
      sensitiveMode = !sensitiveMode;
      if (sensitiveMode) {
        localStorage.setItem(sensitiveModeStorageKey, "true");
      } else {
        localStorage.removeItem(sensitiveModeStorageKey);
      }
      applySensitiveMode();
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
        markOnboarded();
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
        markOnboarded();
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

    function loadBatchDemo() {
      const batch = [
        samples.ACCEPT,
        samples.CAUSAL,
        samples.SYSTEMATIC,
        samples.CONFLICT,
        samples.MULTIMODAL
      ].filter(Boolean);
      document.getElementById("input").value = JSON.stringify(batch, null, 2);
      onInputChange();
      markPayloadLoaded({ scroll: true });
      decideBatch();
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
    initOnboardingState();
    renderGuidedFields();
    setGateMode("single");
    updateRoiCalculator();
    applySensitiveMode();
    document.getElementById("history-list").addEventListener("click", handleHistoryListClick);
    document.getElementById("history-list").addEventListener("keydown", handleHistoryListKeydown);
    maybeLoadSharedPayload();
    onInputChange();
    renderHistory();
</script>
</body>
</html>
"""
    rendered = (
        html.replace("__SAMPLE_JSON__", sample_json)
        .replace("__SAMPLE_COMPACT_JSON__", json.dumps(sample, sort_keys=True))
        .replace("__SAMPLES_JSON__", samples_json)
        .replace("__UI_VERSION__", CAPAS_UI_VERSION)
    )
    return _apply_inline_csp_hashes(rendered)


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


def _api_workspace(handler: BaseHTTPRequestHandler) -> str:
    raw = handler.headers.get("x-capas-workspace", "default")
    workspace = re.sub(r"[^A-Za-z0-9_.-]+", "-", raw).strip("-")
    return workspace[:80] or "default"


def _api_authorized(handler: BaseHTTPRequestHandler) -> bool:
    token = getattr(handler.server, "capas_api_token", "")  # type: ignore[attr-defined]
    if not token:
        return True
    supplied = handler.headers.get("authorization", "")
    return supplied == f"Bearer {token}"


def _api_audit_dir(handler: BaseHTTPRequestHandler) -> Path | None:
    value = getattr(handler.server, "capas_audit_dir", "")  # type: ignore[attr-defined]
    if not value:
        return None
    path = Path(str(value))
    return path if path.is_absolute() else ROOT / path


def _append_api_audit(handler: BaseHTTPRequestHandler, operation: str, result: dict[str, Any]) -> None:
    audit_dir = _api_audit_dir(handler)
    if audit_dir is None:
        return
    workspace = _api_workspace(handler)
    audit_dir.mkdir(parents=True, exist_ok=True)
    claim = result.get("input_claim", {}) if isinstance(result, dict) else {}
    entry = {
        "operation": operation,
        "workspace": workspace,
        "schema_version": CAPAS_CLAIM_SCHEMA_VERSION,
        "verdict": result.get("verdict"),
        "summary": result.get("summary"),
        "claim_id": claim.get("id") if isinstance(claim, dict) else None,
        "fine_tune_ready": result.get("fine_tune_ready"),
        "decision": result,
    }
    with (audit_dir / f"{workspace}.jsonl").open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(entry, sort_keys=True) + "\n")


def _read_api_audit(handler: BaseHTTPRequestHandler) -> dict[str, Any]:
    audit_dir = _api_audit_dir(handler)
    workspace = _api_workspace(handler)
    if audit_dir is None:
        return {"workspace": workspace, "decisions": [], "audit_enabled": False}
    path = audit_dir / f"{workspace}.jsonl"
    decisions: list[dict[str, Any]] = []
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            try:
                decisions.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return {"workspace": workspace, "decisions": decisions[-250:], "audit_enabled": True}


def provenance_verification_report(payload: dict[str, Any]) -> dict[str, Any]:
    training_evidence = payload.get("training_evidence") if isinstance(payload, dict) else None
    provenance = training_evidence.get("provenance") if isinstance(training_evidence, dict) else None
    if not isinstance(provenance, dict):
        provenance = {}
    checks = {
        "review_hash_verified": _verify_review_hash(provenance),
        "source_urls_recoverable_hashable": _verify_sources(provenance),
        "witness_registry_resolved": _verify_witness_registry(provenance),
        "ro_crate_validated": _verify_ro_crate(provenance),
        "reviewer_attestation_verified": _verify_reviewer_attestation(provenance),
    }
    return {
        "schema_version": CAPAS_CLAIM_SCHEMA_VERSION,
        "provenance_ready": all(checks.values()),
        "checks": checks,
        "verification_surface": "local_cli_or_enterprise_api",
        "non_claim": "This verifies declared provenance artifacts and hashes; it does not infer scientific truth.",
    }


class CapasApiHandler(BaseHTTPRequestHandler):
    server_version = "CAPASClaimGate/0.1"

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003 - stdlib callback name
        return

    def do_GET(self) -> None:  # noqa: N802 - stdlib callback name
        if not _api_authorized(self):
            _write_response_json(self, 401, {"error": "unauthorized", "fine_tune_ready": False})
            return
        if self.path == "/health":
            _write_response_json(self, 200, {
                "status": "ok",
                "service": "capas-claim-gate",
                "schema_version": CAPAS_CLAIM_SCHEMA_VERSION,
                "schema_id": CANONICAL_SCHEMA_ID,
                "audit_enabled": _api_audit_dir(self) is not None,
            })
        elif self.path.startswith("/decisions"):
            _write_response_json(self, 200, _read_api_audit(self))
        else:
            _write_response_json(self, 404, {"error": "not found", "available": ["/health", "/decisions", "/decide", "/batch", "/provenance-check"]})

    def do_POST(self) -> None:  # noqa: N802 - stdlib callback name
        if not _api_authorized(self):
            _write_response_json(self, 401, {"error": "unauthorized", "fine_tune_ready": False})
            return
        try:
            payload = _read_request_json(self)
            if self.path == "/decide":
                if not isinstance(payload, dict):
                    raise ValueError("/decide expects one JSON object")
                result = decide_external_claim(payload)
                _append_api_audit(self, "decide", result)
                _write_response_json(self, 200, result)
            elif self.path == "/batch":
                result = run_batch(payload, mode="decide")
                _append_api_audit(self, "batch", result)
                _write_response_json(self, 200, result)
            elif self.path == "/provenance-check":
                if not isinstance(payload, dict):
                    raise ValueError("/provenance-check expects one JSON object")
                _write_response_json(self, 200, provenance_verification_report(payload))
            else:
                _write_response_json(self, 404, {"error": "not found", "available": ["/health", "/decisions", "/decide", "/batch", "/provenance-check"]})
        except (json.JSONDecodeError, ValueError) as exc:
            _write_response_json(self, 400, {"error": str(exc), "fine_tune_ready": False})


def cmd_serve(args: argparse.Namespace) -> int:
    server = HTTPServer((args.host, args.port), CapasApiHandler)
    server.capas_api_token = args.api_token or os.environ.get("CAPAS_API_TOKEN", "")  # type: ignore[attr-defined]
    server.capas_audit_dir = args.audit_dir or os.environ.get("CAPAS_AUDIT_DIR", "")  # type: ignore[attr-defined]
    print(f"CAPAS API listening on http://{args.host}:{args.port}")
    print("endpoints: GET /health, GET /decisions, POST /decide, POST /batch, POST /provenance-check")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nshutting down")
    finally:
        server.server_close()
    return 0


def cmd_provenance_check(args: argparse.Namespace) -> int:
    payload = _load_json(Path(args.input))
    report = provenance_verification_report(payload)
    if args.output:
        _write_json(Path(args.output), report)
    if args.json or not args.output:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"provenance_ready: {report['provenance_ready']}")
        print(f"wrote {args.output}")
    return 0 if report["provenance_ready"] else 1


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
    serve.add_argument("--api-token", default="", help="optional bearer token; also read from CAPAS_API_TOKEN")
    serve.add_argument("--audit-dir", default="", help="optional workspace JSONL audit directory; also read from CAPAS_AUDIT_DIR")
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

    provenance_check = subparsers.add_parser("provenance-check", help="verify review/source/witness/RO-Crate provenance artifacts")
    provenance_check.add_argument("--input", required=True, help="path to claim/evidence JSON with training_evidence.provenance")
    provenance_check.add_argument("--output", help="optional provenance verification report path")
    provenance_check.add_argument("--json", action="store_true", help="print JSON even when --output is supplied")
    provenance_check.set_defaults(func=cmd_provenance_check)

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
