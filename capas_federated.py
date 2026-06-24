# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""CAPAS — federated survive-refutation ledger: all five structural lenses, integrated.

Each lens is LANDED TO STRUCTURE (no quantum vibes — the content is Beta-credence +
independence-grouping; the physics words are intuition pumps, named as such):

  EPISTEMIC (corroboration-by-survival)      -> outcomes are survival against challenge.
  MATERIALIST (distribute verification)      -> K resolvers, and only INDEPENDENT groups count.
  ENTANGLEMENT (collusion = non-separable)   -> resolvers sharing a group are correlated; we
                                                count independent GROUPS once (consilience), so
                                                colluding votes don't multiply — decohered.
  SUPERPOSITION (don't collapse early)        -> an open claim carries a Beta survival CREDENCE;
                                                it COLLAPSES to survived/refuted only when
                                                INDEPENDENT agreement crosses a threshold.
  NON-LOCALITY (global constraint)            -> standing is over the whole ledger (the braid).
  TRIALECTIC (feed-forward)                   -> standing weights the next admission (capas_ledger).
  COMPLEMENTARITY (identity trilemma)         -> identity_tradeoff() makes the unavoidable
                                                sacrifice explicit (a design-space relation, not
                                                a Heisenberg bound).

HONEST RESIDUAL (the field's, only made costlier): if colluders are genuinely INDEPENDENT
(Sybil across real groups), federation still breaks — independence is supplied, not proven.
"""
from __future__ import annotations

from typing import Any


def resolve_federated(claim_id: str, resolver_votes: list[dict[str, Any]],
                      min_independent: int = 2) -> dict[str, Any]:
    """Resolve a claim by K resolvers, counting only INDEPENDENT groups. resolver_votes:
    [{verdict:'survived'|'refuted', group}]. Correlated (same-group) votes count ONCE, so
    collusion must capture INDEPENDENT groups, not merely spin up identities. Below
    min_independent groups the claim stays OPEN (superposition not collapsed)."""
    surv = {v.get("group") for v in resolver_votes if v.get("verdict") == "survived" and v.get("group") is not None}
    refu = {v.get("group") for v in resolver_votes if v.get("verdict") == "refuted" and v.get("group") is not None}
    contested = surv & refu                              # a group that voted both ways is not a clean signal
    surv -= contested; refu -= contested
    s, r = len(surv), len(refu)
    total = s + r
    credence = round((s + 1) / (total + 2), 4)           # Beta survival credence (superposition, landed)
    if total < min_independent or s == r:
        outcome = "open"                                  # not enough INDEPENDENT signal -> uncollapsed
    else:
        outcome = "survived" if s > r else "refuted"
    return {
        "claim_id": claim_id, "outcome": outcome, "credence": credence,
        "independent_survived": s, "independent_refuted": r, "raw_votes": len(resolver_votes),
        "collapsed": outcome != "open",
        "anti_collusion": "votes sharing a group count once; collusion must capture INDEPENDENT groups (decoherence)",
        "residual": "if colluders are genuinely independent (Sybil across real groups) this still breaks",
    }


_TRILEMMA = {"unique", "self_sovereign", "private"}


def identity_tradeoff(keep: list[str]) -> dict[str, Any]:
    """Complementarity, landed to a design-space relation: you can hold at most TWO of
    {unique (Sybil-resistant), self_sovereign (no central authority), private}. Naming the
    sacrifice is the honest move — it is a trade-off surface, NOT an uncertainty bound."""
    keep_s = set(keep) & _TRILEMMA
    sacrificed = sorted(_TRILEMMA - keep_s)
    feasible = len(keep_s) <= 2
    return {"keep": sorted(keep_s), "sacrificed": sacrificed, "feasible": feasible,
            "note": ("at most two of {unique, self_sovereign, private} are jointly achievable "
                     "(the Decentralized Identity Trilemma); a design must name which it drops")
                    if feasible else "asking for all three is infeasible — the trilemma forbids it"}
