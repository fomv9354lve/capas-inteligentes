# SPDX-License-Identifier: Apache-2.0
"""Engine changes after the AI vs AI+CAPAS experiment (2026-10-15):
1. re-derivation: the engine re-runs a Python snippet (opt-in only) and recomputes ledger metrics from the rows;
2. scope: a text that generalises beyond one run or one period is REWRITE; a text naming another Python version
   than the evidence ran on is HOLD;
3. one-way override: an AI may be stricter than the verdict, never looser;
plus the two false blocks the experiment found (claim text with "<a>", indexing "grid[0]" read as a citation)."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import capas  # noqa: E402
import capas_rederive as rd  # noqa: E402

V = capas.CAPAS_CLAIM_SCHEMA_VERSION
PY = "%d.%d" % sys.version_info[:2]


def prog(text, snippet, expected, observed=None, version=PY, **extra):
    ev = {"language": "python", "language_version": version, "claim_api": "x", "code_snippet": snippet,
          "expected_output": expected, "execution_observed": True, "runtime_environment_declared": True, **extra}
    ev["observed_output"] = expected if observed is None else observed
    return {"schema_version": V, "claim": {"id": "t", "type": "programming_language_behavior_claim", "text": text}, "evidence": ev}


def ledger(text, reported, metric, period, rows, tol=0.005):
    return {"schema_version": V, "claim": {"id": "l", "type": "financial_metric_claim", "text": text},
            "evidence": {"reported_value": reported, "tolerance": tol,
                         "ledger": {"rows_csv": rows, "metric": metric, "period": period}}}


ROWS_Q1 = ("date,account,customer,amount\n2026-01-05,revenue,A,100\n2026-01-20,cogs,,40\n"
           "2026-02-03,revenue,B,200\n2026-02-10,cogs,,90\n2026-03-07,revenue,A,300\n2026-03-30,cogs,,110\n")


# ---------------------------------------------------------------- 1. re-derivation
def test_hosted_default_never_executes(monkeypatch):
    monkeypatch.delenv(rd.EXEC_ENV, raising=False)
    r = capas.decide_external_claim(prog(f"On Python {PY} this prints 3.", "print(1+2)\n", "3"))
    assert "rederivation" not in r


def test_rerun_catches_a_wrong_transcription():
    # the AI transcribed the expected output as observed; the snippet really prints 4
    r = capas.decide_external_claim(prog(f"On Python {PY} this prints 3.", "print(2+2)\n", "3"), rederive=True)
    assert r["verdict"] == "REJECT"
    assert r["rederivation"]["observed"] == "4" and r["rederivation"]["declared_observed_differs"] is True
    assert any("differs from the engine's own run" in n for n in r["notices"])


def test_rerun_confirms_and_is_hashed():
    r = capas.decide_external_claim(prog(f"On Python {PY} this prints 3.", "print(1+2)\n", "3"), rederive=True)
    assert r["verdict"] == "ACCEPT" and r["rederivation"]["ran"] is True
    assert capas.verify_audit_hash(r)["verified"] is True
    assert any(n.startswith("rederived:") for n in r["notices"])   # notices are inside the v2 hash body


def test_rerun_exception_line_is_the_observed_output():
    r = capas.decide_external_claim(prog(f"On Python {PY} it raises.", "d={}\nprint(d.get('b'))\nprint(d['b'])\n",
                                         "None\nKeyError: 'b'"), rederive=True)
    assert r["verdict"] == "ACCEPT", r["reason"]


def test_rerun_on_another_version_holds():
    r = capas.decide_external_claim(prog("On Python 2.7 this prints 3.", "print(1+2)\n", "3", version="2.7"), rederive=True)
    assert r["verdict"] == "HOLD" and "not the declared version" in r["reason"]


def test_rerun_timeout_holds(monkeypatch):
    monkeypatch.setattr(rd, "TIMEOUT_S", 1)
    r = capas.decide_external_claim(prog(f"On Python {PY} it prints 1.", "while True: pass\n", "1"), rederive=True)
    assert r["verdict"] == "HOLD" and "could not re-run" in r["reason"]


def test_ledger_recomputes_and_accepts():
    r = capas.decide_external_claim(ledger("Gross margin for 2026-Q1 was 60.0%.", 0.6,
                                           "(sum(revenue) - sum(cogs)) / sum(revenue)", "2026-Q1", ROWS_Q1))
    assert r["verdict"] == "ACCEPT", r["reason"]
    assert abs(r["rederivation"]["value"] - 0.6) < 1e-12


def test_ledger_wrong_number_rejects_even_if_reference_was_copied():
    p = ledger("Gross margin for 2026-Q1 was 70.0%.", 0.7, "(sum(revenue) - sum(cogs)) / sum(revenue)", "2026-Q1", ROWS_Q1)
    p["evidence"]["reference_value"] = 0.7          # the AI copied the reported value as the reference
    r = capas.decide_external_claim(p)
    assert r["verdict"] == "REJECT" and r["rederivation"]["declared_reference_differs"] is True


def test_ledger_missing_month_holds():
    rows = "\n".join(l for l in ROWS_Q1.splitlines() if not l.startswith("2026-02"))
    r = capas.decide_external_claim(ledger("Revenue for 2026-Q1 was 400.", 400, "sum(revenue)", "2026-Q1", rows, tol=0.5))
    assert r["verdict"] == "HOLD" and r["rederivation"]["missing_months"] == ["2026-02"]


def test_ledger_growth_and_distinct():
    rows = ROWS_Q1 + "2025-10-01,revenue,A,300\n2025-11-01,revenue,B,150\n2025-12-01,revenue,C,50\n"
    assert rd.ledger_metric(rows, "sum(revenue) / sum(revenue, prev) - 1", "2026-Q1")["value"] == pytest.approx(0.2)
    assert rd.ledger_metric(rows, "sum(revenue) / distinct(customer, revenue)", "2026-Q1")["value"] == pytest.approx(300)


def test_ledger_spec_cannot_execute_code():
    for bad in ("__import__('os').system('true')", "sum(revenue).__class__", "open('x')"):
        r = capas.decide_external_claim(ledger("Revenue was 600.", 600, bad, "2026-Q1", ROWS_Q1, tol=0.5))
        # the spec is parsed, never executed: HOLD (the derived fields stay missing) and the notice names the error
        assert r["verdict"] == "HOLD" and any("ledger spec error" in n for n in r["notices"]), bad


# ---------------------------------------------------------------- 2. scope and version
@pytest.mark.parametrize("text", [
    "sorted() keeps equal keys in order in every Python 3 release.",
    "This snippet always prints 3.",
    "dict order is guaranteed regardless of the interpreter.",
    "sorted() can order any Python list; this run prints 3.",
    "Any Python iterable yields nothing when iterated twice.",
    "int() accepts any string that contains digits.",
    "It works for all strings in Python.",
])
def test_generalisation_is_rewrite(text):
    r = capas.decide_external_claim(prog(text, "print(1+2)\n", "3"))
    assert r["verdict"] == "REWRITE" and "generalises beyond the evidence" in r["reason"]


def test_generalisation_over_periods_is_rewrite():
    r = capas.decide_external_claim(ledger("Gross margin was 60.0% in every quarter.", 0.6,
                                           "(sum(revenue) - sum(cogs)) / sum(revenue)", "2026-Q1", ROWS_Q1))
    assert r["verdict"] == "REWRITE"


@pytest.mark.parametrize("text", ["This snippet prints all three items: 3.", "It prints every element once: 3.",
                                  "The loop visits each item in the list and prints 3.", "It joins all strings in the list: 3.",
                                  "The snippet prints the values of all keys in d: 3.", "all numbers in data are summed to 3."])
def test_description_of_one_run_is_not_generalisation(text):
    assert capas.decide_external_claim(prog(text, "print(1+2)\n", "3"))["verdict"] == "ACCEPT"


def test_text_names_another_version_than_the_evidence():
    r = capas.decide_external_claim(prog("On Python 3.14 this prints 5000.", "print(5000)\n", "5000", version="3.9.6"))
    assert r["verdict"] == "HOLD" and "another Python version" in r["reason"]


# ---------------------------------------------------------------- false blocks found by the experiment
def test_tag_like_text_is_refused_with_a_path_forward():
    # kept refused (frozen §6 refutation); the message now says where markup goes (experiment C020)
    r = capas.decide_external_claim(prog("findall returns ['<a>', '<b>'] here.", "print(1)\n", "1"))
    assert r["verdict"] == "HOLD" and any("code_snippet" in e for e in r["schema_errors"])
    assert capas.decide_external_claim(prog("The error is < 0.01 here.", "print(1)\n", "1"))["verdict"] == "ACCEPT"


def test_indexing_is_not_a_citation():
    r = capas.decide_external_claim(prog("Setting grid[0][0] = 9 also changes grid[1][0].", "print(1)\n", "1"))
    assert r["verdict"] == "ACCEPT", r["reason"]
    r2 = capas.decide_external_claim(prog("As shown in [3], this prints 1.", "print(1)\n", "1"))
    assert r2["verdict"] == "HOLD"   # a real numeric citation still needs its hypotheses checked


# ---------------------------------------------------------------- 3. one-way override
@pytest.mark.parametrize("verdict,ai,final", [
    ("ACCEPT", "state_as_written", "state_as_written"), ("ACCEPT", "withhold", "withhold"),
    ("REWRITE", "state_as_written", "narrow"), ("REWRITE", "withhold", "withhold"),
    ("REJECT", "state_as_written", "withhold"), ("REJECT", "narrow", "withhold"),
    ("HOLD", "state_as_written", "withhold"), ("BOGUS", "state_as_written", "withhold"),
])
def test_enforce_is_one_way(verdict, ai, final):
    out = capas.enforce(ai, {"verdict": verdict, "licensed_claim": "the narrower statement"})
    assert out["action"] == final
    assert out["overridden"] == (final != ai)
