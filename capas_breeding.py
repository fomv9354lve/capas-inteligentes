# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""CAPAS breeding lock — reject the well-made lie by failure to INTEGRATE, not by inspection.

You cannot detect a coherent fabrication by looking at it (the GIGO floor). Biology never inspects
a gene for "truth"; reproductive isolation makes the incompatible thing unable to breed. Here the
"genome" is CAPAS's existing corpus of established invariants (capas_invariants: T2<=2T1, conservation,
probability bounds, stoichiometry, dimensions, ...). A claim must INTERBREED with that corpus: we run
its evidence through every applicable law. An internally-coherent fabrication that VIOLATES an
established law produces an inviable hybrid — caught WITHOUT detecting the lie.

DISPOSITION (the delta over a raw invariant audit): a collision at a LOAD-BEARING law is NOT rejected —
it is preserved as HOLD + a demand for the strongest ex-post falsifier (a genuine revolutionary result
also contradicts the corpus; auto-rejecting it would make the gate an ORTHODOXY PUMP that kills paradigm
shifts — the Jain syadvada / Talmud preserved-dissent organ). A collision at a derivation/consistency
law is a computational error -> REWRITE (re-level, fix). No collision -> VIABLE (the claim bred).

HONEST BOUND (do not strip): this is below the GIGO floor only RELATIVE TO A CLEAN CORPUS — a lie that
entered first becomes the standard the lock enforces. And a CRYPTIC fabrication engineered consistent
with every invariant BREEDS FINE and is admitted (VIABLE): the lock raises the lie's cost from
"consistent with yourself" to "consistent with the whole genome of accepted knowledge", it does NOT
break the floor. A corpus-DISCONNECTED claim (no law applies) evades the lock entirely (UNTESTED) —
low corpus-connection is the fabricator's escape, reported not hidden.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any

import capas_invariants

# Laws whose violation is a collision with an ESTABLISHED WORLD/ACCOUNTING LAW (physics, conservation,
# probability): a hit means "contradicts known science" -> revolutionary-or-fabrication -> HOLD + falsifier.
LOAD_BEARING = {
    "quantum", "probability", "sum", "stoichiometry", "charge_balance", "oxidation_states",
    "mole_mass", "dimensions", "bounds", "hardy_weinberg", "ohms_law", "accounting",
}
# Everything else in the registry is a DERIVATION/consistency check (GRIM, arithmetic, epi computations):
# a hit is a computational error -> REWRITE (re-level / fix), not a law collision.

_BOUND = ("OPTIMISTIC relative to a CLEAN corpus (orthodoxy-pump risk); a cryptic fabrication consistent "
          "with every invariant breeds fine (the GIGO floor stays); a corpus-disconnected claim evades the lock.")


def breeding_lock(evidence: dict[str, Any]) -> dict[str, Any]:
    """Interbreed a claim's evidence with CAPAS's invariant corpus. Returns a fail-closed disposition
    that PRESERVES load-bearing collisions as HOLD (never auto-rejects a paradigm-shift-or-fabrication)."""
    audit = capas_invariants.audit(evidence if isinstance(evidence, dict) else {})
    laws_checked = audit.get("laws_checked", [])
    collisions = list(audit.get("violations", []))

    if not audit.get("applicable"):
        verdict, demand_falsifier = "UNTESTED", False
        reason = "no corpus invariant applies — the claim never bred; the breeding lock is silent (evasion by low corpus-connection)"
    elif not collisions:
        verdict, demand_falsifier = "VIABLE", False
        reason = (f"viable hybrid: consistent with all {len(laws_checked)} applicable invariant(s). "
                  f"NOTE: a cryptic fabrication consistent with every invariant would also land here (the floor).")
    else:
        load_hits = [c for c in collisions if c in LOAD_BEARING]
        if load_hits:
            verdict, demand_falsifier = "HOLD", True
            reason = (f"INVIABLE hybrid — collision at load-bearing law(s) {load_hits}: contradicts established "
                      f"science, i.e. revolutionary-or-fabrication. PRESERVED as HOLD (not rejected); demand the "
                      f"strongest ex-post falsifier. [{audit.get('summary','')}]")
        else:
            verdict, demand_falsifier = "REWRITE", False
            reason = f"derivation collision at {collisions}: re-level / fix the computation. [{audit.get('summary','')}]"

    out = {
        "verdict": verdict,
        "demand_falsifier": demand_falsifier,
        "collisions": collisions,
        "corpus_connection": len(laws_checked),   # how many laws it had to breed with (density)
        "laws_checked": laws_checked,
        "reason": reason,
        "bound": _BOUND,
    }
    payload = json.dumps({"v": verdict, "c": sorted(collisions), "n": len(laws_checked)}, sort_keys=True)
    out["breeding_audit_hash"] = "sha256:" + hashlib.sha256(payload.encode()).hexdigest()[:24]
    return out


if __name__ == "__main__":
    # a true extension breeds; a T2>2T1 fabrication is an inviable hybrid held for a falsifier
    print("viable :", breeding_lock({"probabilities": [0.1, 0.9]})["verdict"])
    print("inviable:", breeding_lock({"probabilities": [1.7, 0.9]})["verdict"], "(prob bound collision)")
