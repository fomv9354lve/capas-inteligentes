# CAPAS Claim Gate - Customer Ready Brief

## One-page value proposition

CAPAS is a deterministic quality gate for scientific claims before they enter reports, datasets, or fine-tuning pipelines. It does not ask an LLM whether a claim is true. It checks whether supplied structured evidence licenses the exact claim wording, then emits an auditable `ACCEPT`, `REWRITE`, `REJECT`, or `HOLD`.

The business value is senior-review leverage: reviewers stop re-reading every candidate claim from scratch and instead focus on the claims CAPAS identifies as missing evidence, over-claiming, contradicted, or provenance-blocked.

Category framing: CAPAS is **Training Data Assurance for Scientific AI**. It is the control layer between retrieval/extraction systems and model fine-tuning, preventing unsupported scientific claims from entering governed datasets.

## Executive so what

The risk is not only hallucination at inference time. The upstream risk is that plausible but unsupported scientific claims enter fine-tuning data and become part of the model's learned behavior. CAPAS addresses that earlier control point.

Executive outcome:

- Reduce senior-review hours by routing reviewers to exceptions.
- Reduce dataset rework by catching overclaims before fine-tuning.
- Improve auditability by attaching schema, decision reason, source spans, provenance blockers, and `non_claim` markers to every output.
- Give model-risk, research-integrity, and AI-governance teams a measurable approval gate.

## Primary persona and buyer

Primary user: AI governance lead or scientific data steward responsible for training-data quality.

Economic buyer: Head of AI governance, research integrity, scientific data platforms, model risk, or regulated R&D operations.

Secondary users: journal reproducibility teams, pharma evidence-review teams, finance model-risk teams, and academic labs building curated scientific datasets.

## Before / after workflow

Before CAPAS:

- Candidate claims are reviewed in spreadsheets, notebooks, or prose.
- Reviewers debate whether wording is too strong.
- Fine-tuning datasets inherit weak provenance.
- Audit trails are reconstructed after the fact.

After CAPAS:

- Paper text, abstracts, theorem notes, or local metadata exports can be ingested into candidate claims with visible evidence spans.
- Claims are typed against `capas-claim-payload-v3`.
- Required evidence fields are checked deterministically.
- Batch review produces explicit rates for `ACCEPT`, `REWRITE`, `REJECT`, `HOLD`, and `fine_tune_ready`.
- RO-Crate, reviewer attestation, witness registry, and source hash blockers are visible before data moves downstream.

## Two-week pilot design

Scope: 500 candidate scientific training claims from one vertical corpus.

Pilot steps:

1. Select one vertical: AI governance, pharma evidence review, academic journal reproducibility, or finance model-risk.
2. Convert 500 candidate claims into CAPAS payloads using the guided form, CLI, or upstream extraction adapter.
3. Run CAPAS batch gate.
4. Sample 100 decisions for senior-review adjudication.
5. Measure reviewer agreement, false rejects, rewrite acceptance, provenance blocker rate, and time saved.

Pilot success metrics:

- At least 80% reviewer agreement on `ACCEPT` and `REJECT`.
- Less than 5% confirmed false rejects in the adjudicated sample.
- At least 25% reduction in senior-review hours.
- Full audit trail for all `fine_tune_ready` positives.

## Simulated case study

Illustrative run: CAPAS gated 1,000 candidate training claims.

- 620 accepted for ordinary downstream use.
- 230 rewritten before reuse.
- 110 rejected before downstream risk.
- 40 held for missing or unresolved evidence.
- 40 reached `fine_tune_ready` after external provenance verification.

Assumption model: 30 minutes of manual review per claim vs. 5 minutes of triage review after CAPAS. That is 25,000 minutes avoided, or roughly 417 senior-review hours.

At an illustrative USD 180/hour expert review rate, the same pilot model represents about USD 75k of senior-review capacity redirected to exceptions, adjudication, and provenance resolution.

## ROI calculator assumptions

Core formula:

`hours avoided = claims * (manual_minutes_per_claim - capas_triage_minutes_per_claim) / 60`

`capacity value = hours avoided * expert_hourly_rate`

Default pilot model:

- 1,000 claims.
- 30 manual minutes per claim.
- 5 CAPAS-guided triage minutes per claim.
- USD 180/hour senior reviewer loaded cost.
- 417 hours avoided.
- About USD 75k review capacity avoided.

This is a capacity model, not a promise of booked savings. The pilot should measure actual baseline review time, adjudication time, false reject rate, and downstream rework avoided.

## Vertical demo: AI governance

Demo story: an AI governance team wants to curate high-confidence scientific claims for model fine-tuning. CAPAS receives candidate claims, checks typed evidence, blocks claims without verified provenance, and exports a CSV audit trail for review committee signoff.

Live demo sequence:

1. Load the AI governance guided demo.
2. Paste a paper abstract or theorem note into Paper/Text Ingestion.
3. Extract candidate claims, inspect evidence spans, and confirm one candidate.
4. Run `Decide`.
5. Show the verdict and fine-tune blockers.
6. Run `Batch` on a mixed list.
7. Show the executive dashboard and per-item expandable rows.
8. Toggle Sensitive mode and export redacted CSV.

## Pricing hypothesis

These are working hypotheses, not published pricing:

- Two-week pilot: USD 15k-25k for 500 claims, setup, adjudication support, and executive readout.
- Team tier: USD 2k-5k per month for guided review, local history/export, and schema-governed batch workflows.
- Enterprise/API tier: USD 50k-150k per year for CLI/API integration, GitHub Action enforcement, provenance registry integration, and support for regulated corpora.

## Integration story

Current surfaces:

- Browser UI for guided review, batch inspection, history, export, and share flows.
- `capas.py decide` for single-claim CLI gating.
- `capas.py batch` for corpus gating.
- `capas.py serve` for local REST integration.
- GitHub Action for pipeline enforcement.

Upstream integration story:

- Semantic Scholar, PubMed, Elicit, or internal retrieval can prepare candidate evidence.
- The browser includes a local paper/text ingestion preview: pasted text or local files become candidate claims with spans, and no candidate can be decided until a human confirms it.
- CAPAS remains the deterministic final gate: retrieve and extract upstream, then decide with CAPAS.

## Partner-ready workflow view

1. Ingest: paper text, theorem notes, metadata exports, or local corpus snippets.
2. Confirm: human reviewer accepts candidate evidence spans.
3. Gate: schema v3 plus claim-type rules emit ACCEPT/REWRITE/REJECT/HOLD.
4. Provenance: source hashes, RO-Crate, reviewer attestation, and witness registry blockers are resolved through CLI/API surfaces.
5. Approve: only fine-tune-ready positives enter governed training datasets.

This lets a consulting or enterprise AI team sell a concrete operating model, not only a technical validator.

## Paper/theory ingestion boundary

CAPAS can ingest pasted paper text, abstracts, theorem notes, local text/Markdown/JSON/JSONL files, and PDF provenance metadata in the browser. Candidate extraction is deterministic and span-based. It does not perform full academic argument mining, theorem proving, or automatic scientific certification. For PDF text extraction and local corpora, use the CLI standalone path: `retrieve`, `extract`, `align`, `reason`, and `pipeline`.

## Sensitive data mode

Sensitive mode disables payload-embedded share URLs and redacts payload/decision fields in CSV export. This is intended for demos and regulated workflows where claim text, source IDs, reviewer IDs, or provenance paths must not leave the local review context.

## Customer-facing caveat

CAPAS structures and gates supplied evidence. It does not infer hidden evidence, certify broad scientific truth, or replace external review. `fine_tune_ready: true` is only appropriate after active provenance verification through CLI/API surfaces that can hash sources, resolve registries, validate RO-Crate packets, and verify reviewer attestations.
