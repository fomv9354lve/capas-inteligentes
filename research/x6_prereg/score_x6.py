#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""X6 scoring (PREREG §4-§6): validity conditions V1-V3, CAPAS criteria 1-6, every measure for every arm.

Inputs (all sealed before the outcomes were labelled, except outcomes.jsonl):
  --outcomes outcomes.jsonl          label_outcomes.py output
  --capas capas_verdicts.jsonl       {claim_id, verdict, hold_class, checker_accepted}
  --judges judges/                   run_judges.py output (<model>__<arm>.jsonl + JUDGES_SEAL.json)
  --excluded coder_exclusions.jsonl  {claim_id, why}: coder disagreements (capas_coders.py), removed from EVERY arm
  --candidates-noncontaminated N     non-contaminated candidates (denominator of V2)
  --coders-independent yes|no        V3
Rules: FA = bad ACCEPT / bad; FR = good REJECT / good; ACCEPT floor = good ACCEPT / good; UNPARSED counts as HOLD;
criterion 6 uses the Newcombe paired-difference interval (method 10) at 95 % and the exact McNemar test; a tie is not a
win; ties on the best judge FA must all be beaten.
Run: python3 research/x6_prereg/score_x6.py --outcomes ... --capas ... --judges ... --excluded ... \
       --candidates-noncontaminated N --coders-independent no [--json out.json]"""
from __future__ import annotations

import argparse, json, math, sys
from pathlib import Path

Z = 1.959963984540054


def wilson(k: int, n: int) -> tuple[float | None, float | None]:
    if n == 0:
        return (None, None)
    p = k / n; d = 1 + Z * Z / n; c = (p + Z * Z / (2 * n)) / d; h = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n)) / d
    return (c - h, c + h)


def newcombe_paired(x: list[int], y: list[int]) -> tuple[float, float, float]:
    """Newcombe (1998) method 10 for the difference of paired proportions p1 - p2 (x, y: 0/1 per subject)."""
    n = len(x)
    e = sum(a and b for a, b in zip(x, y)); f = sum(a and not b for a, b in zip(x, y))
    g = sum((not a) and b for a, b in zip(x, y)); h = n - e - f - g
    p1, p2 = (e + f) / n, (e + g) / n
    l1, u1 = wilson(e + f, n); l2, u2 = wilson(e + g, n)
    denom = math.sqrt((e + f) * (g + h) * (e + g) * (f + h))
    if denom == 0:
        phi = 0.0
    else:
        num = e * h - f * g
        num = max(num - n / 2, 0) if num > 0 else num
        phi = num / denom
    d = p1 - p2
    lo = d - math.sqrt(max((p1 - l1) ** 2 - 2 * phi * (p1 - l1) * (u2 - p2) + (u2 - p2) ** 2, 0))
    hi = d + math.sqrt(max((u1 - p1) ** 2 - 2 * phi * (u1 - p1) * (p2 - l2) + (p2 - l2) ** 2, 0))
    return d, lo, hi


def mcnemar_exact(x: list[int], y: list[int]) -> float:
    f = sum(a and not b for a, b in zip(x, y)); g = sum((not a) and b for a, b in zip(x, y)); m = f + g
    if m == 0:
        return 1.0
    k = min(f, g)
    return min(1.0, 2 * sum(math.comb(m, i) for i in range(k + 1)) / 2 ** m)


def load(p) -> list[dict]:
    return [json.loads(l) for l in Path(p).read_text(encoding="utf-8").splitlines() if l.strip()]


def measures(verdicts: dict[str, str], outcome: dict[str, str], ids: list[str], hold_class: dict[str, str] | None = None) -> dict:
    bad = [i for i in ids if outcome[i] == "malo"]; good = [i for i in ids if outcome[i] == "bueno"]
    v = {i: ("HOLD" if verdicts.get(i, "UNPARSED") == "UNPARSED" else verdicts[i]) for i in ids}
    fa = sum(v[i] == "ACCEPT" for i in bad); fr = sum(v[i] == "REJECT" for i in good); af = sum(v[i] == "ACCEPT" for i in good)
    holds = [i for i in ids if v[i] == "HOLD"]
    acc = [i for i in ids if v[i] == "ACCEPT"]
    table = {vd: {"bad": sum(v[i] == vd for i in bad), "good": sum(v[i] == vd for i in good)} for vd in ("ACCEPT", "REWRITE", "REJECT", "HOLD")}
    return {"n_bad": len(bad), "n_good": len(good), "table": table,
            "FA": f"{fa}/{len(bad)}", "FA_ci95": wilson(fa, len(bad)), "FR": f"{fr}/{len(good)}", "FR_ci95": wilson(fr, len(good)),
            "accept_floor": af / len(good) if good else None, "hold_share": len(holds) / len(ids) if ids else None,
            "informative_rate": (len(ids) - len(holds)) / len(ids) if ids else None,
            "engine_gap_holds": sum(1 for i in holds if (hold_class or {}).get(i) == "engine_gap"),
            "PVP": f"{sum(outcome[i] == 'bueno' for i in acc)}/{len(acc)}",
            "unparsed": sum(1 for i in ids if verdicts.get(i, "UNPARSED") == "UNPARSED"),
            "_fa_vector": [1 if v[i] == "ACCEPT" else 0 for i in bad]}


def main() -> int:
    ap = argparse.ArgumentParser()
    for k in ("outcomes", "capas", "judges", "excluded", "candidates-noncontaminated", "coders-independent"):
        ap.add_argument(f"--{k}", required=True)
    ap.add_argument("--json")
    a = ap.parse_args()
    outcome = {o["claim_id"]: o["outcome"] for o in load(a.outcomes)}
    capas_rows = {r["claim_id"]: r for r in load(a.capas)}
    excluded = {r["claim_id"] for r in load(a.excluded)}
    ids = sorted(i for i in capas_rows if i in outcome and i not in excluded)
    cap = measures({i: capas_rows[i]["verdict"] for i in ids}, outcome, ids, {i: capas_rows[i].get("hold_class") for i in ids})
    seal = json.loads((Path(a.judges) / "JUDGES_SEAL.json").read_text(encoding="utf-8"))
    judges = {}
    for name, meta in seal["arms"].items():
        if meta.get("not_run"):
            judges[name] = {"not_run": meta["not_run"]}; continue
        rows = {r["claim_id"]: r["verdict"] for r in load(Path(a.judges) / f"{name}.jsonl")}
        judges[name] = measures(rows, outcome, ids)
    # validity
    n_nc = int(a.candidates_noncontaminated)
    V = {"V1": cap["n_bad"] >= 20 and cap["n_good"] >= 20,
         "V2": len(excluded) <= 0.20 * n_nc,
         "V3": a.coders_independent == "yes"}
    # criteria
    c = {1: cap["FA_ci95"][1] is not None and cap["FA_ci95"][1] <= 0.30,
         2: cap["FR_ci95"][1] is not None and cap["FR_ci95"][1] <= 0.25,
         3: cap["accept_floor"] is not None and cap["accept_floor"] >= 0.40,
         4: cap["hold_share"] is not None and cap["hold_share"] <= 0.30,
         5: all(capas_rows[i].get("checker_accepted") is True for i in ids)}
    eligible = {n: j for n, j in judges.items() if "not_run" not in j and n.split("__")[1] in ("A", "B") and (j["accept_floor"] or 0) >= 0.40}
    comparisons = {}
    if eligible:
        best = min(int(j["FA"].split("/")[0]) for j in eligible.values())
        tied = [n for n, j in eligible.items() if int(j["FA"].split("/")[0]) == best]
        for n in tied:
            d, lo, hi = newcombe_paired(cap["_fa_vector"], eligible[n]["_fa_vector"])
            comparisons[n] = {"diff": d, "ci95": (lo, hi), "mcnemar_p": mcnemar_exact(cap["_fa_vector"], eligible[n]["_fa_vector"]),
                              "below_zero": hi < 0}
        c[6] = all(x["below_zero"] for x in comparisons.values())
    else:
        c[6] = False
    void = not all(V.values())
    status = ("VOID (validity condition failed)" if not (V["V1"] and V["V2"]) else
              "EXPLORATORY (V3: coders not independent; no pass is claimed)" if not V["V3"] else
              "PASS" if all(c.values()) else "FAIL")
    grade = "pilot-grade" if min(cap["n_bad"], cap["n_good"]) < 40 else "pre-registered size"
    if cap["engine_gap_holds"] > 0.30 * max(1, round((cap["hold_share"] or 0) * len(ids))):
        status += "; coverage failure (> 30 % of HOLDs are engine_gap)"
    for m in [cap, *[j for j in judges.values() if "_fa_vector" in j]]:
        m.pop("_fa_vector", None)
    out = {"status": status, "grade": grade, "validity": V, "criteria": c, "capas": cap, "judges": judges,
           "comparisons": comparisons, "n_scored": len(ids), "n_excluded_coder_disagreement": len(excluded), "void": void}
    text = json.dumps(out, indent=1, default=str)
    if a.json:
        Path(a.json).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
