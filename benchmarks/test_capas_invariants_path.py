# SPDX-License-Identifier: Apache-2.0
"""Coverage for the evidence.invariants downgrade-only filter integrated into
capas.decide_external_claim, plus the capas_invariants combiner (audit) and its
domain checkers, and the universal-anchor-mode REWRITE branches.

Every assertion exercises a REAL capas.py / capas_invariants.py body with valid
inputs and checks a fail-closed invariant of the result. No live LLM / network /
external dataset is needed for any path here, so nothing is skipped.

Run:  python benchmarks/test_capas_invariants_path.py   (exit 0 == pass)
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import capas  # noqa: E402
import capas_invariants as ci  # noqa: E402

SV = capas.CAPAS_CLAIM_SCHEMA_VERSION


def _mk(evidence: dict, claim_type: str = "exact_model_solution") -> dict:
    """A schema-valid v3 payload around the given evidence + claim type."""
    return {
        "schema_version": SV,
        "claim": {"id": "c", "type": claim_type, "text": "a model claim"},
        "evidence": evidence,
    }


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


# --------------------------------------------------------------------------- #
# 1. evidence.invariants is allowed on EVERY claim type (reserved namespace)   #
#    and a PASSING invariant block is pure pass-through (verdict untouched).   #
# --------------------------------------------------------------------------- #
def test_passing_invariant_is_pass_through() -> None:
    # Balanced books: assets == liabilities + equity -> PASS, verdict unchanged.
    res = capas.decide_external_claim(
        _mk({"abs_error": 0.01, "tolerance": 0.1,
             "invariants": {"accounting": {"assets": 100, "liabilities": 60, "equity": 40}}})
    )
    _check(res["verdict"] == "ACCEPT", f"passing invariant must not downgrade: {res['verdict']}")
    ia = res["invariant_audit"]
    _check(ia["applicable"] is True, "accounting block must be applicable")
    _check(ia["verdict"] == "PASS", f"balanced books must PASS: {ia}")
    _check("accounting" in ia["laws_checked"], "accounting law must be recorded")
    _check(ia["violations"] == [], "no violations expected on a balanced sheet")
    _check("OVERRIDDEN" not in res["reason"], "no override text on a passing invariant")
    # Pass-through keeps the licensed claim intact.
    _check(res["licensed_claim"] is not None, "ACCEPT keeps a licensed claim")


# --------------------------------------------------------------------------- #
# 2. No invariant block at all -> applicable False, verdict untouched (N/A).   #
# --------------------------------------------------------------------------- #
def test_no_invariant_block_is_na() -> None:
    res = capas.decide_external_claim(_mk({"abs_error": 0.01, "tolerance": 0.1}))
    _check(res["verdict"] == "ACCEPT", "no-invariant claim keeps its native verdict")
    ia = res["invariant_audit"]
    _check(ia["applicable"] is False, "no block -> not applicable")
    _check(ia["verdict"] == "N/A", f"empty invariants -> N/A: {ia['verdict']}")
    _check(ia["laws_checked"] == [], "nothing checked")
    _check("no domain invariant applies" in ia["summary"], "N/A summary text")


# --------------------------------------------------------------------------- #
# 3. A VIOLATED invariant downgrades an otherwise-ACCEPT verdict to REJECT     #
#    (fail-closed, downgrade-only), clears licensed_claim/rewrite, and stamps  #
#    the OVERRIDDEN reason.                                                    #
# --------------------------------------------------------------------------- #
def test_violated_invariant_downgrades_to_reject() -> None:
    res = capas.decide_external_claim(
        _mk({"abs_error": 0.01, "tolerance": 0.1,
             "invariants": {"accounting": {"assets": 100, "liabilities": 60, "equity": 5}}})
    )
    _check(res["verdict"] == "REJECT", f"books that do not close must REJECT: {res['verdict']}")
    _check("OVERRIDDEN by a domain invariant violation" in res["reason"], "override reason text")
    _check(res["licensed_claim"] is None, "downgrade clears licensed_claim")
    _check(res["rewrite"] is None, "downgrade clears rewrite")
    ia = res["invariant_audit"]
    _check(ia["verdict"] == "FLAG", "violated invariant must FLAG")
    _check("accounting" in ia["violations"], "accounting flagged as a violation")


# --------------------------------------------------------------------------- #
# 4. The override is STRICTER-ONLY: an already-REJECT verdict is never widened #
#    by the filter, and the override branch is skipped (verdict != REJECT).    #
# --------------------------------------------------------------------------- #
def test_override_never_widens_a_reject() -> None:
    # abs_error > tolerance -> native REJECT; a violated invariant must not loosen it.
    res = capas.decide_external_claim(
        _mk({"abs_error": 5.0, "tolerance": 0.1,
             "invariants": {"accounting": {"assets": 100, "liabilities": 1, "equity": 1}}})
    )
    _check(res["verdict"] == "REJECT", "native REJECT stays REJECT")
    # The override clause requires verdict != REJECT, so its text is NOT appended.
    _check("OVERRIDDEN" not in res["reason"], "override branch skipped on an existing REJECT")


# --------------------------------------------------------------------------- #
# 5. A violated invariant downgrades a REWRITE (anchor-mode) verdict too,      #
#    exercising the relative_anchor REWRITE branch then the override.         #
# --------------------------------------------------------------------------- #
def test_violated_invariant_downgrades_a_rewrite() -> None:
    ev = {
        "anchor_mode": "relative_anchor",
        "local_property_tests_pass": True,
        "relative_anchor_reference": "GPT-4",
        "relative_anchor_comparison_pass": True,
        # GRIM-impossible mean: 3.33 cannot be a k/10 to 2 decimals.
        "invariants": {"grim": {"mean": 3.33, "n": 10}},
    }
    res = capas.decide_external_claim(_mk(ev, "universal_anchor_claim"))
    _check(res["verdict"] == "REJECT", f"REWRITE must be downgraded to REJECT: {res['verdict']}")
    _check("OVERRIDDEN" in res["reason"], "override applied over a REWRITE")
    _check("grim" in res["invariant_audit"]["violations"], "grim flagged")


def test_anchor_mode_rewrite_passes_when_invariants_hold() -> None:
    # Same relative_anchor claim, but with a GRIM-CONSISTENT mean -> REWRITE stands.
    ev = {
        "anchor_mode": "relative_anchor",
        "local_property_tests_pass": True,
        "relative_anchor_reference": "GPT-4",
        "relative_anchor_comparison_pass": True,
        "invariants": {"grim": {"mean": 3.3, "n": 10}},  # 33/10 = 3.3 -> consistent
    }
    res = capas.decide_external_claim(_mk(ev, "universal_anchor_claim"))
    _check(res["verdict"] == "REWRITE", f"consistent GRIM keeps the REWRITE: {res['verdict']}")
    _check(res["invariant_audit"]["verdict"] == "PASS", "consistent GRIM must PASS")
    _check(res["licensed_claim"] is not None, "REWRITE licenses a bounded claim")


# --------------------------------------------------------------------------- #
# 6. Universal (top-level) invariants: probability bounds and sum conservation #
#    read keys directly off the invariants block.                             #
# --------------------------------------------------------------------------- #
def test_probability_bound_violation_downgrades() -> None:
    res = capas.decide_external_claim(
        _mk({"abs_error": 0.01, "tolerance": 0.1,
             "invariants": {"probabilities": [0.5, 1.7]}})  # 1.7 > 1 -> impossible
    )
    _check(res["verdict"] == "REJECT", "out-of-[0,1] probability must REJECT")
    _check("probability" in res["invariant_audit"]["violations"], "probability flagged")


def test_sum_conservation_violation_downgrades() -> None:
    res = capas.decide_external_claim(
        _mk({"abs_error": 0.01, "tolerance": 0.1,
             "invariants": {"parts": [10, 20, 30], "total": 999}})  # 60 != 999
    )
    _check(res["verdict"] == "REJECT", "non-conserving parts/total must REJECT")
    _check("sum" in res["invariant_audit"]["violations"], "sum flagged")


def test_distribution_normalization_pass_through() -> None:
    # A normalized distribution + in-range probs -> PASS, claim survives.
    res = capas.decide_external_claim(
        _mk({"abs_error": 0.01, "tolerance": 0.1,
             "invariants": {"distribution": {"a": 0.25, "b": 0.75}}})
    )
    _check(res["verdict"] == "ACCEPT", "normalized distribution is pass-through")
    _check(res["invariant_audit"]["verdict"] == "PASS", "sum-to-1 distribution PASSES")


# --------------------------------------------------------------------------- #
# 7. The audit_hash folds in the invariant verdict and is re-derivable: the    #
#    same payload reproduces, and a flagged block changes the hash.            #
# --------------------------------------------------------------------------- #
def test_audit_hash_includes_invariant_and_reproduces() -> None:
    flagged = capas.decide_external_claim(
        _mk({"abs_error": 0.01, "tolerance": 0.1,
             "invariants": {"accounting": {"assets": 100, "liabilities": 1, "equity": 1}}})
    )
    clean = capas.decide_external_claim(_mk({"abs_error": 0.01, "tolerance": 0.1}))
    _check(flagged["audit_hash"] != clean["audit_hash"],
           "the invariant verdict must change the audit hash")
    # Re-derivation matches the stored hash (tamper-evident, deterministic).
    _check(capas.reproduce_audit_hash(flagged) == flagged["audit_hash"],
           "flagged-claim audit hash must reproduce")
    _check(capas.reproduce_audit_hash(clean) == clean["audit_hash"],
           "clean-claim audit hash must reproduce")


# --------------------------------------------------------------------------- #
# 8. The capas_invariants.audit combiner directly: PASS / FLAG / N/A and the   #
#    fail-closed behaviour when a checker raises.                              #
# --------------------------------------------------------------------------- #
def test_audit_combiner_pass_flag_na() -> None:
    # PASS: balanced sheet.
    a = ci.audit({"accounting": {"assets": 10, "liabilities": 6, "equity": 4}})
    _check(a["applicable"] and a["verdict"] == "PASS", f"balanced -> PASS: {a}")

    # FLAG: probability out of bounds (universal, top-level key).
    f = ci.audit({"probabilities": [-0.2]})
    _check(f["applicable"] and f["verdict"] == "FLAG", f"negative prob -> FLAG: {f}")
    _check("probability" in f["violations"], "probability in violations list")

    # N/A: nothing applies.
    n = ci.audit({"unrelated": 123})
    _check(n["applicable"] is False and n["verdict"] == "N/A", f"nothing applies -> N/A: {n}")

    # Multiple laws, mixed -> the failing one drives the combined FLAG.
    mixed = ci.audit({
        "accounting": {"assets": 10, "liabilities": 6, "equity": 4},   # PASS
        "parts": [1, 2], "total": 99,                                  # FLAG
    })
    _check(mixed["verdict"] == "FLAG", "any single violation flags the whole audit")
    _check("sum" in mixed["violations"] and "accounting" in mixed["laws_checked"],
           "both laws appear; only sum violates")


def test_audit_non_dict_evidence_is_empty_na() -> None:
    # audit defensively coerces non-dict evidence to {} (fail-closed, no crash).
    r = ci.audit(None)  # type: ignore[arg-type]
    _check(r["applicable"] is False and r["verdict"] == "N/A", "None evidence -> N/A")
    r2 = ci.audit("not a dict")  # type: ignore[arg-type]
    _check(r2["verdict"] == "N/A", "str evidence -> N/A")


# --------------------------------------------------------------------------- #
# 9. Direct domain checkers: non-applicable, applicable-PASS, applicable-FLAG. #
# --------------------------------------------------------------------------- #
def test_individual_checkers_branches() -> None:
    # accounting: not applicable without the full triple.
    _check(ci.check_accounting({"accounting": {"assets": 1}})["applies"] is False,
           "partial accounting block is not applicable")
    # accounting: non-numeric -> FLAG.
    bad = ci.check_accounting({"accounting": {"assets": "x", "liabilities": 1, "equity": 1}})
    _check(bad["verdict"] == "FLAG", "non-numeric accounting -> FLAG")

    # grim: not applicable without mean+n.
    _check(ci.check_grim({"grim": {"mean": 3.0}})["applies"] is False, "grim needs n")
    # grim: consistent mean PASSES.
    _check(ci.check_grim({"grim": {"mean": 3.3, "n": 10}})["verdict"] == "PASS",
           "33/10 is a consistent mean")
    # grim: out-of-range against a declared scale -> FLAG.
    oor = ci.check_grim({"grim": {"mean": 99.0, "n": 1, "scale_min": 1, "scale_max": 5}})
    _check(oor["verdict"] == "FLAG", "mean outside scale range -> FLAG")

    # probability bounds: not applicable without probs/dist.
    _check(ci.check_probability_bounds({})["applies"] is False, "no probs -> N/A")
    # distribution that does not sum to 1 -> FLAG.
    dn = ci.check_probability_bounds({"distribution": {"a": 0.2, "b": 0.2}})
    _check(dn["verdict"] == "FLAG", "unnormalized distribution -> FLAG")

    # sum: not applicable without both keys / wrong types.
    _check(ci.check_sum({"parts": [1, 2]})["applies"] is False, "sum needs a total")
    _check(ci.check_sum({"parts": "x", "total": 3})["applies"] is False, "parts must be a list")
    # sum: conserved -> PASS.
    _check(ci.check_sum({"parts": [1, 2, 3], "total": 6})["verdict"] == "PASS",
           "conserved parts -> PASS")


def main() -> int:
    tests = [v for k, v in sorted(globals().items())
             if k.startswith("test_") and callable(v)]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"ok   {t.__name__}")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            print(f"FAIL {t.__name__}: {exc}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
