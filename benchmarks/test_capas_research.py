#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""Exercise the research/cognitive entry points in capas.py with REAL, valid inputs.

Slice: the local "scientific reasoning" pipeline that capas.py actually ships in-module
(extract -> align -> deterministic gate -> reasoning checklist -> standalone pipeline),
plus the source-ingest and regex-extraction helpers that feed it.

These are deterministic guardrails (NOT a scientific oracle, NOT an LLM). Every path here is
driven WITHOUT a live LLM, network, or external dataset by supplying source text inline via
`payload["source"]["text"]`, or by writing a tiny corpus fixture INSIDE the repo (the only place
the path guard allows) into a scratch dir we clean up.

Honest limits (paths that genuinely need deps -> exercised only via their declined/note branch,
never via a real fetch/parse):
  * `_read_url_source` real HTTP fetch -> needs network. We only drive the `allow_web=False`
    decline branch (returns a note, no socket opened).
  * `_read_pdf_source_path` real parse -> needs `pypdf` + a real PDF. We only drive the
    not-parsed/missing-file note branch.
These are reported as untestable-without-deps in the agent summary, not faked.

Run: `python3 benchmarks/test_capas_research.py` or `pytest benchmarks/test_capas_research.py`.
"""
from __future__ import annotations

import hashlib as _hashlib
import json
import shutil

import capas

SCHEMA = capas.CAPAS_CLAIM_SCHEMA_VERSION
LEGAL_VERDICTS = {"ACCEPT", "REWRITE", "REJECT", "HOLD"}


def _payload(claim_type: str, text: str, evidence: dict, source_text: str | None = None) -> dict:
    p: dict = {
        "schema_version": SCHEMA,
        "claim": {"id": "c1", "type": claim_type, "text": text},
        "evidence": dict(evidence),
    }
    if source_text is not None:
        p["source"] = {"id": "s1", "kind": "text", "text": source_text}
    return p


# --------------------------------------------------------------------------------------
# align_claim_text: ALIGNED / WARN / MISALIGNED / HOLD_SCHEMA branches
# --------------------------------------------------------------------------------------
def test_align_aligned() -> None:
    p = _payload(
        "exact_model_solution",
        "the exact solution within the model is reproduced to tolerance",
        {"abs_error": 0.0, "tolerance": 1e-3},
    )
    out = capas.align_claim_text(p)
    assert out["alignment_status"] == "ALIGNED"
    assert out["alignment_pass"] is True
    assert out["issues"] == []
    # claim text mentions an expected concept for the type
    assert out["claim_type_terms_found"], "expected at least one matched claim-type term"


def test_align_warn_missing_vocab() -> None:
    # physical_accuracy claim text with no expected vocab -> WARN (warning, not a hard issue)
    p = _payload(
        "physical_accuracy",
        "the widget performs as intended overall",
        {"within_chemical_accuracy": True},
    )
    out = capas.align_claim_text(p)
    assert out["alignment_status"] == "WARN"
    assert out["alignment_pass"] is True
    assert out["warnings"], "WARN must carry at least one warning"


def test_align_misaligned_exact_model_with_experimental_scope() -> None:
    # exact_model_solution licenses truth-in-a-model; experimental/real-world prose is a hard issue
    p = _payload(
        "exact_model_solution",
        "measured experimentally in a real-world laboratory device",
        {"abs_error": 0.0, "tolerance": 1e-3},
    )
    out = capas.align_claim_text(p)
    assert out["alignment_status"] == "MISALIGNED"
    assert out["alignment_pass"] is False
    assert any("exact_model_solution" in issue for issue in out["issues"])
    assert out["experiment_scope_patterns_found"], "experimental scope should be detected"


def test_align_universal_anchor_overclaim_is_misaligned() -> None:
    # strong physical-correctness prose while universal_anchor_pass is False -> hard issue
    p = _payload(
        "universal_anchor_claim",
        "this is provably exact and physically correct everywhere",
        {
            "anchor_mode": "relative_anchor",
            "local_property_tests_pass": True,
            "universal_anchor_pass": False,
        },
    )
    out = capas.align_claim_text(p)
    assert out["alignment_status"] == "MISALIGNED"
    assert out["strong_physical_patterns_found"], "strong physical patterns expected"


def test_align_hold_schema_on_bad_payload() -> None:
    # payload that fails CAPAS schema validation short-circuits to HOLD_SCHEMA before semantics
    out = capas.align_claim_text({"claim": {"type": "exact_model_solution"}})
    assert out["alignment_status"] == "HOLD_SCHEMA"
    assert out["alignment_pass"] is False
    assert out["issues"], "schema errors must be surfaced"


# --------------------------------------------------------------------------------------
# extraction helpers: _extract_number / _extract_bool / _extract_string / spans
# --------------------------------------------------------------------------------------
def test_extract_primitive_helpers() -> None:
    assert capas._extract_number("abs_error = 0.0", "abs_error") == 0.0
    assert capas._extract_number("tolerance: 1e-3", "tolerance") == 1e-3
    assert capas._extract_number("no value here", "abs_error") is None
    assert capas._extract_bool("within_chemical_accuracy = true", "within_chemical_accuracy") is True
    assert capas._extract_bool("protocol_registered: no", "protocol_registered") is False
    assert capas._extract_bool("absent", "protocol_registered") is None
    assert capas._extract_string("anchor_mode = absolute_anchor", "anchor_mode") == "absolute_anchor"
    assert capas._extract_string("missing", "anchor_mode") is None
    # field name with underscores must match underscore/space/hyphen variants
    assert capas._extract_bool("local property tests pass: pass", "local_property_tests_pass") is True


def test_extract_field_from_sources_returns_span() -> None:
    sources = [{"source_id": "s1", "kind": "text", "text": "line one\nabs_error = 0.0\n", "retrieval_status": "read", "retrieval_note": ""}]
    value, span = capas._extract_field_from_sources(sources, "abs_error", "number")
    assert value == 0.0
    assert span is not None
    assert span["field"] == "abs_error"
    assert span["source_id"] == "s1"
    assert span["line"] == 2  # span is 1-indexed and points at the matched line
    # a field that is absent yields (None, None)
    missing_value, missing_span = capas._extract_field_from_sources(sources, "tolerance", "number")
    assert missing_value is None and missing_span is None


# --------------------------------------------------------------------------------------
# extract_evidence: complete / partial / none + candidate payload assembly
# --------------------------------------------------------------------------------------
def test_extract_evidence_complete_from_inline_text() -> None:
    src = "abs_error = 0.0\ntolerance = 1e-3\nverification_independence = independent\n"
    p = _payload("exact_model_solution", "exact model solution to tolerance", {}, src)
    out = capas.extract_evidence(p)
    assert out["extraction_status"] == "complete"
    assert out["extracted_evidence"]["abs_error"] == 0.0
    assert out["extracted_evidence"]["tolerance"] == 1e-3
    assert "abs_error" in out["evidence_spans"]
    assert out["missing_fields_after_extraction"] == []
    # candidate payload merges extracted evidence and carries the schema version
    cand = out["candidate_payload"]
    assert cand["schema_version"] == SCHEMA
    assert cand["evidence"]["abs_error"] == 0.0


def test_extract_evidence_partial() -> None:
    # only abs_error present; tolerance missing -> partial, with the missing field named
    src = "abs_error = 0.0\n"
    p = _payload("exact_model_solution", "exact model solution", {}, src)
    out = capas.extract_evidence(p)
    assert out["extraction_status"] == "partial"
    assert "tolerance" in out["missing_fields_after_extraction"]


def test_extract_evidence_none_no_source() -> None:
    p = _payload("exact_model_solution", "exact model solution", {})
    out = capas.extract_evidence(p)
    assert out["extraction_status"] == "none"
    assert "no source text was supplied" in out["extraction_notes"]


# --------------------------------------------------------------------------------------
# retrieve_evidence_snippets: matched-line path + retrieval-note path
# --------------------------------------------------------------------------------------
def test_retrieve_snippets_matches_required_fields() -> None:
    src = "intro line\nabs_error = 0.0\nmid\ntolerance = 1e-3\n"
    p = _payload("exact_model_solution", "exact model solution", {}, src)
    snippets = capas.retrieve_evidence_snippets(p)
    matched = {f for s in snippets for f in s["matched_fields"]}
    assert {"abs_error", "tolerance"} <= matched
    for s in snippets:
        assert s["line"] is not None
        assert s["snippet"]


def test_retrieve_snippets_surfaces_retrieval_note_for_undelivered_source() -> None:
    # a web source with allow_web=False is never fetched; it surfaces a note-only snippet
    p = {
        "schema_version": SCHEMA,
        "claim": {"id": "c1", "type": "exact_model_solution", "text": "exact model solution"},
        "evidence": {},
        "source": {"id": "s1", "url": "https://example.com/paper"},
    }
    snippets = capas.retrieve_evidence_snippets(p, allow_web=False)
    assert snippets, "note-bearing source should still produce a snippet entry"
    assert snippets[0]["retrieval_note"], "decline note must be surfaced"
    assert snippets[0]["matched_fields"] == []


# --------------------------------------------------------------------------------------
# scientific_reasoning_report: CLEAR / WARN / BLOCK_ACCEPT branches
# --------------------------------------------------------------------------------------
def test_reasoning_clear_when_complete_aligned_accept() -> None:
    src = "abs_error = 0.0\ntolerance = 1e-3\nverification_independence = independent\n"
    p = _payload("exact_model_solution", "the exact model solution reproduced to tolerance", {}, src)
    extraction = capas.extract_evidence(p)
    candidate = extraction["candidate_payload"]
    alignment = capas.align_claim_text(candidate)
    gate = capas.decide_external_claim(candidate)
    report = capas.scientific_reasoning_report(candidate, extraction, alignment, gate)
    assert report["reasoning_status"] == "CLEAR"
    assert report["risks"] == []


def test_reasoning_warn_on_weak_independence() -> None:
    # complete + aligned but verification independence undeclared -> a risk, gate not ACCEPT -> WARN
    src = "abs_error = 0.0\ntolerance = 1e-3\n"
    p = _payload("exact_model_solution", "the exact model solution reproduced to tolerance", {}, src)
    extraction = capas.extract_evidence(p)
    candidate = extraction["candidate_payload"]
    alignment = capas.align_claim_text(candidate)
    gate = capas.decide_external_claim(candidate)
    report = capas.scientific_reasoning_report(candidate, extraction, alignment, gate)
    assert report["reasoning_status"] in {"WARN", "BLOCK_ACCEPT"}
    assert any("independence" in r for r in report["risks"])


def test_reasoning_block_accept_when_gate_accepts_with_open_risk() -> None:
    # Construct a candidate that the gate ACCEPTs but that still carries a reasoning risk
    # (missing source spans for required fields), forcing BLOCK_ACCEPT.
    candidate = {
        "schema_version": SCHEMA,
        "claim": {"id": "c1", "type": "exact_model_solution", "text": "exact model solution to tolerance"},
        "evidence": {"abs_error": 0.0, "tolerance": 1e-3},
    }
    gate = capas.decide_external_claim(candidate)
    assert gate["verdict"] == "ACCEPT"  # structurally complete evidence -> ACCEPT
    # extraction has NO spans (evidence came from the payload, not a parsed source)
    extraction = {
        "extraction_status": "complete",
        "required_fields": ["abs_error", "tolerance"],
        "evidence_spans": {},  # no auditable spans -> reasoning risk
    }
    alignment = capas.align_claim_text(candidate)
    report = capas.scientific_reasoning_report(candidate, extraction, alignment, gate)
    assert report["reasoning_status"] == "BLOCK_ACCEPT"
    assert any("span" in r for r in report["risks"])


# --------------------------------------------------------------------------------------
# standalone_pipeline: ACCEPT pass-through + the two HOLD-override safety welds
# --------------------------------------------------------------------------------------
def test_pipeline_accept_passthrough() -> None:
    src = "abs_error = 0.0\ntolerance = 1e-3\nverification_independence = independent\n"
    p = _payload("exact_model_solution", "the exact model solution reproduced to tolerance", {}, src)
    out = capas.standalone_pipeline(p)
    assert out["pipeline_status"] == "PASS"
    assert out["final_decision"]["verdict"] in LEGAL_VERDICTS
    assert out["fine_tune_ready"] is False
    # all sub-reports present
    for key in ("extraction", "semantic_alignment", "scientific_reasoning", "capas_gate_decision", "final_decision"):
        assert key in out


def test_pipeline_misalignment_overrides_accept_to_hold() -> None:
    # evidence is complete (gate would ACCEPT) but the prose overclaims experimental scope:
    # the pipeline must downgrade the final decision to HOLD (fail-closed weld).
    src = "abs_error = 0.0\ntolerance = 1e-3\n"
    p = _payload(
        "exact_model_solution",
        "measured experimentally in a real-world laboratory device",
        {},
        src,
    )
    out = capas.standalone_pipeline(p)
    assert out["semantic_alignment"]["alignment_status"] == "MISALIGNED"
    assert out["final_decision"]["verdict"] == "HOLD"
    assert out["final_decision"]["licensed_claim"] is None
    # the underlying gate may have said ACCEPT; the pipeline never ACCEPTs past a misalignment
    assert out["final_decision"]["verdict"] != "ACCEPT"


def test_pipeline_never_accepts_on_open_reasoning_risk() -> None:
    # complete evidence + aligned prose, but no source spans / weak independence can keep a risk open;
    # whatever the gate says, an ACCEPT may only survive if reasoning is not BLOCK_ACCEPT.
    src = "abs_error = 0.0\ntolerance = 1e-3\n"
    p = _payload("exact_model_solution", "the exact model solution reproduced to tolerance", {}, src)
    out = capas.standalone_pipeline(p)
    if out["scientific_reasoning"]["reasoning_status"] == "BLOCK_ACCEPT":
        assert out["final_decision"]["verdict"] != "ACCEPT"
    assert out["final_decision"]["verdict"] in LEGAL_VERDICTS


# --------------------------------------------------------------------------------------
# _source_records: text / corpus(json,jsonl,dir) / declined-pdf / declined-web branches
# --------------------------------------------------------------------------------------
def test_source_records_inline_text() -> None:
    p = _payload("exact_model_solution", "exact model solution", {}, "abs_error = 0.0\n")
    recs = capas._source_records(p)
    assert len(recs) == 1
    assert recs[0]["retrieval_status"] == "present"
    assert recs[0]["text"]


def test_source_records_declined_web_note_no_network() -> None:
    # allow_web=False: the URL is NEVER fetched; a decline note is recorded instead.
    p = {"claim": {"type": "exact_model_solution"}, "source": {"id": "s", "url": "https://example.com"}}
    recs = capas._source_records(p, allow_web=False)
    assert recs[0]["retrieval_status"] == "not_retrieved"
    assert "allow-web" in recs[0]["retrieval_note"]


def test_source_records_declined_pdf_note_missing_file() -> None:
    # PDF path that does not exist (or pypdf missing): note branch, no real parse.
    p = {"claim": {"type": "exact_model_solution"}, "source": {"id": "s", "kind": "pdf", "path": "no_such_research_file.pdf"}}
    recs = capas._source_records(p)
    assert recs[0]["kind"] == "pdf"
    assert recs[0]["retrieval_status"] == "not_parsed"
    assert recs[0]["retrieval_note"]


def test_source_records_corpus_json_inside_repo(tmp_corpus) -> None:
    json_rel = tmp_corpus("docs.json", json.dumps([
        {"id": "d1", "title": "abs_error report", "abstract": "abs_error = 0.0 and tolerance = 1e-3 within model"},
        {"id": "d2", "title": "unrelated", "abstract": "nothing relevant here"},
    ]))
    p = {
        "schema_version": SCHEMA,
        "claim": {"id": "c", "type": "exact_model_solution", "text": "exact abs_error tolerance model solution"},
        "evidence": {},
        "source": {"id": "s", "kind": "corpus", "path": json_rel},
    }
    recs = capas._source_records(p)
    assert recs[0]["retrieval_status"] == "corpus_matched"
    assert "abs_error" in recs[0]["text"]
    # the corpus path flows all the way through extraction
    ex = capas.extract_evidence(p)
    assert ex["extraction_status"] == "complete"
    assert ex["extracted_evidence"]["abs_error"] == 0.0


def test_read_corpus_jsonl_and_dir_and_nomatch(tmp_corpus) -> None:
    jsonl_rel = tmp_corpus("docs.jsonl", json.dumps({"text": "abs_error = 0.0"}) + "\n" + json.dumps({"text": "tolerance = 1e-3"}) + "\n")
    p = {"claim": {"type": "exact_model_solution", "text": "abs_error tolerance model"}}
    text, note = capas._read_corpus_source_path(jsonl_rel, p)
    assert text and note is None

    # directory aggregation (the .jsonl above lives in the same dir)
    dir_rel = jsonl_rel.rsplit("/", 1)[0]
    dir_text, dir_note = capas._read_corpus_source_path(dir_rel, p)
    assert dir_text and dir_note is None

    # a query with no matching terms yields the explicit no-match note
    no_rel = tmp_corpus("none.jsonl", json.dumps({"text": "completely unrelated content"}) + "\n")
    _, nomatch_note = capas._read_corpus_source_path(no_rel, {"claim": {"type": "exact_model_solution", "text": "abs_error tolerance"}})
    assert nomatch_note == "corpus source had no deterministic matches for claim terms or required fields"

    # a missing corpus file yields a not-found note
    _, missing_note = capas._read_corpus_source_path("definitely_missing_research.json", p)
    assert missing_note == "corpus source not found: definitely_missing_research.json"


def test_corpus_query_terms_include_required_and_text_tokens() -> None:
    p = {"claim": {"type": "exact_model_solution", "text": "reproduce the harmonic oscillator energy"}}
    terms = capas._corpus_query_terms(p)
    # required decision fields for the type are seeded
    assert "abs_error" in terms or "tolerance" in terms
    # long alphabetic tokens (>=5 chars) from the text are seeded
    assert "harmonic" in terms


# --------------------------------------------------------------------------------------
# path guard: sources must stay inside the repo (security invariant of the ingest layer)
# --------------------------------------------------------------------------------------
def test_source_path_guard_blocks_escape() -> None:
    for fn in (capas._read_source_path, lambda v: capas._read_pdf_source_path(v)):
        try:
            fn("../../../etc/passwd")
        except ValueError as exc:
            assert "inside the CAPAS repository" in str(exc)
        else:  # pragma: no cover - guard must raise
            raise AssertionError("path-escape guard did not fire")


def test_corpus_path_guard_blocks_escape() -> None:
    try:
        capas._read_corpus_source_path("../../../etc/passwd", {"claim": {"type": "exact_model_solution"}})
    except ValueError as exc:
        assert "inside the CAPAS repository" in str(exc)
    else:  # pragma: no cover - guard must raise
        raise AssertionError("corpus path-escape guard did not fire")


# --------------------------------------------------------------------------------------
# Provenance verification machinery (drives each helper to True AND False with real
# hashes computed against shipped repo fixtures — no network, no faked coverage).
# --------------------------------------------------------------------------------------
def _sha_file_rel(rel: str) -> str:
    return _hashlib.sha256((capas.ROOT / rel).read_bytes()).hexdigest()


def test_verify_review_hash_true_and_false() -> None:
    packet = {"reviewer": "demo", "decision": "approved", "notes": "ok"}
    good = {"review_packet": packet, "review_sha256": capas._stable_json_hash(packet)}
    assert capas._verify_review_hash(good) is True
    assert capas._verify_review_hash({"review_packet": packet, "review_sha256": "deadbeef"}) is False
    assert capas._verify_review_hash({}) is False


def test_verify_sources_and_source_url_verified(tmp_corpus) -> None:
    rel = tmp_corpus("prov_src.txt", "source-backed evidence body\n")
    src_hash = _sha_file_rel(rel)
    good = {"source_urls": [rel], "source_hashes": {rel: src_hash}}
    assert capas._verify_sources(good) is True
    assert capas._verify_sources({"source_urls": [rel], "source_hashes": {rel: "00"}}) is False
    assert capas._verify_sources({}) is False
    assert capas._source_url_verified(rel, src_hash) is True
    assert capas._source_url_verified(rel, "nope") is False
    assert capas._source_url_verified(rel, None) is False


def test_verify_witness_registry_true_and_false() -> None:
    reg_rel = str(capas.WITNESS_REGISTRY_PATH.relative_to(capas.ROOT))
    registry = json.loads(capas.WITNESS_REGISTRY_PATH.read_text(encoding="utf-8"))
    witness_id = next(iter(registry["witnesses"]))
    good = {
        "witness_id": witness_id,
        "witness_registry_path": reg_rel,
        "witness_registry_sha256": _sha_file_rel(reg_rel),
    }
    assert capas._verify_witness_registry(good) is True
    assert capas._verify_witness_registry(
        {"witness_id": "no-such-witness", "witness_registry_path": reg_rel}) is False
    assert capas._verify_witness_registry(
        {"witness_id": witness_id, "witness_registry_path": reg_rel, "witness_registry_sha256": "00"}) is False
    assert capas._verify_witness_registry({}) is False


def test_verify_reviewer_attestation_true_and_false() -> None:
    reg_rel = str(capas.REVIEWER_REGISTRY_PATH.relative_to(capas.ROOT))
    registry = json.loads(capas.REVIEWER_REGISTRY_PATH.read_text(encoding="utf-8"))
    reviewer_id = next(iter(registry["reviewers"]))
    attestation = "I attest this claim boundary was reviewed."
    att_hash = _hashlib.sha256(attestation.encode("utf-8")).hexdigest()
    good = {
        "reviewer": {"reviewer_id": reviewer_id, "attestation": attestation, "attestation_sha256": att_hash},
        "reviewer_registry_path": reg_rel,
        "reviewer_registry_sha256": _sha_file_rel(reg_rel),
    }
    assert capas._verify_reviewer_attestation(good) is True
    bad = json.loads(json.dumps(good))
    bad["reviewer"]["attestation_sha256"] = "00"
    assert capas._verify_reviewer_attestation(bad) is False
    unknown = json.loads(json.dumps(good))
    unknown["reviewer"]["reviewer_id"] = "stranger"
    assert capas._verify_reviewer_attestation(unknown) is False
    assert capas._verify_reviewer_attestation({}) is False


def test_verify_ro_crate_true_and_false() -> None:
    crate_rel = "benchmarks/ro_crates/trace_024/ro-crate-metadata.json"
    good = {"ro_crate_path": crate_rel, "ro_crate_sha256": _sha_file_rel(crate_rel)}
    assert capas._verify_ro_crate(good) is True
    assert capas._verify_ro_crate({"ro_crate_path": crate_rel, "ro_crate_sha256": "00"}) is False
    assert capas._verify_ro_crate({}) is False


def test_provenance_verification_report_shape() -> None:
    empty = capas.provenance_verification_report({"training_evidence": {"provenance": {}}})
    assert empty["provenance_ready"] is False
    assert set(empty["checks"]) == {
        "review_hash_verified", "source_urls_recoverable_hashable", "witness_registry_resolved",
        "ro_crate_validated", "reviewer_attestation_verified",
    }
    assert capas.provenance_verification_report({})["provenance_ready"] is False


def test_evaluate_fine_tune_readiness_blockers() -> None:
    res = capas.evaluate_fine_tune_readiness(
        {"claim": {"type": "exact_model_solution"}, "evidence": {}},
        verdict="ACCEPT", missing_fields=[], schema_errors=[])
    assert res["fine_tune_ready"] is False
    assert res["fine_tune_blockers"]
    assert res["fine_tune_criteria"]["verdict_accept"] is True
    rej = capas.evaluate_fine_tune_readiness(
        {"claim": {"type": "exact_model_solution"}, "evidence": {}},
        verdict="REJECT", missing_fields=["x"], schema_errors=[])
    assert rej["fine_tune_criteria"]["verdict_accept"] is False
    assert rej["fine_tune_criteria"]["schema_clean"] is False
    assert any("not ACCEPT" in b for b in rej["fine_tune_blockers"])


# --------------------------------------------------------------------------------------
# Demo-report builders over the shipped fixtures + exception_queue_entry.
# --------------------------------------------------------------------------------------
def test_build_demo_report_and_render_markdown() -> None:
    report = capas.build_demo_report()
    assert report["demo_verdict"] == "PASS"
    assert report["product_name"] == "CAPAS Claim Gate"
    assert set(report["claim_verdict_counts"]).issubset(LEGAL_VERDICTS)
    assert report["claim_examples"]
    md = capas._render_markdown(report)
    assert md.startswith("# CAPAS Product Demo Report")
    assert "Claim Gate Summary" in md
    assert "Decision Examples" in md


def test_trace_summary_and_claim_check_helpers() -> None:
    summary = capas._trace_summary("trace_039")
    assert summary["trace_id"] == "trace_039"
    for key in ("physical_evidence_level", "anchor_mode", "claim_scope"):
        assert key in summary

    report = capas._load_json(capas.CLAIM_REPORT)
    checks = capas._claim_checks(report)
    assert isinstance(checks, list) and checks
    first = checks[0]
    assert capas._find_check(checks, first["trace_id"], first["claim_id"]) is first
    try:
        capas._find_check(checks, "no_trace", "no_claim")
    except ValueError as exc:
        assert "missing claim check" in str(exc)
    else:  # pragma: no cover - must raise
        raise AssertionError("_find_check did not raise on missing check")


def test_exception_queue_entry_from_real_result() -> None:
    payload = {
        "schema_version": SCHEMA,
        "claim": {"id": "q1", "type": "statistical_confidence", "text": "significant effect"},
        "evidence": {"p_value": 0.40, "alpha": 0.05, "effect_direction_confirmed": True},
    }
    result = capas.decide_external_claim(payload)
    assert result["verdict"] in LEGAL_VERDICTS
    entry = capas.exception_queue_entry(0, result)
    assert entry is not None
    assert entry["index"] == 0
    assert entry["claim_id"] == "q1"
    assert entry["verdict"] == result["verdict"]
    assert "next_action" in entry
    assert capas.exception_queue_entry(1, {"verdict": "ACCEPT"}) is None


# --------------------------------------------------------------------------------------
# Additional align_claim_text overclaim branches (claim_transition / causal /
# systematic_review / evidence_conflict) — each driven to a real MISALIGNED/WARN.
# --------------------------------------------------------------------------------------
def test_align_claim_transition_overclaim_is_misaligned() -> None:
    r = capas.align_claim_text({
        "schema_version": SCHEMA,
        "claim": {"id": "c", "type": "claim_transition",
                  "text": "this upgrade proves the stronger claim is certified"},
        "evidence": {"upgrade_evidence_present": False},
    })
    assert r["alignment_status"] == "MISALIGNED"
    assert any("proof/certification" in i for i in r["issues"])


def test_align_causal_without_intervention_is_misaligned() -> None:
    r = capas.align_claim_text({
        "schema_version": SCHEMA,
        "claim": {"id": "c", "type": "causal_mechanism_claim",
                  "text": "the intervention has a causal mechanism effect"},
        "evidence": {"intervention_or_natural_experiment": False, "temporal_order_established": True,
                     "confounders_controlled": False, "mechanism_evidence_present": True},
    })
    assert r["alignment_status"] == "MISALIGNED"
    assert any("causal wording" in i for i in r["issues"])


def test_align_systematic_review_requires_registered_protocol() -> None:
    r = capas.align_claim_text({
        "schema_version": SCHEMA,
        "claim": {"id": "c", "type": "systematic_review_claim",
                  "text": "a systematic review with inclusion and bias protocol"},
        "evidence": {"protocol_registered": False, "inclusion_criteria_declared": True,
                     "risk_of_bias_assessed": True, "effect_consistency": True},
    })
    assert r["alignment_status"] == "MISALIGNED"
    assert any("registered protocol" in i for i in r["issues"])


def test_align_evidence_conflict_warns_without_contradicting_sources() -> None:
    r = capas.align_claim_text({
        "schema_version": SCHEMA,
        "claim": {"id": "c", "type": "evidence_conflict_claim",
                  "text": "the evidence conflict is resolved"},
        "evidence": {"supporting_sources": ["a"], "contradicting_sources": [],
                     "conflict_resolution_method": "meta_analysis", "resolution_pre_registered": True},
    })
    # empty contradicting_sources triggers the WARN branch (structurally usable).
    assert r["alignment_status"] in {"WARN", "ALIGNED"}
    assert any("contradicting_sources" in w for w in r.get("warnings", []))


# --------------------------------------------------------------------------------------
# UI renderer + CSP hashing: _render_ui emits the gate's HTML for each verdict sample.
# This is the function the gate uses to render its decision surface; calling it with a
# valid sample returns a complete CSP-hardened HTML document.
# --------------------------------------------------------------------------------------
def test_render_ui_emits_csp_hardened_html_for_each_sample() -> None:
    for name, sample in capas._ui_samples().items():
        html = capas._render_ui(sample)
        assert isinstance(html, str) and len(html) > 1000, name
        lowered = html.lower()
        assert "<html" in lowered or "<!doctype" in lowered, name
        assert "Content-Security-Policy" in html, name


def test_csp_sha256_and_inline_hashing() -> None:
    h = capas._csp_sha256("alert(1)")
    assert h.startswith("'sha256-") and h.endswith("'")
    html = (
        '<meta http-equiv="Content-Security-Policy" content="default-src \'self\'">'
        "<style>.a{color:red}</style>"
        '<button onclick="go()" style="color:blue">x</button>'
        "<script>go()</script>"
    )
    out = capas._apply_inline_csp_hashes(html)
    # the placeholder CSP is rewritten to include computed script/style hashes.
    assert "script-src" in out and "style-src" in out
    assert "'sha256-" in out
    assert "unsafe-hashes" in out


# --------------------------------------------------------------------------------------
# pytest fixture (also works under the __main__ runner below)
# --------------------------------------------------------------------------------------
def _make_tmp_corpus_factory(created_dirs: list):
    base = capas.ROOT / "_research_test_corpus_tmp"
    base.mkdir(exist_ok=True)
    created_dirs.append(base)

    def factory(name: str, content: str) -> str:
        path = base / name
        path.write_text(content, encoding="utf-8")
        return str(path.relative_to(capas.ROOT))

    return factory


try:  # pragma: no cover - only when pytest is present
    import pytest

    @pytest.fixture
    def tmp_corpus():
        created: list = []
        factory = _make_tmp_corpus_factory(created)
        yield factory
        for d in created:
            shutil.rmtree(d, ignore_errors=True)
except ImportError:  # pragma: no cover - plain-runner path
    pytest = None  # type: ignore


def _run_all() -> int:
    created: list = []
    factory = _make_tmp_corpus_factory(created)
    failures = 0
    try:
        for name, fn in sorted(globals().items()):
            if not (name.startswith("test_") and callable(fn)):
                continue
            try:
                if "tmp_corpus" in getattr(fn, "__code__").co_varnames[: fn.__code__.co_argcount]:
                    fn(factory)
                else:
                    fn()
            except Exception as exc:  # noqa: BLE001 - report and continue
                failures += 1
                print(f"FAIL {name}: {exc}")
            else:
                print(f"ok   {name}")
    finally:
        for d in created:
            shutil.rmtree(d, ignore_errors=True)
    print(f"\n{'PASS' if failures == 0 else 'FAIL'}: {failures} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(_run_all())
