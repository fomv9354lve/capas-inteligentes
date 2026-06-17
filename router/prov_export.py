from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .trace import RunTrace, stable_hash


PROV_NS = "http://www.w3.org/ns/prov#"
CAPAS_NS = "https://example.org/capas-inteligentes#"


def run_trace_to_prov_json(trace: RunTrace, *, bundle_id: str | None = None) -> dict[str, Any]:
    """Export a RunTrace as a small PROV-shaped JSON document.

    This intentionally uses PROV's core vocabulary:
    - Entity: workload, decision, result, module/code, event metrics.
    - Activity: each trace event stage.
    - Agent: this router/costurero software.

    Domain-specific fields such as physical evidence are preserved as
    `capas:*` attributes. If those fields prove useful across projects,
    they should become a named PROV profile, not a replacement for PROV.
    """

    bid = bundle_id or f"capas:run:{trace.hash()[:16]}"
    workload_id = f"{bid}:workload"
    decision_id = f"{bid}:decision"
    result_id = f"{bid}:result"
    agent_id = "capas:agent:costurero"

    prov: dict[str, Any] = {
        "prefix": {
            "prov": PROV_NS,
            "capas": CAPAS_NS,
        },
        "bundle": bid,
        "entity": {
            workload_id: {
                "prov:type": "capas:Workload",
                "capas:workloadHash": trace.workload_hash,
                "capas:summary": trace.workload_summary,
            },
            decision_id: {
                "prov:type": "capas:RoutingDecision",
                "capas:route": trace.decision_route,
                "capas:reason": trace.decision_reason,
            },
        },
        "activity": {},
        "agent": {
            agent_id: {
                "prov:type": "prov:SoftwareAgent",
                "capas:name": "CAPAS INTELIGENTES costurero",
            }
        },
        "used": {},
        "wasGeneratedBy": {},
        "wasAssociatedWith": {},
        "wasDerivedFrom": {},
        "wasAttributedTo": {},
        "specializationOf": {},
    }

    if trace.result_hash is not None:
        prov["entity"][result_id] = {
            "prov:type": "capas:Result",
            "capas:resultHash": trace.result_hash,
            "capas:summary": trace.result_summary,
        }
        prov["wasDerivedFrom"][f"{result_id}:from:{workload_id}"] = {
            "prov:generatedEntity": result_id,
            "prov:usedEntity": workload_id,
        }
        prov["wasAttributedTo"][f"{result_id}:agent"] = {
            "prov:entity": result_id,
            "prov:agent": agent_id,
        }

    previous_entity = workload_id
    for idx, event in enumerate(trace.events):
        event_id = f"{bid}:activity:{idx}:{event.stage}"
        metrics_id = f"{bid}:entity:{idx}:{event.stage}:metrics"
        event_dict = asdict(event)
        prov["activity"][event_id] = {
            "prov:type": f"capas:{event.stage}",
            "capas:status": event.status,
            "capas:message": event.message,
            "capas:timestamp": event.timestamp,
        }
        prov["entity"][metrics_id] = {
            "prov:type": "capas:EventMetrics",
            "capas:stage": event.stage,
            "capas:metrics": event.metrics,
            "capas:eventHash": stable_hash(event_dict),
        }
        prov["used"][f"{event_id}:used:{previous_entity}"] = {
            "prov:activity": event_id,
            "prov:entity": previous_entity,
        }
        prov["wasGeneratedBy"][f"{metrics_id}:generatedBy:{event_id}"] = {
            "prov:entity": metrics_id,
            "prov:activity": event_id,
        }
        prov["wasAssociatedWith"][f"{event_id}:agent"] = {
            "prov:activity": event_id,
            "prov:agent": agent_id,
        }
        previous_entity = metrics_id

        if event.stage == "route":
            prov["wasGeneratedBy"][f"{decision_id}:generatedBy:{event_id}"] = {
                "prov:entity": decision_id,
                "prov:activity": event_id,
            }

        if event.stage == "engine_provenance":
            module_id = f"{bid}:engine_module"
            prov["entity"][module_id] = {
                "prov:type": "capas:EngineModule",
                "capas:engineId": event.metrics.get("engine_id"),
                "capas:modulePath": event.metrics.get("module_path"),
                "capas:moduleSha256": event.metrics.get("module_sha256"),
                "capas:functionName": event.metrics.get("function_name"),
            }
            prov["used"][f"{event_id}:used:{module_id}"] = {
                "prov:activity": event_id,
                "prov:entity": module_id,
            }

        if event.stage == "physical_evidence":
            evidence_id = f"{bid}:physical_evidence"
            prov["entity"][evidence_id] = {
                "prov:type": "capas:PhysicalEvidence",
                "capas:physicalEvidenceLevel": event.metrics.get("physical_evidence_level"),
                "capas:physicalEvidenceDetail": event.metrics.get("physical_evidence_detail"),
                "capas:observable": event.metrics.get("observable"),
                "capas:units": event.metrics.get("units"),
                "capas:absError": event.metrics.get("abs_error"),
                "capas:expected": event.metrics.get("expected"),
                "capas:value": event.metrics.get("value"),
                "capas:benchmarkFamily": event.metrics.get("benchmark_family"),
                "capas:referenceTruth": event.metrics.get("reference_truth"),
                "capas:verificationIndependence": event.metrics.get("verification_independence"),
                "capas:witnessStack": event.metrics.get("witness_stack"),
                "capas:certificationStatus": event.metrics.get("certification_status"),
                "capas:formalBoundStatus": event.metrics.get("formal_bound_status"),
                "capas:sourceLabel": event.metrics.get("source_label"),
                "capas:discardedWeight": event.metrics.get("discarded_weight"),
                "capas:actualErrorSquared": event.metrics.get("actual_error_squared"),
                "capas:composedStateErrorBound": event.metrics.get("composed_state_error_bound"),
                "capas:boundSlack": event.metrics.get("bound_slack"),
                "capas:boundType": event.metrics.get("bound_type"),
                "capas:boundScope": event.metrics.get("bound_scope"),
                "capas:evidenceHash": event.metrics.get("evidence_hash"),
            }
            prov["wasGeneratedBy"][f"{evidence_id}:generatedBy:{event_id}"] = {
                "prov:entity": evidence_id,
                "prov:activity": event_id,
            }
            if trace.result_hash is not None:
                prov["wasDerivedFrom"][f"{evidence_id}:from:{result_id}"] = {
                    "prov:generatedEntity": evidence_id,
                    "prov:usedEntity": result_id,
                }

    if trace.result_hash is not None:
        execute_events = [
            f"{bid}:activity:{idx}:{event.stage}"
            for idx, event in enumerate(trace.events)
            if event.stage == "execute" and event.status == "ok"
        ]
        if execute_events:
            prov["wasGeneratedBy"][f"{result_id}:generatedBy:{execute_events[-1]}"] = {
                "prov:entity": result_id,
                "prov:activity": execute_events[-1],
            }

    prov["capas:traceHash"] = trace.hash()
    return prov


def classify_prov_mapping(trace: RunTrace) -> dict[str, Any]:
    """Explain what is standard PROV vs a domain-specific CAPAS profile."""

    has_physical_evidence = False
    evidence_levels: list[str] = []
    if trace.result_summary:
        level = trace.result_summary.get("physical_evidence_level")
        if level:
            has_physical_evidence = True
            evidence_levels.append(str(level))
    for event in trace.events:
        metrics = event.metrics or {}
        nested = [metrics]
        result = metrics.get("result")
        if isinstance(result, dict):
            nested.append(result)
        for item in nested:
            level = item.get("physical_evidence_level") if isinstance(item, dict) else None
            if level:
                has_physical_evidence = True
                evidence_levels.append(str(level))

    return {
        "standard_prov_covers": [
            "workload/result/module as entities",
            "ingest/cost_model/route/execute as activities",
            "costurero as software agent",
            "used, wasGeneratedBy, wasDerivedFrom, wasAssociatedWith relations",
        ],
        "capas_profile_needed_for": [
            "routing decision semantics",
            "cost-model metrics and frontier estimates",
            "physical evidence level and domain correctness claims",
            "trace hash policy and audit decisions",
        ],
        "formal_novelty_assessment": (
            "RunTrace does not require a replacement for PROV. It fits PROV as a domain profile. "
            "The product contribution is the CAPAS profile and workflow that binds routing, "
            "engine provenance, and physical-evidence auditing into one sealed trace."
        ),
        "physical_evidence_found_in_trace_events": has_physical_evidence,
        "physical_evidence_levels": sorted(set(evidence_levels)),
    }
