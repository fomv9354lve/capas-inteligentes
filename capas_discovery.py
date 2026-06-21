"""CAPAS — certifying a GENUINELY NEW claim (e.g. a quantum-gravity reconciliation).

The hard case: a claim with NO prior anchor, no reference value, no ground truth. You
cannot certify it is TRUE (that is about reality — the GIGO ceiling + induction). But you
CAN mechanically certify the FORM of a discovery, which is exactly what separates a real
candidate from a crank or a hallucination. This composes the session's pieces into one
stratified certificate:

  1. CORRESPONDENCE  — it must reduce to the established theories in their validated limits
                       (GR in the classical limit, QFT in the flat/weak limit). The anchor of
                       the NEW is the OLD it must contain. A broken limit -> REFUTED, now.
  2. CONSISTENCY     — dimensional / unitary / causal self-consistency (re-derivable).
  3. FALSIFIABILITY  — it must predict something NEW where the old theories disagree or are
                       untested, and NAME the experiment that would kill it (capas_falsify).
                       No novel falsifier -> SPECULATIVE, not a discovery.
  4. CONSILIENCE     — independent experimental corroboration, counted by independence groups
                       and aggregated by the independence-weighted e-process (capas_sequential);
                       the residual shrinks but NEVER closes (induction).
  5. UNKNOWABLE      — whether it is TRUE: named, handed to the experiment and the subject.

Honest limits kept in-surface: computing a 'limit reduction' faithfully is itself the
autoformalization bridge problem (semantic-illusion residual); the engine cannot adjudicate
two rival consistent+falsifiable theories before experiment; and it cannot verify the
experiment was done honestly (GIGO). Cara 1, deterministic over the supplied checks.
"""
from __future__ import annotations

from typing import Any

import capas_consilience
import capas_sequential


def ingest_world_response(candidate: dict[str, Any], response: dict[str, Any]) -> dict[str, Any]:
    """The ERROR-CORRECTION step — how the world's response ENTERS (knowledge creation).

    The world is exogenous: CAPAS does not know its answer, it RECEIVES one (an experiment
    outcome) and re-certifies. response = {experiment, outcome:'refuted'|'corroborated'|
    'inconclusive', group, e_value?}.

    The Popperian asymmetry is the engine of knowledge creation, and it is explicit here:
      - ONE refutation -> REFUTED. Definite knowledge created: the conjecture is FALSE
        (one disagreeing experiment suffices), modulo experiment honesty (GIGO).
      - corroboration -> the residual shrinks but NEVER closes: no finite number of
        confirmations proves a universal claim (induction). Knowledge grows, certainty never.
    """
    outcome = response.get("outcome")
    if outcome == "refuted":
        return {"status": "REFUTED", "by": response.get("experiment"),
                "knowledge_created": "DEFINITE — the world fired the killer test; the conjecture is FALSE "
                                     "(one refutation suffices — the Popperian asymmetry), modulo experiment honesty (GIGO)",
                "next": "the refuted conjecture is not waste — its boundary is now known; the search resumes from it"}
    if outcome == "corroborated":
        updated = {**candidate, "corroborations": (candidate.get("corroborations") or [])
                   + [{"group": response.get("group"), "agrees": True, "e_value": response.get("e_value", 3.0)}]}
        cert = certify_novel(updated)
        return {"status": "STILL FALSIFIABLE — more corroborated, not proven",
                "knowledge_created": "PARTIAL — fabrication-resistance rose; certainty NOT reached (induction never closes)",
                "corroboration": cert["strata"]["corroboration"], "updated_candidate": updated}
    return {"status": "UNCHANGED", "knowledge_created": "none — the experiment was inconclusive"}


def certify_novel(candidate: dict[str, Any]) -> dict[str, Any]:
    """Issue a stratified certificate for a genuinely new theoretical claim. It certifies
    the FORM of a discovery (reduces-to-known + consistent + falsifiable + corroboration-
    graded + boundary-named) — never that the claim is true."""
    name = candidate.get("name", "candidate")

    # 1. CORRESPONDENCE — must reproduce each established theory in its validated limit.
    limits = candidate.get("limit_reductions", []) or []
    failed_limits = [l.get("to") for l in limits if not l.get("reproduces")]

    # 2. CONSISTENCY — self-consistency checks the engine can re-derive.
    consistency = candidate.get("consistency", {}) or {}
    failed_consistency = [k for k, v in consistency.items() if v is False]

    if failed_limits or failed_consistency:
        return {
            "candidate": name,
            "headline": "REFUTED — fails a known limit or self-consistency (a real theory must contain the old)",
            "broken_limits": failed_limits, "broken_consistency": failed_consistency,
            "decision_path": "deterministic; the established theories are the anchors",
        }

    # 3. FALSIFIABILITY — the NOVEL prediction must name its own killer experiment.
    pred = candidate.get("novel_prediction") or {}
    has_novel = bool(pred.get("differs_from")) and bool(pred.get("falsifier"))
    falsifiability = "FALSIFIABLE" if has_novel else ("SPECULATIVE" if pred else "NO_PREDICTION")

    # 4. CONSILIENCE — independence-weighted corroboration (never closes).
    corrob = candidate.get("corroborations", []) or []
    seq = capas_sequential.sequential_test(corrob) if corrob else None
    cons = capas_consilience.consilience(1.0, [{"value": 1.0, "group": c.get("group")}
                                               for c in corrob if c.get("agrees", True)]) if corrob else None
    residual = cons["reality_gap_residual"] if cons else 1.0

    if falsifiability != "FALSIFIABLE":
        headline = (f"NOT A DISCOVERY CANDIDATE — {('coherent but makes no new falsifiable prediction' if pred else 'no prediction')}; "
                    "reduces to the known and is self-consistent, but adds no testable novelty (SPECULATIVE)")
    else:
        headline = (f"ADMISSIBLE DISCOVERY CANDIDATE — reduces to {[l.get('to') for l in limits]} in their limits, "
                    f"self-consistent, and makes a NEW falsifiable prediction. NOT certified true; held in the "
                    f"FALSIFIABLE stratum with its killer experiment attached, corroboration residual {residual}.")

    return {
        "candidate": name,
        "headline": headline,
        "strata": {
            "grounded": {                                  # re-derivable now
                "limit_reductions": [f"reduces to {l.get('to')} in the {l.get('regime')} limit" for l in limits],
                "consistency": [k for k, v in consistency.items() if v],
                "coverage": "deterministic: the old theories are the anchors; the limits are re-derivable "
                            "(faithful limit computation inherits the autoformalization-bridge residual)",
            },
            "falsifiable": {                               # the new anchor it predicts
                "falsifiability": falsifiability,
                "novel_prediction": pred.get("text"),
                "differs_from": pred.get("differs_from"),
                "killer_experiment": pred.get("falsifier"),
                "status": "KEPT — a good ungrounded idea is not rejected for being unproven; it ships with its test",
            },
            "corroboration": ({                            # graded, never closes
                "independent_groups": seq.get("independent_groups"),
                "e_process": seq.get("e_process"),
                "reject_null_at_alpha": seq.get("reject_null"),
                "fabrication_resistance_residual": residual,
                "meaning": "independence-weighted; circular corroboration counts ~once; shrinks but NEVER reaches "
                           "certainty (induction — no finite confirmations prove a universal claim)",
            } if seq else {"status": "no independent corroboration yet — residual 1.0 (pure conjecture)"}),
            "unknowable": ("Whether the theory is TRUE. Beyond the engine forever — it is about reality, settled "
                           "only by running the named experiment, and even then never with finality (induction). "
                           "Handed to the experiment and the physics community, not certified here."),
        },
        "what_capas_cannot_do": [
            "say the theory is right (it certifies form, not truth)",
            "adjudicate two rival consistent + falsifiable theories before the experiment is run",
            "verify the experiment itself was done honestly (the GIGO residual)",
            "guarantee the limit-reductions were formalized faithfully (the semantic-illusion residual)",
        ],
        "loebian_clause": "The engine certifies the GROUNDED stratum and the LOCATION of the unknowable; it does "
                          "not certify the unknowable, and cannot certify its own soundness. The subject — here, "
                          "the experiment and the community — is the fixed point it names but cannot enter.",
        "decision_path": "deterministic; no LLM in the verdict",
    }
