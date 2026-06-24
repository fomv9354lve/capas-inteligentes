# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""CAPAS — settling dynamics: the engine THINKS, not only verifies.

The research-grounded completion of the layered triad. A verifier runs bottom-up
only (detect error). THINKING settles: each pass sends a top-down prediction back
down (propose the next plank for each open conjecture — walk its bridge), grounds
what it can, and passes UP ONLY THE RESIDUAL (the unexplained part — the free-
energy / predictive-coding law: a layer never passes its work product up, only its
prediction error). The loop iterates until the residual stabilizes — relaxation to
a fixed point — and the certification layer fires ALL-OR-NONE (Dehaene ignition):
a "thought" is declared only when total residual reaches zero.

The IIT correction: clean layer separation can destroy integration, so settling is
routed through a strongly-recurrent, hard-to-partition INTEGRATION CORE — the braid
— whose mutual-coherence (correspondence/reciprocity across the whole) makes the
settled verdict IRREDUCIBLE, not a disjoint AND of independent checks. Ignition
requires residual==0 AND braid coherence (no same-target disagreement).

supply_fn(conjecture)->payload|None is the proposer walking a bridge one step
(deterministic for tests; an LLM in its triage role for the live engine). It never
decides; it only supplies the next checkable plank, which CAPAS then re-derives.
"""
from __future__ import annotations

from typing import Any, Callable

import capas_admissibility
import capas_braid
import capas_hierarchy
import capas_integration

_GROUNDED = ("VERIFIED",)


_META = ("depends_on", "target", "value")


def _is_grounded(payload: dict[str, Any]) -> bool:
    own = {**payload, "evidence": {k: v for k, v in (payload.get("evidence") or {}).items()
                                   if k not in _META}}
    return capas_admissibility.admissibility(own)["class"] in _GROUNDED


def _residual(payload: dict[str, Any]) -> int:
    """Total unexplained residual across the dependency stack (the only thing that
    propagates up): count of sub-claims not yet grounded."""
    deps = (payload.get("evidence") or {}).get("depends_on") or []
    r = 0 if _is_grounded(payload) or deps else (0 if _is_grounded(payload) else 1)
    if not deps:
        return 0 if _is_grounded(payload) else 1
    for d in deps:
        r += _residual(d)
    return r


def _advance(payload: dict[str, Any], supply: Callable[[dict], dict | None]) -> dict[str, Any]:
    """Top-down pass: for each not-yet-grounded sub-claim, let the proposer supply
    its next plank (walk the bridge one step). Returns the revised payload."""
    ev = dict(payload.get("evidence") or {})
    deps = ev.get("depends_on")
    if deps:
        ev["depends_on"] = [_advance(d, supply) for d in deps]
        return {**payload, "evidence": ev}
    if _is_grounded(payload):
        return payload
    supplied = supply(payload)
    return supplied if supplied is not None else payload


def _braid_core(payload: dict[str, Any]) -> capas_braid.Braid:
    """Integration core: weave the grounded leaves into the braid by their target.
    Leaves carry evidence['target'] and evidence['value']."""
    br = capas_braid.Braid()

    def _walk(p):
        ev = p.get("evidence") or {}
        for d in ev.get("depends_on") or []:
            _walk(d)
        if "target" in ev and "value" in ev and _is_grounded(p):
            br.add({**p, "evidence": {k: v for k, v in ev.items() if k not in _META}},
                   target=ev["target"], value=float(ev["value"]), method=(p.get("claim") or {}).get("id", "?"))
    _walk(payload)
    return br


def settle(payload: dict[str, Any], supply: Callable[[dict], dict | None],
           max_passes: int = 8) -> dict[str, Any]:
    """Run the relaxation: settle the hierarchy by iterating top-down proposal +
    bottom-up grounding until the residual stabilizes (a fixed point). Ignite
    (declare a grounded thought) only at residual==0 AND braid coherence."""
    current = payload
    trajectory = [_residual(current)]
    passes = 0
    for passes in range(1, max_passes + 1):
        current = _advance(current, supply)
        r = _residual(current)
        trajectory.append(r)
        if r == 0 or r == trajectory[-2]:        # ignition, or fixed point (stuck)
            break

    final_residual = trajectory[-1]
    core = _braid_core(current)
    faults = core.faults()
    coherent = not faults
    phi = capas_integration.integration(core)         # the irreducibility of the thought (Φ-proxy)
    tree = capas_hierarchy.think(current)
    ignited = final_residual == 0 and coherent and tree["composed_class"] == "VERIFIED"
    if ignited:
        verdict, note = "GROUNDED (ignited)", "the hierarchy settled to a coherent fixed point — a thought"
    elif final_residual == 0 and not coherent:
        verdict, note = "BRAID-INCOHERENT", "all leaves grounded but the whole does not integrate (IIT fault)"
    else:
        verdict, note = "DEFERRED (open)", "settled with residual > 0 — handed to the subject (the open frontier)"

    return {
        "schema": "capas-settled-thought-v1",
        "verdict": verdict,
        "passes": passes,                         # thought-steps
        "residual_trajectory": trajectory,        # the relaxation: residual falling (or stuck)
        "settled_residual": final_residual,
        "ignited": ignited,
        "braid_coherent": coherent, "braid_faults": faults,
        "integration_phi_proxy": phi["algebraic_connectivity"],   # λ₂: irreducibility of the thought
        "irreducible": phi["irreducible"],
        "composed_class": tree["composed_class"],
        "frontier": tree["residual_to_subject"],
        "note": note,
        "law": "residual-only upward, prediction downward, relax to fixed point, ignite all-or-none; "
               "integration core = the braid (the verdict is irreducible, not a disjoint AND).",
    }
