# Round 1 — quantum-hardware benchmarking scientist (JP/CN/CERN tradition)

Sources: waves 4 (Japan), 2 (China), 6 (CERN), 7 (Taiwan, US); repo: `research/atlas_corpus/README.md`, `capas_ingest.py`,
`docs/CODING_GUIDE_EVIDENCE_FIELDS.md`, `docs/proof_ledger.json`.

## 1. Giants I bring

1. **Hayata & Yamamoto, "Quantum anomaly for benchmarking quantum computing", PRR 22 Sep 2026**
   (https://journals.aps.org/prresearch/abstract/10.1103/l8w6-pk4m). Axial-anomaly coefficient reproduced on trapped-ion
   Reimei *without error mitigation*. Inherits: a claim type whose reference value is an exact theoretical number, with
   **mitigation status as a declared field**.
2. **GB/T 47468-2026, test methods for quantum computing system performance, eff. 2026-11-01**
   (https://openstd.samr.gov.cn/bzgk/gb/std_list?p.p2=GB%2FT+47468). Inherits: a `method_standard` slot on quantum claims.
   Text not read (wave 2 says so): the slot only, not conformance.
3. **VERaiPHY / PHYSTAT review, arXiv 2607.10039** (https://arxiv.org/abs/2607.10039). Inherits three structure-checkable
   fields: independent-data calibration, coverage check (nominal vs empirical), look-elsewhere correction; and
   "data touched only at the final test" = the sealed runner.
4. **CMS two-team sign-off before unblinding** (https://cms.cern/node/1378); PADME blind procedure
   (https://link.springer.com/article/10.1007/JHEP06(2025)040). Inherits: GOVERNANCE §6 is the mechanised CMS rule.
5. **IBM standard benchmark strategies** (https://research.ibm.com/publications/defining-standard-strategies-for-quantum-benchmarks),
   QCVV review (https://arxiv.org/pdf/2503.16383), measured QV trailing vendor claims (https://alphaxiv.org/abs/2503.04905).
   Inherits: the benchmark ≠ diagnostic split `capas_quantum_physics.py` must keep (edge-TLS diagnostic, T2≤2T1 gate).
6. **Academia Sinica AI-driven calibration, Apr 2026** (https://www.sinica.edu.tw/en/news_content/55/3757) and
   **Zuchongzhi-3** fidelities with no snapshot (https://bcas.cas.cn/highlight/202504/t20250424_1041936.html).
   Inherits: the two live cases the per-parameter dated snapshot controls for.

## 2. Critique of the 5 actions

1. **PVP verification budget — KEEP, change the unit.** `capas_ingest.results` already splits provenance into
   `read / declared / derived`; the budget is those counts per batch plus the share of layout elements with
   `field_dates`. Test: `verification_budget` regenerates from the E4b ingest claims; release fails without it.
2. **Adapters DCC/D-SI and RO-Crate — CHANGE the order.** No quantum device issues a DCC; it serves no corpus we have.
   First close **adapter 4** (the README admits hash mismatch is caught by the runner, not the verdict) and save the
   **real** `BackendProperties` download at the next Atlas run (tested only on FakeKingston). Then RO-Crate; DCC last.
   Test: tampered `meta.sources` sha → HOLD from the engine with no runner.
3. **Replay certificate (PICID) — KEEP; the strongest action.** It turns `attest_conformance` from SCOPED to BACKED and is
   the CMS second team in code. Test: a script importing nothing from `capas.py` re-derives every verdict in
   `phase2b/` and `phase2c/` from the rule trace alone.
4. **CAPAS vs LLM-judge on X6 (Atlas) — CHANGE.** Atlas's clean count is 1/1 and 2/2 — anecdote, as the README says; a
   Bayesian judge-bias estimate on that n is the prior echoed back. Run action 4 on the next sealed Ginibre batch (≥20
   bad, ≥20 good); Atlas stays the physics oracle, not the sample. PNAS 37 % vs 94 % is a reproduction rate, not a judge
   false-accept rate: a declared prior only with that caveat in the pre-registration.
5. **Retraction Watch + RegCheck — KEEP** (cheap; not my domain). Add VERaiPHY's three fields as the physics counterpart,
   same regression tests, in-sample cost declared.

**Missing (2):**
- **A. `theory_invariant_claim`**: {measured, se, exact theory value, tolerance rule, `error_mitigation` declared}.
  Undeclared mitigation → HOLD. Test: a synthetic anomaly-coefficient fixture passes only with mitigation declared.
- **B. Calibrator provenance** in `calibration_snapshot`: `calibrator` = human | automated | ai_model (+ tool). Undeclared →
  notice like `field_freshness: not evaluable`, never silence. Test: same verdict with any calibrator; provenance
  enters the audit hash.

## 3. Integration order (90 days, tool only)

- **Weeks 1–2:** adapter 4 in the engine; real `BackendProperties` stored with hash at the next Atlas job; budget counts
  from provenance (actions 2, 1).
- **Weeks 3–5:** replay certificate over sealed Atlas and Ginibre files; `attest_conformance` → BACKED (action 3).
- **Weeks 5–7:** A, B, VERaiPHY fields, `method_standard` slot; tests in `benchmarks/test_calibration_snapshot.py`.
- **Weeks 7–10:** RO-Crate adapter; action 5 with in-sample cost on X1–X5.
- **Weeks 10–13:** pre-register action 4 on the next Ginibre batch. DCC deferred until a classical-instrument partner exists.

## 4. Ahead / behind

**CAPAS is ahead** in one precise thing: the judge is frozen at a tag before coding, verdicts are sealed by hash before
the outcome opens, and freshness is per parameter with a timezone-deterministic test. Zuchongzhi-3 publishes fidelities
with no snapshot; IBM re-measured only CZ while T1/readout/sx stayed identical between 02:16 and 11:51 (E4). CMS
blinding is a human protocol; nobody in the wave files mechanises it.

**My tradition is ahead** in statistics and in drift. Coverage checks, look-elsewhere correction, uncertainty
propagation and two-team sign-off have decades of practice; GB/T 47468 is a national test method. CAPAS's quantum law
gave PASS on the E4 snapshot that then failed (calibration predicted +17 % per layer, observed +70 %): exact identities,
no drift model, and an anecdotal blind n.

## 5. Red lines

1. No sentence claiming conformance to GB/T 47468-2026 until its text is read; a field name is not conformance.
2. No published Atlas blind rate below 20 claims per class; 1/1 and 2/2 stay labelled anecdote.
3. No estimate promoted to a gate (the ZZ estimate was 24× off the published value); the anomaly coefficient enters
   only with exact theory value and declared mitigation.

## 6. Positioning as a reference

My tradition positions through standards bodies (SAMR for GB/T), vendor benchmark definitions (IBM), PHYSTAT/VERaiPHY
reviews and PRR/PRL letters. The one step: a one-page **admissibility annex for quantum benchmark reports** (snapshot
with `field_dates`, calibrator, mitigation status, method standard), Zuchongzhi-3's published set as the first worked
HOLD and E4/E4b as worked ACCEPT/REJECT, attached to the NeurIPS workshop submission already in §9.
