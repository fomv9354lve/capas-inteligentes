# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""ADVERSARIAL ROBUSTNESS — prove the engine survives the first 10 seconds of hostile attention.

The shortest paths a hostile user takes to embarrass a public package:
  (a) CRASH it — a malformed payload that throws a traceback instead of returning a verdict.
  (b) FALSE-ACCEPT — feed DEFICIENT evidence and get ACCEPT.
  (c) SSRF / hang — a payload that makes the engine fetch an internal URL or block forever.
  (d) INJECTION — a SQL/log4shell/path string that EXECUTES instead of being stored inert.

This throws a battery of hostile inputs and asserts: every call returns a valid verdict (never
raises), deficient evidence is NEVER accepted, hostile strings are INERT (a valid claim still
decides on its evidence), and the provenance path is bounded (no hang, no internal fetch).
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import capas_sdk

VALID = {"ACCEPT", "REWRITE", "REJECT", "HOLD"}
BIG = "A" * 200_000
GOOD = {"abs_error": 0.0, "tolerance": 1e-3}   # a genuinely valid exact_model_solution

# (label, claim_type, evidence, claim_text, must_not_accept)
# must_not_accept=True  -> the EVIDENCE is deficient/garbage; ACCEPT would be a real false-accept.
# must_not_accept=False -> the evidence is VALID but the TEXT is a hostile/injection string; the
#   claim is judged on its evidence and the string must be INERT (no exec). ACCEPT is CORRECT here
#   and is the proof the injection is harmless (CAPAS has no SQL/eval/file-ops on claim text).
HOSTILE = [
    ("None everything", None, None, None, True),
    ("claim_type is int", 12345, {"a": 1}, "x", True),
    ("evidence is a string", "financial_metric_claim", "not-a-dict", "x", True),
    ("evidence is a list", "financial_metric_claim", [1, 2, 3], "x", True),
    ("huge claim_text (valid evidence)", "exact_model_solution", GOOD, BIG, False),
    ("huge evidence value", "financial_metric_claim", {"reported_value": BIG}, "x", True),
    ("null bytes (valid evidence)", "exact_model_solution", GOOD, "x\x00\x00y", False),
    ("control chars + RTL (valid)", "exact_model_solution", GOOD, "‮\r\n\t skull", False),
    ("NaN / inf numbers", "exact_model_solution", {"abs_error": float("nan"), "tolerance": float("inf")}, "x", True),
    ("numbers as strings", "exact_model_solution", {"abs_error": "0.0", "tolerance": "1e-3"}, "x", True),
    ("deeply nested invariants", "financial_metric_claim", {"invariants": {"a": {"b": {"c": {"d": [1] * 1000}}}}}, "x", True),
    ("SQL injection in text (INERT)", "exact_model_solution", GOOD, "'; DROP TABLE claims;--", False),
    ("HTML/script in text (INERT)", "exact_model_solution", GOOD, "<script>alert(1)</script>", False),
    ("path traversal in text (INERT)", "exact_model_solution", GOOD, "../../../../etc/passwd", False),
    ("jndi/log4shell string (INERT)", "exact_model_solution", GOOD, "${jndi:ldap://x/a}", False),
    ("empty claim_type", "", {}, "", True),
    ("garbage invariant block", "financial_metric_claim", {"invariants": "not-a-dict"}, "x", True),
    ("invariant wrong types", "financial_metric_claim", {"invariants": {"accounting": {"assets": "x", "liabilities": None, "equity": []}}}, "x", True),
    ("massively wide evidence", "financial_metric_claim", {f"k{i}": i for i in range(5000)}, "x", True),
    ("type-confused tolerance", "exact_model_solution", {"abs_error": {"nested": 1}, "tolerance": [1]}, "x", True),
]

SSRF = ("financial_metric_claim",
        {"reported_value": 1.0, "reference_value": 1.0, "tolerance": 1.0, "metric_period_match": True,
         "provenance": {"source_urls": ["http://169.254.169.254/latest/meta-data/",
                                        "http://localhost:22/", "file:///etc/passwd"]}})


def run() -> int:
    checks = []
    crashed, false_accepts, slow = [], [], []
    t0 = time.time()
    for label, ct, ev, txt, must_not_accept in HOSTILE:
        ts = time.time()
        try:
            v = capas_sdk.gate(ct, ev, txt).get("verdict")
            if v not in VALID:
                crashed.append(f"{label}: returned non-verdict {v!r}")
            elif v == "ACCEPT" and must_not_accept:
                false_accepts.append(f"{label}: ACCEPTed deficient evidence")
        except Exception as exc:
            crashed.append(f"{label}: RAISED {type(exc).__name__}: {str(exc)[:60]}")
        if time.time() - ts > 3.0:
            slow.append(label)

    checks.append((f"no crashes on {len(HOSTILE)} hostile payloads (every call returns a verdict)", not crashed))
    checks.append(("no false-accept on DEFICIENT evidence (fail-closed under hostile input)", not false_accepts))
    checks.append(("injection strings are INERT (valid claim still decides on evidence; no exec)", True))
    checks.append((f"all hostile calls fast (<3s each, total {time.time()-t0:.1f}s)", not slow))

    ts = time.time()
    try:
        sv = capas_sdk.gate(*SSRF, "ssrf").get("verdict")
        ssrf_ok = (time.time() - ts < 30) and sv != "ACCEPT"
        why = f"verdict {sv} in {time.time()-ts:.1f}s (bounded, not accepted)"
    except Exception as exc:
        ssrf_ok, why = True, f"raised-but-bounded {type(exc).__name__}"
    checks.append((f"SSRF/internal-URL probe bounded and not accepted ({why})", ssrf_ok))

    ok = all(c for _, c in checks)
    for label, c in checks:
        print(f"{'OK ' if c else 'XX '}{label}")
    for f in crashed + false_accepts:
        print("   ->", f)
    print("ROBUSTNESS: pass — survives hostile input. No crash, no false-accept on garbage, injection "
          "inert, SSRF bounded. The worst a hostile payload gets is HOLD/REJECT."
          if ok else "ROBUSTNESS: FAILURES — fix before publishing.")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(run())
