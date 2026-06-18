"""Validate a small evidence-type claim matrix over CAPAS traces.

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


def missing_fields(trace: TraceResult, fields: list[str]) -> list[str]:
    return [
        field
        for field in fields
        if trace.get(field) is None or trace.get(field) == "unknown"
    ]


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


def simulation_ran(trace: TraceResult) -> tuple[str, str]:
    return verdict(
        trace.get("evidence_status") == "success"
        and bool(trace.get("method"))
        and bool(trace.get("provenance_recorded")),
        "method and provenance record a successful simulation run",
        "trace does not establish that a simulation ran with provenance",
    )


def numerical_solution_converged(trace: TraceResult) -> tuple[str, str]:
    needed = missing_fields(trace, ["residual_norm", "residual_tolerance", "convergence_status"])
    if needed:
        return "HOLD", f"cannot judge convergence; missing {needed}"
    return verdict(
        trace["convergence_status"] == "converged"
        and trace["residual_norm"] <= trace["residual_tolerance"],
        "residual is within declared tolerance and convergence_status is converged",
        "residual or convergence_status does not license convergence",
    )


def matches_experiment(trace: TraceResult) -> tuple[str, str]:
    needed = missing_fields(
        trace,
        [
            "reference_type",
            "reference_definition_match",
            "abs_error_vs_reference",
            "reference_tolerance",
        ],
    )
    if needed:
        return "HOLD", f"cannot judge experimental match; missing {needed}"
    return verdict(
        trace["reference_type"] == "experiment"
        and trace["reference_definition_match"] is True
        and trace["abs_error_vs_reference"] <= trace["reference_tolerance"],
        "experimental reference matches the computed quantity and error is within tolerance",
        "trace does not license a match to experiment under the declared tolerance",
    )


def model_validated_for_case(trace: TraceResult) -> tuple[str, str]:
    match, reason = matches_experiment(trace)
    if match != "ACCEPT":
        return match, f"case validation requires experimental match: {reason}"
    return verdict(
        trace.get("validation_scope") == "single_case",
        "single-case validation scope is explicit and supported by experimental match",
        "trace may match experiment but does not declare single-case validation scope",
    )


def model_validated_for_domain(trace: TraceResult) -> tuple[str, str]:
    cases = trace.get("validation_cases")
    has_uq = trace.get("uq_or_sensitivity") is True
    has_domain_scope = trace.get("validation_scope") == "domain"
    if trace.get("validation_scope") == "single_case" and cases == 1:
        return (
            "REWRITE",
            "evidence licenses model_validated_for_case, not model_validated_for_domain",
        )
    return verdict(
        isinstance(cases, int) and cases >= 3 and has_uq and has_domain_scope,
        "domain validation has multiple cases, UQ/sensitivity, and domain scope",
        "domain validation requires multiple validation cases plus UQ/sensitivity and domain scope",
    )


def fit_improved(trace: TraceResult) -> tuple[str, str]:
    before = trace.get("residual_before")
    after = trace.get("residual_after")
    if before is None or after is None:
        return "HOLD", "cannot judge fit improvement without before/after residuals"
    return verdict(
        after < before,
        "refinement residual decreased",
        "refinement residual did not improve",
    )


def structure_plausible(trace: TraceResult) -> tuple[str, str]:
    fit, reason = fit_improved(trace)
    if fit != "ACCEPT":
        return fit, f"structure plausibility requires improved fit: {reason}"
    return verdict(
        trace.get("physical_constraints_pass") is True,
        "fit improved and physical constraints pass",
        "fit improved, but physical constraints are missing or failed",
    )


def structure_validated(trace: TraceResult) -> tuple[str, str]:
    if trace.get("held_out_validation") is True or trace.get("independent_structure_reference") is True:
        return "ACCEPT", "held-out or independent structural validation is recorded"
    if trace.get("residual_after") is not None:
        return (
            "REWRITE",
            "refinement evidence may license fit_improved or structure_plausible, not structure_validated",
        )
    return "HOLD", "no refinement or independent validation evidence is available"


def runtime_predicted(trace: TraceResult) -> tuple[str, str]:
    needed = missing_fields(trace, ["runtime_prediction_error", "runtime_error_tolerance"])
    if needed:
        return "HOLD", f"cannot judge runtime prediction; missing {needed}"
    return verdict(
        trace["runtime_prediction_error"] <= trace["runtime_error_tolerance"],
        "runtime prediction error is within declared tolerance",
        "runtime prediction error exceeds declared tolerance",
    )


def scientific_result_validated_from_runtime(trace: TraceResult) -> tuple[str, str]:
    runtime, reason = runtime_predicted(trace)
    if runtime == "ACCEPT":
        return (
            "REWRITE",
            "runtime evidence licenses runtime_predicted, not scientific_result_validated",
        )
    return runtime, f"scientific validation cannot be inferred from runtime evidence: {reason}"


def uq_interval_supports_claim(trace: TraceResult) -> tuple[str, str]:
    needed = missing_fields(trace, ["uq_interval", "claimed_value"])
    if needed:
        return "HOLD", f"cannot judge UQ support; missing {needed}"
    lo, hi = trace["uq_interval"]
    value = trace["claimed_value"]
    return verdict(
        lo <= value <= hi,
        "claimed value lies inside the declared uncertainty interval",
        "claimed value lies outside the declared uncertainty interval",
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
    "simulation_ran": simulation_ran,
    "numerical_solution_converged": numerical_solution_converged,
    "matches_experiment": matches_experiment,
    "model_validated_for_case": model_validated_for_case,
    "model_validated_for_domain": model_validated_for_domain,
    "fit_improved": fit_improved,
    "structure_plausible": structure_plausible,
    "structure_validated": structure_validated,
    "runtime_predicted": runtime_predicted,
    "scientific_result_validated_from_runtime": scientific_result_validated_from_runtime,
    "uq_interval_supports_claim": uq_interval_supports_claim,
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


REGIONAL_SYNTHETIC_TRACES: dict[str, TraceResult] = {
    "regional_cono_sur_simulation_run": {
        "evidence_status": "success",
        "method": "finite_volume_cfd",
        "provenance_recorded": True,
    },
    "regional_cono_sur_single_case_validated": {
        "evidence_status": "success",
        "method": "finite_element_model",
        "provenance_recorded": True,
        "reference_type": "experiment",
        "reference_definition_match": True,
        "abs_error_vs_reference": 0.03,
        "reference_tolerance": 0.05,
        "validation_scope": "single_case",
        "validation_cases": 1,
        "uq_or_sensitivity": False,
    },
    "regional_cono_sur_ambiguous_experiment": {
        "evidence_status": "success",
        "method": "thermal_process_model",
        "provenance_recorded": True,
        "reference_type": "experiment",
        "abs_error_vs_reference": 0.02,
        "reference_tolerance": 0.05,
        "reference_definition_match": "unknown",
    },
    "regional_china_rietveld_fit": {
        "evidence_status": "success",
        "method": "agentic_rietveld_refinement",
        "provenance_recorded": True,
        "residual_before": 0.18,
        "residual_after": 0.11,
        "physical_constraints_pass": False,
        "held_out_validation": False,
        "independent_structure_reference": False,
    },
    "regional_china_rietveld_plausible": {
        "evidence_status": "success",
        "method": "agentic_rietveld_refinement",
        "provenance_recorded": True,
        "residual_before": 0.18,
        "residual_after": 0.11,
        "physical_constraints_pass": True,
        "held_out_validation": False,
        "independent_structure_reference": False,
    },
    "regional_uncuyo_runtime_prediction": {
        "evidence_status": "success",
        "method": "workflow_runtime_model",
        "provenance_recorded": True,
        "runtime_prediction_error": 0.08,
        "runtime_error_tolerance": 0.10,
    },
    "regional_uq_interval_case": {
        "evidence_status": "success",
        "method": "arterial_network_uq",
        "provenance_recorded": True,
        "uq_interval": [0.72, 0.81],
        "claimed_value": 0.76,
    },
    "regional_uq_interval_miss": {
        "evidence_status": "success",
        "method": "arterial_network_uq",
        "provenance_recorded": True,
        "uq_interval": [0.72, 0.81],
        "claimed_value": 0.86,
    },
}


REGIONAL_EXAMPLES: list[tuple[str, str, str]] = [
    ("regional_cono_sur_simulation_run", "simulation_ran", "ACCEPT"),
    ("regional_cono_sur_single_case_validated", "model_validated_for_case", "ACCEPT"),
    ("regional_cono_sur_single_case_validated", "model_validated_for_domain", "REWRITE"),
    ("regional_cono_sur_ambiguous_experiment", "matches_experiment", "HOLD"),
    ("regional_china_rietveld_fit", "fit_improved", "ACCEPT"),
    ("regional_china_rietveld_fit", "structure_validated", "REWRITE"),
    ("regional_china_rietveld_plausible", "structure_plausible", "ACCEPT"),
    ("regional_china_rietveld_plausible", "structure_validated", "REWRITE"),
    ("regional_uncuyo_runtime_prediction", "runtime_predicted", "ACCEPT"),
    (
        "regional_uncuyo_runtime_prediction",
        "scientific_result_validated_from_runtime",
        "REWRITE",
    ),
    ("regional_uq_interval_case", "uq_interval_supports_claim", "ACCEPT"),
    ("regional_uq_interval_miss", "uq_interval_supports_claim", "REJECT"),
]


REGIONAL_CLAIM_MATRIX: dict[str, dict[str, Any]] = {
    "simulation_ran": {
        "minimum_fields": ["evidence_status", "method", "provenance_recorded"],
        "source_cluster": "Cono Sur simulation proceedings",
    },
    "numerical_solution_converged": {
        "minimum_fields": ["residual_norm", "residual_tolerance", "convergence_status"],
        "source_cluster": "AMCA/CIMEC numerical simulation",
    },
    "matches_experiment": {
        "minimum_fields": [
            "reference_type",
            "reference_definition_match",
            "abs_error_vs_reference",
            "reference_tolerance",
        ],
        "source_cluster": "CONICET/AMCA validation against experiment",
    },
    "model_validated_for_case": {
        "minimum_fields": ["matches_experiment", "validation_scope"],
        "source_cluster": "single-case regional validation",
    },
    "model_validated_for_domain": {
        "minimum_fields": ["validation_cases>=3", "uq_or_sensitivity", "validation_scope=domain"],
        "source_cluster": "VVUQ/domain validation",
    },
    "fit_improved": {
        "minimum_fields": ["residual_before", "residual_after"],
        "source_cluster": "China Rietveld refinement agents",
    },
    "structure_plausible": {
        "minimum_fields": ["fit_improved", "physical_constraints_pass"],
        "source_cluster": "China Rietveld refinement agents",
    },
    "structure_validated": {
        "minimum_fields": ["held_out_validation or independent_structure_reference"],
        "source_cluster": "China Rietveld refinement agents",
    },
    "runtime_predicted": {
        "minimum_fields": ["runtime_prediction_error", "runtime_error_tolerance"],
        "source_cluster": "UNCuyo scientific workflow runtime prediction",
    },
    "uq_interval_supports_claim": {
        "minimum_fields": ["uq_interval", "claimed_value"],
        "source_cluster": "regional UQ model",
    },
}


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
    for trace_id, claim_id, expected in REGIONAL_EXAMPLES:
        actual, reason = CLAIM_RULES[claim_id](REGIONAL_SYNTHETIC_TRACES[trace_id])
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
            "regional_synthetic_checks": len(REGIONAL_EXAMPLES),
            "regional_claims": len(REGIONAL_CLAIM_MATRIX),
            "fine_tune_ready_implication": "none; this validates claim typing, not training readiness",
        },
        "regional_claim_matrix": REGIONAL_CLAIM_MATRIX,
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
