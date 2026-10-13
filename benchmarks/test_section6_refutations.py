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

def test_bounded_scope_with_bounded_text_accepts_when_quantifier_declared():
    # since run 6 the bounded path needs the declaration; without it -> REWRITE (see test_run6_* below)
    assert capas.decide_external_claim(_p(BOUNDED_TEXT, "bounded", text_quantifier="bounded"))["verdict"] == "ACCEPT"
    assert capas.decide_external_claim(_p(BOUNDED_TEXT, "bounded"))["verdict"] == "REWRITE"

def test_universal_text_with_uniform_bound_proven_accepts():
    assert capas.decide_external_claim(_p(UNIVERSAL_TEXT, "universal", uniform_bound_proven=True))["verdict"] == "ACCEPT"

def test_spanish_universal_markers_are_caught():
    t = "Teorema: la identidad vale para cualquier escritura de la fórmula, sin restricción de alcance."
    assert capas.decide_external_claim(_p(t, "bounded"))["verdict"] == "REWRITE"


# --- Run 6 (xAI, 2026-10-13) refuted C6-02 AGAIN: UNIVERSAL_TEXT_RE is a closed list; "Theorem: holds universally.",
# "vale para cualesquiera n", "for arbitrary n", "in all cases", "whatever writing", "for n = 1, 2, 3, ..." passed with a
# declared bounded scope and no uniform bound. A regex over prose cannot be complete. Structural closure: a bounded
# declared scope without a uniform bound can ACCEPT only if the coder DECLARES text_quantifier="bounded"; missing ->
# REWRITE (declare it); "universal" -> REWRITE; declared bounded but the text visibly universal -> REWRITE (contradiction).
RUN6_TEXTS = ["Theorem: holds universally.", "Teorema: vale para cualesquiera n.", "Theorem: holds for arbitrary n.",
              "vale para cada n", "vale siempre", "vale en general", "forall n the identity holds", "for infinitely many writings",
              "without restriction", "with no restrictions", "irrespective of the writing", "whichever writing", "whatever writing",
              "in all cases", "universally true", "the result is universal", "for arbitrary order", "no bound on the order",
              "for n = 1, 2, 3, ...", "over the whole domain", "for the entire family", "Lemma: an identity (scope unstated)."]

def test_run6_bounded_scope_without_text_quantifier_never_accepts():
    for t in RUN6_TEXTS:
        for sc in ("bounded", "finite"):
            d = capas.decide_external_claim(_p(t, sc))
            assert d["verdict"] == "REWRITE", (t, sc, d["verdict"])
            assert d["licensed_claim"] != t

def test_declared_bounded_text_quantifier_accepts_bounded_text():
    d = capas.decide_external_claim(_p(BOUNDED_TEXT, "bounded", text_quantifier="bounded"))
    assert d["verdict"] == "ACCEPT"

def test_declared_universal_text_quantifier_rewrites():
    assert capas.decide_external_claim(_p(BOUNDED_TEXT, "bounded", text_quantifier="universal"))["verdict"] == "REWRITE"

def test_declared_bounded_but_text_visibly_universal_is_a_contradiction():
    d = capas.decide_external_claim(_p(UNIVERSAL_TEXT, "bounded", text_quantifier="bounded"))
    assert d["verdict"] == "REWRITE" and "contradict" in d["reason"].lower()

def test_uniform_bound_proven_still_licenses_universal_text():
    assert capas.decide_external_claim(_p("Theorem: holds universally.", "universal", uniform_bound_proven=True))["verdict"] == "ACCEPT"


# --- Run 7 (xAI, 2026-10-13), by reading (it could not execute): "Theorem: holds universally." with text_quantifier
# declared "bounded" falls to ACCEPT because UNIVERSAL_TEXT_RE lacks 'universally'. The structural rule carries the
# weight (missing declaration -> REWRITE); the regex is the CONTRADICTION guard, so it must at least cover every
# universal marker an auditor has already produced. Declared bounded + any run-6 text -> REWRITE (contradiction).
def test_run7_declared_bounded_but_run6_universal_texts_are_contradictions():
    for t in RUN6_TEXTS[:-1]:   # the last one is the genuinely scope-unstated lemma
        d = capas.decide_external_claim(_p(t, "bounded", text_quantifier="bounded"))
        assert d["verdict"] == "REWRITE" and "contradict" in d["reason"].lower(), (t, d["verdict"], d["reason"][:80])

def test_scope_unstated_lemma_with_declared_bounded_quantifier_accepts():
    assert capas.decide_external_claim(_p("Lemma: an identity (scope unstated).", "bounded", text_quantifier="bounded"))["verdict"] == "ACCEPT"
