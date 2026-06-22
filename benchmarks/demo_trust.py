"""Demo + check: trust-with-accountability — how the human actually handles declarations.

Deterministic. A declaration cannot be re-derived; the human weights it by the source's
TRACK RECORD (earned by surviving refutation, not declarable) and records it against an
identity for later accountability. Asserts: the SAME gamed declaration is worth less from an
unproven/refuted attester than a proven one; a re-derived (GATE) result is not discounted;
and track record moves only with real outcomes, never by declaration.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import capas_trust as T

LOG = ([{"attester": "rigorous_lab", "outcome": "survived"}] * 5 +
       [{"attester": "caught_fraud", "outcome": "survived"}] * 1 +
       [{"attester": "caught_fraud", "outcome": "refuted"}] * 4)


def run() -> int:
    checks = []
    unknown = T.provisional_weight(1.0, "unknown_new", LOG, scope="ATTEST")
    proven = T.provisional_weight(1.0, "rigorous_lab", LOG, scope="ATTEST")
    fraud = T.provisional_weight(1.0, "caught_fraud", LOG, scope="ATTEST")

    checks.append(("unknown attester: a declaration is worth only the 0.5 prior (not the gamed 1.0)",
                   unknown["provisional_weight"] == 0.5))
    checks.append(("proven track record (5 survived) lifts the same declaration above the prior",
                   proven["provisional_weight"] > unknown["provisional_weight"]))
    checks.append(("a refuted attester is discounted BELOW an unknown one",
                   fraud["provisional_weight"] < unknown["provisional_weight"]))

    gate = T.provisional_weight(1.0, "unknown_new", LOG, scope="GATE")
    checks.append(("a RE-DERIVED (GATE) result is NOT discounted — it stands on its own proof",
                   gate["provisional_weight"] == 1.0))

    # track record cannot be declared: an attester not in the log has 0 resolved, trust = prior
    checks.append(("track record is earned, not declarable (no log entries -> 0.5 prior, n=0)",
                   T.track_record(LOG, "made_up_name")["resolved"] == 0
                   and T.track_record(LOG, "made_up_name")["trust"] == 0.5))

    ok = all(c for _, c in checks)
    for label, c in checks:
        print(f"{'✅' if c else '❌'} {label}")
    print(f"   same gamed declaration -> unknown {unknown['provisional_weight']} · "
          f"proven {proven['provisional_weight']} · refuted {fraud['provisional_weight']}")
    print("TRUST-WITH-ACCOUNTABILITY (the human mechanism, mechanized): pass ✅" if ok
          else "TRUST: FAILURES ❌")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(run())
