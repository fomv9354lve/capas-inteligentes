"""Demo + check: the verified knowledge braid (grounding by position, not node).

Deterministic; no network/key. Asserts:
  - two grounded claims that re-derive the SAME target by different methods
    CORRESPOND (reciprocal support / ayni);
  - a claim that is LOCALLY GROUNDED yet disagrees on the same target is a braid
    FAULT — caught by the whole, not by its own receipt (grounding by position);
  - tampering one node changes the non-local braid root (topological robustness).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import capas_braid as B

SV = "capas-claim-payload-v3"
FIN = {"reported_value": 1.0, "reference_value": 1.0, "tolerance": 1.0, "metric_period_match": True}


def _p(cid, text, ev):
    return {"schema_version": SV, "claim": {"id": cid, "type": "financial_metric_claim", "text": text},
            "evidence": {**FIN, **ev}}


def _ratio(cid, text, ca, cl, reported):
    return _p(cid, text, {"accounting": {"identity": "financial_ratio", "ratio": "current_ratio",
                                         "current_assets": ca, "current_liabilities": cl, "reported": reported}})


def run() -> int:
    br = B.Braid()
    T = "current_ratio:helios"
    a = br.add(_ratio("A", "current ratio 2.0", 200, 100, 2.0), target=T, value=2.0, method="m1")
    b = br.add(_ratio("B", "current ratio 2.0 (other components)", 400, 200, 2.0), target=T, value=2.0, method="m2")
    c = br.add(_ratio("C", "current ratio 3.0", 300, 100, 3.0), target=T, value=3.0, method="m3")

    checks = [
        ("A,B added (locally grounded)", a["added"] and b["added"]),
        ("B CORRESPONDS with A (same target, two methods -> reciprocity)", b["corresponds"] == ["A"]),
        ("C is added (locally grounded) BUT is a braid FAULT (disagrees on same target)",
         c["added"] and c["braid_fault"] and set(c["contradicts"]) == {"A", "B"}),
        ("A's position certificate: reciprocal support from B, incoherent due to C",
         br.position_certificate("A")["reciprocal_support"] == 1
         and br.position_certificate("A")["braid_coherent"] is False),
        ("C: locally grounded yet braid-INCOHERENT (caught by the whole, not the node)",
         br.position_certificate("C")["braid_coherent"] is False),
        ("braid surfaces the fault between C and {A,B}", len(br.faults()) == 2),
    ]
    root_before = br.root()
    t = br.tamper("A", 9.9)
    checks.append(("tamper A -> non-local braid root changes (topological robustness)",
                   t["root_changed"] and br.root() != root_before))

    ok = True
    for label, good in checks:
        ok = ok and good
        print(f"{'✅' if good else '❌'} {label}")
    print("KNOWLEDGE BRAID: all checks pass ✅" if ok else "BRAID: FAILURES ❌")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(run())
