# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""Demo + check: the independence-weighted sequential e-test (THE WELD).

Deterministic. The contribution is falsifiable and checked here: a CIRCULAR corroboration
(5 experiments, all the SAME independence group) must NOT reach significance — the naive
independence-blind product crosses 1/alpha (false confidence), the weld does not. The SAME
5 experiments across 5 INDEPENDENT groups must reach significance in both. That gap is the
false confidence the weld strips out (exactly the inflation POPPER-style aggregation, which
assumes independence, silently permits).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import capas_sequential as S

E = 4.0          # each experiment's e-value
ALPHA = 0.05     # threshold 1/alpha = 20


def run() -> int:
    checks = []

    # 1) CIRCULAR: 5 experiments, one shared source -> not really 5 independent tests
    circular = [{"e_value": E, "group": "sourceA", "name": f"exp{i}"} for i in range(5)]
    rc = S.sequential_test(circular, ALPHA)
    checks.append(("circular corroboration: naive product crosses 1/alpha (false confidence)",
                   rc["naive_reject_null"] is True))
    checks.append(("circular corroboration: WELD refuses significance (counts the group ~once)",
                   rc["reject_null"] is False))
    checks.append((f"   weld stripped {rc['false_confidence_removed']}x false confidence "
                   f"(naive {rc['naive_e_process']} -> adjusted {rc['e_process']}, thresh {rc['reject_threshold']})",
                   rc["false_confidence_removed"] and rc["false_confidence_removed"] > 1))

    # 2) GENUINELY INDEPENDENT: same 5 experiments, 5 distinct groups
    indep = [{"e_value": E, "group": f"src{i}", "name": f"exp{i}"} for i in range(5)]
    ri = S.sequential_test(indep, ALPHA)
    checks.append(("independent corroboration: WELD reaches significance (correctly rejects null)",
                   ri["reject_null"] is True and ri["naive_reject_null"] is True))
    checks.append(("independent case == naive (no inflation to remove when truly independent)",
                   abs(ri["e_process"] - ri["naive_e_process"]) < 1e-6))

    # 3) e-value calibrator validity: p=1 -> e<=1 ; smaller p -> larger e ; monotone
    e1, e_mid, e_small = S.p_to_e(1.0), S.p_to_e(0.05), S.p_to_e(0.001)
    checks.append(("p_to_e valid: p=1 -> e<=1, and strictly decreasing in p",
                   e1 <= 1.0 and e1 < e_mid < e_small))

    # 4) bridge from consilience structure runs end to end
    levels = [{"claimed": 2.0, "adjacencies": [{"value": 2.0, "group": g} for g in "ABC"]}]
    rb = S.from_consilience_levels(levels, ALPHA)
    checks.append(("from_consilience_levels: 3 independent corroborations drive the e-test",
                   rb["independent_groups"] == 3 and rb["experiments"] == 3))

    ok = all(c for _, c in checks)
    for label, c in checks:
        print(f"{'✅' if c else '❌'} {label}")
    print("INDEPENDENCE-WELDED SEQUENTIAL E-TEST: pass ✅" if ok else "SEQUENTIAL: FAILURES ❌")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(run())
