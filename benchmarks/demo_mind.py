# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""Deep end-to-end: the full cognitive loop wired through capas_mind.cognize().

Exercises generate(guided) -> settle -> integrate(nodal Φ-core) -> certify in one
call, on a realistic multi-claim scenario. Deterministic; no network/key.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import capas_mind as M
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

    checks = []

    # full loop: two conjectures on the SAME target (coupled) -> settle, integrate, ignite
    cog = M.cognize(top("thesis", [conj("e1", "FINDING", 1.0), conj("e2", "FINDING", 1.0)]), supply)
    th = cog["thought"]
    checks.append(("cognize wires the loop: settles + integrates + certifies in one call",
                   set(["verdict", "thought", "certificate", "frontier_to_subject"]).issubset(cog)))
    checks.append(("ignites a grounded thought (residual->0) with an IRREDUCIBLE core (Φ>0)",
                   th["ignited"] and th["settled_residual"] == 0 and th["integration_phi_proxy"] > 0
                   and th["irreducible"]))
    checks.append(("the unified certificate carries the RCC strata + the Löbian self-bar",
                   "strata" in cog["certificate"] and "parallax_self_bar" in cog["certificate"]))

    # a non-closeable sub-claim -> the loop defers to the subject (open frontier)
    def supply_partial(c):
        return None if c["claim"]["id"] == "e2" else supply(c)
    cog2 = M.cognize(top("thesis2", [conj("e1", "FINDING", 1.0), conj("e2", "FINDING", 1.0)]), supply_partial)
    checks.append(("an unprovable sub-claim -> DEFERRED, the frontier handed to the subject",
                   cog2["thought"]["ignited"] is False and cog2["thought"]["settled_residual"] > 0))

    # generation guidance wired: the value model steers toward the groundable continuation
    pool = [conj(f"g{i}", "X", 1.0) for i in range(3)] + [supply(conj("gg", "X", 1.0))]
    vm = M.fit_value([{**c, "evidence": {k: v for k, v in c["evidence"].items() if k not in ("target", "value")}} for c in pool])
    current = {**conj("cur", "X", 1.0), "evidence": {k: v for k, v in conj("cur", "X", 1.0)["evidence"].items() if k not in ("target", "value")}}
    groundable = {**current, "evidence": {**current["evidence"], "raw_data": {"group_a": a, "group_b": b}}}
    fluent = {**current, "evidence": {**current["evidence"], "note": "clearly true"}}
    choice = M.guided_choice(current, [fluent, groundable], vm)
    checks.append(("generation step wired: the value model chooses the groundable continuation",
                   choice["chosen"] is groundable and choice["gain"] > 0))

    ok = True
    for label, good in checks:
        ok = ok and good
        print(f"{'✅' if good else '❌'} {label}")
    print("FULL COGNITIVE LOOP (capas_mind): all checks pass ✅" if ok else "MIND: FAILURES ❌")
    if ok:
        print(f"\n  sample thought: verdict={cog['verdict']} passes={th['passes']} "
              f"residual={th['residual_trajectory']} Φ-proxy={th['integration_phi_proxy']} irreducible={th['irreducible']}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(run())
