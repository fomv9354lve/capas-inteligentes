from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CRATES = ROOT / "benchmarks" / "ro_crates"

RO_CRATE = "https://w3id.org/ro/crate/1.1"
PROCESS_RUN = "https://w3id.org/ro/wfrun/process/0.5"
WORKFLOW_RUN = "https://w3id.org/ro/wfrun/workflow/0.5"
WORKFLOW_RO_CRATE = "https://w3id.org/workflowhub/workflow-ro-crate/1.0"
CAPAS_PROFILE = "https://example.org/capas-inteligentes/ro-crate/physical-evidence/0.1"

PRESENT_EVIDENCE_REQUIRED = {
    "physicalEvidenceLevel": "capas:physicalEvidenceLevel",
    "verificationIndependence": "capas:verificationIndependence",
    "referenceTruth": "capas:referenceTruth",
}

ALLOWED_EVIDENCE_STATUS = {
    "present",
    "none_declared",
    "not_applicable_failed",
    "not_applicable_rejected",
}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _type_contains(node: dict[str, Any], expected: str) -> bool:
    node_type = node.get("@type")
    if isinstance(node_type, list):
        return expected in node_type
    return node_type == expected


def _node(crate: dict[str, Any], node_id: str) -> dict[str, Any]:
    for node in crate.get("@graph", []):
        if node.get("@id") == node_id:
            return node
    raise AssertionError(f"missing node {node_id}")


def _nodes_of_type(crate: dict[str, Any], expected: str) -> list[dict[str, Any]]:
    return [node for node in crate.get("@graph", []) if _type_contains(node, expected)]


def _ids(value: Any) -> set[str]:
    if isinstance(value, dict):
        value = [value]
    if not isinstance(value, list):
        return set()
    return {item.get("@id") for item in value if isinstance(item, dict) and item.get("@id")}


def _conforms_to(node: dict[str, Any]) -> set[str]:
    return _ids(node.get("conformsTo"))


def _validate_crate(crate_dir: Path) -> list[str]:
    failures: list[str] = []
    crate = _load(crate_dir / "ro-crate-metadata.json")

    try:
        context = crate.get("@context", [])
        if "https://w3id.org/ro/crate/1.1/context" not in context:
            failures.append("missing RO-Crate context")
        if "https://w3id.org/ro/terms/workflow-run/context" not in context:
            failures.append("missing Workflow Run context")
        if not any(isinstance(item, dict) and "capas" in item for item in context):
            failures.append("missing CAPAS JSON-LD context")

        metadata = _node(crate, "ro-crate-metadata.json")
        root = _node(crate, "./")
        workflow_nodes = _nodes_of_type(crate, "ComputationalWorkflow")
        action_nodes = _nodes_of_type(crate, "CreateAction")

        if len(workflow_nodes) != 1:
            failures.append(f"expected one ComputationalWorkflow, found {len(workflow_nodes)}")
        if len(action_nodes) != 1:
            failures.append(f"expected one CreateAction run, found {len(action_nodes)}")
        if not workflow_nodes or not action_nodes:
            return failures

        workflow = workflow_nodes[0]
        action = action_nodes[0]

        for profile in (RO_CRATE, PROCESS_RUN, WORKFLOW_RUN, WORKFLOW_RO_CRATE, CAPAS_PROFILE):
            if profile not in _conforms_to(metadata):
                failures.append(f"metadata missing conformsTo {profile}")
            if profile not in _conforms_to(root):
                failures.append(f"root missing conformsTo {profile}")
        for profile in (PROCESS_RUN, WORKFLOW_RUN, WORKFLOW_RO_CRATE, CAPAS_PROFILE):
            try:
                profile_node = _node(crate, profile)
                if not _type_contains(profile_node, "CreativeWork"):
                    failures.append(f"profile node {profile} is not CreativeWork")
            except AssertionError:
                failures.append(f"missing profile CreativeWork node {profile}")

        if root.get("mainEntity", {}).get("@id") != workflow.get("@id"):
            failures.append("root mainEntity does not point to ComputationalWorkflow")
        if root.get("mentions", {}).get("@id") != action.get("@id"):
            failures.append("root mentions does not point to CreateAction run")
        if action.get("instrument", {}).get("@id") != workflow.get("@id"):
            failures.append("CreateAction instrument does not point to workflow")
        if action.get("object", {}).get("@id") != "entity:workload":
            failures.append("CreateAction object does not point to workload")
        if action.get("actionStatus") not in {"CompletedActionStatus", "FailedActionStatus"}:
            failures.append("CreateAction has unsupported actionStatus")

        workload = _node(crate, "entity:workload")
        if workload.get("exampleOfWork", {}).get("@id") != "parameter:workload":
            failures.append("workload does not realize parameter:workload")
        parameter_workload = _node(crate, "parameter:workload")
        parameter_result = _node(crate, "parameter:result")
        if not _type_contains(parameter_workload, "FormalParameter"):
            failures.append("parameter:workload is not FormalParameter")
        if not _type_contains(parameter_result, "FormalParameter"):
            failures.append("parameter:result is not FormalParameter")
        if not parameter_workload.get("additionalType"):
            failures.append("parameter:workload missing additionalType")
        if not parameter_result.get("additionalType"):
            failures.append("parameter:result missing additionalType")

        evidence_status = root.get("capas:evidenceStatus")
        if evidence_status not in ALLOWED_EVIDENCE_STATUS:
            failures.append(f"unsupported root evidenceStatus {evidence_status!r}")
        if action.get("capas:evidenceStatus") != evidence_status:
            failures.append("CreateAction evidenceStatus does not match root")

        evidence_nodes = [node for node in crate.get("@graph", []) if node.get("@type") == "capas:PhysicalEvidence"]
        if evidence_status == "present":
            if len(evidence_nodes) != 1:
                failures.append(f"expected one PhysicalEvidence node, found {len(evidence_nodes)}")
            else:
                evidence = evidence_nodes[0]
                for label, key in PRESENT_EVIDENCE_REQUIRED.items():
                    if key not in evidence:
                        failures.append(f"PhysicalEvidence missing {label}")
                result_id = action.get("result", {}).get("@id")
                if result_id:
                    result = _node(crate, result_id)
                    if result.get("exampleOfWork", {}).get("@id") != "parameter:result":
                        failures.append("result does not realize parameter:result")
                    if result.get("capas:physicalEvidence", {}).get("@id") != evidence.get("@id"):
                        failures.append("result does not point to PhysicalEvidence")
                    if evidence.get("about", {}).get("@id") != result_id:
                        failures.append("PhysicalEvidence about does not point to result")
        elif evidence_nodes:
            failures.append(f"non-present evidenceStatus has PhysicalEvidence nodes: {len(evidence_nodes)}")

        if evidence_status == "not_applicable_failed" and action.get("actionStatus") != "FailedActionStatus":
            failures.append("failed evidenceStatus must use FailedActionStatus")
        if evidence_status == "not_applicable_rejected" and action.get("capas:decisionRoute") not in {
            "QPU_REQUIRED",
            "TENSOR_REQUIRED",
            "TENSOR_TOO_SLOW",
        }:
            failures.append("rejected evidenceStatus must record a rejection route")

    except Exception as exc:
        failures.append(f"{type(exc).__name__}: {exc}")
    return failures


def main() -> int:
    failures: list[str] = []
    crate_dirs = sorted(path for path in CRATES.iterdir() if path.is_dir() and path.name.startswith("trace_"))
    for crate_dir in crate_dirs:
        crate_failures = _validate_crate(crate_dir)
        if crate_failures:
            failures.extend(f"{crate_dir.name}: {failure}" for failure in crate_failures)
        else:
            print(f"{crate_dir.name}: CAPAS profile ok")

    if failures:
        print("CAPAS profile validation failures:")
        for failure in failures:
            print(f"  {failure}")
        return 1
    print(f"validate_capas_profile passed ({len(crate_dirs)} crates)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
