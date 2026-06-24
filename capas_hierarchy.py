# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""CAPAS — the layered triad (capas): same triad per layer, ordered inward.

The verdict need NOT be a flat deterministic decision. It is a COMPOSITION across
LAYERS, each running the same triad (propose / ground / defer) at its own level
and in its own REGIME — generative at the bottom, deterministic at the gate,
relational in the weave, metacognitive in the monitor, apophatic at the frontier.
The same form recurs at every scale (self-similar — "as above, so below"); a claim
is "thought" by settling this hierarchy, not by a single check.

Multi-hop is realized as DEPTH: a claim may declare evidence['depends_on'] = a list
of sub-claim payloads (the bridge's lemma chain). think() grounds the dependency
DAG bottom-up (each sub-claim re-derived deterministically at the GATE layer) and
composes upward (the relational layer): the whole is GROUNDED only if its own
re-derivation passes AND every dependency is grounded; a single REFUTED sub-claim
sinks it (contradiction propagates); an UNKNOWABLE sub-claim leaves a residual the
subject must close. Determinism lives in ONE layer; the composition, the
carried-forward conjectures, and the open residual do not.
"""
from __future__ import annotations

from typing import Any

import capas_admissibility

# The regime gradient (ordered inward). Each layer runs the triad in its regime.
LAYERS = [
    {"level": 0, "name": "perception / proposal", "regime": "generative",
     "triad": "propose — imagine the decomposition (LLM / value function)"},
    {"level": 1, "name": "re-derivation / GATE", "regime": "deterministic",
     "triad": "ground — re-derive each leaf (the hard invariant; determinism lives here)"},
    {"level": 2, "name": "weave / integration", "regime": "relational",
     "triad": "compose — coherence across dependencies (the braid)"},
    {"level": 3, "name": "monitor / admissibility", "regime": "metacognitive",
     "triad": "certify — grade the certification (grounded/generated/unknowable)"},
    {"level": 4, "name": "frontier / subject", "regime": "apophatic",
     "triad": "defer — the open unknowable, handed to the subject"},
]


def _key(payload: dict[str, Any]) -> str:
    c = payload.get("claim") or {}
    return str(c.get("id") or c.get("text"))


def _compose(own: str, children: list[str]) -> str:
    classes = [own] + children
    if "REFUTED" in classes:
        return "REFUTED"                       # one contradiction sinks the whole
    if "ATTEST_DEFER" in classes:
        return "ATTEST_DEFER"                  # an unknowable sub-claim -> defer to subject
    if all(c == "VERIFIED" for c in classes):
        return "VERIFIED"                      # own + every dependency grounded
    if any(c in ("CONJECTURE", "PARTIAL", "UNSUPPORTED", "FORM_OK", "SPECULATION") for c in classes):
        return "CONJECTURE"                    # carried forward — a sub-claim still needs grounding
    return own


def think(payload: dict[str, Any], _seen: frozenset[str] | None = None, _depth: int = 0) -> dict[str, Any]:
    """Settle the layered hierarchy for a claim: ground dependencies bottom-up,
    re-derive this claim at the GATE layer, compose upward, defer the residual."""
    _seen = _seen or frozenset()
    cid = _key(payload)
    if cid in _seen:
        return {"claim": cid, "composed_class": "CYCLE", "depth": _depth, "children": []}
    _seen = _seen | {cid}

    ev = payload.get("evidence", {}) or {}
    deps = ev.get("depends_on") or []
    children = [think(d, _seen, _depth + 1) for d in deps]

    own_payload = {**payload, "evidence": {k: v for k, v in ev.items()
                                           if k not in ("depends_on", "target", "value")}}
    adm = capas_admissibility.admissibility(own_payload)
    own_class = adm["class"]
    composed = _compose(own_class, [c["composed_class"] for c in children])

    residual = [{"claim": c["claim"], "class": c["composed_class"]}
                for c in children if c["composed_class"] in ("ATTEST_DEFER", "CONJECTURE")]
    return {
        "claim": cid, "depth": _depth,
        "own_class": own_class, "own_score": adm["score"],
        "composed_class": composed,
        "regime_at_this_level": LAYERS[min(2 if children else 1, 4)]["regime"],
        "children": children,
        "residual_to_subject": [r for r in residual if r["class"] == "ATTEST_DEFER"],
        "open_conjectures": [r for r in residual if r["class"] == "CONJECTURE"],
    }


def certify_hierarchy(payload: dict[str, Any]) -> dict[str, Any]:
    """A layered certificate: the composed verdict, the regime gradient it traversed,
    the grounded sub-tree, and the open frontier. Determinism is one layer, not all."""
    tree = think(payload)

    def _flat(node, acc):
        acc.append((node["depth"], node["claim"], node["own_class"], node["composed_class"]))
        for c in node["children"]:
            _flat(c, acc)
        return acc

    flat = _flat(tree, [])
    return {
        "schema": "capas-layered-certificate-v1",
        "claim": tree["claim"],
        "composed_verdict": tree["composed_class"],
        "regime_gradient": [f"L{l['level']} {l['name']} [{l['regime']}]" for l in LAYERS],
        "layers_traversed": max(d for d, *_ in flat) + 1,
        "subtree": [{"depth": d, "claim": c, "own": o, "composed": comp} for d, c, o, comp in flat],
        "frontier": tree["residual_to_subject"],
        "open_conjectures": tree["open_conjectures"],
        "note": "The verdict is a composition across regimes (generative -> deterministic -> "
                "relational -> metacognitive -> apophatic), not a flat deterministic decision. "
                "The same triad recurs at every layer; thinking is the settling of the hierarchy.",
    }
