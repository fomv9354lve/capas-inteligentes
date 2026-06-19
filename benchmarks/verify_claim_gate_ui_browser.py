from __future__ import annotations

import base64
import json
import shutil
import subprocess
import sys
import tempfile
import time
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
    ok("shared_payload_loaded", document.getElementById("input").value.includes("shared_claim"));
    ok("share_button_exists", document.getElementById("share-btn"));
    ok("export_button_exists", document.getElementById("export-btn"));
    ok("theme_button_exists", document.getElementById("theme-toggle"));
    ok("schema_version_badge_exists", document.getElementById("schema-version-badge")?.textContent.includes("schema v2"));
    ok("shared_payload_badge_visible", document.getElementById("shared-payload-badge")?.hidden === false);
    ok("help_button_exists", document.getElementById("help-btn"));
    ok("theme_button_initial_system", document.getElementById("theme-toggle").textContent === "System");
    toggleTheme();
    ok("theme_toggle_sets_light", document.documentElement.dataset.theme === "light");
    ok("theme_button_labels_light", document.getElementById("theme-toggle").textContent === "Light");
    toggleTheme();
    ok("theme_toggle_sets_dark", document.documentElement.dataset.theme === "dark");
    ok("theme_button_labels_dark", document.getElementById("theme-toggle").textContent === "Dark");
    toggleTheme();
    ok("theme_toggle_returns_system", !document.documentElement.dataset.theme);
    ok("theme_button_labels_system", document.getElementById("theme-toggle").textContent === "System");
    localStorage.removeItem("capas_decision_history_v1");
    document.getElementById("input").value = "";
    decide();
    ok("empty_input_message", document.getElementById("verdict-area").textContent.includes("Input required"));

    const helpButton = document.getElementById("help-btn");
    helpButton.focus();
    openHelpModal(helpButton);
    ok("help_modal_opens", document.getElementById("help-modal-backdrop").classList.contains("open"));
    ok("help_modal_has_dialog_role", document.getElementById("help-modal").getAttribute("role") === "dialog");
    ok("help_modal_has_aria_modal", document.getElementById("help-modal").getAttribute("aria-modal") === "true");
    ok("help_modal_focuses_inside", document.getElementById("help-modal").contains(document.activeElement));
    ok("help_modal_mentions_pipeline", document.getElementById("help-modal-backdrop").textContent.includes("retrieve"));
    ok("help_modal_lists_claim_type_requirements", document.querySelectorAll("#help-modal .claim-type-list li").length === 7);
    ok("help_modal_lists_schema_v2_financial_fields", document.getElementById("help-modal").textContent.includes("financial_metric_claim") && document.getElementById("help-modal").textContent.includes("metric_period_match"));
    ok("help_modal_lists_schema_v2_statistical_fields", document.getElementById("help-modal").textContent.includes("statistical_confidence") && document.getElementById("help-modal").textContent.includes("effect_direction_confirmed"));
    ok("help_modal_lists_schema_v2_reproducibility_fields", document.getElementById("help-modal").textContent.includes("reproducibility_check") && document.getElementById("help-modal").textContent.includes("independent_reproduction_pass"));
    ok("help_modal_documents_fine_tune_readiness", document.getElementById("help-modal").textContent.includes("fine_tune_ready") && document.getElementById("help-modal").textContent.includes("does not silently certify training data"));
    closeHelpModal();
    ok("help_modal_closes", !document.getElementById("help-modal-backdrop").classList.contains("open"));
    ok("help_modal_returns_focus_to_trigger", document.activeElement === helpButton);

    localStorage.setItem("capas_decision_history_v1", JSON.stringify([{
      id: '<img src=x onerror="window.__xss=true">',
      verdict: "HOLD",
      reason: "legacy audit artifact",
      payload: JSON.stringify({
        claim: { id: '<img src=x onerror="window.__xss=true">', type: "exact_model_solution", text: "legacy" },
        evidence: { abs_error: 0, tolerance: 0.001 }
      }),
      decision: { verdict: "HOLD" },
      timestamp: new Date().toISOString()
    }]));
    decisionHistory = loadHistory();
    ok("legacy_history_sanitized_in_memory", decisionHistory.length === 0);
    ok("legacy_history_sanitized_storage", JSON.parse(localStorage.getItem("capas_decision_history_v1") || "[]").length === 0);

    buildDraft();
    ok("draft_status_is_amber", document.getElementById("json-status").className.includes("draft"));
    ok("draft_not_decided", document.getElementById("verdict-area").textContent.includes("Draft built, not decided"));

    loadSample("REWRITE");
    ok("rewrite_verdict", document.querySelector(".verdict-badge.REWRITE"));
    ok("rewrite_diff_visible", document.querySelector(".rewrite-diff"));
    ok("syntax_highlight_visible", document.querySelector("#output .json-key"));

    loadSample("REJECT");
    ok("reject_verdict", document.querySelector(".verdict-badge.REJECT"));
    ok("reject_output_json", document.getElementById("output").textContent.includes('"verdict": "REJECT"'));

    loadSample("INVALID");
    ok("invalid_schema_holds", document.querySelector(".verdict-badge.HOLD"));
    ok("invalid_output_json", document.getElementById("output").textContent.includes('"schema_errors"'));

    document.getElementById("input").value = JSON.stringify([samples.ACCEPT, samples.REJECT], null, 2);
    decideBatch();
    ok("batch_summary_visible", document.getElementById("verdict-area").textContent.includes("Batch summary"));
    ok("batch_progress_visible", document.querySelector(".batch-progress-fill"));
    ok("batch_progress_label_visible", document.getElementById("verdict-area").textContent.includes("claims processed"));
    ok("batch_per_item_table_visible", document.querySelectorAll(".batch-row").length === 2);
    ok("batch_per_item_reason_visible", document.querySelector(".batch-row-reason")?.textContent.length > 0);
    ok("batch_output_json", document.getElementById("output").textContent.includes('"batch_mode": "decide"'));
    ok("batch_schema_version", document.getElementById("output").textContent.includes('"schema_version": "capas-claim-payload-v2"'));
    document.getElementById("input").value = JSON.stringify(samples.ACCEPT, null, 2);
    decideBatch();
    ok("batch_single_object_autowrap", document.getElementById("output").textContent.includes('"item_count": 1'));

    document.getElementById("input").value = JSON.stringify({
      claim: { id: "stat_sig", type: "statistical_confidence", text: "The effect is statistically significant at alpha 0.05." },
      evidence: { p_value: 0.01, alpha: 0.05, effect_direction_confirmed: true }
    });
    decide();
    ok("statistical_confidence_accept", document.querySelector(".verdict-badge.ACCEPT"));
    document.getElementById("input").value = JSON.stringify({
      claim: { id: "repro_rw", type: "reproducibility_check", text: "The result is independently reproducible." },
      evidence: { artifact_available: true, independent_reproduction_pass: false }
    });
    decide();
    ok("reproducibility_check_rewrite", document.querySelector(".verdict-badge.REWRITE"));
    document.getElementById("input").value = JSON.stringify({
      claim: { id: "finance_accept", type: "financial_metric_claim", text: "The reported metric matches the reference for the same period." },
      evidence: { reported_value: 101.2, reference_value: 101.0, tolerance: 0.5, metric_period_match: true }
    });
    decide();
    ok("financial_metric_claim_accept", document.querySelector(".verdict-badge.ACCEPT"));

    const firstHistory = document.querySelector(".history-item");
    ok("history_item_exists", firstHistory);
    if (firstHistory) firstHistory.click();
    ok("history_restore_keeps_output", document.getElementById("output").textContent.includes("verdict"));
    ok("history_timestamp_visible", Boolean(document.querySelector(".history-ts")?.textContent.trim()));
    ok("history_delete_button_visible", Boolean(document.querySelector(".history-delete")));
    const historyLengthBeforeDelete = decisionHistory.length;
    document.querySelector(".history-delete")?.click();
    ok("history_delete_removes_one_entry", decisionHistory.length === historyLengthBeforeDelete - 1);

    document.getElementById("output").scrollTop = 999;
    decide();
    ok("output_scroll_resets_to_top", document.getElementById("output").scrollTop === 0);
    ok("share_button_privacy_label", document.getElementById("share-btn").getAttribute("aria-label").includes("payload is embedded"));

    clearHistory();
    ok("clear_history_empties_list", document.getElementById("history-count").textContent.includes("0/50"));

    if (window.innerWidth <= 560) {
      const gridColumns = getComputedStyle(document.querySelector(".grid")).gridTemplateColumns.trim().split(/\s+/);
      const actionColumns = getComputedStyle(document.querySelector(".action-row")).gridTemplateColumns.trim().split(/\s+/);
      ok("mobile_viewport_active", window.innerWidth <= 560, String(window.innerWidth));
      ok("mobile_grid_single_column", gridColumns.length === 1, gridColumns.join("|"));
      ok("mobile_action_row_single_column", actionColumns.length === 1, actionColumns.join("|"));
      ok("mobile_topbar_wraps_actions", document.querySelector(".topbar-actions").getBoundingClientRect().top > document.querySelector(".topbar-left").getBoundingClientRect().top);
      ok("mobile_output_within_viewport", document.getElementById("output").getBoundingClientRect().right <= window.innerWidth);
      openHelpModal(helpButton);
      const modalRect = document.getElementById("help-modal").getBoundingClientRect();
      ok("mobile_modal_fits_width", modalRect.left >= 0 && modalRect.right <= window.innerWidth);
      ok("mobile_modal_fits_height", modalRect.top >= 0 && modalRect.bottom <= window.innerHeight);
      closeHelpModal();
    }

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
            shared_payload = {
                "claim": {
                    "id": "shared_claim",
                    "type": "exact_model_solution",
                    "text": "The shared model solution is within tolerance.",
                },
                "evidence": {"abs_error": 0.0, "tolerance": 0.001},
            }
            encoded = base64.urlsafe_b64encode(
                json.dumps(shared_payload, sort_keys=True).encode("utf-8")
            ).decode("ascii").rstrip("=")
            def run_chrome(name: str, *extra_args: str) -> subprocess.CompletedProcess[str]:
                command = [
                    chrome,
                    "--headless=new",
                    "--disable-gpu",
                    "--no-sandbox",
                    "--dump-dom",
                    "--virtual-time-budget=2000",
                    *extra_args,
                    f"{harness_path.as_uri()}?p={encoded}",
                ]
                last_proc: subprocess.CompletedProcess[str] | None = None
                for attempt in range(3):
                    last_proc = subprocess.run(
                        command,
                        text=True,
                        capture_output=True,
                        timeout=20,
                    )
                    if last_proc.returncode == 0 and last_proc.stdout:
                        return last_proc
                    time.sleep(0.2 * (attempt + 1))
                assert last_proc is not None
                return last_proc

            proc = run_chrome("desktop")
            mobile_proc = run_chrome("mobile", "--window-size=390,844", "--force-device-scale-factor=1")
        desktop_passed = proc.returncode == 0 and 'data-capas-e2e="PASS"' in proc.stdout
        mobile_passed = mobile_proc.returncode == 0 and 'data-capas-e2e="PASS"' in mobile_proc.stdout
        passed = desktop_passed and mobile_passed
        checks.append({"check": "chrome_available", "passed": True, "detail": chrome})
        checks.append({
            "check": "browser_e2e_desktop_pass",
            "passed": desktop_passed,
            "detail": (
                "desktop browser checks passed"
                if desktop_passed
                else f"returncode={proc.returncode}; stderr={proc.stderr.strip()}; stdout_tail={proc.stdout[-4000:]}"
            ),
        })
        checks.append({
            "check": "browser_e2e_mobile_pass",
            "passed": mobile_passed,
            "detail": (
                "mobile browser checks passed"
                if mobile_passed
                else f"returncode={mobile_proc.returncode}; stderr={mobile_proc.stderr.strip()}; stdout_tail={mobile_proc.stdout[-4000:]}"
            ),
        })

    report = {
        "claim_gate_browser_e2e_ready": passed,
        "checks": checks,
        "scope": "Runs the generated static UI in real headless Chrome/Chromium desktop and mobile viewports and exercises shared URLs, Build Draft, ACCEPT/REWRITE/REJECT/HOLD paths, INVALID schema output, syntax highlighting, history restore, clear history, and responsive batch/modal layout.",
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
