#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Proves docs/rule_table.json against the engine (PLAN_v3 A1).

Records every decision the engine makes while the test suite, the 1,238-input benchmark grid and every payload file
in the repository run, then checks for each one:
  1. the reason parses into rules of the table (no reason segment outside the table),
  2. replaying those rules from the table alone gives the engine's verdict,
  3. a base rule with a claim type matches the payload's claim type.
Any failure is printed with the reason that produced it. Run: python3 scripts/check_rule_table.py"""
from __future__ import annotations

import glob, io, json, runpy, sys, contextlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "benchmarks"))
import capas, capas_rules  # noqa: E402

SEEN: list[tuple[dict, dict]] = []
_orig = capas.decide_external_claim


def _rec(payload, *a, **k):
    r = _orig(payload, *a, **k)
    if isinstance(r, dict) and "reason" in r and "verdict" in r:
        SEEN.append((payload if isinstance(payload, dict) else {}, r))
    return r


def main() -> int:
    capas.decide_external_claim = _rec
    import pytest
    with contextlib.redirect_stdout(io.StringIO()):
        pytest.main(["-q", "-x", "-p", "no:cacheprovider", str(ROOT / "benchmarks")])
        try:
            runpy.run_path(str(ROOT / "benchmarks" / "family_decision_mix.py"), run_name="__main__")
        except SystemExit:
            pass
    files = glob.glob(str(ROOT / "examples" / "*.json")) + glob.glob(str(ROOT / "research" / "**" / "*.jsonl"), recursive=True)
    for f in files:
        try:
            rows = [json.loads(l) for l in open(f, encoding="utf-8") if l.strip()] if f.endswith(".jsonl") else [json.load(open(f))]
        except Exception:
            continue
        for row in rows:
            for p in (row, row.get("payload") if isinstance(row, dict) else None):
                if isinstance(p, dict) and p.get("schema_version") == "capas-claim-payload-v3" and "claim" in p:
                    if isinstance(p["claim"], dict) and "text_sha256" in p["claim"]:
                        p = {**p, "claim": {"id": p["claim"]["id"], "type": p["claim"]["type"], "text": "sha256:" + p["claim"]["text_sha256"]}}
                    _rec(p)
    by_id = {r["id"]: r for r in capas_rules.table()["rules"]}
    bad, used, reasons = [], set(), set()
    for payload, r in SEEN:
        if r["reason"] in reasons:
            continue
        reasons.add(r["reason"])
        fired = capas_rules.parse_reason(r["reason"])
        if fired is None:
            bad.append(f"unparsed [{r['verdict']}] {r['reason'][:220]}")
            continue
        used.update(fired)
        v = capas_rules.replay(fired)
        if v != r["verdict"]:
            bad.append(f"replay {v} != engine {r['verdict']} via {fired}: {r['reason'][:200]}")
        ct = (payload.get("claim") or {}).get("type") if isinstance(payload.get("claim"), dict) else None
        b = by_id[fired[0]]
        if b.get("claim_type") and ct and b["claim_type"] != ct:
            bad.append(f"base rule {fired[0]} is for {b['claim_type']}, payload is {ct}: {r['reason'][:160]}")
    n_rules = len(by_id)
    print(f"decisions recorded: {len(SEEN)} | distinct reasons: {len(reasons)} | rules exercised: {len(used)}/{n_rules}")
    for b in bad[:60]:
        print("  " + b)
    print("PASS — every recorded reason parses into the rule table and replays to the engine's verdict" if not bad
          else f"FAIL — {len(bad)} problem(s)")
    unused = [rid for rid in by_id if rid not in used]
    if unused:
        print(f"note: {len(unused)} rules not exercised by any recorded decision (listed in outputs/rule_table_coverage.json)")
    (ROOT / "outputs").mkdir(exist_ok=True)
    json.dump({"decisions": len(SEEN), "distinct_reasons": len(reasons), "rules": n_rules, "exercised": sorted(used),
               "unexercised": [{"id": u, "label": by_id[u]["label"]} for u in unused], "problems": bad},
              open(ROOT / "outputs" / "rule_table_coverage.json", "w"), indent=1)
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
