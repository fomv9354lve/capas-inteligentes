# CAPAS Enterprise Integration Pack

CAPAS is designed to sit between extraction/annotation and model training:

`Paper or corpus source -> extraction/annotation -> CAPAS gate -> dataset registry -> training pipeline`

## 1. CLI

```bash
capas decide --input claim.json --output decision.json
capas batch --input claims.json --output batch-report.json
capas provenance-check --input claim-with-training-evidence.json --json
```

## 2. Local API

```bash
CAPAS_API_TOKEN=change-me CAPAS_AUDIT_DIR=outputs/api-audit \
  capas serve --host 127.0.0.1 --port 8765
```

Endpoints:

- `GET /health`
- `GET /decisions` with `X-CAPAS-Workspace: <workspace>`
- `POST /decide`
- `POST /batch`
- `POST /provenance-check`

Use `Authorization: Bearer <token>` when `CAPAS_API_TOKEN` or `--api-token`
is configured.

## 3. GitHub Action

```yaml
- uses: ./.github/actions/capas-claim-gate
  with:
    mode: batch
    input: examples/external_claim_batch.json
    output: outputs/capas-action-report.json
```

## 4. Label Studio / Argilla handoff

Annotation tools should export one JSON payload per claim with:

- `schema_version`
- `claim.id`, `claim.type`, `claim.text`
- `evidence`
- optional `training_evidence.provenance`

CAPAS then emits `ACCEPT`, `REWRITE`, `REJECT`, or `HOLD` and preserves the
decision as an audit artifact.

## 5. Hugging Face Datasets handoff

Store CAPAS metadata per row:

- `capas_schema_version`
- `capas_verdict`
- `capas_reason`
- `capas_fine_tune_ready`
- `capas_decision_json`

This allows a dataset card to disclose which rows were accepted, rewritten,
rejected, or held before fine-tuning.
