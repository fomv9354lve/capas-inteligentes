# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""CAPAS — persisted survive-refutation ledger (the third pole made material).

capas_ledger is PURE (log in -> log out). It had no state, so the GATE (a verdict now) and the
LEDGER (accountability over time) were never connected — the engine's biggest internal
disconnection. This wires them: a gated decision is ATTESTED to a persisted, hash-chained log
bound to an attester identity; the world later RESOLVES it survived|refuted; the attester's
STANDING is earned by surviving refutation, and weights every future ATTEST claim they make.

Stdlib only; file-backed under CAPAS_DATA_DIR (default ./_ledger). The verdict stops being a
one-shot and becomes a time-extended, refutable record — which is the actual moat
(trust-as-certification-standard), not another gate.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import capas_ledger


def _path() -> Path:
    # Default to a USER data dir (~/.capas), never the package install location (site-packages may
    # be read-only/shared). Override with CAPAS_DATA_DIR. Falls back to a temp dir if home is unwritable.
    default = Path.home() / ".capas" / "ledger"
    d = Path(os.environ.get("CAPAS_DATA_DIR", str(default)))
    try:
        d.mkdir(parents=True, exist_ok=True)
    except OSError:
        import tempfile
        d = Path(tempfile.gettempdir()) / "capas_ledger"
        d.mkdir(parents=True, exist_ok=True)
    return d / "ledger.json"


def load() -> list[dict[str, Any]]:
    f = _path()
    return json.loads(f.read_text()) if f.is_file() else []


def save(log: list[dict[str, Any]]) -> None:
    _path().write_text(json.dumps(log, indent=2, default=str))


def attest(certificate: dict[str, Any], attester: str, at: str | None = None) -> dict[str, Any]:
    """Gate a decision into the persisted ledger bound to an attester. Returns the provisional
    admissibility weight (GATE = full proof weight; ATTEST = only the attester's earned standing)."""
    log = capas_ledger.attest(load(), certificate, attester, at=at)
    save(log)
    return capas_ledger.admit(log, certificate, attester,
                              scope="GATE" if certificate.get("verdict") == "ACCEPT" else "ATTEST")


def resolve(claim_id: str, outcome: str) -> dict[str, Any]:
    """The world's measurement: mark an open claim survived|refuted. This is how reputation is
    earned — the only mechanism CAPAS cannot fake (the world, not the engine, decides)."""
    save(capas_ledger.resolve(load(), claim_id, outcome))
    return {"claim_id": claim_id, "outcome": outcome, "recorded": True}


def standing(attester: str) -> dict[str, Any]:
    """An attester's reputation, earned only by surviving refutation over time."""
    return capas_ledger.standing(load(), attester)
