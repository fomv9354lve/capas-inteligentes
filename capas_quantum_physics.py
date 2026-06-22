"""CAPAS — quantum physical-consistency gates (deterministic, re-derivable).

These gates do NOT cross text<->reality. They re-derive whether a CLAIMED set of device
numbers (a calibration row, or a circuit-fidelity claim) is internally consistent with
TEXTBOOK physics. A claim that violates a physical invariant is flagged WITHOUT measuring
anything — this is record<->text / text<->text re-derivation, exactly CAPAS's exact-GATE
domain. The invariants below are first-order established physics, NOT second-order inference;
where a value is calibration-snapshot reference data (best edges, TLS clusters) it is marked
as reference, not law.

Invariants encoded:
  1. Coherence (T2 <= 2*T1):    standard Markovian decoherence bounds T2 by 2*T1. A reported
     T2 > 2*T1 is admissible ONLY if the method is declared as a dynamical-decoupling sequence
     (CPMG/echo), which refocuses low-frequency (TLS / 1/f) noise. Undeclared violation -> FLAG.
  2. Thermal (P01 >= P10):      readout-asymmetry thermometry. P01 (relax: measure 0 | prep 1)
     >= P10 (excite: measure 1 | prep 0) for a passive qubit; n_th = P10/(P01-P10) is the mean
     thermal photon number and must be finite and >= 0. P10 >= P01 -> negative/divergent -> FLAG.
  3. Parallel readout floor:    real circuits measure all qubits simultaneously, so the
     admissible floor must use the PARALLEL (MEAS_2) readout error, which can be many times the
     isolated (MEAS) value. An error budget built on isolated readout UNDER-estimates the floor.
  4. Error accumulation:        success ~ prod(1-eps); a claimed circuit fidelity above the
     calibration-derived budget is FLAG_TOO_CLEAN (physically impossible), far below is
     FLAG_TOO_NOISY (drift / wrong device / mis-mapped qubits).
  5. Gate anomaly (CZ >> RZZ):  on one coupler, CZ error >> RZZ error signals an amplitude-
     resonant TLS (the full-amplitude CZ hits it, the fractional RZZ misses it); the edge's
     nominal CZ fidelity is not trustworthy for a high-amplitude gate.

Every verdict is one of ADMISSIBLE / FLAG_* and carries the re-derivation, so the gate is
auditable. None of these require a live device — they gate the TEXT of a claim against physics.
"""
from __future__ import annotations

from typing import Any

# --- physical constants / thresholds (first-order, documented) ---
_DD_METHODS = ("cpmg", "echo", "hahn", "dynamical_decoupling", "dd", "carr-purcell", "cp")
# RZZ/CZ ratio on a healthy coupler is ~0.8-1.1 (both are ZZ-type). A CZ that is much worse
# than its RZZ on the SAME edge is the TLS-amplitude-resonance signature.
_TLS_RZZ_OVER_CZ = 0.5      # RZZ/CZ below this (CZ anomalously bad) is suspect
_TLS_MIN_CZ = 5e-3          # ...and only meaningful once CZ itself is clearly elevated


def check_coherence(t1_us: float, t2_us: float, method: str = "ramsey") -> dict[str, Any]:
    """Gate a reported (T1, T2) pair against T2 <= 2*T1. A violation is admissible only if the
    method is a declared dynamical-decoupling sequence (which lifts the bound by refocusing
    low-frequency noise); otherwise it is physically inconsistent OR evidence of an active TLS."""
    t1, t2 = float(t1_us), float(t2_us)
    is_dd = any(m in str(method).lower() for m in _DD_METHODS)
    ratio = round(t2 / t1, 4) if t1 > 0 else float("inf")
    bound_ok = t2 <= 2 * t1 + 1e-9

    if bound_ok:
        verdict = "ADMISSIBLE"
        why = f"T2/T1 = {ratio} <= 2.0 — consistent with Markovian decoherence"
    elif is_dd:
        verdict = "ADMISSIBLE"
        why = (f"T2/T1 = {ratio} > 2.0 but method is dynamical-decoupling ({method}); CPMG/echo "
               f"refocuses low-frequency TLS/1-f noise and can exceed the Ramsey 2*T1 bound")
    else:
        verdict = "FLAG_INCONSISTENT"
        why = (f"T2/T1 = {ratio} > 2.0 with undeclared/Ramsey method — violates T2<=2*T1. Either "
               f"the method is actually CPMG (declare it) or the qubit has an active TLS "
               f"(T1 is TLS-suppressed while echo partially refocuses): the number is not trustworthy")
    return {
        "invariant": "T2 <= 2*T1 (Markovian); CPMG/DD exempt",
        "t1_us": t1, "t2_us": t2, "t2_over_t1": ratio, "method": method,
        "dd_declared": is_dd, "verdict": verdict, "why": why,
    }


def check_thermal(p01: float, p10: float) -> dict[str, Any]:
    """Gate readout asymmetry. P01 = P(0|prep 1) (relaxation), P10 = P(1|prep 0) (thermal
    excitation). A passive qubit near the ground state has P01 >= P10; the mean thermal photon
    number n_th = P10/(P01-P10) must be finite and non-negative."""
    p01, p10 = float(p01), float(p10)
    if p01 <= p10:
        return {
            "invariant": "P01 >= P10 (passive thermal qubit); n_th = P10/(P01-P10) >= 0",
            "p01": p01, "p10": p10, "n_thermal": None,
            "verdict": "FLAG_UNPHYSICAL",
            "why": (f"P10 ({p10:.2e}) >= P01 ({p01:.2e}) implies a negative/divergent thermal "
                    f"population — unphysical for a passive readout (mis-labeled P01/P10, an "
                    f"inverted/over-driven readout, or a fabricated calibration row)"),
        }
    n_th = round(p10 / (p01 - p10), 4)
    # effective temperature proxy kT/hw ~ n_th/(1+n_th); flag implausibly hot residual population
    hot = n_th > 0.5
    return {
        "invariant": "P01 >= P10; n_th = P10/(P01-P10)",
        "p01": p01, "p10": p10, "n_thermal": n_th,
        "verdict": "FLAG_HOT" if hot else "ADMISSIBLE",
        "why": (f"residual thermal population n_th = {n_th} photons "
                + ("— implausibly hot, readout resonator likely mis-thermalized or the row is suspect"
                   if hot else "— physically consistent (cold qubit)")),
    }


def parallel_readout_floor(readout_parallel: list[float]) -> float:
    """First-order floor on the fraction of shots landing OUTSIDE the ideal support, using the
    PARALLEL (MEAS_2 / simultaneous) readout errors of the measured qubits: 1 - prod(1-ro_par).
    This is the floor that applies to REAL circuits (all qubits measured at once), which the
    isolated single-qubit readout under-estimates."""
    prod = 1.0
    for ro in readout_parallel:
        prod *= (1 - float(ro))
    return round(1 - prod, 6)


def check_readout_floor_basis(readout_isolated: list[float], readout_parallel: list[float]) -> dict[str, Any]:
    """Surface the gap between the isolated and parallel readout floors so a gate cannot silently
    use the optimistic (isolated) number. A claim that quotes single-qubit readout for a
    multi-qubit measured circuit is using the wrong basis."""
    iso = parallel_readout_floor(readout_isolated)   # same formula, isolated inputs
    par = parallel_readout_floor(readout_parallel)
    blowup = round(par / iso, 2) if iso > 0 else float("inf")
    return {
        "isolated_floor": iso, "parallel_floor": par, "blowup_x": blowup,
        "verdict": "USE_PARALLEL",
        "why": (f"simultaneous-readout floor {par:.3%} is {blowup}x the isolated floor {iso:.3%}; "
                f"real circuits measure all qubits at once — the admissible floor MUST use MEAS_2, "
                f"or the gate will falsely flag a physically-consistent result as TOO_NOISY"),
    }


def circuit_success_budget(n_measured: int, cz_layers: int, czs_per_layer: int,
                           sx_per_layer: int, cz_err: float, sx_err: float,
                           readout_err: float) -> dict[str, Any]:
    """Multiplicative first-order success-probability budget for a circuit:
    P_success ~ (1-cz)^(cz_layers*czs_per_layer) * (1-sx)^(cz_layers*sx_per_layer) * (1-ro)^n_measured.
    Returns the predicted achievable fidelity ceiling from the calibration."""
    n_cz = cz_layers * czs_per_layer
    n_sx = cz_layers * sx_per_layer
    p_gate = (1 - cz_err) ** n_cz * (1 - sx_err) ** n_sx
    p_ro = (1 - readout_err) ** n_measured
    p = p_gate * p_ro
    return {
        "predicted_fidelity_ceiling": round(p, 6),
        "predicted_error": round(1 - p, 6),
        "n_cz_gates": n_cz, "n_sx_gates": n_sx, "n_measured": n_measured,
        "components": {"gate_survival": round(p_gate, 6), "readout_survival": round(p_ro, 6)},
    }


def gate_circuit_fidelity_claim(claimed_fidelity: float, n_measured: int, cz_layers: int,
                                czs_per_layer: int, sx_per_layer: int, cz_err: float,
                                sx_err: float, readout_err: float, slack: float = 1.5) -> dict[str, Any]:
    """Gate a CLAIMED circuit fidelity against the calibration-derived budget. A claim cleaner
    than the physical ceiling (times a slack for model first-order-ness) is FLAG_TOO_CLEAN; far
    below is FLAG_TOO_NOISY. `slack` (>1) widens the admissible band for the first-order model and
    for error mitigation (ZNE/PEC can recover some fidelity, so the ceiling is not absolute)."""
    budget = circuit_success_budget(n_measured, cz_layers, czs_per_layer, sx_per_layer,
                                    cz_err, sx_err, readout_err)
    ceiling = budget["predicted_fidelity_ceiling"]
    claimed = float(claimed_fidelity)
    # admissible error band: claimed error must be within [ceiling_error/slack, ...]; "too clean"
    # means claimed fidelity exceeds the ceiling by more than the slack allows.
    too_clean_threshold = 1 - (1 - ceiling) / slack
    if claimed > too_clean_threshold:
        verdict = "FLAG_TOO_CLEAN"
        why = (f"claimed fidelity {claimed:.3f} exceeds the calibration ceiling {ceiling:.3f} "
               f"(even with {slack}x mitigation slack -> {too_clean_threshold:.3f}); a result this "
               f"clean is not physically reachable on this device/depth — fabricated, post-selected, "
               f"wrong device, or undeclared error mitigation")
    elif claimed < ceiling / (slack * slack):
        verdict = "FLAG_TOO_NOISY"
        why = (f"claimed fidelity {claimed:.3f} is far below the ceiling {ceiling:.3f} — drift, "
               f"mis-mapped qubits (a bad edge/TLS zone), or a different circuit than declared")
    else:
        verdict = "ADMISSIBLE"
        why = (f"claimed fidelity {claimed:.3f} is consistent with the calibration ceiling "
               f"{ceiling:.3f} for {budget['n_cz_gates']} CZ + {budget['n_sx_gates']} SX gates "
               f"and {n_measured}-qubit readout")
    return {"verdict": verdict, "why": why, "claimed_fidelity": claimed,
            "predicted_ceiling": ceiling, "too_clean_threshold": round(too_clean_threshold, 6),
            "budget": budget,
            "consilience": ("the calibration (IBM's independent daily benchmark) and the multiplicative "
                            "error model both bound this claim" if verdict == "ADMISSIBLE"
                            else "the claim disagrees with the calibration-derived physical budget")}


def check_edge_tls(cz_err: float, rzz_err: float) -> dict[str, Any]:
    """Gate a coupler's reported errors for an amplitude-resonant TLS signature: CZ error much
    worse than RZZ error on the SAME edge. (Healthy edges have RZZ/CZ ~ 0.8-1.1.) When present,
    the edge's nominal CZ fidelity is unreliable for a full-amplitude 2-qubit gate."""
    cz, rzz = float(cz_err), float(rzz_err)
    ratio = round(rzz / cz, 4) if cz > 0 else float("inf")
    tls = (ratio < _TLS_RZZ_OVER_CZ) and (cz > _TLS_MIN_CZ)
    return {
        "cz_error": cz, "rzz_error": rzz, "rzz_over_cz": ratio,
        "verdict": "FLAG_TLS_RESONANT_EDGE" if tls else "ADMISSIBLE",
        "why": (f"RZZ/CZ = {ratio} << 1 with CZ = {cz:.2e} elevated: the full-amplitude CZ excites "
                f"an amplitude-resonant TLS that the fractional RZZ avoids — do not trust this edge's "
                f"CZ fidelity for a high-amplitude gate" if tls else
                f"RZZ/CZ = {ratio} — coupler errors are consistent (no amplitude-resonant TLS signature)"),
    }


# ---------------------------------------------------------------------------
# DERIVED-QUANTITY gates. A second class of invariant: from PUBLISHED quantities
# (T1, T2, gate time) EXACTLY re-derive a quantity the vendor does NOT publish, and gate
# the claim against that derived quantity's own physical bound. "It's in the numbers,
# they just don't show it." These are exact identities, not estimates.
# ---------------------------------------------------------------------------

# minimal Haar-averaged single-qubit gate infidelity from T1 relaxation alone, ~ t_g/(3*T1).
# Adding dephasing only INCREASES error, so this is a TRUE lower bound regardless of T2 — a
# reported gate error below it is physically impossible. Convention prefactor 1/3 (amplitude
# damping, average gate fidelity); a slack widens it so convention differences never false-flag.
_COH_FLOOR_COEF = 1.0 / 3.0


def pure_dephasing(t1_us: float, t2_us: float) -> dict[str, Any]:
    """EXACTLY re-derive the pure-dephasing rate the vendor does not publish, from T1 and T2:
    1/T2 = 1/(2*T1) + Gamma_phi  ->  Gamma_phi = 1/T2 - 1/(2*T1). Gamma_phi >= 0 is required
    (equivalent to T2 <= 2*T1). Classifies whether the qubit is dephasing-limited (environmental
    phase noise — a packaging/materials problem) or T1-limited (energy loss)."""
    t1, t2 = float(t1_us), float(t2_us)
    g_phi = 1.0 / t2 - 1.0 / (2.0 * t1) if t1 > 0 and t2 > 0 else float("nan")
    admissible = g_phi >= -1e-12
    t_phi = (1.0 / g_phi) if g_phi > 0 else float("inf")
    # share of the total T2 rate that is pure dephasing vs relaxation
    rate_t2 = 1.0 / t2 if t2 > 0 else float("inf")
    deph_share = (g_phi / rate_t2) if rate_t2 > 0 and admissible else float("nan")
    if not admissible:
        mech = "UNPHYSICAL (Gamma_phi < 0 -> T2 > 2*T1)"
    elif deph_share > 0.66:
        mech = "dephasing-limited (environmental phase noise — packaging/materials, not junction fab)"
    elif deph_share < 0.34:
        mech = "T1-limited (energy relaxation dominates; better fab/materials would help)"
    else:
        mech = "balanced (relaxation and dephasing comparable)"
    return {
        "gamma_phi_per_us": round(g_phi, 8) if g_phi == g_phi else None,
        "t_phi_us": round(t_phi, 2) if t_phi != float("inf") else None,
        "dephasing_share": round(deph_share, 4) if deph_share == deph_share else None,
        "mechanism": mech, "admissible": bool(admissible),
        "identity": "Gamma_phi = 1/T2 - 1/(2*T1) (exact); Gamma_phi >= 0 required",
    }


def gate_error_coherence_floor(gate_time_ns: float, t1_us: float, t2_us: float) -> dict[str, Any]:
    """The physical LOWER BOUND on a single-qubit gate error from coherence alone. The relaxation
    floor t_g/(3*T1) is a hard bound (independent of T2 and control); the fuller decoherence
    estimate t_g/2*(1/T1 + 1/T2) is used to attribute reported error to decoherence vs control."""
    tg = float(gate_time_ns) * 1e-3   # ns -> us
    t1, t2 = float(t1_us), float(t2_us)
    relax_floor = _COH_FLOOR_COEF * tg / t1 if t1 > 0 else 0.0
    deco_estimate = 0.5 * tg * (1.0 / t1 + 1.0 / t2) if t1 > 0 and t2 > 0 else 0.0
    return {"relaxation_floor": round(relax_floor, 8),     # HARD lower bound (gate cannot be cleaner)
            "decoherence_estimate": round(deco_estimate, 8),  # estimate, for control-vs-decoherence split
            "gate_time_ns": float(gate_time_ns)}


def gate_error_admissible(reported_error: float, gate_time_ns: float, t1_us: float, t2_us: float,
                          slack: float = 1.5) -> dict[str, Any]:
    """Gate a REPORTED single-qubit gate error against its coherence floor. Below the relaxation
    floor (with slack for convention) -> FLAG_TOO_CLEAN: a gate cannot be cleaner than relaxation
    permits (fabricated / wrong device / mis-attributed). Far above the decoherence estimate is
    NOT a flag — it's a poorly-CALIBRATED but admissible gate (control-dominated); we note it."""
    fl = gate_error_coherence_floor(gate_time_ns, t1_us, t2_us)
    floor = fl["relaxation_floor"]
    deco = fl["decoherence_estimate"]
    err = float(reported_error)
    hard_floor = floor / slack
    if err < hard_floor:
        verdict = "FLAG_TOO_CLEAN"
        why = (f"reported gate error {err:.2e} is below the relaxation floor {floor:.2e} "
               f"(t_g/(3*T1)); a gate cannot be cleaner than energy relaxation allows — "
               f"physically impossible (fabricated / wrong T1 / mis-attributed)")
    else:
        verdict = "ADMISSIBLE"
        control_dominated = err > 2.0 * deco and deco > 0
        why = (f"reported gate error {err:.2e} >= relaxation floor {floor:.2e}; "
               + (f"control-dominated (~{deco:.2e} is decoherence; the rest is calibration residual "
                  f"-> needs recalibration, not better hardware)" if control_dominated
                  else f"consistent with the decoherence estimate {deco:.2e}"))
    return {"verdict": verdict, "why": why, "reported_error": err,
            "relaxation_floor": floor, "decoherence_estimate": deco,
            "control_dominated": bool(err > 2.0 * deco and deco > 0)}


def derive_hidden_quantities(row: dict[str, Any]) -> dict[str, Any]:
    """Surface what is re-derivable from a calibration row but NOT published: pure dephasing rate
    + mechanism (exact), and the gate-error coherence floor (exact). This is CAPAS as a derivation
    engine — 'it's in the numbers, they just don't show it' — with each derived quantity carrying
    its own admissibility bound. EXACT only; approximate derivations (ZZ-residual from CZ/RZZ,
    loss tangent assuming a frequency) are deliberately NOT here — they are diagnostics, not gates."""
    out: dict[str, Any] = {}
    if "t1_us" in row and "t2_us" in row:
        out["pure_dephasing"] = pure_dephasing(row["t1_us"], row["t2_us"])
        if "gate_time_ns" in row:
            out["gate_coherence_floor"] = gate_error_coherence_floor(
                row["gate_time_ns"], row["t1_us"], row["t2_us"])
    return out


def check_zz_residual(zz_hz: float, threshold_hz: float = 1.0e5) -> dict[str, Any]:
    """Gate a coupler's residual ZZ coupling against an engineering target. IBM PUBLISHES this
    EXACTLY per edge (general.zz_*, in GHz) — it is measured data, NOT an estimate from the
    CZ/RZZ ratio (which over-states it: e.g. edge 131-138 estimates ~86 kHz from CZ/RZZ but the
    PUBLISHED value is 3.56 kHz, 24x smaller — gating on the estimate would false-flag). On a
    tunable-coupler device (Heron) the coupler nulls ZZ to single-digit kHz; a residual far above
    the target means the coupler is not nulling (always-on entanglement during idle -> qubits not
    independently addressable). This is an ENGINEERING-TARGET threshold, not a fundamental identity."""
    zz = abs(float(zz_hz))
    flag = zz > threshold_hz
    return {"zz_residual_hz": zz, "threshold_hz": threshold_hz,
            "verdict": "FLAG_HIGH_ZZ" if flag else "ADMISSIBLE",
            "why": (f"residual ZZ {zz/1e3:.2f} kHz exceeds the {threshold_hz/1e3:.0f} kHz coupler-nulling "
                    f"target — the tunable coupler is not suppressing ZZ; the pair entangles during idle"
                    if flag else
                    f"residual ZZ {zz/1e3:.2f} kHz is within the coupler-nulling target (independently "
                    f"addressable)"),
            "note": "EXACT published quantity (general.zz_*), not the CZ/RZZ estimate"}


def audit_calibration_row(row: dict[str, Any]) -> dict[str, Any]:
    """Run every applicable physical-consistency gate over one qubit/edge calibration row and
    return a combined verdict. The row may carry: t1_us, t2_us, t2_method, p01, p10,
    readout_isolated/readout_parallel (lists), cz_error, rzz_error, and a single-qubit-gate
    claim (gate_error + gate_time_ns, gated against the coherence floor). ADMISSIBLE only if
    every applicable invariant passes — fail-closed: any flag dominates."""
    checks: dict[str, Any] = {}
    if "t1_us" in row and "t2_us" in row:
        checks["coherence"] = check_coherence(row["t1_us"], row["t2_us"], row.get("t2_method", "ramsey"))
    if "p01" in row and "p10" in row:
        checks["thermal"] = check_thermal(row["p01"], row["p10"])
    if "readout_isolated" in row and "readout_parallel" in row:
        checks["readout_basis"] = check_readout_floor_basis(row["readout_isolated"], row["readout_parallel"])
    if "cz_error" in row and "rzz_error" in row:
        checks["edge_tls"] = check_edge_tls(row["cz_error"], row["rzz_error"])
    if "gate_error" in row and "gate_time_ns" in row and "t1_us" in row and "t2_us" in row:
        checks["gate_coherence"] = gate_error_admissible(
            row["gate_error"], row["gate_time_ns"], row["t1_us"], row["t2_us"])
    if "zz_residual_hz" in row:
        checks["zz_residual"] = check_zz_residual(row["zz_residual_hz"])

    flags = [k for k, v in checks.items() if str(v.get("verdict", "")).startswith("FLAG")]
    out = {
        "verdict": "ADMISSIBLE" if not flags else "FLAG",
        "flags": flags,
        "checks": checks,
        "note": ("every applicable physical invariant holds — the calibration row is internally "
                 "consistent with textbook physics (record<->text re-derivation; no device needed)"
                 if not flags else
                 f"{len(flags)} physical inconsistency(ies) — the claimed numbers contradict physics"),
    }
    derived = derive_hidden_quantities(row)
    if derived:
        out["derived"] = derived   # exact re-derivation of unpublished quantities (Gamma_phi, floor)
    return out
