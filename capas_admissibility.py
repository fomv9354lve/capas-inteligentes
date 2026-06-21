"""CAPAS — continuous admissibility: turn the verdict into a graded REWARD.

A binary ACCEPT/REJECT cannot drive search and kills imagination (it rejects the
unproven-but-coherent). This computes a continuous distance-to-admissibility in
[0,1] from the deterministic receipt, decomposed into the three quantities the
analysis identified:

  * coherence    — does it violate a grounded invariant? (0 = refuted, 1 = consistent)
  * groundedness — fraction of the claim already re-derived / attested
  * viability    — of the ungrounded remainder, the fraction that is in-principle
                   CHECKABLE (supply data / fix a field) vs IRREDUCIBLE (needs the
                   human subject: attestation, beyond-frontier, intention)

The score RANKS: VERIFIED (1.0) > coherent-viable CONJECTURE > ATTEST-deferred >
REFUTED (0.0). A coherent viable conjecture scores ABOVE a refuted claim — so an
optimizer (or a person) is steered toward viable bridges, never away from the
unproven. `next_obligations` is the gradient: the minimal planks that, if closed,
most raise the score (distance-to-proof made actionable). This is the dense,
multi-domain VERIFIABLE REWARD that RLVR/AlphaProof-style loops lack for OPEN
empirical claims — CAPAS as the reward function of a knowledge-growth loop.
Deterministic; the verdict is unchanged, only re-expressed as a graded signal.
"""
from __future__ import annotations

from typing import Any

import capas_verify

# Check statuses bucketed by epistemic meaning.
_GROUNDED = {"VERIFIED", "RECONCILED", "ATTESTED", "ATTESTED_SURFACED", "PRECOMMITTED_SEED"}
_REFUTED = {"FAIL", "FAILED"}
# Irreducible gaps: cannot be closed by supplying data — they need the SUBJECT
# (a signed attestation, a beyond-frontier proof, a human judgement on intention).
_IRREDUCIBLE = {"BEYOND_FRONTIER", "UNBACKED", "ABSTAIN", "UNJUSTIFIED_DIVERGENCE",
                "SEED_CONDITIONAL", "UNRESOLVED_EVIDENCE"}
# Everything else non-grounded is a VIABLE gap: closeable by supplying/fixing inputs.
# (NOT_SUPPLIED, MISSING_COMPONENTS, NO_SEED, UNJUSTIFIED_BAND, MALFORMED, UNKNOWN_*,
#  NONPOSITIVE_DENOMINATOR, UNTRUSTED_VK, NO_FACTS, DISCREPANCY, UNRESOLVED, ...)


def _bucket(status: str | None) -> str:
    if status in _GROUNDED:
        return "grounded"
    if status in _REFUTED:
        return "refuted"
    if status in _IRREDUCIBLE:
        return "irreducible"
    return "viable"  # default: an unrecognised non-grounded status is treated as closeable


def admissibility(payload: dict[str, Any]) -> dict[str, Any]:
    """Continuous, decomposed admissibility of a claim — a dense verifiable reward."""
    receipt = capas_verify.verify(payload)
    checks = receipt.get("checks", []) or []
    verdict = receipt.get("verified_verdict")

    g = v = r = f = 0
    viable_obl, irreducible_obl = [], []
    for c in checks:
        b = _bucket(c.get("status"))
        if b == "grounded":
            g += 1
        elif b == "refuted":
            f += 1
        elif b == "irreducible":
            r += 1; irreducible_obl.append({"check": c.get("check"), "status": c.get("status")})
        else:
            v += 1; viable_obl.append({"check": c.get("check"), "status": c.get("status")})

    if f > 0:  # contradicts grounded knowledge -> inadmissible-because-refuted
        coherence, groundedness, viability, score, klass = 0.0, 0.0, 0.0, 0.0, "REFUTED"
    else:
        coherence = 1.0
        total = g + v + r
        if total == 0:  # bare claim: only the base contract ran, nothing to re-derive
            groundedness = 1.0 if verdict == "ACCEPT" else 0.0
            viability = 1.0
            score = 0.6 if verdict == "ACCEPT" else 0.15
            klass = "FORM_OK" if verdict == "ACCEPT" else "UNSUPPORTED"
        else:
            groundedness = g / total
            viability = v / (v + r) if (v + r) > 0 else 1.0
            # grounded counts full; a viable gap is half-credit (reachable); an
            # irreducible gap is quarter-credit (needs the subject).
            score = min(1.0, groundedness + (v * 0.5 + r * 0.25) / total)
            if groundedness >= 0.999:
                klass = "VERIFIED"
            elif g > 0:
                klass = "PARTIAL"
            elif v >= max(r, 1):
                klass = "CONJECTURE"      # coherent, viable, ungrounded — the good idea
            elif r > 0:
                klass = "ATTEST_DEFER"    # coherent but needs the human subject
            else:
                klass = "SPECULATION"

    return {
        "score": round(score, 4),                 # the dense reward in [0,1]
        "class": klass,                            # REFUTED|SPECULATION|ATTEST_DEFER|CONJECTURE|PARTIAL|VERIFIED|FORM_OK|UNSUPPORTED
        "components": {"coherence": coherence, "groundedness": round(groundedness, 4),
                       "viability": round(viability, 4)},
        "verdict": verdict, "scope": receipt.get("scope"),
        "next_obligations": viable_obl,            # the gradient: close these to raise the score
        "irreducible_residual": irreducible_obl,   # what only the subject can close (defer)
        "receipt_id": receipt.get("receipt_id"),
    }


def reward(payload: dict[str, Any]) -> float:
    """Thin RLVR hook: the dense verifiable reward for a proposed claim. A coherent
    viable conjecture earns real positive reward; a refuted (asserted-but-false)
    claim earns 0; full re-derivation earns 1.0. Steers a proposer toward
    verifiable novelty, not away from the unproven."""
    return admissibility(payload)["score"]
