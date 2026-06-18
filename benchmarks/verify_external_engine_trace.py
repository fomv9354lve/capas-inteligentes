from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from router import EngineSpec, Workload, run_with_trace  # noqa: E402


ENGINE_PATH = Path(os.environ.get("CAPAS_PRIVATE_HEISENBERG_ENGINE", ""))


def event(trace, stage: str):
    for e in trace.events:
        if e.stage == stage:
            return e
    raise AssertionError(f"missing event {stage}")


def main() -> None:
    if not ENGINE_PATH.is_file():
        print(
            "verify_external_engine_trace skipped: set "
            "CAPAS_PRIVATE_HEISENBERG_ENGINE to a local engine module to run "
            "this private-adapter check."
        )
        return
    workload = Workload(
        kind="dense",
        n_qubits=2,
        engine=EngineSpec(
            module_path=str(ENGINE_PATH),
            function_name="ground_state_energy",
            kwargs={"n_rungs": 1, "J_leg": 1.0, "J_rung": 1.0},
            engine_id="real_heisenberg_ladder.ground_state_energy",
        ),
    )
    result, trace = run_with_trace(workload)
    assert trace.decision_route == "external_engine"
    assert abs(result["result"] + 0.75) < 1e-12
    provenance = event(trace, "engine_provenance").metrics
    assert provenance["module_sha256"]
    assert provenance["function_name"] == "ground_state_energy"
    assert trace.result_hash
    assert trace.result_summary["type"] == "dict"
    print("verify_external_engine_trace passed")


if __name__ == "__main__":
    main()
