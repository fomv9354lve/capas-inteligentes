/* capas-records.js — one validator for engine responses and decision-log records, shared by app.html and audit.html
   (external re-audit fb52d8c, cases D and I). Generated contract data comes from capas-contracts.js
   (scripts/gen_gate_contracts.py, from the engine); this file holds only the checks.

   What it checks, and what it does not:
     - structure, types and the operational combinations the engine actually produces (verdict x licence x
       reuse boundary x next action x thesis x training readiness, criteria and blockers), and that the response
       carries the claim the request sent (id, type, text and the rest of the claim object);
     - for live responses only, the schema version and the v2 recipe fields (old log records keep a separate path);
     - the audit_hash FORMAT. The browser does not recompute the hash (that needs the engine's canonical JSON; use
       POST /api/gate/verify or capas_check.py), and a hash that matches proves the covered fields are unchanged,
       not who produced them. Fields outside the v2 hash body (licensed_claim, fine_tune_ready, the certificate)
       are covered here by the combination checks only.
   localStorage is not immutable: a record that passes is "format-checked", never "verified". */
(function () {
  "use strict";
  var VERDICTS = ["ACCEPT", "REWRITE", "REJECT", "HOLD"];
  var SHA = /^sha256:[0-9a-f]{64}$/;
  var C = (window.CAPAS_CONTRACTS && window.CAPAS_CONTRACTS.response_contract) || null;

  function isObj(v) { return !!v && typeof v === "object" && !Array.isArray(v); }
  function isStrArr(v) { return Array.isArray(v) && v.every(function (x) { return typeof x === "string"; }); }

  /* Canonical JSON (sorted keys) for the equality checks below. Equality of content, never proof of origin. */
  function canon(v) {
    if (Array.isArray(v)) return "[" + v.map(canon).join(",") + "]";
    if (isObj(v)) return "{" + Object.keys(v).sort().map(function (k) { return JSON.stringify(k) + ":" + canon(v[k]); }).join(",") + "}";
    return JSON.stringify(v === undefined ? null : v);
  }

  /* Engine response contract. Returns {ok, problems[]}. `request` is the payload object that was sent.
     opts.live (default true): a response that just came over the network must carry exactly the schema version and
     audit-hash recipe the engine emits today, with every v2 field. opts.live = false is the separate path for records
     already in the decision log (older recipes stay readable there); the operational combination checks apply to both.
     External re-audit d2bce91, P1-01 and P1-02. */
  function checkResponse(r, request, opts) {
    var live = !(opts && opts.live === false);
    var p = [];
    if (!isObj(r)) return { ok: false, problems: ["response is not a JSON object"] };
    if (r.error) p.push("response carries an error field");
    if (VERDICTS.indexOf(r.verdict) < 0) p.push("verdict is not one of ACCEPT, REWRITE, REJECT, HOLD");
    if (typeof r.schema_version !== "string") p.push("schema_version missing");
    if (live) {
      var versions = (C && C.schema_versions) || [];
      if (typeof r.schema_version === "string" && versions.indexOf(r.schema_version) < 0) p.push("unsupported schema_version " + r.schema_version);
      ((C && C.required_v2) || []).forEach(function (k) { if (r[k] === undefined) p.push(k + " missing (live responses use recipe v2)"); });
    }
    if (!isObj(r.input_claim)) p.push("input_claim missing");
    if (typeof r.reason !== "string" || !r.reason.trim()) p.push("reason missing or not a string");
    if (!Array.isArray(r.required_fields)) p.push("required_fields is not an array");
    if (typeof r.audit_hash !== "string" || !SHA.test(r.audit_hash)) p.push("audit_hash is not sha256:<64 hex>");
    if (r.audit_hash_recipe !== undefined) {
      if (r.audit_hash_recipe !== "v2") p.push("unknown audit_hash_recipe " + String(r.audit_hash_recipe));
      if (!isStrArr(r.rules_fired) || !r.rules_fired.length) p.push("rules_fired missing (recipe v2)");
      if (typeof r.rule_table_sha256 !== "string" || !SHA.test(r.rule_table_sha256)) p.push("rule_table_sha256 malformed");
      if (typeof r.evidence_sha256 !== "string" || !SHA.test(r.evidence_sha256)) p.push("evidence_sha256 malformed");
      if (typeof r.engine_version !== "string") p.push("engine_version missing");
      if (r.notices !== undefined && !isStrArr(r.notices)) p.push("notices is not a string array");
    }
    // types of the operational fields the UI renders (verifier pass: string values here crashed rendering or showed
    // a REJECT as "FT READY")
    [["schema_errors", isStrArr], ["missing_fields", isStrArr], ["fine_tune_blockers", isStrArr]].forEach(function (f) {
      if (r[f[0]] !== undefined && !f[1](r[f[0]])) p.push(f[0] + " is not a string array");
    });
    ["fine_tune_ready", "text_licensed_as_written"].forEach(function (k) {
      if (r[k] !== undefined && typeof r[k] !== "boolean") p.push(k + " is not a boolean");
    });
    ["licensed_claim", "rewrite"].forEach(function (k) {
      if (r[k] !== undefined && r[k] !== null && typeof r[k] !== "string") p.push(k + " is not a string or null");
    });
    if (r.admissibility_certificate !== undefined && !isObj(r.admissibility_certificate)) p.push("admissibility_certificate is not an object");
    if (r.fine_tune_criteria !== undefined && !isObj(r.fine_tune_criteria)) p.push("fine_tune_criteria is not an object");
    if (r.input_claim !== undefined && isObj(r.input_claim) && (typeof r.input_claim.id !== "string" || typeof r.input_claim.type !== "string")) p.push("input_claim id/type are not strings");
    if (isObj(request) && isObj(request.claim) && isObj(r.input_claim)) {
      if (r.input_claim.id !== request.claim.id) p.push("response names another claim id than the request");
      if (r.input_claim.type !== request.claim.type) p.push("response names another claim type than the request");
      if (r.input_claim.text !== request.claim.text) p.push("response claim text differs from the request");
      else if (canon(r.input_claim) !== canon(request.claim)) p.push("response input_claim differs from the request claim");
    }
    // operational combinations (outside the v2 hash body; the engine never produces these)
    var cert = isObj(r.admissibility_certificate) ? r.admissibility_certificate : null;
    var boundary = cert && isObj(cert.lattice) ? cert.lattice.reuse_boundary : undefined;
    if (r.verdict !== "ACCEPT" && r.fine_tune_ready === true) p.push(r.verdict + " marked fine_tune_ready");
    if ((r.verdict === "REJECT" || r.verdict === "HOLD") && r.licensed_claim) p.push(r.verdict + " carries a licensed claim");
    if (C && C.reuse_boundary_by_verdict && boundary !== undefined) {
      var allowed = C.reuse_boundary_by_verdict[r.verdict] || [];
      if (allowed.indexOf(boundary) < 0) p.push(r.verdict + " with reuse boundary " + boundary);
    }
    if (r.verdict === "ACCEPT" && r.text_licensed_as_written === undefined && r.audit_hash_recipe === "v2") p.push("ACCEPT without text_licensed_as_written");
    // training readiness: the flag, the criteria and the blockers must say the same thing (the engine sets
    // fine_tune_ready = no blockers, one blocker per failed criterion)
    if (typeof r.fine_tune_ready === "boolean" && isObj(r.fine_tune_criteria)) {
      var vals = Object.keys(r.fine_tune_criteria).map(function (k) { return r.fine_tune_criteria[k]; });
      if (!vals.every(function (v) { return typeof v === "boolean"; })) p.push("fine_tune_criteria values are not booleans");
      var failed = vals.filter(function (v) { return v !== true; }).length;
      var nBlock = isStrArr(r.fine_tune_blockers) ? r.fine_tune_blockers.length : null;
      if (r.fine_tune_ready && (failed > 0 || nBlock)) p.push("fine_tune_ready true with failed criteria or blockers");
      if (!r.fine_tune_ready && failed === 0 && !nBlock) p.push("fine_tune_ready false with every criterion passed and no blocker");
      if (nBlock !== null && nBlock !== failed) p.push("fine_tune_blockers do not match the failed criteria");
    } else if (r.fine_tune_ready === true && live) p.push("fine_tune_ready true without fine_tune_criteria");
    if (cert) {
      if (boundary === "training_ready" && r.fine_tune_ready !== true) p.push("reuse boundary training_ready without fine_tune_ready");
      if (r.fine_tune_ready === true && boundary !== undefined && boundary !== "training_ready") p.push("fine_tune_ready with reuse boundary " + boundary);
      var action = isObj(cert.next_action) ? cert.next_action.kind : undefined;
      if (live && cert.next_action !== undefined && typeof action !== "string") p.push("certificate next_action has no kind");
      if (typeof action === "string" && C && C.next_action_by_verdict) {
        if ((C.next_action_by_verdict[r.verdict] || []).indexOf(action) < 0) p.push(r.verdict + " with next action " + action);
        else if (action === "approve_for_controlled_reuse" && r.fine_tune_ready !== true) p.push("approve_for_controlled_reuse without fine_tune_ready");
        else if (action === "verify_provenance_for_training" && r.fine_tune_ready === true) p.push("verify_provenance_for_training with fine_tune_ready");
      }
      var dia = isObj(cert.dialectic) ? cert.dialectic : null;
      if (dia && isObj(r.input_claim) && dia.thesis !== undefined && dia.thesis !== r.input_claim.text) p.push("certificate thesis differs from the claim text");
      if (dia && dia.licensed_thesis !== undefined && (dia.licensed_thesis || null) !== (r.licensed_claim || null)) p.push("certificate licensed thesis differs from licensed_claim");
    }
    return { ok: p.length === 0, problems: p };
  }

  /* Decision-log record. trust: "format_checked" (passes every check) | "invalid" (kept, set aside, never shown as a
     decision). Legacy records (no run metadata, or recipe v1) stay format_checked with their provenance as found. */
  function checkRecord(e) {
    var p = [];
    if (!isObj(e)) return { trust: "invalid", problems: ["not an object"] };
    if (VERDICTS.indexOf(e.verdict) < 0) p.push("verdict");
    if (typeof e.id !== "string" || !e.id.trim() || e.id === "-" || /[<>⟨˂˃‹›\u0000-\u001f]/.test(e.id)) p.push("id");
    if (typeof e.reason !== "string" || !e.reason.trim()) p.push("reason");
    if (typeof e.timestamp !== "string" || isNaN(new Date(e.timestamp).getTime())) p.push("timestamp");
    if (typeof e.payload !== "string") p.push("payload");
    if (!isObj(e.decision)) p.push("decision");
    else {
      if (e.decision.verdict !== e.verdict) p.push("decision.verdict differs");
      if (typeof e.decision.audit_hash !== "string" || !SHA.test(e.decision.audit_hash)) p.push("audit_hash format");
      try {
        var pl = JSON.parse(e.payload);
        if (!isObj(pl) || !isObj(pl.claim) || pl.claim.id !== e.id) p.push("payload claim id differs");
        // claim.text is kept as written ("The error is < 0.01." is legitimate, external re-audit d2bce91 P1-04);
        // every renderer of the log escapes it (escHtml / esc / textContent), benchmarks/verify_gate_app_contract.py K.
        var rc = checkResponse(e.decision, pl, { live: false });
        rc.problems.forEach(function (x) { if (x.indexOf("audit_hash") < 0) p.push(x); });
      } catch (_) { p.push("payload is not JSON"); }
    }
    return { trust: p.length ? "invalid" : "format_checked", problems: p };
  }

  /* Split stored rows into trusted (format-checked) and set-aside; never deletes. Idempotent. */
  function partition(rows) {
    var ok = [], bad = [];
    (Array.isArray(rows) ? rows : []).forEach(function (r) {
      var c = checkRecord(r);
      if (c.trust === "format_checked") ok.push(r); else bad.push({ record: r, problems: c.problems, set_aside_at: new Date().toISOString() });
    });
    return { ok: ok, bad: bad };
  }

  var KEY = "capas_decision_history_v1", QKEY = "capas_decision_history_quarantine_v1";
  /* Load the log: invalid rows are MOVED to the quarantine key (with their problems), not deleted. */
  function load() {
    var raw, parsed;
    try { raw = localStorage.getItem(KEY); parsed = raw ? JSON.parse(raw) : []; } catch (_) { return { rows: [], setAside: quarantined(), unreadable: true }; }
    var parts = partition(parsed);
    if (parts.bad.length) {
      try {
        var q = quarantined().concat(parts.bad);
        localStorage.setItem(QKEY, JSON.stringify(q.slice(-200)));
        localStorage.setItem(KEY, JSON.stringify(parts.ok));
      } catch (_) { /* leave storage as it was: nothing is lost */ }
    }
    return { rows: parts.ok, setAside: quarantined(), unreadable: false };
  }
  function quarantined() {
    try { var q = JSON.parse(localStorage.getItem(QKEY) || "[]"); return Array.isArray(q) ? q : []; } catch (_) { return []; }
  }
  /* Returns true only when the write succeeded. */
  function save(rows) {
    try { localStorage.setItem(KEY, JSON.stringify(rows)); return localStorage.getItem(KEY) === JSON.stringify(rows); } catch (_) { return false; }
  }
  /* Newest REQUEST first (request_seq, then timestamp for legacy rows). */
  function order(rows) {
    return rows.slice().sort(function (a, b) {
      var ra = a.run && a.run.requested_at || a.timestamp, rb = b.run && b.run.requested_at || b.timestamp;
      if (ra !== rb) return ra < rb ? 1 : -1;
      return ((b.run && b.run.seq) || 0) - ((a.run && a.run.seq) || 0);
    });
  }
  /* Re-render on language change without letting lang.js restore static HTML over live components. */
  function onLanguageChange(fn) {
    var L = window.KQLang;
    if (!L || L.__capasWrapped) { (window.__capasLangHooks = window.__capasLangHooks || []).push(fn); return; }
    window.__capasLangHooks = [fn];
    var t = L.toggle, s = L.set;
    L.toggle = function () { t.apply(L, arguments); window.__capasLangHooks.forEach(function (h) { try { h(); } catch (_) {} }); };
    L.set = function () { s.apply(L, arguments); window.__capasLangHooks.forEach(function (h) { try { h(); } catch (_) {} }); };
    L.__capasWrapped = true;
  }
  function lang() { try { return window.KQLang ? window.KQLang.cur() : "en"; } catch (_) { return "en"; } }

  window.CapasRecords = { checkResponse: checkResponse, checkRecord: checkRecord, partition: partition, load: load,
                          save: save, order: order, quarantined: quarantined, onLanguageChange: onLanguageChange,
                          lang: lang, KEY: KEY, QKEY: QKEY };
})();
