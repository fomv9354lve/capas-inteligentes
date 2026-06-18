from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "outputs" / "fresh_clone_install_report.json"


def _stable_text(text: str, tmp_root: Path | None = None) -> str:
    stable = text.replace(str(ROOT), "<CAPAS_ROOT>")
    if tmp_root is not None:
        stable = stable.replace(str(tmp_root.resolve()), "<TMP_CAPAS_FRESH_CLONE>")
        stable = stable.replace(str(tmp_root), "<TMP_CAPAS_FRESH_CLONE>")
        stable = stable.replace(f"/private{tmp_root}", "<TMP_CAPAS_FRESH_CLONE>")
        stable = stable.replace(f"/private{tmp_root.resolve()}", "<TMP_CAPAS_FRESH_CLONE>")
    stable = re.sub(r"sha256=[0-9a-f]{64}", "sha256=<wheel-hash>", stable)
    stable = re.sub(r"size=\d+", "size=<wheel-size>", stable)
    stable = re.sub(
        r"Found existing installation: capas-claim-gate [0-9]+(?:\.[0-9]+)*",
        "Found existing installation: capas-claim-gate <existing-version>",
        stable,
    )
    stable = re.sub(
        r"/(?:private/)?var/folders/[^\s]+/pip-ephem-wheel-cache-[^\s]+",
        "<PIP_EPHEM_WHEEL_CACHE>",
        stable,
    )
    return stable


def _stable_command(command: list[str], tmp_root: Path | None = None) -> str:
    return " ".join(_stable_text(part, tmp_root=tmp_root) for part in command)


def _run(
    command: list[str],
    cwd: Path,
    env: dict[str, str] | None = None,
    tmp_root: Path | None = None,
) -> dict[str, object]:
    try:
        proc = subprocess.run(command, cwd=cwd, text=True, capture_output=True, env=env)
        return {
            "command": _stable_command(command, tmp_root=tmp_root),
            "returncode": proc.returncode,
            "stdout_tail": _stable_text(proc.stdout[-2000:], tmp_root=tmp_root),
            "stderr_tail": _stable_text(proc.stderr[-2000:], tmp_root=tmp_root),
            "passed": proc.returncode == 0,
        }
    except FileNotFoundError as exc:
        return {
            "command": _stable_command(command, tmp_root=tmp_root),
            "returncode": 127,
            "stdout_tail": "",
            "stderr_tail": _stable_text(str(exc), tmp_root=tmp_root),
            "passed": False,
        }


def main() -> int:
    tmp_root = Path(tempfile.mkdtemp(prefix="capas-fresh-clone-"))
    results: list[dict[str, object]] = []
    try:
        clone_dir = tmp_root / "repo"
        venv_dir = tmp_root / "venv"

        ignore = shutil.ignore_patterns(
            ".git",
            "__pycache__",
            ".pytest_cache",
            ".ruff_cache",
            ".mypy_cache",
            ".venv",
            "venv",
            "build",
            "dist",
            "*.egg-info",
            "*.pyc",
        )
        shutil.copytree(ROOT, clone_dir, ignore=ignore)
        results.append({
            "command": "copy current source tree to <TMP_CAPAS_FRESH_CLONE>/repo",
            "returncode": 0,
            "stdout_tail": "",
            "stderr_tail": "",
            "passed": True,
        })

        results.append(_run([sys.executable, "-m", "venv", "--system-site-packages", str(venv_dir)], tmp_root, tmp_root=tmp_root))
        if not results[-1]["passed"]:
            raise AssertionError("venv creation failed")

        python = venv_dir / "bin" / "python"
        capas = venv_dir / "bin" / "capas"
        env = os.environ.copy()
        env["PATH"] = f"{venv_dir / 'bin'}{os.pathsep}{env.get('PATH', '')}"

        results.append(
            _run(
                [str(python), "-m", "pip", "install", "--no-deps", "--no-build-isolation", "-e", "."],
                clone_dir,
                tmp_root=tmp_root,
            )
        )
        results.append(_run([str(capas), "schema"], clone_dir, env=env, tmp_root=tmp_root))
        results.append(_run([str(capas), "check-input", "--input", "examples/external_claim_accept.json"], clone_dir, env=env, tmp_root=tmp_root))
        results.append(_run([str(capas), "demo"], clone_dir, env=env, tmp_root=tmp_root))
        results.append(_run([str(capas), "decide", "--input", "examples/external_claim_rewrite.json"], clone_dir, env=env, tmp_root=tmp_root))
        results.append(_run([str(capas), "validate"], clone_dir, env=env, tmp_root=tmp_root))

        passed = all(item["passed"] for item in results)
        report = {
            "fresh_clone_install_smoke": passed,
            "scope": (
                "Local fresh source checkout plus editable install in a temporary venv using system "
                "site packages, --no-deps, and --no-build-isolation. This proves package entrypoint/root "
                "discovery outside the working tree; it does not prove PyPI dependency "
                "resolution from a blank machine."
            ),
            "results": results,
        }
        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

        for item in results:
            status = "ok" if item["passed"] else "failed"
            print(f"{item['command']}: {status}")
        print(f"fresh_clone_install_smoke: {passed}")
        print(f"report written to {REPORT_PATH}")
        return 0 if passed else 1
    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
