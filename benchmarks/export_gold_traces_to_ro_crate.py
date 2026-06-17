from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from benchmarks.verify_prov_export import _trace_from_dict  # noqa: E402
from router.ro_crate_export import write_ro_crate_for_trace  # noqa: E402


def _has_physical_evidence(crate: dict) -> bool:
    return any(node.get("@type") == "capas:PhysicalEvidence" for node in crate.get("@graph", []))


def main() -> None:
    traces_dir = ROOT / "benchmarks" / "gold_traces"
    crates_dir = ROOT / "benchmarks" / "ro_crates"
    crates_dir.mkdir(parents=True, exist_ok=True)
    report: dict[str, dict] = {}

    for path in sorted(traces_dir.glob("trace_*.json")):
        if path.name.endswith(".prov.json"):
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        trace = _trace_from_dict(data)
        trace_id = data["trace_id"]
        crate_dir = crates_dir / trace_id
        crate_path = write_ro_crate_for_trace(trace, crate_dir, trace_payload=data)
        crate = json.loads(crate_path.read_text(encoding="utf-8"))
        report[trace_id] = {
            "coverage_case": data.get("coverage_case"),
            "decision_route": trace.decision_route,
            "error": trace.error,
            "crate_path": str(crate_path),
            "has_physical_evidence_entity": _has_physical_evidence(crate),
            "conforms_to": crate["@graph"][0].get("conformsTo"),
        }

    report_path = crates_dir / "ro_crate_export_report.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(f"exported {len(report)} RO-Crates")
    print(report_path)


if __name__ == "__main__":
    main()
