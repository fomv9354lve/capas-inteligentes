# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""CAPAS — intake membrane: shrink the EXTRACTION residual to the max (fail-closed).

The pilot moved the residual here: paper text -> structured evidence fields. Extraction
cannot be made perfect (the autoformalization/bridge ceiling), but it can be made
FAIL-CLOSED, TRIANGULATED, and GRADED so the residual is measured and routed, never a
silent error:

  - the LLM PROPOSES each field (imagination); we never trust it;
  - each field must be GROUNDED in a quotable source SPAN — no span, no field;
  - K INDEPENDENT extractions must AGREE; agreement bounds the per-field residual
    (consilience: 1/(1+independent_agreers), shrinks geometrically, never 0);
  - DISAGREEMENT -> the field is DEFERRED to a human, NOT fabricated;
  - a deferred/absent required field leaves the payload incomplete, so the deterministic
    gate FAILS CLOSED (HOLD) — extraction uncertainty can never become a false ACCEPT.

The extractor is INJECTED: a deterministic mock for the test (proves the fail-closed
triangulation logic, the moat-preserving part), a DeepSeek extractor for live use (the
proposer, triage role, key from env). `capas` is imported lazily.
"""
from __future__ import annotations

from typing import Any, Callable

# extractor(field, claim_text, source_text, idx) -> {"supported": True|False|None, "span": str|None}
Extractor = Callable[[str, str, str, int], dict[str, Any]]


def extract_field(field: str, claim_text: str, source_text: str, extractor: Extractor,
                  k: int = 3) -> dict[str, Any]:
    """Run K INDEPENDENT span-grounded extractions of one field and triangulate them."""
    results = [extractor(field, claim_text, source_text, i) for i in range(k)]
    votes = [r.get("supported") for r in results]
    spans = [r.get("span") for r in results if r.get("span")]
    decided = [v for v in votes if v is not None]
    distinct = set(decided)

    if not decided or len(distinct) != 1:
        return {"field": field, "value": None, "status": "DEFER",
                "why": "independent extractions disagree or abstain — routed to a human, not fabricated",
                "residual": 1.0, "votes": votes}
    value = distinct.pop()
    if value is True and not spans:                    # affirmative claim needs a grounding span
        return {"field": field, "value": None, "status": "DEFER",
                "why": "affirmed but no source span grounds it — not fabricated", "residual": 1.0, "votes": votes}
    agreers = len(decided)
    return {"field": field, "value": bool(value), "status": "EXTRACTED",
            "residual": round(1.0 / (1.0 + agreers), 4),   # graded; shrinks with independent agreement, never 0
            "span": spans[0] if spans else None, "votes": votes}


def extract_field_multimodel(field: str, claim_text: str, source_text: str,
                             extractors: list[Extractor], runs_per_model: int = 1) -> dict[str, Any]:
    """C2 FIX — triangulate across DISTINCT models. Each extractor is a different model
    (genuinely independent), so a SYSTEMATIC single-model misread (which K runs of that SAME
    model would agree on and miss) is now exposed the moment a model that does not share its
    bias disagrees -> DEFER. Independence groups = MODELS, so the residual reflects real
    model-diversity, not repeated same-model runs."""
    per_model = []
    for ex in extractors:
        runs = [ex(field, claim_text, source_text, r) for r in range(runs_per_model)]
        sv = [v.get("supported") for v in runs if v.get("supported") is not None]
        spans = [v.get("span") for v in runs if v.get("span")]
        per_model.append({"supported": (sv[0] if sv and len(set(sv)) == 1 else None),
                          "span": spans[0] if spans else None})
    decided = [p["supported"] for p in per_model if p["supported"] is not None]
    spans = [p["span"] for p in per_model if p["span"]]
    if not decided or len(set(decided)) != 1:
        return {"field": field, "value": None, "status": "DEFER",
                "why": "models disagree or abstain — a systematic single-model misread is caught across models",
                "residual": 1.0, "models": len(extractors), "model_votes": [p["supported"] for p in per_model]}
    value = decided[0]
    if value is True and not spans:
        return {"field": field, "value": None, "status": "DEFER",
                "why": "affirmed but no source span grounds it", "residual": 1.0}
    groups = len(decided)                              # independent MODELS that agree
    return {"field": field, "value": bool(value), "status": "EXTRACTED",
            "residual": round(1.0 / (1.0 + groups), 4), "models_agreeing": groups,
            "span": spans[0] if spans else None}


def intake_multimodel(claim_text: str, claim_type: str, source_text: str,
                      extractors: list[Extractor]) -> dict[str, Any]:
    """Like intake(), but each field is triangulated across DISTINCT models (C2-resistant)."""
    import capas
    required = capas.required_fields_for_claim(claim_type) or []
    evidence, deferred, per_field, total = {}, [], [], 1.0
    for field in required:
        r = extract_field_multimodel(field, claim_text, source_text, extractors)
        per_field.append(r)
        if r["status"] == "EXTRACTED":
            evidence[field] = r["value"]; total *= r["residual"]
        else:
            deferred.append(field)
    return {"payload": {"schema_version": "capas-claim-payload-v3",
                        "claim": {"id": "intake", "type": claim_type, "text": claim_text}, "evidence": evidence},
            "evidence_extracted": evidence, "deferred_fields": deferred,
            "extraction_residual": round(total, 6), "fail_closed": bool(deferred), "per_field": per_field,
            "note": "independence is across DISTINCT models; a systematic single-model misread is caught and deferred."}


def intake(claim_text: str, claim_type: str, source_text: str, extractor: Extractor,
           k: int = 3) -> dict[str, Any]:
    """Build a structured payload from raw text — fail-closed. Returns the evidence the
    extraction could GROUND, the DEFERRED fields, the measured residual, and a ready-to-gate
    payload. Deferred required fields keep the payload incomplete -> the gate HOLDs."""
    import capas
    required = capas.required_fields_for_claim(claim_type) or []
    evidence, deferred, per_field = {}, [], []
    for field in required:
        r = extract_field(field, claim_text, source_text, extractor, k)
        per_field.append(r)
        if r["status"] == "EXTRACTED":
            evidence[field] = r["value"]
        else:
            deferred.append(field)
    # extraction residual over the whole claim = product of per-field residuals (geometric)
    total = 1.0
    for r in per_field:
        total *= r["residual"] if r["status"] == "EXTRACTED" else 1.0
    payload = {"schema_version": "capas-claim-payload-v3",
               "claim": {"id": "intake", "type": claim_type, "text": claim_text},
               "evidence": evidence}
    return {
        "payload": payload,
        "evidence_extracted": evidence,
        "deferred_fields": deferred,                   # routed to a human — NOT fabricated
        "extraction_residual": round(total, 6),        # measured; never 0 (the bridge ceiling)
        "fail_closed": bool(deferred),                 # any deferred required field -> the gate will HOLD
        "per_field": per_field,
        "note": "the LLM proposes fields; only span-grounded, independently-agreed fields are kept; "
                "disagreement defers to a human; extraction uncertainty can never become a false ACCEPT.",
    }


def _extract_prompt(field: str, claim_text: str, source_text: str) -> str:
    return (f"Source:\n{source_text}\n\nClaim: {claim_text}\n\nDoes the SOURCE explicitly support the "
            f"evidence field '{field}'? Answer STRICT JSON {{\"supported\":true|false,\"span\":\"<exact quote "
            f"from the source, or empty>\"}}. Only true if a quotable span grounds it.")


def gemini_extractor(field: str, claim_text: str, source_text: str, idx: int,
                     key: str | None = None, model: str = "gemini-2.0-flash") -> dict[str, Any]:
    """Live extractor on GOOGLE GEMINI — a DISTINCT lab from DeepSeek, so the two are
    genuinely independent for C2-resistant triangulation. Key from env (GEMINI_KEY), triage
    role, never stored; no key -> abstain (fail-closed)."""
    import json
    import os
    import subprocess
    import tempfile
    key = key or os.environ.get("GEMINI_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not key:
        return {"supported": None, "span": None}
    body = json.dumps({"contents": [{"parts": [{"text": _extract_prompt(field, claim_text, source_text)}]}],
                       "generationConfig": {"temperature": 0.4 + 0.2 * idx, "responseMimeType": "application/json"}})
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        f.write(body); bf = f.name
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
        out = subprocess.run(["curl", "-s", "-m", "60", url, "-H", "Content-Type: application/json",
                              "--data", f"@{bf}"], capture_output=True, text=True)
        txt = json.loads(out.stdout)["candidates"][0]["content"]["parts"][0]["text"]
        r = json.loads(txt)
        span = r.get("span") or None
        return {"supported": r.get("supported"), "span": span if (span and span.strip()) else None}
    except Exception:
        return {"supported": None, "span": None}
    finally:
        import os as _os
        _os.unlink(bf)


def deepseek_extractor(field: str, claim_text: str, source_text: str, idx: int,
                       key: str | None = None, model: str = "deepseek-v4-flash") -> dict[str, Any]:
    """Live extractor (proposer, triage role). Asks whether the SOURCE supports the field and
    to quote the grounding span. Independent runs vary by `idx` (temperature/seed). Key from
    env; no key -> abstain (supported=None) so intake fails closed."""
    import json
    import os
    import subprocess
    import tempfile
    key = key or os.environ.get("DEEPSEEK_KEY") or os.environ.get("CAPAS_TRIAGE_KEY")
    if not key:
        return {"supported": None, "span": None}
    prompt = (f"Source:\n{source_text}\n\nClaim: {claim_text}\n\nDoes the SOURCE explicitly support the "
              f"evidence field '{field}'? Answer STRICT JSON {{\"supported\":true|false,\"span\":\"<exact quote "
              f"from the source, or empty>\"}}. Only true if a quotable span grounds it.")
    bodyd = json.dumps({"model": model, "temperature": 0.4 + 0.2 * idx, "response_format": {"type": "json_object"},
                        "messages": [{"role": "user", "content": prompt}], "max_tokens": 300})
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        f.write(bodyd); bf = f.name
    try:
        out = subprocess.run(["curl", "-s", "-m", "60", "https://api.deepseek.com/v1/chat/completions",
                              "-H", f"Authorization: Bearer {key}", "-H", "Content-Type: application/json",
                              "--data", f"@{bf}"], capture_output=True, text=True)
        r = json.loads(json.loads(out.stdout)["choices"][0]["message"]["content"])
        span = r.get("span") or None
        return {"supported": r.get("supported"), "span": span if (span and span.strip()) else None}
    except Exception:
        return {"supported": None, "span": None}
    finally:
        import os as _os
        _os.unlink(bf)
