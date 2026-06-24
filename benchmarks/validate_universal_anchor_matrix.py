# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""Validate the D11 local-oracle vs universal-anchor matrix.

This is the executable guard against turning the D11 traces into a dominance
claim. The matrix asks a narrower question:

    Do absolute universal anchors add detection coverage that local checks miss,
    while also admitting cases where local checks are sufficient or both pass?

If all four main cells are represented, the licensed claim is complementarity,
not universal superiority over local/property/metamorphic testing.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TRACE_DIR = ROOT / "benchmarks" / "gold_traces"
REPORT_PATH = ROOT / "benchmarks" / "universal_anchor_matrix_report.json"

D11_TRACE_RANGE = range(28, 40)

REQUIRED_CELLS = {
    "local_miss_anchor_catch",
    "local_catch_anchor_not_needed",
    "both_catch",
    "both_pass",
    "no_anchor_control",
}


def _load_trace(trace_id: str) -> dict[str, Any]:
    path = TRACE_DIR / f"{trace_id}.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    result = payload.get("result")
    if not result:
        raise AssertionError(f"{trace_id}: missing result")
    return result["result"]


def _anchor_caught(trace: dict[str, Any]) -> bool:
    if trace.get("invariant_caught") is True:
        return True
    return trace.get("universal_anchor_pass") is False


def _cell(trace: dict[str, Any]) -> str:
    anchor_mode = trace.get("anchor_mode")
    if anchor_mode == "none":
        return "no_anchor_control"
    if anchor_mode != "absolute_anchor":
        return "not_d11_absolute_anchor"

    local_caught = trace.get("local_oracle_caught") is True
    anchor_pass = trace.get("universal_anchor_pass")
    anchor_caught = _anchor_caught(trace)

    if local_caught and anchor_caught:
        return "both_catch"
    if local_caught and isinstance(anchor_pass, str) and anchor_pass.startswith("not_evaluated"):
        return "local_catch_anchor_not_needed"
    if local_caught and not anchor_caught:
        return "local_catch_anchor_not_needed"
    if not local_caught and anchor_caught:
        return "local_miss_anchor_catch"
    if not local_caught and anchor_pass is True:
        return "both_pass"
    return "unclassified"


def main() -> int:
    cells: dict[str, list[str]] = defaultdict(list)
    trace_rows: list[dict[str, Any]] = []

    for trace_num in D11_TRACE_RANGE:
        trace_id = f"trace_{trace_num:03d}"
        trace = _load_trace(trace_id)
        coverage_case = trace.get("coverage_case", "")
        if not (
            coverage_case.startswith("universal_invariant_")
            or coverage_case == "claim_transition_bounded_agent_scientific_reasoning"
        ):
            continue
        cell = _cell(trace)
        cells[cell].append(trace_id)
        trace_rows.append({
            "trace_id": trace_id,
            "coverage_case": coverage_case,
            "cell": cell,
            "anchor_mode": trace.get("anchor_mode"),
            "local_property_tests_pass": trace.get("local_property_tests_pass"),
            "local_oracle_caught": trace.get("local_oracle_caught"),
            "universal_anchor_pass": trace.get("universal_anchor_pass"),
            "invariant_caught": trace.get("invariant_caught"),
            "benchmark_family": trace.get("benchmark_family"),
            "agent_kind": trace.get("agent_kind", "not_agent_trace"),
            "claim_scope": trace.get("claim_scope"),
        })

    missing = sorted(REQUIRED_CELLS - set(cells))
    marginal_anchor_detection = cells.get("local_miss_anchor_catch", [])
    local_sufficient_controls = cells.get("local_catch_anchor_not_needed", [])
    redundant_detection_controls = cells.get("both_catch", [])
    positive_controls = cells.get("both_pass", [])
    no_anchor_controls = cells.get("no_anchor_control", [])

    licensed_claim = (
        "complementarity_not_dominance"
        if not missing
        and marginal_anchor_detection
        and local_sufficient_controls
        and redundant_detection_controls
        and positive_controls
        and no_anchor_controls
        else "insufficient_matrix_coverage"
    )

    report = {
        "matrix_status": "passed" if not missing else "failed",
        "licensed_claim": licensed_claim,
        "forbidden_claims": [
            "universal anchors dominate local/property/metamorphic testing",
            "local tests imply universal physical correctness",
            "D11 proves benchmark-level LLM-agent utility",
        ],
        "allowed_claim": (
            "Across the current D11 traces, absolute universal anchors add "
            "coverage in some locally plausible failures, while local checks "
            "remain sufficient or redundant in other cells. The evidence "
            "licenses complementarity, not dominance."
        ),
        "required_cells": sorted(REQUIRED_CELLS),
        "missing_cells": missing,
        "cell_counts": {cell: len(ids) for cell, ids in sorted(cells.items())},
        "cells": {cell: ids for cell, ids in sorted(cells.items())},
        "marginal_anchor_detection_count": len(marginal_anchor_detection),
        "local_sufficient_control_count": len(local_sufficient_controls),
        "redundant_detection_control_count": len(redundant_detection_controls),
        "positive_control_count": len(positive_controls),
        "no_anchor_control_count": len(no_anchor_controls),
        "trace_rows": trace_rows,
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    if missing:
        print(f"universal anchor matrix failed; missing cells: {', '.join(missing)}")
        print(f"report written to {REPORT_PATH}")
        return 1

    print("universal anchor matrix passed")
    print(f"licensed_claim: {licensed_claim}")
    print(f"cell_counts: {report['cell_counts']}")
    print(f"report written to {REPORT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
