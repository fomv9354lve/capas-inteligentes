#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""designlab/check — the ONE design gate. Runs the whole lab as a single command.

Two complementary layers, fail-closed:
  1. layout_lint.py   — fast STATIC lint of the HTML source (canonical bg logo, nav logo, footer,
                        column 1200, balanced tags, nav signature). No browser, milliseconds.
  2. render_check.py  — LIVE render (Playwright, local capas_api) that MEASURES the real geometry:
                        column/gutter/nav parity, no mobile overflow, console errors, axe a11y, and
                        pixel-regression vs baseline (reusing pixeldiff.py).

Static lint runs first (cheap, catches the obvious); the render gate runs second (the real proof).

    python3 designlab/check.py            # static lint + render layout gate
    python3 designlab/check.py --diff      # + pixel regression vs baseline
    python3 designlab/check.py --a11y-strict   # also hard-fail on critical accessibility findings

deploy_site.py --ui calls this before deploying, so a design regression breaks the build locally
instead of shipping to Azure.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

# The pure-HTML-shell marketing/doc pages the SOURCE lint applies to (canonical .section-inner +
# "1200px" in the markup). app.html (the Gate App) is intentionally NOT here — its layout lives in
# external CSS under a strict CSP, so it's proven by the RENDER gate (real geometry) instead, and by
# deploy_site.validate() (tags + nav). krenniq.html is a separate product surface with its own nav.
SHELL_PAGES = ["docs/index.html", "docs/customer-brief.html", "docs/benchmark.html",
               "docs/security.html", "docs/pilot-packet.html", "docs/audit.html"]


def main() -> int:
    passthrough = [a for a in sys.argv[1:] if a in ("--diff", "--strict", "--a11y-strict")]

    print("########## 1/2 · STATIC LINT (designlab/layout_lint.py — 6 shell pages) ##########")
    static = subprocess.run([sys.executable, str(HERE / "layout_lint.py"), *SHELL_PAGES],
                            cwd=str(ROOT)).returncode

    print("\n########## 2/2 · RENDER GATE (designlab/render_check.py check) ##########")
    render = subprocess.run([sys.executable, str(HERE / "render_check.py"), "check", *passthrough],
                            cwd=str(ROOT)).returncode

    ok = static == 0 and render == 0
    print("\n================ DESIGN GATE:",
          "PASS — static lint + render gate both green" if ok
          else f"FAIL — static={'ok' if static == 0 else 'FAIL'} render={'ok' if render == 0 else 'FAIL'}",
          "================")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
