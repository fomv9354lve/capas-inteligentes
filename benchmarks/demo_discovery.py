# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""Demo + check: certifying a GENUINELY NEW claim (quantum-gravity reconciliation).

Deterministic. Certifies the FORM of a discovery, never its truth. Asserts: a candidate
that reduces to GR/QFT, is self-consistent, and makes a NEW falsifiable prediction is held
as an ADMISSIBLE DISCOVERY CANDIDATE (not true) with its killer experiment attached and the
truth-question handed to the experiment; a theory that breaks a known limit is REFUTED; a
mere reinterpretation with no novel prediction is SPECULATIVE; and two INDEPENDENT
corroborations do NOT yet cross significance (induction — never closes).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import capas_discovery as D

REAL = {
    "name": "Candidate QG reconciliation",
    "limit_reductions": [{"to": "General Relativity", "regime": "classical", "reproduces": True},
                         {"to": "Quantum Field Theory", "regime": "flat", "reproduces": True}],
    "consistency": {"dimensional": True, "unitary": True, "causal": True},
    "novel_prediction": {"text": "Planck-scale photon dispersion", "differs_from": ["GR", "QM"],
                         "falsifier": {"experiment": "GRB time-of-flight vs energy", "refutes_if": "no dispersion"}},
    "corroborations": [{"group": "Fermi-LAT", "agrees": True, "e_value": 3.0},
                       {"group": "MAGIC", "agrees": True, "e_value": 3.0}],
}
CRANK = {"name": "Crank", "limit_reductions": [{"to": "GR", "regime": "classical", "reproduces": False}],
         "consistency": {"dimensional": True}, "novel_prediction": {"text": "all", "differs_from": ["GR"], "falsifier": {}}}
REINTERP = {"name": "Reinterpretation", "limit_reductions": [{"to": "GR", "regime": "classical", "reproduces": True}],
            "consistency": {"dimensional": True}, "novel_prediction": {"text": "same", "differs_from": [], "falsifier": {}}}


def run() -> int:
    checks = []
    r = D.certify_novel(REAL)
    checks.append(("real candidate -> ADMISSIBLE DISCOVERY CANDIDATE (form certified, NOT truth)",
                   r["headline"].startswith("ADMISSIBLE")))
    checks.append(("its novel prediction is KEPT with the killer experiment attached",
                   r["strata"]["falsifiable"]["killer_experiment"].get("experiment") is not None
                   and r["strata"]["falsifiable"]["falsifiability"] == "FALSIFIABLE"))
    checks.append(("truth is named UNKNOWABLE and handed to the experiment (not certified)",
                   "TRUE" in r["strata"]["unknowable"] and "experiment" in r["strata"]["unknowable"]))
    checks.append(("2 independent corroborations do NOT yet cross significance (induction never closes)",
                   r["strata"]["corroboration"]["reject_null_at_alpha"] is False
                   and r["strata"]["corroboration"]["fabrication_resistance_residual"] > 0))

    checks.append(("crank breaking the GR limit -> REFUTED", D.certify_novel(CRANK)["headline"].startswith("REFUTED")))
    checks.append(("reinterpretation with no novel prediction -> SPECULATIVE (not a discovery)",
                   "SPECULATIVE" in D.certify_novel(REINTERP)["headline"]))

    # THE KNOWLEDGE-CREATION ASYMMETRY (Popper): corroboration shrinks but never closes;
    # one refutation is definitive. This is how the world's response ENTERS.
    cand, residuals = REAL, []
    for src in ("HESS", "VERITAS", "CTA"):                     # the world keeps corroborating
        upd = D.ingest_world_response(cand, {"experiment": src, "outcome": "corroborated", "group": src})
        cand = upd["updated_candidate"]
        residuals.append(upd["corroboration"]["fabrication_resistance_residual"])
    shrinks_never_zero = all(residuals[i] > residuals[i + 1] for i in range(len(residuals) - 1)) and residuals[-1] > 0
    checks.append((f"world corroborates -> residual shrinks {residuals} but NEVER 0 (induction never closes)",
                   shrinks_never_zero))

    refute = D.ingest_world_response(REAL, {"experiment": "GRB time-of-flight", "outcome": "refuted"})
    checks.append(("ONE refutation -> REFUTED, definite knowledge (Popperian asymmetry)",
                   refute["status"] == "REFUTED" and "DEFINITE" in refute["knowledge_created"]))

    ok = all(c for _, c in checks)
    for label, c in checks:
        print(f"{'✅' if c else '❌'} {label}")
    print("NOVEL-CLAIM CERTIFICATION (certify the form of a discovery, never its truth): pass ✅" if ok
          else "DISCOVERY: FAILURES ❌")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(run())
