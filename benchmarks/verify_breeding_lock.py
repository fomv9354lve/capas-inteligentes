#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""Verify the breeding lock: force a claim to interbreed with CAPAS's invariant corpus; kill the
inviable hybrid (contradicts an established law) as HOLD+falsifier, PRESERVED not rejected; admit
the viable one; and honestly ADMIT the cryptic fabrication (consistent with every law) — the floor.
Run: `python3 benchmarks/verify_breeding_lock.py`."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import capas_breeding as b

# (name, evidence, expected_verdict, expect_demand_falsifier)
CASES = [
    ("valid probabilities",            {"probabilities": [0.1, 0.9]},               "VIABLE",   False),
    ("quantum T2<=2T1 (valid)",        {"quantum": {"t1_us": 120, "t2_us": 90}},          "VIABLE",   False),
    ("valid conservation",             {"parts": [30, 40, 30], "total": 100},        "VIABLE",   False),
    ("prob bound violation",           {"probabilities": [1.7, 0.9]},               "HOLD",     True),
    ("quantum T2>2T1 (law collision)", {"quantum": {"t1_us": 50, "t2_us": 300}},          "HOLD",     True),
    ("conservation violation",         {"parts": [30, 40, 40], "total": 100},        "HOLD",     True),
    ("corpus-disconnected (evasion)",  {"foo": 1, "bar": "x"},                       "UNTESTED", False),
    # CRYPTIC fabrication (the FLOOR): a FALSE claim whose numbers satisfy every law -> must be VIABLE
    ("cryptic fabrication (FLOOR)",    {"quantum": {"t1_us": 100, "t2_us": 150}, "probabilities": [0.5, 0.5]}, "VIABLE", False),
]

def main() -> int:
    fails = []
    for name, ev, exp_v, exp_f in CASES:
        r = b.breeding_lock(ev)
        v, f = r["verdict"], r["demand_falsifier"]
        ok = (v == exp_v) and (f == exp_f)
        # a HOLD must NEVER be a hard reject (preserved dissent) and must be re-derivable
        if v == "HOLD":
            ok = ok and v != "REJECT" and r["breeding_audit_hash"].startswith("sha256:")
        mark = "ok " if ok else "FAIL"
        print(f"  [{mark}] {name:34s} -> {v:9s} falsifier={f}  (conn={r['corpus_connection']})")
        if not ok:
            fails.append(f"{name}: got {v}/{f}, want {exp_v}/{exp_f}")
    # determinism
    a1 = b.breeding_lock({"probabilities": [1.7]}); a2 = b.breeding_lock({"probabilities": [1.7]})
    if a1["breeding_audit_hash"] != a2["breeding_audit_hash"]:
        fails.append("audit_hash not deterministic")
    if fails:
        print("\nFAIL:"); [print("  -", x) for x in fails]; return 1
    print(f"\nOK {len(CASES)}/{len(CASES)}: inviable hybrids HELD (not rejected) + falsifier demanded; "
          f"viable admitted; cryptic-consistent fabrication ADMITTED (floor, honest); evasion reported.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
