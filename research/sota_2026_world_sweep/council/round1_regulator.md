# Round 1 — Regulatory-science reviewer (pharma / medical-device evidence tradition)

## 1. Giants I bring

1. **FDA technical-rejection criteria + Validator Rules v1.6 / Pinnacle 21 (FDA–PMDA harmonised IDs)** — https://www.pharmasug.org/download/sde/rtp2022/PharmaSUG-NCSDE_2022-08.pdf , https://www.certara.com/blog/how-does-pinnacle-21-enterprise-differ-from-the-community-version/ . Inherits: rejection precedes review (form before substance), **stable, versioned rule IDs** with severity classes, a published change log. HOLD's ancestor.
2. **MHRA staged authorisation against pre-specified evidence thresholds (Commission report 2026-09-10, accepted 2026-10-06)** — https://www.raps.org/resource/euro-roundup-mhra-commission-makes-recommendations-on-ai-regulatory-framework-in-the-uk.html . Inherits: thresholds fixed before data; licence only up to the stage reached. The pilot go/no-go (FA ≤ 30 %, FR ≤ 25 %, ≥ 40/40, Wilson 95 %) is this logic.
3. **Health Canada ML-device guidance, Predetermined Change Control Plans** — https://www.blg.com/en/insights/2025/02/health-canadas-evolving-regulatory-framework-for-machine-learning-enabled-medical-devices . Inherits: a written change envelope; a rule change outside it re-opens validation. CAPAS does this as "blind rates belong to the frozen tag"; name it a PCCP.
4. **TGA Feb-2026 AI-SaMD guidance** — https://www.tga.gov.au/node/514668 . Inherits: synthetic data count **only as a supplement**, with documented generation rationale. The ledger's `pharma_admissibility` (3,024 synthetic cases, "0 false-accepts") is contract coverage, not performance.
5. **SFDA MDS-G010ML (independent review of the clinical evaluation by someone not involved in development)** and **MFDS–HSA guiding principles for ML-device trials** — https://tamimi.com/law-update-articles/new-guidance-for-ai-and-big-data-medical-devices-in-saudi-arabia , https://www.mfds.go.kr/eng/brd/m_40/view.do?seq=72637 . Inherits: the independent reviewer is a release requirement — §6 counter-signature gates every release.
6. **NZ Medsafe Verification Pathway (≥ 2 recognised regulators, no independent re-analysis)** and **COFEPRIS reliance** — https://www.medsafe.govt.nz/consultations/verification-pathway-rules-outcome.pdf . Inherits a negative rule: reliance transfers verdicts, not evidence. A foreign verdict is a declared field, never an ACCEPT.

## 2. Critique of the 5-action plan

1. **PVP verification budget — KEEP, change the unit.** "Coverage declared" is not evidence. The certificate must carry the `read / declared / derived` counts `capas_ingest.results` already splits, per claim and per batch. Test: ledger `verification_budget` per sealed batch; release fails if absent; an ACCEPT with zero `read` fields is flagged `declared-only`.
2. **Adapters 5–6 (DCC/D-SI, RO-Crate) — CHANGE the order.** DCC serves Atlas. The beachhead needs a **validator-report adapter** first: a Pinnacle 21-style report with a technical-rejection error → HOLD before any statistical rule fires. Test: two fixtures (TRC error → HOLD; clean → proceeds); RO-Crate after.
3. **Re-verifiable certificate (PICID) — KEEP, strongest action for a regulator.** Add: every reason line cites rule ID + version. Test: replay script in CI that never imports `capas.py`; divergence breaks the build; a verdict without a rule ID fails schema.
4. **CAPAS vs LLM-judge on X6 — CHANGE the primary endpoint.** No regulator cares whether you beat an LLM. Primary endpoint: false-accept rate with Wilson CI on the sealed batch; comparator: the sponsor's human review baseline (pilot packet). LLM-judge arm secondary. Test: sealed pre-registration naming primary endpoint, arms and n.
5. **Retraction Watch + paper-vs-prereg — KEEP.** This is SAP-vs-CSR review. Make the prereg diff **field-level** (endpoint, alpha, n, analysis, direction). Test: regression tests; X1–X5 cost declared in-sample.

**Missing (2):** (A) **Rule registry**: stable IDs, versions, severity (reject / error / warning), change log; blind rates indexed by rule-set version. Test: a page-vs-ledger check that every public rate names its rule-set version. (B) **Retire "0 false-accepts" as a headline** for the synthetic corpus; label it "contract coverage" on every surface. Test: wording guard in CI.

## 3. Integration order (90 days, tool only)

- Weeks 1–2: rule registry (A) + rule IDs in every reason; action 5 rules with regression tests; wording guard (B).
- Weeks 3–5: action 3 replay verifier in CI; certificate carries rule IDs, versions, read/declared/derived counts; `verification_budget` ledger field and release gate (action 1).
- Weeks 6–8: validator-report adapter → HOLD on TRC; then DCC/D-SI (action 2).
- Weeks 9–12: X6 sealed under a frozen envelope; primary endpoint FA with CI; human baseline arm; LLM arm secondary (action 4). Nothing opened before verdict hashes are committed.

## 4. Where CAPAS is ahead / where my tradition is ahead

Ahead: no regulator freezes its own review instrument, seals its verdicts and publishes its blind error rate with the leakage declared. FDA/Pinnacle gate format; CAPAS gates evidence-field admissibility (significance-vs-alpha, multiplicity, CI-excludes-null, direction, endpoint) that Validator Rules skip. The `read/declared/derived` split is cleaner than any submission provenance I review.

My tradition is ahead: rule traceability (IDs, versions, severity, harmonised across agencies), change control as a written envelope, the independent reviewer as a hard requirement, and sample sizes that make a false-accept rate mean something. Forty bad records at a 30 % threshold is an honest pilot gate, not fitness-for-use evidence; the readout must say so in those words.

## 5. Red lines

1. **No ACCEPT by reliance.** A verdict from a regulator, journal, reviewer or model is a declared field, never an input to the verdict.
2. **No performance number from synthetic or in-sample data.** "0 false-accepts" on 3,024 synthetic cases appears only as contract coverage; X1–X5 rates are never cited for the current engine.
3. **No rule change between freeze and open.** A rule written from a batch's failures makes that batch training data; its rate belongs to the old rule-set version only.

## 6. Positioning as a reference

My tradition positions through rule harmonisation (FDA–PMDA Validator Rules), guidance with consultation, sandboxes (MHRA AI Airlock) and practitioner venues (PharmaSUG). One step: publish the statistical-admissibility rule set in Pinnacle 21 rule-ID format, the synthetic corpus as its conformance suite, and present it at PharmaSUG as the space Validator Rules v1.6 leaves open. Validators adopt rules by ID, not by paper.
