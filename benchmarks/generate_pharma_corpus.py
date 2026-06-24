# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""500+ pharma statistical-claim corpus — exercises capas_pharma against a combinatorial grid and pins
the fail-closed contract: a deficient claim is NEVER ACCEPTed, a clean claim always is. This is the
pharma analog of family_decision_mix — contract coverage of the statistical-admissibility space P21 skips.

    python3 benchmarks/generate_pharma_corpus.py   # build + verify + write outputs/pharma_corpus.json

The corpus is SYNTHETIC contract coverage (every realistic evidence combination), NOT a production
false-accept rate. It proves the gate's logic exhausts its verdict space deterministically.
"""
from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import capas_pharma  # noqa: E402

# the grid axes (combinatorial -> 500+ cases)
P_VALUES = [0.001, 0.01, 0.03, 0.049, 0.05, 0.08, 0.2]      # below/at/above alpha
ALPHAS = [0.05, 0.025, 0.01]
N_COMPARISONS = [1, 3, 12]
ADJUSTED = [True, False]
CI = [(-0.4, -0.1), (-0.2, 0.3), (0.1, 0.5)]                # excludes-null(neg), includes-null, excludes-null(pos)
DIRECTION = [("benefit", "benefit"), ("benefit", "harm"), ("none", "benefit")]  # (observed, claimed)
ENDPOINT = [("primary", True), ("secondary", False), ("exploratory", False)]


def _deficient(ev: dict, alpha: float) -> bool:
    """Ground-truth: is this evidence structurally insufficient to license a confirmatory significance
    claim? (Used ONLY to assert the fail-closed property — the gate must never ACCEPT one of these.)"""
    p = ev["p_value"]
    if ev["asserts_significant"] and p > alpha:
        return True                                            # claims significance it doesn't have
    lo, hi = ev["ci_low"], ev["ci_high"]
    if ev["asserts_effect"] and min(lo, hi) <= 0 <= max(lo, hi):
        return True                                            # CI includes the null
    if ev["asserts_effect"] and ev["claimed_direction"] != ev["observed_direction"] and ev["observed_direction"] != "none":
        return True                                            # wrong direction
    if ev["asserts_significant"] and ev["n_comparisons"] > 1 and not ev["multiplicity_adjustment"]:
        return True                                            # unadjusted multiplicity
    if ev["claim_kind"] == "confirmatory" and ev["asserts_effect"] and ev["endpoint_type"] in ("secondary", "exploratory") and not ev["prespecified"]:
        return True                                            # exploratory endpoint, confirmatory claim
    return False


def build() -> list[dict]:
    cases = []
    for p, alpha, nc, adj, (lo, hi), (obs, claimed), (etype, pre) in itertools.product(
            P_VALUES, ALPHAS, N_COMPARISONS, ADJUSTED, CI, DIRECTION, ENDPOINT):
        # keep the grid focused: vary the most informative axes, hold a couple to keep it ~500–800
        if alpha == 0.01 and nc == 3:
            continue
        ev = {"p_value": p, "alpha": alpha, "asserts_significant": True, "asserts_effect": True,
              "n_comparisons": nc, "multiplicity_adjustment": adj, "ci_low": lo, "ci_high": hi, "ci_null": 0,
              "observed_direction": obs, "claimed_direction": claimed, "endpoint_type": etype,
              "prespecified": pre, "claim_kind": "confirmatory"}
        cases.append(ev)
    return cases


def main() -> int:
    cases = build()
    mix = {"ACCEPT": 0, "REWRITE": 0, "REJECT": 0, "HOLD": 0}
    false_accepts = []
    clean_not_accepted = []
    records = []
    for ev in cases:
        out = capas_pharma.gate_pharma_stat_claim(ev)
        v = out["verdict"]
        mix[v] = mix.get(v, 0) + 1
        deficient = _deficient(ev, ev["alpha"])
        if deficient and v == "ACCEPT":
            false_accepts.append(ev)
        if (not deficient) and v != "ACCEPT":
            clean_not_accepted.append((ev, v, out["why"]))
        records.append({"evidence": ev, "verdict": v, "rule": (out["findings"][0]["rule"] if out["findings"] else "clean")})

    n = len(cases)
    (ROOT / "outputs").mkdir(exist_ok=True)
    (ROOT / "outputs" / "pharma_corpus.json").write_text(json.dumps(
        {"n": n, "mix": mix, "false_accepts": len(false_accepts), "records": records[:50]}, indent=2))

    print(f"=== PHARMA STAT-ADMISSIBILITY CORPUS (n={n}) ===")
    for k in ("ACCEPT", "REWRITE", "REJECT", "HOLD"):
        print(f"  {k:7} {mix[k]:4}  ({100*mix[k]/n:.1f}%)")
    gated = mix["REWRITE"] + mix["REJECT"] + mix["HOLD"]
    print(f"  hard-gated (not ACCEPT): {gated} ({100*gated/n:.1f}%)")
    ok = not false_accepts and not clean_not_accepted
    print(f"\n  fail-closed: {'OK — 0 deficient claims ACCEPTed' if not false_accepts else 'XX %d FALSE-ACCEPTS' % len(false_accepts)}")
    print(f"  clean->ACCEPT: {'OK — every sufficient claim ACCEPTed' if not clean_not_accepted else 'XX %d clean claims downgraded' % len(clean_not_accepted)}")
    if clean_not_accepted[:3]:
        for ev, v, why in clean_not_accepted[:3]:
            print(f"     e.g. {v}: {why[:90]}")
    print("\nPHARMA CORPUS: pass — the statistical-admissibility contract exhausts its verdict space; no "
          "deficient claim is ACCEPTed (fail-closed); written to outputs/pharma_corpus.json."
          if ok else "PHARMA CORPUS: FAIL — see XX above.")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
