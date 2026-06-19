# CAPAS Provenance Registry Operations

Fine-tune readiness requires active provenance verification. Browser UI can
preview the criteria; CLI/API verification resolves the artifacts.

## Required registries

- Witness registry: `docs/witness_registry.json`
- Reviewer registry: `docs/reviewer_registry.json`
- RO-Crate metadata: `benchmarks/ro_crates/<trace>/ro-crate-metadata.json`
- Source URL hashes: `training_evidence.provenance.source_hashes`

## Verification command

```bash
capas provenance-check --input examples/external_claim_fine_tune_ready.json --json
```

The command verifies:

- review packet SHA-256
- source URL/file SHA-256
- witness ID in registry
- RO-Crate metadata hash and structure
- reviewer ID and attestation hash

## Enterprise API endpoint

```bash
curl -H "Authorization: Bearer $CAPAS_API_TOKEN" \
  -H "X-CAPAS-Workspace: pilot" \
  -H "Content-Type: application/json" \
  --data @examples/external_claim_fine_tune_ready.json \
  http://127.0.0.1:8765/provenance-check
```
