# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""PILOT (real corpus) — falsifiability vs plausibility on 28 AGENT-CODED cases.

The seed was hand-coded by me (not an independent oracle). This corpus was coded by two
research subagents from public sources (Retraction Watch / journal notices for the 14
RETRACTED cases; replication/meta-analysis records for the 14 VALID cases) — a real step
toward independence (still agent-coded, not human-adjudicated; that is the next step).

Every case is a famous claim that PASSED plausibility (published in a top venue). The test:
does CAPAS separate the retracted from the replicated BY STRUCTURE, and what does it get
wrong? We report the full confusion matrix, including the two failure modes that matter:
  - FALSE-ACCEPT (a fraud accepted) — the dangerous one;
  - FALSE-REJECT (a valid claim rejected) — the 'good idea wrongly rejected' one.

Evidence coercion (transparent, uniform): booleans pass through; a reported significance
string on p_value counts as significant (p=0.001, alpha=0.05); a False/absent significance
counts as not significant (p=1.0). No per-case tuning.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import capas

CF = {"intervention_or_natural_experiment": False, "temporal_order_established": False,
      "confounders_controlled": False, "mechanism_evidence_present": False}
CT = {k: True for k in CF}
RF = {"artifact_available": False, "independent_reproduction_pass": False}
RT = {"artifact_available": True, "independent_reproduction_pass": True}
SF = {"protocol_registered": False, "inclusion_criteria_declared": False,
      "risk_of_bias_assessed": False, "effect_consistency": False}
ST = {k: True for k in SF}
STAT_SIG = {"p_value": "significant", "alpha": "0.05", "effect_direction_confirmed": True}
STAT_NO = {"p_value": False, "alpha": False, "effect_direction_confirmed": False}

CORPUS = [
    # ---- 14 RETRACTED / false ----
    ("Wakefield MMR-autism", "false", "causal_mechanism_claim", CF),
    ("Schon transistors", "false", "reproducibility_check", RF),
    ("Hwang SCNT cloning", "false", "reproducibility_check", RF),
    ("Stapel social priming", "false", "causal_mechanism_claim", CF),
    ("Obokata STAP", "false", "reproducibility_check", RF),
    ("Voinnet RNA silencing", "false", "reproducibility_check", RF),
    ("Macchiarini trachea", "false", "causal_mechanism_claim",
     {**CF, "intervention_or_natural_experiment": True, "temporal_order_established": True}),
    ("Reuben analgesia", "false", "causal_mechanism_claim", CF),
    ("Boldt HES colloid", "false", "causal_mechanism_claim", CF),
    ("Wolfe-Simon arsenic life", "false", "reproducibility_check",
     {"artifact_available": True, "independent_reproduction_pass": False}),
    ("LaCour canvassing", "false", "causal_mechanism_claim", CF),
    ("Fujii antiemetic", "false", "statistical_confidence", STAT_NO),
    ("Surgisphere HCQ", "false", "reproducibility_check", RF),
    ("Vitamin K2 review", "false", "systematic_review_claim", SF),
    # ---- 14 VALID / replicated ----
    ("LIGO GW150914", "valid", "statistical_confidence", STAT_SIG),
    ("Higgs boson", "valid", "statistical_confidence", STAT_SIG),
    ("Muon g-2", "valid", "reproducibility_check", RT),
    ("Gravity Probe B", "valid", "statistical_confidence", STAT_SIG),
    ("Eddington 1919", "valid", "causal_mechanism_claim", CT),
    ("ISIS-2 aspirin", "valid", "statistical_confidence", STAT_SIG),
    ("RECOVERY dexamethasone", "valid", "systematic_review_claim", ST),
    ("Pfizer BNT162b2", "valid", "statistical_confidence", STAT_SIG),
    ("SPRINT BP control", "valid", "systematic_review_claim", ST),
    ("LDL Mendelian randomization", "valid", "causal_mechanism_claim", CT),
    ("CFC ozone depletion", "valid", "causal_mechanism_claim", CT),
    ("Cochrane handwashing", "valid", "systematic_review_claim", ST),
    ("Many Labs anchoring", "valid", "reproducibility_check", RT),
    ("Many Labs Stroop", "valid", "reproducibility_check", RT),
]


def _normalize(evidence):
    e = dict(evidence)
    if "p_value" in e:
        if e["p_value"] is False:
            e["p_value"], e["alpha"] = 1.0, 0.05
        else:
            e["p_value"], e["alpha"] = 0.001, 0.05
    return e


def run() -> int:
    fa = fr = tn = tp = 0   # false-accept, false-reject, true-gate(neg), true-accept(pos)
    rows, money, false_accepts, false_rejects = [], [], [], []
    for name, gt, ctype, evidence in CORPUS:
        payload = {"schema_version": "capas-claim-payload-v3",
                   "claim": {"id": name.lower().replace(" ", "_"), "type": ctype, "text": name},
                   "evidence": _normalize(evidence)}
        verdict = capas.decide_external_claim(payload).get("verdict")
        accepted = verdict == "ACCEPT"
        if gt == "false":
            if accepted: fa += 1; false_accepts.append(name)
            else: tn += 1; money.append(name)
        else:
            if accepted: tp += 1
            else: fr += 1; false_rejects.append(name)
        rows.append((name, gt, verdict, "ACCEPT" if accepted else "GATED"))

    n_false = sum(1 for _, gt, _, _ in CORPUS if gt == "false")
    n_valid = len(CORPUS) - n_false
    print("PILOT (real, agent-coded corpus, n=28) — falsifiability vs plausibility\n")
    print(f"{'case':30s} {'truth':6s} {'CAPAS':8s} {'outcome'}")
    for name, gt, v, o in rows:
        flag = "  <- FALSE-ACCEPT" if (gt == "false" and o == "ACCEPT") else ("  <- false-reject" if (gt == "valid" and o == "GATED") else "")
        print(f"{name:30s} {gt:6s} {str(v):8s} {o}{flag}")
    print(f"\nConfusion: fraud GATED {tn}/{n_false} · fraud FALSE-ACCEPTED {fa}/{n_false} (the dangerous error)")
    print(f"           valid ACCEPTED {tp}/{n_valid} · valid FALSE-REJECTED {fr}/{n_valid} (good-idea-rejected)")
    acc = (tn + tp) / len(CORPUS)
    print(f"Overall separation accuracy: {acc:.1%}  (plausibility alone: 0% — all 28 passed plausibility)")
    if false_accepts: print("FALSE-ACCEPTS (must review):", false_accepts)
    if false_rejects: print("FALSE-REJECTS (good ideas gated):", false_rejects)
    print("\nHONESTY: agent-coded corpus (a step toward independence, not human-adjudicated); transparent "
          "uniform coercion; the result stands or falls on the coding, which is auditable via the cited sources.")
    # the load-bearing property: ZERO false-accepts (fail-closed moat); separation well above chance
    ok = (fa == 0 and acc >= 0.85)
    print("PILOT RESULT:", "GATE HOLDS — 0 false-accepts, separation %.0f%%" % (acc * 100) if ok
          else "REVIEW — inspect misclassifications above")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(run())
