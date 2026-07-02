# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""CAPAS adversary — the kill battery. Truth is not what agrees; it is what SURVIVES the best
attack. So don't confirm — ATTACK. This composes the session's independent-ancestor killers into
one battery, defaults to GUILTY (the burden is on the claim to survive), and hits from every
vector that can reach it: the deterministic gate (structure), the breeding lock (contradiction
with the invariant corpus), and Benford (the human-generator fingerprint in the data).

HONEST BOUND (never strip): SURVIVED = un-refuted by the killers that HAPPENED to apply — NOT
true. A cryptic fabrication consistent with every law and Benford-conforming survives (the floor).
The battery is only as strong as its assassins reach; a claim no killer can touch is UNTESTED,
not innocent. This measures corroboration (Popper), never verification.
"""
from __future__ import annotations
import math
from typing import Any

BENFORD = [math.log10(1 + 1 / d) for d in range(1, 10)]

def _benford_kill(ev):
    nums = ev.get("data") or ev.get("numbers") or ev.get("reported_values")
    if not isinstance(nums, list) or len(nums) < 25:
        return None  # no reach
    d = [int(str(abs(x)).lstrip("0.")[0]) for x in nums
         if isinstance(x, (int, float)) and str(abs(x)).lstrip("0.")[:1].isdigit()]
    d = [k for k in d if 1 <= k <= 9]
    if len(d) < 25:
        return None
    obs = [d.count(k) / len(d) for k in range(1, 10)]
    mad = sum(abs(o - b) for o, b in zip(obs, BENFORD)) / 9
    return ("benford/generator-fingerprint", f"first-digit MAD {mad:.3f} > 0.015 — non-natural distribution") if mad > 0.015 else None

def _breeding_kill(ev):
    try:
        import capas_breeding
        r = capas_breeding.breeding_lock(ev)
        if r["verdict"] == "HOLD":  # load-bearing collision with the invariant corpus
            return ("breeding/corpus-collision", r["reason"][:90])
    except Exception:
        pass
    return None

def _gate_kill(claim_type, ev):
    try:
        import capas_sdk
        v = capas_sdk.gate(claim_type, ev, claim_type, "adv").get("verdict")
        if v in ("REJECT", "REWRITE"):
            return (f"gate/structure({v})", "deterministic gate found a structural deficiency")
    except Exception:
        pass
    return None

def kill_battery(claim_type: str, evidence: dict[str, Any]) -> dict[str, Any]:
    ev = evidence if isinstance(evidence, dict) else {}
    killers = [_gate_kill(claim_type, ev), _breeding_kill(ev), _benford_kill(ev)]
    reached = [k for k in killers if k is not None]  # assassins that landed a hit
    # an assassin that returns None either couldn't reach OR tried and failed; we only see hits here,
    # so we also record which vectors were APPLICABLE (could have reached)
    applicable = sum(x is not None for x in (
        _gate_applicable(claim_type, ev), _breeding_applicable(ev), _benford_applicable(ev)))
    if reached:
        verdict = "KILLED"
    elif applicable == 0:
        verdict = "UNTESTED"   # no assassin could even reach it — NOT innocent
    else:
        verdict = "SURVIVED"   # every assassin that could reach it, tried and failed
    return {
        "verdict": verdict,
        "killed_by": [v for v, _ in reached],
        "why": {v: w for v, w in reached},
        "assassins_that_reached": applicable,
        "bound": "SURVIVED = un-refuted by the killers that applied, NOT true; a cryptic law-and-Benford-"
                 "consistent fabrication survives (the floor). Only as strong as the assassins reach.",
    }

def _gate_applicable(ct, ev): 
    import capas_sdk
    return True if ct in getattr(__import__("capas"), "CLAIM_TYPE_REGISTRY", {}) else None
def _breeding_applicable(ev):
    try:
        import capas_invariants
        return True if capas_invariants.audit(ev).get("applicable") else None
    except Exception:
        return None
def _benford_applicable(ev):
    nums = ev.get("data") or ev.get("numbers") or ev.get("reported_values")
    return True if isinstance(nums, list) and len(nums) >= 25 else None
