from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .prov_export import run_trace_to_prov_json
from .trace import RunTrace, stable_hash


RO_CRATE_CONTEXT = "https://w3id.org/ro/crate/1.1/context"
RO_CRATE_CONFORMS_TO = "https://w3id.org/ro/crate/1.1"
WORKFLOW_RUN_CRATE_PROFILE = "https://w3id.org/workflowhub/workflow-ro-crate/1.0"
CAPAS_PROFILE = "https://example.org/capas-inteligentes/ro-crate/physical-evidence/0.1"


def run_trace_to_ro_crate_metadata(
    trace: RunTrace,
    *,
    trace_file: str,
    prov_file: str | None = None,
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

    graph: list[dict[str, Any]] = [
        {
            "@id": "ro-crate-metadata.json",
            "@type": "CreativeWork",
            "conformsTo": [
                {"@id": RO_CRATE_CONFORMS_TO},
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
            "hasPart": [{"@id": trace_file}],
            "conformsTo": [
                {"@id": WORKFLOW_RUN_CRATE_PROFILE},
                {"@id": CAPAS_PROFILE},
            ],
            "capas:traceHash": trace.hash(),
            "capas:workloadHash": trace.workload_hash,
        },
        {
            "@id": trace_file,
            "@type": ["File", "DigitalDocument"],
            "name": "Sealed CAPAS RunTrace",
            "encodingFormat": "application/json",
            "sha256": _file_sha256_if_exists(trace_file),
            "about": {"@id": trace_id},
        },
        {
            "@id": trace_id,
            "@type": "CreateAction",
            "name": "CAPAS costurero traced run",
            "instrument": {"@id": "software:capas-costurero"},
            "object": {"@id": "entity:workload"},
            "result": {"@id": result_id} if trace.result_hash else None,
            "capas:routingDecision": {"@id": decision_id},
            "capas:traceHash": trace.hash(),
            "capas:traceSchemaVersion": trace.trace_schema_version,
            "capas:hashAlgorithm": trace.hash_algorithm,
            "capas:error": trace.error,
        },
        {
            "@id": "software:capas-costurero",
            "@type": "SoftwareApplication",
            "name": "CAPAS INTELIGENTES costurero",
            "applicationCategory": "Scientific provenance and evidence tracing",
        },
        {
            "@id": "entity:workload",
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
                "sha256": _file_sha256_if_exists(prov_file),
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
            break
    if evidence:
        graph.append(
            {
                "@id": evidence_id,
                "@type": "capas:PhysicalEvidence",
                "name": "Physical evidence attached to result",
                "capas:physicalEvidenceLevel": evidence.get("physical_evidence_level"),
                "capas:verificationIndependence": evidence.get("verification_independence"),
                "capas:referenceTruth": evidence.get("reference_truth"),
                "capas:benchmarkFamily": evidence.get("benchmark_family"),
                "capas:observable": evidence.get("observable"),
                "capas:expected": evidence.get("expected"),
                "capas:value": evidence.get("value"),
                "capas:absError": evidence.get("abs_error"),
                "capas:units": evidence.get("units"),
                "capas:detail": evidence.get("physical_evidence_detail"),
                "capas:certificationStatus": evidence.get("certification_status"),
                "capas:sourceLabel": evidence.get("source_label"),
                "capas:evidenceHash": stable_hash(evidence),
                "about": {"@id": result_id},
            }
        )
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
    trace_path = out_dir / "runtrace.json"
    prov_path = out_dir / "runtrace.prov.json"
    crate_path = out_dir / "ro-crate-metadata.json"

    trace_path.write_text(json.dumps(trace_payload, indent=2, sort_keys=True), encoding="utf-8")
    prov_path.write_text(json.dumps(run_trace_to_prov_json(trace), indent=2, sort_keys=True), encoding="utf-8")
    crate = run_trace_to_ro_crate_metadata(
        trace,
        trace_file="runtrace.json",
        prov_file="runtrace.prov.json",
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


def _file_sha256_if_exists(path: str) -> str | None:
    p = Path(path)
    if not p.exists():
        return None
    return stable_hash(p.read_bytes().hex())


def _strip_none(data: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in data.items() if v is not None}
