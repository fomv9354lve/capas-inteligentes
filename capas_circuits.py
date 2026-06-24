# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""CAPAS — arithmetic-circuit (R1CS) backend for re-derivation rules.

Turns a re-derivation rule into a Rank-1 Constraint System — the exact object a
SNARK (groth16 / EZKL / halo2) proves knowledge of a satisfying witness for — and
verifies that a supplied witness satisfies every constraint and binds to the
declared public output.

This is REAL and runnable: R1CS satisfiability *is* the circuit. What a production
SNARK adds on top of this same R1CS is succinctness (constant-size proof) and
zero-knowledge (the witness stays hidden). Register a production verifier via
capas_verify.register_zk_backend("ezkl-<vk>", ...); this `capas-r1cs` backend is
the deterministic, dependency-free reference that proves the circuit layer works.

A constraint is (A·w) * (B·w) = (C·w), where each of A/B/C is a linear combination
over the witness w (a map var->value, with the constant wire "one" = 1).
"""
from __future__ import annotations

import ast
import operator
from typing import Any

LinComb = dict[str, float]
Constraint = tuple[LinComb, LinComb, LinComb]
_EPS = 1e-6


# ── linear-combination compiler (parses an affine expression over named vars) ──
def _linear_combo(expr: str, allowed: set[str]) -> LinComb:
    """Parse a *linear* arithmetic expression into a linear combination. Rejects
    var*var (nonlinear) — those would need intermediate-wire constraints."""
    def comb(node: ast.AST) -> LinComb:
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return {"one": float(node.value)}
        if isinstance(node, ast.Name):
            if node.id not in allowed:
                raise ValueError(f"unknown variable '{node.id}'")
            return {node.id: 1.0}
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            inner = comb(node.operand)
            sign = -1.0 if isinstance(node.op, ast.USub) else 1.0
            return {k: sign * v for k, v in inner.items()}
        if isinstance(node, ast.BinOp):
            left, right = comb(node.left), comb(node.right)
            if isinstance(node.op, ast.Add):
                return _add(left, right)
            if isinstance(node.op, ast.Sub):
                return _add(left, {k: -v for k, v in right.items()})
            if isinstance(node.op, (ast.Mult, ast.Div)):
                lc = _const(left); rc = _const(right)
                if isinstance(node.op, ast.Mult):
                    if lc is not None:
                        return {k: lc * v for k, v in right.items()}
                    if rc is not None:
                        return {k: rc * v for k, v in left.items()}
                    raise ValueError("nonlinear (var*var) needs an intermediate-wire circuit")
                # Div: only by a constant keeps it linear
                if rc is not None and rc != 0:
                    return {k: v / rc for k, v in left.items()}
                raise ValueError("nonlinear division needs an intermediate-wire circuit")
        raise ValueError("disallowed expression element")

    return comb(ast.parse(str(expr), mode="eval").body)


def _add(a: LinComb, b: LinComb) -> LinComb:
    out = dict(a)
    for k, v in b.items():
        out[k] = out.get(k, 0.0) + v
    return out


def _const(lc: LinComb) -> float | None:
    """Return the constant value of a linear combination, or None if it has vars."""
    if set(lc) <= {"one"}:
        return lc.get("one", 0.0)
    return None


# ── compile a re-derivation rule into R1CS constraints ──
def compile_rule(rule: dict[str, Any], output_var: str) -> dict[str, Any]:
    op = rule.get("operation")
    one = {"one": 1.0}
    if op == "linear_calibration":   # slope * x = signal - intercept
        cons = [({"slope": 1.0}, {output_var: 1.0}, {"signal": 1.0, "intercept": -1.0})]
        public = ["signal", "intercept", "slope"]
    elif op == "ratio":              # denominator * out = numerator
        cons = [({"denominator": 1.0}, {output_var: 1.0}, {"numerator": 1.0})]
        public = ["numerator", "denominator"]
    elif op == "percent_recovery":   # expected * out = measured * 100
        cons = [({"expected": 1.0}, {output_var: 1.0}, {"measured": 100.0})]
        public = ["measured", "expected"]
    elif op == "expression":         # out = <linear combo of inputs>
        allowed = set(rule.get("inputs", [])) | {"one"}
        lc = _linear_combo(rule.get("expression", ""), allowed)
        cons = [({output_var: 1.0}, one, lc)]   # out * 1 = linear_combo
        public = sorted(set(rule.get("inputs", [])))
    else:
        raise ValueError(f"unsupported circuit operation '{op}'")
    return {"constraints": cons, "public": public, "output": output_var}


def _dot(lc: LinComb, w: dict[str, float]) -> float:
    return sum(coeff * float(w.get(var, 0.0)) for var, coeff in lc.items())


def satisfied(circuit: dict[str, Any], witness: dict[str, Any]) -> tuple[bool, list[int]]:
    w = {"one": 1.0, **{k: float(v) for k, v in witness.items()}}
    failures = []
    for i, (A, B, C) in enumerate(circuit["constraints"]):
        if abs(_dot(A, w) * _dot(B, w) - _dot(C, w)) > _EPS:
            failures.append(i)
    return (not failures, failures)


def r1cs_backend(proof: dict[str, Any], public_inputs: dict[str, Any], statement: Any) -> bool:
    """ZK-backend signature. statement = {circuit:{operation,...}, output:"<var>"};
    proof = {witness:{all wire assignments incl. the output}}; public_inputs =
    {claimed_output, public:{revealed input values}}. Verifies the witness satisfies
    the compiled R1CS AND binds to the declared public output and public inputs."""
    if not isinstance(statement, dict):
        return False
    circuit = compile_rule(statement.get("circuit") or {}, statement.get("output", "out"))
    witness = (proof or {}).get("witness") or {}
    ok, _ = satisfied(circuit, witness)
    if not ok:
        return False
    out_var = circuit["output"]
    claimed = public_inputs.get("claimed_output")
    if claimed is not None and abs(float(witness.get(out_var, 0.0)) - float(claimed)) > _EPS:
        return False
    # public inputs, if revealed, must match the witness (no input swapping)
    revealed = public_inputs.get("public") or {}
    if isinstance(revealed, dict):
        for var, val in revealed.items():
            if abs(float(witness.get(var, 0.0)) - float(val)) > _EPS:
                return False
    return True


if __name__ == "__main__":  # tiny self-check
    st = {"circuit": {"operation": "linear_calibration"}, "output": "x"}
    good = {"witness": {"signal": 105, "intercept": 5, "slope": 2, "x": 50}}
    bad = {"witness": {"signal": 105, "intercept": 5, "slope": 2, "x": 99}}
    print("good:", r1cs_backend(good, {"claimed_output": 50}, st))   # True
    print("bad :", r1cs_backend(bad, {"claimed_output": 99}, st))    # False (97.5≠99 fails R1CS)
