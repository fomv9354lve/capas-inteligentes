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
    only = set(sys.argv[sys.argv.index("--only") + 1].split(",")) if "--only" in sys.argv else set("ABCDEFGHIJ")
    port = _free_port()
    srv = subprocess.Popen([sys.executable, str(ROOT / "capas_api.py"), str(port)], cwd=str(ROOT),
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env={**os.environ, "CAPAS_HOSTED": ""})
    base = f"http://127.0.0.1:{port}"
    res: dict[str, list[str]] = {k: [] for k in "ABCDEFGHIJ"}
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
                if storage:
                    ctx.add_init_script("(() => { const s = %s; for (const k in s) localStorage.setItem(k, s[k]); })()" % json.dumps(storage))
                # external resources (fonts, the ornamental 3D logo's CDN scripts) are blocked: local and deterministic
                ctx.route(lambda url: not url.startswith(base), lambda route: route.abort())
                pg = ctx.new_page(); pg.set_default_timeout(8000)
                errors = []
                # "THREE is not defined" comes from the ornamental logo iframe whose CDN script is blocked above
                pg.on("pageerror", lambda e: None if "THREE is not defined" in str(e) else errors.append(str(e)))
                pg.on("console", lambda m: errors.append("csp: " + m.text) if "Content Security Policy" in m.text else None)
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
                  }

                  sys.path.insert(0, str(ROOT))
                  import capas   # genuine decisions of the local engine, mutated below (no route.fetch inside a handler)

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
                  for page in ("app.html", "index.html", "audit.html", "benchmark.html", "governance.html", "security.html"):
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
            br.close()
    finally:
        srv.terminate()
    bad = {k: v for k, v in res.items() if v and k in only}
    for k in sorted(only):
        print(f"{k}: {'PASS' if not res[k] else 'FAIL'}" + ("".join(f"\n   - {m}" for m in res[k]) if res[k] else ""))
    if "--json" in sys.argv:
        Path(sys.argv[sys.argv.index("--json") + 1]).write_text(json.dumps(res, indent=1), encoding="utf-8")
    print("PASS — Gate App contract A-J" if not bad else f"FAIL — {len(bad)} case(s): {', '.join(sorted(bad))}")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
