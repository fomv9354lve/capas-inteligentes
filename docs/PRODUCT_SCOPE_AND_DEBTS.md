# CAPAS Product Scope and Debt Status

This document separates closed implementation debt from debt that requires an
external actor. It is part of the product contract: CAPAS should not present a
stronger status than the evidence supports.

## Closed in the local product surface

### Batch mode

CAPAS can now process multiple claim/evidence objects in one command:

```bash
capas batch --input examples/external_claim_batch.json --json
```

Accepted input shapes:

- a JSON array of claim/evidence objects,
- an object with `items: [...]`,
- an object with `claims: [...]`.

Batch mode applies the same deterministic per-claim gates. It does not infer
new evidence and it does not make the batch fine-tune ready.

### Local HTTP API

CAPAS exposes a local stdlib HTTP API for integration tests and pipeline
prototypes:

```bash
capas serve --host 127.0.0.1 --port 8765
```

Endpoints:

- `GET /health`
- `POST /decide`
- `POST /batch`

This is an integration surface, not a hosted SaaS endpoint.

### Browser E2E

The static Claim Gate UI has a real headless Chrome/Chromium E2E check:

```bash
python benchmarks/verify_claim_gate_ui_browser.py
```

It exercises:

- empty-input handling,
- `Build Draft`,
- draft/null status,
- `REWRITE` decision,
- rewrite diff,
- syntax-highlighted JSON output,
- history restore.

## Still intentionally not complete

### Formal RO-Crate profile registration

Current status: `formal_profile_registered: False`.

CAPAS has a local profile packet and readiness validator:

```bash
python scripts/prepare_profile_registration_packet.py
python benchmarks/verify_profile_registration_packet.py
```

This does not equal formal registration. Formal registration requires acceptance
or listing by the relevant RO-Crate/profile registry process or maintainers.

### fine_tune_ready

Current status: always `False`.

This is intentional. A decision may be structurally valid and still not be a
training datum. `fine_tune_ready=True` requires all of the following:

1. deterministic gate decision is `ACCEPT` or explicitly licensed `REWRITE`,
2. required evidence fields are present and source-backed,
3. claim text passes semantic/scope alignment,
4. witness independence is declared,
5. evidence level and scope are declared,
6. blind or external review confirms that the licensed claim is correct,
7. no unresolved schema, source, or provenance warnings remain.

Until blind/external review exists, the product must keep
`fine_tune_ready=False`.

### Build Draft heuristic

`Build Draft` is an onboarding assistant. It can scaffold a candidate JSON
payload from incomplete text or partial JSON, but it is not an evidence
extractor and it never licenses a claim. The strict gate still decides only
after the user supplies explicit evidence.

### Semantic verification limits

CAPAS provides deterministic lexical/scope guardrails through `capas align` and
the standalone pipeline. It does not perform broad scientific language
understanding. If a claim requires domain interpretation outside the structured
fields, CAPAS should return `HOLD` or require an upstream verifier.

### GitHub Actions Node warning

The project tracks GitHub Actions runtime deprecation warnings. If upstream
actions still emit Node runtime warnings after version updates, the warning is
treated as non-blocking external platform debt, not a CAPAS product failure.

## Validation command

The product gate remains:

```bash
capas validate
```

This validates local implementation readiness, not external adoption.
