#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""Option B — single source of truth for the browser gate's evidence contracts.

The browser app (docs/app.html) historically hand-mirrors capas.py's contracts in
JS. This script EXPORTS the canonical contracts straight from capas.py so the
browser consumes generated data instead of a hand-maintained copy:

  docs/capas-contracts.js    ->  window.CAPAS_CONTRACTS = {...}  (CSP-safe external)
  docs/capas-contracts.json  ->  the same payload for tooling

Run after any change to CLAIM_TYPE_REGISTRY / ANCHOR_MODE_CONTRACTS in capas.py.
A companion check (benchmarks/verify_gate_contracts_match.py) fails if the app's
inline contracts ever drift from this source.
"""
from __future__ import annotations

import json
from pathlib import Path

import capas

ROOT = Path(__file__).resolve().parents[1]


def build_contracts() -> dict:
    reg = capas.CLAIM_TYPE_REGISTRY
    anchors = capas.ANCHOR_MODE_CONTRACTS
    return {
        "schema_version": capas.CAPAS_CLAIM_SCHEMA_VERSION,
        "generated_from": "capas.py CLAIM_TYPE_REGISTRY + ANCHOR_MODE_CONTRACTS",
        "required": {t: list(s["required"]) for t, s in reg.items()},
        "optional": {t: list(s.get("optional", [])) for t, s in reg.items()},
        "descriptions": {t: s.get("description", "") for t, s in reg.items()},
        # Re-audit 5 (2026-10-14): the Gate App builds its form controls from these types, never from example values.
        "field_types": {f: capas.evidence_field_type(f) for t, s in reg.items()
                        for f in list(s["required"]) + list(s.get("optional", []))},
        # External re-audit fb52d8c (case D): the browser validates engine responses against the engine's own contract.
        "response_contract": {
            "verdicts": ["ACCEPT", "REWRITE", "REJECT", "HOLD"],
            "audit_hash_recipes": ["v2"],
            "reuse_boundary_by_verdict": capas.REUSE_BOUNDARY_BY_VERDICT,
            "required_v2": ["schema_version", "input_claim", "verdict", "reason", "required_fields", "audit_hash",
                            "audit_hash_recipe", "rules_fired", "rule_table_sha256", "evidence_sha256", "engine_version"],
        },
        "anchor_mode_contracts": {
            m: {
                "required": list(c["required"]),
                "optional": list(c.get("optional", [])),
                "license": c.get("license", ""),
            }
            for m, c in anchors.items()
        },
    }


def main() -> int:
    contracts = build_contracts()
    payload = json.dumps(contracts, indent=2, sort_keys=True)
    docs = ROOT / "docs"
    (docs / "capas-contracts.json").write_text(payload + "\n", encoding="utf-8")
    js = (
        "/* GENERATED from capas.py by scripts/gen_gate_contracts.py — do not edit by hand.\n"
        "   Single source of truth for the browser gate's evidence contracts.\n"
        "   Regenerate after changing CLAIM_TYPE_REGISTRY / ANCHOR_MODE_CONTRACTS. */\n"
        "window.CAPAS_CONTRACTS = " + payload + ";\n"
    )
    (docs / "capas-contracts.js").write_text(js, encoding="utf-8")
    print(f"wrote docs/capas-contracts.js and .json with {len(contracts['required'])} claim families "
          f"and {len(contracts['anchor_mode_contracts'])} anchor contracts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
