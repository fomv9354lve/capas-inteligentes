#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""Verify CAPAS-física multi-tier audit (nodal skeleton + domain invariants + RMT corpus).
Pre-registered: internal-inconsistency FLAGs, consistent PASSes, cross-domain fabrication KILLED.
Run: `python3 benchmarks/verify_capas_fisica.py`."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import capas_physica as cf
import capas_nodal as nod

def main() -> int:
    fails = []
    # 1. RMT closed-form collision (the paper's x=0.13 row) -> FLAG on rmt/closed_form
    r = cf.audit({"x":0.13,"k":150,"C_hat":0.0549,"C_pred":0.0550,"sigma":0.0004,"z":-0.23})
    if r["verdict"] != "FLAG" or not any(t=="rmt" and f=="closed_form" for t,f in r["flags"]):
        fails.append(f"x=0.13 should FLAG rmt/closed_form, got {r['verdict']} {r['flags']}")
    # 2. consistent RMT row -> PASS
    if cf.audit({"x":0.30,"k":60,"C_hat":0.1343,"C_pred":0.1336,"sigma":0.0014,"z":0.49})["verdict"] != "PASS":
        fails.append("x=0.30 should PASS")
    # 3. cross-domain fabrication: |corr|>1 killed by the nodal skeleton in ANY domain
    if nod.check({"corr":1.4})["verdict"] != "KILLED":
        fails.append("corr=1.4 should be KILLED by the nodal |corr|<=1 law")
    # 4. nodal skeleton spans multiple strata from one small set
    reach = nod.check({"p":0.5,"corr":0.5,"var":0.1})["strata_reached"]
    if len({"quantum","finance","epi","rmt","stats"} & set(reach)) < 4:
        fails.append(f"nodal skeleton should span >=4 strata, got {reach}")
    if fails:
        print("FAIL:"); [print("  -", x) for x in fails]; return 1
    print("OK: RMT collision FLAGs, consistent row PASSes, cross-domain fabrication KILLED by nodal law, "
          "skeleton spans >=4 strata. Multi-tier audit (nodal+domain+RMT) composes fail-closed.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
