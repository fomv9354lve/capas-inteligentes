#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""layout_lint — lint de consistencia de layout para el shell KRENIQ (CAPAS + landing + Atlas).

Rompe el build si una página no cumple la fuente única de verdad del shell:
  - tags balanceados (div/section/nav/footer)
  - logo flotante canónico de fondo  (.bg-logo iframe -> logo_kreniq_volum_trico.html)
  - nav con el logo canónico          (.nav-logo img -> krenniq-logo.png)
  - footer con el logo canónico
  - ancho de columna == 1200px         (.section-inner / .hero-inner max-width canónico)
  - nav idéntico entre páginas del MISMO producto (firma de nav igual)

Uso:  python3 designlab/layout_lint.py docs/krenniq.html docs/index.html ...
Sin args: lintea docs/*.html. Exit 0 si todo pasa, 1 si algo falla (apto para CI)."""
from __future__ import annotations
import glob
import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANON_COL = "1200px"            # ancho de columna canónico (.section-inner)
TAGS = ("div", "section", "nav", "footer")


def _balanced(html: str) -> list[str]:
    bad = []
    for t in TAGS:
        o = len(re.findall(r"<%s[\s>]" % t, html))
        c = html.count("</%s>" % t)
        if o != c:
            bad.append("<%s>: %d abiertos / %d cerrados" % (t, o, c))
    return bad


def _nav_signature(html: str) -> str | None:
    m = re.search(r"<nav\b.*?</nav>", html, re.S)
    if not m:
        return None
    # firma = secuencia de hrefs de los nav-links (lo que define "el mismo nav")
    hrefs = re.findall(r'<a[^>]*href="([^"]+)"', m.group(0))
    return hashlib.sha1("|".join(hrefs).encode()).hexdigest()[:12]


def lint_page(path: Path) -> list[str]:
    html = path.read_text(encoding="utf-8")
    errs = _balanced(html)
    if "logo_kreniq_volum_trico.html" not in html:
        errs.append("falta el logo flotante canónico de fondo (.bg-logo iframe)")
    if "krenniq-logo.png" not in html:
        errs.append("falta el logo canónico (krenniq-logo.png) en nav/footer")
    if "<nav" not in html:
        errs.append("falta <nav>")
    # ancho de columna canónico: la página o su CSS debe definir max-width:1200px
    if CANON_COL not in html.replace(" ", ""):
        errs.append("no usa el ancho de columna canónico (%s)" % CANON_COL)
    return errs


def main():
    args = sys.argv[1:]
    files = [Path(a) for a in args] if args else sorted((ROOT / "docs").glob("*.html"))
    files = [f for f in files if f.is_file() and ".bak." not in f.name and "_prev" not in str(f)]
    fail = 0
    sigs: dict[str, list[str]] = {}
    for f in files:
        errs = lint_page(f)
        sig = _nav_signature(f.read_text(encoding="utf-8"))
        sigs.setdefault(sig or "no-nav", []).append(f.name)
        if errs:
            fail += 1
            print("✗ %s" % f.name)
            for e in errs:
                print("    - %s" % e)
        else:
            print("✓ %s" % f.name)
    print("\nfirmas de nav (páginas con el MISMO nav comparten firma):")
    for sig, names in sigs.items():
        print("  %s : %s" % (sig, ", ".join(names)))
    print("\n%s — %d/%d páginas OK" % ("FALLO" if fail else "TODO OK", len(files) - fail, len(files)))
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
