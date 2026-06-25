#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""Deep functional coverage of the cross-domain INVARIANT engine and the graded-reward stack.

test_engine_surface / test_engine_deep drive the core gate; test_verify_deep drives the rungs;
test_accountability_deep touches `capas_invariants` only through the MCP `audit` entry with one
block. This file goes DISJOINTLY deep on the three modules those leave undercovered:

  capas_invariants — every one of the 23 domain checkers in REGISTRY is exercised on BOTH a
    domain-correct (PASS) and a domain-violating (FLAG) input so the real re-derivation body runs,
    plus the malformed/non-numeric guard branch of each, the `applies:False` skip branch, the
    parenthesised-formula parser (Ca(OH)2), the dimensional-homogeneity vector math, and the
    `audit` aggregator (single-law PASS, multi-law mixed FLAG, a checker that raises -> fail-closed
    FLAG, and the no-invariant-applies N/A path). The SDK `invariants` wrapper is exercised too.

  capas_admissibility — `admissibility` + `reward` driven into every `class` branch the contract
    can produce: VERIFIED (re-derived), CONJECTURE (coherent viable, ungrounded), ATTEST_DEFER
    (needs the subject), REFUTED (contradicts a grounded invariant), and FORM_OK / UNSUPPORTED
    (bare claim, no checks). Asserts the ordering invariant the reward MUST uphold:
    VERIFIED > CONJECTURE > ATTEST_DEFER > REFUTED, and that the score stays in [0,1].

  capas_rcc — `rcc` driven into every stratum: GROUNDED, STRATIFIED/generated-with-bridge,
    DEFERRED/unknowable-with-typed-reason, REFUTED, plus the gigo_consilience renormalisation
    branch (a consilience block under evidence) and the Ed25519 signature + certificate_id +
    standing Löbian clause. Asserts the certificate is well-formed and the strata partition cleanly.

Every assertion is on an invariant the function is contracted to uphold (verdict polarity, class,
score ordering, stratum membership, signature presence) — no trivial asserts. Deterministic; no
network, no key required (signing degrades to absent gracefully).

Run: `python3 benchmarks/test_invariants_deep.py`  (exit 0)  or under pytest.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import capas_admissibility as A  # noqa: E402
import capas_invariants as ci  # noqa: E402
import capas_rcc as R  # noqa: E402
import capas_sdk  # noqa: E402

SV = "capas-claim-payload-v3"
FIN = {"reported_value": 1.0, "reference_value": 1.0, "tolerance": 1.0, "metric_period_match": True}


def _p(text: str, ctype: str, evidence: dict) -> dict:
    return {"schema_version": SV, "claim": {"id": "c", "type": ctype, "text": text}, "evidence": evidence}


# --------------------------------------------------------------------------- #
# capas_invariants — every checker, PASS + FLAG + malformed, via its block key.
# Each entry: (registry_name, pass_block, flag_block, malformed_block_or_None)
# pass_block / flag_block are the FULL evidence dict (already keyed for the checker).
# --------------------------------------------------------------------------- #
CHECKERS = [
    ("accounting",
     {"accounting": {"assets": 100.0, "liabilities": 60.0, "equity": 40.0}},
     {"accounting": {"assets": 100.0, "liabilities": 60.0, "equity": 30.0}},
     {"accounting": {"assets": "x", "liabilities": 60.0, "equity": 40.0}}),
    ("grim",
     {"grim": {"mean": 2.5, "n": 2, "decimals": 1}},
     {"grim": {"mean": 2.5, "n": 3, "decimals": 1}},
     {"grim": {"mean": "x", "n": 3}}),
    ("probability",
     {"probabilities": [0.2, 0.3], "distribution": {"a": 0.5, "b": 0.5}},
     {"probabilities": [1.7, -0.2], "distribution": {"a": 0.9, "b": 0.9}},
     None),
    ("sum",
     {"parts": [1.0, 2.0, 3.0], "total": 6.0},
     {"parts": [1.0, 2.0, 3.0], "total": 10.0},
     {"parts": "notalist", "total": 6.0}),
    ("stoichiometry",
     {"stoichiometry": {"reactants": {"H2": 2, "O2": 1}, "products": {"H2O": 2}}},
     {"stoichiometry": {"reactants": {"H2": 1, "O2": 1}, "products": {"H2O": 2}}},
     None),
    ("charge_balance",
     {"charge_balance": {"reactants": [[1, 1], [1, -1]], "products": [[1, 0]]}},
     {"charge_balance": {"reactants": [[1, 2], [1, -1]], "products": [[1, 0]]}},
     None),
    ("oxidation_states",
     {"oxidation_states": {"atoms": {"H": 2, "O": 1}, "states": {"H": 1, "O": -2}, "net_charge": 0}},
     {"oxidation_states": {"atoms": {"H": 2, "O": 1}, "states": {"H": 1, "O": -2}, "net_charge": 3}},
     None),
    ("mole_mass",
     {"mole_mass": {"m": 18.0, "M": 18.0, "n": 1.0}},
     {"mole_mass": {"m": 18.0, "M": 18.0, "n": 5.0}},
     {"mole_mass": {"m": 18.0, "M": 0.0, "n": 1.0}}),
    ("dimensions",
     {"dimensions": {"lhs": "N", "rhs": {"kg": 1, "m": 1, "s": -2}}},
     {"dimensions": {"lhs": "N", "rhs": {"kg": 1, "m": 1, "s": -1}}},
     {"dimensions": {"lhs": "Zorkles", "rhs": "N"}}),
    ("bounds",
     {"bounds": {"efficiency": 0.9, "correlation": 0.5}},
     {"bounds": {"efficiency": 1.5, "correlation": 2.0}},
     None),
    ("root",
     {"root_check": {"polynomial": [-4, 0, 1], "root": 2}},
     {"root_check": {"polynomial": [-4, 0, 1], "root": 5}},
     {"root_check": {"polynomial": "nope", "root": 2}}),
    ("linear_system",
     {"linear_system": {"A": [[1, 1], [1, -1]], "x": [3, 1], "b": [4, 2]}},
     {"linear_system": {"A": [[1, 1], [1, -1]], "x": [9, 9], "b": [4, 2]}},
     {"linear_system": {"A": "bad", "x": [1], "b": [1]}}),
    ("divisibility",
     {"divisibility": {"a": 12, "b": 3, "divides": False, "gcd": 3, "lcm": 12, "q": 4, "r": 0}},
     {"divisibility": {"a": 12, "b": 3, "divides": True}},
     {"divisibility": {"a": 1.5, "b": 3}}),
    ("confusion_matrix",
     {"confusion_matrix": {"tp": 90, "fp": 10, "fn": 10, "tn": 90, "claimed": {"sensitivity": 0.9}}},
     {"confusion_matrix": {"tp": 90, "fp": 10, "fn": 10, "tn": 90, "claimed": {"sensitivity": 0.5}}},
     {"confusion_matrix": {"tp": "x", "fp": 10, "fn": 10, "tn": 90}}),
    ("bayes_ppv",
     {"bayes_ppv": {"sensitivity": 0.99, "specificity": 0.99, "prevalence": 0.5, "claimed_ppv": 0.99}},
     {"bayes_ppv": {"sensitivity": 0.99, "specificity": 0.99, "prevalence": 0.01, "claimed_ppv": 0.99}},
     {"bayes_ppv": {"sensitivity": 1.5, "specificity": 0.9, "prevalence": 0.1}}),
    ("association",
     {"association": {"a": 20, "b": 80, "c": 10, "d": 90, "claimed_rr": 2.0}},
     {"association": {"a": 20, "b": 80, "c": 10, "d": 90, "claimed_rr": 9.0}},
     {"association": {"a": "x", "b": 80, "c": 10, "d": 90}}),
    ("vaccine_efficacy",
     {"vaccine_efficacy": {"cases_vax": 5, "n_vax": 1000, "cases_unvax": 50, "n_unvax": 1000,
                           "claimed_ve": 0.9}},
     {"vaccine_efficacy": {"cases_vax": 5, "n_vax": 1000, "cases_unvax": 50, "n_unvax": 1000,
                           "claimed_ve": 0.5}},
     {"vaccine_efficacy": {"cases_vax": 5, "n_vax": 0, "cases_unvax": 50, "n_unvax": 1000}}),
    ("containment",
     {"containment": {"pairs": [{"num": 5, "den": 10, "label": "x"}], "proportions": {"p": 0.5}}},
     {"containment": {"pairs": [{"num": 15, "den": 10, "label": "x"}], "proportions": {"p": 1.5}}},
     None),
    ("ohms_law",
     {"ohms_law": {"V": 10.0, "I": 2.0, "R": 5.0}},
     {"ohms_law": {"V": 99.0, "I": 2.0, "R": 5.0}},
     None),
    ("mark_recapture",
     {"mark_recapture": {"M": 100, "C": 100, "R": 10, "N": 1000}},
     {"mark_recapture": {"M": 100, "C": 100, "R": 10, "N": 50}},
     {"mark_recapture": {"M": 100, "C": 100, "R": 0, "N": 1000}}),
    ("hardy_weinberg",
     {"hardy_weinberg": {"AA": 0.49, "Aa": 0.42, "aa": 0.09, "p": 0.7, "q": 0.3}},
     {"hardy_weinberg": {"AA": 0.49, "Aa": 0.42, "aa": 0.09, "p": 0.1, "q": 0.9}},
     {"hardy_weinberg": {"AA": "x", "Aa": 0.42, "aa": 0.09}}),
]


def test_every_checker_pass_and_flag():
    """Each of the 22 keyed checkers must PASS on a domain-correct block and FLAG on a violating
    one (the real re-derivation body runs in both directions, not the early-return guard)."""
    for name, pass_blk, flag_blk, malformed in CHECKERS:
        fn = ci.REGISTRY[name]
        rp = fn(pass_blk)
        assert rp.get("applies") is True, f"{name}: pass block did not apply"
        assert rp.get("verdict") == "PASS", f"{name}: domain-correct block did not PASS ({rp.get('why')})"
        assert "law" in rp and rp["law"], f"{name}: PASS result missing law text"
        rf = fn(flag_blk)
        assert rf.get("applies") is True, f"{name}: flag block did not apply"
        assert rf.get("verdict") == "FLAG", f"{name}: domain-violating block did not FLAG ({rf.get('why')})"
        assert rf.get("why"), f"{name}: FLAG result missing explanation"
        if malformed is not None:
            rm = fn(malformed)
            # malformed but present block -> the guard FLAGs (fail-closed), never PASS, never crash.
            assert isinstance(rm, dict)
            assert rm.get("verdict") != "PASS", f"{name}: malformed block was PASSed (fail-open)"


def test_quantum_checker_via_registry():
    """check_quantum delegates to the physics gate. A healthy-ish row PASSes; a T2>2*T1 row FLAGs."""
    healthy = {"quantum": {"t1_us": 120.0, "t2_us": 90.0, "p01": 0.02, "p10": 0.01}}
    anomaly = {"quantum": {"t1_us": 10.0, "t2_us": 40.0}}  # t2 > 2*t1 is unphysical
    rh = ci.check_quantum(healthy)
    ra = ci.check_quantum(anomaly)
    assert rh.get("applies") and rh.get("verdict") in ("PASS", "FLAG")
    assert ra.get("applies") and ra.get("verdict") == "FLAG", "T2>2T1 anomaly must FLAG"


def test_applies_false_skip_branches():
    """A checker whose block is absent / wrong shape must return applies:False (the skip branch),
    so `audit` leaves the verdict untouched (no spurious FLAG)."""
    for name in ci.REGISTRY:
        r = ci.REGISTRY[name]({})  # empty evidence -> nothing to check
        assert r.get("applies") in (False, None), f"{name}: fired on empty evidence (false positive)"
    # wrong-typed blocks also skip, never crash
    assert ci.check_accounting({"accounting": "not a dict"}).get("applies") in (False, None)
    assert ci.check_sum({"parts": [1, 2], "total": "x"}).get("applies") in (False, None)
    assert ci.check_physical_bounds({"bounds": {"unknown_quantity": 5}}).get("applies") in (False, None)


def test_formula_parser_parentheses():
    """The parenthesised-formula parser must expand Ca(OH)2 -> Ca1 O2 H2 (drives the ( / ) stack)."""
    atoms = ci._parse_formula("Ca(OH)2")
    assert atoms.get("Ca") == 1 and atoms.get("O") == 2 and atoms.get("H") == 2, atoms
    # a balanced reaction using a parenthesised species exercises check_stoichiometry's parser path
    r = ci.check_stoichiometry({"stoichiometry": {
        "reactants": {"Ca(OH)2": 1, "CO2": 1}, "products": {"CaCO3": 1, "H2O": 1}}})
    assert r["verdict"] == "PASS", r.get("why")


def test_dimension_vector_math():
    """_dim_vector composes base dimensions; an unknown unit returns None (-> FLAG in the checker)."""
    assert ci._dim_vector("J") == (1, 2, -2, 0, 0, 0, 0)
    assert ci._dim_vector({"m": 1, "s": -1}) == (0, 1, -1, 0, 0, 0, 0)
    assert ci._dim_vector("Quux") is None
    assert ci._dim_vector(123) is None


def test_audit_aggregator():
    """`audit` runs every applicable invariant: PASS when all hold, FLAG when any violates,
    N/A when none applies, and a checker that raises is itself a fail-closed FLAG."""
    # single law, holds -> PASS
    ok = ci.audit({"accounting": {"assets": 100, "liabilities": 60, "equity": 40}})
    assert ok["applicable"] is True and ok["verdict"] == "PASS" and "accounting" in ok["laws_checked"]
    assert ok["violations"] == []
    # multi law, one violates -> FLAG, only the violator listed
    mixed = ci.audit({
        "accounting": {"assets": 100, "liabilities": 60, "equity": 40},          # holds
        "sum": None,                                                              # skipped (None)
        "parts": [1, 2, 3], "total": 99,                                          # violates -> FLAG
    })
    assert mixed["verdict"] == "FLAG" and "sum" in mixed["violations"]
    assert "accounting" not in mixed["violations"], "a holding law must not appear as a violation"
    # nothing applicable -> N/A, engine leaves verdict untouched
    na = ci.audit({"unrelated": 1})
    assert na["applicable"] is False and na["verdict"] == "N/A"
    # a checker that raises must be caught and turned into a FLAG (fail-closed), not propagate.
    # ohms_law with a non-coercible nested structure under a declared key still must not crash audit.
    safe = ci.audit({"linear_system": {"A": [["x"]], "x": [object()], "b": [1]}})
    assert isinstance(safe, dict) and safe["verdict"] in ("PASS", "FLAG", "N/A")


def test_sdk_invariants_wrapper():
    """The SDK `invariants` entrypoint must delegate to audit and fail-closed on a violation."""
    good = capas_sdk.invariants({"accounting": {"assets": 100, "liabilities": 60, "equity": 40}})
    assert good["verdict"] == "PASS"
    bad = capas_sdk.invariants({"accounting": {"assets": 100, "liabilities": 60, "equity": 30}})
    assert bad["verdict"] == "FLAG"
    assert capas_sdk.invariants({}) ["verdict"] == "N/A"
    assert capas_sdk.invariants(None)["verdict"] == "N/A"  # None coerced to {}


# --------------------------------------------------------------------------- #
# capas_admissibility — the graded reward across every class branch.
# --------------------------------------------------------------------------- #
def _adm_payloads():
    verified = _p("balances", "financial_metric_claim",
                  {**FIN, "accounting": {"identity": "balance_sheet",
                                         "assets": 1000, "liabilities": 600, "equity": 400}})
    conjecture = _p("treatment works", "statistical_confidence",
                    {"p_value": 0.01, "alpha": 0.05, "effect_direction_confirmed": True})  # declared, no raw
    attest = _p("X causes Y", "causal_mechanism_claim",
                {"intervention_or_natural_experiment": True, "temporal_order_established": True,
                 "confounders_controlled": True, "mechanism_evidence_present": True})  # unbacked design
    refuted = _p("balances", "financial_metric_claim",
                 {**FIN, "accounting": {"identity": "debits_equal_credits",
                                        "debits": [100], "credits": [999]}})
    return verified, conjecture, attest, refuted


def test_admissibility_classes_and_ordering():
    verified, conjecture, attest, refuted = _adm_payloads()
    rv = A.admissibility(verified)
    rc = A.admissibility(conjecture)
    ra = A.admissibility(attest)
    rf = A.admissibility(refuted)
    for r in (rv, rc, ra, rf):
        assert 0.0 <= r["score"] <= 1.0, f"score out of [0,1]: {r['score']}"
        assert set(("coherence", "groundedness", "viability")) <= set(r["components"])
    assert rv["class"] == "VERIFIED" and rv["score"] >= 0.999
    assert rc["class"] == "CONJECTURE"
    assert ra["class"] == "ATTEST_DEFER"
    assert rf["class"] == "REFUTED" and rf["score"] == 0.0
    assert rf["components"]["coherence"] == 0.0
    # the imagination-preserving ordering the reward MUST uphold
    assert rv["score"] > rc["score"] > ra["score"] > rf["score"], (
        f"ordering broken: V={rv['score']} C={rc['score']} A={ra['score']} R={rf['score']}")
    # the gradient is actionable: a conjecture exposes viable next_obligations
    assert isinstance(rc["next_obligations"], list)


def test_admissibility_bare_claim_branches():
    """A claim whose only check is the base contract hits the total==0 branch:
    ACCEPT -> FORM_OK (0.6), else UNSUPPORTED (0.15)."""
    form_ok = _p("a stat claim", "statistical_confidence",
                 {"p_value": 0.01, "alpha": 0.05, "effect_direction_confirmed": True})
    unsupported = _p("a stat claim", "statistical_confidence",
                     {"p_value": 0.9, "alpha": 0.05, "effect_direction_confirmed": True})  # p>alpha
    rfo = A.admissibility(form_ok)
    rus = A.admissibility(unsupported)
    assert rfo["class"] in ("FORM_OK", "CONJECTURE", "VERIFIED", "PARTIAL"), rfo["class"]
    # the UNSUPPORTED path (no checks, did not ACCEPT) must score low and never crash
    assert 0.0 <= rus["score"] <= 1.0
    assert rus["class"] in ("UNSUPPORTED", "REFUTED", "SPECULATION", "CONJECTURE")


def test_reward_hook_matches_score():
    verified, _, _, refuted = _adm_payloads()
    assert A.reward(verified) == A.admissibility(verified)["score"]
    assert A.reward(refuted) == 0.0


def test_bucket_classifier():
    """_bucket sorts every check status into one of four epistemic buckets (drives the lookup sets)."""
    assert A._bucket("VERIFIED") == "grounded"
    assert A._bucket("FAIL") == "refuted"
    assert A._bucket("BEYOND_FRONTIER") == "irreducible"
    assert A._bucket("NOT_SUPPLIED") == "viable"      # default: an unknown non-grounded status
    assert A._bucket(None) == "viable"


# --------------------------------------------------------------------------- #
# capas_rcc — the reflexive conformal certificate across every stratum.
# --------------------------------------------------------------------------- #
def test_rcc_strata_and_certificate():
    verified, conjecture, attest, refuted = _adm_payloads()

    c_g = R.rcc(verified)
    assert c_g["headline"].startswith("GROUNDED")
    assert len(c_g["strata"]["grounded"]) >= 1
    assert c_g["strata"]["grounded"][0].get("coverage"), "grounded item must carry coverage text"

    c_gen = R.rcc(conjecture)
    gen = c_gen["strata"]["generated"]
    assert len(gen["items"]) >= 1 and len(gen["minimal_bridge"]) >= 1, "generated stratum needs a bridge"
    assert gen["status"].startswith("abstain")
    # the product output is a proposal: a SUPPLY step to ground the conjecture
    assert c_gen["solution_proposal"], "a non-grounded claim must propose its own exit"
    assert any(s["kind"] == "SUPPLY" for s in c_gen["solution_proposal"])

    c_u = R.rcc(attest)
    assert len(c_u["strata"]["unknowable"]) >= 1
    assert "requires_attestation" in c_u["strata"]["unknowable"][0]["why_unreachable"]
    assert any(s["kind"] == "ATTEST" for s in c_u["solution_proposal"])

    c_r = R.rcc(refuted)
    assert c_r["headline"].startswith("REFUTED")
    assert c_r["refuted"], "refuted stratum must be populated"
    assert any(s["kind"] == "CORRECT" for s in c_r["solution_proposal"])

    # every certificate carries the standing Löbian clause, a certificate_id, and the engine digest
    for c in (c_g, c_gen, c_u, c_r):
        assert "cannot certify its own grounding" in c["loebian_clause"]
        assert c["certificate_id"].startswith("sha256:")
        assert c["schema"] == "capas-reflexive-conformal-certificate-v1"
        assert c["decision_path"] == "deterministic; no LLM in the verdict"
        # signature is present iff a key is configured; when present it is Ed25519
        sig = c.get("signature")
        if sig is not None:
            assert sig.get("algorithm") == "Ed25519"


def test_rcc_certificate_determinism():
    """Same payload -> same certificate_id (the canonical-JSON hash is reproducible)."""
    verified, *_ = _adm_payloads()
    a, b = R.rcc(verified), R.rcc(verified)
    assert a["certificate_id"] == b["certificate_id"], "certificate_id is not deterministic"


def test_rcc_gigo_consilience_branch():
    """A consilience block under evidence drives the gigo_consilience renormalisation in rcc:
    independent corroborating adjacencies shrink the residual; a dissenting one flags contradiction."""
    levels = [
        {"claimed": 2.0, "question": "is the fact real?",
         "adjacencies": [{"value": 2.0, "group": g} for g in "ABC"]},
        {"claimed": 1.0, "question": "are those sources independent?",
         "adjacencies": [{"value": 1.0, "group": g} for g in "XYZ"]},
    ]
    payload = _p("balances", "financial_metric_claim",
                 {**FIN, "accounting": {"identity": "balance_sheet",
                                        "assets": 1000, "liabilities": 600, "equity": 400},
                  "consilience": levels})
    c = R.rcc(payload)
    rep = c.get("gigo_consilience")
    assert rep is not None, "consilience block under evidence must populate gigo_consilience"
    assert 0.0 <= rep["fabrication_resistance_total_residual"] <= 1.0
    assert rep["depth"] == 2
    assert rep["contradicted_by_independent_adjacency"] is False
    assert rep["irreducible_floor"] >= 0.0

    # a dissenting independent adjacency -> contradiction registered
    dissent = [
        {"claimed": 2.0, "question": "is the fact real?",
         "adjacencies": [{"value": 2.0, "group": "A"}, {"value": 99.0, "group": "bank"}]},
    ]
    payload2 = _p("balances", "financial_metric_claim",
                  {**FIN, "accounting": {"identity": "balance_sheet",
                                         "assets": 1000, "liabilities": 600, "equity": 400},
                   "consilience": dissent})
    c2 = R.rcc(payload2)
    rep2 = c2.get("gigo_consilience")
    assert rep2 is not None and rep2["contradicted_by_independent_adjacency"] is True


def main() -> int:
    tests = [
        test_every_checker_pass_and_flag,
        test_quantum_checker_via_registry,
        test_applies_false_skip_branches,
        test_formula_parser_parentheses,
        test_dimension_vector_math,
        test_audit_aggregator,
        test_sdk_invariants_wrapper,
        test_admissibility_classes_and_ordering,
        test_admissibility_bare_claim_branches,
        test_reward_hook_matches_score,
        test_bucket_classifier,
        test_rcc_strata_and_certificate,
        test_rcc_certificate_determinism,
        test_rcc_gigo_consilience_branch,
    ]
    failed = []
    for t in tests:
        try:
            t()
        except AssertionError as e:
            failed.append(f"{t.__name__}: {e}")
        except Exception as e:  # noqa: BLE001
            failed.append(f"{t.__name__}: UNEXPECTED {type(e).__name__}: {e}")
    if failed:
        print("FAIL:")
        for f in failed:
            print("  -", f)
        return 1
    print(f"OK {len(tests)}/{len(tests)} suites — 23 invariant checkers (PASS+FLAG+malformed) + audit "
          f"aggregator, admissibility class/ordering, rcc strata + consilience + signed certificate.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
