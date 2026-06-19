from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRODUCT = ROOT / "docs" / "product.html"
BRIEF = ROOT / "docs" / "CUSTOMER_READY_BRIEF.md"
METRICS = ROOT / "outputs" / "pilot_metrics.json"
UI = ROOT / "outputs" / "capas_claim_gate_ui.html"
REPORT = ROOT / "outputs" / "customer_product_assets_report.json"


REQUIRED = {
    "landing page with narrative": (PRODUCT, ["Stop weak claims", "Read pilot plan", "workflow change"]),
    "landing page screenshots": (PRODUCT, ["CAPAS screenshot mock", "ACCEPT", "RO-Crate pending"]),
    "guided no-code form": (UI, ["Guided claim builder", "buildGuidedPayload", "Build JSON from form"]),
    "paper text ingestion": (UI, ["Paper / text ingestion", "extractCandidateClaims", "candidate claims extracted from paper or text", "evidence_spans"]),
    "human in the loop": (UI, ["Confirm & build payload", "human_confirmed", "CAPAS will not decide unconfirmed candidates"]),
    "local metadata adapter": (UI, ["normalizeLocalMetadataExport", "local_semantic_scholar_pubmed_metadata_adapter", "DOI / external ID", "Paper title"]),
    "paper ingestion report": (UI, ["paper_ingestion_preview", "buildIngestionReport", "source_metadata"]),
    "executive dashboard": (UI, ["Executive batch and provenance dashboard", "metric-ft-ready", "metric-provenance"]),
    "pilot metrics": (METRICS, ["fine_tune_ready_count", "hours_avoided", "simulated_case_study"]),
    "vertical demo": (BRIEF, ["Vertical demo: AI governance", "pharma evidence review", "model-risk"]),
    "pricing hypothesis": (BRIEF, ["Pricing hypothesis", "Two-week pilot", "Enterprise/API tier"]),
    "customer-facing docs": (BRIEF, ["One-page value proposition", "Customer-facing caveat", "Integration story"]),
    "sensitive data mode": (UI, ["sensitive-mode-toggle", "Sensitive mode", "redacted in sensitive data mode"]),
    "integration story": (BRIEF, ["GitHub Action", "Semantic Scholar", "Elicit"]),
    "case study": (BRIEF, ["CAPAS gated 1,000 candidate training claims", "230 rewritten", "110 rejected"])
}


def read(path: Path) -> str:
    if path.suffix == ".json":
        return json.dumps(json.loads(path.read_text(encoding="utf-8")), sort_keys=True)
    return path.read_text(encoding="utf-8")


def main() -> int:
    checks = []
    for name, (path, snippets) in REQUIRED.items():
        exists = path.exists()
        text = read(path) if exists else ""
        missing = [snippet for snippet in snippets if snippet not in text]
        checks.append({
            "check": name,
            "passed": exists and not missing,
            "path": str(path.relative_to(ROOT)),
            "missing": missing,
        })
    metrics = json.loads(METRICS.read_text(encoding="utf-8")) if METRICS.exists() else {}
    checks.append({
        "check": "case study rates match brief",
        "passed": metrics.get("rates", {}).get("rewritten") == 0.23
        and metrics.get("rates", {}).get("rejected") == 0.11
        and metrics.get("rates", {}).get("fine_tune_ready") == 0.04,
        "path": str(METRICS.relative_to(ROOT)),
        "missing": [],
    })
    passed = all(check["passed"] for check in checks)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps({"customer_product_assets_ready": passed, "checks": checks}, indent=2, sort_keys=True), encoding="utf-8")
    for check in checks:
        print(f"{check['check']}: {'ok' if check['passed'] else 'failed'}")
        if check["missing"]:
            print(f"  missing: {check['missing']}")
    print(f"customer_product_assets_ready: {passed}")
    print(f"report written to {REPORT}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
