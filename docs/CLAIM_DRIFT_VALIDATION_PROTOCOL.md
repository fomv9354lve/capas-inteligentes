# CAPAS Claim Drift Validation Protocol

Purpose: measure whether claim drift occurs often enough, and with enough operational cost, to justify a claim-level admissibility gate.

CAPAS does not claim to certify broad scientific truth. This protocol tests a narrower question:

> When scientific source material is converted into reusable dataset, report, or fine-tuning records, how often does the reusable claim say more than the supplied evidence licenses?

## 1. Unit of Analysis

The unit is one candidate reusable claim.

Each record should include:

- `record_id`
- `source_id`
- `source_type` such as paper, report, benchmark note, or review
- `source_span`
- `candidate_claim`
- `intended_reuse` such as report, dataset, evaluation set, or fine-tuning
- `claim_type`
- `supplied_evidence`
- `capas_verdict`
- `capas_reason`
- `capas_blockers`
- `reviewer_action`
- `adjudicated_outcome`

## 2. Sampling Plan

Use a corpus that reflects the buyer's actual workflow.

Minimum pilot design:

- 500 candidate reusable claims for a directional readout
- 1,000 candidate reusable claims for a stronger operating baseline
- Stratified sampling across source type, domain, reviewer team, and claim type
- Blind first-pass human review before seeing the CAPAS output, when feasible
- Adjudication for disputed cases by a second domain reviewer

Do not mix synthetic stress tests with production-corpus findings. Stress tests validate software behavior; corpus pilots validate market and operating relevance.

## 3. Drift Classes

Use a small, auditable taxonomy:

- `scope_drift`: the reusable claim is broader than the source span
- `causal_drift`: association becomes causation
- `certainty_drift`: tentative evidence becomes certain language
- `population_drift`: narrow sample becomes broad population
- `temporal_drift`: time-bound result becomes general claim
- `method_drift`: model, assay, or benchmark context is omitted
- `provenance_drift`: source, reviewer, license, or witness evidence is incomplete
- `no_drift`: supplied evidence licenses the reusable claim

## 4. CAPAS Decision Mapping

Map verdicts to operational outcomes:

- `ACCEPT`: supplied evidence licenses the claim boundary for controlled reuse
- `REWRITE`: evidence supports a weaker or narrower claim
- `REJECT`: supplied evidence contradicts or fails the required claim contract
- `HOLD`: the record is not evaluable due to missing schema, evidence, or provenance

Every `REWRITE` or `HOLD` should become a reviewer work item with a next action.

## 5. Metrics

Core metrics:

- `drift_rate = (REWRITE + REJECT + boundary_HOLD) / N`
- `rewrite_rate = REWRITE / N`
- `exclusion_rate = REJECT / N`
- `schema_gap_rate = schema_HOLD / N`
- `provenance_gap_rate = provenance_HOLD / N`
- `accept_rate = ACCEPT / N`
- `fine_tune_ready_rate = fine_tune_ready_true / N`

Reviewer metrics:

- `reviewer_agreement_rate`
- `capas_reviewer_agreement_rate`
- `adjudication_overturn_rate`
- `median_minutes_to_triage`
- `median_minutes_to_resolution`
- `rewrite_to_accept_conversion_rate`

Economic modeling metrics:

- `baseline_review_minutes_per_record`
- `capas_triage_minutes_per_record`
- `exception_resolution_minutes_per_record`
- `review_capacity_redirected_hours`

Economic figures are planning assumptions until calibrated against buyer time logs.

## 6. Hypotheses

Suggested pilot hypotheses:

- H1: At least 10% of candidate reusable claims require rewrite, rejection, or hold before controlled reuse.
- H2: CAPAS reduces variance in reviewer decisions by making claim-type evidence contracts explicit.
- H3: CAPAS shortens triage time by routing non-accepted claims into explicit exception queues.
- H4: REWRITE cases convert to ACCEPT after reviewer correction at a measurable rate.
- H5: Claim-level gating catches issues that source-level provenance and dataset-lineage controls do not catch.

Thresholds should be set with the buyer before the pilot starts.

## 7. Reviewer Workflow

1. Select candidate claim records from the target corpus.
2. Capture source span and intended reuse.
3. Assign a CAPAS claim type or mark unsupported.
4. Supply evidence fields.
5. Run CAPAS.
6. Route output:
   - `ACCEPT`: eligible for controlled reuse
   - `REWRITE`: reviewer narrows claim and resubmits
   - `REJECT`: exclude or collect new evidence
   - `HOLD`: repair schema, missing evidence, or provenance
7. Adjudicate disputed records.
8. Export audit packet and decision mix.

## 8. Required Deliverables

A validation pilot should produce:

- Claim contamination register
- Decision mix by claim type and source type
- Exception queue with blockers and next actions
- REWRITE to ACCEPT conversion log
- Provenance blocker report
- Audit export JSON/CSV
- Methodology notes and exclusions
- Executive readout with measured rates and caveats

## 9. Non-Claims

This protocol does not establish that:

- CAPAS verifies scientific truth
- CAPAS replaces domain expert review
- CAPAS can infer hidden evidence
- Internal stress-test rates generalize to a buyer's corpus
- Any modeled review-hour savings are guaranteed

The purpose is narrower and auditable: measure claim drift, decision repeatability, exception routing, and the operational value of claim-level admissibility.

