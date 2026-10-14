# Round 2 — Regulatory-science reviewer

**Verdict: AGREE WITH CONDITIONS.**

**(a) Red lines.** None crossed. "No ACCEPT by reliance" and "no performance number from synthetic or in-sample data" are in the vocabulary fixes; "no rule change between freeze and open" is existing leakage policy and A5 respects it (cost declared in-sample). Rule IDs + versions + severity per reason line and `engine_tag` in the hash body (A1) are the rule registry I asked for.

**(b) The single change I still demand.** A4's sealed pre-registration must carry a **pre-specified pass/fail threshold on CAPAS's own false-accept upper bound** (Wilson 95 %), as `docs/pilot-packet.html` does (FA ≤ 30 %, FR ≤ 25 %, ≥ 40/40), not only "both rates with intervals". Two rates with intervals is a description; a regulator reads evidence only against a threshold fixed before the data (MHRA staged authorisation, wave 7). With ≥ 20 bad records the bound will be wide; then the entry says "pilot-grade" and never migrates to the home page. The threshold may be the pooled 32 % or stricter, but it is written, hashed and co-signed with the protocol.

Conditions: A3c (validator-report adapter) at day 75–90 is fine if it does not slip past 90 while pharma is the beachhead; the Retraction Watch snapshot in A5 gets a `max_age_days` like `field_dates`, so a stale snapshot is HOLD `stale_field`, never a silent pass; A2's `declared-only` flag is written into the A1 trace, not only the release check.

**(c) Where I was wrong.** I wrote that the `read / declared / derived` provenance split is "cleaner than any submission provenance I review". Rule-RL, quantum and AI-eval showed it is not yet load-bearing: a source-hash mismatch is caught by the sealed runner, not by `decide()`, so a verdict can ACCEPT on a source the engine never verified. In my vocabulary: a validator that reports an error and lets the submission through. Adapter 4 inside the verdict (A3a) before any new format is the right order; I withdraw my request to put the pharma adapter ahead of it.
