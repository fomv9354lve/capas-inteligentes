# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""CAPAS SDK — a fail-closed verification layer you wrap around your LLM.

    pip install capas-claim-gate
    from capas_sdk import gate, reward, verified

CAPAS never lets an unsupported claim through as ACCEPT. It re-derives what is
re-derivable, grades the rest, and DEFERS what it cannot verify (HOLD) — so an LLM's
plausible-but-unsupported output cannot become a trusted decision. No language model is
ever in the verdict.

What it is — and is NOT (rigorous honesty, kept in the public surface):
  - It GATES structured claims fail-closed: 0 false-accepts on honestly-declared evidence.
  - It RE-DERIVES numbers from raw inputs: a reported value that does not recompute is REJECTed.
  - It GRADES the ungrounded-but-falsifiable remainder and emits a dense, gameable-resistant
    reward (the RLVR signal).
  - It does NOT detect fraud-by-lying. Extraction/grounding reaches record<->text, never
    text<->reality: a competent liar who declares correct methods and withholds raw data
    defeats any text-only check. That is the irreducible GIGO ceiling — only re-derivation
    on the actual raw data crosses it, when the data exists.

The boost is RELIABILITY, not capability. The model does not get smarter; its output becomes
admissible-or-deferred instead of plausible-or-wrong. LLM-alone false-accepts; LLM+CAPAS does
not (see examples/boost_your_llm.py).
"""
from __future__ import annotations

from typing import Any, Callable

import capas
import capas_admissibility
import capas_rcc

_SCHEMA = "capas-claim-payload-v3"


def _payload(claim_type: str, evidence: dict[str, Any], claim_text: str, claim_id: str) -> dict[str, Any]:
    # claim.text must be non-empty or schema validation fails -> everything HOLDs. Guard it.
    return {"schema_version": _SCHEMA,
            "claim": {"id": claim_id or "claim", "type": claim_type,
                      "text": claim_text or claim_id or claim_type or "claim"},
            "evidence": evidence or {}}


def gate(claim_type: str, evidence: dict[str, Any], claim_text: str = "", claim_id: str = "claim") -> dict[str, Any]:
    """The deterministic verdict for a structured claim: ACCEPT / REWRITE / REJECT / HOLD,
    with machine-readable reasons, missing fields, and the licensed rewrite. No LLM."""
    return capas.decide_external_claim(_payload(claim_type, evidence, claim_text, claim_id))


_REWARD_BY_VERDICT = {"ACCEPT": 1.0, "REWRITE": 0.5, "HOLD": 0.25, "REJECT": 0.0}


def reward(claim_type: str, evidence: dict[str, Any], claim_text: str = "", claim_id: str = "claim") -> float:
    """A dense verifiable reward in [0,1], ALIGNED WITH THE GATE — the RLVR signal your model
    cannot game by being plausible: ACCEPT (admissible) -> 1.0; REWRITE (fixable) -> 0.5;
    HOLD (unverifiable, deferred) -> 0.25; REJECT (refuted/unsupported) -> 0.0. (For the finer
    re-derivation-based continuous score, call capas_admissibility.reward directly — note it
    scores the re-derivable slice, a stricter and DIFFERENT signal than the contract gate.)"""
    verdict = gate(claim_type, evidence, claim_text, claim_id).get("verdict")
    return _REWARD_BY_VERDICT.get(verdict, 0.0)


def certificate(claim_type: str, evidence: dict[str, Any], claim_text: str = "", claim_id: str = "claim") -> dict[str, Any]:
    """A signed, re-derivable admissibility certificate (the audit artifact a regulated buyer
    purchases): stratifies the claim into grounded / generated / unknowable and names the
    boundary it cannot enter."""
    return capas_rcc.rcc(_payload(claim_type, evidence, claim_text, claim_id))


def verified(propose: Callable[[], dict[str, Any]], claim_type: str,
             claim_text: str = "", claim_id: str = "claim") -> dict[str, Any]:
    """Wrap an LLM. `propose()` returns the evidence dict your model claims supports the
    statement; CAPAS gates it. The model PROPOSES (imagination); CAPAS DISPOSES (the verdict).
    The proposal can never become the verdict — even a model that returns 'verdict: ACCEPT'
    is ignored; only the deterministic gate on the proposed evidence decides."""
    evidence = propose() or {}
    out = gate(claim_type, evidence, claim_text, claim_id)
    out["llm_proposed_evidence"] = evidence
    out["note"] = "LLM proposed the evidence; CAPAS gated it deterministically (the proposal is not the verdict)"
    return out


def gate_text(text: str, claim_type: str, extractor: Callable, claim_id: str = "claim") -> dict[str, Any]:
    """Raw text -> fail-closed gate via the intake membrane. The extractor (your LLM) proposes
    each evidence field grounded in a source span; CAPAS keeps only span-grounded fields, DEFERS
    disagreements to a human (never fabricates), and gates the result. Extraction uncertainty
    can never become a false ACCEPT. NOTE: this grounds text<->record, not text<->reality — a
    source that LIES about its methods will pass; that is the GIGO ceiling, not a CAPAS bug."""
    import capas_intake
    r = capas_intake.intake(claim_text=text, claim_type=claim_type, source_text=text, extractor=extractor)
    verdict = capas.decide_external_claim(r["payload"]).get("verdict")
    return {"verdict": verdict, "extracted": r["evidence_extracted"],
            "deferred": r["deferred_fields"], "extraction_residual": r["extraction_residual"],
            "fail_closed": r["fail_closed"]}


def gate_quantum(calibration_row: dict[str, Any]) -> dict[str, Any]:
    """Gate a REPORTED quantum calibration/result claim against textbook physical invariants —
    deterministically, with NO device. Pass a row with any of: t1_us, t2_us, t2_method, p01, p10,
    readout_isolated/readout_parallel (lists), cz_error, rzz_error. Returns ADMISSIBLE only if
    every applicable invariant holds (T2<=2*T1 unless DD declared; P01>=P10 thermal; CZ~RZZ;
    parallel-readout basis). Fail-closed: any physical inconsistency flags the row.

    This is the quantum analog of GRIM/statcheck — it rejects a spec/result that contradicts
    physics without re-running the experiment (record<->text re-derivation). To gate a NOISY
    MEASUREMENT against the device's calibrated noise model instead, use capas_quantum_hw."""
    import capas_quantum_physics
    return capas_quantum_physics.audit_calibration_row(calibration_row or {})


def invariants(block: dict[str, Any]) -> dict[str, Any]:
    """Check a block of declared quantities against every applicable DOMAIN LAW — deterministic,
    cross-domain, no oracle, no LLM. `block` may carry any of: accounting{assets,liabilities,
    equity}, quantum{...}, grim{mean,n,decimals?}, probabilities[...]/distribution{...},
    parts[...]+total. Returns PASS only if every applicable invariant holds (fail-closed).

    Same mechanism behind the core gate: when this block is supplied under evidence.invariants,
    a violation OVERRIDES the verdict to REJECT for ANY claim type. Internal consistency under a
    domain's laws is the largest slice of text<->reality CAPAS can re-derive without an oracle —
    it does not break the GIGO ceiling, it raises the cost of lying to 'fabricate a consistent
    world'. The finance/psychology/quantum fraud cases are one mechanism (see demo_invariants)."""
    import capas_invariants
    return capas_invariants.audit(block or {})


def admit(claim_type: str, evidence: dict[str, Any], attester: str, claim_text: str = "",
          claim_id: str = "claim", at: str | None = None) -> dict[str, Any]:
    """Gate a claim AND enter it into the persisted survive-refutation ledger, bound to an
    attester. The verdict stops being a one-shot: it becomes a time-extended, refutable record.
    Returns the verdict + the PROVISIONAL WEIGHT — for a GATE (ACCEPT, proof-backed) the weight is
    full; for an ATTEST (declared, non-re-derivable) it is worth only the attester's standing
    EARNED by surviving refutation. This connects the gate (now) to accountability (over time) —
    the third pole, and the actual moat (trust-as-certification-standard)."""
    import capas_ledger_store
    verdict = gate(claim_type, evidence, claim_text, claim_id)
    cert = {"claim_id": claim_id, "verdict": verdict.get("verdict"),
            "claim_type": claim_type, "reason": verdict.get("reason")}
    weight = capas_ledger_store.attest(cert, attester, at=at)
    return {"verdict": verdict.get("verdict"), "claim_id": claim_id, "attester": attester,
            "provisional_weight": weight, "decision": verdict,
            "note": "attested to the survive-refutation ledger; call resolve() as the world measures it"}


def resolve(claim_id: str, outcome: str) -> dict[str, Any]:
    """The world's measurement on an attested claim: 'survived' or 'refuted'. This is the only
    mechanism CAPAS cannot fake — the world, not the engine, earns or destroys an attester's
    standing. Adversarial/temporal refutation is what makes the ATTEST slice accountable."""
    import capas_ledger_store
    return capas_ledger_store.resolve(claim_id, outcome)


def standing(attester: str) -> dict[str, Any]:
    """An attester's reputation, earned ONLY by surviving refutation over time (not by self-claim)."""
    import capas_ledger_store
    return capas_ledger_store.standing(attester)


def error_budget(calibration_row: dict[str, Any]) -> dict[str, Any]:
    """Beat the vendor benchmark: re-derive the COMPLETE per-layer error budget from a device's
    OWN published calibration fields, vs its optimistic headline (RB) number — fully auditable.
    Plus mitigation_prescription via error_correction(). (See docs/BEATING_THE_BENCHMARK.md.)"""
    import capas_quantum_physics
    return capas_quantum_physics.complete_error_budget(calibration_row or {})


def error_correction(calibration_row: dict[str, Any]) -> dict[str, Any]:
    """The deterministic error-correction prescription (DD / rep_delay / reset / readout) re-derived
    from a calibration row — the corrections the vendor panel does not hand you."""
    import capas_quantum_physics
    return capas_quantum_physics.mitigation_prescription(calibration_row or {})


__all__ = ["gate", "reward", "certificate", "verified", "gate_text", "gate_quantum", "invariants",
           "admit", "resolve", "standing", "error_budget", "error_correction"]
