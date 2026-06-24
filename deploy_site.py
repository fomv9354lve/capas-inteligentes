# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""ONE clean deploy cycle: validate -> deploy -> VERIFY the live site matches local. No guessing.

The whole point: an edit must land on the live Azure site with proof, not hope. This script
(1) validates every docs/*.html page (balanced tags + identical 7-item nav), (2) builds & deploys
the container, then (3) polls the live URL and refuses to report success until the served bytes are
byte-identical to the committed local files. If the live copy never matches, it FAILS loudly with the
mismatching page — so a half-deployed or cached state can never masquerade as done.

    python3 deploy_site.py            # validate + deploy + verify
    python3 deploy_site.py --verify   # just verify live == local (no deploy)

Why "missing sections" happened before: HTML was served with no Cache-Control, so a normal reload
showed a stale/partial copy. capas_api.py now serves `no-cache` + ETag; this script proves the bytes.
"""
from __future__ import annotations

import hashlib
import re
import ssl
import subprocess
import sys
import time
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"
BASE = "https://capas.lemonground-e6ebae60.eastus.azurecontainerapps.io/"
APP = "capas"
RG = "capas-rg"

# The pages that carry the shared shell + nav. (index served at "/" too.)
PAGES = ["index.html", "app.html", "customer-brief.html", "benchmark.html",
         "security.html", "pilot-packet.html", "audit.html"]
NAV_ITEMS = ["Home", "Intro+", "Gate App", "Methodology", "Pilot", "Audit", "Benchmark", "Security", "Atlas"]

_CTX = ssl.create_default_context()
_CTX.check_hostname = False
_CTX.verify_mode = ssl.CERT_NONE  # Azure cert is valid; tolerate local CA-bundle gaps on 3.14


class _V(HTMLParser):
    VOID = {"br", "img", "meta", "link", "input", "hr", "path", "polyline", "svg",
            "circle", "rect", "line", "use", "source", "col", "area", "iframe"}

    def __init__(self):
        super().__init__()
        self.stack, self.stray = [], 0

    def handle_starttag(self, t, a):
        if t == "iframe":
            return
        if t not in self.VOID:
            self.stack.append(t)

    def handle_endtag(self, t):
        if t in self.VOID:
            return
        if self.stack and self.stack[-1] == t:
            self.stack.pop()
        elif t in self.stack:
            while self.stack and self.stack.pop() != t:
                pass
        else:
            self.stray += 1


def validate() -> bool:
    ok = True
    print("=== VALIDATE (structure + nav parity) ===")
    for p in PAGES:
        h = (DOCS / p).read_text(encoding="utf-8")
        v = _V()
        v.feed(h)
        nav = re.search(r"<nav>.*?</nav>", h, re.S)
        items = re.findall(r">(Home|Intro\+|Gate App|Methodology|Pilot|Audit|Benchmark|Security|Atlas)<",
                           nav.group(0) if nav else "")
        items_uniq = list(dict.fromkeys(items))
        navs = h.count("<nav>"), h.count("</nav>")
        good = (not v.stack and not v.stray and navs == (1, 1) and items_uniq == NAV_ITEMS)
        ok = ok and good
        flag = "OK " if good else "XX "
        print(f"  {flag}{p:20} unclosed={len(v.stack)} stray={v.stray} nav={navs[0]}/{navs[1]} "
              f"items={'·'.join(items_uniq) if items_uniq != NAV_ITEMS else '7 canonical'}")
    print("VALIDATE:", "PASS" if ok else "FAIL")
    return ok


def _fetch(path: str) -> bytes:
    # unique query each call defeats any intermediary cache so we read the TRUE current revision
    cb = hashlib.sha1(f"{path}{time.time()}".encode()).hexdigest()[:8]
    req = urllib.request.Request(f"{BASE}{path}?cb={cb}", headers={"Cache-Control": "no-cache"})
    return urllib.request.urlopen(req, timeout=30, context=_CTX).read()


def verify_live() -> bool:
    print("=== VERIFY (live bytes == local bytes) ===")
    all_ok = True
    for p in PAGES:
        local = (DOCS / p).read_bytes()
        try:
            live = _fetch(p)
        except Exception as e:
            print(f"  XX {p:20} fetch error: {e}")
            all_ok = False
            continue
        same = hashlib.sha256(live).hexdigest() == hashlib.sha256(local).hexdigest()
        all_ok = all_ok and same
        print(f"  {'OK ' if same else 'XX '}{p:20} live={len(live)}B local={len(local)}B "
              f"{'identical' if same else 'MISMATCH'}")
    print("VERIFY:", "PASS — live is the committed version" if all_ok else "FAIL — live differs from local")
    return all_ok


def deploy() -> bool:
    print("=== DEPLOY (az containerapp up --source) ===")
    r = subprocess.run(["az", "containerapp", "up", "--name", APP, "--resource-group", RG,
                        "--source", "."], cwd=str(ROOT), capture_output=True, text=True)
    # az often exits non-zero on the log-stream teardown (OOM 144) AFTER a successful revision push;
    # the authoritative signal is the post-deploy live-bytes check, not az's exit code.
    tail = "\n".join((r.stdout + r.stderr).splitlines()[-6:])
    print(tail)
    print(f"(az exit {r.returncode} — not authoritative; the VERIFY step below is the real gate)")
    _rebind_krenniq()
    return True


def _rebind_krenniq() -> None:
    # CRITICAL (see CLAUDE.md §2): every capas image update breaks the TLS SNI bindings of the custom
    # hostnames on this app at the edge (curl -> no peer certificate), so they go DOWN after a deploy.
    # Re-bind BOTH the apex (krenniq.com, the umbrella landing) and capas.krenniq.com (the tool) every
    # time — idempotent. The edge then takes ~2–5 min to propagate. (atlas.krenniq.com is on the atlas
    # app and is re-bound by Atlas's own deploy.)
    print("=== RE-BIND custom hostnames TLS (always, post-deploy — or the domains die) ===")
    for host, cert in (("krenniq.com", "mc-capas-env-krenniq-com-3031"),
                       ("capas.krenniq.com", "mc-capas-env-capas-krenniq-co-5290")):
        b = subprocess.run(["az", "containerapp", "hostname", "bind", "--hostname", host,
                            "-n", APP, "-g", RG, "--environment", "capas-env", "--certificate", cert],
                           cwd=str(ROOT), capture_output=True, text=True)
        out = b.stdout + b.stderr
        print(f"  {host}:", "ok (SniEnabled)" if "SniEnabled" in out else f"CHECK MANUALLY: {out.strip()[-160:]}")
    print("  (allow ~2–5 min for the edge to serve HTTPS 200 on both)")


def poll_until_live(timeout_s: int = 420) -> bool:
    print(f"=== POLL live until it matches local (<= {timeout_s}s) ===")
    t0 = time.time()
    elapsed = 0.0
    while elapsed < timeout_s:
        if verify_live():
            print(f"LIVE in sync after {elapsed:.0f}s.")
            return True
        time.sleep(15)
        elapsed = time.time() - t0
        print(f"  ...still propagating ({elapsed:.0f}s)")
    print("POLL: TIMEOUT — live never matched local. Investigate the revision.")
    return False


def _ui_gate() -> bool:
    # Optional design gate: run the local UI lab (render + layout-consistency assertions) BEFORE
    # deploying, so a column/gutter/nav/mobile-overflow regression is caught locally in seconds
    # instead of shipping. Opt-in via `--ui` (keeps the plain deploy fast when you don't need it).
    print("=== UI GATE (designlab/check.py) ===")
    r = subprocess.run([sys.executable, "designlab/check.py"], cwd=str(ROOT))
    return r.returncode == 0


def main() -> int:
    if "--verify" in sys.argv:
        return 0 if verify_live() else 1
    if not validate():
        print("Refusing to deploy: fix validation first.")
        return 1
    if "--ui" in sys.argv and not _ui_gate():
        print("Refusing to deploy: UI layout gate failed (run `python3 designlab/check.py`).")
        return 1
    deploy()
    return 0 if poll_until_live() else 1


if __name__ == "__main__":
    raise SystemExit(main())
