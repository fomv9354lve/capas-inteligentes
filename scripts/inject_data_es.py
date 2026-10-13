#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Inject `data-es` attributes into a CAPAS page from {index: spanish_html} JSON batches, using the same
leaf-element extraction as the items dump (same regex, same filters) so indices line up. Idempotent per
element: an element that already has data-es is skipped. Usage:
    python3 scripts/inject_data_es.py docs/index.html batch1.json [batch2.json ...]"""
import html, json, re, sys
from pathlib import Path

page = Path(sys.argv[1]); s = page.read_text(encoding="utf-8")
es = {}
for b in sys.argv[2:]:
    es.update({int(k): v for k, v in json.load(open(b, encoding="utf-8")).items()})
items = []
for m in re.finditer(r"<(h[1-4]|p|li|button|a|span|div|td|th|summary|label)\b([^>]*)>(.*?)</\1>", s, re.S):
    tag, attrs, inner = m.group(1), m.group(2), m.group(3)
    if re.search(r"<(div|p|ul|ol|li|h[1-4]|table|section|nav|script|style)\b", inner): continue
    txt = html.unescape(re.sub(r"<[^>]+>", "", inner)).strip()
    if len(txt) < 3 or re.fullmatch(r"[\d\W_]+", txt): continue
    if tag in ("span", "div", "a") and len(txt) < 4: continue
    items.append((len(items), m.start(1) - 1, tag, attrs))   # ya-traducidos cuentan para que los indices sean estables
done = 0
for i, start, tag, attrs in sorted(items, key=lambda t: -t[1]):   # de atrás hacia adelante: los offsets no se mueven
    if i not in es or "data-es=" in attrs or "data-en=" in attrs: continue
    val = es[i].replace('"', "&quot;")
    head = f"<{tag}{attrs}>"
    assert s[start:start + len(head)] == head, (i, s[start:start + 40])
    s = s[:start] + f'<{tag}{attrs} data-es="{val}">' + s[start + len(head):]
    done += 1
page.write_text(s, encoding="utf-8")
print(f"{done} elementos con data-es inyectados en {page} ({len(items)} candidatos, {len(es)} traducciones dadas)")
