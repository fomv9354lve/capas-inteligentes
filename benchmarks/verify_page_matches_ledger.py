#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""docs/in-depth.html lists the public numbers under CLOSED / BACKED / SCOPED headers. Each line names its command; the
proof ledger (docs/proof_ledger.json) names the same command in `backing` with the authoritative status. The page
must agree with the ledger: same status, and no line without a ledger entry. (External audit 2026-10-13: three lines
sat under the wrong header; the release gate only checked for orphans, not labels.)
Run: python3 benchmarks/verify_page_matches_ledger.py"""
from __future__ import annotations
import json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
PAGE, LEDGER = ROOT / "docs" / "in-depth.html", ROOT / "docs" / "proof_ledger.json"
HEADERS = {"CLOSED &middot;": "CLOSED", "BACKED &middot;": "BACKED", "SCOPED &middot;": "SCOPED"}


def main() -> int:
    html = PAGE.read_text(encoding="utf-8"); ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    by_cmd = {}
    for e in ledger:
        for m in re.finditer(r"((?:benchmarks|research|scripts)/\S+?\.py)", e.get("backing", "")):   # with or without 'python3 '
            by_cmd[m.group(1)] = e
    a = html.index("CLOSED &middot;"); b = html.index("WHAT IS <em>NOT</em> VALIDATED", a)
    seg = html[a:b]; block = None; errs = []; seen = 0
    for m in re.finditer(r'(CLOSED &middot;|BACKED &middot;|SCOPED &middot;)|<li data-es="[^"]*">(.*?)</li>', seg, re.S):
        if m.group(1):
            block = HEADERS[m.group(1)]; continue
        cmds = re.findall(r"python3 (?:-m pytest (?:-q )?)?(\S+\.py)", re.sub(r"<[^>]+>", "", m.group(2)))
        if not cmds:
            errs.append(f"[{block}] line without a command: {re.sub(r'<[^>]+>', '', m.group(2))[:60]!r}"); continue
        seen += 1
        e = next((by_cmd[c] for c in cmds if c in by_cmd), None)
        if e is None:
            errs.append(f"[{block}] no ledger entry backs {cmds}"); continue
        if e["status"] != block:
            errs.append(f"[{block}] {cmds[0]} is {e['status']} in the ledger ({e['id']})")
    print(f"{seen} page lines checked against {len(ledger)} ledger entries")
    print("PASS — in-depth.html agrees with proof_ledger.json" if not errs else "FAIL:\n  " + "\n  ".join(errs))
    return 0 if not errs else 1


if __name__ == "__main__":
    raise SystemExit(main())
