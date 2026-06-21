"""CAPAS — conjecture bridge compiler (Lakatos mechanized).

A coherent-but-unproven claim must NOT be rejected for the absence of proof — it
must be SCAFFOLDED. Given a conjecture, this compiles the minimal bridge: the
ordered set of checkable obligations whose closing would ground it, each tagged
with the concrete action that closes it and whether that action terminates at a
LEAF (CAPAS can then re-derive it) or at the SUBJECT (only a human attestation /
a cryptographic or quantum proof can close it — the Löbian remainder).

It does NOT decide truth; it returns the *program to verification* — "here is
exactly what you would need to show", graded by bridge length and viability. This
is the move that keeps the deterministic engine from killing imagination: REJECT
is reserved for refutation (contradiction with a grounded invariant); everything
coherent-but-unproven gets a compiled bridge, never a rejection.

Depth-1 over CAPAS's own obligation vocabulary (the immediate planks + their
closing actions); deeper multi-hop lemma chains grow as the verified substrate
grows (see the closed loop). Built on capas_admissibility.
"""
from __future__ import annotations

from typing import Any

import capas_admissibility

# obligation status -> (concrete action that closes it, terminal kind)
#   leaf    = once supplied/fixed, CAPAS re-derives it deterministically
#   subject = only the human subject (attestation) or a crypto/quantum proof closes it
_CLOSE = {
    "NOT_SUPPLIED": ("supply the raw data (e.g. group_a/group_b) so the statistic re-computes", "leaf"),
    "MISSING_COMPONENTS": ("supply the missing line items / XBRL concepts for the ratio", "leaf"),
    "NO_FACTS": ("supply a parseable filing instance", "leaf"),
    "ARELLE_UNAVAILABLE": ("install the XBRL backend (arelle) to extract the filing", "leaf"),
    "NO_SEED": ("record the stochastic seed so the run is reproducible", "leaf"),
    "UNJUSTIFIED_BAND": ("attach a recognized tolerance_basis (instrument/method/regulatory)", "leaf"),
    "MALFORMED": ("repair the malformed field / formula", "leaf"),
    "UNKNOWN_RATIO": ("register the ratio's formula + components", "leaf"),
    "UNKNOWN_IDENTITY": ("register the accounting identity", "leaf"),
    "UNKNOWN_QUANTITY": ("register the physical quantity's dimension", "leaf"),
    "UNKNOWN_UNIT": ("register the unit's SI dimension vector", "leaf"),
    "UNKNOWN_ALGORITHM": ("use a supported hash algorithm", "leaf"),
    "NONPOSITIVE_DENOMINATOR": ("provide a positive economic denominator or re-scope the ratio", "leaf"),
    "UNTRUSTED_VK": ("register a trusted zero-knowledge verifying key", "leaf"),
    "DISCREPANCY": ("reconcile the posted figure with the re-derived figure", "leaf"),
    "UNRESOLVED": ("supply the recognized quantity+unit", "leaf"),
    # terminate at the subject (the Löbian remainder)
    "UNBACKED": ("obtain a signed attestation / provenance (only the subject can ground this)", "subject"),
    "BEYOND_FRONTIER": ("supply a CVQC proof (LWE) or attest a real quantum computer", "subject"),
    "ABSTAIN": ("quantify the off-baseline condition, or attest it", "leaf"),
    "SEED_CONDITIONAL": ("pre-register the seed before the data, or attest seed-robustness", "subject"),
    "UNJUSTIFIED_DIVERGENCE": ("attach the signed analyst justification for the manual override", "subject"),
    "UNRESOLVED_EVIDENCE": ("resolve the supplied evidence with a recognized rung, or attest", "subject"),
}


def bridge(payload: dict[str, Any]) -> dict[str, Any]:
    """Compile the minimal bridge that would ground a conjecture."""
    adm = capas_admissibility.admissibility(payload)
    planks, residual = [], []
    for o in adm.get("next_obligations", []):
        action, kind = _CLOSE.get(o.get("status"), ("supply the recognized evidence for this rung", "leaf"))
        (planks if kind == "leaf" else residual).append(
            {"obligation": o.get("status"), "via": o.get("check"), "action": action, "terminates": kind})
    for o in adm.get("irreducible_residual", []):
        action, kind = _CLOSE.get(o.get("status"), ("defer to the subject (attestation)", "subject"))
        residual.append({"obligation": o.get("status"), "via": o.get("check"), "action": action,
                         "terminates": "subject"})

    total = len(planks) + len(residual)
    viability = len(planks) / total if total else 1.0
    if adm["class"] == "REFUTED":
        status = "REFUTED — contradicts a grounded invariant; no bridge (this is refutation, not absence of proof)"
    elif adm["class"] in ("VERIFIED",):
        status = "ALREADY GROUNDED — no bridge needed"
    elif not planks and residual:
        status = "BRIDGE ENDS AT THE SUBJECT — only attestation/a proof closes it (Löbian remainder)"
    else:
        status = "BRIDGE COMPILED — a finite program of checkable planks would ground it"

    return {
        "target": (payload.get("claim") or {}).get("text"),
        "admissibility_score": adm["score"], "class": adm["class"],
        "status": status,
        "minimal_bridge": planks,            # leaf planks: CAPAS re-derives once closed
        "residual_to_subject": residual,     # the Löbian edge: only the subject closes it
        "bridge_length": len(planks),
        "viability": round(viability, 4),
        "next_step": (planks[0] if planks else (residual[0] if residual else None)),  # highest-leverage move
        "note": "Coherent-but-unproven is scaffolded, never rejected. REJECT is reserved for refutation.",
    }
