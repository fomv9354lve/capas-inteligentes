"""Demo + check: the Reflexive Conformal Certificate (RCC).

Asserts the three-stratum behaviour — GROUNDED (re-derived), GENERATED (coherent,
unverified -> abstain + minimal bridge), UNKNOWABLE (named boundary with a typed
reason, incl. the 'magic'/simulability frontier) — plus REFUTED, the signature,
and the standing Löbian self-limitation clause. Deterministic; no network/key.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import capas_rcc as R

SV = "capas-claim-payload-v3"
FIN = {"reported_value": 1.0, "reference_value": 1.0, "tolerance": 1.0, "metric_period_match": True}


def _p(text, ct, ev):
    return {"schema_version": SV, "claim": {"id": "c", "type": ct, "text": text}, "evidence": ev}


def run() -> int:
    grounded = _p("balances", "financial_metric_claim",
                  {**FIN, "accounting": {"identity": "balance_sheet", "assets": 1000, "liabilities": 600, "equity": 400}})
    generated = _p("treatment works", "statistical_confidence",
                   {"p_value": 0.01, "alpha": 0.05, "effect_direction_confirmed": True})
    unk_attest = _p("X causes Y", "causal_mechanism_claim",
                    {"intervention_or_natural_experiment": True, "temporal_order_established": True,
                     "confounders_controlled": True, "mechanism_evidence_present": True})
    unk_magic = _p("beyond frontier", "statistical_confidence",
                   {"p_value": 0.01, "alpha": 0.05, "effect_direction_confirmed": True,
                    "quantum_circuit": {"qubits": 40, "gates": [{"gate": "t", "qubits": [0]}],
                                        "claim": {"type": "probability", "bitstring": "0" * 40, "value": 0.5}}})
    refuted = _p("Water boils at 500C", "statistical_confidence",
                 {"p_value": 0.01, "alpha": 0.05, "effect_direction_confirmed": True})

    checks = []

    c = R.rcc(grounded)
    checks.append(("grounded -> GROUNDED stratum", c["headline"].startswith("GROUNDED")
                   and len(c["strata"]["grounded"]) >= 1))

    c = R.rcc(generated)
    gen = c["strata"]["generated"]
    checks.append(("generated -> abstain + minimal bridge",
                   len(gen["items"]) >= 1 and len(gen["minimal_bridge"]) >= 1))

    c = R.rcc(unk_attest)
    checks.append(("unbacked -> UNKNOWABLE: requires_attestation",
                   len(c["strata"]["unknowable"]) >= 1
                   and "requires_attestation" in c["strata"]["unknowable"][0]["why_unreachable"]))

    c = R.rcc(unk_magic)
    checks.append(("beyond frontier -> UNKNOWABLE: magic/simulability boundary",
                   any("simulability_frontier" in u["why_unreachable"] for u in c["strata"]["unknowable"])))

    c = R.rcc(refuted)
    checks.append(("refuted -> REFUTED", c["headline"].startswith("REFUTED")))

    c = R.rcc(grounded)
    checks.append(("signed (Ed25519) + certificate_id",
                   c.get("signature", {}).get("algorithm") == "Ed25519" and bool(c.get("certificate_id"))))
    checks.append(("standing Löbian self-limitation present",
                   "cannot certify its own soundness" in c["loebian_clause"]
                   and "names but cannot enter" in c["loebian_clause"]))

    ok = True
    for label, good in checks:
        ok = ok and good
        print(f"{'✅' if good else '❌'} {label}")
    print("REFLEXIVE CONFORMAL CERTIFICATE: all checks pass ✅" if ok else "RCC: FAILURES ❌")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(run())
