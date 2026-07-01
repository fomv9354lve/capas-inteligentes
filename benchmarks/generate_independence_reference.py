#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""Generate the per-gate independence reference table (BACKED: regenerates with a hash).

For each claim type, estimate how many MUTUALLY INDEPENDENT constraints its required checks
really amount to (M_eff), from the empirical dependence of those checks across a reference
corpus (the n=28 pilot). The table lets a CAPAS certificate report the gate's effective
strength + theater tax honestly, instead of overstating "N checks" as N independent constraints.

HONEST SCOPE: this is a per-GATE property estimated from the reference corpus, NOT a per-claim
measurement, and it is an OPTIMISTIC UPPER BOUND (reliability-independence is unmeasured). The
pilot evidence is coded near all-pass/all-fail, so M_eff here is low (~1); a richer, varied
corpus would raise it. Regenerate: `python3 benchmarks/generate_independence_reference.py`.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np

import capas
import capas_independence as ci

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "independence_reference.json"


def _load_pilot():
    spec = importlib.util.spec_from_file_location("pilot_real", str(ROOT / "benchmarks" / "pilot_real.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _satisfied(v):
    if isinstance(v, bool):
        return 1 if v else 0
    if isinstance(v, str):
        return 0 if v.lower() in ("false", "no", "0", "") else 1
    if isinstance(v, (int, float)):
        return 1
    return 0


def build() -> dict:
    pilot = _load_pilot()
    reg = capas.CLAIM_TYPE_REGISTRY
    from collections import defaultdict
    groups: dict[str, list] = defaultdict(list)
    for _name, _gt, ctype, ev in pilot.CORPUS:
        req = reg[ctype]["required"]
        groups[ctype].append([_satisfied(ev.get(f, False)) for f in req])

    table: dict[str, dict] = {}
    for ctype, rows in groups.items():
        if len(rows) < 4:  # too few claims to estimate dependence honestly
            continue
        rep = ci.independence_report(np.array(rows, dtype=float))
        table[ctype] = {
            "m_eff": rep["m_eff"],
            "m_eff_li_ji": rep["m_eff_li_ji"],
            "m_eff_participation": rep["m_eff_participation"],
            "independence_yield": rep["independence_yield"],
            "theater_tax": rep["theater_tax"],
            "n_checks": rep["n_checks"],
            "n_reference_claims": len(rows),
        }
    doc = {
        "reference_corpus": "pilot_real (n=28 agent-coded, retracted-vs-replicated)",
        "method": "M_eff = min(Li&Ji 2005, participation ratio) on tetrachoric dependence of the gate's required checks",
        "bound": "OPTIMISTIC UPPER BOUND — per-gate, reliability-independence unmeasured; GIGO floor stays.",
        "caveat": "pilot evidence is coded near all-pass/all-fail, so M_eff is low (~1); varied evidence would raise it.",
        "gates": table,
    }
    payload = json.dumps(doc, sort_keys=True).encode()
    doc["content_sha256"] = "sha256:" + hashlib.sha256(payload).hexdigest()
    return doc


def main() -> int:
    doc = build()
    OUT.write_text(json.dumps(doc, indent=2) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}  ({doc['content_sha256'][:22]}…)")
    for ct, g in sorted(doc["gates"].items()):
        print(f"  {ct:26s} M_eff {g['m_eff']:.2f} of {g['n_checks']} checks  "
              f"(yield {g['independence_yield']:.0%}, theater_tax {g['theater_tax']}x)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
