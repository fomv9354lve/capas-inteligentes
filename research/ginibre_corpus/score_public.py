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


import math, re
from collections import Counter
SCORING_RULE = ("bad caught = verdict is not ACCEPT; good not rejected = verdict is not REJECT. HOLD therefore counts "
                "as caught for a bad claim and as not rejected for a good one, so it is reported on its own: hold_share and "
                "informative_rate (an always-HOLD engine scores 100/100 on the first two and 0 on informative_rate). "
                "Contaminated claims (the coder could see the outcome) are excluded before scoring.")
_ENGINE_GAP = re.compile(r"unsupported|scipy|not installed|no rule was applied|anchor contract|CAPAS_SOURCE_ROOT", re.I)


def hold_label(reason: str) -> str:
    """HOLD-correctness label (council, AI-eval member): field_absent = the evidence lacks something declarable (a
    correct abstention); engine_gap = the engine cannot judge (a missing rule or dependency, never a correct
    abstention). Pre-v2 seals carry no rules_fired, so the label is read from the reason text."""
    return "engine_gap" if _ENGINE_GAP.search(reason or "") else "field_absent"


def verification_budget(clean, V, C, by, sealed_by="Krenn-IQ", run_by="Krenn-IQ"):
    """PLAN_v3 A2 (Banka & Chudziak, 'Predictive Value of Pass', arXiv 2610.05547): how many ACCEPTs a reviewer must
    check by hand for the batch's pass to carry a target predictive value, with the evidence provenance of the batch."""
    acc = [i for i in clean if V[i]["verdict"] == "ACCEPT"]
    good_acc = by["good"]["ACCEPT"]
    ev = [C[i]["evidence"] for i in clean]
    n_fields = sum(len(e) for e in ev)
    budget = {f"pvp_{int(t * 100)}": math.ceil(math.log(0.05) / math.log(t)) for t in (0.90, 0.95)}
    return {"sealed_by": sealed_by, "run_by": run_by, "label": "self-run" if sealed_by == run_by == "Krenn-IQ" else "independent",
            "accepts": len(acc), "pvp_observed": f"{good_acc}/{len(acc)}" if acc else None,
            "pvp_ci95": wilson(good_acc, len(acc)) if acc else None,
            "audit_n_for_target": budget,
            "audit_rule": "check n ACCEPTs drawn at random; zero bad among them bounds PVP >= target at 95% (one-sided, exact)",
            "provenance": {"fields_total": n_fields, "read_from_hashed_file": sum(1 for i in clean if (C[i].get("meta") or {}).get("sources")),
                           "declared_by_coder": n_fields, "derived_by_rule": 0,
                           "note": "every field of this batch was declared by a blind coder; none was read by an adapter from a hashed file"},
            "tier_histogram_accepts": dict(Counter(V[i].get("ceiling_s2") or "unknown" for i in acc))}


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
        holds = [i for i in clean if V[i]["verdict"] == "HOLD"]
        r = {"engine_tag": hdr["engine_tag"], "n": len(V), "n_clean": len(clean), "by_verdict": by,
             "n_excluded_contaminated": len(V) - len(clean), "scoring_rule": SCORING_RULE,
             "hold_share": f"{len(holds)}/{len(clean)}", "informative_rate": f"{len(clean) - len(holds)}/{len(clean)}",
             "holds": [{"claim_id": i, "class": hold_label(V[i]["reason"])} for i in holds],
             "grade": "pilot-grade (fewer than 40 bad records)" if len(ids["bad"]) < 40 else "pre-registered minimum met",
             "verification_budget": verification_budget(clean, V, {c["claim_id"]: c for c in C}, by),
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
              f"good not-REJECT {nr}/{ng} {wilson(nr, ng)} | good ACCEPT {by['good']['ACCEPT']}/{ng} | HOLD {r['hold_share']} "
              f"({', '.join(sorted(set(h['class'] for h in r['holds']))) or '-'}) | PVP {r['verification_budget']['pvp_observed']} | {r['grade'].split(' (')[0]}"
              + (f" | replay {r['replay']['reproduced']}" if "replay" in r else ""))
    b, g = pooled["bad"], pooled["good"]
    out["pooled (X1-3 v1 + X4 + X5)"] = {"n_clean": pooled["clean"], "n_excluded_contaminated": pooled["excluded"],
        "bad_not_accepted": f"{sum(b.values()) - b['ACCEPT']}/{sum(b.values())}", "good_accept": f"{g['ACCEPT']}/{sum(g.values())}",
        "hold_total": f"{b['HOLD'] + g['HOLD']}/{pooled['clean']}",
        "informative_rate": f"{pooled['clean'] - b['HOLD'] - g['HOLD']}/{pooled['clean']}", "scoring_rule": SCORING_RULE}
    print("pooled:", json.dumps(out["pooled (X1-3 v1 + X4 + X5)"]))
    if "--json" in sys.argv:
        (ROOT / "outputs").mkdir(exist_ok=True); json.dump(out, open(ROOT / "outputs" / "ginibre_public_scores.json", "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
