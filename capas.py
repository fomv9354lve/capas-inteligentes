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
                    "id": {"type": "string", "minLength": 1, "maxLength": 256},
                    "type": {"type": "string", "enum": claim_types},
                    "text": {"type": "string", "minLength": 1, "maxLength": 4000},
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
                    "anchor_mode": {"type": "string"},
                    "local_property_tests_pass": {"type": "boolean"},
                    "universal_anchor_pass": {"type": "boolean"},
                    "upgrade_evidence_present": {"type": "boolean"},
                    "physical_evidence_level": {"type": "string"},
                    "verification_independence": {"type": "string"},
                    "reference_truth": {},
                    "current_claim": {
                        "type": "string",
                        "maxLength": 4000,
                        "description": "Optional weaker claim text for REWRITE. Raw HTML angle brackets are rejected because this value can be displayed by downstream consumers.",
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
    if isinstance(claim.get("text"), str) and len(claim["text"]) > 4000:
        errors.append("claim.text must be at most 4000 characters")

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

    if "anchor_mode" in evidence and not isinstance(evidence["anchor_mode"], str):
        errors.append("evidence.anchor_mode must be a string")
    if "current_claim" in evidence:
        current_claim = evidence["current_claim"]
        if not isinstance(current_claim, str):
            errors.append("evidence.current_claim must be a string")
        else:
            if len(current_claim) > 4000:
                errors.append("evidence.current_claim must be at most 4000 characters")
            if "<" in current_claim or ">" in current_claim:
                errors.append("evidence.current_claim must not contain raw HTML angle brackets")
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
  .sample-btn.accept { color: #4ade80; border-color: #4ade80; }
  .sample-btn.rewrite { color: #fb923c; border-color: #fb923c; }
  .sample-btn.hold { color: #94a3b8; border-color: #94a3b8; }
  .sample-btn.invalid { color: #f87171; border-color: #f87171; }
  .grid { display: grid; grid-template-columns: 420px 1fr; gap: 20px; align-items: start; }
  @media (max-width: 800px) { .grid { grid-template-columns: 1fr; } }
  .panel { background: #1a1f2e; border: 1px solid #2d3748; border-radius: 10px; overflow: hidden; }
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
  pre#output {
    background: #0a0d14;
    border: 1px solid #2d3748;
    border-radius: 6px;
    padding: 12px;
    font-size: 12px;
    font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
    overflow: auto;
    max-height: 340px;
    margin: 0;
    color: #94a3b8;
    line-height: 1.6;
  }
  .history-section { margin-top: 28px; padding-bottom: 40px; }
  .history-section h3 { font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.8px; margin: 0 0 10px 0; }
  .history-list { display: flex; flex-direction: column; gap: 6px; }
  .history-item { background: #1a1f2e; border: 1px solid #2d3748; border-radius: 7px; padding: 8px 12px; display: flex; align-items: center; gap: 10px; font-size: 12px; }
  .history-badge { font-size: 10px; font-weight: 800; padding: 2px 8px; border-radius: 10px; flex-shrink: 0; }
  .history-badge.ACCEPT { background: #14532d; color: #4ade80; }
  .history-badge.REJECT { background: #450a0a; color: #f87171; }
  .history-badge.REWRITE { background: #431407; color: #fb923c; }
  .history-badge.HOLD { background: #1e293b; color: #94a3b8; }
  .history-id { color: #64748b; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; flex-shrink: 0; }
  .history-reason { color: #94a3b8; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .empty-state { color: #475569; font-size: 12px; font-style: italic; }
  .no-decision { padding: 32px 16px; text-align: center; color: #475569; font-size: 13px; }
</style>
</head>
<body>

<div class="header">
  <h1>CAPAS Claim Gate</h1>
  <p>Paste a claim/evidence JSON. Decisions are rule-based via <code>capas.py decide</code>. Schema errors surface as <code>HOLD</code>, never as guesses.</p>
</div>

<div class="samples-bar">
  <span>Load sample:</span>
  <button class="sample-btn accept" title="ACCEPT sample" onclick="loadSample('ACCEPT')">&#10003; ACCEPT</button>
  <button class="sample-btn rewrite" title="REWRITE sample" onclick="loadSample('REWRITE')">&#8634; REWRITE</button>
  <button class="sample-btn hold" title="HOLD sample" onclick="loadSample('HOLD')">&#9646; HOLD</button>
  <button class="sample-btn invalid" title="INVALID sample" onclick="loadSample('INVALID')">&#10005; INVALID</button>
</div>

<div class="grid">
  <div>
    <div class="panel">
      <div class="panel-header">
        <span class="panel-title">Input JSON</span>
        <span class="panel-tag" id="type-label"></span>
      </div>
      <textarea id="input" spellcheck="false" oninput="onInputChange()">__SAMPLE_JSON__</textarea>
      <div class="json-status" id="json-status">Waiting for input...</div>
      <button class="decide-btn" onclick="decide()">Decide <span class="decide-hint">⌘↵</span></button>
    </div>
  </div>

  <div>
    <div class="panel">
      <div class="panel-header">
        <span class="panel-title">Decision</span>
        <button class="copy-btn" id="copy-btn" onclick="copyOutput()">Copy JSON</button>
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
  <h3>Recent decisions</h3>
  <div class="history-list" id="history-list">
    <div class="empty-state">No decisions yet.</div>
  </div>
</div>

<script>
    const sample = __SAMPLE_COMPACT_JSON__;
    const samples = __SAMPLES_JSON__;
    const required = {
      exact_model_solution: ["abs_error", "tolerance"],
      physical_accuracy: ["within_chemical_accuracy"],
      universal_anchor_claim: ["anchor_mode", "local_property_tests_pass", "universal_anchor_pass"],
      claim_transition: ["upgrade_evidence_present"]
    };
    const claimTypes = Object.keys(required).sort();
    let decisionHistory = [];

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
      if (typeof safeClaim.text === "string" && safeClaim.text.length > 4000) {
        errors.push("claim.text must be at most 4000 characters");
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
      if (Object.prototype.hasOwnProperty.call(safeEvidence, "anchor_mode") && typeof safeEvidence.anchor_mode !== "string") {
        errors.push("evidence.anchor_mode must be a string");
      }
      if (Object.prototype.hasOwnProperty.call(safeEvidence, "current_claim")) {
        if (typeof safeEvidence.current_claim !== "string") {
          errors.push("evidence.current_claim must be a string");
        } else {
          if (safeEvidence.current_claim.length > 4000) {
            errors.push("evidence.current_claim must be at most 4000 characters");
          }
          if (safeEvidence.current_claim.includes("<") || safeEvidence.current_claim.includes(">")) {
            errors.push("evidence.current_claim must not contain raw HTML angle brackets");
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

    function addToHistory(result) {
      decisionHistory.unshift({ verdict: result.verdict, id: result.input_claim?.id || "-", reason: result.reason });
      decisionHistory = decisionHistory.slice(0, 6);
      document.getElementById("history-list").innerHTML = decisionHistory.map((item) => (
        `<div class="history-item"><span class="history-badge ${item.verdict}">${item.verdict}</span><span class="history-id">${escHtml(item.id)}</span><span class="history-reason">${escHtml(item.reason)}</span></div>`
      )).join("");
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

    function decide() {
      try {
        const payload = JSON.parse(document.getElementById("input").value);
        const result = rule(payload);
        renderVerdict(result);
        document.getElementById("output").textContent = JSON.stringify(result, null, 2);
        addToHistory(result);
        const copy = document.getElementById("copy-btn");
        copy.textContent = "Copy JSON";
        copy.classList.remove("copied");
      } catch (error) {
        document.getElementById("verdict-area").innerHTML = `<div class="alert-block errors"><div class="alert-title">JSON parse error</div>${escHtml(error.message)}</div>`;
        document.getElementById("output").textContent = "";
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
    decide();
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
