#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Inject data-es by OFFSET (keys from dump_untranslated_leaves.py). Each key is the offset of the element's '<';
the opening tag found there must still match the dumped tag, or the batch is refused (stale offsets). Injected from
the end so earlier offsets stay valid. Usage: python3 scripts/inject_data_es_by_offset.py docs/page.html batch.json"""
import json, re, sys
from pathlib import Path

page = Path(sys.argv[1]); s = page.read_text(encoding="utf-8")
batch = json.load(open(sys.argv[2], encoding="utf-8"))
items = sorted(((int(k), v) for k, v in batch.items()), reverse=True)
for off, es in items:
    m = re.match(r"<([a-z][a-z0-9]*)\b([^>]*)>", s[off:off + 400])
    assert m, (off, s[off:off + 40])
    tag, attrs = m.group(1), m.group(2)
    assert "data-es=" not in attrs, (off, "already translated")
    val = es.replace('"', "&quot;")
    s = s[:off] + f"<{tag}{attrs} data-es=\"{val}\">" + s[off + m.end():]
page.write_text(s, encoding="utf-8")
print(f"{len(items)} data-es inyectados en {page}")
