#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Arm B's access to CAPAS v2 (PROTOCOL.md). Re-derivation is ON: Python snippets are re-run by the engine, ledger
metrics are recomputed from evidence.ledger. Every call is logged (arm_B/<model>/calls.jsonl) for scoring: the final
decision of arm B is capas.enforce(<agent's action>, <logged verdict>), applied by score.py.

  python3 research/exp_capas_v2/capas_v2_call.py --requirements python|ledger
  python3 research/exp_capas_v2/capas_v2_call.py --claim R1#7 --agent <name> --log <dir> payload.json   (or '-')"""
from __future__ import annotations

import json, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
import capas  # noqa: E402

TYPES = {"python": "programming_language_behavior_claim", "ledger": "financial_metric_claim"}
LEDGER_DOC = {
    "ledger": {"rows_csv": "<the CSV exactly as in the materials>", "period": "YYYY | YYYY-Qn | YYYY-MM",
               "metric": "arithmetic over aggregates of the rows in the period, e.g. "
                         "'sum(revenue)', '(sum(revenue) - sum(cogs)) / sum(revenue)', "
                         "'sum(revenue) / sum(revenue, prev) - 1' (prev = previous period), "
                         "'sum(revenue) / distinct(customer, revenue)'. Account names as in the CSV."},
    "note": "With evidence.ledger the engine recomputes reference_value itself: do not supply reference_value. "
            "reported_value = the number the claim states (a percentage as a fraction: 42.0% -> 0.42); tolerance = "
            "half a unit of the claim's last stated digit (42.0% -> 0.0005; $1,234 -> 0.5)."}
PY_DOC = {"note": "language 'python'; language_version = the version the claim is about (or the one in the log if the "
                  "claim names none); code_snippet = the snippet exactly; expected_output = what the claim says it "
                  "prints, exactly as it would print, and for an exception its last line (e.g. \"KeyError: 'b'\"). "
                  "The engine re-runs the snippet itself, so observed_output is optional."}


def main() -> int:
    a = sys.argv[1:]
    if a[:1] == ["--requirements"]:
        kind = a[1]; t = TYPES[kind]; reg = capas.CLAIM_TYPE_REGISTRY[t]
        print(json.dumps({"claim_type": t, "required": {f: capas.evidence_field_type(f) for f in reg["required"]},
                          "how": LEDGER_DOC if kind == "ledger" else PY_DOC,
                          "payload_shape": {"schema_version": capas.CAPAS_CLAIM_SCHEMA_VERSION,
                                            "claim": {"id": "R1-7", "type": t, "text": "<the claim sentence>"},
                                            "evidence": {"...": "..."}}}, indent=1))
        return 0
    claim = a[a.index("--claim") + 1]; agent = a[a.index("--agent") + 1]; log = Path(a[a.index("--log") + 1])
    src = a[-1]
    payload = json.loads(sys.stdin.read() if src == "-" else Path(src).read_text(encoding="utf-8"))
    t0 = time.time()
    r = capas.decide_external_claim(payload, rederive=True)
    out = {"verdict": r.get("verdict"), "reason": r.get("reason"), "licensed_claim": r.get("licensed_claim"),
           "allowed_actions": capas.allowed_actions(r), "schema_errors": r.get("schema_errors") or None,
           "missing_fields": r.get("missing_fields") or None, "notices": r.get("notices") or None,
           "audit_hash": r.get("audit_hash")}
    log.mkdir(parents=True, exist_ok=True)
    with (log / "calls.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({"claim": claim, "agent": agent, "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                             "ms": round((time.time() - t0) * 1000, 1), "payload": payload, "verdict": r.get("verdict"),
                             "licensed_claim": r.get("licensed_claim"), "audit_hash": r.get("audit_hash")}) + "\n")
    print(json.dumps({k: v for k, v in out.items() if v is not None}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
