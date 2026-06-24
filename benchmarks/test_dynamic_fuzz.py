# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""Dynamic analysis — property-based fuzzing of the gate (OpenSSF dynamic_analysis criterion).

Generalizes benchmarks/verify_robustness.py (20 hand-built hostile payloads) into a Hypothesis
property test: for ANY generated payload, the gate must (1) never raise an unhandled exception
(fail-closed, not fail-crash) and (2) return one of the four legal verdicts. A self-consistent
fabrication may ACCEPT (the GIGO ceiling), but garbage must never crash the process or slip an
ACCEPT past the schema. Run:  python -m pytest benchmarks/test_dynamic_fuzz.py   (needs `hypothesis`).
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import capas  # noqa: E402
from hypothesis import given, settings, strategies as st  # noqa: E402

VERDICTS = {"ACCEPT", "REWRITE", "REJECT", "HOLD"}

# Arbitrary JSON-ish values, including the shapes a hostile caller would send.
_json = st.recursive(
    st.none() | st.booleans() | st.integers() | st.floats(allow_nan=True, allow_infinity=True) | st.text(),
    lambda children: st.lists(children, max_size=4) | st.dictionaries(st.text(max_size=12), children, max_size=4),
    max_leaves=12,
)

_claim_types = st.sampled_from(sorted(capas.CLAIM_TYPE_REGISTRY) + ["", "not_a_type", "exact_model_solution"])


def _assert_safe(result):
    # The gate must return a dict carrying a legal verdict — never raise, never a non-verdict.
    assert isinstance(result, dict), f"non-dict result: {type(result)}"
    assert result.get("verdict") in VERDICTS, f"illegal verdict: {result.get('verdict')!r}"


@settings(max_examples=300, deadline=None)
@given(payload=_json)
def test_fuzz_arbitrary_payload(payload):
    """Any arbitrary value as the payload must be handled fail-closed (HOLD at worst), never crash."""
    _assert_safe(capas.decide_external_claim(payload))


@settings(max_examples=300, deadline=None)
@given(ctype=_claim_types, evidence=st.dictionaries(st.text(max_size=20), _json, max_size=6), text=st.text(max_size=200))
def test_fuzz_structured_payload(ctype, evidence, text):
    """Well-shaped-but-adversarial payloads: random claim type + random evidence fields + random text."""
    payload = {"schema_version": "capas-claim-payload-v3",
               "claim": {"id": "fuzz", "type": ctype, "text": text or "x"},
               "evidence": evidence}
    _assert_safe(capas.decide_external_claim(payload))


if __name__ == "__main__":
    # Allow a plain `python benchmarks/test_dynamic_fuzz.py` smoke run without pytest.
    test_fuzz_arbitrary_payload()
    test_fuzz_structured_payload()
    print("dynamic fuzz: pass — gate never crashed and every verdict was legal across generated inputs.")
