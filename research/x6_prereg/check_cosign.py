#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Checks that the current PREREG_CAPAS_VS_LLM_JUDGE.md is the version co-signed in COSIGN_LOG.md: the log's last
entry must carry this file's sha256 and a CO-SIGN decision with no blocking objection. Any edit to the document after
the co-signature fails this check until a new co-signature is logged. Run: python3 research/x6_prereg/check_cosign.py"""
import hashlib, json, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main() -> int:
    sha = hashlib.sha256((HERE / "PREREG_CAPAS_VS_LLM_JUDGE.md").read_bytes()).hexdigest()
    log = (HERE / "COSIGN_LOG.md").read_text(encoding="utf-8")
    heads = list(re.finditer(r"^## (\S+) · (\S+) / (\S+) · prereg sha256 ([0-9a-f]{64})$", log, re.M))
    entries = []
    for k, m in enumerate(heads):
        end = heads[k + 1].start() if k + 1 < len(heads) else len(log)
        chunk = log[m.end():end].split("\n## ")[0]          # stop at the next section (e.g. Status)
        entries.append((*m.groups(), chunk[chunk.find("{"):chunk.rfind("}") + 1]))
    if not entries:
        print("FAIL — no co-signature entry in COSIGN_LOG.md"); return 1
    when, prov, model, signed_sha, body = entries[-1]
    try:
        reply = json.loads(body)
    except json.JSONDecodeError:
        print("FAIL — the last entry is not parseable JSON"); return 1
    ok = signed_sha == sha and reply.get("decision") == "CO-SIGN" and not reply.get("blocking_objections")
    print(f"{'PASS' if ok else 'FAIL'} — prereg sha256 {sha[:16]}; last entry {when} {prov}/{model} "
          f"decision {reply.get('decision')} on {signed_sha[:16]}; {len(entries)} review rounds logged")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
