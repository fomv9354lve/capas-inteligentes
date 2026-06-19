# CAPAS Claim Gate - Partner Deck

## 1. Title

**Training Data Assurance for Scientific AI**

CAPAS is a deterministic control layer that prevents unsupported scientific claims from entering reports, governed datasets, and fine-tuning pipelines.

## 2. The client problem

Scientific AI teams are building domain-specific models from papers, reports, theorem notes, experiments, and internal evidence. Candidate claims move into fine-tuning datasets before anyone can prove that the evidence licenses the exact wording.

The result is a governance gap:

- plausible text enters training data,
- expert review is expensive and inconsistent,
- audit trails are reconstructed after the fact,
- downstream users cannot trace why a claim was accepted.

## 3. The so what

CAPAS creates a pre-training quality gate. It does not ask an LLM if a claim is true. It checks typed evidence fields against deterministic rules and emits ACCEPT, REWRITE, REJECT, or HOLD with an auditable reason.

Business impact:

- fewer unsupported claims in training data,
- fewer senior-review hours spent on obvious cases,
- earlier detection of overclaims,
- evidence packets ready for model-risk and research-integrity review.

## 4. Where CAPAS fits

**Retrieve / extract upstream. Decide with CAPAS.**

1. Ingest paper text, theorem notes, metadata exports, or local corpus snippets.
2. Human reviewer confirms candidate evidence spans.
3. CAPAS validates schema v3 and claim-type evidence requirements.
4. CAPAS surfaces provenance blockers: source hashes, RO-Crate, reviewer attestation, witness registry.
5. Only fine-tune-ready claims enter governed datasets.

## 5. Why now

Scientific and regulated AI teams are moving from prompt-only demos to domain-specific fine-tuned systems. That shifts risk upstream: quality is no longer only an inference-time issue; it is a training-data governance issue.

CAPAS gives the buyer a measurable control before fine-tuning.

## 6. Differentiation

CAPAS is not Elicit, Label Studio, Argilla, MLflow, DVC, or a fact-checking benchmark.

- Elicit finds and summarizes research.
- Label Studio and Argilla help humans annotate data.
- MLflow and DVC track datasets and experiments.
- Fact-checking systems evaluate generated claims post hoc.
- CAPAS gates structured scientific claims before they enter training data.

The wedge is the combination of:

- typed scientific claim schemas,
- deterministic gate rules,
- required human confirmation for extracted candidates,
- fine-tune readiness criteria,
- provenance and RO-Crate blockers,
- non-LLM decision markers in every output.

## 7. Pilot design

Two-week pilot:

- 500 candidate claims from one vertical corpus.
- One vertical: AI governance, pharma evidence review, finance model risk, journal reproducibility, or materials R&D.
- CAPAS batch run with human spot adjudication.
- 100-decision senior-review sample.
- Executive readout with decision mix, error cases, provenance blockers, and ROI model.

Success metrics:

- 80%+ reviewer agreement on ACCEPT and REJECT.
- 5% or lower confirmed false reject rate in sample.
- 25%+ senior-review hours avoided.
- 100% audit trail on fine-tune-ready positives.

## 8. ROI model

Default simulated pilot:

- 1,000 candidate claims.
- 30 minutes manual review per claim.
- 5 minutes CAPAS-guided triage per claim.
- 417 senior-review hours avoided.
- USD 180/hour expert loaded cost.
- About USD 75k review capacity avoided.

Formula:

`hours avoided = claims * (manual_minutes - CAPAS_minutes) / 60`

`capacity value = hours avoided * expert_hourly_rate`

This is a capacity model. The pilot validates the actual baseline and triage time.

## 9. Demo flow

1. Open the CAPAS Claim Gate app.
2. Show the training-data assurance workflow and ROI calculator.
3. Paste paper/theory text into Paper/Text Ingestion.
4. Extract candidates and inspect evidence spans.
5. Confirm one candidate and run Decide.
6. Run Batch on mixed claims.
7. Show expandable per-item decisions and fine-tune blockers.
8. Export CSV or run CLI/API/GitHub Action.

## 10. Buyer ask

Authorize a two-week pilot on one real corpus.

Decision needed:

- one accountable AI governance or scientific data owner,
- one corpus of candidate claims,
- one expert reviewer for adjudication,
- agreement on baseline review-time measurement,
- approval to produce a non-production audit readout.

## 11. Boundary statement

CAPAS gates supplied evidence. It does not infer hidden evidence, certify broad scientific truth, or replace expert review. Its value is deterministic structure, traceability, and early risk reduction before scientific claims enter governed AI pipelines.
