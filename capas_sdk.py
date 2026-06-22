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


__all__ = ["gate", "reward", "certificate", "verified", "gate_text", "gate_quantum"]
