# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""Demo + check: the Decision Registry (roadmap #5, the honest buildable-now slice).

Deterministic. Real signed certificates (capas_rcc.rcc) are appended to an append-only,
hash-chained, Merkle-rooted log. Asserts: the chain verifies; a claim's history is
recoverable; re-presenting a certificate proves it authentic; and ANY tamper — altering a
logged entry, reordering, or altering a re-presented certificate body — is CAUGHT.
"""
from __future__ import annotations

import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import capas_rcc as RCC
import capas_registry as REG

SV = "capas-claim-payload-v3"
FIN = {"reported_value": 1.0, "reference_value": 1.0, "tolerance": 1.0, "metric_period_match": True,
       "accounting": {"identity": "balance_sheet", "assets": 1000, "liabilities": 600, "equity": 400}}


def _cert(cid, evidence=None):
    pl = {"schema_version": SV, "claim": {"id": cid, "type": "financial_metric_claim", "text": "x"},
          "evidence": evidence if evidence is not None else FIN}
    return RCC.rcc(pl)


def run() -> int:
    checks = []

    # append three real signed decisions (claim A decided twice -> a lifecycle)
    log = []
    log = REG.append(log, _cert("claim_A"), at="2026-06-21T10:00:00Z")
    log = REG.append(log, _cert("claim_B", evidence={}), at="2026-06-21T10:05:00Z")
    cA2 = _cert("claim_A")
    log = REG.append(log, cA2, at="2026-06-21T11:00:00Z")

    v = REG.verify_chain(log)
    checks.append(("append-only chain verifies after 3 signed decisions", v["intact"] and v["entries"] == 3))

    root1 = REG.merkle_root(log)
    checks.append(("registry has a single Merkle fingerprint", root1.startswith("sha256:")))

    hist = REG.history(log, "claim_A")
    checks.append(("claim history recoverable (claim_A decided twice, in order)",
                   len(hist) == 2 and hist[0]["seq"] < hist[1]["seq"]))

    # re-present the authentic certificate for entry 2 -> proven authentic
    auth = REG.verify_entry(log[2], cA2)
    checks.append(("re-presented authentic certificate -> AUTHENTIC (body digest matches)",
                   auth["body_matches_log"] and not auth["tampered"]))

    # TAMPER 1: alter a logged entry's body_digest -> chain breaks
    tampered_log = copy.deepcopy(log)
    tampered_log[1]["body_digest"] = "sha256:deadbeef"
    vt = REG.verify_chain(tampered_log)
    checks.append(("tampering with a logged entry is CAUGHT (chain breaks at the entry)",
                   vt["intact"] is False and vt["broken_at"] == 1))

    # TAMPER 2: reorder entries -> chain breaks
    reordered = [log[1], log[0], log[2]]
    vr = REG.verify_chain(reordered)
    checks.append(("reordering entries is CAUGHT (append-only proof)", vr["intact"] is False))

    # TAMPER 3: alter a re-presented certificate body -> digest mismatch
    forged = copy.deepcopy(cA2)
    forged["verdict"] = "ACCEPT" if forged.get("verdict") != "ACCEPT" else "REJECT"
    forged_check = REG.verify_entry(log[2], forged)
    checks.append(("altered re-presented certificate -> TAMPERED (digest mismatch)",
                   forged_check["tampered"] is True))

    ok = all(c for _, c in checks)
    for label, c in checks:
        print(f"{'✅' if c else '❌'} {label}")
    print("DECISION REGISTRY (append-only, hash-chained, tamper-evident): pass ✅" if ok
          else "REGISTRY: FAILURES ❌")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(run())
