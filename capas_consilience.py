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
