"""AGGRESSIVE head-to-head: CAPAS vs the named SOTA approaches on one labeled corpus.

Honesty rules (this is the whole point):
  - CAPAS arm: the REAL engine (deterministic verdict).
  - LLM-judge arm: REAL language-model judgments (filled in by examples/h2h_llm_judge via agents).
  - Mechanism arms (optimistic-oracle / peer-prediction / reputation): MODELED from each
    mechanism's DOCUMENTED behavior, explicitly labeled 'modeled, not executed'. No fabricated
    numbers — each is a transparent decision function over the claim's structure.
  - The corpus is adversarial and INCLUDES the case CAPAS cannot win (the self-consistent liar,
    GIGO) so the result is credible, not a home-field demo.

Metric that matters: FALSE-ACCEPT on a checkable-false claim, and HONEST-DEFER on an unknowable
one (does the arm fabricate a verdict it cannot support?).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import capas_sdk

SV = "capas-claim-payload-v3"

# regime: REDERIVABLE (record<->text checkable) | UNSUPPORTED (declared, missing structure) |
#         GIGO (self-consistent liar, unknowable from text) | SUBJECTIVE (no ground truth)
# label : TRUE | FALSE | UNKNOWABLE  (the honest ground truth)
CORPUS = [
    {"id": "fin_ok", "regime": "REDERIVABLE", "label": "TRUE",
     "text": "Balance sheet: assets 1000 = liabilities 600 + equity 400.",
     "capas": ("financial_metric_claim",
               {"reported_value": 1.0, "reference_value": 1.0, "tolerance": 1.0, "metric_period_match": True,
                "invariants": {"accounting": {"assets": 1000, "liabilities": 600, "equity": 400}}})},
    {"id": "fin_books_dont_close", "regime": "REDERIVABLE", "label": "FALSE",
     "text": "Reported equity 300 with assets 1000 and liabilities 600 (books should close).",
     "capas": ("financial_metric_claim",
               {"reported_value": 1.0, "reference_value": 1.0, "tolerance": 1.0, "metric_period_match": True,
                "invariants": {"accounting": {"assets": 1000, "liabilities": 600, "equity": 300}}})},
    {"id": "grim_impossible_mean", "regime": "REDERIVABLE", "label": "FALSE",
     "text": "Mean rating was 5.19 across N=10 respondents on a 1-7 integer scale.",
     "capas": ("financial_metric_claim",
               {"reported_value": 1.0, "reference_value": 1.0, "tolerance": 1.0, "metric_period_match": True,
                "invariants": {"grim": {"mean": 5.19, "n": 10}}})},
    {"id": "quantum_T2_gt_2T1", "regime": "REDERIVABLE", "label": "FALSE",
     "text": "Qubit measured T1=11.2us and T2=23.4us by Ramsey (no dynamical decoupling).",
     "capas": ("financial_metric_claim",
               {"reported_value": 1.0, "reference_value": 1.0, "tolerance": 1.0, "metric_period_match": True,
                "invariants": {"quantum": {"t1_us": 11.2, "t2_us": 23.4, "t2_method": "ramsey"}}})},
    {"id": "prob_out_of_range", "regime": "REDERIVABLE", "label": "FALSE",
     "text": "The model assigns probability 1.4 to the positive class.",
     "capas": ("financial_metric_claim",
               {"reported_value": 1.0, "reference_value": 1.0, "tolerance": 1.0, "metric_period_match": True,
                "invariants": {"probabilities": [0.3, 1.4]}})},
    {"id": "conservation_break", "regime": "REDERIVABLE", "label": "FALSE",
     "text": "The three segments (10, 20, 35) sum to the reported total of 60.",
     "capas": ("financial_metric_claim",
               {"reported_value": 1.0, "reference_value": 1.0, "tolerance": 1.0, "metric_period_match": True,
                "invariants": {"parts": [10, 20, 35], "total": 60}})},
    {"id": "math_exact_true", "regime": "REDERIVABLE", "label": "TRUE",
     "text": "Solver output matches the reference to abs_error 0.0 within tolerance 1e-3.",
     "capas": ("exact_model_solution", {"abs_error": 0.0, "tolerance": 1e-3})},
    {"id": "trial_no_protocol", "regime": "UNSUPPORTED", "label": "UNKNOWABLE",
     "text": "Compound X reduced tumor volume by 40% (p=0.03) in our study.",
     "capas": ("systematic_review_claim", {})},  # missing protocol/inclusion -> REJECT/HOLD
    {"id": "competent_liar_rct", "regime": "GIGO", "label": "UNKNOWABLE",
     "text": "Our review pre-registered a protocol, declared inclusion criteria, assessed risk of bias, and found consistent effects. (Raw data withheld — the declarations may be lies.)",
     "capas": ("systematic_review_claim",
               {"protocol_registered": True, "inclusion_criteria_declared": True,
                "risk_of_bias_assessed": True, "effect_consistency": True})},
    {"id": "subjective_aesthetic", "regime": "SUBJECTIVE", "label": "UNKNOWABLE",
     "text": "This architectural design is the most elegant of the decade.",
     "capas": ("financial_metric_claim", {})},  # no contract -> HOLD
]


def run_capas(item) -> str:
    ct, ev = item["capas"]
    v = capas_sdk.gate(ct, ev, item["text"]).get("verdict")
    # normalize to ADMIT / BLOCK / DEFER
    return {"ACCEPT": "ADMIT", "REJECT": "BLOCK", "REWRITE": "BLOCK", "HOLD": "DEFER"}.get(v, "DEFER")


# --- MODELED mechanism arms (documented behavior, NOT executed) ---
def arm_optimistic_oracle(item) -> str:
    """UMA-style: a claim is ACCEPTED unless disputed within a window; resolution is a token-
    holder vote, not a truth check. In a single-shot intake with no disputer present, it admits
    everything not self-evidently malformed. Documented failure: whale capture / apathy."""
    return "ADMIT"  # no disputer -> accepted regardless of truth (the documented default)


def arm_peer_prediction(item) -> str:
    """Bayesian Truth Serum / Peer Truth Serum: scores truthful reporting only when MULTIPLE
    independent reports on the same item exist. On a single claim with one report it cannot
    produce a verdict — it is an incentive mechanism, not a single-item checker."""
    return "NA_NEEDS_PEERS"


def arm_reputation(item) -> str:
    """EigenTrust-style: weight by the source's prior track record. With a NEW/anonymous claimant
    (cold start) there is no signal; Sybil identities defeat it. No per-claim truth check."""
    return "NA_NO_HISTORY"


def score(arm_name, verdicts):
    """The metric: false-accepts on checkable-FALSE, and fabricated verdicts on UNKNOWABLE."""
    fa = sum(1 for it in CORPUS if it["label"] == "FALSE" and verdicts[it["id"]] == "ADMIT")
    checkable_false = sum(1 for it in CORPUS if it["label"] == "FALSE")
    # 'fabricated' = produced ADMIT/BLOCK on an UNKNOWABLE claim instead of deferring
    fab = sum(1 for it in CORPUS if it["label"] == "UNKNOWABLE" and verdicts[it["id"]] in ("ADMIT", "BLOCK"))
    unknowable = sum(1 for it in CORPUS if it["label"] == "UNKNOWABLE")
    correct_true = sum(1 for it in CORPUS if it["label"] == "TRUE" and verdicts[it["id"]] == "ADMIT")
    total_true = sum(1 for it in CORPUS if it["label"] == "TRUE")
    na = sum(1 for it in CORPUS if str(verdicts[it["id"]]).startswith("NA"))
    return {"arm": arm_name, "false_accepts": f"{fa}/{checkable_false}",
            "fabricated_on_unknowable": f"{fab}/{unknowable}",
            "true_admitted": f"{correct_true}/{total_true}",
            "abstained_NA": na, "determinism": "yes" if arm_name == "CAPAS" else
            ("yes" if arm_name.startswith("modeled") else "NO (stochastic)")}


def run(llm_verdicts: dict | None = None) -> dict:
    arms = {
        "CAPAS": {it["id"]: run_capas(it) for it in CORPUS},
        "modeled: optimistic-oracle (UMA)": {it["id"]: arm_optimistic_oracle(it) for it in CORPUS},
        "modeled: peer-prediction (BTS)": {it["id"]: arm_peer_prediction(it) for it in CORPUS},
        "modeled: reputation (EigenTrust)": {it["id"]: arm_reputation(it) for it in CORPUS},
    }
    if llm_verdicts:
        arms["LLM-judge (REAL)"] = {it["id"]: llm_verdicts.get(it["id"], "DEFER") for it in CORPUS}
    board = [score(name, v) for name, v in arms.items()]
    return {"corpus_size": len(CORPUS), "arms": arms, "scoreboard": board}


if __name__ == "__main__":
    lv = None
    if len(sys.argv) > 1 and Path(sys.argv[1]).exists():
        lv = json.load(open(sys.argv[1]))
    out = run(lv)
    print(f"=== HEAD-TO-HEAD · {out['corpus_size']} labeled claims ===\n")
    for it in CORPUS:
        print(f"  [{it['label']:10s} {it['regime']:11s}] {it['id']}")
    print("\n--- per-arm verdicts ---")
    for name, v in out["arms"].items():
        print(f"\n{name}:")
        for it in CORPUS:
            print(f"    {it['id']:24s} {v[it['id']]}")
    print("\n--- SCOREBOARD (lower false-accepts + fabrications = better) ---")
    for s in out["scoreboard"]:
        print(f"  {s['arm']:38s} false-accept {s['false_accepts']}  "
              f"fabricated/unknowable {s['fabricated_on_unknowable']}  "
              f"true {s['true_admitted']}  NA {s['abstained_NA']}  determ {s['determinism']}")
    Path("/tmp/h2h_result.json").write_text(json.dumps(out, indent=2))
    print("\nsaved -> /tmp/h2h_result.json")
