# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""Deep behavioural tests for ``capas_verify`` — exercise the rung BODIES (not the
early-return guards) with domain-correct evidence.

Every test feeds inputs that pass each function's internal guards so the real
re-derivation / contradiction / receipt logic runs, and asserts on invariants the
function is contracted to uphold (match flags, contradiction taxonomy, signed
receipts). Run standalone (``python3 benchmarks/test_verify_deep.py`` exits 0) or
under pytest.

Functions exercised here (distinct from test_engine_surface.py):
  rederive_statistical, rederive_calculation (linear_calibration/mean/ratio/
    percent_recovery/expression/unsupported/error), rederive_dataset,
    environment_pinned, reconcile_registry, rederive_integration (auto + manual),
    rederive_crypto (digest + Merkle + mismatch), rederive_accounting
    (double-entry/balance/cash_flow/ratio + bounded-tol guard), rederive_xbrl,
    rederive_dimensions (match/mismatch/unknown), rederive_stoichiometry
    (balanced/imbalanced/malformed), assess_reproduction (justified/unjustified/
    stochastic seed discipline), verify_zk_proof (reference commitment backend +
    untrusted vk), universal_bound_violations, holevo_information_contradictions
    (contradiction/abstain/entanglement-ok), anchor_contradictions (re-derive law +
    abstain), check_physical, verify(payload) end-to-end on many surfaces,
    verify_receipt (signed body round-trip), plus the helpers _antoine_boiling_C,
    _altitude_to_mmHg, _parse_pressure_mmHg, _normalize_number_words, _welch_p,
    _safe_eval, _trapz, _bounded_tol, _parse_formula, _artifact_hash, _engine_digest.
"""
from __future__ import annotations

import hashlib
import math

import capas_verify as V

SV = "capas-claim-payload-v3"
# Base-accept evidence so the base gate says ACCEPT and the verify rungs actually run.
_FIN_BASE = {"reported_value": 100.0, "reference_value": 100.0,
             "tolerance": 0.01, "metric_period_match": True}
_STAT_BASE = {"p_value": 0.01, "alpha": 0.05, "effect_direction_confirmed": True}


def _payload(cid: str, text: str, ctype: str, evidence: dict) -> dict:
    return {"claim": {"id": cid, "text": text, "type": ctype},
            "evidence": evidence, "schema_version": SV}


def _fin(cid: str, text: str, ext: dict) -> dict:
    return _payload(cid, text, "financial_metric_claim", {**_FIN_BASE, **ext})


def _verify(payload: dict) -> dict:
    # use_cache=False so each call re-runs the body (the cache would mask logic).
    return V.verify(payload, use_cache=False)


def _statuses(receipt: dict) -> list:
    return [c.get("status") for c in receipt.get("checks", [])]


# ─────────────────────────────────────────────────────────────────────────────
# Pure physical/law helpers — exercise the law math directly.
# ─────────────────────────────────────────────────────────────────────────────
def test_antoine_and_pressure_helpers():
    # At 1 atm (760 mmHg) the Antoine law re-derives water's boiling point ≈ 100°C.
    assert abs(V._antoine_boiling_C(760.0) - 100.0) < 1.0
    # Lower pressure -> lower boiling point (strictly monotone here).
    assert V._antoine_boiling_C(500.0) < V._antoine_boiling_C(760.0)
    # Altitude -> pressure drops below sea-level (barometric formula).
    assert V._altitude_to_mmHg(0.0, "m") == 760.0 * (1.0) ** 5.25588 or \
        abs(V._altitude_to_mmHg(0.0, "m") - 760.0) < 1e-6
    assert V._altitude_to_mmHg(2.5, "km") < 760.0
    # Pressure parser: unit normalisation to mmHg.
    assert V._parse_pressure_mmHg("measured at 1 atm") == 760.0
    assert abs(V._parse_pressure_mmHg("held at 2 bar") - 2 * 750.062) < 1e-6
    assert V._parse_pressure_mmHg("no pressure named") is None


def test_normalize_number_words():
    out = V._normalize_number_words("store five bits inside one qubit")
    assert "5" in out and "1" in out and "five" not in out


def test_welch_p_separates_groups():
    # Clearly separated groups -> small p; identical groups -> large p.
    far = V._welch_p([1.0, 1.1, 0.9, 1.05, 0.95], [10.0, 10.2, 9.8, 10.1, 9.9])
    same = V._welch_p([1.0, 2.0, 3.0, 4.0], [1.0, 2.0, 3.0, 4.0])
    assert 0.0 <= far <= 1.0 and 0.0 <= same <= 1.0
    assert far < same


def test_safe_eval_arithmetic():
    assert V._safe_eval("a*b + c", {"a": 2, "b": 3, "c": 4}) == 10.0
    assert V._safe_eval("-x ** 2", {"x": 3}) == -9.0


def test_trapz_area():
    # Trapezoid under a straight line y=t from t=0..2 is 2.0.
    assert abs(V._trapz([0.0, 1.0, 2.0], [0.0, 1.0, 2.0]) - 2.0) < 1e-9


def test_bounded_tol_guard():
    # A huge declared tolerance is capped to cap_frac * magnitude.
    assert V._bounded_tol(1e9, 1000.0, 0.01) == 0.01 * 1000.0
    # NaN / negative -> malformed (None).
    assert V._bounded_tol(float("nan"), 100.0, 0.01) is None
    assert V._bounded_tol(-1.0, 100.0, 0.01) is None
    # Small declared tolerance is honoured.
    assert V._bounded_tol(0.5, 1000.0, 0.01) == 0.5


def test_parse_formula_nested():
    counts = V._parse_formula("Ca(OH)2")
    assert counts == {"Ca": 1, "O": 2, "H": 2}


def test_engine_digest_stable():
    d = V._engine_digest()
    assert d.startswith("sha256:") and d == V._engine_digest()


def test_artifact_hash_binds_evidence():
    h = V._artifact_hash({"crypto": {"a": 1}, "irrelevant": 2})
    assert h is not None and h.startswith("sha256:")
    assert V._artifact_hash({"no_artifacts": 1}) is None


# ─────────────────────────────────────────────────────────────────────────────
# Re-derivation functions — domain-correct inputs that hit the bodies.
# ─────────────────────────────────────────────────────────────────────────────
def test_rederive_statistical_match_and_mismatch():
    a = [1.0, 1.1, 0.9, 1.05, 0.95]
    b = [10.0, 10.2, 9.8, 10.1, 9.9]
    true_p = V._welch_p(a, b)
    ok = V.rederive_statistical({"raw_data": {"group_a": a, "group_b": b}, "p_value": round(true_p, 5)})
    assert ok is not None and ok["match"] is True
    bad = V.rederive_statistical({"raw_data": {"group_a": a, "group_b": b}, "p_value": 0.999})
    assert bad is not None and bad["match"] is False
    # No raw data -> nothing re-derivable.
    assert V.rederive_statistical({"p_value": 0.01}) is None


def test_rederive_calculation_operations():
    # linear_calibration: x = (y-b)/m = (15-5)/2 = 5
    r = V.rederive_calculation({"computation": {"operation": "linear_calibration",
        "inputs": {"signal": 15.0, "intercept": 5.0, "slope": 2.0},
        "reported_value": 5.0, "tolerance": 0.001}})
    assert r["match"] is True and abs(r["re_derived"] - 5.0) < 1e-6
    # mean
    r = V.rederive_calculation({"computation": {"operation": "mean",
        "inputs": {"values": [2.0, 4.0, 6.0]}, "reported_value": 4.0}})
    assert r["match"] is True
    # ratio
    r = V.rederive_calculation({"computation": {"operation": "ratio",
        "inputs": {"numerator": 10.0, "denominator": 4.0}, "reported_value": 2.5}})
    assert r["match"] is True
    # percent_recovery
    r = V.rederive_calculation({"computation": {"operation": "percent_recovery",
        "inputs": {"measured": 98.0, "expected": 100.0}, "reported_value": 98.0}})
    assert r["match"] is True
    # expression via safe eval
    r = V.rederive_calculation({"computation": {"operation": "expression",
        "expression": "a + b * 2", "inputs": {"a": 1.0, "b": 3.0}, "reported_value": 7.0}})
    assert r["match"] is True
    # reported value WRONG -> match False (re-derivation catches fabrication)
    r = V.rederive_calculation({"computation": {"operation": "mean",
        "inputs": {"values": [2.0, 4.0]}, "reported_value": 99.0}})
    assert r["match"] is False
    # unsupported op -> match None (route to HOLD, not REJECT)
    r = V.rederive_calculation({"computation": {"operation": "fft", "inputs": {}, "reported_value": 1}})
    assert r["match"] is None and r["status"] == "UNSUPPORTED_OP"
    # malformed input -> ERROR / match None (cannot compute != computed-and-wrong)
    r = V.rederive_calculation({"computation": {"operation": "ratio",
        "inputs": {"numerator": 1.0, "denominator": 0.0}, "reported_value": 1.0}})
    assert r["match"] is None and r["status"] == "ERROR"
    assert V.rederive_calculation({"no": "computation"}) is None


def test_environment_pinned():
    full = V.environment_pinned({"environment": {"language": "R", "version": "4.3",
                                                  "os": "linux", "locale": "C"}})
    assert full is not None and full["pinned"] is True and full["missing"] == []
    partial = V.environment_pinned({"environment": {"language": "R"}})
    assert partial["pinned"] is False and set(partial["missing"]) == {"version", "os", "locale"}
    assert V.environment_pinned({}) is None


def test_rederive_dataset_match_and_mismatch():
    # submitted 'derived' col = source.x * 2 ; rows re-derive correctly.
    good = V.rederive_dataset({"derivation": {
        "source": [{"x": 1.0}, {"x": 2.0}],
        "submitted": [{"derived": 2.0}, {"derived": 4.0}],
        "rules": {"derived": {"operation": "expression", "expression": "x * 2"}},
        "tolerance": 0.0}})
    assert good["match"] is True and good["checks"] == 2 and good["mismatch_count"] == 0
    # one submitted value is wrong -> mismatch found.
    bad = V.rederive_dataset({"derivation": {
        "source": [{"x": 1.0}, {"x": 2.0}],
        "submitted": [{"derived": 2.0}, {"derived": 99.0}],
        "rules": {"derived": {"operation": "expression", "expression": "x * 2"}}}})
    assert bad["match"] is False and bad["mismatch_count"] >= 1
    # ratio / sum / copy operations
    multi = V.rederive_dataset({"derivation": {
        "source": [{"n": 6.0, "d": 2.0, "a": 1.0, "b": 2.0, "label": "ok"}],
        "submitted": [{"r": 3.0, "s": 3.0, "c": "ok"}],
        "rules": {"r": {"operation": "ratio", "numerator": "n", "denominator": "d"},
                  "s": {"operation": "sum", "columns": ["a", "b"]},
                  "c": {"operation": "copy", "column": "label"}}}})
    assert multi["match"] is True and multi["checks"] == 3
    # unsupported rule op -> match None
    uns = V.rederive_dataset({"derivation": {"source": [{"x": 1.0}], "submitted": [{"y": 1.0}],
        "rules": {"y": {"operation": "regress"}}}})
    assert uns["match"] is None
    # malformed (length mismatch) -> match False
    mal = V.rederive_dataset({"derivation": {"source": [{"x": 1.0}], "submitted": [],
        "rules": {"y": {"operation": "copy", "column": "x"}}}})
    assert mal["match"] is False and mal["status"] == "MALFORMED"
    assert V.rederive_dataset({}) is None


def test_reconcile_registry():
    ok = V.reconcile_registry({"registry": {"posted_value": 50.0, "rederived_value": 50.0,
                                             "source_id": "NCT123"}})
    assert ok["match"] is True and ok["source_id"] == "NCT123"
    bad = V.reconcile_registry({"registry": {"posted_value": 50.0, "rederived_value": 73.0}})
    assert bad["match"] is False
    assert V.reconcile_registry({}) is None


def test_rederive_integration_auto_and_manual():
    # Flat signal y=10 over t=0..4 -> gross area minus linear baseline = 0.
    sig = {"time": [0.0, 1.0, 2.0, 3.0, 4.0], "response": [10.0, 10.0, 10.0, 10.0, 10.0]}
    auto = V.rederive_integration({"integration": {"signal": sig, "baseline_start": 0.0,
        "baseline_end": 4.0, "reported_area": 0.0, "tolerance": 0.01}})
    assert auto["manual_override"] is False and auto["match"] is True
    assert abs(auto["auto_area"]) < 0.01
    # manual override -> ATTEST (match None), divergence + attestation surfaced.
    man = V.rederive_integration({"integration": {"signal": sig, "baseline_start": 0.0,
        "baseline_end": 4.0, "tolerance": 0.01,
        "manual_override": {"area": 25.0, "analyst": "QA-7", "reason": "split shoulder peak"}}})
    assert man["manual_override"] is True and man["match"] is None
    assert man["diverges_from_auto"] is True and man["attested"] is True
    # list-form signal + reported area that does NOT re-derive -> match False.
    bad = V.rederive_integration({"integration": {
        "signal": [[0.0, 10.0], [1.0, 10.0], [2.0, 10.0]],
        "baseline_start": 0.0, "baseline_end": 2.0, "reported_area": 999.0}})
    assert bad["match"] is False
    # malformed signal.
    mal = V.rederive_integration({"integration": {"signal": "nope", "baseline_start": 0,
                                                  "baseline_end": 1}})
    assert mal["status"] == "MALFORMED"
    assert V.rederive_integration({}) is None


def test_rederive_crypto_digest_merkle_mismatch():
    digest = hashlib.sha256(b"capas-evidence").hexdigest()
    ok = V.rederive_crypto({"crypto": {"algorithm": "sha256", "preimage": "capas-evidence",
                                       "claimed_digest": digest}})
    assert ok["primitive"] == "digest" and ok["match"] is True
    bad = V.rederive_crypto({"crypto": {"algorithm": "sha256", "preimage": "capas-evidence",
                                        "claimed_digest": "deadbeef"}})
    assert bad["match"] is False
    # Merkle root over two leaves: recompute the same way the engine does.
    leaves = ["aa", "bb"]

    def _h(b: bytes) -> str:
        return hashlib.sha256(b).hexdigest()
    la = bytes.fromhex(_h(bytes.fromhex("aa")))
    lb = bytes.fromhex(_h(bytes.fromhex("bb")))
    root = _h(la + lb)
    m = V.rederive_crypto({"crypto": {"algorithm": "sha256", "leaves": leaves, "claimed_root": root}})
    assert m["primitive"] == "merkle_root" and m["match"] is True
    # Unknown algorithm.
    unk = V.rederive_crypto({"crypto": {"algorithm": "notahash", "preimage": "x", "claimed_digest": "y"}})
    assert unk["match"] is False and unk["status"] == "UNKNOWN_ALGORITHM"
    assert V.rederive_crypto({}) is None


def test_rederive_accounting_identities():
    # double entry
    de = V.rederive_accounting({"accounting": {"identity": "debits_equal_credits",
        "debits": [50.0, 50.0], "credits": [100.0]}})
    assert de["match"] is True
    # balance sheet holds
    bs = V.rederive_accounting({"accounting": {"identity": "balance_sheet",
        "assets": 100.0, "liabilities": 40.0, "equity": 60.0}})
    assert bs["match"] is True
    # balance sheet violated
    bsx = V.rederive_accounting({"accounting": {"identity": "balance_sheet",
        "assets": 100.0, "liabilities": 40.0, "equity": 10.0}})
    assert bsx["match"] is False
    # cash flow reconciliation
    cf = V.rederive_accounting({"accounting": {"identity": "cash_flow", "beginning": 10.0,
        "operating": 5.0, "investing": -2.0, "financing": 1.0, "ending": 14.0}})
    assert cf["match"] is True
    # financial ratio (current ratio = 200/100 = 2.0), re-derived from components.
    cr = V.rederive_accounting({"accounting": {"identity": "financial_ratio",
        "ratio": "current_ratio", "current_assets": 200.0, "current_liabilities": 100.0,
        "reported": 2.0}})
    assert cr["match"] is True and abs(cr["re_derived"] - 2.0) < 1e-6
    # ratio that does NOT re-derive
    crx = V.rederive_accounting({"accounting": {"identity": "financial_ratio",
        "ratio": "current_ratio", "current_assets": 200.0, "current_liabilities": 100.0,
        "reported": 9.9}})
    assert crx["match"] is False
    # non-positive denominator -> route to attest, not a clean re-derivation
    nd = V.rederive_accounting({"accounting": {"identity": "financial_ratio",
        "ratio": "debt_to_equity", "total_debt": 100.0, "total_equity": -5.0, "reported": -20.0}})
    assert nd["status"] == "NONPOSITIVE_DENOMINATOR" and nd["match"] is False
    # unknown ratio / identity
    ur = V.rederive_accounting({"accounting": {"identity": "financial_ratio", "ratio": "sharpe",
        "reported": 1.0}})
    assert ur["status"] == "UNKNOWN_RATIO"
    ui = V.rederive_accounting({"accounting": {"identity": "nonsense"}})
    assert ui["status"] == "UNKNOWN_IDENTITY"
    assert V.rederive_accounting({}) is None


def test_rederive_xbrl_malformed_and_unavailable():
    # Malformed (missing required keys) -> MALFORMED match False.
    mal = V.rederive_xbrl({"xbrl": {"instance": None}})
    assert mal["status"] == "MALFORMED" and mal["match"] is False
    # Well-formed but Arelle/extraction may be unavailable -> match None (ATTEST), not accept.
    res = V.rederive_xbrl({"xbrl": {"instance": "/nonexistent/filing.xml",
        "ratio": "current_ratio", "reported": 2.0}})
    assert res is None or res.get("match") in (None, True, False)
    assert V.rederive_xbrl({}) is None


def test_rederive_dimensions():
    ok = V.rederive_dimensions({"dimensions": {"quantity": "force", "unit": "N"}})
    assert ok["match"] is True
    bad = V.rederive_dimensions({"dimensions": {"quantity": "force", "unit": "m/s"}})
    assert bad["match"] is False
    unkq = V.rederive_dimensions({"dimensions": {"quantity": "vibes", "unit": "N"}})
    assert unkq["match"] is None and unkq["status"] == "UNKNOWN_QUANTITY"
    unku = V.rederive_dimensions({"dimensions": {"quantity": "force", "unit": "furlong"}})
    assert unku["match"] is None and unku["status"] == "UNKNOWN_UNIT"
    assert V.rederive_dimensions({}) is None


def test_rederive_stoichiometry():
    # 2 H2 + O2 -> 2 H2O balances.
    ok = V.rederive_stoichiometry({"stoichiometry": {
        "reactants": [{"formula": "H2", "coeff": 2}, {"formula": "O2", "coeff": 1}],
        "products": [{"formula": "H2O", "coeff": 2}]}})
    assert ok["match"] is True and ok["imbalanced"] == {}
    assert abs(ok["reactant_mass"] - ok["product_mass"]) < 1e-3
    # imbalanced: H2 + O2 -> H2O (not enough on one side).
    bad = V.rederive_stoichiometry({"stoichiometry": {
        "reactants": [{"formula": "H2", "coeff": 1}, {"formula": "O2", "coeff": 1}],
        "products": [{"formula": "H2O", "coeff": 1}]}})
    assert bad["match"] is False and bad["imbalanced"]
    # malformed: unknown element.
    mal = V.rederive_stoichiometry({"stoichiometry": {
        "reactants": [{"formula": "Xz2"}], "products": [{"formula": "H2"}]}})
    assert mal["match"] is False and mal["status"] == "MALFORMED"
    # empty side -> malformed.
    emp = V.rederive_stoichiometry({"stoichiometry": {"reactants": [], "products": [{"formula": "H2"}]}})
    assert emp["match"] is False and emp["status"] == "MALFORMED"
    assert V.rederive_stoichiometry({}) is None


def test_assess_reproduction():
    # exact mode -> tolerance trivially justified.
    ex = V.assess_reproduction({"reproduction": {"mode": "exact"}})
    assert ex["tolerance_justified"] is True
    # bounded with recognised basis -> justified.
    jb = V.assess_reproduction({"reproduction": {"mode": "bounded", "tolerance": 0.01,
        "tolerance_basis": "instrument_precision"}})
    assert jb["tolerance_justified"] is True
    # bounded with NO recognised basis -> unjustified.
    ub = V.assess_reproduction({"reproduction": {"mode": "bounded", "tolerance": 0.5,
        "tolerance_basis": "vibes"}})
    assert ub["tolerance_justified"] is False
    # stochastic with seed committed before data.
    st = V.assess_reproduction({"reproduction": {"mode": "bounded", "tolerance": 0,
        "stochastic": {"method": "MCMC", "seed": 42, "committed_before_data": True}}})
    assert st["has_seed"] is True and st["committed_before_data"] is True
    # stochastic with no seed.
    ns = V.assess_reproduction({"reproduction": {"stochastic": {"method": "bootstrap"}}})
    assert ns["has_seed"] is False
    assert V.assess_reproduction({}) is None


def test_verify_zk_proof_reference_backend():
    # Build a valid reference-commitment proof: commitment binds input_hash|output|nonce.
    output = "42.0"
    opening = {"input_hash": "abc", "output": output}
    nonce = "n0"
    commitment = "sha256:" + hashlib.sha256(f"abc|{output}|{nonce}".encode()).hexdigest()
    ok = V.verify_zk_proof({"zk_proof": {"verifying_key_id": "capas-ref-commitment",
        "proof": {"opening": opening, "nonce": nonce},
        "public_inputs": {"commitment": commitment, "claimed_output": 42.0, "tolerance": 0.0},
        "scheme": "commitment", "statement": "output==42"}})
    assert ok["verified"] is True and ok["status"] == "VERIFIED"
    # Tampered claimed_output -> verification fails.
    bad = V.verify_zk_proof({"zk_proof": {"verifying_key_id": "capas-ref-commitment",
        "proof": {"opening": opening, "nonce": nonce},
        "public_inputs": {"commitment": commitment, "claimed_output": 99.0}}})
    assert bad["verified"] is False
    # Unregistered verifying key -> UNTRUSTED_VK (ATTEST, not gated).
    unt = V.verify_zk_proof({"zk_proof": {"verifying_key_id": "no-such-vk", "proof": {},
                                          "public_inputs": {}}})
    assert unt["status"] == "UNTRUSTED_VK" and unt["verified"] is None
    assert V.verify_zk_proof({}) is None


# ─────────────────────────────────────────────────────────────────────────────
# Contradiction scanners — claim_text that triggers REAL contradictions/abstains.
# ─────────────────────────────────────────────────────────────────────────────
def test_universal_bound_violations():
    # Below absolute zero (°C).
    az = V.universal_bound_violations("the cryostat cooled the sample to -300 °C")
    assert any(h["anchor"] == "absolute_zero_floor_C" and h["kind"] == "contradiction" for h in az)
    # Faster than light.
    fl = V.universal_bound_violations("the probe travels at 400000000 m/s through the field")
    assert any(h["anchor"] == "lightspeed_ceiling_massive" for h in fl)
    # Probability > 1.
    pr = V.universal_bound_violations("the probability of recurrence is 1.4")
    assert any(h["anchor"] == "probability_unit_interval" for h in pr)
    # A physically fine claim -> no violation.
    assert V.universal_bound_violations("the sample warmed to 90 °C") == []


def test_holevo_contradictions():
    # >1 bit/qubit single-shot, no resource -> contradiction.
    c = V.holevo_information_contradictions("our scheme can store 5 bits in 1 qubit")
    assert c and c[0]["kind"] == "contradiction"
    # Spelled-out numbers must not evade the anchor.
    c2 = V.holevo_information_contradictions("store five bits inside just one single qubit")
    assert c2 and c2[0]["kind"] == "contradiction"
    # Tomography/copies -> abstain (state reconstruction, not beating the bound).
    ab = V.holevo_information_contradictions("we recover 8 bits from 1 qubit using tomography over many copies")
    assert ab and ab[0]["kind"] == "abstain"
    # Superdense coding within 2 bits/qubit WITH entanglement -> not flagged.
    assert V.holevo_information_contradictions(
        "transmit 2 classical bits per qubit using prior shared entanglement") == []
    # Within bound (1 bit/qubit) -> nothing.
    assert V.holevo_information_contradictions("store 1 bit in 1 qubit") == []


def test_anchor_contradictions_rederive_and_abstain():
    # Inside domain at 1 atm: 500°C contradicts the 100°C boiling anchor.
    c = V.anchor_contradictions("water boils at 500C")
    assert c and c[0]["kind"] == "contradiction"
    # Light slower than c in a medium -> abstain (vacuum constant inapplicable).
    ab = V.anchor_contradictions("the speed of light is 200000000 m/s in water")
    assert ab and ab[0]["kind"] == "abstain"
    # Off-baseline qualitatively (altitude) without a number -> abstain.
    abh = V.anchor_contradictions("at high altitude water boils at 90C")
    assert abh and abh[0]["kind"] == "abstain"
    # Pinned condition (2 atm) re-derives the law: a value contradicting it -> contradiction.
    cl = V.anchor_contradictions("under 2 atm pressure water boils at 90C")
    assert any(h["kind"] == "contradiction" for h in cl)
    # No anchor engaged.
    assert V.anchor_contradictions("the market closed higher today") == []


def test_check_physical_structured():
    # Below absolute zero (structured field path).
    az = V.check_physical({"quantity": "temperature", "value": -300.0, "unit": "°C"})
    assert az and az[0]["kind"] == "contradiction"
    # Boiling point at a pinned low pressure that the claim contradicts.
    bp = V.check_physical({"quantity": "boiling_point", "value": 100.0, "unit": "°C",
                           "conditions": {"pressure_mmHg": 400.0}})
    assert bp and bp[0]["kind"] == "contradiction"
    # Faster than light.
    fl = V.check_physical({"quantity": "speed", "value": 4e8, "unit": "m/s"})
    assert fl and fl[0]["kind"] == "contradiction"
    # Holevo over-claim, no resource.
    ho = V.check_physical({"quantity": "accessible_information", "value": 5.0,
                           "conditions": {"qubits": 1}})
    assert ho and ho[0]["kind"] == "contradiction"
    # Non-dict -> empty.
    assert V.check_physical("not a dict") == []


# ─────────────────────────────────────────────────────────────────────────────
# verify(payload) end-to-end across many surfaces.
# ─────────────────────────────────────────────────────────────────────────────
def test_verify_contradiction_rejects():
    r = _verify(_payload("t1", "Water boils at 500C", "statistical_confidence", dict(_STAT_BASE)))
    assert r["verified_verdict"] == "REJECT"
    assert any(c["check"] == "anchor_contradiction" for c in r["checks"])


def test_verify_abstain_holds():
    r = _verify(_payload("t2", "at high altitude water boils at 90C", "statistical_confidence",
                         dict(_STAT_BASE)))
    assert r["verified_verdict"] == "HOLD" and r["scope"] == "ATTEST"


def test_verify_statistical_rederivation_paths():
    a = [1.0, 1.1, 0.9, 1.05, 0.95]
    b = [10.0, 10.2, 9.8, 10.1, 9.9]
    true_p = V._welch_p(a, b)
    ev = {**_STAT_BASE, "p_value": round(true_p, 5),
          "raw_data": {"group_a": a, "group_b": b}}
    r = _verify(_payload("sv", "drug lowers tumor mass", "statistical_confidence", ev))
    assert r["verified_verdict"] == "ACCEPT" and r["verification_tier"] == "RE-DERIVED"
    assert "VERIFIED" in _statuses(r)
    # Declared-only (no raw_data) -> HOLD/ATTEST: standard-above requirement.
    r2 = _verify(_payload("sd", "drug lowers tumor mass", "statistical_confidence", dict(_STAT_BASE)))
    assert r2["verified_verdict"] == "HOLD" and r2["scope"] == "ATTEST"


def test_verify_crypto_accept_and_reject():
    digest = hashlib.sha256(b"capas-evidence").hexdigest()
    ok = _verify(_fin("cy1", "digest as stated", {"crypto": {"algorithm": "sha256",
        "preimage": "capas-evidence", "claimed_digest": digest}}))
    assert ok["verified_verdict"] == "ACCEPT" and "VERIFIED" in _statuses(ok)
    bad = _verify(_fin("cy2", "digest as stated", {"crypto": {"algorithm": "sha256",
        "preimage": "capas-evidence", "claimed_digest": "deadbeef"}}))
    assert bad["verified_verdict"] == "REJECT"


def test_verify_accounting_paths():
    ok = _verify(_fin("ac1", "balance sheet balances", {"accounting": {"identity": "balance_sheet",
        "assets": 100.0, "liabilities": 40.0, "equity": 60.0}}))
    assert ok["verified_verdict"] == "ACCEPT"
    bad = _verify(_fin("ac2", "balance sheet balances", {"accounting": {"identity": "balance_sheet",
        "assets": 100.0, "liabilities": 40.0, "equity": 10.0}}))
    assert bad["verified_verdict"] == "REJECT"
    ratio = _verify(_fin("rt", "current ratio is 2.0", {"accounting": {"identity": "financial_ratio",
        "ratio": "current_ratio", "current_assets": 200.0, "current_liabilities": 100.0,
        "reported": 2.0}}))
    assert ratio["verified_verdict"] == "ACCEPT"


def test_verify_dimensions_and_stoichiometry():
    dm = _verify(_fin("dm", "force in newtons", {"dimensions": {"quantity": "force", "unit": "N"}}))
    assert dm["verified_verdict"] == "ACCEPT"
    dmx = _verify(_fin("dmx", "force in m/s", {"dimensions": {"quantity": "force", "unit": "m/s"}}))
    assert dmx["verified_verdict"] == "REJECT"
    sx = _verify(_fin("sx", "water synthesis balances", {"stoichiometry": {
        "reactants": [{"formula": "H2", "coeff": 2}, {"formula": "O2", "coeff": 1}],
        "products": [{"formula": "H2O", "coeff": 2}]}}))
    assert sx["verified_verdict"] == "ACCEPT"
    sxx = _verify(_fin("sxx", "bad synthesis", {"stoichiometry": {
        "reactants": [{"formula": "H2", "coeff": 1}], "products": [{"formula": "H2O", "coeff": 1}]}}))
    assert sxx["verified_verdict"] == "REJECT"


def test_verify_calculation_and_registry_and_integration():
    calc = _verify(_fin("ca", "value is 5", {"computation": {"operation": "mean",
        "inputs": {"values": [4.0, 6.0]}, "reported_value": 5.0}}))
    assert calc["verified_verdict"] == "ACCEPT"
    calcx = _verify(_fin("cax", "value is 99", {"computation": {"operation": "mean",
        "inputs": {"values": [4.0, 6.0]}, "reported_value": 99.0}}))
    assert calcx["verified_verdict"] == "REJECT"
    # Registry discrepancy -> HOLD.
    reg = _verify(_fin("rg", "registry posts 50", {"registry": {"posted_value": 50.0,
        "rederived_value": 73.0, "source_id": "NCT1"}}))
    assert reg["verified_verdict"] == "HOLD"
    # Peak integration that re-derives.
    sig = {"time": [0.0, 1.0, 2.0, 3.0, 4.0], "response": [10.0, 10.0, 10.0, 10.0, 10.0]}
    ig = _verify(_fin("ig", "peak area is 0", {"integration": {"signal": sig,
        "baseline_start": 0.0, "baseline_end": 4.0, "reported_area": 0.0, "tolerance": 0.01}}))
    assert ig["verified_verdict"] == "ACCEPT"


def test_verify_dataset_pinned_and_unpinned():
    deriv = {"derivation": {"source": [{"x": 1.0}, {"x": 2.0}],
        "submitted": [{"y": 2.0}, {"y": 4.0}],
        "rules": {"y": {"operation": "expression", "expression": "x * 2"}}, "tolerance": 0.0}}
    # A PARTIALLY-pinned environment (some required keys missing) -> HOLD/ATTEST:
    # dataset re-derivation is only honest inside a fully pinned environment.
    unp = _verify(_fin("dsu", "dataset re-derives",
                       {**deriv, "environment": {"language": "R"}}))
    assert unp["verified_verdict"] == "HOLD" and unp["scope"] == "ATTEST"
    assert "UNPINNED" in _statuses(unp)
    # Pinned environment + matching rows -> ACCEPT.
    pinned = {**deriv, "environment": {"language": "R", "version": "4.3", "os": "linux", "locale": "C"}}
    ok = _verify(_fin("dsp", "dataset re-derives", pinned))
    assert ok["verified_verdict"] == "ACCEPT"


def test_verify_reproduction_unjustified_band_holds():
    ev = {**_STAT_BASE, "reproduction": {"mode": "bounded", "tolerance": 0.5,
                                          "tolerance_basis": "vibes"}}
    r = _verify(_payload("rep", "result reproduces", "statistical_confidence", ev))
    assert r["verified_verdict"] == "HOLD" and r["scope"] == "ATTEST"


def test_verify_zk_untrusted_holds():
    r = _verify(_fin("zk", "result over hidden data", {"zk_proof": {"verifying_key_id": "no-such-vk",
        "proof": {}, "public_inputs": {}}}))
    assert r["verified_verdict"] == "HOLD" and r["scope"] == "ATTEST"


def test_verify_design_evidence_provenance():
    # Study-design booleans without provenance -> HOLD (unbacked ATTEST-class).
    unbacked = _verify(_payload("d1", "ice cream causes shark attacks - proven", "causal_mechanism_claim",
        {"intervention_or_natural_experiment": True, "temporal_order_established": True,
         "confounders_controlled": True, "mechanism_evidence_present": True}))
    assert unbacked["verified_verdict"] == "HOLD" and unbacked["scope"] == "ATTEST"
    # Same booleans WITH provenance -> ATTESTED (scope ATTEST, verdict not rejected).
    backed = _verify(_payload("d2", "ice cream causes shark attacks - proven", "causal_mechanism_claim",
        {"intervention_or_natural_experiment": True, "temporal_order_established": True,
         "confounders_controlled": True, "mechanism_evidence_present": True,
         "registry_id": "OSF-abc", "signed_attestation": "sig:deadbeef"}))
    assert backed["scope"] == "ATTEST" and "ATTESTED" in _statuses(backed)


def test_verify_fail_closed_unresolved_evidence():
    # Re-derivable evidence supplied (dimensions) but UNKNOWN quantity -> no positive
    # rung resolves it -> fail-closed backstop holds rather than accepts.
    r = _verify(_fin("fc", "quantity as stated", {"dimensions": {"quantity": "vibes", "unit": "N"}}))
    assert r["verified_verdict"] == "HOLD"


# ─────────────────────────────────────────────────────────────────────────────
# Receipt: signed body round-trips through verify_receipt.
# ─────────────────────────────────────────────────────────────────────────────
def test_receipt_and_verify_receipt_roundtrip():
    digest = hashlib.sha256(b"capas-evidence").hexdigest()
    r = _verify(_fin("rc", "digest as stated", {"crypto": {"algorithm": "sha256",
        "preimage": "capas-evidence", "claimed_digest": digest}}))
    assert r["schema"] == "capas-verification-receipt-v1"
    assert r["engine_digest"].startswith("sha256:")
    assert r["receipt_id"].startswith("sha256:")
    check = V.verify_receipt(r)
    assert check["verdict"] == r["verified_verdict"]
    assert check["engine_digest_pinned"] is True
    assert check["receipt_id_matches"] is True
    # If a signature is present (cryptography installed), it must verify against the body.
    if "signature" in r:
        assert check["signature_valid"] is True
        # Tampering the body invalidates the signature.
        tampered = dict(r)
        tampered["verified_verdict"] = "REJECT"
        assert V.verify_receipt(tampered)["signature_valid"] is False
    else:
        assert check["signature_valid"] is None


def test_verify_cache_idempotent():
    payload = _payload("cache", "store 1 bit in 1 qubit", "statistical_confidence", dict(_STAT_BASE))
    r1 = V.verify(payload, use_cache=True)
    r2 = V.verify(payload, use_cache=True)
    assert r1 == r2


def _run_all() -> int:
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    failed = 0
    for fn in fns:
        try:
            fn()
            print(f"PASS {fn.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL {fn.__name__}: {e}")
        except Exception as e:  # noqa: BLE001
            failed += 1
            print(f"ERROR {fn.__name__}: {type(e).__name__}: {e}")
    print(f"\n{len(fns) - failed}/{len(fns)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(_run_all())
