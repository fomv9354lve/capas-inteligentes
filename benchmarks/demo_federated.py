# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""Demo + check: the federated ledger integrates all five structural lenses.

Deterministic. Asserts: independent resolvers collapse the claim (superposition -> credence ->
collapse); same-group collusion (many identities, one independent group) does NOT collapse it
(entanglement/decoherence: correlated votes count once); genuinely-independent Sybil DOES break
it (the named residual); and the identity trilemma forbids holding all three properties.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import capas_federated as F


def run() -> int:
    checks = []

    # MATERIALIST + SUPERPOSITION: 5 INDEPENDENT resolvers, 4 survived / 1 refuted -> collapses survived
    indep = [{"verdict": "survived", "group": g} for g in "ABCD"] + [{"verdict": "refuted", "group": "E"}]
    ri = F.resolve_federated("c1", indep)
    checks.append((f"independent resolvers collapse the claim (survived {ri['independent_survived']}/{ri['independent_refuted']}"
                   f", credence {ri['credence']})", ri["outcome"] == "survived" and ri["collapsed"]))

    # ENTANGLEMENT/DECOHERENCE: 5 'survived' votes but ALL from one colluding group -> counts ONCE -> stays OPEN
    collusion = [{"verdict": "survived", "group": "sockpuppet"} for _ in range(5)]
    rc = F.resolve_federated("c2", collusion)
    checks.append(("same-group collusion (5 identities, 1 independent group) does NOT collapse -> stays open",
                   rc["outcome"] == "open" and rc["independent_survived"] == 1))

    # SUPERPOSITION: an undecided claim carries a credence, not a binary
    checks.append(("an uncollapsed claim carries a Beta survival credence (not true/false)",
                   0.0 < rc["credence"] < 1.0 and rc["collapsed"] is False))

    # NAMED RESIDUAL: genuinely-independent Sybil (5 real distinct groups) DOES collapse it
    sybil = [{"verdict": "survived", "group": f"sybil{i}"} for i in range(5)]
    rs = F.resolve_federated("c3", sybil)
    checks.append(("genuinely-independent Sybil DOES break federation (residual named, not hidden)",
                   rs["outcome"] == "survived"))

    # COMPLEMENTARITY: the trilemma forbids all three; naming the sacrifice is feasible
    two = F.identity_tradeoff(["unique", "private"])
    three = F.identity_tradeoff(["unique", "self_sovereign", "private"])
    checks.append(("identity trilemma: holding two is feasible and names the sacrifice",
                   two["feasible"] and two["sacrificed"] == ["self_sovereign"]))
    checks.append(("identity trilemma: asking for all three is infeasible", three["feasible"] is False))

    ok = all(c for _, c in checks)
    for label, c in checks:
        print(f"{'✅' if c else '❌'} {label}")
    print("FEDERATED LEDGER (five lenses, landed to structure): pass ✅" if ok else "FEDERATED: FAILURES ❌")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(run())
