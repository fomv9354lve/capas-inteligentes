# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from benchmarks.verify_prov_export import _trace_from_dict  # noqa: E402
from router.prov_export import classify_prov_mapping, run_trace_to_prov_json  # noqa: E402


def main() -> None:
    out_dir = ROOT / "benchmarks" / "gold_traces"
    report = {}
    for path in sorted(out_dir.glob("trace_*.json")):
        if path.name.endswith(".prov.json"):
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        trace = _trace_from_dict(data)
        prov = run_trace_to_prov_json(trace)
        prov_path = path.with_suffix(".prov.json")
        prov_path.write_text(json.dumps(prov, indent=2, sort_keys=True), encoding="utf-8")
        report[data["trace_id"]] = {
            "coverage_case": data.get("coverage_case"),
            "decision_route": trace.decision_route,
            "error": trace.error,
            "prov_path": str(prov_path),
            "mapping": classify_prov_mapping(trace),
        }
    report_path = out_dir / "prov_export_report.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(f"exported {len(report)} PROV traces")
    print(report_path)


if __name__ == "__main__":
    main()
