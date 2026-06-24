# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""Demo + check: continuous admissibility as a graded verifiable reward.

Asserts the ordering that keeps the signal from killing imagination:
    VERIFIED (1.0) > coherent viable CONJECTURE > ATTEST-deferred > REFUTED (0.0)
A coherent, viable, unproven conjecture must score ABOVE a refuted claim, so an
optimizer is steered toward verifiable bridges, never away from the unproven.
Deterministic; no network/key. Not part of `capas validate` (illustrative).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import capas_admissibility as A
from scipy import stats as _stats

SV = "capas-claim-payload-v3"
FIN = {"reported_value": 1.0, "reference_value": 1.0, "tolerance": 1.0, "metric_period_match": True}


def _p(text, ctype, evidence):
    return {"schema_version": SV, "claim": {"id": "c", "type": ctype, "text": text}, "evidence": evidence}


def run() -> int:
    a = [10.1, 10.3, 9.9, 10.2, 10.0, 10.4, 9.8, 10.1]
    b = [12.0, 12.3, 11.8, 12.1, 12.2, 11.9, 12.4, 12.0]
    p = round(float(_stats.ttest_ind(a, b, equal_var=False)[1]), 5)

    verified = _p("balances", "financial_metric_claim",
                  {**FIN, "accounting": {"identity": "balance_sheet", "assets": 1000, "liabilities": 600, "equity": 400}})
    verified_stat = _p("treatment works", "statistical_confidence",
                       {"p_value": p, "alpha": 0.05, "effect_direction_confirmed": True,
                        "raw_data": {"group_a": a, "group_b": b}})
    conjecture = _p("treatment works", "statistical_confidence",
                    {"p_value": 0.01, "alpha": 0.05, "effect_direction_confirmed": True})  # declared, no raw
    attest = _p("X causes Y", "causal_mechanism_claim",
                {"intervention_or_natural_experiment": True, "temporal_order_established": True,
                 "confounders_controlled": True, "mechanism_evidence_present": True})       # unbacked design
    refuted = _p("balances", "financial_metric_claim",
                 {**FIN, "accounting": {"identity": "debits_equal_credits", "debits": [100], "credits": [999]}})

    rows = [("VERIFIED (re-derived)", verified, "VERIFIED"),
            ("VERIFIED stat (raw)", verified_stat, "VERIFIED"),
            ("CONJECTURE (declared, viable)", conjecture, "CONJECTURE"),
            ("ATTEST_DEFER (needs subject)", attest, "ATTEST_DEFER"),
            ("REFUTED (contradicted)", refuted, "REFUTED")]

    print(f"{'case':32s} | score | class")
    scores = {}
    cls_ok = True
    for label, pl, exp_cls in rows:
        r = A.admissibility(pl)
        scores[label] = r["score"]
        good = r["class"] == exp_cls
        cls_ok = cls_ok and good
        print(f"{label:32s} | {r['score']:.3f} | {r['class']:12s} {'✅' if good else '❌ want ' + exp_cls}")

    ranking_ok = (scores["VERIFIED (re-derived)"] > scores["CONJECTURE (declared, viable)"]
                  > scores["ATTEST_DEFER (needs subject)"] > scores["REFUTED (contradicted)"])
    print()
    print(f"ORDERING VERIFIED > CONJECTURE > ATTEST_DEFER > REFUTED: {'✅' if ranking_ok else '❌'}")
    print(f"imagination not killed (conjecture {scores['CONJECTURE (declared, viable)']:.2f} > "
          f"refuted {scores['REFUTED (contradicted)']:.2f}): "
          f"{'✅' if scores['CONJECTURE (declared, viable)'] > scores['REFUTED (contradicted)'] else '❌'}")
    ok = cls_ok and ranking_ok
    print("ADMISSIBILITY REWARD: all checks pass ✅" if ok else "ADMISSIBILITY: FAILURES ❌")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(run())
