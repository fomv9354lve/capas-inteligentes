from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, Mapping, Sequence

from .cost_model import CostBudget


WorkloadKind = Literal["circuit", "tensor", "dense"]
RouteName = Literal[
    "stim",
    "tensor",
    "dense",
    "external_engine",
    "QPU_REQUIRED",
    "TENSOR_REQUIRED",
    "TENSOR_TOO_SLOW",
]


@dataclass(frozen=True)
class TensorSpec:
    inputs: Sequence[Sequence[Any]]
    output: Sequence[Any] | None = None
    shapes: Sequence[Sequence[int]] | None = None
    size_dict: Mapping[Any, int] | None = None
    arrays: Sequence[Any] | None = None


@dataclass(frozen=True)
class EngineSpec:
    module_path: str
    function_name: str
    kwargs: Mapping[str, Any] = field(default_factory=dict)
    engine_id: str | None = None


@dataclass(frozen=True)
class Workload:
    kind: WorkloadKind
    n_qubits: int | None = None
    circuit: Any | None = None
    tensor: TensorSpec | None = None
    engine: EngineSpec | None = None
    budget: CostBudget = field(default_factory=CostBudget)


@dataclass(frozen=True)
class RouteDecision:
    route: RouteName
    reason: str
    budget: CostBudget
    metrics: dict[str, Any] = field(default_factory=dict)

    @property
    def executable(self) -> bool:
        return self.route in {"stim", "tensor", "dense", "external_engine"}
