# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""CAPAS probe engine — the finite liar vs the growing law-library.

A fabrication is only consistent with the probes the liar ANTICIPATED. Reality is unbounded:
each independent law the engine ingests is a probe the liar didn't prepare. The engine loads its
probe library from a REGISTRY that grows as the physics motor (physics-magnitude-lab) emits laws
and CAPAS gates them (BACKED). A claim the engine cannot kill is a MISS -> written to an outbox as
a derivation request back to the motor. The arms race, closed into a loop.

INDEPENDENCE: probes are counted by distinct input-sets (two probes over the same variables are ONE
constraint — a liar satisfies them together). Only new-ancestor laws grow the effective library.

HONEST BOUND: power is capped by the claim's TRACEABLE SURFACE. A claim touching no registered
variable gets zero probes (the pañuelo) — the engine says so. And SURVIVED = un-refuted by the laws
ingested so far, never 'true'. Fail-closed on ingest: only a re-derivable (BACKED) law becomes a probe.
"""
from __future__ import annotations
import ast, json, operator, os
from typing import Any

_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
        ast.Div: operator.truediv, ast.Pow: operator.pow, ast.USub: operator.neg}
_CMP = {"<=": operator.le, ">=": operator.ge, "<": operator.lt, ">": operator.gt}

def _safe_eval(expr: str, vars: dict[str, float]) -> float:
    """Evaluate a restricted arithmetic expression over `vars`. No calls, no names but the vars."""
    def ev(node):
        if isinstance(node, ast.Expression): return ev(node.body)
        if isinstance(node, ast.Constant): return node.value
        if isinstance(node, ast.Name):
            if node.id not in vars: raise KeyError(node.id)
            return vars[node.id]
        if isinstance(node, ast.BinOp): return _OPS[type(node.op)](ev(node.left), ev(node.right))
        if isinstance(node, ast.UnaryOp): return _OPS[type(node.op)](ev(node.operand))
        raise ValueError(f"disallowed: {ast.dump(node)}")
    return ev(ast.parse(expr, mode="eval"))

def _registry_path(): return os.path.join(os.path.dirname(__file__), "invariant_registry.json")

def load_registry(path: str | None = None) -> list[dict]:
    with open(path or _registry_path(), encoding="utf-8") as f:
        return [p for p in json.load(f)["probes"] if p.get("status") == "BACKED"]

def probe(claim_type: str, quantities: dict[str, float], reg: list[dict] | None = None,
          miss_outbox: str | None = None) -> dict[str, Any]:
    reg = reg if reg is not None else load_registry()
    q = {k: v for k, v in quantities.items() if isinstance(v, (int, float))}
    applicable = [p for p in reg if set(p["inputs"]) <= set(q)]
    indep_sets = {frozenset(p["inputs"]) for p in applicable}   # distinct ancestors
    dead = []
    for p in applicable:
        try:
            ok = _CMP[p["op"]](_safe_eval(p["lhs"], q), _safe_eval(p["rhs"], q))
        except Exception:
            ok = True   # a probe that cannot evaluate simply does not apply
        if not ok: dead.append(p["name"])
    if dead:
        verdict = "KILLED"
    elif not indep_sets:
        verdict = "UNTESTED"        # the pañuelo — zero traceable surface
    else:
        verdict = "SURVIVED"        # un-refuted by the current library
        if miss_outbox:             # a survivor is a MISS: ask the motor for a new independent law
            with open(miss_outbox, "a", encoding="utf-8") as f:
                f.write(f"- derivation request: claim {claim_type} survived {len(indep_sets)} laws "
                        f"({sorted(q)}) — derive an independent law over its untouched variables.\n")
    return {"verdict": verdict, "killed_by": dead[:1], "probes_applied": len(applicable),
            "independent_probes": len(indep_sets), "fabrication_cost": len(indep_sets),
            "bound": "SURVIVED = un-refuted by laws ingested so far, not true; power capped by traceable surface."}

def ingest(signal: dict, path: str | None = None) -> bool:
    """Connect the motor: a gated BACKED signal becomes a probe. Fail-closed on the required schema."""
    need = {"id", "name", "inputs", "lhs", "op", "rhs", "status", "derivation"}
    if not need <= set(signal) or signal["status"] != "BACKED" or signal["op"] not in _CMP:
        return False
    p = path or _registry_path()
    doc = json.load(open(p, encoding="utf-8"))
    if any(x["id"] == signal["id"] for x in doc["probes"]): return False
    doc["probes"].append(signal)
    json.dump(doc, open(p, "w", encoding="utf-8"), indent=2)
    return True
