# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path
from typing import Any

from router.types import RouteDecision, Workload


def file_sha256(path: str | Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_function(module_path: str, function_name: str):
    path = Path(module_path)
    if not path.exists():
        raise FileNotFoundError(module_path)
    module_name = f"_external_engine_{path.stem}_{abs(hash(path))}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    fn = getattr(module, function_name)
    return fn


def execute_external_engine(workload: Workload, decision: RouteDecision) -> dict[str, Any]:
    if decision.route != "external_engine":
        raise ValueError(f"External engine backend received route {decision.route!r}")
    if workload.engine is None:
        raise ValueError("External engine backend requires EngineSpec")

    fn = load_function(workload.engine.module_path, workload.engine.function_name)
    result = fn(**dict(workload.engine.kwargs))
    return {
        "engine_id": workload.engine.engine_id,
        "module_path": workload.engine.module_path,
        "module_sha256": file_sha256(workload.engine.module_path),
        "function_name": workload.engine.function_name,
        "kwargs": dict(workload.engine.kwargs),
        "result": result,
    }
