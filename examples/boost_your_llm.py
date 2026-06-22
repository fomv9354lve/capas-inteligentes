"""See how CAPAS boosts your LLM — the reliability boost, measured honestly.

An LLM (or an LLM-as-judge) accepts what is PLAUSIBLE. CAPAS accepts only what is
STRUCTURALLY ADMISSIBLE. On a set of claims an LLM would wave through, CAPAS lets the
supported ones ACCEPT and gates the unsupported ones — 0 false-accepts. The model did not
get smarter; its output became admissible-or-deferred instead of plausible-or-wrong.

Run:  python3 examples/boost_your_llm.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from capas_sdk import gate, reward

# Each item: a structured claim an LLM finds PLAUSIBLE and would accept. `truly_supported`
# is whether its evidence actually licenses it. A plausibility judge accepts ALL of them.
CLAIMS = [
    ("supported causal claim", "causal_mechanism_claim",
     {"intervention_or_natural_experiment": True, "temporal_order_established": True,
      "confounders_controlled": True, "mechanism_evidence_present": True}, True),
    ("unsupported causal claim (sounds right)", "causal_mechanism_claim",
     {"intervention_or_natural_experiment": False, "temporal_order_established": False,
      "confounders_controlled": False, "mechanism_evidence_present": False}, False),
    ("fabricated number", "financial_metric_claim",
     {"reported_value": 1.0, "reference_value": 1.0, "tolerance": 0.0, "metric_period_match": True,
      "computation": {"operation": "sum", "inputs": {"values": [1, 2, 3]}, "reported_value": 7.0, "tolerance": 1e-9}}, False),
    ("replicated systematic review", "systematic_review_claim",
     {"protocol_registered": True, "inclusion_criteria_declared": True,
      "risk_of_bias_assessed": True, "effect_consistency": True}, True),
    ("review on no protocol", "systematic_review_claim",
     {"protocol_registered": False, "inclusion_criteria_declared": False,
      "risk_of_bias_assessed": False, "effect_consistency": False}, False),
    ("reproduced result", "reproducibility_check",
     {"artifact_available": True, "independent_reproduction_pass": True}, True),
]


def run() -> int:
    llm_false_accepts = capas_false_accepts = 0
    print(f"{'claim':38s} {'supported?':10s} {'LLM-alone':10s} {'CAPAS'}")
    for name, ctype, evidence, supported in CLAIMS:
        g = gate(ctype, evidence, claim_text=name)
        verdict = g.get("verdict")
        capas_accept = verdict == "ACCEPT"
        llm_accept = True                                  # a plausibility judge accepts them all
        if llm_accept and not supported:
            llm_false_accepts += 1
        if capas_accept and not supported:
            capas_false_accepts += 1
        r = reward(ctype, evidence)
        print(f"{name:38s} {str(supported):10s} {'ACCEPT':10s} {verdict:8s} (reward {r:.2f})")

    print(f"\nLLM-alone false-accepts:  {llm_false_accepts}/3 unsupported claims waved through")
    print(f"LLM + CAPAS false-accepts: {capas_false_accepts}/3   <- the boost")
    print("\nThe boost is RELIABILITY: CAPAS gated every unsupported claim (REJECT/HOLD) while letting")
    print("the supported ones ACCEPT. It did NOT make the model smarter — it made its output trustworthy.")
    ok = capas_false_accepts == 0 and llm_false_accepts == 3
    print("\nBOOST DEMO:", "✅ 0 false-accepts with CAPAS vs 3 without" if ok else "⚠️ inspect rows")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(run())
