#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""X6 outcome labelling (PREREG §2), mechanical, run only AFTER every arm's verdicts are sealed.

A claim is `malo` when a commit of the source repository after its assert commit and no later than C2 marks it
corrected, withdrawn or refuted. "Marks" is decided by the fixed vocabulary x6_common.OUTCOME_WORDS, by three rules:
  deleted_with_outcome   a later commit deletes the claim line, and that commit's message or the lines it adds to the
                         same file carry an outcome word
  marked_in_place        a later revision of the source file has a line with the claim's 40-character key and an
                         outcome word
  marked_elsewhere       at C2, any text file of the repository has a line with the claim's key and an outcome word
Otherwise `bueno` (never corrected; PREREG §7 states the survival bias this carries). Commits after C2 are never read.
Run: python3 research/x6_prereg/label_outcomes.py --repo <path> --c2 <sha> --candidates candidates.jsonl --out outcomes.jsonl
     (refuses unless --sealed <SEAL.json> names the same C2 and the verdict files listed in it exist)"""
from __future__ import annotations

import argparse, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from x6_common import OUTCOME_WORDS, TEXT_SUFFIXES, claim_key, file_at, git, norm  # noqa: E402


def label(repo: str, c2: str, cand: dict) -> dict:
    key, text, path, start = claim_key(cand["claim_text"]), cand["claim_text"].strip(), cand["source_file"], cand["assert_commit"]
    commits = git(repo, "rev-list", "--reverse", f"{start}..{c2}", "--", path).split()
    for c in commits:
        diff = git(repo, "show", "--format=%B%x00", "--unified=0", "--no-color", c, "--", path)
        msg, _, body = diff.partition("\x00")
        deleted = any(l.startswith("-") and not l.startswith("---") and l[1:].strip() == text for l in body.splitlines())
        added = "\n".join(l[1:] for l in body.splitlines() if l.startswith("+") and not l.startswith("+++"))
        if deleted and (OUTCOME_WORDS.search(msg) or OUTCOME_WORDS.search(added)):
            return {"claim_id": cand["claim_id"], "outcome": "malo", "outcome_type": "deleted_with_outcome", "evidence_commit": c}
        for line in file_at(repo, c, path).splitlines():
            if key and key in norm(line) and OUTCOME_WORDS.search(line):
                return {"claim_id": cand["claim_id"], "outcome": "malo", "outcome_type": "marked_in_place", "evidence_commit": c}
    for p in git(repo, "ls-tree", "-r", "--name-only", c2).splitlines():
        if not p.endswith(TEXT_SUFFIXES):
            continue
        for line in file_at(repo, c2, p).splitlines():
            if key and key in norm(line) and OUTCOME_WORDS.search(line):
                return {"claim_id": cand["claim_id"], "outcome": "malo", "outcome_type": "marked_elsewhere", "evidence_commit": c2,
                        "evidence_file": p}
    return {"claim_id": cand["claim_id"], "outcome": "bueno", "outcome_type": "never_corrected", "evidence_commit": None}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True); ap.add_argument("--c2", required=True)
    ap.add_argument("--candidates", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--sealed", help="SEAL.json; required unless --test")
    ap.add_argument("--test", action="store_true", help="synthetic repositories only (tests)")
    a = ap.parse_args()
    if not a.test:
        if not a.sealed or not Path(a.sealed).is_file():
            print("REFUSED: outcomes are labelled only after sealing (PREREG §2); pass --sealed SEAL.json"); return 2
        seal = json.loads(Path(a.sealed).read_text(encoding="utf-8"))
        if seal.get("source_repository", {}).get("c2") != a.c2:
            print("REFUSED: --c2 differs from the C2 in SEAL.json"); return 2
        missing = [f for f in seal.get("verdict_files_required", []) if not Path(f).is_file()]
        if missing:
            print(f"REFUSED: sealed verdict files are missing: {missing}"); return 2
    rows = [json.loads(l) for l in Path(a.candidates).read_text(encoding="utf-8").splitlines() if l.strip()]
    out = [label(a.repo, a.c2, r) for r in rows]
    Path(a.out).write_text("".join(json.dumps(o, ensure_ascii=False, sort_keys=True) + "\n" for o in out), encoding="utf-8")
    print(json.dumps({"labelled": len(out), "malo": sum(o["outcome"] == "malo" for o in out),
                      "bueno": sum(o["outcome"] == "bueno" for o in out)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
