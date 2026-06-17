from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence

import cotengra as ctg


BYTES_PER_COMPLEX128 = 16
DEFAULT_MEMORY_BUDGET_BYTES = 512 * 1024**2
DEFAULT_SAFETY_FACTOR = 0.5
# UNVALIDATED POLICY DEFAULT: this is a runtime cutoff, not a physics
# constant. Calibrate it with a wall-time-vs-FLOPs benchmark per machine.
DEFAULT_FLOPS_CEILING = 1e8
DEFAULT_TENSOR_OPTIMIZE = "greedy"

CLIFFORD_GATES = {"I", "H", "S", "X", "Y", "Z", "CX", "CNOT", "CZ", "M", "MEASURE"}
NON_CLIFFORD_GATES = {"T", "TDG", "CCX", "TOFFOLI", "RX", "RY", "RZ", "U", "U1", "U2", "U3"}


@dataclass(frozen=True)
class CostBudget:
    """Runtime policy for materialized routes.

    `memory_budget_bytes` is the total nominal memory budget, while
    `safety_factor` is the usable fraction. The default keeps a 50% headroom
    for temporaries, fragmentation, and the host process.
    """

    memory_budget_bytes: int = DEFAULT_MEMORY_BUDGET_BYTES
    safety_factor: float = DEFAULT_SAFETY_FACTOR
    flops_ceiling: float = DEFAULT_FLOPS_CEILING

    @property
    def usable_memory_bytes(self) -> float:
        return self.memory_budget_bytes * self.safety_factor


@dataclass(frozen=True)
class MagicEstimate:
    n_gates: int
    non_clifford_count: int
    t_count: int
    non_clifford_gates: tuple[str, ...]

    @property
    def is_clifford(self) -> bool:
        return self.non_clifford_count == 0


@dataclass(frozen=True)
class TensorCost:
    contraction_cost: float
    max_size_elements: int
    peak_bytes: int
    contraction_width_log2: float
    n_tensors: int
    memory_viable: bool
    time_viable: bool

    @property
    def viable(self) -> bool:
        return self.memory_viable and self.time_viable


def statevector_bytes(n_qubits: int, bytes_per_amplitude: int = BYTES_PER_COMPLEX128) -> int:
    if n_qubits < 0:
        raise ValueError("n_qubits must be non-negative")
    return bytes_per_amplitude * (1 << n_qubits)


def make_default_tensor_optimizer() -> str:
    """Return the runtime path optimizer used by the router.

    We intentionally use ``greedy`` for online routing. Higher-quality
    optimizers such as ``auto-hq`` or ``HyperOptimizer`` can spend seconds on
    path search or spawn process pools in sandboxed environments. Use them for
    offline analysis by passing an explicit optimizer to ``contraction_cost``.
    """
    return DEFAULT_TENSOR_OPTIMIZE


def dense_route_viability(n_qubits: int, budget: CostBudget | None = None) -> dict[str, Any]:
    budget = budget or CostBudget()
    need = statevector_bytes(n_qubits)
    return {
        "route": "dense" if need <= budget.usable_memory_bytes else "QPU_REQUIRED",
        "n_qubits": n_qubits,
        "statevector_bytes": need,
        "usable_memory_bytes": budget.usable_memory_bytes,
        "memory_viable": need <= budget.usable_memory_bytes,
    }


def normalize_gate_name(gate: Any) -> str:
    if isinstance(gate, str):
        return gate.upper()
    if hasattr(gate, "name"):
        return str(gate.name).upper()
    return str(gate).upper()


def iter_gate_names(circuit: Any) -> Iterable[str]:
    """Extract gate names from simple op lists, Stim circuits, or Qiskit-like circuits."""
    if isinstance(circuit, Sequence) and not isinstance(circuit, (str, bytes)):
        for item in circuit:
            if isinstance(item, tuple) and item:
                yield normalize_gate_name(item[0])
            else:
                yield normalize_gate_name(item)
        return

    # Qiskit-like: circuit.data contains CircuitInstruction tuples/objects.
    data = getattr(circuit, "data", None)
    if data is not None:
        for item in data:
            operation = getattr(item, "operation", item[0] if isinstance(item, tuple) else item)
            yield normalize_gate_name(operation)
        return

    # Stim-like text fallback. Keep this conservative and structural.
    if hasattr(circuit, "__str__"):
        for raw in str(circuit).splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            yield normalize_gate_name(line.split()[0])
        return

    raise TypeError(f"Unsupported circuit type: {type(circuit)!r}")


def magic_estimate(circuit: Any) -> MagicEstimate:
    names = tuple(iter_gate_names(circuit))
    non_clifford = tuple(g for g in names if g not in CLIFFORD_GATES)
    t_count = sum(1 for g in names if g == "T")
    return MagicEstimate(
        n_gates=len(names),
        non_clifford_count=len(non_clifford),
        t_count=t_count,
        non_clifford_gates=non_clifford,
    )


def contraction_cost(
    inputs: Sequence[Sequence[Any]],
    *,
    output: Sequence[Any] | None = None,
    shapes: Sequence[Sequence[int]] | None = None,
    size_dict: Mapping[Any, int] | None = None,
    budget: CostBudget | None = None,
    optimize: Any | None = None,
    bytes_per_element: int = BYTES_PER_COMPLEX128,
) -> TensorCost:
    """Estimate tensor contraction cost with cotengra, without requiring quimb.

    `inputs` is cotengra's index structure: one sequence of index labels per tensor.
    Provide either `shapes` or `size_dict`.
    """
    budget = budget or CostBudget()
    tree = ctg.array_contract_tree(
        inputs,
        output=tuple(output or ()),
        shapes=shapes,
        size_dict=dict(size_dict) if size_dict is not None else None,
        optimize=make_default_tensor_optimizer() if optimize is None else optimize,
    )
    cost = float(tree.contraction_cost())
    max_size = int(tree.max_size())
    peak_bytes = max_size * bytes_per_element
    return TensorCost(
        contraction_cost=cost,
        max_size_elements=max_size,
        peak_bytes=peak_bytes,
        contraction_width_log2=float(tree.contraction_width()),
        n_tensors=len(inputs),
        memory_viable=peak_bytes <= budget.usable_memory_bytes,
        time_viable=cost <= budget.flops_ceiling,
    )


def tensor_route_viability(
    inputs: Sequence[Sequence[Any]],
    *,
    output: Sequence[Any] | None = None,
    shapes: Sequence[Sequence[int]] | None = None,
    size_dict: Mapping[Any, int] | None = None,
    budget: CostBudget | None = None,
    optimize: Any | None = None,
) -> dict[str, Any]:
    tc = contraction_cost(
        inputs,
        output=output,
        shapes=shapes,
        size_dict=size_dict,
        budget=budget,
        optimize=optimize,
    )
    if tc.viable:
        route = "tensor"
    elif tc.memory_viable:
        route = "TENSOR_TOO_SLOW"
    else:
        route = "TENSOR_REQUIRED"
    return {
        "route": route,
        "contraction_cost": tc.contraction_cost,
        "max_size_elements": tc.max_size_elements,
        "peak_bytes": tc.peak_bytes,
        "contraction_width_log2": tc.contraction_width_log2,
        "n_tensors": tc.n_tensors,
        "memory_viable": tc.memory_viable,
        "time_viable": tc.time_viable,
    }


def quimb_available() -> tuple[bool, str | None]:
    try:
        import quimb  # noqa: F401
    except Exception as exc:  # pragma: no cover - environment dependent
        return False, f"{type(exc).__name__}: {exc}"
    return True, None
