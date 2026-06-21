"""CAPAS — the spiral: an OPEN triad that closes FORWARD (knowledge-growth loop).

Not a closed dialectic (thesis-antithesis-synthesis that closes BACKWARD into a
final unity). A spiral: each push, a proposer offers claims; the deterministic
grader (capas_admissibility) routes each by what it IS, not by whether it is
already proven:

  GROUNDED   -> accumulates into the verified SUBSTRATE (the loop's gain)
  CONJECTURE -> carried FORWARD on the FRONTIER with its compiled bridge; it
                closes forward when a later push walks the bridge (supplies the
                missing plank) and it re-derives — moving from frontier to substrate
  UNKNOWABLE -> named on the BOUNDARY and deferred to the subject (never forced)
  REFUTED    -> pruned

The triad never closes back to a synthesis; it closes FORWARD — each round the
grown substrate feeds the next proposal, so the movement resolves ahead of
itself. This is CAPAS as a system that CREATES verifiable knowledge, not only
judges it: the proposer (an LLM in its triage role) imagines, the grader grounds,
the subject holds the frontier. The verdict is never the LLM's.
"""
from __future__ import annotations

from typing import Any, Callable

import capas_admissibility
import capas_conjecture


def _key(payload: dict[str, Any]) -> str:
    c = payload.get("claim") or {}
    return str(c.get("id") or c.get("text"))


def spiral(propose: Callable[[int, list, list], list[dict[str, Any]]], rounds: int = 4) -> dict[str, Any]:
    """Run the open-forward-closing loop. `propose(round, substrate, frontier)`
    returns candidate payloads (a deterministic function for tests, or an LLM
    proposer for the live engine). Returns the trajectory + final strata."""
    substrate: dict[str, dict[str, Any]] = {}   # grounded, by key
    frontier: dict[str, dict[str, Any]] = {}     # carried conjectures, by key
    boundary: dict[str, dict[str, Any]] = {}     # named-unknowable, by key
    trajectory = []

    for r in range(rounds):
        proposals = propose(r, list(substrate.values()), list(frontier.values())) or []
        events = []
        for p in proposals:
            k = _key(p)
            adm = capas_admissibility.admissibility(p)
            cls = adm["class"]
            if cls == "REFUTED":
                frontier.pop(k, None)
                events.append(("pruned (refuted)", k))
            elif cls == "VERIFIED":
                substrate[k] = {"claim": (p.get("claim") or {}).get("text"), "score": adm["score"]}
                if frontier.pop(k, None) is not None:
                    events.append(("CLOSED FORWARD: frontier -> substrate", k))
                else:
                    events.append(("grounded", k))
            elif cls in ("CONJECTURE", "PARTIAL", "FORM_OK", "UNSUPPORTED", "SPECULATION"):
                frontier[k] = {"claim": (p.get("claim") or {}).get("text"), "score": adm["score"],
                               "bridge": capas_conjecture.bridge(p)["next_step"]}
                events.append(("carried forward (conjecture)", k))
            elif cls == "ATTEST_DEFER":
                boundary[k] = {"claim": (p.get("claim") or {}).get("text")}
                frontier.pop(k, None)
                events.append(("deferred to subject (boundary)", k))
        trajectory.append({"round": r, "substrate": len(substrate), "frontier": len(frontier),
                           "boundary": len(boundary), "events": events})

    return {
        "substrate": list(substrate.values()),        # verified knowledge gained
        "frontier": list(frontier.values()),          # live conjectures, still closing forward
        "boundary": list(boundary.values()),          # named unknowable (the subject's edge)
        "trajectory": trajectory,
        "shape": "open triad, closes forward (spiral) — never a closed synthesis",
    }
