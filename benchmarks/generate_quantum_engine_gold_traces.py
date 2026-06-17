from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from router import CostBudget, EngineSpec, Workload, run_with_trace  # noqa: E402


ENGINE_PATH = ROOT / "integrations" / "physics_magnitude_gold_engines.py"
OUT_DIR = ROOT / "benchmarks" / "gold_traces"
AUDIT_CSV = ROOT / "audits" / "gold_trace_audit_template.csv"


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
    ("trace_012", "unverified_variational_energy", {}, "no_evidence_success"),
    ("trace_013", "deliberately_failing_engine", {}, "backend_failed"),
    ("trace_015", "quimb_mps_estimated_bound", {"n": 60, "depth": 6, "max_bond": 8, "seed": 1}, "estimated_bound_candidate"),
    ("trace_016", "schmidt_truncation_formal_bound", {"n_qubits": 4, "keep_rank": 2, "seed": 7}, "formal_bound_success"),
    ("trace_017", "multi_step_schmidt_composition_bound", {"n_qubits": 6, "keep_rank": 2, "seed": 11}, "formal_bound_composition_success"),
]


def _rejected_workload() -> Workload:
    return Workload(
        kind="dense",
        n_qubits=40,
        budget=CostBudget(memory_budget_bytes=2**28, safety_factor=0.5),
    )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    audit_rows = []
    for trace_id, fn, kwargs, coverage_case in TRACE_SPECS:
        workload = Workload(
            kind="dense",
            n_qubits=2,
            engine=EngineSpec(
                module_path=str(ENGINE_PATH),
                function_name=fn,
                kwargs=kwargs,
                engine_id=f"physics_magnitude_quantum_engine.{fn}",
            ),
        )
        result, trace = run_with_trace(workload, raise_on_error=False)
        if coverage_case not in {"backend_failed", "no_evidence_success", "estimated_bound_candidate"}:
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
                "engine_id": f"physics_magnitude_quantum_engine.{fn}",
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
        abs_error = result["result"].get("abs_error")
        abs_error_text = f"{abs_error:.3e}" if isinstance(abs_error, (int, float)) else "n/a"

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
            "inference_blind_judge": "hold" if physical_level in {"analytic", "cross_sim", "estimated_bound", "formal_bound"} else "no",
            "inference_correct": "unknown" if physical_level in {"analytic", "cross_sim", "estimated_bound", "formal_bound"} else "no",
            "inference_correct_evidence": "",
            "physical_evidence_level": result["result"]["physical_evidence_level"],
            "physical_evidence_detail": result["result"]["physical_evidence_detail"],
            "benchmark_family": result["result"].get("benchmark_family", "quantum_engine_invariant"),
            "reference_truth": result["result"].get("reference_truth", "closed_form_quantum_identity"),
            "verification_independence": result["result"].get("verification_independence", "analytic_no_solver"),
            "coverage_case": coverage_case,
            "risk_level": "low",
            "decision": "hold" if physical_level in {"analytic", "cross_sim", "estimated_bound", "formal_bound"} else "reject",
            "notes": (
                "Generated by traced quantum_engine invariant; needs blind inference review before accept."
                if physical_level in {"analytic", "cross_sim"}
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
