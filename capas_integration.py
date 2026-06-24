# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""CAPAS — integration measure: how irreducible is the verified whole (a Φ-proxy).

Answers "clean-layered or nodal?": for INTEGRATION, nodal wins. A clean layered
hierarchy cuts cheaply between layers (reducible); a recurrent NODAL core is hard
to partition (irreducible) — the IIT/claustrum requirement. True Φ is intractable,
so we use a tractable, principled proxy from spectral graph theory: the ALGEBRAIC
CONNECTIVITY (Fiedler value λ₂, the second-smallest eigenvalue of the braid's
correspondence-graph Laplacian).

  λ₂ = 0   -> reducible: the braid splits into parts with NO loss (a disjoint AND
              of independent checks — a verifier, not a unified thought).
  λ₂ > 0   -> irreducible/connected: every bipartition cuts reciprocity edges; the
              whole integrates. Higher λ₂ = harder to partition = more integrated.

Coupling (adding cross-layer reciprocity edges) RAISES λ₂ — deepening the core
toward the irreducible. The settled verdict's integration is λ₂; an "ignited
thought" should sit on a high-λ₂ (strongly coupled) core, not a chain of disjoint
checks.
"""
from __future__ import annotations

from typing import Any

import numpy as np


def integration(braid: Any) -> dict[str, Any]:
    """Spectral integration of a capas_braid.Braid over its correspondence edges."""
    nodes = list(braid.nodes.keys())
    n = len(nodes)
    if n == 0:
        return {"nodes": 0, "edges": 0, "algebraic_connectivity": 0.0, "irreducible": False,
                "interpretation": "empty"}
    idx = {c: i for i, c in enumerate(nodes)}
    A = np.zeros((n, n))
    for e in braid.edges:
        if e.get("type") == "corresponds" and e["a"] in idx and e["b"] in idx:
            i, j = idx[e["a"]], idx[e["b"]]
            A[i, j] = A[j, i] = 1.0
    L = np.diag(A.sum(axis=1)) - A
    eig = np.sort(np.linalg.eigvalsh(L))
    lam2 = float(eig[1]) if n > 1 else 0.0
    n_components = int(np.sum(eig < 1e-9))          # zero eigenvalues = connected components
    irreducible = lam2 > 1e-9
    return {
        "nodes": n, "edges": int(A.sum() / 2),
        "algebraic_connectivity": round(lam2, 4),    # the Φ-proxy
        "connected_components": n_components,
        "irreducible": irreducible,
        "interpretation": (
            "irreducible — every partition cuts reciprocity; the whole integrates (a unified thought)"
            if irreducible else
            f"reducible into {n_components} parts with no loss — a disjoint AND of checks, not one thought"),
        "note": "deepen by coupling (cross-layer reciprocity edges) -> raises algebraic connectivity "
                "toward the irreducible (the nodal core, not the clean layered chain).",
    }
