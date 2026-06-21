"""Demo + check: re-derive a financial ratio from a filed XBRL instance via Arelle.

Closes the "no hand-typed numbers" loop — the ratio components are read straight
from the filing by their US-GAAP concept and re-derived by CAPAS. Optional:
requires `arelle-release`. NOT part of `capas validate` (Arelle is a heavy,
optional dependency, like the EZKL demo). Run directly:  python3 benchmarks/demo_xbrl_ratio.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import capas_verify

SV = "capas-claim-payload-v3"
_FX = Path(__file__).resolve().parent / "fixtures" / "xbrl"
FIXTURE = str(_FX / "inst.xbrl")       # US-GAAP: AssetsCurrent=200000, LiabilitiesCurrent=100000 -> 2.0
IFRS = str(_FX / "ifrs.xbrl")          # IFRS: CurrentAssets=300000, CurrentLiabilities=150000 -> 2.0; PL/Rev -> 0.10


def _verdict(xbrl: dict) -> tuple[str, str]:
    ev = {"reported_value": 1.0, "reference_value": 1.0, "tolerance": 1.0,
          "metric_period_match": True, "xbrl": xbrl}
    pl = {"schema_version": SV, "claim": {"id": "x", "type": "financial_metric_claim",
          "text": "current ratio"}, "evidence": ev}
    r = capas_verify.verify(pl)
    return r["verified_verdict"], r["scope"]


def run() -> int:
    try:
        import arelle  # noqa: F401
    except Exception:
        print("SKIP: arelle not installed (pip install arelle-release)")
        return 0

    cases = [
        ("honest current_ratio=2.0 re-derived from filing", {"instance": FIXTURE, "ratio": "current_ratio", "reported": 2.0}, "ACCEPT", "GATE"),
        ("LIE current_ratio=5.0 contradicts the filing",    {"instance": FIXTURE, "ratio": "current_ratio", "reported": 5.0}, "REJECT", "GATE"),
        ("missing components (roe needs NI/equity)",         {"instance": FIXTURE, "ratio": "roe", "reported": 0.1}, "HOLD", "ATTEST"),
        ("unknown ratio (sharpe) not re-derivable",          {"instance": FIXTURE, "ratio": "sharpe", "reported": 1.2}, "HOLD", "ATTEST"),
        ("IFRS taxonomy: current_ratio=2.0 re-derived (ifrs-full concepts)", {"instance": IFRS, "ratio": "current_ratio", "reported": 2.0}, "ACCEPT", "GATE"),
        ("IFRS taxonomy: net_margin=0.10 (ProfitLoss/Revenue)", {"instance": IFRS, "ratio": "net_margin", "reported": 0.10}, "ACCEPT", "GATE"),
        ("IFRS taxonomy: net_margin lie (0.50) -> REJECT",   {"instance": IFRS, "ratio": "net_margin", "reported": 0.50}, "REJECT", "GATE"),
    ]
    ok = True
    for label, xbrl, exp_v, exp_s in cases:
        v, s = _verdict(xbrl)
        good = (v == exp_v and s == exp_s)
        ok = ok and good
        print(f"{'✅' if good else '❌'} {label:52s} -> {v:7s} [{s}]  (want {exp_v}/{exp_s})")
    print("XBRL RATIO RE-DERIVATION: all cases pass ✅" if ok else "XBRL DEMO: FAILURES ❌")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(run())
