# CAPAS Schema Registry

CAPAS payloads are versioned contracts. Production integrations should pin the
schema URL and reject payloads that do not declare the active version.

## Current schema

- Version: `capas-claim-payload-v3`
- Canonical URL: `https://fomv9354lve.github.io/capas-inteligentes/schema/v3/capas_claim_payload.schema.json`
- Repository path: `docs/schema/v3/capas_claim_payload.schema.json`
- Compatibility rule: v1/v2/missing `schema_version` must fail closed with `HOLD`.

## Local validation

```bash
capas check-input --input examples/external_claim_accept.json --json
capas schema --output docs/schema/v3/capas_claim_payload.schema.json
```

## Integration rule

External systems should treat `$id` as the stable contract and store both
`schema_version` and the schema URL with every accepted decision.
