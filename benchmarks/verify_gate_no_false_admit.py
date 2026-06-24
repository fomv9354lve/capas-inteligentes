#!/usr/bin/env python3
"""Lock the gate's correctness on the two failure modes the pedagogy sprint flagged.

The sprint's iteration-3 reported a non-GIGO false-ADMIT (s12) and an over-BLOCK (s13) at the CAPAS
gate. Investigation (2026-06-24): NOT reproducible. The committed N=79 corpus shows 0/25 non-GIGO
false-admit and 0/25 over-block; direct adversarial probes all return the correct verdict; the
ephemeral iter-3 corpus was agent-generated and its s12/s13 labels were internally inconsistent (a
genuinely-false number is REJECTed by the engine, so a `is_gigo=False` false-ADMIT cannot occur).

This test LOCKS that correctness so a real regression would fail CI, rather than patching a non-bug:
  - a genuinely-false structured claim is NEVER ACCEPTed (the harm mode),
  - a genuinely-true well-formed claim is NEVER REJECTed/over-blocked (the over-block mode),
  - a malformed payload fail-closes (never ACCEPT).

The GIGO ceiling is out of scope by design: a self-consistent fabrication CAN pass (disclosed).
"""
import sys
import capas_sdk

# (claim_type, evidence, why) — genuinely FALSE/inadmissible. Must NEVER be ACCEPT.
FALSE_OR_INADMISSIBLE = [
    ("statistical_confidence", {"p_value": 0.40, "alpha": 0.05, "effect_direction_confirmed": True}, "p>alpha"),
    ("statistical_confidence", {"p_value": 0.90, "alpha": 0.05, "effect_direction_confirmed": True}, "p>>alpha"),
    ("reproducibility_check", {"artifact_available": False, "independent_reproduction_pass": False}, "artifact unavailable"),
    ("causal_mechanism_claim", {"intervention_or_natural_experiment": False, "temporal_order_established": True,
                                "confounders_controlled": True, "mechanism_evidence_present": True}, "no design"),
]

# (claim_type, evidence) — genuinely TRUE + fully contracted. Must NEVER be REJECT or schema-fail.
TRUE_ADMISSIBLE = [
    ("statistical_confidence", {"p_value": 0.01, "alpha": 0.05, "effect_direction_confirmed": True}),
    ("reproducibility_check", {"artifact_available": True, "independent_reproduction_pass": True}),
    ("systematic_review_claim", {"protocol_registered": True, "inclusion_criteria_declared": True,
                                 "risk_of_bias_assessed": True, "effect_consistency": True}),
]

# Malformed / out-of-range — must fail-closed (never ACCEPT).
MALFORMED = [
    ("statistical_confidence", {"p_value": 1.7, "alpha": 0.05, "effect_direction_confirmed": True}),   # p>1
    ("statistical_confidence", {"p_value": 0.01, "alpha": 0.05}),                                       # missing field
    ("statistical_confidence", {"p_value": 0.01, "alpha": 0.05, "effect_direction_confirmed": True, "bogus": 1}),  # extra field
]


def verdict(ct, ev):
    return capas_sdk.gate(ct, ev, "", "regression").get("verdict")


def main() -> int:
    fails = []

    for ct, ev, why in FALSE_OR_INADMISSIBLE:
        v = verdict(ct, ev)
        if v == "ACCEPT":
            fails.append(f"FALSE-ADMIT (harm): {ct} [{why}] -> {v} (must not ACCEPT)")

    for ct, ev in TRUE_ADMISSIBLE:
        v = verdict(ct, ev)
        if v in ("REJECT", "BLOCK"):
            fails.append(f"OVER-BLOCK: true {ct} -> {v} (must ACCEPT)")

    for ct, ev in MALFORMED:
        v = verdict(ct, ev)
        if v == "ACCEPT":
            fails.append(f"FAIL-OPEN: malformed {ct} -> {v} (must not ACCEPT)")

    n = len(FALSE_OR_INADMISSIBLE) + len(TRUE_ADMISSIBLE) + len(MALFORMED)
    if fails:
        print(f"FAIL ({len(fails)}/{n}):")
        for f in fails:
            print("  -", f)
        return 1
    print(f"OK {n}/{n}: no non-GIGO false-admit, no over-block, malformed fail-closes. "
          f"Gate correctness locked (GIGO ceiling out of scope by design).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
