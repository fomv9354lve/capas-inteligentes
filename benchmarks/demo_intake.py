"""Demo + check: the intake membrane shrinks the EXTRACTION residual, fail-closed.

Deterministic (mock extractors prove the triangulation logic; the live DeepSeek extractor is
the untested proposer). The load-bearing safety property: extraction UNCERTAINTY can never
become a false ACCEPT — a deferred/ungrounded field leaves the payload incomplete and the
deterministic gate HOLDs.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import capas
import capas_intake as I

CT = "systematic_review_claim"   # 4 fields: protocol_registered, inclusion_criteria_declared, risk_of_bias_assessed, effect_consistency
TEXT = "Pre-registered RCT, declared inclusion criteria, risk-of-bias assessed, effect consistent across sites."
SRC = "...registered protocol NCT..., inclusion criteria declared, Cochrane risk-of-bias, consistent effect..."


def agree_true(field, ct, st, idx):           # all independent extractions agree + span
    return {"supported": True, "span": f"source grounds {field}"}


def affirm_no_span(field, ct, st, idx):        # affirmed but ungrounded -> must DEFER
    return {"supported": True, "span": None}


def source_absent(field, ct, st, idx):         # source does not support -> field False
    return {"supported": False, "span": None}


def one_disagrees(target):                     # all True except `target`, where extractions disagree
    def ex(field, ct, st, idx):
        if field == target:
            return {"supported": idx % 2 == 0, "span": "x" if idx % 2 == 0 else None}
        return {"supported": True, "span": f"grounds {field}"}
    return ex


def _verdict(payload):
    return capas.decide_external_claim(payload).get("verdict")


def run() -> int:
    checks = []

    # 1) fully grounded + agreeing -> all fields extracted, gate ACCEPTs
    r = I.intake(TEXT, CT, SRC, agree_true, k=3)
    checks.append(("grounded + agreeing extractions -> all fields extracted, no deferrals",
                   not r["deferred_fields"] and len(r["evidence_extracted"]) == 4))
    checks.append(("extracted -> the gate ACCEPTs the well-grounded valid claim",
                   _verdict(r["payload"]) == "ACCEPT"))

    # 2) residual shrinks with more independent agreers (never 0)
    r2 = I.intake(TEXT, CT, SRC, agree_true, k=2)
    r5 = I.intake(TEXT, CT, SRC, agree_true, k=5)
    checks.append(("extraction residual shrinks with more independent agreers, never 0",
                   r5["extraction_residual"] < r2["extraction_residual"] and r5["extraction_residual"] > 0))

    # 3) affirmed WITHOUT a source span -> DEFER (never fabricated)
    rns = I.intake(TEXT, CT, SRC, affirm_no_span, k=3)
    checks.append(("affirmed but ungrounded -> ALL fields deferred (no fabrication)",
                   len(rns["deferred_fields"]) == 4 and not rns["evidence_extracted"]))

    # 4) THE SAFETY PROPERTY: one field's extractions DISAGREE -> deferred -> gate HOLDs, never ACCEPT
    rd = I.intake(TEXT, CT, SRC, one_disagrees("effect_consistency"), k=3)
    checks.append(("disagreement on one field -> it is DEFERRED (routed to a human)",
                   "effect_consistency" in rd["deferred_fields"] and rd["fail_closed"]))
    checks.append(("extraction uncertainty -> gate HOLDs, NEVER a false ACCEPT",
                   _verdict(rd["payload"]) != "ACCEPT"))

    # 5) source contradicts a field -> field False -> gate does not ACCEPT (fraud-like gating)
    ra = I.intake(TEXT, CT, SRC, source_absent, k=3)
    checks.append(("source does not support -> fields False -> gate does not ACCEPT",
                   _verdict(ra["payload"]) != "ACCEPT"))

    ok = all(c for _, c in checks)
    for label, c in checks:
        print(f"{'✅' if c else '❌'} {label}")
    print(f"   (residual k=2 {r2['extraction_residual']} -> k=5 {r5['extraction_residual']}; never 0 — the bridge ceiling)")
    print("INTAKE MEMBRANE (extraction residual: measured, fail-closed, human-routed): pass ✅" if ok
          else "INTAKE: FAILURES ❌")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(run())
