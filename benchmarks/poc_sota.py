"""CAPAS vs SOTA — a REPRODUCIBLE proof of concept (numbers emitted by the real engine).

Run:  python3 benchmarks/poc_sota.py
The split, the per-type breakdown and the engine latency are MEASURED here, not asserted in
prose — so the PoC verifies itself. HONEST SCOPE (read it): the verdicts are deterministic
GIVEN the declared-evidence payloads below, which are hand-coded to match the claim
descriptions. This validates the GATE LOGIC, not a measured property of real frontier-model
papers (that needs an independently-coded corpus; cf. the n=28 retraction pilot). And the
gate rules on what the payload DECLARES, never on whether the declaration matches reality
(the GIGO ceiling) — which is exactly why the declared slice is made accountable, not trusted.
"""
from __future__ import annotations

import sys
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import capas

SV = "capas-claim-payload-v3"


def _p(cid, ctype, evidence):
    return {"schema_version": SV, "claim": {"id": cid, "type": ctype, "text": cid}, "evidence": evidence}


# Scenario 1 (A1-A5) + Scenario 2 (B1-B5), coded to the PoC's descriptions, + fillers to 20.
CLAIMS = [
    # A — frontier-model claims with incomplete/mis-declared evidence
    _p("A1 GPT-4 SOTA MMLU", "statistical_confidence", {"p_value": 0.03, "alpha": 0.05, "effect_direction_confirmed": False}),
    _p("A2 Gemini beats experts", "statistical_confidence", {"p_value": 0.06, "alpha": 0.05, "effect_direction_confirmed": True}),
    _p("A3 LLaMA-3 == GPT-4 HumanEval", "statistical_confidence", {"p_value": 0.03, "alpha": 0.05, "effect_direction_confirmed": True}),
    _p("A4 Claude causal via Constitutional AI", "causal_mechanism_claim",
       {"intervention_or_natural_experiment": True, "temporal_order_established": True, "confounders_controlled": False, "mechanism_evidence_present": True}),
    _p("A5 GPT-4V expert diagnosis", "exact_model_solution", {"abs_error": 0.12, "tolerance": 0.05}),
    # B — semantic inflation (observational->causal, benchmark->universal)
    _p("B1 compute causally improves all tasks", "causal_mechanism_claim",
       {"intervention_or_natural_experiment": False, "temporal_order_established": False, "confounders_controlled": False, "mechanism_evidence_present": False}),
    _p("B2 RLHF causes safety everywhere", "causal_mechanism_claim",
       {"intervention_or_natural_experiment": True, "temporal_order_established": True, "confounders_controlled": False, "mechanism_evidence_present": False}),
    _p("B3 emergence caused by scale thresholds", "causal_mechanism_claim",
       {"intervention_or_natural_experiment": False, "temporal_order_established": False, "confounders_controlled": False, "mechanism_evidence_present": False}),
    _p("B4 instruction tuning universally improves zero-shot", "universal_anchor_claim",
       {"anchor_mode": "scaling", "local_property_tests_pass": True, "universal_anchor_pass": False}),
    _p("B5 CoT physically consistent with human reasoning", "universal_anchor_claim",
       {"anchor_mode": "scaling", "local_property_tests_pass": False, "universal_anchor_pass": False}),
    # fillers to reach the PoC's type mix (8 statistical, 5 causal, 3 universal, 2 repro, 1 physical, 1 exact)
    _p("S6", "statistical_confidence", {"p_value": 0.01, "alpha": 0.05, "effect_direction_confirmed": True}),
    _p("S7", "statistical_confidence", {"p_value": 0.2, "alpha": 0.05, "effect_direction_confirmed": True}),
    _p("S8", "statistical_confidence", {"p_value": 0.04, "alpha": 0.05, "effect_direction_confirmed": True}),
    _p("S9", "statistical_confidence", {"p_value": 0.049, "alpha": 0.05, "effect_direction_confirmed": False}),
    _p("C6", "causal_mechanism_claim",
       {"intervention_or_natural_experiment": True, "temporal_order_established": True, "confounders_controlled": True, "mechanism_evidence_present": True}),
    _p("U6", "universal_anchor_claim", {"anchor_mode": "scaling", "local_property_tests_pass": True, "universal_anchor_pass": True}),
    _p("R1 reproduced", "reproducibility_check", {"artifact_available": True, "independent_reproduction_pass": True}),
    _p("R2 not reproduced", "reproducibility_check", {"artifact_available": True, "independent_reproduction_pass": False}),
    _p("P1 physical", "physical_accuracy", {"within_chemical_accuracy": False}),
    _p("E1 exact", "exact_model_solution", {"abs_error": 0.001, "tolerance": 0.0015}),
]


def run() -> int:
    t0 = time.perf_counter()
    results = [(c["claim"]["id"], c["claim"]["type"], capas.decide_external_claim(c).get("verdict")) for c in CLAIMS]
    dt = time.perf_counter() - t0

    split = Counter(v for _, _, v in results)
    print("CAPAS vs SOTA — reproducible PoC (numbers emitted by the engine)\n")
    print(f"{'claim':42s} {'type':26s} {'verdict'}")
    for cid, ct, v in results:
        print(f"{cid:42s} {ct:26s} {v}")
    n = len(results)
    print(f"\nReal split: " + " · ".join(f"{k} {v} ({v/n:.0%})" for k, v in split.most_common()))
    print(f"Real ENGINE latency: {dt*1000:.2f} ms for {n} claims = {dt/n*1e6:.0f} µs/claim (pure engine, no network)")

    # per-type accept rate
    by_type = {}
    for _, ct, v in results:
        by_type.setdefault(ct, []).append(v)
    print("\nPer claim-type:")
    for ct, vs in sorted(by_type.items()):
        acc = sum(1 for v in vs if v == "ACCEPT")
        print(f"  {ct:26s} n={len(vs)}  accept {acc}/{len(vs)} ({acc/len(vs):.0%})  {dict(Counter(vs))}")

    print("\nHONEST: these verdicts are deterministic GIVEN the declared-evidence payloads above "
          "(hand-coded to the claim descriptions). They validate the gate LOGIC, not a measured "
          "property of real SOTA papers, and never that a declared field matches reality (GIGO).")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
