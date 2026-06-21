"""CAPAS — claim_type proposer (roadmap #7). LLM-assisted, PROPOSE-ONLY, pharma-focused.

The bigger field (non-experts, clinical/pharma teams) is reached WITHOUT touching the
determinism moat. The rule is structural, not a promise: the proposer maps free
clinical/pharma text to a claim FAMILY + its evidence contract, but its output NEVER
enters the deterministic verdict. The engine gates the human-CONFIRMED payload only; the
proposal is a separate, non-binding field the decision path does not read.

Two consequences that keep the moat intact even when the proposer is wrong:
  - the verdict is INVARIANT to the proposal (it is not in the decision path), and
  - if a human confirms the WRONG family, the evidence fails that family's contract and
    the engine fails CLOSED (HOLD/REJECT), never ACCEPT.

Key from env (triage role), never stored. No key -> a transparent DETERMINISTIC keyword
proposal (CLAIM_TYPE_TERMS) — still propose-only, no LLM. Families are validated against
the engine's real CLAIM_TYPE_REGISTRY; an unrecognized suggestion proposes NOTHING (the
engine never guesses a family). `capas` is imported lazily so this module stays light and
loads with the cognitive layer blocked.
"""
from __future__ import annotations

import json
import os
import subprocess
import tempfile
from typing import Any

_PROMPT = """You help a pharma/clinical team classify a scientific claim for the CAPAS
admissibility engine. Given the claim text, pick the SINGLE best claim family from this
exact list (return its key verbatim, or "unknown" if none fits):
{families}

Claim text: {text}

Return STRICT JSON: {{"claim_type":"<key or unknown>","rationale":"<one sentence>"}}.
You only PROPOSE; a human confirms and the deterministic engine decides. Do not invent a family."""


def _registry() -> dict[str, Any]:
    import capas  # lazy: keep this module light and Cara-2-free at load
    return capas.CLAIM_TYPE_REGISTRY


def contract_for(claim_type: str) -> dict[str, Any] | None:
    spec = _registry().get(claim_type)
    if not spec:
        return None
    return {"required": list(spec["required"]), "optional": list(spec.get("optional", [])),
            "description": spec.get("description")}


def _deterministic_proposal(text: str) -> str | None:
    """Transparent keyword scoring against the engine's CLAIM_TYPE_TERMS (no LLM)."""
    import capas
    t = (text or "").lower()
    best, best_score = None, 0
    for ctype, terms in capas.CLAIM_TYPE_TERMS.items():
        score = sum(1 for term in terms if term.lower() in t)
        if score > best_score:
            best, best_score = ctype, score
    return best if best_score > 0 else None


def _ask_llm(text: str, key: str, model: str) -> str | None:
    families = "\n".join(f"- {k}: {v.get('description', '')}" for k, v in _registry().items())
    body = json.dumps({"model": model, "temperature": 0.2, "response_format": {"type": "json_object"},
                       "messages": [{"role": "user", "content": _PROMPT.format(families=families, text=text)}],
                       "max_tokens": 300})
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        f.write(body); bf = f.name
    try:
        out = subprocess.run(["curl", "-s", "-m", "60", "https://api.deepseek.com/v1/chat/completions",
                              "-H", f"Authorization: Bearer {key}", "-H", "Content-Type: application/json",
                              "--data", f"@{bf}"], capture_output=True, text=True)
        return json.loads(json.loads(out.stdout)["choices"][0]["message"]["content"]).get("claim_type")
    except Exception:
        return None
    finally:
        os.unlink(bf)


def propose(text: str, key: str | None = None, model: str = "deepseek-v4-flash") -> dict[str, Any]:
    """PROPOSE a claim family + evidence contract from free text. NON-BINDING — the
    deterministic verdict never reads this. With a key: LLM-assisted; without: transparent
    keyword match. An unrecognized family proposes nothing (the engine never guesses)."""
    key = key or os.environ.get("DEEPSEEK_KEY") or os.environ.get("CAPAS_TRIAGE_KEY")
    if key:
        ctype, method = _ask_llm(text, key, model), "llm-assisted (proposal only)"
    else:
        ctype, method = _deterministic_proposal(text), "deterministic-keyword (proposal only)"

    if not ctype or ctype not in _registry():
        return {"claim_type": None, "binding": False, "method": method,
                "note": "unrecognized — a human must classify; the engine never guesses a family",
                "frontier": "PROPOSAL ONLY — the deterministic verdict ignores this field"}

    contract = contract_for(ctype)
    return {
        "claim_type": ctype,
        "evidence_contract": contract,
        "binding": False,                       # the moat: this can never decide
        "method": method,
        "what_to_confirm": f"Confirm this is a {ctype}, then supply its required evidence: {contract['required']}",
        "frontier": ("PROPOSAL ONLY — the deterministic verdict ignores this field. The engine gates the "
                     "human-confirmed payload; if the family is wrong, the evidence fails its contract and "
                     "the engine fails CLOSED (HOLD/REJECT), never ACCEPT."),
    }
