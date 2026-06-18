"""Validate a small evidence-type claim matrix over existing CAPAS traces.

This script is intentionally conservative. It does not use an LLM, textual
similarity, or a heuristic judge. Each claim is checked against explicit trace
fields. If the fields do not license the claim, the claim is rejected.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
TRACE_DIR = ROOT / "benchmarks" / "gold_traces"
REPORT_PATH = ROOT / "benchmarks" / "evidence_claim_validation_report.json"


@dataclass(frozen=True)
class ClaimCheck:
    trace_id: str
    claim_id: str
    expected_verdict: str
    actual_verdict: str
    passed: bool
    reason: str


TraceResult = dict[str, Any]
Rule = Callable[[TraceResult], tuple[str, str]]


def load_trace_result(trace_id: str) -> TraceResult:
    path = TRACE_DIR / f"{trace_id}.json"
    with path.open() as f:
        payload = json.load(f)
    return payload["result"]["result"]


def verdict(ok: bool, accept_reason: str, reject_reason: str) -> tuple[str, str]:
    if ok:
        return "ACCEPT", accept_reason
    return "REJECT", reject_reason


def exact_model_solution(trace: TraceResult) -> tuple[str, str]:
    return verdict(
        trace.get("abs_error_vs_fci") == 0.0 or trace.get("solver_error_hartree") == 0.0,
        "solver/model error is explicitly zero for the declared model",
        "trace does not show an exact solve for the declared model",
    )


def physically_accurate_chemistry(trace: TraceResult) -> tuple[str, str]:
    return verdict(
        trace.get("physical_evidence_level") == "experimental"
        and trace.get("within_chemical_accuracy") is True,
        "experimental comparison is within the declared chemical-accuracy threshold",
        "experimental evidence records distance to measurement but does not show chemical accuracy",
    )


def robust_physical_chemistry(trace: TraceResult) -> tuple[str, str]:
    if trace.get("physical_evidence_level") != "experimental":
        return "REJECT", "claim requires experimental evidence"
    points = trace.get("convergence_points") or []
    robust_points = [p for p in points if p.get("robustness") == "true_robust"]
    return verdict(
        bool(robust_points),
        f"basis convergence contains {len(robust_points)} true_robust point(s)",
        "no true_robust convergence point is recorded",
    )


def unique_optimum(trace: TraceResult) -> tuple[str, str]:
    degeneracy = trace.get("degeneracy_count")
    return verdict(
        degeneracy == 1,
        "degeneracy_count is 1",
        f"degeneracy_count is {degeneracy}; the trace licenses an optimum set, not a unique decision",
    )


def optimum_set_verified(trace: TraceResult) -> tuple[str, str]:
    return verdict(
        trace.get("physical_evidence_level") == "analytic"
        and trace.get("bound_scope") == "exact_small_instance_brute_force_verified"
        and trace.get("degeneracy_count", 0) >= 1
        and trace.get("abs_error") == 0.0,
        "exact brute-force witness verifies the optimum set for the small instance",
        "trace does not carry exact brute-force optimum-set evidence",
    )


def global_dmrg_formal_certificate(trace: TraceResult) -> tuple[str, str]:
    scope = trace.get("bound_scope")
    return verdict(
        trace.get("physical_evidence_level") == "formal_bound"
        and scope in {"global_dmrg_state_bound", "global_observable_bound"},
        "formal bound scope is global",
        f"formal bound scope is {scope!r}, not a global DMRG/observable certificate",
    )


def single_cut_state_bound(trace: TraceResult) -> tuple[str, str]:
    return verdict(
        trace.get("physical_evidence_level") == "formal_bound"
        and trace.get("bound_scope") == "single_bipartition_state_truncation"
        and trace.get("formal_bound_status")
        == "established_for_single_schmidt_truncation_not_global_dmrg",
        "single-cut Schmidt truncation theorem supports the scoped state bound",
        "trace does not license a single-cut state truncation bound",
    )


def local_properties_imply_universal_scaling(trace: TraceResult) -> tuple[str, str]:
    return verdict(
        trace.get("local_property_tests_pass") is True
        and trace.get("universal_anchor_pass") is True,
        "local properties and universal scaling anchor both pass",
        "local properties pass, but the universal scaling anchor does not",
    )


def universal_anchor_caught_scaling_error(trace: TraceResult) -> tuple[str, str]:
    return verdict(
        trace.get("physical_evidence_level") == "scaling_law_anchor"
        and trace.get("anchor_mode") == "absolute_anchor"
        and trace.get("local_property_tests_pass") is True
        and trace.get("universal_anchor_pass") is False
        and trace.get("invariant_caught") is True,
        "absolute scaling-law anchor catches a locally plausible violation",
        "trace does not show the absolute anchor catching the scaling violation",
    )


CLAIM_RULES: dict[str, Rule] = {
    "exact_model_solution": exact_model_solution,
    "physically_accurate_chemistry": physically_accurate_chemistry,
    "robust_physical_chemistry": robust_physical_chemistry,
    "unique_optimum": unique_optimum,
    "optimum_set_verified": optimum_set_verified,
    "global_dmrg_formal_certificate": global_dmrg_formal_certificate,
    "single_cut_state_bound": single_cut_state_bound,
    "local_properties_imply_universal_scaling": local_properties_imply_universal_scaling,
    "universal_anchor_caught_scaling_error": universal_anchor_caught_scaling_error,
}


EXAMPLES: list[tuple[str, str, str]] = [
    ("trace_021", "exact_model_solution", "ACCEPT"),
    ("trace_021", "physically_accurate_chemistry", "REJECT"),
    ("trace_027", "robust_physical_chemistry", "ACCEPT"),
    ("trace_020", "unique_optimum", "REJECT"),
    ("trace_020", "optimum_set_verified", "ACCEPT"),
    ("trace_016", "global_dmrg_formal_certificate", "REJECT"),
    ("trace_016", "single_cut_state_bound", "ACCEPT"),
    ("trace_038", "local_properties_imply_universal_scaling", "REJECT"),
    ("trace_038", "universal_anchor_caught_scaling_error", "ACCEPT"),
]


def run_checks() -> list[ClaimCheck]:
    checks: list[ClaimCheck] = []
    for trace_id, claim_id, expected in EXAMPLES:
        actual, reason = CLAIM_RULES[claim_id](load_trace_result(trace_id))
        checks.append(
            ClaimCheck(
                trace_id=trace_id,
                claim_id=claim_id,
                expected_verdict=expected,
                actual_verdict=actual,
                passed=actual == expected,
                reason=reason,
            )
        )
    return checks


def main() -> None:
    checks = run_checks()
    failed = [check for check in checks if not check.passed]
    report = {
        "summary": {
            "checks": len(checks),
            "passed": len(checks) - len(failed),
            "failed": len(failed),
            "fine_tune_ready_implication": "none; this validates claim typing, not training readiness",
        },
        "checks": [asdict(check) for check in checks],
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")

    for check in checks:
        status = "ok" if check.passed else "FAIL"
        print(
            f"{check.trace_id} {check.claim_id}: {status} "
            f"({check.actual_verdict}; expected {check.expected_verdict})"
        )
    print(f"report written to {REPORT_PATH}")

    if failed:
        raise SystemExit(1)
    print("validate_evidence_claims passed")


if __name__ == "__main__":
    main()

