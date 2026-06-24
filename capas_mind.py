# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""CAPAS — the orchestrator: one cognitive loop wiring every layer.

Integrates the whole stack into a single entry point so the layers are not just
pairwise-composable but run as one coupled loop:

  GENERATE (proposer; optionally guided by the process reward) ->
  SETTLE   (capas_think: the layered hierarchy relaxes to a fixed point) ->
  INTEGRATE(the nodal braid core; Φ-proxy λ₂ = irreducibility) ->
  CERTIFY  (capas_rcc: the stratified reflexive certificate + the open frontier).

The verdict is the composition across regimes; determinism is one layer; the
subject holds the frontier. cognize() returns one unified certificate: the
settled thought, its integration, the stratified certificate, and what is deferred
to the subject — the engine thinking a claim through, end to end.
"""
from __future__ import annotations

from typing import Any, Callable

import capas_admissibility
import capas_process
import capas_rcc
import capas_think
import capas_value

MATURITY = "research"   # Cara 2 — research-grade, NOT product-verified (see CARA2_BOUNDARY.md)


def cognize(top_payload: dict[str, Any],
            supply: Callable[[dict], dict | None],
            max_passes: int = 8) -> dict[str, Any]:
    """Run the full loop on a claim (with its dependency conjectures) and return a
    unified certificate."""
    # 1-2-3: settle the hierarchy (top-down proposal + bottom-up grounding), with the
    # nodal braid as the integration core and the Φ-proxy reported.
    thought = capas_think.settle(top_payload, supply, max_passes=max_passes)

    # 4: certify the top claim's OWN re-derivation as a reflexive certificate (strata
    # + named frontier + Löbian/parallax self-bar).
    own = {**top_payload, "evidence": {k: v for k, v in (top_payload.get("evidence") or {}).items()
                                       if k not in ("depends_on", "target", "value")}}
    cert = capas_rcc.rcc(own)

    verdict = thought["verdict"]
    return {
        "schema": "capas-cognition-v1",
        "tier": "research-grade (Cara 2) — not product-verified; the verdict's GATE layer is "
                "deterministic, the rest is research scaffolding",
        "claim": (top_payload.get("claim") or {}).get("id"),
        "verdict": verdict,
        "thought": {k: thought[k] for k in ("passes", "residual_trajectory", "settled_residual",
                                            "ignited", "braid_coherent", "integration_phi_proxy",
                                            "irreducible", "frontier")},
        "certificate": {k: cert[k] for k in ("headline", "strata", "boundary", "loebian_clause",
                                             "parallax_self_bar", "certificate_id", "engine_digest")
                        if k in cert},
        "frontier_to_subject": thought["frontier"],
        "decision_path": "deterministic at the GATE layer; generative below, apophatic above; no LLM in the verdict",
        "loop": "generate -> settle -> integrate (nodal Φ-core) -> certify; the subject holds the open frontier",
    }


def guided_choice(current_state: dict[str, Any], candidates: list[dict[str, Any]],
                  value_model: capas_value.ValueModel) -> dict[str, Any]:
    """The generation step, wired: rank continuations by the process reward (the
    value function's groundability gain), returning the chosen continuation. The
    verifier shapes generation; it never emits the token nor the verdict."""
    ranked = capas_process.rank_continuations(current_state, candidates, value_model)
    return {"chosen": ranked[0][1], "gain": ranked[0][0],
            "ranking": [{"gain": g} for g, _ in ranked]}


def fit_value(payloads: list[dict[str, Any]]) -> capas_value.ValueModel:
    """Self-supervised: fit the guidance value model on the engine's own grades."""
    return capas_value.ValueModel().fit(payloads)
