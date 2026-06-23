# CAPAS — Open-Standard Refactor Brief (final posture)

Role for the executor: staff engineer + product architect + hostile pre-release auditor.

## Posture (locked this session)
CAPAS ships **open-core + open-standard**, not closed SaaS and not pure MIT-dump. Open source is
**positioning, not the revenue engine**. The defensible asset is NOT the code — it is the **schema +
admissibility calculus + the certificate + the benchmark corpus + the CAPAS mark/governance**. The
parallel is OPA / SPDX / RO-Crate / OpenLineage, not Datadog.

The one sentence everything must serve:
> CAPAS does not determine truth. It evaluates whether supplied evidence **licenses a specific claim**
> under a **declared admissibility contract**, deterministically and re-derivably.

## The spine: CAPAS gates its own site (do this first — it is the demo, the legal shield, and the moat at once)
Every public number becomes a CAPAS-admissible claim with a re-derivation command. Build
`docs/CLAIMS_REGISTRY.md` (table: claim · location · risk · evidence artifact · regen command · status
keep/rewrite/delete) and SURFACE it on the site as "CAPAS gates itself." This is not just risk
reduction — a claim-admissibility engine whose own claims are all admissible-and-re-derivable is the
"holy-shit" proof the audits asked for. We already have the pieces (`docs/proof_ledger.json`, the
benchmark regen commands, `audit_hash`). Wire them, don't rebuild.

## P0 — integrity (before showing anyone; cheap; we own the pieces)
1. **Numbers policy = gate-or-remove, no grace window.** For each public number
   (`$75k`, `417h`, `10k validations`, `34% rewritten`, `78.4%`): make it re-derivable (link to regen
   command / benchmark) OR mark it a **declared estimate with assumptions shown** OR delete.
   - `$75k` fixed value → REPLACE with a small **interactive savings model** (user enters claims/min-per-
     review/rate; output is computed live, labeled "planning model · your assumptions · not booked
     savings"). This keeps the value story the owner wants, honestly. No fixed headline number.
   - `10k / 34%` → label "synthetic regression corpus · reproducible in /benchmark" or delete.
2. **Banned-words sweep** (legal). Remove anywhere: proven, guaranteed, certified truth, truth engine,
   best, SOTA, industry-leading, secure/unhackable/tamper-proof, eliminates hallucinations. Replace with:
   designed to / reduces / helps mitigate / admissibility / evidence licensing / deterministic gate.
3. **Global disclaimer + license posture.** Footer everywhere:
   "Research software. CAPAS structures and gates supplied claim evidence. It does not infer hidden
   evidence, replace expert/legal/medical/regulatory review, or certify scientific truth." Add a real
   OSI `LICENSE` file or an explicit `License: pending — choose OSI license before public release` TODO.
   Do NOT invent a license.

## P1 — make the thesis FELT (the demo)
4. **Seeded brutal claim-drift demo; Decision panel never empty.** Default load shows a real verdict:
   - Evidence: "X was associated with lower defect rates." Claim: "X reduces defects by 35%."
     → **REWRITE** · boundary: "association evidence does not license causal wording" · allowed rewrite:
     "X is associated with lower observed defect rates in the supplied dataset." (mark `EXAMPLE`).
   - Empty state must still teach: show what a verdict WILL contain (verdict / blockers / licensed reuse
     boundary / open proof obligations / next action / certificate).
5. **Simple vs Advanced split.** Simple Walkthrough = run sample → see boundary → see contract → run gate
   → see certificate → see next action. Advanced (behind a toggle) = Guided builder / Raw JSON / Batch /
   Extraction / CLI-API. Fix the wizard: Step 1 ONLY selects mode; the builder appears in Step 2.
6. **Evidence Contract becomes the protagonist**, not a side panel: claim type · required fields ·
   completed/missing · possible verdict before run · what CAPAS will NOT infer · training-readiness impact.
   When evidence is incomplete, the run button reads "Run anyway — missing evidence will HOLD" (pedagogy,
   not error).
7. **Formalize the Admissibility Certificate** as the output unit (verdict, claim_id, claim_type,
   schema_version, contract/evidence/boundary/provenance/defeaters axes, licensed_reuse_boundary,
   open_proof_obligations, next_operational_action, deterministic_rule_ids, audit_hash). Make it
   **shareable + re-verifiable** — this certificate is the moat seed ("CAPAS-audited", like SPDX/SOC2).

## P2 — open-standard packaging (the moat)
8. **Repo as reference implementation.** README: what it is / what it is NOT / quickstart / schema
   example / `decide` example / batch example / certificate example / deterministic design / limitations /
   contributing / license status / security model. `docs/BENCHMARKS.md` (name · corpus · synthetic-vs-real ·
   regen command · expected output hash · limitations).
9. **Govern the mark, open the core.** Open: schema, calculus, reference gate, CLI, tests, corpus.
   Reserved/governed: the CAPAS mark, the official certification, the official benchmark. State this.
10. **Batch sells utility honestly:** total · ACCEPT/REWRITE/REJECT/HOLD counts · exception queue · top
    blockers · downloadable JSON/CSV · NO booked savings unless user-computed.

## Engineering constraints (non-negotiable)
- Deterministic verdict path; **no LLM in the final verdict** (LLMs may only draft/extract candidates,
  explicitly non-decisional). No network calls in the browser gate. Keep schema v3 compat (migration notes
  if unavoidable). Candidate extraction stays non-decisional. CLI/API remains the provenance-verification path.
- All visual changes go through `designlab/check.py` (layout/nav/mobile/a11y) before deploy via
  `deploy_site.py --ui`.

## Tests to add/keep
ACCEPT (complete valid statistical_confidence) · HOLD (missing p_value/alpha/direction) · REWRITE
(association→causation) · REJECT (artifact unavailable) · HOLD (invalid schema types) · universal_anchor
absolute-only ACCEPT · relative/empirical/benchmark anchor bounded REWRITE · batch aggregation counts ·
certificate fields always present.

## Deliverables from the executor
files changed · risky claims removed/reworded · tests added · commands run · remaining TODOs ·
launch-readiness score · top-5 remaining risks.

## Definition of done
A stranger understands in <20s that CAPAS is an **open, deterministic admissibility gate** — not a truth
machine, not legal/scientific certification, not an LLM judge — a reproducible compiler that decides
whether supplied evidence licenses controlled reuse of a claim. And every number on the site is itself
re-derivable or marked as a declared estimate.

---
### My deltas vs the owner's draft prompt (advice, not orders)
- **Headline:** lead with the comprehensible hook, immediately define precisely. Hook: "Does this claim's
  evidence hold up?" → subhead: "CAPAS compiles supplied evidence into a claim **admissibility** decision —
  it does not determine truth; it decides whether the evidence licenses the claim." (Owner's draft kept the
  precise line as the headline; it is defensible but fails the 20-second stranger test alone.)
- **Elevate training-data governance to a top-3 positioning bet, not item #10.** "Admissibility gate for
  what is allowed into a training set / RAG corpus / automated report" is likely the bigger, more urgent
  2026 buyer than journals. The audits buried it; I would make it a first-class lane.
- **Savings: reframe, don't delete.** Owner wants the value story — make it a user-computed model with
  assumptions shown (honest AND keeps the story), rather than removing it outright.
