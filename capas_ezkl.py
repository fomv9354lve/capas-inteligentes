"""CAPAS — production ZK backend via EZKL (KZG/halo2 SNARK).

Optional. If `ezkl` is installed, capas_verify registers `ezkl_backend` as the
"ezkl" verifying key: it VERIFIES a succinct zero-knowledge proof that a
re-derivation circuit executed correctly on (possibly hidden) inputs. CAPAS is
the verifier; the data holder is the prover (prove_linear_derivation() is the
reference prover used by the demo/test).

This is the real thing the R1CS layer (capas_circuits) is the dependency-free
stand-in for: succinct (constant-size proof) and zero-knowledge (witness hidden).
"""
from __future__ import annotations

import asyncio
import inspect
import json
from pathlib import Path
from typing import Any


def _run(x: Any) -> Any:
    if inspect.iscoroutine(x):
        return asyncio.new_event_loop().run_until_complete(x)
    return x


def ezkl_backend(proof: dict[str, Any], public_inputs: dict[str, Any], statement: Any) -> bool:
    """ZK-backend: verify an EZKL proof. proof carries the artifact paths
    {proof_path, settings_path, vk_path, srs_path?}."""
    import ezkl

    p = proof or {}
    proof_path, settings, vk = p.get("proof_path"), p.get("settings_path"), p.get("vk_path")
    srs = p.get("srs_path")
    if not (proof_path and settings and vk and Path(proof_path).exists()):
        return False
    args = [proof_path, settings, vk] + ([srs] if srs else [])
    try:
        return bool(_run(ezkl.verify(*args)))
    except Exception:
        return False


def prove_linear_derivation(weights: list[float], inputs: list[float], out_dir: str) -> dict[str, str]:
    """Reference PROVER (data holder side): build an ONNX linear model
    y = inputs · weights, then EZKL-setup and prove it. Returns artifact paths
    for the verifier. Requires `ezkl`, `onnx`, `numpy`."""
    import numpy as np
    import onnx
    from onnx import TensorProto, helper
    import ezkl

    d = Path(out_dir); d.mkdir(parents=True, exist_ok=True)
    n = len(weights)
    X = helper.make_tensor_value_info("X", TensorProto.FLOAT, [1, n])
    Y = helper.make_tensor_value_info("Y", TensorProto.FLOAT, [1, 1])
    W = helper.make_tensor("W", TensorProto.FLOAT, [n, 1],
                           np.array(weights, dtype=np.float32).reshape(n, 1).tobytes(), raw=True)
    graph = helper.make_graph([helper.make_node("MatMul", ["X", "W"], ["Y"])], "lin", [X], [Y], [W])
    model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 17)])
    model.ir_version = 9
    onnx.save(model, str(d / "model.onnx"))
    json.dump({"input_data": [list(map(float, inputs))]}, open(d / "input.json", "w"))

    _run(ezkl.gen_settings(str(d / "model.onnx"), str(d / "settings.json")))
    _run(ezkl.compile_circuit(str(d / "model.onnx"), str(d / "model.compiled"), str(d / "settings.json")))
    logrows = json.load(open(d / "settings.json"))["run_args"]["logrows"]
    srs = str(d / "kzg.srs")
    _run(ezkl.gen_srs(srs, logrows))
    _run(ezkl.setup(str(d / "model.compiled"), str(d / "vk.key"), str(d / "pk.key"), srs))
    _run(ezkl.gen_witness(str(d / "input.json"), str(d / "model.compiled"), str(d / "witness.json")))
    _run(ezkl.prove(str(d / "witness.json"), str(d / "model.compiled"), str(d / "pk.key"), str(d / "proof.json"), srs))
    return {"proof_path": str(d / "proof.json"), "settings_path": str(d / "settings.json"),
            "vk_path": str(d / "vk.key"), "srs_path": srs}
