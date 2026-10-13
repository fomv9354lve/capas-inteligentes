#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Parity of the in-browser JS replica (`rule()` in docs/app.html, the OFFLINE fallback) against the Python engine over
the sealed Ginibre payloads. Measured 2026-10-13: 130/233 agree — the replica lags every rule added since 2026-09 and
is NOT authoritative; the Gate App labels it and the single/batch paths use /api/decide when the backend is up.
Needs node + playwright (NODE_PATH=$(npm root -g)). Writes outputs/replica_parity.json."""
import json, os, subprocess, sys, tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
import capas
G = Path("/Users/kreniq/Desktop/KRENIQ/AI Projects/01. Investigacion/Paper - Inverse Ginibre Overlap/CAPAS_CORPUS_2026-10-12")


def main() -> int:
    if not G.exists():
        print("SKIP: corpus not present"); return 2
    rows = []
    for f in ("PARA_CAPAS_claims.jsonl", "PARA_CAPAS_claims_X4.jsonl", "PARA_CAPAS_claims_X5.jsonl"):
        for l in (G / f).read_text(encoding="utf-8").splitlines():
            if l.strip():
                r = json.loads(l); d = capas.decide_external_claim(r["payload"]); d = d.get("decision", d)
                rows.append({"id": r["claim_id"], "payload": r["payload"], "py": d["verdict"]})
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
        json.dump(rows, fh); pf = fh.name
    npm_root = subprocess.run(["npm", "root", "-g"], capture_output=True, text=True).stdout.strip()
    r = subprocess.run(["node", str(ROOT / "benchmarks" / "replica" / "parity.js"), str(ROOT), pf], capture_output=True, text=True,
                       env={**os.environ, "NODE_PATH": npm_root}, timeout=600)
    os.unlink(pf)
    if r.returncode != 0:
        print("node failed:", r.stderr[-300:]); return 1
    res = json.loads(r.stdout.strip().splitlines()[-1])
    json.dump(res, open(ROOT / "outputs" / "replica_parity.json", "w"), indent=1)
    print(f"replica parity: {res['same']}/{res['n']} agree; mismatches by python→js: {res['by_kind']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
