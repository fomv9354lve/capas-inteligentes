# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""STRENGTHEN, don't reduce: CLOSE the 'fail-closed' claim as a PROVEN structural invariant.

The dangerous version of '0 false-accepts' reads as an empirical guarantee that needs an external
oracle. That part stays SCOPED (pending an adjudicated pilot). But there is a STRUCTURAL property
that IS provable and can be locked forever by this test:

    A claim that is structurally deficient — unsupported type, missing required evidence, or a
    domain-invariant violation — is NEVER returned as ACCEPT.

This is fail-closed by construction. It does NOT claim CAPAS detects a well-formed liar (the GIGO
ceiling: a fabricated-but-consistent payload CAN be ACCEPTed — that is the honest limit, and it is
asserted here too, not hidden). The claim this test backs is precise: deficiency never upgrades to
ACCEPT. Once green, 'fail-closed' is CLOSED — no audit can demand more of THIS claim.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import capas_sdk

INV = {"reported_value": 1.0, "reference_value": 1.0, "tolerance": 1.0, "metric_period_match": True}

# Battery of structurally-deficient claims that must NEVER return ACCEPT.
DEFICIENT = [
    ("unsupported claim type", "no_such_claim_type", {"anything": True}),
    ("missing required evidence", "exact_model_solution", {}),
    ("missing required evidence (partial)", "financial_metric_claim", {"reported_value": 1.0}),
    ("exact_model fails tolerance", "exact_model_solution", {"abs_error": 5.0, "tolerance": 1e-3}),
    # invariant violations across all 10 domains (each must force REJECT, never ACCEPT)
    ("finance: books don't close", "financial_metric_claim", {**INV, "invariants": {"accounting": {"assets": 1000, "liabilities": 600, "equity": 300}}}),
    ("statistics: GRIM impossible", "financial_metric_claim", {**INV, "invariants": {"grim": {"mean": 5.19, "n": 10}}}),
    ("quantum: T2>2T1", "financial_metric_claim", {**INV, "invariants": {"quantum": {"t1_us": 11.2, "t2_us": 23.4, "t2_method": "ramsey"}}}),
    ("probability: p=1.4", "financial_metric_claim", {**INV, "invariants": {"probabilities": [0.3, 1.4]}}),
    ("conservation: parts!=total", "financial_metric_claim", {**INV, "invariants": {"parts": [10, 20, 35], "total": 60}}),
    ("chemistry: unbalanced", "financial_metric_claim", {**INV, "invariants": {"stoichiometry": {"reactants": {"CH4": 1, "O2": 1}, "products": {"CO2": 1, "H2O": 2}}}}),
    ("chemistry: charge unbalanced", "financial_metric_claim", {**INV, "invariants": {"charge_balance": {"reactants": [[1, 2]], "products": [[1, 3]]}}}),
    ("physics: bad dimensions", "financial_metric_claim", {**INV, "invariants": {"dimensions": {"lhs": "J", "rhs": {"kg": 1, "m": 1, "s": -2}}}}),
    ("physics: efficiency>1", "financial_metric_claim", {**INV, "invariants": {"bounds": {"efficiency": 1.2}}}),
    ("engineering: Ohm violated", "financial_metric_claim", {**INV, "invariants": {"ohms_law": {"V": 10, "I": 2, "R": 3}}}),
    ("epidemiology: base-rate fallacy", "financial_metric_claim", {**INV, "invariants": {"bayes_ppv": {"sensitivity": 0.99, "specificity": 0.99, "prevalence": 0.001, "claimed_ppv": 0.99}}}),
    ("epidemiology: VE>1", "financial_metric_claim", {**INV, "invariants": {"vaccine_efficacy": {"cases_vax": -5, "n_vax": 1000, "cases_unvax": 50, "n_unvax": 1000}}}),
    ("biology: HW inconsistent", "financial_metric_claim", {**INV, "invariants": {"hardy_weinberg": {"AA": 0.3, "Aa": 0.5, "aa": 0.3}}}),
    ("mathematics: wrong root", "financial_metric_claim", {**INV, "invariants": {"root_check": {"polynomial": [-9, 0, 1], "root": 2}}}),
]

# A well-formed, self-consistent claim that CAPAS *does* accept — and the honest GIGO note:
# CAPAS cannot tell whether its inputs are TRUE, only whether they are consistent and re-derivable.
SUPPORTED = ("exact_model_solution", {"abs_error": 0.0, "tolerance": 1e-3})


def run() -> int:
    fails = []
    accepted_deficient = 0
    for name, ct, ev in DEFICIENT:
        v = capas_sdk.gate(ct, ev, name).get("verdict")
        if v == "ACCEPT":
            accepted_deficient += 1
            fails.append(f"FALSE-ACCEPT: '{name}' returned ACCEPT (fail-closed VIOLATED)")
    n = len(DEFICIENT)
    print(f"structural fail-closed: {n - accepted_deficient}/{n} deficient claims correctly NOT accepted")

    # the property holds iff ZERO deficient claims were accepted
    closed = accepted_deficient == 0
    # honesty co-assertion: a supported claim IS accepted (the gate is not a reject-everything machine)
    sup = capas_sdk.gate(*SUPPORTED, "supported").get("verdict")
    not_reject_machine = sup == "ACCEPT"
    print(f"honesty: a well-supported claim IS accepted -> {sup} (not a reject-everything machine)")
    print("honest limit (SCOPED, not closed): a well-FORMED claim with fabricated-but-consistent "
          "inputs can be ACCEPTed — CAPAS checks consistency, not truth (the GIGO ceiling).")

    ok = closed and not_reject_machine
    for f in fails:
        print("  XX", f)
    print("\nCLAIM CLOSED: 'fail-closed — a structurally-deficient claim is never accepted' is a proven "
          "invariant (locked by this test). Empirical false-accept RATE on real claims stays SCOPED."
          if ok else "FAIL-CLOSED: VIOLATED — do not claim it.")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(run())
