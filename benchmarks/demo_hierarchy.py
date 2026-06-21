"""Demo + check: the layered triad (capas) — multi-hop, regime-gradient verdict.

The verdict is a COMPOSITION across layers/regimes, not a flat deterministic
decision. Asserts multi-hop grounding (all deps grounded -> VERIFIED), refutation
propagating up (one refuted dep -> REFUTED), and an unbacked dep leaving a residual
the subject must close (-> ATTEST_DEFER, frontier). Plus a value-function-at-scale
check (the learned guide tracks the deterministic grade across many payloads).
Deterministic; no network/key.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import capas_hierarchy as H
import capas_value as VAL
import capas_admissibility as A

SV = "capas-claim-payload-v3"
FIN = {"reported_value": 1.0, "reference_value": 1.0, "tolerance": 1.0, "metric_period_match": True}


def _ratio(cid, ca, cl, rep):
    return {"schema_version": SV, "claim": {"id": cid, "type": "financial_metric_claim", "text": cid},
            "evidence": {**FIN, "accounting": {"identity": "financial_ratio", "ratio": "current_ratio",
                                               "current_assets": ca, "current_liabilities": cl, "reported": rep}}}


def _top(cid, deps):
    return {"schema_version": SV, "claim": {"id": cid, "type": "financial_metric_claim", "text": cid},
            "evidence": {**FIN, "accounting": {"identity": "balance_sheet", "assets": 1000,
                                               "liabilities": 600, "equity": 400}, "depends_on": deps}}


def run() -> int:
    sub1, sub2 = _ratio("r1", 200, 100, 2.0), _ratio("r2", 400, 200, 2.0)
    lie = _ratio("rlie", 200, 100, 9.0)
    unbacked = {"schema_version": SV, "claim": {"id": "mech", "type": "causal_mechanism_claim", "text": "mechanism"},
                "evidence": {"intervention_or_natural_experiment": True, "temporal_order_established": True,
                             "confounders_controlled": True, "mechanism_evidence_present": True}}

    checks = []
    g = H.certify_hierarchy(_top("solvent", [sub1, sub2]))
    checks.append(("multi-hop: all dependencies grounded -> VERIFIED",
                   g["composed_verdict"] == "VERIFIED" and g["layers_traversed"] >= 2))
    checks.append(("regime gradient reported (generative..deterministic..apophatic)",
                   len(g["regime_gradient"]) == 5 and "deterministic" in g["regime_gradient"][1]))
    r = H.certify_hierarchy(_top("solvent2", [sub1, lie]))
    checks.append(("refutation in a sub-claim PROPAGATES up -> REFUTED",
                   r["composed_verdict"] == "REFUTED"))
    d = H.certify_hierarchy(_top("solvent3", [sub1, unbacked]))
    checks.append(("an unbacked sub-claim leaves a residual -> ATTEST_DEFER, frontier to subject",
                   d["composed_verdict"] == "ATTEST_DEFER" and [f["claim"] for f in d["frontier"]] == ["mech"]))

    # value function at scale: fit on many engine-generated payloads, check it tracks the grade
    pool = []
    for ca, cl, rep in [(200, 100, 2.0), (300, 100, 3.0), (400, 200, 2.0), (150, 100, 1.5),
                        (500, 250, 2.0), (120, 100, 1.2), (90, 100, 0.9), (1000, 400, 2.5)]:
        pool.append(_ratio(f"v{ca}", ca, cl, rep))                       # grounded
    for pv in [0.01, 0.04, 0.2]:
        pool.append({"schema_version": SV, "claim": {"id": f"s{pv}", "type": "statistical_confidence", "text": "t"},
                     "evidence": {"p_value": pv, "alpha": 0.05, "effect_direction_confirmed": True}})  # declared
    m = VAL.ValueModel().fit(pool)
    import numpy as np
    pred = np.array([m.predict(p) for p in pool])
    true = np.array([A.admissibility(p)["score"] for p in pool])
    corr = float(np.corrcoef(pred, true)[0, 1])
    checks.append((f"value function tracks the deterministic grade at scale (corr={corr:.2f} >= 0.6)", corr >= 0.6))

    ok = True
    for label, good in checks:
        ok = ok and good
        print(f"{'✅' if good else '❌'} {label}")
    print("LAYERED HIERARCHY: all checks pass ✅" if ok else "HIERARCHY: FAILURES ❌")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(run())
