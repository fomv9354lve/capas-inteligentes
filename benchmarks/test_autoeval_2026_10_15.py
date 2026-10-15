# SPDX-License-Identifier: Apache-2.0
"""Regressions from the bounded self-evaluation of 2026-10-15 (12-hypothesis matrix on b7685f1).

1. verify_audit_hash named the v1 recipe for a v2 decision; it must name the recipe actually used and the fields
   the hash covers, and say that a match is integrity of those fields, not authenticity.
2. An ACCEPT with text_licensed_as_written false said "The evidence licenses the claim as worded."
3. The hash coverage the matrix measured stays as measured: covered fields break verification when changed,
   operational fields outside the body do not (documented, not a promise of a signature)."""
from __future__ import annotations

import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import capas  # noqa: E402


def _accept(text="ae1 in this cohort."):
    return capas.decide_external_claim({"schema_version": capas.CAPAS_CLAIM_SCHEMA_VERSION,
                                        "claim": {"id": "ae1", "type": "statistical_confidence", "text": text},
                                        "evidence": {"p_value": 0.01, "alpha": 0.05, "effect_direction_confirmed": True}})


def test_verify_names_the_recipe_used():
    r = _accept()
    assert r["audit_hash_recipe"] == "v2"
    v = capas.verify_audit_hash(r)
    assert v["verified"] is True and v["recipe_version"] == "v2"
    assert v["recipe"] == capas.AUDIT_HASH_RECIPE_V2 and "evidence_sha256" in v["recipe"]
    assert {"evidence_sha256", "rules_fired", "rule_table_sha256", "engine_version", "notices"} <= set(v["covered_fields"])
    assert "authenticate" in v["scope"]


def test_accept_message_respects_text_licence():
    r = _accept()
    assert r["verdict"] == "ACCEPT" and r["text_licensed_as_written"] is False
    assert "as worded" not in r["resolution"]["message"]
    assert "licensed_claim" in r["resolution"]["message"]


def test_hash_coverage_is_as_documented():
    r = _accept()
    for field, value in (("verdict", "REJECT"), ("reason", "x"), ("evidence_sha256", "sha256:" + "0" * 64),
                         ("rules_fired", ["X"]), ("engine_version", "9.9.9"), ("notices", ["n"])):
        m = copy.deepcopy(r); m[field] = value
        assert capas.verify_audit_hash(m)["verified"] is False, field
    for field, value in (("licensed_claim", "Anything."), ("fine_tune_ready", True), ("resolution", {})):
        m = copy.deepcopy(r); m[field] = value
        assert capas.verify_audit_hash(m)["verified"] is True, field   # outside the hash body, by design
    m = copy.deepcopy(r); m["verdict"] = "REJECT"; m["audit_hash"] = capas.reproduce_audit_hash(m)
    assert capas.verify_audit_hash(m)["verified"] is True   # recomputable by anyone: integrity, not origin
