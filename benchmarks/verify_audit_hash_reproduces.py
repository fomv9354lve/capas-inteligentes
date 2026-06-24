"""Conformance check: the gate's audit_hash is RE-DERIVABLE and TAMPER-EVIDENT.

CAPAS's core claim is "re-derive more than you trust". This asserts that property for the gate's
audit_hash: (1) every verdict (ACCEPT / REWRITE / REJECT / HOLD, schema-error HOLD included) carries an
audit_hash; (2) an independent party can reproduce it from the returned result with the published recipe;
(3) altering any load-bearing field of the result makes the recomputed hash diverge — so tampering is
detectable. If any of these fail, the "re-derivable" claim is a slogan, not a property.
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


CASES = {
    "ACCEPT":      ("statistical_confidence", {"p_value": 0.03, "alpha": 0.05, "effect_direction_confirmed": True}),
    "REJECT":      ("statistical_confidence", {"p_value": 0.20, "alpha": 0.05, "effect_direction_confirmed": True}),
    "REWRITE":     ("statistical_confidence", {"p_value": 0.03, "alpha": 0.05, "effect_direction_confirmed": False}),
    "HOLD_missing": ("statistical_confidence", {"p_value": 0.03}),
    "HOLD_schema":  ("statistical_confidence", {"p_value": "not-a-number", "alpha": 0.05, "effect_direction_confirmed": True}),
}


def main() -> int:
    failures = []
    for name, (ct, ev) in CASES.items():
        r = _gate(ct, ev)

        # (1) audit_hash present
        if not r.get("audit_hash"):
            failures.append(f"{name}: no audit_hash on the result")
            continue

        # (2) re-derivable: the published verifier confirms it
        v = capas.verify_audit_hash(r)
        if not v.get("verified"):
            failures.append(f"{name}: audit_hash did not re-derive ({v.get('recomputed')} != {v.get('claimed')})")
            continue

        # (3) tamper-evident: flipping the verdict must break the hash
        tampered = dict(r)
        tampered["verdict"] = "ACCEPT" if r["verdict"] != "ACCEPT" else "REJECT"
        if capas.verify_audit_hash(tampered).get("verified"):
            failures.append(f"{name}: tampering with verdict did NOT change the hash (not tamper-evident)")
            continue

        print(f"  OK {name:13} {r['verdict']:8} audit_hash re-derives + tamper-evident")

    if failures:
        print("FAIL — the audit_hash is not the re-derivable, tamper-evident contract it claims to be:")
        for f in failures:
            print("   XX", f)
        return 1
    print(f"PASS — all {len(CASES)} verdicts carry a re-derivable, tamper-evident audit_hash.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
