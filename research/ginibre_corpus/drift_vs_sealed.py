#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Engine drift vs the SEALED verdict files (X1-3 v2, X4 v4, X5 v6): re-decide every sealed payload with the
CURRENT tree and list every verdict flip with its reason and the known outcome. POST-HOC by construction
(outcomes are known): it measures what a rule change does to the sealed corpora, never a rate.
Run: python3 research/ginibre_corpus/drift_vs_sealed.py  -> outputs/engine_vs_sealed.json + table on stdout"""
import collections, json, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT))
import capas
import os
G = Path(os.environ.get("CAPAS_GINIBRE_CORPUS") or "/Users/kreniq/Desktop/KRENIQ/AI Projects/01. Investigacion/Paper - Inverse Ginibre Overlap/CAPAS_CORPUS_2026-10-12")  # corpus is private (unpublished paper)
SETS = [("X1-3", "PARA_CAPAS_claims.jsonl", "PARA_CAPAS_desenlaces.jsonl", "DE_CAPAS_veredictos_v2.jsonl"),
        ("X4", "PARA_CAPAS_claims_X4.jsonl", "PARA_CAPAS_desenlaces_X4.jsonl", "DE_CAPAS_veredictos_X4.jsonl"),
        ("X5", "PARA_CAPAS_claims_X5.jsonl", "PARA_CAPAS_desenlaces_X5.jsonl", "DE_CAPAS_veredictos_X5.jsonl")]
L = lambda p: [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def main() -> int:
    if not G.exists():
        print("SKIP: corpus not present"); return 2
    head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    flips, kinds = [], collections.Counter()
    for name, cf, of, vf in SETS:
        O = {o["claim_id"]: o["outcome"] for o in L(G / of)}
        S = {v["claim_id"]: v for v in L(G / vf) if not v.get("_header")}
        for rec in L(G / cf):
            cid = rec["claim_id"]; d = capas.decide_external_claim(rec["payload"]); d = d.get("decision", d)
            if d["verdict"] != S[cid]["verdict"]:
                out = O[cid]; s, v = S[cid]["verdict"], d["verdict"]
                kind = ("bad: ACCEPT->caught" if out == "malo" and s == "ACCEPT" and v != "ACCEPT" else
                        "good: loses ACCEPT" if out == "bueno" and s == "ACCEPT" and v != "REJECT" else
                        "good: ->REJECT" if out == "bueno" and v == "REJECT" else "other")
                kinds[kind] += 1
                flips.append({"set": name, "claim_id": cid, "contaminado": rec.get("contaminado"), "type": rec["payload"]["claim"]["type"],
                              "sealed": s, "now": v, "outcome": out, "kind": kind, "reason": (d.get("reason") or "")[:160]})
    res = {"engine_head": head, "n_flips": len(flips), "kinds": dict(kinds), "flips": flips,
           "note": "POST-HOC: outcomes known; measures the effect of rule changes on sealed corpora, not a rate"}
    (ROOT / "outputs").mkdir(exist_ok=True); json.dump(res, open(ROOT / "outputs" / "engine_vs_sealed.json", "w"), ensure_ascii=False, indent=1)
    print(f"engine {head} vs sealed: {len(flips)} flips | {dict(kinds)}")
    for f in flips: print(f"  {f['set']:<5} {f['claim_id']} {'C' if f['contaminado'] else ' '} {f['type']:<24} {f['sealed']:<8}-> {f['now']:<8} {f['outcome']:<6} {f['reason'][:70]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
