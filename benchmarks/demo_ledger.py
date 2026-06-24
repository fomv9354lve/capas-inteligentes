# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""Demo + check: the survive-refutation ledger end to end.

Deterministic. A claim is ATTESTED (signed, hash-chained, bound to an identity), the WORLD
RESOLVES it (survived/refuted), reputation updates, and a NEW declaration is weighted by the
earned standing. Asserts: surviving refutation lifts an identity's standing and its next
declaration's weight; being refuted drops both BELOW an unknown identity; a re-derived (GATE)
result is not discounted; and the tamper-evident chain stays intact through it all.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import capas_ledger as L
import capas_rcc as RCC

SV = "capas-claim-payload-v3"
FIN = {"reported_value": 1.0, "reference_value": 1.0, "tolerance": 1.0, "metric_period_match": True,
       "accounting": {"identity": "balance_sheet", "assets": 1000, "liabilities": 600, "equity": 400}}


def _cert(cid):
    return RCC.rcc({"schema_version": SV, "claim": {"id": cid, "type": "financial_metric_claim", "text": cid},
                    "evidence": FIN})


def run() -> int:
    checks = []
    log = []

    # lab_A attests 3 claims; the world says all survived
    for i in range(3):
        log = L.attest(log, _cert(f"A{i}"), "lab_A", at=f"2026-06-22T0{i}:00:00Z")
        log = L.resolve(log, f"A{i}", "survived")
    # lab_B attests 1 claim; the world refutes it
    log = L.attest(log, _cert("B0"), "lab_B", at="2026-06-22T05:00:00Z")
    log = L.resolve(log, "B0", "refuted")

    sa, sb = L.standing(log, "lab_A"), L.standing(log, "lab_B")
    checks.append((f"surviving refutation lifts standing (lab_A {sa['survived']}surv -> trust {sa['trust']})",
                   sa["trust"] > 0.5))
    checks.append((f"being refuted lowers standing (lab_B {sb['refuted']}ref -> trust {sb['trust']})",
                   sb["trust"] < 0.5))

    # a NEW declaration (would gate ACCEPT) weighted by earned standing
    new = _cert("new_claim")
    wa = L.admit(log, new, "lab_A", scope="ATTEST")
    wb = L.admit(log, new, "lab_B", scope="ATTEST")
    wu = L.admit(log, new, "unknown_lab", scope="ATTEST")
    checks.append(("same new declaration: proven identity weighted ABOVE unknown",
                   wa["provisional_weight"] > wu["provisional_weight"]))
    checks.append(("same new declaration: refuted identity weighted BELOW unknown",
                   wb["provisional_weight"] < wu["provisional_weight"]))

    # GATE (re-derived) is not discounted — stands on its own proof
    g = L.admit(log, new, "unknown_lab", scope="GATE")
    checks.append(("a RE-DERIVED (GATE) result is not discounted by standing", g["provisional_weight"] == wa["gate_reward"]))

    # the tamper-evident chain survives attest + resolve
    checks.append(("the signed hash-chain stays intact through attest + resolve", wa["chain_intact"] is True))

    ok = all(c for _, c in checks)
    for label, c in checks:
        print(f"{'✅' if c else '❌'} {label}")
    print(f"   same new declaration -> lab_A {wa['provisional_weight']} · unknown {wu['provisional_weight']} · lab_B(refuted) {wb['provisional_weight']}")
    print("SURVIVE-REFUTATION LEDGER (declared -> accountable, not verified): pass ✅" if ok
          else "LEDGER: FAILURES ❌")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(run())
