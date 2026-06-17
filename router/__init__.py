"""Complexity routing primitives validated by the benchmark harness."""

from .cost_model import (
    BYTES_PER_COMPLEX128,
    CostBudget,
    MagicEstimate,
    TensorCost,
    dense_route_viability,
    magic_estimate,
    statevector_bytes,
    tensor_route_viability,
)
from .route import route
from .executor import execute
from .pipeline import run_with_trace
from .types import EngineSpec, RouteDecision, TensorSpec, Workload

__all__ = [
    "BYTES_PER_COMPLEX128",
    "CostBudget",
    "MagicEstimate",
    "TensorCost",
    "dense_route_viability",
    "magic_estimate",
    "statevector_bytes",
    "tensor_route_viability",
    "route",
    "execute",
    "run_with_trace",
    "RouteDecision",
    "EngineSpec",
    "TensorSpec",
    "Workload",
]
