#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Writes docs/rule_table.json, the engine's rules AS DATA (PLAN_v3 A1). The builder lives in capas_rules.build()
(it reads capas.decide_external_claim's syntax tree and capas_plan3.RULES; it executes nothing). See capas_rules for
the field definitions; scripts/check_rule_table.py proves the table against the engine on every payload in the repo.
Run: python3 scripts/gen_rule_table.py [--check]"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import capas_rules  # noqa: E402

OUT = capas_rules.TABLE_PATH


def main() -> int:
    t = capas_rules.build()
    text = capas_rules.dump(t)
    if "--check" in sys.argv:
        ok = OUT.is_file() and OUT.read_text(encoding="utf-8") == text
        print("rule table: in sync with the engine" if ok else "FAIL: docs/rule_table.json differs from the engine; run scripts/gen_rule_table.py")
        return 0 if ok else 1
    OUT.write_text(text, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}: {len(t['rules'])} rules "
          f"({sum(r['stage'] == 'base' for r in t['rules'])} base, {sum(r['stage'] != 'base' for r in t['rules'])} downgrade/annotate)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
