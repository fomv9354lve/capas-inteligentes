from __future__ import annotations

import importlib
import platform
import sys
import time
from typing import Any

from .cost_model import dense_route_viability, magic_estimate, tensor_route_viability
from .backends.external_engine_backend import file_sha256
from .executor import execute
from .route import route
from .trace import RunTrace, new_trace, stable_hash, summarize_result
from .types import Workload


def run_with_trace(
    workload: Workload,
    execute_result: bool = True,
    *,
    raise_on_error: bool = True,
    **execute_kwargs,
) -> tuple[Any | None, RunTrace]:
    trace = new_trace(workload)
    trace.add("ingest", "ok", trace.workload_summary, "workload accepted")
    trace.add("runtime_context", "ok", _runtime_context(), "runtime and hardware context recorded")

    try:
        _record_cost_model(workload, trace)
        decision = route(workload)
        trace.decision_route = decision.route
        trace.decision_reason = decision.reason
        trace.add("route", "ok", decision.metrics, decision.reason)

        if not decision.executable:
            trace.add("execute", "skipped", {"route": decision.route}, "route is not executable")
            return None, trace

        if not execute_result:
            trace.add("execute", "skipped", {"route": decision.route}, "execution disabled")
            return None, trace

        t0 = time.perf_counter()
        result = execute(workload, decision, **execute_kwargs)
        runtime_ms = (time.perf_counter() - t0) * 1e3
        summary = summarize_result(result)
        trace.result_summary = summary
        trace.result_hash = stable_hash(summary)
        trace.add("execute", "ok", {"route": decision.route, "runtime_ms": runtime_ms, **summary}, "backend executed")
        evidence = _physical_evidence_from_summary(summary)
        if evidence:
            trace.add("physical_evidence", "ok", evidence, "physical evidence reported by backend")
        return result, trace
    except Exception as exc:
        trace.error = f"{type(exc).__name__}: {exc}"
        trace.add("error", "fail", {"error_type": type(exc).__name__}, str(exc))
        if raise_on_error:
            raise
        return None, trace


def _record_cost_model(workload: Workload, trace: RunTrace) -> None:
    if workload.engine is not None:
        trace.add(
            "engine_provenance",
            "ok",
            {
                "engine_id": workload.engine.engine_id,
                "module_path": workload.engine.module_path,
                "module_sha256": file_sha256(workload.engine.module_path),
                "function_name": workload.engine.function_name,
                "kwargs": dict(workload.engine.kwargs),
            },
            "external engine provenance recorded",
        )

    if workload.kind == "circuit":
        if workload.circuit is None or workload.n_qubits is None:
            trace.add("cost_model", "invalid", {}, "circuit workload missing circuit or n_qubits")
            return
        magic = magic_estimate(workload.circuit)
        dense = dense_route_viability(workload.n_qubits, workload.budget)
        trace.add(
            "cost_model",
            "ok",
            {
                "n_qubits": workload.n_qubits,
                "n_gates": magic.n_gates,
                "non_clifford_count": magic.non_clifford_count,
                "t_count": magic.t_count,
                "dense_statevector_bytes": dense["statevector_bytes"],
                "dense_memory_viable": dense["memory_viable"],
            },
            "circuit features estimated",
        )
        return

    if workload.kind == "tensor":
        if workload.tensor is None:
            trace.add("cost_model", "invalid", {}, "tensor workload missing tensor spec")
            return
        tensor = tensor_route_viability(
            workload.tensor.inputs,
            output=workload.tensor.output,
            shapes=workload.tensor.shapes,
            size_dict=workload.tensor.size_dict,
            budget=workload.budget,
        )
        trace.add("cost_model", "ok", tensor, "tensor contraction cost estimated")
        return

    if workload.kind == "dense":
        if workload.n_qubits is None:
            trace.add("cost_model", "invalid", {}, "dense workload missing n_qubits")
            return
        dense = dense_route_viability(workload.n_qubits, workload.budget)
        trace.add("cost_model", "ok", dense, "dense statevector cost estimated")


def _runtime_context() -> dict[str, Any]:
    context: dict[str, Any] = {
        "python_version": sys.version.split()[0],
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
    }
    for module_name in ("numpy", "scipy", "stim", "cotengra", "quimb", "qiskit_aer"):
        try:
            module = importlib.import_module(module_name)
            key = module_name.replace(".", "_")
            context[f"{key}_available"] = True
            context[f"{key}_version"] = getattr(module, "__version__", None)
        except Exception as exc:
            key = module_name.replace(".", "_")
            context[f"{key}_available"] = False
            context[f"{key}_error"] = f"{type(exc).__name__}: {exc}"
    context["mlx_probe"] = "skipped_in_default_trace; use apple_silicon_thermal_routing.py for Metal/MLX device probes"
    return context


def _physical_evidence_from_summary(summary: dict[str, Any]) -> dict[str, Any]:
    keys = (
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
        "certification_status",
        "formal_bound_status",
        "source_label",
        "discarded_weight",
        "actual_error_squared",
        "composed_state_error_bound",
        "bound_slack",
        "bound_type",
        "bound_scope",
    )
    evidence = {key: summary[key] for key in keys if key in summary}
    if not evidence:
        return {}
    evidence["evidence_hash"] = stable_hash(evidence)
    return evidence
