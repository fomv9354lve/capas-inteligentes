# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
from __future__ import annotations

from typing import Any

from .cost_model import (
    CostBudget,
    dense_route_viability,
    magic_estimate,
    tensor_route_viability,
)
from .types import RouteDecision, TensorSpec, Workload


def route(workload: Workload, budget: CostBudget | None = None) -> RouteDecision:
    """Route a workload using measured cost-model primitives.

    Critical order:
    1. Clifford circuits route to Stim before any dense statevector guard.
    2. Tensor routes must pass both peak-memory and FLOPs gates.
    3. Dense routes are protected by statevector memory budget.
    """
    active_budget = budget or workload.budget

    if workload.engine is not None:
        return RouteDecision(
            "external_engine",
            "explicit external engine workload; route is opt-in and engine provenance is recorded at execution",
            active_budget,
            {
                "engine_id": workload.engine.engine_id,
                "module_path": workload.engine.module_path,
                "function_name": workload.engine.function_name,
            },
        )

    if workload.kind == "circuit":
        return _route_circuit(workload, active_budget)
    if workload.kind == "tensor":
        return _route_tensor(workload, active_budget)
    if workload.kind == "dense":
        return _route_dense(workload, active_budget)
    raise ValueError(f"Unsupported workload kind: {workload.kind!r}")


def _route_circuit(workload: Workload, budget: CostBudget) -> RouteDecision:
    if workload.circuit is None:
        raise ValueError("circuit workload requires `circuit`")
    if workload.n_qubits is None:
        raise ValueError("circuit workload requires `n_qubits`")

    magic = magic_estimate(workload.circuit)
    metrics: dict[str, Any] = {
        "n_qubits": workload.n_qubits,
        "n_gates": magic.n_gates,
        "non_clifford_count": magic.non_clifford_count,
        "t_count": magic.t_count,
        "non_clifford_gates": magic.non_clifford_gates,
    }

    if magic.is_clifford:
        dense = dense_route_viability(workload.n_qubits, budget)
        metrics.update({"dense_statevector_bytes": dense["statevector_bytes"]})
        return RouteDecision(
            route="stim",
            reason="pure Clifford circuit; Stim route is structure-based and does not materialize dense statevector",
            budget=budget,
            metrics=metrics,
        )

    dense = dense_route_viability(workload.n_qubits, budget)
    metrics.update(dense)
    if dense["memory_viable"]:
        return RouteDecision("dense", "non-Clifford circuit fits dense statevector budget", budget, metrics)
    return RouteDecision("QPU_REQUIRED", "non-Clifford circuit exceeds dense budget and no specialized route is available", budget, metrics)


def _route_tensor(workload: Workload, budget: CostBudget) -> RouteDecision:
    if workload.tensor is None:
        raise ValueError("tensor workload requires `tensor`")
    tensor = _tensor_viability(workload.tensor, budget)
    metrics: dict[str, Any] = dict(tensor)

    if tensor["route"] == "tensor":
        return RouteDecision("tensor", "tensor contraction passes peak-memory and FLOPs gates", budget, metrics)

    dense: dict[str, Any] | None = None
    if workload.n_qubits is not None:
        dense = dense_route_viability(workload.n_qubits, budget)
        metrics["dense_fallback"] = dense
        if dense["memory_viable"]:
            reason = "tensor route unavailable, but equivalent dense statevector fits budget"
            return RouteDecision("dense", reason, budget, metrics)

    if tensor["route"] == "TENSOR_TOO_SLOW":
        return RouteDecision("TENSOR_TOO_SLOW", "tensor contraction fits memory but exceeds FLOPs ceiling", budget, metrics)
    return RouteDecision("TENSOR_REQUIRED", "tensor contraction exceeds peak-memory budget", budget, metrics)


def _route_dense(workload: Workload, budget: CostBudget) -> RouteDecision:
    if workload.n_qubits is None:
        raise ValueError("dense workload requires `n_qubits`")
    dense = dense_route_viability(workload.n_qubits, budget)
    if dense["memory_viable"]:
        return RouteDecision("dense", "dense statevector fits memory budget", budget, dict(dense))
    return RouteDecision("QPU_REQUIRED", "dense statevector exceeds memory budget", budget, dict(dense))


def _tensor_viability(tensor: TensorSpec, budget: CostBudget) -> dict[str, Any]:
    return tensor_route_viability(
        tensor.inputs,
        output=tensor.output,
        shapes=tensor.shapes,
        size_dict=tensor.size_dict,
        budget=budget,
    )
