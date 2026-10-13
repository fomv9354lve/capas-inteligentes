# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""CAPAS RMT corpus — invariant checks for positivity-conditioned inverse-Ginibre overlap claims.

The 'laws' of this domain are the paper's own theorems + general RMT/probability bounds. Each check
is deterministic, structure-checkable from declared numbers, needs no oracle (below the GIGO floor):
it forces a claim's tabulated numbers to breed with the closed forms and identities the theory asserts.
A collision -> FLAG (an internal inconsistency), never a proof the mathematics is wrong.
"""
from __future__ import annotations
import math
from typing import Any

PI2 = math.pi**2
def C_closed(x): return (4/PI2)*x/(1-x**2)          # C(x) theorem, x in (0,1): proof written (SSRN v2), AI-reviewed, no peer review; was 'Conjecture 1'

def _pf(applies, ok, law, why):
    return {"applies": applies, "verdict": ("PASS" if ok else "FLAG") if applies else "N/A", "law": law, "why": why}

def check_probability_range(ev):
    ps = {k: v for k, v in ev.items() if k.startswith(("P_", "p_", "orth_")) and isinstance(v, (int, float))}
    if not ps: return _pf(False, True, "", "")
    bad = [f"{k}={v}" for k, v in ps.items() if not (-1e-9 <= v <= 1+1e-9)]
    return _pf(True, not bad, "every probability in [0,1]", "; ".join(bad) or "all in [0,1]")

def check_sign_bound(ev):
    if "sigma_ij" not in ev: return _pf(False, True, "", "")
    ok = abs(ev["sigma_ij"]) <= 1+1e-9
    return _pf(True, ok, "|sigma_ij| <= 1 (Thm 9a)", f"sigma_ij={ev['sigma_ij']}")

def check_orthant(ev):
    need = ("orth_pp", "orth_mm", "orth_pm", "orth_mp")
    if not all(k in ev for k in need): return _pf(False, True, "", "")
    s = sum(ev[k] for k in need); sig = 2*(ev["orth_pp"]+ev["orth_mm"])-1
    ok = abs(s-1) <= 1e-3 and (("sigma_ij" not in ev) or abs(sig-ev["sigma_ij"]) <= 1e-3)
    return _pf(True, ok, "orthants sum to 1; sigma=2(P+++P--)-1 (Thm 9b)", f"sum={s:.4f}")

def check_sphere_conservation(ev):
    if not all(k in ev for k in ("m", "k", "c_S", "c_Sc")): return _pf(False, True, "", "")
    s = ev["m"]*ev["c_S"] + (ev["k"]-ev["m"])*ev["c_Sc"]
    return _pf(True, abs(s-1) <= 1e-3, "m*c_S+(k-m)*c_Sc=1 (Lemma 1)", f"sum={s:.4f}")

def check_theorem3(ev):
    if not all(k in ev for k in ("rho_R", "m", "c_S")): return _pf(False, True, "", "")
    ok = ev["rho_R"] <= ev["m"]*ev["c_S"] + 1e-9
    return _pf(True, ok, "rho_R <= m*c_S (Thm 3)", f"rho_R={ev['rho_R']:.4f} vs m*c_S={ev['m']*ev['c_S']:.4f}")

def check_overlap_bounds(ev):
    hits = {k: ev[k] for k in ("rho_R", "c_S") if k in ev}
    if not hits: return _pf(False, True, "", "")
    bad = [f"{k}={v}" for k, v in hits.items() if not (-1e-9 <= v <= 1+1e-9)]
    return _pf(True, not bad, "rho_R, c_S in [0,1]", "; ".join(bad) or "in range")

def check_theorem1(ev):
    if not all(k in ev for k in ("P_X_pos", "k")): return _pf(False, True, "", "")
    tgt = 2.0**(-ev["k"]); ok = abs(ev["P_X_pos"]-tgt) <= 1e-3*max(tgt, 1e-300)
    return _pf(True, ok, "P(X>0)=2^-k (Thm 1)", f"reported={ev['P_X_pos']:.3g} vs 2^-k={tgt:.3g}")

def check_theorem5(ev):
    if not all(k in ev for k in ("P_sign", "x", "k")): return _pf(False, True, "", "")
    lb = 2.0**(-ev["x"]*ev["k"]); ok = ev["P_sign"] >= lb - 1e-9
    return _pf(True, ok, "P_sign >= 2^-xk (Thm 5)", f"P_sign={ev['P_sign']:.4f} vs lb={lb:.4f}")

def check_closed_form(ev):
    if not all(k in ev for k in ("x", "C_pred")): return _pf(False, True, "", "")
    cf = C_closed(ev["x"]); ok = abs(ev["C_pred"]-cf) <= 0.01*max(cf, 1e-9)
    return _pf(True, ok, "C_pred = (4/pi^2)x/(1-x^2) (C(x) theorem, unrefereed)", f"tabulated={ev['C_pred']:.4f} vs formula={cf:.4f} ({100*(ev['C_pred']-cf)/cf:+.1f}%)")

def check_zscore(ev):
    if not all(k in ev for k in ("C_hat", "C_pred", "sigma", "z")): return _pf(False, True, "", "")
    z = (ev["C_hat"]-ev["C_pred"])/ev["sigma"]; ok = abs(z-ev["z"]) <= 0.15
    return _pf(True, ok, "z = (C_hat - C_pred)/sigma", f"recomputed z={z:+.2f} vs reported z={ev['z']:+.2f}")

REGISTRY = {"probability_range": check_probability_range, "sign_bound": check_sign_bound,
            "orthant": check_orthant, "sphere_conservation": check_sphere_conservation,
            "theorem3": check_theorem3, "overlap_bounds": check_overlap_bounds,
            "theorem1": check_theorem1, "theorem5": check_theorem5,
            "closed_form": check_closed_form, "zscore": check_zscore}

def audit_rmt(ev: dict[str, Any]) -> dict[str, Any]:
    res = {n: f(ev) for n, f in REGISTRY.items()}
    applied = {n: r for n, r in res.items() if r["applies"]}
    flags = [n for n, r in applied.items() if r["verdict"] == "FLAG"]
    return {"applicable": bool(applied), "verdict": ("FLAG" if flags else "PASS") if applied else "N/A",
            "laws_checked": sorted(applied), "flags": flags,
            "detail": {n: r["why"] for n, r in applied.items()}}

if __name__ == "__main__":
    print("corpus RMT:", list(REGISTRY))


# --- G(a,b,gamma), gamma > 1: G-CLOSED (Codex; reconstructed by Ginibre 2026-10-12, reproduces the frozen predictions to
# 1e-8). GOVERNANCE state: `reduced` (paso 2 by Claude, blind test v2 passed, reconstructed by Codex) — NOT a proved law.
# Valid for gaussian design AND gaussian response only; a non-gaussian response adds kappa4*J_y (Y-KURT). Ported verbatim
# from "Paper - Inverse Ginibre Overlap/DERIVACIONES_2026-10-12_LEY_MAESTRA/AUDIT_G/gclosed_check.py"; sympy is optional.
def G_closed_gamma(av: float, bv: float, gv: float) -> float:
    import sympy as sp
    av, bv, gv = map(sp.nsimplify, (av, bv, gv))
    Fs = sp.Symbol("F", positive=True)
    rho = av * (gv - 1) / (gv - av * bv)
    u = v = 1 + bv / (gv - 1); j = gv / (gv - av * bv); l = q = av * gv * (gv - 1) / (gv - av * bv) ** 2
    zetaC = av * gv * (gv - 1) ** 2 * (av * gv + bv - 2 * av * bv) / (gv - av * bv) ** 4
    F = bv / (gv - bv); z = (1 - av) * (gv - bv) / bv; lam = av * gv / bv
    Jf = Fs ** 2 / (1 - lam * Fs ** 2 / (1 + Fs) ** 2); I3f = Jf / 2 * sp.diff(Jf, Fs); I4f = Jf / 3 * sp.diff(I3f, Fs)
    J, I3, I4 = [sp.simplify(e.subs(Fs, F)) for e in (Jf, I3f, I4f)]
    Delta = (gv - bv) / (gv - av * bv); c = (gv - bv) / (gv - 1); dN = bv * (1 - bv) / ((gv - bv) * (gv - 1)); eta = av * gv / bv
    w = ((J - 2 * z * I3 + z ** 2 * I4) / Delta ** 2 + 2 * dN * F * z * (J - z * I3) / Delta + dN ** 2 * F ** 2 * z ** 2 * J
         + (eta - 1) * dN ** 2 * F ** 2) / (c ** 2 * F ** 2)
    Bang = rho * (sp.Rational(3, 4) * (u + v) + w / 2) - l - q
    Vang = j + zetaC + rho ** 2 / 2 * (u + v + 2 * w) - 2 * rho * (l + q)
    r1 = -av * bv * (av ** 2 * bv ** 2 - 2 * av * bv - av * gv ** 2 + av * gv - bv * gv + bv + gv ** 2) / (gv - av * bv) ** 3
    x = sp.Symbol("x"); chi = 2 * sp.asin(x) / sp.pi
    ch, ch1, ch2 = [sp.N(e.subs(x, rho), 30) for e in (chi, sp.diff(chi, x), sp.diff(chi, x, 2))]
    G = (2 * ch * ch1 * (Bang + r1) + (ch1 ** 2 + ch * ch2) * Vang - 4 * (1 - rho ** 2) / sp.pi ** 2) / bv
    return float(sp.N(G, 20))
