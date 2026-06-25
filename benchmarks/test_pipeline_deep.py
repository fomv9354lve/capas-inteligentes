#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""Exercise the intake -> route -> propose triage pipeline end to end — real tests, not gaming.

These three modules are the PROPOSE-side membrane (the LLM imagines; CAPAS disposes). The
deterministic verdict never reads their output, but their fail-closed/triangulation logic is the
moat-preserving part and is barely covered today. This drives the real decision paths:

  - capas_intake: span-grounded K-of-K and multi-model triangulation, DEFER on disagreement,
    DEFER on affirmed-without-span, geometric residual, fail-closed payload assembly, and the
    live extractors' no-key abstain branch.
  - capas_route: strongest-feasible rung selection across re-execution / quantum / zk / signed
    provenance / attest-class / form, strongest-first ordering, jurisdiction demand mapping,
    and the downgrade branches (unpinned env, post-hoc seed, unjustified tolerance).
  - capas_propose: deterministic keyword proposal (no key), evidence-contract lookup, the
    non-binding invariant, and the unrecognized-family -> propose-nothing branch.

Injected mock extractors are deterministic (no network). Live extractors are exercised only via
their no-key abstain path so the suite never calls an external API.
Run: `python3 benchmarks/test_pipeline_deep.py` or pytest.
"""
from __future__ import annotations

import os

import capas
import capas_intake
import capas_propose
import capas_route

_failures: list[str] = []


def check(cond: bool, msg: str) -> None:
    if cond:
        print(f"  PASS  {msg}")
    else:
        _failures.append(msg)
        print(f"  FAIL  {msg}")


# ── deterministic injected extractors (no network) ───────────────────────────
def mk_extractor(supported, span="reported p < 0.01 in the cohort"):
    """A deterministic extractor returning a fixed (supported, span) verdict."""
    def _ex(field, claim_text, source_text, idx):
        return {"supported": supported, "span": span}
    return _ex


def abstaining(field, claim_text, source_text, idx):
    return {"supported": None, "span": None}


def disagreeing(field, claim_text, source_text, idx):
    # alternates True/False across the K independent runs -> must DEFER
    return {"supported": (idx % 2 == 0), "span": "a span"}


# ── capas_intake.extract_field ───────────────────────────────────────────────
def test_extract_field():
    print("\n[capas_intake.extract_field]")
    claim, src = "p<0.01", "the study reported p < 0.01"

    r = capas_intake.extract_field("p_value", claim, src, mk_extractor(True), k=3)
    check(r["status"] == "EXTRACTED", "K-agreeing supported+span -> EXTRACTED")
    check(r["value"] is True, "extracted value is the agreed boolean True")
    check(0.0 < r["residual"] < 1.0, "graded residual in (0,1), never 0 (bridge ceiling)")
    # residual = 1/(1+agreers); k=3 agreers -> 0.25
    check(abs(r["residual"] - 0.25) < 1e-9, "residual = 1/(1+3 agreers) = 0.25")
    check(r["span"], "an EXTRACTED field carries its grounding span")

    r = capas_intake.extract_field("p_value", claim, src, mk_extractor(False), k=3)
    check(r["status"] == "EXTRACTED" and r["value"] is False, "K-agreeing False -> EXTRACTED False")

    # affirmed with NO span -> must DEFER (cannot fabricate a grounding)
    r = capas_intake.extract_field("p_value", claim, src, mk_extractor(True, span=None), k=3)
    check(r["status"] == "DEFER" and r["value"] is None, "affirmed-without-span -> DEFER (not fabricated)")
    check(r["residual"] == 1.0, "deferred field residual is 1.0 (fully unresolved)")

    # disagreeing independent runs -> DEFER
    r = capas_intake.extract_field("p_value", claim, src, disagreeing, k=3)
    check(r["status"] == "DEFER", "disagreeing independent extractions -> DEFER")

    # all abstain -> DEFER
    r = capas_intake.extract_field("p_value", claim, src, abstaining, k=3)
    check(r["status"] == "DEFER", "all-abstaining extractions -> DEFER")
    check(len(r["votes"]) == 3, "votes list records all K runs")


# ── capas_intake.extract_field_multimodel ────────────────────────────────────
def test_extract_field_multimodel():
    print("\n[capas_intake.extract_field_multimodel]")
    claim, src = "p<0.01", "p < 0.01"
    # two distinct models that agree True+span -> EXTRACTED
    r = capas_intake.extract_field_multimodel(
        "p_value", claim, src, [mk_extractor(True), mk_extractor(True)])
    check(r["status"] == "EXTRACTED" and r["value"] is True, "2 distinct models agree -> EXTRACTED")
    check(r["models_agreeing"] == 2, "independence groups counted as MODELS (=2)")
    check(r["residual"] == round(1 / 3, 4), "residual = 1/(1+2 model groups) = 0.3333 (rounded)")

    # systematic single-model misread exposed: one model True, one False -> DEFER
    r = capas_intake.extract_field_multimodel(
        "p_value", claim, src, [mk_extractor(True), mk_extractor(False)])
    check(r["status"] == "DEFER", "models disagree -> DEFER (catches systematic single-model misread)")
    check(r["models"] == 2, "DEFER result reports model count")

    # affirmed but no span across models -> DEFER
    r = capas_intake.extract_field_multimodel(
        "p_value", claim, src, [mk_extractor(True, span=None), mk_extractor(True, span=None)])
    check(r["status"] == "DEFER", "models affirm but no span -> DEFER")


# ── capas_intake.intake ──────────────────────────────────────────────────────
def test_intake():
    print("\n[capas_intake.intake]")
    ctype = "statistical_confidence"
    required = capas.required_fields_for_claim(ctype)
    claim = "the effect was statistically significant"
    src = "we observed p < 0.01 with the predicted effect direction"

    # all fields supported -> complete payload, NOT fail-closed
    res = capas_intake.intake(claim, ctype, src, mk_extractor(True), k=3)
    check(set(res["evidence_extracted"].keys()) == set(required),
          "all required fields extracted -> complete evidence")
    check(res["deferred_fields"] == [], "nothing deferred when every field is grounded")
    check(res["fail_closed"] is False, "complete payload is NOT fail-closed")
    check(res["payload"]["schema_version"] == "capas-claim-payload-v3", "payload carries schema version")
    check(res["payload"]["claim"]["type"] == ctype, "payload claim.type matches requested type")
    check(0.0 < res["extraction_residual"] <= 1.0, "extraction residual in (0,1] (geometric product)")
    check(len(res["per_field"]) == len(required), "per_field entry for every required field")

    # all abstain -> every field deferred -> fail-closed, empty evidence
    res = capas_intake.intake(claim, ctype, src, abstaining, k=3)
    check(set(res["deferred_fields"]) == set(required), "abstaining extractor defers all required fields")
    check(res["evidence_extracted"] == {}, "no evidence grounded when extractor abstains")
    check(res["fail_closed"] is True, "any deferred required field -> fail_closed True (gate will HOLD)")
    check(res["extraction_residual"] == 1.0, "all-deferred residual stays 1.0")

    # unknown claim type -> no required fields -> empty but well-formed payload
    res = capas_intake.intake(claim, "no_such_claim_type", src, mk_extractor(True))
    check(res["evidence_extracted"] == {} and res["deferred_fields"] == [],
          "unknown claim type yields empty payload (engine never guesses fields)")


# ── capas_intake.intake_multimodel ───────────────────────────────────────────
def test_intake_multimodel():
    print("\n[capas_intake.intake_multimodel]")
    ctype = "reproducibility_check"
    required = capas.required_fields_for_claim(ctype)
    claim, src = "the result reproduces", "artifact released; independent team reproduced it"

    res = capas_intake.intake_multimodel(claim, ctype, src, [mk_extractor(True), mk_extractor(True)])
    check(set(res["evidence_extracted"].keys()) == set(required),
          "multi-model intake grounds all fields when models agree")
    check(res["fail_closed"] is False, "agreeing multi-model intake is not fail-closed")
    check(res["payload"]["claim"]["type"] == ctype, "multi-model payload type matches")

    # disagreeing models -> defer everything -> fail-closed
    res = capas_intake.intake_multimodel(claim, ctype, src, [mk_extractor(True), mk_extractor(False)])
    check(set(res["deferred_fields"]) == set(required), "model disagreement defers all fields")
    check(res["fail_closed"] is True, "disagreeing multi-model intake fails closed")


# ── capas_intake live extractors: no-key abstain (no network) ─────────────────
def test_live_extractors_abstain_without_key():
    print("\n[capas_intake live extractors — no-key abstain]")
    saved = {k: os.environ.pop(k, None) for k in
             ("GEMINI_KEY", "GOOGLE_API_KEY", "DEEPSEEK_KEY", "CAPAS_TRIAGE_KEY")}
    try:
        g = capas_intake.gemini_extractor("p_value", "c", "s", 0)
        check(g == {"supported": None, "span": None}, "gemini_extractor abstains with no key (fail-closed)")
        d = capas_intake.deepseek_extractor("p_value", "c", "s", 0)
        check(d == {"supported": None, "span": None}, "deepseek_extractor abstains with no key (fail-closed)")
    finally:
        for k, v in saved.items():
            if v is not None:
                os.environ[k] = v


# ── capas_route.route ────────────────────────────────────────────────────────
def test_route():
    print("\n[capas_route.route]")
    LEGAL_RUNGS = set(capas_route.SOUNDNESS)

    cases = [
        ({"crypto": {"digest": "abc"}}, "re-execution", "GATE"),
        ({"accounting": {"a": 1}}, "re-execution", "GATE"),
        ({"zk_proof": {"pi": 1}}, "zk-snark", "GATE"),
        ({"provenance": {"sig": "x"}}, "signed-provenance", "ATTEST"),
        ({"intervention_or_natural_experiment": True}, "attest", "ATTEST"),
        ({}, "form", "FORM"),
    ]
    for ev, rung, scope in cases:
        r = capas_route.route({"evidence": ev}, "US")
        check(r["selected_rung"] == rung, f"evidence {list(ev) or '∅'} -> rung {rung}")
        check(r["scope"] == scope, f"evidence {list(ev) or '∅'} -> scope {scope}")
        check(r["selected_rung"] in LEGAL_RUNGS, "selected rung is a known soundness rung")
        check(r["soundness_basis"] == capas_route.SOUNDNESS[rung], "soundness basis matches rung table")
        check(r["decision_path"] == "deterministic; no LLM", "route is deterministic (no LLM)")

    # strongest-first: when BOTH re-execution and signed-provenance qualify, re-execution wins
    r = capas_route.route({"evidence": {"crypto": {"d": 1}, "provenance": {"s": 1}}}, "EU")
    check(r["selected_rung"] == "re-execution", "strongest-feasible rung selected over weaker (re-execution > signed)")
    check(len(r["plan"]) >= 2, "plan lists all qualifying candidate rungs")
    plan_rungs = [c["rung"] for c in r["plan"]]
    check(plan_rungs == sorted(plan_rungs, key=lambda x: [
        "re-execution", "quantum-statevector", "zk-snark", "cvqc-mahadev",
        "signed-provenance", "attest", "form"].index(x)),
        "plan is ordered strongest-first")

    # jurisdiction demand mapping (real strings per jurisdiction)
    for j in ("EU", "US", "UK", "SG", "CN", "GLOBAL"):
        r = capas_route.route({"evidence": {"crypto": {"d": 1}}}, j)
        check(r["jurisdiction_demand_satisfied"] == capas_route.JURISDICTION_DEMAND[j],
              f"jurisdiction {j} maps to its real demand string")
    # unknown jurisdiction -> GLOBAL fallback
    r = capas_route.route({"evidence": {"crypto": {"d": 1}}}, "ZZ")
    check(r["jurisdiction_demand_satisfied"] == capas_route.JURISDICTION_DEMAND["GLOBAL"],
          "unknown jurisdiction falls back to GLOBAL demand")
    # None jurisdiction -> GLOBAL
    r = capas_route.route({"evidence": {"crypto": {"d": 1}}})
    check(r["jurisdiction"] is None, "route accepts no-jurisdiction call")
    check(r["jurisdiction_demand_satisfied"] == capas_route.JURISDICTION_DEMAND["GLOBAL"],
          "no jurisdiction -> GLOBAL demand")


def test_route_downgrade_branches():
    print("\n[capas_route.route — downgrade branches]")
    # stochastic method with no seed -> attest (not reproducible)
    r = capas_route.route({"evidence": {"reproduction": {"stochastic": {"method": "mcmc", "seed": None}}}})
    check(r["selected_rung"] == "attest", "stochastic method with no seed -> attest")

    # post-hoc (not pre-committed) seed -> signed-provenance (seed-conditional)
    r = capas_route.route({"evidence": {"reproduction": {
        "stochastic": {"method": "mcmc", "seed": 42, "committed_before_data": False}}}})
    check(r["selected_rung"] == "signed-provenance", "post-hoc seed -> signed-provenance (seed-conditional)")

    # derivation with UNPINNED environment -> still re-execution but flagged not pinned
    r = capas_route.route({"evidence": {"derivation": {"src": "a", "out": "b"}, "environment": {}}})
    check(r["selected_rung"] == "re-execution", "derivation present -> re-execution rung")
    check(any("NOT pinned" in c["reason"] for c in r["plan"]),
          "unpinned environment is flagged in the plan reason")

    # derivation with fully pinned environment
    r = capas_route.route({"evidence": {"derivation": {"src": "a"}, "environment": {
        "language": "py", "version": "3.12", "os": "linux", "locale": "C"}}})
    check(any("pinned environment" in c["reason"] for c in r["plan"]),
          "pinned environment is recognized in the plan reason")


# ── capas_propose ────────────────────────────────────────────────────────────
def test_propose():
    print("\n[capas_propose]")
    saved = {k: os.environ.pop(k, None) for k in ("DEEPSEEK_KEY", "CAPAS_TRIAGE_KEY")}
    try:
        # deterministic keyword proposal (no key) — causal terms present
        p = capas_propose.propose(
            "We established a causal mechanism via an intervention, controlling for confounders, "
            "with the temporal order established.")
        check(p["claim_type"] == "causal_mechanism_claim",
              "keyword proposal maps causal text -> causal_mechanism_claim")
        check(p["binding"] is False, "proposal is NON-BINDING (the moat: it can never decide)")
        check("deterministic" in p["method"], "no-key path uses deterministic keyword method")
        check(p["claim_type"] in capas.CLAIM_TYPE_REGISTRY, "proposed family is a real registry family")
        check(p["evidence_contract"]["required"], "proposal carries the family's required evidence contract")

        # statistical terms -> statistical_confidence
        p = capas_propose.propose("the result was statistically significant at alpha with a low p-value")
        check(p["claim_type"] == "statistical_confidence", "stat terms -> statistical_confidence")

        # no matching terms -> propose nothing (engine never guesses)
        p = capas_propose.propose("the weather is nice today and lunch was good")
        check(p["claim_type"] is None, "no keyword hit -> proposes nothing")
        check(p["binding"] is False, "even the empty proposal is non-binding")

        # empty text -> nothing
        p = capas_propose.propose("")
        check(p["claim_type"] is None, "empty text -> proposes nothing")
    finally:
        for k, v in saved.items():
            if v is not None:
                os.environ[k] = v


def test_contract_for():
    print("\n[capas_propose.contract_for]")
    c = capas_propose.contract_for("statistical_confidence")
    check(c is not None and isinstance(c["required"], list), "contract_for returns required-field list")
    check(set(c["required"]) == set(capas.required_fields_for_claim("statistical_confidence")),
          "contract required fields match the engine's registry")
    check("description" in c, "contract carries the family description")
    check(capas_propose.contract_for("definitely_not_a_family") is None,
          "contract_for(unknown) -> None (no fabricated contract)")


def test_pipeline_end_to_end():
    print("\n[pipeline: propose -> intake -> route]")
    saved = {k: os.environ.pop(k, None) for k in ("DEEPSEEK_KEY", "CAPAS_TRIAGE_KEY")}
    try:
        text = "the result was statistically significant at alpha with a low p-value"
        proposal = capas_propose.propose(text)
        ctype = proposal["claim_type"]
        check(ctype == "statistical_confidence", "propose stage classifies the claim")

        # intake grounds the proposed family's fields
        intake = capas_intake.intake(text, ctype, "we observed p < 0.01 at alpha=0.05, effect as predicted",
                                     mk_extractor(True), k=3)
        payload = intake["payload"]
        check(payload["claim"]["type"] == ctype, "intake builds a payload for the proposed family")
        check(intake["fail_closed"] is False, "grounded intake is not fail-closed")

        # route the assembled payload
        routed = capas_route.route(payload, "EU")
        check(routed["selected_rung"] in capas_route.SOUNDNESS,
              "route selects a rung for the assembled payload")
        # boolean-only stat evidence is attest-class design evidence -> attest or form
        check(routed["scope"] in {"ATTEST", "FORM", "GATE"}, "routed scope is a legal scope")
    finally:
        for k, v in saved.items():
            if v is not None:
                os.environ[k] = v


def main():
    test_extract_field()
    test_extract_field_multimodel()
    test_intake()
    test_intake_multimodel()
    test_live_extractors_abstain_without_key()
    test_route()
    test_route_downgrade_branches()
    test_propose()
    test_contract_for()
    test_pipeline_end_to_end()

    print()
    if _failures:
        print(f"FAILED ({len(_failures)}):")
        for f in _failures:
            print(f"  - {f}")
        raise SystemExit(1)
    print("ALL PIPELINE TESTS PASSED")


# pytest entry points
def test_intake_pipeline_suite():
    test_extract_field()
    test_extract_field_multimodel()
    test_intake()
    test_intake_multimodel()
    test_live_extractors_abstain_without_key()
    assert not _failures, _failures


def test_route_propose_suite():
    test_route()
    test_route_downgrade_branches()
    test_propose()
    test_contract_for()
    test_pipeline_end_to_end()
    assert not _failures, _failures


if __name__ == "__main__":
    main()
