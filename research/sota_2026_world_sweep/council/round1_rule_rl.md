# Round 1 — rule-based verification / RLVR tradition (China)

Persona: DeepSeek / Tencent / Lean-prover / Triage-PiEvo line; SCI-Verifier voiced as the counter-position. Sources: `wave_2_C-E.md`, `wave_6_S.md`, the repo.

## 1. Giants I bring

1. **DeepSeek-R1 §2.2.2** — https://arxiv.org/html/2501.12948v1 (Nature: https://doi.org/10.1038/s41586-025-09422-z). "We adopt a rule-based reward system… the neural reward model may suffer from reward hacking." CAPAS inherits the *justification* for "no model in the verdict": a named failure mode, not a preference. Credit it next to `no_llm_verdict`.
2. **Tencent AI Lab, "One Token to Fool LLM-as-a-Judge"** — https://arxiv.org/abs/2507.08794. A colon or "Thought process:" earns a false-positive reward from GPT-o1 and Claude-4 judges. CAPAS inherits a **test protocol**: master-key negatives for any judge arm.
3. **DeepSeek-Prover-V2 / Kimina-Prover** — https://arxiv.org/abs/2504.21801 , https://arxiv.org/abs/2504.11354. The model proposes, the Lean kernel disposes. CAPAS states the same architecture and misses its standard: the kernel is small and independently checkable; `capas.py` is 8,187 lines.
4. **Triage-PiEvo** (Westlake/Kuaishou, Oct 2026) — https://arxiv.org/abs/2610.14683. Admission tiers C1 (same-channel repeat), C2 (independent channel), C3 (independent evaluator on held-out inputs); Accept only with k=2 supports and zero contradictions; **one contradicting record retracts, and the retraction propagates**. 0 % unreliable evidence admitted vs 100 % ungated. CAPAS inherits the tier vocabulary and the propagation rule.
5. **SCI-Verifier / SCI-VerifyBench** (Shanghai AI Lab, ICLR 2026) — https://arxiv.org/abs/2509.24285. The counter-position, fairly: rule design is "cumbersome", and CAPAS proves it (rule v2 after E4, v4/v5 after engine-caused HOLDs). CAPAS inherits its equivalence taxonomy as deterministic normalizers, never as a model.
6. **GB/T 47468-2026** — https://openstd.samr.gov.cn/bzgk/gb/std_list?p.p2=GB%2FT+47468. Text not read by the sweep; nothing to inherit before it is read.

## 2. Critique of the 5-action plan

1. **Verification budget per batch — KEEP, change the unit.** Declare the Triage tier per field, not "verified vs read": 0 = prose, 1 = artifact with hash, 2 = independent channel, 3 = independent evaluator. Test: `verification_budget` ledger entry per sealed batch with the tier histogram; release fails without it.
2. **Adapters DCC/D-SI and RO-Crate — CHANGE.** RO-Crate is half-built: `ro_crate_path`/`ro_crate_sha256` and `_verify_ro_crate` already exist in `capas.py`. Finish adapter 4 first (provenance mismatch → HOLD **inside the verdict**; today only the runner checks it), then DCC. Test: a tampered crate or invalid DCC signature yields HOLD from `decide()`, not from a script.
3. **Re-verifiable certificate — KEEP, sharpen.** `benchmarks/verify_audit_hash_reproduces.py` does `import capas`: it replays with the engine, so it is not independent. Test: a replay with zero repo imports re-derives every sealed verdict from the rule trace; divergence breaks CI.
4. **CAPAS vs LLM-judge on X6 — KEEP, add the Tencent arm.** Both arms also receive master-key payloads (near-empty evidence plus "Thought process:"); report accuracy *and* master-key false-accept rate. Test: the sealed pre-registration names the master-key set and its hash.
5. **Retraction Watch + RegCheck — KEEP, as ingested fields.** Never a live lookup in the verdict: a dated, hashed Retraction Watch snapshot → `cited_doi_retracted`; prereg-vs-results diff falls out of the existing `prereg` + `results` adapters. Test: missing or unhashed snapshot → HOLD; X1–X5 cost declared in-sample.

**Missing (2):** (A) **Deterministic equivalence normalizers** for REWRITE from the SCI-VerifyBench taxonomy (units, rounding, 5 % = 0.05 = 5e-2); any class that needs a model stays HOLD. Test: equivalence fixtures; a numeric literal stored as text still refused. (B) **Retraction propagation in the proof ledger**: a §6 refutation of an entry downgrades every entry that cites it. Test: dependency field in `proof_ledger.json`; `verify_page_matches_ledger` fails on an orphaned dependent.

## 3. Integration order (90 days)

Weeks 1–2: action 3 (independent replay, rule trace). Weeks 2–4: action 1 (tier histogram, release gate). Weeks 3–6: action 5 as adapters + B. Weeks 5–8: action 2 (adapter 4 into the verdict, then DCC). Weeks 6–9: A. Weeks 8–12: action 4 (X6 sealed, master-key arm). Every step ends in a ledger entry; nothing is called blind before the next sealed batch.

## 4. Ahead / behind

**CAPAS is ahead** where my tradition measures on synthetic ground truth: Triage-PiEvo's 144/144 are planted mechanisms; RLVR rewards exist only where an answer key exists. CAPAS publishes blind rates on real claims (17/21, 16/17), engine frozen at a tag, leakage declared, its own numbers gated. No Chinese system in the wave files gates itself.

**My tradition is ahead** in the kernel: Lean's checker is small, formally verified, and the replay does not depend on the prover. CAPAS's determinism is a large Python file whose independence proof imports itself. Triage-PiEvo has formal admission tiers and retraction propagation; CAPAS has neither as code. SCI-VerifyBench has an equivalence taxonomy; CAPAS's REWRITE is rule-by-rule.

## 5. Red lines

1. No model output ever enters a verdict path — not as tiebreak, not as "semantic residue". The X6 judge arm is a measurement stored outside the verdict.
2. No network call in the verdict. External facts (retractions, registries) arrive as hashed, dated fields or the claim HOLDs.
3. No conformance claim against GB/T 47468-2026 until the standard's text has been read and the mapping is a ledger entry.

## 6. Positioning as a reference

My tradition settles arguments with shared benchmarks and open scorers (miniF2F, PutnamBench, SCI-VerifyBench), arXiv-first, then ICLR/NeurIPS/Nature, standards through SAC. The step: publish the sealed corpus as **CAPAS-Bench** — the 233 claims, the sealed outcomes, the master-key negatives, a deterministic scorer with no repo import — and invite the SCI-Verifier authors to run on it. A verifier becomes a reference when others can be scored under its own protocol.
