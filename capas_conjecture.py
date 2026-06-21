"""CAPAS — conjecture bridge compiler (Lakatos mechanized).

A coherent-but-unproven claim must NOT be rejected for the absence of proof — it
must be SCAFFOLDED. Given a conjecture, this compiles the minimal bridge: the
ordered set of checkable obligations whose closing would ground it, each tagged
with the concrete action that closes it and whether that action terminates at a
LEAF (CAPAS can then re-derive it) or at the SUBJECT (only a human attestation /
a cryptographic or quantum proof can close it — the Löbian remainder).

It does NOT decide truth; it returns the *program to verification* — "here is
exactly what you would need to show", graded by bridge length and viability. This
is the move that keeps the deterministic engine from killing imagination: REJECT
is reserved for refutation (contradiction with a grounded invariant); everything
coherent-but-unproven gets a compiled bridge, never a rejection.

Depth-1 over CAPAS's own obligation vocabulary (the immediate planks + their
closing actions); deeper multi-hop lemma chains grow as the verified substrate
grows (see the closed loop). Built on capas_admissibility.
"""
from __future__ import annotations

from typing import Any

import capas_admissibility

# obligation status -> (concrete action that closes it, terminal kind)
#   leaf    = once supplied/fixed, CAPAS re-derives it deterministically
#   subject = only the human subject (attestation) or a crypto/quantum proof closes it
_CLOSE = {
    "NOT_SUPPLIED": ("supply the raw data (e.g. group_a/group_b) so the statistic re-computes", "leaf"),
    "MISSING_COMPONENTS": ("supply the missing line items / XBRL concepts for the ratio", "leaf"),
    "NO_FACTS": ("supply a parseable filing instance", "leaf"),
    "ARELLE_UNAVAILABLE": ("install the XBRL backend (arelle) to extract the filing", "leaf"),
    "NO_SEED": ("record the stochastic seed so the run is reproducible", "leaf"),
    "UNJUSTIFIED_BAND": ("attach a recognized tolerance_basis (instrument/method/regulatory)", "leaf"),
    "MALFORMED": ("repair the malformed field / formula", "leaf"),
    "UNKNOWN_RATIO": ("register the ratio's formula + components", "leaf"),
    "UNKNOWN_IDENTITY": ("register the accounting identity", "leaf"),
    "UNKNOWN_QUANTITY": ("register the physical quantity's dimension", "leaf"),
    "UNKNOWN_UNIT": ("register the unit's SI dimension vector", "leaf"),
    "UNKNOWN_ALGORITHM": ("use a supported hash algorithm", "leaf"),
    "NONPOSITIVE_DENOMINATOR": ("provide a positive economic denominator or re-scope the ratio", "leaf"),
    "UNTRUSTED_VK": ("register a trusted zero-knowledge verifying key", "leaf"),
    "DISCREPANCY": ("reconcile the posted figure with the re-derived figure", "leaf"),
    "UNRESOLVED": ("supply the recognized quantity+unit", "leaf"),
    # terminate at the subject (the Löbian remainder)
    "UNBACKED": ("obtain a signed attestation / provenance (only the subject can ground this)", "subject"),
    "BEYOND_FRONTIER": ("supply a CVQC proof (LWE) or attest a real quantum computer", "subject"),
    "ABSTAIN": ("quantify the off-baseline condition, or attest it", "leaf"),
    "SEED_CONDITIONAL": ("pre-register the seed before the data, or attest seed-robustness", "subject"),
    "UNJUSTIFIED_DIVERGENCE": ("attach the signed analyst justification for the manual override", "subject"),
    "UNRESOLVED_EVIDENCE": ("resolve the supplied evidence with a recognized rung, or attest", "subject"),
}


def _key(payload: dict[str, Any]) -> str:
    c = payload.get("claim") or {}
    return str(c.get("id") or c.get("text"))


def bridge_multihop(goal: dict[str, Any], substrate: set | None = None, max_depth: int = 8,
                    _anc: frozenset | None = None, _depth: int = 0) -> dict[str, Any]:
    """Deep multi-hop bridge: decompose a goal's dependency chain bottom-up (HTN —
    decompose until every leaf is primitive), reusing the verified SUBSTRATE as a
    cross-call cache (a verified claim is a primitive leaf). Returns the minimal
    grounding chain (leaves -> goal, topologically ordered) or the irreducible
    residual (the deepest leaves only the subject can close). Guards: substrate
    reuse (tabling), explicit cycle detection (no circular dependency), depth cap.
    Mutates `substrate` so later goals reuse grounded sub-claims (the cache grows).
    """
    substrate = substrate if substrate is not None else set()
    _anc = _anc or frozenset()
    k = _key(goal)
    if k in _anc:
        return {"node": k, "status": "CYCLE", "chain": [], "residual": [{"claim": k, "why": "circular dependency"}], "reused": [], "depth": _depth}
    if k in substrate:                                   # tabling / substrate cache hit
        return {"node": k, "status": "REUSED", "chain": [], "residual": [], "reused": [k], "depth": _depth}
    if _depth > max_depth:
        return {"node": k, "status": "DEPTH_CAPPED", "chain": [], "residual": [{"claim": k, "why": "exceeds max_depth"}], "reused": [], "depth": _depth}

    ev = goal.get("evidence") or {}
    deps = ev.get("depends_on") or []
    children = [bridge_multihop(d, substrate, max_depth, _anc | {k}, _depth + 1) for d in deps]
    chain = [c for ch in children for c in ch["chain"]]
    residual = [r for ch in children for r in ch["residual"]]
    reused = [u for ch in children for u in ch["reused"]]
    depth = max([_depth] + [ch["depth"] for ch in children])

    own = {**goal, "evidence": {kk: v for kk, v in ev.items() if kk not in ("depends_on", "target", "value")}}
    own_class = capas_admissibility.admissibility(own)["class"]

    if own_class == "REFUTED":
        return {"node": k, "status": "REFUTED", "chain": chain, "residual": residual + [{"claim": k, "why": "contradicts a grounded invariant"}], "reused": reused, "depth": depth}

    deps_ok = all(ch["status"] in ("GROUNDED", "REUSED") for ch in children)
    if own_class == "VERIFIED" and deps_ok:
        substrate.add(k)                                 # the substrate grows (cache)
        return {"node": k, "status": "GROUNDED", "chain": chain + [k], "residual": residual, "reused": reused, "depth": depth}
    if not deps and own_class != "VERIFIED":             # primitive but not re-derivable -> subject
        b = bridge(own)
        return {"node": k, "status": "IRREDUCIBLE", "chain": chain,
                "residual": residual + [{"claim": k, "why": (b.get("next_step") or {}).get("action", "defer to the subject"), "terminates": "subject"}],
                "reused": reused, "depth": depth}
    return {"node": k, "status": "OPEN", "chain": chain, "residual": residual, "reused": reused, "depth": depth}


def compile_bridge(goal: dict[str, Any], substrate: set | None = None) -> dict[str, Any]:
    """Compile and summarise the multi-hop bridge for a goal."""
    r = bridge_multihop(goal, substrate)
    grounded = r["status"] in ("GROUNDED", "REUSED") and not r["residual"]
    has_cycle = any("circular" in str(x.get("why", "")) for x in r["residual"]) or r["status"] == "CYCLE"
    return {
        "target": (goal.get("claim") or {}).get("id"),
        "status": "GROUNDED — the full chain re-derives" if grounded else
                  ("REFUTED" if r["status"] == "REFUTED" else
                   ("CYCLE — circular dependency detected" if has_cycle else
                    "OPEN — residual deferred to the subject")),
        "minimal_chain": r["chain"],                    # leaves -> goal, the lemma order to ground
        "chain_length": len(r["chain"]),
        "hops": r["depth"],
        "reused_from_substrate": sorted(set(r["reused"])),
        "irreducible_residual": r["residual"],          # only the subject closes these
    }


def bridge(payload: dict[str, Any]) -> dict[str, Any]:
    """Compile the minimal bridge that would ground a conjecture."""
    adm = capas_admissibility.admissibility(payload)
    planks, residual = [], []
    for o in adm.get("next_obligations", []):
        action, kind = _CLOSE.get(o.get("status"), ("supply the recognized evidence for this rung", "leaf"))
        (planks if kind == "leaf" else residual).append(
            {"obligation": o.get("status"), "via": o.get("check"), "action": action, "terminates": kind})
    for o in adm.get("irreducible_residual", []):
        action, kind = _CLOSE.get(o.get("status"), ("defer to the subject (attestation)", "subject"))
        residual.append({"obligation": o.get("status"), "via": o.get("check"), "action": action,
                         "terminates": "subject"})

    total = len(planks) + len(residual)
    viability = len(planks) / total if total else 1.0
    if adm["class"] == "REFUTED":
        status = "REFUTED — contradicts a grounded invariant; no bridge (this is refutation, not absence of proof)"
    elif adm["class"] in ("VERIFIED",):
        status = "ALREADY GROUNDED — no bridge needed"
    elif not planks and residual:
        status = "BRIDGE ENDS AT THE SUBJECT — only attestation/a proof closes it (Löbian remainder)"
    else:
        status = "BRIDGE COMPILED — a finite program of checkable planks would ground it"

    return {
        "target": (payload.get("claim") or {}).get("text"),
        "admissibility_score": adm["score"], "class": adm["class"],
        "status": status,
        "minimal_bridge": planks,            # leaf planks: CAPAS re-derives once closed
        "residual_to_subject": residual,     # the Löbian edge: only the subject closes it
        "bridge_length": len(planks),
        "viability": round(viability, 4),
        "next_step": (planks[0] if planks else (residual[0] if residual else None)),  # highest-leverage move
        "note": "Coherent-but-unproven is scaffolded, never rejected. REJECT is reserved for refutation.",
    }
