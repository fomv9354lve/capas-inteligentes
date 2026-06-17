from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT_CSV = ROOT / "audits" / "gold_trace_audit_template.csv"
REPORT = ROOT / "benchmarks" / "witness_independence_report.json"


INDEPENDENCE_LEVELS = {
    "analytic_no_solver": {
        "strength": 5,
        "description": "Closed-form reference; no computational witness required.",
    },
    "different_library_same_runtime": {
        "strength": 4,
        "description": "Independent library witness in the same Python/runtime process.",
    },
    "different_method_same_runtime": {
        "strength": 4,
        "description": "Different computational method in the same Python/runtime process.",
    },
    "same_runtime_exact_fci_with_external_experimental_reference": {
        "strength": 4,
        "description": "Exact same-runtime model solve compared with an external experimental reference.",
    },
    "different_algorithm_same_runtime": {
        "strength": 3,
        "description": "Different algorithmic calculation in the same runtime/library family.",
    },
    "algorithmic_certificate_exact_svd_same_runtime": {
        "strength": 3,
        "description": "Formal same-runtime mathematical certificate, not an independent witness.",
    },
    "algorithmic_error_certificate_same_runtime": {
        "strength": 2,
        "description": "Same-runtime algorithmic error estimate or non-formal certificate.",
    },
    "none": {
        "strength": 0,
        "description": "No witness or certificate attached.",
    },
}


REQUIRED_COVERAGE = {
    "analytic_no_solver",
    "different_library_same_runtime",
    "different_method_same_runtime",
    "same_runtime_exact_fci_with_external_experimental_reference",
    "different_algorithm_same_runtime",
    "algorithmic_certificate_exact_svd_same_runtime",
    "algorithmic_error_certificate_same_runtime",
    "none",
}


def _rows() -> list[dict[str, str]]:
    with AUDIT_CSV.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main() -> int:
    rows = _rows()
    failures: list[str] = []
    levels = Counter()
    by_level: dict[str, list[str]] = {}

    for row in rows:
        trace_id = row.get("trace_id", "")
        if not trace_id:
            continue
        level = (row.get("verification_independence") or "").strip()
        if not level:
            failures.append(f"{trace_id}: missing verification_independence")
            continue
        if level not in INDEPENDENCE_LEVELS:
            failures.append(f"{trace_id}: unknown verification_independence={level!r}")
            continue
        levels[level] += 1
        by_level.setdefault(level, []).append(trace_id)

    missing = sorted(REQUIRED_COVERAGE - set(levels))
    if missing:
        failures.append(f"missing required independence coverage: {missing}")

    report = {
        "schema": "capas-witness-independence-v1",
        "levels": INDEPENDENCE_LEVELS,
        "counts": dict(sorted(levels.items())),
        "trace_ids_by_level": {k: sorted(v) for k, v in sorted(by_level.items())},
        "coverage_ready": not missing,
        "required_coverage": sorted(REQUIRED_COVERAGE),
        "missing_coverage": missing,
        "failures": failures,
    }
    REPORT.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    if failures:
        print("witness independence validation failures:")
        for failure in failures:
            print(f"  {failure}")
        print(f"report written to {REPORT}")
        return 1

    print("validate_witness_independence passed")
    print(f"counts: {dict(sorted(levels.items()))}")
    print(f"report written to {REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
