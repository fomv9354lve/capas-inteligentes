#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Arm B's only access to CAPAS (PROTOCOL.md). Every call is logged to arm_B/calls.jsonl for the effort measure.

  python3 research/exp_capas_addon/capas_call.py --requirements <claim_type>     # fields, types, example values
  python3 research/exp_capas_addon/capas_call.py --case C0xx --agent B1 payload.json   # decide; prints the verdict
  (payload may also come on stdin with '-')"""
from __future__ import annotations

import json, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
import capas  # noqa: E402

KEEP = ("verdict", "reason", "licensed_claim", "text_licensed_as_written", "missing_fields", "schema_errors",
        "did_you_mean", "audit_hash")


def main() -> int:
    a = sys.argv[1:]
    if a[:1] == ["--requirements"]:
        t = a[1]
        reg = capas.CLAIM_TYPE_REGISTRY.get(t)
        if not reg:
            print(json.dumps({"error": f"unknown claim type {t}", "supported": sorted(capas.CLAIM_TYPE_REGISTRY)})); return 2
        fields = list(reg["required"])
        print(json.dumps({"claim_type": t, "description": reg.get("description", ""), "required": {
            f: {"type": capas.evidence_field_type(f), "example": capas._example_value(f)} for f in fields},
            "payload_shape": {"schema_version": capas.CAPAS_CLAIM_SCHEMA_VERSION,
                              "claim": {"id": "<case id>", "type": t, "text": "<claim sentence>"},
                              "evidence": {f: "<value>" for f in fields}}}, indent=1))
        return 0
    case = a[a.index("--case") + 1] if "--case" in a else None
    agent = a[a.index("--agent") + 1] if "--agent" in a else None
    src = a[-1]
    payload = json.loads(sys.stdin.read() if src == "-" else Path(src).read_text(encoding="utf-8"))
    t0 = time.time()
    r = capas.decide_external_claim(payload)
    out = {k: r.get(k) for k in KEEP if r.get(k) not in (None, [], {})}
    out["resolution"] = (r.get("resolution") or {}).get("message")
    with (HERE / "arm_B" / "calls.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({"case": case, "agent": agent, "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                             "ms": round((time.time() - t0) * 1000, 1), "payload": payload, "verdict": r.get("verdict"),
                             "audit_hash": r.get("audit_hash")}) + "\n")
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
