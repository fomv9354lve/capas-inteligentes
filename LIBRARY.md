# CAPAS — a fail-closed verification layer you wrap around your LLM

```bash
pip install -e .          # from this repo (PyPI publish: TODO)
```

```python
from capas_sdk import gate, reward, verified, certificate

# 1. Gate a structured claim — deterministic verdict, no LLM in the decision.
g = gate("causal_mechanism_claim", {
    "intervention_or_natural_experiment": True,
    "temporal_order_established": True,
    "confounders_controlled": False,          # <- missing
    "mechanism_evidence_present": True,
})
g["verdict"]        # -> "REWRITE"  (with the missing field named and a licensed rewrite)

# 2. A verifiable reward your model can't game by being plausible (RLVR signal).
reward("systematic_review_claim", {                # all four contract fields present
    "protocol_registered": True, "inclusion_criteria_declared": True,
    "risk_of_bias_assessed": True, "effect_consistency": True})        # -> 1.0
reward("causal_mechanism_claim", {})               # unsupported              -> 0.0

# 3. Wrap your LLM: it PROPOSES the evidence, CAPAS DISPOSES the verdict.
def my_llm():                                       # your model returns its claimed evidence
    return {"artifact_available": True, "independent_reproduction_pass": True}
verified(my_llm, "reproducibility_check")["verdict"]   # -> "ACCEPT" (or REJECT/HOLD — never the LLM's call)
```

## What it does — and does NOT (read this; it is the whole point)

- **Gates fail-closed.** An unsupported claim never becomes `ACCEPT`. It is `REJECT` (refuted),
  `REWRITE` (fixable, with the diff), or `HOLD` (unverifiable, deferred). **0 false-accepts on
  honestly-declared evidence.**
- **Re-derives numbers.** A reported value that does not recompute from its inputs is `REJECT`ed
  (fabricated-number detection), not trusted.
- **Emits a dense verifiable reward** aligned with the gate — the RLVR signal a plausibility judge
  can't give, and a model can't game by sounding right.
- **It does NOT detect fraud-by-lying.** Grounding reaches *record ↔ text*, never *text ↔ reality*.
  A source that declares correct methods and withholds its raw data passes — that is the irreducible
  GIGO ceiling, crossed only by re-deriving on the actual data, when it exists. CAPAS says exactly
  which slice it re-derived and which it could only attest.

## The boost, measured

```bash
python3 examples/boost_your_llm.py
# LLM-alone false-accepts:  3/3 unsupported claims waved through
# LLM + CAPAS false-accepts: 0/3   <- the boost
```

The model does not get smarter. Its output becomes **admissible-or-deferred** instead of
plausible-or-wrong. The boost is **reliability**, not capability.

## API

| Call | Returns |
|---|---|
| `gate(claim_type, evidence)` | `{verdict: ACCEPT/REWRITE/REJECT/HOLD, reason, missing_fields, ...}` |
| `reward(claim_type, evidence)` | dense reward in `[0,1]`, aligned with the gate |
| `verified(propose_fn, claim_type)` | gated verdict over the LLM's proposed evidence |
| `certificate(claim_type, evidence)` | signed, re-derivable admissibility certificate (audit artifact) |
| `gate_text(text, claim_type, extractor)` | raw text → fail-closed gate (extraction deferred to a human on disagreement) |

12 claim families ship with evidence contracts; unsupported domains `HOLD` until a team defines a
new contract. No language model is ever in the verdict.
