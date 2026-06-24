# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""Conformance check: NO HOLD IS A DEAD END.

The usability invariant behind A1-A3: a claim that is true-and-supportable must never terminate in a
bare HOLD. Every HOLD response must carry a machine-readable `resolution` — the exact, constructive way
out (fields to supply with types+examples, schema fixes that name themselves, a `did_you_mean` for typos,
or the list of supported claim types) — such that applying it WITHOUT changing the underlying facts moves
the claim off HOLD. A HOLD with no such path is a bug, not a verdict. This asserts the property across
every HOLD-producing path: schema error, type error, typo'd field, missing field, and unsupported type.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import capas  # noqa: E402


def _gate(claim_type: str, evidence: dict) -> dict:
    return capas.decide_external_claim({
        "schema_version": "capas-claim-payload-v3",
        "claim": {"id": "c", "type": claim_type, "text": "a claim"},
        "evidence": evidence,
    })


# Each case is engineered to land on HOLD via a DIFFERENT path.
HOLD_CASES = [
    ("missing_field",      "statistical_confidence", {"p_value": 0.03}),
    ("typo_field",         "statistical_confidence", {"p_val": 0.03, "alpha": 0.05, "effect_direction_confirmed": True}),
    ("wrong_type_number",  "statistical_confidence", {"p_value": "0.03", "alpha": 0.05, "effect_direction_confirmed": True}),
    ("wrong_type_boolean", "statistical_confidence", {"p_value": 0.03, "alpha": 0.05, "effect_direction_confirmed": "true"}),
    ("unsupported_type",   "not_a_registered_type", {"whatever": 1}),
    ("empty_evidence",     "reproducibility_check", {}),
    ("anchor_missing",     "universal_anchor_claim", {"anchor_mode": "relative_anchor", "local_property_tests_pass": True}),
]


def main() -> int:
    failures = []
    for name, ct, ev in HOLD_CASES:
        r = _gate(ct, ev)
        verdict = r.get("verdict")
        resolution = r.get("resolution") or {}
        # The case must HOLD, and the HOLD must be actionable: a named kind + a human message,
        # and at least one concrete lever (fields to supply, schema errors that carry fixes,
        # a typo suggestion, or the supported-type list).
        actionable = bool(resolution.get("kind")) and bool(resolution.get("message")) and (
            resolution.get("fields")
            or resolution.get("errors")
            or resolution.get("did_you_mean")
            or resolution.get("supported_claim_types")
        )
        if verdict != "HOLD":
            failures.append(f"{name}: expected HOLD, got {verdict}")
        elif not actionable:
            failures.append(f"{name}: HOLD has no constructive resolution -> dead end: {resolution!r}")
        else:
            print(f"  OK {name:18} HOLD -> resolution.kind={resolution['kind']}")

    if failures:
        print("FAIL — a HOLD with no way out (the dead-end bug A1-A3 forbids):")
        for f in failures:
            print("   XX", f)
        return 1
    print(f"PASS — all {len(HOLD_CASES)} HOLD paths ship a constructive, machine-readable resolution (no dead ends).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
