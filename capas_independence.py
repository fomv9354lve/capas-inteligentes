# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""CAPAS independence estimator — make the STRENGTH of a verdict legible, not just the verdict.

A gate that runs N checks does NOT impose N independent constraints: correlated checks are
theater (a fabricator pays once). This module measures how many MUTUALLY INDEPENDENT
constraints a set of checks really amounts to (M_eff) and discounts the naive joint
improbability accordingly — so a CAPAS certificate can report its own effective strength
honestly instead of overstating it.

Method (grounded in outputs/_workflow_review/INDEPENDENCE_ESTIMATOR_DESIGN.md):
  - M_eff via Li & Ji (2005) eigenvalue count, hardened against the floating-point artifact
    that inflates it near integer eigenvalues; participation ratio as a cross-check band.
  - dependence from a tetrachoric approximation for binary checks (Digby), Spearman fallback.
  - joint improbability discounted by the independence yield M_eff/N; the naive/effective
    ratio is the "theater tax".

HONEST BOUND (do not strip this): M_eff measures independence of the TESTED ASPECT, not of
RELIABILITY. A shared hidden bias — two checks that break on the same adversarial input —
is invisible here, and that is exactly where a fabricator lives. So M_eff is an OPTIMISTIC
UPPER BOUND on real independent warrant, and the GIGO floor stays: an infinite-budget
fabrication consistent across every probe remains admissible. This tightens a bound; it does
not certify truth.
"""
from __future__ import annotations

import hashlib
import json
import math
from typing import Any

try:
    import numpy as np
except Exception as exc:  # numpy is required for the eigenvalue math
    raise ImportError("capas_independence requires numpy") from exc

_INT_TOL = 1e-8


def _eigs(corr: "np.ndarray") -> "np.ndarray":
    """Eigenvalues of a symmetric correlation matrix, cleaned of tiny fp error."""
    lam = np.linalg.eigvalsh(np.asarray(corr, dtype=float))
    lam = np.abs(lam)
    # snap near-integer eigenvalues to the integer (fixes the Li&Ji frac artifact)
    lam = np.where(np.abs(lam - np.round(lam)) < _INT_TOL, np.round(lam), lam)
    lam = np.clip(lam, 0.0, None)
    return lam


def m_eff_li_ji(corr: "np.ndarray") -> float:
    """Li & Ji (2005): M_eff = sum_i [ I(lam_i >= 1) + frac(lam_i) ]. Hardened."""
    lam = _eigs(corr)
    return float(np.sum((lam >= 1).astype(float) + (lam - np.floor(lam))))


def m_eff_participation(corr: "np.ndarray") -> float:
    """Participation ratio (sum lam)^2 / sum(lam^2): N if independent, ->1 if collinear."""
    lam = _eigs(corr)
    denom = float(np.square(lam).sum())
    return float(lam.sum() ** 2 / denom) if denom > 0 else 0.0


def tetrachoric_approx(a: int, b: int, c: int, d: int) -> float:
    """Digby's closed-form tetrachoric approximation for a 2x2 table [[a,b],[c,d]]
    (with a 0.5 continuity correction). r ~ cos(pi / (1 + (ad/bc)^0.75))."""
    a, b, c, d = a + 0.5, b + 0.5, c + 0.5, d + 0.5
    odds = (a * d) / (b * c)
    return math.cos(math.pi / (1.0 + odds ** 0.75))


def dependence_matrix(check_outcomes: "np.ndarray") -> "np.ndarray":
    """Pairwise dependence among checks. Columns = checks, rows = claims.
    Binary columns -> tetrachoric approximation; otherwise Spearman-rank correlation."""
    X = np.asarray(check_outcomes, dtype=float)
    n, k = X.shape
    R = np.eye(k)
    is_binary = [set(np.unique(X[:, j])).issubset({0.0, 1.0}) for j in range(k)]
    for i in range(k):
        for j in range(i + 1, k):
            xi, xj = X[:, i], X[:, j]
            if np.var(xi) < 1e-12 or np.var(xj) < 1e-12:
                r = 0.0  # a constant check carries no independent information here
            elif is_binary[i] and is_binary[j]:
                a = int(np.sum((xi == 1) & (xj == 1)))
                b = int(np.sum((xi == 1) & (xj == 0)))
                c = int(np.sum((xi == 0) & (xj == 1)))
                d = int(np.sum((xi == 0) & (xj == 0)))
                r = tetrachoric_approx(a, b, c, d)
            else:
                ri = np.argsort(np.argsort(xi))
                rj = np.argsort(np.argsort(xj))
                r = float(np.corrcoef(ri, rj)[0, 1])
            R[i, j] = R[j, i] = float(np.nan_to_num(r))
    return R


def independence_report(check_outcomes: "np.ndarray", p_each: float = 1e-2,
                        p_values: "list[float] | None" = None) -> dict[str, Any]:
    """Full estimate. check_outcomes: rows=claims, cols=checks (0/1 or scores).
    Returns M_eff band, independence yield, dependence-discounted joint improbability,
    and the theater tax. Conservative: headline M_eff = min(Li&Ji, participation)."""
    X = np.asarray(check_outcomes, dtype=float)
    n, k = X.shape
    if k == 0:
        return {"n_checks": 0, "m_eff": 0.0, "note": "no checks"}
    if k == 1:
        R = np.array([[1.0]])
        meff_lj = meff_pr = 1.0
    else:
        R = dependence_matrix(X)
        meff_lj = m_eff_li_ji(R)
        meff_pr = m_eff_participation(R)
    m_eff = min(meff_lj, meff_pr)  # conservative headline (never overstate independence)
    yield_ = m_eff / k
    if p_values is None:
        p_values = [p_each] * k
    naive = float(sum(-math.log10(max(p, 1e-300)) for p in p_values))  # -log10 joint, indep
    effective = naive * yield_                                         # discounted by independence
    tax = naive / effective if effective > 0 else float("inf")
    return {
        "n_checks": k,
        "m_eff": round(m_eff, 3),
        "m_eff_li_ji": round(meff_lj, 3),
        "m_eff_participation": round(meff_pr, 3),
        "independence_yield": round(yield_, 3),
        "theater_checks": round(k - m_eff, 3),
        "naive_neg_log10_joint": round(naive, 2),
        "effective_neg_log10_joint": round(effective, 2),
        "theater_tax": round(tax, 2),
        "bound": "OPTIMISTIC UPPER BOUND — reliability-independence unmeasured; GIGO floor stays.",
    }


_REFERENCE_CACHE: dict[str, Any] = {}


def certificate_block(claim_type: str, reference_path: str | None = None) -> dict[str, Any] | None:
    """The per-gate independence annotation for a certificate, looked up from the reference
    table (benchmarks/generate_independence_reference.py). Returns None if the gate has no
    reference estimate. This is a per-GATE property (from the named corpus), NOT a per-claim
    measurement, and an OPTIMISTIC UPPER BOUND — reliability-independence is unmeasured."""
    import os

    if reference_path is None:
        reference_path = os.path.join(os.path.dirname(__file__), "outputs", "independence_reference.json")
    doc = _REFERENCE_CACHE.get(reference_path)
    if doc is None:
        try:
            with open(reference_path, encoding="utf-8") as fh:
                doc = json.load(fh)
        except (OSError, ValueError):
            return None
        _REFERENCE_CACHE[reference_path] = doc
    gate = (doc.get("gates") or {}).get(claim_type)
    if not gate:
        return None
    return {
        "m_eff": gate["m_eff"],
        "n_checks": gate["n_checks"],
        "independence_yield": gate["independence_yield"],
        "theater_tax": gate["theater_tax"],
        "reference_corpus": doc.get("reference_corpus"),
        "reference_sha256": doc.get("content_sha256"),
        "bound": doc.get("bound"),
    }


def augment_certificate(gate_result: dict[str, Any], check_outcomes: "np.ndarray",
                        p_each: float = 1e-2, p_values: "list[float] | None" = None) -> dict[str, Any]:
    """Attach an independence block to a CAPAS verdict + a re-derivable audit hash over it."""
    rep = independence_report(check_outcomes, p_each=p_each, p_values=p_values)
    payload = json.dumps({"verdict": gate_result.get("verdict"), "independence": rep}, sort_keys=True)
    rep["independence_audit_hash"] = "sha256:" + hashlib.sha256(payload.encode()).hexdigest()[:24]
    out = dict(gate_result)
    out["independence"] = rep
    return out


if __name__ == "__main__":
    # sanity: independent -> M_eff=N tax 1x ; perfectly correlated -> M_eff=1 tax = N
    import numpy as _np
    indep = _np.array([[1, 0, 1, 0, 1, 0], [0, 1, 0, 1, 0, 1], [1, 1, 0, 0, 1, 1],
                       [0, 0, 1, 1, 0, 0], [1, 0, 0, 1, 1, 0], [0, 1, 1, 0, 0, 1]], float)
    same = _np.tile(_np.array([[1], [0], [1], [0], [1], [1]], float), (1, 6))
    print("independent-ish:", independence_report(indep))
    print("collinear (theater):", independence_report(same))
