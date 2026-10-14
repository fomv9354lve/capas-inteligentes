#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Third-party check of the blind-corpus figures from the PUBLIC redacted files (research/ginibre_corpus/public/),
on any clone, without the private corpus.
  1. integrity: every public file matches MANIFEST.json; claim_ids line up across claims, verdicts and outcomes.
  2. figures: verdicts x outcome labels -> the same numbers score_sealed.py derives from the sealed originals.
  3. --replay: re-decides every redacted payload with the engine at the set's frozen tag (git worktree) and counts
     how many sealed verdicts it reproduces. The claim text and free-text fields are hashes here, so a verdict that
     depended on the wording may not reproduce; the mismatches are listed, not hidden.
What this cannot check: that the verdicts were sealed before the outcomes were known (the timestamps are
self-recorded), and that the claim texts behind the hashes are the paper's (checkable once the paper is public).
Run: python3 research/ginibre_corpus/score_public.py [--replay] [--json]"""
import hashlib, json, subprocess, sys, tempfile
from math import sqrt
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]; P = ROOT / "research" / "ginibre_corpus" / "public"
L = lambda p: [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
# The figures the site publishes; a mismatch is a FAIL, not a new number.
PUBLISHED = {"X1-3_v1": ("53/82", "51/63"), "X1-3_v2": ("53/82", "52/63"), "X4": ("11/13", "6/7"), "X5": ("6/8", "10/10")}
# X4-014: its sealed REWRITE came from the wording rule on convergence, which reads the claim text (a hash here).
# It is contaminated, so it is not in any figure. Any other replay mismatch is a FAIL.
TEXT_DEPENDENT = {"X4-014"}


def wilson(k, n, z=1.96):
    if n == 0: return (None, None)
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return round(c - h, 2), round(c + h, 2)


def replay(tag, claims):
    with tempfile.TemporaryDirectory() as td:
        wt = Path(td) / "wt"
        subprocess.run(["git", "worktree", "add", "--detach", str(wt), tag], cwd=ROOT, check=True, capture_output=True)
        try:
            prog = ("import json,sys; sys.path.insert(0,'.'); import capas\n"
                    "for l in sys.stdin:\n r=json.loads(l); p={'schema_version':r['schema_version'],'claim':{'id':r['claim']['id'],"
                    "'type':r['claim']['type'],'text':'sha256:'+r['claim']['text_sha256']},'evidence':r['evidence']}\n"
                    " d=capas.decide_external_claim(p); d=d.get('decision',d); print(json.dumps({'claim_id':r['claim_id'],'verdict':d['verdict']}))")
            res = subprocess.run([sys.executable, "-c", prog], cwd=wt, input="".join(json.dumps(c) + "\n" for c in claims),
                                 capture_output=True, text=True, check=True)
            return {r["claim_id"]: r["verdict"] for r in map(json.loads, res.stdout.splitlines())}
        finally:
            subprocess.run(["git", "worktree", "remove", "--force", str(wt)], cwd=ROOT, capture_output=True)


def main() -> int:
    man = json.loads((P / "MANIFEST.json").read_text(encoding="utf-8"))
    for f, h in man["public"].items():
        if hashlib.sha256((P / f).read_bytes()).hexdigest() != h:
            print(f"FAIL: {f} does not match MANIFEST.json"); return 1
    out, pooled = {}, {"bad": {}, "good": {}, "clean": 0, "excluded": 0}
    for name in ("X1-3_v1", "X1-3_v2", "X4", "X5"):
        C, V, O = (L(P / f"{k}_{name}.jsonl") for k in ("claims", "verdicts", "outcomes"))
        hdr, V = V[0], {v["claim_id"]: v for v in V[1:]}; O = {o["claim_id"]: o["outcome"] for o in O}
        if not (set(V) == set(O) == {c["claim_id"] for c in C}):
            print(f"FAIL {name}: claim_ids differ across files"); return 1
        clean = [i for i in V if not V[i]["contaminado"]]
        ids = {"bad": [i for i in clean if O[i] == "malo"], "good": [i for i in clean if O[i] == "bueno"]}
        by = {k: {v: sum(V[i]["verdict"] == v for i in ids[k]) for v in ("ACCEPT", "REWRITE", "REJECT", "HOLD")} for k in ids}
        nb, ng = len(ids["bad"]), len(ids["good"]); det = nb - by["bad"]["ACCEPT"]; nr = ng - by["good"]["REJECT"]
        r = {"engine_tag": hdr["engine_tag"], "n": len(V), "n_clean": len(clean), "by_verdict": by,
             "bad_not_accepted": f"{det}/{nb}", "bad_ci95": wilson(det, nb), "good_not_rejected": f"{nr}/{ng}", "good_ci95": wilson(nr, ng),
             "good_accept": f"{by['good']['ACCEPT']}/{ng}", "outcomes_file_opened_self_recorded": hdr.get("outcomes_file_opened")}
        if name != "X1-3_v2":
            pooled["clean"] += len(clean); pooled["excluded"] += len(V) - len(clean)
            for k in by:
                for v, n in by[k].items(): pooled[k][v] = pooled[k].get(v, 0) + n
        if "--replay" in sys.argv:
            got = replay(hdr["engine_tag"], C)
            miss = [i for i in V if got[i] != V[i]["verdict"]]
            r["replay"] = {"reproduced": f"{len(V) - len(miss)}/{len(V)}",
                           "mismatches": [{"claim_id": i, "sealed": V[i]["verdict"], "replayed": got[i]} for i in miss]}
        if (r["bad_not_accepted"], r["good_not_rejected"]) != PUBLISHED[name]:
            print(f"FAIL {name}: {r['bad_not_accepted']}, {r['good_not_rejected']} != published {PUBLISHED[name]}"); return 1
        if "replay" in r and {m["claim_id"] for m in r["replay"]["mismatches"]} - TEXT_DEPENDENT:
            print(f"FAIL {name}: replay mismatches {r['replay']['mismatches']}"); return 1
        out[name] = r
        print(f"{name}: tag {hdr['engine_tag']} | clean {len(clean)} | bad not-ACCEPT {det}/{nb} {wilson(det, nb)} | "
              f"good not-REJECT {nr}/{ng} {wilson(nr, ng)} | good ACCEPT {by['good']['ACCEPT']}/{ng}"
              + (f" | replay {r['replay']['reproduced']}" if "replay" in r else ""))
    b, g = pooled["bad"], pooled["good"]
    out["pooled (X1-3 v1 + X4 + X5)"] = {"n_clean": pooled["clean"], "n_excluded_contaminated": pooled["excluded"],
        "bad_not_accepted": f"{sum(b.values()) - b['ACCEPT']}/{sum(b.values())}", "good_accept": f"{g['ACCEPT']}/{sum(g.values())}",
        "hold_total": f"{b['HOLD'] + g['HOLD']}/{pooled['clean']}"}
    print("pooled:", json.dumps(out["pooled (X1-3 v1 + X4 + X5)"]))
    if "--json" in sys.argv:
        (ROOT / "outputs").mkdir(exist_ok=True); json.dump(out, open(ROOT / "outputs" / "ginibre_public_scores.json", "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
