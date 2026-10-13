#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Dump LEAF text elements lacking data-es (second pass after inject_data_es.py, whose non-overlapping regex
swallows leaves nested inside a matched <div>). Scans OPENING tags only, so nothing is consumed; a leaf = the
inner HTML up to the matching close tag contains no block tag and no same-tag opening. Leaves that sit inside
an element already carrying data-es/data-en are dropped (their translation lives in the parent), as are
engine-output / code-like spans that must stay verbatim.
Usage: python3 scripts/dump_untranslated_leaves.py docs/page.html > leaves.json   (keys = offset of '<')"""
import html, json, re, sys
from pathlib import Path

TAGS = r"h[1-4]|p|li|span|td|th|dt|dd|summary|label|button|strong|em|small|figcaption|blockquote"
BLOCK = re.compile(r"<(div|p|ul|ol|li|h[1-4]|table|section|nav|script|style|input|textarea|select|button|form)\b")
SKIP_CLASS = re.compile(r'class="[^"]*\b(vp-row-text|vp-meta|vp-row-tag|vp-badge|vp-schema|vp-title|aj-[a-z]|fam-chip|vc\b|vc-|verdict-chip|verdict-badge|verdict-card-badge|foot-copy|footer-copy|settings-val|audit-val|payload-status-pill|sample-btn|panel-tag|tag )')


def leaves(s: str):
    out = []
    for m in re.finditer(rf"<({TAGS})\b([^>]*)>", s):
        tag, attrs = m.group(1), m.group(2)
        if "data-es=" in attrs or "data-en=" in attrs or attrs.strip().endswith("/"):
            continue
        close = s.find(f"</{tag}>", m.end())
        if close < 0:
            continue
        inner = s[m.end():close]
        if f"<{tag}" in inner or BLOCK.search(inner):
            continue
        txt = html.unescape(re.sub(r"<[^>]+>", "", inner)).strip()
        if len(txt) < 3 or re.fullmatch(r"[\d\W_]+", txt):
            continue
        out.append({"offset": m.start(), "tag": tag, "attrs": attrs.strip(), "inner": inner, "text": re.sub(r"\s+", " ", txt)})
    return out


def translated_ranges(s: str):
    rng = []
    for m in re.finditer(r"<([a-z][a-z0-9]*)\b([^>]*\bdata-(?:es|en)=)[^>]*>", s):
        tag = m.group(1); depth = 1; i = m.end()
        pat = re.compile(rf"<(/?){tag}\b")
        while depth:
            mm = pat.search(s, i)
            if not mm:
                i = len(s); break
            depth += -1 if mm.group(1) else 1; i = mm.end()
        rng.append((m.start(), i))
    return rng


def filtered(s: str):
    rng = translated_ranges(s)
    out = []
    for x in leaves(s):
        o = x["offset"]
        if any(a <= o < b for a, b in rng):
            continue
        if x["tag"] in ("em", "strong", "small"):      # inline fragments: translate the parent instead
            continue
        if SKIP_CLASS.search(x["attrs"]) or x["text"].startswith(("©", '"')):
            continue
        if re.fullmatch(r"[A-Z_ /0-9]+", x["text"]):     # ACCEPT / REWRITE / SCHEMA V3 ...
            continue
        out.append(x)
    return out


if __name__ == "__main__":
    s = Path(sys.argv[1]).read_text(encoding="utf-8")
    print(json.dumps(filtered(s), ensure_ascii=False, indent=0))
