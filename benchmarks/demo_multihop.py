"""Demo + check: deep multi-hop bridge compiler (HTN + cycle guard + substrate cache).

Deterministic; no network/key. Asserts a 3-hop chain compiles and grounds; a cycle
is detected; an irreducible leaf is deferred to the subject; and the verified
SUBSTRATE acts as a cross-call cache (a shared sub-claim is REUSED, shortening the
bridge — the key multi-hop scaling win).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import capas_conjecture as C

SV = "capas-claim-payload-v3"
FIN = {"reported_value": 1.0, "reference_value": 1.0, "tolerance": 1.0, "metric_period_match": True}


def _ground(cid, ca, cl):
    return {"schema_version": SV, "claim": {"id": cid, "type": "financial_metric_claim", "text": cid},
            "evidence": {**FIN, "accounting": {"identity": "financial_ratio", "ratio": "current_ratio",
                                               "current_assets": ca, "current_liabilities": cl, "reported": ca / cl}}}


def _node(cid, deps):
    return {"schema_version": SV, "claim": {"id": cid, "type": "financial_metric_claim", "text": cid},
            "evidence": {**FIN, "accounting": {"identity": "balance_sheet", "assets": 1000, "liabilities": 600, "equity": 400},
                         "depends_on": deps}}


def run() -> int:
    checks = []

    top = _node("top", [_node("mid", [_ground("leaf", 200, 100)])])
    r = C.compile_bridge(top)
    checks.append(("3-hop chain compiles and grounds (leaf->mid->top, hops=2)",
                   r["status"].startswith("GROUNDED") and r["minimal_chain"] == ["leaf", "mid", "top"] and r["hops"] == 2))

    A = {"schema_version": SV, "claim": {"id": "A", "type": "financial_metric_claim", "text": "A"},
         "evidence": {**FIN, "accounting": {"identity": "balance_sheet", "assets": 1, "liabilities": 1, "equity": 0}}}
    A["evidence"]["depends_on"] = [{"schema_version": SV, "claim": {"id": "B", "type": "financial_metric_claim", "text": "B"},
                                    "evidence": {**FIN, "accounting": {"identity": "balance_sheet", "assets": 1, "liabilities": 1, "equity": 0},
                                                 "depends_on": [A]}}]
    checks.append(("circular dependency is detected", C.compile_bridge(A)["status"].startswith("CYCLE")))

    unb = {"schema_version": SV, "claim": {"id": "mech", "type": "causal_mechanism_claim", "text": "m"},
           "evidence": {"intervention_or_natural_experiment": True, "temporal_order_established": True,
                        "confounders_controlled": True, "mechanism_evidence_present": True}}
    rr = C.compile_bridge(_node("t", [unb]))
    checks.append(("irreducible leaf -> OPEN, residual deferred to the subject",
                   rr["status"].startswith("OPEN") and [x["claim"] for x in rr["irreducible_residual"]] == ["mech"]))

    sub = set()
    C.compile_bridge(_node("g1", [_ground("shared", 200, 100)]), sub)
    r2 = C.compile_bridge(_node("g2", [_ground("shared", 200, 100)]), sub)
    checks.append(("substrate cache: a shared sub-claim is REUSED, shortening the bridge",
                   r2["reused_from_substrate"] == ["shared"] and r2["minimal_chain"] == ["g2"]))

    ok = all(c for _, c in checks)
    for label, c in checks:
        print(f"{'✅' if c else '❌'} {label}")
    print("MULTI-HOP BRIDGE: all checks pass ✅" if ok else "MULTI-HOP: FAILURES ❌")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(run())
