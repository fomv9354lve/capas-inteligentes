from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import capas


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "docs" / "schema" / "capas_claim_payload.schema.json"
REPORT_PATH = ROOT / "outputs" / "external_input_schema_report.json"


VALID_EXAMPLES = [
    ROOT / "examples" / "external_claim_accept.json",
    ROOT / "examples" / "external_claim_rewrite.json",
    ROOT / "examples" / "external_claim_hold.json",
]
INVALID_EXAMPLE = ROOT / "examples" / "external_claim_invalid.json"


def _run(command: list[str]) -> dict[str, object]:
    proc = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    return {
        "command": " ".join(command),
        "returncode": proc.returncode,
        "stdout_tail": proc.stdout[-2000:],
        "stderr_tail": proc.stderr[-2000:],
        "passed": proc.returncode == 0,
    }


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    published_schema = _load(SCHEMA_PATH)
    generated_schema = capas.external_claim_payload_schema()
    checks: list[dict[str, object]] = [
        {
            "check": "published_schema_matches_cli_schema",
            "passed": published_schema == generated_schema,
            "detail": str(SCHEMA_PATH.relative_to(ROOT)),
        }
    ]

    for path in VALID_EXAMPLES:
        payload = _load(path)
        errors = capas.validate_external_payload(payload)
        result = _run([sys.executable, "capas.py", "check-input", "--input", str(path.relative_to(ROOT))])
        checks.append({
            "check": f"valid_example:{path.name}",
            "passed": not errors and result["passed"],
            "errors": errors,
            "cli": result,
        })

    invalid_payload = _load(INVALID_EXAMPLE)
    invalid_errors = capas.validate_external_payload(invalid_payload)
    invalid_cli = _run([sys.executable, "capas.py", "check-input", "--input", str(INVALID_EXAMPLE.relative_to(ROOT))])
    invalid_decision = capas.decide_external_claim(invalid_payload)
    checks.append({
        "check": f"invalid_example:{INVALID_EXAMPLE.name}",
        "passed": bool(invalid_errors) and not invalid_cli["passed"] and invalid_decision["verdict"] == "HOLD",
        "errors": invalid_errors,
        "cli": invalid_cli,
        "decision": invalid_decision,
    })

    passed = all(bool(check["passed"]) for check in checks)
    report = {
        "external_input_schema_ready": passed,
        "schema": str(SCHEMA_PATH.relative_to(ROOT)),
        "valid_examples": [str(path.relative_to(ROOT)) for path in VALID_EXAMPLES],
        "invalid_example": str(INVALID_EXAMPLE.relative_to(ROOT)),
        "checks": checks,
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    for check in checks:
        status = "ok" if check["passed"] else "failed"
        print(f"{check['check']}: {status}")
    print(f"external_input_schema_ready: {passed}")
    print(f"report written to {REPORT_PATH}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
