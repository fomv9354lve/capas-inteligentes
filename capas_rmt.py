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
def C_closed(x): return (4/PI2)*x/(1-x**2)          # Conjecture 1 closed form

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
    return _pf(True, ok, "C_pred = (4/pi^2)x/(1-x^2) (Conj 1)", f"tabulated={ev['C_pred']:.4f} vs formula={cf:.4f} ({100*(ev['C_pred']-cf)/cf:+.1f}%)")

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
