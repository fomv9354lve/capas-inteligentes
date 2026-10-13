# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""Two engine debts named by two out-of-sample Ginibre batches (X4-002, X5-003; X5-010). Rules agreed with
the Ginibre session 2026-10-13 (its refutation of a tolerance/abs_error ratio stands: power is a property
of the TEST, not of the result; a lucky hit must not worsen a good claim).

(1) SCOPE — `scope_declared` / `scope_tested` (lists of cells/regimes). Declared ⊄ tested → REWRITE, never
    ACCEPT. Generalising TEXT with neither field → REWRITE (the gate cannot read scope from prose; it can
    demand it be declared). Local text with no fields → judged as before.
(2) POWER — machine-precision regime abs_error <= 1e-12 * max(1, |reference_value|): the tolerance does
    not inform (a circular check gives 3e-14 for any tolerance, same as a legit exact identity). The only
    discriminant is whether a false variant was seen to fail: `negative_control_failed` true → judged
    normally; missing → HOLD; false → REWRITE. Outside that regime: as before (SE + rule (b) cover power).
    Optional: tolerance / |reference_value| > 0.5 → HOLD "tolerance of the order of the object"."""
import capas

def _p(text, **ev):
    e = {"abs_error": 0.018, "tolerance": 0.3}; e.update(ev)
    return {"schema_version": capas.CAPAS_CLAIM_SCHEMA_VERSION,
            "claim": {"id": "t", "type": "exact_model_solution", "text": text}, "evidence": e}

# ---------- (1) scope
GENERAL = "La corrección funciona en toda la ventana útil y para todo k."
LOCAL = "La corrección da abs_error 0.018 en la celda (d=1.2, k=400)."

def test_generalising_text_without_scope_fields_rewrites():
    d = capas.decide_external_claim(_p(GENERAL))
    assert d["verdict"] == "REWRITE" and "scope" in d["reason"].lower()

def test_declared_subset_of_tested_accepts():
    d = capas.decide_external_claim(_p(GENERAL, scope_declared=["d=1.1", "d=1.2", "d=1.3"], scope_tested=["d=1.1", "d=1.2", "d=1.3", "d=2.0"]))
    assert d["verdict"] == "ACCEPT"

def test_declared_not_subset_of_tested_rewrites_even_with_local_text():
    d = capas.decide_external_claim(_p(LOCAL, scope_declared=["d=1.1", "d=1.2", "d=1.3"], scope_tested=["d=1.2"]))
    assert d["verdict"] == "REWRITE" and "scope" in d["reason"].lower()

def test_local_text_needs_no_scope_fields():
    assert capas.decide_external_claim(_p(LOCAL))["verdict"] == "ACCEPT"

def test_x5_003_and_x4_002_shapes_are_caught():
    t3 = "La corrección kurt_true funciona en la ventana útil (d/borde 1.1–1.3, CV(σ²)≤2) (verificada, no heredada)."
    assert capas.decide_external_claim(_p(t3, abs_error=1.59, tolerance=2.0))["verdict"] == "REWRITE"
    t2 = "La curtosis por realización es monótona en el margen y k-casi-independiente ⇒ es un estimador del margen de estabilidad."
    assert capas.decide_external_claim(_p(t2, abs_error=0.07, tolerance=0.1, n_points=3))["verdict"] == "REWRITE"

# ---------- (2) power
def test_machine_precision_without_negative_control_holds():
    d = capas.decide_external_claim(_p(LOCAL, abs_error=3e-14, tolerance=1e-10))
    assert d["verdict"] == "HOLD" and "negative control" in d["reason"].lower()

def test_machine_precision_with_failed_negative_control_accepts():
    assert capas.decide_external_claim(_p(LOCAL, abs_error=3e-14, tolerance=1e-10, negative_control_failed=True))["verdict"] == "ACCEPT"

def test_machine_precision_with_control_that_did_not_fail_rewrites():
    assert capas.decide_external_claim(_p(LOCAL, abs_error=3e-14, tolerance=1e-10, negative_control_failed=False))["verdict"] == "REWRITE"

def test_regime_scales_with_reference_value():
    # abs_error 1e-9 on a value of 1e4 is 1e-13 relative: machine precision -> asks for the control
    assert capas.decide_external_claim(_p(LOCAL, abs_error=1e-9, tolerance=1e-6, reference_value=1e4))["verdict"] == "HOLD"
    # abs_error 1e-9 on a value of 1: not machine precision -> judged as before
    assert capas.decide_external_claim(_p(LOCAL, abs_error=1e-9, tolerance=1e-6))["verdict"] == "ACCEPT"

def test_lucky_hit_is_not_punished():
    # a good MC with absolute tolerance 0.02 that lands 1e-5 from target: NOT machine precision, must ACCEPT
    assert capas.decide_external_claim(_p(LOCAL, abs_error=1e-5, tolerance=0.02))["verdict"] == "ACCEPT"

def test_zero_error_is_machine_precision():
    assert capas.decide_external_claim(_p(LOCAL, abs_error=0.0, tolerance=0.01))["verdict"] == "HOLD"

def test_tolerance_of_the_order_of_the_object_holds():
    d = capas.decide_external_claim(_p(LOCAL, abs_error=0.3, tolerance=0.8, reference_value=1.0))
    assert d["verdict"] == "HOLD" and "order of the object" in d["reason"].lower()
    assert capas.decide_external_claim(_p(LOCAL, abs_error=0.3, tolerance=0.4, reference_value=1.0))["verdict"] == "ACCEPT"


# --- Same lesson as proof_admissibility (§6 run 8): when an ACCEPT depends on a DECLARED scope, the licensed text is
# the text annotated with that scope, never the raw sentence (the gate cannot read prose; the reusable sentence must
# carry its own limit).
def test_accept_with_declared_scope_annotates_licensed_claim():
    d = capas.decide_external_claim(_p(GENERAL, scope_declared=["d=1.1", "d=1.2", "d=1.3"], scope_tested=["d=1.1", "d=1.2", "d=1.3", "d=2.0"]))
    assert d["verdict"] == "ACCEPT"
    assert d["licensed_claim"] != GENERAL and "d=1.1" in d["licensed_claim"] and "scope" in d["licensed_claim"].lower()

def test_accept_without_scope_fields_and_local_text_keeps_raw_text():
    d = capas.decide_external_claim(_p(LOCAL))
    assert d["verdict"] == "ACCEPT" and d["licensed_claim"] == LOCAL
