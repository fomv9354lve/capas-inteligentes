"""CAPAS — cross-domain INVARIANT-consistency engine (the generalization).

The quantum physics gate revealed a mechanism bigger than quantum: a claim about reality
cannot be verified against reality (the GIGO ceiling), but its DECLARED quantities must still
be MUTUALLY CONSISTENT under the laws of their domain — and that consistency is re-derivable
WITHOUT any oracle, because the laws ARE the constraint. A fabricator who declares correct
methods still has to emit numbers that jointly satisfy every invariant the domain imposes;
for rich domains that is combinatorially hard, which is exactly why GRIM/statcheck catch real
fraud. This does NOT break the GIGO ceiling (a fully self-consistent liar still passes) — it
RAISES the cost of lying to "fabricate a globally-consistent world", and it is the largest
slice of text<->reality CAPAS can check with no external oracle.

These are all the SAME mechanism in different domains:
  - accounting:  assets = liabilities + equity           (finance)
  - physics:     T2 <= 2*T1, P01 >= P10, ...              (quantum, via capas_quantum_physics)
  - statistics:  a mean of N integers is a multiple of 1/N (GRIM — catches fabricated means)
  - universal:   probabilities in [0,1]; a distribution sums to 1; parts sum to the total

Each checker is DETERMINISTIC and fail-closed: it can only FLAG (downgrade), never bless.
`audit` runs every applicable invariant over a claim's evidence and returns a combined verdict.
Wired into the core decision as a downgrade-only filter: a violation forces REJECT regardless
of claim type, so the 0-false-accept property is preserved and strengthened.
"""
from __future__ import annotations

from typing import Any, Callable

_TOL = 1e-6


def _num(x: Any) -> float | None:
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


# ---- domain invariant checkers. each returns {applies, verdict in {PASS,FLAG}, why, law} ----

def check_accounting(ev: dict[str, Any]) -> dict[str, Any]:
    """Balance-sheet identity: assets = liabilities + equity (the oldest invariant gate)."""
    acc = ev.get("accounting")
    if not isinstance(acc, dict) or not {"assets", "liabilities", "equity"} <= set(acc):
        return {"applies": False}
    a, l, e = _num(acc["assets"]), _num(acc["liabilities"]), _num(acc["equity"])
    if a is None or l is None or e is None:
        return {"applies": True, "verdict": "FLAG", "law": "assets = liabilities + equity",
                "why": "non-numeric accounting fields"}
    resid = abs(a - (l + e))
    tol = max(_TOL, 1e-3 * max(abs(a), 1.0))
    ok = resid <= tol
    return {"applies": True, "verdict": "PASS" if ok else "FLAG",
            "law": "assets = liabilities + equity",
            "why": (f"balance identity holds (residual {resid:.4g})" if ok else
                    f"balance identity VIOLATED: assets {a} != liabilities {l} + equity {e} "
                    f"(residual {resid:.4g}) — the books do not close")}


def check_quantum(ev: dict[str, Any]) -> dict[str, Any]:
    """Delegate to the physical-invariant gate when a quantum calibration/result block is present."""
    q = ev.get("quantum")
    if not isinstance(q, dict):
        return {"applies": False}
    import capas_quantum_physics
    audit = capas_quantum_physics.audit_calibration_row(q)
    ok = audit["verdict"] == "ADMISSIBLE"
    return {"applies": True, "verdict": "PASS" if ok else "FLAG",
            "law": "textbook quantum invariants (T2<=2T1, P01>=P10, CZ~RZZ, parallel readout)",
            "why": audit["note"], "detail": audit["flags"]}


def check_grim(ev: dict[str, Any]) -> dict[str, Any]:
    """GRIM: a reported mean of N integer-scale responses must be a multiple of 1/N (to the
    reported precision). Catches fabricated/typo'd means in survey/clinical data. Needs a
    `grim` block: {mean, n, decimals?, scale_min?, scale_max?}."""
    g = ev.get("grim")
    if not isinstance(g, dict) or "mean" not in g or "n" not in g:
        return {"applies": False}
    m, n = _num(g["mean"]), _num(g["n"])
    if m is None or n is None or n < 1:
        return {"applies": True, "verdict": "FLAG", "law": "mean is a multiple of 1/N",
                "why": "non-numeric or invalid GRIM inputs"}
    n = int(round(n))
    decimals = int(g.get("decimals", len(str(g["mean"]).split(".")[-1]) if "." in str(g["mean"]) else 2))
    nearest_sum = round(m * n)                       # closest achievable integer total
    reconstructed = round(nearest_sum / n, decimals) # nearest achievable mean, at reported precision
    # GRIM-consistent iff the nearest achievable mean rounds EXACTLY to the reported mean.
    consistent = abs(reconstructed - round(m, decimals)) <= _TOL
    # range check if a scale is declared
    out_of_range = False
    if "scale_min" in g and "scale_max" in g:
        smin, smax = _num(g["scale_min"]), _num(g["scale_max"])
        if smin is not None and smax is not None and not (n * smin - 0.5 <= nearest_sum <= n * smax + 0.5):
            out_of_range = True
    ok = consistent and not out_of_range
    return {"applies": True, "verdict": "PASS" if ok else "FLAG",
            "law": "GRIM: reported mean must equal k/N for integer k",
            "why": (f"mean {m} is achievable with N={n} (nearest k/N -> {reconstructed})" if ok else
                    (f"mean {m} is IMPOSSIBLE with N={n}: nearest achievable is {reconstructed} "
                     f"— inconsistent reported statistics (fabricated / wrong N / typo)"
                     if not out_of_range else
                     f"implied total {nearest_sum} is outside the declared scale range — impossible"))}


def check_probability_bounds(ev: dict[str, Any]) -> dict[str, Any]:
    """Universal: every declared probability/fraction must lie in [0,1]; a declared distribution
    must sum to 1. Needs `probabilities` (list) and/or `distribution` (dict of label->p)."""
    probs = ev.get("probabilities")
    dist = ev.get("distribution")
    if not isinstance(probs, list) and not isinstance(dist, dict):
        return {"applies": False}
    bad = []
    vals = []
    if isinstance(probs, list):
        vals += [(f"p[{i}]", _num(p)) for i, p in enumerate(probs)]
    if isinstance(dist, dict):
        vals += [(str(k), _num(v)) for k, v in dist.items()]
    for label, p in vals:
        if p is None or p < -_TOL or p > 1 + _TOL:
            bad.append(f"{label}={p}")
    dist_ok = True
    if isinstance(dist, dict):
        s = sum(_num(v) or 0.0 for v in dist.values())
        dist_ok = abs(s - 1.0) <= 1e-3
    ok = not bad and dist_ok
    return {"applies": True, "verdict": "PASS" if ok else "FLAG",
            "law": "0 <= p <= 1; distribution sums to 1",
            "why": ("all probabilities in [0,1]" + (" and distribution normalized" if isinstance(dist, dict) else "")
                    if ok else
                    f"probability bound violated: {bad or 'distribution does not sum to 1'}")}


def check_sum(ev: dict[str, Any]) -> dict[str, Any]:
    """Universal conservation: declared parts must sum to the declared total. Needs
    `parts` (list of numbers) and `total`."""
    if "parts" not in ev or "total" not in ev:
        return {"applies": False}
    parts, total = ev.get("parts"), _num(ev.get("total"))
    if not isinstance(parts, list) or total is None:
        return {"applies": False}
    s = sum(_num(x) or 0.0 for x in parts)
    tol = max(_TOL, 1e-3 * max(abs(total), 1.0))
    ok = abs(s - total) <= tol
    return {"applies": True, "verdict": "PASS" if ok else "FLAG",
            "law": "sum(parts) = total",
            "why": (f"parts sum to the total ({s:.6g})" if ok else
                    f"parts sum to {s:.6g} != declared total {total:.6g} — conservation violated")}


REGISTRY: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "accounting": check_accounting,
    "quantum": check_quantum,
    "grim": check_grim,
    "probability": check_probability_bounds,
    "sum": check_sum,
}


def audit(evidence: dict[str, Any]) -> dict[str, Any]:
    """Run every applicable domain invariant over a claim's evidence. Fail-closed: ADMISSIBLE
    only if every applicable law holds. Returns the per-law detail so the verdict is auditable.
    If no invariant applies, `applicable` is False and the engine leaves the verdict untouched."""
    ev = evidence if isinstance(evidence, dict) else {}
    results = {}
    for name, fn in REGISTRY.items():
        try:
            r = fn(ev)
        except Exception as exc:  # a checker error is itself a flag (fail-closed)
            r = {"applies": True, "verdict": "FLAG", "law": name, "why": f"invariant check errored: {exc}"}
        if r.get("applies"):
            results[name] = r
    flags = [n for n, r in results.items() if r.get("verdict") == "FLAG"]
    applicable = bool(results)
    return {
        "applicable": applicable,
        "verdict": ("FLAG" if flags else "PASS") if applicable else "N/A",
        "laws_checked": sorted(results.keys()),
        "violations": flags,
        "results": results,
        "summary": ("; ".join(results[f]["why"] for f in flags) if flags else
                    (f"all {len(results)} applicable invariant(s) hold" if applicable else
                     "no domain invariant applies to this evidence")),
    }
