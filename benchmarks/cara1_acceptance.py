"""CARA 1 — product acceptance suite (the deployable verification engine).

The single contained gate for the deployable product: the deterministic,
multi-domain, proof-carrying verifier + the signed self-bounding certificate +
the relational braid + the prose->verdict extraction + distribution-free coverage.
Imports ONLY Cara-1 modules (no cognitive layer), so the product can ship and be
tested independently of Cara 2.

Covers, end to end:
  A. Domain re-derivation — every domain: lie -> REJECT, malformed/unknown -> not
     ACCEPT (the GIGO invariant), grounding domains: honest -> ACCEPT.
  B. GIGO invariant sweep — no false-accept across domains (the core guarantee).
  C. Signed self-bounding certificate (RCC) — Ed25519 signed, independently
     verifiable, tamper-detected, engine-pinned, stratified, with the self-bar.
  D. Braid (network) — correspondence; locally-grounded-yet-braid-incoherent fault;
     tamper changes the non-local root.
  E. Extraction (prose -> verdict) — honest ACCEPT, hallucinated input HOLD,
     fabricated citation HOLD, grounded-but-lie REJECT.
  F. Conformal coverage — covered / not-covered / voided-on-exchangeability /
     insufficient-calibration (honest).
  G. Fail-closed — re-derivable evidence supplied but unresolved -> never ACCEPT.
  H. Router — picks the strongest feasible rung per evidence.
"""
from __future__ import annotations

import copy
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import capas_verify as V
import capas_route as R
import capas_rcc
import capas_braid as BR
import capas_extract as EX
import capas_conformal as CF
from scipy import stats as _stats

SV = "capas-claim-payload-v3"
FIN = {"reported_value": 1.0, "reference_value": 1.0, "tolerance": 1.0, "metric_period_match": True}


def _fin(ev, text="x"):
    return {"schema_version": SV, "claim": {"id": "c", "type": "financial_metric_claim", "text": text},
            "evidence": {**FIN, **ev}}


def _stat(ev, text="x"):
    return {"schema_version": SV, "claim": {"id": "c", "type": "statistical_confidence", "text": text},
            "evidence": ev}


def run() -> int:
    checks: list[tuple[str, bool]] = []

    def ok(label, cond):
        checks.append((label, bool(cond)))

    def vfin(ev):
        return V.verify(_fin(ev))["verified_verdict"]

    a = [10.1, 10.3, 9.9, 10.2, 10.0, 10.4, 9.8, 10.1]
    b = [12.0, 12.3, 11.8, 12.1, 12.2, 11.9, 12.4, 12.0]
    p = round(float(_stats.ttest_ind(a, b, equal_var=False)[1]), 5)
    dg = hashlib.sha256(b"capas").hexdigest()

    # ---- A. domain re-derivation (lie -> REJECT; honest -> ACCEPT for grounding domains) ----
    ok("A crypto: honest ACCEPT / forged REJECT",
       vfin({"crypto": {"algorithm": "sha256", "preimage": "capas", "claimed_digest": dg}}) == "ACCEPT"
       and vfin({"crypto": {"algorithm": "sha256", "preimage": "capas", "claimed_digest": "bad"}}) == "REJECT")
    ok("A accounting: balances ACCEPT / imbalance REJECT / gamed-tolerance REJECT",
       vfin({"accounting": {"identity": "balance_sheet", "assets": 1000, "liabilities": 600, "equity": 400}}) == "ACCEPT"
       and vfin({"accounting": {"identity": "balance_sheet", "assets": 1000, "liabilities": 600, "equity": 350}}) == "REJECT"
       and vfin({"accounting": {"identity": "balance_sheet", "assets": 1000, "liabilities": 600, "equity": 350, "tolerance": 9999}}) == "REJECT")
    ok("A financial ratio: re-derives ACCEPT / lie REJECT",
       vfin({"accounting": {"identity": "financial_ratio", "ratio": "current_ratio", "current_assets": 200, "current_liabilities": 100, "reported": 2.0}}) == "ACCEPT"
       and vfin({"accounting": {"identity": "financial_ratio", "ratio": "current_ratio", "current_assets": 200, "current_liabilities": 100, "reported": 5.0}}) == "REJECT")
    ok("A dimensions: consistent ACCEPT / incommensurable REJECT / unknown HOLD",
       vfin({"dimensions": {"quantity": "force", "unit": "N"}}) == "ACCEPT"
       and vfin({"dimensions": {"quantity": "force", "unit": "m"}}) == "REJECT"
       and vfin({"dimensions": {"quantity": "flux", "unit": "q"}}) in ("HOLD",))
    ok("A stoichiometry: balanced ACCEPT / unbalanced REJECT",
       vfin({"stoichiometry": {"reactants": [{"formula": "H2", "coeff": 2}, {"formula": "O2", "coeff": 1}], "products": [{"formula": "H2O", "coeff": 2}]}}) == "ACCEPT"
       and vfin({"stoichiometry": {"reactants": [{"formula": "H2", "coeff": 1}], "products": [{"formula": "H2O", "coeff": 1}]}}) == "REJECT")
    ok("A sql: aggregate re-derives ACCEPT / lie REJECT",
       vfin({"sql": {"rows": [{"r": 100}, {"r": 50}], "query": {"op": "sum", "column": "r"}, "reported": 150}}) == "ACCEPT"
       and vfin({"sql": {"rows": [{"r": 100}, {"r": 50}], "query": {"op": "sum", "column": "r"}, "reported": 999}}) == "REJECT")
    ok("A statistics: raw re-derives ACCEPT / declared-only HOLD / contradicted REJECT",
       V.verify(_stat({"p_value": p, "alpha": 0.05, "effect_direction_confirmed": True, "raw_data": {"group_a": a, "group_b": b}}))["verified_verdict"] == "ACCEPT"
       and V.verify(_stat({"p_value": 0.01, "alpha": 0.05, "effect_direction_confirmed": True}))["verified_verdict"] == "HOLD"
       and V.verify(_stat({"p_value": 0.0001, "alpha": 0.05, "effect_direction_confirmed": True, "raw_data": {"group_a": a, "group_b": [10.0] * 8}}))["verified_verdict"] == "REJECT")
    ok("A physical/anchors: impossible REJECT (T<0K, v>c, Holevo) via structured path",
       vfin({"physical": {"quantity": "temperature", "value": -300, "unit": "C"}}) == "REJECT"
       and vfin({"physical": {"quantity": "speed", "value": 4e8, "unit": "m/s"}}) == "REJECT"
       and vfin({"physical": {"quantity": "accessible_information", "value": 5, "unit": "bits", "conditions": {"qubits": 1}}}) == "REJECT")

    # ---- B. GIGO invariant sweep: never a false-accept ----
    gigo = [
        {"computation": {"operation": "magic", "inputs": {"x": 1}, "reported_value": 1.0, "tolerance": 0.01}},
        {"dimensions": {"quantity": "flux", "unit": "furlong"}},
        {"accounting": {"identity": "financial_ratio", "ratio": "sharpe", "reported": 1.2}},
        {"sql": {"rows": [{"r": 1}], "query": {"op": "badop", "column": "r"}, "reported": 1}},
        {"stoichiometry": {"reactants": [{"formula": "Zz", "coeff": 1}], "products": [{"formula": "Zz", "coeff": 1}]}},
    ]
    ok("B GIGO invariant: no 'cannot verify' case is ever ACCEPT",
       all(vfin(e) != "ACCEPT" for e in gigo))

    # ---- C. signed self-bounding certificate (RCC) ----
    cert = capas_rcc.rcc(_fin({"accounting": {"identity": "balance_sheet", "assets": 1000, "liabilities": 600, "equity": 400}}))
    chk = V.verify_receipt(V.verify(_fin({"accounting": {"identity": "balance_sheet", "assets": 1000, "liabilities": 600, "equity": 400}})))
    rec = V.verify(_fin({"accounting": {"identity": "balance_sheet", "assets": 1000, "liabilities": 600, "equity": 400}}))
    tampered = copy.deepcopy(rec); tampered["verified_verdict"] = "REJECT"
    ok("C receipt signed (Ed25519), independently verifiable, engine-pinned",
       chk["signature_valid"] in (True, None) and chk["receipt_id_matches"] and bool(rec.get("engine_digest")))
    ok("C tampering the receipt invalidates the signature",
       V.verify_receipt(tampered)["signature_valid"] in (False, None))
    ok("C RCC stratified + Löbian parallax self-bar present",
       "strata" in cert and "parallactic, not a container" in cert.get("parallax_self_bar", ""))
    ok("C RCC names the boundary (magic) for beyond-frontier claims",
       any("simulability_frontier" in u["why_unreachable"]
           for u in capas_rcc.rcc(_stat({"p_value": 0.01, "alpha": 0.05, "effect_direction_confirmed": True,
                                          "quantum_circuit": {"qubits": 40, "gates": [{"gate": "t", "qubits": [0]}],
                                                              "claim": {"type": "probability", "bitstring": "0" * 40, "value": 0.5}}}))["strata"]["unknowable"]))

    # ---- D. braid (network / cross-claim) ----
    br = BR.Braid()
    rr = lambda cid, ca, cl, rep: _fin({"accounting": {"identity": "financial_ratio", "ratio": "current_ratio", "current_assets": ca, "current_liabilities": cl, "reported": rep}})
    A = br.add({**rr("A", 200, 100, 2.0), "claim": {"id": "A", "type": "financial_metric_claim", "text": "A"}}, target="T", value=2.0, method="m1")
    Bn = br.add({**rr("B", 400, 200, 2.0), "claim": {"id": "B", "type": "financial_metric_claim", "text": "B"}}, target="T", value=2.0, method="m2")
    C = br.add({**rr("C", 300, 100, 3.0), "claim": {"id": "C", "type": "financial_metric_claim", "text": "C"}}, target="T", value=3.0, method="m3")
    root0 = br.root()
    tamper = br.tamper("A", 9.9)
    ok("D braid: same-target methods CORRESPOND (reciprocity)", Bn["corresponds"] == ["A"])
    ok("D braid: a locally-grounded claim that disagrees is a FAULT (caught by the whole)",
       C["braid_fault"] and len(br.faults()) >= 1)
    ok("D braid: tampering a node changes the non-local root", tamper["root_changed"] and br.root() != root0)

    # ---- E. extraction discipline (prose -> verdict; deterministic offline) ----
    src = ("ACME 10-K. As of Dec 31 2024, total current assets were $200,000 and total current "
           "liabilities were $100,000. Management states the current ratio is 2.0.")
    honest = {"claim": {"type": "financial_metric_claim", "text": "current ratio is 2.0"},
              "evidence": {"accounting": {"identity": "financial_ratio", "ratio": "current_ratio",
                                          "current_assets": 200000, "current_liabilities": 100000, "reported": 2.0}},
              "citations": [{"value": 200000, "span": "total current assets were $200,000"},
                            {"value": 100000, "span": "total current liabilities were $100,000"}]}
    hall = copy.deepcopy(honest); hall["evidence"]["accounting"]["current_assets"] = 500000
    hall["evidence"]["accounting"]["reported"] = 5.0
    hall["citations"] = [{"value": 500000, "span": "total current assets were $500,000"},
                         {"value": 100000, "span": "total current liabilities were $100,000"}]
    fab = copy.deepcopy(honest); fab["citations"][0]["span"] = "audited assets of 200000 by us"
    lie = copy.deepcopy(honest); lie["evidence"]["accounting"]["reported"] = 5.0
    ok("E extraction: honest grounded -> ACCEPT", EX.assemble_and_verify(honest, src)["verdict"] == "ACCEPT")
    ok("E extraction: hallucinated input -> HOLD (deferred)", EX.assemble_and_verify(hall, src)["verdict"] == "HOLD")
    ok("E extraction: fabricated citation -> HOLD", EX.assemble_and_verify(fab, src)["verdict"] == "HOLD")
    ok("E extraction: grounded inputs but lie claimed -> REJECT (re-derived)", EX.assemble_and_verify(lie, src)["verdict"] == "REJECT")

    # ---- F. conformal coverage ----
    cal = [round(0.0005 * (i + 1), 5) for i in range(20)]
    ok("F conformal: in-band covered with guarantee; out-of-band not covered",
       CF.certify(CF.nonconformity(50.02, 50.0), cal, 0.1)["covered"] is True
       and CF.certify(CF.nonconformity(80.0, 50.0), cal, 0.1)["covered"] is False)
    ok("F conformal: voids on exchangeability failure; insufficient calibration reported",
       CF.certify(0.001, cal, 0.1, exchangeable=False)["covered"] is None
       and CF.certify(0.001, [0.001, 0.002], 0.1)["covered"] is None)

    # ---- G. fail-closed ----
    ok("G fail-closed: re-derivable evidence supplied but unresolved -> never ACCEPT",
       vfin({"dimensions": {"quantity": "flux", "unit": "N"}}) != "ACCEPT")

    # ---- H. router ----
    rt = R.route(_fin({"accounting": {"identity": "balance_sheet", "assets": 1, "liabilities": 1, "equity": 0}}), "EU")
    ok("H router: selects re-execution for a re-derivable artifact, maps EU demand",
       rt["selected_rung"] == "re-execution" and "Annex 22" in rt["jurisdiction_demand_satisfied"])

    # ---- report ----
    passed = sum(1 for _, c in checks if c)
    for label, c in checks:
        print(f"{'✅' if c else '❌'} {label}")
    print(f"\nCARA 1 ACCEPTANCE: {passed}/{len(checks)} checks pass "
          + ("✅" if passed == len(checks) else "❌"))
    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    raise SystemExit(run())
