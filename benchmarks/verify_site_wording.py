#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Wording the site must never carry again (every item below was a real finding of the 2026-10-13 external audit,
fixed by hand once; a fix without a test escapes). Served pages only. Run: python3 benchmarks/verify_site_wording.py"""
from __future__ import annotations
import re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; DOCS = ROOT / "docs"
PAGES = ["index.html", "in-depth.html", "app.html", "customer-brief.html", "pilot-packet.html", "audit.html",
         "benchmark.html", "security.html", "governance.html", "krenniq.html", "legal.html"]
FORBIDDEN = [
    (r"proprietary research prototype", "license wording contradicts Apache-2.0 (audit item 1)"),
    (r"\bPROVEN\b", "one vocabulary: CLOSED / BACKED / SCOPED"),
    (r">Independent validation<", "the IBM section is a parallel, not a validation"),
    (r"production stack already runs it", "no vendor runs CAPAS"),
    (r"two independent oracles", "both oracles read the vendor's public data"),
    (r"produces or provides", "Gate App mode note (audit item 3)"),
    (r"8/8 load-bearing|The 8 load-bearing|Los 8 invariantes", "the conformance suite has 10 invariants"),
    (r"It is the evidence that the method works", "the 28/28 retrospective is illustrative, not proof"),
    (r">Methodology</a>", "the brief is called Brief everywhere (nav, footer, buttons)"),
    (r"Read methodology", "button renamed with the page"),
    (r"Free this launch month", "undated offer removed from the landing"),
    (r"Inteligencia Cu[aá]ntica</title>", "the umbrella is not a quantum brand"),
    (r"90\+ deterministic rule functions|Más de 90 funciones", "bare count; the registered counts regenerate from the engine (brief audit item 5)"),
    (r"full verdict-space coverage|cobertura completa del espacio de veredictos", "9/12 families reach all four verdicts, three cannot by design (brief audit item 4)"),
    (r"Recent [Gg]ate [Dd]ecisions|Decisiones recientes del gate", "the four decisions are fixed, re-derivable fixtures (brief audit item 8)"),
    (r"wraps any packet in a signed", "/api/decide and /api/gate return unsigned packets (brief audit item 3)"),
    (r"literal output of the engine", "the packet is generated, published and CI-checked, never typed (brief audit item 1)"),
    (r"examples shown here are illustrative|ejemplos de decisión son ilustrativos", "nothing on the brief is illustrative (brief audit item 8)"),
]
TITLES = {"customer-brief.html": "Brief", "audit.html": "Decision log", "governance.html": "Audit"}


def main() -> int:
    errs = []
    for name in PAGES:
        p = DOCS / name
        if not p.is_file():
            continue
        html = p.read_text(encoding="utf-8")
        for pat, why in FORBIDDEN:
            for m in re.finditer(pat, html):
                line = html.count("\n", 0, m.start()) + 1
                errs.append(f"{name}:{line}: {m.group(0)!r} — {why}")
        want = TITLES.get(name)
        if want:
            t = re.search(r"<title>([^<]*)</title>", html)
            if not t or want not in t.group(1):
                errs.append(f"{name}: <title> should mention {want!r}, got {t.group(1) if t else None!r}")
    # 'AI-made' is licensed only by the provenance clause (Osvaldo, 2026-10-14: the corpus claims were written by AI sessions)
    home = (DOCS / "index.html").read_text(encoding="utf-8")
    if "AI-made" in home and "written by AI sessions" not in home:
        errs.append("index.html: 'AI-made' without the provenance clause 'written by AI sessions'")
    print("PASS — no forbidden wording on the served pages" if not errs else "FAIL:\n  " + "\n  ".join(errs))
    return 0 if not errs else 1


if __name__ == "__main__":
    raise SystemExit(main())
