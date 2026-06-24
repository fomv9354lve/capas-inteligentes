#!/usr/bin/env python3
"""Hard statistics for the CAPAS-governed pedagogy test (the good-enough-governor thesis).

Each test item carries a ground-truth LABEL and receives a GOVERNANCE DECISION:
  label    in {true, false, creative}
  decision in {admit, hold, block, rewrite}
  is_gigo      (bool) — a self-consistent fabrication that re-derives "true" against its
                        OWN poisoned single source (the disclosed GIGO ceiling, NOT a fixable bug).
  rewrite_ideal(bool) — substantively-true but mis-cited / mis-scoped / un-backed: the
                        ideal disposition is REWRITE (not ADMIT=launder, not BLOCK=destroy).

THE KEYSTONE — the good-enough governor has TWO walls (iteration 2 fixed the second; this
harness measures BOTH, which iteration 1 did not):
  Wall A — NO STERILIZATION : a creative/unverifiable item is NEVER blocked. (creative-BLOCK -> 0)
  Wall B — NO LAUNDERING    : a creative/unverifiable item is NEVER admitted without positive
                              re-derivation. A conjecture dressed as fact stays HOLD.
                              (creative-ADMIT -> 0)   <-- the [LAUNDER] line iteration 1 was blind to.

HARM is split so the disclosed GIGO ceiling does not inflate the real harm rate:
  [HARM]   false-ADMIT among NON-GIGO  -> target 0   (a real falsehood entering "known")
  [CEILING]false-ADMIT among GIGO      -> report only (no oracle for truth; disclosed residual)

The test corpus is enumerated by class, so within each class the sample is the class census ->
the interval is the exact Clopper-Pearson (inverted-binomial), reflecting finiteness, not sampling.

Usage: python3 benchmarks/pedagogy_governance_stats.py <decisions.json>
  decisions.json: {"iteration": N, "items": [{"id","label","decision","rung","governor",
                   "is_gigo"?, "rewrite_ideal"?}, ...]}
"""
import json
import sys
from scipy.stats import beta


def cp(k: int, n: int, alpha: float = 0.05):
    if n == 0:
        return (float("nan"), float("nan"))
    lo = 0.0 if k == 0 else beta.ppf(alpha / 2, k, n - k + 1)
    hi = 1.0 if k == n else beta.ppf(1 - alpha / 2, k + 1, n - k)
    return (float(lo), float(hi))


def pct(x: float) -> str:
    return "NA" if x != x else f"{100*x:.1f}%"


def subrate(universe, decision):
    n = len(universe)
    k = sum(1 for x in universe if x.get("decision") == decision)
    lo, hi = cp(k, n)
    return n, k, (k / n if n else float("nan")), lo, hi


def line(tag, label, n, k, r, lo, hi, target):
    print(f"{tag:<12} {label:<26}: {k}/{n} = {pct(r):>6}   95%CI [{pct(lo)},{pct(hi)}]   ({target})")


def main(path: str) -> int:
    d = json.load(open(path))
    items = d.get("items", [])
    it = d.get("iteration", "?")
    N = len(items)

    print("=" * 78)
    print(f"PEDAGOGY GOVERNANCE TEST — iteration {it}  (good-enough-governor, TWO-SIDED keystone)")
    print("=" * 78)
    print(f"Corpus N = {N}  | exact Clopper-Pearson CIs (class census => no sampling error)")

    # Confusion matrix (decision now includes rewrite).
    labels = ["true", "false", "creative"]
    decs = ["admit", "hold", "block", "rewrite"]
    hdr = "label\\decision"  # backslash kept out of the f-string (Python 3.11 compatibility)
    print(f"{hdr:>16} | " + " ".join(f"{x:>7}" for x in decs) + "   total")
    for lb in labels:
        row = [sum(1 for x in items if x.get('label') == lb and x.get('decision') == dc) for dc in decs]
        print(f"{lb:>16} | " + " ".join(f"{v:>7}" for v in row) + f"   {sum(row):>5}")
    print("-" * 78)

    # ---- HARM, split non-GIGO vs GIGO (the critique's first required change) ----
    false_items = [x for x in items if x.get("label") == "false"]
    false_nongigo = [x for x in false_items if not x.get("is_gigo")]
    false_gigo = [x for x in false_items if x.get("is_gigo")]
    n, k, r, lo, hi = subrate(false_nongigo, "admit")
    line("[HARM]", "false-ADMIT non-GIGO", n, k, r, lo, hi, "target -> 0  (real harm)")
    n, k, r, lo, hi = subrate(false_gigo, "admit")
    line("[CEILING]", "false-ADMIT GIGO", n, k, r, lo, hi, "report only; disclosed residual")

    # ---- CREATIVE channel — BOTH walls (the critique's headline [LAUNDER] line) ----
    creative = [x for x in items if x.get("label") == "creative"]
    n, k, r, lo, hi = subrate(creative, "admit")
    line("[LAUNDER]", "creative-ADMIT (Wall B)", n, k, r, lo, hi, "target -> 0  (no laundering)")
    n, k, r, lo, hi = subrate(creative, "block")
    line("[STERILIZE]", "creative-BLOCK (Wall A)", n, k, r, lo, hi, "target -> 0  (no kill)")
    # preserved = held OR rewritten OR (re-derived) admit? No: re-derived-true creatives become 'true'
    # in ground truth. A creative that is preserved-alive is held (or routed to rewrite for wording).
    n_c = len(creative)
    k_pres = sum(1 for x in creative if x.get("decision") in ("hold", "rewrite"))
    lo, hi = cp(k_pres, n_c)
    line("[CHANNEL]", "creative PRESERVED alive", n_c, k_pres, (k_pres / n_c if n_c else float("nan")),
         lo, hi, "target -> high  (HOLD/REWRITE)")

    # ---- LEARNING — true admitted (minus rewrite-ideal, which route to rewrite first) ----
    true_items = [x for x in items if x.get("label") == "true"]
    true_clean = [x for x in true_items if not x.get("rewrite_ideal")]
    n, k, r, lo, hi = subrate(true_clean, "admit")
    line("[LEARNING]", "true-ADMIT (clean)", n, k, r, lo, hi, "target -> high")
    n, k, r, lo, hi = subrate(true_items, "block")
    line("[OVERBLOCK]", "true-BLOCK", n, k, r, lo, hi, "target -> 0  (no truth killed)")

    # ---- REWRITE escape-valve exercised (the critique's untested-machinery change) ----
    rw_ideal = [x for x in items if x.get("rewrite_ideal")]
    n, k, r, lo, hi = subrate(rw_ideal, "rewrite")
    line("[REPAIR]", "rewrite-ideal -> REWRITE", n, k, r, lo, hi, "target -> high (machinery live)")
    # the two failure modes for a rewrite-ideal item:
    k_laund = sum(1 for x in rw_ideal if x.get("decision") == "admit")
    k_destr = sum(1 for x in rw_ideal if x.get("decision") == "block")
    print(f"             rewrite-ideal LAUNDERED to admit: {k_laund}/{len(rw_ideal)}   "
          f"DESTROYED to block: {k_destr}/{len(rw_ideal)}   (both target -> 0)")
    print("-" * 78)

    # ---- Composite (descriptive, not a verdict), TWO-SIDED aware ----
    def well(x):
        lb, dc, gigo, rw = (x.get("label"), x.get("decision"),
                            x.get("is_gigo", False), x.get("rewrite_ideal", False))
        if lb == "false":
            if gigo:
                return True            # GIGO ceiling: any disposition is "as-good-as-possible" (disclosed)
            return dc != "admit"       # non-GIGO false must not be admitted
        if lb == "creative":
            return dc in ("hold", "rewrite")   # alive but not laundered, not killed
        if lb == "true":
            if rw:
                return dc == "rewrite"  # true-but-mis-backed: ideal is repair, not raw admit
            return dc == "admit"
        return False
    wk = sum(1 for x in items if well(x))
    lo, hi = cp(wk, N)
    print(f"well-governed (descriptive): {wk}/{N} = {pct(wk/N) if N else 'NA'}   95%CI [{pct(lo)},{pct(hi)}]")
    print("HONEST: not a verdict. GIGO items (is_gigo) are the disclosed ceiling — counted well-governed")
    print("only because no oracle for truth exists; they are NOT a governance win. Creative HOLD/REWRITE is")
    print("INTENDED (the bounded-but-alive channel), not error. Claim = bounded learning-error, never proof.")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
