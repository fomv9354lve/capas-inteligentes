"""Demo + check: the falsifiable-idea generator-filter (imagination vs hallucination).

Deterministic. Independent labels (NOT moved to fit the engine): below absolute zero
and a non-re-deriving sum are REFUTED by anchors; a quantum-circuit conjecture is
deterministically FALSIFIABLE (the simulator is its oracle); a bare empirical claim is
SUBJECT_FALSIFIABLE (only an experiment kills it); an aesthetic claim is SPECULATIVE
(not even wrong). Asserts each lands on its independent label, the kept set = the
falsifiable ones, and the quantum idea ships the SIMULATOR as its attached killer test.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import capas_falsify as F

SV = "capas-claim-payload-v3"
CASES = [
    ("below absolute zero", "REFUTED",
     {"schema_version": SV, "claim": {"id": "1", "type": "physical_claim", "text": "sample sits at -300 C"},
      "evidence": {"physical": {"quantity": "temperature", "value": -300, "unit": "C"}}}),
    ("fabricated sum", "REFUTED",
     {"schema_version": SV, "claim": {"id": "2", "type": "financial_metric_claim", "text": "total is 7"},
      "evidence": {"reported_value": 1.0, "reference_value": 1.0, "tolerance": 0.0, "metric_period_match": True,
                   "computation": {"operation": "sum", "inputs": {"values": [1, 2, 3]}, "reported_value": 7.0, "tolerance": 1e-9}}}),
    ("quantum-circuit conjecture", "FALSIFIABLE",
     {"schema_version": SV, "claim": {"id": "3", "type": "quantum_claim", "text": "this circuit outputs a Bell pair"},
      "evidence": {"quantum_circuit": {"gates": [["H", 0], ["CX", 0, 1]], "claimed_state": "bell"}}}),
    ("empirical, no evidence", "SUBJECT_FALSIFIABLE",
     {"schema_version": SV, "claim": {"id": "4", "type": "empirical_claim", "text": "compound X reduces tumor size in mice"},
      "evidence": {}}),
    ("aesthetic, untestable", "SPECULATIVE",
     {"schema_version": SV, "claim": {"id": "5", "type": "aesthetic_claim", "text": "this molecule is elegant"},
      "evidence": {}}),
]


def run() -> int:
    checks = []
    for name, expect, pl in CASES:
        f = F.falsifiability(pl)
        hit = f["falsifiability"] == expect
        checks.append((f"{name} -> {f['falsifiability']} (== {expect})", hit))

    # the quantum idea must attach the SIMULATOR as its deterministic killer test
    q = F.falsifiability(CASES[2][2])
    sim = any(t.get("rung") == "quantum_circuit" and t["deterministic"] for t in q["killer_test"])
    checks.append(("quantum idea ships the simulator as its attached killer test", sim))

    # the batch filter keeps imagination, discards hallucination
    batch = F.keep_falsifiable([pl for _, _, pl in CASES])
    keep_ok = (batch["kept"] == 2 and batch["discarded_refuted"] == 2
               and batch["discarded_speculative"] == 1)
    checks.append((f"keep_falsifiable: kept {batch['kept']} (imagination), "
                   f"discarded {batch['discarded_refuted']} refuted + {batch['discarded_speculative']} speculative", keep_ok))

    ok = all(c for _, c in checks)
    for label, c in checks:
        print(f"{'✅' if c else '❌'} {label}")
    print("FALSIFIABLE-IDEA GENERATOR (imagination vs hallucination, mechanical): pass ✅" if ok
          else "FALSIFY: FAILURES ❌")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(run())
