#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""The decision packet shown on docs/customer-brief.html ("A real decision packet — not a description of one") is
GENERATED here from the engine, never typed. External audit 2026-10-14: the page showed 7 edited fields and called them
'literal output'. Now: the full packet (every field, audit_hash included) is written to docs/brief_decision_packet.json
and embedded verbatim in the page; verify_brief_packet_matches_engine.py fails CI if the page and the engine diverge.
Run: python3 benchmarks/brief_decision_packet.py [--json]"""
from __future__ import annotations
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import capas  # noqa: E402

PAYLOAD = {
    "schema_version": "capas-claim-payload-v3",
    "claim": {"id": "brief_fin_001", "type": "financial_metric_claim",
              "text": "Reported net assets of 1000 match the audited reference for the period."},
    "evidence": {"reported_value": 1000, "reference_value": 1000, "tolerance": 0.5, "metric_period_match": True,
                 "invariants": {"accounting": {"assets": 1000, "liabilities": 600, "equity": 300}}},
}


def packet() -> dict:
    return capas.decide_external_claim(PAYLOAD)


def render() -> str:
    return json.dumps(packet(), indent=2, ensure_ascii=False, sort_keys=False)


if __name__ == "__main__":
    out = ROOT / "docs" / "brief_decision_packet.json"
    out.write_text(json.dumps({"payload": PAYLOAD, "result": packet()}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if "--json" in sys.argv:
        print(render())
    else:
        r = packet(); print(f"{r['verdict']} · {r['audit_hash']} · {len(r)} fields · written {out.relative_to(ROOT)}")
