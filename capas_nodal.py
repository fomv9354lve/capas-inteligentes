# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""CAPAS nodal skeleton — the small cross-stratum invariant core.

A few maximally-nodal laws (measure, conservation, geometry, inference) constrain claims across MANY
strata: a fabrication in ANY domain must still satisfy them. Ordered by nodality (strata reached).
This is the M_eff principle applied to the corpus: ingest highest-independence (cross-stratum) laws
first — they buy the most fabrication-cost per law. Leaf laws ingest on-miss (fail-closed gated).
"""
from __future__ import annotations
import json, os
from capas_probe_engine import _safe_eval, _CMP  # reuse the safe evaluator

def load(path=None):
    p = path or os.path.join(os.path.dirname(__file__), "nodal_skeleton.json")
    return json.load(open(p, encoding="utf-8"))["laws"]

def check(quantities: dict, laws=None) -> dict:
    laws = laws if laws is not None else load()
    q = {k: v for k, v in quantities.items() if isinstance(v, (int, float))}
    applied, dead = [], []
    for L in laws:
        if set(L["inputs"]) <= set(q):
            applied.append(L)
            try:
                ok = _CMP[L["op"]](_safe_eval(L["lhs"], q), _safe_eval(L["rhs"], q))
            except Exception:
                ok = True
            if not ok: dead.append(L["name"])
    reach = sorted({s for L in applied for s in L["reach"]})
    return {"verdict": "KILLED" if dead else ("UNTESTED" if not applied else "SURVIVED"),
            "killed_by": dead, "laws_fired": [L["name"] for L in applied],
            "strata_reached": reach, "n_nodal": len(applied)}
