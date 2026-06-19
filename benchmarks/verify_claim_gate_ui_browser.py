from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
UI_PATH = ROOT / "outputs" / "capas_claim_gate_ui.html"
REPORT_PATH = ROOT / "outputs" / "claim_gate_ui_browser_report.json"


def _chrome_binary() -> str | None:
    candidates = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "google-chrome",
        "google-chrome-stable",
        "chromium",
        "chromium-browser",
    ]
    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            return str(path)
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    return None


HARNESS = r"""
<script>
(function () {
  const checks = [];
  function ok(name, condition, detail) {
    checks.push({ name, passed: Boolean(condition), detail: detail || "" });
  }
  try {
    localStorage.removeItem("capas_decision_history_v1");
    document.getElementById("input").value = "";
    decide();
    ok("empty_input_message", document.getElementById("verdict-area").textContent.includes("Input required"));

    buildDraft();
    ok("draft_status_is_amber", document.getElementById("json-status").className.includes("draft"));
    ok("draft_not_decided", document.getElementById("verdict-area").textContent.includes("Draft built, not decided"));

    loadSample("REWRITE");
    ok("rewrite_verdict", document.querySelector(".verdict-badge.REWRITE"));
    ok("rewrite_diff_visible", document.querySelector(".rewrite-diff"));
    ok("syntax_highlight_visible", document.querySelector("#output .json-key"));

    const firstHistory = document.querySelector(".history-item");
    ok("history_item_exists", firstHistory);
    if (firstHistory) firstHistory.click();
    ok("history_restore_keeps_output", document.getElementById("output").textContent.includes("verdict"));

    const failures = checks.filter((check) => !check.passed);
    const pre = document.createElement("pre");
    pre.id = "capas-e2e-results";
    pre.textContent = JSON.stringify({ passed: failures.length === 0, checks }, null, 2);
    document.body.appendChild(pre);
    document.body.setAttribute("data-capas-e2e", failures.length === 0 ? "PASS" : "FAIL");
  } catch (error) {
    const pre = document.createElement("pre");
    pre.id = "capas-e2e-results";
    pre.textContent = JSON.stringify({ passed: false, error: String(error), checks }, null, 2);
    document.body.appendChild(pre);
    document.body.setAttribute("data-capas-e2e", "FAIL");
  }
})();
</script>
"""


def main() -> int:
    subprocess.run([sys.executable, "capas.py", "ui"], cwd=ROOT, check=True)
    chrome = _chrome_binary()
    checks = []
    if not chrome:
        checks.append({"check": "chrome_available", "passed": False, "detail": "Chrome/Chromium binary not found"})
        passed = False
    else:
        html = UI_PATH.read_text(encoding="utf-8").replace("</body>", HARNESS + "\n</body>")
        with tempfile.TemporaryDirectory() as tmpdir:
            harness_path = Path(tmpdir) / "capas-e2e.html"
            harness_path.write_text(html, encoding="utf-8")
            proc = subprocess.run(
                [
                    chrome,
                    "--headless=new",
                    "--disable-gpu",
                    "--no-sandbox",
                    "--dump-dom",
                    "--virtual-time-budget=2000",
                    harness_path.as_uri(),
                ],
                text=True,
                capture_output=True,
                timeout=20,
            )
        passed = proc.returncode == 0 and 'data-capas-e2e="PASS"' in proc.stdout
        checks.append({"check": "chrome_available", "passed": True, "detail": chrome})
        checks.append({
            "check": "browser_e2e_pass",
            "passed": passed,
            "detail": (proc.stderr or proc.stdout[-1000:]).strip(),
        })

    report = {
        "claim_gate_browser_e2e_ready": passed,
        "checks": checks,
        "scope": "Runs the generated static UI in a real headless Chrome/Chromium process and exercises Build Draft, Decide, rewrite diff, syntax highlighting, and history restore.",
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    for check in checks:
        print(f"{check['check']}: {'ok' if check['passed'] else 'failed'}")
    print(f"claim_gate_browser_e2e_ready: {passed}")
    print(f"report written to {REPORT_PATH}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
