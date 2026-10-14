# SPDX-License-Identifier: Apache-2.0
"""interval_band_claim (DEBTS C-11, Atlas E4b P2, 2026-10-13): an estimate with an interval judged against a
PRE-REGISTERED band. Whole interval inside -> ACCEPT; whole interval outside -> REJECT; straddling -> REWRITE (the
interval is licensed, the band is not); band not pre-registered -> REWRITE; unreadable band / inconsistent interval
-> HOLD. Numbers are Atlas's real P2: theta 1.393, IC95 [1.259, 1.550]; bands RECUPERA (>= 0.5), PERSISTE
((-0.25, 0.25)), EMPEORA (< -0.25)."""
import capas

BASE = {"estimate": 1.3931894751605383, "ci_low": 1.2586366061033831, "ci_high": 1.5501540531430293,
        "ci_level": 0.95, "band_pre_registered": True, "method": "bootstrap", "resamples": 10000, "seed": 20261013}


def _d(ev, text="P2_persistencia: theta en banda pre-registrada"):
    return capas.decide_external_claim({"schema_version": "capas-claim-payload-v3",
                                        "claim": {"id": "p2", "type": "interval_band_claim", "text": text},
                                        "evidence": ev})


def test_whole_interval_inside_band_accepts():
    r = _d({**BASE, "band": {"low": 0.5}})
    assert r["verdict"] == "ACCEPT" and "inside the pre-registered band [0.5, +inf]" in r["reason"]


def test_whole_interval_outside_band_rejects():
    assert _d({**BASE, "band": {"low": -0.25, "high": 0.25}})["verdict"] == "REJECT"
    assert _d({**BASE, "band": {"high": -0.25}})["verdict"] == "REJECT"


def test_straddling_interval_rewrites_to_the_interval():
    r = _d({**BASE, "band": {"low": 1.4}})
    assert r["verdict"] == "REWRITE" and r["licensed_claim"].startswith("1.39319 with 95% interval [1.25864, 1.55015]")


def test_band_not_pre_registered_licenses_only_the_interval():
    r = _d({**BASE, "band": {"low": 0.5}, "band_pre_registered": False})
    assert r["verdict"] == "REWRITE" and "not declared pre-registered" in r["reason"]
    r = _d({k: v for k, v in {**BASE, "band": {"low": 0.5}}.items() if k != "band_pre_registered"})
    assert r["verdict"] == "HOLD"  # required field missing


def test_unreadable_or_empty_band_holds():
    assert _d({**BASE, "band": {}})["verdict"] == "HOLD"
    assert _d({**BASE, "band": {"low": 1.0, "high": 0.0}})["verdict"] == "HOLD"
    assert _d({**BASE, "band": {"low": "0.5"}})["verdict"] == "HOLD"  # a string bound is not a number


def test_inconsistent_interval_holds():
    assert _d({**BASE, "band": {"low": 0.5}, "ci_low": 1.6})["verdict"] == "HOLD"
    assert _d({**BASE, "band": {"low": 0.5}, "ci_level": 95})["verdict"] == "HOLD"


def test_registry_and_schema_carry_the_type():
    spec = capas.CLAIM_TYPE_REGISTRY["interval_band_claim"]
    assert set(spec["required"]) == {"estimate", "ci_low", "ci_high", "ci_level", "band", "band_pre_registered"}
    assert "interval_band_claim" in str(capas.external_claim_payload_schema())
    assert capas.evidence_field_type("band") == "object" and capas.evidence_field_type("ci_level") == "number"
