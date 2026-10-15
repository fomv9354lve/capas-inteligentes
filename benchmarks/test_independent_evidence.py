# SPDX-License-Identifier: Apache-2.0
"""Experiment v2 (2026-10-15): the AI's errors and CAPAS's misses were the SAME claims, because CAPAS checked the
evidence the AI had assembled. Three fixes make the check independent of that assembly:
1. coverage per source: two entities' rows merged hid one entity's missing month (R5#17, R5#28 shapes);
2. compound claims: each assertion needs its own check ("X grew 22.5%, and both entities grew", R5#7 shape);
3. original materials: the engine reads the source file itself by {path, sha256}."""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import capas  # noqa: E402

V = capas.CAPAS_CLAIM_SCHEMA_VERSION
MX = ("date,account,customer,amount\n2025-04-10,revenue,a,100\n2025-05-10,revenue,b,100\n2025-06-10,revenue,c,100\n"
      "2025-07-10,revenue,a,120\n2025-08-10,revenue,b,120\n2025-09-10,revenue,c,120\n")
CO = ("date,account,customer,amount\n2025-04-10,revenue,x,50\n2025-05-10,revenue,y,50\n2025-06-10,revenue,z,50\n"
      "2025-07-10,revenue,x,60\n2025-09-10,revenue,z,60\n")          # no August rows


def fin(text, reported, ledger, tol=0.5):
    return {"schema_version": V, "claim": {"id": "f", "type": "financial_metric_claim", "text": text},
            "evidence": {"reported_value": reported, "tolerance": tol, "ledger": ledger}}


# ---------------------------------------------------------------- 1. coverage per source
def test_missing_month_in_one_source_holds():
    r = capas.decide_external_claim(fin("Group revenue for Q3 2025 was 480.", 480,
        {"sources": [{"name": "MX", "rows_csv": MX}, {"name": "CO", "rows_csv": CO}], "metric": "sum(revenue)", "period": "2025-Q3"}))
    assert r["verdict"] == "HOLD" and r["rederivation"]["missing_months"] == ["CO:2025-08"]


def test_entity_column_in_a_merged_csv_is_a_source():
    merged = "date,account,entity,amount\n" + "".join(
        f"{l.split(',')[0]},{l.split(',')[1]},{e},{l.split(',')[3]}\n"
        for e, t in (("MX", MX), ("CO", CO)) for l in t.strip().splitlines()[1:])
    r = capas.decide_external_claim(fin("Group revenue for Q3 2025 was 480.", 480,
        {"rows_csv": merged, "metric": "sum(revenue)", "period": "2025-Q3"}))
    assert r["verdict"] == "HOLD"


def test_one_complete_source_is_still_accepted():
    r = capas.decide_external_claim(fin("Mexico revenue for Q3 2025 was 360.", 360,
        {"sources": [{"name": "MX", "rows_csv": MX}, {"name": "CO", "rows_csv": CO}], "metric": "sum(revenue, source=MX)",
         "period": "2025-Q3"}))
    assert r["verdict"] == "ACCEPT", r["reason"]


# ---------------------------------------------------------------- 2. compound claims
def test_compound_claim_without_a_check_for_the_second_assertion_rewrites():
    r = capas.decide_external_claim(fin("Mexico grew revenue 20.0% in Q3 2025, and both entities grew revenue.", 0.2,
        {"sources": [{"name": "MX", "rows_csv": MX}], "metric": "sum(revenue, source=MX) / sum(revenue, prev, source=MX) - 1",
         "period": "2025-Q3"}, tol=0.0005))
    assert r["verdict"] == "REWRITE" and "more assertions than the evidence checks" in r["reason"]


def test_compound_claim_with_a_failing_check_rejects():
    co_full = CO + "2025-08-10,revenue,y,30\n"            # Colombia complete but shrinking: 150 -> 150? make it fall
    co_full = co_full.replace("2025-07-10,revenue,x,60", "2025-07-10,revenue,x,20").replace("2025-09-10,revenue,z,60", "2025-09-10,revenue,z,20")
    r = capas.decide_external_claim(fin("Mexico grew revenue 20.0% in Q3 2025, and Colombia grew revenue too.", 0.2,
        {"sources": [{"name": "MX", "rows_csv": MX}, {"name": "CO", "rows_csv": co_full}],
         "metric": "sum(revenue, source=MX) / sum(revenue, prev, source=MX) - 1", "period": "2025-Q3",
         "checks": [{"metric": "sum(revenue, source=CO) - sum(revenue, prev, source=CO)", "op": ">", "value": 0}]}, tol=0.0005))
    assert r["verdict"] == "REJECT" and r["rederivation"]["checks"][0]["passed"] is False


def test_compound_claim_with_passing_checks_accepts():
    co_full = CO + "2025-08-10,revenue,y,60\n"
    r = capas.decide_external_claim(fin("Mexico grew revenue 20.0% in Q3 2025, and Colombia grew revenue too.", 0.2,
        {"sources": [{"name": "MX", "rows_csv": MX}, {"name": "CO", "rows_csv": co_full}],
         "metric": "sum(revenue, source=MX) / sum(revenue, prev, source=MX) - 1", "period": "2025-Q3",
         "checks": [{"metric": "sum(revenue, source=CO) - sum(revenue, prev, source=CO)", "op": ">", "value": 0}]}, tol=0.0005))
    assert r["verdict"] == "ACCEPT", r["reason"]


def test_comparison_claim_as_a_check():
    r = capas.decide_external_claim(fin("Q3 2025 revenue was 360 and came in above Q2.", 360,
        {"sources": [{"name": "MX", "rows_csv": MX}], "metric": "sum(revenue)", "period": "2025-Q3",
         "checks": [{"metric": "sum(revenue) - sum(revenue, prev)", "op": ">", "value": 0}]}))
    assert r["verdict"] == "ACCEPT", r["reason"]


@pytest.mark.parametrize("text", ["Group revenue for Q3 2025 was 360.", "Revenue and COGS were 360 and 0 in Q3 2025."])
def test_single_assertions_are_not_compound(text):
    r = capas.decide_external_claim(fin(text, 360, {"sources": [{"name": "MX", "rows_csv": MX}], "metric": "sum(revenue)",
                                                    "period": "2025-Q3"}))
    assert r["verdict"] == "ACCEPT", r["reason"]


# ---------------------------------------------------------------- 3. original materials by reference
@pytest.fixture
def root(tmp_path, monkeypatch):
    monkeypatch.setenv("CAPAS_SOURCE_ROOT", str(tmp_path))
    (tmp_path / "mx.csv").write_text(MX, encoding="utf-8")
    (tmp_path / "snippet.py").write_text("print(1+2)\n", encoding="utf-8")
    return tmp_path


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def test_ledger_read_from_the_original_file(root):
    r = capas.decide_external_claim(fin("Mexico revenue for Q3 2025 was 360.", 360,
        {"sources": [{"name": "MX", "path": "mx.csv", "sha256": sha(root / "mx.csv")}], "metric": "sum(revenue)", "period": "2025-Q3"}))
    assert r["verdict"] == "ACCEPT", r["reason"]


def test_tampered_or_missing_original_holds(root):
    r = capas.decide_external_claim(fin("Mexico revenue for Q3 2025 was 360.", 360,
        {"sources": [{"name": "MX", "path": "mx.csv", "sha256": "0" * 64}], "metric": "sum(revenue)", "period": "2025-Q3"}))
    assert r["verdict"] == "HOLD" and "original source file" in r["reason"]
    r2 = capas.decide_external_claim(fin("Mexico revenue for Q3 2025 was 360.", 360,
        {"sources": [{"name": "MX", "path": "../etc/passwd", "sha256": "0" * 64}], "metric": "sum(revenue)", "period": "2025-Q3"}))
    assert r2["verdict"] == "HOLD"


def test_no_source_root_holds(monkeypatch):
    monkeypatch.delenv("CAPAS_SOURCE_ROOT", raising=False)
    r = capas.decide_external_claim(fin("Mexico revenue for Q3 2025 was 360.", 360,
        {"sources": [{"name": "MX", "path": "mx.csv", "sha256": "0" * 64}], "metric": "sum(revenue)", "period": "2025-Q3"}))
    assert r["verdict"] == "HOLD"


def test_code_read_from_the_original_file_overrides_the_inline_copy(root):
    py = "%d.%d" % sys.version_info[:2]
    p = {"schema_version": V, "claim": {"id": "c", "type": "programming_language_behavior_claim", "text": f"On Python {py} it prints 3."},
         "evidence": {"language": "python", "language_version": py, "claim_api": "print",
                      "code_snippet": "print(3)\n",            # the AI's copy: also prints 3, but is not the file
                      "code_ref": {"path": "snippet.py", "sha256": sha(root / "snippet.py")},
                      "expected_output": "3", "observed_output": "3", "execution_observed": True, "runtime_environment_declared": True}}
    r = capas.decide_external_claim(p, rederive=True)
    assert r["verdict"] == "ACCEPT" and r["rederivation"]["observed"] == "3"
    p["evidence"]["code_ref"]["sha256"] = "1" * 64
    assert capas.decide_external_claim(p, rederive=True)["verdict"] == "HOLD"
