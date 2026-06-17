# Complexity Router Product

This project is a practical complexity router for quantum-adjacent workloads.
It is not a claim of new physics and it does not break the exponential wall.

## Product Claim

The router prevents avoidable bad execution choices:

- Clifford circuits route to `stim` before any dense statevector memory guard.
- Dense statevector routes are protected by a memory budget and safety factor.
- Tensor contractions route through `cotengra` only when both peak memory and estimated FLOPs fit policy.
- Non-viable workloads fail clearly with `QPU_REQUIRED`, `TENSOR_REQUIRED`, or `TENSOR_TOO_SLOW`.

## Non-Claims

- No global interception of CPU operations.
- No "0 overhead" lazy layer.
- No claim that provenance/hash gates prove physical correctness.
- No claim that low-magic simulation solves generic QAOA/QFT/Trotter circuits after decomposition.
- No use of the Esfera/Espiral metaphor as a routing decision engine.

## Public API

```python
from router import CostBudget, TensorSpec, Workload, route, execute, run_with_trace

budget = CostBudget(memory_budget_bytes=2 * 1024**3, safety_factor=0.5)
workload = Workload(
    kind="circuit",
    n_qubits=3,
    circuit=[("H", (0,)), ("CNOT", (0, 1)), ("CNOT", (1, 2))],
    budget=budget,
)

decision = route(workload)
result = execute(workload, decision, shots=64)

result, trace = run_with_trace(workload, shots=64)
```

`run_with_trace` is the integration layer: it preserves the path from
workload -> cost model -> route decision -> backend execution -> result hash.
The trace proves provenance of the computational path, not physical truth.

## Validation Commands

```bash
python3 benchmarks/verify_cost_model.py
python3 benchmarks/verify_route.py
python3 benchmarks/verify_product.py
python3 benchmarks/verify_pipeline_trace.py
python3 benchmarks/verify_external_engine_trace.py
python3 benchmarks/verify_heisenberg_engine_sweep.py
python3 benchmarks/run_all.py
```

Expected state:

- `verify_*` scripts pass.
- `run_all.py` reports the bypass/lazy global failures; those failures are intentional evidence that a universal interception layer is not productized.

## Current Backends

- `stim`: executes Clifford circuits.
- `dense`: executes small supported op-list circuits with NumPy.
- `tensor`: executes explicit tensor contractions with `cotengra`.
- `external_engine`: executes an explicit `EngineSpec` by module path and function name, recording the engine file hash in the trace.

`quimb` is optional. It is not required because it can fail in Python 3.14 due to `numba` caching/import behavior.

## Real Engine Trace

The external-engine path has been verified with:

```text
physics_quantum/real_heisenberg_ladder.py::ground_state_energy
```

The sweep `n_rungs=1..4` records the engine file hash, result hash, and trace
hash for each run. Evidence levels:

- `n_rungs=1`: analytic (`E0 = -3/4 J`),
- `n_rungs=2..4`: cross-sim against an independent dense NumPy Hamiltonian.

## Trace Contract

Every traced run records:

- workload hash and summary,
- cost-model metrics,
- route and reason,
- execution status,
- result summary and result hash when executable,
- external engine module hash when an `EngineSpec` is used,
- explicit skipped status when the route is non-executable.

The trace is for provenance and debugging. It does not certify physical
correctness; use the audit templates in `audits/` for that layer.

## Next Product Work

1. Add a JSON workload loader for CLI use.
2. Add wall-time calibration for `CostBudget.flops_ceiling`.
3. Add richer circuit adapters only when backed by tests.
4. Add a low-magic backend only after finding real workloads that live in the low-magic regime.
