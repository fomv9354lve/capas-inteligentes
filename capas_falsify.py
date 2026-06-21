"""CAPAS — falsifiable-idea classifier: the line between imagination and hallucination,
made mechanical (Popper's demarcation over deterministic rungs).

The engine CANNOT tell whether an open conjecture is TRUE — that is the GIGO ceiling.
But it CAN tell whether the idea NAMES WHAT WOULD KILL IT, and whether that killer test
is DETERMINISTIC (the engine can run it now) or belongs to the subject (an experiment).
That demarcation is the whole difference between a good ungrounded idea and a
hallucination — and it is computable without ever claiming the idea is true.

  REFUTED             — a grounded anchor / re-derivation already kills it (dies now)
  FALSIFIABLE         — coherent, ungrounded, AND a DETERMINISTIC test would refute it
                        if run; the engine ATTACHES that test. The good idea: KEPT, not
                        rejected for lacking proof (this is the imagination peer-review
                        usually kills for not being already-grounded).
  SUBJECT_FALSIFIABLE — falsifiable, but only the subject can run the test (empirical /
                        attestable); KEPT, deferred to the subject with the test named.
  SPECULATIVE         — no test could refute it (not even wrong); flagged, NOT kept as a
                        scientific conjecture.
  GROUNDED            — already re-derived; no longer an open conjecture.

This is the EMANCIPATION of the verifier from a rejector: instead of "unproven ->
reject", it is "unproven but falsifiable -> KEEP and attach the experiment that would
kill it." A generator (LLM / human / the cognitive layer) proposes the imagination;
THIS classifier turns each proposal into a falsifiable idea or discards the
hallucination — using CAPAS's own rungs (and the quantum simulator) as the oracles.

Cara 1 (product, deterministic). It imports no generative layer: generation is
upstream; this module only classifies falsifiability and attaches the killer test.
"""
from __future__ import annotations

from typing import Any

import capas_rcc

# Evidence rungs the engine can RE-DERIVE -> a deterministic test exists that could
# return REFUTED. The quantum simulator (quantum_circuit) is one such oracle.
_DETERMINISTIC_RUNGS = {
    "computation", "raw_data", "raw", "derivation", "accounting", "dimensions",
    "stoichiometry", "sql", "quantum_circuit", "circuit", "registry", "integration",
    "zk_proof", "crypto", "xbrl", "reproduction", "consilience",
}
# The SPECIFIC deterministic falsifier per rung — the actual experiment the engine
# runs to try to kill the idea. This is what makes the attached test real rather than a
# generic "supply evidence" placeholder. The quantum_circuit entry is the simulator.
_RUNG_FALSIFIER = {
    "quantum_circuit": "simulate the declared gates and compare the output state/distribution to the "
                       "claim; any deviation beyond tolerance refutes it (the quantum simulator is the oracle)",
    "circuit":         "simulate the declared circuit and compare its output to the claim; a mismatch refutes",
    "computation":     "re-compute the operation from the inputs; result != reported value refutes",
    "raw_data":        "re-derive the reported statistic from the raw rows; a mismatch refutes",
    "stoichiometry":   "balance the reaction and re-derive the molar quantities; an imbalance refutes",
    "accounting":      "re-derive the accounting identity (assets = liabilities + equity); a break refutes",
    "dimensions":      "re-derive the dimensional equation; a unit/exponent mismatch refutes",
    "sql":             "re-execute the query over the committed rows; a different result refutes",
    "derivation":      "re-run the declared derivation chain; a step that does not reproduce refutes",
    "registry":        "reconcile against the public registry figure; a divergence refutes",
    "zk_proof":        "verify the proof against the public inputs; a failed verification refutes",
    "crypto":          "recompute the commitment/signature; a mismatch refutes",
    "xbrl":            "re-derive the tagged figure from the filing; a mismatch refutes",
    "consilience":     "test against each independent adjacency; a disagreeing adjacency refutes",
}
# Claim families that ARE falsifiable but only by a real-world experiment/attestation
# the subject must run (the engine cannot re-derive an experiment).
_SUBJECT_TESTABLE = ("empirical", "clinical", "physical", "financial", "measurement",
                     "chemical", "biolog", "assay", "study")


def _deterministic_falsifier_present(payload: dict[str, Any]) -> bool:
    """Does the idea carry a hook the engine has a rung to re-derive (so a test could
    return REFUTED)? Either supplied evidence, or a declared `falsifier` template the
    conjecturer states as 'this is what would kill my idea'."""
    ev = payload.get("evidence") or {}
    if set(ev) & _DETERMINISTIC_RUNGS:
        return True
    fz = (payload.get("claim") or {}).get("falsifier") or payload.get("falsifier")
    return isinstance(fz, dict) and bool(set(fz) & _DETERMINISTIC_RUNGS)


def falsifiability(payload: dict[str, Any]) -> dict[str, Any]:
    """Classify ONE idea by its falsifiability (not its truth) and attach its killer test."""
    cert = capas_rcc.rcc(payload)
    verdict = cert.get("verdict")
    refuted = cert.get("refuted") or []
    proposal = cert.get("solution_proposal") or []
    det = _deterministic_falsifier_present(payload)

    if refuted or verdict == "REJECT":
        klass = "REFUTED"
        why = "a grounded anchor / re-derivation already refutes it — it dies now"
    elif verdict == "ACCEPT":
        klass = "GROUNDED"
        why = "already re-derived; no longer an open conjecture"
    elif det:
        klass = "FALSIFIABLE"
        why = "ungrounded, but carries a DETERMINISTIC test the engine can run to refute it"
    else:
        ctype = ((payload.get("claim") or {}).get("type") or "").lower()
        if any(k in ctype for k in _SUBJECT_TESTABLE):
            klass = "SUBJECT_FALSIFIABLE"
            why = "falsifiable only by a real-world experiment/attestation the subject must run"
        else:
            klass = "SPECULATIVE"
            why = "no test could refute it (not even wrong) — not kept as a scientific conjecture"

    # The killer test = the SPECIFIC deterministic falsifier for each rung the idea
    # actually carries (the real experiment — e.g. run the simulator), followed by the
    # engine's own correction/supply proposal. This is what makes the idea falsifiable
    # rather than hallucinated: it ships with the experiment that would kill it.
    ev = payload.get("evidence") or {}
    fz = (payload.get("claim") or {}).get("falsifier") or payload.get("falsifier") or {}
    present_rungs = (set(ev) | set(fz if isinstance(fz, dict) else {})) & set(_RUNG_FALSIFIER)
    killer_test = [{"kind": "RUN", "run": _RUNG_FALSIFIER[k], "deterministic": True, "rung": k}
                   for k in sorted(present_rungs)]
    seen = {t["run"] for t in killer_test}
    for s in proposal:
        if s["do"] not in seen:
            killer_test.append({"kind": s["kind"], "run": s["do"], "deterministic": s["kind"] in ("CORRECT", "SUPPLY")})
            seen.add(s["do"])
    return {
        "idea": (payload.get("claim") or {}).get("text"),
        "claim_id": (payload.get("claim") or {}).get("id"),
        "falsifiability": klass,
        "why": why,
        "killer_test": killer_test,                      # the attached experiment(s)
        "deterministic_oracle_exists": det,
        "keep": klass in ("FALSIFIABLE", "SUBJECT_FALSIFIABLE"),  # good idea -> KEEP, do not reject
        "verdict": verdict,
        "note": "the engine does NOT claim the idea is true; it classifies what would kill it. "
                "FALSIFIABLE/SUBJECT_FALSIFIABLE are kept (imagination); REFUTED/SPECULATIVE are not.",
    }


def keep_falsifiable(conjectures: list[dict[str, Any]]) -> dict[str, Any]:
    """Run a BATCH of proposed ideas (from any generator) through the demarcation. KEEP
    the falsifiable ones with their killer tests attached; discard refuted/speculative.
    This is the generator's filter: imagination survives, hallucination does not."""
    buckets: dict[str, list] = {"FALSIFIABLE": [], "SUBJECT_FALSIFIABLE": [],
                                "REFUTED": [], "SPECULATIVE": [], "GROUNDED": []}
    for c in conjectures:
        f = falsifiability(c)
        buckets[f["falsifiability"]].append(f)
    kept = buckets["FALSIFIABLE"] + buckets["SUBJECT_FALSIFIABLE"]
    return {
        "proposed": len(conjectures),
        "kept": len(kept),
        "kept_ideas": kept,                              # the falsifiable survivors + their tests
        "discarded_refuted": len(buckets["REFUTED"]),
        "discarded_speculative": len(buckets["SPECULATIVE"]),
        "already_grounded": len(buckets["GROUNDED"]),
        "by_class": {k: len(v) for k, v in buckets.items()},
        "principle": "kept = imagination (names its own deterministic or subject-run falsifier); "
                     "discarded = hallucination (refuted now, or unfalsifiable). The verifier KEEPS "
                     "good ungrounded ideas instead of rejecting them for being unproven.",
    }
