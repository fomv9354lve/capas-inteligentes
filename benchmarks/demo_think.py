# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""Demo + check: CAPAS settling dynamics — the engine THINKS, not only verifies.

Deterministic; no network/key. Asserts:
  - the hierarchy SETTLES (relaxation): residual falls to 0 and the certification
    layer IGNITES all-or-none -> a grounded thought;
  - a sub-claim the proposer cannot close -> the residual STABILIZES > 0 (fixed
    point) -> DEFERRED to the subject (the open frontier);
  - the BRAID integration core makes the verdict irreducible: grounded leaves that
    disagree on the same target are BRAID-INCOHERENT (the IIT fault), even though
    each is locally grounded.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import capas_think as T
from scipy import stats as _stats

SV = "capas-claim-payload-v3"
FIN = {"reported_value": 1.0, "reference_value": 1.0, "tolerance": 1.0, "metric_period_match": True}


def run() -> int:
    a = [10.1, 10.3, 9.9, 10.2, 10.0, 10.4, 9.8, 10.1]
    b = [12.0, 12.3, 11.8, 12.1, 12.2, 11.9, 12.4, 12.0]
    p = round(float(_stats.ttest_ind(a, b, equal_var=False)[1]), 5)

    def conj(cid, target, val):
        return {"schema_version": SV, "claim": {"id": cid, "type": "statistical_confidence", "text": cid},
                "evidence": {"p_value": p, "alpha": 0.05, "effect_direction_confirmed": True,
                             "target": target, "value": val}}

    def top(cid, deps):
        return {"schema_version": SV, "claim": {"id": cid, "type": "financial_metric_claim", "text": cid},
                "evidence": {**FIN, "accounting": {"identity": "balance_sheet", "assets": 1000,
                                                   "liabilities": 600, "equity": 400}, "depends_on": deps}}

    def supply(c):
        ev = dict(c["evidence"]); ev["raw_data"] = {"group_a": a, "group_b": b}
        return {**c, "evidence": ev}

    def supply_partial(c):
        if c["claim"]["id"] == "s2":
            return None
        return supply(c)

    checks = []

    r = T.settle(top("X", [conj("s1", "t1", 1.0), conj("s2", "t2", 1.0)]), supply)
    checks.append(("settles to ignition (residual -> 0, ignited, braid-coherent)",
                   r["ignited"] and r["residual_trajectory"][-1] == 0 and r["residual_trajectory"][0] > 0
                   and r["verdict"].startswith("GROUNDED")))

    r2 = T.settle(top("Y", [conj("s1", "t1", 1.0), conj("s2", "t2", 1.0)]), supply_partial)
    checks.append(("a non-closeable sub-claim -> residual stabilizes > 0 -> DEFERRED to subject",
                   not r2["ignited"] and r2["settled_residual"] > 0 and r2["verdict"].startswith("DEFERRED")))

    agree = T.settle(top("Z", [conj("s1", "RATIO", 2.0), conj("s2", "RATIO", 2.0)]), supply)
    disagree = T.settle(top("Z2", [conj("s1", "RATIO", 2.0), conj("s2", "RATIO", 9.0)]), supply)
    checks.append(("integration core: agreeing leaves ignite; disagreeing leaves are BRAID-INCOHERENT (IIT)",
                   agree["ignited"] and disagree["verdict"] == "BRAID-INCOHERENT" and len(disagree["braid_faults"]) >= 1))

    ok = True
    for label, good in checks:
        ok = ok and good
        print(f"{'✅' if good else '❌'} {label}")
    print("SETTLING / THINKING: all checks pass ✅" if ok else "THINKING: FAILURES ❌")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(run())
