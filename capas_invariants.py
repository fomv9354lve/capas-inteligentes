# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
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
    # Sumas de ESTIMADOS: si se declaran errores estandar, la tolerancia es k·sigma (k=4) de la
    # diferencia (sigma^2 = sum se_i^2 + se_total^2), no la contabilidad exacta. Sin ellos,
    # el chequeo sigue siendo exacto -- declarar incertidumbre es lo que la compra.
    # (Hallazgo del uso en Ginibre, 2026-10: 0.1066+0.124-0.008 vs 0.227 con se~0.005 era
    # un REJECT falso con tol fija 0.001.)
    se_parts, se_total = ev.get("parts_se"), _num(ev.get("total_se")) if "total_se" in ev else None
    k_sigma = _num(ev.get("k_sigma")) or 4.0
    if se_parts is not None or se_total is not None:
        if se_parts is None:
            se_parts = [0.0] * len(parts)
        if not isinstance(se_parts, list) or len(se_parts) != len(parts):
            return {"applies": True, "verdict": "FLAG", "law": "sum(parts) = total",
                    "why": "parts_se must be a list with one standard error per part"}
        var = sum((_num(x) or 0.0) ** 2 for x in se_parts) + ((se_total or 0.0) ** 2)
        tol = max(tol, k_sigma * var ** 0.5)
    ok = abs(s - total) <= tol
    return {"applies": True, "verdict": "PASS" if ok else "FLAG",
            "law": "sum(parts) = total",
            "tolerance": tol,
            "why": (f"parts sum to {s:.6g}, consistent with declared total {total:.6g} (tol {tol:.3g})" if ok else
                    f"parts sum to {s:.6g} != declared total {total:.6g} (|diff| {abs(s-total):.3g} > tol {tol:.3g}) — conservation violated")}


import re as _re

# --- chemistry: stoichiometric atom balance ---
def _parse_formula(formula: str) -> dict[str, int]:
    """Parse a chemical formula into element->count, handling parentheses: Ca(OH)2 -> {Ca,O2,H2}."""
    def multiply(counts, n):
        return {e: c * n for e, c in counts.items()}

    def merge(a, b):
        for e, c in b.items():
            a[e] = a.get(e, 0) + c
        return a

    tokens = _re.findall(r"([A-Z][a-z]?|\(|\)|\d+)", str(formula))
    stack = [{}]
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if t == "(":
            stack.append({})
        elif t == ")":
            grp = stack.pop()
            n = 1
            if i + 1 < len(tokens) and tokens[i + 1].isdigit():
                n = int(tokens[i + 1]); i += 1
            merge(stack[-1], multiply(grp, n))
        elif t.isdigit():
            pass  # bare leading digit handled as coefficient by caller
        else:  # element
            n = 1
            if i + 1 < len(tokens) and tokens[i + 1].isdigit():
                n = int(tokens[i + 1]); i += 1
            merge(stack[-1], {t: n})
        i += 1
    return stack[0]


def check_stoichiometry(ev: dict[str, Any]) -> dict[str, Any]:
    """Atom conservation: each element's count must match across a balanced reaction. Needs a
    `stoichiometry` block: {reactants: {formula: coeff,...}, products: {formula: coeff,...}}."""
    st = ev.get("stoichiometry")
    if not isinstance(st, dict) or "reactants" not in st or "products" not in st:
        return {"applies": False}
    def side(d):
        tot: dict[str, int] = {}
        for formula, coeff in (d or {}).items():
            atoms = _parse_formula(formula)
            for e, c in atoms.items():
                tot[e] = tot.get(e, 0) + c * float(coeff)
        return tot
    lhs, rhs = side(st["reactants"]), side(st["products"])
    elems = set(lhs) | set(rhs)
    unbalanced = {e: (lhs.get(e, 0), rhs.get(e, 0)) for e in elems
                  if abs(lhs.get(e, 0) - rhs.get(e, 0)) > 1e-9}
    ok = not unbalanced
    return {"applies": True, "verdict": "PASS" if ok else "FLAG",
            "law": "atom conservation: reactant atoms = product atoms, per element",
            "why": ("reaction is balanced (every element conserved)" if ok else
                    f"NOT balanced — element counts differ: "
                    + "; ".join(f"{e}: {l} vs {r}" for e, (l, r) in unbalanced.items()))}


# --- physics: dimensional homogeneity ---
# base SI dimensions: (M mass, L length, T time, I current, K temperature, N amount, J luminous)
_DIM = {
    "kg": (1, 0, 0, 0, 0, 0, 0), "g": (1, 0, 0, 0, 0, 0, 0), "m": (0, 1, 0, 0, 0, 0, 0),
    "s": (0, 0, 1, 0, 0, 0, 0), "A": (0, 0, 0, 1, 0, 0, 0), "K": (0, 0, 0, 0, 1, 0, 0),
    "mol": (0, 0, 0, 0, 0, 1, 0), "cd": (0, 0, 0, 0, 0, 0, 1),
    "N": (1, 1, -2, 0, 0, 0, 0), "J": (1, 2, -2, 0, 0, 0, 0), "W": (1, 2, -3, 0, 0, 0, 0),
    "Pa": (1, -1, -2, 0, 0, 0, 0), "C": (0, 0, 1, 1, 0, 0, 0), "V": (1, 2, -3, -1, 0, 0, 0),
    "Hz": (0, 0, -1, 0, 0, 0, 0), "ohm": (1, 2, -3, -2, 0, 0, 0),
}


def _dim_vector(terms: Any) -> tuple | None:
    """terms: a unit string ('N') or a dict {unit: power}. Returns the 7-vector of base dims."""
    if isinstance(terms, str):
        terms = {terms: 1}
    if not isinstance(terms, dict):
        return None
    vec = [0.0] * 7
    for unit, power in terms.items():
        base = _DIM.get(unit)
        if base is None:
            return None
        for k in range(7):
            vec[k] += base[k] * float(power)
    return tuple(vec)


def check_dimensions(ev: dict[str, Any]) -> dict[str, Any]:
    """Dimensional homogeneity: the two sides of a physical equation must have identical base
    dimensions. Needs `dimensions` block: {lhs: 'N' | {unit:power}, rhs: {'kg':1,'m':1,'s':-2}}."""
    dm = ev.get("dimensions")
    if not isinstance(dm, dict) or "lhs" not in dm or "rhs" not in dm:
        return {"applies": False}
    lhs, rhs = _dim_vector(dm["lhs"]), _dim_vector(dm["rhs"])
    if lhs is None or rhs is None:
        return {"applies": True, "verdict": "FLAG", "law": "dimensional homogeneity",
                "why": "an unknown unit was used (not in the SI base/derived table)"}
    ok = all(abs(a - b) < 1e-9 for a, b in zip(lhs, rhs))
    return {"applies": True, "verdict": "PASS" if ok else "FLAG",
            "law": "dimensional homogeneity: dim(LHS) = dim(RHS)",
            "why": ("both sides share the same base dimensions" if ok else
                    f"dimensions differ: LHS {lhs} != RHS {rhs} (M,L,T,I,K,N,J) — the equation cannot be physical")}


# --- physics/stats: physical & mathematical bounds ---
_BOUNDS = {  # name -> (low, high, reason)
    "efficiency": (0.0, 1.0, "efficiency in [0,1] (no over-unity)"),
    "correlation": (-1.0, 1.0, "Pearson r in [-1,1]"),
    "r_squared": (0.0, 1.0, "R^2 in [0,1]"),
    "probability": (0.0, 1.0, "probability in [0,1]"),
    "mole_fraction": (0.0, 1.0, "mole fraction in [0,1]"),
    "temperature_K": (0.0, float("inf"), "absolute temperature >= 0 K"),
    "speed_m_s": (0.0, 299792458.0, "speed <= c"),
    "ph": (-1.0, 15.0, "pH roughly in [-1,15] for aqueous solutions"),
    # Numerica de algebra lineal (backtest Ginibre): un numero de condicion de 9e17 vuelve la
    # tabla basura aunque el error declarado sea 0.002. Regla 4 del proyecto Ginibre.
    "cond_max": (0.0, 1e12, "matrix condition number must stay <= 1e12 for a numeric result to mean anything"),
    # RMT / Ginibre (pedido por la sesion Ginibre, 2026-10): correlaciones y fracciones son
    # fracciones. rho es un coeficiente de correlacion/solapamiento; F es una fraccion limite.
    "rho": (-1.0, 1.0, "a correlation/overlap coefficient rho lies in [-1, 1]"),
    "F": (0.0, 1.0, "the limit fraction F lies in [0, 1]"),
}


def check_physical_bounds(ev: dict[str, Any]) -> dict[str, Any]:
    """Named physical/mathematical bounds. Needs `bounds` block: {efficiency: 1.2, correlation: 0.9}."""
    b = ev.get("bounds")
    if not isinstance(b, dict):
        return {"applies": False}
    bad = []
    for name, val in b.items():
        v = _num(val)
        lim = _BOUNDS.get(name)
        if lim is None or v is None:
            continue
        lo, hi, _ = lim
        if v < lo - 1e-12 or v > hi + 1e-12:
            bad.append(f"{name}={v} outside [{lo},{hi}] ({lim[2]})")
    applicable = any(name in _BOUNDS for name in b)
    if not applicable:
        return {"applies": False}
    ok = not bad
    return {"applies": True, "verdict": "PASS" if ok else "FLAG",
            "law": "named physical/mathematical bounds",
            "why": ("all bounded quantities within range" if ok else "; ".join(bad))}


# --- mathematics: a declared root must satisfy the polynomial ---
def check_root(ev: dict[str, Any]) -> dict[str, Any]:
    """Re-derivation: a claimed root must satisfy the equation. Needs `root_check` block:
    {polynomial: [a0,a1,...,an], root: x} meaning sum(a_i * x^i) must be ~0. Pure arithmetic,
    no eval — safe."""
    rc = ev.get("root_check")
    if not isinstance(rc, dict) or "polynomial" not in rc or "root" not in rc:
        return {"applies": False}
    coeffs = rc["polynomial"]
    x = _num(rc["root"])
    if not isinstance(coeffs, list) or x is None:
        return {"applies": True, "verdict": "FLAG", "law": "claimed root satisfies the equation",
                "why": "malformed polynomial or root"}
    val = sum((_num(a) or 0.0) * (x ** i) for i, a in enumerate(coeffs))
    tol = rc.get("tol", 1e-6)
    ok = abs(val) <= tol
    return {"applies": True, "verdict": "PASS" if ok else "FLAG",
            "law": "claimed root satisfies the equation: sum(a_i x^i) = 0",
            "why": (f"x={x} satisfies the polynomial (residual {val:.2g})" if ok else
                    f"x={x} is NOT a root: the polynomial evaluates to {val:.4g}, not 0 — the claimed solution is wrong")}


def _close(a: float, b: float, tol: float = 1e-3) -> bool:
    return abs(a - b) <= tol * max(1.0, abs(a), abs(b)) or abs(a - b) <= tol


def _pf(applies, ok, law, why, **extra):
    return {"applies": applies, "verdict": "PASS" if ok else "FLAG", "law": law, "why": why, **extra}


# ===== epidemiology / biostatistics (adversarially red-teamed survivors) =====
def check_confusion_matrix(ev):
    """From declared 2x2 (TP,FP,FN,TN): every metric (Se,Sp,PPV,NPV,accuracy,prevalence) re-derives;
    cells are non-negative integers. Recompute each CLAIMED metric and flag mismatch."""
    cm = ev.get("confusion_matrix")
    if not isinstance(cm, dict) or not all(k in cm for k in ("tp", "fp", "fn", "tn")):
        return {"applies": False}
    tp, fp, fn, tn = (_num(cm[k]) for k in ("tp", "fp", "fn", "tn"))
    if None in (tp, fp, fn, tn):
        return _pf(True, False, "2x2 metric identities", "non-numeric confusion-matrix cell")
    bad = [f"{n}={v} not a non-negative integer" for n, v in (("tp", tp), ("fp", fp), ("fn", fn), ("tn", tn))
           if v < 0 or abs(v - round(v)) > 1e-9]
    N = tp + fp + fn + tn
    d = {}
    if tp + fn > 0: d["sensitivity"] = tp / (tp + fn)
    if tn + fp > 0: d["specificity"] = tn / (tn + fp)
    if tp + fp > 0: d["ppv"] = tp / (tp + fp)
    if tn + fn > 0: d["npv"] = tn / (tn + fn)
    if N > 0: d["accuracy"] = (tp + tn) / N; d["prevalence"] = (tp + fn) / N
    tol = float(cm.get("tol", 1e-3))
    for k, cv in (cm.get("claimed") or {}).items():
        cvn, dv = _num(cv), d.get(k)
        if cvn is not None and dv is not None and not _close(cvn, dv, tol):
            bad.append(f"{k}: claimed {cvn} != recomputed {round(dv, 4)} from the cells")
    return _pf(True, not bad, "2x2 metric identities (Se/Sp/PPV/NPV/accuracy/prevalence)",
               "all declared metrics re-derive from the cells" if not bad else "; ".join(bad),
               recomputed={k: round(v, 4) for k, v in d.items()})


def check_bayes_ppv(ev):
    """Base-rate fallacy gate: PPV=(Se*Prev)/(Se*Prev+(1-Sp)(1-Prev)); NPV likewise. Re-derive
    from declared Se,Sp,prevalence and flag a mismatched claimed PPV/NPV."""
    b = ev.get("bayes_ppv")
    if not isinstance(b, dict) or not all(k in b for k in ("sensitivity", "specificity", "prevalence")):
        return {"applies": False}
    se, sp, pr = (_num(b[k]) for k in ("sensitivity", "specificity", "prevalence"))
    if None in (se, sp, pr) or not (0 <= se <= 1 and 0 <= sp <= 1 and 0 <= pr <= 1):
        return _pf(True, False, "Bayes PPV/NPV identity", "Se/Sp/prevalence missing or outside [0,1]")
    tol = float(b.get("tol", 1e-3)); bad = []
    dp = se * pr + (1 - sp) * (1 - pr)
    dn = sp * (1 - pr) + (1 - se) * pr
    ppv = se * pr / dp if dp > 0 else None
    npv = sp * (1 - pr) / dn if dn > 0 else None
    if b.get("claimed_ppv") is not None and ppv is not None and not _close(_num(b["claimed_ppv"]), ppv, tol):
        bad.append(f"PPV: claimed {b['claimed_ppv']} != Bayes {round(ppv, 4)} (base-rate fallacy)")
    if b.get("claimed_npv") is not None and npv is not None and not _close(_num(b["claimed_npv"]), npv, tol):
        bad.append(f"NPV: claimed {b['claimed_npv']} != Bayes {round(npv, 4)}")
    return _pf(True, not bad, "PPV=(Se*Prev)/(Se*Prev+(1-Sp)(1-Prev))",
               f"PPV re-derives to {round(ppv, 4) if ppv is not None else None}" if not bad else "; ".join(bad))


def check_association(ev):
    """From a 2x2 cohort table (a,b,c,d): RR, OR, RD re-derive. Flag a mismatched claimed measure."""
    a = ev.get("association")
    if not isinstance(a, dict) or not all(k in a for k in ("a", "b", "c", "d")):
        return {"applies": False}
    A, B, C, D = (_num(a[k]) for k in ("a", "b", "c", "d"))
    if None in (A, B, C, D):
        return _pf(True, False, "RR/OR/RD identities", "non-numeric 2x2 cell")
    tol = float(a.get("tol", 1e-3)); bad = []
    re_, ru = (A / (A + B) if A + B else None), (C / (C + D) if C + D else None)
    rr = (re_ / ru) if (re_ is not None and ru) else None
    or_ = (A * D) / (B * C) if (B * C) else None
    rd = (re_ - ru) if (re_ is not None and ru is not None) else None
    for key, val in (("rr", rr), ("or", or_), ("rd", rd)):
        cv = a.get("claimed_" + key)
        if cv is not None and val is not None and not _close(_num(cv), val, tol):
            bad.append(f"{key.upper()}: claimed {cv} != recomputed {round(val, 4)}")
    return _pf(True, not bad, "RR/OR/RD from the 2x2 table",
               f"RR={round(rr,3) if rr else None} OR={round(or_,3) if or_ else None}" if not bad else "; ".join(bad))


def check_vaccine_efficacy(ev):
    """VE = 1 - RR over the two arms; VE <= 1 always (VE>1 needs negative cases). Flag VE>1 or a
    VE inconsistent with the declared attack rates."""
    v = ev.get("vaccine_efficacy")
    if not isinstance(v, dict) or not all(k in v for k in ("cases_vax", "n_vax", "cases_unvax", "n_unvax")):
        return {"applies": False}
    cv, nv, cu, nu = (_num(v[k]) for k in ("cases_vax", "n_vax", "cases_unvax", "n_unvax"))
    if None in (cv, nv, cu, nu) or nv <= 0 or nu <= 0:
        return _pf(True, False, "VE = 1 - RR", "missing/zero arm sizes")
    arv, aru = cv / nv, cu / nu
    ve = 1 - arv / aru if aru > 0 else None
    bad = []
    if ve is not None and ve > 1 + 1e-9:
        bad.append(f"VE={round(ve,4)} > 1 is impossible (needs negative cases)")
    if v.get("claimed_ve") is not None and ve is not None and not _close(_num(v["claimed_ve"]), ve, float(v.get("tol", 1e-3))):
        bad.append(f"claimed VE {v['claimed_ve']} != recomputed {round(ve,4)} from attack rates")
    return _pf(True, not bad, "VE = 1 - (ARV/ARU), VE<=1",
               f"VE re-derives to {round(ve,4)}" if not bad else "; ".join(bad))


def check_count_containment(ev):
    """Every numerator <= its denominator, counts non-negative; declared proportions in [0,1]."""
    c = ev.get("containment")
    if not isinstance(c, dict):
        return {"applies": False}
    bad = []
    for item in (c.get("pairs") or []):
        num, den = _num(item.get("num")), _num(item.get("den"))
        lbl = item.get("label", "num/den")
        if num is None or den is None:
            continue
        if num < 0 or den < 0:
            bad.append(f"{lbl}: negative count")
        elif num > den + 1e-9:
            bad.append(f"{lbl}: numerator {num} > denominator {den}")
    for name, val in (c.get("proportions") or {}).items():
        vv = _num(val)
        if vv is not None and (vv < -1e-9 or vv > 1 + 1e-9):
            bad.append(f"{name}={vv} outside [0,1]")
    if not (c.get("pairs") or c.get("proportions")):
        return {"applies": False}
    return _pf(True, not bad, "numerator <= denominator; proportions in [0,1]",
               "all counts contained and proportions bounded" if not bad else "; ".join(bad))


# ===== engineering =====
def check_ohms_law(ev):
    """V=I*R and P=V*I=I^2*R. Given >=2 independent of (V,I,R[,P]), re-derive and flag inconsistency."""
    o = ev.get("ohms_law")
    if not isinstance(o, dict):
        return {"applies": False}
    V, I, R, P = (_num(o.get(k)) for k in ("V", "I", "R", "P"))
    tol = float(o.get("tol", 1e-2)); bad = []
    if None not in (V, I, R) and not _close(V, I * R, tol):
        bad.append(f"V={V} != I*R={round(I*R,4)}")
    if P is not None and None not in (V, I) and not _close(P, V * I, tol):
        bad.append(f"P={P} != V*I={round(V*I,4)}")
    if P is not None and None not in (I, R) and not _close(P, I * I * R, tol):
        bad.append(f"P={P} != I^2*R={round(I*I*R,4)}")
    applicable = sum(x is not None for x in (V, I, R, P)) >= 3
    if not applicable:
        return {"applies": False}
    return _pf(True, not bad, "Ohm's law V=IR, P=VI=I^2R",
               "the declared electrical quantities are mutually consistent" if not bad else "; ".join(bad))


# ===== chemistry =====
def check_charge_balance(ev):
    """sum(coeff*charge) over reactants = over products (complement to atom balance)."""
    cb = ev.get("charge_balance")
    if not isinstance(cb, dict) or "reactants" not in cb or "products" not in cb:
        return {"applies": False}
    def side(lst):
        return sum((_num(coeff) or 0) * (_num(charge) or 0) for coeff, charge in lst)
    lhs, rhs = side(cb["reactants"]), side(cb["products"])
    ok = abs(lhs - rhs) < 1e-9
    return _pf(True, ok, "charge conservation: sum(coeff*charge) reactants = products",
               "net charge balances" if ok else f"charge NOT balanced: {lhs} (reactants) != {rhs} (products)")


def check_oxidation_states(ev):
    """sum(atom_count * oxidation_state) = species net charge (the defining identity)."""
    o = ev.get("oxidation_states")
    if not isinstance(o, dict) or "atoms" not in o or "states" not in o or "net_charge" not in o:
        return {"applies": False}
    s = sum((_num(o["atoms"].get(e)) or 0) * (_num(o["states"].get(e)) or 0) for e in o["atoms"])
    q = _num(o["net_charge"])
    ok = q is not None and abs(s - q) < 1e-9
    return _pf(True, ok, "sum(count*oxidation_state) = net charge",
               f"oxidation states sum to the net charge ({q})" if ok else
               f"sum of oxidation states {s} != declared net charge {q}")


def check_mole_mass(ev):
    """n = m / M (and N = n*N_A). Fires only when m, M, n are all declared (never invents one)."""
    mm = ev.get("mole_mass")
    if not isinstance(mm, dict) or not all(k in mm for k in ("m", "M", "n")):
        return {"applies": False}
    m, M, n = (_num(mm[k]) for k in ("m", "M", "n"))
    if None in (m, M, n) or M == 0:
        return _pf(True, False, "n = m/M", "missing or zero molar mass")
    ok = _close(n, m / M, float(mm.get("tol", 1e-2)))
    return _pf(True, ok, "n = m / M",
               f"amount {n} mol matches m/M = {round(m/M,4)}" if ok else
               f"n={n} != m/M={round(m/M,4)} — the mole/mass/amount trio is inconsistent")


# ===== mathematics =====
def check_linear_system(ev):
    """For declared Ax=b and a declared solution x, every row must satisfy A[i].x == b[i]."""
    ls = ev.get("linear_system")
    if not isinstance(ls, dict) or not all(k in ls for k in ("A", "x", "b")):
        return {"applies": False}
    A, x, b = ls["A"], ls["x"], ls["b"]
    tol = float(ls.get("tol", 1e-6)); bad = []
    try:
        for i, row in enumerate(A):
            lhs = sum((_num(row[j]) or 0) * (_num(x[j]) or 0) for j in range(len(x)))
            scale = sum(abs(_num(row[j]) or 0) * abs(_num(x[j]) or 0) for j in range(len(x))) + abs(_num(b[i]) or 0)
            if abs(lhs - (_num(b[i]) or 0)) > tol * max(1.0, scale):
                bad.append(f"row {i}: A.x={round(lhs,4)} != b={b[i]}")
    except Exception as exc:
        return _pf(True, False, "Ax=b row residuals", f"malformed system: {exc}")
    return _pf(True, not bad, "claimed solution satisfies Ax=b (every row)",
               "x satisfies every equation" if not bad else "; ".join(bad))


def check_divisibility(ev):
    """Integer identities: a|b => b mod a==0; gcd*lcm==|a*b|; declared a==q*b+r."""
    dv = ev.get("divisibility")
    if not isinstance(dv, dict) or "a" not in dv or "b" not in dv:
        return {"applies": False}
    a, b = _num(dv["a"]), _num(dv["b"])
    if a is None or b is None or a != int(a) or b != int(b):
        return _pf(True, False, "integer divisibility identities", "non-integer a or b")
    import math as _m
    a, b = int(a), int(b); bad = []
    if "divides" in dv:
        actual = (a != 0 and b % a == 0)
        if bool(dv["divides"]) != actual:
            bad.append(f"a|b claimed {dv['divides']} but b mod a = {b % a if a else 'undef'}")
    if "gcd" in dv and "lcm" in dv:
        if abs(int(_num(dv["gcd"])) * int(_num(dv["lcm"]))) != abs(a * b):
            bad.append("gcd*lcm != |a*b|")
    if "q" in dv and "r" in dv:
        q, r = int(_num(dv["q"])), int(_num(dv["r"]))
        if a != q * b + r:
            bad.append(f"a != q*b+r: {a} != {q*b+r}")
    return _pf(True, not bad, "integer divisibility / gcd-lcm / division identities",
               "integer identities hold" if not bad else "; ".join(bad))


# ===== biology =====
def check_mark_recapture(ev):
    """Lincoln-Petersen: N = M*C/R, with R<=M, R<=C, non-negative integers."""
    mr = ev.get("mark_recapture")
    if not isinstance(mr, dict) or not all(k in mr for k in ("M", "C", "R", "N")):
        return {"applies": False}
    M, C, R, N = (_num(mr[k]) for k in ("M", "C", "R", "N"))
    if None in (M, C, R, N) or R <= 0:
        return _pf(True, False, "N = M*C/R", "missing or zero recapture count")
    bad = []
    if R > M + 1e-9 or R > C + 1e-9:
        bad.append("recaptured exceeds marked or second-capture total")
    if not _close(N, M * C / R, float(mr.get("tol", 1e-2))):
        bad.append(f"N={N} != M*C/R={round(M*C/R,2)}")
    return _pf(True, not bad, "Lincoln-Petersen N = M*C/R",
               f"population estimate consistent ({round(M*C/R)})" if not bad else "; ".join(bad))


def check_hardy_weinberg(ev):
    """Genotype frequencies sum to 1; declared allele freqs re-derive (p=AA+Aa/2, q=aa+Aa/2)."""
    hw = ev.get("hardy_weinberg")
    if not isinstance(hw, dict) or not all(k in hw for k in ("AA", "Aa", "aa")):
        return {"applies": False}
    aa_, ab_, bb_ = (_num(hw[k]) for k in ("AA", "Aa", "aa"))
    if None in (aa_, ab_, bb_):
        return _pf(True, False, "Hardy-Weinberg internal consistency", "non-numeric genotype frequency")
    tol = float(hw.get("tol", 1e-3)); bad = []
    if not _close(aa_ + ab_ + bb_, 1.0, tol):
        bad.append(f"genotype freqs sum to {round(aa_+ab_+bb_,4)} != 1")
    p, q = aa_ + ab_ / 2, bb_ + ab_ / 2
    if hw.get("p") is not None and not _close(_num(hw["p"]), p, tol):
        bad.append(f"allele p: claimed {hw['p']} != {round(p,4)}")
    if hw.get("q") is not None and not _close(_num(hw["q"]), q, tol):
        bad.append(f"allele q: claimed {hw['q']} != {round(q,4)}")
    return _pf(True, not bad, "HW: genotype freqs sum to 1; p=AA+Aa/2, q=aa+Aa/2",
               "genotype/allele frequencies are internally consistent" if not bad else "; ".join(bad))


def _decimals(x: Any, default: int = 2, cap: int = 6) -> int:
    """Declared decimal places of a reported number. Scientific notation ("1.2732e-03") counts the precision of
    its shortest decimal form (-exponent = 7), not the characters after the dot (§6 C6-03 boundary, 2026-10-13:
    the old split-on-dot read 8 and FLAGGED a correctly rounded value)."""
    t = str(x).strip()
    if "e" in t.lower():
        try:
            from decimal import Decimal
            return min(cap, max(0, -Decimal(t).as_tuple().exponent))
        except Exception:
            return default
    return min(cap, len(t.split(".")[1])) if "." in t else default


def check_pvalue_consistency(ev: dict[str, Any]) -> dict[str, Any]:
    """statcheck as a law: a reported p must be the p its own test statistic implies.
    Needs a `pvalue_test` block: {stat: t|F|chi2|z|r, df1, df2?, value, op: =|<|>|<=|>=, p}.
    The p is recomputed from (stat, df, value) with scipy and compared at the reported
    precision. An equality that does not round to the recomputed p, or an inequality the
    recomputed p does not satisfy, FLAGs. This is the single most replicated fraud/error
    detector in the literature (Nuijten et al.); here it is just one more invariant."""
    b = ev.get("pvalue_test")
    if not isinstance(b, dict) or not all(k in b for k in ("stat", "df1", "value", "p")):
        return {"applies": False}
    try:
        from scipy import stats as st
    except Exception as exc:
        return {"applies": True, "verdict": "FLAG", "law": "p recomputes from its test statistic",
                "why": f"scipy unavailable: {exc}"}
    stat = str(b["stat"]).lower().replace("χ", "chi").replace("-square", "2").replace("square", "2")
    df1, df2, val, p = _num(b["df1"]), _num(b.get("df2")), _num(b["value"]), _num(b["p"])
    op = str(b.get("op", "=")).strip()
    if None in (df1, val, p) or df1 <= 0:
        return {"applies": True, "verdict": "FLAG", "law": "p recomputes from its test statistic",
                "why": "non-numeric or invalid inputs"}
    def _p_of(v: float) -> float | None:
        if stat == "t":
            return 2 * st.t.sf(abs(v), df1)
        if stat == "f":
            return st.f.sf(v, df1, df2) if (df2 and df2 > 0) else None
        if stat in ("chi2", "chi"):
            return st.chi2.sf(v, df1)
        if stat == "z":
            return 2 * st.norm.sf(abs(v))
        if stat == "r":
            if abs(v) >= 1:
                return None
            tv = v * ((df1 / (1 - v * v)) ** 0.5)
            return 2 * st.t.sf(abs(tv), df1)
        return None
    if stat not in ("t", "f", "chi2", "chi", "z", "r"):
        return {"applies": False}
    if stat == "f" and not (df2 and df2 > 0):
        return {"applies": True, "verdict": "FLAG", "law": "p recomputes from its test statistic",
                "why": "F test needs df2"}
    if stat == "r" and abs(val) >= 1:
        return {"applies": True, "verdict": "FLAG", "law": "p recomputes from its test statistic",
                "why": f"|r|={val} >= 1 is impossible"}
    # El estadistico reportado esta redondeado: t=1.98 significa t in [1.975, 1.985). El p
    # consistente es por tanto un INTERVALO (metodo statcheck), no un punto.
    dv = int(b.get("value_decimals", _decimals(b["value"], 2)))
    half = 0.5 * 10 ** (-dv)
    cands = [x for x in (_p_of(val), _p_of(val - half), _p_of(val + half)) if x is not None]
    if not cands:
        return {"applies": True, "verdict": "FLAG", "law": "p recomputes from its test statistic",
                "why": "could not recompute p"}
    pc, p_lo, p_hi = cands[0], min(cands), max(cands)
    d = int(b.get("decimals", _decimals(b["p"], 2)))
    tol = 0.5 * 10 ** (-d) + 1e-9
    # Igualdad: consistente si p recalculado REDONDEA al p reportado.
    # Desigualdad: estricta, como statcheck — "p < .05" con p recalculado .0501 es un flag.
    if op == "=":
        ok = (p_lo - tol) <= p <= (p_hi + tol)
    elif op == "<":
        ok = p_lo < p + 1e-9
    elif op == "<=":
        ok = p_lo <= p + 1e-9
    elif op == ">":
        ok = p_hi > p - 1e-9
    elif op == ">=":
        ok = p_hi >= p - 1e-9
    else:
        ok = (p_lo - tol) <= p <= (p_hi + tol)
    # Error de decision: ambos lados claramente a distinto lado de .05. Un p reportado
    # exactamente en .05 es ambiguo por construccion y no cuenta como cruce.
    crosses = (op == "=" and (p_hi < 0.05) != (p < 0.05) and (p_lo < 0.05) == (p_hi < 0.05)
               and abs(p - 0.05) > tol)
    return {"applies": True, "verdict": "PASS" if (ok and not crosses) else "FLAG",
            "law": "p recomputes from its test statistic (statcheck)",
            "recomputed_p": round(pc, 6),
            "why": (f"{stat}({df1}{', '+str(df2) if df2 else ''})={val} -> p={pc:.4g}, reported p{op}{p}: consistent" if ok and not crosses else
                    f"{stat}({df1}{', '+str(df2) if df2 else ''})={val} -> p={pc:.4g}, but reported p{op}{p}"
                    + (" — DECISION ERROR across .05" if crosses else " — inconsistent at reported precision"))}


def check_reported_percent(ev: dict[str, Any]) -> dict[str, Any]:
    """A reported percentage must equal 100*k/N at the reported precision. Catches the
    cheapest fabrication tell: a fraction and its percentage that do not agree, or k > N.
    Needs a `reported_percent` block: {k, N, pct, decimals?}."""
    b = ev.get("reported_percent")
    if not isinstance(b, dict) or not all(k in b for k in ("k", "N", "pct")):
        return {"applies": False}
    k, N, pct = _num(b["k"]), _num(b["N"]), _num(b["pct"])
    if None in (k, N, pct) or N <= 0:
        return {"applies": True, "verdict": "FLAG", "law": "percent = 100*k/N", "why": "invalid inputs"}
    if k > N:
        return {"applies": True, "verdict": "FLAG", "law": "percent = 100*k/N",
                "why": f"k={k:g} exceeds N={N:g}: impossible count"}
    calc = 100.0 * k / N
    d = int(b.get("decimals", _decimals(b["pct"], 0)))
    tol = 0.5 * 10 ** (-d) + 1e-9
    # Dos convenciones de reporte coexisten: redondeo (28.57 -> 29) y truncamiento
    # (28.57 -> 28). Ambas son licitas; lo que se marca es un valor que no sale por ninguna.
    import math
    scale = 10 ** d
    truncated = math.floor(calc * scale + 1e-9) / scale
    ok = abs(calc - pct) <= tol or abs(truncated - pct) <= 1e-9
    return {"applies": True, "verdict": "PASS" if ok else "FLAG", "law": "percent = 100*k/N",
            "why": (f"{k:g}/{N:g} = {calc:.{d+1}f}% matches reported {pct}%" if ok else
                    f"{k:g}/{N:g} = {calc:.{d+1}f}% but reported {pct}% — inconsistent")}


# --- RMT / inverse-Ginibre closed-form identities (spec + 10-digit cases: Ginibre session, 2026-10-12) ---
# These are COHERENCE checks between declared closed-form quantities, not "the echo law": the
# u/(1-xu) shape is nearly a rewriting (almost any law fits it by choosing u), so its content as a
# physical law is nil -- but as an algebraic identity between a declared A and a declared C it is
# exact, and a pair that does not agree is caught. Exact identities: relative tol 1e-9. An
# ESTIMATED quantity must declare its standard error: FLAG only beyond 4*SE, and with no SE the
# verdict is HOLD (cannot judge), never a flag.
_RMT_REL = 1e-9
_RMT_K = 4.0


def _rmt_compare(name: str, declared: Any, formula: float, se: float | None,
                 exact: bool) -> tuple[str, str]:
    """-> (verdict, why) for one declared-vs-formula comparison.

    `declared` may be the raw value (float or string) so its reported precision can be read:
    a C declared as 0.48634 is a 5-digit statement, and half a unit in its last digit is the
    honest tolerance (Ginibre corpus finding, 2026-10-13: 1e-9 flagged correctly rounded
    values). Exactness still applies beyond that: 0.48700 against 0.486342 flags."""
    raw = declared
    declared = _num(declared)
    if declared is None:
        return "PASS", f"{name} not declared"
    if exact:
        d = _decimals(raw, default=12, cap=40)   # cap by magnitude, not by 15: 4.0528482e-10 has 17 decimal places
        tol = max(_RMT_REL * max(abs(formula), 1e-12), 0.5 * 10 ** (-d))
        ok = abs(declared - formula) <= tol
        return ("PASS" if ok else "FLAG",
                f"{name}: declared {declared:.10g} vs identity {formula:.10g}" + ("" if ok else " — exact identity violated"))
    if se is None:
        return "HOLD", f"{name} is a measured quantity but no standard error was declared — cannot judge"
    z = abs(declared - formula) / se if se > 0 else float("inf")
    ok = z <= _RMT_K
    return ("PASS" if ok else "FLAG",
            f"{name}: declared {declared:.10g} ± {se:.3g} vs law {formula:.10g} (z = {z:.1f})" + ("" if ok else f" — beyond {_RMT_K:g}·SE"))


def _rmt_combine(parts: list[tuple[str, str]], law: str) -> dict[str, Any]:
    verdicts = [v for v, _ in parts]
    verdict = "FLAG" if "FLAG" in verdicts else ("HOLD" if "HOLD" in verdicts else "PASS")
    return {"applies": True, "verdict": verdict, "law": law, "why": "; ".join(w for _, w in parts)}


def check_rmt_closed_form(ev: dict[str, Any]) -> dict[str, Any]:
    """C(x,d) and C(x,d,tau): with u = x + 2(1-x)d^2 (tau absent) or u = x + 2(1-x)d^2/((1+tau)(1+tau x)),
    A = 1/(1 - x u) and C = (4/pi^2) u/(1 - x u). Declared A and/or C must satisfy both exactly.
    Needs `rmt_closed_form`: {x, d, tau?, A?, C?}. Domain: x in (0,1), d in [0,1) (and d < 1+tau,
    |tau| < 1 when tau given), and 1 - x u > 0."""
    b = ev.get("rmt_closed_form")
    if not isinstance(b, dict) or "x" not in b or "d" not in b:
        return {"applies": False}
    import math
    x, d, tau = _num(b["x"]), _num(b["d"]), (_num(b["tau"]) if "tau" in b else None)
    law = "RMT closed form: A = 1/(1-xu), C = (4/pi^2) u/(1-xu)"
    if x is None or d is None or not (0 < x < 1) or d < 0:
        return {"applies": True, "verdict": "FLAG", "law": law, "why": f"domain: x must be in (0,1) and d >= 0 (got x={x}, d={d})"}
    if tau is None:
        if d >= 1:
            return {"applies": True, "verdict": "FLAG", "law": law, "why": f"domain: d must be < 1 (got {d})"}
        u = x + 2 * (1 - x) * d * d
    else:
        if not (abs(tau) < 1) or d >= 1 + tau:
            return {"applies": True, "verdict": "FLAG", "law": law, "why": f"domain: need |tau| < 1 and d < 1 + tau (got d={d}, tau={tau})"}
        u = x + 2 * (1 - x) * d * d / ((1 + tau) * (1 + tau * x))
    if 1 - x * u <= 0:
        return {"applies": True, "verdict": "FLAG", "law": law, "why": f"domain: 1 - x·u must be > 0 (x·u = {x*u:.6g})"}
    A = 1 / (1 - x * u)
    C = (4 / math.pi ** 2) * u / (1 - x * u)
    parts = [_rmt_compare("A", b.get("A"), A, None, True),
             _rmt_compare("C", b.get("C"), C, None, True)]
    out = _rmt_combine(parts, law); out["u"] = u; out["A_formula"] = A; out["C_formula"] = C
    return out


def check_rmt_F(ev: dict[str, Any]) -> dict[str, Any]:
    """F(a,b,gamma): rho = a(1-l)/(1 - a b l) with l = 1/gamma; F = ((2/pi) asin rho)^2.
    Invariants: 0 <= rho < 1, F in [0,1), and declared rho / F coherent with (a,b,gamma).
    Needs `rmt_F`: {a, b, gamma, rho?, F?}. Domain a, b in [0,1], gamma >= 1."""
    b = ev.get("rmt_F")
    if not isinstance(b, dict) or not all(k in b for k in ("a", "b", "gamma")):
        return {"applies": False}
    import math
    a, bb, g = _num(b["a"]), _num(b["b"]), _num(b["gamma"])
    law = "RMT F: rho = a(1-1/g)/(1-ab/g), F = ((2/pi) asin rho)^2"
    if None in (a, bb, g) or not (0 <= a <= 1 and 0 <= bb <= 1 and g >= 1):
        return {"applies": True, "verdict": "FLAG", "law": law, "why": f"domain: a,b in [0,1], gamma >= 1 (got a={a}, b={bb}, gamma={g})"}
    lam = 1 / g
    rho = a * (1 - lam) / (1 - a * bb * lam)
    F = ((2 / math.pi) * math.asin(rho)) ** 2
    parts = [_rmt_compare("rho", b.get("rho"), rho, None, True),
             _rmt_compare("F", b.get("F"), F, None, True)]
    for nm, val in (("rho", _num(b.get("rho"))), ("F", _num(b.get("F")))):
        if val is not None and not (0 <= val < 1):
            parts.append(("FLAG", f"{nm}={val} outside [0,1)"))
    out = _rmt_combine(parts, law); out["rho_formula"] = rho; out["F_formula"] = F
    return out


def check_rmt_G(ev: dict[str, Any]) -> dict[str, Any]:
    """G(a,b,1) = (4/pi^2) a/(1 - a b). With a = b = x this is C(x) exactly (theorem for x in (0,1):
    proof written, AI-reviewed, no peer review). With a != b the rectangular law is MEASURED:
    a declared G must come with G_se; flag only beyond 4*SE; no SE -> HOLD.
    Needs `rmt_G`: {a, b, gamma, G, G_se?}. Only gamma == 1 is a law; other gamma -> not applicable."""
    b = ev.get("rmt_G")
    if not isinstance(b, dict) or not all(k in b for k in ("a", "b", "gamma", "G")):
        return {"applies": False}
    import math
    a, bb, g, G = _num(b["a"]), _num(b["b"]), _num(b["gamma"]), _num(b["G"])
    if None in (a, bb, g, G) or abs(g - 1) > 1e-12:
        return {"applies": False}
    law = "RMT G(a,b,1) = (4/pi^2) a/(1-ab)"
    if not (0 < a < 1 and 0 < bb < 1):
        return {"applies": True, "verdict": "FLAG", "law": law, "why": f"domain: a, b in (0,1) (got {a}, {bb})"}
    Gf = (4 / math.pi ** 2) * a / (1 - a * bb)
    exact = abs(a - bb) <= 1e-12
    se = _num(b.get("G_se")) if "G_se" in b else None
    if exact and se is not None:
        # a declared SE on an exact identity: judge by SE (a 6-sigma miss must still flag)
        v, w = _rmt_compare("G", G, Gf, se, False)
    else:
        v, w = _rmt_compare("G", G, Gf, se, exact)
    return {"applies": True, "verdict": v, "law": law, "G_formula": Gf,
            "why": w + ("" if exact else " [rectangular law: measured, not a theorem]")}


# ---------------------------------------------------------------- calibration snapshot (Atlas)
# Ley pedida por Atlas (incidente real 2026-10-13): un layout elegido sobre un snapshot de junio
# tenia dos aristas CZ degradadas x15 y x6 y un qubit con T1 = 54 us; la corrida salio 10x por
# debajo de la prediccion. Un snapshot cuyos elementos (o los del layout) rompen una ley de libro,
# quedan lejos de la distribucion del propio dispositivo, o son viejos respecto al job, NO entra
# al triage ni a la seleccion de layout. Esquema que ingiere Atlas:
#   {measured: "YYYY-MM-DD HH:MM:SS", qubits: {id: {t1_us, readout[, t2_us, t2_method, ...]}},
#    edges: {id: error_float | {cz_error, rzz_error, ...}}, [layout: {qubits: [...], edges: [...]}],
#    [job_date: ...], [thresholds: {edge_x_median, readout_x_median, t1_min_frac_median,
#                                   t1_min_us, max_age_days}]}
# Politica fijada por Osvaldo (2026-10-13): absoluta (propuesta de Atlas) + relativa, frescura <= 1 dia.
# Un dispositivo uniformemente malo lo ve la absoluta; un outlier bajo el techo absoluto lo ve la relativa.
# Cualquier valor se sobreescribe en `thresholds`; 0 desactiva un umbral absoluto.
_SNAP_DEFAULTS = {
    "edge_x_median": 5.0,        # relativa: arista con error > 5x la mediana del dispositivo -> outlier
    "readout_x_median": 5.0,     # relativa: readout > 5x la mediana -> outlier
    "t1_min_frac_median": 1 / 3, # relativa: T1 < mediana/3 -> outlier (54 us vs mediana 209 = 0.26x)
    "edge_max_abs": 1e-2,        # absoluta (Atlas): arista con error > 1e-2 -> rechazo
    "t1_min_us": 60.0,           # absoluta (Atlas): T1 < 60 us -> rechazo
    "readout_max_abs": 0.0,      # absoluta opcional de readout (0 = no aplica)
    "t2_min_frac_median": 0.0,   # T2 piso relativo (0 = apagado; Atlas propone 1/3 tras el CSV IBM 2026-10-13)
    "t2_min_us": 0.0,            # T2 piso absoluto en us (0 = apagado; Atlas propone 30)
    "max_age_days": 1.0,         # frescura por job: snapshot <= 1 dia antes del job (Osvaldo 2026-10-13, tras el lote
                                 # ciego de Atlas: "mismo dia" marco 2/2 buenas sin cazar mala alguna; IBM recalibra ~a diario).
                                 # 0 = mismo dia calendario; N>0 = ventana en dias
}


def _parse_ts(x: Any) -> float | None:
    """ISO-ish timestamp -> epoch seconds; None if unparseable (no se juzga)."""
    from datetime import datetime
    if x is None:
        return None
    if isinstance(x, (int, float)):
        return float(x)
    s = str(x).strip().replace("T", " ").replace("Z", "")
    for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(s[:26], fmt).timestamp()
        except ValueError:
            continue
    return None


def check_calibration_snapshot(ev: dict[str, Any]) -> dict[str, Any]:
    import statistics as _st
    snap = ev.get("calibration_snapshot")
    if not isinstance(snap, dict) or not (isinstance(snap.get("qubits"), dict) or isinstance(snap.get("edges"), dict)):
        return {"applies": False}
    law = "calibration_snapshot: no element outside the device distribution, no textbook violation, not stale"
    # alias que usa Atlas en sus fixtures: edge_abs -> edge_max_abs, t1_abs_us -> t1_min_us
    _alias = {"edge_abs": "edge_max_abs", "t1_abs_us": "t1_min_us", "readout_abs": "readout_max_abs"}
    th = {**_SNAP_DEFAULTS, **{_alias.get(k, k): float(v) for k, v in (snap.get("thresholds") or {}).items() if _num(v) is not None}}
    qubits = snap.get("qubits") or {}
    edges = snap.get("edges") or {}
    layout = snap.get("layout") if isinstance(snap.get("layout"), dict) else None
    sel_q = set(map(str, layout.get("qubits", []))) if layout else None
    sel_e = set(map(str, layout.get("edges", []))) if layout else None
    outliers: list[dict[str, Any]] = []
    holds: list[str] = []

    def _edge_err(v: Any) -> float | None:
        if isinstance(v, dict):
            return _num(v.get("cz_error", v.get("error", v.get("gate_error"))))
        return _num(v)

    # 1) aristas: error relativo a la mediana del dispositivo (la mediana se toma sobre TODO el
    #    dispositivo; el layout solo restringe que elementos se juzgan)
    errs = {str(k): _edge_err(v) for k, v in edges.items()}
    errs = {k: v for k, v in errs.items() if v is not None and v >= 0}
    if errs:
        med_e = _st.median(errs.values())
        for k, v in errs.items():
            if sel_e is not None and k not in sel_e:
                continue
            if med_e > 0 and v / med_e > th["edge_x_median"]:
                outliers.append({"element": k, "kind": "edge_error", "value": v,
                                 "ratio_to_median": round(v / med_e, 2), "limit": th["edge_x_median"]})
            elif th["edge_max_abs"] > 0 and v > th["edge_max_abs"]:
                outliers.append({"element": k, "kind": "edge_error_abs", "value": v, "limit_abs": th["edge_max_abs"]})

    # 2) qubits: T1 piso (relativo a la mediana y absoluto) + readout relativo a la mediana
    t1s = {str(k): _num((v or {}).get("t1_us")) for k, v in qubits.items() if isinstance(v, dict)}
    t1s = {k: v for k, v in t1s.items() if v is not None and v > 0}
    ros = {str(k): _num((v or {}).get("readout")) for k, v in qubits.items() if isinstance(v, dict)}
    ros = {k: v for k, v in ros.items() if v is not None and v >= 0}
    t2s = {str(k): _num((v or {}).get("t2_us")) for k, v in qubits.items() if isinstance(v, dict)}
    t2s = {k: v for k, v in t2s.items() if v is not None and v > 0}
    med_t2 = _st.median(t2s.values()) if t2s else None
    med_t1 = _st.median(t1s.values()) if t1s else None
    med_ro = _st.median(ros.values()) if ros else None
    for k, v in qubits.items():
        k = str(k)
        if sel_q is not None and k not in sel_q:
            continue
        if not isinstance(v, dict):
            continue
        t1 = t1s.get(k)
        if t1 is not None:
            if med_t1 and th["t1_min_frac_median"] > 0 and t1 / med_t1 < th["t1_min_frac_median"]:
                outliers.append({"element": k, "kind": "t1_low", "value": t1,
                                 "ratio_to_median": round(t1 / med_t1, 2), "limit": th["t1_min_frac_median"]})
            elif th["t1_min_us"] > 0 and t1 < th["t1_min_us"]:
                outliers.append({"element": k, "kind": "t1_low", "value": t1, "limit_us": th["t1_min_us"]})
        t2 = t2s.get(k)
        if t2 is not None:
            if med_t2 and th["t2_min_frac_median"] > 0 and t2 / med_t2 < th["t2_min_frac_median"]:
                outliers.append({"element": k, "kind": "t2_low", "value": t2,
                                 "ratio_to_median": round(t2 / med_t2, 2), "limit": th["t2_min_frac_median"]})
            elif th["t2_min_us"] > 0 and t2 < th["t2_min_us"]:
                outliers.append({"element": k, "kind": "t2_low", "value": t2, "limit_us": th["t2_min_us"]})
        ro = ros.get(k)
        if ro is not None and med_ro and ro / med_ro > th["readout_x_median"]:
            outliers.append({"element": k, "kind": "readout_high", "value": ro,
                             "ratio_to_median": round(ro / med_ro, 2), "limit": th["readout_x_median"]})
        elif ro is not None and th["readout_max_abs"] > 0 and ro > th["readout_max_abs"]:
            outliers.append({"element": k, "kind": "readout_abs", "value": ro, "limit_abs": th["readout_max_abs"]})
        # 3) leyes de libro por fila (T2 <= 2 T1, termico, piso de compuerta...) via capas_quantum_physics
        row_keys = {"t1_us", "t2_us", "p01", "p10", "readout_isolated", "readout_parallel",
                    "gate_error", "gate_time_ns", "zz_residual_hz"}
        if len(row_keys & set(v)) >= 2:
            try:
                from capas_quantum_physics import audit_calibration_row
                r = audit_calibration_row(v)
                if r.get("verdict") not in ("ADMISSIBLE", None):
                    outliers.append({"element": k, "kind": "textbook_violation",
                                     "why": r.get("summary") or r.get("why") or str(r.get("flags"))})
            except Exception as exc:  # fail-closed
                outliers.append({"element": k, "kind": "textbook_check_errored", "why": str(exc)})
    for k, v in edges.items():
        k = str(k)
        if isinstance(v, dict) and "cz_error" in v and "rzz_error" in v and (sel_e is None or k in sel_e):
            try:
                from capas_quantum_physics import audit_calibration_row
                r = audit_calibration_row(v)
                if r.get("verdict") not in ("ADMISSIBLE", None):
                    outliers.append({"element": k, "kind": "textbook_violation",
                                     "why": r.get("summary") or r.get("why") or str(r.get("flags"))})
            except Exception as exc:
                outliers.append({"element": k, "kind": "textbook_check_errored", "why": str(exc)})

    # 4) frescura: snapshot medido vs fecha del job
    stale = None
    t_meas, t_job = _parse_ts(snap.get("measured")), _parse_ts(snap.get("job_date"))
    if t_meas is not None and t_job is not None:
        from datetime import datetime as _dt
        age_days = (t_job - t_meas) / 86400.0
        cal_days = (_dt.fromtimestamp(t_job).date() - _dt.fromtimestamp(t_meas).date()).days
        if float(th["max_age_days"]).is_integer():
            # politica en dias calendario (IBM recalibra ~a diario): 0 = mismo dia, 1 = hasta el dia anterior...
            if cal_days > int(th["max_age_days"]):
                stale = round(age_days, 2)
        elif age_days > th["max_age_days"]:
            # politica fraccionaria: ventana en dias reales (p.ej. 0.5 = 12 h)
            stale = round(age_days, 2)
    elif snap.get("job_date") is not None and t_meas is None:
        holds.append("measured timestamp unparseable: cannot judge staleness")

    def _fmt(o: dict[str, Any]) -> str:
        if o["kind"] == "edge_error":
            return f"edge {o['element']} error {o['value']:.3g} = {o['ratio_to_median']}x median (> {o['limit']}x)"
        if o["kind"] == "t1_low":
            return (f"qubit {o['element']} T1 {o['value']:.4g} us = {o.get('ratio_to_median', '?')}x median "
                    f"(< {o.get('limit', o.get('limit_us'))})")
        if o["kind"] == "t2_low":
            return (f"qubit {o['element']} T2 {o['value']:.4g} us = {o.get('ratio_to_median', '?')}x median "
                    f"(< {o.get('limit', o.get('limit_us'))})")
        if o["kind"] == "edge_error_abs":
            return f"edge {o['element']} error {o['value']:.3g} > absolute limit {o['limit_abs']:.3g}"
        if o["kind"] == "readout_abs":
            return f"qubit {o['element']} readout {o['value']:.3g} > absolute limit {o['limit_abs']:.3g}"
        if o["kind"] == "readout_high":
            return f"qubit {o['element']} readout {o['value']:.3g} = {o['ratio_to_median']}x median (> {o['limit']}x)"
        return f"{o['element']}: {o['kind']} — {o.get('why')}"

    n_j = (len(sel_q) if sel_q is not None else len(qubits)) + (len(sel_e) if sel_e is not None else len(edges))
    scope = f"layout ({n_j} elements judged, medians over whole device)" if layout else f"whole snapshot ({n_j} elements)"
    extra = {"outliers": outliers, "medians": {"edge_error": med_e if errs else None, "t1_us": med_t1, "t2_us": med_t2, "readout": med_ro},
             "thresholds": th, "stale_days": stale}
    if outliers or stale is not None:
        parts = [_fmt(o) for o in outliers]
        if stale is not None:
            parts.append(f"stale: measured {stale} days before job " +
                         ("(policy: same calendar day)" if th["max_age_days"] <= 0 else f"(> {th['max_age_days']} days)"))
        return {"applies": True, "verdict": "FLAG", "law": law, "why": f"{scope}: " + "; ".join(parts), **extra}
    if holds:
        return {"applies": True, "verdict": "HOLD", "law": law, "why": f"{scope}: " + "; ".join(holds), **extra}
    return {"applies": True, "verdict": "PASS", "law": law,
            "why": f"{scope}: every element within device distribution, no textbook violation, fresh", **extra}


REGISTRY: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "accounting": check_accounting,
    "quantum": check_quantum,
    "grim": check_grim,
    "probability": check_probability_bounds,
    "sum": check_sum,
    "stoichiometry": check_stoichiometry,         # chemistry
    "charge_balance": check_charge_balance,       # chemistry
    "oxidation_states": check_oxidation_states,   # chemistry
    "mole_mass": check_mole_mass,                 # chemistry
    "dimensions": check_dimensions,               # physics
    "bounds": check_physical_bounds,              # physics / math
    "root": check_root,                           # mathematics
    "linear_system": check_linear_system,         # mathematics
    "divisibility": check_divisibility,           # mathematics
    "confusion_matrix": check_confusion_matrix,   # epidemiology / biostatistics
    "bayes_ppv": check_bayes_ppv,                 # epidemiology
    "association": check_association,             # epidemiology
    "vaccine_efficacy": check_vaccine_efficacy,   # epidemiology
    "containment": check_count_containment,       # epidemiology / biology
    "ohms_law": check_ohms_law,                   # engineering
    "mark_recapture": check_mark_recapture,       # biology
    "hardy_weinberg": check_hardy_weinberg,       # biology
    "pvalue_test": check_pvalue_consistency,
    "reported_percent": check_reported_percent,
    "rmt_closed_form": check_rmt_closed_form,
    "rmt_F": check_rmt_F,
    "rmt_G": check_rmt_G,
    "calibration_snapshot": check_calibration_snapshot,  # quantum hardware (Atlas)
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
    # HOLD: una ley que NO PUEDE juzgar (p.ej. cantidad medida sin error estandar declarado).
    # No es violacion: nunca fuerza REJECT; deja el claim en HOLD hasta que se declare lo que falta.
    holds = [n for n, r in results.items() if r.get("verdict") == "HOLD"]
    applicable = bool(results)
    verdict = ("FLAG" if flags else ("HOLD" if holds else "PASS")) if applicable else "N/A"
    return {
        "applicable": applicable,
        "verdict": verdict,
        "laws_checked": sorted(results.keys()),
        "violations": flags,
        "holds": holds,
        "results": results,
        "summary": ("; ".join(results[f]["why"] for f in flags) if flags else
                    ("; ".join(results[h]["why"] for h in holds) if holds else
                     (f"all {len(results)} applicable invariant(s) hold" if applicable else
                      "no domain invariant applies to this evidence"))),
    }
