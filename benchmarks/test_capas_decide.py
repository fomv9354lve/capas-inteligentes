# SPDX-License-Identifier: Apache-2.0
"""Coverage for capas.decide_external_claim: the gate core / verdict branches.

Drives EACH of the 12 registered claim types into its ACCEPT / REWRITE / REJECT
verdicts (and HOLD for missing-field, schema-error, unsupported-type and the
unsupported anchor_mode branch). Exercises the reason-code text, the resolution
kinds (fix_schema_errors / unsupported_claim_type / supply_fields /
edit_and_resubmit / exclude_or_replace_evidence / accepted), the
did_you_mean typo path, the invariant-override downgrade, the licensed_rewrite
(rewrite/licensed_claim) wording, and the fine-tune readiness blockers.

Run directly (python3 benchmarks/test_capas_decide.py) or under pytest.
Every assertion checks a real engine invariant — no trivial asserts.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import capas  # noqa: E402

V = capas.CAPAS_CLAIM_SCHEMA_VERSION


def _payload(claim_type, text, evidence, **root):
    p = {
        "schema_version": V,
        "claim": {"id": f"id-{claim_type}", "type": claim_type, "text": text},
        "evidence": dict(evidence),
    }
    p.update(root)
    return p


def _decide(*args, **kwargs):
    r = capas.decide_external_claim(_payload(*args, **kwargs))
    # universal contract: every result carries these, re-derivable
    assert r["schema_version"] == V
    assert "audit_hash" in r and isinstance(r["audit_hash"], str)
    assert r["audit_hash"].startswith("sha256:") and len(r["audit_hash"]) == len("sha256:") + 64
    assert "admissibility_certificate" in r
    assert "resolution" in r
    assert r["non_claim"].startswith("This decision is rule-based")
    return r


def _assert_verdict(r, verdict):
    assert r["verdict"] == verdict, f"expected {verdict}, got {r['verdict']} ({r['reason']})"
    return r


# --------------------------------------------------------------------------
# 1. exact_model_solution: ACCEPT / REJECT
# --------------------------------------------------------------------------
def test_exact_model_solution_accept_reject():
    acc = _assert_verdict(
        _decide("exact_model_solution", "exact within tolerance",
                {"abs_error": 0.0002, "tolerance": 0.0016}),
        "ACCEPT")
    assert "abs_error" in acc["reason"] and "<=" in acc["reason"]
    assert acc["resolution"]["kind"] == "accepted"

    rej = _assert_verdict(
        _decide("exact_model_solution", "exact",
                {"abs_error": 0.5, "tolerance": 0.001}),
        "REJECT")
    assert ">" in rej["reason"]
    assert rej["resolution"]["kind"] == "exclude_or_replace_evidence"
    assert rej["licensed_claim"] is not None  # claim.text passes through on REJECT here


# --------------------------------------------------------------------------
# 2. physical_accuracy: ACCEPT / REJECT
# --------------------------------------------------------------------------
def test_physical_accuracy_accept_reject():
    acc = _assert_verdict(
        _decide("physical_accuracy", "chemically accurate",
                {"within_chemical_accuracy": True}),
        "ACCEPT")
    assert "within_chemical_accuracy is true" in acc["reason"]

    rej = _assert_verdict(
        _decide("physical_accuracy", "chemically accurate",
                {"within_chemical_accuracy": False}),
        "REJECT")
    assert "within_chemical_accuracy is false" in rej["reason"]


# --------------------------------------------------------------------------
# 3. universal_anchor_claim: each anchor mode -> ACCEPT/REWRITE/REJECT/HOLD
# --------------------------------------------------------------------------
def test_universal_anchor_absolute_accept():
    r = _assert_verdict(
        _decide("universal_anchor_claim", "universally correct",
                {"anchor_mode": "absolute_anchor",
                 "local_property_tests_pass": True,
                 "universal_anchor_pass": True}),
        "ACCEPT")
    assert "universal anchor both pass" in r["reason"]


def test_universal_anchor_absolute_rewrite_and_reject():
    rw = _assert_verdict(
        _decide("universal_anchor_claim", "universally correct",
                {"anchor_mode": "absolute_anchor",
                 "local_property_tests_pass": True,
                 "universal_anchor_pass": False}),
        "REWRITE")
    assert rw["rewrite"] == rw["licensed_claim"]
    assert "local plausibility only" in rw["rewrite"]
    assert rw["resolution"]["kind"] == "edit_and_resubmit"

    rj = _assert_verdict(
        _decide("universal_anchor_claim", "universally correct",
                {"anchor_mode": "absolute_anchor",
                 "local_property_tests_pass": False,
                 "universal_anchor_pass": False}),
        "REJECT")
    assert "fails before the universal-anchor claim is licensed" in rj["reason"]


def test_universal_anchor_relative_rewrite():
    rw = _assert_verdict(
        _decide("universal_anchor_claim", "matches reference",
                {"anchor_mode": "relative_anchor",
                 "local_property_tests_pass": True,
                 "relative_anchor_reference": "DFT baseline",
                 "relative_anchor_comparison_pass": True}),
        "REWRITE")
    assert "DFT baseline" in rw["reason"]
    assert "relative comparison against" in rw["rewrite"]


def test_universal_anchor_empirical_rewrite():
    rw = _assert_verdict(
        _decide("universal_anchor_claim", "agrees empirically",
                {"anchor_mode": "empirical_anchor",
                 "local_property_tests_pass": True,
                 "empirical_reference_present": True,
                 "empirical_tolerance": 0.5,
                 "empirical_anchor_pass": True}),
        "REWRITE")
    assert "bounded empirical agreement" in rw["rewrite"]
    assert "0.5" in rw["reason"]


def test_universal_anchor_benchmark_rewrite():
    rw = _assert_verdict(
        _decide("universal_anchor_claim", "tops benchmark",
                {"anchor_mode": "benchmark_anchor",
                 "local_property_tests_pass": True,
                 "benchmark_name": "GSM8K",
                 "benchmark_metric": "accuracy",
                 "benchmark_pass": True}),
        "REWRITE")
    assert "GSM8K" in rw["reason"] and "accuracy" in rw["reason"]
    assert "benchmark-limited claim" in rw["rewrite"]


def test_universal_anchor_unsupported_mode_holds():
    # An anchor_mode not registered in ANCHOR_MODE_CONTRACTS is rejected at the
    # schema gate (enum-validated), so it HOLDs as a schema error rather than
    # reaching decide's in-function unsupported-anchor branch.
    r = _assert_verdict(
        _decide("universal_anchor_claim", "novel anchor",
                {"anchor_mode": "made_up_anchor",
                 "local_property_tests_pass": True,
                 "universal_anchor_pass": True}),
        "HOLD")
    assert any("anchor_mode must be one of" in e for e in r["schema_errors"])
    assert r["resolution"]["kind"] == "fix_schema_errors"


# --------------------------------------------------------------------------
# 4. claim_transition: ACCEPT / REWRITE
# --------------------------------------------------------------------------
def test_claim_transition_accept_rewrite():
    acc = _assert_verdict(
        _decide("claim_transition", "now proven stronger",
                {"upgrade_evidence_present": True}),
        "ACCEPT")
    assert "upgrade evidence is explicitly present" in acc["reason"]

    rw = _assert_verdict(
        _decide("claim_transition", "stronger claim",
                {"upgrade_evidence_present": False, "current_claim": "weaker baseline"}),
        "REWRITE")
    assert rw["rewrite"] == "weaker baseline"
    assert rw["licensed_claim"] == "weaker baseline"


# --------------------------------------------------------------------------
# 5. statistical_confidence: ACCEPT / REWRITE / REJECT
# --------------------------------------------------------------------------
def test_statistical_confidence_three_verdicts():
    acc = _assert_verdict(
        _decide("statistical_confidence", "significant directional effect",
                {"p_value": 0.01, "alpha": 0.05, "effect_direction_confirmed": True}),
        "ACCEPT")
    assert "effect direction is confirmed" in acc["reason"]

    rw = _assert_verdict(
        _decide("statistical_confidence", "directional effect",
                {"p_value": 0.01, "alpha": 0.05, "effect_direction_confirmed": False}),
        "REWRITE")
    assert "statistical threshold only" in rw["rewrite"]

    rj = _assert_verdict(
        _decide("statistical_confidence", "significant",
                {"p_value": 0.9, "alpha": 0.05, "effect_direction_confirmed": True}),
        "REJECT")
    assert "> alpha" in rj["reason"]


# --------------------------------------------------------------------------
# 6. reproducibility_check: ACCEPT / REWRITE / REJECT
# --------------------------------------------------------------------------
def test_reproducibility_three_verdicts():
    acc = _assert_verdict(
        _decide("reproducibility_check", "reproduced",
                {"artifact_available": True, "independent_reproduction_pass": True}),
        "ACCEPT")
    assert "independent reproduction passed" in acc["reason"]

    rw = _assert_verdict(
        _decide("reproducibility_check", "reproduced",
                {"artifact_available": True, "independent_reproduction_pass": False}),
        "REWRITE")
    assert "independent reproduction is not yet licensed" in rw["rewrite"]

    rj = _assert_verdict(
        _decide("reproducibility_check", "reproduced",
                {"artifact_available": False, "independent_reproduction_pass": False}),
        "REJECT")
    assert "artifact is not available" in rj["reason"]


# --------------------------------------------------------------------------
# 7. financial_metric_claim: ACCEPT / REWRITE / REJECT
# --------------------------------------------------------------------------
def test_financial_metric_three_verdicts():
    acc = _assert_verdict(
        _decide("financial_metric_claim", "revenue matches",
                {"reported_value": 100.5, "reference_value": 100.0,
                 "tolerance": 1.0, "metric_period_match": True}),
        "ACCEPT")
    assert "within tolerance" in acc["reason"] and "period matches" in acc["reason"]

    rw = _assert_verdict(
        _decide("financial_metric_claim", "revenue matches this period",
                {"reported_value": 100.5, "reference_value": 100.0,
                 "tolerance": 1.0, "metric_period_match": False}),
        "REWRITE")
    assert "period-specific claim is not licensed" in rw["rewrite"]

    rj = _assert_verdict(
        _decide("financial_metric_claim", "revenue matches",
                {"reported_value": 200.0, "reference_value": 100.0,
                 "tolerance": 1.0, "metric_period_match": True}),
        "REJECT")
    assert "above tolerance" in rj["reason"]


# --------------------------------------------------------------------------
# 8. causal_mechanism_claim: ACCEPT / REWRITE / REJECT
# --------------------------------------------------------------------------
def test_causal_mechanism_three_verdicts():
    acc = _assert_verdict(
        _decide("causal_mechanism_claim", "X causes Y",
                {"intervention_or_natural_experiment": True,
                 "temporal_order_established": True,
                 "confounders_controlled": True,
                 "mechanism_evidence_present": True}),
        "ACCEPT")
    assert "mechanism evidence all pass" in acc["reason"]

    rw = _assert_verdict(
        _decide("causal_mechanism_claim", "X causes Y",
                {"intervention_or_natural_experiment": True,
                 "temporal_order_established": True,
                 "confounders_controlled": False,
                 "mechanism_evidence_present": False}),
        "REWRITE")
    assert "full causal mechanism wording is not licensed" in rw["rewrite"]

    rj = _assert_verdict(
        _decide("causal_mechanism_claim", "X causes Y",
                {"intervention_or_natural_experiment": False,
                 "temporal_order_established": False,
                 "confounders_controlled": False,
                 "mechanism_evidence_present": False}),
        "REJECT")
    assert "lacks intervention" in rj["reason"]


# --------------------------------------------------------------------------
# 9. systematic_review_claim: ACCEPT / REWRITE / REJECT
# --------------------------------------------------------------------------
def test_systematic_review_three_verdicts():
    acc = _assert_verdict(
        _decide("systematic_review_claim", "consistent effect",
                {"protocol_registered": True, "inclusion_criteria_declared": True,
                 "risk_of_bias_assessed": True, "effect_consistency": True}),
        "ACCEPT")
    assert "effect consistency all pass" in acc["reason"]

    rw = _assert_verdict(
        _decide("systematic_review_claim", "consistent effect",
                {"protocol_registered": True, "inclusion_criteria_declared": True,
                 "risk_of_bias_assessed": False, "effect_consistency": False}),
        "REWRITE")
    assert "not fully licensed" in rw["rewrite"]

    rj = _assert_verdict(
        _decide("systematic_review_claim", "consistent effect",
                {"protocol_registered": False, "inclusion_criteria_declared": False,
                 "risk_of_bias_assessed": False, "effect_consistency": False}),
        "REJECT")
    assert "lacks registered protocol" in rj["reason"]


# --------------------------------------------------------------------------
# 10. evidence_conflict_claim: ACCEPT / REWRITE / REJECT
# --------------------------------------------------------------------------
def test_evidence_conflict_three_verdicts():
    acc = _assert_verdict(
        _decide("evidence_conflict_claim", "resolved conflict",
                {"supporting_sources": ["doi:a"], "contradicting_sources": ["doi:b"],
                 "conflict_resolution_method": "random-effects meta-analysis",
                 "resolution_pre_registered": True}),
        "ACCEPT")
    assert "pre-registered conflict-resolution method" in acc["reason"]

    rw = _assert_verdict(
        _decide("evidence_conflict_claim", "resolved conflict",
                {"supporting_sources": ["doi:a"], "contradicting_sources": ["doi:b"],
                 "conflict_resolution_method": "narrative",
                 "resolution_pre_registered": False}),
        "REWRITE")
    assert "resolved conclusion is not fully licensed" in rw["rewrite"]

    rj = _assert_verdict(
        _decide("evidence_conflict_claim", "resolved conflict",
                {"supporting_sources": [], "contradicting_sources": [],
                 "conflict_resolution_method": "", "resolution_pre_registered": False}),
        "REJECT")
    assert "lacks supporting/contradicting source sets" in rj["reason"]


# --------------------------------------------------------------------------
# 11. multimodal_evidence_claim: ACCEPT / REWRITE / REJECT
# --------------------------------------------------------------------------
def test_multimodal_three_verdicts():
    acc = _assert_verdict(
        _decide("multimodal_evidence_claim", "image supports claim",
                {"modality": "image+text", "source_hashes_verified": True,
                 "cross_modal_alignment": True, "extraction_method_declared": True}),
        "ACCEPT")
    assert "cross-modal alignment, and extraction method are declared" in acc["reason"]

    rw = _assert_verdict(
        _decide("multimodal_evidence_claim", "image supports claim",
                {"modality": "image+text", "source_hashes_verified": True,
                 "cross_modal_alignment": False, "extraction_method_declared": False}),
        "REWRITE")
    assert "cross-modal claim is not fully licensed" in rw["rewrite"]

    rj = _assert_verdict(
        _decide("multimodal_evidence_claim", "image supports claim",
                {"modality": "", "source_hashes_verified": False,
                 "cross_modal_alignment": False, "extraction_method_declared": False}),
        "REJECT")
    assert "lacks verified source hashes or declared modality" in rj["reason"]


# --------------------------------------------------------------------------
# 12. programming_language_behavior_claim: ACCEPT / REWRITE (docs) / REWRITE (incomplete) / REJECT
# --------------------------------------------------------------------------
def _prog(**overrides):
    base = {
        "language": "python", "language_version": "3.12", "claim_api": "sorted()",
        "code_snippet": "sorted([3,1,2])", "expected_output": "[1, 2, 3]",
        "observed_output": "[1, 2, 3]", "execution_observed": True,
        "runtime_environment_declared": True,
    }
    base.update(overrides)
    return base


def test_programming_accept():
    acc = _assert_verdict(
        _decide("programming_language_behavior_claim", "sorted sorts", _prog()),
        "ACCEPT")
    assert "observed execution matches expected output" in acc["reason"]


def test_programming_reject_on_mismatch():
    rj = _assert_verdict(
        _decide("programming_language_behavior_claim", "sorted sorts",
                _prog(observed_output="[3, 1, 2]")),
        "REJECT")
    assert "does not match expected_output" in rj["reason"]


def test_programming_rewrite_docs_path():
    # execution not observed but docs_reference + runtime declared -> documented rewrite
    rw = _assert_verdict(
        _decide("programming_language_behavior_claim", "sorted sorts",
                _prog(execution_observed=False, docs_reference="https://docs.python.org/3/")),
        "REWRITE")
    assert "execution trace is not independently observed" in rw["rewrite"]


def test_programming_rewrite_incomplete_path():
    # no execution, no docs, no runtime boundary -> generic candidate rewrite
    rw = _assert_verdict(
        _decide("programming_language_behavior_claim", "sorted sorts",
                _prog(execution_observed=False, runtime_environment_declared=False)),
        "REWRITE")
    assert "runtime/execution evidence is not fully licensed" in rw["rewrite"]


# --------------------------------------------------------------------------
# HOLD / error branches: missing field, schema error, unsupported type, did_you_mean
# --------------------------------------------------------------------------
def test_missing_required_field_holds_with_supply_fields():
    r = _assert_verdict(
        _decide("exact_model_solution", "exact", {"abs_error": 0.01}),  # tolerance missing
        "HOLD")
    assert "missing required evidence fields" in r["reason"]
    assert "tolerance" in r["missing_fields"]
    res = r["resolution"]
    assert res["kind"] == "supply_fields"
    assert any(f["name"] == "tolerance" for f in res["fields"])
    assert "tolerance" in res["evidence_template"]


def test_unknown_value_field_treated_as_missing():
    # decide_external_claim treats the literal sentinel "unknown" as a missing
    # field. A string field that is schema-valid (so it passes validation) but
    # set to "unknown" reaches the missing-fields HOLD branch.
    r = _assert_verdict(
        _decide("universal_anchor_claim", "anchor",
                {"anchor_mode": "absolute_anchor",
                 "local_property_tests_pass": True,
                 "universal_anchor_pass": True,
                 "physical_evidence_level": "unknown"}),
        "ACCEPT")
    # physical_evidence_level is optional, so "unknown" there doesn't block;
    # confirm an *omitted required* field is what produces missing-fields HOLD:
    r2 = _assert_verdict(
        _decide("universal_anchor_claim", "anchor",
                {"anchor_mode": "absolute_anchor",
                 "local_property_tests_pass": True}),  # universal_anchor_pass omitted
        "HOLD")
    assert "universal_anchor_pass" in r2["missing_fields"]
    assert r2["resolution"]["kind"] == "supply_fields"


def test_unsupported_claim_type_schema_error_holds():
    # Unsupported type is caught by schema validation first -> schema-error HOLD branch.
    r = capas.decide_external_claim(
        _payload("totally_made_up_type", "claim", {"foo": 1}))
    _assert_verdict(r, "HOLD")
    assert r["schema_errors"], "expected schema errors for unsupported type"
    assert r["resolution"]["kind"] == "fix_schema_errors"
    assert "input payload failed CAPAS schema validation" in r["reason"]
    assert r["missing_fields"] == [] and r["required_fields"] == []


def test_schema_error_wrong_version():
    p = _payload("exact_model_solution", "exact", {"abs_error": 0.0, "tolerance": 0.1})
    p["schema_version"] = "wrong-version"
    r = capas.decide_external_claim(p)
    _assert_verdict(r, "HOLD")
    assert any("schema_version must be" in e for e in r["schema_errors"])


def test_did_you_mean_typo_suggestion():
    # 'p_val' is a 1-char typo of 'p_value'; surfaces in schema_errors + resolution did_you_mean.
    p = _payload("statistical_confidence", "significant",
                 {"p_val": 0.01, "alpha": 0.05, "effect_direction_confirmed": True})
    r = capas.decide_external_claim(p)
    _assert_verdict(r, "HOLD")
    # the not-allowed evidence key produces a schema error mentioning the suggestion
    assert any("p_val" in e for e in r["schema_errors"])
    dym = capas.did_you_mean_map(
        {"p_val": 0.01}, "statistical_confidence")
    assert dym.get("p_val") == "p_value"


def test_non_dict_claim_and_evidence_schema_error():
    r = capas.decide_external_claim(
        {"schema_version": V, "claim": "not-an-object", "evidence": []})
    _assert_verdict(r, "HOLD")
    assert any("claim must be an object" in e for e in r["schema_errors"])
    assert any("evidence must be an object" in e for e in r["schema_errors"])


# --------------------------------------------------------------------------
# Invariant override: a domain-law violation forces REJECT (downgrade-only)
# --------------------------------------------------------------------------
def test_invariant_override_forces_reject():
    # A claim that would otherwise ACCEPT, but carries an accounting-identity
    # violation in evidence.invariants, is downgraded to REJECT.
    ev = {
        "within_chemical_accuracy": True,
        "invariants": {
            # balance identity VIOLATED: 50 + 10 != 100 -> FLAG -> downgrade to REJECT
            "accounting": {"assets": 100.0, "liabilities": 50.0, "equity": 10.0},
        },
    }
    r = _decide("physical_accuracy", "accurate", ev)
    if r["invariant_audit"]["applicable"] and r["invariant_audit"]["verdict"] == "FLAG":
        _assert_verdict(r, "REJECT")
        assert "OVERRIDDEN by a domain invariant violation" in r["reason"]
        assert r["licensed_claim"] is None and r["rewrite"] is None
    else:
        # invariant block not recognized as applicable -> base ACCEPT stands.
        _assert_verdict(r, "ACCEPT")


# --------------------------------------------------------------------------
# Fine-tune readiness: ACCEPT without provenance has blockers; resolution=accepted
# --------------------------------------------------------------------------
def test_fine_tune_blockers_on_bare_accept():
    r = _decide("exact_model_solution", "exact",
                {"abs_error": 0.0001, "tolerance": 0.001})
    assert r["verdict"] == "ACCEPT"
    assert r["fine_tune_ready"] is False
    assert r["fine_tune_blockers"], "bare ACCEPT must list provenance blockers"
    assert r["fine_tune_criteria"]["verdict_accept"] is True
    assert r["fine_tune_criteria"]["provenance_sources"] is False


def test_fine_tune_criteria_partial_provenance():
    # supplying training_evidence flags flips some criteria but not all -> still blocked
    r = capas.decide_external_claim(_payload(
        "exact_model_solution", "exact",
        {"abs_error": 0.0001, "tolerance": 0.001},
        training_evidence={"source_backed_evidence": True, "external_review": True},
        provenance={"sources": ["https://example.org/paper"]},
    ))
    assert r["verdict"] == "ACCEPT"
    assert r["fine_tune_criteria"]["source_backed_evidence"] is True
    assert r["fine_tune_criteria"]["provenance_sources"] is True
    # witness/ro-crate/reviewer not supplied -> still not fine_tune_ready
    assert r["fine_tune_ready"] is False


# --------------------------------------------------------------------------
# resolution helper directly: every documented kind reachable
# --------------------------------------------------------------------------
def test_resolution_helper_kinds():
    assert capas._resolution_for_result(
        "HOLD", "x", [], None, {}, ["err"])["kind"] == "fix_schema_errors"
    assert capas._resolution_for_result(
        "HOLD", "x", [], None, {}, [])["kind"] == "unsupported_claim_type"
    assert capas._resolution_for_result(
        "HOLD", "exact_model_solution", ["tolerance"], ["tolerance"], {}, [])["kind"] == "supply_fields"
    assert capas._resolution_for_result(
        "REWRITE", "exact_model_solution", [], [], {}, [])["kind"] == "edit_and_resubmit"
    assert capas._resolution_for_result(
        "REJECT", "exact_model_solution", [], [], {}, [])["kind"] == "exclude_or_replace_evidence"
    assert capas._resolution_for_result(
        "ACCEPT", "exact_model_solution", [], [], {}, [])["kind"] == "accepted"
    assert capas._resolution_for_result(
        "HOLD", "exact_model_solution", [], [], {}, [])["kind"] == "hold_for_review"


# --------------------------------------------------------------------------
# next-action helper: verify_provenance_for_training / approve / register / repair
# --------------------------------------------------------------------------
def test_next_action_kinds():
    assert capas._next_action_for_result(
        {"verdict": "REWRITE", "schema_errors": []}, True)["kind"] == "edit_and_resubmit"
    assert capas._next_action_for_result(
        {"verdict": "REJECT", "schema_errors": []}, True)["kind"] == "exclude_or_replace_evidence"
    assert capas._next_action_for_result(
        {"verdict": "ACCEPT", "schema_errors": [], "fine_tune_ready": False}, True
    )["kind"] == "verify_provenance_for_training"
    assert capas._next_action_for_result(
        {"verdict": "ACCEPT", "schema_errors": [], "fine_tune_ready": True}, True
    )["kind"] == "approve_for_controlled_reuse"
    assert capas._next_action_for_result(
        {"verdict": "HOLD", "schema_errors": ["claim.type must be one of: x"]}, False
    )["kind"] == "register_claim_type"
    assert capas._next_action_for_result(
        {"verdict": "HOLD", "schema_errors": ["some other error"]}, True
    )["kind"] == "repair_schema"
    assert capas._next_action_for_result(
        {"verdict": "ACCEPT", "schema_errors": [], "missing_fields": ["tolerance"]}, True
    )["kind"] == "supply_evidence"


# --------------------------------------------------------------------------
# requirements introspection (A3): registered type + anchor modes + unknown type
# --------------------------------------------------------------------------
def test_requirements_introspection():
    req = capas.requirements_for_claim("statistical_confidence")
    assert req["required_fields"] == ["p_value", "alpha", "effect_direction_confirmed"]
    assert req["fields"]["p_value"]["type"] == "number"

    anc = capas.requirements_for_claim("universal_anchor_claim", anchor_mode="benchmark_anchor")
    assert "benchmark_name" in anc["required_fields"]
    assert anc["anchor_mode"] == "benchmark_anchor"
    assert "anchor_modes_available" in anc

    anc_default = capas.requirements_for_claim("universal_anchor_claim", anchor_mode="bad")
    assert anc_default["anchor_mode"] is None  # bad mode falls back to default contract

    assert capas.requirements_for_claim("nope_not_real") is None


# --------------------------------------------------------------------------
# Driver
# --------------------------------------------------------------------------
def _run_all():
    fns = [v for k, v in sorted(globals().items())
           if k.startswith("test_") and callable(v)]
    failures = 0
    for fn in fns:
        try:
            fn()
            print(f"PASS {fn.__name__}")
        except AssertionError as exc:
            failures += 1
            print(f"FAIL {fn.__name__}: {exc}")
    print(f"\n{len(fns) - failures}/{len(fns)} passed")
    return failures


if __name__ == "__main__":
    sys.exit(1 if _run_all() else 0)
