"""Containment gate: Cara 1 (product) is decoupled from Cara 2 (research/cognitive).

Enforces the load-bearing rule — the dependency arrow never reverses (Cara 1 never
imports Cara 2) — and the honesty firewall — the product certificate surface carries
no consciousness-style overclaim. Wired into `capas validate` so the product cannot
ship coupled to, or over-claiming from, the cognitive layer.
"""
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

CARA1 = {"capas_verify", "capas_route", "capas_rcc", "capas_admissibility", "capas_conformal",
         "capas_braid", "capas_extract", "capas_sql", "capas_xbrl", "capas_quantum",
         "capas_circuits", "capas_ezkl"}
CARA2 = {"capas_conjecture", "capas_loop", "capas_hierarchy", "capas_think", "capas_integration",
         "capas_value", "capas_process", "capas_mind"}

# Genuine overclaim terms that must NEVER appear on the product (Cara 1) output surface.
FORBIDDEN_OUTPUT = ("conscious", "awareness", "sentien", "thinks like", "a mind", "psyche",
                    "lacan", "zizek", "žižek")


def _imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text())
    out: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            out |= {a.name.split(".")[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module:
            out.add(node.module.split(".")[0])
    return out


def run() -> int:
    fails = []

    # 1. dependency direction: no Cara 1 module imports a Cara 2 module
    for mod in sorted(CARA1):
        f = ROOT / f"{mod}.py"
        if not f.exists():
            continue
        bad = _imports(f) & CARA2
        if bad:
            fails.append(f"COUPLING: Cara-1 module {mod} imports Cara-2 {sorted(bad)}")
    print(f"{'✅' if not fails else '❌'} dependency direction: Cara 1 never imports Cara 2 "
          f"({len(CARA1)} product modules scanned)")

    # 2. product ships without Cara 2: Cara 1 modules import-load with the cognitive layer absent
    #    (static check: their imports resolve only within Cara 1 + stdlib/third-party, never Cara 2)
    leaks = [m for m in CARA1 if (ROOT / f"{m}.py").exists() and (_imports(ROOT / f"{m}.py") & CARA2)]
    print(f"{'✅' if not leaks else '❌'} product is Cara-2-optional: no Cara-1 module needs the cognitive layer")

    # 3. honesty firewall: the product certificate surface carries no overclaim
    import capas_rcc
    import capas_verify
    SV = "capas-claim-payload-v3"
    FIN = {"reported_value": 1.0, "reference_value": 1.0, "tolerance": 1.0, "metric_period_match": True}
    pl = {"schema_version": SV, "claim": {"id": "c", "type": "financial_metric_claim", "text": "x"},
          "evidence": {**FIN, "accounting": {"identity": "balance_sheet", "assets": 1000, "liabilities": 600, "equity": 400}}}
    surface = (json.dumps(capas_rcc.rcc(pl)) + json.dumps(capas_verify.verify(pl))).lower()
    found = [t for t in FORBIDDEN_OUTPUT if t in surface]
    if found:
        fails.append(f"OVERCLAIM: product certificate surface contains {found}")
    print(f"{'✅' if not found else '❌'} honesty firewall: product certificate surface free of overclaim terms")

    # 4. Φ is always disclosed as a proxy, never bare "Φ" implying real integrated information
    import capas_integration
    intg = (str(capas_integration.__doc__ or "") + str(capas_integration.integration.__doc__ or "")).lower()
    ok_proxy = "proxy" in intg or "fiedler" in intg or "algebraic connectivity" in intg
    print(f"{'✅' if ok_proxy else '❌'} Φ disclosed as a proxy (spectral algebraic-connectivity heuristic)")
    if not ok_proxy:
        fails.append("Φ not disclosed as a proxy")

    ok = not fails and not leaks
    if fails:
        for x in fails:
            print("   ", x)
    print("CARA DECOUPLING + HONESTY: pass ✅" if ok else "CARA DECOUPLING: FAILURES ❌")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(run())
