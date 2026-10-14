#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""CAPAS — coder agreement (PLAN_v3 A4, council: AI-eval, metascientist, formalist).

The engine is frozen at a tag; the CODER is the unfrozen half of the instrument. From X6 on, two independent blind
coders code the same claims. This module measures their agreement and applies the batch rule:

  field level    per evidence field coded by both: n, agreement, Cohen's kappa (booleans and categories)
  verdict level  both codings decided by the same engine: agreement and kappa over the four verdicts
  exclusions     a claim whose coders disagree on a REQUIRED field of its claim type is excluded from the batch
                 rate and recorded as HOLD, never resolved silently (the A7 report lists it)

Input: two JSONL files, one row per claim, {claim_id, payload} (payload = a CAPAS v3 claim payload).
Run: python3 capas_coders.py A.jsonl B.jsonl [--json OUT]"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

VERDICTS = ("ACCEPT", "REWRITE", "REJECT", "HOLD")


def cohen_kappa(pairs: list[tuple[Any, Any]]) -> float | None:
    """Cohen's kappa for two raters over the same items (None when undefined: no items or chance agreement = 1)."""
    pairs = [(a, b) for a, b in pairs]
    n = len(pairs)
    if n == 0:
        return None
    po = sum(a == b for a, b in pairs) / n
    ca, cb = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / (n * n)
    if pe >= 1.0:
        return None
    return round((po - pe) / (1 - pe), 3)


def _key(v: Any) -> Any:
    return json.dumps(v, sort_keys=True) if isinstance(v, (dict, list)) else v


def field_agreement(a: dict[str, dict], b: dict[str, dict]) -> dict[str, Any]:
    """a, b: {claim_id: evidence}. Fields coded by both coders on the same claim."""
    fields: dict[str, list[tuple[Any, Any]]] = {}
    for cid in sorted(set(a) & set(b)):
        for f in sorted(set(a[cid]) & set(b[cid])):
            fields.setdefault(f, []).append((_key(a[cid][f]), _key(b[cid][f])))
    out = {}
    for f, pairs in fields.items():
        cat = all(isinstance(x, (bool, str)) or x is None for p in pairs for x in p)
        out[f] = {"n": len(pairs), "agree": sum(x == y for x, y in pairs),
                  "agreement": round(sum(x == y for x, y in pairs) / len(pairs), 3),
                  "kappa": cohen_kappa(pairs) if cat else None}
    return out


def compare(rows_a: list[dict], rows_b: list[dict], decide=None) -> dict[str, Any]:
    if decide is None:
        import capas
        decide = capas.decide_external_claim
    import capas
    A = {r["claim_id"]: r["payload"] for r in rows_a}
    B = {r["claim_id"]: r["payload"] for r in rows_b}
    both = sorted(set(A) & set(B))
    fa = field_agreement({c: A[c].get("evidence") or {} for c in both}, {c: B[c].get("evidence") or {} for c in both})
    va, exclusions = [], []
    for c in both:
        ct = (A[c].get("claim") or {}).get("type")
        if ct != (B[c].get("claim") or {}).get("type"):
            exclusions.append({"claim_id": c, "why": "coders chose different claim types"})
            continue
        req = capas.required_fields_for_claim(str(ct), A[c].get("evidence") or {}) or []
        ea, eb = A[c].get("evidence") or {}, B[c].get("evidence") or {}
        dis = [f for f in req if _key(ea.get(f)) != _key(eb.get(f))]
        va.append((decide(A[c])["verdict"], decide(B[c])["verdict"]))
        if dis:
            exclusions.append({"claim_id": c, "why": f"required field(s) disagree: {dis}", "verdict_for_batch": "HOLD"})
    return {"n_a": len(A), "n_b": len(B), "n_both": len(both), "only_a": sorted(set(A) - set(B)), "only_b": sorted(set(B) - set(A)),
            "fields": fa, "verdict_agreement": round(sum(x == y for x, y in va) / len(va), 3) if va else None,
            "verdict_kappa": cohen_kappa(va), "verdict_pairs": dict(Counter(f"{x}/{y}" for x, y in va)),
            "exclusions": exclusions,
            "rule": "a disagreement on a required field excludes the claim from the batch rate and records it as HOLD"}


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print(__doc__); return 2
    load = lambda p: [json.loads(l) for l in Path(p).read_text(encoding="utf-8").splitlines() if l.strip()]
    res = compare(load(argv[1]), load(argv[2]))
    text = json.dumps(res, indent=1, ensure_ascii=False)
    if "--json" in argv:
        Path(argv[argv.index("--json") + 1]).write_text(text + "\n", encoding="utf-8")
    print(f"claims coded by both: {res['n_both']} | verdict agreement {res['verdict_agreement']} kappa {res['verdict_kappa']} | "
          f"exclusions {len(res['exclusions'])}")
    for f, s in sorted(res["fields"].items()):
        print(f"  {f:<34} n={s['n']:<4} agreement={s['agreement']} kappa={s['kappa']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
