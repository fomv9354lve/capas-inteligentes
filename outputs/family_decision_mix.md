# CAPAS per-family decision-mix (decision-space coverage)

Total synthetic payloads: **1238** · run through `capas.decide_external_claim` (the real engine).

> Contract-coverage / decision-space benchmark over synthetic payloads. Demonstrates deterministic, full-verdict-space coverage per family at scale. NOT a real-world drift rate (that needs an independently adjudicated corpus with interrater agreement). Percentages reflect the synthetic grid.

| Claim family | N | ACCEPT | REWRITE | REJECT | HOLD | verdicts reached |
|---|---:|---:|---:|---:|---:|---|
| `exact_model_solution` | 182 | 57.1% | 0.0% | 41.8% | 1.1% | ACCEPT/HOLD/REJECT |
| `physical_accuracy` | 3 | 33.3% | 0.0% | 33.3% | 33.3% | ACCEPT/HOLD/REJECT |
| `statistical_confidence` | 543 | 13.6% | 13.6% | 72.2% | 0.6% | ACCEPT/HOLD/REJECT/REWRITE |
| `reproducibility_check` | 6 | 16.7% | 16.7% | 33.3% | 33.3% | ACCEPT/HOLD/REJECT/REWRITE |
| `financial_metric_claim` | 364 | 8.0% | 8.0% | 83.0% | 1.1% | ACCEPT/HOLD/REJECT/REWRITE |
| `causal_mechanism_claim` | 20 | 5.0% | 15.0% | 60.0% | 20.0% | ACCEPT/HOLD/REJECT/REWRITE |
| `systematic_review_claim` | 20 | 5.0% | 15.0% | 60.0% | 20.0% | ACCEPT/HOLD/REJECT/REWRITE |
| `evidence_conflict_claim` | 20 | 5.0% | 5.0% | 70.0% | 20.0% | ACCEPT/HOLD/REJECT/REWRITE |
| `multimodal_evidence_claim` | 20 | 10.0% | 30.0% | 40.0% | 20.0% | ACCEPT/HOLD/REJECT/REWRITE |
| `programming_language_behavior_claim` | 16 | 6.2% | 18.8% | 25.0% | 50.0% | ACCEPT/HOLD/REJECT/REWRITE |
| `claim_transition` | 3 | 33.3% | 33.3% | 0.0% | 33.3% | ACCEPT/HOLD/REWRITE |
| `universal_anchor_claim` | 41 | 2.4% | 12.2% | 53.7% | 31.7% | ACCEPT/HOLD/REJECT/REWRITE |

Overall: ACCEPT 217 · REWRITE 126 · REJECT 845 · HOLD 50

