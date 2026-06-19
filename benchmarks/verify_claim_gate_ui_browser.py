from __future__ import annotations

import base64
import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import capas


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
  function versioned(payload) {
    return Object.assign({ schema_version: capasSchemaVersion }, payload);
  }
  try {
    ok("shared_payload_loaded", document.getElementById("input").value.includes("shared_claim"));
    ok("share_button_exists", document.getElementById("share-btn"));
    ok("export_button_exists", document.getElementById("export-btn"));
    ok("product_hero_exists", document.querySelector(".product-hero")?.textContent.includes("deterministic quality gate"));
    ok("customer_brief_link_exists", Boolean(document.querySelector('a[href="CUSTOMER_READY_BRIEF.md"]')));
    ok("executive_dashboard_exists", Boolean(document.getElementById("metric-ft-ready")) && Boolean(document.getElementById("metric-provenance")));
    ok("guided_builder_exists", Boolean(document.getElementById("guided-type")) && Boolean(document.getElementById("guided-fields")));
    ok("paper_ingestion_ui_exists", Boolean(document.getElementById("ingest-source-text")) && Boolean(document.getElementById("candidate-claims-list")));
    ok("sensitive_mode_button_exists", Boolean(document.getElementById("sensitive-mode-toggle")));
    ok("theme_button_exists", document.getElementById("theme-toggle"));
    ok("schema_version_badge_exists", document.getElementById("schema-version-badge")?.textContent.includes("schema v3"));
    ok("shared_payload_badge_visible", document.getElementById("shared-payload-badge")?.hidden === false);
    ok("help_button_exists", document.getElementById("help-btn"));
    ok("help_button_controls_modal", document.getElementById("help-btn").getAttribute("aria-controls") === "help-modal");
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
    ok("help_modal_lists_claim_type_requirements", document.querySelectorAll("#help-modal .claim-type-list li").length === 11);
    ok("help_modal_lists_schema_v2_financial_fields", document.getElementById("help-modal").textContent.includes("financial_metric_claim") && document.getElementById("help-modal").textContent.includes("metric_period_match"));
    ok("help_modal_lists_schema_v2_statistical_fields", document.getElementById("help-modal").textContent.includes("statistical_confidence") && document.getElementById("help-modal").textContent.includes("effect_direction_confirmed"));
    ok("help_modal_lists_schema_v2_reproducibility_fields", document.getElementById("help-modal").textContent.includes("reproducibility_check") && document.getElementById("help-modal").textContent.includes("independent_reproduction_pass"));
    ok("help_modal_lists_schema_v3_gap_fields", document.getElementById("help-modal").textContent.includes("causal_mechanism_claim") && document.getElementById("help-modal").textContent.includes("multimodal_evidence_claim"));
    ok("help_modal_documents_fine_tune_readiness", document.getElementById("help-modal").textContent.includes("fine_tune_ready") && document.getElementById("help-modal").textContent.includes("hash-verified external review packet"));
    ok("help_modal_documents_cli_provenance_verification", document.getElementById("help-modal").textContent.includes("The static browser UI previews these criteria") && document.getElementById("help-modal").textContent.includes("capas.py"));
    ok("help_modal_documents_numeric_ranges", document.getElementById("help-modal").textContent.includes("p_value") && document.getElementById("help-modal").textContent.includes("between 0 and 1"));
    ok("help_modal_documents_training_evidence_types", document.getElementById("help-modal").textContent.includes("training_evidence.source_backed_evidence") && document.getElementById("help-modal").textContent.includes("must be booleans"));
    ok("help_modal_documents_anchor_mode_boundary", document.getElementById("help-modal").textContent.includes("absolute_anchor") && document.getElementById("help-modal").textContent.includes("Other anchor modes remain"));
    closeHelpModal();
    ok("help_modal_closes", !document.getElementById("help-modal-backdrop").classList.contains("open"));
    ok("help_modal_returns_focus_to_trigger", document.activeElement === helpButton);

    localStorage.setItem("capas_decision_history_v1", JSON.stringify([{
      id: '<img src=x onerror="window.__xss=true">',
      verdict: "HOLD",
      reason: "legacy audit artifact",
      payload: JSON.stringify(versioned({
        claim: { id: '<img src=x onerror="window.__xss=true">', type: "exact_model_solution", text: "legacy" },
        evidence: { abs_error: 0, tolerance: 0.001 }
      })),
      decision: { verdict: "HOLD" },
      timestamp: new Date().toISOString()
    }]));
    decisionHistory = loadHistory();
    ok("legacy_history_sanitized_in_memory", decisionHistory.length === 0);
    ok("legacy_history_sanitized_storage", JSON.parse(localStorage.getItem("capas_decision_history_v1") || "[]").length === 0);

    buildDraft();
    ok("draft_status_is_amber", document.getElementById("json-status").className.includes("draft"));
    ok("draft_not_decided", document.getElementById("verdict-area").textContent.includes("Draft built, not decided"));
    ok("draft_includes_training_evidence_scaffold", document.getElementById("input").value.includes('"training_evidence"') && document.getElementById("input").value.includes('"source_backed_evidence"'));
    ok("draft_includes_schema_version", document.getElementById("input").value.includes('"schema_version": "capas-claim-payload-v3"'));

    document.getElementById("guided-type").value = "causal_mechanism_claim";
    renderGuidedFields();
    buildGuidedPayload();
    ok("guided_form_builds_schema_v3_payload", document.getElementById("input").value.includes('"schema_version": "capas-claim-payload-v3"') && document.getElementById("input").value.includes('"causal_mechanism_claim"'));
    decide();
    ok("guided_payload_decides", document.getElementById("output").textContent.includes('"verdict"'));
    loadVerticalDemo("AI_GOVERNANCE");
    ok("vertical_demo_loads_ai_governance", document.getElementById("input").value.includes("ai_gov_training_claim_001") && document.querySelector(".verdict-badge.ACCEPT"));

    document.getElementById("ingest-source-text").value = "The paper reports p_value: 0.03, alpha: 0.05, and effect_direction_confirmed: true for the main endpoint. The theory note reports anchor_mode: absolute_anchor, local_property_tests_pass: true, and universal_anchor_pass: true.";
    extractCandidateClaims();
    ok("paper_ingestion_extracts_candidates", ingestCandidates.length >= 1 && document.querySelectorAll(".candidate-row").length >= 1);
    ok("paper_ingestion_shows_evidence_spans", document.querySelector(".candidate-span")?.textContent.includes("line"));
    confirmCandidateClaim(0);
    ok("paper_ingestion_confirm_builds_payload", document.getElementById("input").value.includes('"ingestion"') && document.getElementById("input").value.includes('"human_confirmed": true'));
    decide();
    ok("paper_ingestion_payload_decides", document.getElementById("output").textContent.includes('"verdict"'));
    buildIngestionReport();
    ok("paper_ingestion_report_visible", document.getElementById("output").textContent.includes('"report_type": "paper_ingestion_preview"') && document.getElementById("output").textContent.includes('"evidence_spans"'));

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
    ok("new_schema_v3_sample_buttons_exist", ["CAUSAL", "SYSTEMATIC", "CONFLICT", "MULTIMODAL"].every((name) => typeof samples[name] === "object"));
    loadSample("CAUSAL");
    ok("causal_sample_button_accepts", document.querySelector(".verdict-badge.ACCEPT") && document.getElementById("type-label").textContent === "causal_mechanism_claim");
    loadSample("SYSTEMATIC");
    ok("systematic_sample_button_accepts", document.querySelector(".verdict-badge.ACCEPT") && document.getElementById("type-label").textContent === "systematic_review_claim");
    loadSample("CONFLICT");
    ok("conflict_sample_button_accepts", document.querySelector(".verdict-badge.ACCEPT") && document.getElementById("type-label").textContent === "evidence_conflict_claim");
    loadSample("MULTIMODAL");
    ok("multimodal_sample_button_accepts", document.querySelector(".verdict-badge.ACCEPT") && document.getElementById("type-label").textContent === "multimodal_evidence_claim");

    document.getElementById("input").value = JSON.stringify([samples.ACCEPT, samples.REJECT], null, 2);
    decideBatch();
    ok("batch_summary_visible", document.getElementById("verdict-area").textContent.includes("Batch summary"));
    ok("batch_progress_visible", document.querySelector(".batch-progress-fill"));
    ok("batch_progress_label_visible", document.getElementById("verdict-area").textContent.includes("claims processed"));
    ok("batch_per_item_table_visible", document.querySelectorAll(".batch-row").length === 2);
    ok("batch_per_item_reason_visible", document.querySelector(".batch-row-reason")?.textContent.length > 0);
    ok("batch_per_item_fine_tune_summary_visible", document.querySelector(".batch-row-ft")?.textContent.includes("FT"));
    ok("batch_output_json", document.getElementById("output").textContent.includes('"batch_mode": "decide"'));
    ok("batch_schema_version", document.getElementById("output").textContent.includes('"schema_version": "capas-claim-payload-v3"'));
    document.getElementById("input").value = JSON.stringify(samples.ACCEPT, null, 2);
    decideBatch();
    ok("batch_single_object_autowrap", document.getElementById("output").textContent.includes('"item_count": 1'));

    document.getElementById("input").value = JSON.stringify(versioned({
      claim: { id: "stat_sig", type: "statistical_confidence", text: "The effect is statistically significant at alpha 0.05." },
      evidence: { p_value: 0.01, alpha: 0.05, effect_direction_confirmed: true }
    }));
    decide();
    ok("statistical_confidence_accept", document.querySelector(".verdict-badge.ACCEPT"));
    document.getElementById("input").value = JSON.stringify(versioned({
      claim: { id: "repro_rw", type: "reproducibility_check", text: "The result is independently reproducible." },
      evidence: { artifact_available: true, independent_reproduction_pass: false }
    }));
    decide();
    ok("reproducibility_check_rewrite", document.querySelector(".verdict-badge.REWRITE"));
    document.getElementById("input").value = JSON.stringify(versioned({
      claim: { id: "finance_accept", type: "financial_metric_claim", text: "The reported metric matches the reference for the same period." },
      evidence: { reported_value: 101.2, reference_value: 101.0, tolerance: 0.5, metric_period_match: true }
    }));
    decide();
    ok("financial_metric_claim_accept", document.querySelector(".verdict-badge.ACCEPT"));
    document.getElementById("input").value = JSON.stringify(versioned({
      claim: { id: "causal_accept", type: "causal_mechanism_claim", text: "The intervention causally changes the outcome through the declared mechanism." },
      evidence: { intervention_or_natural_experiment: true, temporal_order_established: true, confounders_controlled: true, mechanism_evidence_present: true }
    }));
    decide();
    ok("causal_mechanism_claim_accept", document.querySelector(".verdict-badge.ACCEPT"));
    document.getElementById("input").value = JSON.stringify(versioned({
      claim: { id: "review_rewrite", type: "systematic_review_claim", text: "The systematic review supports the reported effect." },
      evidence: { protocol_registered: true, inclusion_criteria_declared: true, risk_of_bias_assessed: false, effect_consistency: false }
    }));
    decide();
    ok("systematic_review_claim_rewrite", document.querySelector(".verdict-badge.REWRITE"));
    document.getElementById("input").value = JSON.stringify(versioned({
      claim: { id: "conflict_accept", type: "evidence_conflict_claim", text: "The conflicting evidence is resolved by the declared method." },
      evidence: { supporting_sources: ["s1"], contradicting_sources: ["s2"], conflict_resolution_method: "pre-registered hierarchy", resolution_pre_registered: true }
    }));
    decide();
    ok("evidence_conflict_claim_accept", document.querySelector(".verdict-badge.ACCEPT"));
    document.getElementById("input").value = JSON.stringify(versioned({
      claim: { id: "multi_accept", type: "multimodal_evidence_claim", text: "The multimodal evidence supports the extracted claim." },
      evidence: { modality: "table", source_hashes_verified: true, cross_modal_alignment: true, extraction_method_declared: true }
    }));
    decide();
    ok("multimodal_evidence_claim_accept", document.querySelector(".verdict-badge.ACCEPT"));

    document.getElementById("input").value = JSON.stringify(versioned({
      claim: { id: "external_scaling_anchor_fine_tune_ready", type: "universal_anchor_claim", text: "The generated scaling result is physically consistent with the universal z=1 anchor." },
      evidence: { anchor_mode: "absolute_anchor", local_property_tests_pass: true, universal_anchor_pass: true },
      training_evidence: {
        source_backed_evidence: true,
        external_review: true,
        semantic_alignment: true,
        witness_independence: true,
        provenance: {
          source_urls: ["file://benchmarks/gold_traces/trace_039.json"],
          source_hashes: {
            "file://benchmarks/gold_traces/trace_039.json": "d5884367e508273ef1d54ac507135864b8aa493adf5602f65da55f0a38bc86b6"
          },
          review_id: "external-review-trace-039-v1",
          review_sha256: "120d4d2847ebdf385bd21848d32bf65b7b0cb6e2b072bda9ac3c80f780732640",
          review_packet: {
            claim_id: "external_scaling_anchor_fine_tune_ready",
            decision: "confirms_fine_tune_readiness",
            review_id: "external-review-trace-039-v1",
            reviewer_id: "capas-external-reviewer-demo",
            scope: "training readiness criteria only"
          },
          witness_id: "theory_scaling_law_no_solver",
          witness_registry_path: "docs/witness_registry.json",
          witness_registry_sha256: "64bd434da1acfe79a25905c7b6470485b00194882d2f5e12becbf7baea3e77c8",
          ro_crate_path: "benchmarks/ro_crates/trace_039/ro-crate-metadata.json",
          ro_crate_sha256: "9e8f3769049430f9a620e838e44e936cc4fa6414769f25be611f9388f4080b86",
          reviewer: {
            attestation: "External reviewer confirms source-backed evidence, semantic alignment, witness independence, and ACCEPT scope for trace_039.",
            attestation_sha256: "ebe5ebb8660e891b30ccf0ef34e8457d53cf3caa04ac62416b1d64af13528fbf",
            reviewer_id: "capas-external-reviewer-demo"
          },
          reviewer_registry_path: "docs/reviewer_registry.json",
          reviewer_registry_sha256: "00c3133d7001b4a6e3b9223f0144ab4bfa90fc86a22a2a6220dde3e1f3021202"
        }
      }
    }));
    decide();
    ok("browser_fine_tune_ready_requires_cli", document.getElementById("output").textContent.includes('"fine_tune_ready": false') && document.getElementById("output").textContent.includes("Active provenance gates require capas.py CLI/API verification"));
    ok("browser_provenance_gates_blocked", document.getElementById("output").textContent.includes('"review_hash_verified": false') && document.getElementById("output").textContent.includes('"reviewer_attestation_verified": false'));
    ok("fine_tune_criteria_visible", document.getElementById("output").textContent.includes('"fine_tune_criteria"'));
    ok("fine_tune_status_visible_in_verdict_area", document.getElementById("verdict-area").textContent.includes("Fine-tune readiness") && document.getElementById("verdict-area").textContent.includes("NOT READY"));
    ok("fine_tune_status_is_live_region", document.querySelector(".fine-tune-block")?.getAttribute("role") === "status" && document.querySelector(".fine-tune-block")?.getAttribute("aria-live") === "polite");
    ok("type_label_is_live_region", document.getElementById("type-label")?.getAttribute("role") === "status" && document.getElementById("type-label")?.getAttribute("aria-live") === "polite");

    document.getElementById("input").value = JSON.stringify({
      claim: { id: "missing_schema_version", type: "exact_model_solution", text: "A missing schema version must not be processed as current schema." },
      evidence: { abs_error: 0, tolerance: 0.1 }
    });
    decide();
    ok("missing_schema_version_holds", document.querySelector(".verdict-badge.HOLD") && document.getElementById("output").textContent.includes("schema_version must be capas-claim-payload-v3"));

    const firstHistory = document.querySelector(".history-item");
    ok("history_item_exists", firstHistory);
    if (firstHistory) firstHistory.click();
    ok("history_restore_keeps_output", document.getElementById("output").textContent.includes("verdict"));
    ok("history_timestamp_visible", Boolean(document.querySelector(".history-ts")?.textContent.trim()));
    ok("history_delete_button_visible", Boolean(document.querySelector(".history-delete")));
    document.getElementById("history-filter").value = "finance";
    renderHistory();
    ok("history_filter_input_exists", document.getElementById("history-list").textContent.toLowerCase().includes("finance") || document.getElementById("history-list").textContent.includes("No matching decisions"));
    document.getElementById("history-filter").value = "";
    document.getElementById("history-verdict-filter").value = "ACCEPT";
    renderHistory();
    ok("history_verdict_filter_exists", Boolean(document.getElementById("history-verdict-filter")));
    document.getElementById("history-verdict-filter").value = "";
    renderHistory();
    const historyLengthBeforeDelete = decisionHistory.length;
    document.querySelector(".history-delete")?.click();
    ok("history_delete_removes_one_entry", decisionHistory.length === historyLengthBeforeDelete - 1);

    document.getElementById("output").scrollTop = 999;
    decide();
    ok("output_scroll_resets_to_top", document.getElementById("output").scrollTop === 0);
    ok("share_button_privacy_label", document.getElementById("share-btn").getAttribute("aria-label").includes("payload is embedded"));
    ok("share_app_button_exists", document.getElementById("share-app-btn").getAttribute("aria-label").includes("without embedding"));
    toggleSensitiveMode();
    ok("sensitive_mode_turns_on", document.getElementById("sensitive-mode-toggle").textContent.includes("On") && document.getElementById("sensitive-mode-toggle").classList.contains("sensitive-active"));
    ok("sensitive_mode_persists", localStorage.getItem("capas_sensitive_mode_v1") === "true");
    toggleSensitiveMode();
    ok("sensitive_mode_turns_off", document.getElementById("sensitive-mode-toggle").textContent.includes("Off") && !localStorage.getItem("capas_sensitive_mode_v1"));

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
        html = capas._apply_inline_csp_hashes(UI_PATH.read_text(encoding="utf-8").replace("</body>", HARNESS + "\n</body>"))
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
