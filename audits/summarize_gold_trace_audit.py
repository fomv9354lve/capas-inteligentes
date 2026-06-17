from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CSV_PATH = ROOT / "gold_trace_audit_template.csv"


def norm(value: str) -> str:
    if value is None:
        return ""
    if not isinstance(value, str):
        return ""
    return value.strip().lower()


def main() -> int:
    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    audit_columns = [c for c in rows[0].keys() if c and c != "trace_id"] if rows else []
    filled = [r for r in rows if any(norm(r.get(c, "")) for c in audit_columns)]
    decisions = Counter(norm(r.get("decision", "")) or "blank" for r in rows)

    def rate(column: str, value: str = "yes") -> tuple[int, int, float]:
        known = [r for r in rows if norm(r.get(column, "")) in {"yes", "no"}]
        hits = [r for r in known if norm(r.get(column, "")) == value]
        return len(hits), len(known), (len(hits) / len(known) if known else 0.0)

    checks = {
        "hash_gate_pass": rate("hash_gate_pass"),
        "output_correct": rate("output_correct"),
        "inference_correct": rate("inference_correct"),
        "inference_blind_judge": rate("inference_blind_judge"),
    }

    accepted = [r for r in rows if norm(r.get("decision", "")) == "accept"]
    physical_levels = Counter(norm(r.get("physical_evidence_level", "")) or "blank" for r in rows)

    def physical_evidence_acceptable(row: dict[str, str]) -> bool:
        level = norm(row.get("physical_evidence_level", ""))
        risk = norm(row.get("risk_level", ""))
        if level in {"analytic", "cross_sim"}:
            return True
        return level == "invariant" and risk in {"low", "medium"}

    accepted_missing_evidence = [
        r["trace_id"]
        for r in accepted
        if not norm(r.get("output_correct_evidence", ""))
        or not norm(r.get("inference_correct_evidence", ""))
    ]
    accepted_not_blind = [
        r["trace_id"]
        for r in accepted
        if norm(r.get("inference_blind_judge", "")) != "yes"
    ]
    accepted_weak_physics = [
        r["trace_id"]
        for r in accepted
        if not physical_evidence_acceptable(r)
    ]
    high_risk_rejects = [
        r["trace_id"]
        for r in rows
        if norm(r.get("risk_level", "")) == "high" and norm(r.get("decision", "")) == "reject"
    ]
    coverage = Counter(norm(r.get("coverage_case", "")) or "blank" for r in rows)
    required_coverage = {
        "analytic_success",
        "cross_sim_success",
        "no_evidence_success",
        "backend_failed",
        "rejected_by_router",
        "estimated_bound_candidate",
    }
    present_coverage = set(coverage) - {"blank"}
    missing_coverage = sorted(required_coverage - present_coverage)

    print(f"rows: {len(rows)}")
    print(f"filled rows: {len(filled)}")
    print(f"decisions: {dict(decisions)}")
    for name, (hits, known, pct) in checks.items():
        print(f"{name}: {hits}/{known} = {pct:.1%}")
    print(f"physical_evidence_levels: {dict(physical_levels)}")
    print(f"coverage_cases: {dict(coverage)}")
    print(f"missing_required_coverage: {missing_coverage}")
    print(f"accepted missing evidence: {accepted_missing_evidence}")
    print(f"accepted not blind judged: {accepted_not_blind}")
    print(f"accepted weak physical evidence: {accepted_weak_physics}")
    print(f"high-risk rejects: {high_risk_rejects}")

    fine_tune_ready = (
        len(accepted) >= 14
        and not accepted_missing_evidence
        and not accepted_not_blind
        and not accepted_weak_physics
    )
    coverage_ready = not missing_coverage
    print(f"fine_tune_ready: {fine_tune_ready}")
    print(f"coverage_ready: {coverage_ready}")
    return 0 if fine_tune_ready or coverage_ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
