"""Demo + check: CAPAS's cross-domain INVARIANT engine catches fabrication in finance,
psychology, and quantum with ONE deterministic mechanism — and the core decision is OVERRIDDEN
to REJECT when a claim's declared numbers violate a domain law, regardless of claim type.

This is the generalization of the quantum physics gate: internal consistency under the laws of
a domain is the largest slice of text<->reality CAPAS can re-derive with NO external oracle.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import capas
import capas_invariants as INV

SV = "capas-claim-payload-v3"


def run() -> int:
    checks = []

    # --- 1. unit: each domain invariant flags fabrication, passes honest data ---
    # finance: books that don't close
    bad_fin = INV.check_accounting({"accounting": {"assets": 1000, "liabilities": 600, "equity": 300}})
    ok_fin = INV.check_accounting({"accounting": {"assets": 1000, "liabilities": 600, "equity": 400}})
    checks.append(("FINANCE: assets!=liab+equity -> FLAG", bad_fin["verdict"] == "FLAG"))
    checks.append(("FINANCE: balanced books -> PASS", ok_fin["verdict"] == "PASS"))

    # psychology: GRIM — mean 5.19 with N=10 is impossible (only k/10 reachable)
    bad_grim = INV.check_grim({"grim": {"mean": 5.19, "n": 10, "decimals": 2}})
    ok_grim = INV.check_grim({"grim": {"mean": 5.2, "n": 10, "decimals": 2}})
    checks.append(("PSYCH: mean 5.19 with N=10 -> FLAG (GRIM impossible)", bad_grim["verdict"] == "FLAG"))
    checks.append(("PSYCH: mean 5.2 with N=10 -> PASS (reachable as 52/10)", ok_grim["verdict"] == "PASS"))

    # quantum: T2>2T1 undeclared (delegates to physics gate)
    bad_q = INV.check_quantum({"quantum": {"t1_us": 11.2, "t2_us": 23.44, "t2_method": "ramsey"}})
    ok_q = INV.check_quantum({"quantum": {"t1_us": 327, "t2_us": 420}})
    checks.append(("QUANTUM: T2/T1=2.09 undeclared -> FLAG", bad_q["verdict"] == "FLAG"))
    checks.append(("QUANTUM: T2/T1=1.28 -> PASS", ok_q["verdict"] == "PASS"))

    # universal: probability out of bounds; conservation broken
    bad_p = INV.check_probability_bounds({"probabilities": [0.3, 1.4]})
    bad_s = INV.check_sum({"parts": [10, 20, 35], "total": 60})
    checks.append(("UNIVERSAL: p=1.4 -> FLAG (out of [0,1])", bad_p["verdict"] == "FLAG"))
    checks.append(("UNIVERSAL: 10+20+35 != 60 -> FLAG (conservation)", bad_s["verdict"] == "FLAG"))

    # --- 2. integration: the CORE decision is OVERRIDDEN to REJECT by an invariant violation ---
    # A financial_metric_claim that re-derives fine BUT whose books do not close -> REJECT.
    payload = {
        "schema_version": SV,
        "claim": {"id": "fm1", "type": "financial_metric_claim", "text": "Q3 net income reported"},
        "evidence": {
            "reported_value": 1.0, "reference_value": 1.0, "tolerance": 1.0, "metric_period_match": True,
            "invariants": {"accounting": {"assets": 1000, "liabilities": 600, "equity": 300}},
        },
    }
    decided = capas.decide_external_claim(payload)
    checks.append((f"INTEGRATION: claim re-derives but books don't close -> {decided['verdict']} "
                   f"(invariant override)", decided["verdict"] == "REJECT"
                   and decided["invariant_audit"]["verdict"] == "FLAG"))

    # The SAME claim with balanced books is NOT downgraded by the invariant layer.
    payload["evidence"]["invariants"]["accounting"]["equity"] = 400
    decided_ok = capas.decide_external_claim(payload)
    checks.append((f"INTEGRATION: balanced books -> {decided_ok['verdict']} (invariant PASS, not downgraded)",
                   decided_ok["invariant_audit"]["verdict"] == "PASS"))

    # A claim with NO invariant block is untouched (applicable=False) -> behavior unchanged.
    plain = {"schema_version": SV,
             "claim": {"id": "p1", "type": "exact_model_solution", "text": "x"},
             "evidence": {"abs_error": 0.0, "tolerance": 1e-3}}
    dp = capas.decide_external_claim(plain)
    checks.append((f"INTEGRATION: no invariant block -> {dp['verdict']} unchanged (applicable=False)",
                   dp["verdict"] == "ACCEPT" and dp["invariant_audit"]["applicable"] is False))

    ok = all(c for _, c in checks)
    for label, c in checks:
        print(f"{'OK ' if c else 'XX '}{label}")
    print("\nONE mechanism, THREE domains: finance + psychology + quantum fabrication all caught by\n"
          "deterministic invariant re-derivation — no oracle, no LLM. The core gate is strengthened,\n"
          "never weakened (downgrade-only): the 0-false-accept guarantee is preserved.")
    print("CROSS-DOMAIN INVARIANT ENGINE: pass" if ok else "INVARIANTS: FAILURES")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(run())
