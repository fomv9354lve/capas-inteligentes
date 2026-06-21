"""Demo + check: the open-forward-closing triad engine (#1 bridge, #2 spiral, #3 conformal).

Deterministic; no network/key. Asserts:
  #1 bridge      — a conjecture compiles a checkable bridge; a refuted claim does
                   not; an unbacked claim's bridge ends at the subject.
  #2 spiral      — a conjecture carried forward CLOSES FORWARD into the substrate
                   when its bridge is walked; refuted pruned; unbacked -> boundary.
  #3 conformal   — a real distribution-free coverage guarantee, that VOIDS honestly
                   under exchangeability failure (the {unknowable} face).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import capas_conjecture as CJ
import capas_loop as LP
import capas_conformal as CF
from scipy import stats as _stats

SV = "capas-claim-payload-v3"
FIN = {"reported_value": 1.0, "reference_value": 1.0, "tolerance": 1.0, "metric_period_match": True}


def _p(cid, t, ct, ev):
    return {"schema_version": SV, "claim": {"id": cid, "type": ct, "text": t}, "evidence": ev}


def run() -> int:
    a = [10.1, 10.3, 9.9, 10.2, 10.0, 10.4, 9.8, 10.1]
    b = [12.0, 12.3, 11.8, 12.1, 12.2, 11.9, 12.4, 12.0]
    p = round(float(_stats.ttest_ind(a, b, equal_var=False)[1]), 5)
    checks = []

    # #1 bridge compiler
    decl = _p("t1", "treatment works", "statistical_confidence",
              {"p_value": p, "alpha": 0.05, "effect_direction_confirmed": True})
    b1 = CJ.bridge(decl)
    checks.append(("#1 conjecture compiles a checkable bridge (leaf next step)",
                   b1["bridge_length"] >= 1 and b1["next_step"]["terminates"] == "leaf"))
    causal = _p("t3", "X causes Y", "causal_mechanism_claim",
                {"intervention_or_natural_experiment": True, "temporal_order_established": True,
                 "confounders_controlled": True, "mechanism_evidence_present": True})
    b2 = CJ.bridge(causal)
    checks.append(("#1 unbacked claim's bridge ends at the subject",
                   "SUBJECT" in b2["status"] and any(r["terminates"] == "subject" for r in b2["residual_to_subject"])))
    refuted = _p("t2", "Water boils at 500C", "statistical_confidence",
                 {"p_value": 0.01, "alpha": 0.05, "effect_direction_confirmed": True})
    checks.append(("#1 refuted claim gets NO bridge (refutation, not absence of proof)",
                   CJ.bridge(refuted)["status"].startswith("REFUTED")))

    # #2 spiral closes forward
    def proposer(r, substrate, frontier):
        if r == 0:
            return [decl]                      # conjecture -> frontier
        if r == 1:
            grounded = _p("t1", "treatment works", "statistical_confidence",
                          {"p_value": p, "alpha": 0.05, "effect_direction_confirmed": True,
                           "raw_data": {"group_a": a, "group_b": b}})  # walk the bridge
            return [grounded, refuted, causal]
        return []
    sp = LP.spiral(proposer, rounds=2)
    closed_fwd = any("CLOSED FORWARD" in e[0] for t in sp["trajectory"] for e in t["events"])
    checks.append(("#2 spiral: conjecture CLOSES FORWARD into the substrate",
                   closed_fwd and len(sp["substrate"]) == 1))
    checks.append(("#2 spiral: refuted pruned, unbacked deferred to boundary",
                   len(sp["boundary"]) == 1 and len(sp["frontier"]) == 0))

    # #3 conformal coverage
    cal = [0.001, 0.002, 0.0015, 0.0008, 0.003, 0.0012, 0.0025, 0.0009, 0.0018, 0.0022,
           0.0011, 0.0013, 0.0007, 0.0026, 0.0014, 0.0019, 0.0021, 0.0006, 0.0016, 0.0028]
    in_band = CF.certify(CF.nonconformity(50.02, 50.0), cal, alpha=0.1)
    checks.append(("#3 conformal: in-band score is covered with a real guarantee",
                   in_band["covered"] is True and "marginal coverage >= 0.90" in in_band["guarantee"]))
    out_band = CF.certify(CF.nonconformity(70.0, 50.0), cal, alpha=0.1)
    checks.append(("#3 conformal: out-of-band score is NOT covered",
                   out_band["covered"] is False))
    voided = CF.certify(0.001, cal, alpha=0.1, exchangeable=False)
    checks.append(("#3 conformal: VOIDS under exchangeability failure (-> {unknowable})",
                   voided["covered"] is None and "exchangeability_failure" in voided["reason"]))
    thin = CF.certify(0.001, [0.001, 0.002], alpha=0.1)
    checks.append(("#3 conformal: insufficient calibration is reported, not faked",
                   thin["covered"] is None and "insufficient_calibration" in thin["reason"]))

    ok = True
    for label, good in checks:
        ok = ok and good
        print(f"{'✅' if good else '❌'} {label}")
    print("ENGINE (bridge + spiral + conformal): all checks pass ✅" if ok else "ENGINE: FAILURES ❌")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(run())
