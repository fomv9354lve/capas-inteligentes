from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .prov_export import run_trace_to_prov_json
from .trace import RunTrace, stable_hash


RO_CRATE_CONTEXT = "https://w3id.org/ro/crate/1.1/context"
RO_CRATE_CONFORMS_TO = "https://w3id.org/ro/crate/1.1"
WORKFLOW_RUN_CRATE_PROFILE = "https://w3id.org/workflowhub/workflow-ro-crate/1.0"
CAPAS_PROFILE = "https://example.org/capas-inteligentes/ro-crate/physical-evidence/0.1"
CAPAS_WORKFLOW_ID = "workflow/capas-costurero-run.py"
CAPAS_SOFTWARE_ID = "software:capas-costurero"
WORKLOAD_ID = "entity:workload"


def run_trace_to_ro_crate_metadata(
    trace: RunTrace,
    *,
    trace_file: str,
    prov_file: str | None = None,
    crate_dir: Path | None = None,
) -> dict[str, Any]:
    """Export a RunTrace as RO-Crate JSON-LD metadata.

    This does not replace Workflow Run RO-Crate. It uses RO-Crate as the
    packaging standard and adds a small CAPAS profile entity for physical
    evidence semantics.
    """

    trace_id = f"trace:{trace.hash()[:16]}"
    result_id = f"{trace_id}:result"
    decision_id = f"{trace_id}:routing-decision"
    evidence_id = f"{trace_id}:physical-evidence"
    root_id = "./"
    run_status = _action_status(trace)
    start_time, end_time = _event_time_bounds(trace)
    has_part = [
        {"@id": trace_file},
        {"@id": CAPAS_WORKFLOW_ID},
        {"@id": CAPAS_SOFTWARE_ID},
        {"@id": WORKLOAD_ID},
        {"@id": decision_id},
    ]
    if trace.result_hash:
        has_part.append({"@id": result_id})

    graph: list[dict[str, Any]] = [
        {
            "@id": "ro-crate-metadata.json",
            "@type": "CreativeWork",
            "conformsTo": [
                {"@id": RO_CRATE_CONFORMS_TO},
                {"@id": WORKFLOW_RUN_CRATE_PROFILE},
                {"@id": CAPAS_PROFILE},
            ],
            "about": {"@id": root_id},
        },
        {
            "@id": root_id,
            "@type": "Dataset",
            "name": "CAPAS traced scientific computation crate",
            "description": (
                "RO-Crate package containing a sealed RunTrace, optional PROV export, "
                "routing decision, runtime context, and CAPAS physical evidence metadata."
            ),
            "hasPart": has_part,
            "conformsTo": [
                {"@id": RO_CRATE_CONFORMS_TO},
                {"@id": WORKFLOW_RUN_CRATE_PROFILE},
                {"@id": CAPAS_PROFILE},
            ],
            "datePublished": end_time,
            "capas:traceHash": trace.hash(),
            "capas:workloadHash": trace.workload_hash,
            "capas:workflowRunCrateAlignment": "shape-compatible-with-workflow-run-ro-crate-v0",
        },
        {
            "@id": trace_file,
            "@type": ["File", "DigitalDocument"],
            "name": "Sealed CAPAS RunTrace",
            "encodingFormat": "application/json",
            "sha256": _file_sha256_if_exists(trace_file, crate_dir),
            "about": {"@id": trace_id},
        },
        {
            "@id": trace_id,
            "@type": "CreateAction",
            "name": "CAPAS costurero traced run",
            "agent": {"@id": CAPAS_SOFTWARE_ID},
            "instrument": {"@id": CAPAS_WORKFLOW_ID},
            "object": {"@id": WORKLOAD_ID},
            "result": {"@id": result_id} if trace.result_hash else None,
            "actionStatus": run_status,
            "startTime": start_time,
            "endTime": end_time,
            "capas:routingDecision": {"@id": decision_id},
            "capas:traceHash": trace.hash(),
            "capas:traceSchemaVersion": trace.trace_schema_version,
            "capas:hashAlgorithm": trace.hash_algorithm,
            "capas:error": trace.error,
            "capas:decisionRoute": trace.decision_route,
            "capas:decisionReason": trace.decision_reason,
            "capas:evidenceStatus": None,
        },
        {
            "@id": CAPAS_WORKFLOW_ID,
            "@type": ["File", "SoftwareSourceCode", "ComputationalWorkflow"],
            "name": "CAPAS costurero workflow",
            "description": (
                "Workflow plan that ingests a scientific workload, records runtime context, "
                "estimates routing cost, executes or skips the selected engine, and attaches "
                "CAPAS physical-evidence metadata."
            ),
            "programmingLanguage": "Python",
            "input": {"@id": "parameter:workload"},
            "output": {"@id": "parameter:result"},
            "capas:traceSchemaVersion": trace.trace_schema_version,
        },
        {
            "@id": "parameter:workload",
            "@type": "FormalParameter",
            "name": "Scientific workload",
            "additionalType": "https://bioschemas.org/FormalParameter",
        },
        {
            "@id": "parameter:result",
            "@type": "FormalParameter",
            "name": "Result summary or skipped/failure state",
            "additionalType": "https://bioschemas.org/FormalParameter",
        },
        {
            "@id": CAPAS_SOFTWARE_ID,
            "@type": "SoftwareApplication",
            "name": "CAPAS INTELIGENTES costurero",
            "applicationCategory": "Scientific provenance and evidence tracing",
        },
        {
            "@id": WORKLOAD_ID,
            "@type": "Dataset",
            "name": "Workload summary",
            "capas:workloadHash": trace.workload_hash,
            "capas:summary": trace.workload_summary,
        },
        {
            "@id": decision_id,
            "@type": "Thing",
            "name": "Routing decision",
            "capas:route": trace.decision_route,
            "capas:reason": trace.decision_reason,
        },
    ]

    if prov_file:
        graph[1]["hasPart"].append({"@id": prov_file})
        graph.append(
            {
                "@id": prov_file,
                "@type": ["File", "DigitalDocument"],
                "name": "W3C PROV-shaped export",
                "encodingFormat": "application/json",
                "sha256": _file_sha256_if_exists(prov_file, crate_dir),
            }
        )

    if trace.result_hash:
        graph.append(
            {
                "@id": result_id,
                "@type": "Dataset",
                "name": "Result summary",
                "capas:resultHash": trace.result_hash,
                "capas:summary": trace.result_summary,
            }
        )

    evidence = _physical_evidence_from_trace(trace)
    evidence_status = _evidence_status(trace, evidence)
    for node in graph:
        if node.get("@id") == root_id:
            node["capas:evidenceStatus"] = evidence_status
        if node.get("@id") == trace_id:
            node["capas:evidenceStatus"] = evidence_status
            break
    if evidence:
        graph.append(
            {
                "@id": evidence_id,
                "@type": "capas:PhysicalEvidence",
                "name": "Physical evidence attached to result",
                "capas:physicalEvidenceLevel": evidence.get("physical_evidence_level"),
                "capas:verificationIndependence": evidence.get("verification_independence"),
                "capas:witnessStack": evidence.get("witness_stack"),
                "capas:evidenceStatusDetail": evidence.get("evidence_status_detail"),
                "capas:degeneracyCount": evidence.get("degeneracy_count"),
                "capas:optimalAssignments": evidence.get("optimal_assignments"),
                "capas:tasks": evidence.get("tasks"),
                "capas:people": evidence.get("people"),
                "capas:costs": evidence.get("costs"),
                "capas:balanceLambda": evidence.get("balance_lambda"),
                "capas:conflicts": evidence.get("conflicts"),
                "capas:spinEncoding": evidence.get("spin_encoding"),
                "capas:isingH": evidence.get("ising_h"),
                "capas:isingJ": evidence.get("ising_J"),
                "capas:constantOffset": evidence.get("constant_offset"),
                "capas:mappingTerms": evidence.get("mapping_terms"),
                "capas:falsificationNotes": evidence.get("falsification_notes"),
                "capas:referenceTruth": evidence.get("reference_truth"),
                "capas:benchmarkFamily": evidence.get("benchmark_family"),
                "capas:observable": evidence.get("observable"),
                "capas:expected": evidence.get("expected"),
                "capas:value": evidence.get("value"),
                "capas:absError": evidence.get("abs_error"),
                "capas:units": evidence.get("units"),
                "capas:detail": evidence.get("physical_evidence_detail"),
                "capas:certificationStatus": evidence.get("certification_status"),
                "capas:formalBoundStatus": evidence.get("formal_bound_status"),
                "capas:sourceLabel": evidence.get("source_label"),
                "capas:discardedWeight": evidence.get("discarded_weight"),
                "capas:actualErrorSquared": evidence.get("actual_error_squared"),
                "capas:composedStateErrorBound": evidence.get("composed_state_error_bound"),
                "capas:boundSlack": evidence.get("bound_slack"),
                "capas:boundType": evidence.get("bound_type"),
                "capas:boundScope": evidence.get("bound_scope"),
                "capas:evidenceHash": stable_hash(evidence),
                "about": {"@id": result_id},
            }
        )
        for node in graph:
            if node.get("@id") == root_id:
                node["hasPart"].append({"@id": evidence_id})
                break
        if trace.result_hash:
            for node in graph:
                if node.get("@id") == result_id:
                    node["capas:physicalEvidence"] = {"@id": evidence_id}
                    break

    for idx, event in enumerate(trace.events):
        event_id = f"{trace_id}:event:{idx}:{event.stage}"
        graph.append(
            {
                "@id": event_id,
                "@type": "Action",
                "name": event.stage,
                "actionStatus": event.status,
                "description": event.message,
                "startTime": event.timestamp,
                "capas:metrics": event.metrics,
            }
        )

    return {
        "@context": [
            RO_CRATE_CONTEXT,
            {
                "capas": "https://example.org/capas-inteligentes#",
                "sha256": "https://schema.org/sha256",
            },
        ],
        "@graph": [_strip_none(node) for node in graph],
    }


def write_ro_crate_for_trace(trace: RunTrace, out_dir: Path, *, trace_payload: dict[str, Any]) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    workflow_dir = out_dir / "workflow"
    workflow_dir.mkdir(exist_ok=True)
    trace_path = out_dir / "runtrace.json"
    prov_path = out_dir / "runtrace.prov.json"
    workflow_path = out_dir / CAPAS_WORKFLOW_ID
    crate_path = out_dir / "ro-crate-metadata.json"

    trace_path.write_text(json.dumps(trace_payload, indent=2, sort_keys=True), encoding="utf-8")
    prov_path.write_text(json.dumps(run_trace_to_prov_json(trace), indent=2, sort_keys=True), encoding="utf-8")
    workflow_path.write_text(_workflow_descriptor_source(), encoding="utf-8")
    crate = run_trace_to_ro_crate_metadata(
        trace,
        trace_file="runtrace.json",
        prov_file="runtrace.prov.json",
        crate_dir=out_dir,
    )
    crate_path.write_text(json.dumps(crate, indent=2, sort_keys=True), encoding="utf-8")
    return crate_path


def _physical_evidence_from_trace(trace: RunTrace) -> dict[str, Any]:
    evidence: dict[str, Any] = {}
    if trace.result_summary:
        for key in (
            "physical_evidence_level",
            "physical_evidence_detail",
            "observable",
            "units",
            "abs_error",
            "expected",
            "value",
            "benchmark_family",
            "reference_truth",
            "verification_independence",
            "witness_stack",
            "evidence_status_detail",
            "degeneracy_count",
            "optimal_assignments",
            "tasks",
            "people",
            "costs",
            "balance_lambda",
            "conflicts",
            "spin_encoding",
            "ising_h",
            "ising_J",
            "constant_offset",
            "mapping_terms",
            "falsification_notes",
            "certification_status",
            "formal_bound_status",
            "source_label",
            "discarded_weight",
            "actual_error_squared",
            "composed_state_error_bound",
            "bound_slack",
            "bound_type",
            "bound_scope",
        ):
            if key in trace.result_summary:
                evidence[key] = trace.result_summary[key]
    for event in trace.events:
        if event.stage == "physical_evidence":
            evidence.update(event.metrics)
    return evidence


def _evidence_status(trace: RunTrace, evidence: dict[str, Any]) -> str:
    if evidence:
        level = evidence.get("physical_evidence_level")
        if level == "none":
            return "none_declared"
        return "present"
    if trace.error:
        return "not_applicable_failed"
    if trace.decision_route in {"QPU_REQUIRED", "TENSOR_REQUIRED", "TENSOR_TOO_SLOW"}:
        return "not_applicable_rejected"
    return "missing"


def _action_status(trace: RunTrace) -> str:
    if trace.error:
        return "FailedActionStatus"
    return "CompletedActionStatus"


def _event_time_bounds(trace: RunTrace) -> tuple[str | None, str | None]:
    if not trace.events:
        return None, None
    timestamps = [_iso_from_timestamp(event.timestamp) for event in trace.events]
    return timestamps[0], timestamps[-1]


def _iso_from_timestamp(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp, tz=UTC).isoformat().replace("+00:00", "Z")


def _workflow_descriptor_source() -> str:
    return '''"""CAPAS costurero workflow descriptor.

This file is included so the RO-Crate has a concrete workflow file entity.
The executable implementation lives in router.pipeline.run_with_trace.
"""


def capas_costurero_workflow(workload):
    """Conceptual workflow stages recorded in the sealed RunTrace."""
    ingest(workload)
    record_runtime_context()
    estimate_cost_model()
    route_workload()
    execute_or_skip_backend()
    attach_physical_evidence()
'''


def _file_sha256_if_exists(path: str, base_dir: Path | None = None) -> str | None:
    p = Path(path)
    if not p.is_absolute() and base_dir is not None:
        p = base_dir / p
    if not p.exists():
        return None
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _strip_none(data: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in data.items() if v is not None}
