#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""X6 candidate extraction (PREREG §2), deterministic, run BEFORE sealing.

Candidates: every claim-bearing line ADDED in commits C0..C1 of the source repository (git log --reverse C0..C1),
in text files (.md/.tex/.txt) outside earlier corpus folders. A line is claim-bearing when it carries an assertion
marker (x6_common.ASSERTION_MARKERS) and has at least 40 characters. The assert commit is the commit that added it.
Each candidate gets the excerpt of PREREG §2: lines L-40..L+40 of the file at the assert commit, truncated
symmetrically to 12,000 characters. Duplicates (same normalised text) keep the first occurrence.

Contamination (PREREG §2): a candidate is contaminated when its WHOLE source file at the assert commit already carries
an outcome word (x6_common.OUTCOME_WORDS) for that claim: on the claim line itself, or on any line containing the
claim's 40-character key. Computed here, before sealing; no claim is excluded for contamination later.

Writes candidates.jsonl and contamination.jsonl (sha256 of both go in SEAL.json). Prints counts only.
Run: python3 research/x6_prereg/extract_candidates.py --repo <path> --c0 <sha> --c1 <sha> --out <dir>"""
from __future__ import annotations

import argparse, json, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from x6_common import (ASSERTION_MARKERS, EXCERPT_MAX_CHARS, EXCERPT_RADIUS, EXCLUDED_DIRS, MIN_CLAIM_CHARS,  # noqa: E402
                       OUTCOME_WORDS, TEXT_SUFFIXES, claim_key, file_at, git, norm, sha256_bytes)


def excerpt(lines: list[str], idx: int) -> str:
    lo, hi = max(0, idx - EXCERPT_RADIUS), min(len(lines), idx + EXCERPT_RADIUS + 1)
    text = "\n".join(lines[lo:hi])
    if len(text) <= EXCERPT_MAX_CHARS:
        return text
    # symmetric truncation around the claim line
    centre = len("\n".join(lines[lo:idx])) + 1
    half = EXCERPT_MAX_CHARS // 2
    start = max(0, min(centre - half, len(text) - EXCERPT_MAX_CHARS))
    return text[start:start + EXCERPT_MAX_CHARS]


def added_lines(repo: str, commit: str) -> list[tuple[str, int, str]]:
    """(path, 1-based line number in the new file, text) for every line the commit adds to an eligible file."""
    out, path, new_no = [], None, 0
    diff = git(repo, "show", "--format=", "--unified=0", "--no-color", "--no-renames", commit)
    for raw in diff.splitlines():
        if raw.startswith("+++ "):
            p = raw[4:]
            path = p[2:] if p.startswith("b/") else None
            if path and (not path.endswith(TEXT_SUFFIXES) or any(d in path for d in EXCLUDED_DIRS)):
                path = None
        elif raw.startswith("@@"):
            m = re.search(r"\+(\d+)(?:,(\d+))?", raw)
            new_no = int(m.group(1)) if m else 0
        elif raw.startswith("+") and not raw.startswith("+++") and path:
            out.append((path, new_no, raw[1:]))
            new_no += 1
        elif raw.startswith(" ") and path:
            new_no += 1
    return out


def contaminated(lines: list[str], idx: int, key: str) -> bool:
    if OUTCOME_WORDS.search(lines[idx]):
        return True
    return any(key and key in norm(l) and OUTCOME_WORDS.search(l) for l in lines)


def extract(repo: str, c0: str, c1: str) -> tuple[list[dict], list[dict]]:
    commits = git(repo, "rev-list", "--reverse", "--topo-order", f"{c0}..{c1}").split()
    cands, contam, seen = [], [], set()
    for commit in commits:
        for path, line_no, text in added_lines(repo, commit):
            t = text.strip()
            if len(t) < MIN_CLAIM_CHARS or not ASSERTION_MARKERS.search(t) or t.startswith(("```", "|---")):
                continue
            k = norm(t)
            if k in seen:
                continue
            seen.add(k)
            lines = file_at(repo, commit, path).splitlines()
            idx = min(max(line_no - 1, 0), max(len(lines) - 1, 0))
            if not lines or lines[idx].strip() != t:            # locate by content when the hunk numbering drifted
                idx = next((i for i, l in enumerate(lines) if l.strip() == t), idx)
            cid = "X6-" + sha256_bytes(f"{commit}:{path}:{t}".encode())[:10]
            row = {"claim_id": cid, "claim_text": t, "source_file": path, "assert_commit": commit, "line": idx + 1,
                   "excerpt": excerpt(lines, idx) if lines else t}
            cands.append(row)
            if lines and contaminated(lines, idx, claim_key(t)):
                contam.append({"claim_id": cid, "reason": "outcome word for this claim in its source file at the assert commit"})
    return cands, contam


def dump(rows: list[dict]) -> bytes:
    return "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in rows).encode("utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True); ap.add_argument("--c0", required=True); ap.add_argument("--c1", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    cands, contam = extract(a.repo, a.c0, a.c1)
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    cb, kb = dump(cands), dump(contam)
    (out / "candidates.jsonl").write_bytes(cb); (out / "contamination.jsonl").write_bytes(kb)
    print(json.dumps({"candidates": len(cands), "contaminated": len(contam), "candidates_sha256": sha256_bytes(cb),
                      "contamination_sha256": sha256_bytes(kb), "c0": a.c0, "c1": a.c1}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
