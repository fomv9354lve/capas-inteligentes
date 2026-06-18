from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from router import EngineSpec, Workload, run_with_trace  # noqa: E402


ENGINE_PATH = Path(os.environ.get("CAPAS_PRIVATE_HEISENBERG_ENGINE", ""))
OUT_PATH = ROOT / "benchmarks" / "heisenberg_engine_sweep_results.json"


SX = 0.5 * np.array([[0, 1], [1, 0]], dtype=np.complex128)
SY = 0.5 * np.array([[0, -1j], [1j, 0]], dtype=np.complex128)
SZ = 0.5 * np.array([[1, 0], [0, -1]], dtype=np.complex128)
I2 = np.eye(2, dtype=np.complex128)


def kron_embed(op: np.ndarray, site: int, n_sites: int) -> np.ndarray:
    out = np.array([[1.0]], dtype=np.complex128)
    for i in range(n_sites):
        out = np.kron(out, op if i == site else I2)
    return out


def independent_dense_ladder_energy(n_rungs: int, J_leg: float = 1.0, J_rung: float = 1.0) -> float:
    """Independent dense Hamiltonian for small-rung cross-checks.

    This deliberately does not import the external engine. It uses dense numpy
    Kronecker products instead of the engine's scipy sparse builder.
    """
    n_sites = 2 * n_rungs
    dim = 1 << n_sites
    H = np.zeros((dim, dim), dtype=np.complex128)

    embedded = {
        ("x", i): kron_embed(SX, i, n_sites)
        for i in range(n_sites)
    }
    embedded.update({("y", i): kron_embed(SY, i, n_sites) for i in range(n_sites)})
    embedded.update({("z", i): kron_embed(SZ, i, n_sites) for i in range(n_sites)})

    def add_bond(i: int, j: int, J: float) -> None:
        nonlocal H
        H = H + J * (
            embedded[("x", i)] @ embedded[("x", j)]
            + embedded[("y", i)] @ embedded[("y", j)]
            + embedded[("z", i)] @ embedded[("z", j)]
        )

    for r in range(n_rungs):
        add_bond(2 * r, 2 * r + 1, J_rung)

    for r in range(n_rungs - 1):
        add_bond(2 * r, 2 * (r + 1), J_leg)
        add_bond(2 * r + 1, 2 * (r + 1) + 1, J_leg)

    return float(np.linalg.eigvalsh(H).min().real)


def main() -> None:
    if not ENGINE_PATH.is_file():
        print(
            "verify_heisenberg_engine_sweep skipped: set "
            "CAPAS_PRIVATE_HEISENBERG_ENGINE to a local engine module to run "
            "this private-adapter check."
        )
        return
    rows = []
    for n_rungs in range(1, 5):
        workload = Workload(
            kind="dense",
            n_qubits=2 * n_rungs,
            engine=EngineSpec(
                module_path=str(ENGINE_PATH),
                function_name="ground_state_energy",
                kwargs={"n_rungs": n_rungs, "J_leg": 1.0, "J_rung": 1.0},
                engine_id="real_heisenberg_ladder.ground_state_energy",
            ),
        )
        result, trace = run_with_trace(workload)
        engine_energy = float(result["result"])
        independent_energy = independent_dense_ladder_energy(n_rungs)
        abs_error = abs(engine_energy - independent_energy)
        row = {
            "n_rungs": n_rungs,
            "n_sites": 2 * n_rungs,
            "engine_energy": engine_energy,
            "independent_dense_energy": independent_energy,
            "abs_error": abs_error,
            "trace_hash": trace.hash(),
            "result_hash": trace.result_hash,
            "engine_sha256": result["module_sha256"],
            "physical_evidence_level": "analytic" if n_rungs == 1 else "cross_sim",
        }
        rows.append(row)
        if n_rungs == 1:
            assert abs(engine_energy + 0.75) < 1e-10
        assert abs_error < 1e-9

    OUT_PATH.write_text(json.dumps(rows, indent=2, sort_keys=True), encoding="utf-8")
    for row in rows:
        print(
            f"n_rungs={row['n_rungs']} E_engine={row['engine_energy']:+.12f} "
            f"E_cross={row['independent_dense_energy']:+.12f} "
            f"err={row['abs_error']:.2e} evidence={row['physical_evidence_level']}"
        )
    print(f"wrote {OUT_PATH}")
    print("verify_heisenberg_engine_sweep passed")


if __name__ == "__main__":
    main()
