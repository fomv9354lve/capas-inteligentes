"""CAPAS — learned value function (AlphaProof-style guidance, determinism-safe).

The macrophage move for the SOTA-ahead 'learned value function': absorb it, but
in service of the deterministic core. This predicts a claim's admissibility from
CHEAP features WITHOUT running the (expensive) re-derivation, so the spiral can
PRIORITIZE which conjecture to expand next — but the deterministic grader
(capas_admissibility) always RE-GRADES before anything is grounded. The learned
function guides search; it never decides the verdict.

Transparent by construction: closed-form ridge regression over interpretable
features (presence of each re-derivable domain, amount of numeric content,
provenance). Self-supervised — fit on (payload -> admissibility) pairs the engine
generates about itself. No black box, no training loop, no LLM in the loop.
"""
from __future__ import annotations

from typing import Any

import numpy as np

import capas_admissibility

# Re-derivable / provenance evidence keys -> cheap presence features.
_DOMAIN_KEYS = ("raw_data", "computation", "derivation", "integration", "registry",
                "zk_proof", "quantum_circuit", "crypto", "accounting", "dimensions",
                "xbrl", "physical", "stoichiometry", "reproduction")
_PROV_KEYS = ("provenance", "ro_crate", "registry_id", "signed_attestation", "attestation")


def _count_numbers(obj: Any) -> int:
    if isinstance(obj, dict):
        return sum(_count_numbers(v) for v in obj.values())
    if isinstance(obj, list):
        return sum(_count_numbers(v) for v in obj)
    return 1 if isinstance(obj, (int, float)) and not isinstance(obj, bool) else 0


def features(payload: dict[str, Any]) -> np.ndarray:
    ev = payload.get("evidence", {}) or {}
    f = [1.0]                                   # bias
    f += [1.0 if k in ev else 0.0 for k in _DOMAIN_KEYS]
    f.append(1.0 if any(k in ev for k in _PROV_KEYS) else 0.0)
    f.append(min(_count_numbers(ev), 20) / 20.0)   # amount of groundable numeric content
    f.append(1.0 if (ev.get("raw_data") or ev.get("computation") or ev.get("xbrl")) else 0.0)  # strong-ground flag
    return np.array(f, dtype=float)


class ValueModel:
    """Cheap, transparent surrogate for the deterministic admissibility score."""

    def __init__(self) -> None:
        self.w: np.ndarray | None = None

    def fit(self, payloads: list[dict[str, Any]], lam: float = 1.0) -> "ValueModel":
        X = np.array([features(p) for p in payloads])
        y = np.array([capas_admissibility.admissibility(p)["score"] for p in payloads])
        n_features = X.shape[1]
        self.w = np.linalg.solve(X.T @ X + lam * np.eye(n_features), X.T @ y)
        return self

    def predict(self, payload: dict[str, Any]) -> float:
        if self.w is None:
            raise RuntimeError("ValueModel not fitted")
        return float(np.clip(features(payload) @ self.w, 0.0, 1.0))

    def prioritize(self, payloads: list[dict[str, Any]]) -> list[tuple[float, dict[str, Any]]]:
        """Rank conjectures by predicted value (search guidance). The deterministic
        grader still re-grades each before any is grounded."""
        return sorted(((self.predict(p), p) for p in payloads), key=lambda t: -t[0])
