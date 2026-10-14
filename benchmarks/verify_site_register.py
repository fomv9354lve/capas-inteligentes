#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Register guard for the served pages (owner, 2026-10-14: "no AI wording, big-3 professional"). Enforces the
mechanical half of docs/STYLE_GUIDE.md on VISIBLE text (scripts, styles and data-* attributes excluded; the Spanish
twins are checked separately): no em-dashes, no question headlines, no exclamation marks, no self-praise or metaphor
vocabulary. Run: python3 benchmarks/verify_site_register.py"""
from __future__ import annotations
import html, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; DOCS = ROOT / "docs"
PAGES = ["index.html", "in-depth.html", "app.html", "customer-brief.html", "pilot-packet.html", "audit.html",
         "benchmark.html", "security.html", "governance.html", "krenniq.html", "legal.html"]
SELF_PRAISE = re.compile(r"\b(honest scope|honesty footer|we do(n'?t| not) hide|not a slide|slogan|the punch|the moat|moat is|"
                         r"stop trusting plausible|battle[- ]tested|bulletproof|rock[- ]solid|game[- ]chang\w+|cutting[- ]edge|"
                         r"state[- ]of[- ]the[- ]art|world[- ]class|seamless\w*|leverage\w*|unlock\w*|empower\w*|supercharg\w+|"
                         r"revolutioniz\w+|paradigm|synerg\w+|delve|enemy)\b", re.I)
SELF_PRAISE_ES = re.compile(r"\b(alcance honesto|no lo escondemos|no es una diapositiva|eslogan|el foso|enemigo|"
                            r"revolucionari\w+|sin fricci\w+|de vanguardia|clase mundial)\b", re.I)


def visible(html_src: str, lang: str) -> tuple[str, list[str]]:
    b = re.sub(r"<script.*?</script>|<style.*?</style>|<pre.*?</pre>|<code.*?</code>", "", html_src, flags=re.S)  # engine output and code are literal, not copy
    if lang == "en":
        # English base text: drop the Spanish twins; for krenniq.html the base is Spanish and data-en holds English
        twins = re.findall(r'data-en="([^"]*)"', b)
        b = re.sub(r'data-(es|en)="[^"]*"', "", b)
        heads = [html.unescape(re.sub(r"<[^>]+>", "", h)) for h in re.findall(r"<h[1-4][^>]*>(.*?)</h[1-4]>", b, flags=re.S)]
        text = html.unescape(re.sub(r"<[^>]+>", " ", b))
        return (text + " " + " ".join(html.unescape(t) for t in twins)), heads
    twins = re.findall(r'data-es="([^"]*)"', b)
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", t)) for t in twins), []


def main() -> int:
    errs = []
    for name in PAGES:
        p = DOCS / name
        if not p.is_file():
            continue
        src = p.read_text(encoding="utf-8")
        for lang in ("en", "es"):
            text, heads = visible(src, lang)
            n_dash = text.count("—")
            if n_dash:
                errs.append(f"{name} [{lang}]: {n_dash} em-dash(es) in visible text")
            n_excl = len(re.findall(r"!(?!\[)", text))
            if n_excl:
                errs.append(f"{name} [{lang}]: {n_excl} exclamation mark(s)")
            for h in heads:
                if "?" in h:
                    errs.append(f"{name}: question headline {h.strip()[:70]!r}")
            for m in (SELF_PRAISE if lang == "en" else SELF_PRAISE_ES).finditer(text):
                errs.append(f"{name} [{lang}]: {m.group(0)!r}")
    print("PASS — register guard: no em-dashes, question headlines, exclamations or self-praise on the served pages"
          if not errs else "FAIL:\n  " + "\n  ".join(errs[:60]) + (f"\n  … {len(errs) - 60} more" if len(errs) > 60 else ""))
    return 0 if not errs else 1


if __name__ == "__main__":
    raise SystemExit(main())
