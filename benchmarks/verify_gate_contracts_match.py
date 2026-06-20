#!/usr/bin/env python3
"""Single source of truth: the browser gate consumes capas.py, no copy.

The Gate App no longer hand-mirrors the contracts in JS — it loads the generated
docs/capas-contracts.js (window.CAPAS_CONTRACTS) and reads required /
anchorModeContracts from it. This check asserts:

  1. the generated artifact (capas-contracts.json) matches capas.py exactly, and
  2. the app actually consumes it (no inline contract literal has crept back).

If capas.py changes, regenerate (scripts/gen_gate_contracts.py); this fails until
the artifact agrees again.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import capas

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS_JSON = ROOT / "docs" / "capas-contracts.json"
APP = ROOT / "docs" / "app.html"


def main() -> int:
    gen = json.loads(CONTRACTS_JSON.read_text(encoding="utf-8"))
    app = APP.read_text(encoding="utf-8")
    checks = []

    capas_required = {t: list(s["required"]) for t, s in capas.CLAIM_TYPE_REGISTRY.items()}
    gen_required = {t: list(v) for t, v in gen.get("required", {}).items()}
    checks.append(("generated required == capas.py", gen_required == capas_required))

    capas_anchor = {m: list(c["required"]) for m, c in capas.ANCHOR_MODE_CONTRACTS.items()}
    gen_anchor = {m: list(c["required"]) for m, c in gen.get("anchor_mode_contracts", {}).items()}
    checks.append(("generated anchor contracts == capas.py", gen_anchor == capas_anchor))

    consumes = ("capas-contracts.js" in app
                and "window.CAPAS_CONTRACTS.required" in app)
    checks.append(("app consumes generated contracts (no inline copy)", consumes))

    no_literal = "const required = {" not in app
    checks.append(("no inline contract literal in app", no_literal))

    ok = all(p for _, p in checks)
    print("gate_contracts_single_source_of_truth:", "True" if ok else "False")
    for label, p in checks:
        print(f"  {label}: {'ok' if p else 'FAIL'}")
    if gen_required != capas_required:
        diff = {t: {"gen": gen_required.get(t), "capas": capas_required.get(t)}
                for t in set(gen_required) | set(capas_required)
                if gen_required.get(t) != capas_required.get(t)}
        print("  required mismatch:", diff)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
