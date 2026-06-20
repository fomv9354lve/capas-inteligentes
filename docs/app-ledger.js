/* CAPAS Gate App — deterministic rule-ledger overlay.
 *
 * Loaded as an EXTERNAL classic script (allowed by CSP script-src 'self'), so it
 * adds no inline hash and changes no decision logic. PRESENTATION ONLY.
 *
 * It watches #output (which always holds the full decision JSON the gate produced
 * — required_fields / missing_fields / verdict / input_claim) and renders those
 * evidence-contract obligations as a Rule 1 ✓ / Rule 2 ✗ ledger inside the verdict
 * area. Driven by the rendered result, so it works for sample clicks, the guided
 * builder, and the ?p= autorun path identically.
 *
 * Falta 3: "show the engine" — make CAPAS read as a compiler, not a validator.
 */
(function () {
  "use strict";

  function el(tag, className, text) {
    var node = document.createElement(tag);
    if (className) node.className = className;
    if (text != null) node.textContent = text;
    return node;
  }

  function buildLedger(result) {
    var type = (result.input_claim && result.input_claim.type) || "unknown_claim";
    var required = Array.isArray(result.required_fields) ? result.required_fields : [];
    var missing = Array.isArray(result.missing_fields) ? result.missing_fields : [];
    var schemaErrors = Array.isArray(result.schema_errors) ? result.schema_errors : [];
    var verdict = result.verdict || "HOLD";

    var box = el("div", "capas-ledger");

    var head = el("div", "capas-ledger-head");
    head.appendChild(el("span", "capas-ledger-tag", "Evidence contract"));
    head.appendChild(el("span", "capas-ledger-type", type));
    var passed = Math.max(0, required.length - missing.length);
    head.appendChild(el("span", "capas-ledger-meta",
      required.length ? (passed + "/" + required.length + " obligations met")
                      : (schemaErrors.length + " schema checks")));
    box.appendChild(head);

    if (required.length) {
      required.forEach(function (field, i) {
        var isMissing = missing.indexOf(field) !== -1;
        var row = el("div", "ledger-rule");
        row.appendChild(el("span", "rule-id", "Rule " + (i + 1)));
        row.appendChild(el("span", "rule-name", field));
        row.appendChild(el("span", "rule-status " + (isMissing ? "fail" : "ok"),
          isMissing ? "✗ not supplied" : "✓ supplied"));
        box.appendChild(row);
      });
    } else if (schemaErrors.length) {
      schemaErrors.forEach(function (errText, i) {
        var row = el("div", "ledger-rule");
        row.appendChild(el("span", "rule-id", "Schema " + (i + 1)));
        row.appendChild(el("span", "rule-name", String(errText)));
        row.appendChild(el("span", "rule-status fail", "✗ invalid"));
        box.appendChild(row);
      });
    }

    if (missing.length) {
      var obl = el("div", "ledger-obligation");
      obl.appendChild(document.createTextNode("Failed obligation: "));
      obl.appendChild(el("b", null, missing.join(", ")));
      box.appendChild(obl);
    } else if (verdict !== "ACCEPT" && result.reason) {
      var rule = el("div", "ledger-obligation");
      rule.appendChild(document.createTextNode("Admissibility rule: "));
      rule.appendChild(el("b", null, result.reason));
      box.appendChild(rule);
    }

    var decision = el("div", "ledger-decision");
    decision.appendChild(document.createTextNode("Decision:"));
    decision.appendChild(el("span", "ld-badge " + verdict, verdict));
    if (verdict === "ACCEPT" && result.reason) {
      decision.appendChild(el("span", null, result.reason));
    }
    box.appendChild(decision);

    box.appendChild(el("div", "ledger-nonclaim",
      "Rule-based over supplied evidence fields. Deterministic — not an LLM judgment."));
    return box;
  }

  function currentResult() {
    var output = document.getElementById("output");
    if (!output) return null;
    var text = (output.textContent || "").trim();
    if (!text || text.charAt(0) !== "{") return null; // batch output is an array / non-object
    try {
      return JSON.parse(text);
    } catch (e) {
      return null;
    }
  }

  function syncLedger() {
    var area = document.getElementById("verdict-area");
    if (!area) return;
    var result = currentResult();
    var existing = area.querySelector(".capas-ledger");
    // single-claim decisions only (batch results lack input_claim/required_fields)
    if (!result || !result.input_claim || !Array.isArray(result.required_fields)) {
      if (existing) existing.parentNode.removeChild(existing);
      return;
    }
    if (existing) existing.parentNode.removeChild(existing);
    var ledger = buildLedger(result);
    var banner = area.querySelector(".verdict-banner");
    if (banner && banner.nextSibling) {
      banner.parentNode.insertBefore(ledger, banner.nextSibling);
    } else if (banner) {
      banner.parentNode.appendChild(ledger);
    } else {
      area.appendChild(ledger);
    }
  }

  function schedule() {
    // defer so renderVerdict finishes rewriting #verdict-area first
    window.setTimeout(function () {
      try { syncLedger(); } catch (e) { /* presentation-only, never break the gate */ }
    }, 0);
  }

  function start() {
    var output = document.getElementById("output");
    if (!output) return;
    try {
      var observer = new MutationObserver(schedule);
      observer.observe(output, { childList: true, characterData: true, subtree: true });
    } catch (e) { /* no MutationObserver: fall back to one-shot below */ }
    schedule(); // catch any decision already rendered by the ?p= autorun
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }
})();
