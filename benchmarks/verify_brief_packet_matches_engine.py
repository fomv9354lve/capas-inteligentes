#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""docs/customer-brief.html embeds the engine's decision packet inside <pre id="brief-packet">. It must equal, field for
field, what benchmarks/brief_decision_packet.py produces now, and docs/brief_decision_packet.json must match too.
Run: python3 benchmarks/verify_brief_packet_matches_engine.py [--fix]"""
from __future__ import annotations
import html, json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from benchmarks.brief_decision_packet import PAYLOAD, packet, render  # noqa: E402
PAGE, JSON = ROOT / "docs" / "customer-brief.html", ROOT / "docs" / "brief_decision_packet.json"
PRE = re.compile(r'(<pre id="brief-packet"[^>]*>)(.*?)(</pre>)', re.S)


def main() -> int:
    fix = "--fix" in sys.argv
    page = PAGE.read_text(encoding="utf-8"); m = PRE.search(page)
    live = packet(); errs = []
    if not m:
        errs.append('page has no <pre id="brief-packet">')
    else:
        try:
            shown = json.loads(html.unescape(m.group(2)))
        except json.JSONDecodeError as e:
            shown = None; errs.append(f"page packet is not valid JSON: {e}")
        if shown is not None and shown != live:
            diff = [k for k in set(shown) | set(live) if shown.get(k) != live.get(k)]
            errs.append(f"page packet differs from the engine on: {sorted(diff)}")
    try:
        stored = json.loads(JSON.read_text(encoding="utf-8"))
        if stored.get("result") != live or stored.get("payload") != PAYLOAD:
            errs.append("docs/brief_decision_packet.json differs from the engine")
    except (OSError, json.JSONDecodeError) as e:
        errs.append(f"docs/brief_decision_packet.json unreadable: {e}")
    if errs and fix and m:
        new = page[:m.start(2)] + html.escape(render(), quote=False) + page[m.end(2):]
        PAGE.write_text(new, encoding="utf-8")
        JSON.write_text(json.dumps({"payload": PAYLOAD, "result": live}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print("FIXED: page and JSON regenerated from the engine"); return 0
    print("PASS — the brief's decision packet is the engine's output" if not errs else "FAIL:\n  " + "\n  ".join(errs))
    return 0 if not errs else 1


if __name__ == "__main__":
    raise SystemExit(main())
