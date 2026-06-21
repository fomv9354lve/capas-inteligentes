#!/usr/bin/env python3
"""Regenerate the Content-Security-Policy sha256 hashes for docs/app.html.

app.html ships a strict CSP with `'unsafe-hashes'`, so every inline surface needs
its own sha256 allow-hash:
  style-src  -> the single <style> block + every distinct inline style="..." value
  script-src -> the single <script> block + every distinct inline on*="..." handler

Any edit to the CSS/JS/handlers/inline-styles changes a hash and the browser blocks
the surface. This script recomputes the full hash set from the current inline content
and rewrites the CSP meta tag in place.

Usage:
  python3 scripts/regen_app_csp.py --check   # compare computed vs current (no write)
  python3 scripts/regen_app_csp.py --write   # rebuild the CSP meta tag in app.html
"""
from __future__ import annotations

import base64
import hashlib
import re
import sys
from pathlib import Path

APP = Path(__file__).resolve().parents[1] / "docs" / "app.html"


def sha(value: str) -> str:
    digest = hashlib.sha256(value.encode("utf-8")).digest()
    return "'sha256-" + base64.b64encode(digest).decode("ascii") + "'"


def inline_style_block(html: str) -> str:
    m = re.search(r"<style[^>]*>(.*?)</style>", html, re.S)
    return m.group(1) if m else ""


def inline_script_block(html: str) -> str:
    # the app has exactly one inline <script> with no attributes
    m = re.search(r"<script>(.*?)</script>", html, re.S)
    return m.group(1) if m else ""


def attr_values(html: str, attr_pattern: str) -> list[str]:
    # capture the raw text between the quotes of matching attributes
    return re.findall(attr_pattern, html)


def compute_hashes(html: str) -> tuple[list[str], list[str]]:
    style_block = inline_style_block(html)
    script_block = inline_script_block(html)

    # Scan inline attributes only in real markup, NOT inside the <script>/<style>
    # block bodies (which contain handler strings in JS template literals that are
    # interpolated at runtime and are not static inline handlers).
    markup = re.sub(r"<script>.*?</script>", "", html, flags=re.S)
    markup = re.sub(r"<style[^>]*>.*?</style>", "", markup, flags=re.S)

    # inline style="..." attribute values (double-quoted)
    style_attrs = attr_values(markup, r'\sstyle="([^"]*)"')
    # inline event handlers on*="..." (double-quoted)
    handlers = attr_values(markup, r'\son[a-z]+="([^"]*)"')

    style_hashes = {sha(style_block)} | {sha(v) for v in style_attrs}
    script_hashes = {sha(script_block)} | {sha(v) for v in handlers}
    return sorted(style_hashes), sorted(script_hashes)


def current_hashes(html: str) -> tuple[set[str], set[str]]:
    csp = re.search(r'Content-Security-Policy"\s*content="([^"]*)"', html)
    content = csp.group(1) if csp else ""
    style_seg = re.search(r"style-src([^;]*)", content)
    script_seg = re.search(r"script-src([^;]*)", content)
    sh = set(re.findall(r"'sha256-[^']*'", style_seg.group(1) if style_seg else ""))
    ch = set(re.findall(r"'sha256-[^']*'", script_seg.group(1) if script_seg else ""))
    return sh, ch


def build_csp(style_hashes: list[str], script_hashes: list[str]) -> str:
    # style-src must allow the Google Fonts stylesheet; font-src must allow the
    # gstatic font files. Dropping these blocks Inter / Space Mono and the app
    # silently falls back to system fonts.
    style_src = " ".join(["style-src 'self' 'unsafe-hashes' https://fonts.googleapis.com"] + style_hashes)
    script_src = " ".join(["script-src 'self' 'unsafe-hashes'"] + script_hashes)
    return (
        "default-src 'self'; img-src 'self' data:; "
        + style_src + "; "
        + script_src + "; "
        + "font-src 'self' https://fonts.gstatic.com; "
        + "object-src 'none'; base-uri 'none'; form-action 'none'; connect-src 'none'"
    )


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "--check"
    html = APP.read_text(encoding="utf-8")
    style_hashes, script_hashes = compute_hashes(html)
    cur_style, cur_script = current_hashes(html)

    new_style, new_script = set(style_hashes), set(script_hashes)
    style_ok = new_style == cur_style
    script_ok = new_script == cur_script

    print(f"style-src: computed {len(new_style)} | current {len(cur_style)} | match={style_ok}")
    print(f"script-src: computed {len(new_script)} | current {len(cur_script)} | match={script_ok}")
    if not style_ok:
        print("  style only-in-computed:", sorted(new_style - cur_style))
        print("  style only-in-current :", sorted(cur_style - new_style))
    if not script_ok:
        print("  script only-in-computed:", sorted(new_script - cur_script))
        print("  script only-in-current :", sorted(cur_script - new_script))

    if mode == "--write":
        new_content = build_csp(style_hashes, script_hashes)
        html2 = re.sub(
            r'(Content-Security-Policy"\s*content=")[^"]*(")',
            lambda m: m.group(1) + new_content + m.group(2),
            html,
            count=1,
        )
        APP.write_text(html2, encoding="utf-8")
        print("CSP meta rewritten.")
        return 0

    return 0 if (style_ok and script_ok) else 1


if __name__ == "__main__":
    raise SystemExit(main())
