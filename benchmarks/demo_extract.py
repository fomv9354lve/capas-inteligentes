# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""Demo + check: LLM extraction layer with deterministic span re-verification.

The offline cases are DETERMINISTIC (hand-made proposals simulating the LLM) and
prove the discipline without any network/key: a hallucinated input or a fabricated
citation is dropped and deferred (HOLD/ATTEST); a grounded input whose claimed
value does not re-derive is REJECTed; only a grounded, re-derivable claim ACCEPTs.
The LLM can expand what is verifiable but can never force an ACCEPT.

A live end-to-end path (prose -> DeepSeek proposes -> CAPAS verifies) runs only if
DEEPSEEK_KEY is set. Not part of `capas validate` (needs network/key).
"""
from __future__ import annotations

import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import capas_extract as ex

SRC = ("ACME Corp 10-K. As of December 31, 2024, total current assets were $200,000 "
       "and total current liabilities were $100,000. Management states the current ratio is 2.0.")

_HONEST = {
    "claim": {"type": "financial_metric_claim", "text": "current ratio is 2.0"},
    "evidence": {"accounting": {"identity": "financial_ratio", "ratio": "current_ratio",
                                "current_assets": 200000, "current_liabilities": 100000, "reported": 2.0}},
    "citations": [{"value": 200000, "span": "total current assets were $200,000"},
                  {"value": 100000, "span": "total current liabilities were $100,000"}],
}


def run() -> int:
    cases = []

    # 1) honest, grounded -> CAPAS re-derives 2.0 -> ACCEPT/GATE
    cases.append(("honest grounded extraction", _HONEST, "ACCEPT", "GATE"))

    # 2) hallucinated input ($500k not in source) -> dropped -> deferred HOLD/ATTEST
    hall = copy.deepcopy(_HONEST)
    hall["evidence"]["accounting"]["current_assets"] = 500000
    hall["evidence"]["accounting"]["reported"] = 5.0
    hall["citations"] = [{"value": 500000, "span": "total current assets were $500,000"},
                         {"value": 100000, "span": "total current liabilities were $100,000"}]
    cases.append(("hallucinated input not in source", hall, "HOLD", "ATTEST"))

    # 3) fabricated citation quote (span not in source) -> deferred
    fab = copy.deepcopy(_HONEST)
    fab["citations"] = [{"value": 200000, "span": "assets of exactly 200000 as audited by us"},
                        {"value": 100000, "span": "total current liabilities were $100,000"}]
    cases.append(("fabricated citation quote", fab, "HOLD", "ATTEST"))

    # 4) grounded inputs but claimed 5.0 -> CAPAS re-derives 2.0 -> REJECT
    lie = copy.deepcopy(_HONEST)
    lie["evidence"]["accounting"]["reported"] = 5.0
    cases.append(("grounded inputs, lie claimed (5.0)", lie, "REJECT", "GATE"))

    ok = True
    for label, prop, exp_v, exp_s in cases:
        r = ex.assemble_and_verify(prop, SRC)
        good = r["verdict"] == exp_v and r["scope"] == exp_s
        ok = ok and good
        print(f"{'✅' if good else '❌'} {label:36s} -> {r['verdict']:6s} [{r['scope']}]  "
              f"(want {exp_v}/{exp_s})")
    print("EXTRACTION DISCIPLINE: all cases pass ✅" if ok else "EXTRACTION DEMO: FAILURES ❌")

    import os
    if os.environ.get("DEEPSEEK_KEY") or os.environ.get("CAPAS_TRIAGE_KEY"):
        live = ex.extract_and_verify(SRC)
        print(f"\nLIVE (DeepSeek proposes, CAPAS verifies): {live['verdict']} [{live['scope']}] "
              f"grounded={(live.get('extraction') or {}).get('fully_grounded')}")
    else:
        print("\n(set DEEPSEEK_KEY to run the live prose->verdict path)")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(run())
