from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
UI_PATH = ROOT / "outputs" / "capas_claim_gate_ui.html"
REPORT_PATH = ROOT / "outputs" / "claim_gate_ui_report.json"


REQUIRED_SNIPPETS = [
    "schema_errors",
    "validatePayload",
    "input payload failed CAPAS schema validation",
    "ACCEPT sample",
    "REWRITE sample",
    "REJECT sample",
    "HOLD sample",
    "INVALID schema sample",
    "claim.type must be one of",
    "fine_tune_ready",
    "fine_tune_blockers",
    "not an LLM judgment",
    "aria-label=\"Claim and evidence JSON input\"",
    "aria-label=\"Copy decision JSON\"",
    "focus-visible",
    "localStorage",
    "restoreHistory",
    "historyLimit = 50",
    "Input required",
    "prefers-color-scheme: light",
    "disabled>Copy JSON",
    "minmax(380px, 42%)",
    "Build Draft",
    "Draft built, not decided",
    "renderSchemaAssistant",
    "Missing field assistant",
    "explainSchemaError",
    "CAPAS will not infer them",
    "role=\"button\" tabindex=\"0\"",
    "handleHistoryKey",
    "CAPAS Claim Gate - Design System v10",
    "<meta name=\"description\"",
    "property=\"og:title\"",
    "property=\"og:image\"",
    "name=\"twitter:card\" content=\"summary_large_image\"",
    "http-equiv=\"Content-Security-Policy\"",
    "capas-social-card.svg",
    "<header class=\"topbar\">",
    "aria-label=\"CAPAS Claim Gate\"",
    "aria-hidden=\"true\">CG</div>",
    "class=\"skip-link\" href=\"#main\"",
    "<main class=\"app-body\" id=\"main\">",
    "aria-live=\"polite\" aria-atomic=\"true\"",
    "CAPAS structures and gates supplied claim evidence",
    "claim.text must be at most 2000 characters",
    "<h2 class=\"history-heading\">Recent decisions</h2>",
    "id=\"share-btn\"",
    "copyShareUrl",
    "maybeLoadSharedPayload",
    "id=\"export-btn\"",
    "exportHistoryCsv",
    "id=\"clear-history-btn\"",
    "clearHistory",
    "id=\"theme-toggle\"",
    "toggleTheme",
    "themeStorageKey",
    "Current theme:",
    "id=\"batch-btn\"",
    "Batch input: JSON array",
    "decideBatch",
    "runBatch",
    "payload.claim && payload.evidence",
    "Batch summary",
    "capas-claim-payload-v1",
    "schema_version",
    "id=\"schema-version-badge\"",
    "schema v1",
    "id=\"help-btn\"",
    "openHelpModal(this)",
    "help-modal-backdrop",
    "id=\"help-modal\" role=\"dialog\" aria-modal=\"true\"",
    "CAPAS shortcuts and pipeline modes",
    "openHelpModal",
    "closeHelpModal",
    "isSafeHistoryEntry",
    "containsAngleLikeCharacter(entry.id)",
    "localStorage.setItem(historyStorageKey, JSON.stringify(clean))",
    "document.contains(lastFocusedBeforeHelp)",
    "handleHelpModalKey",
    "focusableHelpElements",
    "retrieve \u2192 extract \u2192 align \u2192 reason \u2192 pipeline",
    "scheduleInputChange",
    "inputChangeTimer",
    "--accent: #4f46e5",
    "--green: #15803d",
    "pre#output { background: var(--bg-3); }",
    "lastOutputJson",
    "--json-key",
    ".json-key { color: var(--json-key); }",
    "if (json.length > 5000)",
    "--accent-glow",
    "Draft - fill null values before deciding",
    "syntaxHighlight",
    "rewrite-diff",
    "json-key",
    "v10 · batch pipelines",
]

FORBIDDEN_SNIPPETS = [
    ".header {",
    "padding: 20px 28px",
    "max-width: 1200px",
]


def main() -> int:
    proc = subprocess.run([sys.executable, "capas.py", "ui"], cwd=ROOT, text=True, capture_output=True)
    html = UI_PATH.read_text(encoding="utf-8") if UI_PATH.exists() else ""
    checks = [
        {
            "check": "capas_ui_command",
            "passed": proc.returncode == 0 and UI_PATH.exists(),
            "detail": (proc.stdout + proc.stderr).strip(),
        }
    ]
    for snippet in REQUIRED_SNIPPETS:
        checks.append({
            "check": f"ui_contains:{snippet}",
            "passed": snippet in html,
            "detail": snippet,
        })
    for snippet in FORBIDDEN_SNIPPETS:
        checks.append({
            "check": f"ui_omits_legacy:{snippet}",
            "passed": snippet not in html,
            "detail": snippet,
        })

    passed = all(item["passed"] for item in checks)
    report = {
        "claim_gate_ui_ready": passed,
        "ui_path": str(UI_PATH.relative_to(ROOT)),
        "checks": checks,
        "scope": (
            "Static HTML contract check. It verifies the generated UI exposes "
            "the schema-aware decision surface; it is not a browser-executed "
            "end-to-end JavaScript test."
        ),
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    for item in checks:
        status = "ok" if item["passed"] else "failed"
        print(f"{item['check']}: {status}")
    print(f"claim_gate_ui_ready: {passed}")
    print(f"report written to {REPORT_PATH}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
