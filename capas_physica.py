# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""CAPAS-física — multi-tier admissibility audit.

Three tiers, ordered by nodality (coverage per law):
  1. NODAL SKELETON  (capas_nodal)      — cross-stratum laws that constrain claims in ANY domain.
  2. DOMAIN INVARIANTS (capas_invariants) — physics/quantum/chem/epi depth (T2<=2T1, conservation...).
  3. RMT CORPUS      (capas_rmt)         — one problem's theorems (inverse-Ginibre positivity overlaps).
Plus leaf laws ingested on-miss (fail-closed) via the probe engine.

Fail-closed: a collision in ANY tier flags. HONEST BOUND (never strip): the corpus is finite and the
domain is unbounded — a fabrication consistent with every INGESTED law but violating an un-ingested one
passes (the floor, at corpus level). Coverage is wide from few nodal laws; it is never complete. And the
verdict is only as trustworthy as the extraction that fed it (the numbers are declared, not gated).
"""
from __future__ import annotations
from typing import Any

def audit(evidence: dict[str, Any]) -> dict[str, Any]:
    import capas_nodal, capas_invariants, capas_rmt
    nodal = capas_nodal.check(evidence)
    domain = capas_invariants.audit(evidence)
    rmt = capas_rmt.audit_rmt(evidence)

    flags = []
    if nodal["verdict"] == "KILLED":       flags += [("nodal", f) for f in nodal["killed_by"]]
    if domain.get("verdict") == "FLAG":    flags += [("domain", f) for f in domain["violations"]]
    if rmt["verdict"] == "FLAG":           flags += [("rmt", f) for f in rmt["flags"]]

    applied = nodal["n_nodal"] + len(domain.get("laws_checked", [])) + len(rmt["laws_checked"])
    verdict = "FLAG" if flags else ("PASS" if applied else "UNTESTED")
    return {
        "verdict": verdict, "flags": flags,
        "laws_applied": applied,
        "tiers": {"nodal": nodal["laws_fired"], "domain": domain.get("laws_checked", []), "rmt": rmt["laws_checked"]},
        "strata_reached": nodal["strata_reached"],
        "bound": "corpus finite vs domain unbounded — an un-ingested law is where a fabrication hides; "
                 "coverage wide-from-few, never complete; verdict only as good as the (un-gated) extraction.",
    }
