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


def validation_taxonomy_observed(trace: TraceResult) -> tuple[str, str]:
    categories = trace.get("validation_categories") or []
    return verdict(
        trace.get("source_type") == "regional_validation_survey"
        and trace.get("surveyed_articles", 0) > 0
        and len(categories) >= 4,
        "regional source records an observed validation taxonomy over surveyed papers",
        "trace does not record a validation taxonomy over surveyed papers",
    )


def experimental_validation_dominates_practice(trace: TraceResult) -> tuple[str, str]:
    counts = trace.get("validation_counts") or {}
    experimental = counts.get("experimental")
    total = trace.get("surveyed_articles")
    if experimental is None or total is None:
        return "HOLD", "cannot judge dominance without experimental count and total"
    return verdict(
        experimental / total > 0.5,
        "experimental validation appears in more than half of surveyed papers",
        f"experimental validation appears in {experimental}/{total} surveyed papers, so dominance is not licensed",
    )


def qualitative_experimental_agreement_reported(trace: TraceResult) -> tuple[str, str]:
    return verdict(
        trace.get("reference_type") == "experiment"
        and trace.get("agreement_claim_type") == "qualitative"
        and bool(trace.get("observables")),
        "source reports qualitative agreement with experiment for declared observables",
        "trace does not record a qualitative experimental-agreement claim",
    )


def agent_refinement_beats_specialist_rwp(trace: TraceResult) -> tuple[str, str]:
    wins = trace.get("agent_rwp_wins")
    total = trace.get("samples")
    return verdict(
        trace.get("source_type") == "rietveld_agent_evaluation"
        and isinstance(wins, int)
        and isinstance(total, int)
        and wins > 0,
        f"agent reports lower Rwp than specialists on {wins}/{total} samples",
        "trace does not record a lower-Rwp comparison against specialists",
    )


def rwp_improvement_implies_structure_validated(trace: TraceResult) -> tuple[str, str]:
    fit, reason = agent_refinement_beats_specialist_rwp(trace)
    if fit == "ACCEPT":
        return (
            "REWRITE",
            "lower Rwp licenses a fit-quality claim, not independent structure validation",
        )
    return fit, f"structure validation cannot be inferred: {reason}"


def scientist_contract_recorded(trace: TraceResult) -> tuple[str, str]:
    return verdict(
        trace.get("source_type") == "scientific_agent_build_contract"
        and trace.get("scientist_authored_contract") is True
        and trace.get("rubric_driven_judge") is True,
        "source records a scientist-authored contract and rubric-driven judge",
        "trace does not record a scientist-authored contract and judge",
    )


def contract_failure_not_physical_failure(trace: TraceResult) -> tuple[str, str]:
    return verdict(
        trace.get("frontier_case_status") == "contract_failure"
        and trace.get("physical_validation_status") == "not_established",
        "frontier is framed as workflow/contract failure, not physical invalidity",
        "trace does not separate contract failure from physical validation failure",
    )


def rct_primary_endpoint_supported(trace: TraceResult) -> tuple[str, str]:
    return verdict(
        trace.get("study_design") in {"randomized_controlled_trial", "randomized_placebo_trial"}
        and trace.get("control_group") in {"usual_care", "placebo"}
        and trace.get("primary_endpoint_met") is True
        and trace.get("effect_ci_excludes_null") is True,
        "randomized trial has control group, primary endpoint, and CI excluding null",
        "trace does not license the RCT primary endpoint claim",
    )


def treatment_benefits_all_subgroups(trace: TraceResult) -> tuple[str, str]:
    subgroups = trace.get("subgroup_effects") or {}
    failed = [
        name
        for name, payload in subgroups.items()
        if payload.get("ci_excludes_null") is not True or payload.get("direction") != "benefit"
    ]
    if failed:
        return (
            "REWRITE",
            f"evidence supports only responsive subgroup(s); not all subgroups: {failed}",
        )
    return verdict(bool(subgroups), "all recorded subgroups show benefit", "no subgroup evidence")


def vaccine_efficacy_trial_supported(trace: TraceResult) -> tuple[str, str]:
    return verdict(
        trace.get("study_design") == "randomized_placebo_trial"
        and trace.get("observer_blind") is True
        and trace.get("vaccine_cases", 10**9) < trace.get("placebo_cases", -1)
        and trace.get("vaccine_efficacy_percent", 0.0) >= trace.get("efficacy_threshold_percent", 0.0),
        "observer-blind placebo trial supports vaccine efficacy within the trial endpoint",
        "trace does not license the vaccine efficacy trial claim",
    )


def vaccine_prevents_all_infection_or_transmission(trace: TraceResult) -> tuple[str, str]:
    if trace.get("study_design") == "randomized_placebo_trial":
        return (
            "REWRITE",
            "trial endpoint licenses symptomatic-disease efficacy, not sterilizing immunity or transmission blocking",
        )
    return "HOLD", "no vaccine trial evidence available"


def gravitational_wave_detection_supported(trace: TraceResult) -> tuple[str, str]:
    return verdict(
        trace.get("detectors") == 2
        and trace.get("matched_filter_snr", 0) >= 8
        and trace.get("false_alarm_years", 0) >= trace.get("false_alarm_year_threshold", 0)
        and trace.get("noise_controls_pass") is True,
        "two-detector matched-filter detection clears false-alarm and noise-control thresholds",
        "trace does not license a gravitational-wave detection claim",
    )


def gravitational_wave_population_rate_precise(trace: TraceResult) -> tuple[str, str]:
    interval = trace.get("population_rate_credible_interval")
    if interval:
        lo, hi = interval
        if lo > 0 and hi / lo > 10:
            return (
                "REWRITE",
                "single-event evidence licenses detection/source claims, not a precise population rate",
            )
    return verdict(
        bool(interval),
        "population rate interval is recorded and not too broad",
        "no population-rate evidence is recorded",
    )


def alphafold_casp14_accuracy_supported(trace: TraceResult) -> tuple[str, str]:
    return verdict(
        trace.get("benchmark") == "CASP14"
        and trace.get("blind_benchmark") is True
        and trace.get("median_backbone_rmsd95_angstrom", 10**9)
        <= trace.get("rmsd95_threshold_angstrom", 10**9)
        and trace.get("confidence_intervals_reported") is True,
        "blind CASP14 benchmark supports near-experimental structure accuracy for many targets",
        "trace does not license the AlphaFold CASP14 accuracy claim",
    )


def alphafold_solves_full_protein_folding(trace: TraceResult) -> tuple[str, str]:
    if trace.get("benchmark") == "CASP14":
        return (
            "REWRITE",
            "CASP14 supports structure-prediction accuracy, not full folding mechanism or all protein contexts",
        )
    return "HOLD", "no AlphaFold benchmark evidence available"


def dart_orbit_change_supported(trace: TraceResult) -> tuple[str, str]:
    delta = trace.get("orbital_period_change_minutes")
    sigma = trace.get("orbital_period_change_sigma_minutes")
    return verdict(
        trace.get("controlled_impact") is True
        and trace.get("pre_post_orbit_measured") is True
        and trace.get("independent_measurement_methods_agree") is True
        and delta is not None
        and sigma is not None
        and abs(delta) > 5 * sigma,
        "controlled impact has pre/post orbit measurements and independent agreement",
        "trace does not license an asteroid-orbit-change claim",
    )


def dart_solves_planetary_defense(trace: TraceResult) -> tuple[str, str]:
    if trace.get("controlled_impact") is True:
        return (
            "REWRITE",
            "DART licenses kinetic-impact deflection for one controlled binary-asteroid case, not planetary-defense solved",
        )
    return "HOLD", "no DART controlled-impact evidence available"


def quantum_sampling_advantage_supported(trace: TraceResult) -> tuple[str, str]:
    return verdict(
        trace.get("task") == "random_circuit_sampling"
        and trace.get("quantum_runtime_seconds", 10**12) < trace.get("classical_reference_runtime_seconds", 0)
        and trace.get("fidelity_benchmark") == "xeb",
        "random-circuit-sampling benchmark supports a task-specific quantum advantage claim",
        "trace does not license a task-specific random-circuit-sampling advantage claim",
    )


def quantum_sampling_implies_useful_fault_tolerant_qc(trace: TraceResult) -> tuple[str, str]:
    if trace.get("task") == "random_circuit_sampling":
        return (
            "REWRITE",
            "random-circuit sampling licenses a benchmark advantage, not useful fault-tolerant quantum computing",
        )
    return "HOLD", "no quantum-sampling benchmark evidence available"


def satellite_qkd_demo_supported(trace: TraceResult) -> tuple[str, str]:
    return verdict(
        trace.get("trusted_relay") is True
        and trace.get("distance_km", 0) >= 1000
        and trace.get("keys_exchanged") is True,
        "trusted-relay satellite QKD demo supports intercontinental quantum-secured communication",
        "trace does not license the satellite QKD demonstration claim",
    )


def satellite_qkd_implies_global_untrusted_quantum_internet(trace: TraceResult) -> tuple[str, str]:
    if trace.get("trusted_relay") is True:
        return (
            "REWRITE",
            "trusted-relay QKD demo does not license a global untrusted quantum internet",
        )
    return "HOLD", "no satellite QKD evidence available"


def gpt3_fewshot_benchmark_supported(trace: TraceResult) -> tuple[str, str]:
    return verdict(
        trace.get("model") == "GPT-3"
        and trace.get("few_shot_setting") is True
        and trace.get("benchmarks_improved") is True,
        "few-shot benchmark evidence supports broad NLP task improvement",
        "trace does not license the GPT-3 few-shot benchmark claim",
    )


def gpt3_implies_agi_or_reliable_reasoner(trace: TraceResult) -> tuple[str, str]:
    if trace.get("model") == "GPT-3":
        return (
            "REWRITE",
            "few-shot NLP benchmark gains do not license AGI or reliable general reasoning",
        )
    return "HOLD", "no GPT-3 benchmark evidence available"


def crispr_embryo_editing_research_supported(trace: TraceResult) -> tuple[str, str]:
    return verdict(
        trace.get("system") == "CRISPR-Cas9"
        and trace.get("embryo_research") is True
        and trace.get("correction_efficiency_percent", 0) > 0,
        "embryo research reports correction in a fraction of embryos",
        "trace does not license the embryo-editing research claim",
    )


def crispr_embryo_editing_clinically_safe(trace: TraceResult) -> tuple[str, str]:
    if trace.get("embryo_research") is True:
        return (
            "REWRITE",
            "embryo correction research does not license clinically safe heritable genome editing",
        )
    return "HOLD", "no embryo-editing evidence available"


def hgp_reference_genome_supported(trace: TraceResult) -> tuple[str, str]:
    return verdict(
        trace.get("project") == "Human Genome Project"
        and trace.get("reference_sequence") is True
        and trace.get("euchromatic_coverage_percent", 0) >= 90,
        "HGP evidence supports a high-quality euchromatic reference genome sequence",
        "trace does not license the HGP reference-sequence claim",
    )


def hgp_solves_genetic_disease(trace: TraceResult) -> tuple[str, str]:
    if trace.get("project") == "Human Genome Project":
        return (
            "REWRITE",
            "reference sequencing does not license solving all genetic disease mechanisms or therapies",
        )
    return "HOLD", "no HGP evidence available"


def higgs_discovery_supported(trace: TraceResult) -> tuple[str, str]:
    return verdict(
        trace.get("experiment") in {"ATLAS", "CMS", "ATLAS_CMS"}
        and trace.get("sigma", 0) >= 5
        and trace.get("mass_gev", 0) >= 120
        and trace.get("properties_consistent_with_sm_higgs") is True,
        "collider evidence licenses discovery of a Higgs-like boson consistent with the Standard Model",
        "trace does not license the Higgs discovery claim",
    )


def higgs_discovery_completes_physics(trace: TraceResult) -> tuple[str, str]:
    if trace.get("properties_consistent_with_sm_higgs") is True:
        return (
            "REWRITE",
            "Higgs discovery completes a Standard Model slot, not all of physics or new-physics searches",
        )
    return "HOLD", "no Higgs evidence available"


def lecanemab_slows_decline_supported(trace: TraceResult) -> tuple[str, str]:
    return verdict(
        trace.get("study_design") == "randomized_placebo_trial"
        and trace.get("population") == "early_alzheimers"
        and trace.get("decline_reduction_percent", 0) > 0
        and trace.get("adverse_events_recorded") is True,
        "trial evidence supports slower decline in early Alzheimer's with recorded adverse events",
        "trace does not license the lecanemab trial claim",
    )


def lecanemab_cures_alzheimers(trace: TraceResult) -> tuple[str, str]:
    if trace.get("population") == "early_alzheimers":
        return (
            "REWRITE",
            "slower decline in early Alzheimer's does not license cure, reversal, or broad-stage efficacy",
        )
    return "HOLD", "no lecanemab evidence available"


def semaglutide_select_mace_supported(trace: TraceResult) -> tuple[str, str]:
    return verdict(
        trace.get("trial") == "SELECT"
        and trace.get("study_design") == "randomized_placebo_trial"
        and trace.get("population") == "overweight_obesity_without_diabetes_with_cvd"
        and trace.get("mace_reduction_percent", 0) > 0,
        "SELECT trial supports MACE reduction in the declared non-diabetic overweight/obesity CVD population",
        "trace does not license the SELECT cardiovascular outcome claim",
    )


def semaglutide_solves_cardiovascular_disease(trace: TraceResult) -> tuple[str, str]:
    if trace.get("trial") == "SELECT":
        return (
            "REWRITE",
            "SELECT supports risk reduction in a defined population, not solving cardiovascular disease generally",
        )
    return "HOLD", "no SELECT evidence available"


def jwst_early_galaxy_observation_supported(trace: TraceResult) -> tuple[str, str]:
    return verdict(
        trace.get("instrument") == "JWST"
        and trace.get("redshift", 0) >= 9
        and trace.get("spectroscopic_confirmation") is True,
        "JWST evidence supports an early massive galaxy observation at high redshift",
        "trace does not license the JWST early-galaxy observation claim",
    )


def jwst_overturns_big_bang(trace: TraceResult) -> tuple[str, str]:
    if trace.get("instrument") == "JWST":
        return (
            "REWRITE",
            "early high-redshift galaxies pressure galaxy-formation models, not Big Bang cosmology as a whole",
        )
    return "HOLD", "no JWST evidence available"


def room_temp_superconductor_established(trace: TraceResult) -> tuple[str, str]:
    if trace.get("retracted") is True or trace.get("independent_replication") is False:
        return (
            "REJECT",
            "claim is not licensed because the record is retracted or lacks independent replication",
        )
    return verdict(
        trace.get("zero_resistance") is True and trace.get("meissner_effect") is True,
        "superconductivity evidence includes zero resistance and Meissner effect",
        "trace does not license established room-temperature superconductivity",
    )


def claim_transition_gate(trace: TraceResult) -> tuple[str, str]:
    if trace.get("evidence_record_status") in {"retracted", "negative_replication"}:
        return (
            "REJECT",
            "stronger claim cannot be upgraded from a retracted or negatively replicated evidence record",
        )
    if trace.get("upgrade_evidence_present") is True:
        return (
            "ACCEPT",
            "upgrade evidence is present, so the attempted stronger claim is licensed within declared scope",
        )
    if trace.get("blocker") and trace.get("required_upgrade_evidence"):
        return (
            "REWRITE",
            "current evidence licenses the narrow claim; stronger claim requires the declared upgrade evidence",
        )
    return "HOLD", "claim transition cannot be judged without blocker and required upgrade evidence"


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
    "validation_taxonomy_observed": validation_taxonomy_observed,
    "experimental_validation_dominates_practice": experimental_validation_dominates_practice,
    "qualitative_experimental_agreement_reported": qualitative_experimental_agreement_reported,
    "agent_refinement_beats_specialist_rwp": agent_refinement_beats_specialist_rwp,
    "rwp_improvement_implies_structure_validated": rwp_improvement_implies_structure_validated,
    "scientist_contract_recorded": scientist_contract_recorded,
    "contract_failure_not_physical_failure": contract_failure_not_physical_failure,
    "rct_primary_endpoint_supported": rct_primary_endpoint_supported,
    "treatment_benefits_all_subgroups": treatment_benefits_all_subgroups,
    "vaccine_efficacy_trial_supported": vaccine_efficacy_trial_supported,
    "vaccine_prevents_all_infection_or_transmission": vaccine_prevents_all_infection_or_transmission,
    "gravitational_wave_detection_supported": gravitational_wave_detection_supported,
    "gravitational_wave_population_rate_precise": gravitational_wave_population_rate_precise,
    "alphafold_casp14_accuracy_supported": alphafold_casp14_accuracy_supported,
    "alphafold_solves_full_protein_folding": alphafold_solves_full_protein_folding,
    "dart_orbit_change_supported": dart_orbit_change_supported,
    "dart_solves_planetary_defense": dart_solves_planetary_defense,
    "quantum_sampling_advantage_supported": quantum_sampling_advantage_supported,
    "quantum_sampling_implies_useful_fault_tolerant_qc": quantum_sampling_implies_useful_fault_tolerant_qc,
    "satellite_qkd_demo_supported": satellite_qkd_demo_supported,
    "satellite_qkd_implies_global_untrusted_quantum_internet": satellite_qkd_implies_global_untrusted_quantum_internet,
    "gpt3_fewshot_benchmark_supported": gpt3_fewshot_benchmark_supported,
    "gpt3_implies_agi_or_reliable_reasoner": gpt3_implies_agi_or_reliable_reasoner,
    "crispr_embryo_editing_research_supported": crispr_embryo_editing_research_supported,
    "crispr_embryo_editing_clinically_safe": crispr_embryo_editing_clinically_safe,
    "hgp_reference_genome_supported": hgp_reference_genome_supported,
    "hgp_solves_genetic_disease": hgp_solves_genetic_disease,
    "higgs_discovery_supported": higgs_discovery_supported,
    "higgs_discovery_completes_physics": higgs_discovery_completes_physics,
    "lecanemab_slows_decline_supported": lecanemab_slows_decline_supported,
    "lecanemab_cures_alzheimers": lecanemab_cures_alzheimers,
    "semaglutide_select_mace_supported": semaglutide_select_mace_supported,
    "semaglutide_solves_cardiovascular_disease": semaglutide_solves_cardiovascular_disease,
    "jwst_early_galaxy_observation_supported": jwst_early_galaxy_observation_supported,
    "jwst_overturns_big_bang": jwst_overturns_big_bang,
    "room_temp_superconductor_established": room_temp_superconductor_established,
    "claim_transition_gate": claim_transition_gate,
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
    ("trace_039", "claim_transition_gate", "ACCEPT"),
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


REGIONAL_REAL_TRACES: dict[str, TraceResult] = {
    "regional_s01_godoy_dardatti_validation_survey": {
        "source_type": "regional_validation_survey",
        "source_url": "https://cimec.org.ar/ojs/index.php/mc/article/view/1854",
        "title": "Validacion de Modelos en Mecanica Computacional",
        "authors": ["Luis A. Godoy", "Patricia M. Dardatti"],
        "surveyed_articles": 104,
        "validation_counts": {
            "experimental": 9,
            "analytic": 33,
            "other_authors_or_methods": 40,
            "commercial_packages": 5,
            "benchmarks": 1,
            "algorithm_efficiency": 13,
        },
        "validation_categories": [
            "experimental",
            "analytic",
            "other_authors_or_methods",
            "commercial_packages",
            "benchmarks",
            "algorithm_efficiency",
        ],
    },
    "regional_s03_romagnoli_hydraulic_jump": {
        "source_type": "regional_simulation_paper",
        "source_url": "https://cimec.org.ar/ojs/index.php/mc/article/view/2826",
        "title": "Simulacion Computacional del Resalto Hidraulico",
        "authors": ["Marta Romagnoli", "Margarita Portapila", "Herve Morvan"],
        "method": "2d_rans_k_epsilon_vof",
        "reference_type": "experiment",
        "agreement_claim_type": "qualitative",
        "observables": ["longitudinal_mean_velocity_U", "turbulent_kinetic_energy_k"],
        "reference_definition_match": "unknown",
    },
    "regional_c35_rongzai_rietveld_agent": {
        "source_type": "rietveld_agent_evaluation",
        "source_url": "https://arxiv.org/abs/2605.13911",
        "title": "Rongzai agent: A Large Language Model-Based Autonomous Assistant for Rietveld Refinement of Neutron Diffraction Data",
        "method": "llm_agent_gsas_ii_rietveld_refinement",
        "samples": 5,
        "agent_rwp_wins": 3,
        "rwp_pairs_agent_vs_specialist": [
            [2.88, 4.42],
            [5.06, 5.40],
            [7.60, 9.00],
        ],
        "independent_structure_reference": False,
        "held_out_validation": False,
    },
    "regional_c36_agentbuild_rietveld": {
        "source_type": "scientific_agent_build_contract",
        "source_url": "https://arxiv.org/abs/2606.12834",
        "title": "Fantastic Scientific Agents and How to Build Them: AgentBuild for Rietveld Refinement",
        "scientist_authored_contract": True,
        "rubric_driven_judge": True,
        "frontier_case_status": "contract_failure",
        "physical_validation_status": "not_established",
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


REGIONAL_REAL_EXAMPLES: list[tuple[str, str, str]] = [
    (
        "regional_s01_godoy_dardatti_validation_survey",
        "validation_taxonomy_observed",
        "ACCEPT",
    ),
    (
        "regional_s01_godoy_dardatti_validation_survey",
        "experimental_validation_dominates_practice",
        "REJECT",
    ),
    (
        "regional_s03_romagnoli_hydraulic_jump",
        "qualitative_experimental_agreement_reported",
        "ACCEPT",
    ),
    ("regional_s03_romagnoli_hydraulic_jump", "matches_experiment", "HOLD"),
    (
        "regional_c35_rongzai_rietveld_agent",
        "agent_refinement_beats_specialist_rwp",
        "ACCEPT",
    ),
    (
        "regional_c35_rongzai_rietveld_agent",
        "rwp_improvement_implies_structure_validated",
        "REWRITE",
    ),
    (
        "regional_c36_agentbuild_rietveld",
        "scientist_contract_recorded",
        "ACCEPT",
    ),
    (
        "regional_c36_agentbuild_rietveld",
        "contract_failure_not_physical_failure",
        "ACCEPT",
    ),
]


US_UK_REAL_TRACES: dict[str, TraceResult] = {
    "usuk_recovery_dexamethasone": {
        "source_type": "top_tier_clinical_trial",
        "source_url": "https://pubmed.ncbi.nlm.nih.gov/32678530/",
        "title": "Dexamethasone in Hospitalized Patients with Covid-19",
        "region_anchor": "UK RECOVERY Collaborative Group",
        "study_design": "randomized_controlled_trial",
        "control_group": "usual_care",
        "primary_endpoint": "28_day_mortality",
        "primary_endpoint_met": True,
        "effect_ci_excludes_null": True,
        "overall_rate_ratio": 0.83,
        "overall_ci": [0.75, 0.93],
        "subgroup_effects": {
            "invasive_mechanical_ventilation": {
                "rate_ratio": 0.64,
                "ci": [0.51, 0.81],
                "ci_excludes_null": True,
                "direction": "benefit",
            },
            "oxygen_without_invasive_ventilation": {
                "rate_ratio": 0.82,
                "ci": [0.72, 0.94],
                "ci_excludes_null": True,
                "direction": "benefit",
            },
            "no_respiratory_support": {
                "rate_ratio": 1.19,
                "ci": [0.92, 1.55],
                "ci_excludes_null": False,
                "direction": "no_benefit",
            },
        },
    },
    "us_biontech_pfizer_bnt162b2": {
        "source_type": "top_tier_vaccine_trial",
        "source_url": "https://www.nejm.org/doi/full/10.1056/NEJMoa2034577",
        "title": "Safety and Efficacy of the BNT162b2 mRNA Covid-19 Vaccine",
        "region_anchor": "US/Germany trial, UK first authorization context",
        "study_design": "randomized_placebo_trial",
        "observer_blind": True,
        "endpoint": "symptomatic_covid_after_second_dose",
        "vaccine_cases": 8,
        "placebo_cases": 162,
        "vaccine_efficacy_percent": 95.0,
        "efficacy_threshold_percent": 50.0,
    },
    "usuk_ligo_gw150914": {
        "source_type": "top_tier_astrophysics_detection",
        "source_url": "https://arxiv.org/abs/1602.03837",
        "title": "Observation of Gravitational Waves from a Binary Black Hole Merger",
        "region_anchor": "US LIGO with UK collaboration participation",
        "detectors": 2,
        "matched_filter_snr": 24,
        "false_alarm_years": 203000,
        "false_alarm_year_threshold": 100,
        "noise_controls_pass": True,
        "population_rate_credible_interval": [2, 600],
    },
    "uk_alphafold_casp14": {
        "source_type": "top_tier_ai_biology_benchmark",
        "source_url": "https://www.nature.com/articles/s41586-021-03819-2",
        "title": "Highly accurate protein structure prediction with AlphaFold",
        "region_anchor": "UK DeepMind",
        "benchmark": "CASP14",
        "blind_benchmark": True,
        "median_backbone_rmsd95_angstrom": 0.96,
        "rmsd95_threshold_angstrom": 1.5,
        "confidence_intervals_reported": True,
        "scope": "single_chain_structure_prediction_many_targets",
    },
    "us_dart_dimorphos": {
        "source_type": "top_tier_planetary_defense_experiment",
        "source_url": "https://www.nature.com/articles/s41586-023-05805-2",
        "title": "Orbital period change of Dimorphos due to the DART kinetic impact",
        "region_anchor": "US NASA DART",
        "controlled_impact": True,
        "pre_post_orbit_measured": True,
        "independent_measurement_methods_agree": True,
        "orbital_period_change_minutes": -33.0,
        "orbital_period_change_sigma_minutes": 1.0,
    },
}


US_UK_EXAMPLES: list[tuple[str, str, str]] = [
    ("usuk_recovery_dexamethasone", "rct_primary_endpoint_supported", "ACCEPT"),
    ("usuk_recovery_dexamethasone", "treatment_benefits_all_subgroups", "REWRITE"),
    ("us_biontech_pfizer_bnt162b2", "vaccine_efficacy_trial_supported", "ACCEPT"),
    (
        "us_biontech_pfizer_bnt162b2",
        "vaccine_prevents_all_infection_or_transmission",
        "REWRITE",
    ),
    ("usuk_ligo_gw150914", "gravitational_wave_detection_supported", "ACCEPT"),
    ("usuk_ligo_gw150914", "gravitational_wave_population_rate_precise", "REWRITE"),
    ("uk_alphafold_casp14", "alphafold_casp14_accuracy_supported", "ACCEPT"),
    ("uk_alphafold_casp14", "alphafold_solves_full_protein_folding", "REWRITE"),
    ("us_dart_dimorphos", "dart_orbit_change_supported", "ACCEPT"),
    ("us_dart_dimorphos", "dart_solves_planetary_defense", "REWRITE"),
]


DEBUNK_10_TRACES: dict[str, TraceResult] = {
    "debunk10_sycamore_random_sampling": {
        "source_type": "top_tier_quantum_benchmark",
        "source_url": "https://www.nature.com/articles/s41586-019-1666-5",
        "title": "Quantum supremacy using a programmable superconducting processor",
        "task": "random_circuit_sampling",
        "quantum_runtime_seconds": 200,
        "classical_reference_runtime_seconds": 10000 * 365 * 24 * 3600,
        "fidelity_benchmark": "xeb",
        "fault_tolerant": False,
        "useful_application": False,
    },
    "debunk10_micius_qkd": {
        "source_type": "top_tier_quantum_communication_demo",
        "source_url": "https://arxiv.org/abs/1801.04418",
        "title": "Satellite-relayed intercontinental quantum network",
        "trusted_relay": True,
        "distance_km": 7600,
        "keys_exchanged": True,
        "untrusted_repeater": False,
        "global_network_deployed": False,
    },
    "debunk10_gpt3_fewshot": {
        "source_type": "top_tier_ai_benchmark",
        "source_url": "https://arxiv.org/abs/2005.14165",
        "title": "Language Models are Few-Shot Learners",
        "model": "GPT-3",
        "few_shot_setting": True,
        "benchmarks_improved": True,
        "struggles_recorded": True,
    },
    "debunk10_crispr_embryo": {
        "source_type": "top_tier_gene_editing_embryo_research",
        "source_url": "https://www.nature.com/articles/nature23305",
        "title": "Correction of a pathogenic gene mutation in human embryos",
        "system": "CRISPR-Cas9",
        "embryo_research": True,
        "correction_efficiency_percent": 72.0,
        "clinical_pregnancy": False,
        "long_term_safety": False,
    },
    "debunk10_hgp_reference": {
        "source_type": "top_tier_genomics_reference",
        "source_url": "https://en.wikipedia.org/wiki/Human_Genome_Project",
        "title": "Human Genome Project reference sequence",
        "project": "Human Genome Project",
        "reference_sequence": True,
        "euchromatic_coverage_percent": 92.1,
        "disease_mechanisms_solved": False,
    },
    "debunk10_higgs_discovery": {
        "source_type": "top_tier_particle_physics_discovery",
        "source_url": "https://arxiv.org/abs/1207.7214",
        "title": "Observation of a new particle in the search for the Standard Model Higgs boson with the ATLAS detector",
        "experiment": "ATLAS",
        "sigma": 5.9,
        "mass_gev": 126.0,
        "properties_consistent_with_sm_higgs": True,
        "new_physics_closed": False,
    },
    "debunk10_lecanemab": {
        "source_type": "top_tier_alzheimers_trial",
        "source_url": "https://www.nejm.org/doi/full/10.1056/NEJMoa2212948",
        "title": "Lecanemab in Early Alzheimer's Disease",
        "study_design": "randomized_placebo_trial",
        "population": "early_alzheimers",
        "decline_reduction_percent": 27.0,
        "adverse_events_recorded": True,
    },
    "debunk10_semaglutide_select": {
        "source_type": "top_tier_cardiometabolic_trial",
        "source_url": "https://www.nejm.org/doi/full/10.1056/NEJMoa2307563",
        "title": "Semaglutide and Cardiovascular Outcomes in Obesity without Diabetes",
        "trial": "SELECT",
        "study_design": "randomized_placebo_trial",
        "population": "overweight_obesity_without_diabetes_with_cvd",
        "mace_reduction_percent": 20.0,
    },
    "debunk10_jwst_early_galaxy": {
        "source_type": "top_tier_astronomy_observation",
        "source_url": "https://arxiv.org/abs/2303.00306",
        "title": "A massive interacting galaxy 510 million years after the Big Bang",
        "instrument": "JWST",
        "redshift": 9.3127,
        "spectroscopic_confirmation": True,
        "standard_cosmology_refuted": False,
    },
    "debunk10_retracted_superconductor": {
        "source_type": "top_tier_retracted_superconductivity_claim",
        "source_url": "https://en.wikipedia.org/wiki/Room-temperature_superconductor",
        "title": "Room-temperature / near-ambient superconductivity claims",
        "retracted": True,
        "independent_replication": False,
        "zero_resistance": "contested",
        "meissner_effect": False,
    },
}


DEBUNK_10_EXAMPLES: list[tuple[str, str, str]] = [
    ("debunk10_sycamore_random_sampling", "quantum_sampling_advantage_supported", "ACCEPT"),
    (
        "debunk10_sycamore_random_sampling",
        "quantum_sampling_implies_useful_fault_tolerant_qc",
        "REWRITE",
    ),
    ("debunk10_micius_qkd", "satellite_qkd_demo_supported", "ACCEPT"),
    (
        "debunk10_micius_qkd",
        "satellite_qkd_implies_global_untrusted_quantum_internet",
        "REWRITE",
    ),
    ("debunk10_gpt3_fewshot", "gpt3_fewshot_benchmark_supported", "ACCEPT"),
    ("debunk10_gpt3_fewshot", "gpt3_implies_agi_or_reliable_reasoner", "REWRITE"),
    ("debunk10_crispr_embryo", "crispr_embryo_editing_research_supported", "ACCEPT"),
    ("debunk10_crispr_embryo", "crispr_embryo_editing_clinically_safe", "REWRITE"),
    ("debunk10_hgp_reference", "hgp_reference_genome_supported", "ACCEPT"),
    ("debunk10_hgp_reference", "hgp_solves_genetic_disease", "REWRITE"),
    ("debunk10_higgs_discovery", "higgs_discovery_supported", "ACCEPT"),
    ("debunk10_higgs_discovery", "higgs_discovery_completes_physics", "REWRITE"),
    ("debunk10_lecanemab", "lecanemab_slows_decline_supported", "ACCEPT"),
    ("debunk10_lecanemab", "lecanemab_cures_alzheimers", "REWRITE"),
    ("debunk10_semaglutide_select", "semaglutide_select_mace_supported", "ACCEPT"),
    (
        "debunk10_semaglutide_select",
        "semaglutide_solves_cardiovascular_disease",
        "REWRITE",
    ),
    ("debunk10_jwst_early_galaxy", "jwst_early_galaxy_observation_supported", "ACCEPT"),
    ("debunk10_jwst_early_galaxy", "jwst_overturns_big_bang", "REWRITE"),
    ("debunk10_retracted_superconductor", "room_temp_superconductor_established", "REJECT"),
]


CLAIM_TRANSITION_TRACES: dict[str, TraceResult] = {
    "upgrade_sycamore_to_useful_qc": {
        "current_claim": "task_specific_random_circuit_sampling_advantage",
        "attempted_claim": "useful_fault_tolerant_quantum_computing",
        "blocker": "benchmark_task_not_useful_fault_tolerant_workload",
        "required_upgrade_evidence": [
            "logical_error_budget",
            "fault_tolerant_operations",
            "useful_algorithmic_workload",
            "best_classical_baseline",
        ],
        "upgrade_evidence_present": False,
        "evidence_record_status": "active",
    },
    "upgrade_micius_to_untrusted_quantum_internet": {
        "current_claim": "trusted_relay_satellite_qkd_demo",
        "attempted_claim": "global_untrusted_quantum_internet",
        "blocker": "trusted_relay_topology",
        "required_upgrade_evidence": [
            "untrusted_repeater_or_device_independent_topology",
            "operational_network_segments",
            "attack_model",
            "key_rate_under_declared_assumptions",
        ],
        "upgrade_evidence_present": False,
        "evidence_record_status": "active",
    },
    "upgrade_gpt3_to_reliable_reasoning": {
        "current_claim": "few_shot_nlp_benchmark_gain",
        "attempted_claim": "reliable_general_reasoning",
        "blocker": "benchmark_improvement_not_robust_reasoning",
        "required_upgrade_evidence": [
            "pre_registered_reasoning_tasks",
            "adversarial_controls",
            "calibration",
            "out_of_distribution_evaluation",
        ],
        "upgrade_evidence_present": False,
        "evidence_record_status": "active",
    },
    "upgrade_crispr_embryo_to_clinical_safety": {
        "current_claim": "embryo_editing_research_signal",
        "attempted_claim": "clinically_safe_heritable_genome_editing",
        "blocker": "editing_fraction_not_long_term_clinical_safety",
        "required_upgrade_evidence": [
            "off_target_assay",
            "mosaicism_controls",
            "long_term_followup",
            "regulatory_scope",
        ],
        "upgrade_evidence_present": False,
        "evidence_record_status": "active",
    },
    "upgrade_hgp_to_disease_solution": {
        "current_claim": "reference_genome_sequence",
        "attempted_claim": "genetic_disease_mechanisms_solved",
        "blocker": "reference_sequence_not_function_or_therapy",
        "required_upgrade_evidence": [
            "variant_to_function_map",
            "causal_mechanism",
            "clinical_validation",
            "intervention_trial",
        ],
        "upgrade_evidence_present": False,
        "evidence_record_status": "active",
    },
    "upgrade_higgs_to_physics_complete": {
        "current_claim": "higgs_like_boson_discovered",
        "attempted_claim": "physics_complete",
        "blocker": "one_standard_model_particle_not_all_open_physics",
        "required_upgrade_evidence": [
            "precision_couplings",
            "dark_matter_resolution",
            "neutrino_mass_resolution",
            "quantum_gravity_or_declared_hypothesis_space_exclusions",
        ],
        "upgrade_evidence_present": False,
        "evidence_record_status": "active",
    },
    "upgrade_lecanemab_to_alzheimers_cure": {
        "current_claim": "slower_decline_early_alzheimers",
        "attempted_claim": "alzheimers_cure",
        "blocker": "slower_decline_not_reversal_or_cure",
        "required_upgrade_evidence": [
            "durable_functional_benefit",
            "disease_reversal_or_arrest_endpoint",
            "stage_stratified_efficacy",
            "net_safety_benefit",
        ],
        "upgrade_evidence_present": False,
        "evidence_record_status": "active",
    },
    "upgrade_semaglutide_to_cvd_solution": {
        "current_claim": "select_mace_reduction_defined_population",
        "attempted_claim": "cardiovascular_disease_solved",
        "blocker": "defined_population_risk_reduction_not_universal_solution",
        "required_upgrade_evidence": [
            "absolute_risk_by_population",
            "long_horizon_safety",
            "discontinuation_effects",
            "mechanism_separated_outcomes",
        ],
        "upgrade_evidence_present": False,
        "evidence_record_status": "active",
    },
    "upgrade_jwst_to_big_bang_refutation": {
        "current_claim": "early_high_redshift_massive_galaxy_observed",
        "attempted_claim": "big_bang_refuted",
        "blocker": "galaxy_formation_pressure_not_cosmology_refutation",
        "required_upgrade_evidence": [
            "replicated_spectroscopic_sample",
            "mass_systematics_controls",
            "lambda_cdm_model_comparison",
            "cosmological_parameter_exclusion",
        ],
        "upgrade_evidence_present": False,
        "evidence_record_status": "active",
    },
    "upgrade_retracted_superconductor_to_established": {
        "current_claim": "no_established_room_temperature_superconductor_claim",
        "attempted_claim": "room_temperature_superconductivity_established",
        "blocker": "retraction_and_no_independent_replication",
        "required_upgrade_evidence": [
            "independent_replication",
            "zero_resistance",
            "meissner_effect",
            "sample_structure_characterization",
        ],
        "upgrade_evidence_present": False,
        "evidence_record_status": "retracted",
    },
}


CLAIM_TRANSITION_EXAMPLES: list[tuple[str, str, str]] = [
    ("upgrade_sycamore_to_useful_qc", "claim_transition_gate", "REWRITE"),
    ("upgrade_micius_to_untrusted_quantum_internet", "claim_transition_gate", "REWRITE"),
    ("upgrade_gpt3_to_reliable_reasoning", "claim_transition_gate", "REWRITE"),
    ("upgrade_crispr_embryo_to_clinical_safety", "claim_transition_gate", "REWRITE"),
    ("upgrade_hgp_to_disease_solution", "claim_transition_gate", "REWRITE"),
    ("upgrade_higgs_to_physics_complete", "claim_transition_gate", "REWRITE"),
    ("upgrade_lecanemab_to_alzheimers_cure", "claim_transition_gate", "REWRITE"),
    ("upgrade_semaglutide_to_cvd_solution", "claim_transition_gate", "REWRITE"),
    ("upgrade_jwst_to_big_bang_refutation", "claim_transition_gate", "REWRITE"),
    ("upgrade_retracted_superconductor_to_established", "claim_transition_gate", "REJECT"),
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
    "validation_taxonomy_observed": {
        "minimum_fields": ["source_type", "surveyed_articles", "validation_categories"],
        "source_cluster": "Godoy/Dardatti regional validation survey",
    },
    "experimental_validation_dominates_practice": {
        "minimum_fields": ["surveyed_articles", "validation_counts.experimental"],
        "source_cluster": "Godoy/Dardatti regional validation survey",
    },
    "qualitative_experimental_agreement_reported": {
        "minimum_fields": ["reference_type=experiment", "agreement_claim_type=qualitative", "observables"],
        "source_cluster": "Romagnoli/Portapila/Morvan hydraulic jump simulation",
    },
    "agent_refinement_beats_specialist_rwp": {
        "minimum_fields": ["samples", "agent_rwp_wins", "rwp_pairs_agent_vs_specialist"],
        "source_cluster": "Rongzai Rietveld refinement agent",
    },
    "rwp_improvement_implies_structure_validated": {
        "minimum_fields": ["agent_refinement_beats_specialist_rwp", "independent_structure_reference"],
        "source_cluster": "Rongzai Rietveld refinement agent",
    },
    "scientist_contract_recorded": {
        "minimum_fields": ["scientist_authored_contract", "rubric_driven_judge"],
        "source_cluster": "AgentBuild Rietveld refinement",
    },
    "contract_failure_not_physical_failure": {
        "minimum_fields": ["frontier_case_status", "physical_validation_status"],
        "source_cluster": "AgentBuild Rietveld refinement",
    },
    "rct_primary_endpoint_supported": {
        "minimum_fields": ["study_design", "control_group", "primary_endpoint_met", "effect_ci_excludes_null"],
        "source_cluster": "US/UK top-tier randomized clinical trial",
    },
    "treatment_benefits_all_subgroups": {
        "minimum_fields": ["subgroup_effects"],
        "source_cluster": "US/UK top-tier randomized clinical trial",
    },
    "vaccine_efficacy_trial_supported": {
        "minimum_fields": ["observer_blind", "vaccine_cases", "placebo_cases", "vaccine_efficacy_percent"],
        "source_cluster": "top-tier vaccine efficacy trial",
    },
    "vaccine_prevents_all_infection_or_transmission": {
        "minimum_fields": ["endpoint", "transmission_or_asymptomatic_evidence"],
        "source_cluster": "top-tier vaccine efficacy trial",
    },
    "gravitational_wave_detection_supported": {
        "minimum_fields": ["detectors", "matched_filter_snr", "false_alarm_years", "noise_controls_pass"],
        "source_cluster": "LIGO gravitational-wave detection",
    },
    "gravitational_wave_population_rate_precise": {
        "minimum_fields": ["population_rate_credible_interval"],
        "source_cluster": "LIGO population inference",
    },
    "alphafold_casp14_accuracy_supported": {
        "minimum_fields": ["benchmark=CASP14", "blind_benchmark", "median_backbone_rmsd95_angstrom"],
        "source_cluster": "AlphaFold CASP14 blind benchmark",
    },
    "alphafold_solves_full_protein_folding": {
        "minimum_fields": ["mechanistic_folding_evidence", "all_contexts_validation"],
        "source_cluster": "AlphaFold overclaim control",
    },
    "dart_orbit_change_supported": {
        "minimum_fields": ["controlled_impact", "pre_post_orbit_measured", "independent_measurement_methods_agree"],
        "source_cluster": "NASA DART controlled impact",
    },
    "dart_solves_planetary_defense": {
        "minimum_fields": ["hazardous_asteroid_generalization", "multiple_target_classes"],
        "source_cluster": "DART overclaim control",
    },
    "quantum_sampling_advantage_supported": {
        "minimum_fields": ["task=random_circuit_sampling", "quantum_runtime_seconds", "classical_reference_runtime_seconds"],
        "source_cluster": "Sycamore random-circuit-sampling benchmark",
    },
    "quantum_sampling_implies_useful_fault_tolerant_qc": {
        "minimum_fields": ["fault_tolerant", "useful_application"],
        "source_cluster": "Sycamore overclaim control",
    },
    "satellite_qkd_demo_supported": {
        "minimum_fields": ["trusted_relay", "distance_km", "keys_exchanged"],
        "source_cluster": "Micius satellite QKD demonstration",
    },
    "satellite_qkd_implies_global_untrusted_quantum_internet": {
        "minimum_fields": ["untrusted_repeater", "global_network_deployed"],
        "source_cluster": "Micius overclaim control",
    },
    "gpt3_fewshot_benchmark_supported": {
        "minimum_fields": ["model=GPT-3", "few_shot_setting", "benchmarks_improved"],
        "source_cluster": "GPT-3 few-shot NLP benchmark",
    },
    "gpt3_implies_agi_or_reliable_reasoner": {
        "minimum_fields": ["general_reasoning_reliability", "agi_evidence"],
        "source_cluster": "GPT-3 overclaim control",
    },
    "crispr_embryo_editing_research_supported": {
        "minimum_fields": ["system=CRISPR-Cas9", "embryo_research", "correction_efficiency_percent"],
        "source_cluster": "human embryo CRISPR research",
    },
    "crispr_embryo_editing_clinically_safe": {
        "minimum_fields": ["clinical_pregnancy", "long_term_safety"],
        "source_cluster": "human embryo CRISPR overclaim control",
    },
    "hgp_reference_genome_supported": {
        "minimum_fields": ["project=Human Genome Project", "reference_sequence", "euchromatic_coverage_percent"],
        "source_cluster": "Human Genome Project reference sequence",
    },
    "hgp_solves_genetic_disease": {
        "minimum_fields": ["disease_mechanisms_solved", "therapeutic_validation"],
        "source_cluster": "HGP overclaim control",
    },
    "higgs_discovery_supported": {
        "minimum_fields": ["experiment", "sigma>=5", "mass_gev", "properties_consistent_with_sm_higgs"],
        "source_cluster": "ATLAS/CMS Higgs discovery",
    },
    "higgs_discovery_completes_physics": {
        "minimum_fields": ["new_physics_closed"],
        "source_cluster": "Higgs overclaim control",
    },
    "lecanemab_slows_decline_supported": {
        "minimum_fields": ["study_design", "population=early_alzheimers", "decline_reduction_percent", "adverse_events_recorded"],
        "source_cluster": "lecanemab randomized trial",
    },
    "lecanemab_cures_alzheimers": {
        "minimum_fields": ["cure_endpoint", "reversal_endpoint", "broad_stage_efficacy"],
        "source_cluster": "lecanemab overclaim control",
    },
    "semaglutide_select_mace_supported": {
        "minimum_fields": ["trial=SELECT", "population", "mace_reduction_percent"],
        "source_cluster": "semaglutide SELECT cardiovascular outcomes trial",
    },
    "semaglutide_solves_cardiovascular_disease": {
        "minimum_fields": ["all_cvd_populations", "disease_elimination"],
        "source_cluster": "semaglutide overclaim control",
    },
    "jwst_early_galaxy_observation_supported": {
        "minimum_fields": ["instrument=JWST", "redshift", "spectroscopic_confirmation"],
        "source_cluster": "JWST early-galaxy observation",
    },
    "jwst_overturns_big_bang": {
        "minimum_fields": ["standard_cosmology_refuted"],
        "source_cluster": "JWST overclaim control",
    },
    "room_temp_superconductor_established": {
        "minimum_fields": ["independent_replication", "zero_resistance", "meissner_effect", "retracted"],
        "source_cluster": "room-temperature superconductivity overclaim control",
    },
    "claim_transition_gate": {
        "minimum_fields": ["current_claim", "attempted_claim", "blocker", "required_upgrade_evidence", "upgrade_evidence_present"],
        "source_cluster": "CAPAS claim upgrade roadmap",
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
    for trace_id, claim_id, expected in REGIONAL_REAL_EXAMPLES:
        actual, reason = CLAIM_RULES[claim_id](REGIONAL_REAL_TRACES[trace_id])
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
    for trace_id, claim_id, expected in US_UK_EXAMPLES:
        actual, reason = CLAIM_RULES[claim_id](US_UK_REAL_TRACES[trace_id])
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
    for trace_id, claim_id, expected in DEBUNK_10_EXAMPLES:
        actual, reason = CLAIM_RULES[claim_id](DEBUNK_10_TRACES[trace_id])
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
    for trace_id, claim_id, expected in CLAIM_TRANSITION_EXAMPLES:
        actual, reason = CLAIM_RULES[claim_id](CLAIM_TRANSITION_TRACES[trace_id])
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
            "regional_real_checks": len(REGIONAL_REAL_EXAMPLES),
            "us_uk_canonical_checks": len(US_UK_EXAMPLES),
            "debunk_10_more_checks": len(DEBUNK_10_EXAMPLES),
            "debunk_10_more_overclaims": 10,
            "claim_transition_checks": len(CLAIM_TRANSITION_EXAMPLES),
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
