from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CRATES = ROOT / "benchmarks" / "ro_crates"


EXPECTED = {
    "trace_001": ("analytic_success", "present", True, "CompletedActionStatus"),
    "trace_011": ("cross_sim_success", "present", True, "CompletedActionStatus"),
    "trace_018": ("cross_library_success", "present", True, "CompletedActionStatus"),
    "trace_019": ("combinatorial_optimization_function_level", "present", True, "CompletedActionStatus"),
    "trace_020": ("combinatorial_optimization_degenerate_function_level", "present", True, "CompletedActionStatus"),
    "trace_012": ("no_evidence_success", "none_declared", True, "CompletedActionStatus"),
    "trace_013": ("backend_failed", "not_applicable_failed", False, "FailedActionStatus"),
    "trace_014": ("rejected_by_router", "not_applicable_rejected", False, "CompletedActionStatus"),
    "trace_015": ("estimated_bound_candidate", "present", True, "CompletedActionStatus"),
    "trace_016": ("formal_bound_success", "present", True, "CompletedActionStatus"),
    "trace_017": ("formal_bound_composition_success", "present", True, "CompletedActionStatus"),
}


def load_crate(trace_id: str) -> dict:
    path = CRATES / trace_id / "ro-crate-metadata.json"
    if not path.exists():
        raise AssertionError(f"missing {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def root_node(crate: dict) -> dict:
    for node in crate.get("@graph", []):
        if node.get("@id") == "./":
            return node
    raise AssertionError("missing root dataset node")


def metadata_node(crate: dict) -> dict:
    for node in crate.get("@graph", []):
        if node.get("@id") == "ro-crate-metadata.json":
            return node
    raise AssertionError("missing ro-crate-metadata.json node")


def has_physical_evidence(crate: dict) -> bool:
    return any(node.get("@type") == "capas:PhysicalEvidence" for node in crate.get("@graph", []))


def type_contains(node: dict, expected: str) -> bool:
    node_type = node.get("@type")
    if isinstance(node_type, list):
        return expected in node_type
    return node_type == expected


def workflow_node(crate: dict) -> dict:
    for node in crate.get("@graph", []):
        if type_contains(node, "ComputationalWorkflow"):
            return node
    raise AssertionError("missing ComputationalWorkflow node")


def create_action_node(crate: dict) -> dict:
    for node in crate.get("@graph", []):
        if type_contains(node, "CreateAction"):
            return node
    raise AssertionError("missing CreateAction run node")


def ids(items: list[dict]) -> set[str]:
    return {item.get("@id") for item in items if isinstance(item, dict)}


def main() -> int:
    failures = []
    for trace_id, (coverage, status, evidence_expected, action_status) in EXPECTED.items():
        try:
            crate = load_crate(trace_id)
            assert "@context" in crate, "missing @context"
            assert "@graph" in crate, "missing @graph"
            root = root_node(crate)
            metadata = metadata_node(crate)
            workflow = workflow_node(crate)
            action = create_action_node(crate)
            metadata_conforms = metadata.get("conformsTo", [])
            root_conforms = root.get("conformsTo", [])
            assert any(item.get("@id") == "https://w3id.org/ro/crate/1.1" for item in metadata_conforms), "missing RO-Crate conformance"
            assert any(item.get("@id") == "https://w3id.org/workflowhub/workflow-ro-crate/1.0" for item in metadata_conforms), "missing Workflow Run RO-Crate metadata conformance"
            assert any(item.get("@id") == "https://w3id.org/ro/crate/1.1" for item in root_conforms), "missing root RO-Crate conformance"
            assert any(item.get("@id") == "https://w3id.org/workflowhub/workflow-ro-crate/1.0" for item in root_conforms), "missing root Workflow Run RO-Crate conformance"
            assert any(item.get("@id") == "https://example.org/capas-inteligentes/ro-crate/physical-evidence/0.1" for item in root_conforms), "missing CAPAS profile conformance"
            assert root.get("capas:evidenceStatus") == status, f"wrong evidenceStatus {root.get('capas:evidenceStatus')}"
            assert has_physical_evidence(crate) is evidence_expected, "wrong PhysicalEvidence presence"
            root_parts = ids(root.get("hasPart", []))
            assert "workflow/capas-costurero-run.py" in root_parts, "workflow not listed as crate part"
            assert "software:capas-costurero" in root_parts, "software not listed as crate part"
            assert "entity:workload" in root_parts, "workload not listed as crate part"
            assert workflow.get("input", {}).get("@id") == "parameter:workload", "workflow missing input parameter"
            assert workflow.get("output", {}).get("@id") == "parameter:result", "workflow missing output parameter"
            assert action.get("actionStatus") == action_status, f"wrong actionStatus {action.get('actionStatus')}"
            assert action.get("agent", {}).get("@id") == "software:capas-costurero", "run missing agent"
            assert action.get("instrument", {}).get("@id") == "workflow/capas-costurero-run.py", "run missing workflow instrument"
            assert action.get("object", {}).get("@id") == "entity:workload", "run missing workload object"
            assert action.get("capas:evidenceStatus") == status, "run action missing evidenceStatus"
            report_path = CRATES / "ro_crate_export_report.json"
            report = json.loads(report_path.read_text(encoding="utf-8"))
            assert report[trace_id]["coverage_case"] == coverage, "wrong coverage_case"
            print(f"{trace_id}: ok ({coverage}, {status}, {action_status})")
        except Exception as exc:
            failures.append(f"{trace_id}: {type(exc).__name__}: {exc}")
    if failures:
        print("RO-Crate validation failures:")
        for failure in failures:
            print(f"  {failure}")
        return 1
    print("validate_ro_crates passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
