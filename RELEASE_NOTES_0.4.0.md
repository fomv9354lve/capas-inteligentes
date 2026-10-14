# capas-claim-gate 0.4.0 — release notes (draft, 2026-10-13)

Engine, package and surfaces as of tag v0.4.0 (2026-10-13, commit 6a8471b). Site deployed 2026-10-13; this file is the
changelog the release carries. Every figure below is re-derivable (command given) or marked as declared.

## Validation (new)

- **Blind self-gating corpus** of 233 real research claims from a sister project (Ginibre): coded blind by a
  separate session, engine frozen at a git tag *before* coding, verdicts sealed by sha256 *before* outcomes
  were opened, double-counted. Blind X1–3: bad-not-ACCEPT 53/82, good-not-REJECT 52/63. Out-of-sample
  X4+X5: 17/21 and 16/17 (Wilson 95% [0.60–0.92], [0.73–0.99]). `python3 research/ginibre_corpus/score_sealed.py`
- **Retraction audit (negative result):** recomputable numeric inconsistencies do not separate 6,348
  retracted-for-data papers from 888 clean controls (1.58% vs 2.13% severe). CAPAS is not a fraud detector.
  `python3 research/retraction_audit/grade_severity.py`
- **Cross-family counter-signature (GOVERNANCE §6):** 8 model-directed runs by another model family; 3 of 7
  public claims refuted and fixed the same day (scope false-accept, unsealed figure, unversioned grading).
  Transcripts and the report gate: `research/section6_package/`.
- **Quantum calibration law** (`calibration_snapshot`): 4/4 blind on real ibm_kingston GHZ runs, plus a
  prospective layout choice that halved the per-layer error with identical circuits.
  `python3 -m pytest benchmarks/test_calibration_snapshot.py`

## Engine rules (all optional evidence fields; a missing field never produces ACCEPT on the affected path)

- `exact_model_solution`: `error_statistic` + `n_cells` (Šidák-corrected SE tolerance for a max over cells),
  `scope_declared` / `scope_tested` (declared ⊄ tested → REWRITE; an ACCEPT on a declared scope licenses the
  text annotated with that scope, never raw), `negative_control_failed` (machine-precision regime
  abs_error ≤ 1e-12·max(1,|reference_value|): missing → HOLD, false → REWRITE), `tolerance_rationale`,
  `reference_value` (tolerance of the order of the object → HOLD).
- `proof_admissibility`: `text_quantifier` — a bounded declared scope without a uniform bound licenses the
  text only when `text_quantifier="bounded"` is declared, and then as the text annotated with its scope;
  visibly universal text with a bounded declaration → REWRITE (contradiction).
- `statistical_confidence`: `test_statistic` recomputes p (statcheck-style); mechanism wording needs
  `null_control_passed`.
- RMT identities: declared precision of scientific-notation literals read correctly; a literal coarser than
  the identity's magnitude → HOLD; relative floor 1e-12.
- Invariants: `calibration_snapshot` (absolute + relative device filters, calendar-day freshness, T2 floor as
  configuration), `pvalue_test`, `reported_percent`, `sum`, `rmt_closed_form` / `rmt_F` / `rmt_G`.
- Text/solver-log extractor derives its fields from the registry tables (no hand-kept subset).

## Surfaces

- Gate App: single and batch decisions run through the live Python engine; the in-browser replica is not
  authoritative (parity 130/233) and the page returns HOLD without a backend; local audit history validated
  by the engine's `audit_hash`; CSP hashes cover script-template inline styles. Six content pages bilingual
  (ES via `lang.js`).
- Package ships `capas_breeding` and `capas_independence` (direct imports since 2026-09). `capas validate`
  (full product gate) passes end-to-end; `capas_extract` (grounded-extraction gate) restored, PDF parser moved
  to `capas_pdf_extract`.
- Conformance: `no_llm_verdict` backed by `benchmarks/verify_determinism.py` (static call-graph + 245
  payloads identical across interpreters with the network blocked).

## Known limits (unchanged, stated)

GIGO ceiling (a self-consistent fabrication passes); the gate does not read prose — a declared field is the
coder's responsibility; one auditor family so far; n is small everywhere above.
