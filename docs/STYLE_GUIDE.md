# CAPAS site style guide — professional register (adopted 2026-10-14)

Owner's instruction: "no AI wording, big-3 professional". The register is that of a senior consulting deliverable:
conclusion first, one idea per sentence, evidence instead of adjectives, no theatre.

## Sentences
- Lead with the finding. Headlines are declarative statements of fact, never questions, never slogans.
  Bad: "Does this claim's evidence hold up?" Good: "CAPAS decides whether declared evidence licenses a claim."
- One idea per sentence, at most 25 words, active voice, present tense.
- No em-dashes (— or &mdash;) anywhere in visible text. Use a period, a colon or a comma. En-dashes stay only in
  numeric ranges (3–10×) and in ids.
- No exclamation marks. No rhetorical "not X, it's Y" constructions. No sentence fragments as drama ("Not a slide.").
- No metaphors or combat vocabulary: moat, punch, enemy, weld, battle, kill, beachhead (say "first market"), slide,
  slogan, pitch, "the point", hero. No anthropomorphism: the engine "returns HOLD", it does not "refuse" or "say no".
- No self-praise adjectives: honest, real, true, genuine, literal, transparent, rigorous, robust, deterministic-as-
  praise. Where the text wants to say "honest", show the number or the limit instead. "Honest scope:" becomes
  "Scope:" or "Limits:". "we do not hide it" is deleted; the limit itself stays.
- No "we" as a character ("we measured", "we didn't invent"). Prefer the subject: "The gate", "The blind corpus",
  "The 2026-10-13 run". "Our own run" becomes "a Krenn·IQ run".
- No parenthetical asides longer than four words. Move them to a sentence.

## Numbers and claims
- Every number carries its denominator and, where it matters, its date and the tag of the engine that produced it.
- Three or more related numbers go in a table, not in prose.
- A limit is stated once, plainly, next to the number it limits. Not repeated as a refrain.
- Vocabulary is fixed: claim, evidence fields, verdict (ACCEPT / REWRITE / REJECT / HOLD), audit hash, sealed batch,
  blind rate, rule, adapter, proof ledger, pre-registration. "Gate" is a noun (the gate, the Gate App), not a verb,
  except in code identifiers.

## Labels and structure
- Section labels (eyebrows) are nouns: "Measured performance", "Verdict contract", "Limits", "Workflow", "Evidence".
- Keep every HTML id, class, link, code block, table, number and `data-es` attribute. Edit text only. Update the
  `data-es` Spanish twin of every sentence you change, in the same register (Spanish from Mexico, neutral, no
  anglicisms where a Spanish term exists; product and field names stay in English).
- Do not add inline styles or elements. Do not expand: target 10–25 % fewer words per page.

## Literal strings that verifiers require (keep them exactly)
index.html: "Deterministic Scientific Claim Gate", "admissibility", "ACCEPT, REWRITE, REJECT, or HOLD",
"No language model in the verdict", "Where it Lives", "Verdict Reference", "What it is, measured", "Krenn-IQ",
"53 / 82", "51 / 63", "does not certify scientific truth", "Not a fraud detector, and we measured it",
"in-depth.html#ledger", "Reference Gate Decisions", "SCHEMA V3", "statistical_confidence", "audit_hash", "claim_id",
"evidence_contract", class="bg-logo", src="logo_kreniq_volum_trico.html", class="bg-veil".
in-depth.html: "In depth", "The Core", "One mechanism. 10 domains. 26 gates", "contamination cascade",
"should this have been said", "Use Cases", id="ledger", "Architectural parallel (not a validation)",
"WHAT IS <em>NOT</em> VALIDATED", the three block headers starting "CLOSED &middot;", "BACKED &middot;",
"SCOPED &middot;", and every `python3 …` command inside the ledger lines.
customer-brief.html: "Brief", "Deterministic claim ", "Reproducible engine benchmark", "Disclaimers", the whole
`<pre id="brief-packet">…</pre>` block untouched.
pilot-packet.html: "Pilot Packet", "Two-week", "Roles", "Success criteria", "Governance", "disclaimer".
benchmark.html: every `<tr>` of the table and the `overall:` line untouched; "N=1238"; "78.4".
All pages: the nav and footer markup untouched; titles untouched.
Forbidden phrases: everything in `benchmarks/verify_site_wording.py` (run it before finishing).

## Checks every editor runs before finishing
    python3 benchmarks/verify_site_wording.py
    python3 benchmarks/verify_customer_product_assets.py
    python3 designlab/layout_lint.py docs/<file>
    python3 scripts/dump_untranslated_leaves.py docs/<file>   # count must not grow
and, where it applies: verify_page_matches_ledger.py (in-depth), verify_brief_packet_matches_engine.py (brief),
verify_benchmark_page_matches_mix.py (benchmark), verify_claim_gate_ui.py (app).
