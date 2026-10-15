#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Writes SEAL.json for X6 (PREREG §9, step 2). Refuses unless the pre-registration is the co-signed version, the
engine tag exists and points at the given commit, and the candidate and contamination lists exist.

SEAL.json carries: the sha256 of the pre-registration; the engine tag and commit; rule_table_sha256 (of the table at
that tag); the sha256 of capas_check.py; judge_prompts_sha256 and the sha256 of run_judges.py, extract_candidates.py,
label_outcomes.py, draw_sample.py, score_x6.py and x6_common.py; the source repository's canonical remote URL and
C0, C1, C2; the sha256 of the candidate and contamination lists; the judge model ids; the date.
It never pushes the tag: it prints the command, which the operator runs (step 4).
Run: python3 research/x6_prereg/seal_prereg.py --engine-tag capas-x6-v1 --repo <ginibre repo> --remote <url>
       --c0 <sha> --c1 <sha> --c2 <sha> --lists <dir with candidates.jsonl + contamination.jsonl> --out SEAL.json [--dry]"""
from __future__ import annotations

import argparse, datetime as dt, hashlib, json, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from x6_common import git, sha256_file  # noqa: E402
import run_judges  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    for k in ("engine-tag", "repo", "remote", "c0", "c1", "c2", "lists", "out"):
        ap.add_argument(f"--{k}", required=True)
    ap.add_argument("--dry", action="store_true", help="print SEAL.json without the co-signature and tag checks")
    a = ap.parse_args()
    if not a.dry:
        if subprocess.run([sys.executable, str(HERE / "check_cosign.py")], capture_output=True).returncode != 0:
            print("REFUSED: the pre-registration is not the co-signed version (run check_cosign.py)"); return 2
    try:
        tag_commit = git(ROOT, "rev-list", "-n", "1", a.engine_tag).strip()
    except subprocess.CalledProcessError:
        tag_commit = None
        if not a.dry:
            print(f"REFUSED: engine tag {a.engine_tag} does not exist locally"); return 2
    lists = Path(a.lists)
    rule_table = git(ROOT, "show", f"{a.engine_tag}:docs/rule_table.json") if tag_commit else (ROOT / "docs" / "rule_table.json").read_text(encoding="utf-8")
    models = list(run_judges.MODELS)
    seal = {
        "prereg_sha256": sha256_file(HERE / "PREREG_CAPAS_VS_LLM_JUDGE.md"),
        "engine": {"tag": a.engine_tag, "commit": tag_commit,
                   "rule_table_sha256": "sha256:" + hashlib.sha256(rule_table.encode("utf-8")).hexdigest(),
                   "capas_check_sha256": sha256_file(ROOT / "capas_check.py")},
        "judge_prompts_sha256": run_judges.judge_prompts_sha256(),
        "scripts_sha256": {p: sha256_file(HERE / p) for p in ("run_judges.py", "extract_candidates.py", "label_outcomes.py",
                                                                "draw_sample.py", "score_x6.py", "x6_common.py")},
        "source_repository": {"remote": a.remote, "c0": a.c0, "c1": a.c1, "c2": a.c2,
                              "c1_date": git(a.repo, "show", "-s", "--format=%cI", a.c1).strip(),
                              "c2_date": git(a.repo, "show", "-s", "--format=%cI", a.c2).strip()},
        "candidates_file": str((lists / "candidates.jsonl").resolve().relative_to(Path(a.out).resolve().parent)) if not a.dry else str(lists / "candidates.jsonl"),
        "contamination_file": str((lists / "contamination.jsonl").resolve().relative_to(Path(a.out).resolve().parent)) if not a.dry else str(lists / "contamination.jsonl"),
        "candidates_sha256": sha256_file(lists / "candidates.jsonl"),
        "contamination_sha256": sha256_file(lists / "contamination.jsonl"),
        "judge_models": models,
        "verdict_files_required": ["capas_verdicts.jsonl", "judges/JUDGES_SEAL.json"],
        "sealed_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "sealed_by": "Krenn-IQ", "note": "timestamps self-recorded; the pushed tag and the public history are the external clock",
    }
    c1_age = (dt.datetime.now(dt.timezone.utc) - dt.datetime.fromisoformat(seal["source_repository"]["c1_date"])).days
    if c1_age < 30 and not a.dry:
        print(f"REFUSED: C1 is {c1_age} days old; PREREG §2 needs at least 30"); return 2
    text = json.dumps(seal, indent=1, sort_keys=True) + "\n"
    if a.dry:
        print(text); print(f"(dry run: C1 is {c1_age} days old)"); return 0
    Path(a.out).write_text(text, encoding="utf-8")
    print(text)
    print(f"next (PREREG §9 step 4): git tag -a {a.engine_tag} {tag_commit} -m 'X6 sealed engine' && git push origin {a.engine_tag}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
