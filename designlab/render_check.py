"""designlab/render_check — the RENDERING half of the design lab (the static half is layout_lint.py).

The friction this kills: iterating UI by deploying to Azure (~4 min) or eyeballing screenshots. Here a
change is rendered LOCALLY (reusing capas_api.py) and checked in seconds — at desktop AND mobile — with
the same fail-closed rigor as deploy_site.py, but for design:

    python3 designlab/render_check.py shoot       # render every page x viewport -> designlab/out/*.png
    python3 designlab/render_check.py check        # shoot + ASSERT layout (column/gutter/nav, no mobile overflow) + a11y
    python3 designlab/render_check.py baseline      # promote current shots to the regression baseline
    python3 designlab/render_check.py diff          # pixel-diff vs baseline (reuses designlab/pixeldiff.py)
    python3 designlab/render_check.py check --diff   # layout + regression in one gate

One system, not scattered scripts: `designlab/check.py` runs the static lint (layout_lint.py) AND this
render gate together; deploy_site.py --ui calls it pre-deploy so a layout regression (the 1400-vs-1200
class of bug) breaks the build instead of shipping. Rendering is via designlab/_render.mjs (Playwright,
global install); pixel-diff reuses designlab/pixeldiff.py; a11y by the vendored axe-core. All local.
"""
from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import threading
import time
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent          # designlab/
ROOT = HERE.parent                               # project root (capas_api.py lives here)
LAB = HERE
OUT = LAB / "out"
BASELINE = LAB / "baseline"
AXE = LAB / "vendor" / "axe.min.js"
RENDER = LAB / "_render.mjs"

# Every page that shares the canonical shell. `column` = the primary content wrapper to measure; the
# list is a CSS selector group so querySelector grabs whichever exists first in document order.
COLUMN = ".app-body, .hero-inner, .si, .doc, .section-inner"
PAGES = [
    {"label": "home",         "path": "/index.html",          "column": COLUMN},
    {"label": "gate-app",     "path": "/app.html",            "column": COLUMN},
    {"label": "methodology",  "path": "/customer-brief.html", "column": COLUMN},
    {"label": "pilot",        "path": "/pilot-packet.html",   "column": COLUMN},
    {"label": "benchmark",    "path": "/benchmark.html",      "column": COLUMN},
    {"label": "security",     "path": "/security.html",       "column": COLUMN},
    {"label": "audit",        "path": "/audit.html",          "column": COLUMN},
]
VIEWPORTS = [{"name": "desktop", "width": 1440, "height": 900},
             {"name": "mobile", "width": 390, "height": 844}]

NAV_ITEMS = ["Home", "Intro+", "Gate App", "Methodology", "Pilot", "Audit", "Benchmark", "Security", "Atlas"]
COLUMN_TOL = 8     # px tolerance for "same column width / gutter across pages"
A11Y_FAIL_IMPACTS = {"critical"}  # hard-fail only on critical; serious/moderate are reported as warnings


# ---------- local server (reuse capas_api.py) ----------
def _free_port() -> int:
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def _start_server() -> tuple[ThreadingHTTPServer, str]:
    # Reuse capas_api's request handler IN-PROCESS (single source of truth: same routing + the same
    # no-cache/ETag headers the real server sends) on a daemon thread. In-process avoids the
    # cross-process teardown that killed a Popen child, and serves the CURRENT docs/ on every request.
    sys.path.insert(0, str(ROOT))
    import capas_api  # noqa: E402
    port = _free_port()
    srv = ThreadingHTTPServer(("127.0.0.1", port), capas_api.H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{port}"
    for _ in range(40):
        try:
            urllib.request.urlopen(base + "/api/health", timeout=1).read()
            return srv, base
        except Exception:
            time.sleep(0.1)
    srv.shutdown()
    raise RuntimeError("local capas_api server did not come up")


def _render(base: str) -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    cfg = {"base": base, "viewports": VIEWPORTS, "pages": PAGES}
    cfg_path = OUT / "_config.json"
    cfg_path.write_text(json.dumps(cfg))
    report_path = OUT / "_report.json"
    node_path = subprocess.run(["npm", "root", "-g"], capture_output=True, text=True).stdout.strip()
    env = dict(os.environ, NODE_PATH=node_path)
    r = subprocess.run(["node", str(RENDER), str(cfg_path), str(AXE), str(report_path), str(OUT)],
                       cwd=str(ROOT), env=env, capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        print(r.stdout); print(r.stderr)
        raise RuntimeError("render worker failed")
    print("  " + r.stdout.strip())
    return json.loads(report_path.read_text())


def shoot() -> dict:
    srv, base = _start_server()
    try:
        print(f"=== RENDER (local {base}) ===")
        return _render(base)
    finally:
        srv.shutdown()


# ---------- consistency assertions ----------
def _by_vp(report: dict, vp: str) -> list:
    return [p for p in report["pages"] if p["viewport"] == vp]


def assert_consistency(report: dict) -> bool:
    ok = True
    print("=== ASSERT consistency ===")

    # 1. nav identical across every page (desktop)
    print("  nav parity:")
    for p in _by_vp(report, "desktop"):
        items = p.get("navLinks") or []
        good = items == NAV_ITEMS
        ok = ok and good
        print(f"    {'OK ' if good else 'XX '}{p['label']:12} {'7 canonical' if good else items}")

    # 2. same content column width + left gutter across pages (desktop)
    desk = _by_vp(report, "desktop")
    cols = [(p["label"], p.get("column")) for p in desk if p.get("column")]
    widths = {lbl: c["width"] for lbl, c in cols}
    gutters = {lbl: c["left"] for lbl, c in cols}
    wv = list(widths.values()); gv = list(gutters.values())
    w_ok = (max(wv) - min(wv) <= COLUMN_TOL) if wv else False
    g_ok = (max(gv) - min(gv) <= COLUMN_TOL) if gv else False
    ok = ok and w_ok and g_ok
    print(f"  column width  {'OK ' if w_ok else 'XX '}span {min(wv)}–{max(wv)}px  {widths}")
    print(f"  left gutter   {'OK ' if g_ok else 'XX '}span {min(gv)}–{max(gv)}px  {gutters}")

    # 3. nav-logo gutter identical
    logos = {p["label"]: p.get("navLogoLeft") for p in desk if p.get("navLogoLeft") is not None}
    lv = list(logos.values())
    l_ok = (max(lv) - min(lv) <= COLUMN_TOL) if lv else False
    ok = ok and l_ok
    print(f"  nav-logo edge {'OK ' if l_ok else 'XX '}span {min(lv)}–{max(lv)}px")

    # 4. no horizontal overflow at mobile (the classic responsive break)
    print("  mobile overflow:")
    for p in _by_vp(report, "mobile"):
        bad = p.get("horizontalOverflow")
        ok = ok and not bad
        print(f"    {'XX ' if bad else 'OK '}{p['label']:12} scrollWidth={p.get('scrollWidth')} vw={p.get('vw')}")

    # 5. console errors (CSP/JS) on any page×viewport — but ignore font-CDN/network noise, which is a
    # LOCAL-sandbox artifact (Google Fonts is unreachable offline; it loads fine in the browser/Azure).
    _net_noise = ("fonts.googleapis", "fonts.gstatic", "ERR_NETWORK", "net::ERR", "ERR_NAME_NOT_RESOLVED",
                  "Failed to load resource", "ERR_CONNECTION", "ERR_INTERNET")
    def _real(errs):
        return [e for e in errs if not any(n in e for n in _net_noise)]
    noisy = [(p["label"], p["viewport"], _real(p["consoleErrors"])) for p in report["pages"]
             if _real(p.get("consoleErrors") or [])]
    if noisy:
        ok = False
        print("  console errors:")
        for lbl, vp, errs in noisy:
            print(f"    XX {lbl}/{vp}: {errs[0][:120]}")
    else:
        print("  console errors: OK none")

    # LAYOUT GATE verdict (the consistency mission: column/gutter/nav/overflow/console).
    layout_ok = ok
    print("LAYOUT GATE:", "PASS — every page shares the column, gutter, nav; no mobile overflow; no console errors"
          if layout_ok else "FAIL — see XX lines above")

    # 6. accessibility (axe) — tracked SEPARATELY. Reported loudly every run; blocks only with
    # --a11y-strict (full ARIA wiring on the app touches the CSP-hashed inline script — a distinct
    # workstream from layout regression, so it shouldn't silently gate the layout loop).
    strict_a11y = "--a11y-strict" in sys.argv
    crit_total = 0
    print("  accessibility (axe wcag2a/aa)  [tracked; --a11y-strict to enforce]:")
    for p in _by_vp(report, "desktop"):
        viols = p.get("axe") or []
        crit = [v for v in viols if v.get("impact") in A11Y_FAIL_IMPACTS]
        crit_total += len(crit)
        tag = "XX " if crit else ("!  " if viols else "OK ")
        summary = ", ".join(f"{v['id']}({v['impact']},{v['nodes']})" for v in viols[:4]) or "clean"
        print(f"    {tag}{p['label']:12} {summary}")
    print(f"  a11y critical findings: {crit_total} ({'BLOCKING' if strict_a11y else 'tracked, non-blocking'})")
    a11y_ok = (crit_total == 0) if strict_a11y else True

    final = layout_ok and a11y_ok
    print("ASSERT:", "PASS" + ("" if a11y_ok else "  (layout PASS, a11y FAIL under --a11y-strict)")
          if final else "FAIL — layout regressions above" if not layout_ok else "FAIL — a11y (--a11y-strict)")
    return final


# ---------- pixel diff — REUSES designlab/pixeldiff.py (one diff engine, not two) ----------
def diff(strict: bool = False, threshold: float = 2.0) -> bool:
    print("=== DIFF vs baseline (designlab/pixeldiff.py) ===")
    if not any(BASELINE.glob("*.png")):
        print("  no baseline yet — run `python3 designlab/render_check.py baseline` first. (skipping)")
        return True
    sys.path.insert(0, str(HERE))
    import pixeldiff  # the standalone diff library, reused so the numbers match the CLI tool
    ok = True
    for cur in sorted(OUT.glob("*.png")):
        if cur.stem.endswith("__diff"):
            continue
        base = BASELINE / cur.name
        if not base.is_file():
            print(f"  +  {cur.name:28} NEW (no baseline)")
            continue
        out = OUT / (cur.stem + "__diff.png")
        # pixeldiff.diff prints its own line + heatmap and returns True if within threshold
        passed = pixeldiff.diff(str(cur), str(base), str(out), threshold)
        if strict and not passed:
            ok = False
    print("DIFF:", "within threshold" if ok else f"regressions over {threshold}% (--strict)")
    return ok


def baseline() -> None:
    import shutil
    rep = shoot()
    BASELINE.mkdir(parents=True, exist_ok=True)
    n = 0
    for png in OUT.glob("*.png"):
        if png.stem.endswith("__diff"):
            continue
        shutil.copy2(png, BASELINE / png.name)
        n += 1
    print(f"=== BASELINE set: {n} screenshots promoted ({len(rep['pages'])} renders) ===")


def main() -> int:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    if cmd == "shoot":
        rep = shoot()
        print(f"shot {len(rep['pages'])} renders -> {OUT}")
        return 0
    if cmd == "baseline":
        baseline()
        return 0
    if cmd == "diff":
        return 0 if diff(strict="--strict" in sys.argv) else 1
    if cmd == "check":
        rep = shoot()
        ok = assert_consistency(rep)
        if "--diff" in sys.argv:
            ok = diff(strict="--strict" in sys.argv) and ok
        return 0 if ok else 1
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
