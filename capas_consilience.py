# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""CAPAS — consilience: reach OUTSIDE the re-derivable slice by INDEPENDENT adjacency.

Re-derivation proves record↔evidence, never evidence↔reality (the GIGO residual is
irreducible — we cannot cross it). But we can SHRINK it by adjacency: surround the
unverifiable fact with INDEPENDENT verifiable constraints — the same fact reached by
a different method, a different source, a conservation law, an aggregate it must sum
into, a temporal series. Each adjacency is itself in the re-derivable slice; their
CONVERGENCE (consilience) bounds the out-of-slice reality. A fabrication must be
consistent not just with itself but with every independent adjacency — exponentially
harder per independent constraint.

The load-bearing subtlety: only INDEPENDENT adjacency reaches reality. Fabricated
data is internally consistent (high WITHIN-source adjacency) but breaks against
independent EXTERNAL constraints. So consilience counts INDEPENDENCE GROUPS, not raw
adjacencies — re-derivations of the same source do not add reality-anchoring; a
different source/method/scale/law does. (Whewell's consilience; the reason
double-entry, reconciliation and triangulation exist.)

This converts the binary GIGO residual into a GRADED fabrication-resistance: from
'pure GIGO (unconstrained)' to 'reality-anchored by consilience'. It does NOT verify
reality — it measures how tightly the verifiable web pins the reality-claim, i.e.
how much room is left in the {unknowable}. And if an independent adjacency DISAGREES,
the web itself contradicts the claim (the fabrication broke against the outside).
"""
from __future__ import annotations

from typing import Any


def consilience(claimed: float, adjacencies: list[dict[str, Any]], tol: float = 1e-6) -> dict[str, Any]:
    """Score how tightly INDEPENDENT verifiable adjacencies pin a reality-claim.

    Each adjacency: {value, group, method?, source?} where `group` is an independence
    id — adjacencies sharing a group are NOT independent of each other. An adjacency
    CORROBORATES if its implied value agrees with `claimed` within tol, else DISSENTS.
    """
    corro_groups: set = set()
    dissent_groups: set = set()
    dissent: list[dict[str, Any]] = []
    for adj in adjacencies or []:
        try:
            v = float(adj["value"])
        except (KeyError, TypeError, ValueError):
            continue
        g = adj.get("group", adj.get("source", id(adj)))
        rel = abs(v - float(claimed)) / max(abs(float(claimed)), abs(v), 1e-9)
        if rel <= tol or abs(v - float(claimed)) <= tol:
            corro_groups.add(g)
        else:
            dissent_groups.add(g)
            dissent.append({"value": v, "group": g, "via": adj.get("method") or adj.get("source")})

    resistance = len(corro_groups)                       # INDEPENDENT corroborations
    residual = round(1.0 / (1.0 + resistance), 4)        # graded GIGO residual (1.0 = pure GIGO)

    if dissent_groups:
        status = ("CONTRADICTED — an independent adjacency disagrees; the verifiable web breaks the "
                  "claim (the fabrication did not survive the outside)")
    elif resistance == 0:
        status = "PURE GIGO — no independent adjacency; consistency only, reality unconstrained"
    elif resistance == 1:
        status = "WEAKLY ANCHORED — one independent corroboration; some reality constraint"
    else:
        status = f"REALITY-ANCHORED by consilience — {resistance} independent corroborations"

    return {
        "claimed": float(claimed),
        "fabrication_resistance": resistance,            # # independent groups that corroborate
        "reality_gap_residual": residual,                # how much room is left in the {unknowable}
        "independent_corroborations": sorted(map(str, corro_groups)),
        "dissent": dissent,
        "status": status,
        "note": "INDEPENDENCE is what reaches reality: re-derivations of the same source share a group "
                "and count once; a fabrication must corrupt every independent adjacency consistently. "
                "This bounds the GIGO residual; it does not verify evidence↔reality.",
    }


def consilience_recursive(levels: list[dict[str, Any]], tol: float = 1e-6) -> dict[str, Any]:
    """Renormalize the GIGO residual: apply consilience to the residual itself, level
    by level. Each level answers the previous level's open question with its OWN
    independent adjacencies — level 0: is the fact real? level 1: are its adjacencies
    independent? level 2: is THAT independence real (separate custody / provenance)?
    The total residual is the PRODUCT of per-level residuals (the unverifiable must
    fail at every level), so it shrinks GEOMETRICALLY toward the irreducible subject
    (Löb) — never to 0. The unknown-unknown is MOVED up one level per recursion, not
    eliminated; the deepest level is the floor the subject still holds.

    levels: list of {claimed, adjacencies, question}.
    """
    per, total = [], 1.0
    for lv in levels:
        r = consilience(lv["claimed"], lv.get("adjacencies") or [], tol)
        contradicted = r["status"].startswith("CONTRADICTED")
        per.append({"question": lv.get("question"), "residual": r["reality_gap_residual"],
                    "resistance": r["fabrication_resistance"], "contradicted": contradicted})
        total *= r["reality_gap_residual"]
    floor = per[-1]["residual"] if per else 1.0
    return {
        "depth": len(levels),
        "per_level": per,
        "total_residual": round(total, 6),          # geometric product — the moved, thinned {unknowable}
        "irreducible_floor": floor,                  # the deepest open level -> the subject's remaining judgment
        "moved_to": per[-1]["question"] if per else None,
        "any_contradiction": any(p["contradicted"] for p in per),
        "note": "each level is a renormalization step (a flattener applied to the unknowable itself); "
                "the residual shrinks geometrically toward the irreducible subject but never reaches 0 — "
                "the unknown-unknown is moved up a level per recursion, not closed.",
    }


def from_braid(target: str, claimed: float, braid: Any, tol: float = 1e-6) -> dict[str, Any]:
    """Auto-gather a claim's independent adjacencies from the verified BRAID: every
    node grounding the same `target` by a DIFFERENT method is an independent
    corroboration (method = independence group). The braid IS the adjacency graph;
    consilience reads it. (braid is duck-typed — any object with a .nodes dict of
    {target, value, method}; no import, to avoid the braid<->rcc<->consilience cycle.)"""
    adjacencies = [{"value": n.get("value"), "group": n.get("method"), "source": cid}
                   for cid, n in getattr(braid, "nodes", {}).items() if n.get("target") == target]
    out = consilience(claimed, adjacencies, tol)
    out["gathered_from_braid"] = len(adjacencies)
    return out


def trialectic(levels: list[dict[str, Any]], tol: float = 1e-6) -> dict[str, Any]:
    """Trialectic (triadic, open-forward) view of the recursive renormalization: at
    each level a TRIAD — thesis (the claim/question), antithesis (the independent
    adjacencies that could refute it), synthesis (corroborated, or contradicted) —
    and the synthesis's own independence OPENS the next thesis (closes forward). The
    residual shrinks geometrically toward the subject; the triad never closes back."""
    r = consilience_recursive(levels, tol)
    triads, running = [], 1.0
    for i, lv in enumerate(levels):
        pl = r["per_level"][i]
        running *= pl["residual"]
        triads.append({
            "level": i,
            "thesis": lv.get("question") or f"claim at level {i}",
            "antithesis": f"{len(lv.get('adjacencies') or [])} independent adjacencies that could refute",
            "synthesis": ("CONTRADICTED — the web breaks it" if pl["contradicted"]
                          else f"corroborated by {pl['resistance']} independent group(s)"),
            "residual_after": round(running, 6),
        })
    return {**r, "triads": triads,
            "shape": "trialectic recursion — each triad (thesis/antithesis/synthesis) renormalizes the "
                     "residual; the synthesis opens the next thesis (open-forward, never closes back); "
                     "geometric shrink toward the subject, the floor it never crosses."}
