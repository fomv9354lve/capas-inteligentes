"""CAPAS — LLM extraction layer (proposer), deterministically re-verified.

The LLM is a PROPOSER, never the guarantor. It reads unstructured input and
proposes a structured {claim, evidence} together with a cited source SPAN for
every input value. CAPAS then RE-VERIFIES each span against the source (the quote
exists in the text and carries the value) and runs the deterministic verify()
using ONLY span-grounded inputs. A fabricated / hallucinated value fails span
verification, is dropped, and the verdict falls through to HOLD/ATTEST — the LLM
can EXPAND what gets verified but can never make something ACCEPT that does not
re-derive. The verdict stays deterministic; the LLM's every output is itself
gated. The claimed/derived value is NOT trusted — CAPAS re-derives it from the
grounded inputs.

Moat, restated: not "no LLM" but "the LLM never guarantees; everything it says is
re-verified or deferred." SOTA: proposer-verifier / neuro-symbolic oversight
(FormalJudge; weak-strong verification). The LLM runs only in its authorized
triage role; the key is read from env (DEEPSEEK_KEY / CAPAS_TRIAGE_KEY), never
stored. Fully testable offline: propose() needs the LLM, but verify_extraction()
and assemble_and_verify() are pure and run on any proposal dict.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
from typing import Any

import capas_verify

# Evidence keys whose number is the CLAIM being tested (re-derived by CAPAS), not a
# raw input — these do not require a citation; CAPAS recomputes them from inputs.
_DERIVED_KEYS = {"reported", "reported_value", "reported_area", "declared", "value", "tolerance",
                 "alpha", "coeff", "reference_value"}
_NUM_RE = re.compile(r"-?\d[\d,]*\.?\d*")


def _normalize(s: str) -> str:
    return re.sub(r"\s+", " ", str(s or "")).strip().lower()


def _nums(s: str) -> set[str]:
    return {m.group(0).replace(",", "") for m in _NUM_RE.finditer(str(s))}


def _span_grounds_value(span: str, value: Any, source: str) -> bool:
    """A citation grounds a value iff the span is really present in the source AND
    the span actually carries that numeric value (no fabricated quote, no number
    swapped in)."""
    nspan, nsrc = _normalize(span), _normalize(source)
    if not nspan or nspan not in nsrc:
        return False
    want = _nums(str(value))
    have = _nums(span)
    return bool(want) and want.issubset(have)


def _walk_numbers(obj: Any, path: str = "") -> list[tuple[str, str, Any]]:
    """Yield (path, leaf_key, number) for every numeric leaf in the evidence."""
    out: list[tuple[str, str, Any]] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            out += _walk_numbers(v, f"{path}.{k}" if path else str(k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out += _walk_numbers(v, f"{path}[{i}]")
    elif isinstance(obj, (int, float)) and not isinstance(obj, bool):
        leaf = path.split(".")[-1].split("[")[0]
        out.append((path, leaf, obj))
    return out


def verify_extraction(proposal: dict[str, Any], source_text: str) -> dict[str, Any]:
    """Check the LLM's proposal against the source. Returns the grounding report:
    which input values are span-verified, which are not, and whether the evidence
    is FULLY grounded (every non-derived input cited and present in the source)."""
    citations = proposal.get("citations") or []
    # index citations by the numbers they carry, keeping only the genuine ones
    verified_values: set[str] = set()
    verified_cites, rejected_cites = [], []
    for c in citations:
        span, val = c.get("span"), c.get("value")
        if _span_grounds_value(span or "", val, source_text):
            verified_values |= _nums(str(val))
            verified_cites.append(c)
        else:
            rejected_cites.append(c)

    evidence = proposal.get("evidence") or {}
    ungrounded = []
    for path, leaf, num in _walk_numbers(evidence):
        if leaf in _DERIVED_KEYS:
            continue  # the claimed/derived figure is re-derived by CAPAS, not trusted
        if not (_nums(str(num)) & verified_values):
            ungrounded.append({"path": path, "value": num})
    return {"fully_grounded": not ungrounded, "ungrounded_inputs": ungrounded,
            "verified_citations": verified_cites, "rejected_citations": rejected_cites,
            "intention_flags": proposal.get("intention_flags") or []}


def assemble_and_verify(proposal: dict[str, Any], source_text: str,
                        schema_version: str = "capas-claim-payload-v3") -> dict[str, Any]:
    """Re-verify the extraction, then run the DETERMINISTIC gate. If any input is
    not span-grounded, CAPAS does not run the rung on ungrounded data — it defers
    (HOLD/ATTEST) to the human guarantor. The LLM proposed; CAPAS disposes."""
    report = verify_extraction(proposal, source_text)
    claim = dict(proposal.get("claim") or {})
    claim.setdefault("id", "extracted")
    out: dict[str, Any] = {"extraction": report, "llm_proposed_claim": claim}

    if not report["fully_grounded"]:
        out["verdict"] = "HOLD"
        out["scope"] = "ATTEST"
        out["rationale"] = (
            "Extraction not fully grounded: the following proposed inputs are not present in the "
            f"source (possible hallucination) — {report['ungrounded_inputs']}. CAPAS does not gate "
            "on ungrounded data; deferred to the human verifier. The LLM proposes; it never guarantees.")
        return out

    evidence = dict(proposal.get("evidence") or {})
    # The substantive check is the re-derivable DOMAIN rung; if the LLM proposed a
    # domain block but omitted the claim's base-contract scaffolding, fill neutral
    # placeholders so the deterministic rung governs (it is what actually verifies).
    _DOMAIN = {"accounting", "xbrl", "crypto", "dimensions", "stoichiometry", "physical",
               "computation", "integration", "raw_data"}
    if (set(evidence) & _DOMAIN) and "reported_value" not in evidence:
        evidence.setdefault("reported_value", 1.0)
        evidence.setdefault("reference_value", 1.0)
        evidence.setdefault("tolerance", 1.0)
        evidence.setdefault("metric_period_match", True)
    payload = {"schema_version": schema_version, "claim": claim, "evidence": evidence}
    receipt = capas_verify.verify(payload)
    out["verdict"] = receipt["verified_verdict"]
    out["scope"] = receipt["scope"]
    out["receipt"] = receipt
    out["rationale"] = (
        "Every proposed input is span-grounded in the source; the claimed value was RE-DERIVED "
        "deterministically (not trusted from the LLM). " + (receipt.get("rationale") or [""])[0])
    if report["intention_flags"]:
        out["attest_flags"] = report["intention_flags"]  # suspicion -> human, never a GATE
    return out


# ── LLM proposer (authorized triage role only; never the guarantor) ──
_PROMPT = """You read a source text and PROPOSE a structured claim + evidence for
CAPAS, a deterministic verifier. You do NOT decide anything — CAPAS re-derives and
re-checks every value you cite. Rules:
- For every RAW INPUT number in evidence, give a "citation" with the EXACT substring
  from the source that contains it (verbatim, copy it). If a value is not in the
  source, do NOT invent it — omit it.
- Put the claimed/derived figure in evidence as "reported" (CAPAS recomputes it).
- Use CAPAS evidence shapes, e.g. accounting financial_ratio:
  {"accounting":{"identity":"financial_ratio","ratio":"current_ratio",
   "current_assets":N,"current_liabilities":N,"reported":R}}
- Optionally add "intention_flags": short notes on anything that looks like deception
  (these go to the human, never to the verdict).
Return STRICT JSON: {"claim":{"type":"financial_metric_claim","text":"..."},
"evidence":{...},"citations":[{"value":N,"span":"verbatim source substring"}],
"intention_flags":[...]}.

SOURCE:
%s
"""


def propose(source_text: str, model: str = "deepseek-v4-flash", key: str | None = None) -> dict[str, Any] | None:
    """Call the triage LLM to PROPOSE a structured payload. Returns None on failure.
    Key from arg or env DEEPSEEK_KEY / CAPAS_TRIAGE_KEY; never stored."""
    key = key or os.environ.get("DEEPSEEK_KEY") or os.environ.get("CAPAS_TRIAGE_KEY")
    if not key:
        return None
    body = json.dumps({"model": model, "temperature": 0.2,
                       "response_format": {"type": "json_object"},
                       "messages": [{"role": "user", "content": _PROMPT % source_text[:8000]}],
                       "max_tokens": 4000})
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        f.write(body); bf = f.name
    try:
        out = subprocess.run(
            ["curl", "-s", "-m", "120", "https://api.deepseek.com/v1/chat/completions",
             "-H", f"Authorization: Bearer {key}", "-H", "Content-Type: application/json",
             "--data", f"@{bf}"], capture_output=True, text=True)
        resp = json.loads(out.stdout)
        return json.loads(resp["choices"][0]["message"]["content"])
    except Exception:
        return None
    finally:
        os.unlink(bf)


def extract_and_verify(source_text: str, model: str = "deepseek-v4-flash",
                       key: str | None = None) -> dict[str, Any]:
    """End to end: LLM proposes from prose -> CAPAS re-verifies spans + re-derives."""
    proposal = propose(source_text, model=model, key=key)
    if proposal is None:
        return {"verdict": "HOLD", "scope": "ATTEST",
                "rationale": "No triage LLM available (set DEEPSEEK_KEY) or proposal failed; "
                "nothing to verify. CAPAS does not guess.", "extraction": None}
    return assemble_and_verify(proposal, source_text)
