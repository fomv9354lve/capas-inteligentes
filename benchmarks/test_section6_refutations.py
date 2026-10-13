# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""Refutations found by §6 counter-signatures (other model families), frozen as tests so they cannot return.
Run 2, xAI grok-4.7, 2026-10-13 — C6-02 REFUTADO: proof_admissibility ACCEPTed a text saying
"Theorem ... for every writing, with no restriction on scope" because the EVIDENCE declared
claim_scope "bounded " (whitespace-normalised to the allowlist) with uniform_bound_proven False.
The declared scope contradicted the text and the gate licensed the text. Same hole as X4-008."""
import capas

def _p(text, scope, **ev):
    e = {"claim_scope": scope, "steps_all_valid": True, "load_bearing_step_identified": True,
         "uniform_bound_proven": False, "independent_reproduction_pass": True}; e.update(ev)
    return {"schema_version": capas.CAPAS_CLAIM_SCHEMA_VERSION,
            "claim": {"id": "c602", "type": "proof_admissibility", "text": text}, "evidence": e}

UNIVERSAL_TEXT = "Theorem: the identity holds for every writing of the formula, with no restriction on scope."
BOUNDED_TEXT = "Lemma: the identity holds for the 12 writings enumerated in Table 2."

def test_c602_exact_counterexample_no_longer_accepts():
    for scope in ("bounded ", "bounded\t", "bounded\n", "bounded\xa0", "bounded"):
        d = capas.decide_external_claim(_p(UNIVERSAL_TEXT, scope))
        assert d["verdict"] == "REWRITE", (repr(scope), d["verdict"])
        assert "scope" in d["reason"].lower() and d["licensed_claim"] != UNIVERSAL_TEXT

def test_bounded_scope_with_bounded_text_still_accepts():
    assert capas.decide_external_claim(_p(BOUNDED_TEXT, "bounded"))["verdict"] == "ACCEPT"

def test_universal_text_with_uniform_bound_proven_accepts():
    assert capas.decide_external_claim(_p(UNIVERSAL_TEXT, "universal", uniform_bound_proven=True))["verdict"] == "ACCEPT"

def test_spanish_universal_markers_are_caught():
    t = "Teorema: la identidad vale para cualquier escritura de la fórmula, sin restricción de alcance."
    assert capas.decide_external_claim(_p(t, "bounded"))["verdict"] == "REWRITE"
