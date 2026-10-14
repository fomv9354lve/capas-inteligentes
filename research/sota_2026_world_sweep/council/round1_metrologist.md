# Round 1 — the metrologist (PTB / IMEKO tradition)

Sources: `wave_3_F-I.md`, `wave_2_C-E.md`, repo. No new web research.

## 1. Giants I bring

1. **PTB Digital Calibration Certificate (DCC)** — https://www.ptb.de/news/dcc (DCC Conference Feb 2026, DCC2Ind Jan
   2026, Boehringer ~150,000 calibrations/yr from 2027). CAPAS inherits the **object**: a calibration result is a signed,
   dated, machine-readable document, one date per parameter. The repo's `field_dates` (coding guide, rule v2) is already
   the DCC dating discipline; what is missing is the rest of the record.
2. **D-SI metadata model** — https://imeko.org/publications/tc6-2025/IMEKO-TC6-2025-003.pdf and
   https://imeko.org/publications/tc6-2025/IMEKO-TC6-2025-010.pdf. CAPAS inherits the **quadruple**: value, unit,
   uncertainty (with distribution and dependencies), date. Today `calibration_snapshot` carries value and date only.
3. **AI-Met / AI.Cert (PTB, 2025-01-17)** — wave 3, medium confidence (snippets). Inherits the **stance**: AI supports
   conformity assessment, the decision stays with the deterministic procedure. CAPAS already says this; cite it as prior art.
4. **Fraunhofer IAIS AI Assessment Catalog** —
   https://www.iais.fraunhofer.de/en/publications/studies/2023/ai-assessment-catalog.html. Inherits one sentence:
   "complements rather than replaces formal compliance" (arXiv 2601.08295). Say so on every certificate.
5. **GB/T 47468-2026** test methods for QC performance — https://openstd.samr.gov.cn/bzgk/gb/std_list?p.p2=GB%2FT+47468
   (existence and dates high; text not read). Inherits the **measurand discipline**: a number is comparable only with its
   test method declared.

## 2. Critique of the 5 actions

1. **PVP verification budget — keep, sharpen.** `capas_ingest.results` already splits provenance into `read / declared /
   derived`. "Verified against artifact" = field read by an adapter from a sha256-verified source; "only read" = declared
   by hand. Test: `verification_budget` per sealed batch computed from that split, release fails without it.
2. **DCC/D-SI + RO-Crate — keep DCC, change its spec, defer RO-Crate.** "Invalid signature → HOLD" is necessary and
   insufficient. The adapter must extract the uncertainty and the **law must consume it** (see missing action A).
   Prerequisite the plan hides: there is no DCC fixture in the repo; the test needs a real DCC example, not a hand-made one.
   Test: a tampered XML → HOLD; a value within its uncertainty of a threshold → HOLD "not decidable".
3. **Replay certificate (PICID) — keep.** In my tradition a certificate is what a third party checks without the issuer.
   Change: the certificate must carry engine tag/commit, rule trace, input hashes. Test: replay in CI; this closes
   `attest_conformance` (SCOPED today) to CLOSED.
4. **CAPAS vs LLM-judge on X6 — keep, change the design.** You do not compare two instruments against each other; you
   compare each against the reference (the sealed outcome) and report degrees of equivalence, as in a key comparison. The
   PNAS 37 %/94 % figures are reproduction rates, not judge error rates: a category mismatch as a "declared prior". Use
   them as context only. Test: sealed pre-registration naming the reference and both error rates with intervals.
5. **Two cheap rules — keep one, restrict the other.** Retraction Watch DOI → HOLD: keep. Paper-vs-prereg diff is not
   cheap: it reads prose, which CAPAS does not. Restrict to structured prereg files (`atlas_prereg/v1`
   `metric_definitions` vs the coded claim). Test: regression tests on X1–X5, in-sample cost declared.

**Missing A — uncertainty as a first-class field with a decision rule.** `capas_invariants.py` flags edge > 1e-2 and T1 <
60 µs on point values. Without uncertainty that is not a conformity statement. Add optional `*_u` and `coverage_factor`
to the snapshot; when |value − threshold| < k·u → HOLD "not decidable", never FLAG or PASS. Test: fixture pairs.
**Missing B — measurand and method declared.** A `cz` error from IBM and a GB/T 47468-2026 test are not commensurable
unless `measurand`/`method` are declared. Missing → the law does not compare across devices; it says so.

## 3. Integration order (90 days)

Weeks 1–2: missing A and B in the snapshot schema and the law; tests; ledger entry. Weeks 3–4: action 1 from the
provenance split. Weeks 5–8: DCC adapter (D-SI value/unit/u/date, signature present and valid → else HOLD, sha256).
Weeks 8–10: action 3, close `attest_conformance`. Weeks 10–12: action 5 (restricted) and the X6 pre-registration
(execution when Atlas has a batch). RO-Crate after day 90.

## 4. Ahead / behind

**CAPAS ahead.** My tradition certifies instruments, never claims, and nobody at PTB publishes the blind error rate of
the certificate process itself. Sealed blind batches, a ledger with CLOSED/BACKED/SCOPED and release blocking, and
self-application have no counterpart in metrology (wave 3: "no German system returns a fail-closed verdict on a claim").

**My tradition ahead.** Uncertainty is mandatory, signed, traceable to the SI; comparisons use declared decision rules;
equivalence between laboratories is measured, not asserted. CAPAS's snapshot law compares point values to thresholds,
and `source.input_sha256` is integrity, not authenticity: it proves the file is unchanged, not who measured.

## 5. Red lines

1. I do not sign a FLAG/PASS against a threshold without uncertainty and a declared decision rule.
2. I do not sign the word "signed" where the mechanism is sha256. Hash = integrity; signature = authenticity. Keep them
   apart on the site and in the ledger.
3. I do not sign a cross-device or cross-standard comparison of numbers without a measurand and method declaration.

## 6. Positioning as a reference

My tradition positions itself through IMEKO TC6, the DCC conference and DCC2Ind, and metrology inside reproducibility
networks (ITRN 2027 at INRiM, wave 3). One concrete step: publish a D-SI-compatible export of `calibration_snapshot`
(value, unit, u, date per parameter) and present the mapping at IMEKO TC6 — the one venue where "a reported number
judged against a signed, dated, uncertain snapshot" is the native language.
