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
    # X4-001's shape ("k-casi-independiente") was caught only by the weak marker '-independiente'; since the 07:15 cost fix
    # weak markers alone do not trigger, so this one is a DECLARED loss (1 bad) traded for 4 good claims kept in ACCEPT.
    t2 = "La curtosis por realización es monótona en el margen y k-casi-independiente ⇒ es un estimador del margen de estabilidad."
    assert capas.decide_external_claim(_p(t2, abs_error=0.07, tolerance=0.1, n_points=3))["verdict"] == "ACCEPT"

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

def test_accept_without_scope_fields_and_local_text_licenses_evidence_not_raw_text():
    # External audit 2026-10-14: ACCEPT never licenses the raw sentence; it licenses the declared evidence, annotated.
    d = capas.decide_external_claim(_p(LOCAL))
    assert d["verdict"] == "ACCEPT" and d["licensed_claim"].endswith(LOCAL) and d["licensed_claim"].startswith("[licensed on the declared")
    assert d["text_licensed_as_written"] is False


# --- Ginibre convention (a), 2026-10-13: a closed form sustained by chi2/dof + rivals is coded in test_statistic on the
# exact_model_solution itself (the engine used to read test_statistic only on statistical_confidence and ignored it here).
# rivals decide ACCEPT-vs-REJECT (the claimed form must beat every declared rival); absolute fit decides ACCEPT-vs-REWRITE
# (best of the rivals but not consistent in absolute terms = X4-026's honest reading: SE underestimated at low R).
def _ts(**ts):
    return _p(LOCAL, abs_error=0.5, tolerance=2.0, tolerance_unit="SE", n_replicates=200, test_statistic=ts)

def test_chi2_best_of_rivals_and_consistent_accepts():
    d = capas.decide_external_claim(_ts(kind="chi2_dof", value=1.1, dof=6, rivals=[1027, 44030]))
    assert d["verdict"] == "ACCEPT" and "rival" in d["reason"].lower()

def test_chi2_best_of_rivals_but_inconsistent_rewrites():
    d = capas.decide_external_claim(_ts(kind="chi2_dof", value=4.23, dof=6, rivals=[1027, 44030]))   # X4-026 shape
    assert d["verdict"] == "REWRITE" and "absolute" in d["reason"].lower()

def test_chi2_rival_fits_better_rejects():
    d = capas.decide_external_claim(_ts(kind="chi2_dof", value=4.23, dof=6, rivals=[1.2, 44030]))
    assert d["verdict"] == "REJECT"

def test_chi2_no_rivals_inconsistent_rejects_and_consistent_accepts():
    assert capas.decide_external_claim(_ts(kind="chi2_dof", value=4.23, dof=6))["verdict"] == "REJECT"
    assert capas.decide_external_claim(_ts(kind="chi2_dof", value=0.9, dof=6))["verdict"] == "ACCEPT"

def test_chi2_missing_dof_holds():
    assert capas.decide_external_claim(_ts(kind="chi2_dof", value=4.23))["verdict"] == "HOLD"


# --- Ginibre trap (CRIT_FINO, cell CA): each model fitted with free alpha, beta on the residual. principal chi2/dof 0.74
# with its constraint at z +1.20; rival_limite chi2/dof 0.40 but with alpha at z -64.1 — the free parameter absorbed the
# difference. A copied chi2/dof would REJECT the correct law. Rule: rivals are chi2/dof WITH the claim's constraint
# imposed; a rival given as {chi2_dof, z_constraint} with |z| > 4 is self-refuting and does not count as a rival.
def test_rival_whose_constraint_is_rejected_does_not_count():
    d = capas.decide_external_claim(_ts(kind="chi2_dof", value=0.74, dof=6, z_constraint=1.20,
                                        rivals=[{"chi2_dof": 0.40, "z_constraint": -64.1}]))
    assert d["verdict"] == "ACCEPT" and "self-refuting" in d["reason"].lower(), d["reason"]

def test_rival_with_consistent_constraint_counts():
    d = capas.decide_external_claim(_ts(kind="chi2_dof", value=0.74, dof=6, rivals=[{"chi2_dof": 0.40, "z_constraint": 0.3}]))
    assert d["verdict"] == "REJECT"

def test_principal_own_constraint_rejected():
    d = capas.decide_external_claim(_ts(kind="chi2_dof", value=0.74, dof=6, z_constraint=-64.1))
    assert d["verdict"] == "REJECT" and "constraint" in d["reason"].lower()

def test_rival_dict_without_chi2_holds():
    assert capas.decide_external_claim(_ts(kind="chi2_dof", value=0.74, dof=6, rivals=[{"z_constraint": 0.3}]))["verdict"] == "HOLD"


# --- Cost fix (Osvaldo, 2026-10-13 07:15): the scope-in-text rule fired on WEAK nouns ('ventana', 'régimen', 'siempre',
# '-independiente') and cost 5 good claims for 2 bad on X1-X5 (post-hoc). Weak markers alone no longer trigger; only a
# quantifier or an explicit generalisation does ('para todo', 'for all/every/any', '∀', 'funciona en', 'holds for/over',
# 'en general', 'independiente de'). POST-HOC on X1-X5; the Atlas blind corpus (tag atlas-ciego-v3) tests it out of sample.
WEAK_ONLY = ["H estima C(x,d): en d=0 los pulls son +0.01 y −0.29 SE; dentro del dominio d≤0.6 χ²/dof=1.39 sobre 6 celdas.",   # 'ventana'-type
             "OLS con n mayor que p es otro régimen: C_p=p·E[σ²] se duplica al duplicar p.",
             "Ley individual con f=e_j (τ=0): P(signo igual)−½ predice 12 puntos fuera de muestra, k-independiente."]
STRONG = ["La corrección funciona en la ventana útil (d/borde 1.1–1.3).", "Universalidad de entradas iid: t5, t3 y Rademacher coinciden con el gaussiano.", "ψ es invariante bajo Π↦SΠ para todo S∈GL(m).",
          "The identity holds for every writing.", "El resultado vale en general.", "independiente de k para k ≥ 64"]

def test_weak_markers_alone_do_not_trigger_scope_rule():
    for t in WEAK_ONLY:
        d = capas.decide_external_claim(_p(t))
        assert d["verdict"] == "ACCEPT", (t, d["verdict"], d["reason"][:80])

def test_strong_markers_still_trigger():
    for t in STRONG:
        d = capas.decide_external_claim(_p(t))
        assert d["verdict"] == "REWRITE" and "scope" in d["reason"].lower(), (t, d["verdict"])


# --- Atlas phase 2(a): a joint chi2 criterion (one test over the cells, no per-cell tolerance) is a complete
# exact_model_solution on its own — abs_error/tolerance are not required when test_statistic carries the test.
def _chi2only(value, dof, **extra):
    return {"schema_version": capas.CAPAS_CLAIM_SCHEMA_VERSION,
            "claim": {"id": "c", "type": "exact_model_solution", "text": "Falsador conjunto chi2 sobre las celdas pre-registradas."},
            "evidence": {"test_statistic": {"kind": "chi2", "value": value, "dof": dof, "alpha": 0.05}, "n_replicates": 6, **extra}}

def test_joint_chi2_alone_is_judged():
    assert capas.decide_external_claim(_chi2only(83.354, 5))["verdict"] == "REJECT"     # mirror_ext v5: 83.35 > 11.07
    assert capas.decide_external_claim(_chi2only(9.112, 3))["verdict"] == "REJECT"      # rep12 v8: 9.11 > 7.815
    assert capas.decide_external_claim(_chi2only(0.933, 3))["verdict"] == "ACCEPT"      # regime S1: 0.93 < 7.815

def test_chi2_without_dof_still_holds():
    p = _chi2only(0.933, 3); del p["evidence"]["test_statistic"]["dof"]
    assert capas.decide_external_claim(p)["verdict"] == "HOLD"


# --- LIVE BUG (deploy 2026-10-13 11:40): the container has no scipy, so the joint chi2 p-value was None and the stage
# fell through to ACCEPT (83.35 on 5 dof accepted live). Without scipy the joint test must HOLD — never fail open.
def test_joint_chi2_without_scipy_holds(monkeypatch):
    import builtins
    real_import = builtins.__import__
    def fake(name, *a, **k):
        if name.startswith("scipy"): raise ImportError("no scipy")
        return real_import(name, *a, **k)
    monkeypatch.setattr(builtins, "__import__", fake)
    d = capas.decide_external_claim(_chi2only(83.354, 5))
    assert d["verdict"] == "HOLD" and "scipy" in d["reason"].lower(), d["reason"]
