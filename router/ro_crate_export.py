from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .prov_export import run_trace_to_prov_json
from .trace import RunTrace, stable_hash


RO_CRATE_CONTEXT = "https://w3id.org/ro/crate/1.1/context"
RO_CRATE_CONFORMS_TO = "https://w3id.org/ro/crate/1.1"
WORKFLOW_RUN_CONTEXT = "https://w3id.org/ro/terms/workflow-run/context"
PROCESS_RUN_CRATE_PROFILE = "https://w3id.org/ro/wfrun/process/0.5"
WORKFLOW_RUN_CRATE_PROFILE = "https://w3id.org/ro/wfrun/workflow/0.5"
WORKFLOW_RO_CRATE_PROFILE = "https://w3id.org/workflowhub/workflow-ro-crate/1.0"
CAPAS_PROFILE = "https://example.org/capas-inteligentes/ro-crate/physical-evidence/0.1"
CAPAS_WORKFLOW_ID = "workflow/capas-costurero-run.cwl"
CAPAS_SOFTWARE_ID = "software:capas-costurero"
WORKLOAD_ID = "entity:workload"


def run_trace_to_ro_crate_metadata(
    trace: RunTrace,
    *,
    trace_file: str,
    prov_file: str | None = None,
    crate_dir: Path | None = None,
) -> dict[str, Any]:
    """Export a RunTrace as RO-Crate JSON-LD metadata.

    This does not replace Workflow Run RO-Crate. It uses RO-Crate as the
    packaging standard and adds a small CAPAS profile entity for physical
    evidence semantics.
    """

    trace_id = f"trace:{trace.hash()[:16]}"
    result_id = f"{trace_id}:result"
    decision_id = f"{trace_id}:routing-decision"
    evidence_id = f"{trace_id}:physical-evidence"
    root_id = "./"
    run_status = _action_status(trace)
    start_time, end_time = _event_time_bounds(trace)
    has_part = [
        {"@id": trace_file},
        {"@id": CAPAS_WORKFLOW_ID},
        {"@id": CAPAS_SOFTWARE_ID},
        {"@id": WORKLOAD_ID},
        {"@id": decision_id},
    ]
    if trace.result_hash:
        has_part.append({"@id": result_id})

    graph: list[dict[str, Any]] = [
        {
            "@id": "ro-crate-metadata.json",
            "@type": "CreativeWork",
            "conformsTo": [
                {"@id": RO_CRATE_CONFORMS_TO},
                {"@id": PROCESS_RUN_CRATE_PROFILE},
                {"@id": WORKFLOW_RUN_CRATE_PROFILE},
                {"@id": WORKFLOW_RO_CRATE_PROFILE},
                {"@id": CAPAS_PROFILE},
            ],
            "about": {"@id": root_id},
        },
        {
            "@id": root_id,
            "@type": "Dataset",
            "name": "CAPAS traced scientific computation crate",
            "description": (
                "RO-Crate package containing a sealed RunTrace, optional PROV export, "
                "routing decision, runtime context, and CAPAS physical evidence metadata."
            ),
            "hasPart": has_part,
            "conformsTo": [
                {"@id": RO_CRATE_CONFORMS_TO},
                {"@id": PROCESS_RUN_CRATE_PROFILE},
                {"@id": WORKFLOW_RUN_CRATE_PROFILE},
                {"@id": WORKFLOW_RO_CRATE_PROFILE},
                {"@id": CAPAS_PROFILE},
            ],
            "mainEntity": {"@id": CAPAS_WORKFLOW_ID},
            "mentions": {"@id": trace_id},
            "datePublished": end_time,
            "capas:traceHash": trace.hash(),
            "capas:workloadHash": trace.workload_hash,
            "capas:workflowRunCrateAlignment": "shape-compatible-with-workflow-run-crate-0.5",
        },
        {
            "@id": PROCESS_RUN_CRATE_PROFILE,
            "@type": "CreativeWork",
            "name": "Process Run Crate",
            "version": "0.5",
        },
        {
            "@id": WORKFLOW_RUN_CRATE_PROFILE,
            "@type": "CreativeWork",
            "name": "Workflow Run Crate",
            "version": "0.5",
        },
        {
            "@id": WORKFLOW_RO_CRATE_PROFILE,
            "@type": "CreativeWork",
            "name": "Workflow RO-Crate",
            "version": "1.0",
        },
        {
            "@id": CAPAS_PROFILE,
            "@type": "CreativeWork",
            "name": "CAPAS Physical Evidence Profile",
            "version": "0.1",
            "description": (
                "Draft profile extending Workflow Run RO-Crate-style traces with "
                "first-class physical evidence, witness independence, reference truth, "
                "and explicit success/no-evidence/failure/rejection states."
            ),
        },
        {
            "@id": trace_file,
            "@type": ["File", "DigitalDocument"],
            "name": "Sealed CAPAS RunTrace",
            "encodingFormat": "application/json",
            "sha256": _file_sha256_if_exists(trace_file, crate_dir),
            "about": {"@id": trace_id},
        },
        {
            "@id": trace_id,
            "@type": "CreateAction",
            "name": "CAPAS costurero traced run",
            "agent": {"@id": CAPAS_SOFTWARE_ID},
            "instrument": {"@id": CAPAS_WORKFLOW_ID},
            "object": {"@id": WORKLOAD_ID},
            "result": {"@id": result_id} if trace.result_hash else None,
            "actionStatus": run_status,
            "startTime": start_time,
            "endTime": end_time,
            "capas:routingDecision": {"@id": decision_id},
            "capas:traceHash": trace.hash(),
            "capas:traceSchemaVersion": trace.trace_schema_version,
            "capas:hashAlgorithm": trace.hash_algorithm,
            "capas:error": trace.error,
            "capas:decisionRoute": trace.decision_route,
            "capas:decisionReason": trace.decision_reason,
            "capas:evidenceStatus": None,
        },
        {
            "@id": CAPAS_WORKFLOW_ID,
            "@type": ["File", "SoftwareSourceCode", "ComputationalWorkflow"],
            "name": "CAPAS costurero workflow",
            "description": (
                "Workflow plan that ingests a scientific workload, records runtime context, "
                "estimates routing cost, executes or skips the selected engine, and attaches "
                "CAPAS physical-evidence metadata."
            ),
            "programmingLanguage": "Python",
            "input": {"@id": "parameter:workload"},
            "output": {"@id": "parameter:result"},
            "capas:traceSchemaVersion": trace.trace_schema_version,
        },
        {
            "@id": "parameter:workload",
            "@type": "FormalParameter",
            "name": "Scientific workload",
            "description": "Structured scientific workload routed by the CAPAS costurero.",
            "additionalType": "Dataset",
        },
        {
            "@id": "parameter:result",
            "@type": "FormalParameter",
            "name": "Result summary or skipped/failure state",
            "description": "Structured result summary, skipped state, or failure state.",
            "additionalType": "Dataset",
        },
        {
            "@id": CAPAS_SOFTWARE_ID,
            "@type": "SoftwareApplication",
            "name": "CAPAS INTELIGENTES costurero",
            "applicationCategory": "Scientific provenance and evidence tracing",
        },
        {
            "@id": WORKLOAD_ID,
            "@type": "Dataset",
            "name": "Workload summary",
            "capas:workloadHash": trace.workload_hash,
            "capas:summary": trace.workload_summary,
            "exampleOfWork": {"@id": "parameter:workload"},
        },
        {
            "@id": decision_id,
            "@type": "Thing",
            "name": "Routing decision",
            "capas:route": trace.decision_route,
            "capas:reason": trace.decision_reason,
        },
    ]

    if prov_file:
        graph[1]["hasPart"].append({"@id": prov_file})
        graph.append(
            {
                "@id": prov_file,
                "@type": ["File", "DigitalDocument"],
                "name": "W3C PROV-shaped export",
                "encodingFormat": "application/json",
                "sha256": _file_sha256_if_exists(prov_file, crate_dir),
            }
        )

    if trace.result_hash:
        graph.append(
            {
                "@id": result_id,
                "@type": "Dataset",
                "name": "Result summary",
                "capas:resultHash": trace.result_hash,
                "capas:summary": trace.result_summary,
                "exampleOfWork": {"@id": "parameter:result"},
            }
        )

    evidence = _physical_evidence_from_trace(trace)
    evidence_status = _evidence_status(trace, evidence)
    for node in graph:
        if node.get("@id") == root_id:
            node["capas:evidenceStatus"] = evidence_status
        if node.get("@id") == trace_id:
            node["capas:evidenceStatus"] = evidence_status
            break
    if evidence and evidence_status == "present":
        graph.append(
            {
                "@id": evidence_id,
                "@type": "capas:PhysicalEvidence",
                "name": "Physical evidence attached to result",
                "capas:physicalEvidenceLevel": evidence.get("physical_evidence_level"),
                "capas:verificationIndependence": evidence.get("verification_independence"),
                "capas:witnessStack": evidence.get("witness_stack"),
                "capas:evidenceStatusDetail": evidence.get("evidence_status_detail"),
                "capas:degeneracyCount": evidence.get("degeneracy_count"),
                "capas:optimalAssignments": evidence.get("optimal_assignments"),
                "capas:tasks": evidence.get("tasks"),
                "capas:people": evidence.get("people"),
                "capas:costs": evidence.get("costs"),
                "capas:balanceLambda": evidence.get("balance_lambda"),
                "capas:conflicts": evidence.get("conflicts"),
                "capas:spinEncoding": evidence.get("spin_encoding"),
                "capas:isingH": evidence.get("ising_h"),
                "capas:isingJ": evidence.get("ising_J"),
                "capas:constantOffset": evidence.get("constant_offset"),
                "capas:mappingTerms": evidence.get("mapping_terms"),
                "capas:falsificationNotes": evidence.get("falsification_notes"),
                "capas:basis": evidence.get("basis"),
                "capas:geometry": evidence.get("geometry"),
                "capas:bondLengthAngstrom": evidence.get("bond_length_angstrom"),
                "capas:basisOrbitals": evidence.get("basis_orbitals"),
                "capas:absErrorVsFci": evidence.get("abs_error_vs_fci"),
                "capas:absErrorVsExperimental": evidence.get("abs_error_vs_experimental"),
                "capas:chemicalAccuracyThresholdHartree": evidence.get("chemical_accuracy_threshold_hartree"),
                "capas:withinChemicalAccuracy": evidence.get("within_chemical_accuracy"),
                "capas:solverErrorHartree": evidence.get("solver_error_hartree"),
                "capas:modelErrorHartree": evidence.get("model_error_hartree"),
                "capas:modelBindingEnergyHartree": evidence.get("model_binding_energy_hartree"),
                "capas:experimentalBindingEnergyHartree": evidence.get("experimental_binding_energy_hartree"),
                "capas:electronicAtomizationEnergyHartree": evidence.get("electronic_atomization_energy_hartree"),
                "capas:zpeCorrectedAtomizationEnergyHartree": evidence.get("zpe_corrected_atomization_energy_hartree"),
                "capas:experimentalAtomizationEnergyHartree": evidence.get("experimental_atomization_energy_hartree"),
                "capas:experimentalAtomizationEnergyKcalMol": evidence.get("experimental_atomization_energy_kcal_mol"),
                "capas:vibrationalZpeHartree": evidence.get("vibrational_zpe_hartree"),
                "capas:vibrationalZpeCmInverse": evidence.get("vibrational_zpe_cm_inverse"),
                "capas:harmonicFrequenciesCmInverse": evidence.get("harmonic_frequencies_cm_inverse"),
                "capas:convergencePoints": evidence.get("convergence_points"),
                "capas:monotonicNonincreasingError": evidence.get("monotonic_nonincreasing_error"),
                "capas:firstWithinChemicalAccuracyBasis": evidence.get("first_within_chemical_accuracy_basis"),
                "capas:firstRobustBasis": evidence.get("first_robust_basis"),
                "capas:ceilingBasisSolved": evidence.get("ceiling_basis_solved"),
                "capas:ceilingBasisOrbitals": evidence.get("ceiling_basis_orbitals"),
                "capas:referenceFciTotalEnergyHartree": evidence.get("reference_fci_total_energy_hartree"),
                "capas:referenceExperimentalD0CmInverse": evidence.get("reference_experimental_d0_cm_inverse"),
                "capas:referenceDefinitionErrorHartree": evidence.get("reference_definition_error_hartree"),
                "capas:referenceDefinitionCorrectedErrorHartree": evidence.get("reference_definition_corrected_error_hartree"),
                "capas:referenceDefinitionMatch": evidence.get("reference_definition_match"),
                "capas:referenceDefinitionCorrection": evidence.get("reference_definition_correction"),
                "capas:referenceTruth": evidence.get("reference_truth"),
                "capas:benchmarkFamily": evidence.get("benchmark_family"),
                "capas:observable": evidence.get("observable"),
                "capas:expected": evidence.get("expected"),
                "capas:value": evidence.get("value"),
                "capas:absError": evidence.get("abs_error"),
                "capas:units": evidence.get("units"),
                "capas:detail": evidence.get("physical_evidence_detail"),
                "capas:certificationStatus": evidence.get("certification_status"),
                "capas:formalBoundStatus": evidence.get("formal_bound_status"),
                "capas:sourceLabel": evidence.get("source_label"),
                "capas:discardedWeight": evidence.get("discarded_weight"),
                "capas:actualErrorSquared": evidence.get("actual_error_squared"),
                "capas:composedStateErrorBound": evidence.get("composed_state_error_bound"),
                "capas:boundSlack": evidence.get("bound_slack"),
                "capas:boundType": evidence.get("bound_type"),
                "capas:boundScope": evidence.get("bound_scope"),
                "capas:localPropertyTests": evidence.get("local_property_tests"),
                "capas:localPropertyTestsPass": evidence.get("local_property_tests_pass"),
                "capas:localOracleCaught": evidence.get("local_oracle_caught"),
                "capas:universalAnchor": evidence.get("universal_anchor"),
                "capas:universalAnchorPass": evidence.get("universal_anchor_pass"),
                "capas:invariantCaught": evidence.get("invariant_caught"),
                "capas:generatorError": evidence.get("generator_error"),
                "capas:anchorKind": evidence.get("anchor_kind"),
                "capas:anchorMode": evidence.get("anchor_mode"),
                "capas:scalingPoints": evidence.get("scaling_points"),
                "capas:fittedExponent": evidence.get("fitted_exponent"),
                "capas:expectedExponent": evidence.get("expected_exponent"),
                "capas:exponentTolerance": evidence.get("exponent_tolerance"),
                "capas:fitRSquared": evidence.get("fit_r_squared"),
                "capas:finiteSizeNotes": evidence.get("finite_size_notes"),
                "capas:randomSeed": evidence.get("random_seed"),
                "capas:variantCount": evidence.get("variant_count"),
                "capas:randomizedVariants": evidence.get("randomized_variants"),
                "capas:minAbsError": evidence.get("min_abs_error"),
                "capas:maxAbsError": evidence.get("max_abs_error"),
                "capas:agentKind": evidence.get("agent_kind"),
                "capas:agentId": evidence.get("agent_id"),
                "capas:agentPrompt": evidence.get("agent_prompt"),
                "capas:agentResponse": evidence.get("agent_response"),
                "capas:structureMapping": evidence.get("structure_mapping"),
                "capas:preRegisteredSuccessCriterion": evidence.get("pre_registered_success_criterion"),
                "capas:claimScope": evidence.get("claim_scope"),
                "capas:evidenceHash": stable_hash(evidence),
                "about": {"@id": result_id},
            }
        )
        for node in graph:
            if node.get("@id") == root_id:
                node["hasPart"].append({"@id": evidence_id})
                break
        if trace.result_hash:
            for node in graph:
                if node.get("@id") == result_id:
                    node["capas:physicalEvidence"] = {"@id": evidence_id}
                    break

    for idx, event in enumerate(trace.events):
        event_id = f"{trace_id}:event:{idx}:{event.stage}"
        graph.append(
            {
                "@id": event_id,
                "@type": "Action",
                "name": event.stage,
                "actionStatus": event.status,
                "description": event.message,
                "startTime": event.timestamp,
                "capas:metrics": event.metrics,
            }
        )

    return {
        "@context": [
            RO_CRATE_CONTEXT,
            WORKFLOW_RUN_CONTEXT,
            {
                "capas": "https://example.org/capas-inteligentes#",
                "sha256": "https://schema.org/sha256",
            },
        ],
        "@graph": [_strip_none(node) for node in graph],
    }


def write_ro_crate_for_trace(trace: RunTrace, out_dir: Path, *, trace_payload: dict[str, Any]) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    workflow_dir = out_dir / "workflow"
    workflow_dir.mkdir(exist_ok=True)
    trace_path = out_dir / "runtrace.json"
    prov_path = out_dir / "runtrace.prov.json"
    workflow_path = out_dir / CAPAS_WORKFLOW_ID
    crate_path = out_dir / "ro-crate-metadata.json"

    for stale_workflow in workflow_dir.glob("capas-costurero-run.*"):
        if stale_workflow != workflow_path:
            stale_workflow.unlink()

    trace_path.write_text(json.dumps(trace_payload, indent=2, sort_keys=True), encoding="utf-8")
    prov_path.write_text(json.dumps(run_trace_to_prov_json(trace), indent=2, sort_keys=True), encoding="utf-8")
    workflow_path.write_text(_workflow_descriptor_source(), encoding="utf-8")
    crate = run_trace_to_ro_crate_metadata(
        trace,
        trace_file="runtrace.json",
        prov_file="runtrace.prov.json",
        crate_dir=out_dir,
    )
    crate_path.write_text(json.dumps(crate, indent=2, sort_keys=True), encoding="utf-8")
    return crate_path


def _physical_evidence_from_trace(trace: RunTrace) -> dict[str, Any]:
    evidence: dict[str, Any] = {}
    if trace.result_summary:
        for key in (
            "physical_evidence_level",
            "physical_evidence_detail",
            "observable",
            "units",
            "abs_error",
            "expected",
            "value",
            "benchmark_family",
            "reference_truth",
            "verification_independence",
            "witness_stack",
            "evidence_status_detail",
            "degeneracy_count",
            "optimal_assignments",
            "tasks",
            "people",
            "costs",
            "balance_lambda",
            "conflicts",
            "spin_encoding",
            "ising_h",
            "ising_J",
            "constant_offset",
            "mapping_terms",
            "falsification_notes",
            "basis",
            "geometry",
            "bond_length_angstrom",
            "basis_orbitals",
            "abs_error_vs_fci",
            "abs_error_vs_experimental",
            "chemical_accuracy_threshold_hartree",
            "within_chemical_accuracy",
            "solver_error_hartree",
            "model_error_hartree",
            "model_binding_energy_hartree",
            "experimental_binding_energy_hartree",
            "electronic_atomization_energy_hartree",
            "zpe_corrected_atomization_energy_hartree",
            "experimental_atomization_energy_hartree",
            "experimental_atomization_energy_kcal_mol",
            "vibrational_zpe_hartree",
            "vibrational_zpe_cm_inverse",
            "harmonic_frequencies_cm_inverse",
            "convergence_points",
            "monotonic_nonincreasing_error",
            "first_within_chemical_accuracy_basis",
            "first_robust_basis",
            "ceiling_basis_solved",
            "ceiling_basis_orbitals",
            "reference_fci_total_energy_hartree",
            "reference_experimental_d0_cm_inverse",
            "reference_definition_error_hartree",
            "reference_definition_corrected_error_hartree",
            "reference_definition_match",
            "reference_definition_correction",
            "certification_status",
            "formal_bound_status",
            "source_label",
            "discarded_weight",
            "actual_error_squared",
            "composed_state_error_bound",
            "bound_slack",
            "bound_type",
            "bound_scope",
            "local_property_tests",
            "local_property_tests_pass",
            "local_oracle_caught",
            "universal_anchor",
            "universal_anchor_pass",
            "invariant_caught",
            "generator_error",
            "anchor_kind",
            "anchor_mode",
            "scaling_points",
            "fitted_exponent",
            "expected_exponent",
            "exponent_tolerance",
            "fit_r_squared",
            "finite_size_notes",
            "random_seed",
            "variant_count",
            "randomized_variants",
            "min_abs_error",
            "max_abs_error",
            "agent_kind",
            "agent_id",
            "agent_prompt",
            "agent_response",
            "structure_mapping",
            "pre_registered_success_criterion",
            "claim_scope",
        ):
            if key in trace.result_summary:
                evidence[key] = trace.result_summary[key]
    for event in trace.events:
        if event.stage == "physical_evidence":
            evidence.update(event.metrics)
    if evidence.get("physical_evidence_level") == "analytic":
        evidence.setdefault("verification_independence", "analytic_no_solver")
        evidence.setdefault(
            "reference_truth",
            {
                "kind": "closed_form_or_exact_invariant",
                "expected": evidence.get("expected"),
                "detail": evidence.get("physical_evidence_detail"),
            },
        )
    return evidence


def _evidence_status(trace: RunTrace, evidence: dict[str, Any]) -> str:
    if evidence:
        level = evidence.get("physical_evidence_level")
        if level == "none":
            return "none_declared"
        return "present"
    if trace.error:
        return "not_applicable_failed"
    if trace.decision_route in {"QPU_REQUIRED", "TENSOR_REQUIRED", "TENSOR_TOO_SLOW"}:
        return "not_applicable_rejected"
    return "missing"


def _action_status(trace: RunTrace) -> str:
    if trace.error:
        return "FailedActionStatus"
    return "CompletedActionStatus"


def _event_time_bounds(trace: RunTrace) -> tuple[str | None, str | None]:
    if not trace.events:
        return None, None
    timestamps = [_iso_from_timestamp(event.timestamp) for event in trace.events]
    return timestamps[0], timestamps[-1]


def _iso_from_timestamp(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp, tz=UTC).isoformat().replace("+00:00", "Z")


def _workflow_descriptor_source() -> str:
    return '''cwlVersion: v1.2
class: CommandLineTool
label: CAPAS costurero workflow descriptor
doc: |
  Conceptual Workflow Run RO-Crate descriptor for the CAPAS costurero.
  The executable implementation lives in router.pipeline.run_with_trace.
  This descriptor exists so the crate has a recognized workflow entity while
  preserving Python as the implementation language in RO-Crate metadata.
baseCommand: capas-costurero-run
inputs:
  workload:
    type: File
    doc: Structured scientific workload routed by the CAPAS costurero.
outputs:
  result:
    type: File
    outputBinding:
      glob: runtrace.json
    doc: Structured RunTrace result, skipped state, or failure state.
requirements:
  InlineJavascriptRequirement: {}
'''


def _file_sha256_if_exists(path: str, base_dir: Path | None = None) -> str | None:
    p = Path(path)
    if not p.is_absolute() and base_dir is not None:
        p = base_dir / p
    if not p.exists():
        return None
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _strip_none(data: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in data.items() if v is not None}
