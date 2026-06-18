# CAPAS External Reviewer Prompt

Thank you for reviewing CAPAS Claim Gate.

CAPAS is a rule-based evidence gate for scientific-computation claims. It is not
an LLM judge, not a new provenance standard, and not fine-tune ready. The narrow
question is whether this evidence/claim split helps audit scientific-computation
outputs.

Please run:

```bash
python -m pip install -e .
capas demo
capas schema
capas check-input --input examples/external_claim_rewrite.json
capas decide --input examples/external_claim_rewrite.json
capas ui
```

Then answer:

1. Would this evidence/claim split help you audit scientific-computation outputs?
2. Which required field, evidence level, or decision category is missing for your workflow?
3. Would you trust `REWRITE`/`HOLD` decisions more than a binary pass/fail gate?
4. What would block adoption in your workflow?

Please do not evaluate CAPAS as a simulator. Evaluate it as an evidence-typed
claim gate over computation traces.
