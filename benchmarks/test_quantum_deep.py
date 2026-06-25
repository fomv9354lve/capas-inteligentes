# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""Deep functional coverage of the quantum-physics admissibility gate.

Exercises capas_sdk.{gate_quantum, error_budget, error_correction} and the underlying
capas_quantum_physics public functions with REALISTIC IBM-Heron-style calibration rows so the
physics paths (not just the input guards) execute. Covers the three regimes called out in the
task: the T2 > 2*T1 anomaly (unphysical / TLS), dephasing-limited qubits, and healthy qubits.

Run directly (`python3 benchmarks/test_quantum_deep.py` -> exit 0) or under pytest.
"""
from __future__ import annotations

import math

import capas_quantum_physics as qp
import capas_sdk


# --------------------------------------------------------------------------- #
# Realistic calibration rows (IBM Heron-style magnitudes).
# --------------------------------------------------------------------------- #
def _healthy_row() -> dict:
    """A physically self-consistent transmon/edge row: T2 < 2*T1, cold readout, nulled ZZ."""
    return {
        "t1_us": 220.0,
        "t2_us": 180.0,            # 180 < 440 -> T2 <= 2*T1 holds
        "t2_method": "echo",
        "p01": 1.2e-2,             # relaxation during readout
        "p10": 3.0e-3,             # thermal excitation; P01 > P10 -> n_th finite, cold
        "readout_isolated": [8.0e-3, 9.0e-3],
        "readout_parallel": [1.4e-2, 1.6e-2],
        "readout": 1.0e-2,
        "cz_error": 3.0e-3,
        "rzz_error": 2.7e-3,       # RZZ/CZ ~ 0.9 -> healthy coupler
        "sx_error": 2.5e-4,
        "gate_error": 4.0e-4,      # well above the relaxation floor
        "gate_time_ns": 32.0,
        "zz_residual_hz": 3.5e3,   # 3.5 kHz < 100 kHz target
        "cz_time_ns": 68.0,
        "idle_ns": 40.0,
        "sx_per_layer": 2,
    }


def _t2_anomaly_row() -> dict:
    """T2 > 2*T1 with an undeclared (Ramsey) method -> unphysical / active-TLS signature."""
    row = _healthy_row()
    row["t1_us"] = 100.0
    row["t2_us"] = 250.0           # 250 > 2*100 -> violates the bound
    row["t2_method"] = "ramsey"
    return row


def _t2_anomaly_dd_row() -> dict:
    """Same T2 > 2*T1 numbers but a DECLARED dynamical-decoupling method lifts the bound."""
    row = _t2_anomaly_row()
    row["t2_method"] = "cpmg"
    return row


def _dephasing_limited_row() -> dict:
    """Long T1 but T2 far below 2*T1 -> pure dephasing dominates (packaging/materials limited)."""
    row = _healthy_row()
    row["t1_us"] = 300.0
    row["t2_us"] = 40.0            # Gamma_phi = 1/40 - 1/600 >> relaxation share
    row["t2_method"] = "ramsey"
    return row


# --------------------------------------------------------------------------- #
# SDK surface: gate_quantum (audit_calibration_row)
# --------------------------------------------------------------------------- #
def test_gate_quantum_healthy_admissible():
    out = capas_sdk.gate_quantum(_healthy_row())
    assert isinstance(out, dict)
    assert out["verdict"] == "ADMISSIBLE", out
    assert out["flags"] == []
    # every applicable sub-check ran
    for k in ("coherence", "thermal", "readout_basis", "edge_tls", "gate_coherence", "zz_residual"):
        assert k in out["checks"], (k, out["checks"].keys())
    # exact re-derivation of unpublished quantities attached
    assert "derived" in out
    assert "pure_dephasing" in out["derived"]
    assert out["checks"]["coherence"]["verdict"] == "ADMISSIBLE"


def test_gate_quantum_t2_anomaly_flags():
    out = capas_sdk.gate_quantum(_t2_anomaly_row())
    assert out["verdict"] == "FLAG"
    assert "coherence" in out["flags"]
    assert out["checks"]["coherence"]["verdict"] == "FLAG_INCONSISTENT"
    assert out["checks"]["coherence"]["t2_over_t1"] > 2.0


def test_gate_quantum_t2_anomaly_dd_exempt():
    out = capas_sdk.gate_quantum(_t2_anomaly_dd_row())
    # CPMG declared -> the T2>2*T1 bound is lifted; coherence no longer flags
    assert out["checks"]["coherence"]["verdict"] == "ADMISSIBLE"
    assert out["checks"]["coherence"]["dd_declared"] is True
    assert "coherence" not in out["flags"]


def test_gate_quantum_empty_row_admissible_vacuously():
    out = capas_sdk.gate_quantum({})
    # no applicable invariants -> no flags -> ADMISSIBLE, with no checks run
    assert out["verdict"] == "ADMISSIBLE"
    assert out["checks"] == {}
    assert out["flags"] == []


# --------------------------------------------------------------------------- #
# SDK surface: error_budget (complete_error_budget)
# --------------------------------------------------------------------------- #
def test_error_budget_rederives_complete_floor():
    out = capas_sdk.error_budget(_healthy_row())
    assert isinstance(out, dict)
    headline = out["headline_ibm_rb"]
    floor = out["exact_complete_floor"]
    assert headline == 3.0e-3
    # the complete floor must be >= the headline RB (it adds omitted terms)
    assert floor >= headline
    assert out["exact_gap_x"] >= 1.0
    comps = out["components_per_layer"]
    for key in ("cz_rb_headline", "dephasing_per_layer", "zz_idle", "leakage_estimate"):
        assert key in comps, comps.keys()
    # structured-circuit literature band is [3x, 10x] of the floor
    lo, hi = out["structured_circuit_band"]
    assert math.isclose(hi, round(floor * 10, 5), rel_tol=1e-6)
    assert lo < hi
    assert out["dominant_omitted_term"] in comps


def test_error_budget_dephasing_dominates():
    out = capas_sdk.error_budget(_dephasing_limited_row())
    # a strongly dephasing-limited qubit makes the dephasing term the dominant omitted contributor
    comps = out["components_per_layer"]
    assert comps["dephasing_per_layer"] > 0.0
    # dephasing should beat the (tiny) ZZ-idle and leakage estimate terms
    assert comps["dephasing_per_layer"] > comps["zz_idle"]


# --------------------------------------------------------------------------- #
# SDK surface: error_correction (mitigation_prescription)
# --------------------------------------------------------------------------- #
def test_error_correction_prescribes_dd_for_dephasing():
    out = capas_sdk.error_correction(_dephasing_limited_row())
    assert isinstance(out, dict)
    assert out["n_actions"] == len(out["prescription"])
    assert out["n_actions"] >= 1
    actions = " ".join(a["action"] for a in out["prescription"])
    # dephasing-limited (Tphi small) -> dynamical decoupling prescribed
    assert "dynamical_decoupling" in actions
    # every action carries a re-derived reason
    for a in out["prescription"]:
        assert a["reason"]


def test_error_correction_empty_row_no_actions():
    out = capas_sdk.error_correction({})
    assert out["prescription"] == []
    assert out["n_actions"] == 0


# --------------------------------------------------------------------------- #
# Module physics: pure_dephasing identity Gamma_phi = 1/T2 - 1/(2*T1)
# --------------------------------------------------------------------------- #
def test_pure_dephasing_dephasing_limited():
    out = qp.pure_dephasing(300.0, 40.0)
    assert out["admissible"] is True
    expected_gphi = 1.0 / 40.0 - 1.0 / (2.0 * 300.0)
    assert math.isclose(out["gamma_phi_per_us"], round(expected_gphi, 8), rel_tol=1e-6)
    assert 0.0 < out["dephasing_share"] <= 1.0
    assert "dephasing-limited" in out["mechanism"]


def test_pure_dephasing_unphysical_when_t2_exceeds_2t1():
    out = qp.pure_dephasing(100.0, 250.0)   # Gamma_phi < 0
    assert out["admissible"] is False
    assert "UNPHYSICAL" in out["mechanism"]


def test_pure_dephasing_t1_limited():
    # T2 ~ 2*T1 -> dephasing share near zero -> relaxation-limited
    out = qp.pure_dephasing(200.0, 399.0)
    assert out["admissible"] is True
    assert "T1-limited" in out["mechanism"]


# --------------------------------------------------------------------------- #
# Module physics: gate-error coherence floor + admissibility
# --------------------------------------------------------------------------- #
def test_gate_error_coherence_floor_relaxation_bound():
    fl = qp.gate_error_coherence_floor(32.0, 220.0, 180.0)
    tg_us = 32.0e-3
    assert math.isclose(fl["relaxation_floor"], round((1.0 / 3.0) * tg_us / 220.0, 8), rel_tol=1e-6)
    # the fuller decoherence estimate must exceed the relaxation-only floor
    assert fl["decoherence_estimate"] >= fl["relaxation_floor"]


def test_gate_error_admissible_too_clean_below_floor():
    # report a gate error 100x below the relaxation floor -> physically impossible
    fl = qp.gate_error_coherence_floor(32.0, 220.0, 180.0)
    out = qp.gate_error_admissible(fl["relaxation_floor"] / 100.0, 32.0, 220.0, 180.0)
    assert out["verdict"] == "FLAG_TOO_CLEAN"


def test_gate_error_admissible_control_dominated():
    out = qp.gate_error_admissible(5.0e-3, 32.0, 220.0, 180.0)
    assert out["verdict"] == "ADMISSIBLE"
    assert out["control_dominated"] is True


# --------------------------------------------------------------------------- #
# Module physics: thermal, ZZ residual, edge TLS, readout basis
# --------------------------------------------------------------------------- #
def test_check_thermal_cold_and_unphysical():
    cold = qp.check_thermal(1.2e-2, 3.0e-3)
    assert cold["verdict"] == "ADMISSIBLE"
    assert cold["n_thermal"] is not None and cold["n_thermal"] >= 0.0
    inverted = qp.check_thermal(3.0e-3, 1.2e-2)   # P10 >= P01
    assert inverted["verdict"] == "FLAG_UNPHYSICAL"
    assert inverted["n_thermal"] is None


def test_check_zz_residual_target():
    ok = qp.check_zz_residual(3.5e3)
    assert ok["verdict"] == "ADMISSIBLE"
    high = qp.check_zz_residual(5.0e5)            # 500 kHz >> 100 kHz target
    assert high["verdict"] == "FLAG_HIGH_ZZ"
    assert high["zz_residual_hz"] == 5.0e5


def test_check_edge_tls_signature():
    healthy = qp.check_edge_tls(3.0e-3, 2.7e-3)
    assert healthy["verdict"] == "ADMISSIBLE"
    # elevated CZ with much smaller RZZ -> amplitude-resonant TLS signature
    tls = qp.check_edge_tls(2.0e-2, 1.0e-3)
    assert tls["verdict"] == "FLAG_TLS_RESONANT_EDGE"
    assert tls["rzz_over_cz"] < 1.0


def test_check_readout_floor_basis_blowup():
    out = qp.check_readout_floor_basis([8.0e-3, 9.0e-3], [1.4e-2, 1.6e-2])
    assert out["verdict"] == "USE_PARALLEL"
    assert out["parallel_floor"] > out["isolated_floor"]
    assert out["blowup_x"] > 1.0


# --------------------------------------------------------------------------- #
# Module physics: derived quantities + circuit fidelity budget + claim gate
# --------------------------------------------------------------------------- #
def test_derive_hidden_quantities():
    out = qp.derive_hidden_quantities(_healthy_row())
    assert "pure_dephasing" in out
    assert "gate_coherence_floor" in out
    assert out["pure_dephasing"]["admissible"] is True


def test_circuit_success_budget_and_claim_gate():
    budget = qp.circuit_success_budget(
        n_measured=4, cz_layers=10, czs_per_layer=2, sx_per_layer=2,
        cz_err=3.0e-3, sx_err=2.5e-4, readout_err=1.0e-2,
    )
    assert 0.0 < budget["predicted_fidelity_ceiling"] < 1.0
    assert budget["n_cz_gates"] == 20
    # a claimed fidelity ABOVE the physical ceiling (with slack) -> TOO_CLEAN
    too_clean = qp.gate_circuit_fidelity_claim(
        claimed_fidelity=0.999, n_measured=4, cz_layers=10, czs_per_layer=2,
        sx_per_layer=2, cz_err=3.0e-3, sx_err=2.5e-4, readout_err=1.0e-2,
    )
    assert too_clean["verdict"] == "FLAG_TOO_CLEAN"


# --------------------------------------------------------------------------- #
# Module physics: XEB / speckle purity / coherent-fraction reconciliation
# --------------------------------------------------------------------------- #
def test_xeb_and_purity_and_coherent_fraction():
    ideal = {"00": 0.5, "11": 0.5}
    counts = {"00": 480, "11": 470, "01": 25, "10": 25}
    f_xeb = qp.xeb_linear_fidelity(ideal, counts)
    assert isinstance(f_xeb, float)
    f_purity = qp.speckle_purity_fidelity(counts, n_qubits=2)
    assert f_purity >= 0.0
    verdict = qp.coherent_fraction_verdict(f_xeb=0.70, f_purity=0.95, depth=20)
    assert verdict["verdict"] == "FLAG_COHERENT_RECOVERABLE"
    assert 0.0 <= verdict["coherent_fraction"] <= 1.0


def test_reconcile_budget_with_measurement():
    # measured well above the incoherent budget with high coherent fraction -> pessimistic by design
    out = qp.reconcile_budget_with_measurement(
        measured_xeb=0.40, predicted_xeb=0.25, coherent_fraction=0.6, depth=20,
    )
    assert out["verdict"] == "BUDGET_PESSIMISTIC_COHERENT"
    assert out["gap"] > 0.0
    within = qp.reconcile_budget_with_measurement(0.26, 0.25, 0.6)
    assert within["verdict"] == "WITHIN_BUDGET"


# --------------------------------------------------------------------------- #
# Module physics: kappa correlation-discount estimate + application
# --------------------------------------------------------------------------- #
def test_estimate_kappa_and_apply_discount():
    # synthesize a decaying XEB-vs-depth curve consistent with a per-layer error
    naive = 0.02
    true_kappa = 0.7
    per_layer = true_kappa * naive
    depths = [6, 8, 10, 12, 14, 16]
    measured = [(1.0 - per_layer) ** d for d in depths]
    est = qp.estimate_kappa(depths, measured, naive_layer_error=naive)
    assert est["kappa"] is not None
    assert est["kappa"] > 0.0
    assert est["n_points"] == len(depths)
    applied = qp.apply_correlation_discount(naive, est["kappa"])
    assert applied["verdict"] in ("CORRECTED", "FLAG_ANTICORRELATED")
    assert applied["corrected_layer_error"] > 0.0


def test_apply_correlation_discount_anticorrelated_flag():
    out = qp.apply_correlation_discount(0.02, kappa=1.5)
    assert out["verdict"] == "FLAG_ANTICORRELATED"


# --------------------------------------------------------------------------- #
# Module physics: quantum-advantage / commitment-depth gate
# --------------------------------------------------------------------------- #
def test_quantum_advantage_committed_early():
    out = qp.gate_quantum_advantage_claim(
        claimed_circuit_depth=40, commitment_depth=20, asserts_quantum_hardness=True,
    )
    assert out["verdict"] == "FLAG_CLASSICALLY_REPRODUCIBLE"
    assert out["committed_before_claim"] is True


def test_quantum_advantage_admissible_when_uncommitted():
    out = qp.gate_quantum_advantage_claim(
        claimed_circuit_depth=20, commitment_depth=40, asserts_quantum_hardness=True,
    )
    assert out["verdict"] == "ADMISSIBLE"
    assert out["committed_before_claim"] is False


# --------------------------------------------------------------------------- #
# Standalone runner (so `python3 benchmarks/test_quantum_deep.py` exits 0).
# --------------------------------------------------------------------------- #
def _run_all() -> int:
    fns = [v for k, v in sorted(globals().items())
           if k.startswith("test_") and callable(v)]
    failed = 0
    for fn in fns:
        try:
            fn()
            print(f"PASS {fn.__name__}")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            print(f"FAIL {fn.__name__}: {type(exc).__name__}: {exc}")
    print(f"\n{len(fns) - failed}/{len(fns)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(_run_all())
