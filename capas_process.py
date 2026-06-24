# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""CAPAS — process reward: verification shapes GENERATION at the state level.

How a verifier improves the generational heuristic at character/word/relevant-state
granularity. Instead of scoring only the final claim, CAPAS evaluates the learned
value function (capas_value, a cheap surrogate for the deterministic admissibility)
at EACH partial state of generation, yielding a DENSE step reward — the gain in
predicted groundability from one state to the next. The generation heuristic then
prefers the continuation that most raises groundability, so the proposer is steered
token-by-token toward claims CAPAS can actually ground (and away from fluent-but-
ungroundable continuations — hallucinations earn ~0 process reward).

This is the AlphaProof / LeanProgress / process-reward-model pattern (step-level
credit = distance-to-proof at each step), but driven by CAPAS's open-empirical
verifier rather than a closed math oracle. The value function GUIDES; the
deterministic grader still re-grades any grounded result.
"""
from __future__ import annotations

from typing import Any

import capas_value


def value_of(state: dict[str, Any], model: capas_value.ValueModel) -> float:
    """Predicted groundability of a partial generation state (a partial payload)."""
    return model.predict(state)


def process_reward(prev_state: dict[str, Any], next_state: dict[str, Any],
                   model: capas_value.ValueModel) -> float:
    """The dense per-step reward: how much this generative step raised groundability.
    A groundable addition (a cited input, raw data) earns positive reward; a fluent
    but ungroundable continuation earns ~0 — steering generation toward verifiability."""
    return round(model.predict(next_state) - model.predict(prev_state), 4)


def rank_continuations(current: dict[str, Any], candidates: list[dict[str, Any]],
                       model: capas_value.ValueModel) -> list[tuple[float, dict[str, Any]]]:
    """Rank candidate continuations by process reward — the heuristic at the
    generation step. Highest groundability-gain first. The verifier never emits the
    token; it only re-weights the proposer's options toward what it can ground."""
    return sorted(((process_reward(current, c, model), c) for c in candidates), key=lambda t: -t[0])


def trajectory(states: list[dict[str, Any]], model: capas_value.ValueModel) -> list[float]:
    """The groundability rising (or not) as a proposal is built up state by state."""
    return [round(model.predict(s), 3) for s in states]
