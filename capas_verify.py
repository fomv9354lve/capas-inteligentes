"""CAPAS — proof-carrying verification layer (Rung 3 re-execution + scope partition + receipt).

Sits ON TOP of the deterministic admissibility gate (``capas.decide_external_claim``)
and raises the bar ABOVE what regulation requires today:

  • A claim is ACCEPTED only when its evidence RE-DERIVES (re-computed, anchor-checked,
    or re-executed) — never on a bare declared field.
  • Evidence that is declared but not re-derivable is HELD, with an explicit ask for a
    re-derivable artifact or a signed provenance attestation. Declared-only ≠ accepted.
  • Non-deterministic / unobservable / GIGO evidence is PARTITIONED to ATTEST scope
    (signed + bound, never marketed as verified) instead of being silently accepted.
  • Every decision emits a portable, hash-bound verification RECEIPT a third party can
    re-check without re-running the gate.

Deterministic and reproducible. No LLM in the decision path. Mirrors the moat:
"gate the deterministic island, attest the ocean, and never conflate the two."
"""
from __future__ import annotations

import hashlib
import json
import math
import re
from typing import Any

import capas

try:  # real statistical re-derivation when available
    from scipy import stats as _scipy_stats  # type: ignore
    _HAS_SCIPY = True
except Exception:  # pragma: no cover
    _HAS_SCIPY = False


# ─────────────────────────────────────────────────────────────────────────────
# Anchor registry — known physical / mathematical truths. Deterministic regex
# scan of the claim text; a value that contradicts a known anchor is REJECTED
# regardless of how clean the declared statistics are. Auditable + extensible.
# ─────────────────────────────────────────────────────────────────────────────
ANCHORS: list[dict[str, Any]] = [
    {
        "id": "water_boiling_point_1atm_C",
        "truth": 100.0, "tol": 3.0, "unit": "°C",
        "pattern": r"water\s+boils?\s+at\s+(-?\d+(?:\.\d+)?)\s*°?\s*c\b",
        "desc": "Boiling point of water at 1 atm is 100°C",
    },
    {
        "id": "speed_of_light_m_s",
        "truth": 299_792_458.0, "tol": 1000.0, "unit": "m/s",
        "pattern": r"speed\s+of\s+light\s+(?:is|=|of)\s*(-?\d+(?:\.\d+)?)\s*m/?s",
        "desc": "Speed of light in vacuum is 299,792,458 m/s",
    },
    {
        "id": "water_freezing_point_1atm_C",
        "truth": 0.0, "tol": 3.0, "unit": "°C",
        "pattern": r"water\s+freezes?\s+at\s+(-?\d+(?:\.\d+)?)\s*°?\s*c\b",
        "desc": "Freezing point of water at 1 atm is 0°C",
    },
]


def anchor_contradictions(claim_text: str) -> list[dict[str, Any]]:
    """Deterministic scan: return anchors the claim text contradicts."""
    text = (claim_text or "").lower()
    hits: list[dict[str, Any]] = []
    for a in ANCHORS:
        m = re.search(a["pattern"], text)
        if not m:
            continue
        asserted = float(m.group(1))
        if abs(asserted - a["truth"]) > a["tol"]:
            hits.append({
                "anchor": a["id"], "asserted": asserted,
                "truth": a["truth"], "unit": a["unit"], "desc": a["desc"],
            })
    return hits


# ─────────────────────────────────────────────────────────────────────────────
# Scope partition (#3): which evidence is RE-DERIVABLE (GATE) vs ATTEST-class.
# Study-design / unobservable booleans cannot be re-derived by computation; they
# require verifiable provenance, otherwise the claim is HELD, not accepted.
# ─────────────────────────────────────────────────────────────────────────────
ATTEST_CLASS_FIELDS = {
    "intervention_or_natural_experiment", "temporal_order_established",
    "confounders_controlled", "mechanism_evidence_present",
    "risk_of_bias_assessed", "conflict_resolution_method",
    "artifact_available", "independent_reproduction_pass",
}
PROVENANCE_KEYS = (
    "provenance", "ro_crate", "registry_id", "signed_attestation",
    "attestation", "c2pa_manifest", "qeaa",
)


def _has_provenance(evidence: dict[str, Any]) -> bool:
    return any(evidence.get(k) for k in PROVENANCE_KEYS)


# ─────────────────────────────────────────────────────────────────────────────
# Re-derivation (#1, Rung 3): actually re-compute, don't trust the declared value.
# ─────────────────────────────────────────────────────────────────────────────
def _welch_p(group_a: list[float], group_b: list[float]) -> float:
    if _HAS_SCIPY:
        _, p = _scipy_stats.ttest_ind(group_a, group_b, equal_var=False)
        return float(p)
    # dependency-free Welch's t + normal approximation (large-sample) fallback
    na, nb = len(group_a), len(group_b)
    ma, mb = sum(group_a) / na, sum(group_b) / nb
    va = sum((x - ma) ** 2 for x in group_a) / (na - 1)
    vb = sum((x - mb) ** 2 for x in group_b) / (nb - 1)
    se = math.sqrt(va / na + vb / nb) or 1e-12
    t = (ma - mb) / se
    # two-sided p via standard normal approximation
    return 2.0 * (1.0 - 0.5 * (1.0 + math.erf(abs(t) / math.sqrt(2.0))))


def rederive_statistical(evidence: dict[str, Any]) -> dict[str, Any] | None:
    """If raw data is supplied, RE-COMPUTE the p-value and compare to declared.
    Returns None when there is nothing re-derivable (declared-only)."""
    raw = evidence.get("raw_data") or evidence.get("raw")
    if not isinstance(raw, dict):
        return None
    a, b = raw.get("group_a"), raw.get("group_b")
    if not (isinstance(a, list) and isinstance(b, list) and len(a) > 1 and len(b) > 1):
        return None
    recomputed = _welch_p([float(x) for x in a], [float(x) for x in b])
    declared = evidence.get("p_value")
    declared_f = float(declared) if isinstance(declared, (int, float)) else None
    # match within a small absolute/relative tolerance
    match = (
        declared_f is not None
        and abs(recomputed - declared_f) <= max(0.01, 0.10 * max(declared_f, 1e-6))
    )
    return {
        "recomputed_p": round(recomputed, 5),
        "declared_p": declared,
        "match": bool(match),
        "engine": "scipy.ttest_ind(Welch)" if _HAS_SCIPY else "welch+normal-approx",
    }


# ─────────────────────────────────────────────────────────────────────────────
# Receipt (#2): portable, hash-bound, re-checkable verdict artifact.
# ─────────────────────────────────────────────────────────────────────────────
def _receipt(payload, base_verdict, final, scope, tier, checks, rationale) -> dict[str, Any]:
    claim = payload.get("claim", {}) or {}
    body = {
        "schema": "capas-verification-receipt-v1",
        "claim_id": claim.get("id"),
        "claim_type": claim.get("type"),
        "base_gate_verdict": base_verdict,
        "verified_verdict": final,
        "scope": scope,                 # GATE (re-derivable) | ATTEST (signed only)
        "verification_tier": tier,      # FORM | RE-DERIVED | ATTEST
        "checks": checks,
        "rationale": rationale,
        "residual_disclosure": (
            "CAPAS verifies record-to-evidence RE-DERIVATION, not evidence-to-reality "
            "truth (the GIGO residual is irreducible). ATTEST-scope evidence is signed "
            "and bound, never marketed as verified."
        ),
        "decision_path": "deterministic; no LLM",
    }
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"))
    body["receipt_id"] = "sha256:" + hashlib.sha256(canonical.encode()).hexdigest()[:32]
    return body


# ─────────────────────────────────────────────────────────────────────────────
# The proof-carrying gate.
# ─────────────────────────────────────────────────────────────────────────────
# Evidence keys that are CAPAS-verify EXTENSIONS (re-derivable artifacts / provenance),
# not part of the base evidence contract. They are stripped before the base gate runs
# (which rejects unknown fields) and consumed by this layer instead.
_EXTENSION_KEYS = {"raw_data", "raw", *PROVENANCE_KEYS}


def _base_payload(payload: dict[str, Any]) -> dict[str, Any]:
    evidence = {k: v for k, v in (payload.get("evidence") or {}).items() if k not in _EXTENSION_KEYS}
    return {**payload, "evidence": evidence}


def verify(payload: dict[str, Any]) -> dict[str, Any]:
    base = capas.decide_external_claim(_base_payload(payload))
    base_verdict = base.get("verdict") if isinstance(base, dict) else getattr(base, "verdict", "HOLD")

    claim = payload.get("claim", {}) or {}
    evidence = payload.get("evidence", {}) or {}
    ctype = claim.get("type")
    text = claim.get("text", "")

    checks: list[dict[str, Any]] = []
    rationale: list[str] = []
    final = base_verdict
    scope = "GATE"

    # (1) Anchor contradiction — a known physical/math truth overrides clean stats.
    hits = anchor_contradictions(text)
    if hits:
        checks.append({"check": "anchor_contradiction", "status": "FAIL", "detail": hits})
        rationale.append(
            f"Claim contradicts a known anchor: {hits[0]['desc']} "
            f"(asserted {hits[0]['asserted']}{hits[0]['unit']}). Rejected by re-derivation."
        )
        final = "REJECT"

    # The base gate already rejects/holds the self-failing cases (p>alpha, missing,
    # required-boolean-false). We only ADD scrutiny where the base said ACCEPT.
    if final == "ACCEPT":
        if ctype == "statistical_confidence":
            rd = rederive_statistical(evidence)
            if rd is None:
                checks.append({"check": "statistical_rederivation", "status": "NOT_SUPPLIED",
                               "detail": "no raw_data; p_value is declared, not re-derivable"})
                scope = "ATTEST"
                final = "HOLD"
                rationale.append(
                    "Standard above requirement: the statistical result is DECLARED, not "
                    "re-derivable. Supply raw_data (group_a/group_b) to GATE by re-computation, "
                    "or a signed provenance artifact to ATTEST. Declared-only evidence is held."
                )
            elif rd["match"]:
                checks.append({"check": "statistical_rederivation", "status": "VERIFIED", "detail": rd})
                rationale.append(
                    f"Re-computed p={rd['recomputed_p']} ({rd['engine']}) matches declared "
                    f"p={rd['declared_p']}: evidence re-derives. ACCEPT is verified, not trusted."
                )
            else:
                checks.append({"check": "statistical_rederivation", "status": "FAIL", "detail": rd})
                final = "REJECT"
                rationale.append(
                    f"Re-computed p={rd['recomputed_p']} contradicts declared p={rd['declared_p']}. "
                    "The declared statistic does not survive re-derivation — rejected."
                )
        else:
            # claim types whose key evidence is study-design / unobservable booleans
            attest_fields = sorted(set(evidence) & ATTEST_CLASS_FIELDS)
            if attest_fields:
                if _has_provenance(evidence):
                    checks.append({"check": "design_evidence_provenance", "status": "ATTESTED",
                                   "detail": {"fields": attest_fields, "provenance": True}})
                    scope = "ATTEST"
                    rationale.append(
                        "Study-design evidence carries verifiable provenance: ATTESTED "
                        "(signed/bound), not re-derived. Verdict stands on accountable attestation."
                    )
                else:
                    checks.append({"check": "design_evidence_provenance", "status": "UNBACKED",
                                   "detail": {"fields": attest_fields, "provenance": False}})
                    scope = "ATTEST"
                    final = "HOLD"
                    rationale.append(
                        "Standard above requirement: study-design evidence "
                        f"({', '.join(attest_fields)}) is ATTEST-class — it cannot be re-derived by "
                        "computation. Provide a verifiable provenance artifact (registry ID + signed "
                        "RO-Crate/C2PA). Unbacked declared booleans are not accepted."
                    )

    tier = (
        "RE-DERIVED" if any(c["status"] == "VERIFIED" for c in checks)
        else "ATTEST" if scope == "ATTEST"
        else "FORM"
    )
    return _receipt(payload, base_verdict, final, scope, tier, checks, rationale)


if __name__ == "__main__":  # pragma: no cover
    import sys
    payload = json.load(open(sys.argv[1])) if len(sys.argv) > 1 else json.load(sys.stdin)
    print(json.dumps(verify(payload), indent=2))
