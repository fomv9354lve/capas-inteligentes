# PLAN v2 — integrated from the eight round-1 critiques (for round-2 vote)

Drafted by the CAPAS session from `round1_*.md`. Every change below names who asked for it. The owner's framing stands:
recognise what exists, integrate what is missing, strengthen the tool, credit the giants.

## Vocabulary fixes adopted before anything else (red lines that cost nothing)
- sha256 = **integrity**; signature = **authenticity**. No page or doc calls a hash "signed" (metrologist, formalist).
- The audit hash is **not** a certificate or "proof-carrying" until an engine-independent checker replays sealed
  verdicts in CI (formalist red line). Wording guard extended.
- Every blind rate is published **with the HOLD share and the informative rate beside it**: an engine that always HOLDs
  scores 100/100 on "bad-not-ACCEPT / good-not-REJECT" (AI-eval red line; the Atlas pilot's 12/12 HOLD showed it).
  `score_sealed.py` adds `hold_share` and `informative_rate` per set; home and in-depth show them.
- No performance number from synthetic or in-sample data on any surface: "0 false-accepts on 3,024 synthetic cases"
  survives only as *contract coverage* (regulator); X1–X5 re-scores are in-sample by declaration (already stated).
- No ACCEPT by reliance: a regulator's, journal's or model's verdict is a declared field, never a verdict input (regulator).
- No composite score, ranking or quality index of claims or authors — four words and a trace (metascientist).
- No sentence claiming conformance to GB/T 47468-2026 until its text is read; no Atlas blind rate below 20 claims per
  class (quantum). Chapultepec: say only "mechanically satisfies P3's research clause", never "complies with /
  endorsed by" (Mexico). "Fraud detector" stays banned.

## The actions, re-ordered (unanimous: the certificate goes first)

### A1 — Re-verifiable verdict certificate (was A3). Owner: core. Target: day 30.
What: the audit-hash body carries `engine_tag`/`engine_commit`, ordered `rules_fired` (stable rule IDs + versions,
severity) and input hashes; the rule table is data, not code; every reason line carries its rule ID + version
(regulator); a verdict without a rule ID fails schema.
Checker: `capas_check.py` — an **engine-independent replayer that imports nothing from capas.py**, verifies each step
of the trace without selecting rules itself (AI-eval: otherwise it is a second replica, cf. replica parity 130/233),
written by a session that did not write capas.py (metascientist, GOVERNANCE §6), runnable with python3 only by an
SNII evaluator (Mexico). CI replays every sealed verdict (phase2b/2c, X1–X5 where the corpus is present).
Closes: `attest_conformance` SCOPED → CLOSED when the replay is green on the signed CI result.
Why first: it is what makes Chapultepec P3 literally true — "a decision explained" = a third party re-runs it without
the engine (Mexico); strongest action for a regulator (regulator); the PICID standard (formalist).

### A2 — Verification budget per sealed batch (PVP). Owner: eval. Target: day 45.
Unit, by consensus: counts of **read / declared / derived** fields from `capas_ingest` provenance + `verify_sources`
hash matches (formalist: mechanical, never hand-declared), plus the share of layout elements carrying `field_dates`
(quantum), expressed as a Triage-PiEvo tier histogram per field (0 prose / 1 hashed artifact / 2 independent channel /
3 independent evaluator) (rule-RL). An ACCEPT with zero `read` fields is flagged `declared-only` (regulator).
Sealed **inside the batch manifest before outcomes open** (metascientist; BRI invalidation-count model). Ledger entry
`verification_budget`; release fails without it. Enforced at release, not inside the verdict (AI-eval).

### A3 — Provenance and adapters, in this order. Owner: ingest. Target: day 60 for 3a–3b.
3a. **Adapter 4 first**: source-hash mismatch → HOLD **inside `decide()`**, not only in the runner (rule-RL, quantum,
    AI-eval). The RO-Crate path (`ro_crate_sha256`, `_verify_ro_crate`) already exists in capas.py — finish it.
3b. **RO-Crate / REWIRE packages**: pure hash replay of declared reproducibility artifacts (Mexico, formalist,
    metascientist). Also: save the raw `BackendProperties` download at the next Atlas job (quantum).
3c. **Pharma validator-report adapter** (Pinnacle 21-style): a technical-rejection error → HOLD before any statistical
    rule, for the beachhead (regulator).
3d. **DCC / D-SI last** (no quantum device issues one; no Mexican lab issues one): schema mapping with fixtures first;
    the adapter must **extract per-parameter uncertainty** and the calibration law must consume it — add `*_u` and
    `coverage_factor` to `calibration_snapshot`, and HOLD "not decidable" inside the guard band instead of FLAG/PASS
    against a bare threshold (metrologist red line); signature verification only against a declared trust root.
3e. Generic registry pre-registration import (OSF) into the `prereg` adapter, `band_pre_registered` derived from
    timestamps, never typed (metascientist). After day 90.

### A4 — CAPAS vs LLM-judge on a sealed batch. Owner: eval. Target: next sealed batch (≥ 20 bad, ≥ 20 good).
Design changes adopted: each judge is compared **against the sealed outcome**, not against the other (metrologist);
labels = sealed outcomes, Atlas as oracle not as sample (quantum; Atlas clean n is 1/1 and 2/2); primary endpoint =
false-accept rate with Wilson CI vs the sponsor's human-review baseline, LLM arm secondary (regulator); judge arm run
k ≥ 5 with permutations on structured **and** prose renderings, plus the Tencent "One Token" master-key arm (AI-eval,
rule-RL); judge outputs stored outside the verdict; minimal detectable difference stated (n≈40 cannot separate 60 %
from 80 %); the other-family model **co-signs the protocol before sealing** (metascientist, Transparent Psi order).
Priors corrected: PNAS 37 %/94 % is a reproduction rate — context in SCOPED, never a judge prior (all); base rate =
Nature 2026 55.1 % replicability + JuStRank bias figures. Retire the `head_to_head` ledger entry (n=10, modeled arms).
Subordinate to A1: tag, checker hash and judge outputs sealed before outcomes open.

### A5 — Structural rules from the giants. Owner: core. Target: day 75.
- `cited_doi_retracted`: Retraction Watch as a **hashed, dated snapshot ingested as a field**, never a live lookup;
  offline or absent → explicit HOLD, never silence; only downgrades (all).
- Pre-registration adherence: **field-level** diff of the prereg skeleton vs the results payload (endpoint, alpha, n,
  analysis, direction) → REWRITE; the prose "RegCheck" is dropped as "cheap" — the repo's own Phase 0 measured
  sensitivity 0.89 / PPV 0.24 (metascientist, formalist, regulator).
- statcheck-style recompute of p when `test_statistic` is declared (today "taken as declared") (metascientist).
- `would_have_failed_if` on every ACCEPT (metascientist; the severity vocabulary).
- Physics counterpart: VERaiPHY's three fields — independent-data calibration, coverage check, look-elsewhere (quantum).
- Deterministic equivalence normalizers for REWRITE from SCI-VerifyBench's taxonomy; retraction propagation inside
  the proof ledger (rule-RL).
Cost of every new rule measured on X1–X5 and declared in-sample.

### A6 — New required field `ai_use_declared {tool, purpose, phase}` (Mexico; Chapultepec duty 3, CNPq 2.664, FWF).
The Ginibre corpus is AI-written and the engine does not demand the declaration. Missing → never ACCEPT (REWRITE).

### A7 — Sealed-batch report in the BRI template, retroactive to X1–X5 labelled in-sample (Mexico, metascientist):
criteria declared before unsealing, invalidation/exclusion count, HOLD share, informative rate, scoring rule, all in
the same ledger entry as the rate.

## Positioning (no engineering)
- **Red Mexicana de Reproducibilidad**: founded by people and institutions (UNAM CCOIA, CIMAT, Cinvestav, IPN-CIC,
  REMERI/CUDI; RBR statutes as template; UKRN contact; then GFRN admission by consensus). Osvaldo joins as a founding
  researcher, not a vendor; CAPAS is one catalog entry (Apache-2.0, forkable); **the network, not Krenn·IQ, runs the
  next sealed batch** (GOVERNANCE §6, constructor ≠ verifier). (Mexico red line, adopted.)
- **CAPAS-Bench** (rule-RL): publish the sealed Atlas corpus and future batches with a no-import scorer and invite the
  SCI-Verifier authors to run on it. The Ginibre corpus stays private until the paper is public.
- NeurIPS 2026 "Verification in the Age of AI Scientists" (12 Dec): submit the sealed protocol + A1 checker.
- Credits page "Sobre hombros de gigantes": every work named in round 1 §1, with what CAPAS inherits from each.

## Order for the next 90 days
Day 0–30: vocabulary fixes + HOLD-share metric + A1. Day 30–45: A2. Day 45–60: A3a–3b, A6. Day 60–75: A5 (first
three items), A7. Day 75–90: A3c, A4 pre-registration co-signed and sealed. After 90: A3d, A3e, remaining A5 items.

## Round-2 question to each member
Read this file and all eight `round1_*.md`. Answer in `round2_<persona>.md` (≤ 350 words): **AGREE / AGREE WITH
CONDITIONS / DISAGREE**, listing (a) any red line of yours this plan still crosses, (b) the single change you would
still demand, (c) one thing another member said that you were wrong about. A plan is adopted when no member DISAGREES
and every condition is either folded in or explicitly deferred with a reason.
