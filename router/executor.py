# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
from __future__ import annotations

from .backends import execute_dense_circuit, execute_external_engine, execute_stim_circuit, execute_tensor_contract
from .route import route
from .types import RouteDecision, Workload


def execute(workload: Workload, decision: RouteDecision | None = None, **kwargs):
    decision = decision or route(workload)
    if decision.route == "stim":
        return execute_stim_circuit(workload, decision, **kwargs)
    if decision.route == "dense":
        return execute_dense_circuit(workload, decision)
    if decision.route == "tensor":
        return execute_tensor_contract(workload, decision)
    if decision.route == "external_engine":
        return execute_external_engine(workload, decision)
    raise RuntimeError(f"Route is not executable: {decision.route} ({decision.reason})")
