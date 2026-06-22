from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRODUCT = ROOT / "docs" / "index.html"
BRIEF = ROOT / "docs" / "CUSTOMER_READY_BRIEF.md"
BRIEF_HTML = ROOT / "docs" / "customer-brief.html"
DECK = ROOT / "docs" / "PARTNER_DECK.md"
PACKET_HTML = ROOT / "docs" / "pilot-packet.html"
METRICS = ROOT / "outputs" / "pilot_metrics.json"
UI = ROOT / "outputs" / "capas_claim_gate_ui.html"
REPORT = ROOT / "outputs" / "customer_product_assets_report.json"
SCHEMA_REGISTRY = ROOT / "docs" / "SCHEMA_REGISTRY.md"
ENTERPRISE_PACK = ROOT / "docs" / "ENTERPRISE_INTEGRATION_PACK.md"
PROVENANCE_OPS = ROOT / "docs" / "PROVENANCE_REGISTRY_OPERATIONS.md"
SECURITY_APPENDIX = ROOT / "docs" / "SECURITY_COMPLIANCE_APPENDIX.md"
PILOT_ROI = ROOT / "docs" / "PILOT_ROI_BUSINESS_CASE.md"
PAPER_CONNECTORS = ROOT / "docs" / "PAPER_INGESTION_CONNECTORS.md"
CLAIM_DRIFT_VALIDATION = ROOT / "docs" / "CLAIM_DRIFT_VALIDATION_PROTOCOL.md"
LOGO = ROOT / "docs" / "capas-transition-network-logo.svg"
LOGO_HTML = ROOT / "docs" / "gemini-code-1781935819867.html"
THREE_JS = ROOT / "docs" / "vendor" / "three-r128" / "three.min.js"
ORBIT_CONTROLS = ROOT / "docs" / "vendor" / "three-r128" / "OrbitControls.js"
CANONICAL_SCHEMA = ROOT / "docs" / "schema" / "v3" / "capas_claim_payload.schema.json"
HF_EXAMPLE = ROOT / "examples" / "huggingface_dataset_capas_metadata.json"
LABEL_STUDIO_EXAMPLE = ROOT / "examples" / "label_studio_capas_task.json"
ARGILLA_EXAMPLE = ROOT / "examples" / "argilla_capas_record.json"


REQUIRED = {
    "landing page with narrative": (PRODUCT, ["Deterministic Scientific Claim Gate", "Admissibility", "ACCEPT, REWRITE, REJECT, or HOLD", "No language model in the verdict", "Where it Lives", "Verdict Reference", "The Core", "Krenn-IQ", "One mechanism. 10 domains. 26 gates", "does not certify scientific truth", "contamination cascade", "should this have been said"]),
    "scalable transition-network logo": (LOGO, ["viewBox=\"0 0 128 128\"", "CAPAS transition network logo", "cyan licensed paths", "magenta drift paths"]),
    "landing page logo placement": (PRODUCT, ["class=\"bg-logo\"", "src=\"logo_kreniq_volum_trico.html\"", "class=\"bg-veil\""]),
    "exact dynamic html logo": (LOGO_HTML, ["Kreniq - Red de Transiciones 3D", "vendor/three-r128/three.min.js", "vendor/three-r128/OrbitControls.js", "new THREE.Scene()", "THREE.OrbitControls", "COLOR_EDGE_CYAN = 0x00E5FF", "COLOR_EDGE_MAGENTA = 0xE61062", "TOTAL_NODES = 36", "THREE.TubeGeometry", "camera.position.set(0, 10, 80)", "matrixGroup.position.y = Math.sin(Date.now() * 0.001) * 1.5"]),
    "local three.js dependency": (THREE_JS, ["Three.js Authors", "THREE={}"]),
    "local orbit controls dependency": (ORBIT_CONTROLS, ["THREE.OrbitControls", "OrbitControls"]),
    "gate app header without discarded logo": (UI, ["aria-label=\"CAPAS Claim Gate\"", "krenniq-logo.png", "class=\"nav-logo\"", "Gate App", "class=\"nav-cta\"", "Audit"]),
    "landing page screenshots": (PRODUCT, ["Recent Gate Decisions", "SCHEMA V3", "statistical_confidence"]),
    "product business case": (PRODUCT, ["Verdict Reference", "Where it Lives", "Use Cases", "audit_hash", "claim_id", "evidence_contract", "reviewer_action"]),
    "designed methodology page": (BRIEF_HTML, ["Methodology", "Deterministic claim ", "Reproducible engine benchmark", "Disclaimers"]),
    "designed pilot packet": (PACKET_HTML, ["Pilot Packet", "Two-week", "Roles", "Success criteria", "Governance", "disclaimer"]),
    "guided no-code form": (UI, ["CAPAS workflow", "Guided Claim Builder", "Evidence contract", "builder-preview", "buildGuidedPayload", "Build guided payload", "evidence field for"]),
    "paper text ingestion": (UI, ["Candidate extraction aid", "extractCandidateClaims", "candidate claims extracted from paper or text", "Evidence spans", "evidence_spans", "parseBooleanEvidenceValue", "numberPattern", "parseFloat"]),
    "human in the loop": (UI, ["Confirm & build payload", "human_confirmed", "Human confirmation gate", "CAPAS will not decide unconfirmed candidates"]),
    "local metadata adapter": (UI, ["normalizeLocalMetadataExport", "local_semantic_scholar_pubmed_metadata_adapter", "DOI / external ID", "Paper title"]),
    "paper ingestion report": (UI, ["paper_ingestion_preview", "buildIngestionReport", "source_metadata"]),
    "executive dashboard": (UI, ["Executive batch and provenance dashboard", "metric-ft-ready", "metric-provenance", "Batch training readiness preview"]),
    "pilot roi calculator": (UI, ["Pilot capacity model", "updateRoiCalculator", "roi-hours", "review capacity planning estimate"]),
    "workflow view": (UI, ["Claim admissibility workflow", "Select mode", "Inspect decision"]),
    "pilot metrics": (METRICS, ["fine_tune_ready_count", "hours_avoided", "capacity_value_avoided_usd", "simulated_case_study"]),
    "vertical demo": (BRIEF, ["Vertical demo: AI governance", "pharma evidence review", "model-risk"]),
    "executive so what": (BRIEF, ["Executive so what", "Training Data Assurance for Scientific AI", "Reduce senior-review hours"]),
    "roi assumptions": (BRIEF, ["ROI calculator assumptions", "capacity value", "USD 180/hour"]),
    "pricing hypothesis": (BRIEF, ["Pricing hypothesis", "Two-week pilot", "Enterprise/API tier"]),
    "customer-facing docs": (BRIEF, ["One-page value proposition", "Customer-facing caveat", "Integration story"]),
    "sensitive data mode": (UI, ["sensitive-mode-toggle", "Sensitive mode", "redacted in sensitive data mode"]),
    "integration story": (BRIEF, ["GitHub Action", "Semantic Scholar", "Elicit"]),
    "case study": (BRIEF, ["CAPAS gated 1,000 structured evidence records", "10,000 structured payload records", "230 rewritten", "110 rejected"]),
    "partner deck": (DECK, ["Training Data Assurance for Scientific AI", "two-week pilot", "ROI model", "Buyer ask"]),
    "canonical schema registry": (SCHEMA_REGISTRY, ["Canonical URL", "capas-claim-payload-v3", "schema/v3/capas_claim_payload.schema.json"]),
    "canonical schema file": (CANONICAL_SCHEMA, ["https://fomv9354lve.github.io/capas-inteligentes/schema/v3/capas_claim_payload.schema.json", "capas-claim-payload-v3"]),
    "enterprise integration pack": (ENTERPRISE_PACK, ["GET /decisions", "POST /provenance-check", "Label Studio", "Hugging Face Datasets"]),
    "provenance registry operations": (PROVENANCE_OPS, ["review packet SHA-256", "witness ID in registry", "RO-Crate metadata hash"]),
    "security compliance appendix": (SECURITY_APPENDIX, ["Optional bearer token", "Workspace-scoped JSONL audit log", "training-data provenance"]),
    "pilot ROI business case": (PILOT_ROI, ["1,000 structured records", "417 hours", "USD 83,400", "10,000 structured CAPAS payload records"]),
    "paper ingestion connectors": (PAPER_CONNECTORS, ["browser preview", "local CLI pipeline", "Semantic Scholar/PubMed-like metadata"]),
    "claim drift validation protocol": (CLAIM_DRIFT_VALIDATION, ["claim drift occurs often enough", "drift_rate", "rewrite_to_accept_conversion_rate", "Claim contamination register", "Non-Claims"]),
    "huggingface metadata example": (HF_EXAMPLE, ["capas_schema_version", "capas_decision_json"]),
    "label studio handoff example": (LABEL_STUDIO_EXAMPLE, ["claim_type", "source_span", "capas_schema_version"]),
    "argilla handoff example": (ARGILLA_EXAMPLE, ["required_evidence_fields", "reproducibility_check"])
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
        and metrics.get("rates", {}).get("fine_tune_ready") == 0.04
        and metrics.get("stress_test_record_count") == 10000,
        "path": str(METRICS.relative_to(ROOT)),
        "missing": [],
    })
    checks.append({
        "check": "roi model matches brief",
        "passed": metrics.get("review_economics", {}).get("capacity_value_avoided_usd") == 75060
        and metrics.get("review_economics", {}).get("expert_hourly_rate_usd") == 180,
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
