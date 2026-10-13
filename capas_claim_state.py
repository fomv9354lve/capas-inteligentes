# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""CAPAS verdict -> ceiling in the corpus' claim-state vocabulary (GOVERNANCE §2).

Un veredicto de CAPAS dice si la REDACCION esta licenciada por la evidencia declarada. No dice
que el claim sea verdadero. Por eso este modulo no promueve: devuelve el TECHO que el claim
puede llevar en el registro (`CURRENT_TRUTH.md`) y lo que aun falta para subir.

Reglas que lo gobiernan:
  §2 regla madre: numerica nunca implica prueba -> un ACCEPT sobre evidencia numerica es
     `empirical`, nunca `proved`.
  §6 constructor != verificador: `proved` exige una pierna cross-family. CAPAS es un
     verificador estructural, no esa pierna; nunca concede `proved` por si solo.
  Un REJECT por invariante de dominio es `refuted` (contraejemplo). Un REJECT estructural
  (evidencia que no re-deriva) no refuta nada: el claim queda `unknown`.
"""
from __future__ import annotations

from typing import Any

STATES = ("proved", "closed-local", "empirical", "reduced", "open", "refuted", "stale", "unknown")
STALE_AFTER_DAYS = 365


def claim_state_ceiling(decision: dict[str, Any], *, cross_family_certified: bool = False,
                        age_days: int | None = None) -> dict[str, Any]:
    v = str(decision.get("verdict", "")).upper()
    reason = str(decision.get("reason", "") or "")
    ctype = str(decision.get("claim_type", "") or "")
    licensed = str(decision.get("licensed_claim", "") or "")
    required: list[str] = []

    if age_days is not None and age_days > STALE_AFTER_DAYS:
        return {"ceiling": "stale", "why": f"last verified {age_days} days ago (> {STALE_AFTER_DAYS})",
                "required_for_proved": ["re-verify, then apply the verdict rules"]}

    if v == "REJECT":
        if "invariant violation" in reason.lower():
            ceiling, why = "refuted", "a domain invariant is violated: a counterexample, by §6 it degrades the claim at once"
        else:
            ceiling, why = "unknown", "the declared evidence does not license the claim; nothing was refuted"
    elif v == "HOLD":
        ceiling, why = "unknown", "CAPAS could not judge: evidence missing or a law could not be applied"
    elif v == "REWRITE":
        if "leading-order" in licensed.lower() or "leading order" in licensed.lower() or "uniform bound" in reason.lower():
            ceiling, why = "closed-local", "the licensed wording is the bounded/leading-order statement; the universal claim is not licensed"
        else:
            ceiling, why = "reduced", "only the rewritten, weaker claim is licensed"
    elif v == "ACCEPT":
        if ctype == "proof_admissibility":
            if cross_family_certified:
                ceiling, why = "proved", "uniform bound proven AND certified by a cross-family leg (§6)"
            else:
                ceiling, why = "closed-local", "proof structure licensed by CAPAS; `proved` needs a §6 cross-family certification"
                required.append("§6: an independent cross-family route (other model / Lean / symbolic) reproduces the proof")
        else:
            ceiling, why = "empirical", "evidence is numeric/structural: §2 — a harness gives empirical, never derived"
            required.append("a symbolic derivation or formal proof, then §6 cross-family certification")
    else:
        ceiling, why = "unknown", f"unrecognized verdict {v!r}"

    return {"ceiling": ceiling, "why": why, "required_for_proved": required, "verdict": v}
