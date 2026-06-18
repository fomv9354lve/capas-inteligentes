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
    "trace_021": ("quantum_chemistry_experimental_reference", "present", True, "CompletedActionStatus"),
    "trace_022": ("quantum_chemistry_experimental_reference_improved_basis", "present", True, "CompletedActionStatus"),
    "trace_023": ("quantum_chemistry_experimental_reference_larger_basis", "present", True, "CompletedActionStatus"),
    "trace_024": ("quantum_chemistry_reference_definition_corrected", "present", True, "CompletedActionStatus"),
    "trace_025": ("quantum_chemistry_polyatomic_electronic_vibrational", "present", True, "CompletedActionStatus"),
    "trace_026": ("quantum_chemistry_larger_polyatomic_electronic_vibrational", "present", True, "CompletedActionStatus"),
    "trace_027": ("quantum_chemistry_basis_convergence_to_experiment", "present", True, "CompletedActionStatus"),
    "trace_028": ("universal_invariant_adversarial_failure", "present", True, "CompletedActionStatus"),
    "trace_029": ("universal_invariant_local_catches_anchor_not_needed", "present", True, "CompletedActionStatus"),
    "trace_030": ("universal_invariant_both_oracles_catch", "present", True, "CompletedActionStatus"),
    "trace_031": ("universal_invariant_non_heisenberg_adversarial_failure", "present", True, "CompletedActionStatus"),
    "trace_032": ("universal_invariant_no_anchor_control", "present", True, "CompletedActionStatus"),
    "trace_033": ("universal_invariant_scaling_law_adversarial_failure", "present", True, "CompletedActionStatus"),
    "trace_034": ("universal_invariant_scaling_law_positive_control", "present", True, "CompletedActionStatus"),
    "trace_035": ("universal_invariant_scaling_law_local_catches", "present", True, "CompletedActionStatus"),
    "trace_036": ("universal_invariant_scaling_law_simulation_generated", "present", True, "CompletedActionStatus"),
    "trace_012": ("no_evidence_success", "none_declared", False, "CompletedActionStatus"),
    "trace_013": ("backend_failed", "not_applicable_failed", False, "FailedActionStatus"),
    "trace_014": ("rejected_by_router", "not_applicable_rejected", False, "CompletedActionStatus"),
    "trace_015": ("estimated_bound_candidate", "present", True, "CompletedActionStatus"),
    "trace_016": ("formal_bound_success", "present", True, "CompletedActionStatus"),
    "trace_017": ("formal_bound_composition_success", "present", True, "CompletedActionStatus"),
}

RO_CRATE = "https://w3id.org/ro/crate/1.1"
PROCESS_RUN = "https://w3id.org/ro/wfrun/process/0.5"
WORKFLOW_RUN = "https://w3id.org/ro/wfrun/workflow/0.5"
WORKFLOW_RO_CRATE = "https://w3id.org/workflowhub/workflow-ro-crate/1.0"
CAPAS_PROFILE = "https://example.org/capas-inteligentes/ro-crate/physical-evidence/0.1"
CAPAS_WORKFLOW_ID = "workflow/capas-costurero-run.cwl"


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


def physical_evidence_node(crate: dict) -> dict:
    for node in crate.get("@graph", []):
        if node.get("@type") == "capas:PhysicalEvidence":
            return node
    raise AssertionError("missing PhysicalEvidence node")


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
            for profile in (RO_CRATE, PROCESS_RUN, WORKFLOW_RUN, WORKFLOW_RO_CRATE, CAPAS_PROFILE):
                assert any(item.get("@id") == profile for item in metadata_conforms), f"missing metadata conformance {profile}"
                assert any(item.get("@id") == profile for item in root_conforms), f"missing root conformance {profile}"
            assert root.get("mainEntity", {}).get("@id") == workflow.get("@id"), "root mainEntity does not point to workflow"
            assert root.get("mentions", {}).get("@id") == action.get("@id"), "root mentions does not point to run action"
            assert root.get("capas:evidenceStatus") == status, f"wrong evidenceStatus {root.get('capas:evidenceStatus')}"
            assert has_physical_evidence(crate) is evidence_expected, "wrong PhysicalEvidence presence"
            root_parts = ids(root.get("hasPart", []))
            assert CAPAS_WORKFLOW_ID in root_parts, "workflow not listed as crate part"
            assert "software:capas-costurero" in root_parts, "software not listed as crate part"
            assert "entity:workload" in root_parts, "workload not listed as crate part"
            assert workflow.get("input", {}).get("@id") == "parameter:workload", "workflow missing input parameter"
            assert workflow.get("output", {}).get("@id") == "parameter:result", "workflow missing output parameter"
            assert action.get("actionStatus") == action_status, f"wrong actionStatus {action.get('actionStatus')}"
            assert action.get("agent", {}).get("@id") == "software:capas-costurero", "run missing agent"
            assert action.get("instrument", {}).get("@id") == CAPAS_WORKFLOW_ID, "run missing workflow instrument"
            assert action.get("object", {}).get("@id") == "entity:workload", "run missing workload object"
            assert action.get("capas:evidenceStatus") == status, "run action missing evidenceStatus"
            report_path = CRATES / "ro_crate_export_report.json"
            report = json.loads(report_path.read_text(encoding="utf-8"))
            assert report[trace_id]["coverage_case"] == coverage, "wrong coverage_case"
            if coverage.startswith("universal_invariant_"):
                evidence = physical_evidence_node(crate)
                assert "capas:localPropertyTestsPass" in evidence, "missing local property result"
                assert "capas:localOracleCaught" in evidence, "missing local oracle caught result"
                assert evidence.get("capas:universalAnchor"), "missing universal anchor"
                assert "capas:universalAnchorPass" in evidence, "missing universal anchor result"
                assert "capas:invariantCaught" in evidence, "missing invariant caught result"
                assert evidence.get("capas:preRegisteredSuccessCriterion"), "missing pre-registered success criterion"
                assert evidence.get("capas:claimScope"), "missing claim scope"
            if coverage == "universal_invariant_adversarial_failure":
                assert evidence.get("capas:localPropertyTestsPass") is True, "local property tests did not pass"
                assert evidence.get("capas:localOracleCaught") is False, "local oracle should not catch this adversarial case"
                assert evidence.get("capas:universalAnchorPass") is False, "universal anchor should fail this adversarial case"
                assert evidence.get("capas:invariantCaught") is True, "invariant did not catch the adversarial case"
            elif coverage == "universal_invariant_local_catches_anchor_not_needed":
                assert evidence.get("capas:localPropertyTestsPass") is False, "local property tests should fail"
                assert evidence.get("capas:localOracleCaught") is True, "local oracle should catch this case"
                assert evidence.get("capas:universalAnchorPass") == "not_evaluated_local_oracle_failed", "universal anchor should not be needed"
                assert evidence.get("capas:invariantCaught") is False, "invariant should not be credited"
            elif coverage == "universal_invariant_both_oracles_catch":
                assert evidence.get("capas:localPropertyTestsPass") is False, "local property tests should fail"
                assert evidence.get("capas:localOracleCaught") is True, "local oracle should catch this case"
                assert evidence.get("capas:universalAnchorPass") is False, "universal anchor should fail this case"
                assert evidence.get("capas:invariantCaught") is True, "invariant should catch this case too"
            elif coverage == "universal_invariant_non_heisenberg_adversarial_failure":
                assert evidence.get("capas:localPropertyTestsPass") is True, "local property tests should pass"
                assert evidence.get("capas:localOracleCaught") is False, "local oracle should miss this case"
                assert evidence.get("capas:universalAnchorPass") is False, "Bell entropy anchor should fail this case"
                assert evidence.get("capas:invariantCaught") is True, "Bell entropy invariant should catch this case"
            elif coverage == "universal_invariant_no_anchor_control":
                assert evidence.get("capas:physicalEvidenceLevel") == "no_universal_anchor_control", "wrong no-anchor evidence level"
                assert evidence.get("capas:localPropertyTestsPass") is True, "local property tests should pass"
                assert evidence.get("capas:localOracleCaught") is False, "local oracle should not catch valid arbitrary state"
                assert evidence.get("capas:universalAnchorPass") == "not_applicable_no_universal_anchor", "anchor should be not applicable"
                assert evidence.get("capas:invariantCaught") is False, "no invariant should be credited"
            elif coverage == "universal_invariant_scaling_law_adversarial_failure":
                assert evidence.get("capas:physicalEvidenceLevel") == "scaling_law_anchor", "wrong scaling evidence level"
                assert evidence.get("capas:anchorKind") == "absolute_scaling_law", "wrong anchor kind"
                assert evidence.get("capas:localPropertyTestsPass") is True, "local scaling checks should pass"
                assert evidence.get("capas:universalAnchorPass") is False, "scaling anchor should fail"
                assert evidence.get("capas:invariantCaught") is True, "scaling invariant should catch"
                assert evidence.get("capas:absError") > evidence.get("capas:exponentTolerance"), "exponent error should exceed tolerance"
                assert len(evidence.get("capas:scalingPoints", [])) >= 5, "missing scaling points"
            elif coverage == "universal_invariant_scaling_law_positive_control":
                assert evidence.get("capas:physicalEvidenceLevel") == "scaling_law_anchor", "wrong scaling evidence level"
                assert evidence.get("capas:anchorKind") == "absolute_scaling_law", "wrong anchor kind"
                assert evidence.get("capas:localPropertyTestsPass") is True, "local scaling checks should pass"
                assert evidence.get("capas:universalAnchorPass") is True, "scaling anchor should pass"
                assert evidence.get("capas:invariantCaught") is False, "positive control should not be caught"
                assert evidence.get("capas:absError") <= evidence.get("capas:exponentTolerance"), "exponent error should be within tolerance"
                assert len(evidence.get("capas:scalingPoints", [])) >= 5, "missing scaling points"
            elif coverage == "universal_invariant_scaling_law_local_catches":
                assert evidence.get("capas:physicalEvidenceLevel") == "scaling_law_anchor", "wrong scaling evidence level"
                assert evidence.get("capas:anchorKind") == "absolute_scaling_law", "wrong anchor kind"
                assert evidence.get("capas:localPropertyTestsPass") is False, "local scaling checks should fail"
                assert evidence.get("capas:localOracleCaught") is True, "local oracle should catch constant sequence"
                assert evidence.get("capas:universalAnchorPass") == "not_evaluated_local_oracle_failed", "scaling anchor should not be credited"
                assert evidence.get("capas:invariantCaught") is False, "invariant should not be credited"
            elif coverage == "universal_invariant_scaling_law_simulation_generated":
                assert evidence.get("capas:physicalEvidenceLevel") == "scaling_law_anchor", "wrong scaling evidence level"
                assert evidence.get("capas:anchorKind") == "absolute_scaling_law", "wrong anchor kind"
                assert evidence.get("capas:localPropertyTestsPass") is True, "local scaling checks should pass"
                assert evidence.get("capas:universalAnchorPass") is True, "simulation-generated scaling anchor should pass"
                assert evidence.get("capas:invariantCaught") is False, "positive simulation control should not be caught"
                assert evidence.get("capas:absError") <= evidence.get("capas:exponentTolerance"), "exponent error should be within tolerance"
                assert len(evidence.get("capas:scalingPoints", [])) >= 5, "missing simulation scaling points"
                assert "Exact diagonalization" in evidence.get("capas:finiteSizeNotes", ""), "missing simulation provenance note"
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
