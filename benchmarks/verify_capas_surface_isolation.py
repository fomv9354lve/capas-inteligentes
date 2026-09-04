#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""CAPAS serves CAPAS: no forked sibling pages, and no redirect standing in for them.

docs/ carried frozen copies of a sibling product's pages, and capas_api.py grew a
301 to paper over the fact that they had gone stale. Both are gone; this asserts
they stay gone. A vendored fork drifts from its source in silence — the redirect
was the tell, not the fix.

The nav link to the sibling is deliberate and is asserted PRESENT: CAPAS and Atlas
are siblings under one brand and cross-link on purpose. Isolation here means CAPAS
stops *hosting* another product, not that it stops *pointing* at it.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
API = ROOT / "capas_api.py"

FORBIDDEN_GLOBS = ("atlas-*.html", "atlas_*.svg")
FORBIDDEN_FILES = ("evidence.html",)
FORBIDDEN_DIRS = ("atlas_data",)
SIBLING_NAV_HREF = 'href="https://atlas.krenniq.com/"'


def main() -> int:
    fails: list[str] = []

    for pat in FORBIDDEN_GLOBS:
        for f in sorted(DOCS.glob(pat)):
            fails.append(f"forked sibling page still present: docs/{f.name}")
    for name in FORBIDDEN_FILES:
        if (DOCS / name).exists():
            fails.append(f"forked sibling page still present: docs/{name}")
    for d in FORBIDDEN_DIRS:
        if (DOCS / d).is_dir():
            fails.append(f"forked sibling assets still present: docs/{d}/")

    api = API.read_text(encoding="utf-8")
    if "atlas.krenniq.com" in api:
        fails.append("capas_api.py still redirects to the sibling product (the 301 fork-patch)")

    index = (DOCS / "index.html").read_text(encoding="utf-8")
    if SIBLING_NAV_HREF not in index:
        fails.append("docs/index.html lost the sibling nav link to Atlas — that link is intended")

    if fails:
        print("FAIL:")
        for x in fails:
            print("  -", x)
        return 1
    print("OK: CAPAS's surface is CAPAS only — no forked sibling pages, no assets, and no "
          "redirect standing in for them; the intended sibling nav link is intact.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
