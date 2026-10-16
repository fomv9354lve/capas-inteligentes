#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Browser regression for the external re-audit of fb52d8c (cases A-J). Real page served by the local capas_api
with its CSP active, real controls (fill/click), responses held and released at the HTTP boundary (Playwright route
objects kept unresolved until the test releases them: a deterministic barrier, no sleep as synchronisation).

  A  edit while a request is pending (debounce allowed to finish) -> the old result is never the current decision
  B  batches out of order; edit after a batch; single<->batch with a request pending; a replaced batch stops dispatching
  C  same claim id, A slow ACCEPT, B fast REJECT -> history keeps both, B first, survives reload; B failing keeps A
  D  HTTP 200 with an incomplete / mistyped / contradictory body -> protocol error, nothing exportable or recorded;
     genuine engine responses of all four verdicts still complete (positive controls)
  E  engine not run (500, 429, timeout, abort) -> no "evidence evaluated / schema checked / complete" claims
  F  system light preference (and a stored light theme) -> the app stays in one coherent dark palette
  G  navigation at 320/390/768/1024/1440 on the shell pages -> links inside the nav box, no nav/subnav overlap, no
     horizontal page overflow, language toggle and last link reachable
  H  the server-submission notice is visible next to the Run control actually used, in every mode
  I  decision log: a malformed hash is not shown as a trusted decision; counts survive ES/EN
  J  guided proof_admissibility with empty text -> visible validation, no exception, no invented claim
  K  external re-audit d2bce91: type then Ctrl+Enter at once -> the result stays current after the debounce; a claim
     text with "<" is recorded and rendered as text; at 390 px the decision panel fills the gate column
     (the D list also gained: REJECT whose certificate says approve, READY with failed criteria, unsupported schema
     version, other claim text, v2 fields stripped)

Run: python3 benchmarks/verify_gate_app_contract.py [--only A,B] [--json out.json]"""
from __future__ import annotations

import json, os, socket, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V3 = "capas-claim-payload-v3"


def _free_port() -> int:
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p


def stat(cid, p=0.01, direction=True, text=None):
    return {"schema_version": V3, "claim": {"id": cid, "type": "statistical_confidence", "text": text or f"{cid} in this cohort."},
            "evidence": {"p_value": p, "alpha": 0.05, "effect_direction_confirmed": direction}}


class Held:
    """Routes for /api/decide: requests whose body contains a held marker wait until released."""
    def __init__(self, page):
        self.page, self.hold, self.waiting, self.seen = page, set(), [], []
        page.route("**/api/decide", self._on)

    def _on(self, route):
        body = route.request.post_data or ""
        self.seen.append(body)
        if any(m in body for m in self.hold):
            self.waiting.append(route)
        else:
            route.continue_()

    def release(self, marker=None):
        keep = []
        for r in self.waiting:
            if marker is None or marker in (r.request.post_data or ""):
                r.continue_()
            else:
                keep.append(r)
        self.waiting = keep

    def pump(self, until, timeout=8.0):
        t = time.time()
        while time.time() - t < timeout:
            if until():
                return True
            self.page.wait_for_timeout(25)
        return False


def main() -> int:
    from playwright.sync_api import sync_playwright
    only = set(sys.argv[sys.argv.index("--only") + 1].split(",")) if "--only" in sys.argv else set("ABCDEFGHIJK")
    port = _free_port()
    srv = subprocess.Popen([sys.executable, str(ROOT / "capas_api.py"), str(port)], cwd=str(ROOT),
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env={**os.environ, "CAPAS_HOSTED": ""})
    base = f"http://127.0.0.1:{port}"
    res: dict[str, list[str]] = {k: [] for k in "ABCDEFGHIJK"}
    try:
        for _ in range(80):
            try:
                socket.create_connection(("127.0.0.1", port), timeout=0.2).close(); break
            except OSError:
                time.sleep(0.1)
        with sync_playwright() as p:
            br = p.chromium.launch()

            def fresh(width=1440, height=900, scheme="dark", storage=None):
                ctx = br.new_context(viewport={"width": width, "height": height}, color_scheme=scheme)
                # a CSP violation is reported with the handler sample and the element, so a failure names its cause
                ctx.add_init_script("""document.addEventListener('securitypolicyviolation', (e) => {
                    const t = e.target && e.target.outerHTML ? e.target.outerHTML.slice(0, 160) : '';
                    console.error('CSPVIOLATION ' + e.violatedDirective + ' sample=' + (e.sample || '') + ' element=' + t); });""")
                if storage:
                    ctx.add_init_script("(() => { const s = %s; for (const k in s) localStorage.setItem(k, s[k]); })()" % json.dumps(storage))
                # external resources (fonts, the ornamental 3D logo's CDN scripts) are blocked: local and deterministic
                ctx.route(lambda url: not url.startswith(base), lambda route: route.abort())
                pg = ctx.new_page(); pg.set_default_timeout(8000)
                errors = []
                # "THREE is not defined" comes from the ornamental logo iframe whose CDN script is blocked above
                pg.on("pageerror", lambda e: None if "THREE is not defined" in str(e) else errors.append(str(e)))
                pg.on("console", lambda m: errors.append(m.text[:400]) if m.text.startswith("CSPVIOLATION") else None)
                return ctx, pg, errors

            def select_mode(pg, mode, phase="gate"):
                pg.evaluate("goToPhase('choose', {focus: false})"); pg.wait_for_timeout(120)
                if mode != "guided" and not pg.locator(f"#workflow-mode-{mode}").is_visible() and not pg.locator("#adv-modes-toggle").is_checked():
                    pg.click("label.adv-toggle-label")   # the "show advanced inputs" switch
                pg.click(f"#workflow-mode-{mode}")
                pg.evaluate(f"goToPhase('{phase}', {{focus: false}})"); pg.wait_for_timeout(120)

            def open_raw(pg):
                pg.goto(base + "/app.html", wait_until="domcontentloaded")
                pg.wait_for_timeout(900)          # the first-visit example request settles
                select_mode(pg, "raw")

            def step(pg, name):
                pg.click(f"button.step-tab[data-step='{name}']"); pg.wait_for_timeout(120)

            def edit(pg, payload):
                step(pg, "complete"); pg.fill("#input", payload if isinstance(payload, str) else json.dumps(payload))

            def run(pg):
                step(pg, "gate"); pg.click("#phase-run")

            def run_single(pg, payload):
                edit(pg, payload); run(pg)

            def state(pg):
                return pg.evaluate("""(() => { let o = {}; try { o = JSON.parse(document.getElementById('output').textContent || '{}'); } catch (_) {}
                    return {input: document.getElementById('input').value, shown: o.input_claim ? o.input_claim.id : (o.results ? 'batch:' + o.results.map(r => r.result.input_claim && r.result.input_claim.id).join('|') : null),
                            verdict: o.verdict, copy_disabled: document.getElementById('copy-btn').disabled,
                            stale: !!document.getElementById('stale-result'), area: document.getElementById('verdict-area').innerText,
                            status: (document.getElementById('payload-status-card') || {}).innerText || '',
                            hist: JSON.parse(localStorage.getItem('capas_decision_history_v1') || '[]')}; })()""")

            # ---------------------------------------------------------------- A
            if "A" in only:
              try:
                  ctx, pg, errs = fresh(); open_raw(pg); h = Held(pg)
                  h.hold.add('"PENDING_A"')
                  run_single(pg, stat("PENDING_A"))
                  h.pump(lambda: h.waiting)
                  edit(pg, stat("EDITED_B", p=0.3))
                  pg.wait_for_timeout(450)                     # let the editor's debounce complete before releasing A
                  h.release('"PENDING_A"'); h.pump(lambda: "PENDING_A" in (pg.locator("#output").text_content() or "") or not h.waiting, 4)
                  pg.wait_for_timeout(400); step(pg, "gate")
                  s = state(pg)
                  if not s["copy_disabled"]:
                      res["A"].append(f"A result exportable while the input is B (shown={s['shown']})")
                  if s["shown"] == "PENDING_A" and not s["stale"]:
                      res["A"].append("A shown for input B without a stale notice")
                  # A -> B -> A: going back to A's exact text must not revive A
                  edit(pg, stat("PENDING_A")); pg.wait_for_timeout(450); step(pg, "gate")
                  if not state(pg)["copy_disabled"]:
                      res["A"].append("A -> B -> A revived the invalidated result as current")
                  if errs: res["A"].append(f"page errors: {errs[:2]}")
                  ctx.close()

              except Exception as exc:   # a harness failure is recorded, never a pass
                  res["A"].append(f"harness error: {type(exc).__name__}: {str(exc).splitlines()[0][:160]}")
            # ---------------------------------------------------------------- B
            if "B" in only:
              try:
                  ctx, pg, errs = fresh(); open_raw(pg); select_mode(pg, "batch")
                  h = Held(pg); h.hold.add('"BATCH_A')
                  run_single(pg, [stat("BATCH_A1"), stat("BATCH_A2")])
                  h.pump(lambda: len(h.waiting) >= 2)
                  run_single(pg, [stat("BATCH_B1"), stat("BATCH_B2", p=0.3)])
                  h.pump(lambda: "BATCH_B" in (pg.locator("#output").text_content() or ""), 6)
                  h.release('"BATCH_A'); pg.wait_for_timeout(700)
                  s = state(pg)
                  if "BATCH_A" in str(s["shown"]):
                      res["B"].append(f"older batch replaced the newer one: shown {s['shown']}")
                  edit(pg, [stat("BATCH_C1")]); pg.wait_for_timeout(450); step(pg, "gate")
                  if not state(pg)["copy_disabled"]:
                      res["B"].append("batch result still exportable after the batch input was edited")
                  # a replaced batch stops dispatching its queue
                  h.hold = {'"QUEUE_A'}; h.seen.clear()
                  run_single(pg, [stat(f"QUEUE_A{i}") for i in range(8)])
                  h.pump(lambda: len(h.waiting) >= 4)
                  pending_a = len(h.waiting)
                  if pending_a > 4:
                      res["B"].append(f"{pending_a} requests in flight (limit 4)")
                  run_single(pg, [stat("QUEUE_B1")])
                  h.pump(lambda: "QUEUE_B1" in (pg.locator("#output").text_content() or ""), 6)
                  h.release('"QUEUE_A'); pg.wait_for_timeout(900)
                  sent_a = sum('"QUEUE_A' in b for b in h.seen)
                  if sent_a > 4:
                      res["B"].append(f"replaced batch kept dispatching its queue: {sent_a} of 8 sent")
                  if "QUEUE_A" in str(state(pg)["shown"]):
                      res["B"].append("replaced batch became the shown result")
                  # single pending, then switch to batch: the single result must not become current in batch context
                  select_mode(pg, "raw")
                  h.hold = {'"MODE_A"'}
                  run_single(pg, stat("MODE_A")); h.pump(lambda: h.waiting)
                  select_mode(pg, "batch")
                  h.release('"MODE_A"'); pg.wait_for_timeout(700)
                  if not state(pg)["copy_disabled"]:
                      res["B"].append("single result became exportable in batch mode")
                  select_mode(pg, "raw"); pg.wait_for_timeout(200)
                  if not state(pg)["copy_disabled"]:
                      res["B"].append("returning to raw mode revived the single result computed before the switch")
                  if errs: res["B"].append(f"page errors: {errs[:2]}")
                  ctx.close()

              except Exception as exc:   # a harness failure is recorded, never a pass
                  res["B"].append(f"harness error: {type(exc).__name__}: {str(exc).splitlines()[0][:160]}")
            # ---------------------------------------------------------------- C
            if "C" in only:
              try:
                  ctx, pg, errs = fresh(); open_raw(pg); pg.evaluate("localStorage.removeItem('capas_decision_history_v1'); decisionHistory = []; renderHistory()")
                  h = Held(pg); h.hold.add('"p_value": 0.01')
                  failed = []
                  pg.on("requestfailed", lambda r: failed.append(r.post_data or "") if "/api/decide" in r.url else None)
                  run_single(pg, stat("SAME_ID", p=0.01)); h.pump(lambda: h.waiting)
                  run_single(pg, stat("SAME_ID", p=0.3)); pg.wait_for_timeout(700)
                  h.release(); pg.wait_for_timeout(700)
                  if any('"p_value": 0.01' in f for f in failed):
                      res["C"].append("the earlier run's request was aborted, so its decision could not be kept as an antecedent")
                  s = state(pg)
                  verdicts = [r["verdict"] for r in s["hist"] if r["id"] == "SAME_ID"]
                  if s["verdict"] != "REJECT":
                      res["C"].append(f"screen shows {s['verdict']} (want B's REJECT)")
                  if verdicts[:1] != ["REJECT"] or "ACCEPT" not in verdicts:
                      res["C"].append(f"history {verdicts} (want REJECT first, ACCEPT kept as antecedent)")
                  pg.reload(wait_until="domcontentloaded"); pg.wait_for_timeout(300)
                  v2 = [r["verdict"] for r in state(pg)["hist"] if r["id"] == "SAME_ID"]
                  if v2 != verdicts:
                      res["C"].append(f"after reload history {v2} != {verdicts}")
                  # B fails: A stays, and is not shown as B's evaluation
                  ctx.close(); ctx, pg, errs = fresh(); open_raw(pg); pg.evaluate("localStorage.removeItem('capas_decision_history_v1'); decisionHistory = []; renderHistory()")
                  run_single(pg, stat("FAIL_ID", p=0.01)); pg.wait_for_timeout(700)
                  pg.unroute("**/api/decide"); pg.route("**/api/decide", lambda r: r.abort())
                  run_single(pg, stat("FAIL_ID", p=0.3)); pg.wait_for_timeout(700)
                  s = state(pg)
                  if [r["verdict"] for r in s["hist"] if r["id"] == "FAIL_ID"] != ["ACCEPT"]:
                      res["C"].append(f"after B failed, history {[r['verdict'] for r in s['hist']]} (want A's ACCEPT only)")
                  if s["verdict"] == "ACCEPT":
                      res["C"].append("A's ACCEPT shown as the evaluation of B after B failed")
                  if errs: res["C"].append(f"page errors: {errs[:2]}")
                  ctx.close()

              except Exception as exc:   # a harness failure is recorded, never a pass
                  res["C"].append(f"harness error: {type(exc).__name__}: {str(exc).splitlines()[0][:160]}")
            # ---------------------------------------------------------------- D
            if "D" in only:
              try:
                  ctx, pg, errs = fresh(); open_raw(pg)
                  pg.evaluate("localStorage.removeItem('capas_decision_history_v1'); decisionHistory = []; renderHistory()")
                  bodies = {
                      "minimal ACCEPT": '{"verdict":"ACCEPT"}',
                      "invalid JSON": '{"verdict":',
                      "wrong types": None,
                      "other claim id": None,
                      "REJECT with licence": None,
                      "REJECT ready for training": None,
                      "REJECT with claim_licensed boundary": None,
                      "schema_errors not an array": None,
                      "missing_fields not an array": None,
                      "REJECT fine_tune_ready as a string": None,
                      "REJECT whose certificate says approve": None,
                      "ACCEPT ready with failed criteria": None,
                      "unsupported schema version": None,
                      "other claim text": None,
                      "v2 fields stripped": None,
                      # external re-audit b7685f1: READY with an incomplete or substituted criteria set
                      "READY with no criteria": None,
                      "READY with only verdict_accept": None,
                      "READY with one criterion dropped": None,
                      "READY with 14 invented criteria": None,
                      "READY without fine_tune_blockers": None,
                      "certificate removed": None,
                      # re-audit a853e2a: names merged into one key joined like the real set
                      "READY with two criteria merged into one key": None,
                      "READY with all criteria merged into one key": None,
                      "certificate dialectic empty": None,
                      # re-audit fa6d38f: READY while the same response lists schema errors / missing fields
                      "READY with a schema error listed": None,
                      "READY with a missing field listed": None,
                  }

                  def make_ready(d, criteria, blockers=True):
                      d["fine_tune_ready"] = True; d["fine_tune_criteria"] = criteria
                      if blockers: d["fine_tune_blockers"] = []
                      else: d.pop("fine_tune_blockers", None)
                      c = d["admissibility_certificate"]; c["lattice"]["reuse_boundary"] = "training_ready"
                      c["next_action"] = {"kind": "approve_for_controlled_reuse", "label": "Approve this claim boundary for controlled reuse."}

                  sys.path.insert(0, str(ROOT))
                  import capas   # genuine decisions of the local engine, mutated below (no route.fetch inside a handler)
                  full = {k: True for k in capas.FINE_TUNE_CRITERIA_LABELS}   # the engine's catalogue, all passed

                  def mutate(kind):
                      def h(route):
                          if bodies[kind] is not None:
                              route.fulfill(status=200, content_type="application/json", body=bodies[kind]); return
                          d = json.loads(json.dumps(capas.decide_external_claim(json.loads(route.request.post_data))))
                          if kind == "wrong types":
                              d["reason"] = 42; d["required_fields"] = "x"
                          elif kind == "other claim id":
                              d["input_claim"]["id"] = "somebody_else"
                          elif kind == "REJECT with licence":
                              d["licensed_claim"] = "The treatment works."
                          elif kind == "REJECT ready for training":
                              d["fine_tune_ready"] = True
                          elif kind == "schema_errors not an array":
                              d["schema_errors"] = "oops"
                          elif kind == "missing_fields not an array":
                              d["missing_fields"] = "oops"
                          elif kind == "REJECT fine_tune_ready as a string":
                              d["fine_tune_ready"] = "true"
                          elif kind == "REJECT with claim_licensed boundary":
                              d.setdefault("admissibility_certificate", {}).setdefault("lattice", {})["reuse_boundary"] = "claim_licensed"
                          elif kind == "REJECT whose certificate says approve":
                              c = d["admissibility_certificate"]
                              c["next_action"] = {"kind": "approve_for_controlled_reuse", "label": "Approve this claim for training."}
                              c["dialectic"]["thesis"] = "The treatment works."
                          elif kind == "ACCEPT ready with failed criteria":
                              d["fine_tune_ready"] = True          # criteria still false, blockers still listed
                          elif kind == "unsupported schema version":
                              d["schema_version"] = "unsupported-future-v999"
                          elif kind == "other claim text":
                              d["input_claim"]["text"] = "Something the request never said."
                          elif kind == "v2 fields stripped":
                              for k in ("audit_hash_recipe", "rules_fired", "rule_table_sha256", "evidence_sha256", "engine_version"):
                                  d.pop(k, None)
                          elif kind == "READY with no criteria":
                              make_ready(d, {})
                          elif kind == "READY with only verdict_accept":
                              make_ready(d, {"verdict_accept": True})
                          elif kind == "READY with one criterion dropped":
                              make_ready(d, {k: v for k, v in full.items() if k != "source_urls_recoverable_hashable"})
                          elif kind == "READY with 14 invented criteria":
                              make_ready(d, {f"made_up_{i}": True for i in range(len(full))})
                          elif kind == "READY without fine_tune_blockers":
                              make_ready(d, dict(full), blockers=False)
                          elif kind == "certificate removed":
                              d.pop("admissibility_certificate", None)
                          elif kind == "READY with two criteria merged into one key":
                              names = sorted(full); merged = dict(full); a, b = names[0], names[1]
                              merged.pop(a); merged.pop(b); merged[a + "|" + b] = True
                              make_ready(d, merged)
                          elif kind == "READY with all criteria merged into one key":
                              make_ready(d, {"|".join(sorted(full)): True})
                          elif kind == "certificate dialectic empty":
                              d["admissibility_certificate"]["dialectic"] = {}
                          elif kind == "READY with a schema error listed":
                              make_ready(d, dict(full)); d["schema_errors"] = ["evidence.p_value: expected number"]
                          elif kind == "READY with a missing field listed":
                              make_ready(d, dict(full)); d["missing_fields"] = ["alpha"]
                          elif kind == "READY control (full criteria set)":
                              make_ready(d, dict(full))
                          route.fulfill(status=200, content_type="application/json", body=json.dumps(d))
                      return h
                  for kind in bodies:
                      pg.unroute("**/api/decide"); pg.route("**/api/decide", mutate(kind))
                      payload = stat("D_" + kind.replace(" ", "_"), p=0.3 if "REJECT" in kind else 0.01)
                      if kind == "missing_fields not an array":
                          payload["evidence"].pop("effect_direction_confirmed")   # a genuine HOLD
                      run_single(pg, payload); pg.wait_for_timeout(600)
                      s = state(pg)
                      if not s["copy_disabled"] or s["verdict"] in ("ACCEPT", "REWRITE") and kind != "invalid JSON":
                          res["D"].append(f"{kind}: shown verdict {s['verdict']}, copy disabled={s['copy_disabled']}")
                      if "undefined" in s["area"]:
                          res["D"].append(f"{kind}: 'undefined' rendered")
                      if any(r["id"] == payload["claim"]["id"] for r in s["hist"]):
                          res["D"].append(f"{kind}: recorded in the decision log")
                  # positive control for the mutations: the engine's full criteria set, all true, passes as READY
                  bodies["READY control (full criteria set)"] = None
                  pg.unroute("**/api/decide"); pg.route("**/api/decide", mutate("READY control (full criteria set)"))
                  run_single(pg, stat("D_READY_CONTROL")); pg.wait_for_timeout(600)
                  s = state(pg)
                  if s["verdict"] != "ACCEPT" or s["copy_disabled"] or "READY" not in s["area"] or "NOT READY" in s["area"]:
                      res["D"].append(f"READY control: shown {s['verdict']}, copy disabled={s['copy_disabled']}")
                  # batch: an item whose response sends {} as its criteria is never counted FT READY
                  def batch_route(route):
                      d = json.loads(json.dumps(capas.decide_external_claim(json.loads(route.request.post_data))))
                      if d["input_claim"]["id"] == "D_BATCH_EMPTY": make_ready(d, {})
                      if d["input_claim"]["id"] == "D_BATCH_MERGED": make_ready(d, {"|".join(sorted(full)): True})
                      if d["input_claim"]["id"] == "D_BATCH_SCHEMA": make_ready(d, dict(full)); d["schema_errors"] = ["evidence.p_value: expected number"]
                      if d["input_claim"]["id"] == "D_BATCH_MISSING": make_ready(d, dict(full)); d["missing_fields"] = ["alpha"]
                      route.fulfill(status=200, content_type="application/json", body=json.dumps(d))
                  pg.unroute("**/api/decide"); pg.route("**/api/decide", batch_route)
                  select_mode(pg, "batch"); run_single(pg, [stat("D_BATCH_EMPTY"), stat("D_BATCH_MERGED"), stat("D_BATCH_SCHEMA"), stat("D_BATCH_MISSING"), stat("D_BATCH_OK")]); pg.wait_for_timeout(1400)
                  bo = pg.evaluate("(() => { try { return JSON.parse(document.getElementById('output').textContent); } catch (_) { return {}; } })()")
                  items = {(r.get("result") or {}).get("input_claim", {}).get("id"): r for r in bo.get("results", [])}
                  for bid in ("D_BATCH_EMPTY", "D_BATCH_MERGED", "D_BATCH_SCHEMA", "D_BATCH_MISSING"):
                      bad = items.get(bid) or {}
                      if (bad.get("result") or {}).get("fine_tune_ready") is True or bo.get("fine_tune_ready") is True:
                          res["D"].append(f"batch: {bid} counted READY (status {bad.get('status')})")
                  if "FT READY" in pg.locator("#verdict-area").inner_text():
                      res["D"].append("batch: 'FT READY' shown for an item with empty criteria")
                  select_mode(pg, "raw")
                  pg.unroute("**/api/decide")
                  # positive controls: the four genuine verdicts complete (shown, recorded, exportable)
                  for name in ("ACCEPT", "REWRITE", "REJECT", "HOLD"):
                      step(pg, "gate")
                      if not pg.locator(".samples-drawer[open]").count():
                          pg.click(".samples-drawer summary")
                      pg.click(f"button[aria-label='Load {name} sample']"); pg.wait_for_timeout(800)
                      s = state(pg)
                      if s["verdict"] != name or s["copy_disabled"]:
                          res["D"].append(f"genuine {name}: shown {s['verdict']}, copy disabled={s['copy_disabled']}")
                  if errs: res["D"].append(f"page errors: {errs[:2]}")
                  ctx.close()

              except Exception as exc:   # a harness failure is recorded, never a pass
                  res["D"].append(f"harness error: {type(exc).__name__}: {str(exc).splitlines()[0][:160]}")
            # ---------------------------------------------------------------- E
            if "E" in only:
              try:
                  for kind in ("500", "429", "abort"):
                      ctx, pg, errs = fresh(); open_raw(pg)
                      code = None if kind == "abort" else int(kind)
                      def responder(c):
                          def h(route):
                              route.abort() if c is None else route.fulfill(status=c, body="{}")
                          return h
                      pg.route("**/api/decide", responder(code))
                      run_single(pg, stat("E_" + kind)); pg.wait_for_timeout(700)
                      s = state(pg)
                      txt = (s["status"] + " " + s["area"]).lower()
                      for bad in ("evidence evaluated", "schema checked", "hold complete", "gate complete"):
                          if bad in txt:
                              res["E"].append(f"{kind}: claims {bad!r} although the engine did not run")
                      if not s["copy_disabled"]:
                          res["E"].append(f"{kind}: fallback exportable")
                      ctx.close()
                  for fail_all in (True, False):
                      ctx, pg, errs = fresh(); open_raw(pg); select_mode(pg, "batch")
                      def batch_responder(all_fail):
                          def h(route):
                              body = route.request.post_data or ""
                              if all_fail or "E_B2" in body:
                                  route.fulfill(status=500, body="{}")
                              else:
                                  route.continue_()
                          return h
                      pg.route("**/api/decide", batch_responder(fail_all))
                      run_single(pg, [stat("E_B1"), stat("E_B2")]); pg.wait_for_timeout(900)
                      s = state(pg); txt = (s["status"] + " " + s["area"]).lower()
                      tag = "batch all-failed" if fail_all else "batch partial"
                      for bad in ("gate complete", "items evaluated with deterministic", "2/2 claims"):
                          if bad in txt:
                              res["E"].append(f"{tag}: claims {bad!r}")
                      if fail_all and not s["copy_disabled"]:
                          res["E"].append(f"{tag}: exportable although nothing was decided")
                      if "partial" not in txt and not fail_all:
                          res["E"].append(f"{tag}: not identified as partial")
                      ctx.close()

              except Exception as exc:   # a harness failure is recorded, never a pass
                  res["E"].append(f"harness error: {type(exc).__name__}: {str(exc).splitlines()[0][:160]}")
            # ---------------------------------------------------------------- F
            if "F" in only:
              try:
                  for storage in (None, {"capas_theme_v1": "light", "capas-theme": "light"}):
                      ctx, pg, errs = fresh(scheme="light", storage=storage)
                      pg.goto(base + "/app.html", wait_until="domcontentloaded"); pg.wait_for_timeout(300)
                      v = pg.evaluate("(() => { const c = getComputedStyle(document.documentElement); return [document.documentElement.dataset.theme, c.getPropertyValue('--bg').trim(), c.getPropertyValue('--text-1').trim(), getComputedStyle(document.querySelector('pre#output') || document.body).backgroundColor]; })()")
                      if v[1].lower() in ("#ffffff", "#fff") or v[2].lower() == "#09090b":
                          res["F"].append(f"system light{' + stored light' if storage else ''}: theme={v[0]} --bg={v[1]} --text-1={v[2]}")
                      ctx.close()

              except Exception as exc:   # a harness failure is recorded, never a pass
                  res["F"].append(f"harness error: {type(exc).__name__}: {str(exc).splitlines()[0][:160]}")
            # ---------------------------------------------------------------- G
            if "G" in only:
              try:
                  for page in ("app.html", "index.html", "audit.html", "benchmark.html", "governance.html", "security.html",
                               "pilot-packet.html", "customer-brief.html", "in-depth.html"):
                      for w in (320, 390, 768, 1024, 1440):
                          ctx, pg, errs = fresh(width=w)
                          pg.goto(f"{base}/{page}", wait_until="domcontentloaded"); pg.wait_for_timeout(250)
                          g = pg.evaluate("""(() => { const nav = document.querySelector('nav'), links = document.querySelector('nav .nav-links'), sub = document.querySelector('.subnav');
                              const r = e => e ? e.getBoundingClientRect() : null; const n = r(nav), l = r(links), s = r(sub);
                              const lang = r(document.querySelector('nav [data-lang-btn]')); const last = r([...document.querySelectorAll('nav .nav-links a')].pop());
                              return {doc: document.documentElement.scrollWidth, vw: innerWidth, navB: n.bottom, linksB: l ? l.bottom : 0, subT: s ? s.top : null,
                                      langR: lang ? lang.right : 0, lastR: last ? last.right : 0}; })()""")
                          tag = f"{page}@{w}"
                          if g["doc"] > g["vw"] + 1:
                              res["G"].append(f"{tag}: document {g['doc']}px wider than viewport {g['vw']}")
                          if g["linksB"] > g["navB"] + 1:
                              res["G"].append(f"{tag}: nav links end at {g['linksB']:.0f} below the nav box {g['navB']:.0f}")
                          if g["subT"] is not None and g["subT"] < g["navB"] - 1:
                              res["G"].append(f"{tag}: subnav starts at {g['subT']:.0f} inside the nav ({g['navB']:.0f})")
                          clipped = pg.evaluate("""(w) => { const out = []; for (const e of document.querySelectorAll('body *')) {
                              const cs = getComputedStyle(e); if (cs.position === 'fixed' || cs.display === 'none' || e.closest('.bg-logo')) continue;
                              const r = e.getBoundingClientRect(); if (!(r.width > 0 && r.right > w + 2)) continue;
                              let a = e.parentElement, inBox = false; while (a && a !== document.body) { if (getComputedStyle(a).overflowX !== 'visible') { inBox = true; break; } a = a.parentElement; }
                              if (inBox) continue; const pr = e.parentElement.getBoundingClientRect(); if (pr.right > w + 2) continue;
                              out.push((e.className && typeof e.className === 'string' ? e.className : e.tagName) + '@' + Math.round(r.right)); }
                              return out.slice(0, 3); }""", g["vw"])
                          if clipped:
                              res["G"].append(f"{tag}: content beyond the viewport, clipped by the page: {clipped}")
                          if g["langR"] > g["vw"] + 1 or g["lastR"] > g["vw"] + 1:
                              res["G"].append(f"{tag}: language toggle or last link outside the viewport")
                          ctx.close()

              except Exception as exc:   # a harness failure is recorded, never a pass
                  res["G"].append(f"harness error: {type(exc).__name__}: {str(exc).splitlines()[0][:160]}")
            # ---------------------------------------------------------------- H
            if "H" in only:
              try:
                  for w in (1440, 390):
                      for mode in ("guided", "raw", "batch", "ingestion"):
                          for phase in ("gate",):
                              ctx, pg, errs = fresh(width=w, height=900)
                              pg.goto(base + "/app.html", wait_until="domcontentloaded"); pg.wait_for_timeout(250)
                              select_mode(pg, mode, phase); pg.wait_for_timeout(150)
                              v = pg.evaluate("""(() => { const vis = e => { if (!e) return false; const r = e.getBoundingClientRect(), cs = getComputedStyle(e);
                                      return r.width > 0 && r.height > 0 && cs.visibility !== 'hidden' && cs.display !== 'none' && +cs.opacity > 0.3; };
                                  const runs = [...document.querySelectorAll('#phase-run, #decide-btn, #batch-btn')].filter(vis);
                                  const notes = [...document.querySelectorAll('[data-submit-notice]')].filter(vis);
                                  return {runs: runs.map(e => e.id), notes: notes.length,
                                          near: runs.every(b => notes.some(n => { const a = b.getBoundingClientRect(), c = n.getBoundingClientRect();
                                               return Math.abs((a.top + a.bottom) / 2 - (c.top + c.bottom) / 2) < 160; }))}; })()""")
                              if v["runs"] and not (v["notes"] and v["near"]):
                                  res["H"].append(f"{mode}/{phase}@{w}: run controls {v['runs']} without a visible submission notice beside them")
                              ctx.close()

              except Exception as exc:   # a harness failure is recorded, never a pass
                  res["H"].append(f"harness error: {type(exc).__name__}: {str(exc).splitlines()[0][:160]}")
            # ---------------------------------------------------------------- I
            if "I" in only:
              try:
                  good = None
                  ctx, pg, errs = fresh(); open_raw(pg)
                  pg.evaluate("localStorage.removeItem('capas_decision_history_v1'); decisionHistory = []; renderHistory()")
                  run_single(pg, stat("I_GOOD")); pg.wait_for_timeout(800)
                  good = state(pg)["hist"]
                  bad = json.loads(json.dumps(good[0])) if good else None
                  if bad:
                      bad["id"] = "I_BAD"; bad["payload"] = bad["payload"].replace("I_GOOD", "I_BAD"); bad["decision"]["input_claim"]["id"] = "I_BAD"
                      bad["decision"]["audit_hash"] = "sha256:not-a-real-hash"
                      pg.evaluate("rows => localStorage.setItem('capas_decision_history_v1', JSON.stringify(rows))", [bad] + good)
                  pg.goto(base + "/audit.html", wait_until="domcontentloaded"); pg.wait_for_timeout(300)
                  rows = pg.evaluate("[...document.querySelectorAll('#rows tr')].map(r => r.innerText)")
                  if any("I_BAD" in r and "ACCEPT" in r and "not trusted" not in r.lower() and "no confiable" not in r.lower() for r in rows):
                      res["I"].append("malformed-hash record listed as a trusted ACCEPT")
                  cnt_en = pg.locator("#count").inner_text()
                  pg.click("[data-lang-btn]"); pg.wait_for_timeout(250)
                  cnt_es = pg.locator("#count").inner_text()
                  n_rows = pg.evaluate("[...document.querySelectorAll('#rows tr')].filter(r => !r.querySelector('.empty')).length")
                  if cnt_es.strip().startswith("0") and n_rows:
                      res["I"].append(f"Spanish count {cnt_es!r} while {n_rows} row(s) are shown (English: {cnt_en!r})")
                  pg.click("[data-lang-btn]"); pg.wait_for_timeout(200)
                  if pg.locator("#count").inner_text() != cnt_en:
                      res["I"].append("count changed after ES -> EN round trip")
                  # a failed write is never shown as saved: the row stays and the page says the change was not saved
                  n_before = pg.evaluate("[...document.querySelectorAll('#rows tr')].filter(r => !r.querySelector('.empty')).length")
                  pg.evaluate("() => { Storage.prototype.setItem = function () { throw new Error('quota'); }; return true; }")
                  pg.locator("#rows [data-delete]").first.click(); pg.wait_for_timeout(200)
                  n_after = pg.evaluate("[...document.querySelectorAll('#rows tr')].filter(r => !r.querySelector('.empty')).length")
                  if n_after != n_before:
                      res["I"].append(f"delete with failing storage removed a row from view ({n_before} -> {n_after}) although nothing was saved")
                  if "could not be saved" not in pg.locator("#count").inner_text() and "No se pudo guardar" not in pg.locator("#count").inner_text():
                      res["I"].append("failed write not reported")
                  stored = json.loads(pg.evaluate("localStorage.getItem('capas_decision_history_v1')") or "[]")
                  quarantine = pg.evaluate("localStorage.getItem('capas_decision_history_quarantine_v1')")
                  if not any(r.get("id") == "I_BAD" for r in stored) and not (quarantine and "I_BAD" in quarantine):
                      res["I"].append("invalid record deleted silently (neither kept nor set aside)")
                  ctx.close()

              except Exception as exc:   # a harness failure is recorded, never a pass
                  res["I"].append(f"harness error: {type(exc).__name__}: {str(exc).splitlines()[0][:160]}")
            # ---------------------------------------------------------------- J
            if "J" in only:
              try:
                  ctx, pg, errs = fresh(); pg.goto(base + "/app.html", wait_until="domcontentloaded"); pg.wait_for_timeout(300)
                  select_mode(pg, "guided", "complete")
                  pg.select_option("#guided-type", "proof_admissibility"); pg.wait_for_timeout(150)
                  for sel in pg.query_selector_all("#guided-fields select")[:1]:
                      sel.select_option("true")          # a generated control: a CSP-blocked handler would surface as an error
                  pg.fill("#guided-claim-text", "")
                  pg.click("button:has-text('Build guided payload')"); pg.wait_for_timeout(300)
                  if errs:
                      res["J"].append(f"exception: {errs[0][:120]}")
                  msg = pg.evaluate("(() => { const e = document.querySelector('[data-field-error=\"guided-claim-text\"]'); return e && e.offsetParent !== null ? e.innerText : ''; })()")
                  if not msg:
                      res["J"].append("no visible validation beside the claim text field")
                  try:
                      built = json.loads(pg.evaluate("document.getElementById('input').value") or "{}")
                      if (built.get("claim") or {}).get("type") == "proof_admissibility" and built["claim"].get("text"):
                          res["J"].append(f"a claim text was invented: {built['claim']['text'][:60]!r}")
                  except json.JSONDecodeError:
                      pass
                  ctx.close()
              except Exception as exc:   # a harness failure is recorded, never a pass
                  res["J"].append(f"harness error: {type(exc).__name__}: {str(exc).splitlines()[0][:160]}")
            # ---------------------------------------------------------------- K
            if "K" in only:
              try:
                  # 1. type, then Ctrl+Enter at once: one request, no edit after it -> still current after the debounce
                  for i in range(3):
                      ctx, pg, errs = fresh(); open_raw(pg)
                      h = Held(pg); n0 = len(h.seen)
                      step(pg, "complete"); pg.fill("#input", json.dumps(stat(f"K_FAST_{i}")))
                      pg.press("#input", "Control+Enter")
                      h.pump(lambda: state(pg)["shown"] == f"K_FAST_{i}"); pg.wait_for_timeout(600)   # past the 300 ms debounce
                      s = state(pg)
                      if s["shown"] != f"K_FAST_{i}" or s["stale"] or s["copy_disabled"]:
                          res["K"].append(f"fast run {i}: shown={s['shown']} stale={s['stale']} copy_disabled={s['copy_disabled']}")
                      if len(h.seen) - n0 != 1:
                          res["K"].append(f"fast run {i}: {len(h.seen) - n0} requests")
                      ctx.close()
                  # A -> B -> A still marks the old result stale (no revival by equal text)
                  ctx, pg, errs = fresh(); open_raw(pg)
                  a = json.dumps(stat("K_ABA")); run_single(pg, a); pg.wait_for_timeout(700)
                  step(pg, "complete"); pg.fill("#input", a + " "); pg.wait_for_timeout(50); pg.fill("#input", a); pg.wait_for_timeout(500)
                  s = state(pg)
                  if not (s["stale"] and s["copy_disabled"]):
                      res["K"].append("A -> B -> A revived the earlier result")
                  ctx.close()
                  # 2. math text is recorded and shown as text, not markup
                  ctx, pg, errs = fresh(); open_raw(pg)
                  pg.evaluate("localStorage.removeItem('capas_decision_history_v1'); decisionHistory = []; renderHistory()")
                  for cid, text in (("K_MATH", "The error is < 0.01."), ("K_MARKUP", "x <img src=x onerror=\"window.__pwned=1\"> < 1")):
                      run_single(pg, stat(cid, text=text)); pg.wait_for_timeout(700)
                      s = state(pg)
                      if not any(r["id"] == cid for r in s["hist"]):
                          res["K"].append(f"{cid}: not recorded in the decision log")
                  pg.goto(base + "/audit.html", wait_until="domcontentloaded"); pg.wait_for_timeout(400)
                  if pg.evaluate("!!window.__pwned || !!document.querySelector('img[src=x]')"):
                      res["K"].append("claim text executed as markup")
                  if errs: res["K"].append(f"page errors: {errs[:2]}")
                  ctx.close()
                  # 3. at 390 px the decision panel uses the full gate column (P1-05)
                  ctx, pg, errs = fresh(width=390, height=900); open_raw(pg)
                  run_single(pg, stat("K_MOBILE", p=0.3)); pg.wait_for_timeout(800)
                  m = pg.evaluate("""(() => { const g = document.querySelector('#gate > .grid'), v = document.getElementById('verdict-area');
                      return {grid: g.getBoundingClientRect().width, panel: v.getBoundingClientRect().width,
                              cols: getComputedStyle(g).gridTemplateColumns}; })()""")
                  if m["panel"] < 0.85 * m["grid"]:
                      res["K"].append(f"390 px: decision panel {m['panel']:.0f}px of a {m['grid']:.0f}px gate (columns {m['cols']})")
                  ctx.close()
              except Exception as exc:   # a harness failure is recorded, never a pass
                  res["K"].append(f"harness error: {type(exc).__name__}: {str(exc).splitlines()[0][:160]}")
            br.close()
    finally:
        srv.terminate()
    bad = {k: v for k, v in res.items() if v and k in only}
    for k in sorted(only):
        print(f"{k}: {'PASS' if not res[k] else 'FAIL'}" + ("".join(f"\n   - {m}" for m in res[k]) if res[k] else ""))
    if "--json" in sys.argv:
        Path(sys.argv[sys.argv.index("--json") + 1]).write_text(json.dumps(res, indent=1), encoding="utf-8")
    print("PASS — Gate App contract A-K" if not bad else f"FAIL — {len(bad)} case(s): {', '.join(sorted(bad))}")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
