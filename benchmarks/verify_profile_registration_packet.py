from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "outputs" / "profile_registration_readiness_report.json"

REQUIRED_FILES = {
    "profile_doc": ROOT / "docs" / "profile" / "CAPAS_PHYSICAL_EVIDENCE_PROFILE.md",
    "jsonld_context": ROOT / "docs" / "profile" / "capas-physical-evidence-context.jsonld",
    "registration_metadata": ROOT / "docs" / "profile" / "capas-profile-registration.json",
    "issue_template": ROOT / "docs" / "profile" / "RO_CRATE_PROFILE_REGISTRATION_ISSUE.md",
    "alignment_doc": ROOT / "docs" / "WORKFLOW_RUN_RO_CRATE_ALIGNMENT.md",
    "example_crate": ROOT / "benchmarks" / "ro_crates" / "trace_039" / "ro-crate-metadata.json",
    "local_validator": ROOT / "benchmarks" / "validate_capas_profile.py",
    "packet_manifest": ROOT / "outputs" / "profile_registration_packet" / "manifest.json",
}

REQUIRED_CONTEXT_TERMS = [
    "PhysicalEvidence",
    "evidenceStatus",
    "physicalEvidenceLevel",
    "verificationIndependence",
    "referenceTruth",
    "absError",
    "boundScope",
    "claimScope",
    "anchorMode",
    "universalAnchorPass",
    "localPropertyTestsPass",
]

REQUIRED_PACKET_FILES = [
    "CAPAS_PHYSICAL_EVIDENCE_PROFILE.md",
    "capas-physical-evidence-context.jsonld",
    "capas-profile-registration.json",
    "RO_CRATE_PROFILE_REGISTRATION_ISSUE.md",
    "WORKFLOW_RUN_RO_CRATE_ALIGNMENT.md",
    "trace_039-ro-crate-metadata.json",
    "validate_capas_profile.py",
    "REGISTRATION_REQUEST.md",
]

NOT_REGISTERED_PROFILE_STATUSES = {
    "local_draft_not_registered",
    "external_review_requested_not_registered",
}


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    results: list[dict] = []

    for name, path in REQUIRED_FILES.items():
        results.append({
            "check": name,
            "path": str(path.relative_to(ROOT)),
            "passed": path.exists(),
            "detail": "exists" if path.exists() else "missing",
        })

    metadata = _load_json(REQUIRED_FILES["registration_metadata"]) if REQUIRED_FILES["registration_metadata"].exists() else {}
    results.append({
        "check": "profile_status_is_not_registered",
        "passed": metadata.get("profile_status") in NOT_REGISTERED_PROFILE_STATUSES,
        "detail": metadata.get("profile_status"),
    })
    results.append({
        "check": "registration_completion_rule_external",
        "passed": "external" in str(metadata.get("completion_rule", "")).lower(),
        "detail": metadata.get("completion_rule", ""),
    })

    context = _load_json(REQUIRED_FILES["jsonld_context"]) if REQUIRED_FILES["jsonld_context"].exists() else {}
    terms = context.get("@context", {})
    missing_terms = [term for term in REQUIRED_CONTEXT_TERMS if term not in terms]
    results.append({
        "check": "context_has_capas_evidence_terms",
        "passed": not missing_terms,
        "detail": {"missing_terms": missing_terms},
    })

    manifest = _load_json(REQUIRED_FILES["packet_manifest"]) if REQUIRED_FILES["packet_manifest"].exists() else {}
    copied = set(manifest.get("copied", []))
    missing_packet_files = [name for name in REQUIRED_PACKET_FILES if name not in copied]
    results.append({
        "check": "packet_manifest_ready",
        "passed": manifest.get("status") == "ready" and not manifest.get("missing"),
        "detail": {"status": manifest.get("status"), "missing": manifest.get("missing", [])},
    })
    results.append({
        "check": "packet_contains_registration_artifacts",
        "passed": not missing_packet_files,
        "detail": {"missing_packet_files": missing_packet_files},
    })
    results.append({
        "check": "packet_declares_not_formally_registered",
        "passed": manifest.get("formal_registration_complete") is False,
        "detail": {
            "formal_registration_complete": manifest.get("formal_registration_complete"),
            "profile_status": manifest.get("profile_status"),
        },
    })

    passed = sum(1 for item in results if item["passed"])
    failed = len(results) - passed
    report = {
        "profile_registration_packet_ready": failed == 0,
        "formal_profile_registered": False,
        "passed": passed,
        "failed": failed,
        "results": results,
        "non_degradation": (
            "This readiness gate proves only that a registration packet is locally "
            "complete. It does not prove formal RO-Crate profile registration."
        ),
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    for item in results:
        status = "ok" if item["passed"] else "missing"
        print(f"{item['check']}: {status}")
    print(f"profile_registration_packet_ready: {report['profile_registration_packet_ready']}")
    print(f"formal_profile_registered: {report['formal_profile_registered']}")
    print(f"report written to {REPORT_PATH}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
