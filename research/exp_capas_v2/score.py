#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Deterministic scoring of experiment v2 (PROTOCOL.md, Measures 1-5), per model.

Layout: arm_A/<model>/decisions*.jsonl, arm_B/<model>/decisions*.jsonl, arm_B/<model>/calls.jsonl,
oracle/labels.json, effort.json. Decision row: {"claim": "R1#7", "decision": "state_as_written"|"narrow"|"withhold",
"narrowed_text"?, "evidence"?, "why"}.
Arm B's FINAL decision = capas.enforce(row decision, last logged verdict for that claim); no logged verdict ->
enforce against no verdict = withhold (fail-closed). A missing/malformed row counts as state_as_written for the error
measure and as a block for the false-block measure (worst case for each).
Run: python3 research/exp_capas_v2/score.py [--json out.json]"""
from __future__ import annotations

import json, math, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
import capas  # noqa: E402

ACTIONS = {"state_as_written", "narrow", "withhold"}


def rows(d: Path) -> dict[str, dict]:
    out = {}
    for p in sorted(d.glob("decisions*.jsonl")):
        for line in p.read_text(encoding="utf-8").splitlines():
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(r, dict) and isinstance(r.get("claim"), str):
                out[r["claim"]] = r
    return out


def verdicts(d: Path) -> dict[str, dict]:
    out = {}
    p = d / "calls.jsonl"
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            try:
                c = json.loads(line)
            except json.JSONDecodeError:
                continue
            out[c.get("claim")] = {"verdict": c.get("verdict"), "licensed_claim": c.get("licensed_claim")}
    return out


def mcnemar(b: int, c: int) -> float:
    m = b + c
    return 1.0 if m == 0 else min(1.0, 2 * sum(math.comb(m, i) for i in range(min(b, c) + 1)) / 2 ** m)


def score_arm(labels, decided: dict[str, str]):
    ids = sorted(labels)
    err = [int(labels[i]["category"] != "valid" and decided.get(i, "MISSING") in ("state_as_written", "MISSING")) for i in ids]
    blk = [int(labels[i]["category"] == "valid" and decided.get(i) != "state_as_written") for i in ids]
    by = {}
    for i in ids:
        c = labels[i]["category"]; by.setdefault(c, {}); k = decided.get(i, "MISSING"); by[c][k] = by[c].get(k, 0) + 1
    n_bad = sum(labels[i]["category"] != "valid" for i in ids)
    return {"errors": sum(err), "error_rate_nonvalid": round(sum(err) / n_bad, 4), "per_100_claims": round(100 * sum(err) / len(ids), 1),
            "false_blocks": sum(blk), "false_blocks_per_100": round(100 * sum(blk) / len(ids), 1), "by_category": by,
            "missing": [i for i in ids if i not in decided]}, err


def main() -> int:
    labels = json.loads((HERE / "oracle" / "labels.json").read_text(encoding="utf-8"))
    models = sorted({p.name for p in (HERE / "arm_A").iterdir() if p.is_dir()} if (HERE / "arm_A").exists() else set())
    out = {"n_claims": len(labels), "models": {}}
    for m in models:
        ra, rb, vb = rows(HERE / "arm_A" / m), rows(HERE / "arm_B" / m), verdicts(HERE / "arm_B" / m)
        da = {k: r["decision"] for k, r in ra.items() if r.get("decision") in ACTIONS}
        prop = {k: r["decision"] for k, r in rb.items() if r.get("decision") in ACTIONS}
        db = {k: capas.enforce(a, vb.get(k) or {}, rb[k].get("narrowed_text"))["action"] for k, a in prop.items()}
        A, ea = score_arm(labels, da); B, eb = score_arm(labels, db); Bp, _ = score_arm(labels, prop)
        only_a = sum(x and not y for x, y in zip(ea, eb)); only_b = sum(y and not x for x, y in zip(ea, eb))
        p = mcnemar(only_a, only_b)
        cond_a = A["error_rate_nonvalid"] >= 0.10
        cond_b = B["errors"] * 2 <= A["errors"] and only_a > only_b and p < 0.05
        cond_c = (B["false_blocks"] - A["false_blocks"]) * 100 / len(labels) <= 2
        out["models"][m] = {"A_alone": A, "B_with_capas_enforced": B, "B_agent_proposal_unenforced": Bp,
                            "paired": {"only_A_wrong": only_a, "only_B_wrong": only_b, "mcnemar_exact_p": p},
                            "errors_avoided_per_100": round(100 * (A["errors"] - B["errors"]) / len(labels), 1),
                            "extra_false_blocks_per_100": round(100 * (B["false_blocks"] - A["false_blocks"]) / len(labels), 1),
                            "capas_calls": len(vb), "claims_without_capas_call": sum(1 for k in labels if k not in vb),
                            "enforcement_changed": sum(1 for k in prop if db[k] != prop[k]),
                            "success": {"a_room": cond_a, "b_halves_p05": cond_b, "c_false_blocks": cond_c,
                                        "verdict": "NO ROOM" if not cond_a else "SUCCESS" if cond_b and cond_c else "FAIL"}}
    eff = HERE / "effort.json"
    if eff.exists():
        out["effort"] = json.loads(eff.read_text(encoding="utf-8"))
    text = json.dumps(out, indent=1)
    if "--json" in sys.argv:
        Path(sys.argv[sys.argv.index("--json") + 1]).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
