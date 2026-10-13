#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Run a frozen CAPAS engine on an Atlas claims file and write a SEALED verdict file (sha256 header).
The engine is imported from a git worktree checked out at the declared tag; the header records the commit the
worktree is at, the claims file sha256 and the verdict body sha256. `outcomes_file_opened` is declared by the
caller and must be false for a blind run. No judgement happens here: the engine decides, this script records.

Usage: python3 run_sealed.py <engine_dir> <tag> <claims.jsonl> <out.jsonl> [--opened] [--note "..."]
"""
import datetime as dt, hashlib, importlib, json, subprocess, sys
from pathlib import Path


def main() -> int:
    eng, tag, src, out = sys.argv[1:5]
    opened = "--opened" in sys.argv
    note = sys.argv[sys.argv.index("--note") + 1] if "--note" in sys.argv else ""
    eng = Path(eng).resolve()
    commit = subprocess.run(["git", "--no-optional-locks", "-C", str(eng), "rev-parse", "HEAD"],
                            capture_output=True, text=True, check=True).stdout.strip()
    sys.path.insert(0, str(eng))
    for m in [m for m in list(sys.modules) if m.startswith("capas")]:
        del sys.modules[m]
    capas = importlib.import_module("capas")
    assert Path(capas.__file__).resolve().parent == eng, capas.__file__
    raw = Path(src).read_bytes()
    rows = []
    for line in raw.decode("utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        r = capas.decide_external_claim(rec["payload"])
        rows.append({"claim_id": rec["claim_id"], "contaminado": rec.get("contaminado"),
                     "claim_type": rec["payload"]["claim"]["type"], "verdict": r.get("verdict"),
                     "reason": r.get("reason"), "licensed_claim": r.get("licensed_claim"),
                     "audit_hash": r.get("audit_hash")})
    body = "\n".join(json.dumps(x, ensure_ascii=False, sort_keys=True) for x in rows) + "\n"
    counts: dict[str, int] = {}
    for x in rows:
        counts[x["verdict"]] = counts.get(x["verdict"], 0) + 1
    header = {"_header": True, "engine_tag": tag, "engine_commit": commit,
              "evaluated_at": dt.datetime.now().replace(microsecond=0).isoformat(),
              "claims_sha256": hashlib.sha256(raw).hexdigest(),
              "verdicts_body_sha256": hashlib.sha256(body.encode()).hexdigest(), "n": len(rows),
              "outcomes_file_opened": opened, "blind": not opened, "note": note, "verdict_counts": counts}
    text = json.dumps(header, ensure_ascii=False) + "\n" + body
    Path(out).write_text(text, encoding="utf-8")
    print(f"{tag} {commit[:7]} n={len(rows)} {counts} file_sha256={hashlib.sha256(text.encode()).hexdigest()}")
    for x in rows:
        print(f"  {x['claim_id']}: {x['verdict']} — {x['reason']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
