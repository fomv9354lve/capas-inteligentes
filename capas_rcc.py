"""CAPAS — Reflexive Conformal Certificate (RCC).

The artifact the cross-disciplinary audit converged on but nobody has built: a
certificate that does not just rule on a claim but STRATIFIES the claim into

  GROUNDED   — re-derived / attested, with the kind of coverage that grounds it
  GENERATED  — coherent and in-distribution but unverified -> abstain, with the
               minimal bridge (the obligations that would ground it)
  UNKNOWABLE — the boundary the certifier names but provably cannot enter, each
               item tagged with WHY it is unreachable (the Löbian remainder)

and that ALWAYS carries the standing Löbian clause: a system cannot certify its
own soundness (Löb's theorem), so this certificate is OTHER-grounded — by the
published engine digest, the Ed25519 signature, and deferral to the human
subject — never self-grounded. It is, as far as the surveyed state of the art
shows, the first certificate that maps its own boundary of the unknowable: a
calibrated statement of what it cannot calibrate.

This is the formal twin of perceptual reality-monitoring's failure mode ("this
might be a dream"): instead of confabulating over its ungrounded region, the
certifier names that region and hands it to the subject. Built on
capas_admissibility (the graded reward) + capas_verify (the signed receipt).
"""
from __future__ import annotations

from typing import Any

import capas_admissibility
import capas_verify

# Why an irreducible item is UNREACHABLE by deterministic re-derivation. Each is a
# distinct face of the Löbian remainder — the place the certifier cannot ground.
_UNKNOWABLE_REASON = {
    "BEYOND_FRONTIER": "beyond_simulability_frontier — non-stabilizerness ('magic'); "
                       "no efficient deterministic re-derivation exists (cf. the computed t* frontier)",
    "UNBACKED": "requires_attestation — study-design / unobservable evidence; only the human "
                "subject can ground it (a signed attestation, not a computation)",
    "ABSTAIN": "off_domain_inapplicable — the anchored law/constant does not apply here; the "
               "condition must be quantified or attested",
    "SEED_CONDITIONAL": "requires_subject_judgment — reproducible only under a producer-chosen "
                        "seed; robustness across seeds is a human call",
    "UNJUSTIFIED_DIVERGENCE": "requires_signed_human_judgment — a manual override with no reason",
    "UNRESOLVED_EVIDENCE": "fail_closed_unresolved — re-derivable evidence supplied but no rung "
                           "resolved it; held rather than accepted",
}
_LOEBIAN_CLAUSE = (
    "A grounding-monitor cannot certify its own grounding (Löb's theorem: no consistent system "
    "proves its own soundness). This certificate is therefore OTHER-grounded — by the pinned "
    "engine digest, the Ed25519 signature, and deferral of the UNKNOWABLE stratum to the human "
    "subject — never self-grounded. The subject is the self-grounded fixed point this certificate "
    "names but cannot enter."
)


def _coverage_for(check: dict[str, Any]) -> str:
    name, status = check.get("check"), check.get("status")
    if status in ("VERIFIED",):
        if name in ("statistical_rederivation",):
            return "bounded — re-computed within the declared (basis-justified) tolerance"
        return "exact — bit/byte-deterministic re-derivation (coverage = 1)"
    if status == "RECONCILED":
        return "exact — posted figure reconciles with the re-derived figure"
    if status in ("ATTESTED", "ATTESTED_SURFACED", "PRECOMMITTED_SEED"):
        return "attested — grounded in a signed human/provenance act, not re-derived"
    return "n/a"


def rcc(payload: dict[str, Any]) -> dict[str, Any]:
    """Issue a Reflexive Conformal Certificate for a claim."""
    adm = capas_admissibility.admissibility(payload)
    receipt = capas_verify.verify(payload)
    checks = receipt.get("checks", []) or []

    grounded, generated, unknowable = [], [], []
    refuted = []
    for c in checks:
        b = capas_admissibility._bucket(c.get("status"))
        item = {"check": c.get("check"), "status": c.get("status")}
        if b == "grounded":
            grounded.append({**item, "coverage": _coverage_for(c)})
        elif b == "refuted":
            refuted.append(item)
        elif b == "irreducible":
            unknowable.append({**item, "why_unreachable":
                               _UNKNOWABLE_REASON.get(c.get("status"), "requires_attestation — "
                               "not re-derivable by the engine; defer to the subject")})
        else:
            generated.append(item)

    # The generated stratum carries its minimal bridge (what would ground it).
    bridge = adm.get("next_obligations", [])

    # GIGO residual, graded by INDEPENDENT adjacency (consilience). Re-derivation never
    # reaches evidence<->reality; if the claim carries independent corroborations, we
    # don't close that gap — we MEASURE how tightly the verifiable web pins it, and
    # recursion moves the unknown-unknown up a level (it never reaches 0; Löb).
    consilience_report = None
    cons = (payload.get("evidence") or {}).get("consilience")
    if cons:
        import capas_consilience
        try:
            r = capas_consilience.consilience_recursive(cons)
            consilience_report = {
                "fabrication_resistance_total_residual": r["total_residual"],
                "depth": r["depth"], "moved_to": r["moved_to"],
                "irreducible_floor": r["irreducible_floor"],
                "contradicted_by_independent_adjacency": r["any_contradiction"],
                "meaning": "the GIGO residual graded by independent adjacency; does NOT verify "
                           "reality, measures how much room is left in the {unknowable} (shrinks "
                           "geometrically with recursion, never to 0 — the subject holds the floor).",
            }
        except Exception:
            consilience_report = None

    verdict = receipt.get("verified_verdict")
    if refuted:
        headline = "REFUTED — contradicts a grounded invariant (inadmissible-because-false)"
    elif grounded and not generated and not unknowable:
        headline = "GROUNDED — fully re-derived; only the standing Löbian limit applies"
    elif unknowable and not grounded:
        headline = "DEFERRED — the substantive claim falls in the UNKNOWABLE stratum (the subject must close it)"
    else:
        headline = "STRATIFIED — partially grounded; generated remainder abstained; unknowable named"

    body = {
        "schema": "capas-reflexive-conformal-certificate-v1",
        "claim_id": (payload.get("claim") or {}).get("id"),
        "headline": headline,
        "verdict": verdict, "scope": receipt.get("scope"),
        "admissibility_score": adm.get("score"),          # the dense reward in [0,1]
        "strata": {
            "grounded": grounded,                          # re-derived/attested, with coverage
            "generated": {"items": generated, "minimal_bridge": bridge,
                          "status": "abstain — coherent, in-distribution, unverified"},
            "unknowable": unknowable,                      # the named boundary, with typed reasons
        },
        "refuted": refuted,
        "boundary": ([u["why_unreachable"] for u in unknowable]
                     or ["none specific to this claim; the standing Löbian limit below always holds"]),
        "gigo_consilience": consilience_report,   # graded reality-anchoring (None if no adjacencies supplied)
        "loebian_clause": _LOEBIAN_CLAUSE,
        "self_limitation": ("This certificate certifies the GROUNDED stratum and the LOCATION of "
                            "its own UNKNOWABLE stratum; it does NOT certify the unknowable, and it "
                            "cannot certify its own soundness. That is not a defect — it is the "
                            "constitutive condition (the certifier that names what it cannot reach)."),
        # Žižek sharpening: keep {unknowable} PARALLACTIC, not substantive, so the
        # certificate of its own limit does not become a new guarantor (a 'big Other'
        # / fetishistic disavowal). The unknowable is NOT hidden content the system
        # lacks (no Other of the Other holds it); it is the registered NON-COINCIDENCE
        # between re-derivation (GATE) and attestation (ATTEST). And the certifier bars
        # ITSELF: the criteria by which it sorts grounded/generated/unknowable are
        # themselves ungrounded within it — that sorting axiom is the certifier's own
        # unknown-known, the unmarked place it tags FROM but cannot tag. Included as
        # content so this very certificate is not mistaken for a final ground.
        "parallax_self_bar": (
            "The UNKNOWABLE stratum is parallactic, not a container: it is the non-coincidence "
            "between GATE (re-derivation) and ATTEST (the subject), not content a hidden Other "
            "possesses. The act of sorting grounded/generated/unknowable rests on this engine's "
            "own axioms, which it cannot certify from within (its unknown-known). This clause is "
            "included so the certificate of a limit is not itself taken as the final ground — the "
            "Real has shifted to the unmarked place from which this tagging is done."),
        "engine_digest": receipt.get("engine_digest"),
        "decision_path": "deterministic; no LLM in the verdict",
    }
    import json
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"))
    import hashlib
    body["certificate_id"] = "sha256:" + hashlib.sha256(canonical.encode()).hexdigest()[:32]
    sig = capas_verify._sign_receipt(canonical)
    if sig is not None:
        body["signature"] = sig
    return body
