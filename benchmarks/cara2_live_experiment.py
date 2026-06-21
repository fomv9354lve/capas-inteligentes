"""Cara 2 — LIVE controlled experiment: does CAPAS-connected generation ground more?

A paired A/B with a real LLM proposer (DeepSeek, triage role; key from env), judged
by the deterministic verifier (the same CAPAS in both arms — the JUDGE, not part of
the treatment).

  CONTROL arm   : the LLM extracts a claim+evidence with cited spans, ONE shot.
  CONNECTED arm : the LLM extracts; CAPAS verifies; if it does not ground, CAPAS
                  returns the SPECIFIC gap (which input was not found verbatim in the
                  source); the LLM revises; re-judge — up to K rounds.

Sources are paired (same text both arms), mixing TRUE-groundable statements (measure
the lift) and LIES (measure that the connected arm NEVER produces a false-accept —
the moat must hold). Metrics: groundability rate (control vs connected) and
false-accept rate (must be 0 in both). No hallucinated advantage: the verdict is the
deterministic CAPAS verdict; the LLM never decides.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import capas_extract as EX

KEY = os.environ.get("DEEPSEEK_KEY") or os.environ.get("CAPAS_TRIAGE_KEY")

# Paired sources: (source_text, true_ratio, is_lie). current_ratio = CA / CL.
def _src(ca, cl, claimed):
    return (f"Quarterly report. As of the period end, total current assets were ${ca:,} and "
            f"total current liabilities were ${cl:,}. Management reports a current ratio of {claimed}.")

TRUE = [(_src(ca, cl, round(ca / cl, 2)), round(ca / cl, 2)) for ca, cl in
        [(200000, 100000), (450000, 150000), (320000, 160000), (510000, 170000), (240000, 120000),
         (600000, 200000), (135000, 90000), (280000, 140000), (720000, 240000), (165000, 110000)]]
LIES = [(_src(ca, cl, bad), round(ca / cl, 2)) for ca, cl, bad in
        [(200000, 100000, 5.0), (450000, 150000, 9.0), (320000, 160000, 1.0), (510000, 170000, 7.0), (240000, 120000, 0.5)]]


# HARD sources (CARA2_HARD=1): the current-asset/liability figures are BURIED among
# distractors (property, goodwill, long-term debt) and written verbatim in varied
# formats, so a one-shot extraction tends to pick the wrong figure or mis-cite the
# span -> CAPAS HOLDs -> the feedback loop has headroom to correct.
def _hard(prop, goodwill, ca, cl, ltd, claimed):
    return (f"In fiscal 2024 the balance sheet showed property of {prop}, goodwill of {goodwill}, "
            f"and inventory plus receivables comprising total current assets of {ca}, against "
            f"accounts payable and short-term borrowings totaling current liabilities of {cl}, "
            f"with long-term debt of {ltd}. The board cited a current ratio of {claimed}.")

HARD_TRUE = [
    (_hard("$3,400,000", "$1,100,000", "$1,800,000", "$900,000", "$2,200,000", 2.0), 2.0),
    (_hard("$5.6 million", "$2.0 million", "$4,500,000", "$1,500,000", "$3.0 million", 3.0), 3.0),
    (_hard("$890,000", "$120,000", "$640,000", "$320,000", "$410,000", 2.0), 2.0),
    (_hard("$12,000,000", "$3,300,000", "$7,200,000", "$2,400,000", "$5,000,000", 3.0), 3.0),
    (_hard("$2,750,000", "$600,000", "$1,250,000", "$1,000,000", "$1,900,000", 1.25), 1.25),
    (_hard("$430,000", "$75,000", "$510,000", "$170,000", "$260,000", 3.0), 3.0),
    (_hard("$8,100,000", "$1,900,000", "$3,600,000", "$1,800,000", "$4,400,000", 2.0), 2.0),
    (_hard("$1,050,000", "$240,000", "$960,000", "$640,000", "$770,000", 1.5), 1.5),
]
HARD_LIES = [
    (_hard("$3,400,000", "$1,100,000", "$1,800,000", "$900,000", "$2,200,000", 6.0), 2.0),
    (_hard("$5.6 million", "$2.0 million", "$4,500,000", "$1,500,000", "$3.0 million", 8.0), 3.0),
    (_hard("$890,000", "$120,000", "$640,000", "$320,000", "$410,000", 0.5), 2.0),
    (_hard("$12,000,000", "$3,300,000", "$7,200,000", "$2,400,000", "$5,000,000", 1.0), 3.0),
]

if os.environ.get("CARA2_HARD"):
    TRUE, LIES = HARD_TRUE, HARD_LIES

_PROMPT = """Read the source and PROPOSE a structured claim for a deterministic verifier.
Return STRICT JSON: {{"claim":{{"type":"financial_metric_claim","text":"..."}},
"evidence":{{"accounting":{{"identity":"financial_ratio","ratio":"current_ratio",
"current_assets":N,"current_liabilities":N,"reported":R}}}},
"citations":[{{"value":N,"span":"EXACT verbatim substring from the source containing N"}}]}}
Cite the verbatim source substring for current_assets and current_liabilities. Do not invent numbers.{feedback}

SOURCE:
{src}"""


def _ask(src: str, feedback: str = "") -> dict | None:
    body = json.dumps({"model": "deepseek-v4-flash", "temperature": 0.3,
                       "response_format": {"type": "json_object"},
                       "messages": [{"role": "user", "content": _PROMPT.format(src=src, feedback=feedback)}],
                       "max_tokens": 1200})
    for _attempt in range(3):                    # retry transient API failures
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            f.write(body); bf = f.name
        try:
            out = subprocess.run(["curl", "-s", "-m", "90", "https://api.deepseek.com/v1/chat/completions",
                                  "-H", f"Authorization: Bearer {KEY}", "-H", "Content-Type: application/json",
                                  "--data", f"@{bf}"], capture_output=True, text=True)
            return json.loads(json.loads(out.stdout)["choices"][0]["message"]["content"])
        except Exception:
            continue
        finally:
            os.unlink(bf)
    return None


def _control(src: str) -> str:
    prop = _ask(src)
    return EX.assemble_and_verify(prop, src)["verdict"] if prop else "ERROR"


def _connected(src: str, rounds: int = 2) -> str:
    prop = _ask(src)
    if not prop:
        return "ERROR"
    for _ in range(rounds):
        res = EX.assemble_and_verify(prop, src)
        if res["verdict"] in ("ACCEPT", "REJECT"):       # grounded or refuted -> done
            return res["verdict"]
        gap = (res.get("extraction") or {}).get("ungrounded_inputs") or []
        fb = (f"\nCAPAS could NOT verify these inputs (not found verbatim in the source): {gap}. "
              "Copy the EXACT source substring for each value; do not invent.")
        nxt = _ask(src, feedback=fb)
        if nxt:
            prop = nxt
    return EX.assemble_and_verify(prop, src)["verdict"]


def run() -> int:
    if not KEY:
        print("SKIP: set DEEPSEEK_KEY to run the live experiment.")
        return 0

    print(f"paired sources: {len(TRUE)} true-groundable, {len(LIES)} lies\n")
    c_true = k_true = 0
    for src, _ in TRUE:
        cv, kv = _control(src), _connected(src)
        c_true += int(cv == "ACCEPT"); k_true += int(kv == "ACCEPT")
    c_fa = k_fa = 0
    for src, _ in LIES:
        cv, kv = _control(src), _connected(src)
        c_fa += int(cv == "ACCEPT"); k_fa += int(kv == "ACCEPT")

    nT, nL = len(TRUE), len(LIES)
    print(f"GROUNDABILITY (true claims, n={nT}):")
    print(f"   control   (one-shot, no CAPAS): {c_true}/{nT}  ({100*c_true/nT:.0f}%)")
    print(f"   connected (CAPAS feedback loop): {k_true}/{nT}  ({100*k_true/nT:.0f}%)")
    print(f"   lift: {100*(k_true-c_true)/nT:+.0f} points")
    print(f"\nFALSE-ACCEPT (lies, n={nL}) — must be 0 in BOTH (the moat):")
    print(f"   control: {c_fa}/{nL}   connected: {k_fa}/{nL}")
    moat_ok = (c_fa == 0 and k_fa == 0)
    lift_ok = (k_true >= c_true)
    print(f"\n{'✅' if moat_ok else '❌'} moat holds (no false-accept in either arm)")
    print(f"{'✅' if lift_ok else '❌'} connected grounds at least as many true claims as control "
          f"({'lift measured' if k_true > c_true else 'no lift this run'})")
    print("\nCARA 2 LIVE: " + ("✅ measured" if (moat_ok and lift_ok) else "❌"))
    return 0 if (moat_ok and lift_ok) else 1


if __name__ == "__main__":
    raise SystemExit(run())
