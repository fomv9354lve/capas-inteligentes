"""CAPAS — the survive-refutation ledger (the field's #1 buildable piece, closed).

The 2024-2026 SOTA verdict: you cannot incentivize truth on declared evidence (collusion-
proof is impossible; peer-prediction is empirically weak/backfires). The one mechanism the
literature does NOT prove impossible is reputation-EARNED-BY-SURVIVING-REFUTATION. This
module closes that loop over the existing primitives:

  attest()  — bind a signed, hash-chained admissibility decision to an ATTESTER identity
              (capas_registry: tamper-evident, Ed25519). The claim enters as outcome='open'.
  resolve() — the WORLD responds: an adversarial/temporal refutation marks the entry
              'survived' or 'refuted' (the measurement that collapses the open claim).
  standing()— the attester's reputation = survival rate over RESOLVED attestations
              (capas_trust: earned, not declarable).
  admit()   — a NEW claim's provisional weight: GATE (re-derived) stands on its proof;
              ATTEST (declared) is worth only the attester's earned standing.

It does NOT make a declared claim true (no mechanism does). It makes the declaration
ACCOUNTABLE: signed against an identity, on a tamper-evident chain, weighted by a record
that can only be earned by surviving challenge — so a later refutation lands on that
identity and decays its standing. Open residuals (Sybil, collusion, cash-in) are the
field's, not solved here — only made costlier. (cf. capas-pilot-and-component-attacks,
the SOTA deep-research synthesis.)
"""
from __future__ import annotations

from typing import Any

import capas_registry
import capas_trust

_REWARD = {"ACCEPT": 1.0, "REWRITE": 0.5, "HOLD": 0.25, "REJECT": 0.0}


def attest(log: list[dict[str, Any]], certificate: dict[str, Any], attester: str,
           at: str | None = None) -> list[dict[str, Any]]:
    """Append a signed decision bound to an attester identity; outcome starts 'open'."""
    new = capas_registry.append(log, certificate, at=at)
    new[-1] = {**new[-1], "attester": attester, "outcome": "open"}
    return new


def resolve(log: list[dict[str, Any]], claim_id: str, outcome: str) -> list[dict[str, Any]]:
    """The world's measurement: mark an open claim 'survived' or 'refuted'. Returns a new log.
    Note: this re-stamps an entry, so the hash-chain must be re-verified against the ORIGINAL
    decision body, not the mutable outcome (outcome is metadata the world appends over time)."""
    assert outcome in ("survived", "refuted"), "outcome must be survived|refuted"
    out = []
    for e in log:
        if e.get("claim_id") == claim_id and e.get("outcome") == "open":
            out.append({**e, "outcome": outcome})
        else:
            out.append(dict(e))
    return out


def standing(log: list[dict[str, Any]], attester: str) -> dict[str, Any]:
    """The attester's reputation, earned by surviving refutation (capas_trust)."""
    return capas_trust.track_record(log, attester)


def admit(log: list[dict[str, Any]], certificate: dict[str, Any], attester: str,
          scope: str = "ATTEST") -> dict[str, Any]:
    """Provisional admissibility weight for a NEW claim: GATE stands on proof; ATTEST is worth
    only the attester's earned standing."""
    base = _REWARD.get(certificate.get("verdict"), 0.0)
    w = capas_trust.provisional_weight(base, attester, log, scope=scope)
    w["claim_id"] = certificate.get("claim_id")
    w["chain_intact"] = capas_registry.verify_chain(log).get("intact")
    return w
