from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import capas


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "outputs" / "standalone_pipeline_report.json"


CASES = [
    {
        "name": "accept_from_explicit_solver_log",
        "path": ROOT / "examples" / "standalone_pipeline_accept.json",
        "expected_extraction": "complete",
        "expected_alignment": "ALIGNED",
        "expected_final": "ACCEPT",
    },
    {
        "name": "semantic_scope_mismatch_blocks_accept",
        "path": ROOT / "examples" / "standalone_pipeline_semantic_hold.json",
        "expected_extraction": "complete",
        "expected_alignment": "MISALIGNED",
        "expected_final": "HOLD",
    },
    {
        "name": "universal_anchor_overclaim_rewrites",
        "path": ROOT / "examples" / "standalone_pipeline_anchor_rewrite.json",
        "expected_extraction": "complete",
        "expected_alignment": "MISALIGNED",
        "expected_final": "REWRITE",
    },
    {
        "name": "multisource_spans_are_auditable",
        "path": ROOT / "examples" / "standalone_pipeline_multisource.json",
        "expected_extraction": "complete",
        "expected_alignment": "ALIGNED",
        "expected_final": "ACCEPT",
    },
]


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _run_cli(*args: str) -> dict:
    proc = subprocess.run([sys.executable, "capas.py", *args], cwd=ROOT, text=True, capture_output=True)
    return {
        "command": " ".join([sys.executable, "capas.py", *args]),
        "returncode": proc.returncode,
        "stdout_tail": proc.stdout[-2000:],
        "stderr_tail": proc.stderr[-2000:],
    }


def main() -> int:
    checks: list[dict[str, object]] = []
    for case in CASES:
        payload = _load(case["path"])
        pipeline = capas.standalone_pipeline(payload)
        extraction = pipeline["extraction"]
        alignment = pipeline["semantic_alignment"]
        final_decision = pipeline["final_decision"]
        cli = _run_cli("pipeline", "--input", str(case["path"].relative_to(ROOT)), "--json")

        checks.append(
            {
                "check": case["name"],
                "passed": (
                    extraction["extraction_status"] == case["expected_extraction"]
                    and alignment["alignment_status"] == case["expected_alignment"]
                    and final_decision["verdict"] == case["expected_final"]
                    and all(
                        field in extraction["evidence_spans"]
                        for field in extraction["required_fields"]
                    )
                    and cli["returncode"] == 0
                ),
                "expected": {
                    "extraction_status": case["expected_extraction"],
                    "alignment_status": case["expected_alignment"],
                    "final_verdict": case["expected_final"],
                },
                "actual": {
                    "extraction_status": extraction["extraction_status"],
                    "extracted_evidence": extraction["extracted_evidence"],
                    "evidence_spans": extraction["evidence_spans"],
                    "retrieved_snippets": extraction["retrieved_snippets"],
                    "alignment_status": alignment["alignment_status"],
                    "alignment_issues": alignment["issues"],
                    "gate_verdict": pipeline["capas_gate_decision"]["verdict"],
                    "final_verdict": final_decision["verdict"],
                    "final_reason": final_decision["reason"],
                },
                "cli": cli,
            }
        )

    explicit_only = capas.extract_evidence(
        {
            "claim": {
                "id": "no_hidden_inference",
                "type": "exact_model_solution",
                "text": "The exact model solution is within tolerance.",
            },
            "source": {"kind": "paper_excerpt", "text": "The result looks excellent but no numeric error is declared."},
        }
    )
    checks.append(
        {
            "check": "extractor_does_not_infer_hidden_evidence",
            "passed": explicit_only["extraction_status"] == "none" and explicit_only["extracted_evidence"] == {},
            "actual": explicit_only,
        }
    )

    passed = all(bool(check["passed"]) for check in checks)
    report = {
        "standalone_pipeline_mvp_ready": passed,
        "scope": "local explicit extraction + deterministic semantic alignment + CAPAS gate",
        "non_claims": [
            "does not retrieve remote evidence",
            "does not parse PDFs",
            "does not perform broad scientific reasoning",
            "does not use an LLM at runtime",
        ],
        "checks": checks,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    for check in checks:
        print(f"{check['check']}: {'ok' if check['passed'] else 'failed'}")
    print(f"standalone_pipeline_mvp_ready: {passed}")
    print(f"report written to {REPORT}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
