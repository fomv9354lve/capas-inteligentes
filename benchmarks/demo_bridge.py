# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""Demo + check: attacking the autoformalization frontier by triangulation.

Deterministic. The claim: "ALL values in the batch are below the limit 100." Three
formalizations are produced; one is a SEMANTIC ILLUSION ('at least one below' instead of
'all below') that COMPILES and that a type checker waves through. The probe battery includes
a mixed batch where 'all' and 'exists' DIVERGE — so the differential exposes the illusion and
the bridge fails closed. With only the two correct, independent formalizations the bridge is
trusted and the semantic residual shrinks as independent agreers are added (geometric, never 0).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import capas_bridge as B

LIMIT = 100
PROBES = [
    {"values": [10, 20, 30]},     # all below
    {"values": [50, 99]},         # all below
    {"values": [50, 200]},        # MIXED: 'all below' False, 'exists below' True  <- the discriminator
    {"values": [300, 400]},       # none below
]

# correct formalizations of "all values below the limit", produced independently:
F_all_1 = {"name": "all_v1", "group": "modelA", "fn": lambda p: all(x < LIMIT for x in p["values"])}
F_all_2 = {"name": "all_v2", "group": "modelB", "fn": lambda p: max(p["values"]) < LIMIT}
# SEMANTIC ILLUSION: 'at least one below' — compiles, wrong meaning:
F_illusion = {"name": "exists_v1", "group": "modelC", "fn": lambda p: any(x < LIMIT for x in p["values"])}
# a third correct, independent formalization (for the shrink check):
F_all_3 = {"name": "all_v3", "group": "modelD", "fn": lambda p: sum(1 for x in p["values"] if x >= LIMIT) == 0}


def run() -> int:
    checks = []

    # 1) the illusion is CAUGHT (what the compiler is blind to) -> fail closed
    r_ill = B.triangulate([F_all_1, F_all_2, F_illusion], PROBES,
                          back_translation=[{"name": "exists_v1", "agreement": 0.2}])
    checks.append(("semantic illusion (all->exists) DETECTED, bridge fails closed (DEFER)",
                   r_ill["decision"] == "DEFER" and "exists_v1" in [d["name"] for d in r_ill["dissenting_formalizations"]]))
    checks.append((f"   the discriminating probe is exposed (divergent probes {r_ill['divergent_probes']})",
                   2 in r_ill["divergent_probes"]))
    checks.append(("   back-translation independently flags the same illusion",
                   "exists_v1" in r_ill["back_translation_failures"]))

    # 2) two correct INDEPENDENT formalizations agree on all probes -> bridge trusted, graded
    r2 = B.triangulate([F_all_1, F_all_2], PROBES)
    checks.append((f"two independent correct formalizations -> TRUST, residual {r2['semantic_residual']}",
                   r2["decision"] == "TRUST" and r2["semantic_residual"] == round(1 / 3, 4)))

    # 3) adding a third independent agreer shrinks the residual (geometric, never 0)
    r3 = B.triangulate([F_all_1, F_all_2, F_all_3], PROBES)
    checks.append((f"third independent agreer shrinks residual ({r2['semantic_residual']} -> {r3['semantic_residual']}, never 0)",
                   r3["semantic_residual"] < r2["semantic_residual"] and r3["semantic_residual"] > 0))

    # C3 CLOSED: active probe SELECTION finds the discriminator that fixed probes missed.
    F_correct = {"name": "all", "group": "A", "fn": lambda p: all(x < LIMIT for x in p["values"])}
    F_wrong = {"name": "exists", "group": "B", "fn": lambda p: any(x < LIMIT for x in p["values"])}
    fixed_no_discriminator = [{"values": [10, 20]}, {"values": [50, 99]}]      # all-below only -> agree -> false TRUST
    weak = B.triangulate([F_correct, F_wrong], fixed_no_discriminator)
    pool = [{"values": [10, 20]}, {"values": [50, 200]}, {"values": [300]}]    # pool contains a mixed (discriminating) case
    sel = B.select_discriminating_probes([F_correct, F_wrong], pool)
    strong = B.triangulate([F_correct, F_wrong], sel["discriminating_probes"])
    checks.append(("C3: fixed probes miss the discriminator -> false TRUST", weak["decision"] == "TRUST"))
    checks.append(("C3 CLOSED: active selection finds the discriminating probe -> DEFER (illusion caught)",
                   sel["found"] >= 1 and strong["decision"] == "DEFER"))

    ok = all(c for _, c in checks)
    for label, c in checks:
        print(f"{'✅' if c else '❌'} {label}")

    # ── DOCUMENTED LIMIT (the new frontier after the attack — named, not hidden) ──
    # If every formalization shares the SAME systematic error (here <= vs <) AND no probe hits
    # the discriminating instance (x == 100), they all agree and the bridge FALSELY trusts.
    # The two holes: (C2) independence is SUPPLIED not MEASURED -> correlated mis-translation
    # survives; (C3) probe selection is not optimal -> the discriminating instance can be absent
    # (Bayesian experimental design, unbuilt). The frontier moved here; it did not vanish.
    P_no_boundary = [{"values": [10, 20]}, {"values": [50, 99]}, {"values": [50, 200]}, {"values": [300]}]
    Fle1 = {"name": "le1", "group": "mA", "fn": lambda p: all(x <= LIMIT for x in p["values"])}
    Fle2 = {"name": "le2", "group": "mB", "fn": lambda p: max(p["values"]) <= LIMIT}
    Fle3 = {"name": "le3", "group": "mC", "fn": lambda p: sum(1 for x in p["values"] if x > LIMIT) == 0}
    r_lim = B.triangulate([Fle1, Fle2, Fle3], P_no_boundary)
    limit_holds = r_lim["decision"] == "TRUST"   # the KNOWN miss (documented, not a pass)
    print(f"⚠️  documented limit: shared systematic error + no discriminating probe -> "
          f"FALSE {r_lim['decision']} (conf {r_lim['bridge_confidence']}). New frontier = C2 (measured "
          f"independence) + C3 (optimal probe selection). {'limit reproduced' if limit_holds else 'LIMIT CLOSED?'}")

    print("BRIDGE-FRONTIER ATTACK (triangulation catches the semantic illusion): pass ✅" if ok
          else "BRIDGE: FAILURES ❌")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(run())
