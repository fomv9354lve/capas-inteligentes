#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Deterministic envelope conversion for the Atlas corpus (format pilot, 2026-10-13). Atlas coded FLAT payloads
{claim_type, meta, <evidence fields>, calibration_snapshot?} because the guide did not define the v3 envelope.
Conversion (no judgement, no field invention):
  claim  = {id: claim_id, type: claim_type, text: meta.statement}
  evidence = every other key; calibration_snapshot -> evidence.invariants.calibration_snapshot
Usage: python3 convert_atlas_payload.py in.jsonl out.jsonl  (prints sha256 of both)"""
import hashlib, json, sys


def convert(rec: dict) -> dict:
    p = dict(rec["payload"]); meta = p.pop("meta", {}) or {}
    ct = p.pop("claim_type"); snap = p.pop("calibration_snapshot", None)
    ev = {k: v for k, v in p.items()}
    if snap is not None:
        ev["invariants"] = {**(ev.get("invariants") or {}), "calibration_snapshot": snap}
    return {"claim_id": rec["claim_id"], "contaminado": rec.get("contaminado"), "meta": meta,
            "payload": {"schema_version": "capas-claim-payload-v3",
                        "claim": {"id": rec["claim_id"], "type": ct, "text": str(meta.get("statement") or ct)},
                        "evidence": ev}}


def main() -> int:
    src, out = sys.argv[1:3]
    rows = [convert(json.loads(l)) for l in open(src, encoding="utf-8") if l.strip()]
    body = "\n".join(json.dumps(r, ensure_ascii=False, sort_keys=True) for r in rows) + "\n"
    open(out, "w", encoding="utf-8").write(body)
    print("in  sha256", hashlib.sha256(open(src, "rb").read()).hexdigest())
    print("out sha256", hashlib.sha256(body.encode()).hexdigest(), f"({len(rows)} claims)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
