from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REVIEWER_MANIFEST = ROOT / "outputs" / "external_reviewer_packet" / "manifest.json"
PROFILE_MANIFEST = ROOT / "outputs" / "profile_registration_packet" / "manifest.json"
RELEASE_REPORT = ROOT / "outputs" / "release_readiness_report.json"

EXPECTED_RELEASE_BLOCKERS = {
    "git_remote_configured",
    "release_tag_v0_1_0_exists",
    "github_cli_authenticated",
}


def _run_allow_fail(command: list[str]) -> None:
    subprocess.run(command, cwd=ROOT, check=False)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    _run_allow_fail([sys.executable, "scripts/prepare_external_reviewer_packet.py"])
    _run_allow_fail([sys.executable, "scripts/prepare_profile_registration_packet.py"])
    _run_allow_fail([sys.executable, "scripts/check_release_readiness.py"])

    reviewer = _load(REVIEWER_MANIFEST)
    profile = _load(PROFILE_MANIFEST)
    release = _load(RELEASE_REPORT)

    assert reviewer["status"] == "ready"
    assert not reviewer["missing"]
    assert profile["status"] == "ready"
    assert not profile["missing"]
    assert release["release_ready"] is False

    failed_checks = {
        item["check"]
        for item in release["results"]
        if item["passed"] is False
    }
    assert failed_checks == EXPECTED_RELEASE_BLOCKERS, failed_checks

    print("verify_external_mvp_readiness passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
