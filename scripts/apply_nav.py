#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Single source of the CAPAS site navigation (owner decision 2026-10-14: group the nav by task).
Audit CAP-19: top level is CAPAS-centred (Product · Application · Evidence · Pilot · Documentation); the Krenn·IQ
ecosystem (krenniq.com, Atlas) moves to the secondary bar, which also lists the pages of the current group. The current
page is marked in both bars. Rewrites the nav-links block and the sub-nav of every
CAPAS page, and keeps the sub-nav rule in each page's inline <style> (the pages inline the shell's CSS).
Run: python3 scripts/apply_nav.py [--check]   (--check exits 1 if any page differs from this definition)"""
import re, sys
from pathlib import Path
DOCS = Path(__file__).resolve().parents[1] / "docs"
GH = "https://github.com/fomv9354lve/capas-inteligentes/blob/main/"
I = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{}</svg>'
ICON = {"product": '<circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/>',
        "app": '<path d="M9 3H5a2 2 0 0 0-2 2v4m6-6h10a2 2 0 0 1 2 2v4M9 3v18m0 0h10a2 2 0 0 0 2-2V9M9 21H5a2 2 0 0 1-2-2V9m0 0h18"/>',
        "evidence": '<path d="M18 20V10"/><path d="M12 20V4"/><path d="M6 20v-6"/>',
        "pilot": '<polyline points="9 11 12 14 22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>',
        "docs": '<path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>'}
# (key, EN, ES, icon, [(href, EN, ES)])  — the first page of a group is where its top-level link points
GROUPS = [
    ("product", "Product", "Producto", "product", [("index.html", "Overview", "Resumen"), ("in-depth.html", "In depth", "A fondo")]),
    ("app", "Application", "Aplicación", "app", [("app.html", "Gate App", "Gate App"), ("audit.html", "Decision log", "Registro de decisiones")]),
    ("evidence", "Evidence", "Evidencia", "evidence", [("benchmark.html", "Benchmark", "Benchmark"), ("in-depth.html#ledger", "Proof ledger", "Ledger de pruebas"),
                                                       ("governance.html", "Audit and governance", "Auditoría y gobierno")]),
    ("pilot", "Pilot", "Piloto", "pilot", [("pilot-packet.html", "Pilot packet", "Paquete de piloto"), ("customer-brief.html", "Decision brief", "Brief de decisión")]),
    ("docs", "Documentation", "Documentación", "docs", [("security.html", "Security", "Seguridad"), (GH + "LIBRARY.md", "Library and API", "Biblioteca y API"),
                                                        (GH + "THREAT_MODEL.md", "Threat model", "Modelo de amenazas"), ("legal.html", "Legal", "Legal")]),
]
PAGE_GROUP = {"index.html": "product", "in-depth.html": "product", "app.html": "app", "audit.html": "app", "benchmark.html": "evidence",
              "governance.html": "evidence", "pilot-packet.html": "pilot", "customer-brief.html": "pilot", "security.html": "docs"}
CSS = ("/* sub-nav (scripts/apply_nav.py) */.subnav{position:sticky;top:var(--nav-h,60px);z-index:99;display:flex;gap:4px;"
       "padding:6px var(--gutter,48px);border-bottom:1px solid rgba(255,255,255,0.06);background:rgba(8,8,16,0.88);"
       "backdrop-filter:blur(12px);overflow-x:auto}.subnav a{color:rgba(255,255,255,0.5);text-decoration:none;font-size:12px;"
       "padding:5px 12px;border-radius:6px;white-space:nowrap}.subnav a:hover{color:rgba(255,255,255,0.85)}"
       ".subnav a.active{color:#fff;background:rgba(255,255,255,0.06)}.subnav-sep{flex:1;min-width:16px}"
       ".subnav-eco{align-self:center;font-size:10px;letter-spacing:.08em;text-transform:uppercase;color:rgba(255,255,255,0.3);padding:0 4px}@media(max-width:1100px){nav{flex-wrap:wrap;height:auto;min-height:var(--nav-h,60px);padding-top:8px;padding-bottom:8px;row-gap:6px}.nav-links{order:3;width:100%;flex-wrap:wrap;justify-content:flex-start}.subnav{position:static}}"
       "@media(max-width:760px){.subnav{position:static;padding:6px 16px;flex-wrap:wrap}.subnav-sep{flex-basis:100%;height:0}.nav-links{flex-wrap:wrap;overflow-x:visible}.nav-links a{padding:6px 10px}.nav-links svg{display:none}}")


# Shared responsive layer (2026-10-14, after the fb52d8c re-audit's verifier found content clipped by body
# overflow-x:hidden): multi-column grids collapse on phones, grid children may shrink, long code wraps, tables scroll in
# their own box, footers wrap. Injected into every CAPAS page and into krenniq.html / legal.html (no nav there).
LAYOUT_CSS = ("/* layout (scripts/apply_nav.py) */"
              ".verdicts-grid{grid-template-columns:repeat(auto-fit,minmax(220px,1fr))!important}"
              "[class*=grid]>*,[style*='grid-template-columns']>*,.hero-inner>*{min-width:0}"
              ".hero-right,.verdict-panel,.verdict-preview{max-width:100%}"
              ".hero-actions,.cta-row,.btn-row{flex-wrap:wrap}"
              "footer,.footer-links{flex-wrap:wrap}.footer-disclaimer{max-width:100%;box-sizing:border-box}"
              "@media(max-width:760px){.hero-inner,.si,.g2,.g3,.core-grid,.verdicts-grid,"
              "main [style*='grid-template-columns'],section [style*='grid-template-columns']{grid-template-columns:minmax(0,1fr)!important;gap:16px!important}"
              ".modes,.split{grid-template-columns:minmax(0,1fr)!important}"
              ".stat-bar-inner,.pipeline-steps,.grid,.hero-metrics{grid-template-columns:repeat(2,minmax(0,1fr))!important}"
              "footer>div{max-width:100%;flex-wrap:wrap}"
              "code{overflow-wrap:anywhere;word-break:break-word}"
              "table{display:block;max-width:100%;overflow-x:auto}pre{max-width:100%;overflow-x:auto}}")
LAYOUT_ONLY = ["krenniq.html", "legal.html"]


def links(page):
    g, out = PAGE_GROUP[page], []
    for key, en, es, icon, pages in GROUPS:
        act = ' class="active" aria-current="true"' if key == g else ""
        out.append(f'<a href="{pages[0][0]}"{act}>{I.format(ICON[icon])}<span data-es="{es}">{en}</span></a>')
    return '<div class="nav-links" aria-label="Primary">' + "".join(out) + "</div>"


def subnav(page):
    g = PAGE_GROUP[page]; key, en, es, _, pages = next(x for x in GROUPS if x[0] == g)
    items = []
    for href, a, b in pages:
        act = ' class="active" aria-current="page"' if href == page else ""
        items.append(f'<a href="{href}"{act} data-es="{b}">{a}</a>')
    eco = ('<span class="subnav-sep"></span><span class="subnav-eco" data-es="Ecosistema">Ecosystem</span>'
           '<a href="https://krenniq.com/">Krenn·IQ</a><a href="https://atlas.krenniq.com/">Atlas</a>')
    return f'<div class="subnav" aria-label="{en}">' + "".join(items) + eco + "</div>"


def apply(page, src):
    src = re.sub(r'<div class="nav-links"[^>]*>.*?</div>', lambda m: links(page), src, count=1, flags=re.S)
    src = re.sub(r'\n?<div class="subnav"[^>]*>.*?</div>', "", src, flags=re.S)
    src = re.sub(r"(</nav>)", lambda m: m.group(1) + "\n" + subnav(page), src, count=1)
    src = re.sub(r"/\* sub-nav \(scripts/apply_nav\.py\) \*/[^\n<]*?(?=</style>|\n)", "", src)
    src = src.replace("</style>", CSS + LAYOUT_CSS + "</style>", 1)
    return src


def apply_layout_only(src):
    src = re.sub(r"/\* layout \(scripts/apply_nav\.py\) \*/[^\n<]*?(?=</style>|\n)", "", src)
    return src.replace("</style>", LAYOUT_CSS + "</style>", 1)


def main() -> int:
    check, diff = "--check" in sys.argv, []
    for page in PAGE_GROUP:
        p = DOCS / page; src = p.read_text(encoding="utf-8"); new = apply(page, src)
        if new != src:
            diff.append(page)
            if not check:
                p.write_text(new, encoding="utf-8")
    for page in LAYOUT_ONLY:
        p = DOCS / page; src = p.read_text(encoding="utf-8"); new = apply_layout_only(src)
        if new != src:
            diff.append(page)
            if not check:
                p.write_text(new, encoding="utf-8")
    print(("FAIL — nav differs from scripts/apply_nav.py on: " + ", ".join(diff)) if check and diff else
          f"nav: {len(PAGE_GROUP)} pages " + ("checked" if check else f"written ({len(diff)} changed)"))
    return 1 if check and diff else 0


if __name__ == "__main__":
    sys.exit(main())
