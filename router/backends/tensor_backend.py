from __future__ import annotations

import cotengra as ctg

from router.types import RouteDecision, Workload


def execute_tensor_contract(workload: Workload, decision: RouteDecision):
    if decision.route != "tensor":
        raise ValueError(f"Tensor backend received route {decision.route!r}")
    if workload.kind != "tensor" or workload.tensor is None:
        raise ValueError("Tensor backend requires a tensor workload")
    spec = workload.tensor
    if spec.arrays is None:
        raise ValueError("Tensor execution requires TensorSpec.arrays")
    return ctg.array_contract(
        spec.arrays,
        spec.inputs,
        output=tuple(spec.output or ()),
        optimize="greedy",
    )
