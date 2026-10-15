#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""X6 sample draw and primary-coder designation (PREREG §2), run AFTER the tag is pushed.

Seed: the outputValue of the first NIST Randomness Beacon pulse (chain 2) published after the tag push time
(GET https://beacon.nist.gov/beacon/2.0/pulse/time/next/<ms>), read as an integer. The pulse JSON is saved beside the
sample so anyone can check it against the beacon's public record.
Sample: contaminated candidates are removed (their list was sealed); if more than 120 remain, 120 are drawn with
random.Random(seed).sample over the candidates in their sealed order; otherwise all are kept.
Primary coder: the parity of the seed: even -> coder 1, odd -> coder 2.
Output: <out>/sample.jsonl (claim_id, claim_text, excerpt, source_file, assert_commit, line; no outcome exists yet),
<out>/beacon_pulse.json, <out>/DRAW.json.
Run: python3 research/x6_prereg/draw_sample.py --seal SEAL.json --tag-pushed-at 2026-11-20T10:00:00Z --out x6/
     [--pulse saved_pulse.json]   (offline re-derivation from a saved pulse)"""
from __future__ import annotations

import argparse, datetime as dt, hashlib, json, random, sys, urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from x6_common import SAMPLE_MAX, sha256_file  # noqa: E402


def fetch_pulse(after: dt.datetime) -> dict:
    ms = int(after.timestamp() * 1000)
    req = urllib.request.Request(f"https://beacon.nist.gov/beacon/2.0/pulse/time/next/{ms}", headers={"User-Agent": "capas-x6/1.0"})
    return json.loads(urllib.request.urlopen(req, timeout=60).read())


def draw(candidates: list[dict], contaminated: set[str], seed: int) -> list[dict]:
    clean = [c for c in candidates if c["claim_id"] not in contaminated]
    if len(clean) <= SAMPLE_MAX:
        return clean
    picked = set(c["claim_id"] for c in random.Random(seed).sample(clean, SAMPLE_MAX))
    return [c for c in clean if c["claim_id"] in picked]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seal", required=True); ap.add_argument("--tag-pushed-at", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--pulse", help="a saved pulse JSON (re-derivation without network)")
    a = ap.parse_args()
    seal = json.loads(Path(a.seal).read_text(encoding="utf-8"))
    base = Path(a.seal).resolve().parent
    cand_p, cont_p = base / seal["candidates_file"], base / seal["contamination_file"]
    if sha256_file(cand_p) != seal["candidates_sha256"] or sha256_file(cont_p) != seal["contamination_sha256"]:
        print("REFUSED: candidate or contamination list differs from SEAL.json"); return 2
    after = dt.datetime.fromisoformat(a.tag_pushed_at.replace("Z", "+00:00"))
    pulse = json.loads(Path(a.pulse).read_text()) if a.pulse else fetch_pulse(after)
    p = pulse["pulse"]
    if int(p.get("chainIndex", 2)) != 2:
        print("REFUSED: the pulse is not from chain 2"); return 2
    t = dt.datetime.fromisoformat(p["timeStamp"].replace("Z", "+00:00"))
    if t <= after:
        print("REFUSED: the pulse is not later than the tag push"); return 2
    seed = int(p["outputValue"], 16)
    candidates = [json.loads(l) for l in cand_p.read_text(encoding="utf-8").splitlines() if l.strip()]
    contaminated = {json.loads(l)["claim_id"] for l in cont_p.read_text(encoding="utf-8").splitlines() if l.strip()}
    sample = draw(candidates, contaminated, seed)
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    body = "".join(json.dumps(c, ensure_ascii=False, sort_keys=True) + "\n" for c in sample).encode("utf-8")
    (out / "sample.jsonl").write_bytes(body)
    (out / "beacon_pulse.json").write_text(json.dumps(pulse, indent=1), encoding="utf-8")
    draw_rec = {"pulse_uri": p.get("uri"), "pulse_time": p["timeStamp"], "tag_pushed_at": a.tag_pushed_at,
                "seed_hex_prefix": p["outputValue"][:32], "primary_coder": 1 if seed % 2 == 0 else 2,
                "candidates": len(candidates), "contaminated": len(contaminated), "sample": len(sample),
                "sample_sha256": hashlib.sha256(body).hexdigest()}
    (out / "DRAW.json").write_text(json.dumps(draw_rec, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(draw_rec, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
