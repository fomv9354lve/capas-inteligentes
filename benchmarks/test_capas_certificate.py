#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""Exercise the audit_hash + admissibility-certificate slice of capas.py — real tests, not gaming.

Covers paths the engine-surface/deep suites leave thin:
  - the canonical decision body builder (`_audit_hash_body`) and the sha256 over it (`_hash_audit_body`),
  - re-derivation determinism (`reproduce_audit_hash`) and third-party tamper-evidence (`verify_audit_hash`),
  - tamper-divergence: mutating ANY canonical field (claim / verdict / reason / required_fields /
    invariant_audit) flips the recomputed hash, while a non-canonical field does NOT,
  - the certificate issuance path (`build_admissibility_certificate`) across all four verdicts
    (ACCEPT / REWRITE / REJECT / HOLD), plus the schema-error HOLD path and the unregistered-type path,
  - the lattice/argument helpers it composes: `_axis` (clamping), `_registered_contract_for_claim`
    (registered / anchor-mode / unregistered branches), `_provenance_axis_score` (each rung),
    `_next_action_for_result` (each next-action kind), and `exception_queue_entry`,
  - the SDK certificate route (`capas_sdk.certificate` -> capas_rcc) returns a dict.

These call the real functions with valid inputs and assert hash/canonicalization invariants. No mocks,
no excluded code. Run: `python3 benchmarks/test_capas_certificate.py` or pytest.
"""
import copy

import capas
import capas_sdk

SCHEMA = capas.CAPAS_CLAIM_SCHEMA_VERSION


def _payload(claim_type, evidence, text="claim", cid="c"):
    return {
        "schema_version": SCHEMA,
        "claim": {"id": cid, "type": claim_type, "text": text},
        "evidence": evidence,
    }


# ---------------------------------------------------------------------------
# canonical body + sha256 + re-derivation determinism
# ---------------------------------------------------------------------------
def test_canonical_body_and_hash_are_deterministic():
    body = capas._audit_hash_body(
        claim={"id": "c", "type": "statistical_confidence", "text": "effect"},
        verdict="ACCEPT",
        reason="p<alpha",
        required_fields=["p_value", "alpha"],
        invariant_audit={"verdict": "PASS", "extra": "ignored"},
    )
    # body keys are exactly the published recipe surface
    assert set(body) == {
        "schema_version", "input_claim", "verdict", "reason",
        "required_fields", "invariant_audit",
    }
    # invariant_audit is reduced to just the verdict STRING (not the whole dict)
    assert body["invariant_audit"] == "PASS"
    assert body["schema_version"] == SCHEMA

    h1 = capas._hash_audit_body(body)
    h2 = capas._hash_audit_body(copy.deepcopy(body))
    assert h1 == h2, "same body must hash identically"
    assert h1.startswith("sha256:") and len(h1) == len("sha256:") + 64


def test_audit_body_normalizes_non_dict_invariant_and_empty_required():
    # invariant_audit not a dict -> None; required_fields falsy -> []
    body = capas._audit_hash_body("claim-str", "HOLD", "reason", None, "not-a-dict")
    assert body["invariant_audit"] is None
    assert body["required_fields"] == []


def test_reproduce_audit_hash_matches_engine_on_accept():
    r = capas_sdk.gate(
        "statistical_confidence",
        {"p_value": 0.01, "alpha": 0.05, "effect_direction_confirmed": True},
        "effect is real", "acc",
    )
    assert r["verdict"] == "ACCEPT"
    assert r["audit_hash"] == capas.reproduce_audit_hash(r), "third party must re-derive engine hash"


def test_reproduce_audit_hash_matches_on_every_verdict():
    cases = [
        ("statistical_confidence",
         {"p_value": 0.01, "alpha": 0.05, "effect_direction_confirmed": True}, "ACCEPT"),
        ("statistical_confidence",
         {"p_value": 0.40, "alpha": 0.05, "effect_direction_confirmed": True}, "REJECT"),
        ("universal_anchor_claim",
         {"anchor_mode": "relative_anchor", "local_property_tests_pass": True,
          "relative_anchor_reference": "baseline-X", "relative_anchor_comparison_pass": True}, "REWRITE"),
        ("statistical_confidence", {}, "HOLD"),  # missing required evidence
    ]
    for ct, ev, expected in cases:
        r = capas_sdk.gate(ct, ev, "claim text", "v")
        assert r["verdict"] == expected, f"{ct}: expected {expected}, got {r['verdict']}"
        assert r["audit_hash"] == capas.reproduce_audit_hash(r), f"{ct}: hash not re-derivable"


# ---------------------------------------------------------------------------
# verify_audit_hash (third-party tamper-evidence wrapper)
# ---------------------------------------------------------------------------
def test_verify_audit_hash_confirms_untampered_result():
    r = capas_sdk.gate(
        "exact_model_solution", {"abs_error": 0.0, "tolerance": 1e-3}, "exact", "v1")
    v = capas.verify_audit_hash(r)
    assert v["audit_hash_present"] is True
    assert v["verified"] is True
    assert v["claimed"] == v["recomputed"]
    assert "sha256" in v["recipe"]


def test_verify_audit_hash_absent_when_no_hash():
    v = capas.verify_audit_hash({"verdict": "HOLD"})  # no audit_hash key
    assert v["audit_hash_present"] is False
    assert v["verified"] is None
    assert "no audit_hash" in v["note"]

    # non-dict input is tolerated (claimed -> None branch)
    v2 = capas.verify_audit_hash("not-a-dict")
    assert v2["audit_hash_present"] is False


# ---------------------------------------------------------------------------
# tamper-divergence: change a CANONICAL field -> different hash
# ---------------------------------------------------------------------------
def test_tamper_on_each_canonical_field_diverges():
    r = capas_sdk.gate(
        "statistical_confidence",
        {"p_value": 0.01, "alpha": 0.05, "effect_direction_confirmed": True},
        "effect is real", "tamper",
    )
    baseline = r["audit_hash"]
    assert baseline == capas.reproduce_audit_hash(r)

    # each of the five canonical inputs, when mutated, must change the recomputed hash
    t1 = dict(r); t1["verdict"] = "REJECT"
    t2 = dict(r); t2["reason"] = r["reason"] + " (edited)"
    t3 = dict(r); t3["required_fields"] = list(r.get("required_fields") or []) + ["smuggled"]
    t4 = dict(r); t4["input_claim"] = {**r["input_claim"], "text": "a stronger claim"}
    t5 = dict(r); t5["invariant_audit"] = {"verdict": "FLAGGED"}
    for tampered in (t1, t2, t3, t4, t5):
        assert capas.reproduce_audit_hash(tampered) != baseline
        # and verify_audit_hash flags the mismatch (claimed audit_hash no longer matches recompute)
        assert capas.verify_audit_hash(tampered)["verified"] is False


def test_non_canonical_field_does_not_change_hash():
    r = capas_sdk.gate(
        "statistical_confidence",
        {"p_value": 0.01, "alpha": 0.05, "effect_direction_confirmed": True},
        "effect", "noncanon",
    )
    base = capas.reproduce_audit_hash(r)
    smuggled = dict(r)
    smuggled["did_you_mean"] = {"anything": "here"}
    smuggled["resolution"] = "totally different"
    # these fields are NOT part of the canonical body -> hash is unchanged
    assert capas.reproduce_audit_hash(smuggled) == base
    # but the claimed audit_hash still verifies, so the result is not flagged as tampered
    assert capas.verify_audit_hash(smuggled)["verified"] is True


# ---------------------------------------------------------------------------
# build_admissibility_certificate across verdicts
# ---------------------------------------------------------------------------
def _cert(r):
    c = r["admissibility_certificate"]
    assert set(c) >= {
        "calculus_version", "metaphor", "claim_contract",
        "lattice", "dialectic", "proof_obligations", "next_action",
    }
    axes = c["lattice"]["axes"]
    assert set(axes) == {"contract", "evidence", "boundary", "provenance", "defeaters"}
    for axis in axes.values():
        assert isinstance(axis["score"], int) and isinstance(axis["level"], str)
    return c


def test_certificate_accept_path():
    r = capas_sdk.gate(
        "statistical_confidence",
        {"p_value": 0.01, "alpha": 0.05, "effect_direction_confirmed": True},
        "effect", "ca")
    assert r["verdict"] == "ACCEPT"
    c = _cert(r)
    assert c["lattice"]["reuse_boundary"] in {"claim_licensed", "training_ready"}
    assert c["next_action"]["kind"] in {
        "verify_provenance_for_training", "approve_for_controlled_reuse"}
    # ACCEPT contract is fully registered, evidence axis at its top rung
    assert c["claim_contract"]["registered"] is True
    assert c["lattice"]["axes"]["evidence"]["score"] >= 3


def test_certificate_reject_path():
    r = capas_sdk.gate(
        "statistical_confidence",
        {"p_value": 0.40, "alpha": 0.05, "effect_direction_confirmed": True},
        "effect", "cr")
    assert r["verdict"] == "REJECT"
    c = _cert(r)
    assert c["lattice"]["reuse_boundary"] == "claim_excluded"
    assert c["next_action"]["kind"] == "exclude_or_replace_evidence"
    # REJECT records the warrant as a rebuttal
    assert c["dialectic"]["rebuttals"], "REJECT must carry a rebuttal"


def test_certificate_rewrite_path():
    r = capas_sdk.gate(
        "universal_anchor_claim",
        {"anchor_mode": "relative_anchor", "local_property_tests_pass": True,
         "relative_anchor_reference": "baseline-X", "relative_anchor_comparison_pass": True},
        "universal correctness", "cw")
    assert r["verdict"] == "REWRITE"
    c = _cert(r)
    assert c["lattice"]["reuse_boundary"] == "bounded_rewrite"
    assert c["next_action"]["kind"] == "edit_and_resubmit"
    # non-absolute anchor contract forbids ACCEPT and emits that proof obligation
    assert c["claim_contract"]["absolute_accept_only"] is True
    assert any("non-absolute anchors" in po for po in c["proof_obligations"])
    assert any("edit claim.text" in po for po in c["proof_obligations"])


def test_certificate_hold_missing_evidence_path():
    r = capas_sdk.gate("statistical_confidence", {}, "effect", "ch")
    assert r["verdict"] == "HOLD"
    c = _cert(r)
    assert c["next_action"]["kind"] == "supply_evidence"
    # missing fields surface as both proof obligations and dialectic undercutters
    assert any(po.startswith("evidence: provide") for po in c["proof_obligations"])
    assert any(u.startswith("missing ") for u in c["dialectic"]["undercutters"])


def test_certificate_schema_error_hold_carries_rederivable_hash():
    # malformed payload (claim not a dict) -> schema-error HOLD branch in decide_external_claim
    bad = {"schema_version": SCHEMA, "claim": "not-a-dict", "evidence": {}}
    r = capas.decide_external_claim(bad)
    assert r["verdict"] == "HOLD"
    assert r["schema_errors"], "schema-error HOLD must list errors"
    # even a schema-error HOLD carries a re-derivable audit_hash (uniform contract)
    assert r["audit_hash"] == capas.reproduce_audit_hash(r)
    c = _cert(r)
    assert c["lattice"]["reuse_boundary"] == "schema_blocked"
    assert c["next_action"]["kind"] in {"repair_schema", "register_claim_type"}


def test_certificate_unregistered_claim_type_path():
    bad = _payload("totally_made_up_type", {"foo": 1}, "claim", "u")
    r = capas.decide_external_claim(bad)
    c = _cert(r)
    assert c["claim_contract"]["registered"] is False
    # an unregistered contract forces a "register a claim type" next action and proof obligation
    assert c["next_action"]["kind"] == "register_claim_type"


# ---------------------------------------------------------------------------
# direct exercise of the lattice/argument helpers
# ---------------------------------------------------------------------------
def test_axis_clamps_out_of_range_scores():
    levels = capas.ADMISSIBILITY_AXIS_LEVELS["contract"]
    top = capas._axis("contract", 999)
    bottom = capas._axis("contract", -42)
    assert top["score"] == len(levels) - 1
    assert top["level"] == levels[-1]
    assert bottom["score"] == 0
    assert bottom["level"] == levels[0]
    mid = capas._axis("contract", 1)
    assert mid["score"] == 1 and mid["level"] == levels[1]


def test_registered_contract_branches():
    # registered ordinary spec
    reg = capas._registered_contract_for_claim("statistical_confidence", {})
    assert reg["registered"] is True
    assert reg["required_fields"] and reg["anchor_license"] is None

    # universal_anchor with a known anchor_mode -> anchor contract branch
    anchored = capas._registered_contract_for_claim(
        "universal_anchor_claim", {"anchor_mode": "relative_anchor"})
    assert anchored["registered"] is True
    assert anchored["anchor_mode"] == "relative_anchor"
    assert anchored["anchor_license"] is not None
    assert anchored["absolute_accept_only"] is True  # non-absolute

    # absolute_anchor -> absolute_accept_only False
    absolute = capas._registered_contract_for_claim(
        "universal_anchor_claim", {"anchor_mode": "absolute_anchor"})
    assert absolute["absolute_accept_only"] is False

    # unregistered type
    un = capas._registered_contract_for_claim("nope_not_real", {})
    assert un["registered"] is False
    assert un["required_fields"] == [] and un["anchor_license"] is None


def test_provenance_axis_score_each_rung():
    # all-true short-circuit -> 4
    assert capas._provenance_axis_score(
        {"external_review": True, "semantic_alignment": True, "witness_independence": True}) == 4
    # rung 3: external_review + semantic_alignment + witness_independence but not all-true overall
    assert capas._provenance_axis_score({
        "external_review": True, "semantic_alignment": True,
        "witness_independence": True, "source_backed_evidence": False}) == 3
    # rung 2: source_backed_evidence + provenance_sources (with a False elsewhere)
    assert capas._provenance_axis_score({
        "source_backed_evidence": True, "provenance_sources": True,
        "external_review": False}) == 2
    # rung 1: provenance_sources only (other gating keys False)
    assert capas._provenance_axis_score({
        "provenance_sources": True, "source_backed_evidence": False,
        "external_review": False}) == 1
    # rung 0: nothing present
    assert capas._provenance_axis_score({}) == 0
    assert capas._provenance_axis_score({"external_review": False}) == 0


def test_next_action_for_result_kinds():
    # register: unregistered contract + schema error naming the missing contract
    a = capas._next_action_for_result(
        {"verdict": "HOLD",
         "schema_errors": ["no registered evidence contract for claim.type"]},
        contract_registered=False)
    assert a["kind"] == "register_claim_type"

    # repair_schema: schema errors but contract registered
    b = capas._next_action_for_result(
        {"verdict": "HOLD", "schema_errors": ["evidence.x is not allowed"]},
        contract_registered=True)
    assert b["kind"] == "repair_schema"

    # supply_evidence: registered, no schema errors, missing fields
    c = capas._next_action_for_result(
        {"verdict": "HOLD", "schema_errors": [], "missing_fields": ["p_value"]},
        contract_registered=True)
    assert c["kind"] == "supply_evidence"

    # edit_and_resubmit / exclude_or_replace_evidence
    d = capas._next_action_for_result({"verdict": "REWRITE"}, contract_registered=True)
    assert d["kind"] == "edit_and_resubmit"
    e = capas._next_action_for_result({"verdict": "REJECT"}, contract_registered=True)
    assert e["kind"] == "exclude_or_replace_evidence"

    # ACCEPT not-yet-fine-tune-ready vs ready
    f = capas._next_action_for_result(
        {"verdict": "ACCEPT", "fine_tune_ready": False}, contract_registered=True)
    assert f["kind"] == "verify_provenance_for_training"
    g = capas._next_action_for_result(
        {"verdict": "ACCEPT", "fine_tune_ready": True}, contract_registered=True)
    assert g["kind"] == "approve_for_controlled_reuse"

    # fallthrough hold_for_review
    h = capas._next_action_for_result({"verdict": "HOLD"}, contract_registered=True)
    assert h["kind"] == "hold_for_review"


def test_exception_queue_entry_for_non_accept_and_none_for_clean_accept():
    rej = capas_sdk.gate(
        "statistical_confidence",
        {"p_value": 0.40, "alpha": 0.05, "effect_direction_confirmed": True},
        "effect", "q_rej")
    entry = capas.exception_queue_entry(7, rej)
    assert entry is not None
    assert entry["index"] == 7
    assert entry["claim_id"] == "q_rej"
    assert entry["verdict"] == "REJECT"
    assert entry["reuse_boundary"] == "claim_excluded"
    assert isinstance(entry["proof_obligations"], list)

    # a result without an admissibility_certificate yields None
    assert capas.exception_queue_entry(0, {"verdict": "HOLD"}) is None


# ---------------------------------------------------------------------------
# SDK certificate route (capas_sdk.certificate -> capas_rcc.rcc)
# ---------------------------------------------------------------------------
def test_sdk_certificate_route_returns_dict():
    out = capas_sdk.certificate(
        "statistical_confidence",
        {"p_value": 0.01, "alpha": 0.05, "effect_direction_confirmed": True},
        "effect", "sdk_cert")
    assert isinstance(out, dict) and out, "SDK certificate route must return a non-empty dict"


def _run_all():
    import inspect
    fns = [
        obj for name, obj in sorted(globals().items())
        if name.startswith("test_") and inspect.isfunction(obj)
    ]
    for fn in fns:
        fn()
    print(f"OK {len(fns)}/{len(fns)} certificate/audit_hash tests passed.")


if __name__ == "__main__":
    _run_all()
