# Round 1 — formalist (IL/CH/CZ/FR/AT tradition)

Premise: a verdict is worth what an outsider can re-check without trusting its producer. The audit hash (`capas.py:562–577`) is sha256 over {input, verdict, reason, required_fields, invariant_audit}. It proves the result was not altered after emission; it does **not** prove the verdict follows from the rules — a buggy engine emits a perfectly re-derivable hash. Integrity ≠ proof.

## 1. Giants I bring

- **PICID** (Katz Lab, HUJI; FMCAD 2026; https://arxiv.org/abs/2503.12083). Inherit: the verifier emits a proof an *independent checker* validates "so users need not rely solely on the verifier's output". Rule: verdict + replayable rule trace + a checker that does not import the engine.
- **Kirsch, "Untrusted Authors, Trusted Answers"** (CTU; https://arxiv.org/abs/2607.14137). Inherit: answers self-certify by *replay at the source*; fidelity grades; verified checker, untrusted author. CAPAS has the replay (`capas_ingest.verify_sources`) and the grades (CLOSED/BACKED/SCOPED). Missing: the checker.
- **LeanProbe / AI for Math @ EPFL** (https://aiformath.epfl.ch). Inherit: the kernel is the only verdict; agents get *verifiable* feedback over MCP. CAPAS's `.mcp.json` server is convergent design.
- **Inria "Leaning and Rocq'ing"** (https://www.renaissancephilanthropy.org/leaning-and-rocqing). Inherit the gap: a kernel certifies proof ⊢ statement, never statement ⊨ intent. Claim-text → fields is autoformalization by an untrusted coder; the GIGO ceiling is this gap.
- **ISTA Henzinger, Alignment Monitoring** (https://arxiv.org/abs/2508.00021). Inherit: guarantees hold only while model matches reality; monitor the gap. CAPAS's leakage rule and `max_age_days` (`capas_invariants.py:915`) are this principle.
- **ÖAWI 2026 §3.5(a)** (https://oeawi.at/wp-content/uploads/2026/07/OAWI-Richtlinie-2026.pdf): "Für die eigentliche Urteilsfindung sind KI-Anwendungen nicht zulässig." Inherit the number *zero*; JuStRank (https://arxiv.org/abs/2412.09569) is the measured reason.

## 2. Critique of the 5 actions

1. **PVP budget — keep, change the source.** Nobody *declares* coverage; derive it from the `provenance.read / declared / derived` split `capas_ingest.results` already writes. "Verified against artifact" = a `verify_sources` hash match. Test: script-generated `verification_budget` ledger entry per sealed batch; release fails if absent or hand-edited.
2. **DCC/D-SI and RO-Crate/Guix — keep, split and reorder.** A signature without a declared trust root is theatre. Phase 1: D-SI → `calibration_snapshot` mapping, fixtures and tampered fixtures. Phase 2: XMLDSig against a declared root, recorded in provenance. RO-Crate is cheaper and is pure Kirsch replay (package hash → `reproducibility_check.artifact_available`): first.
3. **PICID certificate — keep, make it action #1.** (a) Engine emits `rule_trace` = ordered (rule_id, fields read, predicate, outcome); (b) the frozen rule table ships as *data*, not Python; (c) `capas_check.py`, no `import capas`, replays trace against table and recomputes verdict and hash; (d) hash body gains `engine_tag`. Test: CI replays every sealed verdict file (Ginibre X1–X5, Atlas v2/v3); one divergence breaks the build. Until (c) exists, "certificate" appears on no page.
4. **CAPAS vs LLM-judge on X6 — keep, subordinate.** Only after 3; tag, checker sha256 and the judge's outputs sealed before outcomes open; declared power (X4+X5 gave 21+17). A noisy X6 will be read as a win. Test: the sealed prereg names both hashes.
5. **Retraction Watch + RegCheck — change.** A rule that calls a live database is not deterministic over time: same payload, different verdict next month. Rule: `retraction_db_snapshot {sha256, date}` is a declared source; the rule fires on the snapshot and only downgrades; no snapshot → abstains and says so. RegCheck is structural already: diff `capas_ingest.prereg` skeleton fields (metric, direction, threshold) against the result payload; no prose diff. Test: regression tests + in-sample cost on X1–X5, labelled.

**Missing (2):**
- **A. Faithfulness number.** Two independent coders per sealed batch; field-level agreement published (`coder_agreement` ledger entry); disagreement on a required field → HOLD. The only mechanical handle on statement ⊨ intent.
- **B. Engine identity in every verdict** (3d, a leakage fix): today a verdict cannot be tied to the tag whose blind rate it inherits.

## 3. Integration order (90 days)

Weeks 1–3: rule table as data, `rule_trace`, `engine_tag`; checker replays Ginibre and Atlas sealed files in CI. Weeks 4–5: action 1 from provenance; action 5 as snapshot rules. Weeks 6–8: RO-Crate adapter, then D-SI mapping. Weeks 9–12: action A on the next Atlas batch (E4), then action 4 sealed on top. Every step ends in a backed ledger entry.

## 4. Ahead / behind

**CAPAS is ahead** in one honest respect: it applies the discipline to *itself*. PICID, Kirsch and LeanProbe verify others' objects; none publishes its own blind error rate, freezes itself before a trial, or lets another company's model attack its claims. ETH (https://arxiv.org/abs/2604.21965) isolates the agent; CAPAS also isolates the instrument.

**My tradition is ahead** where trust is earned: verdicts carry proofs a stranger re-checks with a tiny, itself-verified checker (Kirsch, Lean 4 core); the trusted computing base is small and named. CAPAS's TCB is an 8,187-line `capas.py` plus its ledger's honesty. A hash over that is a promise, not a proof.

## 5. Red lines

1. No page calls the audit hash a "certificate" or "proof-carrying" before an engine-independent checker replays sealed verdicts in CI.
2. No rule whose outcome depends on a network call at decision time.
3. No blind rate quoted without its engine tag.

## 6. Positioning

Formalists earn standing with artifacts: PICID at FMCAD, LeanFlow at the ICML AI-for-Math workshop, Kirsch's mechanised Lean core, LeanProbe as a server others plug in. The one step: ship `capas_check.py` plus the sealed verdict files as the artifact of the NeurIPS "Verification in the Age of AI Scientists" submission, so a reviewer re-derives every number without running CAPAS. SwissRN/GFRN (https://crsuzh.pages.uzh.ch/swissrn/contents/news/posts/2026-04-22b/GFRN.html) is a channel; the checker is the credential.
