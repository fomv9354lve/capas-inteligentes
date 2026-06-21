"""CAPAS — split-conformal coverage for the GROUNDED stratum.

Makes the RCC's "coverage α" a REAL distribution-free, finite-sample guarantee
instead of an asserted one. Split conformal prediction: given a calibration set
of nonconformity scores {s_i} from known-good re-derivations and a new score s,
the result is "covered" iff s <= q, where q is the ceil((n+1)(1-alpha))-th
smallest calibration score. Under EXCHANGEABILITY this guarantees marginal
coverage >= 1-alpha — no distributional assumptions.

The honest part (and the bridge to the {unknowable} stratum): the guarantee holds
ONLY under exchangeability. If the new instance is out-of-distribution (the
calibration set does not cover it), the guarantee VOIDS — and that void is exactly
the 'exchangeability_failure' face of the Löbian remainder: the boundary the
certifier names but cannot enter. Conformal does not paper over it; it reports it.
"""
from __future__ import annotations

import math
from typing import Any


def nonconformity(re_derived: float, declared: float, relative: bool = True) -> float:
    """Score how far a re-derived value is from the declared one (smaller = better)."""
    d = abs(float(re_derived) - float(declared))
    if relative:
        return d / max(abs(float(declared)), abs(float(re_derived)), 1e-9)
    return d


def threshold(cal_scores: list[float], alpha: float) -> float | None:
    """Split-conformal threshold q. Returns None if no calibration data; math.inf
    if the calibration set is too small to guarantee this alpha (the guarantee
    cannot be issued — itself an honest outcome)."""
    n = len(cal_scores)
    if n == 0:
        return None
    rank = math.ceil((n + 1) * (1 - alpha))
    if rank > n:
        return math.inf
    return sorted(cal_scores)[rank - 1]


def certify(score: float, cal_scores: list[float], alpha: float = 0.1,
            exchangeable: bool = True) -> dict[str, Any]:
    """Issue a distribution-free coverage statement for a re-derivation score."""
    if not exchangeable:
        return {"covered": None, "guarantee": None,
                "reason": "exchangeability_failure — the new instance is out of the calibration "
                          "distribution; no coverage guarantee can be issued (defer to {unknowable})"}
    q = threshold(cal_scores, alpha)
    if q is None:
        return {"covered": None, "guarantee": None, "reason": "no_calibration_set"}
    if q == math.inf:
        need = math.ceil((1 - alpha) / alpha)
        return {"covered": None, "guarantee": None,
                "reason": f"insufficient_calibration_for_alpha (need >= ~{need} calibration points "
                          f"for alpha={alpha}; have {len(cal_scores)})"}
    return {"covered": bool(score <= q), "threshold": round(float(q), 8), "alpha": alpha,
            "nonconformity": round(float(score), 8), "n_calibration": len(cal_scores),
            "guarantee": f"marginal coverage >= {1 - alpha:.2f} (split conformal, distribution-free)"}
