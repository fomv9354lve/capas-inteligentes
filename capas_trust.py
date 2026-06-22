"""CAPAS — how the human actually works: trust-with-accountability, not verification.

A declaration ('confounders were controlled') cannot be re-derived from text. A human
reviewer does not verify it — they (a) weight it by the source's TRACK RECORD, (b) record
it against the source's IDENTITY so a later refutation has a target, and (c) defer the
truth-question to an adversarial, temporal process (replication, audit). This module
mechanizes that: an attester's reputation is EARNED by past claims that SURVIVED refutation
and LOST by claims that were REFUTED — it cannot be declared, only accumulated against
reality. A new declaration's provisional weight is its gate-reward DISCOUNTED by the
attester's track record, so 'gaming by declaring true' buys almost nothing from an unproven
identity, and a refuted attester's future declarations are discounted hard.

This does NOT eliminate fraud (no human system does). It raises its cost and makes it
eventually-attributable — an EQUILIBRIUM, computed over the tamper-evident registry. Honest
residual: Sybil identities (spin up a fresh one) and cash-in (build reputation on easy
claims, spend it on one big lie) — humans counter these with identity cost (institution,
real name) and consequence-magnitude; both are out of scope here and named, not hidden.

Outcomes come from the world (capas_discovery.ingest_world_response): each resolved
registry entry carries outcome in {'survived','refuted','open'}.
"""
from __future__ import annotations

from typing import Any


def track_record(registry_log: list[dict[str, Any]], attester: str) -> dict[str, Any]:
    """Reputation from the registry: a Beta-smoothed survival rate over this attester's
    RESOLVED attestations. Earned against reality, not declarable."""
    survived = refuted = open_ = 0
    for e in registry_log:
        if e.get("attester") != attester:
            continue
        o = e.get("outcome", "open")
        if o == "survived": survived += 1
        elif o == "refuted": refuted += 1
        else: open_ += 1
    resolved = survived + refuted
    trust = (survived + 1) / (resolved + 2)          # Laplace prior: unknown attester -> 0.5
    return {"attester": attester, "survived": survived, "refuted": refuted, "open": open_,
            "resolved": resolved, "trust": round(trust, 4),
            "note": "trust is earned by surviving refutation, lost by being refuted; it cannot be declared"}


def provisional_weight(gate_reward: float, attester: str, registry_log: list[dict[str, Any]],
                       scope: str = "ATTEST") -> dict[str, Any]:
    """A declaration's provisional admissibility = gate reward DISCOUNTED by the attester's
    track record. A GATE (re-derived) result is NOT discounted — it stands on its own proof;
    an ATTEST (declared) result is only worth the identity's earned trust."""
    tr = track_record(registry_log, attester)
    if scope == "GATE":
        weight = gate_reward                          # re-derived -> trust-independent
        basis = "GATE: re-derived, stands on its own proof (track record not applied)"
    else:
        weight = round(gate_reward * tr["trust"], 4)  # ATTEST: declaration worth only the earned trust
        basis = (f"ATTEST: declaration discounted by track record "
                 f"({tr['survived']} survived / {tr['refuted']} refuted -> trust {tr['trust']})")
    return {"attester": attester, "scope": scope, "gate_reward": gate_reward,
            "provisional_weight": weight, "track_record": tr, "basis": basis}
