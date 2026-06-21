"""Demo + check: the claim_type proposer (roadmap #7) and its STRUCTURAL frontier.

Deterministic (no key -> transparent keyword proposal). Proves the moat is intact while
reaching non-experts: the proposer maps pharma text to a family + contract, but
  (1) the verdict is INVARIANT to the proposal — even a forged "verdict":"ACCEPT" injected
      into the payload does not change the engine's decision (it computes, never trusts);
  (2) confirming the WRONG family fails CLOSED (evidence misses that contract -> not ACCEPT);
  (3) an unrecognized claim proposes NOTHING (no guessed family);
  (4) the decision path never imports the proposer (containment).
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import capas
import capas_propose as P


def _verdict(payload):
    return capas.decide_external_claim(payload).get("verdict")


def run() -> int:
    checks = []

    # (0) proposer maps pharma text -> a real family + its contract, NON-BINDING
    prop = P.propose("In the Phase III trial the effect was statistically significant, p-value below alpha")
    checks.append(("pharma text -> proposes statistical_confidence, binding=False",
                   prop["claim_type"] == "statistical_confidence" and prop["binding"] is False
                   and "p_value" in prop["evidence_contract"]["required"]))

    # (3) unrecognized -> proposes nothing (never guesses a family)
    none_prop = P.propose("zzz wobble nonsense")
    checks.append(("unrecognized text -> proposes NOTHING (no guessed family)",
                   none_prop["claim_type"] is None))

    # a known payload + its baseline verdict
    payload = {"claim": {"id": "p1", "type": "financial_metric_claim", "text": "x"},
               "evidence": {"reported_value": 1.0, "reference_value": 1.0, "tolerance": 1.0, "metric_period_match": True}}
    base = _verdict(payload)

    # (1a) attaching the proposal does NOT change the verdict (proposal is not in the decision path)
    with_prop = {**payload, "proposal": prop}
    checks.append(("verdict INVARIANT to an attached proposal", _verdict(with_prop) == base))

    # (1b) STRONG: injecting a FORGED "verdict":"ACCEPT" into the payload does not change the decision
    forged = {**payload, "verdict": "ACCEPT", "proposal": {"claim_type": "exact_model_solution", "binding": False}}
    checks.append(("forged verdict/proposal injected -> engine ignores it and returns its own verdict",
                   _verdict(forged) == base))

    # (2) confirming the WRONG family fails CLOSED: financial evidence under a causal contract
    wrong_type = {"claim": {"id": "p2", "type": "causal_mechanism_claim", "text": "x"},
                  "evidence": {"reported_value": 1.0, "reference_value": 1.0, "tolerance": 1.0, "metric_period_match": True}}
    wv = _verdict(wrong_type)
    checks.append((f"wrong confirmed family -> fails CLOSED (verdict {wv}, not ACCEPT)", wv != "ACCEPT"))

    # (4) containment: the decision path never imports the proposer
    def _imports(mod):
        tree = ast.parse((ROOT / f"{mod}.py").read_text())
        out = set()
        for n in ast.walk(tree):
            if isinstance(n, ast.Import):
                out |= {a.name.split(".")[0] for a in n.names}
            elif isinstance(n, ast.ImportFrom) and n.module:
                out.add(n.module.split(".")[0])
        return out
    leak = [m for m in ("capas", "capas_verify", "capas_route", "capas_admissibility")
            if "capas_propose" in _imports(m)]
    checks.append(("containment: no decision module imports capas_propose", not leak))

    ok = all(c for _, c in checks)
    for label, c in checks:
        print(f"{'✅' if c else '❌'} {label}")
    print("CLAIM_TYPE PROPOSER + STRUCTURAL FRONTIER (LLM proposes, engine disposes): pass ✅" if ok
          else "PROPOSER: FAILURES ❌")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(run())
