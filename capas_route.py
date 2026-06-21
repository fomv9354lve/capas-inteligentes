"""CAPAS — unified intelligent certification router.

One engine, many verification rungs, routed by the REAL properties of the evidence
(is the result deterministically re-derivable? is the data private? is it a quantum
computation, and is it below the classical-simulability frontier?). Each rung is
labelled with its actual soundness basis — exact (unconditional), knowledge-
soundness under a pairing assumption (KZG/q-SDH) for succinct/ZK, LWE for CVQC,
EUF-CMA for signatures — and its scope (GATE = re-derived/proved; ATTEST = signed).

The router selects the STRONGEST feasible rung whose required artifact is present,
maps it to the jurisdiction demand it satisfies, and states the honest fallback.
Deterministic, no LLM. Pairs with capas_verify (which executes the selected rung).
"""
from __future__ import annotations

from typing import Any

try:
    from capas_quantum import classify as _q_classify
except Exception:  # pragma: no cover
    _q_classify = None

# Rung soundness basis (real, not figurative).
SOUNDNESS = {
    "re-execution":        "exact, unconditional (deterministic recomputation / byte-equality)",
    "quantum-statevector": "exact, unconditional (classical statevector / Gottesman-Knill below frontier)",
    "zk-snark":            "computational: knowledge-soundness under KZG/q-SDH; succinct + hides witness",
    "cvqc-mahadev":        "computational: soundness under LWE (classical verification of a quantum prover)",
    "signed-provenance":   "computational: EUF-CMA signatures + binding commitments (attestation, not re-derivation)",
    "attest":              "accountability only — no verification of the underlying fact (GIGO residual)",
    "form":                "decidable schema/type validation (well-formedness only)",
}
SCOPE = {
    "re-execution": "GATE", "quantum-statevector": "GATE", "zk-snark": "GATE",
    "cvqc-mahadev": "GATE", "signed-provenance": "ATTEST", "attest": "ATTEST", "form": "FORM",
}

# What a rung satisfies, per jurisdiction's key binding demand.
JURISDICTION_DEMAND = {
    "EU": "GMP Annex 22 static deterministic re-derivable model (LLMs barred); AI Act Art.10 traceability; eIDAS QEAA",
    "US": "21 CFR Part 11 / ALCOA+ trace-any-result-to-raw-data; MRM SR 26-2 byproduct-not-reconstructed evidence",
    "UK": "MHRA GxP independent record-lifecycle reconstruction; PRA SS1/23 independent replication 'regardless of technology'",
    "SG": "MAS AIRM auditor must 'replicate the implementation and its results'",
    "CN": "GB machine-readable persistent provenance / NMPA re-derivable trial data",
    "GLOBAL": "ISO/IEC 42001 + NIST AI RMF measured-not-asserted controls; RO-Crate / C2PA / W3C PROV",
}

PROVENANCE_KEYS = ("provenance", "ro_crate", "registry_id", "signed_attestation",
                   "attestation", "c2pa_manifest", "qeaa")
ATTEST_CLASS_FIELDS = {
    "intervention_or_natural_experiment", "temporal_order_established",
    "confounders_controlled", "mechanism_evidence_present",
    "risk_of_bias_assessed", "conflict_resolution_method",
    "artifact_available", "independent_reproduction_pass",
}


def route(payload: dict[str, Any], jurisdiction: str | None = None) -> dict[str, Any]:
    ev = payload.get("evidence", {}) or {}
    candidates: list[dict[str, Any]] = []

    def add(rung: str, reason: str, **extra: Any) -> None:
        candidates.append({"rung": rung, "soundness": SOUNDNESS[rung], "scope": SCOPE[rung],
                           "reason": reason, **extra})

    # ── exact re-derivation rungs (strongest: unconditional) ──
    if ev.get("crypto") is not None:
        add("re-execution", "a cryptographic digest/Merkle artifact is present (bit-exact recomputation)")
    if ev.get("accounting") is not None:
        add("re-execution", "an accounting identity is present (re-derived arithmetic)")
    if ev.get("dimensions") is not None:
        add("re-execution", "a dimensional-consistency claim is present (SI exponent check)")
    if any(k in ev for k in ("computation", "integration")):
        add("re-execution", "a deterministic computation/integration artifact is present")
    if ev.get("derivation") is not None:
        env = ev.get("environment") or {}
        pinned = all(env.get(k) for k in ("language", "version", "os", "locale"))
        add("re-execution", "a source->derived dataset is present"
            + (" with a pinned environment" if pinned else " but the environment is NOT pinned (downgrade to attest)"),
            environment_pinned=pinned)
    if ev.get("raw_data") or ev.get("raw"):
        add("re-execution", "raw data is present to recompute the declared statistic")

    # ── quantum rung (exact below the simulability frontier, else CVQC/attest) ──
    if ev.get("quantum_circuit") is not None and _q_classify is not None:
        cls = _q_classify(ev["quantum_circuit"])
        if cls["engine_statevector_runnable"]:
            add("quantum-statevector",
                f"quantum claim below the frontier (n={cls['qubits']}, t={cls['t_count']}, Clifford={cls['clifford_only']})",
                frontier=cls)
        elif ev.get("quantum_proof"):
            add("cvqc-mahadev", f"quantum claim beyond classical simulation (n={cls['qubits']}, t={cls['t_count']}); a quantum proof is supplied", frontier=cls)
        else:
            add("attest", f"quantum claim beyond the classical-simulability frontier (n={cls['qubits']}, t={cls['t_count']}); no quantum proof — attest a real QC", frontier=cls)

    # ── zero-knowledge / succinct rung (hidden data, large, or explicitly proved) ──
    if ev.get("zk_proof") is not None:
        add("zk-snark", "a zero-knowledge / circuit proof is present (verifies over hidden data; succinct)")

    # ── signed provenance (attestation, not re-derivation) ──
    if any(ev.get(k) for k in PROVENANCE_KEYS):
        add("signed-provenance", "a signed provenance / attestation artifact is present")

    # ── attest-class design evidence with no re-derivable artifact ──
    design = sorted(set(ev) & ATTEST_CLASS_FIELDS)
    if design and not candidates:
        add("attest", f"only study-design / unobservable evidence ({', '.join(design)}); not re-derivable by computation")

    if not candidates:
        add("form", "no re-derivable artifact or provenance supplied; only schema/contract checks apply")

    # strongest-first ordering
    order = ["re-execution", "quantum-statevector", "zk-snark", "cvqc-mahadev",
             "signed-provenance", "attest", "form"]
    candidates.sort(key=lambda c: order.index(c["rung"]))
    selected = candidates[0]

    return {
        "selected_rung": selected["rung"],
        "scope": selected["scope"],
        "soundness_basis": selected["soundness"],
        "why": selected["reason"],
        "plan": [{"rung": c["rung"], "scope": c["scope"], "soundness": c["soundness"], "reason": c["reason"]}
                 for c in candidates],
        "jurisdiction": jurisdiction,
        "jurisdiction_demand_satisfied": JURISDICTION_DEMAND.get((jurisdiction or "GLOBAL").upper(), JURISDICTION_DEMAND["GLOBAL"]),
        "fallback": "if the selected rung's artifact fails to verify, CAPAS does not silently accept: "
                    "it REJECTs (re-derivation/proof fails) or HOLDs and routes to the next-strongest rung, "
                    "ending at ATTEST (signed, never marketed as verified) for the irreducible residual.",
        "decision_path": "deterministic; no LLM",
    }


if __name__ == "__main__":  # pragma: no cover
    import json
    import sys
    payload = json.load(open(sys.argv[1])) if len(sys.argv) > 1 else json.load(sys.stdin)
    juris = sys.argv[2] if len(sys.argv) > 2 else None
    print(json.dumps(route(payload, juris), indent=2))
