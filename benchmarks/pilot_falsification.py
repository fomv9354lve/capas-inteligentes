# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""PILOT — capitalize on the lead: falsifiability beats plausibility (retrospective).

The genuine edge (per our SOTA sweeps): the field maximizes PLAUSIBILITY (LLM-judges,
co-scientists) and that gets gamed; CAPAS gates on STRUCTURE (is the claim licensed by
re-derivable / independent evidence?) and treats refutation as the strongest signal.

This pilot tests that edge against the WORLD'S OWN RESPONSE — famous RETRACTED/false
claims (ground truth known) vs matched valid claims. Every fraud here was MAXIMALLY
plausible (published in Nature/Lancet/Science -> plausibility passed) yet structurally
inadmissible at publication time (no independent reproduction, no controls, unauditable
data). The money shot: plausibility said YES, CAPAS gates, the world (retraction) proved
CAPAS right.

HONESTY (load-bearing, applies our own discipline to ourselves):
  - This is an ILLUSTRATIVE SEED with hand-coded payloads reflecting publication-time
    evidence — NOT the validated pilot. I coded the payloads, so I am not an independent
    oracle (the fail-open risk). A real pilot needs an INDEPENDENTLY-coded corpus
    (Retraction Watch / PubPeer) + the plausibility-LLM baseline arm run live.
  - `plausibility_passed` is a documented FACT (the venue accepted it), not my judgement.
  - ground_truth is documented (retracted / replicated). CAPAS's verdict is deterministic.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import capas

# Each case: publication-time evidence as a CAPAS payload + documented facts.
CORPUS = [
    # ---- FALSE (retracted), but maximally plausible at publication ----
    {"name": "Wakefield 1998 MMR->autism", "venue": "The Lancet", "ground_truth": "false",
     "plausibility_passed": True, "why_false": "retracted 2010; no controls, undisclosed conflicts, never reproduced",
     "payload": {"claim": {"id": "wakefield", "type": "causal_mechanism_claim", "text": "MMR vaccine causes autism"},
                 "evidence": {"intervention_or_natural_experiment": False, "temporal_order_established": False,
                              "confounders_controlled": False, "mechanism_evidence_present": False}}},
    {"name": "Schon 2001 molecular transistor", "venue": "Science/Nature", "ground_truth": "false",
     "plausibility_passed": True, "why_false": "retracted; data fabricated/duplicated, never independently reproduced",
     "payload": {"claim": {"id": "schon", "type": "reproducibility_check", "text": "single-molecule transistor demonstrated"},
                 "evidence": {"artifact_available": False, "independent_reproduction_pass": False}}},
    {"name": "Surgisphere 2020 HCQ mortality", "venue": "The Lancet", "ground_truth": "false",
     "plausibility_passed": True, "why_false": "retracted; database never auditable, no independent access",
     "payload": {"claim": {"id": "surgisphere", "type": "reproducibility_check", "text": "HCQ raises COVID mortality (observational)"},
                 "evidence": {"artifact_available": False, "independent_reproduction_pass": False}}},
    # ---- VALID (replicated / pre-registered) controls ----
    {"name": "Statins reduce CV events", "venue": "multiple RCTs + meta-analysis", "ground_truth": "valid",
     "plausibility_passed": True, "why_valid": "pre-registered RCTs, independently replicated, consistent effect",
     "payload": {"claim": {"id": "statins", "type": "systematic_review_claim", "text": "statins reduce cardiovascular events"},
                 "evidence": {"protocol_registered": True, "inclusion_criteria_declared": True,
                              "risk_of_bias_assessed": True, "effect_consistency": True}}},
    {"name": "LIGO gravitational waves", "venue": "PRL", "ground_truth": "valid",
     "plausibility_passed": True, "why_valid": "independently reproduced across detectors/events",
     "payload": {"claim": {"id": "ligo", "type": "reproducibility_check", "text": "direct detection of gravitational waves"},
                 "evidence": {"artifact_available": True, "independent_reproduction_pass": True}}},
    {"name": "Significant pre-registered effect", "venue": "registered report", "ground_truth": "valid",
     "plausibility_passed": True, "why_valid": "pre-registered, effect direction confirmed below alpha",
     "payload": {"claim": {"id": "prereg", "type": "statistical_confidence", "text": "effect significant as pre-registered"},
                 "evidence": {"p_value": 0.001, "alpha": 0.05, "effect_direction_confirmed": True}}},
]


def run() -> int:
    rows, money = [], []
    false_gated = valid_accepted = n_false = n_valid = 0
    for c in CORPUS:
        payload = {"schema_version": "capas-claim-payload-v3", **c["payload"]}
        verdict = capas.decide_external_claim(payload).get("verdict")
        gated = verdict != "ACCEPT"
        if c["ground_truth"] == "false":
            n_false += 1
            false_gated += int(gated)
            if c["plausibility_passed"] and gated:
                money.append(c["name"])
        else:
            n_valid += 1
            valid_accepted += int(verdict == "ACCEPT")
        rows.append((c["name"], c["ground_truth"], "plaus✓" if c["plausibility_passed"] else "plaus✗", verdict,
                     "GATED" if gated else "passed"))

    print("PILOT (illustrative seed) — falsifiability vs plausibility on retracted-vs-valid claims\n")
    print(f"{'case':34s} {'truth':6s} {'plaus':6s} {'CAPAS':8s} {'gate'}")
    for name, gt, pl, v, g in rows:
        print(f"{name:34s} {gt:6s} {pl:6s} {str(v):8s} {g}")
    print()
    print(f"FALSE claims gated by CAPAS:   {false_gated}/{n_false}")
    print(f"VALID claims accepted by CAPAS: {valid_accepted}/{n_valid}")
    print(f"MONEY SHOT (plausible + CAPAS-gated + world-confirmed-false): {money}")

    # success of the SEED: every retracted-but-plausible claim is gated, no valid one is rejected outright
    ok = (false_gated == n_false and valid_accepted == n_valid)
    print("\nSEED RESULT:", "✅ separation holds — CAPAS gates the plausible-but-false, passes the replicated"
          if ok else "⚠️ separation imperfect — inspect rows (honest, not forced)")
    print("NOTE: illustrative seed, hand-coded payloads. Validated pilot needs an INDEPENDENTLY-coded "
          "corpus (Retraction Watch/PubPeer) + the live plausibility-LLM baseline arm.")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(run())
