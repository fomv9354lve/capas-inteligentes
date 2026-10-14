#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""docs/benchmark.html must carry EXACTLY the counts in outputs/family_decision_mix.json (per family, overall, and the
hard-gated percentage). The page is hand-authored HTML; the JSON regenerates on every engine change — found stale on
2026-10-13 (exact_model_solution 104/2 vs 101/5 ACCEPT/HOLD after that day's rules). Same discipline as
verify_gate_contracts_match.py. Run: python3 benchmarks/verify_benchmark_page_matches_mix.py [--fix]"""
from __future__ import annotations
import json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "docs" / "benchmark.html"
MIX = ROOT / "outputs" / "family_decision_mix.json"
ROW = re.compile(r'<tr><td class="fam">([^<]+)</td><td class="n">(\d+)</td><td class="n">(\d+)</td><td class="n">(\d+)</td><td class="n">(\d+)</td><td class="n">(\d+)</td><td>(\d) / 4</td></tr>')
OVERALL = re.compile(r"overall: \{[^}]*\}")


def expected_row(fam: str, j: dict) -> str:
    c = j["counts"]
    return (f'<tr><td class="fam">{fam}</td><td class="n">{j["n"]}</td><td class="n">{c.get("ACCEPT", 0)}</td>'
            f'<td class="n">{c.get("REWRITE", 0)}</td><td class="n">{c.get("REJECT", 0)}</td><td class="n">{c.get("HOLD", 0)}</td>'
            f'<td>{len(j["verdicts_reached"])} / 4</td></tr>')


def main() -> int:
    fix = "--fix" in sys.argv
    html = PAGE.read_text(encoding="utf-8"); mix = json.loads(MIX.read_text(encoding="utf-8"))
    fams = mix["families"]; om = mix["overall_mix"]; total = mix["total_payloads"]
    errs, new = [], html
    for m in ROW.finditer(html):
        fam = m.group(1); j = fams.get(fam)
        if j is None:
            errs.append(f"{fam}: in page, not in JSON"); continue
        if m.group(0) != expected_row(fam, j):
            errs.append(f"{fam}: page {m.groups()[1:6]} != json ({j['n']}, {j['counts'].get('ACCEPT',0)}, {j['counts'].get('REWRITE',0)}, {j['counts'].get('REJECT',0)}, {j['counts'].get('HOLD',0)})")
            new = new.replace(m.group(0), expected_row(fam, j))
    missing = set(fams) - set(ROW.findall(html) and [r[0] for r in ROW.findall(html)])
    if missing: errs.append(f"families missing from page: {sorted(missing)}")
    ov = f"overall: {{'ACCEPT': {om['ACCEPT']}, 'REWRITE': {om['REWRITE']}, 'REJECT': {om['REJECT']}, 'HOLD': {om['HOLD']}}}"
    cur = OVERALL.search(html)
    if not cur or cur.group(0) != ov:
        errs.append(f"overall line: page '{cur.group(0) if cur else None}' != '{ov}'"); new = OVERALL.sub(ov, new)
    import hashlib
    sha = hashlib.sha256(MIX.read_bytes()).hexdigest()[:16]
    for m in re.finditer(r"sha256 <code>([0-9a-f]{16})…</code>", html):
        if m.group(1) != sha:
            errs.append(f"page provenance sha {m.group(1)} != json {sha}"); new = new.replace(m.group(0), f"sha256 <code>{sha}…</code>")
    # the prose "Overall mix" line (EN and ES) carries counts + percentages; it drifts too
    for v in ("ACCEPT", "REWRITE", "REJECT", "HOLD"):
        pct = f"{om[v] / total * 100:.1f}"
        for m in re.finditer(rf"{v} (\d+)</strong> \(([\d.,]+)%\)", html):
            if m.group(1) != str(om[v]) or m.group(2).replace(",", ".") != pct:
                errs.append(f"prose {v} {m.group(1)} ({m.group(2)}%) != {om[v]} ({pct}%)")
                sep = "," if "," in m.group(2) else "."
                new = new.replace(m.group(0), f"{v} {om[v]}</strong> ({pct.replace('.', sep)}%)")
    hard = round((om["REJECT"] + om["REWRITE"]) / total * 100, 1)
    if f"{hard}" not in html: errs.append(f"hard-gated {hard}% not on page")
    if f"N={total}" not in html: errs.append(f"N={total} not on page")
    if errs and fix and new != html:
        PAGE.write_text(new, encoding="utf-8"); print("FIXED rows/overall from JSON:\n  " + "\n  ".join(errs)); return 0
    print(("PASS — benchmark.html matches family_decision_mix.json" if not errs else "FAIL — benchmark.html is stale vs family_decision_mix.json:\n  " + "\n  ".join(errs)))
    return 0 if not errs else 1


if __name__ == "__main__":
    raise SystemExit(main())
