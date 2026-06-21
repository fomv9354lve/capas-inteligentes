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


if __name__ == "__main__":
    raise SystemExit(run())
