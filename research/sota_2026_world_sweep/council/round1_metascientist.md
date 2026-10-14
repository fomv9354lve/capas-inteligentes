# Round 1 — metascientist (NL / BR / HU / AU reproducibility tradition)

Sources: wave_5_N-R.md, wave_1_A-B.md, wave_3_F-I.md; repo files named inline.

## 1. Giants I bring (what CAPAS inherits, exactly)

1. **statcheck** (Nuijten, Tilburg) — https://statcheck.io . The rule: recompute p from declared statistic and df. The coding guide still says "p is taken as declared (not recomputed)" even with `test_statistic{kind,value,df}` present. The ancestor's one rule, not yet honoured.
2. **metacheck** (Lakens, Mesquida, Bekkers; beta 5 Jun 2026) — https://www.scienceverse.org/metacheck/ , https://github.com/scienceverse/metacheck . Inherits the Retraction Watch/PubPeer cross-reference, the wording "LLM opt-in, declared, classification-only", and the refusal "never automated quality assessments, rankings, or scoring".
3. **Severity (Mayo/Lakens)** — https://www.tandfonline.com/doi/full/10.1080/2833373X.2024.2376046 . A pre-registration is worth what it would have refuted. `hold_has_resolution` does this for HOLD; ACCEPT never says what would have flipped it.
4. **Brazilian Reproducibility Initiative** (Amaral; eLife, 10 Jul 2026) — https://elifesciences.org/reviewed-preprints/111001 . The reporting protocol: criteria declared before unsealing; invalidations published as a number (53/143); result as a range over criteria (20–44 %) plus "≥ half" (27 %). CAPAS publishes 53/82 and 17/21 but neither its exclusions nor a range over scoring rules.
5. **Transparent Psi / AMP** (Kekecs, ELTE) — DOI 10.1098/rsos.191375 , 10.1371/journal.pone.0335330 . Born-open data (hash at creation, not at seal); the opponent co-writes the protocol *before* data. §6 counter-signature attacks claims afterwards; the Hungarian order is stronger.
6. **Brodeur et al., PNAS, Jun 2026** — https://doi.org/10.1073/pnas.2524747123 . 37 % vs 94 % supports "no model in the verdict" — but it measures AI-*led reproduction teams*, not LLM-as-judge. A citation, not a prior.

## 2. Critique of the 5 actions

1. **Verification budget — keep, change the moment.** Coverage is BRI's invalidation count in another vocabulary; honest only inside the sealed manifest *before* outcomes open. Test: `verification_budget` hashed with the sealed verdicts; `score_sealed.py` refuses a batch without it; release fails if the ledger lacks it.
2. **Adapters DCC + RO-Crate — change the order.** RO-Crate: keep (what `artifact_available` should point at). DCC: defer; Boehringer deploys 2027, no pharma-statistics sponsor ships one today. Use the slot for what the beachhead has: an OSF/clinical-registry pre-registration export into the `prereg` adapter (today `atlas_prereg/v1` only). Test: real registration fixture → skeletons; `band_pre_registered` *derived* from timestamps, never typed.
3. **Replay certificate — keep, with §6.** The replayer must be a second implementation by someone who did not write `capas.py`, not a second call to it. Test as stated; replayer's authorship recorded in the ledger.
4. **CAPAS vs LLM-judge on X6 — keep, change three things.** (a) Drop PNAS 37 % as judge-bias prior (wrong category); use the *Nature* 2026 55.1 % replication base rate (Tyner, Aczél et al.) as claim-level prior and JuStRank for judge bias. (b) The sealed prereg carries the scoring rule and the exclusion rule (BRI). (c) State the minimal detectable difference: with n ≈ 40 (X4+X5) you cannot separate 60 % from 80 %; declare X6 a pilot or size it. Test: prereg sha before coding; Wilson intervals; exclusions published; power stated.
5. **Two cheap rules — split.** Retraction Watch on a *declared* `cited_doi` → HOLD: keep (unreachable database = "not evaluable" notice, per the freshness precedent). RegCheck paper-vs-prereg → REWRITE: **drop as "cheap"**. The repo's own Phase 0 (`research/registration_adherence/README.md`) measured title-level diff against COMPare at sensitivity 0.89 / PPV 0.24, and semantic mapping did not beat it. Text diff is metacheck's advisory territory. Replace with field-level adherence: the prereg skeleton's metric-definition hash must match the `prereg_sha` the results claim cites; mismatch → REWRITE. Deterministic, half-built.

**Missing (2).** A. **statcheck recompute**: `test_statistic` declared → recompute p; disagreement beyond rounding → REWRITE. Test: statcheck's documented cases as fixtures (the rule, not the GPL code). B. **Severity line on ACCEPT**: every ACCEPT emits `would_have_failed_if` (field, threshold). Test: property test that mutating that field flips the verdict.

## 3. Integration order (90 days, tool only)

Weeks 1–2: A + 5a. Weeks 3–4: 1 + 5b. Weeks 5–8: 3 (second implementer). Weeks 6–10: 4 (X6 prereg co-signed by the other-family model *before* sealing; code; seal; open). Weeks 9–12: 2 (RO-Crate; generic prereg import). DCC: 2027.

## 4. Ahead / behind

**Ahead:** the instrument itself is pre-registered (engine frozen before coding, verdicts sealed before outcomes), leakage declared, own numbers release-gated. metacheck will not even score; BRI took 7 years and 56 labs for one batch; TPP is one human-audited study. **Behind:** three things CAPAS states but has not done — pre-declared scoring rule with published exclusions (BRI), opponent in the protocol before data (TPP), the ancestral recompute (statcheck). And base rates: 55.1 % (Nature 2026) is a measured prior; CAPAS's pooled 33/103 is one project's claims.

## 5. Red lines

1. No composite score, ranking, or "quality index" of claims or authors. Four words and a trace.
2. No blind rate without its exclusion count and pre-declared scoring rule in the same ledger entry.
3. PNAS 37 % is not a judge-bias prior; no rate from the current engine until the next sealed batch.

## 6. Positioning as a reference

My tradition positions through registries and networks: OSF registrations, Registered Reports, UKRN-listed national networks (RBR is listed; Hungary has none), AIMOS (AUS-RN), and the Springer collection *Severity and Learning from Error* (deadline 15 Dec 2026, https://link.springer.com/collections/ebjdhfadcd ). One step: register X6 on OSF as a sealed protocol and submit the "pre-registered instrument" chapter to that collection — the severity vocabulary is the one the blind rate already speaks.
