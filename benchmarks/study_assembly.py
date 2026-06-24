# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""CAPAS — cross-domain study: tamper-evident assembly + SCOPED→BACKED flip contract.

This is the ASSEMBLE/ROOT layer for the blind-adjudicated n=500 confusion-matrix study
pre-registered in docs/PREREGISTRATION_CROSS_DOMAIN_ADJUDICATION.md (§9 replay, §10
tamper-evidence, §11 reuse) and specified in docs/CROSS_DOMAIN_STUDY_PROTOCOL.md +
docs/CROSS_DOMAIN_STUDY_ANALYSIS_PLAN.md. It does ONE thing: it binds four streams of
records — the frozen corpus, every CAPAS verdict, every human adjudication, and the H2
plausibility baseline — into the SAME append-only, hash-chained, Merkle-rooted registry
already shipped in capas_registry.py, so their ordering cannot be rewritten after the fact
and any single record is independently re-derivable.

Design invariants (all inherited from the existing engine, NOT re-implemented here):

  * Tamper-evidence is capas_registry.append / merkle_root / verify_chain. We do not fork
    the chain logic; we feed it canonical "certificate" bodies and let it chain them. A
    reorder / insertion / deletion of ANY record breaks verify_chain at the offending seq.

  * Body integrity + authorship of a CAPAS verdict is the existing Ed25519 receipt produced
    by capas_verify._receipt(): a canonical body, a receipt_id = "sha256:" +
    sha256(canonical)[:32], an engine_digest = sha256(capas_verify.py source), and an
    optional Ed25519 signature. capas_verify.verify_receipt() re-checks the receipt_id and
    (if present) the signature; it returns a DICT, not a bool.

  * The verdict has NO language model in it (capas_verify receipt decision_path =
    "deterministic; no LLM"). That makes the replay guarantee total: re-running the engine
    on the frozen corpus reproduces every verdict and every receipt_id bit-for-bit, so a
    third party replays the whole study without trusting us.

  * The H2 plausibility-baseline arm MAY use an LLM-judge, but that judge's output is logged
    as a SEPARATE record kind (RECORD_BASELINE) and NEVER as a CAPAS verdict. This module
    enforces that split structurally.

THE BINDING THAT MAKES verify_entry ROUND-TRIP (important, and tested below):
  capas_registry.verify_entry(entry, certificate) recomputes _body_digest(certificate) and
  compares it to entry["body_digest"]. So the object passed to verify_entry MUST be the
  EXACT dict that was appended. For a CAPAS verdict we therefore append the receipt ITSELF
  as the chained certificate body (so verify_entry(entry, receipt).body_matches_log is True
  and verify_receipt(receipt) re-validates receipt_id + signature). Study-side metadata
  (record_kind, audit_hash, track) is carried in a SEPARATE sidecar index keyed by chain
  seq — NOT inside the chained body — so the round-trip is exact. Corpus / adjudication /
  baseline records have no signed receipt, so they ARE their own certificate bodies.

Determinism: this module supplies NO timestamps of its own (mirrors capas_registry — the
caller passes `at` if a wall-clock anchor is wanted; None = unstamped so the chain stays
reproducible). Persistence is the caller's: append the returned log to JSONL, write the
returned artifact to disk.

Run:  python3 benchmarks/study_assembly.py        # self-test of binding + replay + flip gate
      python3 benchmarks/study_assembly.py --replay   # replay-entrypoint usage note
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from typing import Any, Callable

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import capas_registry
import capas_verify

PREREGISTRATION_PATH = "docs/PREREGISTRATION_CROSS_DOMAIN_ADJUDICATION.md"
PROTOCOL_PATH = "docs/CROSS_DOMAIN_STUDY_PROTOCOL.md"
ANALYSIS_PLAN_PATH = "docs/CROSS_DOMAIN_STUDY_ANALYSIS_PLAN.md"
CLAIMS_REGISTRY_PATH = "docs/CLAIMS_REGISTRY.md"

# The four record kinds that share ONE chain. Their relative ordering is what the chain
# protects: a corpus item frozen (appended) BEFORE the verdict that decides it; a verdict
# before the adjudication that rules on it. Mixing them in one chain makes "we adjudicated
# this before we saw the verdict" a forgeable claim — verify_chain catches any post-hoc
# reordering across all streams at once.
RECORD_CORPUS = "corpus_item"            # a frozen, public-sourced claim payload (or the freeze manifest)
RECORD_VERDICT = "capas_verdict"         # a signed, LLM-free CAPAS receipt
RECORD_ADJUDICATION = "human_ruling"     # a Track-A verification or Track-B blind ruling
RECORD_BASELINE = "plausibility_baseline"  # H2 arm (may be LLM-judge); NEVER a verdict

_RECORD_KINDS = {RECORD_CORPUS, RECORD_VERDICT, RECORD_ADJUDICATION, RECORD_BASELINE}
_RECEIPT_SCHEMA = "capas-verification-receipt-v1"


def _canonical(obj: Any) -> str:
    """Same canonicalization the registry and receipt use: sorted keys, no whitespace."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def _sha(s: str) -> str:
    return "sha256:" + hashlib.sha256(s.encode()).hexdigest()


# ─────────────────────────────────────────────────────────────────────────────
# 1. Record builders. Each returns (certificate_body, sidecar_meta). The certificate
#    body is what gets chained by capas_registry.append; the sidecar meta carries study
#    metadata OUT of the chained body so verify_entry round-trips exactly.
# ─────────────────────────────────────────────────────────────────────────────
def assemble_corpus_record(item: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """Freeze ONE corpus claim (or the corpus freeze manifest) into a registry-appendable
    certificate body. Content-addressed: corpus_digest = sha256(canonical(item)). Appending
    all corpus items BEFORE any verdict is what makes 'frozen before collection' a
    chain-provable fact. The certificate body IS the record (no signed receipt), so it
    passes through verify_entry against itself."""
    cid = item.get("id") or item.get("claim_id")
    if not cid:
        raise ValueError("corpus item needs a stable 'id' (frozen public-artifact key)")
    corpus_digest = _sha(_canonical(item))
    cert = {
        "claim_id": cid,
        "verdict": "FROZEN",                     # corpus items are not decided, they are frozen
        "scope": "CORPUS",
        "engine_digest": None,                   # no engine decided a corpus item
        "certificate_id": corpus_digest,         # content-addressed
        "source": item.get("source"),            # public artifact provenance (no synthetic)
        "domain": item.get("domain"),            # one of the 10 stratification domains
        "track": item.get("track"),              # "A" computable / "B" blind-human (pre-assigned)
        "corpus_digest": corpus_digest,
        "signature": None,
    }
    meta = {"record_kind": RECORD_CORPUS, "domain": item.get("domain"), "track": item.get("track")}
    return cert, meta


def assemble_verdict_record(receipt: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """Bind ONE CAPAS verdict. The chained certificate body IS the capas_verify receipt
    AS PRODUCED — unmodified — so capas_registry.verify_entry(entry, receipt) re-derives
    its body digest exactly and capas_verify.verify_receipt(receipt) re-validates its
    receipt_id + Ed25519 signature. The receipt's receipt_id IS the verdict's audit_hash;
    we surface it in the SIDECAR (not in the body) so the chained body stays bit-identical
    to what capas_verify emitted."""
    if not isinstance(receipt, dict) or receipt.get("schema") != _RECEIPT_SCHEMA:
        raise ValueError(f"expected a capas_verify receipt (schema {_RECEIPT_SCHEMA})")
    # Structural guarantee: the verdict stream is LLM-free.
    if receipt.get("decision_path") != "deterministic; no LLM":
        raise ValueError("verdict stream must be LLM-free (decision_path != 'deterministic; no LLM')")
    meta = {
        "record_kind": RECORD_VERDICT,
        "audit_hash": receipt.get("receipt_id"),         # re-derivable via verify_receipt
        "engine_digest": receipt.get("engine_digest"),   # pins capas_verify.py source digest
        "evidence_artifact_hash": receipt.get("evidence_artifact_hash"),
    }
    # The receipt is the certificate body, untouched.
    return receipt, meta


def assemble_adjudication_record(ruling: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """Bind ONE human ruling. Two tracks, recorded SEPARATELY (never averaged):
      Track A — verification of computable truth (a deterministic re-derivation a human ran).
      Track B — blind external human adjudication (adjudicator id + label; κ computed later).
    Bound to the verdict it rules on by `decides_claim_id`. Because the verdict was appended
    earlier in the SAME chain, 'ruled blind, before the verdict was revealed' is a checkable
    ordering fact, not a courtesy. The certificate body IS the record (no signed receipt)."""
    track = ruling.get("track")
    if track not in ("A", "B"):
        raise ValueError("adjudication needs track 'A' (computable) or 'B' (blind human)")
    cid = ruling.get("claim_id")
    cert = {
        "claim_id": cid,
        "verdict": ruling.get("ruling"),          # ADMISSIBLE / REWRITE_ONLY / INADMISSIBLE
        "scope": f"TRACK_{track}",
        "engine_digest": None,
        "certificate_id": _sha(_canonical(
            {k: v for k, v in ruling.items() if k != "signature"})),
        "decides_claim_id": ruling.get("decides_claim_id", cid),
        "blind": bool(ruling.get("blind", track == "B")),
        "signature": ruling.get("signature"),     # optional adjudicator attestation
    }
    if track == "A":
        cert["computable_check"] = ruling.get("computable_check")   # which deterministic check
        cert["re_derived_value"] = ruling.get("re_derived_value")
    else:
        cert["adjudicator_id"] = ruling.get("adjudicator_id")       # for κ across the panel
        cert["label"] = ruling.get("ruling")
    meta = {"record_kind": RECORD_ADJUDICATION, "track": track,
            "adjudicator_id": ruling.get("adjudicator_id")}
    return cert, meta


def assemble_baseline_record(measure: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """Bind ONE H2 plausibility-baseline measurement (e.g. an LLM-judge accept/reject).
    Recorded as its OWN kind so it is auditable but can NEVER be mistaken for, or mixed into,
    the CAPAS verdict stream. This is the structural guarantee that H2 is 'CAPAS (LLM-free)
    vs a baseline that may use an LLM', not a leak."""
    cert = {
        "claim_id": measure.get("claim_id"),
        "verdict": measure.get("label"),          # baseline's accept/reject (NOT a CAPAS verdict)
        "scope": "BASELINE",
        "engine_digest": None,
        "certificate_id": _sha(_canonical(measure)),
        "baseline_system": measure.get("system"), # e.g. "frontier-llm-judge@<pinned-id>"
        "plausibility": measure.get("plausibility"),
        "plausibility_sd": measure.get("plausibility_sd"),
        "signature": None,
    }
    meta = {"record_kind": RECORD_BASELINE, "baseline_system": measure.get("system")}
    return cert, meta


# ─────────────────────────────────────────────────────────────────────────────
# 2. Append with a sidecar index. capas_registry.append chains the certificate body;
#    we keep a parallel sidecar list (one entry per seq) carrying study metadata so the
#    chained bodies stay bit-identical to what their producers emitted.
# ─────────────────────────────────────────────────────────────────────────────
def append_record(log: list[dict[str, Any]], sidecar: list[dict[str, Any]],
                  built: tuple[dict[str, Any], dict[str, Any]],
                  at: str | None = None) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Append ANY of the four built records (cert_body, meta) to the shared chain via the
    existing capas_registry.append(). One chain, one Merkle tree, one ordering proof.
    Returns NEW (log, sidecar) — neither input is mutated."""
    cert, meta = built
    if meta.get("record_kind") not in _RECORD_KINDS:
        raise ValueError(f"unknown record_kind {meta.get('record_kind')!r}")
    new_log = capas_registry.append(log, cert, at=at)
    new_sidecar = sidecar + [{"seq": len(log), **meta}]
    return new_log, new_sidecar


# ─────────────────────────────────────────────────────────────────────────────
# 3. Published artifact — carries the Merkle root. One file a reviewer can pin.
# ─────────────────────────────────────────────────────────────────────────────
def build_study_artifact(log: list[dict[str, Any]], sidecar: list[dict[str, Any]],
                         analysis: dict[str, Any], preregistration_digest: str) -> dict[str, Any]:
    """Assemble the single published artifact for the study. It carries:
      * merkle_root  — the registry fingerprint (any altered/added/removed record changes
                       it: capas_registry.merkle_root);
      * chain_head + verify_chain result — append-only integrity, re-derivable with NO
                       original bodies (capas_registry.verify_chain);
      * record_counts — per record_kind (from the sidecar, which is the authoritative kind map);
      * analysis      — the pre-locked single-shot analysis (H1 / H2 / H3), computed ONCE by
                       the analysis-plan unit and recorded here (this module binds it to the
                       chain so numbers and source records cannot drift apart);
      * preregistration_digest — pins which protocol this artifact answers (§9/§11).

    This module does NOT compute the statistics; it binds them to the tamper-evident chain.
    The artifact itself is then content-addressed (artifact_id)."""
    chain = capas_registry.verify_chain(log)
    counts: dict[str, int] = {k: 0 for k in _RECORD_KINDS}
    for m in sidecar:
        k = m.get("record_kind")
        if k in counts:
            counts[k] += 1
    body = {
        "schema": "capas-study-artifact-v1",
        "study": "cross-domain blind-adjudicated admissibility (n=500)",
        "preregistration": PREREGISTRATION_PATH,
        "protocol": PROTOCOL_PATH,
        "analysis_plan": ANALYSIS_PLAN_PATH,
        "preregistration_digest": preregistration_digest,
        "merkle_root": capas_registry.merkle_root(log),
        "chain_intact": chain.get("intact"),
        "chain_head": chain.get("head"),
        "entries": chain.get("entries"),
        "record_counts": counts,
        "engine_digest": capas_verify._engine_digest(),  # which engine replays the verdicts
        "analysis": analysis,                            # H1 / H2 / H3, computed once
        "replay": {
            "guarantee": "deterministic; no LLM in any verdict. Re-running capas_verify on the "
                         "frozen corpus reproduces every verdict and every audit_hash "
                         "(receipt_id) bit-for-bit. See replay_study().",
            "engine_digest": capas_verify._engine_digest(),
        },
        "verify": {
            "chain": "capas_registry.verify_chain(log) — re-derives the hash chain; catches any "
                     "reorder/insertion/deletion across corpus+verdict+adjudication+baseline.",
            "entry": "capas_registry.verify_entry(entry, receipt) — re-present a verdict; its body "
                     "digest must re-derive (body_matches_log). The receipt_id + Ed25519 signature "
                     "are validated separately by capas_verify.verify_receipt(receipt), which "
                     "returns a dict {receipt_id_matches, signature_valid, ...}.",
        },
    }
    body["artifact_id"] = _sha(_canonical(body))
    return body


# ─────────────────────────────────────────────────────────────────────────────
# 4. Replay guarantee — the heart of "a third party can replay the whole study".
# ─────────────────────────────────────────────────────────────────────────────
def replay_study(corpus: list[dict[str, Any]],
                 logged_verdicts: list[dict[str, Any]],
                 logged_meta: list[dict[str, Any]],
                 engine: Callable[[dict[str, Any]], dict[str, Any]] | None = None
                 ) -> dict[str, Any]:
    """Re-run the deterministic engine on the frozen corpus and prove every logged verdict +
    audit_hash reproduces EXACTLY.

    `corpus`          : the frozen payloads (claim+evidence), in the SAME order logged.
    `logged_verdicts` : the verdict receipts (chained certificate bodies) as stored.
    `logged_meta`     : the sidecar meta for each verdict (carries audit_hash, engine_digest).
    `engine`          : the verdict function. Default = capas_verify.verify_external_claim if
                        present, else capas_verify.verify. (No LLM in either.)

    A reproduced receipt_id that differs from the logged audit_hash means EITHER the corpus
    was altered OR a different engine ran — both study-invalidating, both caught here without
    trusting the original run."""
    if engine is None:
        engine = getattr(capas_verify, "verify_external_claim", None) \
            or getattr(capas_verify, "verify", None)
    if engine is None:
        return {"replayed": False, "reason": "no deterministic engine entrypoint found"}
    if not (len(corpus) == len(logged_verdicts) == len(logged_meta)):
        return {"replayed": False, "reason": "corpus / verdict / meta count mismatch (frozen set changed)"}

    mismatches: list[dict[str, Any]] = []
    engine_digest_now = capas_verify._engine_digest()
    for i, (payload, logged, meta) in enumerate(zip(corpus, logged_verdicts, logged_meta)):
        fresh = engine(payload)
        if isinstance(fresh, dict) and fresh.get("schema") == _RECEIPT_SCHEMA:
            fresh_receipt = fresh
        elif isinstance(fresh, dict) and isinstance(fresh.get("receipt"), dict):
            fresh_receipt = fresh["receipt"]
        else:
            fresh_receipt = None
        if not isinstance(fresh_receipt, dict):
            mismatches.append({"i": i, "reason": "engine returned no receipt"})
            continue
        if fresh_receipt.get("receipt_id") != meta.get("audit_hash"):
            mismatches.append({
                "i": i, "claim_id": logged.get("claim_id"),
                "logged_audit_hash": meta.get("audit_hash"),
                "replayed_audit_hash": fresh_receipt.get("receipt_id"),
                "reason": "audit_hash mismatch (corpus altered or engine changed)"})
        if fresh_receipt.get("verified_verdict") != logged.get("verified_verdict"):
            mismatches.append({
                "i": i, "claim_id": logged.get("claim_id"),
                "logged_verdict": logged.get("verified_verdict"),
                "replayed_verdict": fresh_receipt.get("verified_verdict"),
                "reason": "verdict mismatch"})
        if meta.get("engine_digest") and meta["engine_digest"] != engine_digest_now:
            mismatches.append({
                "i": i, "logged_engine_digest": meta.get("engine_digest"),
                "engine_digest_now": engine_digest_now,
                "reason": "engine_digest drift (capas_verify.py source differs from the run)"})
    return {
        "replayed": not mismatches,
        "n": len(corpus),
        "engine_digest": engine_digest_now,
        "mismatches": mismatches[:50],
        "mismatch_count": len(mismatches),
        "note": "deterministic; no LLM. Exact reproduction of audit_hash + verdict over the frozen "
                "corpus is the citation-grade replay guarantee (prereg §9).",
    }


# ─────────────────────────────────────────────────────────────────────────────
# 5. SCOPED→BACKED flip contract — the precondition gate. We ENCODE which rows flip and
#    the wording standard; we do NOT flip them. CLAIMS_REGISTRY.md is curated — only the
#    COMPLETED study (run + replayed by a third party) earns the edit, a separate
#    human-reviewed act. This function reports whether the completion preconditions hold; if
#    they do, it emits the exact replacement-wording standard. It returns text; writes nothing.
# ─────────────────────────────────────────────────────────────────────────────
_FLIP_ROWS = {
    "row21_false_accept_rate": {
        "claim": "Empirical false-accept / false-reject RATE on real claims",
        "from_status": "SCOPED", "to_status": "BACKED", "hypothesis": "H1",
        "requires": ("h1_pooled_false_accept_ci", "h1_per_domain"),
        "rederive": "python3 benchmarks/study_assembly.py --replay (reproduces every verdict + "
                    "audit_hash on the frozen corpus) → pooled + per-domain false-accept CI in the artifact",
        "wording_standard":
            "Value + 95% Clopper-Pearson CI from the locked single-shot analysis, the Merkle root of the "
            "study registry, and the replay command. State the adjudication track split (A computable-truth "
            "vs B blind-human, κ) and keep the GIGO-ceiling caveat — the rate is against adjudicated "
            "structural admissibility, NOT ultimate truth.",
    },
    "row22_retrospective_28": {
        "claim": "Separated 28 retracted-vs-replicated claims by structure",
        "from_status": "SCOPED", "to_status": "BACKED", "hypothesis": "H1",
        "requires": ("h1_pooled_false_accept_ci",),
        "rederive": "python3 benchmarks/study_assembly.py --replay → blind-coded n=500 confusion matrix "
                    "supersedes the n=28 agent-coded retrospective; receipts in registry",
        "wording_standard":
            "Replace 'agent-coded, publicly-known retrospective (n=28)' with the blind-coded n=500 result + "
            "Merkle root. The n=28 stays cited as the pilot that motivated the study; the BACKED number is the "
            "blind-adjudicated corpus, not the retrospective.",
    },
    "row23_vs_llm_judge": {
        "claim": "At par with a frontier LLM-judge on accuracy; ahead on determinism",
        "from_status": "SCOPED", "to_status": "BACKED", "hypothesis": "H2",
        "requires": ("h2_auc", "h2_balanced_accuracy", "h2_separation_above_baseline"),
        "rederive": "python3 benchmarks/head_to_head_sota.py on the locked n=500 corpus + the live "
                    "plausibility-baseline arm logged as RECORD_BASELINE",
        "wording_standard":
            "Replace the 10-claim modeled corpus with the n=500 result: AUC / balanced accuracy for CAPAS vs "
            "the pinned LLM-judge baseline, and whether H2 (separation strictly above baseline) was SUPPORTED. "
            "If H2 is not supported, the row is corrected to that finding — BACKED means 'measured & reported', "
            "not 'measured & favorable'. Determinism advantage is already CLOSED elsewhere.",
    },
}


def evaluate_flip_preconditions(study_artifact: dict[str, Any],
                                replay_result: dict[str, Any]) -> dict[str, Any]:
    """Decide, mechanically, whether the completed study earns each SCOPED→BACKED flip. Returns
    one entry per row with eligible:bool and the exact replacement-wording standard. NEVER edits
    CLAIMS_REGISTRY.md — a maintainer applies the flip by hand after this gate (and only this
    gate) passes. Fail-closed: any missing precondition, broken chain, or failed replay leaves
    the row SCOPED."""
    chain_ok = bool(study_artifact.get("chain_intact"))
    replay_ok = bool(replay_result.get("replayed"))
    analysis = study_artifact.get("analysis", {}) or {}

    # Global §8 preconditions: adjudicator agreement κ ≥ 0.6 (H3) and a complete audit trail.
    kappa = analysis.get("h3_inter_adjudicator_kappa")
    kappa_ok = isinstance(kappa, (int, float)) and kappa >= 0.6
    audit_trail_complete = chain_ok and (study_artifact.get("entries") or 0) > 0

    rows: dict[str, Any] = {}
    for key, spec in _FLIP_ROWS.items():
        have = all(analysis.get(r) is not None for r in spec["requires"])
        eligible = bool(chain_ok and replay_ok and kappa_ok and audit_trail_complete and have)
        rows[key] = {
            "claim": spec["claim"],
            "flip": f'{spec["from_status"]} → {spec["to_status"]}',
            "hypothesis": spec["hypothesis"],
            "eligible": eligible,
            "blocked_by": [] if eligible else [
                *([] if chain_ok else ["chain not intact (verify_chain failed)"]),
                *([] if replay_ok else ["replay failed (audit_hash/verdict not reproduced)"]),
                *([] if kappa_ok else ["H3 κ < 0.6 (adjudicator agreement below floor)"]),
                *([] if audit_trail_complete else ["incomplete audit trail"]),
                *([f"missing analysis field: {r}" for r in spec["requires"] if analysis.get(r) is None]),
            ],
            "rederive": spec["rederive"],
            "wording_standard": spec["wording_standard"],
            "merkle_root": study_artifact.get("merkle_root"),
        }
    return {
        "claims_registry": CLAIMS_REGISTRY_PATH,
        "global_preconditions": {
            "chain_intact": chain_ok, "replay_clean": replay_ok,
            "h3_kappa_ge_0.6": kappa_ok, "audit_trail_complete": audit_trail_complete,
        },
        "rows": rows,
        "note": "This gate REPORTS eligibility and emits the wording standard. It does NOT edit "
                "docs/CLAIMS_REGISTRY.md — the curated registry is flipped by a maintainer, by hand, only "
                "after this fail-closed gate passes on a study replayed by an independent party. SCOPED "
                "stands until then.",
    }


# ─────────────────────────────────────────────────────────────────────────────
# Self-test: builds a tiny 4-stream chain, proves tamper-evidence, proves verify_entry
# round-trips on the receipt, proves the flip gate is fail-closed on an incomplete study.
# Runs offline, deterministic, no network.
# ─────────────────────────────────────────────────────────────────────────────
def _selftest() -> None:
    log: list[dict[str, Any]] = []
    sidecar: list[dict[str, Any]] = []

    # (a) freeze one public-sourced corpus item (no synthetic).
    corpus_item = {"id": "psy-001", "domain": "biology", "track": "B",
                   "source": "https://retractionwatch.com/<public-record>",
                   "claim": {"id": "psy-001", "type": "reproducibility_check"},
                   "evidence": {"independent_reproduction_pass": False}}
    log, sidecar = append_record(log, sidecar, assemble_corpus_record(corpus_item))

    # (b) a real capas_verify receipt (LLM-free) → appended as its own certificate body.
    receipt = capas_verify._receipt(
        payload={"claim": {"id": "psy-001", "type": "reproducibility_check"},
                 "evidence": {"independent_reproduction_pass": False}},
        base_verdict="HOLD", final="HOLD", scope="ATTEST", tier="FORM",
        checks=[{"check": "form", "status": "OK"}], rationale=["self-test"])
    vbuilt = assemble_verdict_record(receipt)
    log, sidecar = append_record(log, sidecar, vbuilt)

    # (c) Track-B blind ruling, bound to the verdict's claim.
    ruling = {"claim_id": "psy-001", "decides_claim_id": "psy-001", "track": "B",
              "adjudicator_id": "adj-7", "ruling": "INADMISSIBLE", "blind": True}
    log, sidecar = append_record(log, sidecar, assemble_adjudication_record(ruling))

    # (d) H2 baseline (may be an LLM-judge) — logged, but never a verdict.
    log, sidecar = append_record(log, sidecar, assemble_baseline_record(
        {"claim_id": "psy-001", "system": "frontier-llm-judge@pinned", "label": "ACCEPT",
         "plausibility": 0.81, "plausibility_sd": 0.03}))

    # chain must be intact.
    chain = capas_registry.verify_chain(log)
    assert chain["intact"], chain

    # the verdict entry must re-present authentically: verify_entry against the RECEIPT itself.
    vseq = next(m["seq"] for m in sidecar if m["record_kind"] == RECORD_VERDICT)
    ventry = log[vseq]
    ve = capas_registry.verify_entry(ventry, receipt)
    assert ve["body_matches_log"], ve  # body digest re-derives → entry is the logged verdict

    # the receipt_id (== audit_hash) + signature are validated SEPARATELY via verify_receipt,
    # which returns a DICT (not a bool); we read its fields, never assert it as a boolean.
    vr = capas_verify.verify_receipt(receipt)
    assert isinstance(vr, dict), vr
    assert vr.get("receipt_id_matches") is True, vr   # audit_hash re-derivable
    assert sidecar[vseq]["audit_hash"] == receipt["receipt_id"]

    # tamper: reorder two records → chain breaks (ordering cannot be rewritten post hoc).
    tampered = [log[1], log[0]] + log[2:]
    assert not capas_registry.verify_chain(tampered)["intact"]

    # the verdict stream is structurally LLM-free: a receipt without the deterministic path is rejected.
    bad = dict(receipt); bad["decision_path"] = "llm-judge"
    try:
        assemble_verdict_record(bad)
        raise AssertionError("expected LLM-tainted verdict to be rejected")
    except ValueError:
        pass

    # flip gate is FAIL-CLOSED on an incomplete study (no analysis, failed replay).
    artifact = build_study_artifact(log, sidecar, analysis={}, preregistration_digest="sha256:<prereg>")
    gate = evaluate_flip_preconditions(artifact, replay_result={"replayed": False})
    assert all(not r["eligible"] for r in gate["rows"].values()), "incomplete study must not flip rows"
    assert artifact["merkle_root"] == capas_registry.merkle_root(log)

    print("study_assembly self-test OK")
    print("  records:", len(log),
          "| counts:", artifact["record_counts"],
          "| merkle_root:", artifact["merkle_root"][:24], "…")
    print("  verdict round-trip body_matches_log:", ve["body_matches_log"],
          "| receipt_id_matches:", vr.get("receipt_id_matches"),
          "| signature_valid:", vr.get("signature_valid"))
    print("  flip rows gated SCOPED (fail-closed):",
          ", ".join(k for k, r in gate["rows"].items() if not r["eligible"]))


if __name__ == "__main__":
    if "--replay" in sys.argv:
        print("Replay entrypoint: load the frozen corpus + logged verdict receipts + sidecar meta "
              "(JSONL persisted by the caller), then call "
              "study_assembly.replay_study(corpus, logged_verdicts, logged_meta). Deterministic; no LLM. "
              "Exact reproduction of every audit_hash is the citation guarantee (prereg §9).")
    else:
        _selftest()
