# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""Demo + check: consilience — bounding the GIGO residual by INDEPENDENT adjacency.

Deterministic. Asserts: no adjacency -> pure GIGO (residual 1.0); independent
corroborations shrink the residual; same-source corroborations do NOT (fake
consilience caught by independence grouping); an independent dissent CONTRADICTS the
claim (the fabrication broke against the outside).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import capas_consilience as CO


def run() -> int:
    checks = []

    r0 = CO.consilience(2.0, [])
    checks.append(("no adjacency -> PURE GIGO (residual 1.0)",
                   r0["fabrication_resistance"] == 0 and r0["reality_gap_residual"] == 1.0 and "PURE GIGO" in r0["status"]))

    r3 = CO.consilience(2.0, [{"value": 2.0, "group": "auditorA"}, {"value": 2.0, "group": "XBRL"}, {"value": 2.0, "group": "bank"}])
    checks.append(("3 INDEPENDENT corroborations -> reality-anchored, residual shrinks",
                   r3["fabrication_resistance"] == 3 and r3["reality_gap_residual"] < 0.3 and "ANCHORED" in r3["status"]))

    rsame = CO.consilience(2.0, [{"value": 2.0, "group": "A"}] * 3)
    checks.append(("3 SAME-source corroborations -> resistance 1 (fake consilience caught)",
                   rsame["fabrication_resistance"] == 1))

    rcon = CO.consilience(2.0, [{"value": 2.0, "group": "A"}, {"value": 5.0, "group": "bank"}])
    checks.append(("an independent adjacency DISAGREES -> CONTRADICTED (web breaks the claim)",
                   "CONTRADICTED" in rcon["status"] and len(rcon["dissent"]) == 1))

    r5 = CO.consilience(2.0, [{"value": 2.0, "group": g} for g in "ABCDE"])
    checks.append(("more independent adjacency -> smaller residual (monotone)",
                   r5["reality_gap_residual"] < r3["reality_gap_residual"]))

    ok = all(c for _, c in checks)
    for label, c in checks:
        print(f"{'✅' if c else '❌'} {label}")
    print("CONSILIENCE (reach outside the slice by adjacency): all checks pass ✅" if ok else "CONSILIENCE: FAILURES ❌")
    return 0 if ok else 1


def run_recursive() -> int:
    import capas_consilience as CO
    # geometric shrink: each recursion moves the unknown-unknown up a level
    levels = [
        {"claimed": 2.0, "question": "is the fact real?", "adjacencies": [{"value": 2.0, "group": g} for g in "ABC"]},
        {"claimed": 1.0, "question": "are those sources independent?", "adjacencies": [{"value": 1.0, "group": g} for g in "XYZ"]},
        {"claimed": 1.0, "question": "is that independence real (separate custody)?", "adjacencies": [{"value": 1.0, "group": g} for g in "PQ"]},
    ]
    r1 = CO.consilience_recursive(levels[:1])
    r2 = CO.consilience_recursive(levels[:2])
    r3 = CO.consilience_recursive(levels[:3])
    ok = (r2["total_residual"] < r1["total_residual"] and r3["total_residual"] < r2["total_residual"]
          and r3["total_residual"] > 0 and r3["irreducible_floor"] > 0)
    print(f"{'✅' if ok else '❌'} recursive flattening: residual shrinks geometrically "
          f"({r1['total_residual']} -> {r2['total_residual']} -> {r3['total_residual']}) but never 0 "
          f"(floor {r3['irreducible_floor']} = the subject)")
    # trialectic view: same geometric shrink, exposed as triads (thesis/antithesis/synthesis)
    t = CO.trialectic(levels)
    tri_ok = (len(t["triads"]) == 3 and t["total_residual"] == r3["total_residual"]
              and t["triads"][-1]["residual_after"] == r3["total_residual"]
              and all("corroborated" in x["synthesis"] for x in t["triads"]))
    print(f"{'✅' if tri_ok else '❌'} trialectic: 3 open-forward triads, residual_after matches the geometric product "
          f"(synthesis opens the next thesis)")

    # from_braid: a claim's independent adjacencies auto-gathered from the verified braid
    class _StubBraid:  # duck-typed (no import -> no braid<->rcc<->consilience cycle)
        nodes = {"n1": {"target": "mass", "value": 2.0, "method": "scale"},
                 "n2": {"target": "mass", "value": 2.0, "method": "stoichiometry"},
                 "n3": {"target": "mass", "value": 2.0, "method": "balance"},
                 "n4": {"target": "volume", "value": 9.9, "method": "scale"}}
    fb = CO.from_braid("mass", 2.0, _StubBraid())
    fb_ok = (fb["gathered_from_braid"] == 3 and fb["fabrication_resistance"] == 3 and "ANCHORED" in fb["status"])
    print(f"{'✅' if fb_ok else '❌'} from_braid: 3 same-target/different-method nodes auto-joined as independent "
          f"corroborations (volume node ignored)")

    ok = ok and tri_ok and fb_ok
    print("RECURSIVE CONSILIENCE: pass ✅" if ok else "RECURSIVE: FAIL ❌")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(run_recursive() if "--recursive" in sys.argv else run())
