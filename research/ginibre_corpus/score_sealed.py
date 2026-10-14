#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Recompute the blind-corpus figures from the SEALED files only (no engine run, no outcomes-at-coding-time):
verifies each verdict file's claims_sha256 against the claims file, then crosses verdicts x outcomes.
Figures: X1-3 (blind, v2), X4 (out-of-sample, v4), X5 (out-of-sample, v6), cumulative X4+X5.
Run: python3 research/ginibre_corpus/score_sealed.py [--json]"""
import hashlib, json, sys
from math import sqrt
from pathlib import Path
# The sealed corpus lives with the (not yet public) Ginibre paper, OUTSIDE this repo: claim texts and outcome notes
# quote unpublished results. Override with CAPAS_GINIBRE_CORPUS=<dir>. Absent dir -> rc 2 (SKIP, "cannot verify
# here"), never rc 0 (the figures are not re-derived) and never rc 1 (nothing was found broken).
import os
G = Path(os.environ.get("CAPAS_GINIBRE_CORPUS") or
         "/Users/kreniq/Desktop/KRENIQ/AI Projects/01. Investigacion/Paper - Inverse Ginibre Overlap/CAPAS_CORPUS_2026-10-12")
# X1-3 uses the v1 seal (00:14, outcomes_file_opened: false). v2 (00:18) applied one rule change made at 00:16 and its
# header does not record the flag, so it cannot carry the phrase "sealed before outcomes were opened" (external
# re-audit 2026-10-14). v2 is reported beside it, labelled.
SETS = [("X1-3 (blind, v1)", "PARA_CAPAS_claims.jsonl", "PARA_CAPAS_desenlaces.jsonl", "DE_CAPAS_veredictos.jsonl"),
        ("X4 (out-of-sample, v4)", "PARA_CAPAS_claims_X4.jsonl", "PARA_CAPAS_desenlaces_X4.jsonl", "DE_CAPAS_veredictos_X4.jsonl"),
        ("X5 (out-of-sample, v6)", "PARA_CAPAS_claims_X5.jsonl", "PARA_CAPAS_desenlaces_X5.jsonl", "DE_CAPAS_veredictos_X5.jsonl")]


def wilson(k, n, z=1.96):
    if n == 0: return (None, None)
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return round(c - h, 2), round(c + h, 2)


def load(p): return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def main() -> int:
    if not G.exists():
        print(f"SKIP: corpus dir not present ({G})"); return 2
    out, agg = {}, {"mal_det": 0, "mal": 0, "bue_nr": 0, "bue": 0}
    for name, cf, of, vf in SETS:
        rows = load(G / vf); hdr = rows[0]; V = {r["claim_id"]: r for r in rows[1:]}
        sha = hashlib.sha256((G / cf).read_bytes()).hexdigest()
        if sha != hdr["claims_sha256"]:
            print(f"FAIL {name}: claims sha256 {sha[:12]} != header {hdr['claims_sha256'][:12]}"); return 1
        body = "\n".join(json.dumps(x, ensure_ascii=False) for x in rows[1:]) + "\n"
        O = {o["claim_id"]: o["outcome"] for o in load(G / of)}
        clean = [i for i in V if not V[i]["contaminado"]]
        mal = [i for i in clean if O[i] == "malo"]; bue = [i for i in clean if O[i] == "bueno"]
        det = sum(V[i]["verdict"] != "ACCEPT" for i in mal); nr = sum(V[i]["verdict"] != "REJECT" for i in bue)
        by = {cls: {v: sum(1 for i in ids if V[i]["verdict"] == v) for v in ("ACCEPT", "REWRITE", "REJECT", "HOLD")}
              for cls, ids in (("bad", mal), ("good", bue))}
        out[name] = {"by_verdict": by, "n_excluded_contaminated": len(V) - len(clean),
                     "hold_share": round((by["bad"]["HOLD"] + by["good"]["HOLD"]) / max(1, len(clean)), 3),
                     "good_accept": f"{by['good']['ACCEPT']}/{len(bue)}",
                     "engine_tag": hdr["engine_tag"], "engine_commit": hdr["engine_commit"][:7], "claims_sha256": sha[:12],
                     "outcomes_opened_before_sealing": hdr.get("outcomes_file_opened", None), "n_clean": len(clean),
                     "bad_not_accepted": f"{det}/{len(mal)}", "bad_rate": round(det / len(mal), 2), "bad_ci95": wilson(det, len(mal)),
                     "good_not_rejected": f"{nr}/{len(bue)}", "good_rate": round(nr / len(bue), 2), "good_ci95": wilson(nr, len(bue))}
        agg.setdefault("by", {"bad": {}, "good": {}})
        for cls in ("bad", "good"):
            for v, n in by[cls].items():
                agg["by"][cls][v] = agg["by"][cls].get(v, 0) + n
        agg["clean"] = agg.get("clean", 0) + len(clean); agg["excluded"] = agg.get("excluded", 0) + len(V) - len(clean)
        if "out-of-sample" in name:
            agg["mal_det"] += det; agg["mal"] += len(mal); agg["bue_nr"] += nr; agg["bue"] += len(bue)
        print(f"{name}: tag {hdr['engine_tag']} | clean {len(clean)} | bad not-ACCEPT {det}/{len(mal)} {wilson(det, len(mal))} | good not-REJECT {nr}/{len(bue)} {wilson(nr, len(bue))}")
    out["X4+X5 (out-of-sample, cumulative)"] = {"bad_not_accepted": f"{agg['mal_det']}/{agg['mal']}", "bad_ci95": wilson(agg["mal_det"], agg["mal"]),
                                                "good_not_rejected": f"{agg['bue_nr']}/{agg['bue']}", "good_ci95": wilson(agg["bue_nr"], agg["bue"])}
    print(f"X4+X5 cumulative (engine frozen BEFORE coding, verdicts sealed BEFORE outcomes): bad not-ACCEPT {agg['mal_det']}/{agg['mal']} "
          f"{wilson(agg['mal_det'], agg['mal'])} | good not-REJECT {agg['bue_nr']}/{agg['bue']} {wilson(agg['bue_nr'], agg['bue'])}")
    b = agg["by"]
    out["pooled X1-5 (blind, v1 + X4 + X5)"] = {"by_verdict": b, "n_clean": agg["clean"], "n_excluded_contaminated": agg["excluded"],
        "bad_not_accepted": f"{agg['clean'] and sum(b['bad'].values()) - b['bad']['ACCEPT']}/{sum(b['bad'].values())}",
        "good_not_rejected": f"{sum(b['good'].values()) - b['good']['REJECT']}/{sum(b['good'].values())}",
        "good_accept": f"{b['good']['ACCEPT']}/{sum(b['good'].values())}",
        "good_accept_or_rewrite": f"{b['good']['ACCEPT'] + b['good']['REWRITE']}/{sum(b['good'].values())}",
        "hold_total": f"{b['bad']['HOLD'] + b['good']['HOLD']}/{agg['clean']}"}
    # v2 of X1-3, reported beside v1, labelled: one rule change after v1; outcomes-opened flag not recorded
    rows2 = load(G / "DE_CAPAS_veredictos_v2.jsonl"); V2 = {r["claim_id"]: r for r in rows2[1:]}; O1 = {o["claim_id"]: o["outcome"] for o in load(G / "PARA_CAPAS_desenlaces.jsonl")}
    c2 = [i for i in V2 if not V2[i]["contaminado"]]; m2 = [i for i in c2 if O1[i] == "malo"]; g2 = [i for i in c2 if O1[i] == "bueno"]
    out["X1-3 v2 (one rule change after v1; outcomes-opened flag NOT recorded)"] = {
        "bad_not_accepted": f"{sum(V2[i]['verdict'] != 'ACCEPT' for i in m2)}/{len(m2)}", "good_not_rejected": f"{sum(V2[i]['verdict'] != 'REJECT' for i in g2)}/{len(g2)}"}
    Path("outputs").mkdir(exist_ok=True)
    json.dump(out, open("outputs/ginibre_sealed_scores.json", "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
