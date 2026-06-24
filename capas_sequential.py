# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""CAPAS — independence-weighted sequential e-value test (THE WELD).

POPPER (ICML'25) gives Type-I error control over falsification by aggregating
per-experiment evidence into a sequential e-process and rejecting the null only when
it crosses 1/alpha (Ville's inequality => P(ever falsely reject | null) <= alpha).
But that aggregation is valid only if the experiments are INDEPENDENT — POPPER, and
e-value/sequential-testing work generally, assume it. Citation-graph integrity work
(CIDRE) shows real corroboration is often CIRCULAR (same authors / method / source),
so an independence-blind product injects false confidence.

This module fuses consilience's independence grouping INTO the e-process:
  - within one independence group (dependent evidence): combine by AVERAGING — a valid
    e-value combiner for ARBITRARILY dependent e-values (Vovk & Wang), which counts
    redundant/circular corroboration ~once (matches consilience's 'count the group, not
    the re-derivations').
  - across independent groups: combine by PRODUCT — the valid e-value multiplication.
Reject the null (the conjecture SURVIVES falsification) when the running e-process
E >= 1/alpha. The weld removes exactly the inflation a naive independence-blind product
would add from same-source corroboration.

Null H0 here = "the conjecture is false/spurious". A falsification experiment whose
outcome is unlikely under H0 yields a LARGE e-value (evidence the conjecture survives).

Honest boundary (the C2 known-unknown, not hidden): independence is taken from the
SUPPLIED grouping (same as consilience / capas_falsify), NOT measured from a citation
graph. So this closes the statistical-control gap (C1) and USES independence, but the
independence MEASUREMENT (CIDRE-style) remains the open next weld. Cara 1, deterministic.
"""
from __future__ import annotations

from typing import Any


def p_to_e(p: float, kappa: float = 0.5) -> float:
    """Calibrate a p-value into a valid e-value via e = kappa * p**(kappa-1),
    kappa in (0,1). Integral over p in (0,1] is 1, so E[e | H0] <= 1 (a valid e-value).
    Small p (outcome unlikely under 'the conjecture is false') -> large e."""
    p = min(max(float(p), 1e-12), 1.0)
    k = min(max(float(kappa), 1e-6), 1.0 - 1e-6)
    return k * (p ** (k - 1.0))


def _mean(xs: list[float]) -> float:
    return sum(xs) / len(xs) if xs else 1.0


def sequential_test(experiments: list[dict[str, Any]], alpha: float = 0.05) -> dict[str, Any]:
    """Independence-weighted sequential e-test.

    experiments: list of {e_value? , p_value? , group, name?}. `group` is the
    independence id (re-use consilience / braid grouping). Either e_value or p_value
    per experiment (p_value is calibrated via p_to_e).
    Returns the independence-adjusted e-process vs the naive (blind) product, the
    reject threshold 1/alpha, and what the weld removed.
    """
    # collect e-values per independence group
    groups: dict[Any, list[float]] = {}
    naive_e: list[float] = []
    for x in experiments or []:
        if "e_value" in x and x["e_value"] is not None:
            e = float(x["e_value"])
        else:
            e = p_to_e(x.get("p_value", 1.0))
        e = max(e, 0.0)
        g = x.get("group", x.get("name", id(x)))
        groups.setdefault(g, []).append(e)
        naive_e.append(e)

    # within group: AVERAGE (valid for dependent e-values; counts the group once-ish)
    per_group = {str(g): {"combined_e": round(_mean(es), 6), "n": len(es)} for g, es in groups.items()}
    # across independent groups: PRODUCT
    E = 1.0
    for es in groups.values():
        E *= _mean(es)
    naive_E = 1.0
    for e in naive_e:
        naive_E *= e

    thresh = 1.0 / float(alpha)
    reject = E >= thresh
    naive_reject = naive_E >= thresh
    return {
        "alpha": alpha,
        "reject_threshold": round(thresh, 4),               # 1/alpha
        "e_process": round(E, 6),                            # independence-adjusted
        "reject_null": reject,                               # conjecture survives falsification @ Type-I<=alpha
        "independent_groups": len(groups),
        "experiments": len(naive_e),
        "per_group": per_group,
        "naive_e_process": round(naive_E, 6),                # independence-BLIND product (what POPPER-style does)
        "naive_reject_null": naive_reject,
        "false_confidence_removed": round(naive_E / E, 4) if E > 0 else None,  # inflation the weld stripped
        "weld": ("within-group AVERAGE (valid for dependent e-values; circular corroboration counts ~once) "
                 "x across-group PRODUCT (valid for independent groups); reject when e_process >= 1/alpha"),
        "honest_boundary": "independence is from the SUPPLIED grouping, not measured (CIDRE-style measurement "
                           "is the open next weld); valid only insofar as the grouping reflects real independence",
    }


def evalue_process(evalues: list[float], alpha: float = 0.05) -> dict[str, Any]:
    """ANYTIME-VALID sequential e-process — the POPPER-grade rigor for the weld.

    The running PRODUCT of (independent) e-values is a test martingale under the null
    (each e-value has E[e] <= 1), so by VILLE'S INEQUALITY
        P( sup_t  product_t  >= 1/alpha  |  null )  <=  alpha .
    You may therefore STOP AND REJECT the instant the process crosses 1/alpha, at ANY
    time and after ANY number of observations, with Type-I error controlled at alpha —
    no fixed sample size, no multiple-testing penalty. (Demonstrated by Monte-Carlo in
    benchmarks/demo_sequential_typeI.py: the empirical ever-cross rate under the null
    stays <= alpha.)"""
    thresh = 1.0 / float(alpha)
    running, first, trace = 1.0, None, []
    for i, e in enumerate(evalues):
        running *= max(float(e), 0.0)
        trace.append(round(running, 4))
        if first is None and running >= thresh:
            first = i
    return {
        "final_e": round(running, 6),
        "reject_threshold": round(thresh, 4),
        "crossed": first is not None,
        "first_crossing_index": first,          # stop here — valid at this stopping time
        "trace": trace,
        "guarantee": "anytime-valid: P(ever cross 1/alpha | null) <= alpha (Ville's inequality "
                     "on the e-value test martingale); reject at the first crossing, any time.",
    }


def from_consilience_levels(levels: list[dict[str, Any]], alpha: float = 0.05) -> dict[str, Any]:
    """Bridge: read a consilience-style adjacency set ([{value, group}...] under
    `adjacencies`) as falsification experiments. Each corroborating adjacency that
    matches the claim is one experiment in its independence group. Lets the same
    structure that grades GIGO drive the sequential e-test."""
    claimed = levels[0].get("claimed") if levels else None
    exps = []
    for lv in levels:
        c = lv.get("claimed", claimed)
        for adj in lv.get("adjacencies") or []:
            try:
                agree = abs(float(adj["value"]) - float(c)) <= 1e-6
            except (KeyError, TypeError, ValueError):
                continue
            # a corroborating adjacency is an experiment that FAILED to refute -> evidence
            # for the claim; encode as a modest e-value, grouped by its independence id.
            exps.append({"e_value": float(adj.get("e_value", 3.0)) if agree else 0.2,
                         "group": adj.get("group", adj.get("source")), "name": adj.get("method")})
    return sequential_test(exps, alpha)
