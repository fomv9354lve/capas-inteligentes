from __future__ import annotations

import hashlib
import json
import time
from dataclasses import asdict, dataclass, field
from typing import Any


def stable_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), default=repr)


def stable_hash(data: Any) -> str:
    return hashlib.sha256(stable_json(data).encode("utf-8")).hexdigest()


def summarize_workload(workload: Any) -> dict[str, Any]:
    summary = {
        "kind": getattr(workload, "kind", None),
        "n_qubits": getattr(workload, "n_qubits", None),
    }
    circuit = getattr(workload, "circuit", None)
    if circuit is not None:
        try:
            summary["circuit_len"] = len(circuit)
        except TypeError:
            summary["circuit_repr_hash"] = stable_hash(repr(circuit))
    tensor = getattr(workload, "tensor", None)
    if tensor is not None:
        summary["tensor_n_inputs"] = len(getattr(tensor, "inputs", ()) or ())
        summary["tensor_has_arrays"] = getattr(tensor, "arrays", None) is not None
    engine = getattr(workload, "engine", None)
    if engine is not None:
        summary["engine"] = {
            "engine_id": getattr(engine, "engine_id", None),
            "module_path": getattr(engine, "module_path", None),
            "function_name": getattr(engine, "function_name", None),
            "kwargs_hash": stable_hash(dict(getattr(engine, "kwargs", {}) or {})),
        }
    budget = getattr(workload, "budget", None)
    if budget is not None:
        summary["budget"] = asdict(budget)
    return summary


def summarize_result(result: Any) -> dict[str, Any]:
    if hasattr(result, "shape"):
        return {
            "type": type(result).__name__,
            "shape": tuple(int(x) for x in result.shape),
            "dtype": str(getattr(result, "dtype", "")),
        }
    if isinstance(result, dict):
        summary: dict[str, Any] = {
            "type": type(result).__name__,
            "repr": repr(result)[:200],
        }
        nested = result.get("result")
        if isinstance(nested, dict):
            for key in (
                "physical_evidence_level",
                "physical_evidence_detail",
                "observable",
                "units",
                "abs_error",
                "expected",
                "value",
                "benchmark_family",
                "reference_truth",
                "verification_independence",
                "certification_status",
                "source_label",
                "n",
                "depth",
                "max_bond",
            ):
                if key in nested:
                    summary[key] = nested[key]
        return summary
    return {
        "type": type(result).__name__,
        "repr": repr(result)[:200],
    }


@dataclass(frozen=True)
class TraceEvent:
    stage: str
    status: str
    metrics: dict[str, Any] = field(default_factory=dict)
    message: str = ""
    timestamp: float = field(default_factory=time.time)


@dataclass
class RunTrace:
    workload_hash: str
    workload_summary: dict[str, Any]
    trace_schema_version: str = "capas-runtrace-v2"
    hash_algorithm: str = "sha256(stable_json)"
    events: list[TraceEvent] = field(default_factory=list)
    decision_route: str | None = None
    decision_reason: str | None = None
    result_hash: str | None = None
    result_summary: dict[str, Any] | None = None
    error: str | None = None

    def add(self, stage: str, status: str, metrics: dict[str, Any] | None = None, message: str = "") -> None:
        self.events.append(TraceEvent(stage, status, metrics or {}, message))

    def as_dict(self) -> dict[str, Any]:
        return {
            "trace_schema_version": self.trace_schema_version,
            "hash_algorithm": self.hash_algorithm,
            "workload_hash": self.workload_hash,
            "workload_summary": self.workload_summary,
            "decision_route": self.decision_route,
            "decision_reason": self.decision_reason,
            "result_hash": self.result_hash,
            "result_summary": self.result_summary,
            "error": self.error,
            "events": [asdict(e) for e in self.events],
        }

    def hash(self) -> str:
        return stable_hash(self.as_dict())


def new_trace(workload: Any) -> RunTrace:
    summary = summarize_workload(workload)
    return RunTrace(workload_hash=stable_hash(summary), workload_summary=summary)
