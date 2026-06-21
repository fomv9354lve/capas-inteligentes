"""Proof-carrying verification layer — stress battery.

Proves that capas_verify.verify() raises the bar above the base gate:
  • catches anchor-violating claims by re-derivation (T1),
  • does NOT accept a declared-only statistic (standard above requirement),
  • ACCEPTs only when the statistic re-derives from supplied raw data,
  • REJECTs a declared statistic that contradicts its own raw data (lie caught),
  • partitions unbacked study-design booleans to HOLD/ATTEST (T4),
  • ATTESTs (does not auto-reject) the same booleans when provenance is supplied.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import capas_verify
from scipy import stats as _stats

SV = "capas-claim-payload-v3"


def _payload(cid, text, ctype, evidence):
    return {"claim": {"id": cid, "text": text, "type": ctype}, "evidence": evidence, "schema_version": SV}


def run():
    # raw data with a real, large separation -> tiny p
    a = [10.1, 10.3, 9.9, 10.2, 10.0, 10.4, 9.8, 10.1]
    b = [12.0, 12.3, 11.8, 12.1, 12.2, 11.9, 12.4, 12.0]
    true_p = float(_stats.ttest_ind(a, b, equal_var=False)[1])

    cases = [
        # (label, payload, expected_verdict, expected_scope)
        ("T1 anchor lie (water 500C, valid stats)",
         _payload("t1", "Water boils at 500C", "statistical_confidence",
                  {"p_value": 0.01, "alpha": 0.05, "effect_direction_confirmed": True}),
         "REJECT", "GATE"),
        ("T2 fails own rule (p=0.12>alpha)",
         _payload("t2", "Drug reduces tumors", "statistical_confidence",
                  {"p_value": 0.12, "alpha": 0.05, "effect_direction_confirmed": True}),
         "REJECT", "GATE"),
        ("T3 causal missing intervention",
         _payload("t3", "ice cream causes shark attacks", "causal_mechanism_claim",
                  {"intervention_or_natural_experiment": False, "temporal_order_established": True,
                   "confounders_controlled": False, "mechanism_evidence_present": True}),
         "REJECT", "GATE"),
        ("T4 causal all-true but UNBACKED",
         _payload("t4", "ice cream causes shark attacks - proven by RCT", "causal_mechanism_claim",
                  {"intervention_or_natural_experiment": True, "temporal_order_established": True,
                   "confounders_controlled": True, "mechanism_evidence_present": True}),
         "HOLD", "ATTEST"),
        ("STD-ABOVE: stats declared-only (no raw data)",
         _payload("s1", "Treatment works", "statistical_confidence",
                  {"p_value": 0.01, "alpha": 0.05, "effect_direction_confirmed": True}),
         "HOLD", "ATTEST"),
        ("RE-DERIVED: stats with raw data that matches declared p",
         _payload("s2", "Treatment works", "statistical_confidence",
                  {"p_value": round(true_p, 5), "alpha": 0.05, "effect_direction_confirmed": True,
                   "raw_data": {"group_a": a, "group_b": b}}),
         "ACCEPT", "GATE"),
        ("LIE CAUGHT: declared p=0.0001 but raw data gives ~no effect",
         _payload("s3", "Treatment works", "statistical_confidence",
                  {"p_value": 0.0001, "alpha": 0.05, "effect_direction_confirmed": True,
                   "raw_data": {"group_a": a, "group_b": [10.0, 10.1, 9.9, 10.2, 10.0, 10.1, 9.95, 10.05]}}),
         "REJECT", "GATE"),
        ("PASSAGE A: CDS calibration result RE-DERIVES from raw signal",
         _payload("a1", "Sample concentration is 50.0 units", "financial_metric_claim",
                  {"reported_value": 50.0, "reference_value": 50.0, "tolerance": 1.0, "metric_period_match": True,
                   "computation": {"operation": "linear_calibration",
                                   "inputs": {"signal": 105.0, "intercept": 5.0, "slope": 2.0},
                                   "reported_value": 50.0, "tolerance": 0.01}}),
         "ACCEPT", "GATE"),
        ("PASSAGE A FRAUD: reported value does NOT re-derive from raw signal",
         _payload("a2", "Sample concentration is 50.0 units", "financial_metric_claim",
                  {"reported_value": 50.0, "reference_value": 50.0, "tolerance": 1.0, "metric_period_match": True,
                   "computation": {"operation": "linear_calibration",
                                   "inputs": {"signal": 200.0, "intercept": 5.0, "slope": 2.0},
                                   "reported_value": 50.0, "tolerance": 0.01}}),
         "REJECT", "GATE"),
        ("ATTESTED: causal all-true WITH signed provenance",
         _payload("s4", "intervention X causes outcome Y", "causal_mechanism_claim",
                  {"intervention_or_natural_experiment": True, "temporal_order_established": True,
                   "confounders_controlled": True, "mechanism_evidence_present": True,
                   "registry_id": "NCT01234567", "signed_attestation": "sha256:deadbeef"}),
         "ATTEST", "ATTEST"),
    ]

    print(f"(re-derivation engine: {'scipy' if capas_verify._HAS_SCIPY else 'fallback'}; true_p of fixture = {true_p:.2e})\n")
    rows = []
    all_ok = True
    for label, payload, exp_verdict, exp_scope in cases:
        r = capas_verify.verify(payload)
        v, sc, tier = r["verified_verdict"], r["scope"], r["verification_tier"]
        # "ATTEST" expected verdict means: verdict stands (not rejected) AND scope==ATTEST
        verdict_ok = (sc == "ATTEST" and v not in ("REJECT",)) if exp_verdict == "ATTEST" else (v == exp_verdict)
        scope_ok = sc == exp_scope
        ok = verdict_ok and scope_ok
        all_ok &= ok
        rows.append((label, r["base_gate_verdict"], v, sc, tier, "✅" if ok else "❌"))

    w = max(len(r[0]) for r in rows)
    print(f"{'case'.ljust(w)} | base   | verified| scope  | tier")
    print("-" * (w + 40))
    for label, base, v, sc, tier, mark in rows:
        print(f"{label.ljust(w)} | {base:<6} | {v:<7} | {sc:<6} | {tier:<10} {mark}")
    print()
    if all_ok:
        print("PROOF-CARRYING VERIFICATION: all cases pass ✅")
        return 0
    print("PROOF-CARRYING VERIFICATION: FAILURES ❌")
    return 1


if __name__ == "__main__":
    raise SystemExit(run())
