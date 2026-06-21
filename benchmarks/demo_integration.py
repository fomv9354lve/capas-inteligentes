"""Demo + check: integration (Φ-proxy, nodal vs layered) + process reward (generation).

Deterministic; no network/key. Asserts:
  - INTEGRATION: a disjoint set of grounded checks is REDUCIBLE (algebraic
    connectivity λ₂ = 0); coupling them (nodal reciprocity edges) makes the whole
    IRREDUCIBLE (λ₂ > 0); stronger coupling raises λ₂ toward the irreducible.
  - PROCESS REWARD: the value function gives a positive step reward for a
    groundable continuation (adds citable raw data) and ~0 for an ungroundable one
    — steering generation at the state level toward verifiability.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import capas_braid as B
import capas_integration as I
import capas_value as VAL
import capas_process as PR
from scipy import stats as _stats

SV = "capas-claim-payload-v3"
FIN = {"reported_value": 1.0, "reference_value": 1.0, "tolerance": 1.0, "metric_period_match": True}


def _ratio(cid, ca, cl, rep):
    return {"schema_version": SV, "claim": {"id": cid, "type": "financial_metric_claim", "text": cid},
            "evidence": {**FIN, "accounting": {"identity": "financial_ratio", "ratio": "current_ratio",
                                               "current_assets": ca, "current_liabilities": cl, "reported": rep}}}


def run() -> int:
    checks = []

    # INTEGRATION — nodal coupling raises the Φ-proxy
    disjoint = B.Braid()
    for i, (ca, cl) in enumerate([(200, 100), (300, 100), (400, 200)]):
        disjoint.add(_ratio(f"d{i}", ca, cl, ca / cl), target=f"t{i}", value=ca / cl, method=f"m{i}")
    lam_disjoint = I.integration(disjoint)["algebraic_connectivity"]
    checks.append(("disjoint grounded checks are REDUCIBLE (λ₂ = 0 — not one thought)",
                   lam_disjoint == 0.0 and not I.integration(disjoint)["irreducible"]))

    coupled = B.Braid()
    ids = []
    for i, (ca, cl) in enumerate([(200, 100), (300, 100), (400, 200)]):
        r = coupled.add(_ratio(f"c{i}", ca, cl, ca / cl), target=f"t{i}", value=ca / cl, method=f"m{i}")
        ids.append(r["claim_id"])
    coupled.couple(ids[0], ids[1]); coupled.couple(ids[1], ids[2])      # a chain (nodal)
    lam_chain = I.integration(coupled)["algebraic_connectivity"]
    coupled.couple(ids[0], ids[2])                                       # close the loop (stronger)
    lam_loop = I.integration(coupled)["algebraic_connectivity"]
    checks.append(("coupling makes it IRREDUCIBLE (λ₂ > 0) and stronger coupling raises λ₂",
                   lam_chain > 0.0 and lam_loop > lam_chain and I.integration(coupled)["irreducible"]))

    # PROCESS REWARD — verification shapes generation at the state level
    a = [10.1, 10.3, 9.9, 10.2, 10.0, 10.4, 9.8, 10.1]
    b = [12.0, 12.3, 11.8, 12.1, 12.2, 11.9, 12.4, 12.0]
    p = round(float(_stats.ttest_ind(a, b, equal_var=False)[1]), 5)

    def stat(ev):
        return {"schema_version": SV, "claim": {"id": "s", "type": "statistical_confidence", "text": "t"}, "evidence": ev}
    pool = [_ratio(f"v{ca}", ca, cl, ca / cl) for ca, cl in [(200, 100), (300, 100), (400, 200), (150, 100)]]
    pool += [stat({"p_value": p, "alpha": 0.05, "effect_direction_confirmed": True, "raw_data": {"group_a": a, "group_b": b}}),
             stat({"p_value": 0.01, "alpha": 0.05, "effect_direction_confirmed": True})]
    model = VAL.ValueModel().fit(pool)

    current = stat({"p_value": p, "alpha": 0.05, "effect_direction_confirmed": True})          # bare conjecture
    add_groundable = stat({"p_value": p, "alpha": 0.05, "effect_direction_confirmed": True,
                           "raw_data": {"group_a": a, "group_b": b}})                          # cite raw data
    add_fluent = stat({"p_value": p, "alpha": 0.05, "effect_direction_confirmed": True, "note": "very significant!!"})  # ungroundable
    ranked = PR.rank_continuations(current, [add_fluent, add_groundable], model)
    checks.append(("process reward: groundable continuation beats the fluent-ungroundable one",
                   ranked[0][1] is add_groundable and ranked[0][0] > 0 and ranked[1][0] <= ranked[0][0]))
    traj = PR.trajectory([current, add_groundable], model)
    checks.append(("groundability rises as a citable element is added (state-level guidance)",
                   traj[1] > traj[0]))

    ok = True
    for label, good in checks:
        ok = ok and good
        print(f"{'✅' if good else '❌'} {label}")
    print("INTEGRATION + PROCESS: all checks pass ✅" if ok else "INTEGRATION/PROCESS: FAILURES ❌")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(run())
