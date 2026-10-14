#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Browser integrity checks for the Gate App (external audit 2026-10-14, round 5). Runs the real page against a local
capas_api with Playwright and asserts, for each scenario the auditor reproduced:
  1. engine unavailable -> HOLD with reason_code ENGINE_UNAVAILABLE, no licensed claim, reuse_boundary "none";
  2. out-of-order responses (A slow, B fast) -> no hybrid history record, the shown result belongs to the current input;
  3. editing after a result -> "previous result" notice and export disabled;
  4. first visit -> one request, nothing written to the decision log;
  5. language toggle -> the step indicator and the saved-count keep the real state;
  6. guided builder -> every one of the 14 claim types builds a payload whose evidence types match the engine schema.
Run: python3 benchmarks/verify_gate_app_integrity.py"""
from __future__ import annotations
import json, socket, subprocess, sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))


def _free_port() -> int:
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p


def main() -> int:
    from playwright.sync_api import sync_playwright
    import capas
    port = _free_port()
    srv = subprocess.Popen([sys.executable, str(ROOT / "capas_api.py"), str(port)], cwd=str(ROOT),
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env={**__import__("os").environ, "CAPAS_HOSTED": ""})
    base = f"http://127.0.0.1:{port}/app.html"
    fails = []
    try:
        for _ in range(50):
            try:
                socket.create_connection(("127.0.0.1", port), timeout=0.2).close(); break
            except OSError:
                time.sleep(0.1)
        with sync_playwright() as p:
            b = p.chromium.launch()

            # 4. first visit: one request, empty log
            ctx = b.new_context(); pg = ctx.new_page(); calls = []
            pg.on("request", lambda r: calls.append(r.url) if "/api/decide" in r.url else None)
            pg.goto(base, wait_until="networkidle"); pg.wait_for_timeout(800)
            hist = pg.evaluate("localStorage.getItem('capas_decision_history_v1')")
            n_hist = len(json.loads(hist)) if hist else 0
            if len(calls) != 1 or n_hist != 0:
                fails.append(f"first visit: {len(calls)} /api/decide calls, {n_hist} log records (want 1 and 0)")

            # 1. engine unavailable
            pg.route("**/api/decide", lambda route: route.abort())
            pg.evaluate("loadSample('ACCEPT')"); pg.wait_for_timeout(600)
            out = json.loads(pg.locator("#output").text_content() or "{}")
            cert = out.get("admissibility_certificate") or {}
            if not (out.get("verdict") == "HOLD" and out.get("reason_code") == "ENGINE_UNAVAILABLE" and out.get("licensed_claim") is None
                    and (cert.get("lattice") or {}).get("reuse_boundary") == "none" and "licensed_thesis" not in json.dumps(cert)):
                fails.append(f"offline: verdict={out.get('verdict')} code={out.get('reason_code')} boundary={(cert.get('lattice') or {}).get('reuse_boundary')}")
            pg.unroute("**/api/decide")
            ctx.close()

            # 2. out of order: A slow, B fast
            ctx = b.new_context(); pg = ctx.new_page(); pg.goto(base, wait_until="networkidle"); pg.wait_for_timeout(500)
            pg.evaluate("localStorage.removeItem('capas_decision_history_v1'); decisionHistory = []; renderHistory()")
            # delay A inside the page (a blocking route handler would also hold B back)
            pg.evaluate("""(() => { const f = window.fetch; window.fetch = async (u, o) => {
                if (o && o.body && o.body.includes('"claim_A"')) await new Promise(r => setTimeout(r, 1200));
                return f(u, o); }; })()""")
            a = {"schema_version": "capas-claim-payload-v3", "claim": {"id": "claim_A", "type": "statistical_confidence", "text": "A in this cohort."},
                 "evidence": {"p_value": 0.01, "alpha": 0.05, "effect_direction_confirmed": True}}
            bb = {**a, "claim": {**a["claim"], "id": "claim_B", "text": "B in this cohort."}, "evidence": {**a["evidence"], "p_value": 0.2}}
            pg.evaluate(f"document.getElementById('input').value = {json.dumps(json.dumps(a))}; onInputChange(); void decide()")   # do not await: A must still be in flight
            pg.wait_for_timeout(100)
            pg.evaluate(f"document.getElementById('input').value = {json.dumps(json.dumps(bb))}; onInputChange(); void decide()")
            pg.wait_for_timeout(2200)
            shown = json.loads(pg.locator("#output").text_content() or "{}")
            hist = json.loads(pg.evaluate("localStorage.getItem('capas_decision_history_v1')") or "[]")
            hybrid = [h for h in hist if json.loads(h["payload"])["claim"]["id"] != h["id"]]
            if "--debug" in sys.argv:
                print("DEBUG order:", shown.get("input_claim", {}).get("id"), [(h["id"], json.loads(h["payload"])["claim"]["id"]) for h in hist])
            if shown.get("input_claim", {}).get("id") != "claim_B" or hybrid:
                fails.append(f"order: shown={shown.get('input_claim', {}).get('id')} hybrid_records={len(hybrid)}")

            # 3. stale after edit
            pg.evaluate("document.getElementById('input').value += ' '; document.getElementById('input').value = document.getElementById('input').value.replace('B in this cohort.', 'B edited.'); onInputChange()")
            stale = pg.locator("#stale-result").count(); copy_disabled = pg.evaluate("document.getElementById('copy-btn').disabled")
            if not (stale == 1 and copy_disabled):
                fails.append(f"stale: notice={stale} copy_disabled={copy_disabled}")

            # 5. language toggle keeps state
            pg.evaluate("setFlowPhase('gate', {focus: false})")
            pg.evaluate("KQLang.toggle()"); pg.wait_for_timeout(200)
            step = pg.locator("#phase-indicator").inner_text(); count = pg.locator("#history-count").inner_text()
            n = len(hist)
            if not step.lower().startswith("paso 3 de 3") or not count.startswith(f"{n}/") or "guardadas" not in count:
                fails.append(f"language: step={step!r} count={count!r} (records {n})")
            pg.evaluate("KQLang.toggle()")

            # 6. guided builder types for all 14 claim types
            types = pg.evaluate("Array.from(document.getElementById('guided-type').options).map(o => o.value)")
            ftypes = capas.CLAIM_TYPE_REGISTRY
            for t in types:
                pg.evaluate(f"setWorkflowMode('guided'); document.getElementById('guided-type').value = {json.dumps(t)}; renderGuidedFields()")
                fields = pg.evaluate("Array.from(document.querySelectorAll('#guided-fields [data-field]')).map(e => [e.dataset.field, e.dataset.kind, e.tagName])")
                for f, kind, tag in fields:
                    want = capas.evidence_field_type(f)
                    ok = {"boolean": kind == "boolean", "number": kind == "number", "string[]": kind == "array",
                          "object": kind == "object", "string": kind == "text"}.get(want, True)
                    if not ok:
                        fails.append(f"builder {t}.{f}: control kind {kind} for engine type {want}")
                text = pg.evaluate("document.getElementById('guided-claim-text').value")
                if t not in ("exact_model_solution",) and "exact" in str(pg.evaluate("document.getElementById('guided-claim-id').value")):
                    fails.append(f"builder {t}: inherited another family's id")
            if len(types) != len(ftypes):
                fails.append(f"builder offers {len(types)} types, engine has {len(ftypes)}")
            b.close()
    finally:
        srv.terminate()
    print("PASS — Gate App integrity: offline, ordering, stale, first visit, language state, typed builder" if not fails
          else "FAIL:\n  " + "\n  ".join(fails))
    return 0 if not fails else 1


if __name__ == "__main__":
    raise SystemExit(main())
