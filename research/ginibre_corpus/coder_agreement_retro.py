#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Retroactive coder agreement on the one field of the blind corpus that two sessions coded independently
(PLAN_v3 A4, owner 2026-10-14). On 2026-10-13 a second blind session re-coded `steps_all_valid` for the 22 X1-3
proof claims that the first coder had coded False (RECODIF_VALIDEZ.md): declara_hueco -> False, declara_valido ->
True, no_dice -> not coded.

Limits stated in the output: the 22 were SELECTED on coder A's value (all False), so kappa is not informative
(coder A is constant); both coders are AI sessions run by Krenn-IQ ("self-run"); in-sample (outcomes known when this
is published). It is the first agreement figure, not the protocol's: from X6 the two coders are the network's.

Author side (needs the private corpus) writes research/ginibre_corpus/public/coder_agreement_steps_all_valid.json;
anyone re-derives the figures from that file with --public.
Run: python3 research/ginibre_corpus/coder_agreement_retro.py [--public]"""
import json, os, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT))
from capas_coders import cohen_kappa  # noqa: E402

G = Path(os.environ.get("CAPAS_GINIBRE_CORPUS") or
         "/Users/kreniq/Desktop/KRENIQ/AI Projects/01. Investigacion/Paper - Inverse Ginibre Overlap/CAPAS_CORPUS_2026-10-12")
PUB = ROOT / "research" / "ginibre_corpus" / "public" / "coder_agreement_steps_all_valid.json"
MAP = {"declara_hueco": False, "declara_valido": True, "no_dice": None}


def summarize(pairs: list[dict]) -> dict:
    coded = [p for p in pairs if p["coder_b"] is not None]
    return {"field": "steps_all_valid", "n_claims": len(pairs), "n_coded_by_both": len(coded),
            "agree": sum(p["coder_a"] == p["coder_b"] for p in coded),
            "agreement": f"{sum(p['coder_a'] == p['coder_b'] for p in coded)}/{len(pairs)} (no_dice counted as disagreement)",
            "kappa": cohen_kappa([(p["coder_a"], p["coder_b"]) for p in coded]),
            "kappa_note": "not informative: the 22 were selected on coder A's value (all False), so coder A is constant",
            "run": "self-run (both coders are Krenn-IQ AI sessions), in-sample"}


def main() -> int:
    if "--public" in sys.argv:
        d = json.loads(PUB.read_text(encoding="utf-8"))
        s = summarize(d["pairs"])
        ok = all(s[k] == d["summary"][k] for k in ("n_claims", "n_coded_by_both", "agree", "kappa"))
        print(json.dumps(s, indent=1)); print("PASS — summary re-derived from the public pairs" if ok else "FAIL — summary differs")
        return 0 if ok else 1
    if not G.exists():
        print("SKIP: private corpus not on this machine; use --public"); return 2
    A = {json.loads(l)["claim_id"]: json.loads(l) for l in open(G / "PARA_CAPAS_claims.jsonl", encoding="utf-8")}
    pairs = []
    for line in open(G / "recodif_validez.jsonl", encoding="utf-8"):
        r = json.loads(line)
        pairs.append({"claim_id": r["id"], "contaminado": r["contaminado"],
                      "coder_a": A[r["id"]]["payload"]["evidence"].get("steps_all_valid"), "coder_b": MAP[r["decision"]]})
    out = {"source": "RECODIF_VALIDEZ.md protocol, 2026-10-13; quotes withheld (unpublished paper)", "pairs": pairs, "summary": summarize(pairs)}
    PUB.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(out["summary"], indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
