# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from router import CostBudget, EngineSpec, Workload, run_with_trace  # noqa: E402


ENGINE_PATH = ROOT / "integrations" / "capas_public_evidence_engines.py"
ADVERSARIAL_ENGINE_PATH = ROOT / "integrations" / "universal_invariant_adversarial_engines.py"
OUT_DIR = ROOT / "benchmarks" / "gold_traces"
AUDIT_CSV = ROOT / "audits" / "gold_trace_audit_template.csv"

UNIVERSAL_INVARIANT_COVERAGE = {
    "universal_invariant_adversarial_failure",
    "universal_invariant_local_catches_anchor_not_needed",
    "universal_invariant_both_oracles_catch",
    "universal_invariant_non_heisenberg_adversarial_failure",
    "universal_invariant_no_anchor_control",
    "universal_invariant_scaling_law_adversarial_failure",
    "universal_invariant_scaling_law_positive_control",
    "universal_invariant_scaling_law_local_catches",
    "universal_invariant_scaling_law_simulation_generated",
    "universal_invariant_scaling_law_randomized_adversarial",
    "universal_invariant_scaling_law_agent_generated_adversarial",
    "claim_transition_bounded_agent_scientific_reasoning",
}


TRACE_SPECS = [
    ("trace_001", "hadamard_square_returns_zero", {}, "analytic_success"),
    ("trace_002", "bell_entropy_ln2", {}, "analytic_success"),
    ("trace_003", "product_entropy_zero", {}, "analytic_success"),
    ("trace_004", "ghz_entropy_ln2", {"n_qubits": 3}, "analytic_success"),
    ("trace_005", "born_rule_plus_state", {}, "analytic_success"),
    ("trace_006", "heisenberg_dimer_ground_state", {"J": 1.0}, "analytic_success"),
    ("trace_007", "transverse_field_ising_two_spin_ground_state", {"J": 1.0, "h": 0.7}, "analytic_success"),
    ("trace_008", "particle_in_box_energy", {"n": 1, "mass": 1.0, "length": 1.0, "hbar": 1.0}, "analytic_success"),
    ("trace_009", "harmonic_oscillator_energy", {"n": 0, "omega": 1.0, "hbar": 1.0}, "analytic_success"),
    ("trace_010", "pauli_z_ground_energy", {"field": 1.25}, "analytic_success"),
    ("trace_011", "bell_entropy_cross_sim", {}, "cross_sim_success"),
    ("trace_018", "bell_entropy_scipy_cross_library", {}, "cross_library_success"),
    ("trace_019", "assignment_to_ising_function_level", {}, "combinatorial_optimization_function_level"),
    ("trace_020", "assignment_to_ising_degenerate_function_level", {}, "combinatorial_optimization_degenerate_function_level"),
    ("trace_021", "h2_sto3g_experimental_reference", {}, "quantum_chemistry_experimental_reference"),
    ("trace_022", "h2_ccpvdz_experimental_reference", {}, "quantum_chemistry_experimental_reference_improved_basis"),
    ("trace_023", "h2_ccpvtz_experimental_reference", {}, "quantum_chemistry_experimental_reference_larger_basis"),
    ("trace_024", "h2_ccpvtz_reference_definition_corrected", {}, "quantum_chemistry_reference_definition_corrected"),
    ("trace_025", "h2o_sto3g_electronic_vibrational_reference", {}, "quantum_chemistry_polyatomic_electronic_vibrational"),
    ("trace_026", "ch4_sto3g_electronic_vibrational_reference", {}, "quantum_chemistry_larger_polyatomic_electronic_vibrational"),
    ("trace_027", "h2_basis_convergence_to_experiment", {}, "quantum_chemistry_basis_convergence_to_experiment"),
    ("trace_028", "heisenberg_wrong_sign_passes_local_properties", {}, "universal_invariant_adversarial_failure"),
    ("trace_029", "heisenberg_nonhermitian_local_catches_anchor_not_needed", {}, "universal_invariant_local_catches_anchor_not_needed"),
    ("trace_030", "heisenberg_scaled_coupling_both_oracles_catch", {}, "universal_invariant_both_oracles_catch"),
    ("trace_031", "bell_product_state_passes_local_properties_but_fails_entropy", {}, "universal_invariant_non_heisenberg_adversarial_failure"),
    ("trace_032", "normalized_random_state_without_universal_anchor", {}, "universal_invariant_no_anchor_control"),
    ("trace_033", "ising_gap_wrong_exponent_passes_local_monotonicity", {}, "universal_invariant_scaling_law_adversarial_failure"),
    ("trace_034", "ising_gap_correct_exponent_noisy_passes_scaling_anchor", {}, "universal_invariant_scaling_law_positive_control"),
    ("trace_035", "ising_gap_constant_sequence_local_catches_before_scaling", {}, "universal_invariant_scaling_law_local_catches"),
    ("trace_036", "ising_gap_exact_diagonalization_scaling_anchor", {}, "universal_invariant_scaling_law_simulation_generated"),
    ("trace_037", "ising_gap_randomized_wrong_exponent_family", {}, "universal_invariant_scaling_law_randomized_adversarial"),
    ("trace_038", "ising_gap_scripted_agent_wrong_exponent", {}, "universal_invariant_scaling_law_agent_generated_adversarial"),
    ("trace_039", "bounded_agent_scientific_reasoning_upgrade_evidence", {}, "claim_transition_bounded_agent_scientific_reasoning"),
    ("trace_012", "unverified_variational_energy", {}, "no_evidence_success"),
    ("trace_013", "deliberately_failing_engine", {}, "backend_failed"),
    ("trace_015", "quimb_mps_estimated_bound", {"n": 60, "depth": 6, "max_bond": 8, "seed": 1}, "estimated_bound_candidate"),
    ("trace_016", "schmidt_truncation_formal_bound", {"n_qubits": 4, "keep_rank": 2, "seed": 7}, "formal_bound_success"),
    ("trace_017", "multi_step_schmidt_composition_bound", {"n_qubits": 6, "keep_rank": 2, "seed": 11}, "formal_bound_composition_success"),
]


def _engine_path_for(function_name: str) -> Path:
    if function_name in {
        "heisenberg_wrong_sign_passes_local_properties",
        "heisenberg_nonhermitian_local_catches_anchor_not_needed",
        "heisenberg_scaled_coupling_both_oracles_catch",
        "bell_product_state_passes_local_properties_but_fails_entropy",
        "normalized_random_state_without_universal_anchor",
        "ising_gap_wrong_exponent_passes_local_monotonicity",
        "ising_gap_correct_exponent_noisy_passes_scaling_anchor",
        "ising_gap_constant_sequence_local_catches_before_scaling",
        "ising_gap_exact_diagonalization_scaling_anchor",
        "ising_gap_randomized_wrong_exponent_family",
        "ising_gap_scripted_agent_wrong_exponent",
        "bounded_agent_scientific_reasoning_upgrade_evidence",
    }:
        return ADVERSARIAL_ENGINE_PATH
    return ENGINE_PATH


def _rejected_workload() -> Workload:
    return Workload(
        kind="dense",
        n_qubits=40,
        budget=CostBudget(memory_budget_bytes=2**28, safety_factor=0.5),
    )


def main() -> None:
    if not ENGINE_PATH.exists():
        raise SystemExit(
            "Full historical corpus generation requires private/local evidence "
            "engine adapters that are intentionally not shipped in the public "
            "CAPAS package. Run scripts/build_evidence_corpus.py to validate "
            "the published trace corpus instead."
        )
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    audit_rows = []
    for trace_id, fn, kwargs, coverage_case in TRACE_SPECS:
        engine_path = _engine_path_for(fn)
        workload = Workload(
            kind="dense",
            n_qubits=2,
            engine=EngineSpec(
                module_path=str(engine_path),
                function_name=fn,
                kwargs=kwargs,
                engine_id=f"{engine_path.stem}.{fn}",
            ),
        )
        result, trace = run_with_trace(workload, raise_on_error=False)
        if coverage_case in UNIVERSAL_INVARIANT_COVERAGE:
            assert result is not None
            summary = result["result"]
            assert "local_property_tests_pass" in summary
            assert "local_oracle_caught" in summary
            assert "universal_anchor_pass" in summary
            assert "invariant_caught" in summary
            assert summary["claim_scope"]
            assert summary["anchor_mode"] in {"absolute_anchor", "none"}
            if coverage_case == "universal_invariant_adversarial_failure":
                assert summary["anchor_mode"] == "absolute_anchor"
                assert summary["local_property_tests_pass"] is True
                assert summary["universal_anchor_pass"] is False
                assert summary["invariant_caught"] is True
            elif coverage_case == "universal_invariant_local_catches_anchor_not_needed":
                assert summary["anchor_mode"] == "absolute_anchor"
                assert summary["local_property_tests_pass"] is False
                assert summary["local_oracle_caught"] is True
                assert summary["universal_anchor_pass"] == "not_evaluated_local_oracle_failed"
            elif coverage_case == "universal_invariant_both_oracles_catch":
                assert summary["anchor_mode"] == "absolute_anchor"
                assert summary["local_property_tests_pass"] is False
                assert summary["local_oracle_caught"] is True
                assert summary["universal_anchor_pass"] is False
                assert summary["invariant_caught"] is True
            elif coverage_case == "universal_invariant_non_heisenberg_adversarial_failure":
                assert summary["anchor_mode"] == "absolute_anchor"
                assert summary["local_property_tests_pass"] is True
                assert summary["universal_anchor_pass"] is False
                assert summary["invariant_caught"] is True
            elif coverage_case == "universal_invariant_no_anchor_control":
                assert summary["anchor_mode"] == "none"
                assert summary["local_property_tests_pass"] is True
                assert summary["universal_anchor_pass"] == "not_applicable_no_universal_anchor"
                assert summary["invariant_caught"] is False
            elif coverage_case == "universal_invariant_scaling_law_adversarial_failure":
                assert summary["anchor_kind"] == "absolute_scaling_law"
                assert summary["anchor_mode"] == "absolute_anchor"
                assert summary["local_property_tests_pass"] is True
                assert summary["universal_anchor_pass"] is False
                assert summary["invariant_caught"] is True
                assert summary["abs_error"] > summary["exponent_tolerance"]
            elif coverage_case == "universal_invariant_scaling_law_positive_control":
                assert summary["anchor_kind"] == "absolute_scaling_law"
                assert summary["anchor_mode"] == "absolute_anchor"
                assert summary["local_property_tests_pass"] is True
                assert summary["universal_anchor_pass"] is True
                assert summary["invariant_caught"] is False
                assert summary["abs_error"] <= summary["exponent_tolerance"]
            elif coverage_case == "universal_invariant_scaling_law_local_catches":
                assert summary["anchor_kind"] == "absolute_scaling_law"
                assert summary["anchor_mode"] == "absolute_anchor"
                assert summary["local_property_tests_pass"] is False
                assert summary["local_oracle_caught"] is True
                assert summary["universal_anchor_pass"] == "not_evaluated_local_oracle_failed"
            elif coverage_case == "universal_invariant_scaling_law_simulation_generated":
                assert summary["anchor_kind"] == "absolute_scaling_law"
                assert summary["anchor_mode"] == "absolute_anchor"
                assert summary["local_property_tests_pass"] is True
                assert summary["universal_anchor_pass"] is True
                assert summary["invariant_caught"] is False
                assert summary["abs_error"] <= summary["exponent_tolerance"]
                assert "Exact diagonalization" in summary["finite_size_notes"]
            elif coverage_case == "universal_invariant_scaling_law_randomized_adversarial":
                assert summary["anchor_kind"] == "absolute_scaling_law"
                assert summary["anchor_mode"] == "absolute_anchor"
                assert summary["local_property_tests_pass"] is True
                assert summary["universal_anchor_pass"] is False
                assert summary["invariant_caught"] is True
                assert summary["variant_count"] == 8
                assert len(summary["randomized_variants"]) == 8
                assert summary["min_abs_error"] > summary["exponent_tolerance"]
            elif coverage_case == "universal_invariant_scaling_law_agent_generated_adversarial":
                assert summary["anchor_kind"] == "absolute_scaling_law"
                assert summary["anchor_mode"] == "absolute_anchor"
                assert summary["agent_kind"] == "scripted_agent"
                assert summary["agent_id"] == "scripted_scaling_agent_v1"
                assert summary["local_property_tests_pass"] is True
                assert summary["universal_anchor_pass"] is False
                assert summary["invariant_caught"] is True
                assert summary["abs_error"] > summary["exponent_tolerance"]
            elif coverage_case == "claim_transition_bounded_agent_scientific_reasoning":
                assert summary["anchor_kind"] == "absolute_scaling_law"
                assert summary["anchor_mode"] == "absolute_anchor"
                assert summary["agent_kind"] == "scripted_agent_with_motor_backend"
                assert summary["local_property_tests_pass"] is True
                assert summary["universal_anchor_pass"] is True
                assert summary["invariant_caught"] is False
                assert summary["upgrade_evidence_present"] is True
                assert summary["abs_error"] <= summary["exponent_tolerance"]
        elif coverage_case not in {"backend_failed", "no_evidence_success", "estimated_bound_candidate"}:
            assert result is not None
            assert result["result"]["abs_error"] < 1e-9
        payload = {
            "trace_id": trace_id,
            "coverage_case": coverage_case,
            "result": result,
            "trace": trace.as_dict(),
            "trace_hash": trace.hash(),
        }
        (OUT_DIR / f"{trace_id}.json").write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

        if result is None:
            audit_rows.append({
                "trace_id": trace_id,
                "source_file": str(OUT_DIR / f"{trace_id}.json"),
                "engine_id": f"{engine_path.stem}.{fn}",
                "engine_hash": "",
                "hash_gate_pass": "yes",
                "output_value": "",
                "output_units": "",
                "output_correct": "no",
                "output_correct_evidence": "backend failed before producing a result",
                "reasoning_claim": "failed trace captured as provenance, not training gold",
                "inference_blind_judge": "no",
                "inference_correct": "no",
                "inference_correct_evidence": "no result to infer from",
                "physical_evidence_level": "none",
                "physical_evidence_detail": trace.error or "backend failed",
                "benchmark_family": "FailureCoverage",
                "reference_truth": "none",
                "verification_independence": "none",
                "coverage_case": coverage_case,
                "risk_level": "high",
                "decision": "reject",
                "notes": "Intentional failed trace; validates that the format seals failures honestly.",
            })
            continue

        physical_level = result["result"]["physical_evidence_level"]
        output_correct = "yes" if result["result"].get("abs_error") in (None, 0.0) or (
            isinstance(result["result"].get("abs_error"), (int, float)) and result["result"]["abs_error"] < 1e-9
        ) else "no"
        if physical_level in {"none", "estimated_bound"}:
            output_correct = "unknown"
        if coverage_case in {
            "universal_invariant_scaling_law_positive_control",
            "universal_invariant_scaling_law_simulation_generated",
        }:
            output_correct = "yes"
        elif coverage_case in UNIVERSAL_INVARIANT_COVERAGE:
            output_correct = "no"
        abs_error = result["result"].get("abs_error")
        abs_error_text = f"{abs_error:.3e}" if isinstance(abs_error, (int, float)) else "n/a"

        is_universal_invariant_control = coverage_case in UNIVERSAL_INVARIANT_COVERAGE
        audit_rows.append({
            "trace_id": trace_id,
            "source_file": str(OUT_DIR / f"{trace_id}.json"),
            "engine_id": result["engine_id"],
            "engine_hash": result["module_sha256"],
            "hash_gate_pass": "yes",
            "output_value": json.dumps(result["result"]["value"], sort_keys=True),
            "output_units": result["result"]["units"],
            "output_correct": output_correct,
            "output_correct_evidence": f"{result['result']['observable']}: expected {result['result']['expected']}, abs_error={abs_error_text}",
            "reasoning_claim": result["result"]["physical_evidence_detail"],
            "inference_blind_judge": "no" if is_universal_invariant_control else "hold" if physical_level in {"analytic", "cross_sim", "estimated_bound", "formal_bound", "experimental"} else "no",
            "inference_correct": "no" if is_universal_invariant_control else "unknown" if physical_level in {"analytic", "cross_sim", "estimated_bound", "formal_bound", "experimental"} else "no",
            "inference_correct_evidence": "",
            "physical_evidence_level": result["result"]["physical_evidence_level"],
            "physical_evidence_detail": result["result"]["physical_evidence_detail"],
            "benchmark_family": result["result"].get("benchmark_family", "quantum_engine_invariant"),
            "reference_truth": result["result"].get("reference_truth", "closed_form_quantum_identity"),
            "verification_independence": result["result"].get("verification_independence", "analytic_no_solver"),
            "coverage_case": coverage_case,
            "risk_level": "high" if is_universal_invariant_control else "low",
            "decision": "reject" if is_universal_invariant_control else "hold" if physical_level in {"analytic", "cross_sim", "estimated_bound", "formal_bound", "experimental"} else "reject",
            "notes": (
                "Universal-invariant matrix/control trace; rejects generated output for training while preserving coverage evidence."
                if is_universal_invariant_control
                else
                "Generated by traced quantum_engine invariant; needs blind inference review before accept."
                if physical_level in {"analytic", "cross_sim"}
                else "Experimental-reference trace; records solver/model error separation and needs blind inference review."
                if physical_level == "experimental"
                else "Formal truncation certificate; scope is explicit and does not imply an observable certificate."
                if physical_level == "formal_bound"
                else "Estimated-bound trace; useful evidence metadata, but not a formal certificate."
                if physical_level == "estimated_bound"
                else "Kept as universal coverage trace; not training gold because evidence is none."
            ),
        })

    rejected_trace_id = "trace_014"
    rejected_workload = _rejected_workload()
    result, trace = run_with_trace(rejected_workload)
    assert result is None
    payload = {
        "trace_id": rejected_trace_id,
        "coverage_case": "rejected_by_router",
        "result": result,
        "trace": trace.as_dict(),
        "trace_hash": trace.hash(),
    }
    (OUT_DIR / f"{rejected_trace_id}.json").write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    audit_rows.append({
        "trace_id": rejected_trace_id,
        "source_file": str(OUT_DIR / f"{rejected_trace_id}.json"),
        "engine_id": "router.memory_guard",
        "engine_hash": "",
        "hash_gate_pass": "yes",
        "output_value": "",
        "output_units": "",
        "output_correct": "no",
        "output_correct_evidence": "router rejected execution before materializing dense statevector",
        "reasoning_claim": trace.decision_reason or "",
        "inference_blind_judge": "no",
        "inference_correct": "no",
        "inference_correct_evidence": "rejection trace; no scientific output",
        "physical_evidence_level": "none",
        "physical_evidence_detail": trace.decision_reason or "route rejected",
        "benchmark_family": "RouterGuard",
        "reference_truth": "memory_budget_guard",
        "verification_independence": "none",
        "coverage_case": "rejected_by_router",
        "risk_level": "high",
        "decision": "reject",
        "notes": "Intentional rejected trace; validates that the format seals non-execution honestly.",
    })

    extra_fields = ["benchmark_family", "reference_truth", "verification_independence", "coverage_case"]
    # Preserve existing audit judgments, and append new generated trace rows.
    with AUDIT_CSV.open(newline="", encoding="utf-8") as f:
        existing = list(csv.DictReader(f))
        fieldnames = [name for name in (existing[0].keys() if existing else audit_rows[0].keys()) if name]
    for field in extra_fields:
        if field not in fieldnames:
            fieldnames.append(field)
    by_id = {r["trace_id"]: r for r in audit_rows}
    merged = []
    for row in existing:
        clean = {k: row.get(k, "") for k in fieldnames}
        if clean["trace_id"] in by_id:
            clean.update(by_id[clean["trace_id"]])
        merged.append(clean)
    seen = {row["trace_id"] for row in merged}
    for trace_id in sorted(set(by_id) - seen):
        clean = {k: "" for k in fieldnames}
        clean.update(by_id[trace_id])
        merged.append(clean)
    with AUDIT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(merged)

    print(f"wrote {len(audit_rows)} gold traces to {OUT_DIR}")
    print(f"updated {AUDIT_CSV}")


if __name__ == "__main__":
    main()
