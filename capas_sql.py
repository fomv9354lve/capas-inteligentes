# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""CAPAS — tabular SQL-aggregate re-derivation + Proof-of-SQL scale hook.

The macrophage move for 'ZK at scale' (Space and Time's Proof of SQL: sub-second
ZK proofs over 1M+ rows). CAPAS absorbs it two ways, both keeping the moat:

  * SMALL data CAPAS OWNS — rederive_sql() re-computes a claimed aggregate
    (SUM/AVG/COUNT/MIN/MAX, optional WHERE and GROUP BY) directly from supplied
    rows and checks it against the reported value. A real new tabular rung
    (clinical ADaM aggregates, financial roll-ups), deterministic.
  * LARGE data CAPAS VERIFIES — a Proof-of-SQL proof grounds the same aggregate
    succinctly without shipping/re-running the rows. CAPAS is the verifier; the
    GPU prover (sxt-proof-of-sql) is external, registered through the EXISTING ZK
    rung (capas_verify.register_zk_backend). The reference backend here binds the
    query result to the table commitment so the path is runnable/testable; a
    production deployment registers the real sxt verifier.
"""
from __future__ import annotations

import hashlib
import operator
from typing import Any

_CMP = {"==": operator.eq, "!=": operator.ne, ">": operator.gt, ">=": operator.ge,
        "<": operator.lt, "<=": operator.le}


def _where(rows: list[dict], w: dict | None) -> list[dict]:
    if not w:
        return rows
    col, op, val = w["column"], w.get("op", "=="), w["value"]
    return [r for r in rows if _CMP[op](r.get(col), val)]


def _agg(values: list, op: str) -> float:
    if op == "count":
        return float(len(values))
    nums = [float(v) for v in values]
    if op == "sum":
        return sum(nums)
    if op == "avg":
        return sum(nums) / len(nums) if nums else 0.0
    if op == "min":
        return min(nums)
    if op == "max":
        return max(nums)
    raise ValueError(f"unsupported aggregate {op}")


def rederive_sql(evidence: dict[str, Any]) -> dict[str, Any] | None:
    """Re-derive a claimed SQL aggregate from the rows. evidence['sql'] =
    {rows, query:{op, column, where?, group_by?}, reported, tolerance}."""
    q = evidence.get("sql")
    if not isinstance(q, dict):
        return None
    rows, query = q.get("rows"), q.get("query") or {}
    reported, tol = q.get("reported"), float(q.get("tolerance", 1e-6) or 0.0)
    op, col, gb = query.get("op"), query.get("column"), query.get("group_by")
    try:
        sel = _where(rows, query.get("where"))
        if gb:
            groups: dict[Any, list] = {}
            for r in sel:
                groups.setdefault(r.get(gb), []).append(1 if op == "count" else r.get(col))
            re_derived = {str(k): round(_agg(v, op), 6) for k, v in groups.items()}
            match = (isinstance(reported, dict)
                     and set(re_derived) == set(map(str, reported))
                     and all(abs(re_derived[str(k)] - float(reported[k])) <= tol for k in reported))
            return {"op": op, "group_by": gb, "re_derived": re_derived, "reported": reported,
                    "rows_scanned": len(sel), "match": bool(match)}
        vals = sel if op == "count" else [r.get(col) for r in sel]
        re_derived = _agg(vals, op)
        match = reported is not None and abs(re_derived - float(reported)) <= tol
        return {"op": op, "re_derived": round(re_derived, 6), "reported": reported,
                "rows_scanned": len(sel), "match": bool(match)}
    except (KeyError, ValueError, TypeError):
        return {"status": "MALFORMED", "match": False}


# ── Proof-of-SQL scale backend (verification side; registered in the ZK rung) ──
def sql_proof_backend(proof: dict[str, Any], public_inputs: dict[str, Any], statement: Any) -> bool:
    """Reference verifier: a Proof-of-SQL proof binds the claimed query RESULT to a
    commitment of the table, so a large aggregate is grounded without re-running the
    rows. Reference binding = sha256(table_commitment | query | result | nonce); a
    production deployment registers the real sxt-proof-of-sql verifier instead."""
    p = proof or {}
    needed = ("table_commitment", "query", "result", "nonce", "opening")
    if not all(k in p for k in needed):
        return False
    recomputed = "sha256:" + hashlib.sha256(
        f"{p['table_commitment']}|{p['query']}|{p['result']}|{p['nonce']}".encode()).hexdigest()
    return recomputed == p["opening"] and str(p["result"]) == str(public_inputs.get("reported"))


def register(verifier=None) -> None:
    """Register the Proof-of-SQL backend in CAPAS's ZK rung. Pass the real sxt
    verifier for production; omit to use the reference commitment-binding backend."""
    import capas_verify
    capas_verify.register_zk_backend("proof-of-sql", verifier or sql_proof_backend)
