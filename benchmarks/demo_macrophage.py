"""Demo + check: constructive integration of the SOTA-ahead areas (the macrophage).

Each absorbed in service of the deterministic core, never as the verdict:
  #A learned value function — predicts admissibility cheaply to GUIDE search; the
     deterministic grader still re-grades before grounding.
  #B SQL aggregate rung (small data CAPAS owns) + Proof-of-SQL backend on the ZK
     rung (large data CAPAS verifies succinctly).
  #C self-consistency / semantic-entropy as an ATTEST-class calibration flag —
     the proposer's own uncertainty surfaced to the subject, never the verdict.
Deterministic; no network/key.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import capas_verify as V
import capas_sql
import capas_value as VAL
import capas_extract as EX
from scipy import stats as _stats

SV = "capas-claim-payload-v3"
FIN = {"reported_value": 1.0, "reference_value": 1.0, "tolerance": 1.0, "metric_period_match": True}


def _p(text, ev, ct="financial_metric_claim"):
    return {"schema_version": SV, "claim": {"id": "c", "type": ct, "text": text},
            "evidence": ev if ct == "statistical_confidence" else {**FIN, **ev}}


def run() -> int:
    rows = [{"region": "US", "rev": 100}, {"region": "US", "rev": 150}, {"region": "EU", "rev": 200}]
    checks = []

    # #B SQL aggregate rung
    def vd(ev):
        return V.verify(_p("x", ev))["verified_verdict"]
    checks.append(("#B SQL SUM re-derives (honest ACCEPT / lie REJECT)",
                   vd({"sql": {"rows": rows, "query": {"op": "sum", "column": "rev"}, "reported": 450}}) == "ACCEPT"
                   and vd({"sql": {"rows": rows, "query": {"op": "sum", "column": "rev"}, "reported": 999}}) == "REJECT"))
    checks.append(("#B SQL GROUP BY + COUNT/WHERE re-derive",
                   vd({"sql": {"rows": rows, "query": {"op": "sum", "column": "rev", "group_by": "region"}, "reported": {"US": 250, "EU": 200}}}) == "ACCEPT"
                   and vd({"sql": {"rows": rows, "query": {"op": "count", "where": {"column": "rev", "op": ">", "value": 120}}, "reported": 2}}) == "ACCEPT"))

    # #B Proof-of-SQL backend (scale path) on the ZK rung
    capas_sql.register()
    op = "sha256:" + hashlib.sha256("tblC|SELECT SUM(rev)|450|n1".encode()).hexdigest()
    zk = {"zk_proof": {"verifying_key_id": "proof-of-sql", "public_inputs": {"reported": 450},
                       "statement": "SUM(rev)",
                       "proof": {"table_commitment": "tblC", "query": "SELECT SUM(rev)", "result": 450,
                                 "nonce": "n1", "opening": op}}}
    checks.append(("#B Proof-of-SQL proof grounds a large aggregate succinctly (ZK rung)",
                   V.verify(_p("big", zk))["verified_verdict"] == "ACCEPT"))

    # #A learned value function guides search (never decides)
    a = [10.1, 10.3, 9.9, 10.2, 10.0, 10.4, 9.8, 10.1]
    b = [12.0, 12.3, 11.8, 12.1, 12.2, 11.9, 12.4, 12.0]
    p = round(float(_stats.ttest_ind(a, b, equal_var=False)[1]), 5)
    train = [_p("x", {"accounting": {"identity": "balance_sheet", "assets": 1000, "liabilities": 600, "equity": 400}}),
             _p("t", {"p_value": p, "alpha": 0.05, "effect_direction_confirmed": True, "raw_data": {"group_a": a, "group_b": b}}, "statistical_confidence"),
             _p("t", {"p_value": 0.01, "alpha": 0.05, "effect_direction_confirmed": True}, "statistical_confidence"),
             _p("x", {"sql": {"rows": rows, "query": {"op": "sum", "column": "rev"}, "reported": 450}})]
    m = VAL.ValueModel().fit(train)
    strong = _p("t", {"p_value": p, "alpha": 0.05, "effect_direction_confirmed": True, "raw_data": {"group_a": a, "group_b": b}}, "statistical_confidence")
    weak = _p("t", {"p_value": 0.01, "alpha": 0.05, "effect_direction_confirmed": True}, "statistical_confidence")
    checks.append(("#A value function ranks the groundable conjecture above the declared-only one",
                   m.predict(strong) > m.predict(weak)))

    # #C self-consistency calibration flag
    agree = EX.semantic_agreement([{"citations": [{"value": 200000}, {"value": 100000}]}] * 3)
    disagree = EX.semantic_agreement([{"citations": [{"value": 200000}]}, {"citations": [{"value": 500000}]}, {"citations": [{"value": 300000}]}])
    checks.append(("#C agreement: consistent proposals -> high_confidence; inconsistent -> ATTEST flag",
                   agree["flag"] == "high_confidence" and disagree["flag"].startswith("ATTEST")))

    ok = True
    for label, good in checks:
        ok = ok and good
        print(f"{'✅' if good else '❌'} {label}")
    print("MACROPHAGE (value + Proof-of-SQL + calibration): all checks pass ✅" if ok else "MACROPHAGE: FAILURES ❌")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(run())
