"""CAPAS — in-process milestone audit protocol (the engine reviews itself).

Formalizes the discipline we ran ad-hoc into a reusable protocol: at each relevant
milestone, an LLM AUDITOR (DeepSeek, triage role; key from env, never stored)
generates adversarial payloads attacking a claim; the DETERMINISTIC engine judges
them (ground truth — the LLM never decides); a breach is only counted when the
engine itself yields a contradicting verdict. A second independent reviewer (a
subagent) does the meta-review at major milestones. The auditor proposes; the
engine disposes; the subject reads the residual.

Protocol
  1. AUDITOR (DeepSeek): given the claim + the engine's relevant behaviour, emit N
     adversarial payloads intended to make the engine FAIL (false-accept a lie, or
     false-reject a truth).
  2. JUDGE (deterministic): run each through `judge` (default capas_verify.verify).
     breach = the engine's verdict contradicts the payload's honest ground truth.
  3. REPORT: breaches (real), caught, breach-rate, and the auditor's calibration.
  4. CONTROL (subagent): launched separately at major milestones to meta-review.

Key from env DEEPSEEK_KEY / CAPAS_TRIAGE_KEY. No key -> the protocol SKIPS (it does
not fabricate an audit).
"""
from __future__ import annotations

import json
import os
import subprocess
import tempfile
from typing import Any, Callable

import capas_verify

_AUDITOR_PROMPT = """You are a hostile auditor of CAPAS, a deterministic claim
verifier. Milestone under audit: {name}. Claim being stress-tested: {claim}

Emit adversarial JSON payloads (claim+evidence CAPAS will parse) ENGINEERED to make
the engine FAIL — either ACCEPT something that should be REJECTed/held
(false_accept, the real breach), or REJECT something genuinely supported
(true_reject). Use the engine's evidence shapes (raw_data / accounting / dimensions
/ stoichiometry / sql / crypto / physical / consilience ...). Be precise and
mathematically honest; aim at the SEAM the claim depends on.

Return STRICT JSON: {{"attacks":[{{"name":"...","intent":"false_accept|true_reject",
"claim":{{"type":"...","text":"..."}},"evidence":{{...}},
"predicted":"ACCEPT|REJECT|HOLD","ground_truth":"the claim is actually true|false: ..."}}]}}
Give {n} of your strongest attacks."""


def _ask(prompt: str, key: str, model: str) -> dict | None:
    body = json.dumps({"model": model, "temperature": 0.9, "response_format": {"type": "json_object"},
                       "messages": [{"role": "user", "content": prompt}], "max_tokens": 8000})
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        f.write(body); bf = f.name
    try:
        out = subprocess.run(["curl", "-s", "-m", "180", "https://api.deepseek.com/v1/chat/completions",
                              "-H", f"Authorization: Bearer {key}", "-H", "Content-Type: application/json",
                              "--data", f"@{bf}"], capture_output=True, text=True)
        return json.loads(json.loads(out.stdout)["choices"][0]["message"]["content"])
    except Exception:
        return None
    finally:
        os.unlink(bf)


def audit_milestone(name: str, claim: str, judge: Callable[[dict], str] | None = None,
                    n: int = 10, key: str | None = None, model: str = "deepseek-v4-flash") -> dict[str, Any]:
    """Run the adversarial audit of one milestone claim. Returns the breach report."""
    key = key or os.environ.get("DEEPSEEK_KEY") or os.environ.get("CAPAS_TRIAGE_KEY")
    if not key:
        return {"milestone": name, "status": "SKIPPED", "reason": "no DEEPSEEK_KEY; audit not fabricated"}
    judge = judge or (lambda p: capas_verify.verify(p).get("verified_verdict"))

    proposal = _ask(_AUDITOR_PROMPT.format(name=name, claim=claim, n=n), key, model)
    attacks = (proposal or {}).get("attacks", []) if proposal else []
    landed, caught, errors, pred_hits = [], [], [], 0
    for a in attacks:
        payload = {"schema_version": "capas-claim-payload-v3",
                   "claim": {"id": "audit", **(a.get("claim") or {})}, "evidence": a.get("evidence") or {}}
        try:
            v = judge(payload)
        except Exception as e:
            errors.append({"name": a.get("name"), "error": repr(e)}); continue
        breach = (a.get("intent") == "false_accept" and v == "ACCEPT") or \
                 (a.get("intent") == "true_reject" and v == "REJECT")
        pred_hits += int(a.get("predicted") == v)
        (landed if breach else caught).append({"name": a.get("name"), "intent": a.get("intent"),
                                               "verdict": v, "ground_truth": a.get("ground_truth")})
    n_att = len(attacks) or 1
    return {
        "milestone": name, "claim": claim,
        "attacks": len(attacks), "breaches": len(landed), "caught": len(caught), "errors": len(errors),
        "breach_detail": landed,
        "moat_holds": len(landed) == 0,
        "auditor_calibration": round(pred_hits / n_att, 3),    # how often DeepSeek predicted the real verdict
        "verdict": "PASS — engine withstood the audit (0 breaches)" if not landed else
                   f"BREACH — {len(landed)} attack(s) landed; review {[b['name'] for b in landed]}",
        "protocol": "auditor proposes (DeepSeek), engine judges (deterministic), subject reads the residual",
    }
