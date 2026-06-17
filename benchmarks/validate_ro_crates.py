from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CRATES = ROOT / "benchmarks" / "ro_crates"


EXPECTED = {
    "trace_001": ("analytic_success", "present", True),
    "trace_011": ("cross_sim_success", "present", True),
    "trace_012": ("no_evidence_success", "none_declared", True),
    "trace_013": ("backend_failed", "not_applicable_failed", False),
    "trace_014": ("rejected_by_router", "not_applicable_rejected", False),
    "trace_015": ("estimated_bound_candidate", "present", True),
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


def main() -> int:
    failures = []
    for trace_id, (coverage, status, evidence_expected) in EXPECTED.items():
        try:
            crate = load_crate(trace_id)
            assert "@context" in crate, "missing @context"
            assert "@graph" in crate, "missing @graph"
            root = root_node(crate)
            metadata = metadata_node(crate)
            metadata_conforms = metadata.get("conformsTo", [])
            root_conforms = root.get("conformsTo", [])
            assert any(item.get("@id") == "https://w3id.org/ro/crate/1.1" for item in metadata_conforms), "missing RO-Crate conformance"
            assert any(item.get("@id") == "https://example.org/capas-inteligentes/ro-crate/physical-evidence/0.1" for item in root_conforms), "missing CAPAS profile conformance"
            assert root.get("capas:evidenceStatus") == status, f"wrong evidenceStatus {root.get('capas:evidenceStatus')}"
            assert has_physical_evidence(crate) is evidence_expected, "wrong PhysicalEvidence presence"
            report_path = CRATES / "ro_crate_export_report.json"
            report = json.loads(report_path.read_text(encoding="utf-8"))
            assert report[trace_id]["coverage_case"] == coverage, "wrong coverage_case"
            print(f"{trace_id}: ok ({coverage}, {status})")
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
