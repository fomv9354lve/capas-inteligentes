#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Deterministic scoring of the AI vs AI+CAPAS experiment (PROTOCOL.md, Measures 1-4).

Inputs: oracle/labels.json, arm_A/decisions.jsonl, arm_B/decisions.jsonl, arm_B/calls.jsonl, effort.json (tokens and
wall time per agent, copied from the run notifications). A decision row:
  {"case_id", "decision": "state_as_written"|"narrow"|"withhold", "narrowed_text"?, "evidence_quotes": [str],
   "audit_hash"? (arm B), "capas_verdict"? (arm B), "overrode_capas"? (arm B), "why"}
A missing or malformed row counts as `state_as_written` for the error measure and as a block for the false-block
measure (the worst reading for each), and is reported.
Run: python3 research/exp_capas_addon/score.py [--json out.json]"""
from __future__ import annotations

import json, math, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
import capas  # noqa: E402

ACTIONS = {"state_as_written", "narrow", "withhold"}


def load_rows(arm_dir: Path) -> dict[str, dict]:
    """Every decisions*.jsonl of the arm (one file per agent); the last row per case wins (a corrected decision)."""
    out = {}
    for p in sorted(arm_dir.glob("decisions*.jsonl")):
        for line in p.read_text(encoding="utf-8").splitlines():
            if line.strip():
                try:
                    r = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(r, dict):
                    out[r.get("case_id")] = r
    return out


def mcnemar_exact(b: int, c: int) -> float:
    m = b + c
    if m == 0:
        return 1.0
    return min(1.0, 2 * sum(math.comb(m, i) for i in range(min(b, c) + 1)) / 2 ** m)


def main() -> int:
    labels = json.loads((HERE / "oracle" / "labels.json").read_text(encoding="utf-8"))
    ids = sorted(labels)
    arms = {k: load_rows(HERE / f"arm_{k}") for k in ("A", "B")}
    calls = [json.loads(l) for l in (HERE / "arm_B" / "calls.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()] \
        if (HERE / "arm_B" / "calls.jsonl").exists() else []
    hashes_ok = set()
    for c in calls:   # an audit_hash counts as reproducible when the logged payload re-derives it
        if capas.decide_external_claim(c["payload"]).get("audit_hash") == c.get("audit_hash"):
            hashes_ok.add(c.get("audit_hash"))
    res, err_vec = {}, {}
    for k, rows in arms.items():
        errors, blocks, missing, repro, by_cat = [], [], [], 0, {}
        for i in ids:
            cat = labels[i]["category"]; r = rows.get(i)
            d = r.get("decision") if isinstance(r, dict) else None
            if d not in ACTIONS:
                missing.append(i)
            stated = d == "state_as_written" or d not in ACTIONS
            err = cat != "valid" and stated
            blk = cat == "valid" and d != "state_as_written"
            errors.append(int(err)); blocks.append(int(blk))
            by_cat.setdefault(cat, {"n": 0, "state_as_written": 0, "narrow": 0, "withhold": 0, "missing": 0})
            by_cat[cat]["n"] += 1; by_cat[cat][d if d in ACTIONS else "missing"] += 1
            case_text = (HERE / "cases" / f"{i}.json").read_text(encoding="utf-8")
            quotes = (r or {}).get("evidence_quotes") or []
            ok = bool(quotes) and all(isinstance(q, str) and q.strip() and q.strip() in case_text for q in quotes)
            if k == "B":
                ok = ok and (r or {}).get("audit_hash") in hashes_ok
            repro += int(ok)
        n_bad = sum(labels[i]["category"] != "valid" for i in ids); n_good = len(ids) - n_bad
        err_vec[k] = errors
        res[k] = {"errors_in_final_answer": sum(errors), "per_100_cases": round(100 * sum(errors) / len(ids), 1),
                  "error_rate_on_nonvalid": f"{sum(errors)}/{n_bad}",
                  "false_blocks": sum(blocks), "false_block_rate_on_valid": f"{sum(blocks)}/{n_good}",
                  "reproducible_decisions": f"{repro}/{len(ids)}", "missing_or_malformed": missing, "by_category": by_cat}
    a, b = err_vec["A"], err_vec["B"]
    only_a = sum(x and not y for x, y in zip(a, b)); only_b = sum(y and not x for x, y in zip(a, b))
    eff = json.loads((HERE / "effort.json").read_text(encoding="utf-8")) if (HERE / "effort.json").exists() else {}
    b_calls = [c for c in calls if c.get("case")]
    out = {"n_cases": len(ids), "arms": res,
           "paired_errors": {"only_A_wrong": only_a, "only_B_wrong": only_b, "mcnemar_exact_p": mcnemar_exact(only_a, only_b)},
           "errors_avoided_per_100": round(100 * (sum(a) - sum(b)) / len(ids), 1),
           "extra_false_blocks_per_100": round(100 * (res["B"]["false_blocks"] - res["A"]["false_blocks"]) / len(ids), 1),
           "capas_calls": len(b_calls), "capas_calls_per_case": round(len(b_calls) / len(ids), 2),
           "capas_overrides": sum(1 for r in arms["B"].values() if r.get("overrode_capas")),
           "effort": eff}
    text = json.dumps(out, indent=1)
    if "--json" in sys.argv:
        Path(sys.argv[sys.argv.index("--json") + 1]).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
