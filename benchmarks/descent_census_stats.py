#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""Hard statistics for the CAPAS descent census (rung-2 literal check).

The census is a CENSUS, not a sample: every quantitative claim on the audited served surfaces is
checked. So the "sample" IS the distribution of the variable (quantitative-claim correctness on the
live surface) — there is no sampling error. The interval below is therefore the EXACT (Clopper-Pearson,
i.e. inverted exact binomial) interval, not an asymptotic normal approximation. It quantifies only the
residual uncertainty from finiteness, not from sampling.

Honest scope (what this does NOT license): this measures the LIVE SURFACE's quantitative-claim defect
rate and the descent's marginal catch over a gestalt read. It is NOT a powered CAPAS-vs-LLM inferential
comparison — that needs the pre-registered blind design (discordant pairs >= 11 for p<0.001; the n=500
study), which this is not. No composite verdict; the number is re-derivable from the census JSON.

Usage: python3 benchmarks/descent_census_stats.py <census.json>
  where census.json is the Workflow result object (keys: population_N, mismatch_k, unbacked_k,
  full_census, relations, ...).
"""
import json
import sys
from scipy.stats import beta


def clopper_pearson(k: int, n: int, alpha: float = 0.05):
    """Exact (inverted-binomial) two-sided 1-alpha CI for a binomial proportion."""
    if n == 0:
        return (0.0, 0.0)
    lo = 0.0 if k == 0 else beta.ppf(alpha / 2, k, n - k + 1)
    hi = 1.0 if k == n else beta.ppf(1 - alpha / 2, k + 1, n - k)
    return (float(lo), float(hi))


def pct(x: float) -> str:
    return f"{100*x:.2f}%"


def main(path: str) -> int:
    with open(path) as f:
        c = json.load(f)

    census = c.get("full_census", [])
    # Denominator comes from the raw census itself, so numerator and denominator share one universe.
    N = len(census) if census else c.get("population_N", 0)
    # Recompute from the raw census so the numbers are ours, not the workflow's summary.
    mismatch = [x for x in census if x.get("verdict") == "mismatch"]
    unbacked = [x for x in census if x.get("verdict") == "unbacked"]
    matched = [x for x in census if x.get("verdict") in ("match", "self-backing")]
    k_mis = len(mismatch)
    k_unb = len(unbacked)

    print("=" * 72)
    print("CAPAS DESCENT CENSUS — HARD STATISTICS (rung-2 literal check)")
    print("=" * 72)
    print(f"Design        : CENSUS (every quantitative claim) -> sample == distribution, zero sampling error")
    print(f"Population N   : {N} quantitative claims across {len(c.get('per_surface', []))} served surfaces")
    for s in c.get("per_surface", []):
        print(f"    - {s['surface']}: {s['n']}")
    print("-" * 72)

    # Defect = a claim whose backing disagrees (re-derivation contradicts the page).
    lo, hi = clopper_pearson(k_mis, N)
    print(f"MISMATCH (defect) : k={k_mis}/{N}  point={pct(k_mis/N) if N else 'NA'}")
    print(f"  exact 95% CI    : [{pct(lo)}, {pct(hi)}]  (Clopper-Pearson)")

    # Unbacked = a claim with no locatable in-repo re-derivation (admissible-as-illustrative, not proven).
    lo2, hi2 = clopper_pearson(k_unb, N)
    print(f"UNBACKED          : k={k_unb}/{N}  point={pct(k_unb/N) if N else 'NA'}")
    print(f"  exact 95% CI    : [{pct(lo2)}, {pct(hi2)}]")

    # Re-derivable rate = matched / N, the positive integrity statement.
    k_ok = len(matched)
    lo3, hi3 = clopper_pearson(k_ok, N)
    print(f"RE-DERIVABLE OK   : k={k_ok}/{N}  point={pct(k_ok/N) if N else 'NA'}")
    print(f"  exact 95% CI    : [{pct(lo3)}, {pct(hi3)}]")
    print("-" * 72)

    # The methodology's value metric: of the real defects, how many would a gestalt read miss?
    missed = [x for x in mismatch if x.get("holistic_would_miss")]
    print(f"DESCENT VALUE     : {len(missed)}/{k_mis} mismatches are gestalt-invisible "
          f"(both values individually plausible -> only the literal/relational rung catches them)")
    for m in mismatch:
        tag = "gestalt-MISS" if m.get("holistic_would_miss") else "gestalt-visible"
        print(f"    [{m.get('severity','?'):>6}] {m.get('surface','?')}: "
              f"{m.get('value','?')} vs source {m.get('source_value','?')} ({tag}) — {m.get('asserts','')}")
    print("-" * 72)

    rel = c.get("relations", {}) or {}
    tot_rel = rel.get("total_repeated_facts", "?")
    drift = rel.get("drifting_facts", "?")
    print(f"RUNG-6 RELATIONS  : {tot_rel} facts repeated across >=2 surfaces; {drift} drifting")
    for r in rel.get("repeated_facts", []):
        if not r.get("agree", True):
            print(f"    DRIFT [{r.get('severity','?')}] {r.get('fact','?')}: "
                  f"{r.get('occurrences')} (auth={r.get('authoritative_source','?')}) — {r.get('drift','')}")
    print("=" * 72)
    print("INTERPRETATION (honest):")
    print(" - The CI is exact and reflects finiteness only; the census removes sampling error by construction.")
    print(" - This bounds the LIVE SURFACE's quantitative-claim integrity + the descent's marginal catch.")
    print(" - It is NOT a CAPAS-vs-LLM inferential test (needs the pre-registered blind n>=500 design).")
    print("=" * 72)
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
