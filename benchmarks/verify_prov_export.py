from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from router.prov_export import classify_prov_mapping, run_trace_to_prov_json  # noqa: E402
from router.trace import RunTrace, TraceEvent  # noqa: E402


def _trace_from_dict(data: dict) -> RunTrace:
    trace_data = data["trace"] if "trace" in data else data
    trace = RunTrace(
        workload_hash=trace_data["workload_hash"],
        workload_summary=trace_data["workload_summary"],
        decision_route=trace_data.get("decision_route"),
        decision_reason=trace_data.get("decision_reason"),
        result_hash=trace_data.get("result_hash"),
        result_summary=trace_data.get("result_summary"),
        error=trace_data.get("error"),
    )
    for event in trace_data["events"]:
        trace.events.append(
            TraceEvent(
                stage=event["stage"],
                status=event["status"],
                metrics=event.get("metrics", {}),
                message=event.get("message", ""),
                timestamp=event.get("timestamp", 0.0),
            )
        )
    return trace


def main() -> None:
    source = ROOT / "benchmarks" / "gold_traces" / "trace_001.json"
    trace = _trace_from_dict(json.loads(source.read_text(encoding="utf-8")))
    prov = run_trace_to_prov_json(trace)
    classification = classify_prov_mapping(trace)

    assert prov["prefix"]["prov"] == "http://www.w3.org/ns/prov#"
    assert prov["entity"]
    assert prov["activity"]
    assert prov["agent"]
    assert prov["used"]
    assert prov["wasGeneratedBy"]
    assert prov["capas:traceHash"] == trace.hash()
    assert "RoutingDecision" in json.dumps(prov)
    assert "PhysicalEvidence" in json.dumps(prov)
    assert classification["physical_evidence_found_in_trace_events"] is True
    assert classification["physical_evidence_levels"] == ["analytic"]

    out = ROOT / "benchmarks" / "gold_traces" / "trace_001.prov.json"
    out.write_text(json.dumps(prov, indent=2, sort_keys=True), encoding="utf-8")
    report = ROOT / "benchmarks" / "prov_mapping_report.json"
    report.write_text(json.dumps(classification, indent=2, sort_keys=True), encoding="utf-8")
    print("verify_prov_export passed")
    print(json.dumps(classification, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
