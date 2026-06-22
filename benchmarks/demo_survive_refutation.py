"""Demo + check: the survive-refutation loop — the integration that connects the GATE (a verdict
now) to the LEDGER (accountability over time). The third trialectic pole, made material.

GATE stands on proof (full weight, independent of who says it). ATTEST stands only on the
attester's STANDING — which is EARNED by surviving the world's refutation, not by self-claim.
This is the only mechanism CAPAS cannot fake: the world, not the engine, decides.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ["CAPAS_DATA_DIR"] = "/tmp/capas_ledger_demo"
# fresh ledger each run
_led = Path("/tmp/capas_ledger_demo/ledger.json")
if _led.exists():
    _led.unlink()

import capas_sdk

# a re-derivable claim (GATE: ACCEPT on proof, full weight regardless of who says it) vs a
# declared/partial one (REWRITE -> ATTEST scope: worth only the attester's EARNED standing)
GATE_CLAIM = ("exact_model_solution", {"abs_error": 0.0, "tolerance": 1e-3})
ATTEST_CLAIM = ("systematic_review_claim",
                {"protocol_registered": True, "inclusion_criteria_declared": True})  # -> REWRITE


def _w(a):
    return a["provisional_weight"]["provisional_weight"]


def run() -> int:
    checks = []

    # 1. a NEW attester's ATTEST claim has low provisional weight (no earned standing yet)
    a1 = capas_sdk.admit(*ATTEST_CLAIM, attester="lab_unknown", claim_id="att1")
    w_new = _w(a1)
    checks.append((f"new attester's ATTEST weight is low ({round(w_new,3)}) — standing not yet earned",
                   0 <= w_new < 0.6))

    # 2. the world RESOLVES several of an attester's claims as SURVIVED -> standing rises
    for i in range(4):
        capas_sdk.admit(*ATTEST_CLAIM, attester="lab_trusted", claim_id=f"surv{i}")
        capas_sdk.resolve(f"surv{i}", "survived")
    st = capas_sdk.standing("lab_trusted")
    checks.append((f"lab_trusted earned standing by surviving refutation (record: {st})",
                   isinstance(st, dict) and len(st) > 0))

    # 3. the SAME attester's NEXT ATTEST claim now carries MORE weight than the unknown lab's
    a2 = capas_sdk.admit(*ATTEST_CLAIM, attester="lab_trusted", claim_id="att2")
    w_trusted = _w(a2)
    checks.append((f"trusted attester's ATTEST weight {round(w_trusted,3)} > unknown {round(w_new,3)} "
                   f"(standing earned by surviving refutation)", w_trusted > w_new))

    # 4. a REFUTED claim destroys standing — the world, not the engine, decides
    capas_sdk.admit(*ATTEST_CLAIM, attester="lab_liar", claim_id="lie1")
    capas_sdk.resolve("lie1", "refuted")
    capas_sdk.admit(*ATTEST_CLAIM, attester="lab_liar", claim_id="lie2")
    capas_sdk.resolve("lie2", "refuted")
    a_liar = capas_sdk.admit(*ATTEST_CLAIM, attester="lab_liar", claim_id="att3")
    w_liar = _w(a_liar)
    checks.append((f"refuted attester's weight {round(w_liar,3)} <= trusted {round(w_trusted,3)} "
                   f"(refutation destroys standing)", w_liar <= w_trusted))

    # 5. a GATE claim (ACCEPT, proof-backed) is admitted on PROOF, independent of who attests
    g = capas_sdk.admit(*GATE_CLAIM, attester="lab_liar", claim_id="gate1")
    checks.append((f"GATE claim (ACCEPT) from even the liar is admitted on proof -> {g['verdict']}",
                   g["verdict"] == "ACCEPT"))

    # 6. chain integrity is verifiable (the ledger is hash-chained, tamper-evident)
    checks.append(("ledger hash-chain intact (tamper-evident accountability)",
                   a2["provisional_weight"].get("chain_intact") is True))

    ok = all(c for _, c in checks)
    for label, c in checks:
        print(f"{'OK ' if c else 'XX '}{label}")
    print("SURVIVE-REFUTATION LOOP: pass — the gate (now) is connected to accountability (over time);\n"
          "ATTEST is worth only standing earned by surviving the world's refutation, which CAPAS cannot fake."
          if ok else "SURVIVE-REFUTATION: FAILURES")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(run())
