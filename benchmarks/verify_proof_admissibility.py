#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""Verify the proof_admissibility claim type: gate whether the evidence licenses 'theorem'.
Core gate = a QUANTIFIER-SCOPE check (capas_language): a universally-quantified claim needs a bound
uniform over the quantified index; finite/leading-order checks license only the checked scope.
Run: `python3 benchmarks/verify_proof_admissibility.py`."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import capas_sdk as C

def v(ev):
    return C.gate("proof_admissibility", ev, claim_text="X is a theorem")["verdict"]

def main() -> int:
    base = {"claim_scope": "universal", "steps_all_valid": True,
            "load_bearing_step_identified": True, "uniform_bound_proven": True}
    checks = [
        # (label, evidence patch, expected verdict)
        ("universal + uniform bound proven -> theorem licensed", {}, "ACCEPT"),
        ("bounded claim, steps+crux ok -> licensed", {"claim_scope": "bounded", "uniform_bound_proven": False}, "ACCEPT"),
        ("universal but NO uniform bound (finite checks only) -> downgrade",
         {"uniform_bound_proven": False}, "REWRITE"),
        ("a step does not validate (a gap) -> not a proof", {"steps_all_valid": False}, "REJECT"),
        ("load-bearing step not identified -> inadmissible", {"load_bearing_step_identified": False}, "REJECT"),
    ]
    fails = []
    for label, patch, expected in checks:
        got = v({**base, **patch})
        if got != expected:
            fails.append(f"{label}: expected {expected}, got {got}")
    # fail-closed: a missing required field HOLDs, never a false ACCEPT
    miss = C.gate("proof_admissibility", {"claim_scope": "universal", "steps_all_valid": True,
                                          "load_bearing_step_identified": True}, "x")["verdict"]
    if miss != "HOLD":
        fails.append(f"missing uniform_bound_proven should HOLD (fail-closed), got {miss}")
    # determinism: same input -> same audit hash
    ev = {**base, "uniform_bound_proven": False}
    h1 = C.gate("proof_admissibility", ev, "x").get("audit_hash")
    h2 = C.gate("proof_admissibility", ev, "x").get("audit_hash")
    if h1 != h2:
        fails.append("verdict is not deterministic (audit_hash differs)")
    if fails:
        print("FAIL:"); [print("  -", x) for x in fails]; return 1
    print("OK: proof_admissibility gates the word 'theorem' — universal claim without a uniform bound "
          "downgrades to leading-order + conjectured remainder (REWRITE); a gap or unidentified crux REJECTs; "
          "a proven uniform bound or a bounded claim ACCEPTs; missing evidence HOLDs (fail-closed); deterministic.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
