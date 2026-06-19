from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "outputs" / "batch_api_report.json"
PORT = 8766


def _json_request(url: str, payload: object | None = None) -> dict:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = Request(url, data=data, headers={"content-type": "application/json"})
    with urlopen(request, timeout=5) as response:
        return json.loads(response.read().decode("utf-8"))


def _wait_for_health() -> bool:
    deadline = time.time() + 10
    while time.time() < deadline:
        try:
            health = _json_request(f"http://127.0.0.1:{PORT}/health")
        except (OSError, URLError):
            time.sleep(0.2)
            continue
        return health.get("status") == "ok"
    return False


def main() -> int:
    checks: list[dict] = []
    batch_proc = subprocess.run(
        [
            sys.executable,
            "capas.py",
            "batch",
            "--input",
            "examples/external_claim_batch.json",
            "--json",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    try:
        batch_report = json.loads(batch_proc.stdout)
    except json.JSONDecodeError:
        batch_report = {}
    checks.append({
        "check": "batch_cli_runs",
        "passed": batch_proc.returncode == 0 and batch_report.get("item_count") == 3,
        "detail": batch_proc.stderr.strip(),
    })
    checks.append({
        "check": "batch_cli_summary",
        "passed": batch_report.get("summary") == {"ACCEPT": 1, "HOLD": 1, "REWRITE": 1},
        "detail": batch_report.get("summary"),
    })

    server = subprocess.Popen(
        [sys.executable, "capas.py", "serve", "--host", "127.0.0.1", "--port", str(PORT)],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        healthy = _wait_for_health()
        checks.append({"check": "api_health", "passed": healthy, "detail": f"port {PORT}"})
        accept_payload = json.loads((ROOT / "examples" / "external_claim_accept.json").read_text(encoding="utf-8"))
        api_decision = _json_request(f"http://127.0.0.1:{PORT}/decide", accept_payload) if healthy else {}
        checks.append({
            "check": "api_decide_accept",
            "passed": api_decision.get("verdict") == "ACCEPT",
            "detail": api_decision.get("reason"),
        })
        batch_payload = json.loads((ROOT / "examples" / "external_claim_batch.json").read_text(encoding="utf-8"))
        api_batch = _json_request(f"http://127.0.0.1:{PORT}/batch", batch_payload) if healthy else {}
        checks.append({
            "check": "api_batch_summary",
            "passed": api_batch.get("summary") == {"ACCEPT": 1, "HOLD": 1, "REWRITE": 1},
            "detail": api_batch.get("summary"),
        })
    finally:
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()

    passed = all(check["passed"] for check in checks)
    report = {
        "batch_api_ready": passed,
        "checks": checks,
        "scope": "Verifies batch CLI and local stdlib HTTP API. This is not an externally hosted SaaS endpoint.",
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    for check in checks:
        print(f"{check['check']}: {'ok' if check['passed'] else 'failed'}")
    print(f"batch_api_ready: {passed}")
    print(f"report written to {REPORT_PATH}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
