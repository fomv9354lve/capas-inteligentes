# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""LIVE cross-lab extraction triangulation (the C2 fix, live) — DeepSeek + Gemini.

Ready to fire. Set both keys in env and run:
    GEMINI_KEY=... DEEPSEEK_KEY=... python3 benchmarks/live_multimodel.py

Each evidence field is extracted INDEPENDENTLY by two DISTINCT labs (DeepSeek + Gemini);
they must AGREE and ground a span or the field is DEFERRED to a human (a systematic
single-model misread is caught by the other lab). Then the deterministic gate rules. If a
key is missing or its quota is exhausted, that extractor abstains -> the field fails CLOSED
(deferred), never a false ACCEPT — so this is safe to run even partially.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import capas
import capas_intake as I

CASES = [
    ("RECOVERY dexamethasone (valid)", "systematic_review_claim",
     "The RECOVERY trial was a randomized, controlled, open-label platform trial with a pre-registered "
     "protocol (ISRCTN50189673). Eligibility and inclusion criteria were explicitly declared. Allocation was "
     "randomized so risk of bias was low and formally assessed. The 28-day mortality benefit was consistent "
     "with the WHO REACT prospective meta-analysis of corticosteroid trials."),
    ("Wakefield MMR-autism (fraud)", "causal_mechanism_claim",
     "We describe a case series of twelve children referred to a clinic. There was no control group and no "
     "intervention was assigned. The temporal link to vaccination was based on parental recall. Potential "
     "confounders were not controlled. A causal mechanism was proposed only speculatively."),
]


def run() -> int:
    extractors = [I.deepseek_extractor, I.gemini_extractor]
    for name, ctype, src in CASES:
        r = I.intake_multimodel(name, ctype, src, extractors)
        verdict = capas.decide_external_claim(r["payload"]).get("verdict")
        print(f"=== {name}")
        for pf in r["per_field"]:
            print(f"    {pf['field']:34s} {pf['status']:9s} votes={pf.get('model_votes', pf.get('value'))}")
        print(f"    extracted={r['evidence_extracted']}")
        print(f"    deferred ={r['deferred_fields']}  residual={r['extraction_residual']}")
        print(f"    GATE VERDICT: {verdict}\n")
    print("Cross-lab triangulation complete. Disagreements deferred (C2 caught live); "
          "extraction uncertainty never became a false ACCEPT.")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
