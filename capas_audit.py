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

HONESTY CAVEAT (load-bearing — do not strip):
  `audit_milestone` is a CONSISTENCY PROBE, not a correctness/moat measurement. Its
  "ground truth" is the auditor's self-declared intent and the engine's own verdict,
  so "0 breaches" is TAUTOLOGICAL: the engine agreeing with the only oracle present
  (itself) proves internal consistency, NOT that the verdicts are right. A low
  auditor-anticipation number is equally compatible with a strong engine and with one
  that returns consistent nonsense — it does NOT discriminate. The ONLY non-tautological
  evidence is `audit_against_truth`: an INDEPENDENT, externally-known truth per case
  (arithmetic, a physical constant, a known-false claim — authored outside both the
  engine and the auditor), measuring (a) engine accuracy vs that truth, and (b) the
  discriminating subset where the auditor PREDICTED one verdict, the engine CONTRADICTED
  it, and the independent truth confirmed the engine. That subset is the real signal.
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
        "attacks": len(attacks), "self_inconsistencies": len(landed), "consistent": len(caught), "errors": len(errors),
        "inconsistency_detail": landed,
        # NOT a moat/correctness claim. The only oracle here is the engine + the auditor's
        # self-declared intent, so this measures INTERNAL CONSISTENCY, not whether the
        # verdicts are right. Real evidence requires audit_against_truth (independent truth).
        "self_consistent": len(landed) == 0,
        "auditor_anticipation": round(pred_hits / n_att, 3),   # how often the auditor's model matched the engine
        "anticipation_note": "this number says NOTHING about engine correctness: a low value is equally "
                             "consistent with a strong engine and with consistent nonsense. It only measures "
                             "whether the auditor anticipated a deterministic function. NOT evidence of a moat.",
        "verdict": "SELF-CONSISTENT (tautological — engine agrees with itself; not a correctness claim)"
                   if not landed else
                   f"SELF-INCONSISTENCY — {len(landed)} case(s); review {[b['name'] for b in landed]}",
        "caveat": "consistency probe only; run audit_against_truth for non-tautological evidence",
        "protocol": "auditor proposes (DeepSeek), engine judges (deterministic), subject reads the residual",
    }


def audit_against_truth(cases: list[dict[str, Any]], judge: Callable[[dict], str] | None = None,
                        key: str | None = None, model: str = "deepseek-v4-flash") -> dict[str, Any]:
    """The NON-TAUTOLOGICAL test. Each case carries an INDEPENDENT truth verdict
    (authored from external fact — arithmetic, a physical constant, a known-false
    claim — NOT from the engine or the auditor). We measure:
      (a) engine accuracy vs that independent truth (the real number), and
      (b) the DISCRIMINATING subset: cases where the auditor PREDICTED verdict P, the
          engine produced V != P, and the independent truth confirmed V. Only this
          subset distinguishes 'brilliant engine' from 'consistent nonsense' — it is
          the test the consistency probe cannot give.
    case: {name, claim, evidence, truth:'ACCEPT|REJECT|HOLD'}. Auditor prediction is
    optional (needs a key); without it, only engine accuracy (a) is reported.
    """
    judge = judge or (lambda p: capas_verify.verify(p).get("verified_verdict"))
    key = key or os.environ.get("DEEPSEEK_KEY") or os.environ.get("CAPAS_TRIAGE_KEY")
    rows, correct, discriminators = [], 0, []
    for c in cases:
        payload = {"schema_version": "capas-claim-payload-v3",
                   "claim": {"id": c.get("name", "case"), **(c.get("claim") or {})},
                   "evidence": c.get("evidence") or {}}
        v = judge(payload)
        truth = c.get("truth")
        engine_right = (v == truth)
        correct += int(engine_right)
        pred = None
        if key:
            p = _ask(f"Predict CAPAS's deterministic verdict (ACCEPT/REJECT/HOLD only) for this claim+evidence, "
                     f"as STRICT JSON {{\"verdict\":\"...\"}}: {json.dumps(payload)}", key, model)
            pred = (p or {}).get("verdict") if p else None
        # the discriminating case: auditor wrong, engine contradicts it, independent truth confirms engine
        if pred and pred != v and engine_right:
            discriminators.append({"name": c.get("name"), "auditor_said": pred, "engine_said": v, "truth": truth})
        rows.append({"name": c.get("name"), "engine": v, "truth": truth, "engine_right": engine_right,
                     "auditor_pred": pred})
    n = len(cases) or 1
    return {
        "cases": len(cases),
        "engine_accuracy_vs_independent_truth": round(correct / n, 3),   # (a) the real number
        "discriminating_cases": discriminators,                          # (b) the only moat-relevant evidence
        "discriminator_count": len(discriminators),
        "rows": rows,
        "reading": "engine_accuracy is the honest correctness number (independent oracle). "
                   "discriminating_cases are the only ones that distinguish a strong engine from "
                   "consistent nonsense: auditor predicted X, engine did Y!=X, independent truth confirmed Y.",
    }
