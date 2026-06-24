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
    ok = abs(s - total) <= tol
    return {"applies": True, "verdict": "PASS" if ok else "FLAG",
            "law": "sum(parts) = total",
            "why": (f"parts sum to the total ({s:.6g})" if ok else
                    f"parts sum to {s:.6g} != declared total {total:.6g} — conservation violated")}


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
