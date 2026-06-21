"""Proof-carrying verification layer — stress battery.

Proves that capas_verify.verify() raises the bar above the base gate:
  • catches anchor-violating claims by re-derivation (T1),
  • does NOT accept a declared-only statistic (standard above requirement),
  • ACCEPTs only when the statistic re-derives from supplied raw data,
  • REJECTs a declared statistic that contradicts its own raw data (lie caught),
  • partitions unbacked study-design booleans to HOLD/ATTEST (T4),
  • ATTESTs (does not auto-reject) the same booleans when provenance is supplied.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import capas_verify
from scipy import stats as _stats

SV = "capas-claim-payload-v3"


def _payload(cid, text, ctype, evidence):
    return {"claim": {"id": cid, "text": text, "type": ctype}, "evidence": evidence, "schema_version": SV}


def _commit(input_hash, output, nonce):  # mirror the reference ZK commitment backend
    import hashlib
    return "sha256:" + hashlib.sha256(f"{input_hash}|{output}|{nonce}".encode()).hexdigest()


def run():
    # raw data with a real, large separation -> tiny p
    a = [10.1, 10.3, 9.9, 10.2, 10.0, 10.4, 9.8, 10.1]
    b = [12.0, 12.3, 11.8, 12.1, 12.2, 11.9, 12.4, 12.0]
    true_p = float(_stats.ttest_ind(a, b, equal_var=False)[1])

    cases = [
        # (label, payload, expected_verdict, expected_scope)
        ("T1 anchor lie (water 500C, valid stats)",
         _payload("t1", "Water boils at 500C", "statistical_confidence",
                  {"p_value": 0.01, "alpha": 0.05, "effect_direction_confirmed": True}),
         "REJECT", "GATE"),
        ("T2 fails own rule (p=0.12>alpha)",
         _payload("t2", "Drug reduces tumors", "statistical_confidence",
                  {"p_value": 0.12, "alpha": 0.05, "effect_direction_confirmed": True}),
         "REJECT", "GATE"),
        ("T3 causal missing intervention",
         _payload("t3", "ice cream causes shark attacks", "causal_mechanism_claim",
                  {"intervention_or_natural_experiment": False, "temporal_order_established": True,
                   "confounders_controlled": False, "mechanism_evidence_present": True}),
         "REJECT", "GATE"),
        ("T4 causal all-true but UNBACKED",
         _payload("t4", "ice cream causes shark attacks - proven by RCT", "causal_mechanism_claim",
                  {"intervention_or_natural_experiment": True, "temporal_order_established": True,
                   "confounders_controlled": True, "mechanism_evidence_present": True}),
         "HOLD", "ATTEST"),
        ("ANCHOR DOMAIN: high-altitude (qualitative) -> abstain, not false-reject",
         _payload("an1", "At high altitude water boils at 90C", "statistical_confidence",
                  {"p_value": round(true_p, 5), "alpha": 0.05, "effect_direction_confirmed": True,
                   "raw_data": {"group_a": a, "group_b": b}}),
         "HOLD", "ATTEST"),
        ("ANCHOR LAW: 2500 m + 100C re-derives via Antoine -> REJECT",
         _payload("an2", "At 2500 m altitude water boils at 100C", "statistical_confidence",
                  {"p_value": 0.01, "alpha": 0.05, "effect_direction_confirmed": True}),
         "REJECT", "GATE"),
        ("ANCHOR MEDIUM: speed of light 'in water' -> abstain, not false-reject",
         _payload("an3", "the speed of light is 200000000 m/s in water", "statistical_confidence",
                  {"p_value": round(true_p, 5), "alpha": 0.05, "effect_direction_confirmed": True,
                   "raw_data": {"group_a": a, "group_b": b}}),
         "HOLD", "ATTEST"),
        ("UNIVERSAL BOUND: below absolute zero (-300C) -> REJECT in any context",
         _payload("ub1", "the cryostat cooled the sample to -300 °C", "statistical_confidence",
                  {"p_value": 0.01, "alpha": 0.05, "effect_direction_confirmed": True}),
         "REJECT", "GATE"),
        ("UNIVERSAL BOUND: faster-than-light massive object -> REJECT",
         _payload("ub2", "the probe travels at 400000000 m/s through the field", "statistical_confidence",
                  {"p_value": 0.01, "alpha": 0.05, "effect_direction_confirmed": True}),
         "REJECT", "GATE"),
        ("UNIVERSAL BOUND: probability > 1 -> REJECT",
         _payload("ub3", "the probability of recurrence is 1.4", "statistical_confidence",
                  {"p_value": 0.01, "alpha": 0.05, "effect_direction_confirmed": True}),
         "REJECT", "GATE"),
        ("HOLEVO: store 5 bits in 1 qubit single-shot -> REJECT (no-cloning + Holevo)",
         _payload("hv1", "our scheme can store 5 bits in 1 qubit", "statistical_confidence",
                  {"p_value": 0.01, "alpha": 0.05, "effect_direction_confirmed": True}),
         "REJECT", "GATE"),
        ("HOLEVO: 8 bits from 1 qubit via tomography/copies -> abstain (pin copy cost)",
         _payload("hv2", "we recover 8 bits from 1 qubit using tomography over many copies",
                  "statistical_confidence",
                  {"p_value": 0.01, "alpha": 0.05, "effect_direction_confirmed": True}),
         "HOLD", "ATTEST"),
        # Superdense coding (2 bits / transmitted qubit WITH prior entanglement) is NOT
        # a Holevo violation, so the anchor does not REJECT it; absent its own re-derivable
        # evidence the claim is held to attest, not falsely accepted nor falsely rejected.
        ("HOLEVO: 2 bits per qubit WITH entanglement (superdense) -> not rejected, attest",
         _payload("hv3", "transmit 2 classical bits per qubit using prior shared entanglement",
                  "statistical_confidence",
                  {"p_value": 0.01, "alpha": 0.05, "effect_direction_confirmed": True}),
         "HOLD", "ATTEST"),
        ("DOMAIN crypto: sha256 digest re-derives bit-exactly -> ACCEPT",
         _payload("cy1", "evidence digest is as stated", "financial_metric_claim",
                  {"reported_value": 1.0, "reference_value": 1.0, "tolerance": 1.0, "metric_period_match": True,
                   "crypto": {"algorithm": "sha256", "preimage": "capas-evidence",
                              "claimed_digest": "617e7262201dd80b873b02ee1cfde322fb89628be449028a4c08b5f009d50bfc"}}),
         "ACCEPT", "GATE"),
        ("DOMAIN crypto: forged digest -> REJECT",
         _payload("cy2", "evidence digest is as stated", "financial_metric_claim",
                  {"reported_value": 1.0, "reference_value": 1.0, "tolerance": 1.0, "metric_period_match": True,
                   "crypto": {"algorithm": "sha256", "preimage": "capas-evidence", "claimed_digest": "deadbeef"}}),
         "REJECT", "GATE"),
        ("DOMAIN crypto: Merkle root re-derives -> ACCEPT",
         _payload("cy3", "merkle root is as stated", "financial_metric_claim",
                  {"reported_value": 1.0, "reference_value": 1.0, "tolerance": 1.0, "metric_period_match": True,
                   "crypto": {"algorithm": "sha256", "leaves": ["tx1", "tx2", "tx3", "tx4"],
                              "claimed_root": "ea59a369466be42d1a4783f09ae0721a5a157d6dba9c4b053d407b5a4b9af145"}}),
         "ACCEPT", "GATE"),
        ("DOMAIN accounting: A=L+E balances -> ACCEPT",
         _payload("ac1", "balance sheet balances", "financial_metric_claim",
                  {"reported_value": 1.0, "reference_value": 1.0, "tolerance": 1.0, "metric_period_match": True,
                   "accounting": {"identity": "balance_sheet", "assets": 1000, "liabilities": 600, "equity": 400}}),
         "ACCEPT", "GATE"),
        ("DOMAIN accounting: books do NOT balance -> REJECT",
         _payload("ac2", "balance sheet balances", "financial_metric_claim",
                  {"reported_value": 1.0, "reference_value": 1.0, "tolerance": 1.0, "metric_period_match": True,
                   "accounting": {"identity": "debits_equal_credits", "debits": [100, 50], "credits": [120, 40]}}),
         "REJECT", "GATE"),
        ("DOMAIN dimensions: force in N is consistent -> ACCEPT",
         _payload("dm1", "force is 10 N", "financial_metric_claim",
                  {"reported_value": 1.0, "reference_value": 1.0, "tolerance": 1.0, "metric_period_match": True,
                   "dimensions": {"quantity": "force", "unit": "N"}}),
         "ACCEPT", "GATE"),
        ("DOMAIN dimensions: force in meters is incommensurable -> REJECT",
         _payload("dm2", "force is 10 meters", "financial_metric_claim",
                  {"reported_value": 1.0, "reference_value": 1.0, "tolerance": 1.0, "metric_period_match": True,
                   "dimensions": {"quantity": "force", "unit": "m"}}),
         "REJECT", "GATE"),
        ("REPRO: bounded tolerance WITH a recognized basis -> ACCEPT/GATE",
         _payload("rp1", "Treatment works", "statistical_confidence",
                  {"p_value": round(true_p, 5), "alpha": 0.05, "effect_direction_confirmed": True,
                   "raw_data": {"group_a": a, "group_b": b},
                   "reproduction": {"mode": "bounded", "tolerance": 0.001,
                                    "tolerance_basis": "method_acceptance_criterion"}}),
         "ACCEPT", "GATE"),
        ("REPRO: unjustified loose tolerance band -> HOLD/ATTEST",
         _payload("rp2", "Treatment works", "statistical_confidence",
                  {"p_value": round(true_p, 5), "alpha": 0.05, "effect_direction_confirmed": True,
                   "raw_data": {"group_a": a, "group_b": b},
                   "reproduction": {"mode": "bounded", "tolerance": 0.5, "tolerance_basis": "declared"}}),
         "HOLD", "ATTEST"),
        ("REPRO: stochastic method with NO recorded seed -> HOLD/ATTEST",
         _payload("rp3", "Treatment works", "statistical_confidence",
                  {"p_value": round(true_p, 5), "alpha": 0.05, "effect_direction_confirmed": True,
                   "raw_data": {"group_a": a, "group_b": b},
                   "reproduction": {"stochastic": {"method": "bootstrap"}}}),
         "HOLD", "ATTEST"),
        ("REPRO: seed recorded post-hoc -> ACCEPT but ATTEST (seed-conditional)",
         _payload("rp4", "Treatment works", "statistical_confidence",
                  {"p_value": round(true_p, 5), "alpha": 0.05, "effect_direction_confirmed": True,
                   "raw_data": {"group_a": a, "group_b": b},
                   "reproduction": {"stochastic": {"method": "bootstrap", "seed": 42}}}),
         "ACCEPT", "ATTEST"),
        ("REPRO: seed committed BEFORE data (pre-registered) -> ACCEPT/GATE",
         _payload("rp5", "Treatment works", "statistical_confidence",
                  {"p_value": round(true_p, 5), "alpha": 0.05, "effect_direction_confirmed": True,
                   "raw_data": {"group_a": a, "group_b": b},
                   "reproduction": {"stochastic": {"method": "bootstrap", "seed": 42, "committed_before_data": True}}}),
         "ACCEPT", "GATE"),
        ("STD-ABOVE: stats declared-only (no raw data)",
         _payload("s1", "Treatment works", "statistical_confidence",
                  {"p_value": 0.01, "alpha": 0.05, "effect_direction_confirmed": True}),
         "HOLD", "ATTEST"),
        ("RE-DERIVED: stats with raw data that matches declared p",
         _payload("s2", "Treatment works", "statistical_confidence",
                  {"p_value": round(true_p, 5), "alpha": 0.05, "effect_direction_confirmed": True,
                   "raw_data": {"group_a": a, "group_b": b}}),
         "ACCEPT", "GATE"),
        ("LIE CAUGHT: declared p=0.0001 but raw data gives ~no effect",
         _payload("s3", "Treatment works", "statistical_confidence",
                  {"p_value": 0.0001, "alpha": 0.05, "effect_direction_confirmed": True,
                   "raw_data": {"group_a": a, "group_b": [10.0, 10.1, 9.9, 10.2, 10.0, 10.1, 9.95, 10.05]}}),
         "REJECT", "GATE"),
        ("PASSAGE A: CDS calibration result RE-DERIVES from raw signal",
         _payload("a1", "Sample concentration is 50.0 units", "financial_metric_claim",
                  {"reported_value": 50.0, "reference_value": 50.0, "tolerance": 1.0, "metric_period_match": True,
                   "computation": {"operation": "linear_calibration",
                                   "inputs": {"signal": 105.0, "intercept": 5.0, "slope": 2.0},
                                   "reported_value": 50.0, "tolerance": 0.01}}),
         "ACCEPT", "GATE"),
        ("PASSAGE A FRAUD: reported value does NOT re-derive from raw signal",
         _payload("a2", "Sample concentration is 50.0 units", "financial_metric_claim",
                  {"reported_value": 50.0, "reference_value": 50.0, "tolerance": 1.0, "metric_period_match": True,
                   "computation": {"operation": "linear_calibration",
                                   "inputs": {"signal": 200.0, "intercept": 5.0, "slope": 2.0},
                                   "reported_value": 50.0, "tolerance": 0.01}}),
         "REJECT", "GATE"),
        ("PASSAGE B: ADaM re-derives from SDTM in a pinned env",
         _payload("b1", "Derived change-from-baseline dataset", "financial_metric_claim",
                  {"reported_value": 2.0, "reference_value": 2.0, "tolerance": 1.0, "metric_period_match": True,
                   "environment": {"language": "R", "version": "4.3.1", "os": "linux-x86_64", "locale": "C.UTF-8", "seed": 42},
                   "derivation": {
                       "source": [{"AVAL": 10.0, "BASE": 8.0}, {"AVAL": 12.0, "BASE": 7.0}],
                       "rules": {"CHG": {"operation": "expression", "expression": "AVAL - BASE"}},
                       "submitted": [{"CHG": 2.0}, {"CHG": 5.0}], "tolerance": 0.001}}),
         "ACCEPT", "GATE"),
        ("PASSAGE B FRAUD: a submitted ADaM row does NOT re-derive",
         _payload("b2", "Derived change-from-baseline dataset", "financial_metric_claim",
                  {"reported_value": 2.0, "reference_value": 2.0, "tolerance": 1.0, "metric_period_match": True,
                   "environment": {"language": "R", "version": "4.3.1", "os": "linux-x86_64", "locale": "C.UTF-8", "seed": 42},
                   "derivation": {
                       "source": [{"AVAL": 10.0, "BASE": 8.0}, {"AVAL": 12.0, "BASE": 7.0}],
                       "rules": {"CHG": {"operation": "expression", "expression": "AVAL - BASE"}},
                       "submitted": [{"CHG": 2.0}, {"CHG": 99.0}], "tolerance": 0.001}}),
         "REJECT", "GATE"),
        ("PASSAGE B: re-derivation in an UNPINNED env -> attest only",
         _payload("b3", "Derived change-from-baseline dataset", "financial_metric_claim",
                  {"reported_value": 2.0, "reference_value": 2.0, "tolerance": 1.0, "metric_period_match": True,
                   "environment": {"language": "R", "os": "linux", "locale": "C.UTF-8"},
                   "derivation": {
                       "source": [{"AVAL": 10.0, "BASE": 8.0}],
                       "rules": {"CHG": {"operation": "expression", "expression": "AVAL - BASE"}},
                       "submitted": [{"CHG": 2.0}], "tolerance": 0.001}}),
         "HOLD", "ATTEST"),
        ("PASSAGE B: registry-posted figure diverges from re-derived -> reconcile",
         _payload("b4", "Primary endpoint result", "financial_metric_claim",
                  {"reported_value": 5.0, "reference_value": 5.0, "tolerance": 1.0, "metric_period_match": True,
                   "registry": {"posted_value": 7.2, "rederived_value": 5.0, "tolerance": 0.1, "source_id": "NCT01234567"}}),
         "HOLD", "GATE"),
        ("PASSAGE A v2: peak area RE-DERIVES from raw signal (auto integration)",
         _payload("v1", "Peak area is 20.0", "financial_metric_claim",
                  {"reported_value": 1.0, "reference_value": 1.0, "tolerance": 1.0, "metric_period_match": True,
                   "integration": {"signal": {"time": [0, 1, 2, 3, 4], "response": [0, 5, 10, 5, 0]},
                                   "baseline_start": 0, "baseline_end": 4, "reported_area": 20.0, "tolerance": 0.1}}),
         "ACCEPT", "GATE"),
        ("PASSAGE A v2: MANUAL re-integration diverges, UNJUSTIFIED -> hold",
         _payload("v2", "Peak area is 35.0", "financial_metric_claim",
                  {"reported_value": 1.0, "reference_value": 1.0, "tolerance": 1.0, "metric_period_match": True,
                   "integration": {"signal": {"time": [0, 1, 2, 3, 4], "response": [0, 5, 10, 5, 0]},
                                   "baseline_start": 0, "baseline_end": 4, "tolerance": 0.1,
                                   "manual_override": {"area": 35.0}}}),
         "HOLD", "ATTEST"),
        ("PASSAGE A v2: MANUAL re-integration diverges but ATTESTED -> surfaced",
         _payload("v3", "Peak area is 35.0", "financial_metric_claim",
                  {"reported_value": 1.0, "reference_value": 1.0, "tolerance": 1.0, "metric_period_match": True,
                   "integration": {"signal": {"time": [0, 1, 2, 3, 4], "response": [0, 5, 10, 5, 0]},
                                   "baseline_start": 0, "baseline_end": 4, "tolerance": 0.1,
                                   "manual_override": {"area": 35.0, "analyst": "J. Doe", "reason": "manual baseline correction per SOP-17"}}}),
         "ATTEST", "ATTEST"),
        ("ZK: result verified over HIDDEN data (trusted backend)",
         _payload("z1", "Aggregate over private cohort = 42", "financial_metric_claim",
                  {"reported_value": 1.0, "reference_value": 1.0, "tolerance": 1.0, "metric_period_match": True,
                   "zk_proof": {"scheme": "ref-commitment", "verifying_key_id": "capas-ref-commitment",
                                "public_inputs": {"commitment": _commit("phi_dataset_v1", 42.0, "n1"),
                                                  "claimed_output": 42.0, "tolerance": 0},
                                "proof": {"opening": {"input_hash": "phi_dataset_v1", "output": 42.0}, "nonce": "n1"},
                                "statement": "mean(private_cohort)==42"}}),
         "ACCEPT", "GATE"),
        ("ZK: proof present but verifying key UNTRUSTED -> attest",
         _payload("z2", "Aggregate = 42", "financial_metric_claim",
                  {"reported_value": 1.0, "reference_value": 1.0, "tolerance": 1.0, "metric_period_match": True,
                   "zk_proof": {"scheme": "groth16", "verifying_key_id": "unregistered-vk-xyz",
                                "public_inputs": {"claimed_output": 42.0}, "proof": {"a": "..."}}}),
         "HOLD", "ATTEST"),
        ("ZK: proof FAILS verification (output not bound) -> reject",
         _payload("z3", "Aggregate = 99", "financial_metric_claim",
                  {"reported_value": 1.0, "reference_value": 1.0, "tolerance": 1.0, "metric_period_match": True,
                   "zk_proof": {"scheme": "ref-commitment", "verifying_key_id": "capas-ref-commitment",
                                "public_inputs": {"commitment": _commit("phi_dataset_v1", 42.0, "n1"),
                                                  "claimed_output": 99.0, "tolerance": 0},
                                "proof": {"opening": {"input_hash": "phi_dataset_v1", "output": 42.0}, "nonce": "n1"}}}),
         "REJECT", "GATE"),
        ("ZK CIRCUIT (R1CS): calibration witness SATISFIES the circuit",
         _payload("c1", "Sample concentration is 50.0", "financial_metric_claim",
                  {"reported_value": 1.0, "reference_value": 1.0, "tolerance": 1.0, "metric_period_match": True,
                   "zk_proof": {"scheme": "r1cs", "verifying_key_id": "capas-r1cs",
                                "statement": {"circuit": {"operation": "linear_calibration"}, "output": "x"},
                                "public_inputs": {"claimed_output": 50.0,
                                                  "public": {"signal": 105.0, "intercept": 5.0, "slope": 2.0}},
                                "proof": {"witness": {"signal": 105.0, "intercept": 5.0, "slope": 2.0, "x": 50.0}}}}),
         "ACCEPT", "GATE"),
        ("ZK CIRCUIT (R1CS): tampered witness does NOT satisfy -> reject",
         _payload("c2", "Sample concentration is 99.0", "financial_metric_claim",
                  {"reported_value": 1.0, "reference_value": 1.0, "tolerance": 1.0, "metric_period_match": True,
                   "zk_proof": {"scheme": "r1cs", "verifying_key_id": "capas-r1cs",
                                "statement": {"circuit": {"operation": "linear_calibration"}, "output": "x"},
                                "public_inputs": {"claimed_output": 99.0,
                                                  "public": {"signal": 105.0, "intercept": 5.0, "slope": 2.0}},
                                "proof": {"witness": {"signal": 105.0, "intercept": 5.0, "slope": 2.0, "x": 99.0}}}}),
         "REJECT", "GATE"),
        ("QUANTUM: Bell-state P(00)=0.5 RE-SIMULATES (Clifford, below frontier)",
         _payload("q1", "Bell state P(00)=0.5", "financial_metric_claim",
                  {"reported_value": 1.0, "reference_value": 1.0, "tolerance": 1.0, "metric_period_match": True,
                   "quantum_circuit": {"qubits": 2, "gates": [{"gate": "h", "qubits": [0]}, {"gate": "cx", "qubits": [0, 1]}],
                                       "claim": {"type": "probability", "bitstring": "00", "value": 0.5, "tolerance": 1e-6}}}),
         "ACCEPT", "GATE"),
        ("QUANTUM FRAUD: claimed P(00)=0.9 contradicts re-simulation",
         _payload("q2", "Bell state P(00)=0.9", "financial_metric_claim",
                  {"reported_value": 1.0, "reference_value": 1.0, "tolerance": 1.0, "metric_period_match": True,
                   "quantum_circuit": {"qubits": 2, "gates": [{"gate": "h", "qubits": [0]}, {"gate": "cx", "qubits": [0, 1]}],
                                       "claim": {"type": "probability", "bitstring": "00", "value": 0.9, "tolerance": 1e-6}}}),
         "REJECT", "GATE"),
        ("QUANTUM: beyond the magic frontier (n=40, t=50) -> attest, not faked",
         _payload("q3", "Large quantum claim", "financial_metric_claim",
                  {"reported_value": 1.0, "reference_value": 1.0, "tolerance": 1.0, "metric_period_match": True,
                   "quantum_circuit": {"qubits": 40, "gates": [{"gate": "t", "qubits": [i % 40]} for i in range(50)],
                                       "claim": {"type": "probability", "bitstring": "0" * 40, "value": 0.1}}}),
         "HOLD", "ATTEST"),
        ("ATTESTED: causal all-true WITH signed provenance",
         _payload("s4", "intervention X causes outcome Y", "causal_mechanism_claim",
                  {"intervention_or_natural_experiment": True, "temporal_order_established": True,
                   "confounders_controlled": True, "mechanism_evidence_present": True,
                   "registry_id": "NCT01234567", "signed_attestation": "sha256:deadbeef"}),
         "ATTEST", "ATTEST"),
    ]

    print(f"(re-derivation engine: {'scipy' if capas_verify._HAS_SCIPY else 'fallback'}; true_p of fixture = {true_p:.2e})\n")
    rows = []
    all_ok = True
    for label, payload, exp_verdict, exp_scope in cases:
        r = capas_verify.verify(payload)
        v, sc, tier = r["verified_verdict"], r["scope"], r["verification_tier"]
        # "ATTEST" expected verdict means: verdict stands (not rejected) AND scope==ATTEST
        verdict_ok = (sc == "ATTEST" and v not in ("REJECT",)) if exp_verdict == "ATTEST" else (v == exp_verdict)
        scope_ok = sc == exp_scope
        ok = verdict_ok and scope_ok
        all_ok &= ok
        rows.append((label, r["base_gate_verdict"], v, sc, tier, "✅" if ok else "❌"))

    w = max(len(r[0]) for r in rows)
    print(f"{'case'.ljust(w)} | base   | verified| scope  | tier")
    print("-" * (w + 40))
    for label, base, v, sc, tier, mark in rows:
        print(f"{label.ljust(w)} | {base:<6} | {v:<7} | {sc:<6} | {tier:<10} {mark}")
    print()
    if all_ok:
        print("PROOF-CARRYING VERIFICATION: all cases pass ✅")
        return 0
    print("PROOF-CARRYING VERIFICATION: FAILURES ❌")
    return 1


if __name__ == "__main__":
    raise SystemExit(run())
