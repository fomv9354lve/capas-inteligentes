from __future__ import annotations

import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "external_reviewer_packet"

FILES = [
    ("PRODUCT.md", ROOT / "PRODUCT.md"),
    ("README.md", ROOT / "README.md"),
    ("capas_product_demo_report.md", ROOT / "outputs" / "capas_product_demo_report.md"),
    ("capas_product_demo_report.json", ROOT / "outputs" / "capas_product_demo_report.json"),
    ("external_claim_accept.json", ROOT / "examples" / "external_claim_accept.json"),
    ("external_claim_rewrite.json", ROOT / "examples" / "external_claim_rewrite.json"),
    ("external_claim_hold.json", ROOT / "examples" / "external_claim_hold.json"),
    ("external_claim_invalid.json", ROOT / "examples" / "external_claim_invalid.json"),
    ("capas_claim_payload.schema.json", ROOT / "docs" / "schema" / "capas_claim_payload.schema.json"),
    ("external_input_schema_report.json", ROOT / "outputs" / "external_input_schema_report.json"),
    ("external_claim_rewrite_decision.json", ROOT / "outputs" / "external_claim_rewrite_decision.json"),
    ("capas_claim_gate_ui.html", ROOT / "outputs" / "capas_claim_gate_ui.html"),
]


REVIEW_PROMPT = """# CAPAS External Reviewer Prompt

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
"""


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    copied = []
    missing = []
    for label, src in FILES:
        if not src.exists():
            missing.append(str(src.relative_to(ROOT)))
            continue
        dst = OUT / label
        shutil.copy2(src, dst)
        copied.append(label)

    (OUT / "REVIEW_PROMPT.md").write_text(REVIEW_PROMPT, encoding="utf-8")
    copied.append("REVIEW_PROMPT.md")

    manifest = {
        "packet": "external_reviewer_packet",
        "status": "ready" if not missing else "incomplete",
        "copied": copied,
        "missing": missing,
        "completion_rule": (
            "External user validation is complete only when an external reviewer "
            "returns feedback that either changes the schema or confirms utility."
        ),
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print(f"external reviewer packet: {manifest['status']}")
    print(f"wrote {OUT}")
    if missing:
        print("missing:")
        for item in missing:
            print(f"  {item}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
