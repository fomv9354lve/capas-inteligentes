# CAPAS Pilot ROI and Business Case

## Business question

Can CAPAS reduce senior scientific review time while improving auditability for
claims entering an AI fine-tuning corpus?

## Pilot design

- Corpus size: 500-1,000 candidate claims.
- Baseline: manual expert review in spreadsheets.
- CAPAS path: extraction/annotation -> guided payload -> deterministic gate ->
  exportable audit artifact.
- Success metrics:
  - review minutes per claim
  - reject/rewrite/hold rates
  - provenance-complete rate
  - fine-tune-ready rate
  - number of downstream dataset defects caught before training

## Example economics

For 1,000 claims:

- manual expert review: 30 minutes per claim = 500 hours
- CAPAS-guided triage: 5 minutes per claim = 83 hours
- avoided senior-review capacity: 417 hours
- at USD 200/hour: USD 83,400 of review capacity avoided

This excludes the larger avoided cost of retraining, compliance remediation, or
removing contaminated data after a model has already learned it.
