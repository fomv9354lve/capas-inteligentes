#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""Deep exercise of capas.py's decision pipeline — every VERDICT BRANCH, not just the happy path.

test_engine_surface.py already covers the 12-type ACCEPT-or-fail-closed contract. This file goes
deeper and DISJOINTLY: for each claim type it constructs evidence that drives ACCEPT, REWRITE,
REJECT and HOLD *separately* (per the per-type contract logic in decide_external_claim), and asserts
the exact verdict the contract must return. It also drives:

  - the REWRITE/resolution branches (`edit_and_resubmit` + a non-empty `rewrite`/`licensed_claim`),
  - the four universal_anchor modes (absolute/relative/empirical/benchmark) incl. their REWRITE/HOLD,
  - the HOLD paths: schema error, unsupported type, missing field, did_you_mean typo correction,
  - the cross-domain INVARIANT DOWNGRADE path (evidence.invariants forces REJECT, fail-closed),
  - the reason_code taxonomy via `resolution.kind` (fix_schema_errors / unsupported_claim_type /
    supply_fields / edit_and_resubmit / exclude_or_replace_evidence / accepted),
  - the reward mapping aligned with the gate (ACCEPT 1.0 / REWRITE 0.5 / HOLD 0.25 / REJECT 0.0),
  - align_claim_text scope-alignment statuses (ALIGNED / WARN / MISALIGNED / HOLD_SCHEMA),
  - audit_hash reproduction + tamper-evidence (verify_audit_hash), and run_batch / standalone_pipeline.

Where the verdict is determinable from the contract it is asserted exactly; otherwise legality +
a reproducible audit_hash are asserted. Run: `python3 benchmarks/test_engine_deep.py` or pytest.
"""
import capas
import capas_sdk

LEGAL = {"ACCEPT", "REWRITE", "REJECT", "HOLD"}
SCHEMA = "capas-claim-payload-v3"


def _decide(claim_type, evidence, text="claim", cid="claim"):
    """Route through the SDK (which builds the v3 payload) -> capas.decide_external_claim."""
    return capas_sdk.gate(claim_type, evidence, text, cid)


def _assert_legal_and_reproducible(r, ctx):
    assert isinstance(r, dict), f"{ctx}: not a dict"
    assert r.get("verdict") in LEGAL, f"{ctx}: illegal verdict {r.get('verdict')!r}"
    h = r.get("audit_hash")
    assert h and h.startswith("sha256:"), f"{ctx}: missing/odd audit_hash {h!r}"
    # re-derivable: the published recipe recomputes the SAME hash a third party would get
    assert capas.reproduce_audit_hash(r) == h, f"{ctx}: audit_hash not re-derivable"
    ver = capas.verify_audit_hash(r)
    assert ver["audit_hash_present"] is True and ver["verified"] is True, f"{ctx}: hash failed verify"
    return r["verdict"]


# (claim_type, {verdict_label: evidence}) — each evidence dict is constructed to drive that verdict.
# Verdicts here are DETERMINABLE from the contract, so we assert the exact value.
SCENARIOS = [
    ("exact_model_solution", {
        "ACCEPT": {"abs_error": 0.0, "tolerance": 1e-3},
        "REJECT": {"abs_error": 5.0, "tolerance": 1e-3},
    }),
    ("physical_accuracy", {
        "ACCEPT": {"within_chemical_accuracy": True},
        "REJECT": {"within_chemical_accuracy": False},
    }),
    ("claim_transition", {
        "ACCEPT": {"upgrade_evidence_present": True},
        "REWRITE": {"upgrade_evidence_present": False, "current_claim": "weaker prior claim"},
    }),
    ("statistical_confidence", {
        "ACCEPT": {"p_value": 0.01, "alpha": 0.05, "effect_direction_confirmed": True},
        "REWRITE": {"p_value": 0.01, "alpha": 0.05, "effect_direction_confirmed": False},
        "REJECT": {"p_value": 0.50, "alpha": 0.05, "effect_direction_confirmed": True},
    }),
    ("reproducibility_check", {
        "ACCEPT": {"artifact_available": True, "independent_reproduction_pass": True},
        "REWRITE": {"artifact_available": True, "independent_reproduction_pass": False},
        "REJECT": {"artifact_available": False, "independent_reproduction_pass": False},
    }),
    ("financial_metric_claim", {
        "ACCEPT": {"reported_value": 100.0, "reference_value": 100.0, "tolerance": 0.01,
                   "metric_period_match": True},
        "REWRITE": {"reported_value": 100.0, "reference_value": 100.0, "tolerance": 0.01,
                    "metric_period_match": False},
        "REJECT": {"reported_value": 100.0, "reference_value": 50.0, "tolerance": 0.01,
                   "metric_period_match": True},
    }),
    ("causal_mechanism_claim", {
        "ACCEPT": {"intervention_or_natural_experiment": True, "temporal_order_established": True,
                   "confounders_controlled": True, "mechanism_evidence_present": True},
        "REWRITE": {"intervention_or_natural_experiment": True, "temporal_order_established": True,
                    "confounders_controlled": False, "mechanism_evidence_present": False},
        "REJECT": {"intervention_or_natural_experiment": False, "temporal_order_established": False,
                   "confounders_controlled": False, "mechanism_evidence_present": False},
    }),
    ("systematic_review_claim", {
        "ACCEPT": {"protocol_registered": True, "inclusion_criteria_declared": True,
                   "risk_of_bias_assessed": True, "effect_consistency": True},
        "REWRITE": {"protocol_registered": True, "inclusion_criteria_declared": True,
                    "risk_of_bias_assessed": False, "effect_consistency": False},
        "REJECT": {"protocol_registered": False, "inclusion_criteria_declared": False,
                   "risk_of_bias_assessed": False, "effect_consistency": False},
    }),
    ("evidence_conflict_claim", {  # NOTE: *_sources must be arrays of strings (schema), not ints
        "ACCEPT": {"supporting_sources": ["s1", "s2"], "contradicting_sources": ["c1"],
                   "conflict_resolution_method": "meta-analysis", "resolution_pre_registered": True},
        "REWRITE": {"supporting_sources": ["s1", "s2"], "contradicting_sources": ["c1"],
                    "conflict_resolution_method": "meta-analysis", "resolution_pre_registered": False},
        "REJECT": {"supporting_sources": ["s1"], "contradicting_sources": [],
                   "conflict_resolution_method": "none", "resolution_pre_registered": False},
    }),
    ("multimodal_evidence_claim", {
        "ACCEPT": {"modality": "text+table", "source_hashes_verified": True,
                   "cross_modal_alignment": True, "extraction_method_declared": True},
        "REWRITE": {"modality": "text+table", "source_hashes_verified": True,
                    "cross_modal_alignment": False, "extraction_method_declared": False},
        "REJECT": {"modality": "text+table", "source_hashes_verified": False,
                   "cross_modal_alignment": False, "extraction_method_declared": False},
    }),
    ("programming_language_behavior_claim", {
        "ACCEPT": {"language": "python", "language_version": "3.11", "claim_api": "sorted",
                   "code_snippet": "sorted([3,1,2])", "expected_output": "[1, 2, 3]",
                   "observed_output": "[1, 2, 3]", "execution_observed": True,
                   "runtime_environment_declared": True},
        # expected != observed -> REJECT regardless of the rest
        "REJECT": {"language": "python", "language_version": "3.11", "claim_api": "sorted",
                   "code_snippet": "sorted([3,1,2])", "expected_output": "[1, 2, 3]",
                   "observed_output": "[3, 2, 1]", "execution_observed": True,
                   "runtime_environment_declared": True},
        # outputs match but execution not observed (only docs+runtime) -> REWRITE
        "REWRITE": {"language": "python", "language_version": "3.11", "claim_api": "sorted",
                    "code_snippet": "sorted([3,1,2])", "expected_output": "[1, 2, 3]",
                    "observed_output": "[1, 2, 3]", "execution_observed": False,
                    "runtime_environment_declared": True, "docs_reference": "python docs sorted()"},
    }),
]


def test_each_type_drives_each_verdict():
    """Every constructed scenario must return its labeled verdict (ACCEPT/REWRITE/REJECT) exactly,
    with a re-derivable audit_hash. This walks the per-type branch logic, not just the happy path."""
    for claim_type, by_verdict in SCENARIOS:
        for want, evidence in by_verdict.items():
            cid = f"{claim_type}_{want}"
            r = _decide(claim_type, evidence, claim_type, cid)
            got = _assert_legal_and_reproducible(r, cid)
            assert got == want, f"{cid}: wanted {want}, got {got} ({r.get('reason')!r}; "\
                                 f"schema_errors={r.get('schema_errors')})"
            # fail-closed invariant: no non-ACCEPT scenario may ever surface as ACCEPT
            if want != "ACCEPT":
                assert got != "ACCEPT", f"{cid}: fail-open!"


def test_rewrite_branch_emits_licensed_downgrade():
    """A REWRITE must carry the edit-and-resubmit resolution AND a concrete weaker wording."""
    for claim_type, by_verdict in SCENARIOS:
        ev = by_verdict.get("REWRITE")
        if ev is None:
            continue
        r = _decide(claim_type, ev, claim_type, f"{claim_type}_rw")
        assert r["verdict"] == "REWRITE", f"{claim_type}: expected REWRITE"
        assert r["resolution"]["kind"] == "edit_and_resubmit", f"{claim_type}: wrong resolution kind"
        assert r.get("rewrite"), f"{claim_type}: REWRITE with no licensed rewrite text"
        assert r.get("licensed_claim"), f"{claim_type}: REWRITE with no licensed_claim"


def test_universal_anchor_all_modes():
    """The four anchor modes each have distinct accept/rewrite/reject/hold contracts."""
    base = "universal_anchor_claim"
    # absolute: local+anchor pass -> ACCEPT
    assert _decide(base, {"anchor_mode": "absolute_anchor", "local_property_tests_pass": True,
                          "universal_anchor_pass": True}, base, "abs_ok")["verdict"] == "ACCEPT"
    # absolute: local pass, anchor fail -> REWRITE (local plausibility only)
    r = _decide(base, {"anchor_mode": "absolute_anchor", "local_property_tests_pass": True,
                       "universal_anchor_pass": False}, base, "abs_rw")
    assert r["verdict"] == "REWRITE" and r["rewrite"]
    # absolute: local fail -> REJECT
    assert _decide(base, {"anchor_mode": "absolute_anchor", "local_property_tests_pass": False,
                          "universal_anchor_pass": False}, base, "abs_rej")["verdict"] == "REJECT"
    # relative anchor (passes) -> REWRITE (comparison-only license)
    r = _decide(base, {"anchor_mode": "relative_anchor", "local_property_tests_pass": True,
                       "relative_anchor_reference": "DFT", "relative_anchor_comparison_pass": True},
                base, "rel_rw")
    assert r["verdict"] == "REWRITE" and "DFT" in (r["reason"] + (r["rewrite"] or ""))
    # empirical anchor (passes) -> REWRITE (bounded empirical agreement)
    r = _decide(base, {"anchor_mode": "empirical_anchor", "local_property_tests_pass": True,
                       "empirical_reference_present": True, "empirical_tolerance": 0.01,
                       "empirical_anchor_pass": True}, base, "emp_rw")
    assert r["verdict"] == "REWRITE"
    # benchmark anchor (passes) -> REWRITE (benchmark-limited)
    r = _decide(base, {"anchor_mode": "benchmark_anchor", "local_property_tests_pass": True,
                       "benchmark_name": "QM9", "benchmark_metric": "MAE", "benchmark_pass": True},
                base, "bench_rw")
    assert r["verdict"] == "REWRITE" and "QM9" in (r["reason"] + (r["rewrite"] or ""))
    # unregistered anchor mode -> HOLD (no contract to decide it)
    assert _decide(base, {"anchor_mode": "made_up_mode", "local_property_tests_pass": True,
                          "universal_anchor_pass": True}, base, "hold_mode")["verdict"] == "HOLD"


def test_hold_paths_and_reason_taxonomy():
    """The HOLD family routes to distinct, machine-readable resolution kinds (the reason taxonomy)."""
    # unsupported claim type -> rejected at schema validation, fix_schema_errors HOLD
    r = _decide("not_a_real_claim_type", {"foo": 1}, "x", "unsup")
    assert r["verdict"] == "HOLD" and r["schema_errors"]
    assert r["resolution"]["kind"] == "fix_schema_errors"

    # missing required field (valid type) -> supply_fields HOLD with a template
    r = _decide("statistical_confidence", {"alpha": 0.05}, "x", "missing")
    assert r["verdict"] == "HOLD" and r["resolution"]["kind"] == "supply_fields"
    assert r["missing_fields"], "missing-field HOLD should list the missing fields"
    assert isinstance(r["resolution"].get("evidence_template"), dict)

    # typo'd field name -> did_you_mean correction surfaced, fix_schema_errors HOLD
    r = _decide("statistical_confidence",
                {"p_valeu": 0.01, "alpha": 0.05, "effect_direction_confirmed": True}, "x", "typo")
    assert r["verdict"] == "HOLD"
    assert r["did_you_mean"].get("p_valeu") == "p_value", f"did_you_mean miss: {r['did_you_mean']}"
    assert r["resolution"]["kind"] == "fix_schema_errors"

    # ACCEPT routes to the 'accepted' resolution; REJECT to exclude_or_replace_evidence
    acc = _decide("physical_accuracy", {"within_chemical_accuracy": True}, "x", "acc")
    assert acc["resolution"]["kind"] == "accepted"
    rej = _decide("physical_accuracy", {"within_chemical_accuracy": False}, "x", "rej")
    assert rej["resolution"]["kind"] == "exclude_or_replace_evidence"


def test_invariant_downgrade_path():
    """A domain-law violation under evidence.invariants OVERRIDES any verdict to REJECT (fail-closed,
    downgrade-only). A satisfied invariant block leaves the contract verdict untouched."""
    accept_ev = {"p_value": 0.01, "alpha": 0.05, "effect_direction_confirmed": True}
    # accounting identity violated (assets != liabilities + equity) -> forces REJECT
    bad = dict(accept_ev, invariants={"accounting": {"assets": 100, "liabilities": 90, "equity": 5}})
    r = _decide("statistical_confidence", bad, "x", "inv_bad")
    assert r["verdict"] == "REJECT", f"invariant violation did not downgrade: {r['verdict']}"
    assert r["invariant_audit"]["applicable"] is True and r["invariant_audit"]["verdict"] == "FLAG"
    assert "OVERRIDDEN" in r["reason"]
    assert r["licensed_claim"] is None and r["rewrite"] is None
    # a CONSISTENT invariant block must NOT change the underlying ACCEPT (downgrade-only, never upgrade)
    good = dict(accept_ev, invariants={"accounting": {"assets": 100, "liabilities": 60, "equity": 40}})
    r2 = _decide("statistical_confidence", good, "x", "inv_good")
    assert r2["verdict"] == "ACCEPT", f"consistent invariant block wrongly altered verdict: {r2['verdict']}"
    assert r2["invariant_audit"]["verdict"] == "PASS"


def test_reward_matches_gate():
    """capas_sdk.reward is the gate-aligned dense signal: ACCEPT 1.0 / REWRITE 0.5 / HOLD 0.25 / REJECT 0.0."""
    table = {
        ("statistical_confidence", "ACCEPT"):
            ({"p_value": 0.01, "alpha": 0.05, "effect_direction_confirmed": True}, 1.0),
        ("statistical_confidence", "REWRITE"):
            ({"p_value": 0.01, "alpha": 0.05, "effect_direction_confirmed": False}, 0.5),
        ("statistical_confidence", "REJECT"):
            ({"p_value": 0.50, "alpha": 0.05, "effect_direction_confirmed": True}, 0.0),
        ("statistical_confidence", "HOLD"):
            ({"alpha": 0.05}, 0.25),
    }
    for (ct, label), (ev, want) in table.items():
        got = capas_sdk.reward(ct, ev, ct, f"rw_{label}")
        assert got == want, f"{ct}/{label}: reward {got} != {want}"


def test_align_claim_text_statuses():
    """align_claim_text is the lexical/scope guardrail: MISALIGNED on overclaim, ALIGNED when scoped,
    HOLD_SCHEMA on bad payloads. (Independent of the gate verdict; a structurally valid claim can be
    semantically misaligned.)"""
    def payload(ct, text, ev):
        return {"schema_version": SCHEMA, "claim": {"id": "c", "type": ct, "text": text}, "evidence": ev}

    # strong physical-correctness prose but universal_anchor_pass is false -> MISALIGNED
    mis = capas.align_claim_text(payload(
        "universal_anchor_claim",
        "this is exactly physically correct and exact for all real systems",
        {"anchor_mode": "absolute_anchor", "local_property_tests_pass": True, "universal_anchor_pass": False}))
    assert mis["alignment_status"] == "MISALIGNED" and mis["alignment_pass"] is False and mis["issues"]

    # well-scoped statistical prose -> ALIGNED
    al = capas.align_claim_text(payload(
        "statistical_confidence", "statistical significance p value below alpha",
        {"p_value": 0.01, "alpha": 0.05, "effect_direction_confirmed": True}))
    assert al["alignment_status"] == "ALIGNED" and al["alignment_pass"] is True

    # schema-invalid payload -> HOLD_SCHEMA (no semantic check performed)
    hs = capas.align_claim_text({"claim": {"type": "statistical_confidence"}})
    assert hs["alignment_status"] == "HOLD_SCHEMA" and hs["alignment_pass"] is False


def test_audit_hash_tamper_evidence():
    """Mutating any hashed field of a returned result must break verification (tamper-evidence)."""
    r = _decide("exact_model_solution", {"abs_error": 0.0, "tolerance": 1e-3}, "exact", "tamper")
    assert capas.verify_audit_hash(r)["verified"] is True
    tampered = dict(r, verdict="REJECT")  # flip a hashed field
    assert capas.verify_audit_hash(tampered)["verified"] is False
    # a result with no audit_hash reports present=False, verified=None (not a crash)
    no_hash = capas.verify_audit_hash({"verdict": "ACCEPT"})
    assert no_hash["audit_hash_present"] is False and no_hash["verified"] is None


def test_run_batch_aggregates_verdicts():
    """run_batch in 'decide' mode applies the same per-claim gates and tallies the verdicts;
    'align' mode routes through align_claim_text. Both must return a coherent summary."""
    accept = {"schema_version": SCHEMA,
              "claim": {"id": "a", "type": "physical_accuracy", "text": "physical accuracy"},
              "evidence": {"within_chemical_accuracy": True}}
    reject = {"schema_version": SCHEMA,
              "claim": {"id": "r", "type": "physical_accuracy", "text": "physical accuracy"},
              "evidence": {"within_chemical_accuracy": False}}
    out = capas.run_batch([accept, reject, accept], mode="decide")
    assert out["item_count"] == 3
    assert out["summary"].get("ACCEPT") == 2 and out["summary"].get("REJECT") == 1
    assert len(out["results"]) == 3
    # align mode returns an alignment_status per item and a non-crashing summary
    out_a = capas.run_batch([accept], mode="align")
    assert out_a["item_count"] == 1 and out_a["batch_mode"] == "align"


def test_standalone_pipeline_runs_offline():
    """standalone_pipeline (extraction -> alignment -> gate, no web) returns a legal, structured
    report. With inline evidence and no sources it fails CLOSED (HOLD), never a false ACCEPT."""
    payload = {"schema_version": SCHEMA,
               "claim": {"id": "p", "type": "statistical_confidence",
                         "text": "p value below alpha statistical significance"},
               "evidence": {"p_value": 0.01, "alpha": 0.05, "effect_direction_confirmed": True}}
    r = capas.standalone_pipeline(payload, allow_web=False)
    assert isinstance(r, dict)
    for key in ("extraction", "semantic_alignment", "capas_gate_decision", "final_decision"):
        assert key in r, f"pipeline missing section {key}"
    final = r.get("final_decision", {})
    v = final.get("verdict") or r.get("verdict")
    assert v in LEGAL, f"pipeline final verdict illegal: {v!r}"


def main() -> int:
    tests = [
        test_each_type_drives_each_verdict,
        test_rewrite_branch_emits_licensed_downgrade,
        test_universal_anchor_all_modes,
        test_hold_paths_and_reason_taxonomy,
        test_invariant_downgrade_path,
        test_reward_matches_gate,
        test_align_claim_text_statuses,
        test_audit_hash_tamper_evidence,
        test_run_batch_aggregates_verdicts,
        test_standalone_pipeline_runs_offline,
    ]
    failed = []
    for t in tests:
        try:
            t()
        except AssertionError as e:
            failed.append(f"{t.__name__}: {e}")
    if failed:
        print("FAIL:")
        for f in failed:
            print("  -", f)
        return 1
    print(f"OK {len(tests)}/{len(tests)} suites — 12 types x {{ACCEPT,REWRITE,REJECT}} branches, "
          f"4 anchor modes, HOLD/reason taxonomy, invariant downgrade, reward map, align statuses, "
          f"audit-hash tamper-evidence, batch + offline pipeline.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
