#!/usr/bin/env python3
"""Real, re-derivable gate decisions shown on the home page (de-mock: no illustrative numbers).

Every verdict + audit_hash rendered in the home's "Recent Gate Decisions" panel and verdict-reference
cards is produced HERE by the real engine. A visitor (or CI) re-runs this and gets byte-identical
verdicts and hashes — that is the spine: CAPAS gates its own claims, re-derivably.

Run:  python3 benchmarks/home_gate_decisions.py          # prints the table
      python3 benchmarks/home_gate_decisions.py --json   # emits outputs/home_gate_decisions.json
"""
import json
import sys
import capas_sdk

# (label, claim_type, evidence, claim_text, claim_id) — the four canonical dispositions.
CASES = [
    ("ACCEPT", "statistical_confidence",
     {"p_value": 0.03, "alpha": 0.05, "effect_direction_confirmed": True},
     "Treatment reduced the endpoint at p=0.03.", "home_accept"),
    ("REWRITE", "statistical_confidence",
     {"p_value": 0.03, "alpha": 0.05, "effect_direction_confirmed": False},
     "Treatment causes the improvement (p=0.03).", "home_rewrite"),
    ("REJECT", "reproducibility_check",
     {"artifact_available": False, "independent_reproduction_pass": False},
     "Result reproduces on any machine.", "home_reject"),
    ("HOLD", "statistical_confidence",
     {"p_value": 0.03, "alpha": 0.05},  # effect_direction_confirmed missing -> fail-closed HOLD
     "Significant effect at p=0.03.", "home_hold"),
    # The "Every decision is an audit artifact" JSON block on the home (claim_drift_001).
    ("REJECT", "causal_mechanism_claim",
     {"intervention_or_natural_experiment": False, "temporal_order_established": True,
      "confounders_controlled": True, "mechanism_evidence_present": True},
     "X causes Y.", "claim_drift_001"),
]


def decisions():
    out = []
    for label, ct, ev, text, cid in CASES:
        r = capas_sdk.gate(ct, ev, text, cid)
        out.append({
            "label": label,
            "claim_type": ct,
            "evidence": ev,
            "verdict": r.get("verdict"),
            "reason": r.get("reason"),
            "rewrite": r.get("rewrite"),
            "audit_hash": r.get("audit_hash"),
        })
    return out


def main() -> int:
    rows = decisions()
    if "--json" in sys.argv:
        path = "outputs/home_gate_decisions.json"
        json.dump(rows, open(path, "w"), indent=2)
        print(f"wrote {path}")
        return 0
    for d in rows:
        print(f"[{d['verdict']:>7}] {d['claim_type']}")
        print(f"          reason : {d['reason']}")
        if d["rewrite"]:
            print(f"          rewrite: {d['rewrite']}")
        print(f"          {d['audit_hash']}")
    # Sanity: the dispositions must be exactly these (fail loud if the engine drifts).
    got = [d["verdict"] for d in rows]
    assert got == ["ACCEPT", "REWRITE", "REJECT", "HOLD", "REJECT"], f"verdict drift: {got}"
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
