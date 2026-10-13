#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Severity grading of audit flags — the rule behind the README's "severos" column (85/3.988 control,
286/18.111 retracted). It lived only in a session scratchpad until 2026-10-13, when the §6 counter-signature
(xAI, run 4) correctly refuted the figure as irreproducible from the repo. Versioned here; re-derive with:
    python3 research/retraction_audit/grade_severity.py
Reads data/audit_results.json (+ data/meta_full.json for retraction reasons). No network."""
import json, re, collections, sys
from pathlib import Path
D = Path(__file__).resolve().parent / "data"
SEV = {"decision_error", "impossible", "numeric_mismatch"}


def sev(d: dict) -> str:
    w = d["why"]
    if "DECISION ERROR" in w:
        return "decision_error"
    if "exceeds N" in w or "100.0%" in w or re.search(r"\b0/\d+ = 0\.00% but reported [1-9]", w):
        return "impossible"
    m = re.search(r"= (\d+\.\d+)% but reported (\d+(?:\.\d+)?)%", w)
    if m:
        return "rounding" if abs(float(m.group(1)) - float(m.group(2))) < 1.0 else "numeric_mismatch"
    m = re.search(r"p=(\d\.\d+), but reported p[<=>]*(\d?\.\d+)", w)
    if m:
        return "rounding" if abs(float(m.group(1)) - float(m.group(2))) < 0.01 else "numeric_mismatch"
    return "other"


def main() -> int:
    res = json.load(open(D / "audit_results.json"))
    out = {}
    for g in ("CTL", "FAB"):
        R = [r for r in res if r["group"] == g]
        items = sum(r["checked"] for r in R)
        grades = collections.Counter(sev(d) for r in R for d in r["detail"])
        severe = sum(v for k, v in grades.items() if k in SEV)
        chk = sum(1 for r in R if r["checked"] > 0)
        paper_sev = sum(1 for r in R if any(sev(d) in SEV for d in r["detail"]))
        out[g] = {"papers": len(R), "checkable": chk, "items": items, "severe": severe,
                  "pct_severe": round(100 * severe / items, 2) if items else None,
                  "papers_with_severe": paper_sev, "grades": dict(grades)}
        print(f"{g}: papers {len(R)} | chequeables {chk} | items {items} | severos {severe} = {out[g]['pct_severe']}% | "
              f"papers con severo {paper_sev}/{chk} | grados {dict(grades)}")
    try:
        from scipy.stats import fisher_exact
        c, f = out["CTL"], out["FAB"]
        o, p = fisher_exact([[f["severe"], f["items"] - f["severe"]], [c["severe"], c["items"] - c["severe"]]])
        print(f"Fisher por item FAB vs CTL: OR {o:.2f}, p {p:.4f}")
    except ImportError:
        pass
    json.dump(out, open(D / "severity_summary.json", "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
