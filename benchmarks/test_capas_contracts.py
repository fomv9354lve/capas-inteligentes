#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""Exercise the evidence-contract validators and per-claim-type licensing rules in capas.py.

This slice drives the *contract* layer, not the surface smoke test:

  * `validate_external_payload` — required/optional checks, type coercion guards
    (numeric/boolean/string/list), out-of-range guards (p_value/alpha in [0,1],
    abs_error/tolerance/empirical_tolerance >= 0, NaN/inf rejection), unknown-field /
    did-you-mean handling, angle-bracket + control-char guards, provenance & training
    object validation.
  * The per-claim-type decision handlers inside `decide_external_claim` — every
    ACCEPT / REWRITE / REJECT licensing branch for each of the 12 claim types
    (significance-vs-alpha + direction for stats, balance/period for finance,
    intervention/temporal/confounder/mechanism for causal, protocol/inclusion/bias for
    systematic review, supporting/contradicting/method/pre-registration for evidence
    conflict, modality/hashes/alignment for multimodal, expected-vs-observed/execution
    for programming behavior, the four anchor_mode contracts).
  * Contract-introspection helpers: `required_fields_for_claim`,
    `allowed_evidence_fields_for_claim`, `evidence_field_type`, `did_you_mean_map`,
    `requirements_for_claim`, `_resolution_for_result`, `_closest_field`, `_edit_distance`.

Real inputs only: valid + boundary + invalid evidence so each validator/handler body runs and
the asserted verdict/error reflects the licensing rule. No live LLM/network is touched — the
contract layer is pure. Run: `python3 benchmarks/test_capas_contracts.py` or pytest.
"""
from __future__ import annotations

import capas

SCHEMA = capas.CAPAS_CLAIM_SCHEMA_VERSION
LEGAL = {"ACCEPT", "REWRITE", "REJECT", "HOLD"}


# --------------------------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------------------------
def _payload(claim_type: str, evidence: dict, *, text: str = "A worded claim.",
             cid: str = "c1") -> dict:
    return {
        "schema_version": SCHEMA,
        "claim": {"id": cid, "type": claim_type, "text": text},
        "evidence": evidence,
    }


def _decide(claim_type: str, evidence: dict, **kw) -> dict:
    res = capas.decide_external_claim(_payload(claim_type, evidence, **kw))
    assert res["verdict"] in LEGAL, res["verdict"]
    assert res["schema_version"] == SCHEMA
    # Every result carries a re-derivable audit hash.
    assert isinstance(res.get("audit_hash"), str) and res["audit_hash"].startswith("sha256:")
    return res


def _errors(payload: dict) -> list[str]:
    return capas.validate_external_payload(payload)


# ============================================================================================
# 1. validate_external_payload — structural / required-field guards
# ============================================================================================
def test_payload_must_be_object():
    assert capas.validate_external_payload([]) == ["payload must be a JSON object"]
    assert capas.validate_external_payload("nope") == ["payload must be a JSON object"]


def test_schema_version_mismatch():
    p = _payload("statistical_confidence", {"p_value": 0.01, "alpha": 0.05,
                                            "effect_direction_confirmed": True})
    p["schema_version"] = "wrong-version"
    errs = _errors(p)
    assert any("schema_version must be" in e for e in errs)


def test_claim_and_evidence_must_be_objects():
    p = {"schema_version": SCHEMA, "claim": "x", "evidence": []}
    errs = _errors(p)
    assert any("claim must be an object" in e for e in errs)
    assert any("evidence must be an object" in e for e in errs)


def test_claim_fields_must_be_nonempty_strings():
    p = _payload("statistical_confidence", {"p_value": 0.01, "alpha": 0.05,
                                            "effect_direction_confirmed": True})
    p["claim"] = {"id": "", "type": "statistical_confidence", "text": "  "}
    errs = _errors(p)
    assert any("claim.id must be a non-empty string" in e for e in errs)
    assert any("claim.text must be a non-empty string" in e for e in errs)


def test_claim_id_length_and_text_length_caps():
    p = _payload("statistical_confidence", {"p_value": 0.01, "alpha": 0.05,
                                            "effect_direction_confirmed": True})
    p["claim"]["id"] = "x" * 300
    p["claim"]["text"] = "y" * 2100
    errs = _errors(p)
    assert any("claim.id must be at most 256 characters" in e for e in errs)
    assert any("claim.text must be at most 2000 characters" in e for e in errs)


def test_unsupported_claim_type_listed():
    p = _payload("totally_made_up", {"p_value": 0.01})
    errs = _errors(p)
    assert any("claim.type must be one of" in e for e in errs)


def test_unknown_root_and_claim_fields_flagged():
    p = _payload("statistical_confidence", {"p_value": 0.01, "alpha": 0.05,
                                            "effect_direction_confirmed": True})
    p["mystery_root"] = 1
    p["claim"]["mystery_claim"] = 1
    errs = _errors(p)
    assert any("mystery_root" in e for e in errs)
    assert any("mystery_claim" in e for e in errs)


def test_source_must_be_object():
    p = _payload("statistical_confidence", {"p_value": 0.01, "alpha": 0.05,
                                            "effect_direction_confirmed": True})
    p["source"] = "a string"
    errs = _errors(p)
    assert any("payload.source must be an object" in e for e in errs)


# ============================================================================================
# 2. Unknown-evidence + did-you-mean + training_evidence-misplacement guards
# ============================================================================================
def test_unknown_evidence_field_with_typo_suggestion():
    # `p_val` is one edit from p_value -> the did-you-mean hint must fire.
    p = _payload("statistical_confidence",
                 {"p_val": 0.01, "alpha": 0.05, "effect_direction_confirmed": True})
    errs = _errors(p)
    assert any("evidence.p_val is not allowed" in e for e in errs)
    assert any("did you mean 'p_value'" in e for e in errs)


def test_training_evidence_in_evidence_block_rejected():
    p = _payload("statistical_confidence",
                 {"p_value": 0.01, "alpha": 0.05, "effect_direction_confirmed": True,
                  "training_evidence": {}})
    errs = _errors(p)
    assert any("evidence.training_evidence is not allowed" in e for e in errs)


def test_invariants_evidence_namespace_is_universally_allowed():
    # `invariants` must NOT be flagged as unknown for any claim type.
    p = _payload("statistical_confidence",
                 {"p_value": 0.01, "alpha": 0.05, "effect_direction_confirmed": True,
                  "invariants": {}})
    errs = _errors(p)
    assert not any("invariants is not allowed" in e for e in errs)


# ============================================================================================
# 3. Type-coercion guards (numeric / boolean / string / list)
# ============================================================================================
def test_numeric_field_string_coercion_message():
    p = _payload("statistical_confidence",
                 {"p_value": "0.01", "alpha": 0.05, "effect_direction_confirmed": True})
    errs = _errors(p)
    assert any("evidence.p_value must be a number" in e and "use the number" in e for e in errs)


def test_numeric_field_unparseable_string_message():
    p = _payload("statistical_confidence",
                 {"p_value": "abc", "alpha": 0.05, "effect_direction_confirmed": True})
    errs = _errors(p)
    assert any("evidence.p_value must be a number" in e and "0.05 (no quotes)" in e for e in errs)


def test_numeric_field_bool_is_not_a_number():
    # bool is an int subclass; the validator must still reject it as numeric.
    p = _payload("exact_model_solution", {"abs_error": True, "tolerance": 1e-3})
    errs = _errors(p)
    assert any("evidence.abs_error must be a number" in e and "boolean" in e for e in errs)


def test_numeric_field_other_type_message():
    p = _payload("exact_model_solution", {"abs_error": [1, 2], "tolerance": 1e-3})
    errs = _errors(p)
    assert any("evidence.abs_error must be a number" in e and "list" in e for e in errs)


def test_boolean_field_string_truthy_coercion():
    p = _payload("statistical_confidence",
                 {"p_value": 0.01, "alpha": 0.05, "effect_direction_confirmed": "true"})
    errs = _errors(p)
    assert any("effect_direction_confirmed must be a boolean" in e and "true (no quotes)" in e
               for e in errs)


def test_boolean_field_nonbool_message():
    p = _payload("statistical_confidence",
                 {"p_value": 0.01, "alpha": 0.05, "effect_direction_confirmed": 1})
    errs = _errors(p)
    assert any("effect_direction_confirmed must be a boolean" in e for e in errs)


def test_string_field_nonstring_message():
    p = _payload("universal_anchor_claim",
                 {"anchor_mode": 123, "local_property_tests_pass": True,
                  "universal_anchor_pass": True})
    errs = _errors(p)
    assert any("evidence.anchor_mode must be a string" in e for e in errs)


def test_list_field_must_be_array_of_strings():
    p = _payload("evidence_conflict_claim",
                 {"supporting_sources": [1, 2], "contradicting_sources": ["ok"],
                  "conflict_resolution_method": "m", "resolution_pre_registered": True})
    errs = _errors(p)
    assert any("evidence.supporting_sources must be an array of strings" in e for e in errs)


# ============================================================================================
# 4. Out-of-range / finiteness guards
# ============================================================================================
def test_p_value_alpha_must_be_in_unit_interval():
    p = _payload("statistical_confidence",
                 {"p_value": 1.5, "alpha": -0.1, "effect_direction_confirmed": True})
    errs = _errors(p)
    assert sum("must be between 0 and 1" in e for e in errs) == 2


def test_p_value_alpha_boundaries_are_valid():
    # 0 and 1 are inclusive boundaries -> no range error.
    p = _payload("statistical_confidence",
                 {"p_value": 0.0, "alpha": 1.0, "effect_direction_confirmed": True})
    errs = _errors(p)
    assert not any("between 0 and 1" in e for e in errs)


def test_nonnegative_fields_reject_negative():
    p = _payload("exact_model_solution", {"abs_error": -1.0, "tolerance": -2.0})
    errs = _errors(p)
    assert sum("must be >= 0" in e for e in errs) == 2


def test_nonfinite_numeric_rejected():
    p = _payload("exact_model_solution", {"abs_error": float("nan"), "tolerance": 1e-3})
    errs = _errors(p)
    assert any("evidence.abs_error must be finite" in e for e in errs)
    p2 = _payload("exact_model_solution", {"abs_error": float("inf"), "tolerance": 1e-3})
    assert any("evidence.abs_error must be finite" in e for e in _errors(p2))


# ============================================================================================
# 5. Injection / homoglyph / control-char guards
# ============================================================================================
def test_angle_bracket_guard_on_claim_text():
    p = _payload("statistical_confidence",
                 {"p_value": 0.01, "alpha": 0.05, "effect_direction_confirmed": True},
                 text="<script>alert(1)</script>")
    errs = _errors(p)
    assert any("angle brackets" in e for e in errs)


def test_control_char_guard_on_claim_id():
    p = _payload("statistical_confidence",
                 {"p_value": 0.01, "alpha": 0.05, "effect_direction_confirmed": True},
                 cid="ab\x00cd")
    errs = _errors(p)
    assert any("control characters" in e for e in errs)


def test_angle_guard_helper_directly():
    errs: list[str] = []
    capas._validate_no_angle_like("safe value", "evidence.x", errs)
    assert errs == []
    capas._validate_no_angle_like("has < bracket", "evidence.x", errs)
    assert errs and "angle" in errs[0]


def test_control_guard_helper_directly():
    errs: list[str] = []
    capas._validate_no_control_char("clean", "evidence.x", errs)
    assert errs == []
    capas._validate_no_control_char("dirty\x1f", "evidence.x", errs)
    assert errs and "control" in errs[0]


def test_long_string_field_caps():
    p = _payload("claim_transition",
                 {"upgrade_evidence_present": False, "current_claim": "z" * 4100})
    errs = _errors(p)
    assert any("current_claim must be at most 4000 characters" in e for e in errs)


def test_code_snippet_length_and_type_guards():
    base = {"language": "python", "language_version": "3.12", "claim_api": "len",
            "code_snippet": 123, "expected_output": "x" * 4100, "observed_output": "y",
            "execution_observed": True, "runtime_environment_declared": True}
    errs = _errors(_payload("programming_language_behavior_claim", base))
    assert any("evidence.code_snippet must be a string" in e for e in errs)
    assert any("evidence.expected_output must be at most 4000 characters" in e for e in errs)


# ============================================================================================
# 6. provenance / training_evidence object validation
# ============================================================================================
def test_provenance_must_be_object():
    p = _payload("statistical_confidence",
                 {"p_value": 0.01, "alpha": 0.05, "effect_direction_confirmed": True})
    p["provenance"] = "not an object"
    errs = _errors(p)
    assert any("provenance must be an object" in e for e in errs)


def test_provenance_field_types():
    p = _payload("statistical_confidence",
                 {"p_value": 0.01, "alpha": 0.05, "effect_direction_confirmed": True})
    p["provenance"] = {"review_id": 5, "sources": [1, 2], "source_hashes": "x",
                       "review_packet": "y", "reviewer": "z"}
    errs = _errors(p)
    assert any("provenance.review_id must be a string" in e for e in errs)
    assert any("provenance.sources must be an array of strings" in e for e in errs)
    assert any("provenance.source_hashes must be an object" in e for e in errs)
    assert any("provenance.review_packet must be an object" in e for e in errs)
    assert any("provenance.reviewer must be an object" in e for e in errs)


def test_training_evidence_must_be_object_and_bool_fields():
    p = _payload("statistical_confidence",
                 {"p_value": 0.01, "alpha": 0.05, "effect_direction_confirmed": True})
    p["training_evidence"] = "nope"
    assert any("training_evidence must be an object" in e for e in _errors(p))
    # well-typed object but a non-bool flag is caught
    p["training_evidence"] = {"source_backed_evidence": "yes"}
    errs = _errors(p)
    assert any("training_evidence.source_backed_evidence must be a boolean" in e for e in errs)


# ============================================================================================
# 7. Per-claim-type licensing — exact_model_solution / physical_accuracy
# ============================================================================================
def test_exact_model_solution_accept_boundary_and_reject():
    # boundary: abs_error == tolerance -> ACCEPT
    assert _decide("exact_model_solution", {"abs_error": 1e-3, "tolerance": 1e-3})["verdict"] == "ACCEPT"
    assert _decide("exact_model_solution", {"abs_error": 1.0, "tolerance": 1e-3})["verdict"] == "REJECT"


def test_physical_accuracy_accept_and_reject():
    assert _decide("physical_accuracy", {"within_chemical_accuracy": True})["verdict"] == "ACCEPT"
    assert _decide("physical_accuracy", {"within_chemical_accuracy": False})["verdict"] == "REJECT"


# ============================================================================================
# 8. Per-claim-type licensing — statistical_confidence (significance vs alpha + direction)
# ============================================================================================
def test_statistical_accept_when_significant_and_directional():
    r = _decide("statistical_confidence",
                {"p_value": 0.01, "alpha": 0.05, "effect_direction_confirmed": True})
    assert r["verdict"] == "ACCEPT"


def test_statistical_rewrite_when_significant_but_no_direction():
    r = _decide("statistical_confidence",
                {"p_value": 0.05, "alpha": 0.05, "effect_direction_confirmed": False})
    assert r["verdict"] == "REWRITE"
    assert "direction" in r["reason"].lower()


def test_statistical_reject_when_not_significant():
    r = _decide("statistical_confidence",
                {"p_value": 0.2, "alpha": 0.05, "effect_direction_confirmed": True})
    assert r["verdict"] == "REJECT"


# ============================================================================================
# 9. reproducibility_check
# ============================================================================================
def test_reproducibility_accept_rewrite_reject():
    assert _decide("reproducibility_check",
                   {"artifact_available": True, "independent_reproduction_pass": True})["verdict"] == "ACCEPT"
    assert _decide("reproducibility_check",
                   {"artifact_available": True, "independent_reproduction_pass": False})["verdict"] == "REWRITE"
    assert _decide("reproducibility_check",
                   {"artifact_available": False, "independent_reproduction_pass": True})["verdict"] == "REJECT"


# ============================================================================================
# 10. financial_metric_claim (balance vs tolerance + period match)
# ============================================================================================
def test_financial_accept_within_tolerance_and_period():
    r = _decide("financial_metric_claim",
                {"reported_value": 100.5, "reference_value": 100.0, "tolerance": 1.0,
                 "metric_period_match": True})
    assert r["verdict"] == "ACCEPT"


def test_financial_rewrite_within_tolerance_period_mismatch():
    r = _decide("financial_metric_claim",
                {"reported_value": 100.5, "reference_value": 100.0, "tolerance": 1.0,
                 "metric_period_match": False})
    assert r["verdict"] == "REWRITE"


def test_financial_reject_outside_tolerance():
    r = _decide("financial_metric_claim",
                {"reported_value": 200.0, "reference_value": 100.0, "tolerance": 1.0,
                 "metric_period_match": True})
    assert r["verdict"] == "REJECT"


# ============================================================================================
# 11. causal_mechanism_claim (intervention/temporal/confounder/mechanism)
# ============================================================================================
def test_causal_accept_all_present():
    r = _decide("causal_mechanism_claim",
                {"intervention_or_natural_experiment": True, "temporal_order_established": True,
                 "confounders_controlled": True, "mechanism_evidence_present": True})
    assert r["verdict"] == "ACCEPT"


def test_causal_rewrite_design_and_temporal_only():
    r = _decide("causal_mechanism_claim",
                {"intervention_or_natural_experiment": True, "temporal_order_established": True,
                 "confounders_controlled": False, "mechanism_evidence_present": False})
    assert r["verdict"] == "REWRITE"


def test_causal_reject_no_intervention():
    r = _decide("causal_mechanism_claim",
                {"intervention_or_natural_experiment": False, "temporal_order_established": True,
                 "confounders_controlled": True, "mechanism_evidence_present": True})
    assert r["verdict"] == "REJECT"


# ============================================================================================
# 12. systematic_review_claim (protocol/inclusion/bias/consistency)
# ============================================================================================
def test_systematic_review_accept_rewrite_reject():
    full = {"protocol_registered": True, "inclusion_criteria_declared": True,
            "risk_of_bias_assessed": True, "effect_consistency": True}
    assert _decide("systematic_review_claim", full)["verdict"] == "ACCEPT"
    partial = dict(full, risk_of_bias_assessed=False, effect_consistency=False)
    assert _decide("systematic_review_claim", partial)["verdict"] == "REWRITE"
    none = dict(full, protocol_registered=False, inclusion_criteria_declared=False)
    assert _decide("systematic_review_claim", none)["verdict"] == "REJECT"


# ============================================================================================
# 13. evidence_conflict_claim (supporting/contradicting/method/pre-registration)
# ============================================================================================
def test_evidence_conflict_accept():
    r = _decide("evidence_conflict_claim",
                {"supporting_sources": ["a"], "contradicting_sources": ["b"],
                 "conflict_resolution_method": "random-effects", "resolution_pre_registered": True})
    assert r["verdict"] == "ACCEPT"


def test_evidence_conflict_rewrite_not_preregistered():
    r = _decide("evidence_conflict_claim",
                {"supporting_sources": ["a"], "contradicting_sources": ["b"],
                 "conflict_resolution_method": "random-effects", "resolution_pre_registered": False})
    assert r["verdict"] == "REWRITE"


def test_evidence_conflict_reject_missing_sets():
    r = _decide("evidence_conflict_claim",
                {"supporting_sources": ["a"], "contradicting_sources": [],
                 "conflict_resolution_method": "random-effects", "resolution_pre_registered": True})
    assert r["verdict"] == "REJECT"


# ============================================================================================
# 14. multimodal_evidence_claim
# ============================================================================================
def test_multimodal_accept_rewrite_reject():
    full = {"modality": "image+text", "source_hashes_verified": True,
            "cross_modal_alignment": True, "extraction_method_declared": True}
    assert _decide("multimodal_evidence_claim", full)["verdict"] == "ACCEPT"
    rew = dict(full, cross_modal_alignment=False, extraction_method_declared=False)
    assert _decide("multimodal_evidence_claim", rew)["verdict"] == "REWRITE"
    rej = dict(full, source_hashes_verified=False, cross_modal_alignment=False,
               extraction_method_declared=False)
    assert _decide("multimodal_evidence_claim", rej)["verdict"] == "REJECT"


# ============================================================================================
# 15. programming_language_behavior_claim
# ============================================================================================
def _prog(**over) -> dict:
    base = {"language": "python", "language_version": "3.12", "claim_api": "len",
            "code_snippet": "len([1,2])", "expected_output": "2", "observed_output": "2",
            "execution_observed": True, "runtime_environment_declared": True}
    base.update(over)
    return base


def test_programming_accept_when_execution_observed():
    assert _decide("programming_language_behavior_claim", _prog())["verdict"] == "ACCEPT"


def test_programming_reject_when_output_mismatch():
    r = _decide("programming_language_behavior_claim", _prog(observed_output="3"))
    assert r["verdict"] == "REJECT"


def test_programming_rewrite_docs_only():
    r = _decide("programming_language_behavior_claim",
                _prog(execution_observed=False, docs_reference="https://docs.python.org"))
    assert r["verdict"] == "REWRITE"


def test_programming_rewrite_incomplete_runtime():
    r = _decide("programming_language_behavior_claim",
                _prog(execution_observed=False, runtime_environment_declared=False))
    assert r["verdict"] == "REWRITE"


# ============================================================================================
# 16. claim_transition
# ============================================================================================
def test_claim_transition_accept_and_rewrite():
    assert _decide("claim_transition", {"upgrade_evidence_present": True})["verdict"] == "ACCEPT"
    r = _decide("claim_transition",
                {"upgrade_evidence_present": False, "current_claim": "weaker statement"})
    assert r["verdict"] == "REWRITE"
    assert r["rewrite"] == "weaker statement"


# ============================================================================================
# 17. universal_anchor_claim — the four anchor_mode contracts
# ============================================================================================
def test_anchor_absolute_accept_and_rewrite():
    a = _decide("universal_anchor_claim",
                {"anchor_mode": "absolute_anchor", "local_property_tests_pass": True,
                 "universal_anchor_pass": True})
    assert a["verdict"] == "ACCEPT"
    r = _decide("universal_anchor_claim",
                {"anchor_mode": "absolute_anchor", "local_property_tests_pass": True,
                 "universal_anchor_pass": False})
    assert r["verdict"] == "REWRITE"


def test_anchor_absolute_reject_when_local_fails():
    r = _decide("universal_anchor_claim",
                {"anchor_mode": "absolute_anchor", "local_property_tests_pass": False,
                 "universal_anchor_pass": True})
    assert r["verdict"] == "REJECT"


def test_anchor_relative_rewrite():
    r = _decide("universal_anchor_claim",
                {"anchor_mode": "relative_anchor", "local_property_tests_pass": True,
                 "relative_anchor_reference": "baseline X",
                 "relative_anchor_comparison_pass": True})
    assert r["verdict"] == "REWRITE"
    assert "baseline X" in r["reason"]


def test_anchor_empirical_rewrite():
    r = _decide("universal_anchor_claim",
                {"anchor_mode": "empirical_anchor", "local_property_tests_pass": True,
                 "empirical_reference_present": True, "empirical_tolerance": 0.5,
                 "empirical_anchor_pass": True})
    assert r["verdict"] == "REWRITE"


def test_anchor_benchmark_rewrite():
    r = _decide("universal_anchor_claim",
                {"anchor_mode": "benchmark_anchor", "local_property_tests_pass": True,
                 "benchmark_name": "GSM8K", "benchmark_metric": "accuracy",
                 "benchmark_pass": True})
    assert r["verdict"] == "REWRITE"
    assert "GSM8K" in r["reason"]


def test_anchor_unsupported_mode_holds_via_schema():
    # An anchor_mode not in the contract registry is a schema error -> HOLD (never ACCEPT).
    r = _decide("universal_anchor_claim",
                {"anchor_mode": "made_up_mode", "local_property_tests_pass": True,
                 "universal_anchor_pass": True})
    assert r["verdict"] == "HOLD"


# ============================================================================================
# 18. missing-field / unsupported-type HOLD + resolution paths
# ============================================================================================
def test_missing_required_field_holds_with_supply_fields_resolution():
    r = _decide("statistical_confidence", {"p_value": 0.01})  # alpha + direction missing
    assert r["verdict"] == "HOLD"
    assert r["resolution"]["kind"] == "supply_fields"
    names = {f["name"] for f in r["resolution"]["fields"]}
    assert {"alpha", "effect_direction_confirmed"} <= names


def test_unknown_field_only_treated_as_unknown_not_missing():
    # `unknown` sentinel value for a required field counts as missing.
    r = _decide("physical_accuracy", {"within_chemical_accuracy": "unknown"})
    # string 'unknown' is a boolean-type violation -> schema error -> HOLD
    assert r["verdict"] == "HOLD"


def test_schema_error_resolution_kind():
    r = _decide("statistical_confidence",
                {"p_value": "0.01", "alpha": 0.05, "effect_direction_confirmed": True})
    assert r["verdict"] == "HOLD"
    assert r["resolution"]["kind"] == "fix_schema_errors"


# ============================================================================================
# 19. Contract-introspection helpers
# ============================================================================================
def test_required_fields_for_claim_anchor_versioned():
    base = capas.required_fields_for_claim("universal_anchor_claim")
    rel = capas.required_fields_for_claim("universal_anchor_claim",
                                          {"anchor_mode": "relative_anchor"})
    assert "relative_anchor_comparison_pass" in rel
    assert "relative_anchor_comparison_pass" not in base
    assert capas.required_fields_for_claim("nope") is None


def test_allowed_evidence_fields_for_claim():
    allowed = capas.allowed_evidence_fields_for_claim("financial_metric_claim")
    assert {"reported_value", "reference_value", "tolerance", "metric_period_match"} <= allowed
    assert capas.allowed_evidence_fields_for_claim("nope") is None


def test_evidence_field_type_table():
    assert capas.evidence_field_type("p_value") == "number"
    assert capas.evidence_field_type("effect_direction_confirmed") == "boolean"
    assert capas.evidence_field_type("anchor_mode") == "string"
    assert capas.evidence_field_type("supporting_sources") == "string[]"
    assert capas.evidence_field_type("not_a_field") == "unknown"


def test_did_you_mean_map():
    sug = capas.did_you_mean_map({"p_val": 0.01, "alpha": 0.05}, "statistical_confidence")
    assert sug.get("p_val") == "p_value"
    # invariants is never suggested-against; an unsupported claim type yields {}
    assert capas.did_you_mean_map({"x": 1}, "nope") == {}


def test_requirements_for_claim_template_and_anchor_modes():
    req = capas.requirements_for_claim("statistical_confidence")
    assert req["required_fields"] == ["p_value", "alpha", "effect_direction_confirmed"]
    assert req["fields"]["p_value"]["type"] == "number"
    assert "p_value" in req["evidence_template"]

    anchor = capas.requirements_for_claim("universal_anchor_claim", "benchmark_anchor")
    assert anchor["anchor_mode"] == "benchmark_anchor"
    assert "benchmark_pass" in anchor["required_fields"]
    assert "anchor_modes_available" in anchor

    # unknown anchor_mode falls back to base contract with anchor_mode None
    fallback = capas.requirements_for_claim("universal_anchor_claim", "bogus")
    assert fallback["anchor_mode"] is None
    assert capas.requirements_for_claim("nope") is None


def test_resolution_for_result_branches():
    # unsupported claim type (required is None, no schema errors)
    r1 = capas._resolution_for_result("HOLD", "nope", [], None, {}, [])
    assert r1["kind"] == "unsupported_claim_type"
    # ACCEPT / REWRITE / REJECT terminal kinds
    assert capas._resolution_for_result("ACCEPT", "statistical_confidence", [],
                                        ["p_value"], {}, [])["kind"] == "accepted"
    assert capas._resolution_for_result("REWRITE", "statistical_confidence", [],
                                        ["p_value"], {}, [])["kind"] == "edit_and_resubmit"
    assert capas._resolution_for_result("REJECT", "statistical_confidence", [],
                                        ["p_value"], {}, [])["kind"] == "exclude_or_replace_evidence"


def test_edit_distance_and_closest_field():
    assert capas._edit_distance("p_value", "p_value") == 0
    assert capas._edit_distance("p_val", "p_value") == 2
    assert capas._closest_field("p_val", {"p_value", "alpha"}) == "p_value"
    # adversarial giant key: must return None without burning cycles
    assert capas._closest_field("x" * 100, {"p_value"}) is None
    # nothing within max_distance
    assert capas._closest_field("zzzzzzzz", {"p_value"}) is None


# ============================================================================================
# runner
# ============================================================================================
def _run() -> None:
    fns = [v for k, v in sorted(globals().items())
           if k.startswith("test_") and callable(v)]
    failures = 0
    for fn in fns:
        try:
            fn()
        except AssertionError as exc:  # pragma: no cover - reporting path
            failures += 1
            print(f"FAIL {fn.__name__}: {exc}")
        except Exception as exc:  # pragma: no cover - reporting path
            failures += 1
            print(f"ERROR {fn.__name__}: {type(exc).__name__}: {exc}")
    print(f"{len(fns) - failures}/{len(fns)} contract tests passed")
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    _run()
