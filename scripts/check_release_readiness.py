from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "outputs" / "release_readiness_report.json"


CHECKS = [
    ("package_manifest", ROOT / "pyproject.toml"),
    ("product_doc", ROOT / "PRODUCT.md"),
    ("readme", ROOT / "README.md"),
    ("ci_workflow", ROOT / ".github" / "workflows" / "ci.yml"),
    ("external_launch_plan", ROOT / "docs" / "EXTERNAL_MVP_LAUNCH_PLAN.md"),
    ("accept_example", ROOT / "examples" / "external_claim_accept.json"),
    ("rewrite_example", ROOT / "examples" / "external_claim_rewrite.json"),
    ("hold_example", ROOT / "examples" / "external_claim_hold.json"),
    ("invalid_example", ROOT / "examples" / "external_claim_invalid.json"),
    ("external_claim_schema", ROOT / "docs" / "schema" / "capas_claim_payload.schema.json"),
    ("external_input_schema_report", ROOT / "outputs" / "external_input_schema_report.json"),
    ("demo_report", ROOT / "outputs" / "capas_product_demo_report.md"),
    ("reviewer_packet_manifest", ROOT / "outputs" / "external_reviewer_packet" / "manifest.json"),
    ("profile_registration_manifest", ROOT / "outputs" / "profile_registration_packet" / "manifest.json"),
]


def _run(command: list[str]) -> tuple[int, str]:
    proc = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    return proc.returncode, (proc.stdout + proc.stderr).strip()


def _stable_detail(output: str) -> str:
    text = output[-4000:]
    text = text.replace(str(ROOT), "<CAPAS_ROOT>")
    text = re.sub(r"dist/\.tmp-[A-Za-z0-9_\\-]+", "dist/.tmp-<build>", text)
    return text


def main() -> int:
    results = []
    for name, path in CHECKS:
        results.append({
            "check": name,
            "path": str(path.relative_to(ROOT)),
            "passed": path.exists(),
            "detail": "exists" if path.exists() else "missing",
        })

    commands = [
        ("fresh_clone_install_smoke", [sys.executable, "benchmarks/verify_fresh_clone_install.py"]),
        ("external_input_schema", [sys.executable, "benchmarks/verify_external_input_schema.py"]),
        ("product_demo_acceptance", [sys.executable, "benchmarks/verify_capas_product_demo.py"]),
        ("product_validate", ["capas", "validate"]),
        ("wheel_build_no_isolation", [sys.executable, "-m", "build", "--wheel", "--no-isolation"]),
    ]
    for name, command in commands:
        code, output = _run(command)
        results.append({
            "check": name,
            "command": " ".join(command),
            "passed": code == 0,
            "detail": _stable_detail(output),
        })

    remote_code, remote_output = _run(["git", "remote", "-v"])
    has_remote = bool(remote_output.strip())
    results.append({
        "check": "git_remote_configured",
        "command": "git remote -v",
        "passed": has_remote,
        "detail": remote_output or "no git remote configured",
    })

    tag_code, tag_output = _run(["git", "tag", "--list", "v0.1.0"])
    has_tag = "v0.1.0" in tag_output.splitlines()
    results.append({
        "check": "release_tag_v0_1_0_exists",
        "command": "git tag --list v0.1.0",
        "passed": has_tag,
        "detail": tag_output or "tag not present",
    })

    gh_code, gh_output = _run(["gh", "auth", "status"])
    results.append({
        "check": "github_cli_authenticated",
        "command": "gh auth status",
        "passed": gh_code == 0,
        "detail": gh_output or "gh auth status produced no output",
    })

    passed = sum(1 for item in results if item["passed"])
    failed = len(results) - passed
    report = {
        "release_ready": failed == 0,
        "passed": passed,
        "failed": failed,
        "results": results,
        "non_degradation": (
            "GitHub publication is not complete until remote, auth, tag, CI run, "
            "and release artifact exist externally."
        ),
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    for item in results:
        status = "ok" if item["passed"] else "missing"
        print(f"{item['check']}: {status}")
    print(f"release_ready: {report['release_ready']}")
    print(f"report written to {REPORT_PATH}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
