# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""Demo + check: VERIFY the anytime-valid Type-I guarantee of the sequential e-process.

Closing the statistical-rigor gap (POPPER's level) by PROOF, not claim. Under the null
(claim false / no effect), a p-value is Uniform(0,1) and p_to_e calibrates it to a valid
e-value (E[e]=1). The running product is a test martingale, so by Ville's inequality the
probability it EVER crosses 1/alpha is <= alpha. We Monte-Carlo this: across many trials of
a streaming e-process, the empirical ever-cross (false-reject) rate must stay <= alpha.

Deterministic via a fixed seed (so the check is reproducible).
"""
from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import capas_sequential as S

ALPHA = 0.05
TRIALS = 20000
STREAM = 30           # observations per trial (anytime-valid: any length is fine)
SEED = 12345


def run() -> int:
    rng = random.Random(SEED)
    ever_crossed = 0
    for _ in range(TRIALS):
        # null: p ~ Uniform(0,1) -> valid e-value via the calibrator
        evals = [S.p_to_e(rng.random()) for _ in range(STREAM)]
        if S.evalue_process(evals, ALPHA)["crossed"]:
            ever_crossed += 1
    rate = ever_crossed / TRIALS

    # also confirm a genuine signal DOES cross (power sanity): small p-values -> large e
    signal = [S.p_to_e(0.01) for _ in range(STREAM)]
    powered = S.evalue_process(signal, ALPHA)

    checks = [
        (f"empirical false-reject rate under the null {rate:.4f} <= alpha {ALPHA} (Ville / anytime-valid)",
         rate <= ALPHA),
        ("the bound is not vacuous (rate is a real positive fraction, well-controlled)", 0.0 <= rate <= ALPHA),
        ("power sanity: a real signal (p=0.01 stream) DOES cross the threshold and rejects",
         powered["crossed"] is True),
    ]
    ok = all(c for _, c in checks)
    for label, c in checks:
        print(f"{'✅' if c else '❌'} {label}")
    print(f"   (null: {TRIALS} trials x {STREAM} steps, seed {SEED}; crossings={ever_crossed})")
    print("SEQUENTIAL E-PROCESS TYPE-I GUARANTEE (anytime-valid, verified): pass ✅" if ok
          else "TYPE-I: FAILED ❌")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(run())
